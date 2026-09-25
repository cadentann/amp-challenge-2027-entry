#!/usr/bin/env python3
"""Isolated Python 3.10 APEX+portable-ANIA worker; never import in generator process."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import sys
from pathlib import Path


EXPECTED = {
    "python": "3.10.20",
    "torch_package": "2.5.1",
    "numpy": "2.2.6",
    "pandas": "2.3.3",
    "runtime_manifest_sha256": "ecacbe1ed1fa840ecd9c684ccf781e808ba33a3f97420384473e3d3115e77fa7",
}
APEX_HEADS = (
    "A. baumannii ATCC 19606", "E. coli ATCC 11775", "E. coli AIC221",
    "E. coli AIC222", "K. pneumoniae ATCC 13883", "P. aeruginosa PA01",
    "P. aeruginosa PA14", "S. aureus ATCC 12600",
    "S. aureus (ATCC BAA-1556) - MRSA",
    "vancomycin-resistant E. faecalis ATCC 700802",
    "vancomycin-resistant E. faecium ATCC 700221",
)
ANIA_HEADS = ("EC", "PA", "SA")


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_surfaces(runtime_assets: Path, portability_dir: Path):
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("worker requires PYTHONHASHSEED=0 from process launch")
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise RuntimeError("scorer worker requires CUDA_VISIBLE_DEVICES='' isolation")
    if sha256(runtime_assets / "RUNTIME_MANIFEST.json") != EXPECTED["runtime_manifest_sha256"]:
        raise RuntimeError("runtime manifest SHA-256 mismatch")
    scorer = load_module("finalist_current_score_batch", runtime_assets / "score_batch.py")
    portability = load_module("finalist_ania_portability", portability_dir / "integration_adapter.py")
    return scorer, portability


def observed_environment() -> dict:
    import numpy as np
    import pandas as pd
    import torch

    return {
        "python": platform.python_version(),
        "torch_package": "2.5.1",
        "torch_runtime": str(torch.__version__),
        "torch_cuda_version": torch.version.cuda,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
    }


def require_environment(expected: dict) -> dict:
    observed = observed_environment()
    if observed != expected:
        raise RuntimeError(f"scorer environment mismatch: observed={observed}, expected={expected}")
    if observed["python"] != EXPECTED["python"]:
        raise RuntimeError("scorer Python changed")
    if observed["torch_package"] != EXPECTED["torch_package"]:
        raise RuntimeError("scorer Torch package pin changed")
    if observed["numpy"] != EXPECTED["numpy"] or observed["pandas"] != EXPECTED["pandas"]:
        raise RuntimeError("scorer numerical package pin changed")
    return observed


def probe(runtime_assets: Path, portability_dir: Path, expected_environment: dict) -> dict:
    environment = require_environment(expected_environment)

    scorer, portability = load_surfaces(runtime_assets, portability_dir)
    scorer.verify_runtime()
    port = portability.probe(runtime_assets, require_hash_seed=True)
    if port.get("status") != "PASS":
        raise RuntimeError(f"ANIA portability probe failed: {port}")
    return {
        "status": "READY_NO_INFERENCE",
        "r_dependency": False,
        "environment": environment,
        "runtime_manifest_sha256": EXPECTED["runtime_manifest_sha256"],
        "ania_portability": port,
    }


def validate_sequences(payload) -> list[str]:
    alphabet = set("ACDEFGHIKLMNPQRSTVWY")
    if not isinstance(payload, list) or not payload:
        raise ValueError("input must be a nonempty sequence list")
    if len(set(payload)) != len(payload):
        raise ValueError("input sequences must be unique")
    for index, sequence in enumerate(payload):
        if not isinstance(sequence, str) or not 8 <= len(sequence) <= 50 or set(sequence) - alphabet:
            raise ValueError(f"invalid sequence at index {index}")
    return payload


def predict_apex(sequences: list[str], runtime_assets: Path, scorer, config):
    import numpy as np
    import torch

    torch.set_num_threads(config["threads"])
    torch.set_num_interop_threads(1)
    torch.manual_seed(config["seed"])
    torch.use_deterministic_algorithms(True)
    sys.path.insert(0, str(runtime_assets / "assets/apex"))
    scorer.import_file("APEX_models", runtime_assets / "assets/apex/APEX_models.py")
    helpers = scorer.import_file("finalist_apex_utils", runtime_assets / "assets/apex/utils.py")
    vocabulary, _ = helpers.make_vocab()
    encoded = torch.LongTensor(helpers.onehot_encoding(np.array(sequences), 52, vocabulary))
    members = []
    for item in config["apex_weights"]:
        model = torch.load(runtime_assets / item["path"], map_location="cpu", weights_only=False).cpu().eval()
        if any(parameter.device.type != "cpu" for parameter in model.parameters()):
            raise RuntimeError("APEX model escaped CPU isolation")
        with torch.inference_mode():
            raw = np.concatenate([model(part).numpy() for part in encoded.split(config["batch_size"])])
            repeat = model(encoded[: min(config["batch_size"], len(sequences))]).numpy()
        if not np.array_equal(raw[: len(repeat)], repeat):
            raise RuntimeError("APEX same-batch repeat changed")
        values = 10 ** (6 - raw)
        if values.shape != (len(sequences), 11) or not np.isfinite(values).all() or not (values > 0).all():
            raise RuntimeError("APEX output contract failed")
        members.append(values)
        del model
    stacked = np.stack(members).astype(np.float32)
    mean = stacked.mean(axis=0)
    if mean.shape != (len(sequences), 11):
        raise RuntimeError("APEX ensemble shape changed")
    return stacked, mean


def score(
    sequences: list[str], runtime_assets: Path, portability_dir: Path,
    expected_environment: dict,
):
    require_environment(expected_environment)
    scorer, portability = load_surfaces(runtime_assets, portability_dir)
    _, config = scorer.verify_runtime()
    apex_members, apex = predict_apex(sequences, runtime_assets, scorer, config)
    ania = portability.predict_ania_log10(sequences, runtime_assets, batch_size=32)
    rows = portability.build_score_rows(sequences, apex, ania)
    if [row["sequence"] for row in rows] != sequences:
        raise RuntimeError("scorer changed sequence order")
    payload = {
        "schema_version": "frontier-scores-v1",
        "apex_heads": list(APEX_HEADS),
        "ania_heads": list(ANIA_HEADS),
        "apex_member_order": [item["name"] for item in config["apex_weights"]],
        "rows": rows,
    }
    return payload, apex_members, apex, ania


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("inspect", "probe", "score"))
    parser.add_argument("--runtime-assets", type=Path)
    parser.add_argument("--portability-dir", type=Path)
    parser.add_argument("--runtime-lock", type=Path)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.mode == "inspect":
        result = {"status": "INSPECT_ONLY_NO_INFERENCE", "environment": observed_environment()}
    else:
        if args.runtime_assets is None or args.portability_dir is None or args.runtime_lock is None:
            raise ValueError("probe/score requires runtime assets, portability directory and runtime lock")
        runtime_lock = json.loads(args.runtime_lock.read_text())
        expected_environment = runtime_lock["environment"]
        if args.mode == "probe":
            result = probe(args.runtime_assets, args.portability_dir, expected_environment)
        else:
            if args.input is None:
                raise ValueError("score mode requires --input")
            sequences = validate_sequences(json.loads(args.input.read_text()))
            result, apex_members, apex, ania = score(
                sequences, args.runtime_assets, args.portability_dir, expected_environment
            )
            import numpy as np
            arrays_path = args.output.with_name("prediction_arrays.npz")
            np.savez(
                arrays_path,
                apex_base_mic_uM=apex_members,
                apex_ensemble_mic_uM=apex,
                ania_log10_mic_uM=ania,
            )
            result["array_artifact"] = arrays_path.name
            result["array_contract"] = {
                name: {
                    "shape": list(array.shape),
                    "dtype": str(array.dtype),
                    "sha256_c_order": hashlib.sha256(array.tobytes(order="C")).hexdigest(),
                }
                for name, array in (
                    ("apex_base_mic_uM", apex_members),
                    ("apex_ensemble_mic_uM", apex),
                    ("ania_log10_mic_uM", ania),
                )
            }
    args.output.write_text(json.dumps(result, separators=(",", ":"), sort_keys=True) + "\n")
    print(json.dumps({"status": result.get("status", "COMPLETE"), "mode": args.mode}, sort_keys=True))


if __name__ == "__main__":
    main()
