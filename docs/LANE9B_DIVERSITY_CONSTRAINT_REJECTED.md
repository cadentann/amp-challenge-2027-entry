# Lane 9b — a diversity constraint was tested and rejected by its own pre-registered rule

Pre-registered 2026-09-26T21:28:32Z, sha
`1c1eb7ca997d6c912084491e5ffd883e002ce4ddcbdceb7c4381c48ba0c7e320`, before any result was computed.
Run on the **three fresh holdout seeds only**; seed 42 excluded so this could not become post-hoc
tuning on exposed data. `CONSENSUS_FIXED` was not modified — the constraint filters its ordered output.

This was the last genuinely unexplored avenue in the campaign: Lane 9 measured chemotype concentration
and Lane 2 measured its consequence for random 25-draws, but neither ran the test Lane 9 specified.

## Result

Family-capped greedy acceptance over the selector's ranked list, at `T = 0.60` with `K = 5` (mild) and
`K = 3` (strict).

| seed | variant | GN@16 | Δ | families per 25-draw | Δ | 5th-pct GN@16 | Δ | largest family |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 8191 | baseline | 0.5171 | — | 9.45 | — | 0.4686 | — | 64 |
| | mild | 0.4886 | −0.0286 | 21.25 | +11.80 | 0.4457 | −0.0229 | 5 |
| | strict | 0.4786 | −0.0386 | 22.78 | +13.33 | 0.4343 | −0.0343 | 3 |
| 6007 | baseline | 0.4714 | — | 9.38 | — | 0.4229 | — | 66 |
| | mild | 0.4671 | −0.0043 | 21.35 | +11.97 | 0.4229 | +0.0000 | 5 |
| | strict | 0.4743 | **+0.0029** | 23.00 | +13.62 | 0.4286 | **+0.0057** | 3 |
| 4423 | baseline | 0.5129 | — | 9.54 | — | 0.4686 | — | 65 |
| | mild | 0.4829 | −0.0300 | 21.86 | +12.33 | 0.4343 | −0.0343 | 5 |
| | strict | 0.4643 | −0.0486 | 23.13 | +13.59 | 0.4229 | −0.0457 | 3 |

Averaged across the three seeds, against the rule fixed in advance:

| variant | Δ families (need ≥ +3.0) | Δ 5th-pct GN (need > 0) | Δ GN@16 (need ≥ −0.010) | meets all three |
|---|---:|---:|---:|---|
| mild `T0.60 K5` | **+12.03** ✓ | **−0.01905** ✗ | **−0.02095** ✗ | **No** |
| strict `T0.60 K3` | **+13.52** ✓ | **−0.02476** ✗ | **−0.02809** ✗ | **No** |

**REJECTED.** Both variants fail two of the three pre-declared conditions.

## What this actually taught us, which is more than the verdict

**The constraint works spectacularly on the metric it targets.** Expected distinct 0.60-linked families
in a random 25-draw goes from ~9.4 to ~22 — the largest family in the portfolio drops from 64–66 out of
100 to 5 or 3. If family coverage were the objective, this is a large, reliable, replicated win.

**And it still loses, because the tail gets *worse*, not better.** This is the result worth recording.
The intuition for a diversity constraint is that it protects against a correlated failure mode — one bad
chemotype taking down a whole draw. The 5th-percentile GN breadth tests exactly that, and it **fell** by
0.019 to 0.025. Forcing the acceptance of lower-ranked peptides lowers the entire distribution, tail
included; it does not trade mean for variance, it pays mean *and* tail to buy family count. Lane 2 had
already stated, from linearity of expectation, that diversity cannot raise the expected number of
actives. This shows it does not protect the downside either, at least as measured by predicted breadth.

**One seed dissents, and that is informative about how thin this is.** On s6007 the strict variant is
*better* on both breadth (+0.0029) and tail (+0.0057). If this had been tested on one seed instead of
three, the sign of the conclusion would have depended on which seed. It is a good illustration of why
the pre-registration required averaging over all three.

**An incidental finding about the shipped entry.** Baseline largest-family sizes on the holdout seeds are
64, 66 and 65 of 100. Seed 42's is **51**. So the shipped portfolio is *less* chemotype-concentrated than
all three fresh seeds — the concentration disclosed in `LIMITATIONS.md` is real, and it is milder in the
entry we ship than in a typical draw from the same method.

## Consequence for the entry

**None. Nothing is changed.** The constraint failed its own bar, so there is no option to surface and no
trade-off for the operator to weigh. Had it passed, adoption would still have required regenerating and
re-validating the entry — invalidating the byte-identical replication, the cross-architecture
reproduction and the clean-room validator receipt — and that cost would have been stated explicitly.

With this closed, **portfolio design is exhausted** alongside the other avenues. See
`FRONTIER_LEDGER.md`.

Evidence: `experiments/LANE9B_DIVERSITY_CONSTRAINT.json`.
