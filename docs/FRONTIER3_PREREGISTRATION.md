# Final frontier campaign — pre-registration

Written and hashed **before** any result in this campaign was computed. Thresholds here are not
revisable after seeing data. If a lane's result falls short of its promotion threshold, the
incumbent stays and the result is reported as it came out.

- **Incumbent (must not be weakened):** AMP-Prompt + `CONSENSUS_FIXED`, full-opportunity selection,
  seed 42. `top.fasta` = `ece3b7062d55d1ac4eb35f60e450cebec229ebfba63b5a0ab7214ecd4e5cb841`.
- **Fallback:** V3, preserved unchanged.
- **Budget:** prepaid balance at campaign start **$9.1639**. Reserve **$2.10 (23%)** for final
  validation, evidence recovery and shutdown margin. Exploration ceiling **$7.05**.
- **Seed policy:** seed 42 is the development and final-artifact seed and is already exposed. No
  policy change may be justified on seed 42. Fresh seeds are named below and were chosen before
  any generation.
- **Selector policy:** `CONSENSUS_FIXED` is frozen. No lane may retune it. Lanes may only test
  *portfolio construction on top of* it, and only under a threshold fixed here.

## Fresh holdout seeds, fixed now

`8191`, `6007`, `4423`. None has been used in any prior AMP-Prompt experiment in this project
(prior use: 42, 6203, 1729, 2718, 3141, and the scale-test set). Chosen as arbitrary distinct
integers before generation. If a seed fails to yield 50,000 eligible candidates within the frozen
65,536 raw ceiling, it is reported as a failure, not replaced.

---

## LANE 1 — fresh full-scale holdout robustness (HIGH EV, GPU)

**Hypothesis.** The incumbent's predicted Gram-negative breadth advantage is a property of the
generator+selector method, not of seed 42 specifically.

**Method.** For each fresh seed: generate to the frozen 65,536 raw ceiling with the unchanged
decoder, apply unchanged eligibility, take the first 50,000 library-valid in generation order, score
every top-eligible member with the frozen battery, select 100 with unchanged `CONSENSUS_FIXED`.

**Primary metric.** APEX GN breadth@16 of the resulting top-100.

**Pre-declared outcomes.**
- **SUPPORTS incumbent** if all three fresh seeds reach GN@16 ≥ 0.40 — i.e. within 0.085 of seed
  42's 0.4843 and far above the random baseline.
- **WEAKENS** if any fresh seed falls below 0.35.
- **SEED-42-LUCKY** if the mean of the three fresh seeds is below 0.42, i.e. seed 42 exceeds the
  fresh mean by more than 0.065.

A SEED-42-LUCKY outcome does **not** change the shipped artifacts — seed 42 remains the frozen
final seed regardless — but it must be recorded prominently in `LIMITATIONS.md` as evidence that
the reported breadth is optimistic for the method in general.

**Kill.** If generation cannot be reproduced on the available hardware, close the lane and record it.

## LANE 2 — random-subset portfolio robustness (HIGH EV, CPU only)

**Hypothesis.** Because the organizers assay a random 25-peptide subset rather than the whole
top-100, the portfolio with the better *expected subset* outcome may differ from the one with the
better top-100 mean.

**Method.** 100,000 Monte Carlo draws per portfolio per rule. Both surviving rule readings: 25 from
top 50, and 25 from top 100. Four portfolios: shipped finalist, superseded E=5000, potency
AMP-Diffusion, V3. Report full distributions of GN/GP/MDR breadth, mean predicted MIC, worst-decile
performance, and count of distinct 0.60-linked families in the draw.

