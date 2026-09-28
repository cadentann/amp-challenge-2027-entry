# Option: put the model weights in the repository

Both participation tiers ask for a GitHub repository **"with model weights and inference code"**. Ours
ships the code and a hash-pinned retrieval script; it does not contain the weights. This is the largest
identified risk to co-authorship eligibility (`TIER_REQUIREMENTS_AND_GAPS.md`, Gap 1).

**This has not been done.** It changes what you publish and may consume Git LFS quota, so it is your
call. Below is exactly how, and the honest trade-offs either way.

## The two readings, with real numbers

| what you ship | files | size | fits free LFS (10 GiB)? |
|---|---|---|---|
| **Narrow** — the *generative* model only | `assets/prompt_model/` — `pytorch_model.bin` 324.8 MB plus `config.json`; the tokenizer vocab is already tracked at `vendor/amp_prompt/vocab.txt` | **~325 MB** (measured) | Yes, comfortably |
| **Broad** — generator plus the ranking evaluator | + 8 APEX weights, 3 ANIA weights | **~546 MB** | Yes for storage; bandwidth is per-clone |

The narrow reading is defensible: APEX and ANIA are *selection* models, not the generative model the
competition is about, and the requirement sits next to "inference code" for generation. The broad
reading is safer if you read "model weights" as everything needed to reproduce the submitted top-100.

Every file is redistributable: the AMP-Prompt checkpoint is **CC-BY-4.0** (attribution required, already
present in `README.md` and `ASSET_SOURCES.json`), APEX and ANIA are **MIT**.

## Narrow option — commands

Run these in the repository, after `scripts/prepare_entry.py` has populated `assets/prompt_model/`:

```bash
git lfs install
git lfs track "assets/prompt_model/pytorch_model.bin"
git add .gitattributes
```

Then remove the directory from `.gitignore` — delete the line `/assets/prompt_model/` — and:

```bash
git add assets/prompt_model
git commit -m "Vendor the AMP-Prompt checkpoint via Git LFS (CC-BY-4.0, attributed)"
```

## What to check before you push

1. **`git lfs env`** — confirm LFS is actually active, or GitHub will reject the 340 MB blob.
2. **Your LFS quota** — free and Pro accounts get **10 GiB storage and 10 GiB/month bandwidth**
   (rechecked 2026-09-28; earlier drafts said 1 GB). Every clone of an LFS file consumes bandwidth,
   including the organizers' verification clone — at 325 MB that is ~3% of a month's allowance.
3. **`prepare_entry.py` still works.** It checks whether the checkpoint is already present and hashes
   correctly before downloading, so a vendored copy short-circuits the fetch. Verify with
   `uv run python scripts/prepare_entry.py` — it should report `cached` for the generator.
4. **Re-run QA**: `python3 qa/final_qa.py <package-root>`. The repo provenance manifest will need
   regenerating, because it deliberately excludes `assets/prompt_model/`.

## The argument for leaving it as it is

Not doing this is also defensible, and it is what we have done:

- Retrieval is **hash-verified**: every byte is checked against a SHA-256 pinned in the repository
  before use, and the run fails closed on mismatch. A vendored copy is trusted only because it is in
  the repo.
- It keeps the repository small enough to clone without LFS, and avoids consuming your LFS bandwidth
  on the organizers' verification clone.
- All 15 source URLs were live and correctly sized at freeze time (`evidence/ASSET_LIVENESS.json`).

The risk is entirely about **rule interpretation**, not integrity: if the organizers read "with model
weights" strictly, retrieval may not satisfy it. That is unknown, it cannot be resolved without asking
them, and it is recorded rather than assumed away.

## If you want both

Push the repository as it stands to establish the submission, then add the weights via LFS as a second
commit. The artifacts, lock and validation evidence are unaffected — the pipeline reads the weights from
the same path either way.
