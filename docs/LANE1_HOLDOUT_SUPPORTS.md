# Lane 1 — fresh full-scale holdout: SUPPORTS, and seed 42 is slightly conservative

The one question the existing data could not answer: is the entry's predicted advantage a property of
the **method**, or did seed 42 happen to be lucky? Answered on three seeds that did not exist when any
policy decision was made.

Criteria frozen **2026-09-26T04:14:15Z**, pre-registration sha
`1f912e1d40382c292ca3b21ce8ed3b09adfc907543b60ba8283f0ff74686eaf0`, before any seed was generated:

- **SUPPORTS** if all three fresh seeds reach GN breadth@16 ≥ 0.40
- **WEAKENS** if any falls below 0.35
- **SEED-42-LUCKY** if the fresh mean is below 0.42

## Method

Seeds `8191`, `6007`, `4423`, named in the pre-registration before generation. Each ran the **full**
pipeline at production scale: 65,536-attempt ceiling, unchanged eligibility, 50,000-member library,
every eligible member scored, unchanged `CONSENSUS_FIXED` selection.

**Each holdout lock differs from the shipped lock in exactly one field, `generation_seed`** — verified
programmatically on the pod and again locally. Selector, anchor, decoder settings, raw ceiling,
eligibility rules, selection universe, scorer-runtime pin and reference set are byte-identical. All
three ran to `COMPLETE` with exit 0 on an RTX 3090.

## Result

| metric | s8191 | s6007 | s4423 | **shipped s42** | fresh mean |
|---|---:|---:|---:|---:|---:|
| **GN breadth@16** | **0.5171** | 0.4714 | **0.5129** | 0.4843 | **0.5005** |
| all-11 breadth@16 | **0.4200** | 0.3918 | **0.4173** | 0.3991 | 0.4097 |
| GP breadth@16 | 0.2500 | **0.2525** | 0.2500 | 0.2500 | 0.2508 |
| MDR breadth@16 | **0.4750** | 0.4500 | **0.4750** | 0.4575 | 0.4667 |
| APEX mean MIC (µM) | **73.15** | 75.32 | 75.08 | 73.46 | 74.52 |
| ANIA EC/PA log10 | **−0.4681** | −0.4488 | **−0.4686** | −0.4624 | −0.4618 |
| scored universe | 48,172 | 48,176 | 48,166 | 48,133 | — |

**Verdict: SUPPORTS = true. WEAKENS = false. SEED-42-LUCKY = false.**

All three clear 0.40 with room to spare. The nearest approach to the 0.35 failure floor is 0.4714 —
not close. And `shipped_minus_fresh_mean = −0.0162`: **seed 42 is slightly below the fresh average**,
the opposite of the lucky-seed failure mode. The method replicates.

## Two of the three fresh seeds beat the shipped entry. We are not switching.

s8191 (0.5171) and s4423 (0.5129) both exceed seed 42's 0.4843 on the primary metric, and s8191 is
better on mean predicted MIC as well. The pre-registration anticipated this and forbids acting on it:

> Do not replace the final seed merely because another fresh seed looks prettier.

Switching now would be post-hoc seed selection on data generated to *test* robustness, not to choose a
winner. It would destroy the prospective guarantee that makes any of these numbers meaningful, and it
would invalidate the byte-identical replication, the cross-architecture reproduction, the
decision-stability certificate and the clean-room validator receipt — all of which bind seed 42's
exact artifacts. **Seed 42 remains frozen.** The higher-scoring seeds are recorded here rather than
omitted, because a reader is entitled to know that a better-looking draw existed and was declined.

The honest reading of the spread is the useful one: GN@16 across four independent seeds is 0.4714 to
0.5171, so **roughly ±0.02 of seed-to-seed variation around a mean near 0.50.** Any comparison
between portfolios smaller than that — including the 0.0071 gap to the potency comparator that earlier
analysis agonised over — is inside seed noise and should not be treated as a real difference.

## Retained artifacts

| seed | library.fasta | top.fasta |
|---|---|---|
| 8191 | `67b17488855b47cb…` | `912d5d5c6db509d5…` |
| 6007 | `8e937201d77b29d9…` | `8925685eba9350e2…` |
| 4423 | `eefa13b073969f77…` | `ad540cecef241c94…` |

Evidence: `experiments/LANE1_HOLDOUT_ADJUDICATION.json`, per-seed bundles under
`frontier3_20260925/holdout/`.
