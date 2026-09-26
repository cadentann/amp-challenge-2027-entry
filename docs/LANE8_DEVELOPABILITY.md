# Lane 8 / 9 — developability and chemotype

Characterisation only. The selector is frozen, nothing was filtered, no peptide was removed by hand,
and the challenge imposes no synthesis-liability constraint — every sequence remains rule-valid.

## Profile, all four portfolios against the 50,000-member library

| metric | **shipped** | E5000 | potency | V3 | library (50k) |
|---|---:|---:|---:|---:|---:|
| longest hydrophobic run, median | 3 | 3 | 3 | 3 | 3 |
| peptides with run ≥5 | **10** | 6 | 6 | 7 | 5,994 (12%) |
| peptides with run ≥7 | **2** | 1 | 0 | 0 | 1,267 (2.5%) |
| β-sheet-prone residue fraction | 0.461 | 0.455 | **0.491** | 0.447 | 0.444 |
| net charge, median | **+10** | +9 | +6 | +8 | +5 |
| peptides with charge ≤ +2 | 0 | 0 | 1 | 1 | 7,512 (15%) |
| GRAVY, median | −0.333 | −0.179 | −0.063 | −0.257 | +0.272 |
| **solubility-risk flags** | **0** | **0** | **0** | **0** | 3,359 (6.7%) |
| cysteine-containing | 3 | 2 | 3 | 3 | 5,580 (11%) |
| C-terminal proline | 1 | 0 | 0 | 5 | 1,137 |
| residues entirely absent | 2 (D, M) | 1 | 2 | 1 | 0 |

Earlier liability screening found **zero** aspartimide (DG/DP), deamidation (NG), pyroglutamate
(N-terminal Q), methionine-oxidation and length>40 liabilities in the shipped top-100, and zero
peptides with extreme GRAVY.

## Reading

**Favourable, and not by design.** The selector flags **0 of 100** on the solubility-risk proxy
against a 6.7% base rate in the library, avoids very low net charge entirely (0 peptides ≤ +2 against
15% in the library), and pulls GRAVY well below the library median (−0.333 vs +0.272). Nothing in
`CONSENSUS_FIXED` references solubility or hydrophobicity; this falls out of selecting for predicted
activity.

**Two mild adverse signals, recorded because they are adverse.** The shipped portfolio has slightly
*more* long hydrophobic runs than any comparator — 10 peptides at ≥5 and 2 at ≥7, against 6/6/7 and
1/0/0 — and the **highest median net charge at +10**. High cationicity drives both antimicrobial
activity and membrane disruption generally, so it is not a free lunch: it is consistent with the
chemotype concentration already disclosed in `LIMITATIONS.md`, and it is exactly the axis on which
haemolysis risk would express itself. We cannot quantify that risk, because the one haemolysis
predictor available is uninformative for peptides this novel
(`LANE3_SAFETY_SCREEN_IS_UNINFORMATIVE.md`).

**No action taken.** A developability filter would be post-hoc on a frozen selector, the liabilities
found are sparse (at most 10 of 100 on the worst axis, and 0 on the synthesis-critical ones), and the
rules impose no such constraint. The profile is disclosed instead.

Evidence: `evidence/LANE8_DEVELOPABILITY.json`, `evidence/PHYSCHEM_LIABILITIES.json`.
