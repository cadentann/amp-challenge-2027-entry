# Lane 9b pre-registration — does a diversity constraint on top of the frozen selector help?

Written and hashed **before any result was computed**. Thresholds here are not revisable afterwards.

## Why this is being run

Lane 9 quantified chemotype concentration in the shipped top-100 (five residues are 78.4% of it; half
the portfolio falls in one 0.60-linked component) and Lane 2 measured the consequence for the
organizers' sampling (12.16 distinct 0.60-families per random 25-draw against the potency portfolio's
2.69). **Neither ran the test Lane 9 itself specified**: whether a *prospectively defined* diversity
constraint applied on top of the unchanged selector would improve subset robustness without destroying
predicted breadth. This closes that gap. It is the last genuinely unexplored avenue in the goal's list.

## What is and is not on the table

- `CONSENSUS_FIXED` is **frozen** and is not modified. The constraint operates strictly as a
  *re-ranking filter on the selector's own ordered output*, never as a change to the selector.
- Tested on the **three fresh holdout seeds only** (8191, 6007, 4423). Seed 42 is the shipped artifact
  and is excluded, so this cannot become post-hoc tuning on exposed data.
- The shipped entry is **not** changed by this lane regardless of outcome. A positive result becomes a
  documented, costed option for the operator, not an adopted change.

## The constraint, defined now

Greedy diversity-capped selection over the frozen selector's ranked output:

> Walk the selector's ordered candidate list from rank 1. Accept a candidate unless it has
> `Levenshtein.ratio >= T` to an already-accepted peptide **and** that would make the accepted set
> contain more than `K` members of the same 0.60-linked family. Stop at 100.

Two parameter settings, both fixed here, no others to be tried:

- **Mild:** `T = 0.60`, `K = 5`
- **Strict:** `T = 0.60`, `K = 3`

## Metrics

On each seed, for baseline (unchanged top-100) and both constrained variants:

1. GN breadth@16 of the 100
2. Expected distinct 0.60-families in a random 25-draw (100,000 Monte Carlo draws)
3. 5th percentile of GN breadth@16 across those draws (tail robustness)
4. Largest 0.60-linked component in the 100

## Pre-declared decision rule

A constrained variant is **worth surfacing to the operator as an option** only if, averaged over all
three holdout seeds, it simultaneously:

- **increases** expected distinct families in a 25-draw by **≥ +3.0**, and
- **increases** the 5th-percentile GN breadth@16 (tail improves, not just the mean), and
- costs **≤ 0.010** of GN breadth@16 on the full 100.

If no variant meets all three, this lane is **closed as unproductive** and the frontier is declared
exhausted on portfolio design.

Even if a variant meets all three, it is **not adopted here**. Adoption would require regenerating and
re-validating the entry, which would invalidate the byte-identical replication, the cross-architecture
reproduction and the clean-room validator receipt. That trade would be the operator's call and the
costs are to be stated explicitly.

## Stated in advance

By linearity of expectation, a diversity constraint **cannot** increase the expected number of active
peptides in a draw. Any benefit is variance, tail and family-coverage only, and must be reported as
such. The constraint necessarily accepts lower-ranked peptides, so a breadth cost is expected; the
question is its size.
