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
| **Whole-library Phase-1 qualification (seqme)** | **HIGHEST of this phase** | $0 | **MIXED, and the adverse half is real.** Behind the AMP-Diffusion baseline on FBD (2.05 vs 1.23), MMD (12.26 vs 6.73) and AuthPct (0.870 vs 0.907) — all beyond seed noise, all replicated. **Then the negative control was run on all fourteen metrics, which corrected the reading in both directions:** a motif-destroyed shuffle beats both libraries on FBD, MMD, precision, recall and clipped density/coverage, so neither the deficit nor four of our leads are quality evidence. Only **FKEA** (we lead) and **AuthPct** (we trail) have controls that behave. No library change. | `SEQME_WHOLE_LIBRARY_AUDIT.md` |
| **Alignment-based novelty and clustering coverage (MMseqs2 vs MarLys, full 50,000)** | HIGH | $0 | **Favours the entry clearly.** 1.47% of the library is ≥80% identical to a known AMP versus the baseline's 3.82% (0.41% vs 1.65% coverage-weighted); 48,833 clusters at 50% identity versus 43,470, largest cluster 0.02% versus 1.04%. Anchors verify the metric: the reference set itself sits at 84.9%. | `SEQME_WHOLE_LIBRARY_AUDIT.md` §6 |
| **Synthesizability rate, full library** | MEDIUM | $0 | 78.18% versus the baseline's 38.43%, seed spread 0.25pp. Caveat recorded: the seven-constraint rule is ours, not the organizers', and it fails 38% of *real* known AMPs, so it measures conformity to those rules. | `ADDENDUM1_MMSEQS_SYNTH.json` |
| **Upstream training-data overlap, measured** | HIGH | $0 | Converted a conceded unknown into a number. **80.4% of AMP-Designer's published peptide corpora are inside the challenge's reference set**, covering 30.1% of it; generator, ANIA and the reference set all descend from the same public databases. **Zero** exact matches between our 50,000 (or our top-100) and any of the eight published files including UniProt's 630,683. Max similarity from our top-100 to that union is 0.7059 — further than from the reference set the rule is written about. | `DATA_AND_MODEL_DISCLOSURE.md` §2–3 |
| **Silent CPU-fallback defect** | HIGH | $0 | Found by a broken rented GPU, then **fixed in code**: `cuda_gate.py` refuses to generate when the intended CUDA path cannot execute, testing both "CUDA absent" and "present but unable to execute a real tensor operation". 13 new tests. Differential run proves published bytes unchanged. Needs one authoritative validator run to be receipted. | `validation/POST_VALIDATION_CHANGES.md` |
| **Clean-clone deployment** | HIGH | prior phase + $0.55 | All eight unchanged official validator checks pass from a clean clone — 116 min on the retrieval variant, and again in **107m40s on the weights-bundled variant on 2026-09-27**, which is the one that will be pushed. Six byte-identical generations across two GPU architectures. | `validator_results/AUTHORITATIVE_VALIDATION_2026-09-27.md` |

## Closed without testing, with the reason

| avenue | EV | why closed |
|---|---|---|
| **New generators** (dsAMP/dsAMPGAN, deepAMP, membrane-targeting directed generation, AMPGen, ProtGPT2+MCL, MOFormer, EBAMP, OmegAMP) | MEDIUM | A documented scan found no locatable public weights for these, and reproducing a generator from a paper description is not reproducing the authors' model. **The load-bearing reason is time, not availability:** four days cannot clear the funnel the incumbent cleared *plus* a prospective protocol. `LANE10_GENERATOR_FRONTIER_CLOSED.md` |
| **MPOGAN** — separated out, and the old reason was **wrong** | LOW-MED | The ledger previously closed MPOGAN inside the row above on "no locatable public weights". **False.** Verified 2026-09-27: `models/gen_models/MPOGAN_finetuning/700_gen.pth` exists (217,695 bytes), `generateCandidates.py` loads only it, `generate_seqs` defaults to **CPU**, and the authors' own example generates exactly 50,000 sequences. Inference was feasible and free. **It closes on rights instead:** the repository has no licence (GitHub API `license` = `null`, no `LICENSE` file, none in the paper or a deposit), and both tiers require shipping model weights. No inference was run. `MPOGAN_LEAD_CLOSED_ON_RIGHTS.md` |
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

**Withdrawn as written: an earlier version of this section said "the high-EV frontier is exhausted".
2026-09-27 disproved that twice in one day**, and the correction is more useful than the claim was:

1. **An entire evaluation family had never been measured.** The competition's Phase 1 screens the full
   50,000-member library with **seqme**. Every comparison in this ledger above scored the **top-100**
   with APEX and ANIA. The audit took a few hours of local CPU and **$0.00**, and it found the entry
   behind the published baseline on two metrics the proposal names. A frontier with a free, unmeasured,
   directly-scored family in it was not exhausted.
2. **A closure premise was simply wrong.** MPOGAN was closed on "no locatable public weights"; the
   weights are in its repository and the authors' own example generates exactly 50,000 sequences. The
   lane still closes, on licence grounds, but not for the reason recorded.

**What can honestly be said instead.** Every avenue in the tables above is either tested with evidence
or closed with a stated reason, and the reasons that now carry the weight are **time** (four days to
October 1, and any library change invalidates every receipt bound to seed 42's exact 50,000) and
**rights** (unlicensed third-party weights cannot be shipped at either tier), not an assertion that
nothing is left to look at. The one family we know is still unmeasured is named: **surrogate activity
prediction with AMPredictor, MBC-Attention and DeepAMP**, the first of the organizers' four Phase-1
families.

**The entry is frozen at seed 42 with `CONSENSUS_FIXED` and full-library selection. V3 is preserved
unchanged.** That is a decision made under a stated deadline, not a claim that the search space is
empty.
