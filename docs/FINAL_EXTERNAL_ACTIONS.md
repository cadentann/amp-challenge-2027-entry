# Final external actions — everything that needs you

**Nothing below has been done.** No repository exists, nothing is pushed or public, no organizer has
access, no Kaggle submission, no attestation accepted. Neither repository variant has a git remote.

Deadline: **October 1, 2026 AOE**.

## Decide first

**Which tier** — recommendation in `RELEASE_PLANS.md` is **full / public**, because the weights gap that
was the main objection is now closed and everything else the full tier asks for was already built and
validated. Minimum forecloses co-authorship by construction; full is a superset. **Your call** —
publishing is irreversible in practice.

**Which variant** — recommendation **B**, which contains the weights, because both tiers ask for a
repository "with model weights and inference code".

| variant | path | tracked files | size | needs LFS |
|---|---|---:|---:|---|
| A — retrieval | `FINAL_SUBMISSION_READY/amp-prompt-consensus-entry` | 143 | 8.5 MB | no |
| **B — weights bundled** | `RELEASE_VARIANTS/entry-with-weights-lfs` | 148 | 659 MB | **yes** |

Confirm the sealed commit before you push — it is the one thing here that changes with every edit:

```bash
git -C RELEASE_VARIANTS/entry-with-weights-lfs log --oneline -1 && git -C RELEASE_VARIANTS/entry-with-weights-lfs status --short
```

`src/`, `tests/`, `qa/`, `docs/`, `data/`, `vendor/`, `scripts/`, `tools/`, `FINALIST.lock.json`,
`uv.lock` and `pyproject.toml` are **byte-identical** between the two, which the compliance audit
checks executably. Exactly **seven tracked files** differ; see `docs/WEIGHTS_VARIANT_VERIFICATION.md`.

**One thing worth knowing before you decide the tier.** The whole-library Phase-1 audit finished on
2026-09-27 and it is genuinely mixed. Ahead of the published AMP-Diffusion baseline on novelty at the
80% identity threshold (1.47% vs 3.82% of the library), clustering coverage, FKEA and our
synthesizability rule; **behind it on FBD, MMD and AuthPct**, all replicated on an independent sample.
A character-shuffled control then showed that FBD, MMD and four of the apparent leads are largely
composition statistics and cannot be argued from in either direction — leaving FKEA (we lead) and
AuthPct (we trail) as the only embedding metrics whose control behaves. It does not change the tier
decision, but it should temper expectations about advancing past Phase 1, where at most 20 teams
continue. `docs/SEQME_WHOLE_LIBRARY_AUDIT.md` has it in full.

---

## 1. Create the GitHub repository

In the browser. Create an **empty** repository — no README, no `.gitignore`, no licence, or the first
push will conflict.

- **Full tier:** visibility **Public**
- **Minimum tier:** visibility **Private**

## 2. Configure Git LFS (only for variant B)

```bash
git lfs install
```

If `git lfs` is missing: `brew install git-lfs` (macOS) or `sudo apt-get install git-lfs` (Debian/Ubuntu).

LFS is already configured *inside* variant B — `.gitattributes` tracks the checkpoint and the object is
in its local LFS store. Step 2 only enables LFS for your user account.

**Quota note:** the checkpoint is 325 MB. GitHub's free tier gives 1 GB LFS storage and 1 GB/month
bandwidth; every clone of the file consumes bandwidth, including the organizers' verification clone.

## 3. Push

Variant B (recommended):

```bash
cd /Volumes/SanDisk/AI_Research/AMP_Challenge/RELEASE_VARIANTS/entry-with-weights-lfs
git remote add origin git@github.com:<your-username>/<repo-name>.git
git push -u origin main
```

Variant A instead:

```bash
cd /Volumes/SanDisk/AI_Research/AMP_Challenge/FINAL_SUBMISSION_READY/amp-prompt-consensus-entry
git remote add origin git@github.com:<your-username>/<repo-name>.git
git push -u origin main
```

Confirm the checkpoint uploaded as LFS, not as a blob:

```bash
git lfs ls-files
# expect: 47944ff42f * assets/prompt_model/pytorch_model.bin
```

**`git push` is the point of no return for anything public.**

## 4. Grant organizer read access — **only if private**

GitHub → your repo → Settings → Collaborators → Add people → **@RasmusML** and **@szymczakpau**,
permission **Read**.

**This is not the submission.** It satisfies a requirement; it does not enter you in the competition.
Step 6 does that. Doing this without step 6 means the organizers can see the repo but you have not
submitted.

Skip this step entirely if the repository is public.

## 5. Optional — verify from the pushed repository

**We already ran exactly this, on exactly this repository, and it passed.** On 2026-09-27 the unchanged
official validator completed **all eight checks** from a clean clone of variant B at commit `2ceb306`
in 107m40s on an RTX A4500, reproducing `a91c0de9…` and `ece3b706…` byte-identically in both of its
generations, with the checkpoint materialised by Git LFS. Receipt:
`validator_results/AUTHORITATIVE_VALIDATION_2026-09-27.md`.

So this step is now genuinely optional — its only remaining value is confirming that **GitHub** serves
the repository the way a local clone did, chiefly LFS. If you skip it, nothing is unverified except the
transport. If you run it, it runs exactly what the organizers run.

**The silent-CPU-fallback risk is now handled inside the entry, not by a checklist item.** A host
where `nvidia-smi` works but CUDA cannot initialise used to make generation fall back to **CPU
silently** and produce sequences that do not match the submitted library — we hit exactly that on a
rented GPU. `src/finalist_entry/cuda_gate.py` now refuses to generate in that situation, testing both
"CUDA absent" and "CUDA present but unable to execute a real tensor operation". You do not have to
remember anything for this to work. The one-liner below is still a useful 2-second pre-check before
committing a host to a multi-hour run:

