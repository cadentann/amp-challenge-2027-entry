# Changes made after the clean-room validation run, and why they cannot affect it

The unchanged official validator was run from a fresh clone of this repository. A small number of
files were then changed. None of them can alter what `uv run generate` does, and this records the
proof rather than asking anyone to take it on trust.

## What changed

| file | change | kind |
|---|---|---|
| `LICENSE` | added (MIT) | licence |
| `docs/` (16 files) | added — method, limitations, disclosure, eligibility, safety screen, null control, homology, reviews, evidence JSONs | documentation |
| `ENGINEERING_STATUS.md` | "Remaining hard gates" rewritten as "Hard gates — all closed"; it still described the pre-authorization state | documentation |
| `PROVENANCE_MANIFEST.json` | regenerated over the final tree | manifest |
| `tests/test_candidate.py` | the two CLI tests now pass `--no-prepare`, so they exercise preflight instead of starting a 550 MB retrieval | test-only |
| `validation/CLEANROOM_VALIDATION.txt`, `validation/CLEANROOM_VALIDATOR_LOG.txt` | added — the receipt and full log of the run itself | receipt |
| `docs/LIMITATIONS.md` | the device-dependence section updated: the clean-room run reproduced the artifacts byte-identically on a **different** GPU architecture, which the section had predicted would not happen | documentation |

Nothing in `src/`, `vendor/`, `scripts/`, `tools/`, `data/`, `scoring_adapter.py`,
`FINALIST.lock.json`, `pyproject.toml` or `uv.lock` was touched. The last two rows were
produced *by* the validated run and could not have existed before it.

## Proof of inertness

1. **Import-graph literal scan.** Every module reachable from the entry point `finalist_entry.cli`
   was parsed — 11 modules, plus `scoring_adapter.py` and `scripts/prepare_entry.py` — and every
   string constant that looks like a path was collected. **None** references `LICENSE`,
   `ENGINEERING_STATUS.md`, `PROVENANCE_MANIFEST.json`, `docs/` or `tests/`.
2. **Lock-referenced paths.** `FINALIST.lock.json` names exactly six paths:
   `vendor/frozen_selector/anchor.json`, `assets/prompt_model`, `data/antibacterial.fasta`,
   `authorization/SCALE8192_5000E_ADJUDICATION_2026-09-25.md`, `runtime/scorer` and
   `vendor/amp_prompt/vocab.txt`. No changed file is among them.
3. **`PROVENANCE_MANIFEST.json` is read only by `tools/verify_manifest.py`** and written only by
   `tools/build_manifest.py`. Neither is invoked by `generate` or by the validator, which runs
   `git clone`, `uv sync`, `uv run --no-sync generate` and nothing else.
4. **Tests are not executed by the validator.** `pyproject.toml` defines one console script,
   `generate`; there is no test hook in the install or run path.
5. The only `LICENSE` string inside the executed tree is the path `assets/ania/LICENSE` in
   `vendor/evaluator/RUNTIME_MANIFEST.json` — a pinned third-party file, unrelated to this
   repository's new `LICENSE`.

## Honest statement of scope

The validated artifact is the tree as it stood at clean-room run time, plus the changes above. The
generation and selection code, the frozen selector, the lock, both environment locks and every
retrieved asset are byte-identical between the two. What was not re-validated is documentation, a
licence file, a regenerated manifest and a test-only flag.


---

# Defect found after validation, and fixed

**`scripts/prepare_entry.py` installed the Linux runtime lock on non-Linux hosts.**

Found by running the script on macOS/arm64 for an unrelated analysis. It correctly detected the
platform and correctly matched the macOS equivalence receipt's environment, and then unconditionally
copied `validation/SCORER_RUNTIME.lock.json` — which is the **Linux** lock — into the runtime. The
final hash check passed precisely because that Linux lock is the hash `FINALIST.lock.json` pins, so
nothing complained. A macOS host would have ended up with a runtime labelled `LINUX_X86_64` while
running a Darwin venv.

The clean-room Linux validation was unaffected: on Linux the Linux lock is the correct one, which is
why the defect survived that run.

**Fix.** `prepare_entry.py` now declares `REQUIRED_PLATFORM = ("Linux", "x86_64")`, refuses to
promote on any other platform with an explicit explanation, re-asserts the platform immediately
before copying the lock so a future edit cannot reintroduce the bug, and additionally verifies that
the validated lock's `environment` matches the environment actually built. Verified on macOS: the
run now fails closed with a clear message and leaves the runtime `PENDING_CROSS_EVALUATOR_EQUIVALENCE`.

This makes an existing constraint explicit rather than changing it. The entry was always Linux-only —
`FINALIST.lock.json` pins a single runtime-lock hash and no macOS runtime lock was ever validated —
but nothing said so, and the script quietly papered over it.


---

# 2026-09-27: a change that IS in the executed path — the silent-CPU-fallback repair

