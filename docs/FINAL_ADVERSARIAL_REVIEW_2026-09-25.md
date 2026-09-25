# Final independent adversarial review

Supersedes the earlier review, which was written against the E=5000 entry. Written adversarially:
the case against the entry comes first and is not softened.

**DECISION: the promoted full-opportunity AMP-Prompt + `CONSENSUS_FIXED` entry ships. The margin
over the alternatives is now broad rather than narrow, but it is still not dominant, and the
residual weakness is real.**

---

## 1. The strongest case AGAINST this entry

**It still loses on mean predicted potency.** APEX mean MIC 73.46 µM versus the potency-ranked
AMP-Diffusion portfolio's 57.06 µM. That gap did **not** close when search opportunity was
equalised, and it is the one metric where the alternative remains clearly ahead.

**Breadth parity is marginal, not victory.** GN@16 0.4843 vs 0.4914 (−0.0071); all-11@16 0.3991 vs
0.4009 (−0.0018). We are behind, if barely, on the metrics closest to the challenge's own
MIC ≤16 µM criterion.

**Everything rests on predictors of known poor generalisation.** AMPBench-MT (2026) reports MIC
regression **R² < 0.30** once train/test are separated at 30% identity. QMAP (2026) reports limited
progress over six years and poor high-potency MIC regression. Our selector consumes exactly this
class of model. A sceptic can reasonably say none of these portfolio differences is trustworthy.

**Safety is unmeasured.** No haemolysis or selectivity evidence *gates* this entry — the selector
is frozen and carries no safety axis. A predicted screen (HemoPI2 v1.3) was run afterwards on all
four portfolios and found no gross outliers, but QMAP (2026) reports low predictability for
hemolysis specifically and the binary call fires for 85–96% of every portfolio, so it does not
discriminate. The "Optimal Selectivity" category is scored on **measured** HC50/MIC50, of which we
have none.

**The tournament was never completed.** ARCADIAMP closed by futility with an unscored third seed;
BroadAMP-GPT killed in one configuration; AMPGen reproducible but killed on time; EBAMP/MOFormer
assets unavailable. This is the best of what was testable, not the winner of an exhaustive search.

## 2. The case FOR

**Full opportunity changed the picture materially.** Under a protocol frozen before any score was
computed, the same generator and same unchanged selector at full search opportunity moved GN@16
from 0.3786 → **0.4843**, closing 94% of the gap to the potency comparator, and passed all six
pre-declared criteria including two it could easily have failed (ANIA preservation, diversity).

**It now leads on more axes than it trails.** Gram-positive breadth (0.2500 vs 0.2425), MDR
breadth (0.4575 vs 0.4475), ANIA EC/PA log10 MIC (−0.4624 vs +0.6930), ANIA anchor rank (0.9965 vs
0.6767), internal diversity (113 vs 333 pairs), novelty margin (0.0353 vs the superseded entry's
0.0000).

**Diversity is a real competition mechanism, not a nicety.** The organizers draw 25 peptides at
random from the advancing list. A portfolio with 333 internally similar pairs concentrates its risk
in a way one with 113 does not.

**Homology red team favours this entry.** Its predicted GN breadth is essentially uncorrelated with
proximity to known antibacterials (Spearman **+0.058**, and **+0.011** on APEX mean MIC) while V3's
is strongly correlated (+0.341, and −0.518 on potency) and the potency portfolio's is +0.180. The
potency portfolio also sits nearer known actives overall (mean 0.713 vs **0.6668**; 98% vs 96% have
a ≥0.60 neighbour). Its edge is the kind most exposed to the homology-controlled reliability
collapse above. These are the shipped entry's own values; earlier drafts quoted the superseded
E=5000 entry's by mistake, and the proximity gap is smaller than those implied.

**Eligibility.** The starter kit calls AMP-Diffusion the baseline "excluded from rankings". Both
higher-potency alternatives are AMP-Diffusion derivatives; this entry is not.

**Engineering is complete and verified.** End-to-end twice, byte-identical, matching an independent
reimplementation exactly; R-free scorer proven exactly equivalent on both platforms across 510,000
values each; all four unchanged official checks pass against the *correct* reference sequences.

## 3. Defects found in this phase — both mine

**D1 — invalid compliance verification (mine).** `_read_fasta` returns `(headers, sequences)`; my
script unpacked it backwards, so `_verify_no_overlap` and `_veritfy_max_simularity` ran against
FASTA headers and passed meaninglessly. Corrected. Consequence: the superseded E=5000 entry was
sitting at **exactly** the 0.80 novelty limit with **zero margin**, which nobody knew. The promoted
entry has 0.0353.

**D2 — `uv sync` failure (found earlier, fixed).** transformers 4.24.0 pulls `tokenizers` with no
CPython 3.12 wheel; the organizers' first command would have failed. Fixed by an override
reproducing the environment that was actually validated.

Both were caught by running the real thing rather than trusting the artifacts. No other material
computational defect was found.

## 4. Attack surfaces

| attack | finding |
|---|---|
| Proxy gaming | Present and symmetric — each portfolio leads on its own objective family. Ours now leads on ANIA *and* ties on APEX breadth. |
| Leakage / homology | **Tested.** This entry has the weakest leakage signature of the three; V3 the strongest. |
| Predictor reliability | **Acknowledged as the dominant uncertainty.** R² < 0.30 under homology control. |
| Family concentration | 113 pairs ≥0.60, none ≥0.80; largest 0.60-linked component 51/100. Better than the potency list (333 pairs, 93/100) but **not** best overall — V3 has 0 pairs and 100 singletons. |
| Novelty | Passes with 0.0353 margin under the official metric — the **only** one of the four with any margin; the other three sit at exactly 0.800000. Unevaluated under the PDF's alternative. |
| Seed robustness | Seven independent seeds, consistent direction at matched opportunity. |
| Reproducibility | Two byte-identical end-to-end runs; independent reimplementation agrees exactly. |
| Portability | Decision-stability PASS; bit-equivalence FAIL, retained and not claimed. |
| Eligibility | Clean for this entry; unresolved for both alternatives. |
| Search opportunity | **Resolved.** Was the largest confound; now equalised and measured. |
| Search intensity vs signal | **Tested after the fact.** Against 10,000 random draws of 100 from the same 48,133-member universe, the selector is +26.4 sd on GN@16 and beats the best draw by 3.4×. The gain is not an artefact of sampling more. See `NULL_CONTROL.md`. |
| Objective gaming, restated | ANIA anchor rank is the selection objective, not evidence for it — it is guaranteed by construction, exactly as the comparator's mean-MIC lead is. Counting it as a "win" overstates the case; §2 above does so and should be read with that discount. |

## 5. What would overturn this

- An organizer statement that AMP-Diffusion derivatives **are** rankable, combined with mean
  predicted MIC mattering more than breadth — then the potency portfolio is the better entry.
- Evidence that APEX mean MIC transfers to the measured panel materially better than breadth,
  ANIA and diversity do.
- Measured HC50 evidence showing our top-100 contains haemolytic outliers. The predicted screen
  found none, but it is not a predictor worth trusting on this endpoint.

## 6. Verdict

Ship the promoted entry. It is not dominant — it trails on mean predicted potency and is marginally
behind on breadth — but it leads on Gram-positive and MDR breadth, both ANIA endpoints, diversity,
novelty margin, homology robustness and eligibility, and it is the only candidate with
prospectively gated, replicated evidence and complete engineering validation.

No biological superiority is claimed. Safety and selectivity are UNKNOWN. Competition performance
is unknown. V3 remains preserved, unchanged, as the validated fallback.
