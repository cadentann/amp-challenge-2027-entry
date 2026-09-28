# Lane 7 — search opportunity has not saturated, and the promotion replicates on fresh seeds

Pre-registered reading, frozen before any seed was generated:

- **SATURATED** if the gain from a 20,000-member nested universe to the full universe is < 0.01 GN@16
  on all seeds
- **MATERIAL GAIN** if any gain exceeds 0.03 — in which case note that more generation might help, and
  record what we did about it

Nested universes are chosen by the same **score-blind** hash ordering the superseded E=5000 policy
used, so no subset is selected with reference to any score. Run on fresh holdout seeds only.

---

> ## Correction (this section is retained deliberately)
>
> **An earlier version of this document reported s8191's 5,000-candidate figure as 0.4671. That number
> was never measured. It was arrived at by subtracting the gain from the full-universe value
> (0.5171 − 0.05 = 0.4671), which in fact recovers the *20,000*-candidate figure, not the 5,000 one.**
> The same version left the 10,000 cell blank although the value existed, and then added an
> explanation for the apparent coincidence — that s8191's 5,000-member prefix "already contained the
> same 100 best-ranked candidates as its 20,000-member prefix". That explanation described an artefact
> of the arithmetic, not anything in the data, and it is withdrawn.
>
> The true value is **0.325714**, the *lowest* 5,000-candidate figure of the three seeds. The
> numerical record in `experiments/LANE1_HOLDOUT_ADJUDICATION.json` was correct throughout; only the
> prose was wrong.
>
> The corrected figure was re-derived by a **second, independently written implementation** reading
> the saved per-seed selections, which also confirmed that the full-universe selection reproduces each
> published `top.fasta` exactly and in order for all three seeds. Both implementations agree on every
> cell below.
>
> Correcting it **strengthens** this lane's conclusion rather than weakening it, which is the reason
> to be careful about numbers that flatter a narrative: s8191's 5,000 → full gain is +0.1914, the
> largest of the three.

---

## Result

All values GN breadth@16 of the top-100 selected by unchanged `CONSENSUS_FIXED` from each nested
universe.

| nested universe | s8191 | s6007 | s4423 |
|---|---:|---:|---:|
| 5,000 (the superseded policy's size) | **0.3257** | 0.3614 | 0.3643 |
| 10,000 | 0.4114 | 0.4057 | 0.4114 |
| 20,000 | 0.4671 | 0.4643 | 0.4343 |
| **full (48,172 / 48,176 / 48,166)** | **0.5171** | **0.4714** | **0.5129** |
| gain 20,000 → full | +0.0500 | +0.0071 | **+0.0786** |
| gain 5,000 → full | **+0.1914** | +0.1100 | +0.1486 |

**SATURATED = false. MATERIAL GAIN = true** (two of three seeds exceed the 0.03 threshold).

## What this establishes

**The full-opportunity promotion replicates on seeds that did not exist when it was decided.** That
promotion was adjudicated on seed 42 — already-exposed data — and an independent reviewer identified
exactly that as its weakest point. Here, on three unseen seeds, a 5,000-member score-blind pool yields
0.3257 to 0.3643 against seed 42's own E=5000 value of 0.3786, and full opportunity yields 0.4714 to
0.5171 against seed 42's 0.4843. Both the baseline and the promoted value reproduce within a few
points on each side. The gain from searching the whole eligible library — **+0.11 to +0.19** across
these seeds — is a property of the method, not an artefact of the seed it was found on.

**Performance had not plateaued by 20,000 candidates**, so full-library selection is load-bearing
rather than merely harmless.

**Scope of the claim.** This measures the *predicted* GN breadth of selections made from nested
subsets of the same scored universe. It shows the selector finds better-scoring peptides when given
more of that universe to search. It is not evidence that those peptides are more active in a
laboratory: every value here is an APEX-derived quantity, and the predictor audit in
`PREDICTOR_RELIABILITY_MEASURED.md` found APEX poorly calibrated in absolute terms on the measured
data we could obtain.

## The 50,000 question, stated precisely

The material gain means the curve was still rising at 20,000, so a *larger search space* helps. Two
distinct things follow, and an earlier version of this document conflated them:

1. **The submitted library is fixed at 50,000 sequences.** This is a hard requirement — the official
   validator's `_verify_sequences` enforces exactly 50,000 unique entries in `library.fasta`, and that
   is executable, not interpretive.
2. **Whether more raw candidates may be generated internally, with the best 50,000 submitted, is a
   different question and we have not found a rule that settles it.** Our pipeline already generates
   up to a 65,536 raw **ceiling** — 51,712 attempts in the production run — and submits the first
   50,000 library-valid ones in generation order; nothing
   discovered so far forbids generating more and selecting the library differently. An earlier draft
   asserted the challenge "fixes the library at 50,000, a hard rule we cannot cross" as though it
   closed avenue 2 as well. It does not.

**We did not act on this, and the reason is protocol rather than rules.** Changing how the library
itself is chosen would be a new selection policy adopted after seeing which seeds scored well — the
same post-hoc move this project has refused throughout — and it would invalidate the byte-identical
replication, the cross-architecture reproduction and the clean-room validator receipt, all of which
bind seed 42's exact 50,000. Recorded as an unexplored avenue with a stated reason, not as a
prohibition.

Evidence: `experiments/LANE7_SATURATION.json` (two seeds, written before s8191 finished),
`experiments/LANE1_HOLDOUT_ADJUDICATION.json` (all three, authoritative).
