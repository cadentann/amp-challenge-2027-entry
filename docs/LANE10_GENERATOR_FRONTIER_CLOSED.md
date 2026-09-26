# Lane 10 / 11 — new generators and portfolio mixtures: closed, with a final check

The pre-registration closed these lanes on time and eligibility grounds. A final bounded scan was run
anyway, because the directive asks for it and because closing a lane on a prediction rather than a
look is the kind of shortcut that hides a missed opportunity.

## What the final scan found

Candidates surfaced for 2025–2026: **dsAMP / dsAMPGAN** (CNN-attention-BiLSTM + GAN), **deepAMP**
(peptide language model, reports >90% of designs beating penetratin on both Gram classes), a
**multi-condition constrained directed generation** framework for membrane-targeting anti-Gram-negative
peptides, and **AntiBP3** (a classifier, not a generator). Plus the families already assessed:
AMPGen, soft-prompt ProtGPT2 + MCL, MPOGAN, MOFormer, EBAMP, OmegAMP.

**None clears the bar this lane set in advance**, which required all of: public source, public
checkpoint, challenge-compatible sequences, fast inference, experimental evidence, and enough time for
a fair comparison before the deadline. For each of the new candidates, public weights could not be
located from the published record. That alone is disqualifying — reproducing a generator from a paper
description is not reproducing the authors' model, and an entry built that way could not honestly be
attributed.

## Why time closes it even if weights appeared

Five days remain. A new generator would have to clear the same funnel this one did: smoke test,
1,000-candidate screen, multi-seed replication against matched controls, full 50,000 generation,
48,000-candidate scoring, official validation from a clean clone, and packaging — and it would need
its own prospectively frozen protocol written before any score was seen, because otherwise the
comparison is exactly the post-hoc selection this project has refused throughout. The incumbent took
weeks to get through that funnel. Starting a second one now would produce either an unvalidated entry
or an abandoned branch.

## Why mixtures stay closed too

A top-100 drawn from two different generators raises a question no public rule answers: which model is
the entry attributed to, and does mixing in any AMP-Diffusion-derived candidate inherit the
"excluded from rankings" status of the baseline. The eligibility downside is unbounded and the upside
is speculative. `ELIGIBILITY_REVIEW.md` §5 records that the derivative question is the one rule
ambiguity that remains genuinely unresolved; deliberately walking into it would be the worst use of
that uncertainty.

## Status

**CLOSED.** Not because nothing exists, but because nothing exists that can be reproduced faithfully
and validated honestly in the time available. Recorded as a scheduling and eligibility decision, not
a scientific judgement against any of these methods.
