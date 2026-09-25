"""Frozen frontier v1 common eligibility/sampling/selection. No model inference."""
from __future__ import annotations
import bisect, hashlib, importlib.util, json, math, statistics, sys
from collections import Counter
from pathlib import Path
from rapidfuzz import fuzz, process

FREEZE_SHA256='82c21d6f5fcfc4bb9282a2c380fa77088243ae71606333faba60e8b59a49099c'
CANONICAL=frozenset('ACDEFGHIKLMNPQRSTVWY')
SEEDS=(1729,2718,3141,4242,5772)
APEX_HEADS=('A. baumannii ATCC 19606','E. coli ATCC 11775','E. coli AIC221','E. coli AIC222','K. pneumoniae ATCC 13883','P. aeruginosa PA01','P. aeruginosa PA14','S. aureus ATCC 12600','S. aureus (ATCC BAA-1556) - MRSA','vancomycin-resistant E. faecalis ATCC 700802','vancomycin-resistant E. faecium ATCC 700221')
ANIA_HEADS=('EC','PA','SA')

def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def file_sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sample_key(seed,s): return digest('frontier-v1|'+str(seed)+'|'+s)
def freeze_check(path):
    if file_sha(path)!=FREEZE_SHA256: raise ValueError('Parent freeze hash mismatch')

def read_fasta(path):
    records=[]; header=None; parts=[]
    for line in Path(path).read_text().splitlines():
        if not line.strip(): continue
        if line.startswith('>'):
            if header is not None: records.append({'header':header,'raw_sequence':''.join(parts),'raw_index':len(records)})
            header=line[1:].strip(); parts=[]
        else:
            if header is None: raise ValueError('FASTA data before first header')
            parts.append(line.strip())
    if header is not None: records.append({'header':header,'raw_sequence':''.join(parts),'raw_index':len(records)})
    return records

def fasta_text(rows): return ''.join(f'>seq{i+1}\n{r["sequence"]}\n' for i,r in enumerate(rows))

def normalize(raw):
    """Common transport normalization only; model adapters own boundary decoding."""
    if not isinstance(raw,str): return None,[]
    compact=''.join(raw.split()); seq=compact.upper(); changes=[]
    if compact!=raw: changes.append('remove_whitespace')
    if seq!=compact: changes.append('uppercase')
    return seq,changes

def lcs_ratio(a,b):
    prev=[0]*(len(b)+1)
    for ca in a:
        cur=[0]
        for j,cb in enumerate(b,1):
            cur.append(prev[j-1]+1 if ca==cb else max(prev[j],cur[-1]))
        prev=cur
    return 2*prev[-1]/(len(a)+len(b)) if a or b else 1.0

def ratio(a,b):
    # RapidFuzz's normalized indel ratio is mathematically Levenshtein.ratio.
    # Package Levenshtein is used where available; boundaries are rational-LCS checked.
    return fuzz.ratio(a,b)/100.0

class ReferenceIndex:
    def __init__(self,references):
        self.references=tuple(sorted(set(references))); self.exact=set(self.references); self.cache={}
        if not self.references: raise ValueError('Empty reference collection')
    def record(self,s):
        if s not in self.cache:
            hit=process.extractOne(s,self.references,scorer=fuzz.ratio)
            value=lcs_ratio(s,hit[0])
            if abs(hit[1]/100-value)>1e-12: raise ValueError('Ratio implementations disagree')
            self.cache[s]={'maximum_ratio':value,'nearest_reference':hit[0],'passes':value<=0.80}
        return self.cache[s]

def eligibility(attempts,ref):
    """Preserves every attempted row; exclusive first failure and all applicable tags."""
    rows=[];seen=set();raw_ids=set()
    for i,a in enumerate(attempts):
        raw_id=a.get('raw_index',i)
        if not isinstance(raw_id,int) or isinstance(raw_id,bool) or raw_id<0 or raw_id in raw_ids: raise ValueError('Invalid/duplicate raw_index')
        raw_ids.add(raw_id)
        s,changes=normalize(a.get('raw_sequence'))
        r=dict(a,raw_index=raw_id,sequence=s,normalizations=changes,library_valid=False,top_eligible=False)
        tags=[]
        if not s or a.get('parse_ok',True) is not True: tags.append('raw_parse')
        if s and (not 8<=len(s)<=50 or set(s)-CANONICAL or a.get('representation_compatible',True) is not True): tags.append('alphabet_length')
        if s in seen: tags.append('duplicate')
        if s: seen.add(s)
        if s in ref.exact: tags.append('library_reference')
        if not tags:
            r['library_valid']=True;r['reference']=ref.record(s)
            if not r['reference']['passes']: tags.append('top_reference')
            else:r['top_eligible']=True
        r['failure_tags']=tags;r['first_failure']=tags[0] if tags else None;rows.append(r)
    return rows

