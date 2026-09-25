from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from .pipeline import preflight, run


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PREPARE_SCRIPT = PROJECT_ROOT / "scripts/prepare_entry.py"


def _prerequisites_present() -> bool:
    """Cheap presence check for the assets a fresh clone does not carry."""
    checkpoint = PROJECT_ROOT / "assets/prompt_model/pytorch_model.bin"
    runtime_lock = PROJECT_ROOT / "runtime/scorer/SCORER_RUNTIME.lock.json"
    return checkpoint.is_file() and runtime_lock.is_file()


def ensure_prepared() -> None:
    """Retrieve and verify the pinned third-party assets if they are not here yet.

    The official validator runs `git clone`, `uv sync`, then
    `uv run --no-sync generate`, so there is no separate step in which an
    organizer could fetch model weights. This does it, and every retrieved byte
    is checked against a hash pinned in this repository before it is used.
    Set FINALIST_SKIP_PREPARE=1 to suppress it.
    """
    if _prerequisites_present() or os.environ.get("FINALIST_SKIP_PREPARE") == "1":
        return
    if not PREPARE_SCRIPT.is_file():
        raise RuntimeError(f"asset preparation script is missing: {PREPARE_SCRIPT}")
    print(
        "[generate] pinned assets are not present in this checkout; retrieving and "
        "verifying them now (about 550 MB, one time).",
        flush=True,
    )
    result = subprocess.run([sys.executable, str(PREPARE_SCRIPT)], cwd=PROJECT_ROOT)
    if result.returncode != 0:
        raise RuntimeError(
            "asset preparation failed; see the output above. The entry cannot run without "
            "its pinned assets. It can be retried directly with "
            "`uv run python scripts/prepare_entry.py`."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Prospective locked AMP-Prompt finalist entry")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument(
        "--no-prepare", action="store_true",
        help="fail instead of retrieving missing pinned assets",
    )
    args = parser.parse_args()
    if not args.no_prepare:
        ensure_prepared()
    if args.preflight_only:
        lock, scorer = preflight(PROJECT_ROOT)
        print(json.dumps({"status": "READY_NO_INFERENCE", "lock_sha256": lock.sha256, "scorer": scorer}, sort_keys=True))
        return
    result = run(PROJECT_ROOT)
    print(json.dumps({"status": result["status"], "run_id": result["run_id"]}, sort_keys=True))


if __name__ == "__main__":
    main()
