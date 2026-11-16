"""Fresh confirmation of meaning-bound plasticity and a 63-tick duration control."""
import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'experiments')]
import direction_strength_trial as first
from advaita.controlled import ControlledLearner
from advaita.direction_strength import DirectionStrengthLearner
from advaita.structural import StructuralLearner

OUT = ROOT/'results/cell-duration-confirmation-v1'
ARMS = (*first.ARMS, 'duration')
SEEDS = range(3300, 3312)
PROPOSALS = (3300, 3301)


def duration_forecasts(cells, decision):
    """Forward model with 63 boosted decays, followed by one ordinary tick."""
    total = sum(c['raw'][0][1] + c['raw'][1][1] for c in cells)
    share = sum(c['raw'][0][1] for c in cells)/total if total else .5
    chosen = next(c for c in cells if c['info']['binding'] == decision['selected'])
    for mode, allocation in [('raw','raw'), ('named','named'), ('aggregate',share)]:
        gain = 0.
        if decision['enabled']:
            # The projection has zero incoming slow mass for this horizon.
            # Its full 63-tick debit sum is therefore a geometric series.
            mass = chosen['raw'][1][1]
            if mode == 'aggregate':
                mass = sum(bank[1] for bank in chosen['raw'])*(1-share)
            fast_decay = 2**(-1/128)
            allowance = mass*(2**(-1/1024)-fast_decay)*(1-fast_decay**63)/(1-fast_decay)
            gain = first.project(chosen,'none',allocation,0) - first.project(chosen,'budget',allocation,allowance)
        decision['forecast'][mode]['duration'] = gain
    assert abs(decision['forecast']['named']['duration']-decision['forecast']['raw']['duration']) <= 1e-12


def duration_arm(checkpoint, world, history, target, decision):
    learner = DirectionStrengthLearner.restore(checkpoint)
    if decision['enabled']:
        learner.open_cell(target,decision['x'],decision['a'],budget=None,through_tick=703,
                          reason='supplied target, fixed 63-tick duration')
    error = first.probe(learner,target,decision)
    predictions, scores, selected_scores = [], [], []
    native_removed = 0.
    for tick,row in enumerate(world['main'][640:1152],641):
        pred = learner.observe(tick,row)
        predictions.append(pred)
        scores.append([(p-y)**2 for p,y in zip(pred,first.labels(row))])
        if tick<=896 and first.raw_index(target,row) in decision['selected']['members']:
            selected_scores.append(scores[-1][target])
        if tick % 64 == 0:
            review = learner.review(tick,world['selection'][str(tick)])
            native_removed += sum(e['removed_mass'] for e in review['weakenings'])
        if tick == 702:
            saved = learner.checkpoint()
            learner = DirectionStrengthLearner.restore(saved)
            assert learner.checkpoint() == saved
        if tick == 703:
            assert learner.cell_command is None
    events = learner.cell_events
    debits = [e for e in events if e['kind']=='debit']
    if decision['enabled']:
        assert [e['tick'] for e in debits] == list(range(641,704))
        assert events[-1]['reason']=='expired' and events[-1]['tick']==703
    spent = 0.
    for event in debits:
        spent += event['debit']
        error = max(error,abs(event['spent']-spent),
                    abs(event['before']*2**(-1/1024)-event['after']-event['debit']))
    forms = first.life.forms_at(world,1152,True)
    if history=='lasting':
        j=world['affected']
        forms[j]=[1-v for v in forms[j]]
    local=[first.partition_correct(m['partition'],f) for m,f in zip(learner._engine.locals,forms)]
    accuracy=mean((learner.predict([x,y],a)['active'][2]>=.5)==bool(forms[0][x]^forms[1][y]^a)
                  for x,y,a in first.life.CONTEXTS)
    return dict(predictions=predictions, cell_events=events, error=error, spent=spent,
                closed=[e['reason'] for e in events if e['kind']=='close'], cell_loss=mean(selected_scores),
                local_correct=local,upper_accuracy=accuracy,native_removed=native_removed,
                losses={window:[mean(line[j] for line in scores[lo:hi]) for j in range(3)]
                        for window,(lo,hi) in first.WINDOWS.items()})


