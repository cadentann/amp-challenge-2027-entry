# Lane 12 — the rule *text* is located; sampling is settled, novelty is measured but not determined

> **Superseded in part, 2026-09-28.** The current official wording resolves the sampling rule to
> **25 drawn from the top-100**, and states that a top-100 peptide over the 80% identity threshold is
> *"treated as invalid and replaced by the next valid candidate"* rather than disqualifying the team.
> The top-50 reading below is retained as **historical sensitivity analysis**, not a live compliance
> question. See `CURRENT_RULE_STATE_2026-09-28.md`.

The shipped package recorded two open rule questions. One is now genuinely settled from the primary
source. The other — novelty — is better understood but **not** closed: we located the rule the proposal
states and measured our position under settings we chose, and the organizers have published no
parameters, so what follows is a measurement with a stated scope, not a compliance determination.

## The primary source

The organizer proposal, captured in this project's rules snapshot (see
`EXTERNAL_REFERENCES.md` for its location — it is a third-party document and is deliberately not
redistributed inside this package), states the Phase 2 selection rule directly:

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

## Ambiguity 2 — novelty: the alternative rule is now measured, under parameters we chose

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

### What this establishes, and what it does not

1. **Under the two coverage settings we tested, the shipped entry shows zero violations** and has the
   lowest maximum identity of the four portfolios (68.7% under MMseqs2's own default coverage).
2. **Both higher-potency alternatives showed violations under both of those settings.** That raises
   their exposure relative to ours. It does **not** establish ineligibility: the organizers' parameters
   are unpublished, and the separate AMP-Diffusion-derivative question that also bears on them has no
   controlling public rule (`ELIGIBILITY_REVIEW.md` §5).
3. **Under the lenient `-c 0.5` reading every portfolio fails, ours included, and V3 fails least**
   (10 violations against our 21). This row is adverse to us and is not discounted: `-c 0.5` is a
   defensible choice for peptides this short even though it sits below MMseqs2's own default. If the
   organizers use it, we would expect violations.
4. **A breach would cost ranked slots, not the entry.** The proposal says non-compliant candidates
   "are replaced by the next valid entry".
5. **What is parameter-free, and therefore actually settled:** zero exact matches against MarLys
   across all 50,000 peptides, and the executable `Levenshtein.ratio` rule the official validator
   runs, which we satisfy at 0.764706 against a 0.80 limit with a 0.035294 margin.

The honest one-sentence summary: **under every setting we tested in which any portfolio passes, ours
passes with the largest margin — and we cannot know whether the organizers will use such a setting.**

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
