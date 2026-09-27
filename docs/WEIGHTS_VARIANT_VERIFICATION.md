# Weights-bundled variant — what was verified, and what was not

> **UPDATE, 2026-09-27 — read this first, then the rest is history.** Three things changed after this
> document was first written. (1) The silent-CPU-fallback risk described at the bottom is **no longer an
> external checklist step**: it is enforced in code by `src/finalist_entry/cuda_gate.py`, which refuses
> to generate when the intended CUDA path cannot execute. (2) **The single authoritative run that both
> that repair and this variant needed has been completed and passed** — all eight official validator
> checks from a clean clone, byte-identical artifacts, 107m40s. See
> `validator_results/AUTHORITATIVE_VALIDATION_2026-09-27.md`. (3) The inertness argument below is
> therefore no longer load-bearing for the receipt; it now only describes the relationship between the
> two *variants*, which remain byte-identical in `src/`.

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

## Steps 15–17 — COMPLETED 2026-09-27

**They were open when this document was written and they are now closed by a completed run.** The
unchanged official validator passed **all eight checks** from a clean clone of this variant at commit
`2ceb306`, in 107m40s, on a Community RTX A4500. Both generations produced
`library.fasta` = `a91c0de9…` and `top.fasta` = `ece3b706…`, identical to the submitted artifacts,
with `raw_generated` 51,712 and `selector_pool_count` 48,133 matching the reference run.

The checkpoint was materialised **by Git LFS** at 340,569,639 bytes and SHA-256 `47944ff4…`, and the log
shows `GPT2LMHeadModel` loading from the clone's own `assets/prompt_model`. So the argument below — that
identical bytes arriving by `git lfs` rather than HTTPS cannot change a deterministic computation — is no
longer only an argument.

Receipt: `validator_results/AUTHORITATIVE_VALIDATION_2026-09-27.md`, with the unedited 999-line log,
machine facts and both run receipts beside it. The two earlier failed pods are still described below and
their logs are retained as `auth_attempt*.log`, because a run that only worked on the third host is worth
saying so about.

**Why the packaging difference specifically is safe, stated as an argument rather than an assurance.**
This argument is about **variant A versus variant B**, and it still holds exactly as written. It is
*not* an argument that either variant is covered by the clean-room receipt — since 2026-09-27 neither
is, because the device-gate repair changed `src/`. Keep the two questions apart.

The pipeline is deterministic given its inputs, and this variant changes no input the pipeline reads:

- **Seven tracked files differ** between variant A (143 tracked) and variant B (148 tracked), as
  `git ls-files` reports on 2026-09-27. Added in B: `.gitattributes`,
  `assets/prompt_model/pytorch_model.bin`, `assets/prompt_model/config.json`,
  `validation/VARIANT_FACTS.txt`, `validation/WEIGHTS_VARIANT_VERIFICATION.md`. Modified in B:
  `.gitignore` (it no longer excludes `assets/prompt_model/`) and `PROVENANCE_MANIFEST.json`
  (regenerated over B's tree). Nothing else — `src/`, `tests/`, `qa/`, `docs/`, `data/`, `vendor/`,
  `scripts/`, `tools/`, `FINALIST.lock.json`, `uv.lock` and `pyproject.toml` are byte-identical.
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
`LIMITATIONS.md`. **It has since been fixed in the entry itself** — `src/finalist_entry/cuda_gate.py`
refuses to generate when the intended CUDA path cannot execute, testing both "CUDA absent" and "CUDA
present but unable to execute a real tensor operation", with 13 tests covering both. See
`validation/POST_VALIDATION_CHANGES.md`.

The external one-liner below is retained because it is still worth running **before** an expensive
run on a host you do not control, and because it is the same check stated in a form an operator can
paste without cloning anything:

```bash
python3 -c "import torch; assert torch.cuda.is_available(), 'CUDA unavailable — generation would fall back to CPU and would not reproduce the submitted library'; print('CUDA OK:', torch.cuda.get_device_name(0))"
```

Run that **before** `uv run generate`. It is included as a gate in `FINAL_EXTERNAL_ACTIONS.md`. It is
the single highest-value operational check in this handoff, because it converts a silent
several-hour wrong-answer failure into an immediate one.
