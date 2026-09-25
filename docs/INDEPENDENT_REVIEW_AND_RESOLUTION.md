# Independent adversarial review — findings and what was done about them

An independent reviewer was given the finalist, the comparators and the raw evidence, and asked to
try to break it. It re-derived the headline metrics from the raw per-peptide score files rather
than trusting any reported number, and ran one analysis the project had never run.

**Verdict: FINALIST_KEEP.**

## What reproduced exactly

From the raw `universe_chunk*/scores.csv` files, joined to the 100 shipped sequences (100/100
matched):

| metric | independently recomputed | as claimed |
|---|---|---|
| APEX GN breadth@16 | 0.484286 | 0.484286 |
| all-11 breadth@16 | 0.399091 | 0.399091 |
| GP breadth@16 | 0.250000 | 0.250000 |
| APEX mean MIC | 73.45665 µM | 73.45665 |
| ANIA EC/PA log10 MIC | −0.462411 | −0.462411 |

Also verified from scratch: top-100 is a subset of the library; zero exact overlap with the 39,448
reference sequences; max `Levenshtein.ratio` 0.764706 with margin 0.035294 and no violations;
113 internal pairs ≥0.60, none ≥0.80. The full-library selection universe was already a supported
enum in `lock.py` before the promotion — no code was changed to enable it.

**The science reproduced. Every defect found was in documentation or packaging.**

## Findings that survived, and their resolution

| # | finding | resolution |
|---|---|---|
| D1 | The retracted 0.1497 novelty figure was still live in `ELIGIBILITY_REVIEW.md`, `DATA_AND_MODEL_DISCLOSURE.md`, `ACTUAL_PRODUCT_COMPARISON` and `PORTFOLIO_COMPLIANCE.json`. `ACTUAL_PRODUCT_COMPARISON` contained a "correction" that was itself the error. | **Fixed.** All four corrected to the measured 0.764706. The inverted correction is withdrawn in place. `ELIGIBILITY_REVIEW.md` rewritten against the shipped entry (length 12–34, top-50 GN 0.5286). |
| D2 | `validation/END_TO_END_VALIDATION.json` recorded the **superseded** top-100 hash and asserted it matched the shipped artifacts. | **Fixed.** Replaced with the post-promotion receipt (`ece3b706…` twice, byte-identical, matching the shipped files). The old receipt is retained as `SUPERSEDED_END_TO_END_VALIDATION_E5000.json`. |
| D3 | The entry `README.md` still declared the entry unauthorized and unvalidated; `ASSET_SOURCES.json` still said the Linux equivalence was pending. | **Fixed.** README rewritten as the organizer-facing document; `ASSET_SOURCES.json` updated to PASS. |
| D4 | `.gitignore` excluded `/FINALIST.lock.json`. Pushed as-is, the organizers' `uv run generate` would have failed closed. | **Fixed.** The lock is tracked deliberately, with a comment saying why. Verified: it is present in the committed tree used for the clean-room run. |
| D5 | `FINAL_HASH_MANIFEST.json` did not cover the five newest artifacts. | **Fixed.** Regenerated over the final package. |
| D6 | Three shipped documents said we had "no HC50 evidence" while `SAFETY_SCREEN.json` carried predicted HC50 for 400 peptides. | **Fixed.** The distinction is now stated explicitly: predicted HC50 exists and is not trusted; **measured** HC50 does not exist. |
| D7 | `LIMITATIONS.md` and the adversarial review attributed the **superseded** entry's homology numbers to the shipped one, overstating the ≥0.60-neighbour gap roughly fourfold. | **Fixed.** Recomputed for the shipped entry: mean max-similarity 0.6668, 96% with a ≥0.60 neighbour, leakage Spearman +0.058 (GN@16) and +0.011 (APEX mean MIC). Conclusion unchanged and slightly stronger. |
| D8 | The attack table called 113 internal pairs "best of the three"; V3 has 0 pairs and 100 singletons. | **Fixed.** Corrected, with single-linkage component sizes added — half the shipped portfolio is one 0.60-linked component. |
| D9 | `FINAL_POLICY.lock.json` carried a `frozen_utc` predating the promotion it documents. | **Fixed.** `amended_utc` added with a note explaining what was frozen when. |
| — | `largest_family80_fraction` was broken: it summed all family fractions instead of taking the maximum, reporting 1.0000000000000007 for every portfolio. | **Removed** from both carriers as uninformative. Single-linkage component sizes replace it. |
| — | The shipped finalist had **no row** in `HEV3_HOMOLOGY_ANALYSIS.json` — the leakage correlation for the portfolio actually being submitted was never computed. | **Computed and added.** It favours the entry. |

## The reviewer's strongest objection — now answered by measurement

The objection: the superseded E=5000 pool was **score-blind** (hash-ordered), a genuine guard
against overfitting the predictors. Promotion to the full library removes that guard and searches
9.6× harder against models with documented R² < 0.30 under homology control. The observed gains
have the shape that harder proxy maximisation produces, and **there was no null control** — no
random-48,133 draw, no permutation baseline — anywhere in the evidence.

That was correct, and the control has now been run. Against 10,000 random draws of 100 from the
**identical** 48,133-member scored universe:

| metric | selector | random mean (sd) | best of 10,000 draws | z |
|---|---:|---:|---:|---:|
| GN breadth@16 | 0.4843 | 0.0709 (0.0157) | 0.1443 | **+26.4** |
| all-11 breadth@16 | 0.3991 | 0.0687 (0.0131) | 0.1291 | **+25.2** |
| APEX mean MIC (µM) | 73.46 | 228.38 (12.65) | 185.57 | **−12.2** |

The selector's portfolio has 6.8× the Gram-negative breadth of an average random 100 and 3.4× the
best of ten thousand random draws. **The full-opportunity gain is not an artefact of sampling
more:** sampling more at random from the same universe gets nowhere close. Searching harder
produced a better portfolio because there was signal to find.

This does **not** rehabilitate the predictors. It holds them fixed and asks only whether the
selector beats chance given them. Whether predicted MIC transfers to the organizers' measured panel
is untouched by it, and remains the dominant uncertainty in this entry. Full method, caveats and
the achievable-ceiling comparison: `NULL_CONTROL.md`.

## What still stands

Two related observations the reviewer made, both recorded as fair:

- **`ania_median_anchor_rank = 0.9965` is the selection objective, not evidence.** It is guaranteed
  by construction, exactly as the potency portfolio's mean-MIC advantage is guaranteed by its own.
  Counting both as "axes we lead on" overstates the case. Strip the gamed axes and the residual
  comparison is close to a wash.
- **Diversity reduces variance, not expected value.** By linearity of expectation, portfolio
  diversity does not change the expected number of active peptides in a random 25-draw — only its
  spread. Since this entry is marginally *behind* on expectation, preferring the lower-variance
  portfolio is the right choice for placing and the wrong one for winning outright. The simulated
  effect is large (12.15 vs 2.70 expected distinct 0.60-families in a 25-draw) but it should not be
  listed alongside breadth as though it were the same kind of advantage.

## Why the finalist was kept

Every alternative is worse on the decisive axes. All three sit at **exactly** the 0.800000 novelty
limit with zero margin, passing only because the rule is a strict `>`; this entry is the only one
of the four with headroom. Both higher-potency alternatives are AMP-Diffusion derivatives, and the
starter kit calls AMP-Diffusion the baseline "excluded from rankings" — so switching would trade a
0.7-percentage-point breadth difference, well inside the documented noise of the predictor class,
for direct exclusion exposure.
