from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from .hashing import require_file


FROZEN_COMMON_CORE_SHA256 = "963085ddb945b04173a6f81c2cab4f016bab366eb497584e1edddcf76f927679"


def load_common_core(project_root: Path):
    path = require_file(
        Path(project_root) / "vendor/frozen_selector/common_core.py",
        FROZEN_COMMON_CORE_SHA256,
        label="frozen common selector",
    )
    spec = importlib.util.spec_from_file_location("finalist_frozen_common_core", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen selector")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def qualify_and_choose_universe(
    sequences: list[str], references: list[str], lock_data: dict, project_root: Path
) -> dict:
    common = load_common_core(project_root)
    attempts = [{"raw_index": index, "raw_sequence": sequence} for index, sequence in enumerate(sequences)]
    rows = common.eligibility(attempts, common.ReferenceIndex(references))
    if any(not row["library_valid"] for row in rows):
        raise RuntimeError("completed library failed frozen eligibility replay")
    top_e = [row for row in rows if row["top_eligible"]]
    if lock_data["selection_universe"] == "full_library":
        selected = top_e
        target = None
    else:
        target = lock_data["selection_pool_size"]
        seed = lock_data["pool_seed"]
        selected = sorted(
            top_e, key=lambda row: (common.sample_key(seed, row["sequence"]), row["sequence"])
        )[:target]
        for row in selected:
            row["sample_hash"] = common.sample_key(seed, row["sequence"])
        if len(selected) != target:
            raise RuntimeError(f"top-E supply shortfall: {len(selected)}/{target}")
    return {
        "schema_version": "frontier-finalist-pool-v1",
        "seed": lock_data["pool_seed"],
        "target": target,
        "eligible_count": len(top_e),
        "selected_count": len(selected),
        "status": "COMPLETE",
        "rows": selected,
    }


def select_consensus(pool: dict, scores: dict, lock, project_root: Path) -> dict:
    common = load_common_core(project_root)
    anchor = json.loads(lock.path_value("anchor_path").read_text())
    rows = common.join_scores(pool, scores["rows"], scores["apex_heads"], scores["ania_heads"])
    results = common.run_selectors(rows, anchor=anchor, top_k=100, native=None, v3_runner=None)
    result = results["CONSENSUS_FIXED"]
    if result.get("status") != "COMPLETE" or result.get("selected_count") != 100:
        raise RuntimeError(f"frozen consensus selection incomplete: {result.get('status')}")
    return result