**Read this section differently from the two above.** Everything recorded so far was provably inert:
documentation, a licence, a manifest, a test flag, and a script that the validator never runs. **This
change is not.** It adds a module to `src/finalist_entry/` and a call to it from `pipeline.run()`, so
it is reachable from the entry point, and the honest status is that **the clean-room validator receipt
does not cover it.**

## The defect

The locked `device_policy` is `auto_prefer_cuda`. When CUDA is unavailable it resolves to CPU and
generation proceeds — silently. On 2026-09-26 a rented host presented a healthy RTX 5090 to
`nvidia-smi` while every PyTorch build returned `torch.cuda.is_available() == False` with
`CUDA unknown error`. Generation started on CPU and would have produced a library that does not match
the submitted artifacts, with nothing in the output saying so. An organizer's reproducibility check on
such a host would have concluded that our entry does not reproduce.

## The repair

A new module `src/finalist_entry/cuda_gate.py`, plus:

| file | change |
|---|---|
| `src/finalist_entry/cuda_gate.py` | **new.** Refuses to generate when the intended CUDA path cannot execute |
| `src/finalist_entry/pipeline.py` | `preflight()` takes `enforce_device_gate`, calls the gate before the scorer probe, returns the verdict; `run()` enforces it and records it in the receipt as `device_gate` |
| `src/finalist_entry/cli.py` | `--preflight-only` reports the verdict without raising, so it stays usable as a diagnostic on any host |
| `tests/test_candidate.py` | **13 new tests**, 35 total, all passing |

**Two checks, because the failure has two shapes.** CUDA absent or no device visible; and CUDA
reporting available but unable to execute — which `is_available()` alone does not catch, and which is
exactly what the RTX 5090 host did.

**The real-tensor probe runs in a child process, using `sys.executable`** — inside the locked
generator environment, never an unrelated system interpreter. That is a deliberate trade-off. An
in-process probe would be a marginally stronger test, but it would make the generating process create
a CUDA context and launch a kernel it did not launch when the submitted artifacts were produced. Those
artifacts are byte-reproducible and several receipts bind those exact bytes; we will not add
un-receipted CUDA work to the path that produces them. In the child, the production process performs
**exactly** the CUDA work it performed before — no extra context, no extra allocation, no extra
kernel, no RNG touched.

**The scorer is untouched.** APEX and ANIA run in a separate pinned runtime and legitimately run on
CPU. `scoring.py` and `scoring_adapter.py` are byte-identical, and a test asserts (against the parsed
module, not its text) that `cuda_gate` imports and calls nothing from them.

**There is an explicit escape hatch:** `FINALIST_ALLOW_CPU_GENERATION=1` proceeds on CPU after
printing a banner saying the output will not match the submitted artifacts. It exists so that
legitimate local CPU work remains possible; it is not for producing a submission.

## What was demonstrated, and what was not

**Demonstrated — the ten computation modules are byte-identical.** `amp_prompt.py`, `library.py`,
`frozen_selector.py`, `scoring.py`, `publish.py`, `evidence.py`, `fasta_io.py`, `hashing.py`,
`lock.py`, `__init__.py` — every one hashes the same before and after. Sampling, RNG seeding,
eligibility, selection, publication and hashing are not merely unaffected in principle; they are the
same bytes. Only `pipeline.py` and `cli.py` differ, plus the new module.

**Demonstrated — identical output through a differential run.** `pipeline.run()` was executed to
`COMPLETE` against the same fixed generator stream and the same fixed scores, once with the
pre-repair `src/` taken from `git HEAD` and once with the repaired `src/`. Published bytes:

| | pre-repair | repaired |
|---|---|---|
| `library.fasta` SHA-256 | `c66d6370de377271…` | `c66d6370de377271…` |
| `top.fasta` SHA-256 | `bcbd2c4daaf90286…` | `bcbd2c4daaf90286…` |
| receipt SHA-256, excluding `run_id` and the new `device_gate` | `9c5ec95d17a065da…` | `9c5ec95d17a065da…` |

The known output prefix is unchanged: both publish `>seq1 / AAAAAAAAAAAA / >seq2 / CAAAAAAAAAAA / …`
identically. Evidence: `qualification_20260927/evidence/DEVICE_GATE_DIFFERENTIAL.json`.

**Not demonstrated — a GPU run.** The fixtures above pin the orchestration; they do not exercise CUDA,
because no GPU was reachable when this was written. **The receipt this change needs is one
authoritative clean-clone run of the unchanged official validator on the chosen release variant.** That
single run closes this gap *and* the weights-variant gap in `docs/WEIGHTS_VARIANT_VERIFICATION.md`
together, which is why it is one run and not two.

**Until that run exists, the correct statement is:** the eight validator checks passed against the tree
as it stood before this repair; the repair is argued and fixture-tested to be output-neutral, and is
not yet receipted. Anyone who prefers the receipted tree can check out the commit before this one — it
is preserved in history and it is the tree the receipt names.
