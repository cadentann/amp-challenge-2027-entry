#!/usr/bin/env python3
"""Prepare, but do not scientifically authorize, the isolated scorer runtime."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "vendor/scorer_subproject"
EXPECTED_RUNTIME = "ecacbe1ed1fa840ecd9c684ccf781e808ba33a3f97420384473e3d3115e77fa7"
WORKER_SHA = "ab5758c8f1121cd2a75c1f9824df998d9a22fb584c57b5acfacc59f20905c67e"
PORT_SHA = "886c904dbc5fdd3883d91deed72893321fd38239bb7106123f47c1d059f81d60"
SCORER_UV_LOCK_SHA = "f7c3822d3b01a79199139c2c5c4b1ed3c7b74b32ea026c5ebf10bb354646d20d"
TORCH_WHEELS = {
    ("Darwin", "arm64"): "23d062bf70776a3d04dbe74db950db2a5245e1ba4f27208a87f0d743b0d06e86",
    ("Linux", "x86_64"): "71328e1bbe39d213b8721678f9dcac30dfc452a46d586f1d514a6aa0a99d4744",
}
TORCH_RUNTIME = {
    ("Darwin", "arm64"): ("2.5.1", None),
    ("Linux", "x86_64"): ("2.5.1+cu124", "12.4"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_assets(source: Path) -> None:
    manifest_path = source / "RUNTIME_MANIFEST.json"
    if sha256(manifest_path) != EXPECTED_RUNTIME:
        raise RuntimeError("source evaluator manifest SHA-256 mismatch")
    manifest = json.loads(manifest_path.read_text())
    for item in manifest["files"]:
        path = source / item["path"]
        if not path.is_file() or path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
            raise RuntimeError(f"source evaluator asset changed: {item['path']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets-source", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--score-timeout-seconds", type=int, required=True)
    args = parser.parse_args()
    source = args.assets_source.resolve()
    target = args.target.resolve()
    if target.exists():
        raise FileExistsError(target)
    if args.score_timeout_seconds < 60:
        raise ValueError("score timeout must be at least 60 seconds")
    verify_assets(source)
    target.mkdir(parents=True)
    try:
        shutil.copytree(source, target / "assets")
        verify_assets(target / "assets")
        environment = dict(os.environ)
        environment["UV_PROJECT_ENVIRONMENT"] = str(target / ".venv")
        subprocess.run(
            ["uv", "sync", "--project", str(PROJECT), "--frozen", "--python", "3.10.20"],
            env=environment,
            check=True,
        )
        inspection_path = target / "ENVIRONMENT_INSPECTION.json"
        inspect_environment = dict(environment)
        inspect_environment["PYTHONHASHSEED"] = "0"
        inspect_environment["CUDA_VISIBLE_DEVICES"] = ""
        subprocess.run(
            [
                str(target / ".venv/bin/python"), str(PROJECT / "scorer_worker.py"),
                "inspect", "--output", str(inspection_path),
            ],
            env=inspect_environment,
            check=True,
        )
        observed = json.loads(inspection_path.read_text())["environment"]
        platform_key = (observed["platform_system"], observed["platform_machine"])
        wheel = TORCH_WHEELS.get(platform_key)
        if wheel is None:
            raise RuntimeError(f"unsupported scorer platform: {platform_key}")
        observed_build = (observed["torch_runtime"], observed["torch_cuda_version"])
        if observed_build != TORCH_RUNTIME[platform_key]:
            raise RuntimeError(
                f"Torch runtime/CUDA build differs from explicit pin: {observed_build}"
            )
        lock = {
            "assets_relative_path": "assets",
            "environment": observed,
            "equivalence_evidence_relative_path": None,
            "equivalence_evidence_sha256": None,
            "portability_manifest_sha256": PORT_SHA,
            "platform_scope": f"UNVALIDATED_{platform_key[0].upper()}_{platform_key[1].upper()}",
            "python_relative_path": ".venv/bin/python",
            "runtime_manifest_sha256": EXPECTED_RUNTIME,
            "scorer_uv_lock_sha256": SCORER_UV_LOCK_SHA,
            "schema_version": "finalist-scorer-runtime-v1",
            "score_timeout_seconds": args.score_timeout_seconds,
            "status": "PENDING_CROSS_EVALUATOR_EQUIVALENCE",
            "torch_wheel_sha256": wheel,
            "worker_sha256": WORKER_SHA,
        }
        (target / "SCORER_RUNTIME.lock.json").write_text(
            json.dumps(lock, indent=2, sort_keys=True) + "\n"
        )
        print(json.dumps({
            "status": lock["status"],
            "target": str(target),
            "runtime_lock_sha256": sha256(target / "SCORER_RUNTIME.lock.json"),
        }, sort_keys=True))
    except BaseException:
        (target / "BOOTSTRAP_FAILED").write_text("incomplete scorer bootstrap\n")
        raise


if __name__ == "__main__":
    main()
