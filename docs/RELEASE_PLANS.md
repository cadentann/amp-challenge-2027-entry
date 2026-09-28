# Two release plans, and which one I would choose

Two variants of the **same validated entry** exist. They differ only in packaging — identical
artifacts, identical lock, identical `src/`, identical `uv.lock`.

| | variant A — retrieval | variant B — weights bundled |
|---|---|---|
| path | `FINAL_SUBMISSION_READY/amp-prompt-consensus-entry` | `RELEASE_VARIANTS/entry-with-weights-lfs` |
| commits | 29 | 30 (A's history plus one) |
| repo size | 9.0 MB | ~659 MB working tree (325 MB LFS object) |
| model weights | fetched and hash-verified at run time | **contained**, via Git LFS |
| needs Git LFS | no | yes |
| clone without LFS | works | degrades to retrieval (see below) |

Everything else is byte-identical. Five files differ in total: `.gitattributes` and
`assets/prompt_model/{pytorch_model.bin,config.json}` added, `.gitignore` and
`PROVENANCE_MANIFEST.json` modified. **None is referenced by any of the 11 modules reachable from the
entry point.**

---

## MINIMUM tier — private repository

**Requirements** (official template): abstract; 50,000-peptide library; ranked top-100 with selection
documentation; summary of training data, external databases and filters; **GitHub repository, private
is fine, with model weights and inference code**; read access to @RasmusML and @szymczakpau.

**Plan:** push **variant B**, keep the repository **private**, grant the two organizers read access.

Rationale: the requirement asks for weights in the repository at *both* tiers, so B satisfies it
literally either way. Privacy costs nothing here — LFS bandwidth is only consumed by the organizers'
clone.

**Outcome:** experimental results returned and inclusion in the benchmark. **No co-authorship.**

---

## FULL tier — public repository, co-authorship eligibility

**Additional requirements:** public repository following the template, with model weights, inference
code and usage docs; permissive OSI licence; `uv` with `uv.lock` and a pinned Python version; entry
point runnable as `uv run generate` with all arguments defaulted; fixed default seed producing
identical output on repeated runs; full training-data disclosure.

**Plan:** push **variant B**, make the repository **public**.

**Status against each item:**

| item | status |
|---|---|
| public repo following the template | ready — your action |
| model weights in the repo | **ready in variant B, and now validated end-to-end** — all eight official checks passed from a clean LFS clone on 2026-09-27 |
| inference code + usage docs | ready — `README.md`, 40 documents in `docs/` |
| OSI licence | ready — MIT at repo root |
| `uv` + `uv.lock` + pinned Python | ready — `requires-python = "==3.12.*"` |
| `uv run generate`, args defaulted | ready and validated |
| fixed seed, identical repeated output | ready — the official validator's own second run confirms it |
| full training-data disclosure | **partial** — see below |

**Two residual risks, neither fixable by us:**

1. **Generator training-data disclosure is second-hand.** We did not assemble or inspect AMP-Prompt's
   training corpus; we report what its authors report, and cannot certify it is disjoint from the
   evaluation panel or from `data/antibacterial.fasta`.
2. **Reproducibility is verified by comparing the organizers' run to our submitted library.** Our
   artifacts have reproduced byte-identically in **six completed runs across two GPU architectures** —
   two on Ada (RTX 4090: the shipped run and its repeat) and four on Ampere (RTX A4500: two inside the
   earlier clean-room validation, and two more inside the 2026-09-27 authoritative validation of
   **variant B**, where the checkpoint was delivered by Git LFS). That is materially stronger than when
   this risk was first written, but it is two architectures, not all devices, and CPU execution is
   untested.

   > **CORRECTION, 2026-09-27.** An earlier version of this line claimed **three** architectures,
   > adding Blackwell (RTX 5090). **There is no receipt for that and the claim was false.** The
   > RTX 5090 pod is the one documented in `docs/WEIGHTS_VARIANT_VERIFICATION.md`: `nvidia-smi` saw
   > the device but no PyTorch build could initialise CUDA, generation silently fell back to CPU, and
   > the pod was terminated without producing any output — so it reproduced nothing. The only
   > completed receipts are `validator_results/CLEANROOM_VALIDATION.txt` (A4500, two runs,
   > `a91c0de9…` / `ece3b706…`) and the two RTX 4090 end-to-end runs. `docs/LIMITATIONS.md` §10
   > always stated two architectures correctly; this document did not, and it is the corrected one.

---

## Recommendation

**Go full / public, using variant B.**

Three reasons.

**The main objection to going public has been removed.** The weights gap was the one requirement we
plainly did not meet, and variant B meets it with the checkpoint's LFS pointer OID equal to the very
SHA-256 the lock pins — the packaging carries its own integrity check.

**Everything else the full tier asks for was already built and validated**, not retrofitted: `uv` with
a locked environment and pinned Python, a defaulted `uv run generate` entry point, a fixed seed whose
identical repeated output the official validator confirms itself, an MIT licence, and disclosure
documents that state their own gaps rather than papering over them. Choosing minimum would discard
work that already satisfies the harder bar.

**The asymmetry probably favours trying, and the word "probably" is doing real work.** Minimum
forecloses co-authorship by construction. Full asks for everything minimum asks for plus more, and this
entry contains all of it.

> **CORRECTION.** An earlier version of this paragraph said that if the organizers judge a full-tier item
> unmet, "the downside is being assessed at the minimum tier anyway". **No public rule says that.** We
> have found nothing in the proposal or the template describing what happens to a full-tier submission
> that fails a full-tier requirement — whether it is reassessed at the minimum tier, returned for
> correction, or rejected. Presenting an unspecified outcome as an automatic fallback was an unsupported
> claim and it is withdrawn.

What can honestly be said: the submission **contains** every minimum-tier deliverable, so a reassessment
at the minimum tier would have the material it needs. Whether the organizers perform one is **unknown and
is theirs to decide.** If a guaranteed benchmark place matters more to you than a chance at
co-authorship, that uncertainty is a real argument for choosing minimum, and it is not a defect in the
entry.

**What would change my recommendation.** Publishing is irreversible in practice. If you would not want
this work public regardless of the co-authorship outcome, take the minimum tier — that is a preference,
not a defect, and nothing here should override it. Note also that public visibility plus an MIT file
does **not** guarantee eligibility: the two residual risks above are real and are the organizers' call.

**The choice is yours.** Nothing has been pushed, published, or shared, and neither variant has a git
remote configured.
