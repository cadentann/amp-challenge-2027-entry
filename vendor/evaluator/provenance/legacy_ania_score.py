import os
os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
import ast,csv,json,hashlib,time,sys,subprocess,pickle,types,collections,zipfile,pickletools,platform
import numpy as np,pandas as pd,torch
ROOT=Path(__file__).resolve().parent;R=ROOT/'results';SOURCE=ROOT/'sources/ania'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protocol=json.loads((ROOT/'protocol.json').read_text());assert sha(ROOT/'protocol.json')==(ROOT/'protocol.sha256').read_text().split()[0]
for p,h in protocol['sha256'].items():assert sha(ROOT/p)==h,p
assert not (R/'scoring_run.json').exists()
started=time.monotonic();torch.set_num_threads(4);torch.manual_seed(0)
seqtable=pd.read_csv(ROOT/'inputs/scoring_sequences.csv');seqs=list(seqtable.sequence)
subprocess.run(['Rscript',str(ROOT/'encode_native.R'),str(ROOT)],check=True,timeout=120)
fcgr=np.loadtxt(R/'fcgr_native.csv',delimiter=',');coords=pd.read_csv(R/'cgr_coordinates.csv')
assert fcgr.shape==(610,256);assert np.array_equal(fcgr.sum(axis=1),np.array(list(map(len,seqs))))
# Execute unchanged function ASTs from pinned author's source; R handles all CGR coordinates/counts.
astsrc=ast.parse((SOURCE/'src/inference/fasta_encoder.py').read_text())
names={'map_kmers_to_pixels','compute_property_maps'};env={'np':np,'pd':pd}
exec(compile(ast.Module(body=[n for n in astsrc.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(SOURCE/'src/inference/fasta_encoder.py'),'exec'),env)
class CGRResult:
 def __init__(self,d): self.d=d
 def rx2(self,n):return self.d[n].to_numpy()
cgr=[CGRResult(coords[coords['index']==i]) for i in range(len(seqs))]
kmers=env['map_kmers_to_pixels'](seqs,cgr,16)
props=pd.read_csv(SOURCE/'configs/AAindex_properties.csv',index_col='AminoAcid')
property_ids=['ARGP820101','CHAM830107','FAUJ880103','GRAR740102','JANJ780101','KYTJ820101','NAKH920104','ROSM880102','WERD780104','ZIMJ680101']
channels=[fcgr.reshape(-1,16,16)]
for prop in property_ids:
 maps=env['compute_property_maps'](kmers,props,prop);mat=np.zeros((len(seqs),16,16))
 for i,m in enumerate(maps):
  for (y,x),v in m.items():assert 0<=x<16 and 0<=y<16;mat[i,y,x]=v
 channels.append(mat)
X=np.stack(channels,axis=1).astype(np.float32);assert X.shape==(610,11,16,16) and np.isfinite(X).all();np.save(R/'encoded_features.npy',X)
sys.path.insert(0,str(SOURCE));from src.models.deep_learning.ANIA import ANIA
allowed={('collections','OrderedDict'):collections.OrderedDict,('torch','FloatStorage'):torch.FloatStorage,('torch','LongStorage'):torch.LongStorage,('torch._utils','_rebuild_tensor_v2'):torch._utils._rebuild_tensor_v2,('torch.torch_version','TorchVersion'):str}
class RestrictedUnpickler(pickle.Unpickler):
 def find_class(self,module,name):
  if (module,name) not in allowed:raise pickle.UnpicklingError(f'Forbidden global {module}.{name}')
  return allowed[module,name]
pm=types.ModuleType('restricted_ania_pickle');pm.Unpickler=RestrictedUnpickler;pm.load=pickle.load;pm.loads=pickle.loads;pm.dump=pickle.dump;pm.dumps=pickle.dumps
meta={};allpred=seqtable.copy()
for species in ['EC','PA','SA']:
 p=SOURCE/f'weights/ANIA_{species}.pt';z=zipfile.ZipFile(p);blob=z.read(next(n for n in z.namelist() if n.endswith('/data.pkl')))
 globals_=sorted({arg for op,arg,pos in pickletools.genops(blob) if op.name=='GLOBAL'});assert set(globals_)=={' '.join(k) for k in allowed}
 ck=torch.load(p,map_location='cpu',pickle_module=pm);hp=ck['hyperparams']
 oc=lambda i:sum(hp[f'inception{i}_{x}_channels'] for x in ['branch1x1','branch3x3','branch5x5','branch_pool'])
 model=ANIA(in_channels=11,inception1_out_channels=oc(1),inception2_out_channels=oc(2),**{k:v for k,v in hp.items() if k in ANIA.__init__.__code__.co_varnames});model.load_state_dict(ck['state_dict'],strict=True);model.cpu().eval()
 with torch.inference_mode():
  predictions=np.concatenate([model(b).numpy().reshape(-1) for b in torch.tensor(X).split(32)])
  repeated=model(torch.tensor(X[:8])).numpy().reshape(-1)
 print(species, 'batch32_vs_batch8_max_diff', float(abs(predictions[:8]-repeated).max()), flush=True)
 with torch.inference_mode(): samebatch=model(torch.tensor(X[:32])).numpy().reshape(-1)
 assert np.array_equal(predictions[:32],samebatch), 'same-batch repeat must be bit-identical'
 assert np.allclose(predictions[:8],repeated,atol=1e-4,rtol=1e-4), 'batch numerical discrepancy > tolerance'
 assert predictions.shape==(610,) and np.isfinite(predictions).all()
 allpred[f'ANIA_{species}_log10_MIC_uM']=predictions;allpred[f'ANIA_{species}_MIC_uM']=10.0**predictions
 meta[species]={'checkpoint_sha256':sha(p),'hyperparams':hp,'checkpoint_keys':list(ck),'version_metadata':{k:str(v) for k,v in ck.items() if k not in ['hyperparams','state_dict']},'pickle_globals':globals_,'repeat_max_abs_diff':float(abs(predictions[:8]-repeated).max()),'range_log10_MIC_uM':[float(predictions.min()),float(predictions.max())]}
 assert time.monotonic()-started<protocol['max_inference_seconds']
allpred.to_csv(R/'ania_predictions.csv',index=False)
run={'completed_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-started,'device':'CPU','threads':4,'cloud_spend_usd':0,'sequence_count':610,'reserve_scored':0,'protocol_sha256':sha(ROOT/'protocol.json'),'environment':{'python':sys.version,'torch':torch.__version__,'numpy':np.__version__,'pandas':pd.__version__},'models':meta,'output_sha256':{p.name:sha(p) for p in R.iterdir() if p.is_file()},'script_sha256':{n:sha(ROOT/n) for n in ['encode_native.R','score.py']}}
(R/'scoring_run.json').write_text(json.dumps(run,indent=2)+'\n');print(json.dumps({'elapsed_seconds':run['elapsed_seconds'],'models':meta},indent=2))
