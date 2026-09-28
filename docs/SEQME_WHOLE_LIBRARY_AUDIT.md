# Whole-library seqme qualification audit — result

**The entry does not change. But this audit found the most consequential unexamined thing left in the
project, and it is not flattering.**

Every prior comparison in this project scored the **top-100** with APEX and ANIA. Phase 1 of the
competition does not do that. It screens the **full 50,000-member library** with **seqme**. No seqme
receipt existed anywhere in this project before today — searched and confirmed absent. This is that
audit.

Protocol frozen before any value was computed: `SEQME_WHOLE_LIBRARY_PREREG.md` and
`SEQME_PREREG_ADDENDUM_1.md`. Datasets and hashes: `SEQME_DATASETS.json`. Raw results:
`SEQME_PASS_A.json`, `SEQME_PASS_B.json`, `SEQME_PASS_B1337.json`, `ADDENDUM1_MMSEQS_SYNTH.json`.
**The negative-control verdict for every metric, which is what corrected §1–3, is
`NEGATIVE_CONTROL_ALL_METRICS.json`.**

**Cost: $0.00. All local CPU.** seqme 0.5.1 at commit `6b8f3221`, ESM-2 `t6_8M`, MMseqs2 `18-8cc5c`.
Embedding 50,000 peptides takes 1.2 minutes on this laptop; a full 50,000-against-103,143 MMseqs2
search takes 6 seconds. Nothing here needed a GPU and nothing here was sampled for cost.

---

## 1. The headline, and a correction I had to make to my own first draft

**Four metrics put us behind the AMP-Diffusion baseline, beyond our own seed-to-seed spread, and all
four replicated on an independent sample:**

| metric | ours | AMP-Diffusion | direction | our seed range |
|---|---:|---:|---|---:|
| FBD vs known antibacterials | **2.0502** | 1.2302 | lower better | 0.0313 |
| FBD vs training set | **2.4197** | 1.2809 | lower better | 0.0293 |
| MMD vs known antibacterials | **12.2646** | 6.7267 | lower better | 0.2482 |
| Authenticity (AuthPct) | **0.8698** | 0.9070 | higher better | 0.0032 |

> **CORRECTION, made before this document was finalised and kept here on purpose.** My first draft
> grouped all four of these together and dismissed them with one argument: that a character-shuffled
> control beats both libraries on "every metric in that family". Then I computed the control's rank on
> **every** metric instead of the four I had looked at, and the claim was wrong in two directions at
> once. **AuthPct's control behaves correctly** — the shuffle is *worst* on it — so that adverse result
> is **not** explained away. And the same control also beats us on six metrics where I had claimed a
> **lead**. The corrected, symmetric reading is §2. The draft's version was convenient in both places;
> this one is not.

## 2. What the negative control actually says, applied symmetrically

The control is `antibacterial.fasta` with each sequence's letters shuffled: length and amino-acid
composition preserved **exactly**, every motif destroyed. If a metric is measuring AMP-likeness, the
shuffle should score badly. Here is where it actually ranks, on all fourteen metrics:

| metric | shuffle | ours | AMP-Diffusion | control verdict |
|---|---:|---:|---:|---|
| **FKEA** (higher better) | 736.8 | **1161.8** | 1062.9 | **behaves — shuffle worst** |
| **Authenticity** (higher better) | 0.7475 | 0.8698 | **0.9070** | **behaves — shuffle worst** |
| FBD antibacterial (lower better) | **0.7248** | 2.0502 | 1.2302 | fails — shuffle beats both |
| MMD antibacterial (lower better) | **2.1465** | 12.2646 | 6.7267 | fails — shuffle beats both |
| Precision (higher better) | **0.8599** | 0.7038 | 0.5297 | fails — shuffle beats both |
| Recall (higher better) | **0.8151** | 0.3891 | 0.3481 | fails — shuffle beats both |
| Clipped density (higher better) | **0.8148** | 0.1901 | 0.0815 | fails — shuffle beats both |
| Clipped coverage (higher better) | **0.6424** | 0.1641 | 0.1222 | fails — shuffle beats both |
| FBD training (lower better) | 1.3533 | 2.4197 | **1.2809** | partial — beats ours, not the baseline |
| Conformity (higher better) | **0.5134** | 0.4351 | 0.4153 | expected by construction — a shuffle preserves net charge exactly |
| Diversity k=5 / k=25 (higher better) | **0.8566 / 0.8569** | 0.7808 / 0.7809 | 0.7781 / 0.7783 | expected by construction — shuffling genuinely raises edit-distance diversity |
| Length (closer better) | 18.7171 | 17.2731 | 25.3204 | expected by construction — a shuffle preserves length exactly |
| 3-gram Jaccard (lower better) | 0.0020 | **0.0018** | 0.0028 | partial — we beat the shuffle, the baseline does not |

