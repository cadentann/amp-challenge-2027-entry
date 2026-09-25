from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .hashing import require_file, sha256


LOCK_NAME = "FINALIST.lock.json"
REQUIRED_KEYS = {
    "schema_version", "status", "arm", "selector", "generation_seed",
    "batch_size", "library_size", "top_size", "raw_ceiling",
    "device_policy", "selection_universe", "selection_pool_size", "pool_seed",
    "top_eligibility_order", "reference_path", "reference_sha256",
    "model_dir", "checkpoint_sha256", "config_sha256", "vocab_path",
    "vocab_sha256", "anchor_path", "anchor_sha256", "scoring_adapter_path",
    "scoring_adapter_sha256", "scoring_runtime_root", "scientific_authorization_path",
    "scoring_runtime_lock_sha256",
    "scientific_authorization_sha256", "torch_version_prefix",
    "transformers_version", "numpy_version", "python_version_prefix",
}


@dataclass(frozen=True)
class FinalistLock:
    path: Path
    data: dict[str, Any]

    def path_value(self, key: str) -> Path:
        value = self.data[key]
        if not isinstance(value, str) or not value:
            raise ValueError(f"{key} must be a nonempty path string")
        path = Path(value)
        if not path.is_absolute():
            path = self.path.parent / path
        return path.resolve()

    @property
    def sha256(self) -> str:
        return sha256(self.path)


def _integer(value: Any, key: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{key} must be an integer")
    return value


def load_finalist_lock(project_root: Path) -> FinalistLock:
    path = (Path(project_root) / LOCK_NAME).resolve()
    if not path.is_file():
        raise RuntimeError(
            f"prospective entry is locked: {LOCK_NAME} is absent; "
            "scientific promotion and final settings have not been authorized"
        )
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("FINALIST lock must be a JSON object")
    missing = sorted(REQUIRED_KEYS - set(data))
    extra = sorted(set(data) - REQUIRED_KEYS)
    if missing or extra:
        raise ValueError(f"FINALIST lock schema mismatch: missing={missing}, extra={extra}")
    if data["schema_version"] != 1 or data["status"] != "FINAL_AUTHORIZED":
        raise ValueError("FINALIST lock is not a final authorization")
    if data["arm"] != "AMP-Prompt":
        raise ValueError("this candidate supports only the authentic AMP-Prompt arm")
    if data["selector"] != "CONSENSUS_FIXED":
        raise ValueError("this candidate supports only the frozen CONSENSUS_FIXED selector")
    _integer(data["generation_seed"], "generation_seed")
    if _integer(data["batch_size"], "batch_size") != 128:
        raise ValueError("authentic AMP-Prompt batch_size must be 128")
    if _integer(data["library_size"], "library_size") != 50_000:
        raise ValueError("official library_size must be 50000")
    if _integer(data["top_size"], "top_size") != 100:
        raise ValueError("official top_size must be 100")
    raw_ceiling = _integer(data["raw_ceiling"], "raw_ceiling")
    if raw_ceiling < 50_000 or raw_ceiling % 128:
        raise ValueError("raw_ceiling must be a multiple of 128 and at least 50000")
    if data["device_policy"] not in {"private_cuda_required", "auto_prefer_cuda", "cpu_required"}:
        raise ValueError("unsupported device_policy")
    universe = data["selection_universe"]
    if universe not in {"full_library", "score_blind_subset"}:
        raise ValueError("selection_universe must be prospectively frozen")
    if data["top_eligibility_order"] != "top_e_then_hash":
        raise ValueError("this adapter implements the frozen top-E-then-hash procedure only")
    if universe == "full_library":
        if data["selection_pool_size"] is not None or data["pool_seed"] is not None:
            raise ValueError("full_library must have null pool size and seed")
    else:
        size = _integer(data["selection_pool_size"], "selection_pool_size")
        seed = _integer(data["pool_seed"], "pool_seed")
        if not 100 <= size <= 50_000:
            raise ValueError("selection_pool_size must be within [100, 50000]")
        del seed
    for key in (
        "checkpoint_sha256", "config_sha256", "vocab_sha256", "reference_sha256",
        "anchor_sha256", "scoring_adapter_sha256", "scientific_authorization_sha256",
        "scoring_runtime_lock_sha256",
    ):
        value = data[key]
        if not isinstance(value, str) or len(value) != 64:
            raise ValueError(f"{key} must be an explicit SHA-256")
    lock = FinalistLock(path=path, data=data)
    require_file(lock.path_value("reference_path"), data["reference_sha256"], label="reference")
    require_file(lock.path_value("vocab_path"), data["vocab_sha256"], label="vocabulary")
    require_file(lock.path_value("anchor_path"), data["anchor_sha256"], label="frozen anchor")
    require_file(
        lock.path_value("scoring_adapter_path"), data["scoring_adapter_sha256"],
        label="scoring adapter",
    )
    scoring_runtime_root = lock.path_value("scoring_runtime_root")
    require_file(
        scoring_runtime_root / "SCORER_RUNTIME.lock.json",
        data["scoring_runtime_lock_sha256"],
        label="scoring runtime lock",
    )
    require_file(
        lock.path_value("scientific_authorization_path"),
        data["scientific_authorization_sha256"], label="scientific authorization",
    )
    model_dir = lock.path_value("model_dir")
    require_file(model_dir / "pytorch_model.bin", data["checkpoint_sha256"], label="checkpoint")
    require_file(model_dir / "config.json", data["config_sha256"], label="model config")
    return lock
