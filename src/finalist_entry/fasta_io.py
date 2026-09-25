from __future__ import annotations

from pathlib import Path


def read_fasta(path: Path) -> list[str]:
    sequences: list[str] = []
    header: str | None = None
    parts: list[str] = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                sequences.append("".join(parts).upper())
            header, parts = line[1:], []
        else:
            if header is None:
                raise ValueError("FASTA sequence appears before the first header")
            parts.append(line)
    if header is not None:
        sequences.append("".join(parts).upper())
    return sequences


def write_fasta(sequences: list[str], path: Path) -> None:
    with Path(path).open("x") as handle:
        for index, sequence in enumerate(sequences, start=1):
            handle.write(f">seq{index}\n{sequence}\n")

