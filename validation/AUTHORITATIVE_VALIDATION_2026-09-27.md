# Authoritative clean-clone validation of the weights-bundled variant — PASSED

**All eight unchanged official validator checks passed from a clean clone of the release variant that
will actually be pushed. Wall clock 107m40s. Exit 0.** This is the receipt the two remaining gaps
needed, and it closes both of them in one run.

```
[1] Cloning /workspace/entryB → /workspace/submission
[2] Installing dependencies
[3] Generating library
[4] Verifying full library
[5] Verifying top list
[6] Checking library overlap with .../antibacterial.fasta
[7] Checking top similarity with .../antibacterial.fasta
[8] Checking reproducibility
All checks passed. Submission is valid!
real	107m40.234s
```

Full log: `AUTHORITATIVE_RUN_LOG.txt` (999 lines, unedited). Machine facts: `AUTHORITATIVE_FACTS.txt`.
Both run receipts: `AUTHORITATIVE_COMPLETE_RECEIPTS.json`.

## What was validated

| | |
|---|---|
| repository | **variant B, the weights-bundled one** — `RELEASE_VARIANTS/entry-with-weights-lfs` |
| commit | `2ceb306b6cac67150ab4536754bfce34e00d1329`, and the clone's HEAD is the same commit |
| validator | `verify_submission.py` SHA-256 `3f2eb1bd61200abfccf07d86e9c226d57f3d12abcf25715af1d90f41531942cf` — byte-identical to the pinned official live snapshot. **Unchanged.** |
| host | RunPod Community, **NVIDIA RTX A4500** (Ampere, capability 8.6), driver 580.159.03, 32 cores |
| toolchain | git 2.43.0, **git-lfs 3.4.1**, uv 0.12.19, Python 3.13.5 + Levenshtein 0.27.5 for the validator |

## The two gaps this closes

**1. The weights-bundled variant had never completed a full run.** Verification had stopped at LFS
transfer and model loading because two pods failed for infrastructure reasons. Now:

| check | result |
|---|---|
| checkpoint materialised by Git LFS | **340,569,639 bytes**, SHA-256 `47944ff42f7ea6a448340d44c2027329833205dd658ec4777e77777bdab1adc9` — the pinned hash |
| `git lfs ls-files` in the clone | `47944ff42f * assets/prompt_model/pytorch_model.bin` |
| model actually loaded from the bundled path | `GPT2LMHeadModel` from `/workspace/submission/assets/prompt_model` — visible in the log |
| scorer runtime built and promoted | `d74ea38c347d7ce99f885566940b2addedb0ebc1097532bded070ab16c3801a1`, the pinned lock |
| `library.fasta` | `a91c0de9200a3d9f4377bfc6f81d36d21ea15bb9c940bd91fab797cd5ae2308b` — **identical to the submitted artifact** |
| `top.fasta` | `ece3b7062d55d1ac4eb35f60e450cebec229ebfba63b5a0ab7214ecd4e5cb841` — **identical to the submitted artifact** |
| `raw_generated` | 51,712 — identical to the reference run |
| `selector_pool_count` / `eligible_for_top` | 48,133 / 48,133 — identical to the reference run |
| reproducibility, check [8] | a second full generation produced the same bytes |

So the checkpoint arriving by `git lfs` rather than by HTTPS changes nothing, which had been argued
and is now measured. **This is also a third completed run on Ampere**, after the two inside the earlier
clean-room validation.

**2. The silent-CPU-fallback repair had no GPU receipt.** It now has three, from the validated run
itself. Both `COMPLETE.json` receipts carry the new field:

```json
"device_gate": {
  "status": "CUDA_OK", "healthy": true, "enforced": true,
  "cpu_override_requested": false, "device_policy": "auto_prefer_cuda",
  "probe": { "ok": true, "probe_value": 8256.0, "stage": "done",
             "torch_version": "2.8.0+cu128", "device_name": "NVIDIA RTX A4500",
             "capability": [8, 6], "child_returncode": 0 } }
```

