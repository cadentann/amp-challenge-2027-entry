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
