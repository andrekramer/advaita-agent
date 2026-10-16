"""Independent saved-trace audit of Experiment 008, without learner imports."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import statistics

ROOT=Path(__file__).resolve().parents[1]
XS=list(itertools.product((0,1),repeat=3))


def close(a,b):
    if isinstance(a,dict):
        assert a.keys()==b.keys()
        for k in a: close(a[k],b[k])
    elif isinstance(a,(list,tuple)):
        assert len(a)==len(b)
        for x,y in zip(a,b): close(x,y)
    elif isinstance(a,float) or isinstance(b,float):
        assert math.isfinite(a) and math.isfinite(b) and abs(a-b)<1e-11,(a,b)
    else: assert a==b,(a,b)


def canon(leaves):
    labels={}; result=[]
    for cube,k in sorted(leaves):
        labels.setdefault(k,len(labels)); result.append((tuple(cube),labels[k]))
    return tuple(result)


def coalesce(leaves):
    leaves=sorted(leaves)
    for i,(a,ka) in enumerate(leaves):
        for j in range(i+1,len(leaves)):
            b,kb=leaves[j]; different=[d for d in range(3) if a[d]!=b[d]]
            if ka==kb and len(different)==1 and {a[different[0]],b[different[0]]}=={0,1}:
                cube=list(a); cube[different[0]]=-1
                return coalesce([r for n,r in enumerate(leaves) if n not in (i,j)]+[(tuple(cube),ka)])
    return canon(leaves)


def pool(structure,enabled):
    structure=tuple((tuple(c),k) for c,k in structure)
    keys=sorted({k for _,k in structure}); fresh=max(keys)+1
    result={structure}
    for i,(cube,_) in enumerate(structure):
        for d,v in enumerate(cube):
            if v!=-1: continue
            children=[]
            for bit in (0,1):
                child=list(cube); child[d]=bit; children.append((tuple(child),fresh+bit))
            s=canon([r for n,r in enumerate(structure) if n!=i]+children)
            if len(s)<=8 and len({k for _,k in s})<=4: result.add(s)
    if enabled:
        for a,b in itertools.combinations(keys,2):
            result.add(coalesce([(c,a if k==b else k) for c,k in structure]))
    assert len(result)<=31
    return sorted(result)


def group(state,x):
    hits=[k for cube,k in state['structure'] if all(v==-1 or v==x[d] for d,v in enumerate(cube))]
    assert len(hits)==1
    return hits[0]


def fit(structure,rows):
    n=len({k for _,k in structure})
    state={'structure':[[list(c),k] for c,k in structure],'counts':[[[0,0],[0,0]] for _ in range(n)]}
    for x in XS: group(state,x)
    for r in rows:
        cell=state['counts'][group(state,r['x'])][r['a']]; cell[0]+=r['y']; cell[1]+=1
    return state


def p(model,x,a):
    r,n=model['counts'][group(model,x)][a]; return (r+1)/(n+2)


def nll(pred,y):
    assert 0<pred<1
    return -math.log(pred if y else 1-pred)


def penalty(model): return .01*len(model['counts'])+.005*len(model['structure'])
def prediction_loss(model,rows): return statistics.mean(nll(p(model,r['x'],r['a']),r['y']) for r in rows)


def streams(seed,branch):
    perm=[0,1,2]; random.Random(seed).shuffle(perm)
    support=[(x,a) for x in XS if x not in ((0,0,0),(1,1,1)) for a in (0,1)]
    tr,vr=random.Random(8000+seed),random.Random(9000+seed)
    training=[]; selection=[]
    for block in range(16):
        rows=support.copy(); tr.shuffle(rows)
        training += [{'x':[x[j] for j in perm],'a':a,'y':a if branch=='changed' and block>=8 else x[0]^a} for x,a in rows]
    for boundary in (48,96,144,192):
        rows=support.copy(); vr.shuffle(rows)
        selection.append([{'x':[x[j] for j in perm],'a':a,'y':a if branch=='changed' and boundary>96 else x[0]^a} for x,a in rows])
    return perm,training,selection


def checkpoint(ev,model,relevant,changed):
    assert ev['before']==ev['after'] and ev['before']['model']==model
    table=[{'x':list(x),'a':a,'p':p(model,x,a)} for x in XS for a in (0,1)]
    close(ev['table'],table)
    held=[{**r,'y':r['a'] if changed else r['x'][relevant]^r['a']} for r in table if tuple(r['x']) in ((0,0,0),(1,1,1))]
    close(ev['withheld'],held)
    assignments=[group(model,x) for x in XS]; assert ev['assignments']==assignments
    effects=[[],[],[]]
    for x in XS:
        for d in range(3):
            other=list(x); other[d]^=1
            effects[d].extend(abs(p(model,x,a)-p(model,other,a)) for a in (0,1))
    metrics={'accuracy':sum((r['p']>.5)==r['y'] for r in held)/4,
             'loss':statistics.mean(nll(r['p'],r['y']) for r in held),
             'forms':len(model['counts']),'leaves':len(model['structure']),
             'partition_matches_relevant_bit':all((group(model,x)==group(model,y))==(x[relevant]==y[relevant]) for x,y in itertools.combinations(XS,2)),
             'context_effect':max(max(v) for v in effects),
             'nuisance_effect':max(max(effects[d]) for d in range(3) if d!=relevant),
             'relevant_effect':min(effects[relevant]),
             'action_effect':min(abs(p(model,x,0)-p(model,x,1)) for x in XS)}
    close(ev['metrics'],metrics)


def acquired(m):
    return (m['forms']==m['leaves']==2 and m['partition_matches_relevant_bit']
            and m['accuracy']==1 and m['loss']<.25 and m['nuisance_effect']<=1e-12 and m['relevant_effect']>=.5)


def verify_run(run):
    seed,branch,variant=run['seed'],run['branch'],run['variant']
    perm,training,selection=streams(seed,branch); assert perm==run['permutation']
    relevant=perm.index(0); enabled=variant=='merge_enabled'
    model=fit((((-1,-1,-1),0),),[]); buffer=[]; seen=0; review=0
    costs={k:0 for k in run['costs']}; losses=[]; reviews=[]; merges=[]
    snapshots={}; state=lambda:{'model':model,'seen':seen,'window_size':len(buffer),'window_start':max(1,seen-47)}
    assert len(run['events'])==196
    for e in run['events']:
        close(e['before'],state())
        if e['kind']=='train':
            assert e['index']==seen+1
            row=e['row']; assert row==training[seen]
            close(e['p'],p(model,row['x'],row['a'])); losses.append(nll(e['p'],row['y']))
            buffer=(buffer+[row])[-48:]; seen+=1
            model=fit(model['structure'],buffer)
            costs['count_refits']+=1; costs['count_refit_rows']+=len(buffer)
        else:
            assert seen==48*(review+1)==e['index']; rows=selection[review]; review+=1
            assert rows==e['selection']
            structures=pool(model['structure'],enabled)
            close([c['state']['structure'] for c in e['candidates']],structures)
            costs['candidate_fits']+=len(structures); costs['candidate_fit_rows']+=len(structures)*len(buffer)
            for c,s in zip(e['candidates'],structures):
                close(c['state'],fit(s,buffer)); close(c['penalty'],penalty(c['state']))
                close(c['training_loss'],prediction_loss(c['state'],buffer))
                close(c['training_objective'],prediction_loss(c['state'],buffer)+penalty(c['state']))
            winner=min(range(len(structures)),key=lambda i:(e['candidates'][i]['training_objective'],structures[i]))
            assert e['winner']==winner
            assert [c['advanced'] for c in e['candidates']]==[i==winner for i in range(len(structures))]
            candidate=e['candidates'][winner]['state']; decision=e['decision']
            inc=prediction_loss(model,rows); cand=prediction_loss(candidate,rows)
            cg=penalty(model)-penalty(candidate); gain=inc-cand+cg; accepted=gain>.001
            merge=accepted and len(candidate['counts'])<len(model['counts'])
            expected={'incumbent_predictions':[p(model,r['x'],r['a']) for r in rows],
                      'candidate_predictions':[p(candidate,r['x'],r['a']) for r in rows],
                      'incumbent_loss':inc,'candidate_loss':cand,'prediction_gain':inc-cand,
                      'complexity_gain':cg,'gain':gain,'accepted':accepted,'merge':merge}
            close(decision,expected)
            if accepted: model=candidate
            if merge: merges.append(seen)
            costs['selection_outcomes']+=12; reviews.append(e)
            if seen in (96,192): snapshots[seen]=state()
        close(e['after'],state())
    assert seen==192 and review==4
    close(run['final_buffer'],buffer); close(run['costs'],costs)
    assert [ev['index'] for ev in run['checkpoints']]==[96,192]
    for ev in run['checkpoints']:
        close(ev['before'],snapshots[ev['index']])
        checkpoint(ev,snapshots[ev['index']]['model'],relevant,branch=='changed' and ev['index']>96)
    initial,final=[ev['metrics'] for ev in run['checkpoints']]
    first=next((i for i in merges if i>96),None)
    stable=first is not None and all(len(e['after']['model']['counts'])==1 for e in reviews if e['index']>=first)
    checks={'acquisition':acquired(initial),'prediction':final['accuracy']==1 and final['loss']<.25}
    if branch=='changed' and enabled:
        checks.update(actual_collapse=first is not None and stable and final['forms']==final['leaves']==1,
                      useful_invariance=final['context_effect']<=1e-12 and final['action_effect']>=.5)
    elif branch=='changed': checks['retains_structure']=final['forms']==final['leaves']==2
    else:
        correct=all(len(e['after']['model']['counts'])==len(e['after']['model']['structure'])==2 and
                    all((group(e['after']['model'],x)==group(e['after']['model'],y))==(x[relevant]==y[relevant])
                        for x,y in itertools.combinations(XS,2)) for e in reviews if e['index']>96)
        checks['preservation']=acquired(final) and not merges and correct
    close(run['metrics'],{'acquisition':initial,'final':final,'checks':checks,'own_pass':all(checks.values()),
                          'first_merge':first,'merge_delay':first-96 if first else None,'merges':merges,
                          'review_forms':[[e['index'],len(e['after']['model']['counts'])] for e in reviews],
                          'training_loss':statistics.mean(losses)})


def main():
    data=json.loads((ROOT/'results/collapse-v1/results.json').read_text())
    for name,digest in data['hashes'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    assert [(r['seed'],r['branch'],r['variant']) for r in data['runs']]==[
        (s,b,v) for s in range(5) for b in ('changed','unchanged') for v in ('merge_enabled','merge_disabled')]
    for run in data['runs']: verify_run(run)
    pairs=[]
    for seed in range(5):
        by={(r['branch'],r['variant']):r for r in data['runs'] if r['seed']==seed}
        for variant in ('merge_enabled','merge_disabled'):
            first=by['changed',variant]; second=by['unchanged',variant]
            assert first['events'][:98]==second['events'][:98]
            assert first['checkpoints'][0]==second['checkpoints'][0]
        for branch in ('changed','unchanged'):
            x=by[branch,'merge_enabled']; y=by[branch,'merge_disabled']
            assert [e['row'] for e in x['events'] if e['kind']=='train']==[e['row'] for e in y['events'] if e['kind']=='train']
            assert [e['selection'] for e in x['events'] if e['kind']=='review']==[e['selection'] for e in y['events'] if e['kind']=='review']
        enabled=by['changed','merge_enabled']['metrics']['final']['loss']
        disabled=by['changed','merge_disabled']['metrics']['final']['loss']
        preserved=enabled<=disabled+.01
        pairs.append({'seed':seed,'enabled_changed_loss':enabled,'disabled_changed_loss':disabled,
                      'prediction_preserved':preserved,'all_conditions_pass':preserved and all(r['metrics']['own_pass'] for r in by.values())})
    close(data['comparison'],{'per_seed':pairs,'passed_seeds':sum(p['all_conditions_pass'] for p in pairs),
                              'overall_pass':all(p['all_conditions_pass'] for p in pairs)})
    assert data['outcome_presentations']==20*(192+48+8)==4960
    assert data['unlabelled_predictions']==20*2*12==480
    print('PASS: 20 runs / 4,960 presentations; independent streams, rolling expiration,')
    print('candidate enumeration, counts, selection, frozen evaluation, criteria, paired controls,')
    print('budgets and source/protocol hashes verified. Prior experiments were not rerun.')


if __name__=='__main__': main()