`probe_value: 8256.0` is the exact arithmetic the gate demands, so the child-process probe really
executed a CUDA kernel inside the locked generator environment and checked the result. **And the
output is byte-identical to the pre-repair artifacts, which is the proof the repair costs nothing.**

## The negative test: the gate fires on real hardware

Not a stub — the same validated clone, same GPU, with the device hidden:

| command | result |
|---|---|
| `CUDA_VISIBLE_DEVICES="" uv run generate` | **exit 1, refused.** `RuntimeError: REFUSING TO GENERATE: the intended CUDA generation path cannot execute.` Probe reached `availability`, `torch.cuda.is_available(): False`, `visible devices: 0` |
| `CUDA_VISIBLE_DEVICES="" uv run generate --preflight-only` | exit 0, reports `"status": "CUDA_UNAVAILABLE"`, does not raise — still usable as a diagnostic anywhere |
| with `FINALIST_ALLOW_CPU_GENERATION=1` | accepted, `"status": "CUDA_UNAVAILABLE_CPU_OVERRIDE_ACCEPTED"`, after printing the banner `The output will NOT match the submitted artifacts. Do not submit it.` |

Before this repair, the first of those three would have spent roughly 50 minutes producing a library
that silently does not match the submission.

## A defect this run exposed in our own test suite

`tests/test_candidate.py::test_cli_reports_absent_lock_explicitly` **failed on the pod** while passing
locally. The cause is worth recording because it is the more instructive half of this run.

The test intended to prove the CLI refuses when `FINALIST.lock.json` is absent. It set
`FINALIST_PROJECT_ROOT` and ran the CLI with `cwd` in a temp directory — but `cli.py` honours neither:
it derives `PROJECT_ROOT` from its own `__file__`. The subprocess therefore kept using the real
repository. On an **incomplete** checkout preflight failed anyway, for an unrelated reason, so the test
went green. On a **fully prepared** checkout — which is what this run produced, and the first one that
ever existed — preflight succeeds and the test failed.

**It had been passing for the wrong reason.** Fixed by copying the package into a temp tree so
`parents[2]` genuinely lands on a lock-less directory, and by asserting the isolation took rather than
trusting it. Verified both ways: 35 tests pass locally, and **35 tests pass on the fully prepared
checkout on the pod** — the exact configuration that exposed the fault. Production code untouched; the
validator does not run tests, so this receipt stands.

## Three failed starts, recorded rather than tidied away

Attempt logs are retained as `auth_attempt1.log`, `auth_attempt2.log`, `auth_attempt3.log`.

1. **A pod that never got a network address.** RTX 4090, `publicIp` empty and `machine` metadata empty
   after 13 minutes — the same failure seen once before. Terminated; ~$0.08. Fixed by requesting
   `supportPublicIp: true`.
2. **`fatal: detected dubious ownership in repository`.** The transferred `.git` carried a foreign uid,
   so git refused every command and the validator's own clone step failed first. Fixed with
   `chown -R root:root` and `git config --global --add safe.directory '*'`.
3. **`pip install Levenshtein` succeeded and `python3` still could not import it.** On this Ubuntu
   24.04 image `pip` is bound to **python3.13** while `python3` is **3.12**. Fixed by running the
   validator with the interpreter that actually has the module.

All three are now in `FINAL_EXTERNAL_ACTIONS.md`, because an organizer or a future operator will hit
the same three and each one looks like a broken submission rather than a broken host.

## Cost

Pod `bv3eakv70sfj7x`, Community RTX A4500 at **$0.19/hr**, 20:00:46Z → 22:00:52Z, **2h 0m ≈ $0.38**.
Plus the two failed starts, ≈ **$0.17** together. **Total ≈ $0.55.** An independent non-LLM watchdog was
armed before the pod was used, with a hard stop at 00:30:45Z; it observed the pod's absence at
22:01:00Z and exited on its own. **0 pods, $0.00/hr** confirmed after termination.
