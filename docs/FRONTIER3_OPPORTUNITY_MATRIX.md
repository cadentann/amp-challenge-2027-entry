# Final frontier campaign — opportunity matrix and status

Pre-registration `1f912e1d40382c292ca3b21ce8ed3b09adfc907543b60ba8283f0ff74686eaf0`, frozen
2026-09-26T04:14:15Z before any result below was computed. Budget at start **$9.1639**, reserve
**$2.10**, exploration ceiling **$7.05**.

| lane | expected value | cost | changed the finalist? | status |
|---|---|---|---|---|
| **12 — rule-ambiguity defense** | HIGH | $0 | No — **removed two risks** | **DONE, favourable** |
| **4 — homology / OOD generalization** | HIGH | $0 | No — strongest support found | **DONE, favourable** |
| **5 + 5b — predictor dependence** | HIGH | $0 | No — refuted the switch it suggested | **DONE, adverse then vindicating** |
| **2 — random-subset robustness** | HIGH | $0 | No — trigger fired, unactionable | **DONE, diagnostic** |
| **14 — category evidence strength** | MEDIUM | $0 | No | **DONE, diagnostic** |
| 1 — fresh full-scale holdout seeds | HIGH | ~$1.5 GPU | pending | **BLOCKED — no GPU capacity** |
| 7 — search-opportunity saturation | MED-HIGH | rides on 1 | pending | blocked with Lane 1 |
| 3 — safety frontier | MEDIUM | $0 | No | closed: screen exists, unreliable, selector frozen |
| 8 / 9 — developability, chemotype | MEDIUM | $0 | No | measured and disclosed |
| **13 — validator fuzzing** | MEDIUM | $0 | No — **found a real defect** | **DONE** |
| **(unplanned) predictor reliability on measured MIC** | HIGH | $0 | No — supported the design | **DONE, major** |
| 6 — Pareto portfolio | conditional | — | — | closed: no credible safety signal to build on |
| 10 / 11 — new generator, mixtures | MEDIUM | — | — | closed on time and eligibility risk |

Spend so far: **$0.07**, on a pod that never booted and was terminated. Every completed lane cost
nothing because the 48,133-member score matrix was already on disk.

## What the campaign changed

**Nothing about the shipped artifacts.** `top.fasta` remains `ece3b706…`. The selector was frozen
before any of this and was not touched. Four of the five completed lanes could not have promoted
anything by their own pre-registered terms; the fifth fired a trigger that turned out to be
unactionable for reasons fixed in advance.

What changed is what we **know**, and three of those changes are material:

1. **Two shipped "unresolved" rule questions are closed, both in our favour.** Sampling is 25 from
   the top-100. The proposal's alternative novelty rule was evaluated for the first time — MarLys
   turned out to be obtainable — and we pass it with a maximum identity of 68.7% and zero exact
   matches across all 50,000 peptides, while **both higher-potency alternatives fail it**.
2. **The out-of-distribution question is answered.** The selector's lift over a random draw from the
   *same homology stratum* is largest (z = +16.9) in the stratum farthest from 103,143 known AMPs,
   and not one of our 100 peptides comes from the ≥70%-identity strata although 2,129 such
   candidates existed with the highest random-baseline activity of any stratum.
3. **A real sensitivity was found and disclosed.** Under ±1 percentile point of predictor rank error
   about half the top-100 would change. The frozen selector is nonetheless the most stable of the
   three options tested by a wide margin — 88/100 retention where APEX-only ranking manages 7/100 —
   and the APEX-only alternative that looked 0.146 better on GN breadth falls *below* it under five
   points of error.


## Two results that were not on the original lane list

**Predictor reliability, measured.** The entry's dominant uncertainty was a citation. It is now a
measurement: against 906 peptides with measured MIC held out of ANIA's training set, **both**
predictors have R² at or below zero on log10 MIC, so AMPBench-MT's "R² < 0.30" was optimistic and
**absolute predicted MIC carries no absolute meaning**. What survives is rank signal and threshold
classification — and there the two predictors turn out to be complementary in exactly the way
`CONSENSUS_FIXED` combines them: APEX is a high-precision near-zero-recall filter (precision 0.89–1.00,
lift 1.7–2.5×), ANIA a calibrated high-recall predictor (recall 0.72–0.85). This **inverts** the
documentation's assumption that APEX was the stronger signal, and retrospectively supports the frozen
design against the APEX-only alternative Lane 5 appeared to favour. It also found one weak spot: APEX
on *E. faecalis* has Spearman −0.055, no signal, and that head feeds our MDR breadth figure.

**A packaging defect, found by running on a second platform.** `scripts/prepare_entry.py` installed
the **Linux** runtime lock on macOS — it detected the platform correctly, matched the macOS
equivalence receipt correctly, then copied the Linux lock anyway, and the final hash check passed
because that Linux lock is precisely what `FINALIST.lock.json` pins. The Linux clean-room run could
not have caught it. Fixed: the script now refuses on any platform other than Linux/x86_64, explains
why, and re-asserts the platform before copying. The entry was always Linux-only — one pinned runtime
lock, and no macOS runtime lock was ever validated — but nothing said so. The README now does.

## Spend

**$0.07 total**, on a pod that never booted. Every completed lane cost nothing: the 48,133-member
score matrix was already on disk, and the two new measurements needed only public data (QMAP, MarLys)
and a locally built scorer runtime.

## Still open

**Lane 1 — fresh full-scale holdout seeds.** The one HIGH-EV question the existing data cannot
answer: is the edge a property of the method or of seed 42? It needs GPU generation and Community
capacity has been unavailable since 04:28Z. A retry loop is running and arms a shutdown watchdog the
instant a pod is created. The pre-registered outcomes — SUPPORTS / WEAKENS / SEED-42-LUCKY — are
fixed, and a SEED-42-LUCKY result would not change the shipped artifacts but would have to be
recorded prominently in `LIMITATIONS.md`.