def sample_pool(rows,seed,target=None):
    if target is not None and (not isinstance(target,int) or isinstance(target,bool) or target<1): raise ValueError('target must be positive or null')
    eligible=[dict(r,sample_hash=sample_key(seed,r['sequence'])) for r in rows if r.get('top_eligible')]
    selected=sorted(eligible,key=lambda r:(r['sample_hash'],r['sequence']))[:target]
    return {'schema_version':'frontier-pool-v1','seed':seed,'target':target,'eligible_count':len(eligible),'selected_count':len(selected),'status':'SUPPLY_SHORTFALL' if target and len(selected)<target else 'COMPLETE','rows':selected}

def equal_n_pools(a,b):
    n=min(len(a['rows']),len(b['rows']))
    return dict(a,rows=a['rows'][:n],selected_count=n,equal_n=True),dict(b,rows=b['rows'][:n],selected_count=n,equal_n=True)

def denominator_report(rows,requested_raw,raw_available=True):
    first=Counter(r['first_failure'] for r in rows if r['first_failure'])
    tags=Counter(t for r in rows for t in r['failure_tags'])
    actual=len(rows);e=sum(r['top_eligible'] for r in rows)
    return {'raw_requested':requested_raw if raw_available else None,'raw_completed':actual if raw_available else None,'accepted_input_count':actual,'library_valid':sum(r['library_valid'] for r in rows),'top_eligible':e,'first_failure_counts':dict(first),'all_failure_counts':dict(tags),'top_per_raw_actual':e/actual if raw_available and actual else None,'top_per_raw_requested':e/requested_raw if raw_available and requested_raw else None,'raw_yield_status':'AVAILABLE' if raw_available else 'UNAVAILABLE_CACHED_ACCEPTED_LIBRARY'}

def prepare_cached_control(library,ref,target=1000):
    """Lazy exact top-E hash sampling, without any numeric prediction input.

    Screening only a hash prefix is identical to filtering all E then taking its
    lowest hashes. Full-library E count is deliberately unknown.
    """
    base=[];seen=set()
    for r in library:
        s,changes=normalize(r['raw_sequence'])
        if not s or not 8<=len(s)<=50 or set(s)-CANONICAL or s in seen or s in ref.exact: raise ValueError('Cached accepted library is invalid')
        seen.add(s);base.append(dict(r,sequence=s,normalizations=changes,library_valid=True))
    pools={}
    for seed in SEEDS:
        ordered=sorted(base,key=lambda r:(sample_key(seed,r['sequence']),r['sequence']))
        chosen=[];scanned=0
        for r in ordered:
            scanned+=1;rr=ref.record(r['sequence'])
            if rr['passes']:
                chosen.append(dict(r,reference=rr,top_eligible=True,sample_hash=sample_key(seed,r['sequence']),first_failure=None,failure_tags=[]))
            if len(chosen)==target: break
        pools[str(seed)]={'schema_version':'frontier-pool-v1','seed':seed,'target':target,'selected_count':len(chosen),'eligible_count':None,'eligible_count_status':'UNSCANNED_LIBRARY_REMAINDER','hash_prefix_examined':scanned,'accepted_library_size':len(base),'raw_requested':None,'raw_completed':None,'raw_yield_status':'UNAVAILABLE_CACHED_ACCEPTED_LIBRARY','control_generator_seed_count':1,'status':'COMPLETE' if len(chosen)==target else 'SUPPLY_SHORTFALL','rows':chosen}
    return pools

def valid_vector(values,n,positive=False):
    return isinstance(values,(tuple,list)) and len(values)==n and all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) and (not positive or x>0) for x in values)

