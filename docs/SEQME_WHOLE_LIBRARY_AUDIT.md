# Whole-library seqme qualification audit — result

**The entry does not change. But this audit found the most consequential unexamined thing left in the
project, and it is not flattering.**

Every prior comparison in this project scored the **top-100** with APEX and ANIA. Phase 1 of the
competition does not do that. It screens the **full 50,000-member library** with **seqme**. No seqme
receipt existed anywhere in this project before today — searched and confirmed absent. This is that
audit.

Protocol frozen before any value was computed: `prereg/SEQME_WHOLE_LIBRARY_PREREG.md` and
`prereg/SEQME_PREREG_ADDENDUM_1.md`. Datasets and hashes: `SEQME_DATASETS.json`. Raw results:
`evidence/SEQME_PASS_A.json`, `evidence/SEQME_PASS_B.json`, `evidence/SEQME_PASS_B1337.json`,
`evidence/ADDENDUM1_MMSEQS_SYNTH.json`.

**Cost: $0.00. All local CPU.** seqme 0.5.1 at commit `6b8f3221`, ESM-2 `t6_8M`, MMseqs2 `18-8cc5c`.
Embedding 50,000 peptides takes 1.2 minutes on this laptop; a full 50,000-against-103,143 MMseqs2
search takes 6 seconds. Nothing here needed a GPU and nothing here was sampled for cost.

---

## 1. The headline, stated against us first

**On the embedding-distribution family the organizers explicitly name, we are behind the
AMP-Diffusion baseline, by margins far larger than our own seed-to-seed spread.**

| metric | ours | AMP-Diffusion | direction | our seed range |
|---|---:|---:|---|---:|
| FBD vs known antibacterials | **2.0502** | 1.2302 | lower better | 0.0313 |
| FBD vs training set | **2.4197** | 1.2809 | lower better | 0.0293 |
| MMD vs known antibacterials | **12.2646** | 6.7267 | lower better | 0.2482 |
| Authenticity (AuthPct) | **0.8698** | 0.9070 | higher better | 0.0032 |

The proposal names Fréchet Biological Distance and Maximum Mean Discrepancy by name, and it publishes
AMP-Diffusion's library as "a published Phase 1 target for participants to beat". On these four
numbers we do not beat it. All four cleared the pre-registered noise bar and **all four replicated on
the independent seed-1337 sample** (§4). This is a real relative weakness and it is the first thing
anyone should be told.

## 2. And now the part that changes how to read it

**Every metric in that family ranks a character-shuffled version of the reference set at or above both
real generated libraries.** The permuted control — `antibacterial.fasta` with each sequence's letters
shuffled, which preserves length and amino-acid composition exactly while destroying every biological
motif — scores:

| metric | permuted nonsense | ours | AMP-Diffusion | real reference |
|---|---:|---:|---:|---:|
| FBD (antibacterial), lower better | **0.7248** | 2.0502 | 1.2302 | 0.0000 |
| MMD (antibacterial), lower better | **2.1465** | 12.2646 | 6.7267 | 0.0000 |
| Precision (antibacterial), higher better | **0.8599** | 0.7038 | 0.5297 | 1.0000 |
| Recall, higher better | **0.8151** | 0.3891 | 0.3481 | 1.0000 |
| Clipped density, higher better | **0.8148** | 0.1901 | 0.0815 | 1.0000 |

**A shuffled control beats both real libraries on all five.** It does so because mean-pooled ESM-2
embeddings of short peptides are dominated by amino-acid composition and length, and shuffling
preserves both perfectly. So these metrics, in the only configuration we can reproduce from public
code, **do not discriminate AMP-likeness from composition-matching.**

**Exactly one metric in the whole suite puts the shuffled control last: FKEA** (737 for permuted,
against 1003 for the real reference, 1063 for AMP-Diffusion and **1162** for us).

Two conclusions, and they are different:

- **The adverse number stands as a number.** If the organizers compute FBD and MMD in a comparable
  configuration, we score worse than the published baseline, whatever drives it. That is a risk to
  advancing past Phase 1 and we are not going to dress it up.
- **The adverse number does not license the inference "our library is less AMP-like".** The same
  instrument prefers nonsense. Reading a quality conclusion out of a metric that fails its own
  negative control is the error this project has spent weeks learning not to make.

