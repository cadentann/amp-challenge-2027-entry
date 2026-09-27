# MPOGAN — lead reopened, verified, and closed on rights

**Outcome: closed. No inference was run, no compute was spent, $0.00.**
**But the reason recorded in the ledger was wrong, and that correction matters more than the outcome.**

## What the ledger said, and why it was wrong

`docs/FRONTIER_LEDGER.md` and `docs/LANE10_GENERATOR_FRONTIER_CLOSED.md` grouped MPOGAN with eight
other 2026 generators and closed them all on one premise:

> "Final documented scan found **no locatable public weights** for the 2026 candidates."

**For MPOGAN that premise is false.** The weights are in the repository, and so is the generation
command. Verified today against the GitHub API rather than a search engine:

| verified fact | value |
|---|---|
| released generator checkpoint | `models/gen_models/MPOGAN_finetuning/700_gen.pth` — **present**, **217,695 bytes** |
| other released weights | `700_dis.pth` and `AMP_classifier/best_model/best_model.pth`, 31,920,185 bytes each; `2000_gen.pth`, `pre_gen.pth`, 217,695 bytes each |
| inference entry point | `generateCandidates.py` → `MyUtils.generate_seqs`, which loads only the generator checkpoint and calls `gen.sample(n)` |
| device | `generate_seqs(..., device: str = 'cpu')` — **CPU by default**; no GPU needed |
| the authors' own documented example | `python generateCandidates.py --model_id 700 --num_outputs 50000 --run_name MPOGAN_finetuning` |
| dependencies | `requirement.txt`: torch 1.12.1, transformers 4.24.0, modlamp, biopython — modest |
| repo activity | last push 2025-05-09, not archived |

The authors' own usage example generates **exactly 50,000 sequences**. So the honest statement is:
**inference feasibility is established, the asset exists, and it would have cost nothing to run.** The
lane was closed on a factual claim that does not survive checking. Recorded here rather than quietly
fixed.

## Why it closes anyway — and this reason is checkable

**The repository carries no licence.**

| check | result |
|---|---|
| GitHub API `license` field for `23AIBox/MPOGAN` | **`null`** |
| `LICENSE` at repo root | **HTTP 404** |
| `LICENSE.md` at repo root | **HTTP 404** |
| `readme.md` reuse terms | none stated |
| a Zenodo or other deposit with terms | none found |
| the paper (*Advanced Science* 2025, DOI 10.1002/advs.202503443) | the **article** is CC BY 4.0 |

The article's CC BY 4.0 licence covers the **article**. It does not licence a separate repository's
source code or model weights. Public visibility is not a grant of rights, and "no licence" defaults to
all rights reserved — the same principle this project already applied to itself when it stopped
claiming that an MIT file plus public visibility guarantees anything.

**This blocks both tiers, not just the public one.** The competition template requires a GitHub
repository containing **model weights and inference code** at the *minimum* tier as well, and the full
tier additionally requires a permissive OSI licence on our repository. An entry built on MPOGAN would
have to ship, or depend on, a checkpoint we have no right to ship. There is no version of this that is
clean, and provenance is the one thing this entry has consistently refused to compromise.

## What was deliberately not done

- **No inference.** The gate in the directive is "only if authentic inference **and a viable
  submission path** are established". Inference is feasible; the submission path is not. Running it
  would have produced numbers we could not use and a temptation to use them anyway.
- **No two-seed screen**, no evaluation, no comparison. Nothing to compare.
- **No attempt to reach the authors.** Contacting third parties needs explicit approval and there are
  four days to the deadline; a permission grant could not be obtained, reviewed and validated in time
  even if it arrived.
- **Its own classifier was never going to be the judge.** Had this proceeded, MPOGAN's bundled
  `AMP_classifier` would have been excluded and the frozen evaluators used, with equal eligible
  candidate counts. Noted so the record shows the comparison design existed; it was not needed.

## The general lesson, which applies beyond MPOGAN

`LANE10_GENERATOR_FRONTIER_CLOSED.md` closed **nine** generators on a single shared premise. That
premise has now been checked for one of them and found wrong. The other eight were **not** re-checked
today, and this document is not evidence about them. What the closure can honestly claim is a
**time-and-validation** argument — four days cannot clear the funnel the incumbent cleared plus a
prospective protocol — and that argument stands on its own. The asset-availability claim should not be
relied on for any of the nine without the kind of direct verification done here.
