# Lane 13 — environment fuzzing: one real defect, and what still stands

The goal was to make it hard for an organizer's environment to break the entry for mundane reasons.
It found one genuine defect, which no amount of re-running on Linux could have caught.

## Cases exercised

| case | result |
|---|---|
| clean `git clone` by the validator itself, no cache | **PASS** — all eight official checks, 116 min |
| fresh `uv sync` on a machine with no prior environment | **PASS** |
| no model weights present, no asset cache | **PASS** — `generate` retrieves and verifies ~550 MB itself |
| no Git LFS | **PASS** — nothing is fetched through LFS; APEX weights come from GitLab's API with `lfs=true` resolved server-side |
| different GPU architecture (Ampere instead of Ada) | **PASS**, and byte-identical output |
| **second operating system (macOS/arm64)** | **FAILED — defect found, now fixed** |
| running from a different working directory | PASS — paths resolve from the lock's own location |
| extra keys in `FINALIST.lock.json` | correctly **refused**: exact key-set validation |
| runtime lock left `PENDING_CROSS_EVALUATOR_EQUIVALENCE` | correctly **refused** by the adapter |
| `uv run` nesting (generate invoking a second `uv sync` for the scorer) | PASS — `UV_*` and `VIRTUAL_ENV` are stripped before the inner sync |

## The defect

`scripts/prepare_entry.py` **installed the Linux runtime lock on macOS.** It detected the platform
correctly, matched the macOS equivalence receipt's environment correctly, and then unconditionally
copied `validation/SCORER_RUNTIME.lock.json` — the **Linux** lock — into the runtime. The final
integrity check passed precisely because that Linux lock is the hash `FINALIST.lock.json` pins, so
nothing complained. A macOS host would have held a runtime labelled `LINUX_X86_64` while running a
Darwin virtualenv.

The Linux clean-room run could not have found this: on Linux, the Linux lock is the right one.

**Fix.** `prepare_entry.py` now declares `REQUIRED_PLATFORM = ("Linux", "x86_64")`, refuses on any
other platform with an explanation, re-asserts the platform immediately before copying the lock so a
future edit cannot reintroduce the bug, and verifies the validated lock's `environment` against the
environment actually built. Verified on macOS: it fails closed and leaves the runtime pending.

This surfaced a constraint that was always true but never stated — the entry is Linux-only, because
`FINALIST.lock.json` pins one runtime-lock hash and no macOS runtime lock was ever validated. The
README now says so.

## Cases deliberately not fuzzed

- **Asset mirror unavailable.** `prepare_entry.py` fails closed with the expected and observed hashes
  when an upstream source serves different bytes, which is the correct behaviour, but we did not
  simulate an outage. If Zenodo, GitLab or GitHub is down at validation time the entry cannot be
  prepared, and there is no fallback mirror. This is a real residual risk and it is stated rather
  than engineered around: mirroring 550 MB of third-party weights into the repository would breach
  the 500 MB release limit and the licences' redistribution expectations.
- **Locale and filesystem ordering.** Sequence ordering is generation order or an explicit sort, never
  directory iteration order, and the one place upstream relied on `glob` order was replaced with
  `sorted(glob(...))` (see `vendor/evaluator/assets/apex/NOTICE.md`). Not separately fuzzed.
- **CPU-only execution.** Untested. The device policy is `auto_prefer_cuda`, so it would run, but the
  generated sequences would differ and no receipt covers it.
