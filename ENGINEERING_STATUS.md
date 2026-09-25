# Engineering status

## Implemented locally

The prospective source adapter implements the official `generate` entry point while remaining inert without `FINALIST.lock.json`. Its generator follows the authenticated AMP-Prompt runner (`c4d90c93e27bc5016774dfefb341262e923f8fb0f2ffbd71d2e2cec5cacdcd9`): Torch 2.8, Transformers 4.24.0, batch 128, top-k 10, top-p 1.0, 34 new-token steps, and one continuous seeded RNG stream. Model reconstruction checks exact equality of every one of 174 checkpoint tensors, the `[10,768]` learned prompt, the `[25,768]` residue embedding, and exact shared storage between the residue embedding and LM head.

The collector stops only after 50,000 valid unique outputs. It examines generator bytes without residue repair and rejects length/alphabet failures, duplicates and exact references. Its prospectively chosen raw ceiling is lock-bound. The frozen selector source is byte-identical to the tournament file. Similarity eligibility is resolved before score access; score-blind subset settings or the full eligible universe remain external lock decisions.

Publication uses a new run-ID directory. It publishes the complete directory only after the 50,000-row library and 100-row unique subset pass. A failed run leaves the previous `generate/` directory intact. FASTA bytes are deterministic across successful repeat publication when the candidate rows are the same.

## Measured local checks

Twenty-one mechanical tests pass without model inference. They cover the absent-lock stop, exact asset retrieval pins, exact reference/length/raw rejection accounting, no raw repair, continuous RNG state across batches, absence of a per-batch RNG reset, conflicting cuBLAS configuration rejection, all-174-tensor restoration, embedding/head tie, complete-only atomic replacement, byte-stable repeat output, frozen selector equality against the canonical tournament module, dual-runtime separation, exact member-array preservation and Linux build pins, the pending scorer lock stop, console entry-point naming, FASTA round trips, flushed partial raw evidence and durable completed-generation evidence before a scorer failure.

The live official validator snapshot has SHA-256 `3f2eb1bd61200abfccf07d86e9c226d57f3d12abcf25715af1d90f41531942cf`. It invokes `uv run --no-sync generate`, requires exactly 50,000 unique sequences and 100 unique subset sequences, checks exact reference overlap and top-list similarity, then invokes the entry again and compares both FASTA files byte for byte. It contains no CPU-only requirement.

## Runtime and cost forecast

These remain engineering forecasts until a locked full run is measured.

| Path | 50k generator | Scoring and selection | Official validator total |
|---|---:|---:|---:|
| AMP-Prompt on RTX 4000 Ada class GPU | about 20–30 min per invocation | about 25–55 min for a locked ~1k score-blind pool; full 50k scoring is materially larger | about 0.9–1.4 h for the ~1k path; about 1.7–2.8 h for full-library scoring |
| AMP-Prompt CPU fallback | expected to be many hours and unmeasured | scorer is CPU-oriented; ~1k is expected in minutes, while 50k needs a dedicated benchmark | unsuitable as a default without measurement |

The validator runs generation twice, so time and any cloud cost must be budgeted twice. A private GPU policy binds explicitly to one visible `cuda:0`, disables TF32 and cuDNN benchmarking, and requests deterministic algorithms. GPU model memory is expected to be modest for GPT-2-sized batch-128 inference, but peak VRAM and host RSS still require a measured locked run. No GPU or cloud work was launched by this integration task.

## Packaging

The candidate source, configuration and provenance copies are small. The authentic AMP archive is 315,661,685 bytes compressed and its checkpoint is 340,569,639 bytes. The current evaluator runtime is about 228 MB on disk. Combining both full asset sets risks exceeding the mandatory 500,000,000-byte release limit. The release therefore uses source plus hash-pinned retrieval and preserves the full canonical weights unchanged. Quantization, truncation and weight substitution are disallowed.

## Hard gates — all closed

These were the six gates that had to pass before this could be a real entry. Each is now closed,
with the evidence that closed it.

1. **Scientific authorization.** `FINALIST.lock.json` fixes seed 42, raw ceiling 65,536,
   `auto_prefer_cuda` device policy and the `full_library` selection universe. The universe was
   chosen by a prospectively frozen experiment (protocol sha `9f69ec59…`, frozen 06:29:42Z before
   any score was computed) that passed all six pre-declared promotion criteria. See
   `docs/HEV1_FULL_OPPORTUNITY_PROTOCOL.md`.
2. **Linux scorer validation.** The pinned Linux x86_64 fixture passes under Torch `2.5.1+cu124`,
   CUDA build `12.4` and the pinned wheel SHA-256. The R-free evaluator reproduces the native
   R-backed one **exactly** across 510,000 values on macOS and again on Linux. Receipts in
   `validation/`. A Linux runtime now reaches `READY_VALIDATED`.
3. **Clean-install test of the dual environments.** Both locked environments install from a fresh
   clone: generator Python 3.12 / Torch 2.8 / NumPy 1.26.4, evaluator Python 3.10 / Torch 2.5.1 /
   NumPy 2.2.6, in separate `uv` projects with separate locks. One defect was found and fixed here:
   `uv sync` failed on a clean machine because transformers 4.24.0 pulls a `tokenizers` release
   with no CPython 3.12 wheel. Resolved by `[tool.uv] override-dependencies`, which reproduces the
   environment that was actually validated — one with no tokenizers package present.
4. **Private GPU run.** Verified on a clean RTX 4090: locked device binding, the 65,536-attempt raw
   supply, and byte-identical FASTA output across two full runs. `validation/END_TO_END_VALIDATION.json`.
5. **Official validator from a clean clone.** Run with the unchanged validator
   (SHA-256 `3f2eb1bd…`) against a fresh clone of this repository. This is what exposed the defect
   that mattered most: the repository had **no asset-retrieval logic at all**, so an organizer's
   clone had no model checkpoint and no scorer runtime and could not run. Since the validator does
   only `git clone`, `uv sync`, `uv run --no-sync generate`, there was no step in which they could
   have fetched them. `scripts/prepare_entry.py` closes it, and `generate` invokes it automatically.
6. **Release size.** The source package is well under the 500,000,000-byte limit, because the
   315 MB generator checkpoint and 235 MB evaluator assets are retrieved from their published
   sources and hash-verified rather than redistributed. Quantization, truncation and weight
   substitution remain disallowed and none was performed.

## What is still not established

Everything scientific. No peptide has been synthesised or assayed; safety, haemolysis and
selectivity are unknown; competition performance is unknown. The predictors this entry ranks with
achieve R² < 0.30 on MIC regression under homology-controlled splits. Read `docs/LIMITATIONS.md`
before making any claim on the basis of this repository.
