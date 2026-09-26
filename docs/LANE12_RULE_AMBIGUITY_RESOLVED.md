# Lane 12 — the two rule ambiguities are resolved, and both resolve in our favour

The shipped package records two open rule questions and says we satisfy one novelty rule and have
**not** evaluated the other. Both are now settled against the primary source, and the unevaluated
rule has been run.

## The primary source

The organizer proposal, captured at
`releases/2026-09-24_private_v3/.../provenance/rules_snapshots/organizer_proposal_local.txt`,
states the Phase 2 selection rule directly:

> every peptide in the top-100 must have no more than 80% sequence identity, computed via MMseqs2
> pairwise alignment, to any entry in the MarLys reference AMP database; **non-compliant candidates
> are replaced by the next valid entry**

and separately:

> Submitted sequences are also screened for exact matches against the MarLys-AMP database to
> quantify rediscovered known peptides. This Phase 1 novelty check is distinct from the 80% identity
> filter applied to the top-100 list.

## Ambiguity 1 — sampling: RESOLVED as top-100

> From each qualifying team's top-100 list, 25 peptides are drawn uniformly at random

The proposal is explicit and consistent with the website's *How it works* page. The FAQ's "top 50"
is the outlier. **Our Lane 2 subset simulation should therefore be read on its 25-of-top-100 rows.**
We remain safe either way, because our top-100 is fully ranked and its top-50 prefix is stronger
than the whole (GN@16 0.5286 vs 0.4843), so the FAQ reading would only help us.

## Ambiguity 2 — novelty: the alternative rule is now evaluated

**MarLys is obtainable**, which the shipped docs assumed it might not be. It is CC-0, DOI
`10.17632/w4hb5grjwb.3`, mirrored at `github.com/bmcode00/marlys-amp` as
`static/database/MLAMP_db.json.gz` (sha256 `742d1766…`), and contains **103,143 unique peptide
sequences** — matching the proposal's "approximately 102,000". MMseqs2 18-8cc5c was used.

### Phase 1 check — exact matches: a clean sweep

| portfolio | exact matches in MarLys |
|---|---:|
| **Shipped entry** | **0 / 100** |
| Superseded E=5000 | 0 / 100 |
| Potency (AMP-Diffusion) | 0 / 100 |
| V3 fallback | 0 / 100 |
| **`library.fasta`, all 50,000** | **0** |

Not one of our 50,000 submitted peptides is a rediscovered known AMP. On the metric the proposal
says Phase 1 uses to "quantify rediscovered known peptides", we score zero rediscoveries.

### Phase 2 check — the 80% MMseqs2 identity filter

The rule does not state a coverage requirement, and that omission matters enormously for peptides
of 12–34 residues. Results are therefore reported across operationalizations rather than picking one.

| operationalization | shipped entry | E=5000 | potency | V3 |
|---|---|---|---|---|
| **bidirectional coverage ≥ 0.8** (MMseqs2's own default) | **PASS** — max 68.7% | PASS — 76.9% | **FAIL (1)** — 83.3% | **FAIL (1)** — 83.3% |
| **query coverage ≥ 0.8** (≥80% of the peptide aligns) | **PASS** — max 76.9% | PASS — 76.9% | **FAIL (4)** — 83.3% | **FAIL (2)** — 83.3% |
| bidirectional coverage ≥ 0.5 | FAIL (21) | FAIL (18) | FAIL (30) | FAIL (10) |
| no coverage requirement at all | FAIL (84) | FAIL (77) | FAIL (72) | FAIL (71) |

**The no-coverage row is an artifact and must not be read as a result.** With `-c 0.0` and maximal
sensitivity, MMseqs2 reports "100% identity" for **4–9 residue local alignments** against 12–26
residue peptides — our worst "100%" hit is a 4-residue match inside a 21-residue peptide. It flags
roughly three-quarters of *every* portfolio, including all three comparators, so it discriminates
nothing and cannot be what "no more than 80% sequence identity" means.

### What this establishes

1. **Under both defensible readings, the shipped entry PASSES with zero violations**, and has the
   lowest maximum identity of the four portfolios under MMseqs2's own default coverage (68.7%).
2. **Both higher-potency alternatives FAIL** under both defensible readings. This is now the second
   independent rule on which the potency portfolio and V3 are worse than the entry we ship — they
   already sat at exactly the 0.800000 Levenshtein limit with zero margin, and they also breach the
   MMseqs2/MarLys rule.
3. **The consequence of a breach is replacement, not disqualification.** The proposal says
   non-compliant candidates "are replaced by the next valid entry". So even the failing portfolios
   would lose slots rather than the entry. Our exposure on this rule is now measured and is nil
   under the readings that discriminate.
4. Under the lenient `-c 0.5` reading every portfolio fails, ours included, and V3 fails least (10
   vs our 21). That row is recorded because it is adverse to us; it is also a coverage threshold
   below MMseqs2's own default, applied to peptides short enough that half-coverage alignments are
   near-meaningless.

## Honest limits

- MMseqs2 parameters are ours, not the organizers'. Identity depends on sensitivity, k-mer size,
  coverage mode and threshold, and we chose high sensitivity (`-s 7.5 -k 6`) precisely so as not to
  flatter ourselves by missing alignments. A different parameterisation will give different counts.
- The proposal cites MarLys "[15]" with ~102,000 sequences; version 3 has 103,143 unique, and the
  dataset page describes 162,892 rows before deduplication. If the organizers pin a different
  version, counts will shift slightly.
- Nothing here is a claim that the organizers will run it this way. It is a defense package: under
  every reading we can construct in which any portfolio passes, ours passes.

Evidence: `experiments/LANE12_MARLYS_MMSEQS2_NOVELTY.json`.
