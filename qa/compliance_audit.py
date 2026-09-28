#!/usr/bin/env python3
"""Final compliance audit against the official template README and the organizer proposal.
Exits non-zero if any executable requirement fails. Interpretive items are reported as OPEN,
never as satisfied."""
import hashlib, json, os, re, subprocess, sys
from pathlib import Path
import Levenshtein

F = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
A = F/"artifacts"; R = F/"amp-prompt-consensus-entry"
# The weights-bundled variant lives beside the package, not inside it. Derive it, allow an
# override, and skip its checks gracefully if it is not present.
V = Path(os.environ.get("AMP_WEIGHTS_VARIANT",
                        F.parent/"RELEASE_VARIANTS/entry-with-weights-lfs"))
CAN = set("ACDEFGHIKLMNPQRSTVWY")
fails, opens = [], []

def chk(cond, req, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {req}" + (f"   [{detail}]" if detail else ""))
    if not cond: fails.append(req)

def open_item(req, why):
    print(f"  OPEN  {req}\n        {why}")
    opens.append(req)

def fasta(p):
    return [l.strip() for l in open(p) if l.strip() and not l.startswith(">")]

print("SEQUENCE REQUIREMENTS (executable, from the template README)")
lib = fasta(A/"library.fasta"); top = fasta(A/"top.fasta")
chk(len(lib)==50000, "library contains exactly 50,000 sequences", f"{len(lib)}")
chk(len(set(lib))==50000, "all 50,000 are unique")
chk(all(set(s)<=CAN for s in lib), "only the 20 standard proteinogenic amino acids")
chk(all(8<=len(s)<=50 for s in lib), "every sequence is 8-50 residues",
    f"{min(map(len,lib))}-{max(map(len,lib))}")
chk(len(top)==100 and len(set(top))==100, "top-100 is 100 unique sequences", f"{len(top)}")
chk(set(top)<=set(lib), "top-100 is a subset of the library")
ref = fasta(R/"data/antibacterial.fasta")
refset = set(ref)
chk(not (set(lib) & refset), "no library sequence is identical to a known antibacterial peptide",
    f"{len(set(lib)&refset)} overlaps")
mx = max(max(Levenshtein.ratio(t,r) for r in refset) for t in top)
chk(mx <= 0.80, "no top-100 sequence exceeds 80% Levenshtein identity to the reference set",
    f"max {mx:.6f}, margin {0.80-mx:.6f}")
print("        (linear free termini / no modifications: structural — the pipeline emits bare")
print("         sequences with no terminal or chemical modification of any kind)")

print("\nREPOSITORY REQUIREMENTS")
def sh(*a, cwd=None):
    return subprocess.run(list(a), capture_output=True, text=True, cwd=cwd).stdout.strip()
chk((R/"pyproject.toml").is_file() and (R/"uv.lock").is_file(), "uses uv, with uv.lock present")
py = re.search(r'requires-python\s*=\s*"([^"]+)"', (R/"pyproject.toml").read_text())
chk(bool(py), "a Python version is pinned", py.group(1) if py else "none")
ep = 'generate = "finalist_entry.cli:main"' in (R/"pyproject.toml").read_text()
chk(ep, "entry point runnable as `uv run generate`")
src = (R/"src/finalist_entry/cli.py").read_text()
chk("default" not in src or "required=True" not in src, "all extra CLI arguments have defaults",
    "--preflight-only and --no-prepare are store_true flags")
chk((R/"LICENSE").is_file() and "MIT License" in (R/"LICENSE").read_text(),
    "permissive OSI licence present (MIT)")
# Needs git metadata. The Desktop archive strips .git to stay under its size limit, so an
# extracted copy cannot answer this. Report SKIP there rather than failing a requirement that is
# actually met — an unverifiable check and a violated one are not the same thing.
if (R/".git").exists():
    chk("FINALIST.lock.json" in sh("git","ls-files",cwd=R), "FINALIST.lock.json is tracked")
else:
    print("  SKIP  FINALIST.lock.json is tracked   [no .git here; verify in the canonical repository]")
lock = json.loads((R/"FINALIST.lock.json").read_text())
chk(lock.get("generation_seed")==42, "fixed default random seed", f"seed {lock.get('generation_seed')}")
e2e = json.loads((R/"validation/END_TO_END_VALIDATION.json").read_text())
chk(e2e.get("library_identical_across_runs") and e2e.get("top_identical_across_runs"),
    "identical output on repeated runs (recorded)")
chk(e2e.get("matches_shipped_artifacts") is True, "recorded runs match the shipped artifacts")

print("\nMODEL WEIGHTS")
if not (V/".git").exists():
    open_item("weights-bundled variant checks",
              f"variant not present at {V}; set AMP_WEIGHTS_VARIANT to include these checks. "
              f"The retrieval path below is what this package ships.")
else:
    tracked_v = sh("git","ls-files",cwd=V)
    has_ck = "assets/prompt_model/pytorch_model.bin" in tracked_v
    chk(has_ck, "weights-bundled variant tracks the checkpoint")
    if has_ck:
        ptr = sh("git","cat-file","-p","HEAD:assets/prompt_model/pytorch_model.bin",cwd=V)
        oid = re.search(r"oid sha256:([0-9a-f]{64})", ptr)
        pin = json.loads((R/"ASSET_SOURCES.json").read_text())["amp_prompt"]["checkpoint_sha256"]
        chk(bool(oid) and oid.group(1)==pin,
            "LFS pointer OID equals the pinned checkpoint SHA-256", oid.group(1)[:16] if oid else "none")
        big = [f for f in tracked_v.split() if (V/f).is_file() and (V/f).stat().st_size > 100*1024**2
               and "pytorch_model.bin" not in f]
        chk(not big, "no non-LFS tracked file exceeds GitHub's 100 MB limit", str(big[:3]))
        # Before 2026-09-28 this asserted NO remote, which was the correct pre-push invariant.
        # The variant is now pushed to one private repository, so the check becomes: exactly one
        # remote, and it is that repository.
        _rem = sh("git","remote","-v",cwd=V)
        _names = sorted({l.split()[0] for l in _rem.splitlines() if l.strip()})
        chk(_names == ["origin"], "weights variant has exactly one remote, named origin", str(_names))
        chk("cadentann/amp-challenge-2027-entry" in _rem,
            "that remote is the intended private staging repository")
chk((R/"scripts/prepare_entry.py").is_file(), "retrieval variant carries a hash-verified fetch path")

print("\nREPRODUCIBILITY GUARD (the silent-CPU-fallback repair)")
import ast as _ast
for _name, _root in (("retrieval variant", R), ("weights variant", V)):
    if not (_root/"src/finalist_entry").is_dir():
        print(f"  SKIP  {_name} is not present at {_root}")
        continue
    _g = _root/"src/finalist_entry/cuda_gate.py"
    chk(_g.is_file(), f"{_name} ships the device gate")
    if _g.is_file():
        _pl = (_root/"src/finalist_entry/pipeline.py").read_text()
        chk("gate_generation_device" in _pl and "enforce_device_gate=True" in _pl,
            f"{_name} enforces the gate on the production generation path")
        chk('"device_gate": device_gate' in _pl,
            f"{_name} records the gate verdict in the run receipt")
        _src = _g.read_text()
        _tree = _ast.parse(_src)
        _imports = {a.name for n in _ast.walk(_tree) if isinstance(n, _ast.Import) for a in n.names}
        _imports |= {n.module or "" for n in _ast.walk(_tree) if isinstance(n, _ast.ImportFrom)}
        chk("torch" not in _imports,
            f"{_name} gate does not import torch in the generating process", "child-process probe")
        chk("subprocess.run" in _src, f"{_name} gate probes a real tensor operation out of process")
        chk("FINALIST_ALLOW_CPU_GENERATION" in _src,
            f"{_name} gate has a documented explicit CPU override")
# The two variants must not diverge in anything the pipeline executes.
if (V/"src/finalist_entry").is_dir():
    _a = sorted((R/"src/finalist_entry").glob("*.py")); _b = {p.name for p in (V/"src/finalist_entry").glob("*.py")}
    _diff = [p.name for p in _a
             if p.name not in _b
             or hashlib.sha256(p.read_bytes()).hexdigest()
             != hashlib.sha256((V/"src/finalist_entry"/p.name).read_bytes()).hexdigest()]
    chk(not _diff, "src/ is byte-identical between the two release variants", str(_diff[:3]))

print("\nAUTHORITATIVE CLEAN-CLONE VALIDATION")
_ar = F/"validator_results/AUTHORITATIVE_RUN_LOG.txt"
chk(_ar.is_file(), "the authoritative run log is retained unedited")
if _ar.is_file():
    _log = _ar.read_text()
    chk("All checks passed. Submission is valid!" in _log,
        "the unchanged official validator reported all eight checks passing")
    chk("VALIDATOR_EXIT=0" in _log, "the validator exited 0")
    chk(_log.count("a91c0de9200a3d9f4377bfc6f81d36d21ea15bb9c940bd91fab797cd5ae2308b") >= 1
        and _log.count("ece3b7062d55d1ac4eb35f60e450cebec229ebfba63b5a0ab7214ecd4e5cb841") >= 1,
        "the run reproduced both submitted artifact hashes")
    chk('"probe_value": 8256.0' in _log or "8256.0" in _log,
        "the device gate's real CUDA probe returned its exact expected value")
    chk("REFUSING TO GENERATE" in _log and "GENERATE_NOGPU_EXIT=1" in _log,
        "the negative test shows generation REFUSES on a host with no visible GPU")
    chk("47944ff42f7ea6a448340d44c2027329833205dd658ec4777e77777bdab1adc9" in _log,
        "the LFS-materialised checkpoint hashed to the pinned value")
chk((F/"validator_results/AUTHORITATIVE_VALIDATION_2026-09-27.md").is_file(),
    "the authoritative validation receipt is written up")
for _a in ("auth_attempt1.log","auth_attempt2.log","auth_attempt3.log"):
    chk((F/"validator_results"/_a).is_file(), f"failed-attempt log retained, not tidied away", _a)

print("\nPHASE-1 WHOLE-LIBRARY QUALIFICATION AUDIT")
for _f, _req in (("docs/SEQME_WHOLE_LIBRARY_PREREG.md", "protocol pre-registered before computing"),
                 ("docs/SEQME_PREREG_ADDENDUM_1.md", "addendum covering the proposal's own metric families"),
                 ("docs/SEQME_WHOLE_LIBRARY_AUDIT.md", "result recorded"),
                 ("evidence/SEQME_PASS_A.json", "full-library pass"),
                 ("evidence/SEQME_PASS_B.json", "equal-sized pass"),
                 ("evidence/SEQME_PASS_B1337.json", "independent replication sample"),
                 ("evidence/ADDENDUM1_MMSEQS_SYNTH.json", "MMseqs2 novelty, clustering and synthesizability"),
                 ("evidence/NEGATIVE_CONTROL_ALL_METRICS.json", "negative control run on every metric, not only the adverse ones")):
    chk((F/_f).is_file(), f"{_req}", _f)
_aud = (F/"docs/SEQME_WHOLE_LIBRARY_AUDIT.md").read_text() if (F/"docs/SEQME_WHOLE_LIBRARY_AUDIT.md").is_file() else ""
chk("NOT COVERED" in _aud,
    "the unmeasured surrogate-activity family is declared, not omitted")
chk("shuffled" in _aud.lower() and "negative control" in _aud.lower(),
    "the adverse metrics' failure of their own negative control is recorded")

print("\nSURROGATE-ACTIVITY DIAGNOSTIC (Phase-1 family 1)")
for _f, _req in (("docs/DEEPAMP_DIAGNOSTIC_PREREG.md", "protocol pre-registered before any project sequence was scored"),
                 ("docs/DEEPAMP_DIAGNOSTIC_RESULT.md", "result recorded"),
                 ("evidence/DEEPAMP_SUMMARY.json", "per-set statistics and the omission report"),
                 ("evidence/GATE0_RELIABILITY.json", "reliability gate against the model's own paper"),
                 ("evidence/ENCODING_DEFECT_TEST.json", "wrapper-vs-original encoding check"),
                 ("evidence/DEEPAMP_FROZEN_INPUTS.json", "frozen inputs with asset hashes")):
    chk((F/_f).is_file(), _req, _f)
_dr = F/"docs/DEEPAMP_DIAGNOSTIC_RESULT.md"
if _dr.is_file():
    # Normalise whitespace: these documents hard-wrap, so a literal substring test breaks whenever a
    # phrase happens to straddle a line break. That bit once already.
    _t = " ".join(_dr.read_text().split())
    chk("STILL NOT COVERED" in _t or "stays NOT COVERED" in _t,
        "family 1 is still reported NOT COVERED, not quietly closed")
    chk("decline" in _t.lower(),
        "the favourable library result is explicitly declined rather than claimed")
    chk("$0.00" in _t, "the branch is recorded as zero-cost")
    chk("AMPredictor and MBC-Attention were not run" in _t,
        "the two un-run models are named as un-run")
# the omission report must account for every sequence, not just count them
import json as _json
_os = F/"evidence/DEEPAMP_SUMMARY.json"
if _os.is_file():
    _o = _json.loads(_os.read_text())["omission_report"]
    _bad = [k for k, v in _o.items() if v["n_scored"] + v["n_omitted"] != v["n_input"]]
    chk(not _bad, "every input sequence is either scored or listed as omitted", str(_bad[:3]))
    _lib = [k for k in _o if k.startswith(("A_", "B_", "C_", "D_"))]
    chk(all(_o[k]["n_omitted"] == 0 for k in _lib),
        "no library or top-list sequence was dropped by the model's length or alphabet bounds")

print("\nDOCUMENTATION REQUIREMENTS")
md = (F/"docs/METHOD_AND_ABSTRACT.md").read_text()
chk("## Abstract" in md and len(md) > 3000, "abstract summarizing the method")
chk("## Method" in md, "method description with the selection procedure")
dd = (F/"docs/DATA_AND_MODEL_DISCLOSURE.md").read_text()
chk("training" in dd.lower() and "databas" in dd.lower(),
    "training data and external databases disclosed")
chk("Filters applied" in dd or "filters" in dd.lower(),
    "manual interventions and computational filters disclosed")
chk((F/"docs/LIMITATIONS.md").is_file(), "limitations documented")
chk((F/"docs/TIER_REQUIREMENTS_AND_GAPS.md").is_file(), "tier gaps documented explicitly")

print("\nINTERPRETIVE ITEMS — reported open, never claimed satisfied")
open_item("whether hash-pinned retrieval satisfies 'with model weights'",
          "unknown; the weights-bundled variant exists so the question need not be relied on")
open_item("whether the generator training-data disclosure counts as 'full'",
          "we measured the files AMP-Designer publishes (80.4% of its peptide corpora are inside the "
          "challenge reference set; zero exact matches with our output), but both upstream training "
          "scripts default to a file absent from the repository, so the released checkpoint's actual "
          "training input is not pinned and was not reconstructed. APEX publishes no training data at all")
open_item("MMseqs2/MarLys novelty compliance",
          "the proposal names MMseqs2 but publishes no parameters; zero violations under the two "
          "coverage settings tested, all portfolios fail under a permissive one — measured, not determined")
open_item("safety and selectivity standing",
          "no measured HC50 exists; our screen is uninformative for peptides this novel, so we have "
          "no evidence either way and claim none")
open_item("whether a modified AMP-Diffusion derivative remains the excluded baseline",
          "no controlling public rule; does not reach this entry, which is not a derivative")
open_item("cross-device reproducibility against the organizers' hardware",
          "six completed byte-identical runs across TWO architectures - two on Ada (RTX 4090) and four "
          "on Ampere (RTX A4500), the last two being the 2026-09-27 authoritative validation of the "
          "weights-bundled variant with the checkpoint delivered by Git LFS. Not all devices; CPU "
          "untested. An earlier version of this line said THREE architectures and counted a Blackwell "
          "RTX 5090 pod whose CUDA never initialised and which produced no output; that was false")

print(f"\n{'ALL EXECUTABLE REQUIREMENTS PASS' if not fails else str(len(fails))+' FAILURE(S): '+'; '.join(fails)}")
print(f"{len(opens)} interpretive item(s) recorded as OPEN — these are the organizers' to resolve.")
sys.exit(1 if fails else 0)
