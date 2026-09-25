# 5,000-E marginal-supply scale test — adjudication

**VERDICT: SCALE GO. The final selection policy is frozen at E = 5,000.**

All four prospectively frozen GO conditions from `FINALIST_SELECTION_UNIVERSE_PROPOSAL.md`
(sha `7a77db5f0acd3c0f487f00bb610a459934ffe757036d63b8729f6e4446809eb6`) pass on both seeds.
No gate, threshold, selector, anchor or scorer was modified at any point. The conditions were
written before any scale outcome existed.

## Why this test was run rather than defaulted away

The proposal states: *"the final 50,000-library run supplies the selected pool by the same
score-blind hash rule; scoring all eligible members is not an implementation shortcut."* The E
policy therefore determines which 100 peptides ship.

Measured directly: **79 of 100 (seed 6203) and 80 of 100 (seed 7919)** top-100 members differ
between the 1,000-E and 5,000-E consensus lists. Running the test changed roughly 80% of the
deliverable. Defaulting to 1,000-E would have shipped a materially different and weaker product.

## Execution

| item | value |
|---|---|
| Seeds | 6203, 7919 — verified unused (1,150 canonical JSONs scanned; appear only in preparation templates and pre-frozen controls) |
| Raw per seed | 8,192 (64 continuous batches of 128) |
| Generation | RTX 4090, pod `imnrmrt3fdcbii`, terminated. GPU spend ≈ $0.40 |
| Runtime | Python 3.12.3, Torch 2.8.0+cu128, CUDA 12.8, Transformers 4.24.0, **no tokenizers package** — matching the frozen successful AMP environment |
| Checkpoint | Zenodo DOI 10.5281/zenodo.17018363, CC-BY-4.0. `prompt_model.zip` `71af768d…`, `pytorch_model.bin` `47944ff4…` — both verified on the pod |
| Runtime checkpoint audit | PASS — 174/174 tensors reconstructed exactly, keysets equal, no forward pass during audit |
| Prefix freeze | both seeds `PASS_EXACT_CONTINUOUS_PREFIX`, `exact_full_row_equality: true` (first 4,096 rows identical to a 4,096 run — validates nesting) |
| Raw hashes | 6203 `0c3a6c7e…`, 7919 `2541e3db…` |

## Supply (proposal pre-condition)

| seed | eligible | required | nested 1,000 ⊂ 5,000 |
|---|---:|---:|---|
| 6203 | 7,657 | ≥5,000 | exact prefix |
| 7919 | 7,654 | ≥5,000 | exact prefix |

No supply shortfall. Pool membership hashes were frozen **before** scoring
(`SCALE_NESTED_POOLS_FROZEN`).

## Scoring

Local Mac CPU, frozen APEX8/ANIA3 runtime (`READY_VALIDATED`, runtime manifest `ecacbe1e…`),
batch 32, 2 threads, original 996-member anchor `fe438eab…`. Eight pools scored, all
`COMPLETE` with `all_joins_exact: true`.

The nested 1,000-E pools were scored **in their own batch context**, not sliced from the 5,000
run, because the frozen numerical plan warns that batch composition can alter float32 results.

## Condition 1 — material marginal benefit (≥ +0.05 top100 GN breadth@16 vs own nested 1,000-E)

| seed | 5,000-E | 1,000-E | gain | verdict |
|---|---:|---:|---:|---|
| 6203 | 0.394286 (276/700) | 0.265714 (186/700) | **+0.128571** | PASS |
| 7919 | 0.407143 (285/700) | 0.248571 (174/700) | **+0.158571** | PASS |

## Condition 2 — preserved tradeoffs vs nested 1,000 (all must be non-adverse, both seeds)

| quantity | 6203 | 7919 | requirement |
|---|---:|---:|---|
| top50 GN@16 delta | +0.137143 | +0.148571 | ≥ 0 |
| top100 GN@8 delta | +0.058571 | +0.068571 | ≥ 0 |
| top100 GN@32 delta | +0.157143 | +0.158571 | ≥ 0 |
| ANIA median anchor-rank delta | +0.042671 | +0.047691 | ≥ 0 (no decline) |
| ANIA EC/PA mean log10 MIC delta | −0.293922 | −0.279795 | ≤ 0 (no worsening) |

PASS both seeds. Notably the ANIA EC/PA potency term **improved** at 5,000-E rather than merely
holding — the usual breadth/potency tension did not appear here.

## Condition 3 — equal-opportunity vs the 5,000-E cached POTENCY control

| quantity | 6203 | 7919 | requirement |
|---|---:|---:|---|
| top100 GN@16 gain | +0.067143 | +0.097143 | ≥ 0.05 in **both** |
| ANIA median anchor-rank gain | +0.198795 | +0.238956 | ≥ 0.05 in one, ≥ 0 in other |
| top50 GN@16 delta | +0.051429 | +0.022857 | no reversal |

PASS. The control is the prospectively hash-selected 5,000-E subset of the accepted
AMP-Diffusion library, frozen before outcomes with rebuild byte-identity verified — equal
selection opportunity, not the easier 1,000-E control.

## Condition 4 — support

Complete 100 for every compared list; complete scores; joins exact. PASS.

## What this does and does not claim

Establishes: at a fixed, prospectively specified selection opportunity, the released AMP-Prompt
generator with the frozen `CONSENSUS_FIXED` selector yields **greater repeated predicted
Gram-negative breadth**, replicated across two fresh unused seeds, without the specified ANIA
reversals, against an equal-opportunity cached control.

Does **not** establish: biological superiority, safety, selectivity, or wet-lab transfer. APEX
and ANIA share predictor ancestry and have recorded measured-threshold transfer failures. A
larger search can exploit correlated surrogate error as well as find genuinely better peptides;
this test cannot separate those. The cached control has a single historical generation seed and
is not fresh generator replication.

## Consequence

Per the proposal's stopping rule — *"If 5,000 passes, freeze exactly 5,000 for final runs"* —
**E = 5,000 is now the frozen final selection policy.** No follow-up 10,000/all-E search,
alternate endpoint, selector switch, or added seed is permitted to rescue or extend this result.

Evidence: `analysis/scale8192_v1/` (inputs, authorizations, scores, `SCALE_ADJUDICATION.json`);
generation evidence `gpu_supervision/window9_scale8192_EXECUTED/window9_evidence.tar.gz`
sha256 `dda6e0db8bc25637943622c8cb6cf0fb9c6914d3e0a1baa50886c3c664d07948`.
