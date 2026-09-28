# Deep-AMP surrogate-activity diagnostic — result: the instrument fails, the branch closes

**Outcome: the finalist does not change. Family 1 of the organizers' Phase-1 metrics stays NOT
COVERED.** One of its three named models was obtained, verified and run; it failed its pre-registered
reliability gate so badly that its verdict on our library — which is **overwhelmingly in our favour** —
cannot be claimed.

**Cost: $0.00. Local CPU only.** No GPU credit spent, no top-up, nothing uploaded. The BATTLE-AMP
benchmark was not installed or run: no Snakemake, no conda environments, no 309 MB cached-prediction
download, one submodule wrapper fetched and nothing else.

Protocol frozen before any project sequence was scored: `prereg/DEEPAMP_DIAGNOSTIC_PREREG.md`.
Inputs and asset hashes: `DEEPAMP_FROZEN_INPUTS.json`, `DEEPAMP_FROZEN_SAMPLES.json`.

---

## 1. What was obtained, and the permissions

| | |
|---|---|
| harness | `szczurek-lab/battleamp-snakemake` @ `8c659c0cc3d69a260b1865984dbea9d1199f651d` (the commit this project pinned on 2026-09-22), **MIT** |
| model wrapper | `szczurek-lab/BattleAMP-deep-amp` @ `0a31ad796732b5e5874c3f92e771057e887f58a9`, the exact submodule commit the harness pins, **MIT**, Copyright 2022 Amir Pandi |
| weights | **in-repo** — all four regressor SavedModels present, no separate fetch, no credentials. Per-file SHA-256 in `DEEPAMP_FROZEN_INPUTS.json` |
| upstream model | Pandi et al., *Nature Communications* 14:7197 (2023), DOI 10.1038/s41467-023-42434-9 |
| variants | LSTM and CNN × gram-negative and gram-positive, four in total, all run |

**Two errors in the organizers' own harness, found while verifying it.**
`battleamp-snakemake/models/registry.yaml` lists Deep-AMP as **`gpu_required: true`** and credits
**"Yan et al., 2023"**. The wrapper's own `model.yaml` says **`gpu_required: false`**, its
`environment.yaml` is headed "CPU-only", and its `inference.sh` sets `CUDA_VISIBLE_DEVICES=""`. The
wrapper is right — all four variants ran on a laptop CPU in seconds, which is why this branch cost
nothing. And the model is Pandi et al., not Yan et al.

## 2. Units, bindings, lengths and omissions — verified, not assumed

**Units.** The wrapper declares `mic_transform: log10`, `mic_unit: uM`, and `predict.py` writes
`10 ** prediction`. So raw output is log10(MIC in µM). Its declared activity threshold is **32 µM**,
which is **not** the competition's **16 µM**; both are reported separately below and neither is
substituted for the other.

**Row binding.** `predict.py` drops the FASTA header and binds rows **positionally**. Our runner keeps
the header, asserts the prediction count equals the input count for every set, and joins by sequence —
safe because every frozen set is fully unique (50,000/50,000 and 100/100).

**Lengths and omissions, counted rather than trusted.** Deep-AMP's `MAX_LEN` is 48.

| set | input | scored | omitted |
|---|---:|---:|---:|
| shipped library, V3 library | 50,000 each | 50,000 each | **0** |
| both n=19,670 samples | 19,670 each | 19,670 each | **0** |
| all five top-100 lists | 100 each | 100 each | **0** |
| **Deep-AMP's own paper's cohort** | 30 | 15 | **15** |

**Every one of those 15 omissions is a 49-residue peptide, one residue over the wrapper's limit.** The
model's own published peptides are 49-mers, so the public wrapper silently discards **half of the
cohort its paper reports**. Named individually in `evidence/DEEPAMP_SUMMARY.json`.

## 3. Gate 0 — the pre-registered reliability check, and it fails

Deep-AMP scored against the 22 measured rows from **its own paper** (*E. coli* MG1655 and
*B. subtilis* PY79 MIC, µM, censored values preserved as bounds). Matching endpoints only:

| variant | endpoint | n | Spearman ρ | p |
|---|---|---:|---:|---:|
| LSTM gram-neg | *E. coli* | 10 | **−0.201** | 0.58 |
| CNN gram-neg | *E. coli* | 10 | **−0.476** | 0.17 |
| LSTM gram-pos | *B. subtilis* | 11 | **−0.032** | 0.93 |
| CNN gram-pos | *B. subtilis* | 11 | **−0.110** | 0.75 |

Three of four are inside the pre-registered |ρ| < 0.30 failure band. **The fourth is worse than
failing, not better: ρ = −0.476 ranks in the wrong direction.** My pre-registration said "|ρ| < 0.30 →
uninformative", which would have let an anti-correlated variant through on magnitude alone. That was an
underspecified rule and I am not going to exploit it: a negative ρ is not usable ranking. No variant
achieves positive rank concordance on its matching endpoint, and every p-value is > 0.15 at n = 10–11,
so all four are also consistent with pure noise.

**The calibration failure is larger than the ranking failure.** Predicted against measured, same
peptides, same paper:

| peptide | measured *E. coli* MIC | predicted, LSTM gram-neg | predicted, CNN gram-neg |
|---|---:|---:|---:|
| 16 | **6.3 µM** | 16,609 µM | 10,195 µM |
| 21 | **10.4 µM** | 14,683 µM | 10,078 µM |
| 27 | **12.5 µM** | 17,195 µM | 9,914 µM |
| 29 | **12.5 µM** | 3,789 µM | 10,097 µM |

