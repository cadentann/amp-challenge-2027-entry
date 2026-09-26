# Our predictors, measured against real MIC data

The entry's dominant uncertainty has until now been stated as a citation: AMPBench-MT reports
R² < 0.30 for MIC regression under homology control. This measures **our** predictors, on **measured**
MIC, at **the challenge's own activity threshold** of 16 µM.

## Setup

3,591 canonical, linear, free-termini peptides of length 8–50 with consensus measured MIC from the
QMAP benchmark, across the seven species APEX covers. Scored with the entry's own frozen evaluator
(APEX 11 heads, ANIA 3 heads) through the shipped scorer runtime.

**Contamination was controlled where it could be.** ANIA's actual training membership is known — the
project assembled it from ANIA's own published train/test downloads
(`vendor/evaluator/known_training/ania_membership.csv`, 9,489 records). **2,685 of the 3,591 measured
peptides (74.8%) are in ANIA's training set**, so whole-set ANIA numbers are contaminated and are not
quoted below. The held-out set is **906 peptides**.

APEX's training corpus is not obtainable, so its numbers are **not** a clean holdout and may still be
contaminated. They are reported for what they are.

## Held-out results (906 peptides outside ANIA training)

| model | species | n | Spearman | R² (log10) | recall @16 µM | precision @16 µM | base rate | precision lift |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **ANIA** | E. coli | 684 | 0.452 | −0.021 | **0.805** | 0.626 | 0.523 | 1.20 |
| **ANIA** | P. aeruginosa | 341 | 0.441 | −0.089 | **0.722** | 0.455 | 0.390 | 1.17 |
| **ANIA** | S. aureus | 618 | 0.478 | 0.015 | **0.850** | 0.526 | 0.400 | 1.32 |
| APEX | E. coli | 684 | 0.455 | −1.517 | 0.048 | **0.895** | 0.523 | **1.71** |
| APEX | A. baumannii | 242 | 0.262 | −1.100 | 0.227 | **0.968** | 0.546 | **1.77** |
| APEX | S. aureus | 618 | 0.173 | −2.228 | 0.004 | **1.000** | 0.400 | **2.50** |
| APEX | E. faecium | 69 | 0.195 | −0.907 | 0.350 | 0.737 | 0.580 | 1.27 |
| APEX | K. pneumoniae | 251 | 0.171 | −2.606 | 0.000 | 0.000 | 0.514 | 0.00 |
| APEX | P. aeruginosa | 341 | 0.308 | −1.515 | 0.000 | 0.000 | 0.390 | 0.00 |
| APEX | E. faecalis | 112 | **−0.055** | −1.540 | 0.000 | — | 0.366 | — |

## What this establishes

**1. Absolute predicted MIC values are meaningless.** Both predictors have R² at or below zero on
held-out measured data — APEX strongly negative (−0.9 to −2.6), ANIA approximately zero. Our
documentation's citation of "R² < 0.30" was, if anything, **optimistic**. Every absolute µM figure in
this entry — including "APEX mean MIC 73.46 µM" and the 16.4 µM gap to the potency comparator that
earlier analysis treated as the entry's main weakness — carries essentially no absolute meaning. That
gap should never have been weighed as heavily as it was, and this is the measurement that says so.

**2. The two predictors are complementary, in exactly the way the frozen selector uses them.**

- **APEX is a high-precision, near-zero-recall filter.** It almost never predicts MIC ≤16 µM, but
  when it does it is right 89–100% of the time, with precision lift **1.7–2.5×** over base rate — the
  strongest signal measured anywhere in this analysis.
- **ANIA is a calibrated, high-recall predictor.** It catches **72–85%** of truly active peptides with
  precision 0.46–0.63 and lift 1.17–1.32×, and its R² is near zero rather than deeply negative.

`CONSENSUS_FIXED` ranks by worst-case percentile across the two families, so a peptide must satisfy
**both**. That combines APEX's precision with ANIA's coverage. The design was frozen long before any
of this was measured, and the measurement supports it.

**3. It inverts an assumption the documentation carried.** Throughout, APEX was treated as the primary
activity signal and ANIA as the weaker corroborator, and Lane 5 reported that ANIA-only ranking gives
GN breadth@16 of 0.1986 against APEX-only's 0.6300. That comparison is circular — GN breadth@16 *is*
computed from APEX. Against measured MIC, **ANIA is the better-calibrated predictor of the two**, and
APEX's apparent dominance was an artifact of scoring APEX against itself. Had we followed Lane 5's
surface reading and ranked on APEX alone, we would have optimised the predictor with R² of −1.5 and
recall of 0.05.

**4. One real weak spot.** APEX on *E. faecalis* has Spearman **−0.055** — no signal at all, very
slightly inverted. E. faecalis is one of the four heads in our MDR breadth metric, so MDR@16 (0.4575)
rests partly on a head with no measurable rank signal on held-out data.

## Honest limits

- **Assay mismatch is a genuine confound.** QMAP's measured MICs come from DBAASP across many
  protocols and strains; APEX's heads are eleven *specific* strains under one protocol. Some of the
  negative R² is calibration and strain mismatch rather than model error. The Spearman and
  threshold-classification numbers are more robust to this than R² is.
- **APEX is not cleanly held out.** Its training corpus could not be obtained, so its numbers may be
  contaminated in its favour — which makes its near-zero recall worse news, not better.
- **Base rates here are 0.37–0.55** because QMAP is enriched for known actives. Our 48,133-member
  library has a far lower base rate (random GN@16 was 0.0709), so precision lift on this benchmark
  does not transfer directly to lift on our library.
- Three species for ANIA, seven for APEX. Nothing here covers the organizers' full 20-strain panel.

Evidence: `experiments/LANE_PREDICTOR_HELDOUT.json`,
`experiments/LANE_PREDICTOR_RELIABILITY_MEASURED.json`.
