# Frontier ledger — every avenue considered, ranked, and resolved

One place to check whether the search was actually exhausted, rather than abandoned. Every avenue is
either **tested with evidence**, or **closed with a stated reason**. Nothing is listed as "not done"
without saying why.

Total campaign spend: **$1.51**. Balance **$7.65**, zero pods running. The $2.10 completion reserve was
never touched.

## Tested, with evidence

| avenue | EV | cost | outcome | evidence |
|---|---|---|---|---|
| **Fresh full-scale holdout robustness** | HIGH | $1.44 | **SUPPORTS.** Three fresh production-scale seeds: GN@16 0.5171 / 0.4714 / 0.5129 vs seed 42's 0.4843. All clear the pre-registered 0.40 bar; fresh mean *exceeds* seed 42, so the shipped draw is mildly conservative. | `LANE1_HOLDOUT_SUPPORTS.md` |
| **Matched controls** | HIGH | $0 | Four independent matched controls run: random-from-same-universe (null control, +26 sd), random-within-homology-stratum (Lane 4), equal-search-opportunity AMP-Diffusion comparison (HEV1), and nested score-blind universes (Lane 7). | `NULL_CONTROL.md`, `LANE4_OOD_STRATIFIED.md`, `LANE7_SATURATION.md` |
| **Search-opportunity saturation** | MED-HIGH | rides on Lane 1 | **Not saturated.** 5,000 → full gains of +0.11 to +0.19 replicate on unseen seeds, independently validating the full-opportunity promotion that was originally decided on exposed seed 42. | `LANE7_SATURATION.md` |
| **Safety / selectivity** | HIGH | $0 | **Adverse to our own evidence.** Our haemolysis screen has negative R² on peptides as novel as ours and ~11% recall; 76% of the obvious evaluation set is in its training data. The clean HC50 result is uninformative, not reassuring. No credible alternative predictor exists with public weights and homology-aware evaluation. | `LANE3_SAFETY_SCREEN_IS_UNINFORMATIVE.md` |
| **Homology / OOD generalization** | HIGH | $0 | The *predicted* advantage is not explained by proximity to known AMPs: lift over a same-stratum random draw is largest (z = +16.9) farthest from 103,143 known AMPs, and none of the 100 comes from the ≥70%-identity strata. | `LANE4_OOD_STRATIFIED.md` |
| **Predictor dependence** | HIGH | $0 | Frozen selector is the **most stable** of three options under rank perturbation (88/100 retention vs APEX-only's 7/100). The APEX-only alternative that looked 0.146 better is circular and collapses under predictor error. | `LANE5_PREDICTOR_DEPENDENCE.md` |
| **Predictor reliability vs measured MIC** | HIGH | $0 | Unplanned and the most consequential: on 906 held-out peptides both predictors have R² ≤ 0, so absolute µM is uncalibrated. APEX is high-precision/near-zero-recall, ANIA calibrated/high-recall — complementary exactly as the frozen selector combines them. Found one dead head (*E. faecalis*, ρ = −0.055). | `PREDICTOR_RELIABILITY_MEASURED.md` |
| **Random-subset robustness** | HIGH | $0 | Our variance is lower and 5th percentile equal to the potency portfolio, with 12.2 vs 2.7 distinct families per 25-draw. Escalation trigger fired for an ineligible comparator; unactionable by pre-registered terms. | `LANE2_SUBSET_ROBUSTNESS.md` |
| **Developability** | MEDIUM | $0 | 0/100 solubility-risk flags against a 6.7% library base rate; zero synthesis-critical liabilities. Two adverse signals disclosed: most long hydrophobic runs of the four portfolios, and highest median net charge (+10). | `LANE8_DEVELOPABILITY.md` |
| **Portfolio design — diversity constraint** | MEDIUM | $0 | **TESTED AND REJECTED** by its own pre-registered rule. Raises families per 25-draw from 9.4 to ~22, but costs 2–3× the allowed breadth budget **and worsens the 5th percentile** — it does not buy downside protection. | `LANE9B_DIVERSITY_CONSTRAINT_REJECTED.md` |
| **Rule-ambiguity defense** | HIGH | $0 | Sampling settled (25 from top-100). Novelty rule located and measured under stated parameters — zero violations under both coverage settings tested, all four portfolios fail under a permissive one. Not a compliance determination. | `LANE12_RULE_AMBIGUITY_RESOLVED.md` |
| **Environment / deployment fuzzing** | MEDIUM | $0 | Ten cases; nine pass. The tenth found a real defect — `prepare_entry.py` installed the Linux runtime lock on macOS. Fixed, and it surfaced that the entry is Linux x86_64 only. | `LANE13_ENVIRONMENT_FUZZING.md` |
| **Category-specific evidence strength** | MEDIUM | $0 | Strongest relative standing on MDR and Gram-positive; the MDR lead survives dropping the dead head but ties on the one MDR head with measurable signal. | `PREDICTOR_RELIABILITY_MEASURED.md` |
| **Clean-clone deployment** | HIGH | prior phase | All eight unchanged official validator checks pass from a clean clone in 116 min, plus byte-identical output on a second GPU architecture. | `validator_results/CLEANROOM_VALIDATION.txt` |

## Closed without testing, with the reason

| avenue | EV | why closed |
|---|---|---|
| **New generators** (dsAMP/dsAMPGAN, deepAMP, membrane-targeting directed generation, AMPGen, ProtGPT2+MCL, MPOGAN, MOFormer, EBAMP, OmegAMP) | MEDIUM | Final documented scan found **no locatable public weights** for the 2026 candidates. Reproducing a generator from a paper description is not reproducing the authors' model and could not be honestly attributed. Even granting weights, five days cannot clear the funnel the incumbent cleared *plus* a prospective protocol. `LANE10_GENERATOR_FRONTIER_CLOSED.md` |
| **Generator mixtures** | MEDIUM | Attribution is undefined for a mixed-provenance top-100, and any AMP-Diffusion-derived component inherits an exclusion question with **no controlling public rule**. Unbounded eligibility downside for speculative gain. |
| **Pareto multi-objective portfolio** | conditional | Required a credible safety axis to build on. Lane 3 established there isn't one. |
| **Predictor recalibration** on the measured QMAP data | MEDIUM | Would create a *new* predictor and therefore a new selector — the post-hoc change the protocol forbids — and would invalidate every reproducibility receipt. Also unlikely to help: the selector consumes **ranks**, which recalibration does not change, and measured Spearman is only ~0.45. |
| **Choosing among selectors using external measured data** | MEDIUM | Genuinely *not* circular, which makes it tempting. Closed anyway: ~900 held-out peptides at ρ ≈ 0.45 cannot discriminate between selectors with useful power, and adopting a different selector after seeing results is still post-hoc, requiring full regeneration and re-validation inside five days. |
| **Alternative library construction** (generate more raw, submit the best 50,000) | MEDIUM | Lane 7 shows the curve was still rising, so this could help. The *submitted* library must be exactly 50,000 (executable), but nothing found forbids generating more internally. **Not a prohibition — an unexplored avenue closed for protocol reasons:** choosing the library differently after seeing which seeds scored well is post-hoc, and it would invalidate all validation evidence bound to seed 42's exact 50,000. Recorded honestly in `LANE7_SATURATION.md`. |
| **Switching to a higher-scoring holdout seed** | — | Two of three fresh seeds beat seed 42. **Explicitly refused** as seed-shopping on robustness data; the pre-registration forbids it and it would invalidate every receipt. `LANE1_HOLDOUT_SUPPORTS.md` |
| **Multi-seed ensemble top-100** | LOW-MED | Could be made deterministic, so the fixed-seed requirement is not the blocker. Closed because it is a method change needing its own prospective protocol and full re-validation, and because "which seed produced this entry" becomes ambiguous against a requirement for a fixed default seed with reproducible output. |
| **Further GPU work** | LOW | No remaining concrete question could change the entry or remove a submission risk. Higher scores from the same optimised predictors are not evidence, as Lane 5 and the predictor audit both demonstrate. |

## What would still change the finalist

For completeness, the things that *would* matter and are outside our reach before the deadline:

- An organizer statement that hash-pinned weight **retrieval** does not satisfy "with model weights" — that
  is a packaging fix, not a science one (`WEIGHTS_IN_REPO_OPTION.md`).
- An organizer statement that AMP-Diffusion derivatives **are** rankable, *combined with* evidence that
  mean predicted MIC transfers better than breadth, diversity and ANIA do. The predictor audit makes the
  second condition unlikely to be demonstrable.
- Any **measured** HC50 on these peptides. We have none and cannot obtain it.

## Verdict

The high-EV frontier is exhausted: every listed category has been tested, and the last unexplored one
(portfolio design via a diversity constraint) was pre-registered, run, and **rejected by its own rule**.
Remaining medium-EV avenues are each closed for a stated reason — no public weights, no controlling rule,
or a post-hoc change that would invalidate the validation evidence without prospective support. None is
likely to change the finalist before October 1.

**The entry is frozen at seed 42 with `CONSENSUS_FIXED` and full-library selection. V3 is preserved
unchanged.**
