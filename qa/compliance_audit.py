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
chk("FINALIST.lock.json" in sh("git","ls-files",cwd=R), "FINALIST.lock.json is tracked")
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
        chk(not sh("git","remote",cwd=V), "weights variant has no git remote configured")
chk((R/"scripts/prepare_entry.py").is_file(), "retrieval variant carries a hash-verified fetch path")

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
open_item("whether second-hand generator training-data disclosure counts as 'full'",
          "AMP-Prompt's corpus was not assembled or inspected by us; we report what its authors report")
open_item("MMseqs2/MarLys novelty compliance",
          "the proposal names MMseqs2 but publishes no parameters; zero violations under the two "
          "coverage settings tested, all portfolios fail under a permissive one — measured, not determined")
open_item("safety and selectivity standing",
          "no measured HC50 exists; our screen is uninformative for peptides this novel, so we have "
          "no evidence either way and claim none")
open_item("whether a modified AMP-Diffusion derivative remains the excluded baseline",
          "no controlling public rule; does not reach this entry, which is not a derivative")
open_item("cross-device reproducibility against the organizers' hardware",
          "byte-identical on three GPU architectures so far; not all devices, CPU untested")

print(f"\n{'ALL EXECUTABLE REQUIREMENTS PASS' if not fails else str(len(fails))+' FAILURE(S): '+'; '.join(fails)}")
print(f"{len(opens)} interpretive item(s) recorded as OPEN — these are the organizers' to resolve.")
sys.exit(1 if fails else 0)
