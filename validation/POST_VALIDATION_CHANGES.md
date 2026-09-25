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

Nothing in `src/`, `vendor/`, `scripts/`, `tools/`, `data/`, `scoring_adapter.py`,
`FINALIST.lock.json`, `pyproject.toml` or `uv.lock` was touched.

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
