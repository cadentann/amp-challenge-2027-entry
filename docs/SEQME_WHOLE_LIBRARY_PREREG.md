# Pre-registration — whole-library seqme qualification audit

**Frozen at 2026-09-27, before any seqme metric value was computed.** Nothing in the entry may change
as a result of this audit except by the promotion rule in §6, which is fixed here.

## 1. Why this audit exists

The public competition description uses **seqme** for computational screening of the **full
50,000-member library**. Every prior comparison in this project scored the **top-100** with APEX and
ANIA. Those are different objects measured by different instruments: a shortlist graded by our own
selector's predictors tells us nothing about how the whole library behaves under the organizers'
screening library. No completed seqme receipt existed anywhere in this project before today —
searched and confirmed absent.

## 2. Tooling, pinned

| | |
|---|---|
| implementation | `szczurek-lab/seqme`, local checkout `upstream/seqme` |
| version | 0.5.1 |
| git commit | `6b8f3221dcbae9ca2bea7fed38fa01224f6d0f82` (2026-09-01) |
| protocol followed | `docs/tutorials/benchmark_peptides.ipynb` from that same commit |
| embedder | ESM-2 `facebook/esm2_t6_8M_UR50D` (the tutorial's own choice), CPU, batch 256 |
| descriptors | seqme `Gravy`, `Charge`, `HydrophobicMoment` (modlamp-backed) |
| compute | local CPU only. **Zero GPU spend.** Measured: 50,000 peptides embed in ~1.2 min |

**The tutorial is not the organizers' scoring configuration.** It is the public worked example from the
same authors as the library the organizers named. We do not know the organizers' metric selection,
reference sets, sample sizes, or weights. No aggregate score will be computed, and no leaderboard
position will be inferred. See §7.

## 3. Datasets, frozen with hashes

Exact contents, counts and SHA-256 in `SEQME_DATASETS.json`. All eight pass a strict 20-letter amino-acid
alphabet check.

| row | n | role |
|---|---:|---|
| AMP-Prompt (shipped entry) `a91c0de9…` | 50,000 | **incumbent, unchanged** |
| AMP-Diffusion (V3 preserved) `7c8dd3a2…` | 50,000 | comparator, equal size |
| AMP-Prompt s8191 / s6007 / s4423 `67b17488…` `8e937201…` `eefa13b0…` | 50,000 each | **exposed development holdouts** — already used in Lane 1. Included **only** to measure seed-to-seed spread of each metric, never as evidence for the entry |
| antibacterial.fasta `cbbeac64…` | 39,448 | real reference — the challenge's own antibacterial set (MarLys-derived, `MLAMP…` ids) |
| training.fasta `4052e695…` | 19,670 | real reference — starter-kit training data |
| antibacterial, character-permuted, seed 42 | 39,448 | **lower anchor**, generated in-process by `sm.utils.shuffle_characters`; needs no external data |

**Reference sets we do not have, declared now rather than discovered later.** The tutorial's
`FBD (UniProt)` needs a length-filtered UniProt background, and its `AMPs`/`DBAASP` rows need
databases not retained in this project. They will be reported **missing**, not substituted. We will
not fabricate a background set.

## 4. Sampling rule — fixed before any value is seen

Two passes, both score-blind. **No metric value may influence which sequences are sampled.**

- **Pass A, full sets, no sampling.** Every metric whose cost is linear or sampled-internal runs on
  the complete set: `Count`, `Uniqueness`, `Novelty`, `Length`, `Diversity`, descriptor distributions,
  and all ESM-2 embedding metrics (embedding 50,000 costs ~1.2 min, so nothing needs subsampling for
  cost). The two 50,000-member libraries are **already equal-sized**, so the incumbent-vs-comparator
  comparison involves no sampling at all.
- **Pass B, equal-sized samples, n = 19,670.** Because FBD, FKEA, AuthPct, Precision and Recall are
  all sample-size sensitive, every row — libraries *and* references — is additionally cut to
  **n = 19,670** (the size of the smallest real set) using `sm.utils.subsample(..., n_samples=19670,
  seed=42)`, the library's own function, taking sequences in the order the file supplies them. Pass B
  is the comparison of record wherever a metric is size-sensitive; Pass A is reported alongside it.
- **Second independent sample, `seed=1337`.** Run **only** to check a result that Pass B flags as
  concerning, exactly as the directive requires. Not run pre-emptively, never averaged with Pass B.

## 5. Direction of each metric

Taken from seqme's own `Metric.objective` property and recorded verbatim in the output, not asserted
by us. `Diversity` uses the library's default `seed=0` at `k=5` (the tutorial's setting) and is
additionally reported at `k=25` as a stability check on its internal sampling.

## 6. Promotion rule — what would license changing the library

A concerning number is a **hypothesis**. A new deterministic library-construction policy may be
proposed **only** if all three of the following hold on the same metric:

1. **Direction** — the incumbent is worse than the AMP-Diffusion comparator, by that metric's own
   declared objective.
2. **Magnitude beyond noise** — the gap exceeds the **full observed range** of that same metric across
   the three exposed AMP-Prompt holdout seeds. This project has already been burned once by arguing
   over inter-portfolio gaps smaller than its own seed-to-seed spread; the spread is measured here
   first, for every metric, so that the comparison cannot repeat that error.
3. **Replication** — it survives the independent `seed=1337` sample.

One favourable metric is **not** sufficient to promote anything, and a single unfavourable metric is
not sufficient to condemn the entry. If a policy is proposed it must itself be frozen in a separate
pre-registration before being run on genuinely new seeds, and the top-100 must remain a subset of its
own library.

**Default outcome: the entry does not change.** The audit's purpose is to know where we stand in the
screening the organizers actually described.

## 7. What this audit will not do

- No official aggregate score. seqme provides components; the organizers' weighting is unpublished and
  will not be guessed.
- No leaderboard rank, no estimate of one.
- No access to hidden evaluation data or private endpoints. Every input is either already in this
  project or a public file already pinned by it.
- No claim that the tutorial's metric set is the organizers' metric set.
- No biological claim. Every number here is a distributional property of sequences.
