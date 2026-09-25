"""Independent public-fixture encoding, transform, serialization and batch checks."""
import ast,csv,importlib.util,json,sys
from pathlib import Path
import numpy as np,pandas as pd,torch
ROOT=Path(__file__).resolve().parents[1];OUT=Path(sys.argv[1])
torch.set_num_threads(json.loads((ROOT/'runtime_config.json').read_text())['threads']);torch.set_num_interop_threads(1);torch.manual_seed(0)
spec=importlib.util.spec_from_file_location('scorer',ROOT/'score_batch.py');scorer=importlib.util.module_from_spec(spec);spec.loader.exec_module(scorer)
_,config=scorer.verify_runtime()
rows=list(csv.DictReader((ROOT/'tests/public_fixture.csv').open()));seqs=[r['sequence'] for r in rows]
arr=np.load(OUT/'prediction_arrays.npz');enc=np.load(OUT/'ania_encoded.npy')
# APEX token encoding assembled without the helper being checked.
vocab={a:i+3 for i,a in enumerate('ACDEFGHIKLMNPQRSTVWY')}
x=np.zeros((len(seqs),52),dtype=np.int64)
for i,s in enumerate(seqs):x[i,:len(s)+2]=[1]+[vocab[a] for a in s]+[2]
scorer.import_file('APEX_models',ROOT/'assets/apex/APEX_models.py')
direct=[];batch_deltas=[]
for item in config['apex_weights']:
 model=torch.load(ROOT/item['path'],map_location='cpu',weights_only=False).cpu().eval()
 with torch.inference_mode():
  pred=np.concatenate([model(t).numpy() for t in torch.tensor(x).split(32)])
  small=np.concatenate([model(t).numpy() for t in torch.tensor(x).split(8)])
 direct.append(np.power(10.0,6-pred));batch_deltas.append(float(np.max(np.abs(pred-small))))
assert np.array_equal(np.stack(direct),arr['apex_base_mic_uM'])
assert np.array_equal(np.mean(direct,axis=0),arr['apex_ensemble_mic_uM'])
assert max(batch_deltas)<=1e-4
# ANIA training preprocessing independently reconstructs every saved feature channel.
coords=pd.read_csv(OUT/'cgr_coordinates.csv')
class C:
 def __init__(self,d):self.d=d
 def rx2(self,k):return self.d[k].to_numpy()
objs=[C(coords[coords['index']==i]) for i in range(len(seqs))]
env={'np':np,'pd':pd}
tree=ast.parse((ROOT/'assets/ania/src/features/cgr_encoding.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'map_kmers','compute_props'}],type_ignores=[]),'author_training_encoder','exec'),env)
kmers=env['map_kmers'](seqs,objs,16)
props=pd.read_csv(ROOT/'assets/ania/configs/AAindex_properties.csv',index_col='AminoAcid')
for channel,prop in enumerate(config['ania_properties'],1):
 maps=env['compute_props'](kmers,props,prop);expected=np.zeros((len(seqs),16,16),np.float32)
 for i,m in enumerate(maps):
  for (y,x),v in m.items():expected[i,y,x]=v
 assert np.array_equal(expected,enc[:,channel])
fcgr=np.loadtxt(OUT/'fcgr_native.csv',delimiter=',',ndmin=2)
assert np.array_equal(fcgr.reshape(len(seqs),16,16).astype(np.float32),enc[:,0])
assert np.array_equal(fcgr.sum(axis=1),list(map(len,seqs)))
ania_deltas=[]
for j,item in enumerate(config['ania_weights']):
 model=scorer.load_ania(ROOT/item['path'],torch)
 with torch.inference_mode():
  small=np.concatenate([model(t).numpy().reshape(-1) for t in torch.tensor(enc).split(8)])
 ania_deltas.append(float(np.max(np.abs(small-arr['ania_log10_mic_uM'][:,j]))))
assert max(ania_deltas)<=1e-4
joined=list(csv.DictReader((OUT/'scores.csv').open()))
assert [(r['candidate_id'],r['sequence']) for r in joined]==[(r['candidate_id'],r['sequence']) for r in rows]
long=list(csv.DictReader((OUT/'apex_base_long.csv').open()))
replayed=np.array([float(r['predicted_mic_uM']) for r in long],np.float32).reshape(8,len(seqs),11)
assert np.array_equal(replayed,arr['apex_base_mic_uM'])
result={'status':'PASS','public_fixture_count':len(seqs),'APEX_base_exact_reference':True,
 'APEX_mean_exact_reconstruction':True,'ANIA_training_inference_features_exact':True,
 'APEX_cross_batch_log10_max_delta':max(batch_deltas),'ANIA_cross_batch_log10_max_delta':max(ania_deltas),
 'strict_sequence_joins':True,'serialized_base_values_exact':True,'torch_version':str(torch.__version__),
 'cross_torch_version_equivalence':'NOT_TESTED; no claim of bit identity with prior Torch 2.2.2'}
scorer.write_json(OUT/'INDEPENDENT_FIXTURE_VALIDATION.json',result);print(json.dumps(result,indent=2))
