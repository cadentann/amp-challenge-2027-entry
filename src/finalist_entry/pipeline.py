from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

from .amp_prompt import AmpPromptStream
from .cuda_gate import gate_generation_device
from .evidence import RawLedger, sync_file, write_json_synced
from .fasta_io import read_fasta
from .fasta_io import write_fasta
from .frozen_selector import qualify_and_choose_universe, select_consensus
from .hashing import sha256
from .library import collect_library
from .lock import load_finalist_lock
from .publish import publish_staged, stage_outputs
from .scoring import probe_scoring, score_pool


def preflight(project_root: Path, *, enforce_device_gate: bool = False):
    """Load the lock, check the generation device, then probe the scorer runtime.

    The device gate runs first and costs one short interpreter start, so a host whose CUDA path
    cannot execute fails in seconds instead of after the scorer probe and ~50 minutes of
    generation. ``enforce_device_gate`` is True only on the production path; ``--preflight-only``
    reports the verdict without raising, so it stays usable as a diagnostic anywhere.
    """
    lock = load_finalist_lock(project_root)
    device_gate = gate_generation_device(lock.data["device_policy"], enforce=enforce_device_gate)
    scorer = probe_scoring(lock)
    return lock, scorer, device_gate


def run(project_root: Path) -> dict:
    project_root = Path(project_root).resolve()
    lock, scorer_probe, device_gate = preflight(project_root, enforce_device_gate=True)
    run_id = uuid.uuid4().hex
    run_root = project_root / ".finalist-runs" / run_id
    evidence = run_root / "evidence"
    stage = run_root / "generate"
    run_root.mkdir(parents=True, exist_ok=False)
    evidence.mkdir(exist_ok=False)
    phase = "REFERENCE_LOAD"
    try:
        references = read_fasta(lock.path_value("reference_path"))
        exact_references = set(references)
        phase = "GENERATOR_LOAD"
        stream = AmpPromptStream(lock, project_root)
        phase = "GENERATION"
        with RawLedger(evidence / "raw_ledger.jsonl", stream.batch_size) as ledger:
            library = collect_library(
                stream,
                exact_references,
                target=50_000,
                raw_ceiling=lock.data["raw_ceiling"],
                batch_observer=ledger.record_batch,
            )
        if len(library.sequences) != 50_000 or len(set(library.sequences)) != 50_000:
            raise RuntimeError("completed generator library failed cardinality or uniqueness")
        phase = "QUALIFICATION"
        pool = qualify_and_choose_universe(library.sequences, references, lock.data, project_root)
        score_sequences = [row["sequence"] for row in pool["rows"]]
        if len(score_sequences) < 100 or len(set(score_sequences)) != len(score_sequences):
            raise RuntimeError("qualified selector universe is too small or contains duplicates")
        if not set(score_sequences) <= set(library.sequences):
            raise RuntimeError("qualified selector universe is not a library subset")
        # Completed generation and the exact score input are durable before any
        # scorer code or model is invoked.
        write_fasta(library.sequences, evidence / "accepted_library.fasta")
        sync_file(evidence / "accepted_library.fasta")
        write_json_synced(evidence / "qualified_pool.json", pool)
        scoring_input = {
            "schema_version": "frontier-finalist-scoring-input-v1",
            "run_id": run_id,
            "lock_sha256": lock.sha256,
            "selection_universe": lock.data["selection_universe"],
            "selection_pool_size": lock.data["selection_pool_size"],
            "pool_seed": lock.data["pool_seed"],
            "top_eligibility_order": lock.data["top_eligibility_order"],
            "library_count": len(library.sequences),
            "qualified_count": len(score_sequences),
            "accepted_library_sha256": sha256(evidence / "accepted_library.fasta"),
            "qualified_sequences_sha256": hashlib.sha256(
                ("\n".join(score_sequences) + "\n").encode("ascii")
            ).hexdigest(),
        }
        write_json_synced(evidence / "scoring_input_manifest.json", scoring_input)
        phase = "SCORING"
        scores = score_pool(score_sequences, lock, evidence / "scoring")
        phase = "SELECTION"
        selection = select_consensus(pool, scores, lock, project_root)
        top = selection["ordered_sequences"]
        if len(top) != 100 or len(set(top)) != 100 or not set(top) <= set(library.sequences):
            raise RuntimeError("internal top-list subset failure")
        receipt = {
            "status": "COMPLETE",
            "run_id": run_id,
            "lock_sha256": lock.sha256,
            "scientific_authorization_sha256": lock.data["scientific_authorization_sha256"],
            "arm": lock.data["arm"],
            "selector": lock.data["selector"],
            "selection_universe": lock.data["selection_universe"],
            "selection_pool_size": lock.data["selection_pool_size"],
            "raw_generated": library.raw_generated,
            "raw_examined": library.raw_examined,
            "rejection_counts": library.rejection_counts,
            "eligible_for_top": pool["eligible_count"],
            "selector_pool_count": pool["selected_count"],
            "device": stream.binding.__dict__,
            "device_gate": device_gate,
            "checkpoint_audit": stream.checkpoint_audit,
            "scorer_probe": scorer_probe,
        }
        phase = "OUTPUT_STAGING"
        stage_outputs(stage, library.sequences, top, receipt)
        receipt["library_sha256"] = sha256(stage / "library.fasta")
        receipt["top_sha256"] = sha256(stage / "top.fasta")
        (stage / "run.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        phase = "PUBLICATION"
        publish_staged(stage, project_root / "generate", run_id)
        write_json_synced(run_root / "COMPLETE.json", receipt)
        return receipt
    except BaseException as error:
        # Failed evidence remains in the run-ID directory and can never masquerade
        # as official output. Existing generate/ bytes remain untouched until publish.
        try:
            write_json_synced(run_root / "FAILED.json", {
                "status": "FAILED",
                "run_id": run_id,
                "phase": phase,
                "error_type": type(error).__name__,
                "message": str(error),
                "lock_sha256": lock.sha256,
            })
        except BaseException:
            pass
        raise
