# Safety / selectivity screen — result and its limits

A credible, reproducible predictor **was** found and run. The result does not change the finalist,
and safety still cannot be claimed. Both of those statements are load-bearing.

## Tool

**HemoPI2 v1.3** — `github.com/raghavagps/HemoPI2`, PyPI `hemopi2`, GPL-3.0, trained on 1,926
experimentally validated hemolytic peptides, giving both a hemolytic/non-hemolytic call and an
HC50 regression.

Used as an **analysis tool only**. It is not shipped in the entry, not imported by the pipeline,
and was not used to filter or retune the frozen selector — so its GPL-3.0 licence does not interact
with the entry's MIT licence.

Run prospectively on all four delivered portfolios at once.

## Raw HC50 results

| portfolio | median HC50 µM | min | p10 | predicted hemolytic | HC50 <10 µM |
|---|---:|---:|---:|---:|---:|
| **Final (full-opportunity)** | 28.79 | 7.43 | 13.40 | 91/100 | 4 |
| Superseded E=5000 | 36.07 | 10.30 | 15.06 | 85/100 | 0 |
| Potency (AMP-Diffusion) | 26.35 | 7.17 | 12.40 | 96/100 | 5 |
| V3 fallback | 29.07 | 7.84 | 15.12 | 94/100 | 1 |

No peptide in any portfolio has predicted HC50 below 5 µM. The binary "hemolytic" call fires for
85–96% of peptides in **every** portfolio, including the AMP-Diffusion ones — this is a property of
the cationic amphipathic class, not a discriminator between our candidates.

## Therapeutic index — and a correction to my own first reading

My first pass computed HC50 ÷ **mean** APEX MIC and produced an alarming median of 0.42 with
TI < 1 for 81/100. **That denominator was wrong.** APEX averages 11 strains including ones a
peptide has no activity against, so mean MIC massively overstates the effective dose. Therapeutic
index is conventionally HC50 ÷ MIC against the organism being treated.

Recomputed conventionally:

| portfolio | TI vs best strain (median) | TI > 1 | TI > 4 | TI vs best Gram-negative (median) |
|---|---:|---:|---:|---:|
| **Final (full-opportunity)** | **8.00** | 100/100 | **82/100** | 4.89 |
| Superseded E=5000 | 8.53 | 100/100 | 80/100 | 6.12 |
| Potency (AMP-Diffusion) | 6.88 | 100/100 | 74/100 | 4.06 |
| V3 fallback | 5.60 | 100/100 | 74/100 | 4.04 |

Under the conventional definition **every peptide in every portfolio has predicted HC50 above its
predicted MIC**, and the final entry leads the potency portfolio and V3 on both the median index
and the fraction exceeding 4×.

The final entry is marginally behind the superseded E=5000 entry (8.00 vs 8.53 median; 4.89 vs 6.12
against the best Gram-negative). That is an adverse signal and it is recorded here rather than
omitted. It is small, it runs in the opposite direction to the large breadth gains, and it rests on
a predictor documented as unreliable — see below.

## Why no safety filter was applied

The directive permits a *minimal pre-declared* safety filter if it would materially improve the
portfolio without destroying activity. It would not, for three reasons:

1. **There is no separable bad tail.** No peptide falls below 5 µM HC50; the distribution is
   continuous and the class-level hemolytic call fires for ~90% of every portfolio, including the
   comparators. A filter would not remove outliers — it would remove most of the library.
2. **The predictor is documented as unreliable.** QMAP (Sci Rep 2026) reports **low predictability
   for hemolytic activity** specifically, and AMPBench-MT (2026) reports MIC regression
   **R² < 0.30** under 30% homology control. Both the numerator and the denominator of any
   therapeutic index built from these models are weak.
3. **It would be post-hoc.** The selector is frozen. Introducing a safety axis after seeing these
   numbers is exactly the retuning the protocol forbids. A safety-aware selector would need its own
   prospectively frozen protocol, which there is no time to run and validate honestly.

## Status

**Safety and selectivity remain UNKNOWN.** What changed is that "unknown" is now *characterised*
rather than merely unexamined: we have a reproducible screen, it found no gross outliers, it places
our entry at or above the comparators on conventional therapeutic index, and it is not trustworthy
enough to rely on.

We make no safety claim. We are not competitive in the "Optimal Selectivity" category, which is
scored on measured HC50/MIC50, and we have no measured data of any kind.

Evidence: `evidence/SAFETY_SCREEN.json`.
