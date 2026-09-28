# Third-party notices

This repository's own code and documentation are MIT licensed; see `LICENSE`.

`LICENSE` is kept as a **pristine MIT file** so that automated licence detectors — including GitHub's
own, and whatever the competition's compliance screening uses — identify it as MIT. Appending this
notice to `LICENSE` previously caused GitHub to report the repository licence as **"Other"
(NOASSERTION)** instead of MIT, which is exactly the wrong answer for a full-tier requirement that asks
for "a permissive OSI-approved license specified in the repository".

## Redistributed in this repository, with attribution

| file(s) | origin | licence | modified? |
|---|---|---|---|
| `assets/prompt_model/pytorch_model.bin` (340,569,639 bytes, SHA-256 `47944ff4…`), `assets/prompt_model/config.json` | AMP-Prompt / AMP-Designer, Zenodo DOI [10.5281/zenodo.17018363](https://doi.org/10.5281/zenodo.17018363), archive member of `prompt_model.zip` | **CC-BY-4.0** — <https://creativecommons.org/licenses/by/4.0/> | **No.** Byte-identical to the published archive member |
| `vendor/amp_prompt/{config.json, soft_prompt_embedding.py, vocab.txt}` | `github.com/jkwang93/AMP-Designer`, branch `AMP-Designer`, commit `07d455dd` | **MIT** | **No.** `vocab.txt` is byte-identical to upstream `voc/vocab.txt` |
| `vendor/evaluator/assets/apex/{APEX_predict.py, utils.py}` | GitLab `machine-biology-group-public/apex-pathogen` @ `417a4441` | **MIT** | **Yes** — changes itemised in `vendor/evaluator/assets/apex/NOTICE.md` |

## Retrieved at run time, not redistributed

`scripts/prepare_entry.py` fetches and hash-verifies these against pins in this repository:

- the eleven APEX weight files and the remaining two APEX source files — **MIT**,
  `gitlab.com/machine-biology-group-public/apex-pathogen`
- all ANIA sources and weights — **MIT**, `github.com/SilverGojo4/ANIA`

## Upstream credits

- **AMP-Prompt / AMP-Designer** — Wang et al., "Discovery of novel antimicrobial peptides with notable
  antibacterial potency by a LLM-based foundation model". Code `github.com/jkwang93/AMP-Designer` (MIT);
  weights Zenodo DOI 10.5281/zenodo.17018363 (CC-BY-4.0).
- **APEX** — GitLab `machine-biology-group-public/apex-pathogen`, MIT.
- **ANIA** — GitHub `SilverGojo4/ANIA`, MIT.
