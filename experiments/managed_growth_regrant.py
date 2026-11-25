"""Compare reversible and one-way group permissions. Run from the repository root."""
import json
from collections import Counter
from statistics import mean

import managed_growth_release as release
from managed_growth import ROOT, interval

OUT = ROOT/'results/managed-growth-regrant-v1'
ARMS = ('keep', 'monitor', 'reversible')


def transitions(arm):
    reviews = arm['reviews']
    return [(now['tick'], now['budget']) for prev,now in zip(reviews,reviews[1:])
            if prev['budget'] != now['budget']]


def same_grouping(part, truth):
    return all((x == part[0]) == (y == truth[0]) for x,y in zip(part, truth))


def recovery(case):
    """Index each episode by actual use and meaningful C/D readout after permission."""
    arm = case['arms']['reversible']
    episodes = []
    for tick, budget in transitions(arm):
        if budget != 4:
            continue
        use = correct = None
        for r in arm['reviews']:
            if r['tick'] < tick:
                continue
            if r['budget'] != 4 or r['tick'] == release.END:
                break
            a,b = r['partitions']
            if use is None and len(set(a))+len(set(b)) == 4:
                use = r['tick']
            if correct is None and same_grouping(b, case['maps'][1]):
                correct = r['tick']
        episodes.append(dict(regrant=tick, fourth_use=use, correct_cd=correct))
    return episodes


def summarize(cases, window):
    comparisons = {}
    for baseline in ('keep','monitor'):
        differences = []
        for c in cases:
            base, new = [release.scores(c['arms'][arm], window) for arm in (baseline,'reversible')]
            gain = [a-b for a,b in zip(base,new)]
            differences.append(gain + [mean(gain[2:4])])
        comparison = {}
        for name, values in zip(('A','B','C','D','overall','CD'),zip(*differences)):
            comparison[name] = dict(mean=mean(values), worst=min(values))
            if name in ('B','CD'):
                comparison[name]['interval'] = interval(values)[1:]
        comparisons[baseline] = comparison

    episodes = [e for c in cases for e in recovery(c)]
    commands = [transitions(c['arms']['reversible']) for c in cases]
    return dict(seeds=len(cases), initial_grants=sum(c['opening']['permit'] for c in cases),
                releases=Counter(t for cs in commands for t,b in cs if b==3),
                regrants=Counter(t for cs in commands for t,b in cs if b==4),
                seeds_released=sum(any(b==3 for _,b in cs) for cs in commands),
                seeds_reopened=sum(any(b==4 for _,b in cs) for cs in commands),
                episodes=episodes, comparisons=comparisons)


def main():
    fresh = [c for seed in range(4300,4324) for c in release.cases(seed,ARMS)]
    replay = [c for seed in range(4200,4224)
              for c in release.cases(seed,ARMS,('short_return',))]
    old = {c['seed']:c for c in (json.loads(line) for line in
           (release.OUT/'cases.jsonl').read_text().splitlines()) if c['history']=='short_return'}
    for c in replay:
        for arm in ('monitor','keep'):
            assert c['arms'][arm] == old[c['seed']]['arms'][arm]
    summary = {h:summarize([c for c in fresh if c['history']==h],
                            'after_short' if h=='short_return' else 'entire_return')
               for h in release.HISTORIES}
    summary['previous_short_return'] = summarize(replay,'after_short')
    OUT.mkdir(exist_ok=True)
    (OUT/'cases.jsonl').write_text(''.join(json.dumps(c,separators=(',',':'))+'\n' for c in fresh+replay))
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')


if __name__ == '__main__':
    main()
