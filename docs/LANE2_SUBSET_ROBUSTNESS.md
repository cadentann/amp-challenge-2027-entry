# Lane 2 — random-subset robustness: the trigger fired, and cannot be acted on

The organizers assay 25 peptides drawn at random from the top-100, not the whole list. 100,000
Monte Carlo draws per portfolio per rule reading.

Lane 12 has since resolved the rule: the proposal says **25 from the top-100**. The
25-of-top-50 rows are retained because the website FAQ said otherwise and because they are
favourable to us.

## 25 drawn from the top-100 (the operative rule)

| portfolio | GN@16 mean | sd | p05 | distinct 0.60-families per draw | P(draw ≥ our median) |
|---|---:|---:|---:|---:|---:|
| **Shipped entry** | 0.4843 | **0.0265** | **0.4400** | **12.16** | 0.521 |
| Potency (AMP-Diffusion) | **0.4913** | 0.0309 | **0.4400** | 2.69 | 0.610 |
| Superseded E=5000 | 0.3785 | 0.0306 | 0.3257 | 11.40 | 0.000 |
| V3 fallback | 0.3529 | 0.0374 | 0.2914 | **25.00** | 0.000 |

## 25 drawn from the top-50 (the FAQ reading)

| portfolio | GN@16 mean | sd | p05 | families | P(draw ≥ our median) |
|---|---:|---:|---:|---:|---:|
| **Shipped entry** | 0.5286 | **0.0183** | 0.4971 | 15.27 | 0.381 |
| Potency | **0.5372** | 0.0222 | 0.5029 | 3.38 | 0.550 |
| Superseded E=5000 | 0.4142 | 0.0258 | 0.3714 | 12.39 | 0.000 |
| V3 | 0.4371 | 0.0268 | 0.3943 | 25.00 | 0.000 |

## Reading

**The pre-registered escalation trigger fired.** Under the FAQ reading, the potency portfolio
exceeds us on P(draw ≥ our median) by 0.170, above the 0.10 threshold. Under the operative
top-100 rule it exceeds us by 0.089, below it. That is recorded rather than glossed.

**It cannot be acted on, for two reasons fixed in advance.** The pre-registration states the
selector is frozen and that no lane may retune it; adopting the potency portfolio means either
switching to a different generator's library or re-ranking on APEX mean, both of which are selector
or generator changes justified by already-exposed data. And Lane 12 has since found that the potency
portfolio shows **MMseqs2/MarLys violations under both coverage settings we tested**, on top of
sitting at exactly the Levenshtein limit with zero margin. That raises its exposure materially; it does
not establish ineligibility, because the organizers' MMseqs2 parameters are unpublished and the
AMP-Diffusion-derivative question has no controlling public rule.

**What the lane does establish, favourably and honestly scoped:**

- Our variance is lower under both readings (0.0265 vs 0.0309; 0.0183 vs 0.0222), and our **5th
  percentile is identical to the potency portfolio's** under the operative rule (0.4400 both). Our
  worst draws are as good as theirs despite a lower mean.
- A random 25-draw from our list contains **12.16 distinct 0.60-linked families on average against
  2.69** from the potency list — a 4.5× difference in how much independent chemistry the organizers
  would actually be testing.
- As pre-declared: by linearity of expectation this **cannot** be claimed as an expected-value
  advantage. It is a variance and family-coverage claim, and it is stated as one.

Evidence: `experiments/LANE2_SUBSET_ROBUSTNESS.json`.
