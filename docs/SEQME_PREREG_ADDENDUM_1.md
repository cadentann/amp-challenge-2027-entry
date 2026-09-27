# Pre-registration addendum 1 — the organizers' own declared metric families

**Frozen 2026-09-27, after `SEQME_WHOLE_LIBRARY_PREREG.md` and before any value in this addendum was
computed.** Pass A of the main protocol was already running when this was written; nothing here
changes Pass A, and no Pass A number influenced what is declared below.

## Why this addendum exists

The main pre-registration followed seqme's public **peptide benchmark tutorial**, because that is the
concrete worked example from the authors of the library the organizers named. While it was running I
re-read the pinned organizer proposal (`provenance/rules_snapshots/organizer_proposal_local.txt`,
§1.5) and found that it **enumerates the Phase-1 metric families directly**. That is a better
authority than the tutorial, so the audit is extended to cover what it names. The proposal is quoted
by family below so the mapping can be checked rather than trusted.

`upstream/ampdiffusion-starter-kit/metrics/README.md` was checked as well: the organizers said the
baseline libraries' Phase-1 metrics would be published at launch, and that file is still a
**placeholder**. There is no published Phase-1 protocol and no published baseline target. That is why
the families below are covered with public tools rather than reproduced.

## Coverage of the four declared Phase-1 families

| family (proposal §1.5) | covered by | status |
|---|---|---|
| **1. Surrogate activity prediction** — "AMPredictor, MBC-Attention, DeepAMP … chosen to reduce any single model's bias" | nothing in this project | **NOT COVERED.** Declared here as the largest gap, before results are seen, so it cannot be quietly omitted later. Our APEX/ANIA evidence is **not** a substitute: different models, and it was computed on the top-100, not the library |
| **2. Sequence-level** — "Uniqueness, internal diversity, novelty relative to known AMPs (alignment-based, using normalized bit-scores), and clustering-based coverage" | Pass A covers uniqueness, diversity, exact-match novelty. **This addendum adds the alignment-based and clustering parts** | covered after this addendum |
| **3. Distributional similarity in embedding space** — "FBD, MMD, and precision/recall … against two reference sets (a curated set of known AMPs and a generic peptide set) using ESM2 and ESM-C" | Pass A/B, ESM-2 | **partially covered**: one reference set (known AMPs), one embedder (ESM-2). No generic peptide set and no ESM-C. Both reported missing |
| **4. Property distribution** — "Conformity of charge and amphiphilicity distributions to those of known AMPs, and rate of sequences satisfying empirically derived synthesizability constraints" | Pass A covers conformity; **this addendum adds a synthesizability rate** | covered after this addendum |

Also declared in the proposal and worth separating: *"Submitted sequences are also screened for exact
matches against the MarLys-AMP database … distinct from the 80% identity filter applied to the
top-100 list."* Pass A's exact-match novelty covers this at library scale; the top-100 identity rule
is already settled elsewhere (`docs/LANE12_RULE_AMBIGUITY_RESOLVED.md`) and is **not** re-litigated
here.

## New metrics, defined before computing

**Tooling.** MMseqs2 `18-8cc5c` (commit `8cc5ce367b5638c4306c2d7cfc652dd099a4643f`), the same binary
Lane 12 used. MarLys-AMP v3 (DOI 10.17632/w4hb5grjwb.3, CC0), 103,143 unique sequences,
`efd1159b…`. All local CPU; one full 50,000-vs-103,143 search measures **6 seconds**, so no
sampling is needed and none is used.

**M1 — alignment-based novelty vs known AMPs.** For every sequence in a library, the maximum hit
against MarLys, reported as:
- `bits_per_residue` = max bit-score ÷ query length, and
- `pident` and `qcov_weighted` (= pident × alnlen/qlen), the two identity readings Lane 12 already
  defined.

**The proposal says "normalized bit-scores" and does not say by what.** We therefore fix and state our
own normalisation rather than guess theirs, and we report the raw maximum bit-score alongside it so
any other normalisation can be recomputed from the saved hits. Direction: **lower is more novel.**

**Coverage settings, both reported, neither privileged.** `-c 0.8` (MMseqs2's own default) and
`-c 0.0` (maximal sensitivity). Lane 12 established that `-c 0.0` reports 100% identity for 4–9
residue *local* alignments against 12–26 residue peptides and flags most of **every** portfolio,
including all comparators — an artifact, not a finding. It is included as a bound, and any conclusion
that holds only at `-c 0.0` is to be reported as an artifact.

**M2 — clustering-based coverage.** `mmseqs easy-cluster` on each library alone, at `--min-seq-id`
0.5 and 0.8 with `-c 0.8`. Reported: cluster count, clusters ÷ sequences, largest cluster's share,
and the top-10 clusters' combined share. Direction: **more clusters and a smaller largest share mean
broader coverage.**

**M3 — synthesizability rate.** The fraction of each library passing **all** of the following. Every
*primitive* is taken verbatim from this project's already-frozen `lane8_developability.py`, so none of
them can be tuned to this answer; the **conjunction** is new and is stated here in full before being
computed:

- longest run of `AVILMFWC` < 7
- longest run of `VIYFWLT` (β-prone) < 5
- fewer than 2 cysteines
- not flagged by LANE8's solubility proxy, i.e. **not** (|net charge| / length < 0.10 **and** GRAVY > 0)
- C-terminal residue is not P
- N-terminal residue is not Q or N
- the first three residues are not all hydrophobic

The proposal's "empirically derived synthesizability constraints" are **not published**. This is
therefore *a* defensible constraint set, explicitly **not** theirs, and a difference between libraries
on it is evidence about these seven rules and nothing more.

## Rows and rule

Same eight rows as `SEQME_DATASETS.json`, same discipline: the three AMP-Prompt holdout seeds are **exposed
development evidence**, included only to measure each new metric's seed-to-seed spread.

`antibacterial.fasta` is a MarLys subset, so under M1 it must score at the ceiling. That is not a bug;
it is the **upper anchor** — it shows what a library of entirely rediscovered known AMPs looks like on
this metric, which is the thing Phase-1 novelty is meant to penalise. The permuted row is the lower
anchor.

**§6 of the main pre-registration governs unchanged.** Direction, magnitude beyond the measured seed
spread, and replication are all still required before anything about the entry may change, and one
favourable or unfavourable metric settles nothing.
