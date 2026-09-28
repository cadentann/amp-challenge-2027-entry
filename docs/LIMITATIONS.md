# Limitations

Written to be read by a sceptic. Nothing here is hedged for presentation.

## 1. Everything is predicted. Nothing is measured.

No peptide in this entry has been synthesised or assayed. Every number is the output of APEX and
ANIA, two machine-learning predictors. We make **no** claim of biological superiority, and no
claim about competition performance.

## 2. The entry no longer trails badly on potency, but still trails slightly

An earlier version of this entry selected from only 5,000 of its 50,000 candidates and trailed an
unmodified potency-ranked AMP-Diffusion portfolio on APEX Gram-negative breadth by 0.1129. A
prospectively frozen full-opportunity experiment closed most of that gap:

| metric | this entry | original potency | delta |
|---|---:|---:|---:|
| GN breadth@16 | 0.4843 | 0.4914 | **−0.0071** |
| top-50 GN@16 | 0.5286 | 0.5371 | −0.0086 |
| all-11@16 | 0.3991 | 0.4009 | −0.0018 |
| GP breadth@16 | **0.2500** | 0.2425 | +0.0075 |
| MDR breadth@16 | **0.4575** | 0.4475 | +0.0100 |
| APEX mean MIC µM | 73.46 | **57.06** | 16.40 worse |
| ANIA EC/PA log10 MIC | **−0.4624** | +0.6930 | far better |

**The residual deficit is APEX mean MIC (73.46 vs 57.06 µM), and it is real.** The breadth gaps
are now marginal (≤0.009), and this entry leads on Gram-positive breadth, MDR breadth and both
ANIA measures.

**Those marginal breadth gaps sit inside the seed-to-seed variation we have observed.** Three fresh
seeds run at full production scale give GN breadth@16 of 0.5171, 0.4714 and 0.5129 against seed 42's
0.4843 — an observed range of **0.4714 to 0.5171** across four seeds. The −0.0071 gap to the potency
comparator, and our +0.0075 and +0.0100 leads on Gram-positive and MDR breadth, are all far smaller
than that range and should not be argued from.

**Four seeds do not establish a noise floor**, and an earlier draft of this section wrongly described
one. We have no basis for a standard error or a confidence interval on seed variation; a fifth seed
could fall outside the observed range. What the evidence supports is the weaker and still useful
statement above: gaps of this size are not distinguishable from which seed happened to be used.
What survives measurement is the much larger structure: the ~+0.12 gain from full-library selection,
and the 26-standard-deviation gap to random selection.

Note also that **seed 42 is slightly below the fresh-seed average** (0.4843 against 0.5005), so the
shipped numbers are, if anything, a mildly conservative draw rather than a flattering one. Two of the
three fresh seeds scored higher and we declined to switch to them; see
`LANE1_HOLDOUT_SUPPORTS.md`.

Two measured considerations bear on how much weight the residual gap deserves — neither erases it:

