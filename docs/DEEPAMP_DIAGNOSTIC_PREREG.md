# Pre-registration — Deep-AMP surrogate-activity diagnostic

**Frozen 2026-09-28, before any Deep-AMP score on any project sequence was computed.** The only
Deep-AMP predictions made before this document existed were on the **three example sequences shipped
inside the wrapper repository** (`sample.fasta`), used to confirm the models load and run on CPU. No
project sequence was scored. Inputs and asset hashes: `DEEPAMP_FROZEN_INPUTS.json`.

## 1. Why this exists, and what it is not

The whole-library seqme audit marked the organizers' **first** Phase-1 metric family — surrogate
activity prediction with **AMPredictor, MBC-Attention and DeepAMP** — as **NOT COVERED**. This closes
part of that gap with one bounded diagnostic.

**These are additional predictor diagnostics.** They are not independent biological validation, not the
official Phase-1 aggregation score, and not a reason to change the finalist. The organizers' weights,
reference sets and tie-breaks are withheld until Phase 1 closes; nothing here estimates a rank.

## 2. What was checked before running anything

**The ledger was checked first.** No prior scoring work exists for any of the three predictors —
searched and confirmed absent. Two prior assets **are** reused rather than rebuilt:
`STAGE2_MEASURED_BENCHMARK_BLUEPRINT.md` (which already pinned `battleamp-snakemake` at
`8c659c0cc3d69a260b1865984dbea9d1199f651d`) and **`pandi2023/`**, which already holds the measured
cohort from Deep-AMP's *own paper*, extracted from the official supplement with hashes and licence.

**Permissions.** The Deep-AMP wrapper `szczurek-lab/BattleAMP-deep-amp` @
`0a31ad796732b5e5874c3f92e771057e887f58a9` is **MIT**, Copyright 2022 Amir Pandi, and **contains the
four trained regressor SavedModels in-repo** — no separate weights fetch, no credentials, nothing
private. `battleamp-snakemake`'s own `LICENSE` file is MIT (GitHub's API reports `NOASSERTION`; the
file is unambiguous). Upstream model: Pandi et al., *Nature Communications* 14:7197 (2023),
DOI 10.1038/s41467-023-42434-9.

**A discrepancy in the harness, recorded now.** `battleamp-snakemake/models/registry.yaml` lists
Deep-AMP with **`gpu_required: true`** and credits "Yan et al., 2023". The wrapper's own
`model.yaml` says **`gpu_required: false`**, `inference.sh` sets `CUDA_VISIBLE_DEVICES=""`, and
`environment.yaml` is headed "CPU-only". The wrapper is the authority on its own model and it is
correct: all four variants load and predict on this laptop's CPU. **So this branch spends $0 of GPU
credit.** The registry's attribution is also wrong — the model is Pandi et al., not Yan et al.

**Units and transform, taken from the wrapper rather than assumed.** `mic_transform: log10`,
`mic_unit: uM`. `predict.py` writes `10 ** prediction`, so raw model output is **log10(MIC in µM)** and
the reported column is **MIC in µM**. The wrapper declares its own activity threshold as **32 µM**,
which is **not** this competition's **16 µM** criterion; both are reported separately and neither is
substituted for the other.

**Row binding, stated because it is a real hazard.** `predict.py` writes only `sequence`, `MIC`,
`MIC_unit` — the FASTA header is **dropped**, and rows are bound to inputs **positionally** by
`zip(sequences, mic_uM)`. Joining results back to a library is therefore by **sequence string**. Every
frozen library and top-list is **fully unique** (verified in `DEEPAMP_FROZEN_INPUTS.json`: 50,000/50,000 and
100/100), so the join is unambiguous. Our own runner preserves the input order *and* the header and
asserts the returned sequence equals the input sequence at each index.

**Supported lengths and omissions.** Deep-AMP's `MAX_LEN` is **48** and its alphabet is the canonical
20. Frozen inputs run 8–40 residues with canonical alphabets, so **no library or top-list sequence
should be dropped**. This is a prediction, and the runner will count and name every omitted sequence
rather than trusting it. The challenge reference set reaches length 50 and *will* lose some rows; if it
is used as an anchor, the exact omitted count is reported.

**No unpublished peptide leaves this machine.** Inference is local, on weights already downloaded. No
web service, no scoring website, no upload of any generated sequence.

