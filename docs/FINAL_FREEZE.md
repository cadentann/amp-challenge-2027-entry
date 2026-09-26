# Final freeze

**The entry is frozen. Nothing has been submitted, published, or shared with the organizers.**

| | |
|---|---|
| generator | AMP-Prompt (AMP-Designer), commit `07d455dd`, weights Zenodo DOI 10.5281/zenodo.17018363 (CC-BY-4.0) |
| selector | `CONSENSUS_FIXED`, frozen, never retuned, 996-member anchor `fe438eab…` |
| seed | 42 |
| selection universe | all 48,133 eligible members of the library |
| `library.fasta` | `a91c0de9200a3d9f4377bfc6f81d36d21ea15bb9c940bd91fab797cd5ae2308b` (50,000 unique) |
| `top.fasta` | `ece3b7062d55d1ac4eb35f60e450cebec229ebfba63b5a0ab7214ecd4e5cb841` (100 ranked) |
| platform | **Linux x86_64** — `FINALIST.lock.json` pins the Linux scorer-runtime lock |
| fallback | V3, preserved unchanged, `45f69b0d…` |

## Why this method and not another

Four candidate portfolios were compared on every axis that could be measured. The two that beat this
entry on predicted potency are both **AMP-Diffusion derivatives**, and the starter kit calls
AMP-Diffusion the baseline "excluded from rankings". They also both **breach the proposal's
MMseqs2/MarLys novelty rule**, which this entry passes, and all three alternatives sit at **exactly**
the 0.800000 Levenshtein limit with zero margin where this entry has 0.035294. The potency gap that
motivated considering them — 16.4 µM of mean predicted MIC — was then shown to rest on a quantity
with no absolute meaning: measured against real MIC data, both predictors have R² at or below zero.

No alternative was promoted. Every lane that could have promoted one either failed its
pre-registered threshold or, in the one case where a threshold fired, pointed at a portfolio that is
ineligible and rule-breaching.

## The final robustness test, run last and passed

The one question the entry could not previously answer was whether its advantage belonged to the
**method** or to seed 42. Three fresh seeds — named in a pre-registration frozen at
2026-09-26T04:14:15Z before any of them was generated — were run at full production scale, each with a
lock differing from the shipped one in exactly one field, `generation_seed`.

| | s8191 | s6007 | s4423 | **shipped s42** | fresh mean |
|---|---:|---:|---:|---:|---:|
| GN breadth@16 | **0.5171** | 0.4714 | **0.5129** | 0.4843 | **0.5005** |

**SUPPORTS = true. WEAKENS = false. SEED-42-LUCKY = false.** All three clear the 0.40 bar; the nearest
approach to the 0.35 failure floor is 0.4714. And the fresh mean *exceeds* seed 42, so the shipped
artifacts are a mildly conservative draw, not a fortunate one.

**Two of the three fresh seeds scored higher than the entry we ship, and we declined to switch.** The
pre-registration forbids replacing the seed "merely because another fresh seed looks prettier", and
switching would be post-hoc selection on data generated to test robustness — invalidating the
byte-identical replication, the cross-architecture reproduction, the decision-stability certificate and
the clean-room validator receipt, all of which bind seed 42's exact artifacts.

**The most useful number this produced is the noise floor.** GN@16 across four independent seeds spans
0.4714 to 0.5171 — about **±0.02**. Every marginal inter-portfolio gap this project argued over is
smaller than that: the −0.0071 deficit to the potency comparator, our +0.0075 Gram-positive lead, our
+0.0100 MDR lead. None of them is a real difference. What survives is the large structure: the ~+0.12
gain from full-library selection (which also replicated on these fresh seeds) and the
26-standard-deviation gap to random selection.

## What is established

- **Seed robustness is established at production scale**, not inferred: three fresh full-scale seeds,
  all passing pre-registered criteria, with seed 42 slightly below their mean.
- **Selection extracts real signal.** Against 10,000 random draws of 100 from the identical scored
  universe, the frozen selector is **26 standard deviations** above chance on predicted Gram-negative
  breadth and 3.4× better than the best of those draws.
- **The advantage is not family recognition.** Stratified by identity to 103,143 known AMPs, the lift
  over a random draw from the *same* stratum is largest (z = +16.9) among the 20,062 candidates with
  no alignment at all, and **none** of the 100 comes from the ≥70%-identity strata.
- **Novelty passes both published rules.** Levenshtein max 0.764706 (margin 0.035294) and MMseqs2 vs
  MarLys max 68.7% with zero violations, plus **zero exact matches across all 50,000** peptides.
- **The predictors are complementary as used.** APEX is a high-precision, near-zero-recall filter
  (precision 0.89–1.00 at 16 µM, 1.7–2.5× base rate); ANIA is calibrated and high-recall (0.72–0.85).
  `CONSENSUS_FIXED` requires both.
- **The selector is the most stable option tested.** Under rank perturbation it retains 88/100 of its
  own list where APEX-only ranking retains 7/100.
- **Engineering is complete.** Two byte-identical end-to-end runs; byte-identical again on a second
  GPU architecture; all eight unchanged official validator checks passed from a clean clone in 116
  minutes; R-free evaluator proven exact across 510,000 values on two platforms; full QA harness green.

## What is not established, stated plainly

- **Nothing is measured.** No peptide has been synthesised or assayed. No biological claim is made.
- **Absolute predicted MIC is meaningless.** Both predictors sit at R² ≤ 0 on held-out measured MIC.
- **Safety and selectivity are UNKNOWN**, and less characterised than the earlier screen implied: the
  haemolysis predictor has negative R² on peptides this novel and detects roughly one in nine. We are
  not competitive in "Optimal Selectivity" and claim nothing there.
- **One APEX head is dead.** *E. faecalis*, Spearman −0.055, and it feeds our MDR breadth figure.
- **Membership is not precisely determined.** Under ±1 percentile point of predictor rank error about
  half the top-100 would change; aggregate properties are far more stable than membership.
- **One chemotype.** Five residues are 78.4% of the portfolio, D and M absent, median net charge +10 —
  the axis on which haemolysis risk would express itself, and the axis we cannot measure.
- **Asset availability is a residual risk.** All 15 pinned URLs were live and correctly sized at
  freeze time, but there is no fallback mirror.
- **Search opportunity has not saturated.** Performance was still climbing at 20,000 candidates, so
  generating beyond 50,000 might help — but the challenge fixes the library at 50,000, so that is a
  rule boundary we cannot cross rather than a choice we made.
- **Competition performance is unknown.**

## Reproducing it

```bash
uv sync
uv run python scripts/prepare_entry.py     # ~550 MB, every byte hash-verified
uv run --no-sync generate --preflight-only
uv run --no-sync generate
```

Linux x86_64 required. Roughly 50 minutes on an RTX 4090.