**Mechanism, measured.** Our library is composition-shifted relative to the reference: GRAVY **+0.135**
versus the reference's **−0.289**, amphiphilicity **0.525** versus **0.395**, net charge **6.18** versus
**3.85**. AMP-Diffusion sits between us and the reference on GRAVY (−0.043) and amphiphilicity
(0.480). FBD is dominated by the squared distance between distribution means, so a systematic
composition offset produces a large FBD while leaving *local* membership high — which is precisely
what we observe (§3). This is not a new weakness. It is a **new, independent measurement of the
"one chemotype" concentration already disclosed in `LIMITATIONS.md`**: five residues are 78.4% of the
top-100, D and M are absent, median net charge is +10.

## 3. Where the entry leads, on the same reference set with the same embedder

Nine metrics, all beyond the seed-noise bar:

| metric | ours | AMP-Diffusion | direction |
|---|---:|---:|---|
| **Precision** (fraction on the reference manifold) | **0.7038** | 0.5297 | higher better |
| **Recall** | **0.3891** | 0.3481 | higher better |
| **Clipped density** | **0.1901** | 0.0815 | higher better |
| **Clipped coverage** | **0.1641** | 0.1222 | higher better |
| **FKEA** (effective support, the one metric that fails the shuffle) | **1161.8** | 1062.9 | higher better |
| Conformity of charge & amphiphilicity | **0.4351** | 0.4153 | higher better |
| Internal diversity, k=5 / k=25 | **0.7808 / 0.7809** | 0.7781 / 0.7783 | higher better |
| 3-gram Jaccard to reference | **0.0018** | 0.0028 | lower better |
| Mean length (reference is 18.72) | **17.27** | 25.32 | closer better |

**The tension between §1 and §3 is the finding, not a contradiction.** FBD and MMD are *moment*
statistics on the whole cloud; precision, recall, density and coverage are *membership* statistics on
nearest-neighbour balls. Our library puts **more** of its individual sequences inside the reference
manifold (0.704 vs 0.530) while its cloud as a whole is **more displaced**. That is the signature of a
distribution that is systematically offset in composition but locally well-placed and at least as
broad — consistent with FKEA, Levenshtein diversity and clustering all favouring us.

Also exact and parameter-free: **Uniqueness 1.0000** and **exact-match novelty 1.0000 against both the
challenge reference set and the training set** — zero of our 50,000 sequences is a rediscovered known
peptide. The proposal screens for exactly this.

## 4. The pre-registered replication check

§6 of the pre-registration requires three things before a number may license changing anything:
direction, magnitude beyond the measured seed spread, and **replication on an independent sample**.
Four metrics reached the third test and it was run on `seed=1337`:

| metric | Pass B gap (seed 42) | seed-1337 gap | seed range (1337) | replicates? |
|---|---:|---:|---:|---|
| FBD (antibacterial) | +0.8200 | +0.7948 | 0.0545 | **YES** |
| FBD (training) | +1.1388 | +1.1118 | 0.0533 | **YES** |
| MMD (antibacterial) | +5.5379 | +5.5057 | 0.5280 | **YES** |
| Authenticity | -0.0373 | -0.0350 | 0.0045 | **YES** |

**All four replicate.** The adverse direction, the magnitude beyond seed noise, and the independence check are all satisfied, on a sample drawn by the same score-blind rule with a different seed. This is not a sampling artifact.

That means the pre-registration's three conditions are met, and §7 explains why a library change is still not proposed. A rule that only ever concludes what is convenient is not a rule, so the conditions being met is recorded plainly here even though the outcome is no change.

## 5. The organizers' own four metric families, and what we can and cannot say

The pinned proposal (§1.5) enumerates the Phase-1 families. The starter kit's `metrics/README.md`,
which promised the baselines' Phase-1 numbers at launch, is still a **placeholder** — so there is no
published protocol and no published target to compare against. Coverage:

| family | status |
|---|---|
| **1. Surrogate activity prediction** (AMPredictor, MBC-Attention, DeepAMP) | **NOT COVERED — the largest gap in this audit.** Declared as such in the addendum before any result was seen. Our APEX/ANIA evidence is not a substitute: different models, and computed on the top-100 rather than the library |
| **2. Sequence-level** (uniqueness, diversity, alignment-based novelty, clustering coverage) | **COVERED.** Uniqueness 1.0, exact novelty 1.0, diversity and clustering both favour us, ≥80%-identity fraction favours us 2.6× (§6) |
| **3. Embedding distributional similarity** (FBD, MMD, precision/recall, ESM-2 **and ESM-C**, **two** reference sets) | **PARTIAL.** One embedder, one reference set. We have no generic peptide background set and no ESM-C, and we did not substitute anything for them |
| **4. Property distribution** (conformity, synthesizability rate) | **COVERED**, with the caveat in §6 that the synthesizability rule is ours, not theirs |

