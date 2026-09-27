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
| Upstream repository | **`github.com/jkwang93/AMP-Designer`**, branch `AMP-Designer` — **MIT** (repo `LICENSE`, and the GitHub API `license` field reports `mit`) |
| Source commit | `07d455dd6eb7ef61fe03b85732966caa32bf3dc4` |
| Weights | Zenodo DOI **10.5281/zenodo.17018363**, `prompt_model.zip`. The Zenodo record's title is `jkwang93/AMP-Designer: AMP-Designer`; it names the GitHub repo above as `isSupplementTo`, published 2025-03, resource type **software** |
| Archive SHA-256 | `71af768d1b7dd0f41db7c395179180dfc85fd28c46f5fa6ed143844c78ffbc5d` |
| Checkpoint SHA-256 | `47944ff42f7ea6a448340d44c2027329833205dd658ec4777e77777bdab1adc9`, 340,569,639 bytes |
| Licence | **CC-BY-4.0** on the Zenodo record; **MIT** on the GitHub repository. Two different licences on the two halves of the same release — we comply with both by attributing and by not modifying either |
| Paper | "Discovery of novel antimicrobial peptides with notable antibacterial potency by a LLM-based foundation model" (the Zenodo record's description) |

**A trap for anyone reproducing this.** The Zenodo record contains **two** different files named
`pytorch_model.bin`: one at the record's top level (340,538,601 bytes, checksum `ebc9576ea885…`) and
one **inside** `prompt_model.zip` (340,569,639 bytes, `47944ff4…`). They are not the same file. This
entry uses the one inside the archive, which is what `scripts/prepare_entry.py` extracts and
hash-checks. Taking the top-level file instead would fail our pin — correctly.

**Independently verified link to the upstream source.** Our vendored `vendor/amp_prompt/vocab.txt` is
**byte-identical** to the upstream repository's `voc/vocab.txt`
(`b887319d2f815b62…`). The upstream training scripts also default to `--n_tokens 10` and
`--max_seq_length 34`, matching the 10 soft tokens this entry uses and the 34-residue maximum length
present in our library. These are checks we ran, not claims we repeated.

### 2.1 What the authors publish, mapped to stage

The repository publishes a `data/` folder and four training scripts. **The mapping below is by file
name and by which script consumes what; it is not certified by the authors.** Both
`train_AMP_GPT.py` and `train_prompt_contrast.py` default `--train_raw_path` to
`train_raw_data.txt`, a file that **is not in the repository**, and the README gives no training
commands. So the exact input that produced the released checkpoint is **not pinned by the
repository and we have not reconstructed it.** We are not going to pretend otherwise.

| stage | script | data, by name and plausible use |
|---|---|---|
| language-model pretraining | `train_AMP_GPT.py` | `data/uniprot/uniport_seq.csv` — 630,683 unique short protein sequences |
| soft-prompt contrastive training | `train_prompt_contrast.py` | `data/prompt_data/amp_data.csv` (9,894) and `data/prompt_data/nonamp_data.csv` (2,298) |
| reference AMP corpora | (not consumed by a pinned path) | `APD3`, `CAMP`, `DBAASP`, `dbAMP`, `DRAMP` active-sequence CSVs |
| distillation / RL, **not used by this entry** | `train_distilation.py`, `Reinforce.py` | — |

This entry uses **only** the released soft-prompt checkpoint for inference. It runs no training,
no distillation and no reinforcement stage.

### 2.2 Overlap with the challenge's reference set — now measured, not conceded

The previous version of this document said we could not certify whether the generator's training data
is disjoint from `data/antibacterial.fasta`. That was honest but it was also a shrug. We have now
**measured** the published files. Exact-match counts, canonical-alphabet sequences only:

| published file | unique | ∩ `antibacterial.fasta` (39,448) | ∩ our 50,000 | ∩ our top-100 | SHA-256 |
|---|---:|---:|---:|---:|---|
| `data/prompt_data/amp_data.csv` | 9,894 | 8,864 (89.6%) | 0 | 0 | `45e1cbb4da41…` |
| `data/prompt_data/nonamp_data.csv` | 2,298 | 2,039 (88.7%) | 0 | 0 | `4eaa09f215dc…` |
| `data/APD3/APD_active_seq.csv` | 3,004 | 2,059 (68.5%) | 0 | 0 | `674e39853eaf…` |
| `data/CAMP/camp_active_sequence.csv` | 2,062 | 1,399 (67.8%) | 0 | 0 | `0a52fb585b25…` |
| `data/DBAASP/dbaasp_active_sequence.csv` | 9,730 | 8,930 (91.8%) | 0 | 0 | `36c70fbbd45d…` |
| `data/DBAMP/dbAMP_active_sequence.csv` | 11,641 | 9,553 (82.1%) | 0 | 0 | `2d560120269e…` |
| `data/DRAMP/DRAMP_active_sequence.csv` | 3,923 | 2,910 (74.2%) | 0 | 0 | `5acc3bde31f3…` |
| `data/uniprot/uniport_seq.csv` | 630,683 | 1,395 (0.2%) | 0 | 0 | `492d280fb0cd…` |

**The answer is that it is not disjoint, and here is by how much.** The union of the six peptide files
is **14,760** unique sequences, of which **11,873
(80.4%)** are in the challenge's reference set. That union covers
**30.1%** of the reference set. The generator's published training
material and the challenge's known-antibacterial reference substantially overlap. Anyone reading our
results should hold that fact alongside them.

**What does *not* overlap: our output.** Exact matches between our artifacts and every one of the eight
published files, including UniProt's 630,683 sequences:

- **library.fasta (50,000): 0**
- **top.fasta (100): 0**

And by the metric the official validator itself uses, the maximum
`Levenshtein.normalized_similarity` from any of our top-100 to that 14,760-sequence union is
**0.705882** (median 0.526316, none at or above 0.80). For comparison, our maximum against the
challenge's own reference set is 0.764706. **So our top-100 sits further from the generator's own
published training data than from the reference set the rule is actually written about.** That is a
measurement, not a novelty claim: proximity to *published* data says nothing about the unpublished
corpus that actually produced the checkpoint.

### 2.3 An unexpected finding about the reference set itself

While measuring the above, two things turned up that are worth recording because they are facts about
data this competition depends on, not about us:

1. **2,039 of the 2,298
   sequences in AMP-Designer's `nonamp_data.csv` — its *negative* class — are present in
   `data/antibacterial.fasta`**, where MarLys annotates them `activity=antimicrobial`. Four examples,
   with their MarLys records, are in the evidence file.
2. **172 sequences appear in both `amp_data.csv` and `nonamp_data.csv`** inside the same repository.

We do not know which reading is right. `nonamp_data.csv` may not mean "not antimicrobial" — in a
contrastive soft-prompt setup the second class can simply be the other prompt condition — or the two
curations genuinely disagree, or the published files are less clean than their names suggest. Point 2
shows the files are not internally disjoint whatever the intent.

**Nothing in our pipeline changes because of this.** We use `data/antibacterial.fasta` exactly as the
official validator does, byte for byte. What it does do is add independent weight to a caution already
in `LIMITATIONS.md`: labels in this field are noisy, and a reference set treated as ground truth by
one group is a negative class to another. Evidence:
`qualification_20260927/evidence/UPSTREAM_TRAINING_DATA_OVERLAP.json`.

## 3. Scoring predictors

| predictor | source | licence | role |
|---|---|---|---|
| APEX (8 ensemble members, 11 strain heads) | GitLab `machine-biology-group-public/apex-pathogen`, commit `417a4441a1e6ef8b10d2352e1c059622d5259f3a`, per-file SHA-256 pinned | MIT | predicted MIC per strain |
| ANIA (EC, PA, SA) | GitHub `SilverGojo4/ANIA`, commit `7bde436e0b5df8e44f9a598e312bd1944006cb3d`, per-file SHA-256 pinned | MIT | predicted log10 MIC |

Both are used as released. **Neither was retrained or recalibrated.**

### 3.1 What each publishes, checked at the pinned commit

We listed both repositories at the exact commits we pin, rather than describing them from memory.

**APEX** publishes, at `417a4441`: `APEX_models.py` (architecture), `utils.py`, `aaindex1.csv` (frozen
amino-acid embeddings, from genome.jp), `APEX_predict.py`, `test_seqs.fasta`, and the eight pretrained
models under `APEX_pathogen_models/` (named by hyperparameters, e.g. `APEX_3&128&2048&1e-06&0.001&2.0`).

**There is no training data and no training script in the pinned APEX repository.** Its README states
the 11-pathogen list and that the eight base learners' predictions are averaged. So APEX's training
corpus is **not disclosed by the artefact we use**, and we have not reconstructed it. That is a
limitation of the upstream release, and we pass it on rather than paper over it.

**ANIA** publishes its full data *pipeline* — `src/data/collect.py`, `clean.py`, `group.py`,
`split.py` — and its README names the sources explicitly: **DBAASP, dbAMP and DRAMP**, restricted to
monomers, with MIC unit conversion from µg/ml to µM, for three species (*E. coli*, *P. aeruginosa*,
*S. aureus*). The curated datasets and encoded features are offered as a download from
`biomics.lab.nycu.edu.tw/ANIA/#/download` — **outside** the repository. So ANIA's sources are
author-reported and its pipeline is inspectable, but the datasets are not pinned by the commit we pin.

### 3.2 Shared ancestry — now quantified rather than asserted

The previous version of this document said APEX and ANIA "are trained on overlapping public
antimicrobial-peptide measurement data". That was right but unquantified, and it understated the
problem, because the **challenge's own reference set draws on the same databases**. We parsed the
`dbs=` field of all 39,448 records in `data/antibacterial.fasta`:

| database | records in `antibacterial.fasta` | share |
|---|---:|---:|
| dbAMP | 20,933 | 53.1% |
| DRAMP | 18,395 | 46.6% |
| DBAASP | 14,496 | 36.7% |
| CAMP | 11,898 | 30.2% |
| SATPdb | 9,740 | 24.7% |
| APD | 2,041 | 5.2% |
| AMPDB | 1,270 | 3.2% |
| DADP, InverPep, CancerPPD, BaAMPs, CyBase, ParaPep | ≤ 601 each | ≤ 1.5% each |

Put beside §2.2 and §3.1, the picture is a **three-way shared ancestry, not two-way**:

- the **generator** publishes AMP corpora from APD3, CAMP, DBAASP, dbAMP and DRAMP;
- **ANIA** harvests DBAASP, dbAMP and DRAMP;
- the **challenge's reference set** aggregates dbAMP, DRAMP, DBAASP, CAMP, APD and others.

**These are the same databases.** Generator, one scorer and the evaluation reference all descend from
one pool of public AMP records. Agreement between APEX and ANIA is therefore weaker corroboration
than two models' agreement would normally be, and the novelty measured against
`antibacterial.fasta` is novelty against a set that is not independent of the generator's own
training material. APEX's contribution to this picture is unknown, because its training data is not
published at all.

We do not claim to have measured the *models'* training overlap — we cannot, since neither model's
actual training file is pinned. What is measured is the overlap of **published data**, in §2.2, and the
common database ancestry, here.

### 3.3 A second observation about the reference set

`data/antibacterial.fasta` is annotated `activity=antimicrobial` for **100%** of its 39,448 records,
while only **7,827 (19.8%)** additionally carry an explicit `antibacterial` sub-annotation (and 14.9%
`anti-gram-`, 4.5% `anti-gram+`). The file's name is `antibacterial.fasta` and the official validator
treats it as *the* reference set; by its own MarLys annotations it is better described as an
**antimicrobial** set of which about a fifth carries a specific antibacterial label.

That is an observation, not a complaint, and it is **not** a licence to treat the rule differently: we
use the file byte-for-byte as the validator does. It matters for two reasons. It partly explains the
label conflict in §2.3 — a broad set will contain another curation's negatives. And it means "novel
relative to known antibacterials" is, in practice, "novel relative to a broad antimicrobial set",
which is a **stricter** bar than the name implies, so our 0.035294 margin is if anything conservative.
Evidence: `qualification_20260927/evidence/REFERENCE_SET_PROVENANCE.json`.

### 3.4 Reliability, unchanged and still the dominant limitation

Recorded diagnostics found measured-threshold transfer failures: predicted MIC thresholds did not
transfer cleanly to held-out measured data, and both predictors sit at R² ≤ 0 on held-out measured
log10 MIC. We do not claim either predictor is calibrated for the organizers' strain panel. See
`PREDICTOR_RELIABILITY_MEASURED.md`.

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