**Two metrics in the entire suite have a negative control that behaves, and they split.** We lead on
**FKEA** (effective support in embedding space) and we trail on **AuthPct**. That is the honest
discriminating result: one for, one against.

**Six metrics rank a motif-destroyed shuffle above both real libraries.** Mean-pooled ESM-2 embeddings
of short peptides are largely a composition-and-length statistic, and the shuffle matches the reference
on both by construction. So **neither** our FBD/MMD deficit **nor** our precision, recall, density and
coverage lead should be read as a statement about quality. That cuts against us on two metrics and in
our favour on four, and it has to be applied to both.

**Three more are shuffle-favouring by construction** rather than by malfunction — conformity (net
charge is preserved exactly), Levenshtein diversity (shuffling really does increase it) and length
(preserved exactly). Comparisons *between the two real libraries* on those remain meaningful; the
shuffle's rank on them is not evidence of anything.

**What survives as a genuine relative weakness, then, is AuthPct: −0.0373, against a seed spread of
0.0032, replicated.** It is small in absolute terms, and it sits beside zero exact matches against any
published training file and a maximum similarity of 0.7059 to the generator's published corpora — so
it is not memorisation in any coarse sense. But it is the one adverse number this audit cannot explain
away, and it is recorded as such rather than buried.

**And the FBD/MMD numbers still matter operationally even though they are not quality evidence.** If
the organizers compute them in a comparable configuration, we score worse than the library they
published as a target to beat. The metric being uninformative does not stop it from being scored.

**Mechanism, measured.** Our library is composition-shifted relative to the reference: GRAVY **+0.135**
versus **−0.289**, amphiphilicity **0.525** versus **0.395**, net charge **6.18** versus **3.85**.
AMP-Diffusion sits between us and the reference on GRAVY (−0.043) and amphiphilicity (0.480). FBD is
dominated by the squared distance between distribution means, so a composition offset produces a large
FBD. This is not a new weakness — it is a new, independent measurement of the **"one chemotype"
concentration already disclosed in `LIMITATIONS.md`**: five residues are 78.4% of the top-100, D and M
absent, median net charge +10.

## 3. Where the entry leads, with the §2 discount applied

| metric | ours | AMP-Diffusion | how much weight it carries |
|---|---:|---:|---|
| **FKEA** effective support | **1161.8** | 1062.9 | **full** — its negative control behaves |
| **fraction ≥80% identical to a known AMP** (§6) | **1.47%** | 3.82% | **full** — MMseqs2 alignment, anchored by the reference set scoring 84.9% |
| **clustering coverage** at 50% identity (§6) | **48,833** | 43,470 | **full** — alignment-based, and the shuffle is not a confound |
| **synthesizability pass rate** (§6) | **78.18%** | 38.43% | **full** on the rule, but the rule is ours (§6 caveat) |
| Precision / Recall / Clipped density / Clipped coverage | 0.7038 / 0.3891 / 0.1901 / 0.1641 | 0.5297 / 0.3481 / 0.0815 / 0.1222 | **discounted** — the shuffle beats us here too |
| Conformity of charge & amphiphilicity | 0.4351 | 0.4153 | **discounted** — shuffle-favouring by construction |
| Internal diversity k=5 / k=25 | 0.7808 / 0.7809 | 0.7781 / 0.7783 | **discounted**, and the margin is tiny |
| Mean length (reference 18.72) | 17.27 | 25.32 | meaningful between real libraries |
| 3-gram Jaccard to reference | 0.0018 | 0.0028 | modest — we beat the shuffle, the baseline does not |

**The leads that survive the discount are the alignment-based and rule-based ones**, which is
convenient to notice but is also where the instruments are transparent: an 80%-identity MMseqs2 hit and
an MMseqs2 cluster mean something checkable, and their anchors behave (the reference set, being a MarLys
subset, scores 84.9% on the identity metric exactly as it must).

