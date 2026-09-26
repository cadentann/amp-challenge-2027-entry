# Weights-bundled variant — what was verified, and what was not

The weights-bundled variant is at `RELEASE_VARIANTS/entry-with-weights-lfs`. This records its
verification precisely, including the two steps that could not be completed and why that is safe.

## Verified

| # | check | result |
|---|---|---|
| 1 | exact checkpoint size | **340,569,639 bytes** |
| 2 | checkpoint SHA-256 | `47944ff42f7ea6a448340d44c2027329833205dd658ec4777e77777bdab1adc9` — **matches the pin** in `ASSET_SOURCES.json` and `FINALIST.lock.json` |
| 3 | LFS tracking rule | `.gitattributes` tracks exactly one path, `assets/prompt_model/pytorch_model.bin` |
| 4 | LFS pointer integrity | the pointer's `oid sha256` **is** the pinned checkpoint hash — LFS uses SHA-256 as its object id, so the packaging carries its own integrity check |
| 5 | repo size | 659 MB working tree; 325 MB LFS store; 328 MB `.git` |
| 6 | GitHub 100 MB limit | only the checkpoint exceeds it and it is under LFS. Largest non-LFS tracked file is `data/antibacterial.fasta` at **4.1 MB** — nothing else is close |
| 7 | clean clone | delivers the real 340,569,639-byte file with the correct hash (verified locally **and** on a Linux pod) |
| 8 | `git lfs pull` | idempotent; the file is real binary, not a pointer |
| 9 | **no-LFS failure mode** | a clone without LFS leaves a 134-byte pointer. `prepare_entry.py` fails both its size and hash checks and **re-downloads from Zenodo**, so the entry degrades to the retrieval path rather than running on a pointer |
| 10 | `uv sync` | succeeds on Linux from the bundled variant |
| 11 | **`prepare_entry.py` with bundled weights** | reports `generator checkpoint already present and verified` — the download is **skipped**, and only the evaluator assets are fetched |
| 12 | scorer runtime | built and promoted to the pinned lock hash `d74ea38c…` |
| 13 | model load | `GPT2LMHeadModel` loaded from the clone's own bundled checkpoint path |
| 14 | stale remote removed | the variant was built by `git clone`, which left an `origin` pointing at a local path. Removed — `git remote` is now empty, so `git remote add origin` will work cleanly |

## Not completed

Steps 15–17 — `uv run generate` to completion, repeated generation, and the unchanged official
validator's eight checks against the bundled variant — were **attempted and not finished**. Two pods
failed for unrelated infrastructure reasons: the first had a GPU that `nvidia-smi` could see but no
build of PyTorch could initialise (see below), and the second never received a network address in 22
minutes. Both were terminated. Rather than spend further on infrastructure roulette, this is recorded
honestly.

**Why that is safe to leave, stated as an argument rather than an assurance.** The pipeline is
deterministic given its inputs, and this variant changes no input the pipeline reads:

- **Five files differ** between the validated repository and this variant: `.gitattributes` and
  `assets/prompt_model/{pytorch_model.bin,config.json}` added, `.gitignore` and
  `PROVENANCE_MANIFEST.json` modified.
- **None is referenced by any of the 11 modules reachable from the entry point** — verified by parsing
  every module's string constants, the same test used for the earlier post-validation changes.
- `FINALIST.lock.json`, `uv.lock` and every file under `src/` are **byte-identical**.
- The one path the execution *does* read, `assets/prompt_model/pytorch_model.bin`, receives
  **byte-identical content** in both variants — same size, same SHA-256.
- Check 11 confirms this behaviourally: the pipeline recognised the bundled bytes as already correct
  and proceeded on exactly the path it takes after a successful download.
- The retrieval variant has passed steps 15–17 **four times**: two byte-identical runs on an RTX 4090,
  and two more inside the clean-room validator on an RTX A4500.

So the only untested thing is whether identical bytes arriving by `git lfs` rather than by HTTPS
changes a deterministic computation. It does not, and check 11 shows the code cannot tell the
difference. **If you want the belt-and-braces run anyway, step 4 of `FINAL_EXTERNAL_ACTIONS.md` runs
exactly it against your pushed repository.**

## An incidental finding worth acting on: silent CPU fallback

On the first pod, `nvidia-smi` reported a healthy RTX 5090 but **every** PyTorch build — the
generator's 2.8.0+cu128 and the system's 2.4.1+cu124 — returned `is_available: False` with
`CUDA unknown error`, with `CUDA_VISIBLE_DEVICES` unset. A host-level CUDA failure, not ours.

The consequence matters for the submission. The device policy is `auto_prefer_cuda`, so generation
**silently fell back to CPU** and began producing sequences at ~43 cores of throughput. Those
sequences would **not** match the submitted library, and nothing in the output announced the fallback.

This is a concrete instance of the cross-device reproducibility risk already disclosed in
`LIMITATIONS.md`, and it suggests a cheap mitigation that costs nothing and changes no code:

```bash
python3 -c "import torch; assert torch.cuda.is_available(), 'CUDA unavailable — generation would fall back to CPU and would not reproduce the submitted library'; print('CUDA OK:', torch.cuda.get_device_name(0))"
```

Run that **before** `uv run generate`. It is included as a gate in `FINAL_EXTERNAL_ACTIONS.md`. It is
the single highest-value operational check in this handoff, because it converts a silent
several-hour wrong-answer failure into an immediate one.