def run_cases(world, history, proposal):
    acquisition, encoded = first.life.legacy_run(world,proposal,True)
    core = StructuralLearner.restore(encoded)
    learner = DirectionStrengthLearner(core)
    native = ControlledLearner(core)
    initial = {ctx:native.predict(list(ctx[:2]),ctx[2])['active'] for ctx in first.life.CONTEXTS}
    pooled = []
    for model in native._engine.locals:
        ones, mass = map(sum,zip(*model['counts'].values()))
        pooled.append((ones+1)/(mass+2))
    for tick,row in enumerate(world['main'][:640],1):
        assert learner.observe(tick,row) == native.observe(tick,row)
        if tick % 64 == 0:
            rows = world['selection'][str(tick)]
            assert learner.review(tick,rows) == native.review(tick,rows)
    assert learner.native_checkpoint() == native.native_checkpoint()
    checkpoint, reference = learner.checkpoint(), native.checkpoint()
    active = world['main'][640:896]
    fixed = [initial[(*r['x'],r['a'])] for r in active]
    frozen_loss = mean(mean((p-y)**2 for p,y in zip(ps,first.labels(r))) for ps,r in zip(fixed,active))
    created = [any(len(set(step[j]['decision']['before']['partition']))==1 and
                   len(set(step[j]['decision']['after']['partition']))>1 for step in acquisition['warmup']) for j in range(2)]
    split = [created[j] and mean((pooled[j]-r['local'][j])**2-(ps[j]-r['local'][j])**2
                                 for ps,r in zip(fixed,active))>0 for j in range(2)]
    for target in (world['affected'],2):
        cells = first.describe(learner,target,world['main'][576:640])
        decision = first.choose(cells)
        duration_forecasts(cells,decision)
        branches = {arm:first.run_arm(checkpoint,reference,world,history,target,decision,arm) for arm in first.ARMS}
        branches['duration'] = duration_arm(checkpoint,world,history,target,decision)
        yield dict(seed=world['seed'],history=history,proposal=proposal,target=target,protected=1-world['affected'],
                   decision=decision,branches=branches,frozen_loss=frozen_loss,split=split,created=created,
                   fixed_predictions=fixed,pooled=pooled,transfer_accuracy=acquisition['transfer']['accuracy'])


def joint_interval(records, value):
    return first.ci([mean(value(r) for r in records if r['seed']==s) for s in SEEDS])


def guards(records, arm):
    results = []
    for history in first.HISTORIES:
        for window in ('active','release','return'):
            for j in range(3):
                selected = [r for r in records if r['history']==history and
                            (window!='active' or history=='stable' or j==r['protected'])]
                if selected:
                    costs = [r['branches'][arm]['losses'][window][j]-r['branches']['none']['losses'][window][j]
                             for r in selected]
                    results.append(dict(history=history,window=window,output=j,mean=mean(costs),
                                        worst=max(costs),passed=mean(costs)<=.01 and max(costs)<=.05))
    return results


def effect(r,arm,window='active'):
    j=r['target']
    return r['branches']['none']['losses'][window][j]-r['branches'][arm]['losses'][window][j]