**We did not compute an aggregate score, and we will not.** The proposal states the aggregation
weights, tie-breaking and reference-set composition are withheld until Phase 1 closes, specifically to
prevent optimizing against them. No leaderboard position is estimated. The tutorial we followed is the
seqme authors' public worked example, **not** the organizers' scoring configuration.

## 6. Addendum metrics: the organizers' families 2 and 4, completed

MMseqs2 `18-8cc5c` against MarLys-AMP v3 (103,143 sequences, CC0), plus the synthesizability rate.
Full library, no sampling.

| | ours | AMP-Diffusion | our seed range | real reference | permuted |
|---|---:|---:|---:|---:|---:|
| **fraction ≥80% identity to a known AMP** (MMseqs2 default `-c 0.8`), lower better | **1.47%** | 3.82% | 0.02% | 84.94% | 0.75% |
| same, coverage-weighted identity | **0.41%** | 1.65% | — | 84.71% | 0.30% |
| **clusters at 50% identity** (of 50,000), higher better | **48,833** | 43,470 | 70 | — | — |
| largest cluster's share, lower better | **0.02%** | 1.04% | 0.02% | — | — |
| singleton share, higher better | **95.94%** | 83.02% | 0.20% | — | — |
| **synthesizability pass rate**, higher better | **78.18%** | 38.43% | 0.25% | 61.86% | 56.99% |

**On the decision-relevant novelty reading — how many library members are ≥80% identical to a known
AMP — we are 2.6× better than the baseline** (1.47% vs 3.82%, and 4× better coverage-weighted). The
anchors confirm the metric works: the reference set, which *is* a MarLys subset, sits at 84.9%.

**Clustering coverage and synthesizability both favour us by very large margins** relative to a seed
spread of 0.02–0.25 percentage points.

**Two honest caveats.** First, the `bits_per_residue` normalisation we defined for "normalized bit
scores" — the proposal does not define it — puts us at 1.193 and AMP-Diffusion at 1.082, i.e. against
us. But the permuted control scores 1.176, essentially our value, and AMP-Diffusion scores *below* the
nonsense control. **That normalisation fails its negative control too**, largely because bits-per-residue
is diluted by AMP-Diffusion's much longer sequences (25.3 vs 17.3 residues). We report it and decline
to argue from it. Second, our synthesizability rule is a conjunction of seven constraints frozen in
this project, not the organizers' unpublished ones — and note that it fails **38% of real known AMPs**,
so it measures conformity to those seven rules, not synthesizability truth.

## 7. Decision

**Nothing about the entry changes.** The pre-registered rule permits *proposing* one new deterministic
library-construction policy when a substantial reproducible weakness is found. One was found, and a
policy is still not proposed. The reasons are stated before, not after, the convenience of the answer:

1. **Any FBD/MMD-reducing policy is composition-matching.** The measured mechanism is a composition
   offset, and the measured fact is that a shuffle of the reference set scores best. Selecting our
   library to move its mean composition toward the reference is optimizing toward what nonsense
   achieves, and it would trade directly against the ≥80%-identity novelty margin where we currently
   lead 2.6×.
2. **It would be post-hoc selection on the metric that flagged it**, with the aggregation weights
   withheld precisely to prevent that.
3. **The cost cannot be justified.** Four days to the deadline; a new library invalidates the
   byte-identical replication, the two-architecture reproduction, the decision-stability certificate
   and the clean-room validator receipt, all of which bind seed 42's exact 50,000 sequences. The
   pre-registration requires the benefit to justify new validation. It does not.
4. **One metric family does not settle a library.** The same rule that stops us promoting on a single
   favourable metric stops us rebuilding on a single unfavourable family.

**What this audit delivers instead is calibrated expectation.** Phase 1 advances at most 20 teams. We
now know, rather than assume, where the library stands on the screening the organizers described: ahead
of the published baseline on sequence-level novelty, clustering coverage, internal diversity,
manifold membership, property conformity and synthesizability; **behind it on the two moment-matching
embedding distances, with the mechanism identified and the instrument shown to fail its own negative
control**; and entirely unmeasured on surrogate activity prediction, which is the family we cannot
reproduce and the one closest to what the competition is actually about.
