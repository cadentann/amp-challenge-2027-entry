# Training data, external database and model disclosure

The challenge requires "full training data disclosure" and "a short summary of training data,
external databases, and any filters applied". This is that disclosure, stated at the limit of what
we can actually verify.

## 1. We trained nothing

No model in this entry was trained, fine-tuned, distilled or quantized by us. Every model is used
as publicly released, at a pinned hash. Our contribution is the selection policy and the
experimental protocol that chose it.

## 2. Generator

| item | value |
|---|---|
| Model | AMP-Prompt (AMP-Designer), soft-prompt GPT-2 |
| Source commit | `07d455dd6eb7ef61fe03b85732966caa32bf3dc4` |
| Weights | Zenodo DOI **10.5281/zenodo.17018363**, `prompt_model.zip` |
| Archive SHA-256 | `71af768d1b7dd0f41db7c395179180dfc85fd28c46f5fa6ed143844c78ffbc5d` |
| Checkpoint SHA-256 | `47944ff42f7ea6a448340d44c2027329833205dd658ec4777e77777bdab1adc9` |
| Licence | CC-BY-4.0 (Zenodo record metadata) |

**Its training corpus is disclosed by its authors, not by us.** We did not assemble, inspect or
modify it. We therefore cannot certify that the generator's training data is disjoint from the
challenge's evaluation panel or from `data/antibacterial.fasta`. We state this as a limitation
rather than asserting independence we have not verified.

## 3. Scoring predictors

| predictor | source | role |
|---|---|---|
| APEX (8 ensemble members, 11 strain heads) | GitLab `machine-biology-group-public/apex-pathogen`, per-file SHA-256 pinned | predicted MIC per strain |
| ANIA (EC, PA, SA) | GitHub `SilverGojo4/ANIA` at commit `7bde436e0b5df8e44f9a598e312bd1944006cb3d`, per-file SHA-256 pinned | predicted log10 MIC |

Both are used as released. **Neither was retrained or recalibrated.**

**Shared ancestry — material limitation.** APEX and ANIA are not independent evidence. They are
trained on overlapping public antimicrobial-peptide measurement data. Agreement between them is
weaker corroboration than it appears, and our consensus selector inherits any bias common to both.
Recorded diagnostics also found measured-threshold transfer failures: predicted MIC thresholds did
not transfer cleanly to held-out measured data. We do not claim either predictor is calibrated for
the organizers' strain panel.

## 4. External databases

| database | use | SHA-256 |
|---|---|---|
| `data/antibacterial.fasta` (supplied by the challenge, 39,448 unique sequences) | exact-overlap exclusion for the library; ≤0.80 similarity rule for the top-100 | `cbbeac64ba95746d87961e8ad9dd0849ae8058d15a300b2e7f6990730ca521e9` |

A fixed 996-member **anchor** derived from earlier project scoring provides the percentile
reference for `CONSENSUS_FIXED` (SHA-256 `fe438eab…`). It is a ranking reference, not training
data, and was frozen before the comparisons reported.

## 5. Filters applied

1. Canonical 20-residue alphabet only.
2. Length 8–50.
3. Uniqueness within the library.
4. Exact-match exclusion against `data/antibacterial.fasta`.
5. Similarity cap of 0.80 to that reference set for selection eligibility.

All five filters precede any score being read. No score-dependent filter is applied at any point.

The selection universe is **every** eligible member of the library — all 48,133 of them. An
earlier frozen policy additionally restricted selection to a score-blind hash-ordered 5,000-member
pool; that restriction was removed by a prospectively frozen full-opportunity experiment and is no
longer part of the pipeline. See `HEV1_FULL_OPPORTUNITY_PROTOCOL.md`.

## 6. Known-sequence inventory

Our inventory of known/published antimicrobial peptides is **partial**. We verified that no
selected peptide is an exact match to the supplied reference set, and that the maximum
`Levenshtein.ratio` from any top-100 member to that set is **0.764706**, against a limit of 0.80 —
a margin of **0.035294**. That is real headroom but it is not large.

An earlier version of this document reported 0.1497 here. That figure was wrong: the verifying
script unpacked the validator's `_read_fasta` as `(sequences, headers)` when it returns
`(headers, sequences)`, so the comparison ran against FASTA headers instead of peptide sequences.
The corrected figure is above, and it is the one measured by the unchanged official function.

We did **not** exhaustively check the top-100 against every public AMP database. Absence of exact
matches does not establish novelty of biological mechanism.

## 7. Compute

Generation: one RunPod RTX 4090 (Secure Cloud), terminated after evidence recovery. Scoring,
eligibility, selection and all analysis: local CPU. Total cloud spend for the entire final phase
was under two US dollars.
