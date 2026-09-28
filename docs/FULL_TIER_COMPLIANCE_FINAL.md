# Full-tier compliance — final audit against the current official requirements

Audited 2026-09-28 against the **live Kaggle "Full Requirements" section** and the official template
README, with the public repository as the object of the audit — not the local copy.

**Repository:** https://github.com/cadentann/amp-challenge-2027-entry
**Commit:** `31735d98e2e73bf97045fec3774a78aacbce23d0` · **Visibility:** PUBLIC · **Branch:** `main`

Statuses are **PASS**, **OPEN** or **N/A**. An interpretive uncertainty is never recorded as a PASS.

---

## Minimum requirements (benchmark participation)

| # | requirement | status | evidence |
|---|---|---|---|
| M1 | Abstract summarising the method | **PASS** | `docs/METHOD_AND_ABSTRACT.md` §Abstract; final paste text in `KAGGLE_WRITEUP_FINAL.md` |
| M2 | 50,000 designed AMPs for computational evaluation | **PASS** | `artifacts/library.fasta`, 50,000 unique, SHA-256 `a91c0de9…` |
| M3 | Ranked top-100 with selection/ranking documentation | **PASS** | `artifacts/top.fasta`, 100 ranked, `ece3b706…`; procedure in `docs/METHOD_AND_ABSTRACT.md` §2–4 |
| M4 | Summary of training data, external databases, manual intervention and computational filters | **PASS** | `docs/DATA_AND_MODEL_DISCLOSURE.md` |
| M5 | GitHub repository with model weights and inference code | **PASS** | public repo above; checkpoint 340,569,639 bytes via Git LFS; `src/finalist_entry/` + `scripts/prepare_entry.py` |
| M6 | Grant read access to @RasmusML and @szymczakpau | **OPEN — your action** | The repository is **public**, so read access exists without an invitation. If the submission interface still asks for explicit collaborator access, the exact step is in `FINAL_SUBMISSION_PACKET.md` §6. Not performed. |

## Full requirements (co-authorship eligibility)

| # | requirement | status | evidence |
|---|---|---|---|
| F1 | **Public** GitHub repository following the provided template | **PASS** | GitHub API reports `"private": false, "visibility": "public"`. Structure follows `szczurek-lab/amp-challenge-2027`: `pyproject.toml`, `uv.lock`, `src/`, `data/`, `scripts/`, `generate` entry point |
| F2 | Trained model weights in the repository | **PASS** | `assets/prompt_model/pytorch_model.bin` via Git LFS. Verified from a clean unauthenticated public clone: **340,569,639 bytes**, SHA-256 `47944ff42f7ea6a448340d44c2027329833205dd658ec4777e77777bdab1adc9`, equal to the pin in `ASSET_SOURCES.json`. LFS pointer OID equals the same hash |
| F3 | Inference code | **PASS** | 13 modules in `src/finalist_entry/`, console script `generate`, plus `scoring_adapter.py` and `vendor/` |
| F4 | Detailed usage documentation | **PASS** | `README.md` (12 KB: quickstart, runtime expectations, how to tell slow from hung, failure modes) plus 80+ documents in `docs/` |
| F5 | Permissive OSI-approved licence **specified in the repository** | **PASS** | `LICENSE` is canonical MIT and **GitHub's own detector now reports `spdx_id: MIT`**. It previously reported `NOASSERTION`/"Other" because a third-party notice had been appended; the notice moved to `THIRD_PARTY_NOTICES.md` and the licence file is now pristine. This was a real defect found by checking GitHub's view rather than our file |
| F6 | Fixed default random seed | **PASS** | `FINALIST.lock.json` `generation_seed: 42`; no CLI argument can change it; `uv run generate` takes no required arguments |
| F7 | Running the generation script twice produces identical output | **PASS** | The unchanged official validator's own check [8] passed: two full generations produced byte-identical `library.fasta` and `top.fasta`. Receipt `validator_results/AUTHORITATIVE_VALIDATION_2026-09-27.md`, exit 0, 107m40s |
| F8 | `uv sync` + entry point reproduces the submitted library | **PASS** | Same receipt: all eight checks, clean clone, `a91c0de9…` and `ece3b706…` reproduced. Six byte-identical generations now exist across two GPU architectures |
| F9 | **Full training-data disclosure** | **OPEN — not fully satisfiable by us** | We disclose everything we can verify: the generator's published corpora measured at 14,760 unique peptides, **80.4% of them inside the challenge reference set**; ANIA's declared sources (DBAASP, dbAMP, DRAMP); zero exact matches between our 50,000 (or top-100) and any published upstream file. **What is not disclosable:** both upstream training scripts default to a file **absent from the upstream repository**, so the released checkpoint's actual training input is not pinned and was not reconstructed, and **APEX publishes no training data at all**. `docs/DATA_AND_MODEL_DISCLOSURE.md` §2–3 |
| F10 | If proprietary or non-public data is used, release it publicly under a permissive licence | **N/A** | We used no proprietary or non-public data. Every input is a public database or a publicly released model; we trained nothing |
| F11 | External database disclosure | **PASS** | `data/antibacterial.fasta` (39,448, challenge-supplied) and MarLys-AMP v3 (103,143, CC0) for novelty measurement; the 996-member ranking anchor is disclosed as a ranking reference, not training data |
| F12 | Filtering and manual-intervention disclosure | **PASS** | Five filters, all score-blind and applied before any score is read, in `docs/DATA_AND_MODEL_DISCLOSURE.md` §5. **No manual curation of any peptide at any point** |
| F13 | Third-party licences and attribution | **PASS** | `THIRD_PARTY_NOTICES.md`: CC-BY-4.0 checkpoint redistributed unmodified with DOI attribution; MIT AMP-Designer and APEX source, with modifications itemised in `vendor/evaluator/assets/apex/NOTICE.md` |