Also exact and parameter-free, needing no discount at all: **Uniqueness 1.0000**, and **exact-match
novelty 1.0000 against both the challenge reference set and the training set** — zero of our 50,000
sequences is a rediscovered known peptide. The proposal screens for precisely this.

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
| **1. Surrogate activity prediction** (AMPredictor, MBC-Attention, DeepAMP) | **STILL NOT COVERED — now with a reason rather than a gap.** Declared as the largest gap in the addendum before any result was seen. On 2026-09-28 **Deep-AMP** was obtained at the exact commit BATTLE-AMP pins, licence-checked (MIT), and run on all four variants on local CPU for $0. It **failed its pre-registered reliability gate on its own paper's measured MICs**: no variant achieves positive rank concordance, and all 15 scored peptides are predicted at 3,789–43,027 µM against 0.4–100 µM measured. Its verdict on our library is overwhelmingly favourable and is **declined as uninterpretable**. AMPredictor and MBC-Attention were not run. `DEEPAMP_DIAGNOSTIC_RESULT.md` |
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
scores" — the proposal does not define it — runs **against** us: 1.193 for our library, 1.082 for
AMP-Diffusion, where lower means more novel. But the permuted control sits at **1.176**, essentially our
value, and AMP-Diffusion comes out *more novel than the nonsense control*. **On that normalisation the
negative control fails too**, largely because bits-per-residue is diluted by AMP-Diffusion's much longer
sequences (25.3 versus 17.3 residues). We report the number and decline to argue from it — in either
direction. The ≥80%-identity fraction in the table above is the reading that does have working anchors,
and it favours us 2.6×. Second, our synthesizability rule is a conjunction of seven constraints frozen in
this project, not the organizers' unpublished ones — and note that it fails **38% of real known AMPs**,
so it measures conformity to those seven rules, not synthesizability truth.

## 7. Decision

**Nothing about the entry changes.** The pre-registered rule permits *proposing* one new deterministic
library-construction policy when a substantial reproducible weakness is found. Weaknesses were found
and no policy is proposed. The reasons, in the order they actually bind:

1. **There is nothing coherent to optimise toward.** The FBD/MMD deficit is a composition offset, and a
   motif-destroyed shuffle scores best on those metrics. Selecting the library to move its mean
   composition toward the reference is optimising toward what the shuffle achieves — and it would trade
   directly against the ≥80%-identity novelty margin where we lead 2.6× on an instrument whose anchors
   *do* behave.
2. **The one adverse metric that survives the negative control is AuthPct, at −0.0373**, and no
   deterministic selection policy plausibly moves it without moving the library away from the reference
   manifold — which is the opposite of what the FBD result would ask for. The two adverse signals point
   in incompatible directions, which is itself a reason not to chase either.
3. **It would be post-hoc selection on the metrics that flagged it**, with the organizers' aggregation
   weights withheld precisely to prevent that.
4. **The cost cannot be justified.** Four days to the deadline; a new library invalidates the
   byte-identical replication, the two-architecture reproduction, the decision-stability certificate and
   the clean-room validator receipt, all of which bind seed 42's exact 50,000 sequences. The
   pre-registration requires the benefit to justify new validation. It does not.
5. **One metric family does not settle a library**, in either direction. The rule that stops us
   promoting on a single favourable metric stops us rebuilding on a single unfavourable family.

**What this audit delivers is calibrated expectation, and it is less flattering than the top-100
evidence.** Phase 1 advances at most 20 teams. What we now know rather than assume:

- **Split on the two metrics whose negative control behaves**: ahead on FKEA, behind on AuthPct.
- **Ahead on the transparent, alignment-based measures**: 1.47% versus 3.82% of the library within 80%
  identity of a known AMP, 48,833 versus 43,470 clusters, 78.18% versus 38.43% on our synthesizability
  rule, and zero exact rediscoveries out of 50,000.
- **Behind on FBD and MMD**, which the proposal names and which will be scored whether or not they are
  informative. The mechanism is our chemotype concentration, already disclosed.
- **Six metrics — four of them ones we lead on — cannot support quality claims at all**, because a
  shuffled control beats both libraries on them.
- **Still unmeasured on surrogate activity prediction**, the first of the organizers' four families and
  the one closest to what the competition is actually about — but no longer unattempted. **Deep-AMP was
  obtained and run on 2026-09-28 and failed its reliability gate on its own paper's measured MICs**,
  predicting 3,789–43,027 µM where 0.4–100 µM was measured; its strongly favourable verdict on our
  library is declined as uninterpretable. AMPredictor and MBC-Attention remain un-run. Our APEX/ANIA
  work is neither those models nor the same object. `DEEPAMP_DIAGNOSTIC_RESULT.md`.

**The most useful thing this audit produced is not a number but a discount rate**: most of the
embedding-space evidence in this project's Phase-1 picture, favourable and unfavourable alike, is
composition-driven and should not be argued from. That conclusion cost nothing and would not have been
visible without running the negative control on every metric rather than on the four that looked bad.
