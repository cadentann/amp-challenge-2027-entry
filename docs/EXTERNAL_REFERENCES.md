# Files referenced by these documents that live outside the package

Some documents cite working files that were deliberately not copied into
`FINAL_SUBMISSION_READY/` — they are raw experimental apparatus rather than deliverables. Nothing
was deleted; all of it is preserved in the project's working namespaces. Paths below are relative
to the project root, `/Volumes/SanDisk/AI_Research/AMP_Challenge/`.

| referenced as | actual location |
|---|---|
| `PORTFOLIOS.json` | `frontier_tournament_20260924/analysis/actual_product_comparison_v1/PORTFOLIOS.json` |
| `FINALIST_SELECTION_UNIVERSE_PROPOSAL.md` | `frontier_tournament_20260924/adjudication/FINALIST_SELECTION_UNIVERSE_PROPOSAL.md` |
| `LINUX_NUMERICAL_STABILITY_PROSPECTIVE_PLAN.md` | `work/frontier_20260924/finalist_integration/linux_claim_harness/protocol/` |
| `preflight_reference_selections.py` | `work/frontier_20260924/finalist_integration/linux_claim_harness/` |
| `classify_exact_numerical_failure.py` | `work/frontier_20260924/finalist_integration/linux_claim_harness_v2/` |
| organizer proposal rules snapshot | `releases/2026-09-24_private_v3/AMP_Entry_Private_Release_v3/provenance/rules_snapshots/organizer_proposal_local.txt` — the primary source for the Phase 1/Phase 2 rule text quoted in `LANE12_RULE_AMBIGUITY_RESOLVED.md`. A third-party document; retained in the project, deliberately not redistributed in this package. |
| `validation/VARIANT_FACTS.txt` | exists only inside the **weights-bundled variant**, at `RELEASE_VARIANTS/entry-with-weights-lfs/validation/VARIANT_FACTS.txt`. It records that variant's own measured facts (checkpoint size, LFS pointer OID, repo size) and is deliberately not duplicated into the retrieval variant or this package |
| `train_raw_data.txt` | **not a project file.** The default value of `--train_raw_path` in AMP-Designer's `train_AMP_GPT.py` and `train_prompt_contrast.py`. It is **absent from the upstream repository too**, which is exactly why the released checkpoint's training input is not pinned. Cited in `DATA_AND_MODEL_DISCLOSURE.md` §2.1 |
| `test_seqs.fasta` | **not a project file.** APEX's example input at `gitlab.com/machine-biology-group-public/apex-pathogen` @ `417a4441`. Cited in `DATA_AND_MODEL_DISCLOSURE.md` §3.1 as part of the file listing of that pinned commit |
| `sample.fasta` | **not a project file.** The three-sequence example shipped inside the Deep-AMP wrapper repo, used only to confirm the models load. Cited in `DEEPAMP_DIAGNOSTIC_PREREG.md` |
| `STAGE2_MEASURED_BENCHMARK_BLUEPRINT.md` | `releases/2026-09-24_private_v3/AMP_Entry_Private_Release_v3/evidence/prior_research/STAGE2_MEASURED_BENCHMARK_BLUEPRINT.md` — the 2026-09-22 audit that pinned the BATTLE-AMP commit reused by the Deep-AMP diagnostic |
| `readme.md` | **not a project file.** MPOGAN's own upstream README at `github.com/23AIBox/MPOGAN`, cited in `MPOGAN_LEAD_CLOSED_ON_RIGHTS.md` for its lack of reuse terms. Lowercase on purpose: that is the upstream filename, and it is **not** this package's `README.md` |
| `requirement.txt`, `LICENSE.md` | **not project files.** MPOGAN's dependency list, and the licence file whose **absence** (HTTP 404) is the finding. Cited in `MPOGAN_LEAD_CLOSED_ON_RIGHTS.md` |
| `SEQME_DATASETS.json` | shipped in this package as `evidence/SEQME_DATASETS.json`; in the canonical project it is `qualification_20260927/prereg/DATASETS.json` |
| `COMPLETE.json`, `runtime.json` | per-run receipts under the relevant experiment directory in `frontier2_20260925/experiments/` |

Also preserved outside the package, and worth knowing about:

- `frontier2_20260925/evidence/incumbent_E5000_artifacts/` — the superseded entry's artifacts,
  unmodified.
- `frontier2_20260925/evidence/hev1_e2e_EXECUTED/` — the two post-promotion end-to-end runs whose
  receipt is summarised in `amp-prompt-consensus-entry/validation/END_TO_END_VALIDATION.json`.
- `frontier2_20260925/experiments/hev1_full_opportunity/scores/` — the per-peptide scores for all
  48,133 universe members, from which every headline metric and the null control are derived.
- `frontier_tournament_20260924/` — the earlier tournament, including the arms that were closed
  without full resolution (ARCADIAMP, BroadAMP-GPT, AMPGen, OmegAMP).

Nothing was overwritten at any point. Superseded artifacts are retained under their own names.
