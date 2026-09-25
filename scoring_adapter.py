#!/usr/bin/env python3
"""Generator-process bridge to the separately locked Python 3.10 scorer."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORKER = HERE / "vendor/scorer_subproject/scorer_worker.py"
PORTABILITY = HERE / "vendor/ania_portability"
WORKER_SHA256 = "ab5758c8f1121cd2a75c1f9824df998d9a22fb584c57b5acfacc59f20905c67e"
PORTABILITY_MANIFEST_SHA256 = "886c904dbc5fdd3883d91deed72893321fd38239bb7106123f47c1d059f81d60"
RUNTIME_MANIFEST_SHA256 = "ecacbe1ed1fa840ecd9c684ccf781e808ba33a3f97420384473e3d3115e77fa7"
SCORER_UV_LOCK_SHA256 = "f7c3822d3b01a79199139c2c5c4b1ed3c7b74b32ea026c5ebf10bb354646d20d"
EXPECTED_ENVIRONMENT_BASE = {
    "python": "3.10.20",
    "torch_package": "2.5.1",
    "numpy": "2.2.6",
    "pandas": "2.3.3",
}
APPROVED_TORCH_WHEELS = {
    ("Darwin", "arm64"): "23d062bf70776a3d04dbe74db950db2a5245e1ba4f27208a87f0d743b0d06e86",
    ("Linux", "x86_64"): "71328e1bbe39d213b8721678f9dcac30dfc452a46d586f1d514a6aa0a99d4744",
}
APPROVED_TORCH_RUNTIME = {
    ("Darwin", "arm64"): ("2.5.1", None),
    ("Linux", "x86_64"): ("2.5.1+cu124", "12.4"),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _inside(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("runtime relative path must be nonempty")
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError("runtime path escapes its root")
    # Preserve a venv's executable symlink when launching it. Resolving that
    # symlink would invoke the base interpreter outside the venv and lose its
    # locked site-packages. The lexical path remains rooted and the runtime
    # lock, environment probe, asset hashes and equivalence receipt are pinned.
    return root / relative_path


def _load_runtime(runtime_root: Path):
    root = Path(runtime_root).resolve()
    lock_path = root / "SCORER_RUNTIME.lock.json"
    lock = json.loads(lock_path.read_text())
    required = {
        "schema_version", "status", "python_relative_path", "assets_relative_path",
        "runtime_manifest_sha256", "worker_sha256", "portability_manifest_sha256",
        "environment", "score_timeout_seconds", "equivalence_evidence_relative_path",
        "equivalence_evidence_sha256", "scorer_uv_lock_sha256", "torch_wheel_sha256",
        "platform_scope",
    }
    if set(lock) != required or lock["schema_version"] != "finalist-scorer-runtime-v1":
        raise RuntimeError("scorer runtime lock schema mismatch")
    if lock["status"] != "READY_VALIDATED":
        raise RuntimeError("scorer runtime is pending cross-evaluator validation")
    if lock["runtime_manifest_sha256"] != RUNTIME_MANIFEST_SHA256:
        raise RuntimeError("scorer runtime manifest pin changed")
    if lock["scorer_uv_lock_sha256"] != SCORER_UV_LOCK_SHA256:
        raise RuntimeError("scorer uv lock pin changed")
    if lock["worker_sha256"] != WORKER_SHA256 or _sha256(WORKER) != WORKER_SHA256:
        raise RuntimeError("scorer worker bytes changed")
    port_manifest = PORTABILITY / "PORTABILITY_MANIFEST.json"
    if (
        lock["portability_manifest_sha256"] != PORTABILITY_MANIFEST_SHA256
        or _sha256(port_manifest) != PORTABILITY_MANIFEST_SHA256
    ):
        raise RuntimeError("ANIA portability manifest changed")
    environment = lock["environment"]
    environment_keys = {
        "python", "torch_package", "torch_runtime", "torch_cuda_version", "numpy", "pandas",
        "platform_system", "platform_machine",
    }
    if not isinstance(environment, dict) or set(environment) != environment_keys:
        raise RuntimeError("scorer environment lock schema changed")
    if any(environment[key] != value for key, value in EXPECTED_ENVIRONMENT_BASE.items()):
        raise RuntimeError("scorer base environment pin changed")
    if not isinstance(environment["torch_runtime"], str) or not environment["torch_runtime"]:
        raise RuntimeError("exact Torch runtime build is unpinned")
    platform_key = (environment["platform_system"], environment["platform_machine"])
    if lock["torch_wheel_sha256"] != APPROVED_TORCH_WHEELS.get(platform_key):
        raise RuntimeError("Torch wheel is not the exact approved platform build")
    if (environment["torch_runtime"], environment["torch_cuda_version"]) != APPROVED_TORCH_RUNTIME.get(platform_key):
        raise RuntimeError("Torch runtime/CUDA build differs from the explicit platform pin")
    expected_scope = {
        ("Darwin", "arm64"): "LOCAL_MACOS_ARM64",
        ("Linux", "x86_64"): "LINUX_X86_64",
    }.get(platform_key)
    if lock["platform_scope"] != expected_scope:
        raise RuntimeError("scorer platform scope differs from its environment")
    timeout = lock["score_timeout_seconds"]
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout < 60:
        raise RuntimeError("invalid scorer timeout")
    python = _inside(root, lock["python_relative_path"])
    assets = _inside(root, lock["assets_relative_path"])
    evidence = _inside(root, lock["equivalence_evidence_relative_path"])
    if not python.is_file() or not os.access(python, os.X_OK):
        raise RuntimeError("locked scorer Python is missing or not executable")
    if _sha256(assets / "RUNTIME_MANIFEST.json") != RUNTIME_MANIFEST_SHA256:
        raise RuntimeError("evaluator asset manifest changed")
    if _sha256(evidence) != lock["equivalence_evidence_sha256"]:
        raise RuntimeError("combined scorer equivalence evidence changed")
    result = json.loads(evidence.read_text())
    required_passes = (
        "apex_member_arrays_exact", "apex_ensemble_exact", "ania_arrays_exact",
        "joined_rows_exact", "stable_order",
    )
    if result.get("status") != "PASS" or not all(result.get(key) is True for key in required_passes):
        raise RuntimeError("combined scorer equivalence has not passed")
    if result.get("platform_scope") != lock["platform_scope"] or result.get("environment") != environment:
        raise RuntimeError("combined scorer evidence belongs to another platform or environment")
    return root, lock, python, assets


def _environment() -> dict[str, str]:
    environment = dict(os.environ)
    environment["PYTHONHASHSEED"] = "0"
    environment["CUDA_VISIBLE_DEVICES"] = ""
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment.pop("VIRTUAL_ENV", None)
    return environment


def _command(
    python: Path, assets: Path, runtime_lock: Path, mode: str, output: Path,
    input_path: Path | None = None,
):
    command = [
        str(python), str(WORKER), mode,
        "--runtime-assets", str(assets),
        "--portability-dir", str(PORTABILITY),
        "--runtime-lock", str(runtime_lock),
        "--output", str(output),
    ]
    if input_path is not None:
        command.extend(("--input", str(input_path)))
    return command


def probe(runtime_root: Path) -> dict:
    root, lock, python, assets = _load_runtime(runtime_root)
    with tempfile.TemporaryDirectory(prefix="finalist-scorer-probe-") as temporary:
        output = Path(temporary) / "probe.json"
        process = subprocess.run(
            _command(python, assets, root / "SCORER_RUNTIME.lock.json", "probe", output),
            env=_environment(), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=min(lock["score_timeout_seconds"], 300), check=False,
        )
        if process.returncode != 0:
            raise RuntimeError(f"scorer probe failed with exit {process.returncode}: {process.stderr[-2000:]}")
        result = json.loads(output.read_text())
    if result.get("status") != "READY_NO_INFERENCE" or result.get("r_dependency") is not False:
        raise RuntimeError("isolated scorer returned the wrong no-inference contract")
    result["runtime_lock_sha256"] = _sha256(root / "SCORER_RUNTIME.lock.json")
    return result


def score_rows(sequences, runtime_root: Path, *, evidence_dir: Path) -> dict:
    root, lock, python, assets = _load_runtime(runtime_root)
    sequences = list(sequences)
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=False)
    input_path = evidence_dir / "sequences.json"
    output_path = evidence_dir / "scores.json"
    input_path.write_text(json.dumps(sequences, separators=(",", ":")) + "\n")
    with input_path.open("rb") as handle:
        os.fsync(handle.fileno())
    process = subprocess.run(
        _command(
            python, assets, root / "SCORER_RUNTIME.lock.json", "score", output_path, input_path
        ),
        env=_environment(), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=lock["score_timeout_seconds"], check=False,
    )
    (evidence_dir / "stdout.txt").write_text(process.stdout)
    (evidence_dir / "stderr.txt").write_text(process.stderr)
    if process.returncode != 0:
        failure = {
            "status": "FAILED", "returncode": process.returncode,
            "input_sha256": _sha256(input_path),
            "runtime_lock_sha256": _sha256(root / "SCORER_RUNTIME.lock.json"),
        }
        (evidence_dir / "FAILED.json").write_text(json.dumps(failure, indent=2, sort_keys=True) + "\n")
        raise RuntimeError(f"isolated scorer failed with exit {process.returncode}")
    payload = json.loads(output_path.read_text())
    arrays_path = evidence_dir / payload.get("array_artifact", "")
    if not arrays_path.is_file():
        raise RuntimeError("isolated scorer did not preserve prediction arrays")
    (evidence_dir / "COMPLETE.json").write_text(json.dumps({
        "status": "COMPLETE",
        "rows": len(payload.get("rows", [])),
        "input_sha256": _sha256(input_path),
        "output_sha256": _sha256(output_path),
        "prediction_arrays_sha256": _sha256(arrays_path),
        "array_contract": payload.get("array_contract"),
        "apex_member_order": payload.get("apex_member_order"),
        "runtime_lock_sha256": _sha256(root / "SCORER_RUNTIME.lock.json"),
    }, indent=2, sort_keys=True) + "\n")
    return payload