## Design constraints (current Kaggle wording)

| constraint | status | measured |
|---|---|---|
| 20 standard proteinogenic amino acids only | **PASS** | verified over all 50,000 and all 100 |
| Length 8–50 residues | **PASS** | library 8–34; top-100 12–34 |
| Linear peptides only | **PASS** | plain sequence strings; no bonds encoded or implied |
| No terminal modifications, including amidation | **PASS** | none specified anywhere in the submission |
| No non-canonical AAs, staples, lipidation, glycosylation, PEGylation, dendrimers | **PASS** | none |
| Unique sequences only | **PASS** | 50,000/50,000 and 100/100 unique |
| Top-100 is a subset of the 50,000 | **PASS** | enforced in code and re-checked by the validator |
| Top-100 ≤80% identity to the reference database | **PASS on the executable check** | max `Levenshtein.ratio` **0.764706**, margin 0.035294 — the only one of four compared portfolios with headroom |

## Open items, classified

**Minimum-entry requirement not yet satisfied:** M6 only, and only if the interface asks for explicit
collaborator access despite public visibility.

**Full-tier-only, not satisfiable by us:** F9. The gap is in what the *upstream authors* published, not
in our disclosure of it.

**Unresolved organizer interpretations** — none of these is ours to settle:
- **MMseqs2/MarLys parameters are unpublished.** We measure max identity **68.7%** at MMseqs2's default
  coverage and **76.9%** at 80% query coverage, **zero violations in both**; a permissive no-coverage
  setting fails *every* portfolio including all three comparators. Passing the executable
  `Levenshtein.ratio` check does **not** settle this. Current wording bounds the consequence: an
  over-threshold candidate is *"treated as invalid and replaced by the next valid candidate"*.
- **Co-authorship.** The website says all advancing teams are co-authors; Kaggle ties eligibility to the
  full tier. Documented discrepancy, `docs/CURRENT_RULE_STATE_2026-09-28.md` §4. We built against the
  stricter reading. **Co-authorship is not claimed as guaranteed.**
- **Whether our F9 disclosure counts as "full".**

**Scientific limitations, not submission requirements:** no peptide has been synthesised or assayed;
both predictors sit at R² ≤ 0 on held-out measured MIC; safety and selectivity are **UNKNOWN** and
unknown safety is evidence of neither good nor poor performance; one APEX head is dead; the library is
one chemotype; on the Phase-1 embedding metrics we are **behind** the published AMP-Diffusion baseline on
FBD and MMD, with a shuffled negative control showing that most of that metric family cannot support
quality claims in either direction; and predicted potency from published oracles — one of the six
declared aggregation components — remains **unmeasured**, because the one implementation we could reach
failed its reliability gate.

**No aggregation score is computed and no qualification rank is estimated anywhere in this project.**
