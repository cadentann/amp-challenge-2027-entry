# Current rule state — 2026-09-28

**This document is the controlling record of the competition rules as they actually stand today.**
Where an older project document reasons from a superseded reading, this one wins, and the older one has
been annotated rather than deleted so the correction history survives.

Sources: the live Kaggle competition page (Overview, Writeups and Rules tabs, read on 2026-09-28
without joining or accepting anything), the public AMP Challenge website, and the pinned organizer
proposal in `provenance/rules_snapshots/`.

---

## 1. Wet-lab sampling — RESOLVED, and the ambiguity is now closed

**Current official wording: 25 peptides are drawn at random from each advancing team's TOP 100.**

Live page, verbatim: *"From each advancing team's top 100 list, 25 peptides are selected at random,
forming a total cohort of 500 peptides."*

An earlier website FAQ said "top 50", and several project documents carried both readings side by side.
**That ambiguity is closed: top-100 is the current rule.** `LANE2_SUBSET_ROBUSTNESS.md` retains its
25-of-top-50 rows as **historical sensitivity analysis only** — they are no longer a live compliance
question.

**Nothing about the entry changes as a result.** Our top-100 is fully ranked and its top-50 prefix is
the stronger half, so we were safe under either reading; the resolution removes an uncertainty rather
than creating an opportunity. **Portfolio optimization is not reopened.**

## 2. Computational qualification — our diagnostics are relevant, and they are not the official score

The live Kaggle page states the Aggregation Score *"integrates multiple complementary aspects,
including"*:

- physicochemical properties of the generated peptides
- predicted potency using published oracles
- biologically informed embeddings
- synthesizability
- novelty to existing AMPs
- diversity of the generated library

**Our qualification work maps onto five of those six**, which makes it relevant evidence:
`SEQME_WHOLE_LIBRARY_AUDIT.md` covers physicochemical conformity, embeddings, novelty and diversity;
its addendum covers a synthesizability rate under **our own** seven-rule definition, not the
organizers'. The sixth — **predicted potency from published oracles** — is the one we could not
reproduce: `DEEPAMP_DIAGNOSTIC_RESULT.md` records Deep-AMP obtained, run, and **failing its reliability
gate on its own paper's measured MICs**, with AMPredictor and MBC-Attention never run.

**What we do not have, and will not manufacture:** the organizers' weights, their reference-set
composition, their tie-breaks, or any aggregate number. The page says the score *"was tuned to
discriminate between known potent and weak antimicrobial peptides, as well as negative examples
including Uniprot, peptides lacking any antimicrobial properties, and synthetic decoys"* — a design we
can read about but not reproduce. **No aggregation score is computed anywhere in this project and no
qualification rank is estimated.**

## 3. Current field size — context, not a forecast

Observed on the live Kaggle page, 2026-09-28: **125 entrants, 22 participants, 18 teams, 19
submissions**, with **up to 20 qualifying teams advancing** after computational screening, and the
competition showing **3 days to go**.

**This does not imply advancement.** More teams may still submit before the deadline; compliance
screening runs first and *"Teams that do not pass will be disqualified"*; and the screening is a
ranking, not a pass/fail against a fixed bar. It is recorded because it is a fact about the current
state, and because it is a reason **not** to delay externalization for further open-ended research.

## 4. Co-authorship — a documented source discrepancy, resolved conservatively

**The two official sources do not agree, and we are not going to paper over it.**

| source | wording |
|---|---|
| public AMP Challenge website | all teams advancing to experimental validation will be co-authors |
| Kaggle submission requirements | *"Teams that meet only the minimum requirements will be included in the experimental benchmark and receive their results, but will not be eligible for co-authorship."* Co-authorship eligibility is attached to a **Full Requirements** tier |

**Our response: build and validate against the stricter FULL tier**, so the entry satisfies the more
demanding reading whichever source controls. The Full tier requires a public repository following the
template, trained model weights, inference code, detailed usage documentation, a permissive OSI licence,
a fixed default seed producing identical repeated output, and full training-data disclosure.

**We do not claim co-authorship is guaranteed.** Meeting the stricter requirements is the most we can do
from our side; which source controls, and how the discrepancy is resolved, is the organizers' to decide.
**No organizer has been contacted about this**, and no message has been drafted or sent.

## 5. Novelty handling — the consequence of a violation is replacement, not disqualification

Current official wording, verbatim: *"All candidates in the top-100 list must have no more than 80%
sequence identity to any peptide in the competition's reference database of known AMPs. Candidates
exceeding this threshold are treated as invalid and **replaced by the next valid candidate**."*

**So a single over-threshold peptide costs a slot, not the entry.** Nothing in the current rules makes
one invalid peptide a team disqualification, and this project's documents should not be read as saying
otherwise.

**Our position, unchanged and preserved:** maximum `Levenshtein.ratio` from any top-100 member to the
challenge reference set is **0.764706**, margin **0.035294** under the 0.80 cap — the only one of the
four portfolios we compared with any headroom at all; the other three sit at exactly 0.800000. Against
MarLys with MMseqs2 the maximum is **68.7%** at MMseqs2's default coverage and **76.9%** at 80% query
coverage, **zero violations in both**. The MMseqs2 parameters remain unpublished, so that reading stays
open — but with replacement rather than disqualification as the consequence, the downside is now
bounded and small.

**The current top-100 is preserved exactly as it is.** The stricter headroom is kept; nothing is
reselected.

---

## What changed in the entry because of this update

**Nothing.** All five items either confirm a position we already held, close an ambiguity in our favour,
or bound a risk we had already disclosed. No artifact, selector, seed, policy or library was touched.
The corrections are to documentation only.
