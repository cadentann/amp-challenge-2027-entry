#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "PROVENANCE_MANIFEST.json").read_text())
for item in manifest["files"]:
    path = ROOT / item["path"]
    assert path.is_file(), item["path"]
    assert path.stat().st_size == item["bytes"], item["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], item["path"]
assert sum(item["bytes"] for item in manifest["files"]) == manifest["total_source_bytes"]
assert manifest["weights_included"] is False
assert manifest["scientific_promotion"] is False
print(json.dumps({"status": "PASS", "files": len(manifest["files"])}, sort_keys=True))
