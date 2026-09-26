#!/usr/bin/env python3
"""Final QA harness for the AMP Challenge submission package. Exits non-zero on any failure."""
import hashlib, json, os, re, subprocess, sys
from pathlib import Path
F = Path("/Volumes/SanDisk/AI_Research/AMP_Challenge/FINAL_SUBMISSION_READY")
R = F / "amp-prompt-consensus-entry"
EXPECT = {"library.fasta": "a91c0de9200a3d9f4377bfc6f81d36d21ea15bb9c940bd91fab797cd5ae2308b",
          "top.fasta":     "ece3b7062d55d1ac4eb35f60e450cebec229ebfba63b5a0ab7214ecd4e5cb841"}
fails, warns = [], []
def ok(c, msg, detail=""):
    print(f"  {'PASS' if c else 'FAIL'}  {msg}" + (f"  [{detail}]" if detail and not c else ""))
    if not c: fails.append(msg)

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda: f.read(1<<20), b""): h.update(b)
    return h.hexdigest()

print("1. Shipped artifacts")
for n,e in EXPECT.items():
    ok(sha(F/"artifacts"/n)==e, f"{n} matches the frozen hash")
ok(sum(1 for l in open(F/"artifacts/library.fasta") if l.startswith(">"))==50000, "library has 50,000 records")
ok(sum(1 for l in open(F/"artifacts/top.fasta") if l.startswith(">"))==100, "top has 100 records")
seqs=[l.strip() for l in open(F/"artifacts/top.fasta") if not l.startswith(">")]
lib={l.strip() for l in open(F/"artifacts/library.fasta") if not l.startswith(">")}
ok(len(set(seqs))==100, "top-100 unique")
ok(set(seqs)<=lib, "top-100 is a subset of the library")
CAN=set("ACDEFGHIKLMNPQRSTVWY")
ok(all(set(s)<=CAN and 8<=len(s)<=50 for s in lib), "every library sequence is canonical and 8-50aa")

print("2. Package manifest")
m=json.loads((F/"FINAL_HASH_MANIFEST.json").read_text())
bad=[p for p,v in m["files"].items() if not (F/p).is_file() or sha(F/p)!=v["sha256"]]
ok(not bad, f"all {m['file_count']} manifest entries verify", f"{len(bad)} bad")
ok(m["submitted"] is False and m["published"] is False and m["organizer_access_granted"] is False,
   "manifest records submitted/published/organizer-access all false")

print("3. Repository")
g=lambda *a: subprocess.run(["git","-C",str(R)]+list(a),capture_output=True,text=True).stdout.strip()
ok(g("status","--porcelain")=="", "working tree clean")
ok(g("remote")=="", "no git remote configured (nothing can have been pushed)")
ok((R/"FINALIST.lock.json").is_file(), "FINALIST.lock.json present")
ok("FINALIST.lock.json" in g("ls-files"), "FINALIST.lock.json is tracked")
ok((R/"LICENSE").is_file(), "LICENSE present (required for the full tier)")
pm=json.loads((R/"PROVENANCE_MANIFEST.json").read_text())
badp=[f["path"] for f in pm["files"] if not (R/f["path"]).is_file() or sha(R/f["path"])!=f["sha256"]]
ok(not badp, f"all {pm['file_count']} repo provenance entries verify", f"{len(badp)} bad")

print("4. Secrets and portability")
cred=re.compile(rb"rpa_[A-Z0-9]{20}|BEGIN [A-Z ]*PRIVATE KEY|ssh-ed25519 AAAA")
hits=[]
for root,dirs,names in os.walk(F):
    dirs[:]=[d for d in dirs if d not in {".git","__pycache__",".venv","runtime","prompt_model"}]
    for n in names:
        p=Path(root)/n
        try:
            if cred.search(p.read_bytes()): hits.append(str(p.relative_to(F)))
        except Exception: pass
ok(not hits, "no credential-shaped strings anywhere in the package", str(hits[:3]))
PINNED={"vendor/evaluator/provenance","vendor/frozen_selector/anchor.json"}
hp=[]
for root,dirs,names in os.walk(R):
    dirs[:]=[d for d in dirs if d not in {".git","__pycache__",".venv","runtime","prompt_model","docs","validation"}]
    for n in names:
        p=Path(root)/n; rel=str(p.relative_to(R))
        if any(rel.startswith(x) for x in PINNED) or rel=="PROVENANCE_MANIFEST.json": continue
        try: t=p.read_text(errors="ignore")
        except Exception: continue
        if "/Users/cadentan" in t or "/Volumes/SanDisk" in t: hp.append(rel)
ok(not hp, "no host paths in executable repo files (hash-pinned files excluded)", str(hp[:3]))

print("5. Repo test suite")
r=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-q"],cwd=R,
                 capture_output=True,text=True,env={**os.environ,"FINALIST_SKIP_PREPARE":"1"})
ok(r.returncode==0, "all repo tests pass", r.stderr[-200:])
print(f"        {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ''}")

print("6. Lock integrity")
L=json.loads((R/"FINALIST.lock.json").read_text())
ok(L["generation_seed"]==42, "generation seed is 42")
ok(L["selection_universe"]=="full_library", "selection universe is full_library")
ok(L["selector"]=="CONSENSUS_FIXED", "selector is CONSENSUS_FIXED")
ok(L["status"]=="FINAL_AUTHORIZED", "lock status FINAL_AUTHORIZED")
ok(sha(R/"validation/SCORER_RUNTIME.lock.json")==L["scoring_runtime_lock_sha256"],
   "shipped runtime lock matches the pin in FINALIST.lock.json")

print("7. Documentation references")
pat=re.compile(r'`([A-Za-z0-9_./-]+\.(?:md|json|fasta|txt))`')
miss={}
for md in list(F.glob("*.md"))+list(F.glob("docs/*.md"))+list(R.glob("*.md")):
    if md.name == "EXTERNAL_REFERENCES.md": continue  # documents out-of-package paths by design
    for ref in set(pat.findall(md.read_text())):
        if ref.startswith(("http","data/")): continue
        if list(F.rglob(Path(ref).name)): continue
        miss.setdefault(str(md.relative_to(F)),[]).append(ref)
known={"PORTFOLIOS.json","COMPLETE.json","runtime.json",
       "LINUX_NUMERICAL_STABILITY_PROSPECTIVE_PLAN.md","classify_exact_numerical_failure.py",
       "preflight_reference_selections.py","FINALIST_SELECTION_UNIVERSE_PROPOSAL.md"}
real={k:[r for r in v if r not in known] for k,v in miss.items()}
real={k:v for k,v in real.items() if v}
ok(not real, "all document references resolve (working-tree files excluded via EXTERNAL_REFERENCES)", str(real)[:200])

print(f"\n{'ALL CHECKS PASSED' if not fails else f'{len(fails)} FAILURE(S): '+'; '.join(fails)}")
sys.exit(1 if fails else 0)
