#!/usr/bin/env python3
"""Pinned APEX+ANIA CPU inference. Requires a hash-bound parent input authorization."""
from __future__ import annotations
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import argparse, ast, collections, csv, hashlib, importlib.util, io, json, pickle, platform
import subprocess, sys, time, types
from pathlib import Path
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent
PARENT_SHA256 = '82c21d6f5fcfc4bb9282a2c380fa77088243ae71606333faba60e8b59a49099c'
ALPHABET = set('ACDEFGHIKLMNPQRSTVWY')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text())

def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')

def verify_runtime():
    manifest = read_json(ROOT/'RUNTIME_MANIFEST.json')
    assert manifest['parent_protocol_sha256'] == PARENT_SHA256
    assert sha(ROOT/'provenance/PARENT_FREEZE.md') == PARENT_SHA256
    for item in manifest['files']:
        p = ROOT/item['path']
        assert p.is_file() and p.stat().st_size == item['bytes'], str(p)
        assert sha(p) == item['sha256'], f'Changed runtime asset: {p}'
    config = read_json(ROOT/'runtime_config.json')
    assert len(config['apex_weights']) == 8 and len(config['ania_weights']) == 3
    return manifest, config

def load_input(path, authorization, purpose):
    """Only read a parent's explicitly named and hashed pool; never discover input files."""
    path = Path(path).resolve()
    auth = read_json(authorization)
    assert auth['parent_protocol_sha256'] == PARENT_SHA256
    assert auth['parent_go'] is True and auth['purpose'] == purpose
    assert purpose in ('public_fixture', 'qualified_pool')
    assert Path(auth['input_path']).resolve() == path
    payload = path.read_bytes()
    assert hashlib.sha256(payload).hexdigest() == auth['input_sha256'], 'Input differs from authorized bytes'
    assert auth.get('protected_reserve', None) is False
    assert not any(x in str(path).lower() for x in ('unexposed_candidate', '/reserve/', 'protected_reserve'))
    reader = csv.DictReader(io.StringIO(payload.decode('utf-8'), newline=''))
    assert {'candidate_id', 'sequence'} <= set(reader.fieldnames or [])
    rows = list(reader)
    assert len(rows) == auth['row_count'] and 0 < len(rows) <= 20000
    ids, sequences = set(), []
    for index, row in enumerate(rows):
        sid, s = row['candidate_id'], row['sequence']
        assert sid and sid not in ids, f'Duplicate/empty candidate_id at row {index}'
        assert isinstance(s, str) and 8 <= len(s) <= 50 and set(s) <= ALPHABET
        h = hashlib.sha256(s.encode('ascii')).hexdigest()
        assert not row.get('sequence_sha256') or row['sequence_sha256'] == h
        ids.add(sid)
        row['sequence_sha256'] = h
        row['input_row_index'] = index
        sequences.append(s)
    # Shared sequences across pools are evaluated once, then joined back by exact sequence.
    unique = list(dict.fromkeys(sequences))
    return rows, unique, auth

def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

def encode_ania(seqs, out, np, pd, config):
    (out/'sequences.txt').write_text('\n'.join(seqs) + '\n')
    subprocess.run([config['rscript'], str(ROOT/'encode_native.R'),
                    str(ROOT/'assets/ania'), str(out/'sequences.txt'), str(out)],
                   check=True, timeout=config['encoding_timeout_seconds'],
                   stdout=(out/'r_stdout.txt').open('w'), stderr=(out/'r_stderr.txt').open('w'))
    fcgr = np.loadtxt(out/'fcgr_native.csv', delimiter=',', ndmin=2)
    assert fcgr.shape == (len(seqs),256)
    assert np.array_equal(fcgr.sum(axis=1), np.array(list(map(len, seqs))))
    coords = pd.read_csv(out/'cgr_coordinates.csv')
    assert len(coords) == sum(map(len, seqs))
    astsrc = ast.parse((ROOT/'assets/ania/src/inference/fasta_encoder.py').read_text())
    names = {'map_kmers_to_pixels','compute_property_maps'}
    functions = [n for n in astsrc.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in functions} == names
    env = {'np':np,'pd':pd}
    exec(compile(ast.Module(body=functions,type_ignores=[]),'author_fasta_encoder','exec'), env)
    class CGRResult:
        def __init__(self, d): self.d=d
        def rx2(self, n): return self.d[n].to_numpy()
    cgr = []
    grouped = dict(tuple(coords.groupby('index',sort=False)))
    for i,s in enumerate(seqs):
        c = grouped[i]
        assert len(c) == len(s) and list(c.position) == list(range(len(s)))
        cgr.append(CGRResult(c))
    kmers = env['map_kmers_to_pixels'](seqs,cgr,16)
    props = pd.read_csv(ROOT/'assets/ania/configs/AAindex_properties.csv',index_col='AminoAcid')
    channels = [fcgr.reshape(-1,16,16)]
    for prop in config['ania_properties']:
        maps=env['compute_property_maps'](kmers,props,prop)
        mat=np.zeros((len(seqs),16,16))
        for i,m in enumerate(maps):
            for (y,x),v in m.items():
                assert 0<=x<16 and 0<=y<16
                mat[i,y,x]=v
        channels.append(mat)
    X=np.stack(channels,axis=1).astype(np.float32)
    assert X.shape==(len(seqs),11,16,16) and np.isfinite(X).all()
    np.save(out/'ania_encoded.npy',X)
    return X