def score_features(apex,ania):
    f={'apex_complete':valid_vector(apex,11,True),'ania_complete':valid_vector(ania,3),'safety_status':'UNKNOWN','selectivity':None}
    if f['apex_complete']:
        logs=[math.log2(v) for v in apex]
        f.update(apex_mean=statistics.mean(apex),apex_log2=statistics.mean(logs),apex_q90=sorted(apex)[math.ceil(.9*len(apex))-1],apex_median=statistics.median(apex),apex_gn_log10=statistics.mean(math.log10(v) for v in apex[:7]),apex_gp_log10=statistics.mean(math.log10(v) for v in apex[7:]),apex_species_worst_um={'EC':max(apex[1:4]),'PA':max(apex[5:7]),'SA':max(apex[7:9])})
        for t in (8,16,32):
            for label,ids in [('all',range(11)),('gn',range(7)),('gp',range(7,11)),('mdr',(3,8,9,10))]:
                vals=[apex[i] for i in ids];f[f'b_{label}_{t}']=sum(v<=t for v in vals)/len(vals)
    if f['ania_complete']:
        f.update(ania_log2=statistics.mean(ania)*math.log2(10),ania_ec_log10=ania[0],ania_pa_log10=ania[1],ania_sa_log10=ania[2],ania_ecpa_log10=statistics.mean(ania[:2]))
    return f

def join_scores(pool,score_rows,apex_heads=APEX_HEADS,ania_heads=ANIA_HEADS):
    if tuple(apex_heads)!=APEX_HEADS or tuple(ania_heads)!=ANIA_HEADS: raise ValueError('Score header order mismatch')
    index={}
    for r in score_rows:
        s=r['sequence']
        if s in index: raise ValueError('Duplicate prediction sequence')
        index[s]=r
    expected={r['sequence'] for r in pool['rows']}
    if len(expected)!=len(pool['rows']): raise ValueError('Duplicate pool sequence')
    if set(index)-expected: raise ValueError('Unexpected prediction sequences; subset explicitly before join')
    rows=[]
    for r in pool['rows']:
        s=r['sequence'];p=index.get(s,{})
        rows.append(dict(r,sequence_hash=digest(s),scores=p,features=score_features(p.get('apex_um'),p.get('ania_log10_um')),score_missing_reason=p.get('missing_reason','NO_ROW' if s not in index else None)))
    return rows

def make_anchor(rows):
    seen=set();complete=[]
    for r in rows:
        s=r['sequence']
        if s in seen: continue
        seen.add(s)
        if r['features']['apex_complete'] and r['features']['ania_complete']: complete.append(r)
    if len(complete)<100: return {'status':'UNAVAILABLE_ANCHOR_LT100','count':len(complete)}
    return {'status':'AVAILABLE','count':len(complete),'sequence_hashes':sorted(digest(r['sequence']) for r in complete),'apex':sorted(r['features']['apex_log2'] for r in complete),'ania':sorted(r['features']['ania_log2'] for r in complete)}

def anchor_rank(sorted_anchor,value):
    lo=bisect.bisect_left(sorted_anchor,value);hi=bisect.bisect_right(sorted_anchor,value);n=len(sorted_anchor)
    if not n: raise ValueError('Empty anchor')
    return (n-hi+0.5*(hi-lo))/n

def pareto_fronts(vectors):
    if not vectors:return []
    n=len(vectors);p=len(vectors[0])
    if any(len(v)!=p or not all(math.isfinite(z) for z in v) for v in vectors):raise ValueError('Invalid objective vectors')
    dominates=[[] for _ in vectors];counts=[0]*n
    for i in range(n):
        for j in range(i+1,n):
            a,b=vectors[i],vectors[j]
            if all(x>=y for x,y in zip(a,b)) and any(x>y for x,y in zip(a,b)):dominates[i].append(j);counts[j]+=1
            elif all(y>=x for x,y in zip(a,b)) and any(y>x for x,y in zip(a,b)):dominates[j].append(i);counts[i]+=1
    front=[i for i,c in enumerate(counts) if not c];out=[]
    while front:
        out.append(front);nxt=[]
        for i in front:
            for j in dominates[i]:
                counts[j]-=1
                if counts[j]==0:nxt.append(j)
        front=sorted(nxt)
    if sum(map(len,out))!=n:raise RuntimeError('Pareto assignment incomplete')
    return out

