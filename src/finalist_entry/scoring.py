from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_adapter(path: Path):
    spec = importlib.util.spec_from_file_location("finalist_scoring_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load scoring adapter")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def probe_scoring(lock) -> dict:
    module = _load_adapter(lock.path_value("scoring_adapter_path"))
    if not hasattr(module, "probe") or not hasattr(module, "score_rows"):
        raise RuntimeError(
            "scoring adapter must expose probe(runtime_root) and "
            "score_rows(sequences, runtime_root, evidence_dir=...)"
        )
    result = module.probe(lock.path_value("scoring_runtime_root"))
    if not isinstance(result, dict) or result.get("status") != "READY_NO_INFERENCE":
        raise RuntimeError(f"scoring adapter is not ready: {result!r}")
    if result.get("r_dependency") is not False:
        raise RuntimeError("portable finalist scorer must not depend on an ambient R installation")
    return result


def score_pool(sequences: list[str], lock, evidence_dir: Path) -> dict:
    module = _load_adapter(lock.path_value("scoring_adapter_path"))
    payload = module.score_rows(
        sequences,
        lock.path_value("scoring_runtime_root"),
        evidence_dir=Path(evidence_dir),
    )
    if not isinstance(payload, dict) or payload.get("schema_version") != "frontier-scores-v1":
        raise RuntimeError("scoring adapter returned the wrong schema")
    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) != len(sequences):
        raise RuntimeError("scoring adapter row count mismatch")
    if [row.get("sequence") for row in rows] != sequences:
        raise RuntimeError("scoring adapter changed sequence order or identity")
    return payload
