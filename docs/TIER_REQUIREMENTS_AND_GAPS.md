# Participation tier requirements, verified against the primary sources — and where we fall short

Checked against the official template README (`upstream/amp-challenge-2027/README.md`) and the
organizer proposal §"Teams can participate in the competition in one of two ways". Both are quoted
rather than paraphrased. **No organizer was contacted; nothing here is an adjudication.**

## What the sources actually require

### Minimum (benchmark participation)

| requirement | our status |
|---|---|
| Abstract summarizing the method | **Ready** — `docs/METHOD_AND_ABSTRACT.md` |
| Library of 50,000 designed AMPs | **Ready** — `artifacts/library.fasta`, 50,000 unique |
| Ranked top-100 with selection documentation | **Ready** — `artifacts/top.fasta` + method section |
| Summary of training data, external databases, filters | **Ready** — `docs/DATA_AND_MODEL_DISCLOSURE.md`, with a disclosed gap (below) |
| GitHub repo (private is fine) **"with model weights and inference code"**; read access to @RasmusML and @szymczakpau | **GAP — see below.** Inference code yes; weights are retrieved, not contained |

### Full (co-authorship eligibility) — all of the above, plus

| requirement | our status |
|---|---|
| **Public** GitHub repo with model weights, inference code, usage docs | **Same weights gap**, and public visibility is your decision |
| Permissive OSI licence (MIT, BSD-3-Clause, Apache 2.0) | **Ready** — MIT at repo root |
| Uses `uv`, with `uv.lock` and a defined Python version | **Ready** — `uv.lock`, `requires-python = "==3.12.*"` |
| Entry point runnable via `uv run generate`; any extra arguments must have defaults | **Ready** — `generate` console script; all arguments defaulted |
| Fixed default random seed, identical output on repeated runs | **Ready** — seed 42; two byte-identical runs recorded |
| Full training data disclosure; non-public data released under a permissive licence | **Partial — see below** |

> The proposal adds: *"Organizers will verify reproducibility by running `uv sync` followed by the
> designated entry-point script, and comparing the output against the submitted library."*

---

## Gap 1 — the repository does not contain the model weights

**Both tiers ask for a repository "with model weights and inference code".** Ours contains inference
code, usage documentation and a hash-pinned retrieval script that fetches the weights from their
published sources and verifies every byte. It does **not** contain the weights themselves.

**Correcting our own earlier justification.** Previous drafts said shipping weights "would breach the
challenge's 500 MB release limit". **There is no such limit in the rules.** Neither the proposal nor
the template mentions any size cap. The `maximum_release_bytes: 500000000` in our `ASSET_SOURCES.json`
is a **self-imposed policy from an earlier phase of this project**, and citing it as an organizer
constraint was wrong.

**Licensing does not block redistribution either:**

| asset | size | licence | redistribution |
|---|---|---|---|
| AMP-Prompt checkpoint (`pytorch_model.bin`) | 340 MB | CC-BY-4.0 | **Permitted** with attribution |
| APEX weights (8 files) | 229 MB | MIT | **Permitted** with attribution |
| ANIA weights (3 files) | 3.4 MB | MIT | **Permitted** with attribution |

So the real obstacles are practical, not legal or rule-based: GitHub rejects individual files over
100 MB without **Git LFS**, and LFS free-tier storage and bandwidth are 1 GB each per month.

**What this means for your decision.** A narrow reading is that "model weights" means the *generative*
model — the 340 MB AMP-Prompt checkpoint — since the APEX/ANIA weights are used for ranking, not
generation. Shipping just that via Git LFS is well within a free LFS allowance. A broad reading would
include the evaluator weights too, totalling ~572 MB, which exceeds the free LFS tier.

**We have not added the weights to the repository**, because doing so changes what you would publish
and (for LFS) may incur a quota you have not agreed to. It is a one-command change if you want it, and
`docs/WEIGHTS_IN_REPO_OPTION.md` gives the exact commands. **Whether hash-pinned retrieval satisfies
the requirement is unknown and is the single largest identified risk to co-authorship eligibility.**

## Gap 2 — training-data disclosure is second-hand for the generator

The requirement is *full* training data disclosure. For APEX and ANIA we can point to published
training sets, and for ANIA we reconstructed the actual membership from its own published downloads.
For **AMP-Prompt we did not assemble or inspect its training corpus** — we disclose what its authors
disclose, and we cannot certify it is disjoint from the evaluation panel or from
`data/antibacterial.fasta`. `docs/DATA_AND_MODEL_DISCLOSURE.md` states this. Whether second-hand
disclosure counts as "full" is for the organizers, not us.

No proprietary or non-public data was used by us, so the "must be released publicly" clause does not
bite.

## Gap 3 — reproducibility is verified by comparing *their* run to *our* library

This is the requirement with the most technical risk, and it is not the same as "identical output on
repeated runs" (which we satisfy — two byte-identical runs on one machine).

The organizers will run the entry point and **compare the output against the submitted library**. Our
generation is a sampling process on a GPU. We have evidence it is more portable than we expected:
byte-identical output on an **RTX 4090 (Ada)** and again on an **RTX A4500 (Ampere)**, two different
architectures. But two devices is not all devices, and we have never tested CPU execution or a
non-CUDA backend. **If the organizers run on hardware where the sampling diverges, the comparison
fails and co-authorship eligibility is at risk.** Nothing in our control fixes this; it is disclosed
in `docs/LIMITATIONS.md`.

The entry also requires **Linux x86_64**, because `FINALIST.lock.json` pins the only scorer-runtime
lock that was ever validated. On another platform `prepare_entry.py` refuses and the entry fails
closed rather than scoring against an unvalidated runtime.

## Third-party licences and attribution, for the record

| component | licence | how we comply |
|---|---|---|
| AMP-Prompt / AMP-Designer weights | CC-BY-4.0 | attributed in README, `ASSET_SOURCES.json`, abstract; retrieved from Zenodo DOI 10.5281/zenodo.17018363 |
| APEX (`apex-pathogen`) | MIT | attributed; two files modified and redistributed with a NOTICE describing the changes |
| ANIA | MIT | attributed; retrieved at a pinned commit |
| MarLys AMP database | CC0 | used for novelty analysis only; not redistributed |
| QMAP benchmark | see package | used for the predictor audit only; not redistributed |
| HemoPI2 | **GPL-3.0** | used as an **external analysis tool only** — never imported, never shipped, never part of the pipeline, so its copyleft does not reach our MIT repository |
| Our own code | MIT | `LICENSE` at repo root |

## Bottom line

Everything the minimum tier asks for exists and is prepared, **except that the repository retrieves
its weights rather than containing them**, which affects both tiers. An MIT file plus public visibility
does **not** by itself establish co-authorship eligibility: the weights question, the second-hand
generator-training disclosure, and the cross-device reproducibility comparison are all unresolved, and
only the organizers can resolve them.