def pareto_order(rows,top_k):
    vec=[(-r['features']['apex_log2'],r['features']['b_gn_16'],r['features']['b_gp_16'],-r['features']['ania_log2'],1-r['reference']['maximum_ratio']) for r in rows]
    fronts=pareto_fronts(vec);chosen=[];assignment={rows[i]['sequence']:rank for rank,front in enumerate(fronts,1) for i in front};distance_cache={}
    def distance(i,j):
        key=tuple(sorted((i,j)))
        if key not in distance_cache:distance_cache[key]=1-ratio(rows[i]['sequence'],rows[j]['sequence'])
        return distance_cache[key]
    for rank,front in enumerate(fronts,1):
        for i in front:assignment[rows[i]['sequence']]=rank
        remaining=set(front)
        while remaining:
            def key(i):
                peers=chosen if chosen else [j for j in front if j!=i]
                d=min(distance(i,j) for j in peers) if peers else 1
                r=rows[i]
                return (-d,-(1-r['reference']['maximum_ratio']),r['features']['apex_mean'],digest(r['sequence']),r['sequence'])
            pick=min(remaining,key=key);chosen.append(pick);remaining.remove(pick)
            if len(chosen)==top_k:return [rows[i] for i in chosen],assignment
    return [rows[i] for i in chosen],assignment

def selector_result(name,pool,scorable,selected,top_k,extra=None):
    n=len(pool);k=len(selected)
    result={'schema_version':'frontier-selector-v1','selector':name,'requested_k':top_k,'pool_count':n,'scorable_count':len(scorable),'coverage':len(scorable)/n if n else None,'coverage_status':'COMPLETE' if n and len(scorable)/n>=.95 else 'COVERAGE_LIMITED','selected_count':k,'complete':k==top_k,'status':'COMPLETE' if k==top_k else 'INCOMPLETE','output_fasta_name':'top.fasta' if k==top_k else 'partial_top.fasta','ordered_sequences':[r['sequence'] for r in selected],'ordered_raw_indices':[r['raw_index'] for r in selected],'top50_sequences':[r['sequence'] for r in selected[:50]],'safety_status':'UNKNOWN','selectivity':None}
    if extra:result.update(extra)
    return result

def unavailable(name,pool,reason,k=100):return selector_result(name,pool,[],[],k,{'status':reason,'available':False})