## 3. Gate 0 — is Deep-AMP informative at all? Run and reported first

Before any library comparison is interpreted, Deep-AMP is scored against the **22 measured rows from
its own paper** (`pandi2023`, Supplementary Table 10): *E. coli* MG1655 MIC (gram-negative) and
*B. subtilis* PY79 MIC (gram-positive), µM, with `>100` right-censored and preserved as a bound.

Reported: Spearman ρ on the uncensored rows, plus a censored-aware concordance over all comparable
pairs, for the gram-negative variants against *E. coli* and the gram-positive variants against
*B. subtilis*.

**Declared interpretation, fixed now:**
- If **|ρ| < 0.30** on the matching endpoint, Deep-AMP is **uninformative for ranking on its own
  paper's data**, and every library number below is reported as **uninterpretable as evidence about
  our entry** — exactly as the haemolysis screen was handled when it failed the same kind of check.
- If **ρ ≥ 0.30**, the library comparison is interpretable, *with* the standing caveat that these 22
  peptides were generated and selected by Deep-AMP's own pipeline and may sit in or beside its training
  data, so this is an **optimistic** ceiling on its reliability, never a lower bound.

## 4. Frozen comparisons

Equal-sized and score-blind by construction; no score was seen when these were chosen.

| comparison | sets | note |
|---|---|---|
| **A — full library** | shipped s42 vs AMP-Diffusion V3 | both exactly 50,000, so equal-sized with **no sampling at all** |
| **B — equal-sized sample** | same two, `n = 19,670`, `sm.utils.subsample(seed=42)` | the identical rule and seed the 2026-09-27 audit used, reused so the two audits are comparable |
| **C — delivered product** | shipped top-100 vs V3 top-100 | the object Phase 2 actually draws from |
| **D — noise floor** | top-100s of holdout seeds s8191, s6007, s4423 | gives the seed-to-seed range for every statistic in C |
| **E — reserved** | `n = 19,670`, `subsample(seed=1337)` | **pre-selected now, run only if §5 fires.** Not run otherwise |

Statistics, all four variants separately (LSTM/CNN × gram-neg/gram-pos): median and mean predicted MIC
in µM, fraction ≤ **16 µM** (the challenge criterion) and fraction ≤ **32 µM** (Deep-AMP's own declared
threshold), and the full distribution's 5th/95th percentiles.

## 5. What counts as a material concern, and what it could change

A **material concern** requires **all three**:

1. **Direction** — the shipped top-100 is worse than V3's top-100 on a gram-negative Deep-AMP variant
   (higher predicted MIC, or a lower fraction ≤16 µM);
2. **Magnitude beyond noise** — the gap exceeds the **full observed range across the four AMP-Prompt
   top-100s** (shipped s42 plus the three holdout seeds), measured on that same statistic;
3. **Instrument credibility** — Gate 0 passed, so the predictor is known to rank better than chance on
   its own paper's measured data.

If it fires: re-check on **sample E** and state **exactly** what entry decision it could change. To be
concrete in advance, the only decisions it could bear on are (a) whether to keep the frozen
`CONSENSUS_FIXED` selector or note a documented third-predictor dissent against it, and (b) whether to
add a disclosure to `LIMITATIONS.md`. It could **not** license reselecting the top-100, changing the
seed, or regenerating the library: those invalidate the byte-identical replication, the
two-architecture reproduction, the decision-stability certificate and the authoritative validator
receipt, all of which bind seed 42's exact artifacts, with three days to the deadline.

**Default outcome: the finalist does not change.** A third predictor preferring a different portfolio
is not evidence that the portfolio is better — it is evidence that predictors disagree, which this
project has already measured directly (APEX and ANIA are not independent, and both sit at R² ≤ 0 on
held-out measured MIC). **Deep-AMP disagreeing with `CONSENSUS_FIXED` is an expected observation, not a
finding.**

## 6. Budget and scope

Local CPU only, **$0 of GPU credit**, inside a three-working-hour ceiling. **The BATTLE-AMP benchmark
is not installed and not run** — no Snakemake, no conda environments, no submodule checkout beyond the
single `deep-amp` wrapper, no 309 MB cached-prediction download. AMPredictor and MBC-Attention are
**not** run in this branch: both are declared `gpu_required: true` and neither is needed to answer the
one question here. They remain **NOT COVERED**, and that stays stated rather than quietly narrowed.
