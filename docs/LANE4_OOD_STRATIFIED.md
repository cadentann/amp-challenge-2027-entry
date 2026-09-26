# Lane 4 — the *predicted* advantage is not explained by proximity to known AMPs

> **Scope.** Every quantity here is APEX-derived. This tests whether the selector's predicted-activity
> advantage can be explained by picking near-neighbours of known AMPs. It cannot. That rules out one
> specific failure mode; it is **not** evidence that the predictions transfer to a laboratory at any
> distance from known sequences, and the predictor audit in `PREDICTOR_RELIABILITY_MEASURED.md` found
> APEX poorly calibrated on the measured data we could obtain.

The shipped homology analysis measured the *correlation* between predicted activity and proximity to
known AMPs. It never answered the question the lane existed to ask: **does the selector's advantage
survive as candidates move farther from known AMP families?** This answers it, and the answer is the
strongest non-circular result in the campaign.

Two improvements over the shipped analysis. The reference set is **MarLys** — 103,143 sequences, the
database the organizer proposal itself names — rather than the 39,448-sequence `antibacterial.fasta`.
And the comparison is against **a random draw from the same stratum**, so proximity is held fixed
instead of being correlated away.

Identity by MMseqs2 18-8cc5c, `-s 7.5 -k 6 -c 0.8 --cov-mode 0`. 28,071 of the 48,133 universe
members (58.3%) have any alignment to MarLys at 80% coverage; the rest have none and are the farthest
stratum.

## Result

| stratum (identity to MarLys) | universe | our top-100 | our GN@16 | random from same stratum | lift | z |
|---|---:|---:|---:|---:|---:|---:|
| **no alignment (farthest)** | 20,062 | **18** | 0.4683 | 0.0349 | **+0.4334** | **+16.9** |
| <50% | 12,876 | 38 | 0.4737 | 0.0837 | +0.3900 | +14.4 |
| 50–60% | 7,713 | 33 | 0.5065 | 0.1005 | +0.4060 | +12.9 |
| 60–70% | 5,353 | 11 | 0.4805 | 0.1131 | +0.3674 | +6.3 |
| 70–80% | 1,855 | **0** | — | 0.1285 | — | — |
| ≥80% | 274 | **0** | — | 0.0996 | — | — |

## What it establishes about the predictions

1. **The lift is preserved at maximum strength in the stratum farthest from known AMPs.** Among the
   20,062 candidates with no detectable alignment to any of 103,143 known AMPs, the selector's picks
   score 0.4683 against a random-draw baseline of 0.0349 — a lift of +0.43 at z = +16.9. Eighteen of
   our hundred peptides come from that stratum.

2. **The selector's own performance is flat across strata** — 0.4683, 0.4737, 0.5065, 0.4805 — while
   the random baseline **rises** with proximity to known AMPs, from 0.0349 to 0.1285. Proximity to
   known AMPs genuinely does predict activity in this universe. The selector is indifferent to it
   anyway. That is the opposite of family recognition.

3. **Not one of our 100 peptides comes from the ≥70% identity strata**, although 2,129 such
   candidates were available and they have the *highest* random-baseline activity of any stratum. The
   frozen selector declined the easiest, most homologous route to a good predicted score. It was
   never told to: nothing in `CONSENSUS_FIXED` references similarity to known AMPs beyond the hard
   0.80 eligibility gate, which sits at a different metric and a different database.

4. Consistent with Lane 12: the maximum MarLys identity among our selected peptides is **68.7%**,
   median 50.0%, and 18 have no alignment at all.

## Honest limits

- MarLys is a proxy for APEX's and ANIA's training corpora, which are not fully obtainable. A
  peptide far from MarLys may still be near something a predictor trained on.
- Strata are defined by *our* MMseqs2 parameterisation; a different coverage threshold moves members
  between bins. The coverage setting used is MMseqs2's own default.
- GN breadth@16 is APEX-derived, so this shows the selector extracts APEX-consistent structure at all
  distances. It is not evidence that APEX is *correct* at those distances — AMPBench-MT's R² < 0.30
  under homology control is precisely a statement that it may not be. What this rules out is the
  specific failure mode of winning by picking near-duplicates of known actives.

Evidence: `experiments/LANE4_OOD_STRATIFIED.json`.
