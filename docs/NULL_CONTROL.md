# Null control — is the full-opportunity gain selection signal, or just searching harder?

Run in response to the independent review, which identified this as the strongest unaddressed
objection: promoting from a score-blind 5,000-member pool to all 48,133 eligible members searches
9.6× harder against predictors with documented R² < 0.30 under homology control, and **no baseline
existed anywhere in the evidence** showing how much of the resulting gain was selection signal
rather than search intensity.

## Method

The comparison is against the only fair control: **random selection of 100 peptides from the exact
same 48,133-member scored universe**, 10,000 independent draws, seed 20260925. Nothing is
regenerated and nothing is rescored — this reuses the scores the selector itself consumed, so the
only thing that varies is how the 100 are chosen.

Also computed: the **achievable ceiling**, the mean of the best 100 members of that universe on
each metric, which is the most any selector could extract.

## Result

| metric | selector | random mean (sd) | best of 10,000 random draws | z | p | ceiling |
|---|---:|---:|---:|---:|---:|---:|
| **GN breadth@16** | **0.4843** | 0.0709 (0.0157) | 0.1443 | **+26.4** | <0.0001 | 0.8600 |
| **all-11 breadth@16** | **0.3991** | 0.0687 (0.0131) | 0.1291 | **+25.2** | <0.0001 | 0.6391 |
| **APEX mean MIC (µM, lower better)** | **73.46** | 228.38 (12.65) | 185.57 | **−12.2** | <0.0001 | 34.62 |

The selector's top-100 has **6.8× the Gram-negative breadth of an average random 100** from the
identical universe, and **3.4× the best of ten thousand random draws**. Not one draw in 10,000 came
within half of it on any metric.

Against the ceiling, `CONSENSUS_FIXED` captures **52%** of the available GN-breadth headroom, **58%**
of the all-11 headroom and **80%** of the mean-MIC headroom. It does not capture more because it is not optimising either
metric: it ranks on worst-case percentile across APEX *and* ANIA, breaking ties on predictor
disagreement. A selector targeting GN@16 directly would reach 0.86 — and would be exactly the
proxy-gaming the frozen design avoids.

## What this does and does not establish

**It does establish** that the selection step extracts large, real structure from the predictor
outputs. The full-opportunity gain is not an artefact of drawing more samples: drawing more samples
*at random* from the same universe gets nowhere near it. Searching 9.6× harder produced a better
portfolio because there was signal to find, and the frozen selector found it.

**It does not establish that the predictors are right.** This control holds the predictors fixed
and asks only whether the selector beats chance *given* them. It says nothing about whether
predicted MIC transfers to the organizers' measured panel. AMPBench-MT's R² < 0.30 under
homology-controlled splits remains the dominant uncertainty in this entry, and this result does not
touch it. A selector can be excellent at maximising a proxy that turns out not to predict reality.

**It does not retroactively justify the promotion.** The promotion was decided under six criteria
frozen before any score was computed (`HEV1_FULL_OPPORTUNITY_PROTOCOL.md`); this control was run
afterwards, at a reviewer's request, and is reported as such. Had it come out the other way it
would have been a serious problem for the entry, which is why it is worth having run.

Evidence: `evidence/NULL_CONTROL.json`.
