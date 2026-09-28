# Consolidated handoff — 2026-09-28

**Nothing has been pushed, published, submitted, shared with the organizers, or attested.** Neither
release variant has a git remote. Deadline, re-verified from the pinned organizer proposal rather than a
countdown: **October 1, 2026 AOE**.

This is the single document to read. It closes the branch, states the delivery plan, and lists the steps
that need you. **There is no open research queue behind it.**

---

## 1. The finalist — unchanged

| | |
|---|---|
| generator | AMP-Prompt (AMP-Designer), commit `07d455dd`, weights Zenodo DOI 10.5281/zenodo.17018363 |
| selector | `CONSENSUS_FIXED`, frozen, never retuned, 996-member anchor `fe438eab…` |
| seed | 42 |
| selection universe | all 48,133 eligible members of the 50,000-peptide library |
| `library.fasta` | `a91c0de9200a3d9f4377bfc6f81d36d21ea15bb9c940bd91fab797cd5ae2308b` |
| `top.fasta` | `ece3b7062d55d1ac4eb35f60e450cebec229ebfba63b5a0ab7214ecd4e5cb841` |
| platform | **Linux x86_64** |
| V3 fallback | `AMP_Entry_Private_Release_v3.zip` = `45f69b0d…`, preserved unchanged |

## 2. The last qualification question is closed — and the answer is about the instrument

The whole-library audit marked the organizers' **first** Phase-1 family — surrogate activity prediction
with AMPredictor, MBC-Attention and DeepAMP — **NOT COVERED**. That is now resolved as far as it
honestly can be. Full detail: `docs/DEEPAMP_DIAGNOSTIC_RESULT.md`.

**Deep-AMP was obtained, verified and run. It failed.** MIT-licensed, weights in-repo, at the exact
submodule commit BATTLE-AMP pins, all four variants on local CPU. Against the **22 measured MICs from
its own paper**, no variant achieves positive rank concordance (ρ −0.48 to +0.06 on matching endpoints,
n = 10–11), and all 15 scored peptides are predicted at **3,789–43,027 µM** where **0.4–100 µM** was
measured. `frac ≤16 µM` is **0.0000** for a cohort in which the paper measured 7/22 *E. coli* and 21/22
*B. subtilis* values at or under 16 µM.

**It scores our library about 2,900× better than the AMP-Diffusion baseline, and we decline to claim
it.** 77.2% of the baseline's sequences land in a saturated ceiling region near 10⁴ µM versus 3.9% of
ours, and inside that region the predictions barely vary (log10 sd 0.098). The "advantage" is mostly
which library gets pushed into the ceiling.

**Family 1 therefore stays NOT COVERED** — now with a reason rather than a gap. AMPredictor and
MBC-Attention were **not run**; both are declared `gpu_required: true` and neither was needed once the
first model's own paper's data disqualified it.

**Three defects found in the organizers' own benchmark harness**, recorded because Phase 1 may rest on
it: `registry.yaml` declares Deep-AMP `gpu_required: true` when its wrapper says false; it credits the
wrong authors; and `MAX_LEN = 48` silently discards all 15 of the 49-residue peptides from the model's
own paper. A wrapper/original encoding divergence was also found and **tested** — it is real but is *not*
the cause of the failure.

**Cost: $0.00.** Local CPU. No GPU credit, no top-up, no upload of any peptide anywhere.

## 3. Five documentation defects corrected

