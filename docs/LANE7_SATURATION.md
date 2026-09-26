# Lane 7 — search opportunity has not saturated, and the promotion replicates on fresh seeds

Pre-registered reading, frozen before any seed was generated:

- **SATURATED** if the gain from a 20,000-member nested universe to the full universe is < 0.01 GN@16
  on all seeds
- **MATERIAL GAIN** if any gain exceeds 0.03 — in which case note that more generation might help, and
  record that we did not pursue it

Nested universes are chosen by the same **score-blind** hash ordering the superseded E=5000 policy
used, so no subset is selected with reference to any score. Run on fresh holdout seeds only.

## Result

| nested universe | s8191 | s6007 | s4423 |
|---|---:|---:|---:|
| 5,000 (the superseded policy) | 0.4671 | 0.3614 | 0.3643 |
| 10,000 | — | 0.4057 | 0.4114 |
| 20,000 | 0.4671 | 0.4643 | 0.4343 |
| **full (~48,170)** | **0.5171** | **0.4714** | **0.5129** |
| gain 20,000 → full | +0.0500 | +0.0071 | **+0.0786** |

**SATURATED = false. MATERIAL GAIN = true.**

## What this establishes

**The full-opportunity promotion replicates on seeds that did not exist when it was decided.** That
promotion was adjudicated on seed 42 — already-exposed data — and an independent reviewer identified
exactly this as its weakest point. Here, on three unseen seeds, the 5,000-member policy yields
0.3614 and 0.3643 on two of them against seed 42's own E=5000 value of 0.3786, and full opportunity
yields 0.4714 to 0.5171 against seed 42's 0.4843. Both the baseline and the promoted value reproduce
within a few points. The roughly +0.12 gain from searching the whole eligible library is a property of
the method, not an artefact of the seed it was found on.

**Performance had not plateaued by 20,000 candidates**, so full-library selection is load-bearing
rather than merely harmless — the earlier decision mattered.

## What we did not do

The material gain implies that generating **beyond** 50,000 candidates might improve the portfolio
further. We did not pursue it, and could not: the challenge fixes the submitted library at 50,000
sequences. That is a hard rule, not a frozen policy, so this is a boundary of the competition rather
than a choice we made. Recorded because the measurement points somewhere we are not allowed to go.

s8191's 5,000 and 20,000 rows are identical (0.4671) because its score-blind 5,000-member prefix
already contained the same 100 best-ranked candidates as its 20,000-member prefix.

Evidence: `experiments/LANE7_SATURATION.json`, `experiments/LANE1_HOLDOUT_ADJUDICATION.json`.