def load_ania(weight, torch):
    # Same restricted checkpoint loader already used in the accepted prior CPU diagnostic.
    allowed={('collections','OrderedDict'):collections.OrderedDict,
             ('torch','FloatStorage'):torch.FloatStorage,('torch','LongStorage'):torch.LongStorage,
             ('torch._utils','_rebuild_tensor_v2'):torch._utils._rebuild_tensor_v2,
             ('torch.torch_version','TorchVersion'):str}
    class RestrictedUnpickler(pickle.Unpickler):
        def find_class(self,module,name):
            if (module,name) not in allowed:
                raise pickle.UnpicklingError(f'Forbidden checkpoint global {module}.{name}')
            return allowed[module,name]
    pm=types.ModuleType('restricted_ania_pickle')
    pm.Unpickler=RestrictedUnpickler
    pm.load=pickle.load;pm.loads=pickle.loads;pm.dump=pickle.dump;pm.dumps=pickle.dumps
    ck=torch.load(weight,map_location='cpu',pickle_module=pm,weights_only=False)
    module=import_file('frontier_author_ania',ROOT/'assets/ania/src/models/deep_learning/ANIA.py')
    hp=ck['hyperparams']
    oc=lambda i:sum(hp[f'inception{i}_{x}_channels'] for x in ['branch1x1','branch3x3','branch5x5','branch_pool'])
    model=module.ANIA(in_channels=11,inception1_out_channels=oc(1),inception2_out_channels=oc(2),
        **{k:v for k,v in hp.items() if k in module.ANIA.__init__.__code__.co_varnames})
    model.load_state_dict(ck['state_dict'],strict=True)
    return model.cpu().eval()