| defect | correction |
|---|---|
| **predictor independence** | "The predictors are complementary" replaced everywhere with **"they fail differently — which is not independence"**, plus the measured shared ancestry: the same DBAASP/dbAMP/DRAMP records reach the generator, ANIA and the reference set, and **APEX publishes no training data at all**, so its overlap cannot even be measured |
| **homology** | "not explained by proximity to known AMPs" narrowed to **"to the known-AMP databases we can see"**. Lane 4's proxy is MarLys (103,143); HEV3's is `antibacterial.fasta` (39,448). Neither is the predictors' training corpora. *I got this wrong once mid-correction — naming the wrong reference set — and fixed it* |
| **raw counts** | `METHOD_AND_ABSTRACT.md` claimed "65,536 raw attempts: 63,403 library-valid, 61,073 top-eligible" — historical figures, and arithmetically impossible for the shipped run. Replaced with the receipt: **51,712 generated, 51,694 examined, 1,691 + 1 + 2 rejected, 50,000 valid, 48,133 top-eligible**. 65,536 is a **ceiling**, not a count |
| **Git LFS quotas** | rechecked against GitHub's documentation: **10 GiB storage and 10 GiB/month bandwidth** on Free and Pro (250 GiB on Team/Enterprise), and data packs replaced by metered billing. Every "1 GB" claim was stale by ten times. At 325 MB the push is ~3% of the allowance — **no longer a practical constraint** |
| **package QA** | the reference check used `rglob`, which on macOS's case-insensitive filesystem resolved MPOGAN's upstream `readme.md` against this package's `README.md`. It passed here and **would have failed on Linux**. Now case-sensitive, with the upstream file documented in `docs/EXTERNAL_REFERENCES.md` |

None required regeneration; the artifacts are untouched.

## 4. Validation receipt

**All eight unchanged official validator checks passed** from a clean clone of the weights-bundled
variant at commit `2ceb306`, exit 0, **107m40s**, on a Community RTX A4500. Both generations produced
`a91c0de9…` and `ece3b706…`, byte-identical to the submitted artifacts, with the checkpoint materialised
by **Git LFS** at its pinned hash and size. Six byte-identical generations now exist across two GPU
architectures. Receipt, unedited 999-line log, machine facts and both run receipts:
`validator_results/AUTHORITATIVE_VALIDATION_2026-09-27.md`.

The silent-CPU-fallback repair is receipted by that same run: `device_gate` `CUDA_OK` with
`probe_value: 8256.0`, and a negative test on the same GPU where hiding the device made generation
**refuse, exit 1**.

**Commit boundary.** Both variants have gained commits since, all documentation, QA and receipts.
`git diff --name-only 2ceb306 HEAD -- src/ FINALIST.lock.json uv.lock pyproject.toml data/ vendor/
scripts/ scoring_adapter.py assets/ .gitattributes` prints **nothing** — re-verified after the final
commit. Everything `uv run generate` reads is byte-identical to the validated tree.

## 5. Repository and LFS delivery plan

**Recommendation: full / public, using variant B.** Your call; publishing is irreversible.
`RELEASE_PLANS.md` argues both sides.

| | variant A — retrieval | **variant B — weights bundled** |
|---|---|---|
| path | `FINAL_SUBMISSION_READY/amp-prompt-consensus-entry` | `RELEASE_VARIANTS/entry-with-weights-lfs` |
| HEAD | `c91739e` (46 commits) | `a5cf155` (37 commits) |
| tracked files | 153 | 162 |
| size | 8.9 MB | 660 MB working tree, 325 MB LFS object |
| git remotes | **0** | **0** |
| validated | inherits the earlier clean-room run | **validated at `2ceb306`** |

`src/` is byte-identical between them, checked executably by the compliance audit. Seven tracked files
differ, none on the executed path.

**LFS specifics.** `.gitattributes` tracks exactly one path,
`assets/prompt_model/pytorch_model.bin`. The LFS pointer's `oid sha256` **is** the pinned checkpoint
hash, so the packaging carries its own integrity check. Largest non-LFS tracked file is 4.1 MB, well
under GitHub's 100 MB cap. The 325 MB push is ~3% of the 10 GiB free-tier allowance. A clone **without**
LFS leaves a 134-byte pointer, which `prepare_entry.py` detects and re-downloads — the entry degrades to
retrieval rather than running on a pointer.

