from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from .fasta_io import write_fasta


def stage_outputs(stage: Path, library: list[str], top: list[str], receipt: dict) -> None:
    stage.mkdir(parents=True, exist_ok=False)
    write_fasta(library, stage / "library.fasta")
    write_fasta(top, stage / "top.fasta")
    (stage / "run.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


def publish_staged(stage: Path, output: Path, run_id: str) -> None:
    """Publish a fully validated directory with rollback if the directory swap fails."""
    stage, output = Path(stage), Path(output)
    if not all((stage / name).is_file() for name in ("library.fasta", "top.fasta", "run.json")):
        raise RuntimeError("refusing to publish an incomplete stage")
    output.parent.mkdir(parents=True, exist_ok=True)
    backup = output.with_name(f".{output.name}.previous-{run_id}")
    if backup.exists():
        raise FileExistsError(f"stale publication backup exists: {backup}")
    moved_old = False
    try:
        if output.exists():
            os.replace(output, backup)
            moved_old = True
        os.replace(stage, output)
    except BaseException:
        if moved_old and not output.exists() and backup.exists():
            os.replace(backup, output)
        raise
    if backup.exists():
        shutil.rmtree(backup)