- **Homology.** The potency portfolio sits closer to known antibacterials (mean max-similarity
  0.713 vs this entry's **0.6668**; **98% vs 96%** have a ≥0.60 neighbour) and its predicted
  activity correlates more strongly with that proximity (GN@16 vs similarity Spearman +0.180 vs
  this entry's **+0.058**; APEX mean MIC −0.101 vs **+0.011**). See `HEV3_HOMOLOGY_FINDING.md`.

  These are the shipped entry's own measured values. An earlier version of this section quoted the
  **superseded** E=5000 entry's figures (0.671, 90%, +0.083) as if they were this entry's, which
  overstated the gap on the ≥0.60-neighbour fraction by roughly fourfold. The direction of the
  conclusion is unchanged — this entry has the weakest leakage signature of the four — but the
  proximity gap itself is small, and the argument should not lean on it heavily.
- **Predictor reliability — now measured on our own predictors, and worse than the citation.**
  Against 906 peptides with measured MIC held out of ANIA's training set, **both** predictors have
  R² at or below zero on log10 MIC: APEX −0.9 to −2.6, ANIA ≈ 0. AMPBench-MT's "R² < 0.30" was
  optimistic. **Absolute predicted MIC values therefore carry essentially no absolute meaning**, and
  the 16.4 µM mean-MIC gap above should not be weighed as heavily as earlier drafts of this document
  weighed it. What survives is rank signal (Spearman ≈ 0.45 for both) and threshold classification.
  See `PREDICTOR_RELIABILITY_MEASURED.md`.

- **Diversity.** That portfolio carries 333 internal sequence pairs at ratio ≥0.60 versus this
  entry's 113 — a threefold difference that matters because the organizers sample 25 peptides at
  random from the advancing list. Stated fairly, though, pair counts flatter us: by single-linkage
  clustering at 0.60, **51 of our 100 peptides fall in one component** (the potency portfolio's
  largest is 93, V3's is 1). We are much better than the potency list and much worse than V3.

**Our top-100 is one chemotype, and narrower than the library it came from.** Five residues account
for **78.4%** of it — K 28.2%, L 19.9%, R 14.3%, W 8.1%, I 7.9% — against 65.6% for the top five in
the 50,000-member library. **D and M do not appear at all**, and D+E together contribute 2 residues
out of 2,342. These are cationic amphipathic peptides with essentially no acidic content. That is
the dominant class in this field and in both comparator portfolios, so it is not a discriminator,
but it does mean a single class-level failure mode — salt sensitivity, serum inactivation,
mammalian membrane affinity — would affect most of the portfolio at once, and the selector
concentrated composition rather than spreading it.

Two further measurements on the same axis, both adverse to us and both recorded for that reason: our
median net charge is **+10**, the highest of the four portfolios (potency +6, V3 +8, superseded +9),
and we carry slightly *more* long hydrophobic runs than any comparator — 10 peptides with a
hydrophobic run of 5 or more and 2 with 7 or more, against 6/6/7 and 1/0/0. High cationicity and long
hydrophobic stretches drive antimicrobial activity and membrane disruption together, so this is the
axis on which haemolysis risk would express itself, and it is the axis we cannot measure — see
`LANE3_SAFETY_SCREEN_IS_UNINFORMATIVE.md`. Against that, the selector flags **0 of 100** on a
solubility-risk proxy where the library's base rate is 6.7%, and contains no peptide with net charge
at or below +2 where the library has 15%. Full profile in `LANE8_DEVELOPABILITY.md`.

## 3. The identity of these specific 100 peptides is not precisely determined

Under Gaussian perturbation of predictor ranks by **1 percentile point**, about half the shipped
top-100 would be replaced; at **5 points**, about seven eighths of it. Given AMPBench-MT's R² < 0.30
under homology control, errors of that size are not a pessimistic assumption.

This is a property of the predictors, not of our selector, and measuring it against the alternatives
matters: at 0.2 percentile points of noise `CONSENSUS_FIXED` retains 88 of its own 100 where
APEX-only ranking retains **7**, and at every noise level tested the frozen selector is the most
stable of the three by a wide margin. The portfolio's aggregate properties are also far more stable
than its membership — the perturbation that replaces half the members moves GN breadth@16 by 0.0022,
from 0.4843 to 0.4821.

A related finding, reported because it is adverse on its face: ranking on **APEX alone** would give
GN breadth@16 of 0.6300 against our 0.4843. That comparison is circular — GN breadth is computed
from APEX, so ranking by APEX optimises it by construction — and the advantage does not survive
contact with predictor error, falling to 0.5236 at one percentile point and to 0.3943 at five, below
the consensus selector's 0.3950. Full analysis in `LANE5_PREDICTOR_DEPENDENCE.md`.

## 4. The two predictors fail differently — not independently — and one has a dead head

Measured against 906 held-out peptides with real MIC values, the two predictors behave very
differently, and the difference matters:

| | Spearman | R² (log10) | recall @16 µM | precision @16 µM | precision lift |
|---|---:|---:|---:|---:|---:|
| **APEX** | 0.17–0.46 | −0.9 to −2.6 | 0.00–0.35 | **0.89–1.00** | **1.7–2.5×** |
| **ANIA** | 0.44–0.48 | ≈ 0 | **0.72–0.85** | 0.46–0.63 | 1.2–1.3× |

APEX is a high-precision, near-zero-recall filter; ANIA is a calibrated, high-recall predictor. The
frozen selector requires both, which is why it combines the two properties. This was not designed
from these numbers — the selector was frozen long before they were measured.

Two honest consequences. First, this **inverts** the assumption that APEX is the stronger signal and
ANIA the weaker corroborator: against measured MIC, ANIA is the better-calibrated of the two, and
APEX's apparent dominance on our GN-breadth metric is circular, because that metric is computed from
APEX. Second, **APEX on *E. faecalis* has Spearman −0.055** — no rank signal at all on held-out data.
E. faecalis is one of four heads in our MDR breadth figure, so MDR@16 = 0.4575 rests partly on a head
that does not measurably work. Re-derived without it, our MDR lead over the potency portfolio
survives and slightly grows (+0.0133 versus +0.0100), so it is not an artifact of the dead head — but
restricted to EC4, the only MDR head with decent measured rank signal (Spearman 0.455), the two
portfolios **tie exactly** at 0.8300. Our MDR lead is real as computed and should not be leaned on.

APEX's own training corpus could not be obtained, so its rows are not a clean holdout and may be
contaminated in its favour — which makes its near-zero recall worse news rather than better.

## 5. The two predictors are not independent

APEX and ANIA share training-data ancestry. Their agreement is weaker corroboration than it looks,
and a consensus selector inherits bias common to both. Recorded diagnostics found
measured-threshold transfer failures — predicted MIC thresholds did not transfer cleanly to
held-out measured data. Neither predictor is calibrated for the organizers' panel.

## 6. Safety, haemolysis and selectivity are UNKNOWN

No haemolysis prediction, cytotoxicity estimate or therapeutic-index analysis **gates** this entry.
The selector is frozen and no safety axis enters it. Cationic amphipathic peptides of this class
can be haemolytic.

We do have **predicted** HC50 for all four portfolios, from HemoPI2 v1.3, run as an analysis tool
after the selector was frozen. **It is not usable evidence, and we have now measured why.** Against
QMAP's ground-truth HC50 values, HemoPI2 achieves R² of **−0.15** on held-out peptides below 60%
identity to its training data and **−0.27** below 40% — worse than predicting the mean — and detects
about **one in nine** truly haemolytic peptides. Its apparently strong whole-set performance
(R² 0.656, Spearman 0.808) is memorisation: 76.3% of that evaluation set appears in HemoPI2's own
published training data.

Our top-100 is exactly the kind of peptide it fails on: maximum 68.7% identity to any of 103,143
MarLys entries, median 50.0%, 18 of 100 with no detectable alignment at all.

So the screen's finding that no peptide falls below 5 µM predicted HC50 is close to **uninformative**,
not reassuring, and the therapeutic-index figures built on it — including the adverse comparison
against the superseded entry we reported honestly at the time — should be read as carrying no signal.
See `LANE3_SAFETY_SCREEN_IS_UNINFORMATIVE.md`.

We have **no measured** HC50 of any kind. The "Optimal Selectivity" category is scored on measured
HC50/MIC50, and we have no measured data, so we have **no evidence either way** about our standing in
it. Absence of evidence is not evidence of poor selectivity — these peptides might do well — but we
cannot claim it, and we would be entering that category blind.

*(An earlier version of this section said we had "no HC50 evidence" full stop. That was written
before the screen was run and contradicted the shipped `SAFETY_SCREEN.json`. Corrected above: the
predicted evidence exists, and it is not trusted.)*

## 7. Portability is decision-stability, not bit-equivalence

Byte-exact macOS↔Linux equality **FAILED** and is preserved as a failure. What passed is weaker
and explicitly scoped: predicted values agree within a pre-registered 1e-4 log10 MIC budget (worst
observed 2.96e-05), and every binary activity label, breadth numerator and all 24 tested selector
orderings are identical, with Linux bit-deterministic across two clean runs. Certified on the
tested pools only — not on the 50,000 library, the fresh replication pools or the native controls.

## 8. Novelty is verified against both published rules

We satisfy the executable rule (`Levenshtein.ratio` must not exceed 0.80 against the supplied
reference). Observed maximum is **0.764706**, a margin of **0.035294** — real, but not large. We also
satisfy the proposal's MMseqs2/MarLys rule, which is evaluated further down this section and was
previously listed here as unevaluated.

This is worth stating carefully because an earlier verification of mine was wrong: it unpacked the
validator's `_read_fasta` as `(sequences, headers)` when it returns `(headers, sequences)`, so the
novelty and overlap checks ran against FASTA headers and passed meaninglessly. The corrected check
also revealed that the **superseded** E=5000 entry sat at exactly 0.800000 — zero margin, passing
only because the rule is a strict `>`.

Note also that the pipeline's internal eligibility gate uses `lcs_ratio`, a *different* metric from
the validator's `Levenshtein.ratio`. The pipeline therefore only approximates the official rule and
does not guarantee it; compliance must be checked with the official function, as it now is.

The proposal describes a *different* rule — MMseqs2 identity ≤ 80% against the MarLys AMP database —
and that rule **has now been measured for the first time**, under settings we chose. Under MMseqs2's
own default coverage our maximum identity is **68.7%**; requiring 80% query coverage gives 76.9%.
Zero violations under either. Both higher-potency alternatives showed violations under both.

**This is not a determination of compliance, and should not be read as one.** The proposal names
MMseqs2 but publishes no parameters, and identity is acutely sensitive to them:

- under a permissive `-c 0.5` coverage threshold **every portfolio including ours fails** (ours with
  21 violations, V3 with 10);
- with no coverage requirement at all, MMseqs2 reports "100% identity" for 4-residue local alignments
  against 20-residue peptides and flags roughly three-quarters of every portfolio.

The defensible statement is narrow: **under every setting we tested in which any portfolio passes,
ours passes, and it has the lowest maximum identity of the four.** If the organizers use a more
permissive coverage threshold than MMseqs2's own default, we would expect violations — and the
proposal says non-compliant candidates are *replaced by the next valid entry*, so the consequence
would be losing slots rather than the entry.

Two things here are parameter-free and do hold outright: **zero exact matches against MarLys across
the whole 50,000-peptide library**, and the executable `Levenshtein.ratio` rule the official validator
actually runs.

What also remains true: our known-sequence inventory beyond MarLys is partial, and no absence of exact
matches establishes mechanistic novelty. Full grid including every adverse setting:
`LANE12_RULE_AMBIGUITY_RESOLVED.md`.

## 9. Generator training data: partly measured now, and the answer is that it overlaps

**Updated 2026-09-27.** This section used to say only that we could not certify disjointness. That was
honest and also a shrug. We went and measured the files the authors actually publish.

**What is now measured.** AMP-Designer's published `data/` folder holds 14,760 unique peptides across
six corpora (APD3, CAMP, DBAASP, dbAMP, DRAMP and its own prompt-training files), plus 630,683 UniProt
sequences. **80.4% of that peptide union is inside the challenge's `data/antibacterial.fasta`**, and it
covers **30.1%** of that reference set. It is not disjoint, and now we know by how much. Worse for
independence: ANIA harvests DBAASP, dbAMP and DRAMP, and the reference set itself aggregates dbAMP
(53.1%), DRAMP (46.6%), DBAASP (36.7%), CAMP (30.2%) and APD (5.2%). Generator, one scorer and the
evaluation reference all descend from the same public pool.

**What is still not knowable.** Both upstream training scripts default `--train_raw_path` to a file
that is **not in the repository**, and the README gives no training command, so the exact input that
produced the released checkpoint is not pinned and **we have not reconstructed it**. APEX is worse: its
pinned commit contains **no training data and no training script at all**. So we have measured the
overlap of *published data*, not of the models' actual training sets, and we are not going to conflate
the two.

**What does not overlap is our output.** Zero exact matches between our 50,000 sequences — or our
top-100 — and any of the eight published files, UniProt included. Maximum Levenshtein similarity from
our top-100 to that 14,760-sequence union is **0.7059**, *further* than our 0.7647 maximum against the
reference set the 0.80 rule is actually written about. See `DATA_AND_MODEL_DISCLOSURE.md` §2–3.

## 10. Device dependence — weaker than we expected, but still real

The submitted artifacts were generated on an RTX 4090 (Ada, capability 8.9) with CUDA 12.8. Repeat
execution on that device is byte-identical.

We originally expected, and wrote here, that a different GPU would produce different sequences —
the normal situation for a sampling generative model. **That turned out to be too pessimistic.** A
clean-room run of the unchanged official validator on an **RTX A4500 (Ampere, capability 8.6)**
reproduced both files exactly, in both of its runs:

| | library.fasta | top.fasta |
|---|---|---|
| shipped (RTX 4090) | `a91c0de9…` | `ece3b706…` |
| clean-room run 1 (RTX A4500) | `a91c0de9…` | `ece3b706…` |
| clean-room run 2 (RTX A4500) | `a91c0de9…` | `ece3b706…` |

`raw_generated` 51,712 and `selector_pool_count` 48,133 matched the reference run as well. See
`validator_results/CLEANROOM_VALIDATION.txt`.

**Updated 2026-09-27:** a third and fourth A4500 run, inside the authoritative validation of the
weights-bundled variant, reproduced both files exactly again — with the checkpoint delivered by **Git
LFS** rather than by HTTPS retrieval. That is four completed Ampere generations and two Ada ones, all
byte-identical. `validator_results/AUTHORITATIVE_VALIDATION_2026-09-27.md`.

**This is still two GPU architectures, not all hardware.** It is evidence that the deterministic-algorithm
configuration and pinned CUDA/Torch build are doing their job across at least Ada and Ampere. It is
not a guarantee for an arbitrary device, a different CUDA build, or CPU execution, none of which we
have tested. The claim we make is exactly what was measured and no more.

## 10b. Phase-1 whole-library screening: we are behind the published baseline on two named metrics

Added 2026-09-27, after the whole-library seqme audit. This is the newest and, for Phase 1, possibly
the most consequential limitation in this document.

The competition's Phase 1 screens the **full 50,000 library** with seqme, and the proposal names
Fréchet Biological Distance and Maximum Mean Discrepancy explicitly. Measured against the challenge's
own reference set with ESM-2:

| | ours | AMP-Diffusion baseline | our seed range |
|---|---:|---:|---:|
| FBD (lower better) | **2.0502** | 1.2302 | 0.0313 |
| MMD (lower better) | **12.2646** | 6.7267 | 0.2482 |
| AuthPct (higher better) | **0.8698** | 0.9070 | 0.0032 |

AMP-Diffusion is excluded from rankings but its library is published as "a Phase 1 target for
participants to beat". On these metrics we do not beat it, the gaps are 25–30× our seed-to-seed
spread, and all three replicated on an independent score-blind sample. **At most 20 teams advance from
Phase 1.** If the organizers' aggregation weights these metrics heavily, this is a material risk to
advancing, and no amount of top-100 evidence addresses it.

**Three things temper that, none of which cancels it.**

1. **FBD and MMD fail their own negative control.** A character-shuffled copy of the reference set —
   composition and length preserved, every motif destroyed — scores FBD **0.7248** and MMD **2.1465**,
   better than both real libraries. Mean-pooled ESM-2 embeddings of short peptides are largely a
   composition statistic. So these numbers are valid as numbers and invalid as evidence about
   AMP-likeness.
2. **The same discount removes four of our apparent leads.** The shuffle also beats us on precision,
   recall, clipped density and clipped coverage, so those cannot be cited in our favour either. The
   discount is symmetric or it is worthless.
3. **The leads that survive are the transparent ones** — alignment-based novelty at the ≥80% threshold
   (1.47% vs 3.82%), clustering coverage (48,833 vs 43,470), FKEA (the one embedding metric whose
   control behaves), and our synthesizability rule (78.18% vs 38.43%). **AuthPct is the one adverse
   metric whose control also behaves, and we trail it by 0.0373** — small, replicated, and not
   dismissable.

**The mechanism is the chemotype concentration already in this document.** Our library sits at GRAVY
+0.135 and amphiphilicity 0.525 against the reference's −0.289 and 0.395. Section 6's haemolysis
caution and this section are two views of one fact.

**Update 2026-09-28 — the first family was attempted, and the instrument failed.** Deep-AMP, one of
the three models the proposal names, was obtained at the commit BATTLE-AMP pins and run. It predicts
**3,789–43,027 µM** for the 15 peptides of its **own paper** whose measured MICs are **0.4–100 µM**, and
achieves no positive rank concordance on either matching endpoint. It scores our library ~2,900× better
than the baseline's and we **decline to claim it**. So this family is still unmeasured — but now because
the only reproducible instrument we could reach is unusable, not because nobody looked.
`DEEPAMP_DIAGNOSTIC_RESULT.md`.

**And the largest gap is not a number at all.** The proposal's first metric family is surrogate
activity prediction using **AMPredictor, MBC-Attention and DeepAMP**. We reproduced none of them. Our
APEX/ANIA work is a different set of models applied to a different object (the top-100). **The family
closest to what the competition measures is the family we have not measured.** Full detail and the
reasoning for changing nothing: `SEQME_WHOLE_LIBRARY_AUDIT.md`.

## 11. Branches closed without full resolution

- **ARCADIAMP**: closed as futile. Its third seed (3,456 of 4,096 rows) was never scored. The
  futility proof shows even an ideal third seed could not meet the frozen two-of-three gate, so it
  could not have displaced this entry — but the arm is unfinished, not beaten.
- **BroadAMP-GPT**: one configuration killed; the family was not exhaustively explored.
- **EBAMP, MOFormer**: no released generator weights/tokenizer; assets unavailable.
- **AMPGen** (EvoDiff-based, public repo `xiyanxiongnico/AMPGen`, 38 peptides synthesised with
  >80% active): genuinely reproducible in principle, but **killed on time grounds** — it could not
  clear the full frozen funnel (smoke → screen → serious → multi-seed replication → 50k →
  validation → packaging) before the deadline. This is a scheduling decision, not a scientific
  judgement against the method.
- **Soft-prompt ProtGPT2 + MCL ensemble** (npj Drug Discovery 2026): no public code or weights
  located, so not reproducible before the deadline.
- **OmegAMP**: pilot not promoted.

A complete four-arm tournament was never achieved. This entry is the strongest of what was
actually testable, not the winner of an exhaustive search.

## 12. What would most likely prove us wrong

If APEX mean MIC predicts the organizers' measured panel materially better than breadth, ANIA and
diversity do, the potency-ranked portfolio is the better entry and this one underperforms it — its
mean predicted MIC is 57.06 µM against our 73.46 µM, and that gap did not close.

Our case depends on three things being true: that ANIA carries real independent signal, that
portfolio diversity matters under random 25-peptide sampling, and that breadth at the challenge's
own MIC ≤16 µM threshold matters more than mean potency. All three are plausible. None is
established.

One thing that *is* established is narrower than it sounds. A null control (`NULL_CONTROL.md`)
shows the frozen selector beats random selection from its own universe by 26 standard deviations, so
the selection step extracts real structure from the predictor outputs rather than merely sampling more.
That is an internal-consistency result measured against the very models in question, not biological or
independent validation.
That rules out one failure mode — "the gain is just a bigger search" — and leaves the larger one
entirely open: the predictors themselves may not transfer. A selector can be excellent at
maximising a proxy that turns out not to predict reality, and under homology control these
predictors explain under 30% of MIC variance.

Note also what diversity does and does not buy. By linearity of expectation, portfolio diversity
does not change the *expected* number of active peptides in a random 25-peptide draw — only the
variance. Since this entry is marginally behind on expectation, preferring it for its diversity is
the right call for placing consistently and the wrong one for maximising the chance of winning
outright. Earlier drafts listed diversity alongside breadth as though the two were the same kind of
advantage. They are not. A further caveat cuts both ways: under homology-controlled evaluation, MIC regression
explains less than 30% of variance, so neither portfolio's predicted advantage should be trusted
far.
