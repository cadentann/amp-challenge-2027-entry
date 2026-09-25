#!/usr/bin/env python3
"""Fail-closed integration surface for the separately verified ANIA Python port."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import sys
from pathlib import Path
from typing import Sequence

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from ania_encoder import (
    ALPHABET_SET,
    PYTHON_HASH_PROBE,
    PYTHON_HASH_SEED_0_VALUE,
    encode_ania_features,
)


EXPECTED_RUNTIME_MANIFEST_SHA256 = "ecacbe1ed1fa840ecd9c684ccf781e808ba33a3f97420384473e3d3115e77fa7"
EXPECTED_ENVIRONMENT = {
    "python": "3.10.20",
    "torch": "2.5.1",
    "numpy": "2.2.6",
    "pandas": "2.3.3",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _import_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def probe(runtime_root: Path, require_hash_seed: bool = True) -> dict:
    """Check the no-R/no-inference portability contract and pinned dependencies."""
    import pandas as pd
    import torch

    runtime_root = Path(runtime_root).resolve()
    manifest_path = HERE / "PORTABILITY_MANIFEST.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    checks = {
        "runtime_manifest": _sha256(runtime_root / "RUNTIME_MANIFEST.json")
        == EXPECTED_RUNTIME_MANIFEST_SHA256,
        "python": platform.python_version() == EXPECTED_ENVIRONMENT["python"],
        "numpy": np.__version__ == EXPECTED_ENVIRONMENT["numpy"],
        "pandas": pd.__version__ == EXPECTED_ENVIRONMENT["pandas"],
        # repair2: compare the PEP 440 public version only. torch.__version__ carries a local
        # version label on every Linux wheel (+cu124 on the default PyPI wheel, +cpu on the CPU
        # index) and none on macOS, where EXPECTED_ENVIRONMENT was recorded. SCORER_RUNTIME.lock
        # already distinguishes torch_package "2.5.1" from torch_runtime "2.5.1+cu124"; this check
        # is the package-level one. Same relaxation repair1 applied to the uv version assertion.
        "torch": str(torch.__version__).split("+", 1)[0] == EXPECTED_ENVIRONMENT["torch"],
        "r_dependency_absent": manifest.get("r_dependency") is False,
        "port_files": all(_sha256(HERE / rel) == digest for rel, digest in manifest["port_files"].items()),
        "source_files": all(_sha256(runtime_root / rel) == digest for rel, digest in manifest["runtime_source_pins"].items()),
    }
    evidence = manifest["equivalence_evidence"]
    evidence_path = HERE / evidence["path"]
    checks["equivalence_evidence_hash"] = _sha256(evidence_path) == evidence["sha256"]
    checks["equivalence_evidence_pass"] = json.loads(evidence_path.read_text())["status"] == "PASS"
    hash_seed_ok = (
        os.environ.get("PYTHONHASHSEED") == "0"
        and hash(PYTHON_HASH_PROBE) == PYTHON_HASH_SEED_0_VALUE
    )
    checks["python_hash_seed_0"] = hash_seed_ok
    if require_hash_seed and not hash_seed_ok:
        checks["status"] = "FAIL"
        checks["first_failure"] = "python_hash_seed_0"
        return checks
    failed = next((key for key, value in checks.items() if value is not True), None)
    checks["status"] = "PASS" if failed is None else "FAIL"
    checks["first_failure"] = failed
    return checks


def _validate_sequences(sequences: Sequence[str]) -> list[str]:
    copied = list(sequences)
    for index, sequence in enumerate(copied):
        if not isinstance(sequence, str) or not 8 <= len(sequence) <= 50 or set(sequence) - ALPHABET_SET:
            raise ValueError(f"invalid sequence at index {index}")
    if len(set(copied)) != len(copied):
        raise ValueError("duplicate sequence")
    return copied


def predict_ania_log10(
    sequences: Sequence[str], runtime_root: Path, batch_size: int = 32
) -> np.ndarray:
    """Return exact float32 ANIA columns in frozen EC, PA, SA order."""
    runtime_root = Path(runtime_root).resolve()
    status = probe(runtime_root)
    if status["status"] != "PASS":
        raise RuntimeError(f"portability probe failed: {status['first_failure']}")
    sequences = _validate_sequences(sequences)
    if batch_size != 32:
        raise ValueError("batch_size must remain the frozen value 32")

    import pandas as pd
    import torch

    # repair3: same PEP 440 public-version comparison as the probe guard above. This second
    # strict check sits inside predict_ania_log10 and was missed by repair2; it blocks Linux
    # for the identical reason. Computation below is untouched.
    if str(torch.__version__).split("+", 1)[0] != EXPECTED_ENVIRONMENT["torch"]:
        raise RuntimeError("torch version mismatch")
    if pd.__version__ != EXPECTED_ENVIRONMENT["pandas"]:
        raise RuntimeError("pandas version mismatch")
    if torch.get_num_threads() != 2:
        torch.set_num_threads(2)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)

    scorer = _import_file("ania_portability_frozen_scorer", runtime_root / "score_batch.py")
    _, config = scorer.verify_runtime()
    if config["batch_size"] != batch_size or config["threads"] != 2:
        raise RuntimeError("frozen runtime execution settings changed")
    encoded, _, _ = encode_ania_features(
        sequences,
        runtime_root / "assets/ania/src/features/cgr_encoding.py",
        runtime_root / "assets/ania/configs/AAindex_properties.csv",
        properties=config["ania_properties"],
    )
    tensor = torch.tensor(encoded)
    predictions = []
    for item in config["ania_weights"]:
        model = scorer.load_ania(runtime_root / item["path"], torch)
        with torch.inference_mode():
            values = np.concatenate(
                [model(part).numpy().reshape(-1) for part in tensor.split(batch_size)]
            )
        predictions.append(values)
    output = np.stack(predictions).T
    if output.shape != (len(sequences), 3) or output.dtype != np.float32 or not np.isfinite(output).all():
        raise AssertionError((output.shape, output.dtype))
    return output


def build_score_rows(
    sequences: Sequence[str], apex_um: np.ndarray, ania_log10_um: np.ndarray
) -> list[dict]:
    """Build the exact score schema consumed by ``common_core.join_scores``."""
    sequences = _validate_sequences(sequences)
    apex_um = np.asarray(apex_um)
    ania_log10_um = np.asarray(ania_log10_um)
    if apex_um.shape != (len(sequences), 11) or not np.isfinite(apex_um).all() or not (apex_um > 0).all():
        raise ValueError("apex_um must be a finite positive (n,11) array")
    if ania_log10_um.shape != (len(sequences), 3) or not np.isfinite(ania_log10_um).all():
        raise ValueError("ania_log10_um must be a finite (n,3) array")
    return [
        {
            "sequence": sequence,
            "apex_um": [float(value) for value in apex_um[index]],
            "ania_log10_um": [float(value) for value in ania_log10_um[index]],
        }
        for index, sequence in enumerate(sequences)
    ]
