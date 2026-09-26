# Lane 5 — predictor dependence: one adverse finding, then a decisive vindication

This lane could not promote anything by design. It was run because an adverse result here is the
kind a reviewer finds and we would rather find it ourselves. It produced both an adverse result and,
on the follow-up it forced, the strongest non-circular argument for the frozen design that exists.

**Validity control:** an independent reimplementation of `CONSENSUS_FIXED` over the 48,133-member
score matrix reproduced the shipped top-100 **exactly and in order**. Everything below is therefore
measuring the real selector.

**Declared deviation from pre-registration.** The pre-registration specified leaving out each of
the 8 APEX ensemble members in turn. That is impossible from the available data: the score matrix
stores the 8-member ensemble *mean* per strain, not per-member arrays. Substituted leave-one-out
over the 11 APEX strain heads and 3 ANIA heads, which answers the same question and is testable.
This is an infeasibility, recorded rather than quietly reinterpreted.

## Leave-one-head-out: PASSES

Removing any single strain head, APEX or ANIA, leaves top-100 overlap at **min 51, median 82,
max 96** out of 100. The pre-registered criterion was ≥50. No individual head drives the selection.

## The adverse finding

| selector | GN breadth@16 | overlap with shipped top-100 |
|---|---:|---:|
| `CONSENSUS_FIXED` (shipped) | 0.4843 | 100 |
| **APEX only** | **0.6300** | 1 |
| ANIA only | 0.1986 | 27 |

Ranking on APEX alone would give predicted Gram-negative breadth of **0.6300** against our 0.4843 —
a gap of 0.146, twenty times the 0.0071 gap to the potency comparator that earlier analysis treated
as the entry's main weakness. On its face the consensus design sacrifices a great deal of predicted
breadth to incorporate a much weaker second predictor.

And the pre-registered robustness criterion **failed**: under Gaussian rank noise at sd = 5% of the
rank range, median top-100 overlap with the shipped list was **14**, against a threshold of 60.

Both of those are reported before their context because that is the order they were found in.

## Why the first finding is circular

GN breadth@16 is computed *from APEX*. A selector that ranks by APEX will score well on an
APEX-derived metric by construction — this is the same objection an independent reviewer already
raised against citing our ANIA anchor rank as evidence, applied symmetrically. The 0.6300 is not
evidence that APEX-only selects better peptides; it is evidence that ranking by APEX optimises APEX.
The consensus selector's lower APEX breadth is the **price of not gaming APEX**, which is what it
was designed to avoid.

## Why the second finding reverses on inspection

Lane 5b applied the identical perturbation to all three selectors and asked how much of its **own**
list each retains — a comparison the pre-registered test omitted.

| rank noise sd | consensus retains | APEX-only retains | ANIA-only retains |
|---|---:|---:|---:|
| 0.002 (≈0.2 percentile points) | **88 / 100** | 7 / 100 | 71 / 100 |
| 0.01 (≈1 point) | **52 / 100** | 5 / 100 | 34 / 100 |
| 0.05 (≈5 points) | **14 / 100** | 2 / 100 | 10 / 100 |

And what happens to the headline metric under the same noise:

| rank noise sd | consensus GN@16 | APEX-only GN@16 |
|---|---:|---:|
| unperturbed | 0.4843 | 0.6300 |
| 0.002 | 0.4914 | 0.6114 |
| 0.01 | **0.4821** | 0.5236 |
| 0.05 | **0.3950** | **0.3943** |

Two things follow.

1. **`CONSENSUS_FIXED` is the most stable of the three selectors at every noise level**, by a wide
   margin — 88/100 retention where APEX-only manages 7/100. The fragility the pre-registered test
   found is a property of ranking 48,133 near-tied candidates with these predictors (mean neighbour
   spacing ~2.1e-5 on the rank scale), not a defect of the consensus design. Measured against the
   alternatives rather than against an absolute bar, the frozen design is the **best available**
   choice on exactly the axis it appeared to fail.
2. **APEX-only's advantage is not robust.** It decays from 0.6300 to 0.5236 at one percentile point
   of predictor error and to 0.3943 at five — where it sits *below* the consensus selector's 0.3950.
   Meanwhile consensus is nearly flat from 0.4843 to 0.4821. Given AMPBench-MT reports R² < 0.30 for
   MIC regression under homology control, errors of one to five percentile points are not a
   pessimistic assumption. The APEX-only edge exists only if the predictor's fine-grained rank
   distinctions are trustworthy, and the published benchmarks say they are not.

## Verdict

**KEEP the incumbent.** The selector was frozen before any of this was measured and is not changed.
The switch this lane appeared to recommend is refuted by the lane's own follow-up: it optimises a
circular metric and its advantage evaporates under the predictor error the literature documents.

**What must be disclosed** — and is, in `LIMITATIONS.md`:

> Under ±1 percentile point of predictor rank error, roughly half of the shipped top-100 would be
> replaced; at ±5 points, roughly seven eighths. This is a property of the predictors rather than of
> our selector — every alternative we tested is more fragile, and the most obvious one is far more
> fragile — but it means the specific identity of these 100 peptides should not be treated as
> precisely determined. The portfolio's aggregate predicted properties are far more stable than its
> membership: the consensus selector's GN breadth moves by 0.0022 under the perturbation that
> replaces half its members.

Evidence: `experiments/LANE5_PREDICTOR_ABLATION.json`, `experiments/LANE5B_NOISE_CONTEXT.json`.
