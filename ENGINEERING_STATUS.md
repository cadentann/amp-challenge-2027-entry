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

## Remaining hard gates

1. A scientific authorization must select and hash the final arm seed, raw ceiling, device policy, selection universe, optional pool size and pool seed.
2. The sealed portable R-free ANIA adapter passes public-33, AMP-1,000, ARCAD-1,000, edge-30 and four retained selector equality checks. The combined worker also passes locally on macOS arm64 for two retained 1,000-row inputs and a matched challenge-valid 27-row edge input: every one of eight APEX member arrays, the ensemble, ANIA arrays, joined rows and four selector orders are exact. A score-blind permutation of the retained AMP 1,000-row pool remains exactly equal between native-R and portable paths on the same ordered input, but differs from the original-order prediction arrays after restoring by sequence. This establishes float32 batch-context sensitivity and makes the full ordered list plus 32-row partitions part of the score evidence. This local receipt does not validate Linux. The pinned Linux x86_64 fixture must pass under the exact Torch `2.5.1+cu124` runtime, CUDA build string `12.4`, and wheel SHA-256 before a Linux runtime lock may become `READY_VALIDATED`.
3. The combined generator/scorer dependency layout needs a clean-install test. Generator Python 3.12/Torch 2.8/NumPy 1.26.4 and the authenticated evaluator Python 3.10/Torch 2.5.1/NumPy 2.2.6 must use separately locked environments unless exact cross-version equivalence is demonstrated.
4. A private GPU run must verify the locked device binding, peak VRAM/RSS, 50,000-row raw ceiling supply, repeated FASTA bytes and total time/cost.
5. The official validator must pass twice from a clean clone. Final submission hardware availability remains an operational uncertainty rather than an existing validator rule.
6. A final source archive must be measured below 500,000,000 bytes after the scoring adapter and retrieval bootstrap are sealed.

An exact generated-sequence prefix comparison against the authenticated GPU stage runner remains a required future private-GPU gate. The local mechanical suite does not claim fresh GPU generation equivalence.

No final scientific promotion is encoded or implied by this candidate.
