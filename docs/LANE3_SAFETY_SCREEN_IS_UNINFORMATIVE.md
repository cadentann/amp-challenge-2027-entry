# Lane 3 — our safety screen is uninformative for peptides as novel as ours

This lane was meant to look for a better safety predictor. It instead measured the one we already
used, and the result is **adverse to our own evidence**. It is recorded prominently because the
shipped safety screen reads as mildly reassuring and should not.

## What was done

`SAFETY_SELECTIVITY_SCREEN.md` reports HemoPI2 v1.3 predicted HC50 for all four portfolios and
notes "no peptide in any portfolio has predicted HC50 below 5 µM". It declines to apply a safety
filter partly by **citing** QMAP's finding of low predictability for haemolytic activity. This lane
replaced the citation with a measurement of *our specific tool*, against QMAP's own ground-truth
HC50 values (1,274 canonical 8–50aa peptides with consensus measured HC50, from all five
homology-controlled splits).

## The first answer was wrong, and why

Measured on the whole set, HemoPI2 looked **good** — Spearman 0.808, R² 0.656 on log10 HC50. That
would have made our safety screen more trustworthy than documented, and it is the result I was about
to report.

It is an artifact. HemoPI2's published training and validation data (1,926 peptides,
`raghavagps/hemopi2`) contains **972 of the 1,274 evaluation peptides — 76.3%**. The apparent
accuracy was mostly memorisation.

## The honest answer

| evaluation subset | n | Spearman | R² (log10) | recall of peptides truly below 25 µM |
|---|---:|---:|---:|---:|
| all (76% contaminated) | 1,232 | 0.808 | 0.656 | 0.650 |
| exact-held-out | 260 | 0.364 | 0.118 | 0.341 |
| held-out, <60% identity to training | 159 | 0.164 | **−0.146** | 0.118 |
| held-out, <40% identity to training | 127 | 0.111 | **−0.268** | **0.111** |

**On peptides genuinely unlike its training data, HemoPI2 is worse than predicting the mean**
(negative R²) and detects roughly **one in nine** truly haemolytic peptides.

## Why this bears directly on our entry

Our top-100 sits exactly in the regime where the tool fails. Lane 4 measured its distance from known
AMPs: maximum 68.7% identity to any of 103,143 MarLys entries, median 50.0%, and 18 of the 100 with
no detectable alignment at all. These are **not** peptides the predictor has seen anything like.

Three consequences, all of which make our documentation more cautious rather than less:

1. **"No peptide has predicted HC50 below 5 µM" is not evidence of safety.** A screen with 11%
   recall would miss roughly eight of every nine haemolytic peptides in our list. The absence of
   flags is close to uninformative.
2. **The therapeutic-index table must be read as uninformative, not merely uncertain.** TI values
   (median 8.00 for the shipped entry) divide a measured-scale HC50 estimate by a predicted MIC. The
   numerator is now shown to carry almost no signal for novel peptides. The comparison *between*
   portfolios on TI is correspondingly meaningless, including the adverse comparison against the
   superseded entry that we reported honestly at the time.
3. **The decision not to apply a safety filter is strengthened, and for a better reason.** The
   original three reasons were: no separable bad tail; predictor documented as unreliable; a filter
   would be post-hoc on a frozen selector. Reasons one and three stand untouched. Reason two is now
   a measurement on the actual tool rather than a citation about the field — and it is much stronger
   than the citation was. Filtering on a signal with negative R² would have been noise injection
   dressed as caution.

## What would have changed the decision

A predictor with public code, public weights and demonstrated homology-controlled performance on
HC50. The bounded search found none. **AmpLyze** (arXiv 2507.08162) reports PCC 0.756 but has no
usable public code or weights and does not state homology-controlled evaluation. **QMAP** is a
benchmark, not a predictor — it is what made this measurement possible. Lane 6 (Pareto portfolio over
a safety axis) is therefore closed: there is no credible safety axis to build one on.

## Status

**Safety and selectivity remain UNKNOWN, and are now known to be *less* characterised than the
shipped screen implied.** The "Optimal Selectivity" category is scored on measured HC50/MIC50 and we
have none, so we have no evidence either way about our standing in it — which is not the same as
expecting to place poorly.

Evidence: `experiments/LANE3_SAFETY_TOOL_RELIABILITY.json`.
