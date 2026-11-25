"""Replay saved release schedules and independently check the decision times and scores."""
import json
import sys
from itertools import groupby
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'experiments'))
import managed_growth_release as study
from advaita.recall_withdrawal import RecallWithdrawal


def audit():
    records = [json.loads(line) for line in (study.OUT/'cases.jsonl').read_text().splitlines()]
    assert len(records) == 72
    assert len({(r['seed'],r['history']) for r in records}) == 72
    for seed, group in groupby(records, key=lambda r:r['seed']):
        cases = list(group)
        assert {c['history'] for c in cases} == set(study.HISTORIES)
        maps, stream, batches = study.pilot.make_world(seed, True, end=study.END)
        core = study.pilot.StructuralLearner([3*seed,3*seed+1],3*seed+2)
        core.train_upper([], [])
        prefix = study.pilot.BudgetLearner(core, 'shadow')
        for t in range(1,385):
            prefix.observe(t,stream[t])
            if t % 64 == 0 and t < 384:
                prefix.review(t,batches[t])
        saved = prefix.checkpoint()
        for case in cases:
            permitted = study.pilot.inspection(prefix)['permit']
            assert case['opening']['permit'] == permitted
            rows, reviews = study.world_rows(case['history'],maps,stream,batches)
            for name, arm in case['arms'].items():
                native = name == 'keep' and permitted
                engine = (RecallWithdrawal if native else study.pilot.BudgetLearner).restore(saved)
                previous_low = False
                expected = None
                for index, review in enumerate(arm['reviews']):
                    t = 384 + 64*index
                    assert review['tick'] == t
                    if permitted and t > 384 and expected is None:
                        if name == 'monitor':
                            projected = study.pilot.inspection(engine)['predicted_gain']
                            assert projected == review['gain']
                            low = projected <= .01
                            if low and previous_low:
                                expected = t
                            previous_low = low
                        if name == 'timer' and t == 768:
                            expected = t
                    engine.budget = 4 if permitted and expected is None else 3
                    assert review['budget'] == engine.budget
                    engine.review(t,reviews[t])
                    assert study.pilot.parts(engine) == review['partitions']
                    if t == study.END:
                        break
                    sums, counts = [0.]*4, [0]*4
                    for k in range(t+1,t+65):
                        row = rows[k]
                        pred = engine.observe(k,row)
                        for j in range(2):
                            i = 2*j+maps[j][row['x'][j]]
                            sums[i] += (pred[j]-row['local'][j])**2
                            counts[i] += 1
                    assert arm['blocks'][index] == dict(start=t+1, sums=sums,counts=counts)
                assert expected == arm['release']
        # Equal histories before their fork imply equal actions and scores.
        lasting, persistent, short = [next(c for c in cases if c['history']==h) for h in study.HISTORIES]
        for arm in study.ARMS:
            for other, n in ((persistent,4),(short,6)):
                assert lasting['arms'][arm]['blocks'][:n] == other['arms'][arm]['blocks'][:n]
                assert lasting['arms'][arm]['reviews'][:n+1] == other['arms'][arm]['reviews'][:n+1]
    print('Verified all 72 cases, 216 continuations, release decisions, scores and shared prefixes.')


if __name__ == '__main__':
    audit()
