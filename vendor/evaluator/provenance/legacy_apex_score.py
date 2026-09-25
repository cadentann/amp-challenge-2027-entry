#!/usr/bin/env python3
"""Immutable, output-isolated CPU APEX inference for the frozen Pandi panel."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
import csv, hashlib, json, platform, sys, time
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'results'
WS=Path('/Users/cadentan/Documents/Codex/2026-09-21/files-pasted-by-the-user-amp')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'scoring_run.json').exists(), 'immutable inference already completed'
protocol=json.loads((ROOT/'protocol.json').read_text())
assert sha(ROOT/'protocol.json')==(ROOT/'protocol.sha256').read_text().split()[0]
for name,digest in protocol['frozen_files'].items(): assert sha(ROOT/name)==digest,name
assert json.loads((ROOT/'support_gate.json').read_text())['status']=='PASS'
assert json.loads((ROOT/'validation_preinference.json').read_text())['status']=='PASS'
sys.path.insert(0,str(ROOT/'inputs/apex_code'))
import numpy as np
import torch
from utils import make_vocab,onehot_encoding
assert torch.__version__=='2.2.2' and np.__version__=='1.26.4'
torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(0)
rows=list(csv.DictReader((ROOT/'inputs/initial22.csv').open()));seqs=[r['sequence'] for r in rows]
assert len(seqs)==22==len(set(seqs)) and all(8<=len(s)<=50 for s in seqs)
panel=protocol['apex_heads'];weights=protocol['weights']
vocab,_=make_vocab();encoded=torch.LongTensor(onehot_encoding(np.array(seqs),52,vocab))
started=time.monotonic();base=[];arrays=[]
for m,entry in enumerate(weights):
    p=WS/'work/stage2_measured/apex_cpu/APEX_pathogen_models'/entry['name']
    assert sha(p)==entry['sha256'] and p.stat().st_size==entry['bytes']
    model=torch.load(p,map_location='cpu',weights_only=False).cpu().eval()
    assert all(x.device.type=='cpu' for x in model.parameters())
    with torch.inference_mode(): values=np.concatenate([10**(6-model(b).numpy()) for b in encoded.split(32)],axis=0)
    assert values.shape==(22,11) and np.isfinite(values).all() and (values>0).all()
    arrays.append(values)
    for r,v in zip(rows,values):
        for h,x in zip(panel,v): base.append({'model_index':m,'model':entry['name'],'amp_id':int(r['amp_id']),
          'sequence_sha256':r['sequence_sha256'],'head':h,'predicted_mic_uM':float(x)})
    del model
mean=np.mean(np.stack(arrays),axis=0)
ensemble=[]
for r,v in zip(rows,mean):
    for h,x in zip(panel,v): ensemble.append({'amp_id':int(r['amp_id']),'sequence_sha256':r['sequence_sha256'],
                                               'head':h,'ensemble_mic_uM':float(x)})
def write(name,rs):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
write('apex_base_long.csv',base);write('apex_ensemble_long.csv',ensemble)
# Exact reconstruction after CSV serialization, before outcomes are joined.
b=list(csv.DictReader((OUT/'apex_base_long.csv').open()));e=list(csv.DictReader((OUT/'apex_ensemble_long.csv').open()))
replayed=np.array([float(r['predicted_mic_uM']) for r in b],dtype=np.float32).reshape(8,22,11).mean(axis=0)
assert np.array_equal(np.array([float(r['ensemble_mic_uM']) for r in e],dtype=np.float32).reshape(22,11),replayed)
elapsed=time.monotonic()-started
run={'completed_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
 'device':'cpu','torch_threads':torch.get_num_threads(),'torch_interop_threads':torch.get_num_interop_threads(),
 'batch_size':32,'seed':0,'models':8,'sequences':22,'heads':11,'base_value_count':len(base),
 'ensemble_value_count':len(ensemble),'model_inference_passes':8,'elapsed_seconds':elapsed,
 'torch_version':torch.__version__,'numpy_version':np.__version__,'python_version':platform.python_version(),
 'protocol_sha256':sha(ROOT/'protocol.json'),'cloud_spend_usd':0,
 'outputs':{n:sha(OUT/n) for n in ['apex_base_long.csv','apex_ensemble_long.csv']},
 'checks':'All frozen hashes verified; 1936 base values and 242 ensemble means serialized; every serialized mean reconstructed exactly.'}
(OUT/'scoring_run.json').write_text(json.dumps(run,indent=2)+'\n')
print(json.dumps(run,indent=2))