def write_csv(path, fields, rows):
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def score(input_path, authorization, out, purpose):
    started=time.monotonic()
    manifest, config=verify_runtime()
    rows,seqs,auth=load_input(input_path,authorization,purpose)
    assert auth['runtime_manifest_sha256'] == sha(ROOT/'RUNTIME_MANIFEST.json')
    out=Path(out).resolve()
    out.mkdir(parents=True,exist_ok=False)  # A completed or failed run is never overwritten.
    write_json(out/'STARTED.json', {'purpose':purpose,'authorization_sha256':sha(authorization),
        'input_sha256':sha(input_path),'runtime_manifest_sha256':sha(ROOT/'RUNTIME_MANIFEST.json')})
    try:
        import numpy as np
        import pandas as pd
        import torch
        assert str(torch.__version__)==config['environment']['torch']
        assert np.__version__==config['environment']['numpy']
        assert pd.__version__==config['environment']['pandas']
        torch.set_num_threads(config['threads']);torch.set_num_interop_threads(1)
        torch.manual_seed(config['seed']);torch.use_deterministic_algorithms(True)
        sys.path.insert(0,str(ROOT/'assets/apex'))
        import_file('APEX_models',ROOT/'assets/apex/APEX_models.py')
        helpers=import_file('frontier_apex_utils',ROOT/'assets/apex/utils.py')
        vocab,_=helpers.make_vocab()
        encoded=torch.LongTensor(helpers.onehot_encoding(np.array(seqs),52,vocab))
        batch=config['batch_size']
        apex=[];repeats=[]
        for item in config['apex_weights']:
            weight=ROOT/item['path']
            # Authenticated APEX release stores complete nn.Module objects, not state_dicts.
            model=torch.load(weight,map_location='cpu',weights_only=False).cpu().eval()
            assert all(p.device.type=='cpu' for p in model.parameters())
            with torch.inference_mode():
                raw=np.concatenate([model(b).numpy() for b in encoded.split(batch)],axis=0)
                repeat=model(encoded[:min(batch,len(seqs))]).numpy()
            assert np.array_equal(raw[:len(repeat)],repeat),'APEX same-batch nondeterminism'
            values=10**(6-raw)
            assert values.shape==(len(seqs),11) and np.isfinite(values).all() and (values>0).all()
            apex.append(values);repeats.append({'model':item['name'],'same_batch_exact':True})
            del model
        apex=np.stack(apex).astype(np.float32)
        # Invert each member first, arithmetic mean in the accepted float32 convention.
        apex_mean=apex.mean(axis=0)
        X=encode_ania(seqs,out,np,pd,config)
        ania=[]
        for item in config['ania_weights']:
            model=load_ania(ROOT/item['path'],torch)
            tensor=torch.tensor(X)
            with torch.inference_mode():
                values=np.concatenate([model(b).numpy().reshape(-1) for b in tensor.split(batch)])
                repeat=model(tensor[:min(batch,len(seqs))]).numpy().reshape(-1)
            assert np.array_equal(values[:len(repeat)],repeat),'ANIA same-batch nondeterminism'
            assert values.shape==(len(seqs),) and np.isfinite(values).all()
            ania.append(values);repeats.append({'model':item['name'],'same_batch_exact':True})
            del model
        ania=np.stack(ania).T
        assert np.isfinite(10.0**ania).all() and (10.0**ania>0).all()
        np.savez(out/'prediction_arrays.npz',apex_base_mic_uM=apex,
                 apex_ensemble_mic_uM=apex_mean,ania_log10_mic_uM=ania)
        hashes=[hashlib.sha256(s.encode('ascii')).hexdigest() for s in seqs]
        write_csv(out/'scored_sequences.csv',['sequence_sha256','sequence'],
                  ({'sequence_sha256':h,'sequence':s} for h,s in zip(hashes,seqs)))
        write_csv(out/'apex_base_long.csv',['sequence_sha256','model_index','model','head','predicted_mic_uM'],
            ({'sequence_sha256':h,'model_index':m,'model':config['apex_weights'][m]['name'],
              'head':head,'predicted_mic_uM':float(apex[m,i,j])}
             for m in range(8) for i,h in enumerate(hashes) for j,head in enumerate(config['apex_heads'])))
        score_fields=[f'APEX_{h}_MIC_uM' for h in config['apex_head_codes']]+[
            f'ANIA_{s}_log10_MIC_uM' for s in ['EC','PA','SA']]
        seq_to_index={s:i for i,s in enumerate(seqs)}
        joined=[]
        for row in rows:
            i=seq_to_index[row['sequence']]
            joined.append({'candidate_id':row['candidate_id'],'input_row_index':row['input_row_index'],
                'sequence_sha256':hashes[i],'sequence':row['sequence'],
                **dict(zip(score_fields,map(float,list(apex_mean[i])+list(ania[i]))))})
        write_csv(out/'scores.csv',['candidate_id','input_row_index','sequence_sha256','sequence']+score_fields,joined)
        # Verify serialization and exact joins independently of DataFrame index ordering.
        with (out/'scores.csv').open(newline='') as f: recovered=list(csv.DictReader(f))
        assert len(recovered)==len(rows)
        for before,after in zip(rows,recovered):
            assert before['candidate_id']==after['candidate_id'] and before['sequence']==after['sequence']
            assert before['sequence_sha256']==after['sequence_sha256']
        reconstructed=np.load(out/'prediction_arrays.npz')
        assert np.array_equal(reconstructed['apex_base_mic_uM'].mean(axis=0),reconstructed['apex_ensemble_mic_uM'])
        assert sha(input_path)==auth['input_sha256'], 'Authorized input changed during scoring'
        run={'status':'COMPLETE','purpose':purpose,'input_rows':len(rows),'unique_sequences':len(seqs),
             'parent_protocol_sha256':PARENT_SHA256,'runtime_manifest_sha256':sha(ROOT/'RUNTIME_MANIFEST.json'),
             'authorization':auth,'input_sha256':sha(input_path),'seed':config['seed'],'batch_size':batch,
             'device':'cpu','threads':torch.get_num_threads(),'environment':{'python':platform.python_version(),
             'torch':str(torch.__version__),'numpy':np.__version__,'pandas':pd.__version__},
             'elapsed_seconds':time.monotonic()-started,'same_batch_repeats':repeats,
             'all_joins_exact':True,'base_mean_reconstruction_exact':True,'protected_reserve_read':False,
             'outputs':{str(p.relative_to(out)):sha(p) for p in sorted(out.iterdir()) if p.is_file()}}
        write_json(out/'COMPLETE.json',run)
        return run
    except Exception as exc:
        write_json(out/'FAILED.json',{'error_type':type(exc).__name__,'error':str(exc),
                   'elapsed_seconds':time.monotonic()-started})
        raise

def main():
    ap=argparse.ArgumentParser(__doc__)
    ap.add_argument('--input',required=True);ap.add_argument('--authorization',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--purpose',choices=['public_fixture','qualified_pool'],required=True)
    args=ap.parse_args()
    result=score(args.input,args.authorization,args.output,args.purpose)
    print(json.dumps({k:result[k] for k in ['status','purpose','input_rows','unique_sequences','elapsed_seconds']}))

if __name__=='__main__': main()
