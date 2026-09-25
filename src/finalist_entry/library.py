from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Callable, Protocol


CANONICAL = frozenset("ACDEFGHIKLMNPQRSTVWY")


class BatchSource(Protocol):
    batch_size: int

    def sample_batch(self) -> list[str]: ...


@dataclass(frozen=True)
class LibraryResult:
    sequences: list[str]
    raw_generated: int
    raw_examined: int
    rejection_counts: dict[str, int]


def rejection_reason(sequence: object, seen: set[str], exact_references: set[str]) -> str | None:
    if not isinstance(sequence, str) or not sequence:
        return "empty_or_non_string"
    # Generator output is judged exactly as emitted. There is no case conversion,
    # whitespace removal, clipping, boundary repair, or residue substitution here.
    if not 8 <= len(sequence) <= 50 or set(sequence) - CANONICAL:
        return "alphabet_or_length"
    if sequence in seen:
        return "duplicate"
    if sequence in exact_references:
        return "exact_reference"
    return None


def collect_library(
    source: BatchSource,
    exact_references: set[str],
    *,
    target: int,
    raw_ceiling: int,
    batch_observer: Callable[[int, list[dict]], None] | None = None,
) -> LibraryResult:
    if target < 1 or source.batch_size < 1:
        raise ValueError("target and batch_size must be positive")
    if raw_ceiling < target or raw_ceiling % source.batch_size:
        raise ValueError("raw_ceiling must cover target and contain complete batches")
    collected: list[str] = []
    seen: set[str] = set()
    rejected: Counter[str] = Counter()
    raw_generated = 0
    raw_examined = 0
    batch_index = 0
    while len(collected) < target:
        if raw_generated + source.batch_size > raw_ceiling:
            raise RuntimeError(
                f"raw ceiling exhausted: {len(collected)}/{target} accepted from "
                f"{raw_generated} generated"
            )
        batch = source.sample_batch()
        if len(batch) != source.batch_size:
            raise RuntimeError(f"generator returned {len(batch)} rows, expected {source.batch_size}")
        raw_generated += len(batch)
        ledger_rows: list[dict] = []
        for batch_offset, sequence in enumerate(batch):
            raw_index = raw_generated - len(batch) + batch_offset
            if len(collected) == target:
                ledger_rows.append({
                    "raw_index": raw_index,
                    "batch_index": batch_index,
                    "batch_offset": batch_offset,
                    "raw_sequence": sequence,
                    "accepted": False,
                    "accepted_index": None,
                    "disposition": "AFTER_TARGET_IN_FINAL_BATCH",
                    "rejection_reason": None,
                })
                continue
            raw_examined += 1
            reason = rejection_reason(sequence, seen, exact_references)
            if reason is not None:
                rejected[reason] += 1
                ledger_rows.append({
                    "raw_index": raw_index,
                    "batch_index": batch_index,
                    "batch_offset": batch_offset,
                    "raw_sequence": sequence,
                    "accepted": False,
                    "accepted_index": None,
                    "disposition": "REJECTED",
                    "rejection_reason": reason,
                })
                continue
            # `seen` is exactly the accepted library. Invalid/reference rows do
            # not change the rejection class of a later attempt.
            seen.add(sequence)
            accepted_index = len(collected)
            collected.append(sequence)
            ledger_rows.append({
                "raw_index": raw_index,
                "batch_index": batch_index,
                "batch_offset": batch_offset,
                "raw_sequence": sequence,
                "accepted": True,
                "accepted_index": accepted_index,
                "disposition": "ACCEPTED",
                "rejection_reason": None,
            })
        if len(ledger_rows) != source.batch_size:
            raise RuntimeError("raw ledger failed to account for a complete batch")
        if batch_observer is not None:
            batch_observer(batch_index, ledger_rows)
        batch_index += 1
    return LibraryResult(collected, raw_generated, raw_examined, dict(sorted(rejected.items())))
