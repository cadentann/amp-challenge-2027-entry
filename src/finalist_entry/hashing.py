from __future__ import annotations

import hashlib
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_file(path: Path, expected_sha256: str, *, label: str) -> Path:
    path = Path(path).resolve()
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    observed = sha256(path)
    if observed != expected_sha256:
        raise RuntimeError(f"{label} SHA-256 mismatch: {observed} != {expected_sha256}")
    return path

