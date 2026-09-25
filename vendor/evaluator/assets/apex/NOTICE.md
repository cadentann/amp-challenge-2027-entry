# Modified APEX files vendored here

`APEX_predict.py` and `utils.py` in this directory are **modified** copies of the files in
`gitlab.com/machine-biology-group-public/apex-pathogen` (MIT). They cannot be retrieved from
upstream, so they are redistributed here under that licence with attribution. Every other APEX
and ANIA file — the other two source files and all eleven weight files — is byte-identical to
upstream and is fetched by `scripts/prepare_entry.py` rather than redistributed.

Upstream at commit `417a4441a1e6ef8b10d2352e1c059622d5259f3a`.

## What was changed, and why

`APEX_predict.py` (upstream 3,213 bytes → 3,465 bytes):

- **`sorted(glob.glob(...))` when loading the eight base learners.** Upstream iterates an
  unsorted `glob`, so ensemble member order depends on directory iteration order. The ensemble
  mean is order-independent, but the retained per-member arrays are not, and this entry's
  equivalence receipts compare member arrays position by position. This is the one change with
  scientific consequence: it makes member order deterministic.
- Models are loaded from a path relative to the file rather than the current directory, and with
  `map_location="cpu"`, so the script works when invoked from anywhere and on a CPU-only host.
- An `-o/--o` output path option, replacing a hardcoded `Predicted_MICs.csv`.
- `-g auto` detects CUDA instead of defaulting to requiring a GPU.
- Formatting only: tabs to spaces, explicit imports in place of `from utils import *`.

`utils.py` (upstream 3,009 bytes → 2,070 bytes): reduced to the two functions this pipeline
calls, `make_vocab` and `onehot_encoding`, both byte-preserved in behaviour. The removed helpers
built AAindex embeddings that the pathogen models do not use.

No model weights, no encoding arithmetic and no prediction logic were altered. The R-free
evaluator built on these files reproduces the native R-backed evaluator exactly across 510,000
values on both validated platforms; see `validation/`.
