#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "PROVENANCE_MANIFEST.json"
EXCLUDED_PARTS = {".venv", ".finalist-runs", "generate", "__pycache__", ".pytest_cache"}
EXCLUDED_NAMES = {"PROVENANCE_MANIFEST.json", "candidate-source.zip", ".DS_Store"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


files = []
for path in sorted(ROOT.rglob("*")):
    relative = path.relative_to(ROOT)
    if not path.is_file() or set(relative.parts) & EXCLUDED_PARTS or path.name in EXCLUDED_NAMES:
        continue
    files.append({
        "path": relative.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    })

payload = {
    "schema_version": "prospective-finalist-source-v1",
    "status": "ENGINEERING_CANDIDATE_LOCK_REQUIRED",
    "arm": "AMP-Prompt",
    "selector": "CONSENSUS_FIXED",
    "entry_point": "generate",
    "weights_included": False,
    "scientific_promotion": False,
    "files": files,
    "total_source_bytes": sum(item["bytes"] for item in files),
}
OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
print(json.dumps({"files": len(files), "bytes": payload["total_source_bytes"]}, sort_keys=True))
