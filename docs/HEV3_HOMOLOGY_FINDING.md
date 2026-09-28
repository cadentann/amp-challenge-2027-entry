# HEV3 — Homology-aware generalisation red team: RESULT

**Finding: against one proxy — proximity to `data/antibacterial.fasta` — the shipped entry has the
weakest leakage signature of the four portfolios. This materially rebuts part of the adverse product
comparison, and it is not a general claim about leakage: the proxy is not the predictors' training
data, and we have since measured that 80.4% of the generator's *published* corpora lie inside that
same proxy file.**

> **Added after an independent review.** This analysis originally covered only the three portfolios
> that existed when it was run, and the row labelled "AMP-Prompt (incumbent)" is the **superseded**
> E=5000 entry — not the entry that ships. The shipped full-opportunity portfolio was never
> measured here, while its conclusions were quoted elsewhere as though it had been. Its row has now
> been computed and is given first below. The conclusion holds and is slightly stronger.

## Question

Are the predicted activity differences between portfolios explained by proximity to known
antibacterial peptides — i.e. models recognising familiar families — rather than by design?

## Method

For all 100 peptides in each delivered portfolio, maximum `Levenshtein.ratio` against the
challenge's 39,448-sequence `antibacterial.fasta`, then the within-portfolio rank correlation
between that proximity and predicted activity. A positive GN@16-vs-similarity correlation, or a
negative APEX-mean-MIC-vs-similarity correlation, indicates predicted activity is being driven by
nearness to known actives.

## Results

| portfolio | mean max-sim | p90 | frac ≥0.60 | GN@16 vs sim (Spearman) | APEX mean MIC vs sim (Spearman) |
|---|---:|---:|---:|---:|---:|
| **Shipped entry (full opportunity)** | **0.6668** | — | 0.960 | **+0.058** | **+0.011** |
| AMP-Prompt (superseded E=5000) | 0.6711 | 0.7368 | 0.900 | +0.083 | −0.227 |
| Original potency | 0.7131 | 0.7826 | 0.980 | +0.180 | −0.101 |
| V3 (fallback) | 0.6520 | 0.7429 | 0.810 | **+0.341** | **−0.518** |

## Interpretation

1. **The shipped entry's predicted Gram-negative breadth is essentially uncorrelated with
   proximity to known antibacterials (+0.058), and its mean-MIC correlation is +0.011 — that is,
   nil.** Its apparent quality is not explained by proximity to this reference set. That is narrower
   than "not explained by family recognition", which earlier drafts claimed and which this design
   cannot establish. It is the weakest leakage
   signature of the four, slightly weaker than the superseded entry's.
2. **V3 shows a strong leakage signature** — GN@16 +0.341 and APEX mean MIC −0.518. Much of V3's
   predicted quality tracks how close its peptides sit to known actives. This is a substantive new
   negative for the validated fallback that was not previously measured.
3. **The potency portfolio sits closest to known antibacterials overall** (mean 0.713 vs the
   shipped entry's 0.6668). The ≥0.60-neighbour gap is narrower than it first appears, though:
   98% versus **96%**, not versus the superseded entry's 90%. This difference is small and the
   argument should not lean on it; the correlation figures, not the proximity figures, carry the
   weight here.

## Why this matters for the finalist decision

The product comparison showed the potency portfolio ahead on APEX Gram-negative breadth
(0.4914 vs the superseded entry's 0.3786; the shipped entry is at 0.4843). This analysis supplies a plausible, measured partial explanation: that
portfolio is systematically **nearer to known antibacterial peptides**, and its predicted activity
correlates more strongly with that nearness than the incumbent's does.

Read alongside AMPBench-MT's homology-controlled result — MIC regression **R² < 0.30** once train
and test are separated at 30% identity — the potency portfolio's edge is precisely the kind most
at risk of failing to transfer: a higher score on a metric whose reliability decays away from
training data, earned by peptides that sit closer to that data.

**This does not overturn the adverse comparison.** It reframes it: the gap is real in predicted
terms but less trustworthy than its size suggests, and the shipped entry's signal is the least
dependent on recognition.

## Limitations, stated plainly

- The reference set is the challenge's `antibacterial.fasta`, **not** APEX's or ANIA's training
  corpora, which are not fully obtainable. This is a proxy for training proximity.
- Correlation is not decomposition; we have not shown the incumbent's signal is *causally* design
  rather than recognition, only that it is not *explained* by this proxy.
- All three comparator portfolios have members at **exactly** the 0.80 eligibility ceiling. The
  shipped entry's maximum is 0.764706, so it is the only one of the four not sitting on the limit.
- Nothing here is biological evidence.