```bash
python3 -c "import torch; assert torch.cuda.is_available(), 'CUDA unavailable - generation would fall back to CPU and would NOT reproduce the submitted library'; print('CUDA OK:', torch.cuda.get_device_name(0))"
```

**Then run the validator — and note the dependency trap we walked into.** The validator imports
`Levenshtein`. On Ubuntu 24.04 images `pip` is often bound to a *different* Python than `python3`, so
`pip install` succeeds and `python3` still cannot import it. Install and run with the same interpreter:

```bash
python3 -m pip install --break-system-packages Levenshtein
python3 scripts/verify_submission.py https://github.com/<your-username>/<repo-name> \
  --antibacterial-fasta data/antibacterial.fasta
```

**And if you clone or copy the repository as an archive, tell git it is yours**, or every git command
fails with `detected dubious ownership` and the validator's own clone step fails first:

```bash
git config --global --add safe.directory '*'
```

Requirements: `git`, `uv`, `git-lfs` (variant B), **Linux x86_64** (the lock pins the only validated
scorer runtime), and a CUDA GPU. Budget **several hours** — it runs `generate` twice, and the pipeline
is mostly single-threaded and CPU-bound. There is no progress output during scoring or selection; that
is by design. `README.md` explains how to distinguish slow from hung.

Expect, at the end: `All checks passed. Submission is valid!`

## 6. Submit on Kaggle

The competition page linked from the official template README. Attach:

| what | exact path | SHA-256 |
|---|---|---|
| 50,000 library | `FINAL_SUBMISSION_READY/artifacts/library.fasta` | `a91c0de9200a3d9f4377bfc6f81d36d21ea15bb9c940bd91fab797cd5ae2308b` |
| ranked top-100 | `FINAL_SUBMISSION_READY/artifacts/top.fasta` | `ece3b7062d55d1ac4eb35f60e450cebec229ebfba63b5a0ab7214ecd4e5cb841` |
| repository link | the URL from step 1 | — |

Verify before uploading:

```bash
cd /Volumes/SanDisk/AI_Research/AMP_Challenge/FINAL_SUBMISSION_READY
shasum -a 256 artifacts/library.fasta artifacts/top.fasta
```

## 7. Abstract and method text

**Do not retype these.** Copy from the file, so what you submit matches what was validated:

- **Abstract:** `FINAL_SUBMISSION_READY/docs/METHOD_AND_ABSTRACT.md`, the section headed
  `## Abstract (draft for submission)`
- **Method / selection documentation:** the same file, section `## Method`
- **Training data, external databases, filters:** `FINAL_SUBMISSION_READY/docs/DATA_AND_MODEL_DISCLOSURE.md`

If the form has a length limit, cut from the end of the abstract rather than the middle — the opening
paragraphs carry the method and the closing ones carry the caveats, and **the caveats should not be the
thing that gets dropped**. If you must shorten, keep the sentence stating that all results are
computational predictions with no wet-lab measurement.

## 8. Attestations

Read and accept them yourself. None has been accepted on your behalf. Before you do, know the three
things we cannot certify, all documented in `docs/TIER_REQUIREMENTS_AND_GAPS.md`:

1. whether hash-pinned retrieval would satisfy "with model weights" — moot if you push variant B;
2. that AMP-Prompt's training corpus is disjoint from the evaluation panel — **it is not.** We measured
   the files its authors publish: 80.4% of that peptide corpus is inside `data/antibacterial.fasta`.
   What remains unknown is the *released checkpoint's* actual training input, which the upstream
   repository does not pin. Our own output has **zero** exact matches against any of it;
3. that generation reproduces on the organizers' specific hardware — byte-identical on **two** GPU
   architectures with completed receipts, Ada (RTX 4090) and Ampere (RTX A4500), CPU untested. An
   earlier version of this line said three and counted a Blackwell RTX 5090 pod that produced no
   output; that was wrong;
4. that the library performs well in the organizers' Phase-1 seqme screening — mixed, measured, and
   now documented in `docs/SEQME_WHOLE_LIBRARY_AUDIT.md` rather than assumed.

## 9. Rotate the RunPod key

Separate from the submission, and it should not wait. Full procedure in
`docs/CREDENTIAL_ROTATION.md`. In short: confirm no pods are running (currently **0 pods, $0.00/hr,
balance $7.23**), create the replacement in the RunPod console, store it straight into your password
manager, revoke the old key, then confirm the old one returns `401`.

**Do not send the replacement to a chat session.** No credential exists in either repository, in 29 and
31 commits of git history, in any manifest, or in the Desktop archive — verified by a broad scan whose
two false-positive classes are documented.

---

## Before you start, optionally re-verify locally

```bash
cd /Volumes/SanDisk/AI_Research/AMP_Challenge/FINAL_SUBMISSION_READY
python3 qa/final_qa.py .            # 24 package checks
python3 qa/compliance_audit.py .    # competition requirements, executable vs interpretive
```

Both currently pass. The second prints six **OPEN** interpretive items — those are the organizers' to
resolve and are deliberately not claimed as satisfied.

## Order of operations

1 → 2 (variant B only) → 3 → 4 (private only) → 5 (optional) → 6 → 7 → 8, with 9 whenever you like.

**Steps 3, 4, 6 and 8 are irreversible or externally visible. Nothing below step 2 has been done.**
