from __future__ import annotations

import json
import os
from pathlib import Path


class RawLedger:
    """Append one complete generator batch and sync it before returning."""

    def __init__(self, path: Path, expected_batch_size: int):
        self.path = Path(path)
        self.expected_batch_size = expected_batch_size
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("x", encoding="utf-8")
        self.batches = 0
        self.rows = 0

    def record_batch(self, batch_index: int, rows: list[dict]) -> None:
        if batch_index != self.batches or len(rows) != self.expected_batch_size:
            raise RuntimeError("raw ledger batch continuity failure")
        for expected_offset, row in enumerate(rows):
            if row.get("batch_index") != batch_index or row.get("batch_offset") != expected_offset:
                raise RuntimeError("raw ledger row continuity failure")
            self._handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        self._handle.flush()
        os.fsync(self._handle.fileno())
        self.batches += 1
        self.rows += len(rows)

    def close(self) -> None:
        if not self._handle.closed:
            self._handle.flush()
            os.fsync(self._handle.fileno())
            self._handle.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def write_json_synced(path: Path, payload: dict) -> None:
    path = Path(path)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def sync_file(path: Path) -> None:
    with Path(path).open("rb") as handle:
        os.fsync(handle.fileno())