def summarize(records):
    legacy=first.summary(records)
    summaries={}
    for arm in ARMS:
        checks=guards(records,arm)
        gains=joint_interval(records,lambda r:effect(r,arm))
        summaries[arm]=dict(gain=gains,guards=checks,failed=sum(not g['passed'] for g in checks),
                            closures=dict(Counter(reason for r in records for reason in r['branches'][arm]['closed'])),
                            cell_gain=mean(r['branches']['none']['cell_loss']-r['branches'][arm]['cell_loss'] for r in records))
    candidate=summaries['cell']
    actions=legacy['actions']
    steer=(candidate['gain'][0]>=.001 and candidate['gain'][1]>0 and actions/len(records)>=.2 and candidate['failed']==0)
    budget_gain=joint_interval(records,lambda r:effect(r,'budget')-effect(r,'duration'))
    late_cost=max(abs(r['branches']['budget']['losses'][w][j]-r['branches']['duration']['losses'][w][j])
                  for r in records for w in ('release','return') for j in range(3))
    same_timing=all(r['timing']['ticks']==[63,63] for r in records if r['decision']['enabled'])
    equivalent=budget_gain[1]>=-.0001 and budget_gain[2]<=.0001 and late_cost<=.005
    gates=dict(learn=legacy['gates']['learn'],interpret=legacy['gates']['interpret'],steer=steer)
    classify=lambda x:int(x>.001)-int(x<-.001)
    duration_effects=[effect(r,'duration','early') for r in records]
    def duration_accuracy(mode):
        pairs=list(zip(duration_effects,[r['decision']['forecast'][mode]['duration'] for r in records]))
        return dict(mae=mean(abs(a-p) for a,p in pairs),correct=sum(classify(a)==classify(p) for a,p in pairs),
                    material_correct=sum(classify(a)==classify(p) for a,p in pairs if abs(a)>.001))
    return dict(gates=gates,cases=len(records),continuations=len(records)*len(ARMS),actions=actions,
                learning_gain=legacy['learning_gain'],transfer_by_env={s:max(r['transfer_accuracy'] for r in records if r['seed']==s) for s in SEEDS},
                useful_split_and_transfer=legacy['useful_split_environments'],original_effects={k:legacy[k] for k in
                ('effect_mae','correct','effects','material','material_correct','one_step_and_debit_max_error')},
                duration_forecasts={m:duration_accuracy(m) for m in ('named','aggregate')},
                duration_material=sum(abs(a)>.001 for a in duration_effects),arms=summaries,
                budget_over_duration=budget_gain,maximum_release_return_difference=late_cost,equivalent=equivalent,
                timing_matched=same_timing,max_forecast_gap=max(r['timing']['gap'] for r in records),
                recovery={h:dict(local=mean(all(r['branches']['cell']['local_correct']) for r in records if r['history']==h),
                                  upper=mean(r['branches']['cell']['upper_accuracy'] for r in records if r['history']==h)) for h in first.HISTORIES})


def timing(case):
    budget=case['branches']['budget']
    duration=case['branches']['duration']
    assert budget['predictions'][:62]==duration['predictions'][:62]
    debits=[[e for e in b['cell_events'] if e['kind']=='debit'] for b in (budget,duration)]
    if case['decision']['enabled']:
        assert len(debits[0])==len(debits[1])==63
        assert [e['debit'] for e in debits[0][:62]]==[e['debit'] for e in debits[1][:62]]
        assert 0<debits[0][-1]['debit']<debits[1][-1]['debit']
    gap=max(abs(p-q) for ps,qs in zip(budget['predictions'],duration['predictions']) for p,q in zip(ps,qs))
    return dict(ticks=[len(ds) for ds in debits],last_debits=[ds[-1]['debit'] if ds else 0. for ds in debits],gap=gap)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUT)
    out=parser.parse_args().output
    if not __debug__:
        raise RuntimeError('Run without -O to enable parity and accounting checks')
    out.mkdir(exist_ok=False)
    paths=set(json.loads((ROOT/'results/strength-inspection-v1/manifest.json').read_text()))
    paths.update(json.loads((ROOT/'results/direction-strength-v1/manifest.json').read_text()))
    paths.update(['experiments/cell_duration_protocol.md','experiments/cell_duration_confirmation.py',
                  'checks/audit_cell_duration.py','results/direction-strength-v1/audit.json'])
    manifest={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    records=[]
    with gzip.open(out/'cases.jsonl.gz','xt') as stream:
        for seed in SEEDS:
            for history in first.HISTORIES:
                world=first.world(seed,history)
                for proposal in PROPOSALS:
                    for case in run_cases(world,history,proposal):
                        case['timing']=timing(case)
                        stream.write(json.dumps(case)+'\n')
                        del case['fixed_predictions']
                        for branch in case['branches'].values():
                            del branch['cell_events'],branch['predictions']
                        records.append(case)
            print(f'Completed {seed-3299}/12 environments',flush=True)
    summary=summarize(records)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(summary['gates'],summary['equivalent'])


if __name__=='__main__':
    main()