def run_selectors(rows,anchor=None,top_k=100,native=None,v3_runner=None):
    if not isinstance(top_k,int) or isinstance(top_k,bool) or top_k<1:raise ValueError('Invalid top_k')
    if len({r['sequence'] for r in rows})!=len(rows):raise ValueError('Duplicate candidate')
    if any(not r.get('top_eligible') or not 8<=len(r['sequence'])<=50 or set(r['sequence'])-CANONICAL or not 0<=r['reference']['maximum_ratio']<=.8 for r in rows):raise ValueError('Noneligible candidate in selector input')
    if len({r['raw_index'] for r in rows})!=len(rows):raise ValueError('Duplicate raw index')
    apex=[r for r in rows if r['features']['apex_complete']];both=[r for r in apex if r['features']['ania_complete']]
    outputs={}
    outputs['POTENCY_APEX11']=selector_result('POTENCY_APEX11',rows,apex,sorted(apex,key=lambda r:(r['features']['apex_mean'],r['raw_index']))[:top_k],top_k)
    breadth=sorted(apex,key=lambda r:(-r['features']['b_all_16'],r['features']['apex_q90'],r['features']['apex_mean'],digest(r['sequence']),r['sequence']))[:top_k]
    outputs['BREADTH_APEX11']=selector_result('BREADTH_APEX11',rows,apex,breadth,top_k,{'threshold_degenerate':bool(apex) and all(r['features']['b_all_16']==0 for r in apex)})
    selected,fronts=pareto_order(both,top_k)
    outputs['PARETO_NO_SELECTIVITY']=selector_result('PARETO_NO_SELECTIVITY',rows,both,selected,top_k,{'front_assignment':fronts,'objective_names':['negative_mean_log2_apex11','GN7_breadth16','GP4_breadth16','negative_mean_log2_ania3','reference_novelty']})
    if anchor and anchor.get('status')=='AVAILABLE':
        if anchor.get('count',0)<100 or any(len(anchor[k])!=anchor['count'] or sorted(anchor[k])!=anchor[k] or not all(math.isfinite(v) for v in anchor[k]) for k in ('apex','ania')):raise ValueError('Invalid frozen anchor')
        ranks={}
        for r in both:
            v=[anchor_rank(anchor['apex'],r['features']['apex_log2']),anchor_rank(anchor['ania'],r['features']['ania_log2'])]
            ranks[r['sequence']]={'apex_rank':v[0],'ania_rank':v[1],'minimum':min(v),'disagreement':max(v)-min(v),'median':statistics.median(v)}
        def ckey(r):
            q=ranks[r['sequence']];return (-q['minimum'],q['disagreement'],-q['median'],digest(r['sequence']),r['sequence'])
        outputs['CONSENSUS_FIXED']=selector_result('CONSENSUS_FIXED',rows,both,sorted(both,key=ckey)[:top_k],top_k,{'ranks':ranks,'anchor_count':anchor['count']})
    else:outputs['CONSENSUS_FIXED']=unavailable('CONSENSUS_FIXED',rows,'UNAVAILABLE_ANCHOR',top_k)
    if native is None:outputs['NATIVE']=unavailable('NATIVE',rows,'UNAVAILABLE_NO_NATIVE_RANKING',top_k)
    else:
        if not native.get('frozen_algorithm_sha256') or not native.get('pre_generation_registered'):raise ValueError('Unfrozen native ranking')
        ids=native['ordered_sequences']
        if len(set(ids))!=len(ids) or set(ids)!={r['sequence'] for r in rows}:raise ValueError('Native order must cover exact pool')
        lookup={r['sequence']:r for r in rows};outputs['NATIVE']=selector_result('NATIVE',rows,rows,[lookup[s] for s in ids[:top_k]],top_k,{'native_algorithm_sha256':native['frozen_algorithm_sha256']})
    if v3_runner:
        ordered=sorted(apex,key=lambda r:r['raw_index']);raw=v3_runner(ordered,top_k);lookup={r['sequence']:r for r in rows}
        outputs['V3_FROZEN']=selector_result('V3_FROZEN',rows,apex,[lookup[s] for s in raw['sequences']],top_k,{'v3_audit':raw})
    else:outputs['V3_FROZEN']=unavailable('V3_FROZEN',rows,'UNAVAILABLE_V3_RUNTIME_OR_ASSETS',top_k)
    return outputs

def activity_vector(r):
    f=r['features']
    if not(f['apex_complete'] and f['ania_complete']):return None
    return [f['apex_gn_log10'],f['apex_gp_log10'],f['ania_ec_log10'],f['ania_pa_log10']]

def activity_coverage(a,b):
    """Parent's four-coordinate >=0.10 log10 improvement dominance; all lower better."""
    if not a or not b:return None
    return sum(any(all(x<=y for x,y in zip(u,v)) and any(y-x>=.10 for x,y in zip(u,v)) for u in a) for v in b)/len(b)

def component_map(sequences,threshold=.8):
    seqs=sorted(set(sequences));parent=list(range(len(seqs)))
    def root(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for i,a in enumerate(seqs):
        for j in range(i):
            if ratio(a,seqs[j])>=threshold-1e-12 and lcs_ratio(a,seqs[j])>=threshold:
                x,y=root(i),root(j)
                if x!=y:parent[y]=x
    groups={}
    for i,s in enumerate(seqs):groups.setdefault(root(i),[]).append(s)
    return {s:min(digest(z) for z in members) for members in groups.values() for s in members}

def family_summary(sequences,mapping):
    if not sequences:return {'count':0,'largest_fraction':None,'hhi':None,'effective_count':None}
    counts=Counter(mapping[s] for s in sequences);n=len(sequences);fr=[c/n for c in counts.values()];h=sum(x*x for x in fr)
    return {'count':len(counts),'largest_fraction':max(fr),'top5_fraction':sum(sorted(fr,reverse=True)[:5]),'hhi':h,'effective_count':1/h}

def family_weighted_mean(rows,values,mapping):
    groups={}
    for r,v in zip(rows,values):groups.setdefault(mapping[r['sequence']],[]).append(v)
    return statistics.mean(statistics.mean(v) for v in groups.values()) if groups else None
