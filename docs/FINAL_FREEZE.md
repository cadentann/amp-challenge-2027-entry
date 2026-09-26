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
AMP-Diffusion the baseline "excluded from rankings" — though no public rule defines when a derivative
stops being the baseline, so that is exposure rather than a settled disqualification. They also both
showed **MMseqs2/MarLys violations under the two coverage settings we tested**, where this entry showed
none; the organizers' parameters are unpublished, so that is a measurement, not a determination. And
all three alternatives sit at **exactly** the 0.800000 Levenshtein limit with zero margin where this
entry has 0.035294 — that one *is* executable and settled. The potency gap that
motivated considering them — 16.4 µM of mean predicted MIC — was then shown to rest on a quantity
that is not calibrated against the measured data we could audit: on that set both predictors have R²
at or below zero on log10 MIC. That scopes the gap as unreliable; it does not make every prediction
meaningless everywhere.

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

**The useful by-product is an observed range for seed sensitivity.** GN@16 across the four seeds we
have spans **0.4714 to 0.5171**. Every marginal inter-portfolio gap this project argued over is far
smaller than that range — the −0.0071 deficit to the potency comparator, our +0.0075 Gram-positive
lead, our +0.0100 MDR lead — so none should be argued from. **Four draws do not calibrate a noise
floor**, and an earlier draft called this "a ±0.02 noise floor" as though it were a measured constant;
that is withdrawn. What survives comfortably above the range is the large structure: the +0.11 to +0.19
gain from full-library selection, which replicated on these fresh seeds.

## What is established

- **Seed robustness is established at production scale**, not inferred: three fresh full-scale seeds,
  all passing pre-registered criteria, with seed 42 slightly below their mean.
- **The selection step exploits predictor structure efficiently.** Against 10,000 random draws of 100
  from the identical scored universe, the frozen selector is **26 standard deviations** above chance on
  *predicted* Gram-negative breadth and 3.4× better than the best draw. This is an internal check
  against the same predictors, **not biological or independent validation** — it says the selector
  works, not that the peptides do.
- **The *predicted* advantage is not explained by proximity to known AMPs.** Stratified by identity to
  103,143 known AMPs, the lift over a random draw from the *same* stratum is largest (z = +16.9) among
  the 20,062 candidates with no alignment at all, and **none** of the 100 comes from the ≥70%-identity
  strata. All APEX-derived: it rules out winning by picking near-duplicates of known actives, and is
  **not** evidence that the predictions transfer to a laboratory.
- **Novelty: the executable rule passes outright; the proposal's rule passes under the settings we
  could test.** Levenshtein max 0.764706 (margin 0.035294) — executable and settled. MMseqs2 vs MarLys
  max 68.7% with zero violations under MMseqs2's default coverage, but the organizers' parameters are
  unpublished and a permissive threshold fails every portfolio. **Zero exact matches across all
  50,000** peptides, which is parameter-free.
- **The predictors are complementary as used.** APEX is a high-precision, near-zero-recall filter
  (precision 0.89–1.00 at 16 µM, 1.7–2.5× base rate); ANIA is calibrated and high-recall (0.72–0.85).
  `CONSENSUS_FIXED` requires both.
- **The selector is the most stable option tested.** Under rank perturbation it retains 88/100 of its
  own list where APEX-only ranking retains 7/100.
- **Engineering is complete.** Two byte-identical end-to-end runs; byte-identical again on a second
  GPU architecture; all eight unchanged official validator checks passed from a clean clone in 116
  minutes; R-free evaluator proven exact across 510,000 values on two platforms; full QA harness green.

## Was the search actually finished?

`docs/FRONTIER_LEDGER.md` is the single place to check. Every avenue is either tested with evidence or
closed with a stated reason — including the ones closed *without* testing, and why.

The last unexplored avenue was portfolio design. It was pre-registered, run on the three fresh holdout
seeds, and **rejected by its own rule**: a family-capped diversity constraint raises expected distinct
families in a random 25-draw from 9.4 to about 22, but costs two to three times the allowed breadth
budget **and makes the 5th percentile worse** — so it does not buy the downside protection that was its
whole rationale. Nothing about the entry changed as a result. See
`docs/LANE9B_DIVERSITY_CONSTRAINT_REJECTED.md`.

## What is not established, stated plainly

- **Nothing is measured.** No peptide has been synthesised or assayed. No biological claim is made.
- **Absolute predicted MIC is meaningless.** Both predictors sit at R² ≤ 0 on held-out measured MIC.
- **Safety and selectivity are UNKNOWN**, and less characterised than the earlier screen implied: the
  haemolysis predictor has negative R² on peptides this novel and detects roughly one in nine. We are
  have no measured HC50 at all, so we have no evidence either way about "Optimal Selectivity" — not a
  prediction that we would place badly, simply no basis to say.
- **One APEX head is dead.** *E. faecalis*, Spearman −0.055, and it feeds our MDR breadth figure.
- **Membership is not precisely determined.** Under ±1 percentile point of predictor rank error about
  half the top-100 would change; aggregate properties are far more stable than membership.
- **One chemotype.** Five residues are 78.4% of the portfolio, D and M absent, median net charge +10 —
  the axis on which haemolysis risk would express itself, and the axis we cannot measure.
- **Asset availability is a residual risk.** All 15 pinned URLs were live and correctly sized at
  freeze time, but there is no fallback mirror.
- **Search opportunity has not saturated, and one avenue is unexplored rather than forbidden.**
  Performance was still climbing at 20,000 candidates. Two distinct things follow. The **submitted
  library must be exactly 50,000** sequences — that is executable, enforced by the official
  validator's `LIBRARY_SIZE = 50_000`. Whether more raw candidates may be generated internally and
  the best 50,000 submitted is a **different question, and we have found no rule that settles it**.
  We already generate 65,536 raw attempts and submit the first 50,000 valid ones in generation order.
  We did not explore choosing the library differently, and the reason is protocol, not rules:
  it would be a new selection policy adopted after seeing which seeds scored well, and it would
  invalidate every reproducibility receipt bound to seed 42's exact 50,000. Recorded as an unexplored
  avenue with a stated reason.
- **Competition performance is unknown.**

## Reproducing it

```bash
uv sync
uv run python scripts/prepare_entry.py     # ~550 MB, every byte hash-verified
uv run --no-sync generate --preflight-only
uv run --no-sync generate
```

Linux x86_64 required. Roughly 50 minutes on an RTX 4090.
