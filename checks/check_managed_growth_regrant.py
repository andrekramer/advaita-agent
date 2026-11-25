"""Replay reversible decisions from observed evidence and independently rescore their effects."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'experiments'))
import managed_growth_regrant as experiment
from managed_growth_release import pilot, world_rows, HISTORIES, END


def check(records):
    indexed = {(c['seed'],c['history']):c for c in records}
    expected = {(s,h) for s in range(4300,4324) for h in HISTORIES}
    expected.update((s,'short_return') for s in range(4200,4224))
    assert set(indexed) == expected and len(indexed) == len(records)
    for (seed, history), case in indexed.items():
        maps, stream, batches = pilot.make_world(seed, True, end=END)
        assert maps == case['maps']
        stream, batches = world_rows(history, maps, stream, batches)
        core = pilot.StructuralLearner([3*seed,3*seed+1],3*seed+2)
        core.train_upper([], [])
        engine = pilot.BudgetLearner(core,'shadow')
        arm = case['arms']['reversible']
        ever_released = previous_low = False
        last_release = None
        for tick in range(1,END+1):
            row = stream[tick]
            ps = engine.observe(tick,row)
            if tick > pilot.DECIDE:
                for j in (0,1):
                    i = 2*j+maps[j][row['x'][j]]
                    sums[i] += (row['local'][j]-ps[j])**2
                    counts[i] += 1
            if tick % 64:
                continue
            if tick < pilot.DECIDE:
                engine.review(tick,batches[tick])
                continue
            index = (tick-pilot.DECIDE)//64
            r = arm['reviews'][index]
            info = pilot.inspection(engine)
            low = not info['permit']
            if index == 0:
                assert json.loads(json.dumps(info)) == case['opening']
                engine.budget = 3 if low else 4
                assert r['gain'] is None
            else:
                assert arm['blocks'][index-1] == dict(start=tick-63,sums=sums,counts=counts)
                if engine.budget == 4 or ever_released:
                    assert info['predicted_gain'] == r['gain']
                if engine.budget==4 and low and previous_low:
                    ever_released = True
                    engine.budget = 3
                    last_release = tick
                elif engine.budget==3 and ever_released and not low:
                    engine.budget = 4
            previous_low = low and engine.budget==4 and index>0
            engine.review(tick,batches[tick])
            assert r['budget']==engine.budget and r['partitions']==pilot.parts(engine)
            assert sum(len(set(p)) for p in r['partitions']) <= r['budget']
            sums,counts = [0.]*4,[0]*4
        assert last_release == arm['release']
        reopen = next((t for t,b in experiment.transitions(arm) if b==4),END)
        blocks = (reopen-pilot.DECIDE)//64
        assert case['arms']['monitor']['blocks'][:blocks] == arm['blocks'][:blocks]
    for seed in range(4300,4324):
        for name in experiment.ARMS:
            lasting = indexed[seed,'lasting_return']['arms'][name]
            for history,n in [('short_return',6),('persistent_shift',4)]:
                other = indexed[seed,history]['arms'][name]
                assert lasting['reviews'][:n+1] == other['reviews'][:n+1]
                assert lasting['blocks'][:n] == other['blocks'][:n]
    print('Verified 96 reversible decision and scoring replays, shared histories and one-way prefixes.')


if __name__ == '__main__':
    check([json.loads(line) for line in (experiment.OUT/'cases.jsonl').read_text().splitlines()])