## 6. Disclosures

`docs/DATA_AND_MODEL_DISCLOSURE.md` is the full statement. The load-bearing parts:

- **We trained nothing.** Every model is used as publicly released at a pinned hash.
- **Training-data overlap is measured, not conceded**: 80.4% of AMP-Designer's published peptide
  corpora (14,760 sequences) lie inside the challenge's `antibacterial.fasta`, covering 30.1% of it.
  Generator, ANIA and the reference set all descend from the same public databases.
- **What is unknowable is stated as such**: both upstream training scripts default to a file absent
  from the repository, so the released checkpoint's actual training input was **not reconstructed**, and
  APEX's pinned commit publishes **no training data at all**.
- **Our output does not overlap**: zero exact matches between our 50,000 sequences, or our top-100, and
  any of the eight published upstream files including UniProt's 630,683. Maximum similarity from the
  top-100 to that corpus is **0.7059** — further than our 0.7647 against the reference set the 0.80 rule
  is written about.
- **Licences**: MIT on our repository; CC-BY-4.0 and MIT on the generator's two halves; MIT for APEX and
  ANIA; attribution in `README.md`, `ASSET_SOURCES.json` and the abstract.

## 7. Unresolved rule questions — six, and they are the organizers' to resolve

`qa/compliance_audit.py` reports these as **OPEN** and never as satisfied. All executable requirements
pass.

1. whether hash-pinned retrieval satisfies "with model weights" — **moot if you push variant B**;
2. whether the training-data disclosure counts as "full", given that the checkpoint's actual training
   input is not pinned upstream and APEX publishes none;
3. MMseqs2/MarLys novelty compliance — the proposal names MMseqs2 and publishes no parameters; zero
   violations under the two coverage settings tested, all portfolios fail under a permissive one;
4. safety and selectivity standing — no measured HC50 exists and our screen is uninformative for
   peptides this novel, so we claim nothing either way;
5. whether a modified AMP-Diffusion derivative remains the excluded baseline — no controlling public
   rule; does not reach this entry;
6. cross-device reproducibility on the organizers' hardware — six byte-identical runs across two
   architectures, still not all devices, CPU untested.

## 8. Submission checklist — everything left is yours

1. **Choose the tier.** Recommendation: full/public with variant B.
2. **Create an empty GitHub repository.**
3. **Push variant B** with `git lfs` configured. ~325 MB, ~3% of the free allowance.
4. **Grant read access** to @RasmusML and @szymczakpau — only if the repository is private.
5. *(Optional)* re-run the validator from the pushed repository. We already ran exactly this on exactly
   this repository and it passed; only GitHub's LFS transport is unverified.
6. **Submit on Kaggle** — abstract from `docs/METHOD_AND_ABSTRACT.md`, `artifacts/library.fasta`,
   `artifacts/top.fasta`, repository link.
7. **Accept or decline attestations.**
8. **Rotate the RunPod API key** — independent of the submission, and it should not wait.
   `docs/CREDENTIAL_ROTATION.md`. Confirm 0 pods first (currently true), create the replacement in the
   console, store it in your password manager, then revoke the old one. **Do not paste the replacement
   into a chat session.**

Exact commands, hashes and the three host traps we hit are in `FINAL_EXTERNAL_ACTIONS.md`.

## 9. What is still not established

Unchanged and worth re-reading before making any claim: nothing has been synthesised or assayed; both
predictors sit at R² ≤ 0 on held-out measured MIC; safety and selectivity are UNKNOWN; one APEX head is
dead; the library is one chemotype; and on the Phase-1 embedding metrics the entry is **behind** the
published baseline on FBD and MMD, with the negative control showing most of that family — favourable
and unfavourable alike — cannot support quality claims. `docs/LIMITATIONS.md` and
`docs/SEQME_WHOLE_LIBRARY_AUDIT.md`.

**Competition performance is unknown.**
