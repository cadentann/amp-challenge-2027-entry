#!/usr/bin/env python3
"""Retrieve every pinned external asset this entry needs, verify it, and build
the isolated scorer runtime.

A fresh clone of this repository contains no model weights and no scorer
runtime: the AMP-Prompt checkpoint (315 MB) and the APEX/ANIA evaluator assets
(235 MB) are third-party artifacts that are fetched from their published
sources rather than redistributed here. This script performs that retrieval.

Everything it writes is verified against a hash that was pinned before the
retrieval ran. Nothing is trusted because it downloaded successfully.

    uv run python scripts/prepare_entry.py

It is idempotent: completed stages are detected and skipped, and partial
downloads are cached under .finalist-downloads/ so an interrupted run resumes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor/evaluator"
DOWNLOADS = ROOT / ".finalist-downloads"
STAGING = ROOT / ".finalist-staging/evaluator-assets"
RUNTIME = ROOT / "runtime/scorer"

RUNTIME_MANIFEST_SHA256 = "ecacbe1ed1fa840ecd9c684ccf781e808ba33a3f97420384473e3d3115e77fa7"
SCORER_RUNTIME_LOCK_SHA256 = "d74ea38c347d7ce99f885566940b2addedb0ebc1097532bded070ab16c3801a1"
SCORE_TIMEOUT_SECONDS = 7200

# Upstream sources, pinned to immutable commits. ANIA's commit is the one the
# evaluator was built against; APEX publishes weights only from a branch ref, so
# the branch tip is pinned here as a commit and every retrieved byte is still
# checked against RUNTIME_MANIFEST.json.
ANIA_REPO = "SilverGojo4/ANIA"
ANIA_COMMIT = "7bde436e0b5df8e44f9a598e312bd1944006cb3d"
APEX_PROJECT_ID = "48405499"
APEX_COMMIT = "417a4441a1e6ef8b10d2352e1c059622d5259f3a"
# Only the APEX files that are byte-identical to upstream are fetched. APEX_predict.py and
# utils.py are modified derivatives that upstream does not serve, so they are vendored under
# vendor/evaluator/assets/apex/ with attribution - see the NOTICE.md beside them.
APEX_SOURCE_FILES = {
    "assets/apex/APEX_models.py": "APEX_models.py",
    "assets/apex/aaindex1.csv": "aaindex1.csv",
}

# FINALIST.lock.json pins one scorer-runtime lock hash, and that lock is the Linux/x86_64 one.
# There is no validated macOS runtime lock, so the pipeline can only be completed on Linux/x86_64.
# The macOS equivalence receipt exists and is shipped, but it certifies the evaluator's numerical
# agreement on macOS - it does not make a macOS runtime satisfy the pinned lock.
REQUIRED_PLATFORM = ("Linux", "x86_64")
EQUIVALENCE_EVIDENCE = {
    ("Linux", "x86_64"): "validation/LINUX_CROSS_EVALUATOR_EQUIVALENCE.json",
}


class PrepareError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def log(message: str) -> None:
    print(f"[prepare] {message}", flush=True)


def matches(path: Path, expected_sha: str, expected_bytes: int | None = None) -> bool:
    if not path.is_file():
        return False
    if expected_bytes is not None and path.stat().st_size != expected_bytes:
        return False
    return sha256(path) == expected_sha


def download(url: str, destination: Path, expected_sha: str, expected_bytes: int | None = None,
             label: str = "") -> Path:
    """Fetch `url` to `destination` and refuse to return unless it hashes."""
    if matches(destination, expected_sha, expected_bytes):
        log(f"cached   {label or destination.name}")
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".partial")
    log(f"fetching {label or destination.name}")
    request = urllib.request.Request(url, headers={"User-Agent": "amp-challenge-entry-prepare/1"})
    try:
        with urllib.request.urlopen(request, timeout=300) as response, temporary.open("wb") as handle:
            shutil.copyfileobj(response, handle, 1024 * 1024)
    except urllib.error.URLError as error:
        raise PrepareError(f"could not retrieve {url}: {error}") from error
    observed = sha256(temporary)
    if observed != expected_sha:
        size = temporary.stat().st_size
        temporary.unlink()
        raise PrepareError(
            f"{label or url} failed verification\n"
            f"  expected sha256 {expected_sha}\n"
            f"  observed sha256 {observed} ({size} bytes)\n"
            f"  The upstream source no longer serves the pinned bytes. "
            f"Do not proceed; this entry is only reproducible against the pinned assets."
        )
    temporary.replace(destination)
    return destination


def load_manifest() -> list[dict]:
    manifest_path = VENDOR / "RUNTIME_MANIFEST.json"
    if sha256(manifest_path) != RUNTIME_MANIFEST_SHA256:
        raise PrepareError("vendored RUNTIME_MANIFEST.json does not match its pin")
    return json.loads(manifest_path.read_text())["files"]


def verify_tree(root: Path, files: list[dict], label: str) -> None:
    missing, wrong = [], []
    for item in files:
        path = root / item["path"]
        if not path.is_file():
            missing.append(item["path"])
        elif path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
            wrong.append(item["path"])
    if missing or wrong:
        detail = "".join(f"\n  missing: {p}" for p in missing) + "".join(f"\n  changed: {p}" for p in wrong)
        raise PrepareError(f"{label} failed verification ({len(missing)} missing, {len(wrong)} changed){detail}")
    log(f"verified {len(files)} files in {label}")


# --------------------------------------------------------------------------
# Stage 1 - AMP-Prompt generator checkpoint (Zenodo, CC-BY-4.0)
# --------------------------------------------------------------------------

def stage_generator(sources: dict) -> None:
    spec = sources["amp_prompt"]
    model_dir = ROOT / "assets/prompt_model"
    checkpoint = model_dir / spec["checkpoint_member"]
    if matches(checkpoint, spec["checkpoint_sha256"], spec["checkpoint_bytes"]):
        log("generator checkpoint already present and verified")
        return
    archive = download(
        spec["archive_url"], DOWNLOADS / "prompt_model.zip",
        spec["archive_sha256"], spec["archive_bytes"], label="AMP-Prompt weights (Zenodo, 315 MB)",
    )
    log("extracting AMP-Prompt archive")
    model_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            name = Path(member.filename)
            if member.is_dir() or name.is_absolute() or ".." in name.parts:
                continue
            # The archive nests its files under a single directory; flatten it.
            relative = Path(*name.parts[1:]) if len(name.parts) > 1 else name
            target = model_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(member) as source, target.open("wb") as handle:
                shutil.copyfileobj(source, handle, 1024 * 1024)
    if not matches(checkpoint, spec["checkpoint_sha256"], spec["checkpoint_bytes"]):
        raise PrepareError(
            f"extracted checkpoint {checkpoint} does not match its pinned sha256 "
            f"{spec['checkpoint_sha256']}"
        )
    log(f"generator checkpoint verified ({spec['checkpoint_bytes']} bytes)")


# --------------------------------------------------------------------------
# Stage 2 - evaluator assets (ANIA + APEX, both MIT)
# --------------------------------------------------------------------------

def stage_ania_source(files: list[dict]) -> None:
    wanted = {
        f["path"]: f for f in files
        if f["path"].startswith("assets/ania/") and not f["path"].startswith("assets/ania/weights/")
    }
    if all(matches(STAGING / p, f["sha256"], f["bytes"]) for p, f in wanted.items()):
        log("cached   ANIA source tree")
        return
    url = f"https://codeload.github.com/{ANIA_REPO}/tar.gz/{ANIA_COMMIT}"
    archive = DOWNLOADS / f"ania-{ANIA_COMMIT[:12]}.tar.gz"
    if not archive.is_file():
        archive.parent.mkdir(parents=True, exist_ok=True)
        log(f"fetching ANIA source at {ANIA_COMMIT[:12]}")
        request = urllib.request.Request(url, headers={"User-Agent": "amp-challenge-entry-prepare/1"})
        with urllib.request.urlopen(request, timeout=300) as response, archive.open("wb") as handle:
            shutil.copyfileobj(response, handle, 1024 * 1024)
    prefix = f"ANIA-{ANIA_COMMIT}/"
    extracted = 0
    with tarfile.open(archive, "r:gz") as bundle:
        for path, item in wanted.items():
            member_name = prefix + path[len("assets/ania/"):]
            try:
                member = bundle.getmember(member_name)
            except KeyError as error:
                raise PrepareError(f"ANIA archive has no member {member_name}") from error
            source = bundle.extractfile(member)
            if source is None:
                raise PrepareError(f"ANIA archive member {member_name} is not a regular file")
            target = STAGING / path
            target.parent.mkdir(parents=True, exist_ok=True)
            with source, target.open("wb") as handle:
                shutil.copyfileobj(source, handle, 1024 * 1024)
            extracted += 1
    log(f"extracted {extracted} ANIA source files")


def stage_apex_source(files: list[dict]) -> None:
    index = {f["path"]: f for f in files}
    for path, upstream in APEX_SOURCE_FILES.items():
        item = index[path]
        encoded = urllib.parse.quote(upstream, safe="")
        url = (
            f"https://gitlab.com/api/v4/projects/{APEX_PROJECT_ID}"
            f"/repository/files/{encoded}/raw?ref={APEX_COMMIT}"
        )
        download(url, STAGING / path, item["sha256"], item["bytes"], label=f"APEX {upstream}")


def stage_weights(config: dict) -> None:
    for entry in config["apex_weights"]:
        # runtime_config.json is hash-pinned and cannot be edited, so the branch
        # ref it carries is replaced with the pinned commit at retrieval time.
        url = entry["url"].replace("ref=main", f"ref={APEX_COMMIT}")
        download(url, STAGING / entry["path"], entry["sha256"], entry["bytes"],
                 label=f"APEX weights {entry['name']} ({entry['bytes'] // 1_000_000} MB)")
    for entry in config["ania_weights"]:
        download(entry["url"], STAGING / entry["path"], entry["sha256"], entry["bytes"],
                 label=f"ANIA weights {entry['name']}")


def stage_vendored(files: list[dict]) -> None:
    vendored_assets = {"assets/apex/APEX_predict.py", "assets/apex/utils.py"}
    count = 0
    for item in files:
        if item["path"].startswith("assets/") and item["path"] not in vendored_assets:
            continue
        source = VENDOR / item["path"]
        if not source.is_file():
            raise PrepareError(f"vendored evaluator file is missing from the repository: {item['path']}")
        target = STAGING / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        count += 1
    shutil.copyfile(VENDOR / "RUNTIME_MANIFEST.json", STAGING / "RUNTIME_MANIFEST.json")
    log(f"installed {count} vendored evaluator files")


def stage_evaluator_assets(files: list[dict]) -> None:
    STAGING.mkdir(parents=True, exist_ok=True)
    stage_vendored(files)
    config = json.loads((VENDOR / "runtime_config.json").read_text())
    stage_ania_source(files)
    stage_apex_source(files)
    stage_weights(config)
    verify_tree(STAGING, files, "evaluator assets")
    if sha256(STAGING / "RUNTIME_MANIFEST.json") != RUNTIME_MANIFEST_SHA256:
        raise PrepareError("staged RUNTIME_MANIFEST.json does not match its pin")


# --------------------------------------------------------------------------
# Stage 3 - isolated scorer runtime
# --------------------------------------------------------------------------

def stage_runtime() -> None:
    if (RUNTIME / "SCORER_RUNTIME.lock.json").is_file():
        if sha256(RUNTIME / "SCORER_RUNTIME.lock.json") == SCORER_RUNTIME_LOCK_SHA256:
            log("scorer runtime already built and validated")
            return
        log("removing an incomplete or unvalidated scorer runtime")
        shutil.rmtree(RUNTIME)
    elif RUNTIME.exists():
        shutil.rmtree(RUNTIME)
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    log("building the isolated Python 3.10 scorer runtime (uv sync)")
    # This may run inside `uv run`, whose VIRTUAL_ENV and UV_* variables would otherwise
    # steer the scorer's own `uv sync` at the generator environment.
    environment = {k: v for k, v in os.environ.items() if not k.startswith("UV_")}
    environment.pop("VIRTUAL_ENV", None)
    environment.pop("PYTHONPATH", None)
    subprocess.run(
        [
            sys.executable, str(ROOT / "tools/bootstrap_scorer_runtime.py"),
            "--assets-source", str(STAGING),
            "--target", str(RUNTIME),
            "--score-timeout-seconds", str(SCORE_TIMEOUT_SECONDS),
        ],
        env=environment,
        check=True,
    )
    promote_runtime()


def promote_runtime() -> None:
    """Install the shipped cross-evaluator equivalence receipt for this platform.

    The receipt is only installed when the runtime that was just built reports
    exactly the environment the receipt was produced under. If it does not, the
    runtime stays PENDING and the entry refuses to score - which is the correct
    outcome, because no equivalence evidence exists for that machine.
    """
    bootstrapped = json.loads((RUNTIME / "SCORER_RUNTIME.lock.json").read_text())
    observed = bootstrapped["environment"]
    key = (observed["platform_system"], observed["platform_machine"])
    relative = EQUIVALENCE_EVIDENCE.get(key)
    if relative is None:
        raise PrepareError(
            f"this entry can only be completed on {REQUIRED_PLATFORM[0]}/{REQUIRED_PLATFORM[1]}, "
            f"and this machine is {key[0]}/{key[1]}.\n"
            f"  FINALIST.lock.json pins one scorer-runtime lock, and the only runtime lock that was\n"
            f"  ever validated is the Linux/x86_64 one. The evaluator assets and the isolated\n"
            f"  runtime have been built successfully and are left in place at {RUNTIME}, but the\n"
            f"  runtime stays PENDING_CROSS_EVALUATOR_EQUIVALENCE and `generate` will refuse to\n"
            f"  score, which is the correct fail-closed behaviour rather than running against an\n"
            f"  unvalidated runtime.\n"
            f"  The shipped macOS equivalence receipt certifies that the evaluator agrees\n"
            f"  numerically on macOS; it does not make a macOS runtime satisfy the pinned lock."
        )
    evidence_source = ROOT / relative
    receipt = json.loads(evidence_source.read_text())
    if receipt.get("environment") != observed:
        raise PrepareError(
            "the scorer runtime that was built does not match the environment the shipped "
            "equivalence evidence was produced under, so it cannot be marked validated.\n"
            f"  built:    {json.dumps(observed, sort_keys=True)}\n"
            f"  evidence: {json.dumps(receipt.get('environment'), sort_keys=True)}"
        )
    target = RUNTIME / "evidence/CROSS_EVALUATOR_EQUIVALENCE.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(evidence_source, target)
    validated = ROOT / "validation/SCORER_RUNTIME.lock.json"
    # Only reached on the one platform whose runtime lock was validated; asserted again so a future
    # edit to EQUIVALENCE_EVIDENCE cannot reintroduce installing this lock on another platform.
    if key != REQUIRED_PLATFORM:
        raise PrepareError(f"refusing to install the {REQUIRED_PLATFORM[0]} runtime lock on {key[0]}/{key[1]}")
    if json.loads(validated.read_text())["environment"] != observed:
        raise PrepareError(
            "the validated runtime lock describes a different environment than the one just built:\n"
            f"  built:     {json.dumps(observed, sort_keys=True)}\n"
            f"  validated: {json.dumps(json.loads(validated.read_text())['environment'], sort_keys=True)}"
        )
    shutil.copyfile(validated, RUNTIME / "SCORER_RUNTIME.lock.json")
    final = sha256(RUNTIME / "SCORER_RUNTIME.lock.json")
    if final != SCORER_RUNTIME_LOCK_SHA256:
        raise PrepareError("installed scorer runtime lock does not match the pin in FINALIST.lock.json")
    log(f"scorer runtime validated for {key[0]}/{key[1]}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--keep-downloads", action="store_true",
                        help="retain the ~550 MB download cache under .finalist-downloads/")
    parser.add_argument("--assets-only", action="store_true",
                        help="retrieve and verify assets but do not build the scorer runtime")
    args = parser.parse_args()
    try:
        sources = json.loads((ROOT / "ASSET_SOURCES.json").read_text())
        files = load_manifest()
        log(f"host: {platform.system()}/{platform.machine()}  python {platform.python_version()}")
        stage_generator(sources)
        stage_evaluator_assets(files)
        if args.assets_only:
            log("assets retrieved and verified; scorer runtime not built (--assets-only)")
            return
        stage_runtime()
    except PrepareError as error:
        print(f"\n[prepare] FAILED\n{error}\n", file=sys.stderr)
        raise SystemExit(2)
    if not args.keep_downloads and DOWNLOADS.exists():
        shutil.rmtree(DOWNLOADS)
        log("removed the download cache (--keep-downloads retains it)")
    print(json.dumps({
        "status": "PREPARED",
        "generator_checkpoint": str((ROOT / "assets/prompt_model/pytorch_model.bin").relative_to(ROOT)),
        "scorer_runtime": str(RUNTIME.relative_to(ROOT)),
        "scorer_runtime_lock_sha256": sha256(RUNTIME / "SCORER_RUNTIME.lock.json"),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