**Pre-declared decision rule.** This lane is **diagnostic only** unless a portfolio beats the
incumbent on **P(draw achieves GN breadth ≥ incumbent's median)** by more than **0.10 absolute**,
in which case that construction is escalated to Lane 9 for prospective testing on the Lane 1
holdout seeds. It may not be adopted on this lane's evidence alone, because all four portfolios
were constructed on already-exposed data.

**Stated in advance:** by linearity of expectation, diversity cannot change the expected count of
active peptides in a draw, only its variance. Any claimed advantage must therefore be stated as a
variance/tail claim, never as an expected-value claim.

## LANE 5 — predictor dependence and ablation (HIGH EV, CPU only)

**Hypothesis.** The incumbent's selection is supported by more than one predictor signal, so it is
not an artefact of a single model.

**Method.** Re-run the frozen selector's ranking arithmetic on the existing 48,133-member score
matrix under: APEX only; ANIA only; each of the 8 APEX members left out in turn; and rank
perturbation with Gaussian noise at 1%, 5% and 10% of the rank range, 200 replicates each.

**Metrics.** Top-100 and top-50 overlap with the shipped list, Spearman rank correlation, and
GN/MDR breadth of each ablated top-100.

**Pre-declared reading.**
- **ROBUST** if median top-100 overlap under 5% rank noise ≥ 60, and no single APEX
  leave-one-out drops overlap below 50.
- **SINGLE-MODEL-DOMINATED** if removing one predictor family changes top-100 overlap by more than
  70 peptides while removing the other changes it by fewer than 30.

This lane cannot promote anything. Its only output is a quantified dependence statement for
`LIMITATIONS.md`. It is run because a bad result is publishable against us and we would rather find
it than have a reviewer find it.

## LANE 7 — search-opportunity saturation (MEDIUM-HIGH EV, rides on Lane 1)

**Method.** On each Lane 1 fresh seed only, select with the unchanged selector from nested
score-blind hash-ordered universes of 5,000 / 10,000 / 20,000 / full eligible, and measure the
marginal gain in GN breadth@16.

**Pre-declared reading.** If the gain from 20,000 to full is below 0.01 GN@16 on all fresh seeds,
the method is declared **saturated** — which retrospectively supports the full-library choice as
harmless rather than essential. If the gain exceeds 0.03, note that additional generation beyond
50,000 might help, and record that we did **not** pursue it (library size is fixed at 50,000 by the
challenge).

No policy changes from this lane. The selection universe is already frozen at full eligible.

## LANE 12 — rule-ambiguity defense (HIGH EV, low cost)

**Method.** Attempt to reproduce the proposal PDF's alternative novelty rule — MMseqs2 alignment
against the MarLys database — and evaluate the shipped top-100 under it alongside the validator's
`Levenshtein.ratio` rule.

**Pre-declared outcomes.** If MMseqs2 and a MarLys release are both obtainable, report margins under
both rules. **If the shipped entry fails the alternative rule, that is a disqualification risk and
must be surfaced immediately and prominently, even though the executable rule passes.** If MarLys
cannot be obtained, close the lane as UNOBTAINABLE and say so plainly rather than substituting a
different database and calling it equivalent.

## LANE 13 / 14 — validator fuzzing, category EV (MEDIUM EV, low cost)

Diagnostic only. Neither may change the finalist. Lane 13 hardens the entry against mundane
organizer-environment failures; Lane 14 states which categories the evidence is strongest and
weakest for, without asserting any probability of winning.

---

## Lanes deliberately not funded

- **Lane 10 (new generator frontier)** and **Lane 11 (generator mixture)**: closed. Six days to
  deadline; the funnel a new generator must clear (smoke → screen → multi-seed → 50k → validation →
  packaging) cannot complete honestly in that time, and a mixture raises an eligibility-identity
  question with no public rule to resolve it. Eligibility risk is not worth a speculative gain.
- **Lane 6 (Pareto portfolio)**: conditional on a credible safety signal existing. None does — the
  one screen available is documented as unreliable for haemolysis. Closed unless Lane 3 changes.
- **Lane 3 (safety frontier)**: one bounded search only. The existing screen already found no
  separable bad tail, and a frozen selector cannot absorb a new axis post-hoc without a fresh
  prospective protocol there is no time to validate.