All 15 scored peptides are predicted between 3,789 and 43,027 µM while their measured MICs span
0.4–100 µM. **`frac ≤ 16 µM` is 0.0000 for the cohort**, although the paper measured 7 of 22 *E. coli*
MICs and 21 of 22 *B. subtilis* MICs at or under 16 µM. The model's own training targets are
log10 values spanning −1.64 to 3.51 with median 1.13; it is emitting ~4.0, i.e. **above its entire
training range**, and the high tail is a near-constant pile-up (log10 median 4.00–4.17, sd as low as
0.098) that looks like a saturated ceiling rather than a prediction.

**I did not determine the root cause, and I am not going to guess at one.** I did test the most obvious
candidate and it is **not** the answer. The wrapper's `predict.py` leaves padded positions as all-zero
vectors, whereas the model's own `code/utils.py` pads with `'-'` and one-hot encodes it, so every one of
the 48 positions carries exactly one 1. That is a real divergence between the public wrapper and the
model's own training code, and it is worth reporting. But re-running the cohort under the **original**
encoding leaves the magnitudes essentially unchanged (log10 median 3.99–4.02) and the correlations still
unusable (+0.268, −0.482, +0.055, −0.156). Evidence: `evidence/ENCODING_DEFECT_TEST.json`. Remaining
candidates, untested here: the published SavedModels may not correspond to the training tables shipped
beside them, or there may be a further preprocessing step the repository does not document.

**Gate 0 fails.** Under the pre-registration, everything in §4 is therefore reported as
**uninterpretable as evidence about our entry**.

## 4. What the library comparison said, and why we are not claiming it

Reported for completeness and transparency, **not as support for the entry**.

| set | LSTM gram-neg median | CNN gram-neg median | frac ≤16 µM (CNN gram-neg) |
|---|---:|---:|---:|
| **shipped library** (50,000) | **5.04 µM** | **6.56 µM** | 0.808 |
| AMP-Diffusion V3 library (50,000) | 14,578 µM | 9,748 µM | 0.090 |
| **shipped top-100** | **2.61 µM** | **3.69 µM** | **0.99** |
| V3 top-100 | 48.1 µM | 17.2 µM | 0.47 |
| our holdout top-100s s8191 / s6007 / s4423 | 1.42 / 1.96 / 1.61 | 3.59 / 3.74 / 3.79 | 1.00 / 1.00 / 1.00 |

Taken at face value this says our library is roughly **2,000–2,900× more potent** than the baseline's
and our top-100 nearly five times better. **We decline to claim any of it**, for three reasons that
would each be sufficient:

1. **The instrument fails Gate 0** on its own paper's measured data, so it has no demonstrated ability
   to rank or calibrate anything.
2. **The gap is an artifact of where each library lands in the saturated region.** 77.2% of V3's
   sequences are predicted above 1,000 µM versus 3.9% of ours, and inside that region the predictions
   barely vary (log10 sd 0.098). The "advantage" is mostly the fraction of each library pushed into a
   ceiling, not a potency difference. Pooled across both libraries, ρ(length, predicted log10 MIC) is
   +0.24 to +0.39, and V3's sequences are longer (mean 25.4 versus 17.3 residues).
3. **The cohort of peptides that were actually measured and found active scores worst of all**
   (median ~10,000–14,800 µM). Any metric that ranks real, assayed, active peptides below both
   generated libraries is not measuring activity.

**A result this favourable, from an instrument this broken, is exactly the kind this project has
repeatedly had to throw away.** It goes in the record as uninterpretable.

## 5. The concern rule could not fire, on two independent grounds

The pre-registered material-concern rule needed **all three** of: our top-100 worse than V3's, a gap
beyond our four-seed range, and Gate 0 passed.

- **Direction fails**: our top-100 is *better* on all four variants, not worse.
- **Credibility fails**: Gate 0 did not pass.

So no material concern exists, **the reserved seed-1337 sample was not scored**, and — as
pre-registered — it stays unscored rather than being spent on a rule that did not trigger. For
completeness, had the rule fired the only decisions it could have borne on were a documented
third-predictor dissent against the frozen selector and a `LIMITATIONS.md` disclosure; it could never
have licensed reselecting the top-100, changing the seed or regenerating the library.

## 6. What this does and does not close

**Closed:** Deep-AMP is now verified, licence-checked, actually executed, and shown to be unusable for
this purpose, with the evidence retained. The lane no longer rests on "not attempted".

**Still open, and stated plainly:** **family 1 remains NOT COVERED.** One of three named models was
attempted and it failed its reliability gate; **AMPredictor and MBC-Attention were not run at all** —
both are declared `gpu_required: true`, and neither was needed once the first model's own paper's data
disqualified it. The organizers' surrogate-activity family is therefore still unmeasured in any usable
sense, and the whole-library audit's `NOT COVERED` marking stands, now with a reason instead of a gap.

One caveat on this whole branch, in the other direction: BATTLE-AMP's harness is by the **same group as
the competition organizers**, so a defect in its Deep-AMP integration is a defect in something Phase 1
might plausibly be built on. That is a reason for us to hold our own results loosely, **not** a
prediction that the organizers will score us with a broken instrument.
