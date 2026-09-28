# Eligibility review — resolved as far as public evidence permits

Rules checked against the official website, its public source repository, the challenge template
and validator, and the official starter kit. **No organizer was contacted.** Nothing here should
be read as organizer adjudication.

## 1. Hard sequence rules — all satisfied

| rule | requirement | this entry |
|---|---|---|
| Alphabet | 20 standard residues | PASS |
| Length | 8–50 | PASS (12–34 in top-100) |
| Uniqueness | no duplicates | PASS (50,000 unique) |
| Termini | linear, free | PASS (no modification performed or implied) |
| Modifications | none | PASS |
| Library overlap | no exact match to `data/antibacterial.fasta` | PASS |
| Top-100 novelty | no `Levenshtein.ratio` > 0.80 to that set | PASS, max 0.764706 |
| Library size | 50,000 | PASS |
| Top list | 100 ranked | PASS |

Measured values are in `evidence/PORTFOLIO_COMPLIANCE.json`.

Verified by the **unchanged** official validator functions (`verify_submission.py`, SHA-256
`3f2eb1bd…`): `_verify_sequences`, `_verify_no_overlap`, `_verify_top`, `_veritfy_max_simularity`.

## 2. Submission tier

**Minimum (benchmark participation)** is fully satisfiable now: abstract, 50,000 library, ranked
top-100 with selection documentation, training/database summary, and a private GitHub repository
with read access granted to the named organizers.

**Full (co-authorship)** additionally needs a public repository, an OSI licence (MIT prepared),
`uv` with `uv.lock` and a pinned Python version, an entry point runnable as `uv run generate`, a
fixed default seed with identical repeated output, and full training-data disclosure. All are
prepared except the public repository itself, which is an irreversible external action reserved
for the operator.

Note the tension in §6: making the repository public is exactly what the full tier requires, and
it is the action the operator must weigh against the unresolved derivative question.

## 3. RESOLVED — sampling is 25 from the top-100

The organizer **proposal** states it directly: "From each qualifying team's top-100 list, 25 peptides
are drawn uniformly at random to form a total cohort of up to 500 peptides." That agrees with the
website's *How it works* page; the FAQ's "top 50" is the outlier, and the proposal is the
authoritative document. See `LANE12_RULE_AMBIGUITY_RESOLVED.md`.

We are safe under either reading regardless, because our top-100 is fully ranked and its top-50
prefix is the stronger half (GN breadth@16 0.5286 versus 0.4843 across all 100). The FAQ reading
would only help us.

The original contradiction, for the record:

- Website *How it works*: "From each advancing team's top 100 list, 25 peptides are selected at random"
- Website FAQ: "A random subset of 25 peptides is drawn from the top 50"
- Proposal PDF: 25 from top 100

**Consequence for us:** our top-100 is fully ranked, so either reading is satisfiable. Our top-50
prefix has GN breadth@16 of 0.5286 versus 0.4843 across the full 100, so the stronger half is
front loaded. No action required; recorded for transparency.

## 4. PARTLY RESOLVED — the rule text is located; compliance is measured, not determined

The template README and validator operationalise novelty as `Levenshtein.ratio` ≤ 0.80 against
`data/antibacterial.fasta`. The proposal instead specifies MMseqs2 identity ≤ 80% against the MarLys
AMP database. These are genuinely different metrics against different reference sets — and the
second one has now been run, because MarLys turned out to be obtainable (CC-0, DOI
10.17632/w4hb5grjwb.3, 103,143 unique sequences).

**Result, stated with its scope.** Under MMseqs2's own default coverage setting our maximum identity
to any MarLys entry is **68.7%** with zero peptides above 80%; requiring 80% query coverage gives
76.9%, again zero. Both higher-potency alternatives showed violations under both of those settings.

**The proposal names MMseqs2 but publishes no parameters, so none of this determines compliance.**
Identity is acutely sensitive to the coverage threshold:

| setting | shipped entry | E5000 | potency | V3 |
|---|---|---|---|---|
| bidirectional coverage ≥ 0.8 (MMseqs2's default) | 0 violations, max 68.7% | 0, 76.9% | 1, 83.3% | 1, 83.3% |
| query coverage ≥ 0.8 | 0 violations, max 76.9% | 0, 76.9% | 4, 83.3% | 2, 83.3% |
| **bidirectional coverage ≥ 0.5** | **21 violations** | 18 | 30 | **10** |
| no coverage requirement | 84 | 77 | 72 | 71 |

The bottom row is an artefact — MMseqs2 reports "100% identity" for 4-residue local alignments against
20-residue peptides — but the `-c 0.5` row is a legitimate and **adverse** reading under which we fail,
and under which V3 fails least. The defensible claim is narrow: **under every setting we tested in
which any portfolio passes, ours passes and has the lowest maximum identity.**

Separately, the proposal's Phase 1 check counts **exact** matches against MarLys, which is
parameter-free: **zero of our 100, and zero of all 50,000**.

The proposal also states that non-compliant candidates "are replaced by the next valid entry", so a
breach would cost ranked slots rather than the entry. Full grid and method:
`LANE12_RULE_AMBIGUITY_RESOLVED.md`.

**Consequence for us under the executable rule:** we satisfy it, with an observed maximum of **0.764706**
against the 0.80 limit — a margin of **0.035294**. That is real but not large, and it is worth
stating precisely, because an earlier version of this document reported "0.1497, a wide margin".
That figure was an artefact: the verification script unpacked the validator's `_read_fasta` as
`(sequences, headers)` when it returns `(headers, sequences)`, so the check ran against FASTA
headers rather than peptides. See `HEV1_PROMOTION_AND_COMPLIANCE_CORRECTION.md`.

The corrected measurement also showed that **all three alternative portfolios** — the superseded
E=5000 entry, the potency-ranked AMP-Diffusion list and the V3 fallback — sit at **exactly
0.800000**, passing only because the rule is a strict `>`. This entry is the only one of the four
with any headroom at all.

> **CORRECTION.** This paragraph used to read "We have **not** evaluated against MarLys/MMseqs2. If the
> organizers apply the PDF's definition, our novelty position is unverified." That was written before the
> lane ran and it contradicts §4's own measured table above. It is replaced, not deleted, so the change
> is visible.

**We have evaluated against MarLys/MMseqs2, and the result does not settle compliance either way.**
Measured with MMseqs2 `18-8cc5c` against MarLys-AMP v3 (103,143 sequences, CC0): under MMseqs2's own
default bidirectional coverage our maximum identity to any MarLys entry is **68.7% with zero peptides
above 80%**, and under an 80% query-coverage requirement the maximum is **76.9%, still zero violations**.
Under a permissive no-coverage setting the figure rises past 80% for **every one of the four portfolios**,
including all three comparators, which §4 explains is a short-alignment artefact rather than a real
identity.

**The proposal names MMseqs2 and publishes no parameters, so this is a measurement, not a determination.**
Passing the executable `Levenshtein.ratio` ≤ 0.80 check — which we do, with margin 0.035294 — settles the
rule the official validator implements. It does **not** settle the PDF's MMseqs2 rule, because the
parameters that rule depends on are unspecified. Our position is therefore **measured and
parameter-dependent**: favourable under both defensible coverage settings we tested, unfavourable under a
setting that fails every portfolio. This remains the most likely rule to change our compliance status, in
either direction, and it is the organizers' to resolve.

## 5. UNRESOLVED — modified-baseline derivative eligibility

The starter kit calls AMP-Diffusion the "official challenge baseline (excluded from rankings)". No
public rule defines when a modified derivative stops being the excluded baseline.

**This is why the entry matters here.** Our submitted entry uses **AMP-Prompt (AMP-Designer)**, a
different generator from a different research group, so it is not an AMP-Diffusion derivative and
this exclusion does not appear to reach it.

Our preserved fallback V3 **is** an AMP-Diffusion derivative (its own packaging describes it as an
"Experimental AMP-Diffusion participant derivative"), and the original potency portfolio is the
unmodified AMP-Diffusion library under an APEX ranking. **If the operator ever elects to submit
V3 or the potency list instead, this unresolved exclusion applies directly to them and should be
raised with the organizers first.** It does not apply to the entry as currently constituted.

## 6. Decisions reserved for the operator

These are external, irreversible, or commit the operator personally. None has been performed.

1. Making the repository public (required for the full co-authorship tier).
2. Granting organizer read access to a private repository (minimum tier).
3. Submitting on Kaggle.
4. Accepting any attestation or agreement.
5. Contacting the organizers about §3, §4 or §5.

## 7. Deadline

**October 1, 2026 AOE.** Submission is via the Kaggle competition page linked from the official
template README.
