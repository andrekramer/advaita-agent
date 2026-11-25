"""Replay saved pilot cases; audit capacity, decisions, source scoring and native parity."""
import json
import math
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments import managed_growth as trial
from advaita.recall_withdrawal import RecallWithdrawal
from advaita.structural import StructuralLearner


def check():
    cases = [json.loads(line) for line in (trial.OUT/'cases.jsonl').read_text().splitlines()]
    assert {(case['seed'], case['condition']) for case in cases} == {
        (s, c) for s in range(4100, 4124) for c in ('valuable', 'redundant')}
    assert len(cases) == 48
    for case in cases:
        seed = case['seed']
        maps, stream, batches = trial.make_world(seed, case['condition'] == 'valuable')
        core = StructuralLearner([3*seed, 3*seed+1], 3*seed+2)
        core.train_upper([], [])
        prefix = trial.BudgetLearner(core, 'shadow')
        for t in range(1, trial.DECIDE+1):
            prefix.observe(t, stream[t])
            if t < trial.DECIDE and t in batches:
                prefix.review(t, batches[t])
        assert json.loads(json.dumps(trial.inspection(prefix))) == case['forecast']
        for budget in (3, 4):
            # For four groups replay with the production engine, without the budget adapter.
            engine = (RecallWithdrawal if budget == 4 else trial.BudgetLearner).restore(prefix.checkpoint())
            engine.budget = budget
            arm = case['branches'][str(budget)]
            for start, end, name in [(385, 640, 'changed'), (641, 832, 'return')]:
                errors = {s: [] for s in trial.SOURCES}
                used = 0
                for t in range(start, end+1):
                    if t-1 in batches:
                        engine.review(t-1, batches[t-1])
                        assert trial.parts(engine) == arm['reviews'][str(t-1)]
                    n = sum(len(set(p)) for p in trial.parts(engine))
                    assert n <= budget
                    used += n == 4
                    row = stream[t]
                    predictions = engine.observe(t, row)
                    for j in (0, 1):
                        source = trial.SOURCES[2*j+maps[j][row['x'][j]]]
                        errors[source].append((row['local'][j]-predictions[j])**2)
                recorded = arm['windows'][name]
                assert used == recorded['extra_ticks']
                for s in trial.SOURCES:
                    assert math.isclose(mean(errors[s]), recorded['source_loss'][s], abs_tol=1e-14)
                overall = sum(map(sum,errors.values())) / (2*(end-start+1))
                assert math.isclose(overall, recorded['loss'], abs_tol=1e-14)
            engine.review(end, batches[end])
            assert trial.parts(engine) == arm['reviews'][str(end)]
    print('48 decisions and 96 continuations verified, including native four-group replay.')


if __name__ == '__main__':
    check()
