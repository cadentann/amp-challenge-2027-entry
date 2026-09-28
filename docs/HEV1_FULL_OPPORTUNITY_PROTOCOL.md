# HIGH-EV #1 — Full-opportunity AMP-Prompt: prospectively frozen protocol

**FROZEN BEFORE ANY RESULT IS COMPUTED.** No threshold, metric, comparator or promotion rule in
this document may be changed after outcomes are seen. If the rule is not met, the current E=5000
entry remains the finalist and this branch is closed.

## 1. Why this is a legitimate new experiment, not a post-hoc policy switch

The existing entry's `E=5000` policy was earned by a prospectively frozen scale test and is frozen.
The governing proposal forbids **re-choosing** the pool size for that entry after seeing outcomes.

This experiment does not edit that entry. It defines a **separate candidate** under its own
prospectively frozen promotion rule, declared here before computation. The incumbent remains
submission-ready and untouched throughout. Only if this candidate clears every criterion below
does it become the finalist; otherwise it is recorded as a closed negative branch.

The motivating observation is documented and quantified: the delivered entry ranked its top-100
from 5,000 candidates while the AMP-Diffusion potency comparator ranked from 50,000 — **10% of the
search opportunity**. That asymmetry is a confound in the product comparison, not a defect in the
selector.

## 2. Hypothesis

At comparable search opportunity, AMP-Prompt + frozen `CONSENSUS_FIXED` closes the APEX
Gram-negative breadth gap against the potency comparator **while preserving** its ANIA advantage,
novelty and portfolio diversity.

## 3. Frozen inputs — nothing regenerated

| item | value |
|---|---|
| Generator | unchanged released AMP-Prompt, commit `07d455dd`, checkpoint `47944ff4…` |
| Generation | **none**. Reuses the existing seed-42 run, raw `cb3aa9cf…`, 65,536 raw **ceiling**, 51,712 attempts actually made |
| Library | the existing delivered `library.fasta`, `a91c0de9…`, 50,000 unique |
| Selection universe | `full_library` — **all** top-eligible library members (48,133) |
| Selector | unchanged `CONSENSUS_FIXED`, source `963085dd…` |
| Anchor | unchanged 996-member anchor `fe438eab…` |
| top_k | 100 |
| Predictors | unchanged APEX8/ANIA3, runtime manifest `ecacbe1e…`, batch 32, 2 threads, CPU |
| Eligibility | unchanged frozen rules, reference `cbbeac64…` |

`full_library` is an explicitly supported value of `selection_universe` in the entry's own lock
schema, so this is a supported configuration, not a modification of the pipeline.

## 4. Comparators (all already computed, common-context scored)

- **INCUMBENT** — current delivered entry, E=5000 top-100 (`ea90c75a…`)
- **POTENCY** — original mean-MIC AMP-Diffusion top-100
- **V3** — official validated fallback top-100

## 5. Metrics reported (full battery, adverse values included)

APEX per-head and ensemble; GN / all-11 / GP / MDR breadth at 8, 16, 32; top-50 prefix of each;
mean predicted MIC; APEX GN and GP mean log10 MIC; ANIA EC/PA/SA log10 MIC; ANIA median
fixed-anchor rank; official Levenshtein novelty vs `antibacterial.fasta`; internal pairwise
similarity pairs at ≥0.60 and ≥0.80; largest family80 fraction; length; charge; hydrophobicity;
amino-acid composition; predictor disagreement.

## 6. PROMOTION RULE — all six must hold

The full-opportunity candidate replaces the incumbent **only if every one of these holds**:

1. **Primary gain.** top-100 APEX GN breadth@16 improves over the INCUMBENT by **≥ +0.05**.
2. **No aggregate regression.** top-100 all-11 breadth@16 is **≥** the incumbent's, and top-50 GN
   breadth@16 is **≥** the incumbent's.
3. **ANIA preserved.** top-100 ANIA median fixed-anchor rank declines by **no more than 0.02**
   versus the incumbent, and ANIA EC/PA mean log10 MIC does **not** worsen by more than 0.05.
4. **Diversity not collapsed.** internal pairs at ratio ≥0.60 is **< 333** (strictly better than
   the potency comparator's documented redundancy) **and ≤ 232** (within 2× the incumbent's 116).
   No pair at ≥0.80.
5. **Novelty.** zero violations of the official rule (`Levenshtein.ratio > 0.80` vs the reference
   set), evaluated with the unchanged official validator function.
6. **Completeness.** exactly 100 unique sequences, all with complete APEX and ANIA scores, and the
   top-100 is a subset of the delivered `library.fasta`.

**Kill criterion.** Failure of any single criterion closes this branch. No criterion may be
relaxed, no metric substituted, no additional seed added to rescue it.

**Tie/ambiguity.** If criterion 1 is met but any of 2–6 fails, the result is recorded as
UNRESOLVED-NOT-PROMOTED and the incumbent stands. There is no partial promotion.

## 7. If promoted

The promoted candidate must then pass, before it can ship: end-to-end `uv run generate` twice with
byte-identical output, unchanged official validator file checks, and an independent adversarial
review. Any failure reverts to the incumbent.

## 8. Eligibility note

Changing the selection universe does not change the generator, model identity, or training data.
It is the same model under a different, already-supported selection configuration. This does not
create a multi-generator hybrid and does not alter the entry's eligibility posture.

## 9. Expected information value

High. This is the single largest unresolved confound in the finalist decision. It resolves whether
the incumbent's APEX deficit is a genuine weakness of the generator+selector or an artefact of
restricted search. Either outcome is decision-relevant: promotion yields a materially stronger
entry; failure converts a suspected confound into a measured, closed negative result.

Cost: local Mac CPU scoring of ~48,133 candidates. No cloud compute. No new generation.
