"""Experiment 007, fixed continuous-world complementarity test. Standard library."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ('full', 'no_feedback', 'no_teaching', 'disconnected', 'online', 'misaligned')
REGIMES = ('LL', 'LH', 'HL', 'HH')
THETA0 = [0.55, 0.0, 0.0, 0.0, 0.0]
RIDGE = 1e-4


def clip(x, low, high):
    return min(high, max(low, x))


def phi(x):
    return [1.0, math.sin(x), math.cos(x), math.sin(2*x), math.cos(2*x)]


def dot(x, y):
    return sum(a*b for a, b in zip(x, y))


def gain(theta, x):
    return clip(dot(theta, phi(x)), .1, 1.)


def true_gain(x):
    return .55 + .25*math.sin(x) + .10*math.cos(2*x)


def solve(matrix, rhs):
    """Partial-pivot Gaussian elimination for the five-dimensional ridge fit."""
    n = len(rhs)
    rows = [list(row) + [value] for row, value in zip(matrix, rhs)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda i: abs(rows[i][col]))
        assert abs(rows[pivot][col]) > 1e-14
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        rows[col] = [v/scale for v in rows[col]]
        for i in range(n):
            if i != col:
                multiplier = rows[i][col]
                rows[i] = [v-multiplier*w for v, w in zip(rows[i], rows[col])]
    return [row[-1] for row in rows]


def fit(records):
    assert records
    size = len(records)
    matrix = [[RIDGE if i == j else 0. for j in range(5)] for i in range(5)]
    rhs = [RIDGE*w for w in THETA0]
    for z, action, target in records:
        f = [.2*action*v for v in phi(z)]
        for i in range(5):
            rhs[i] += f[i]*target/size
            for j in range(5):
                matrix[i][j] += f[i]*f[j]/size
    raw = solve(matrix, rhs)
    return {'matrix': matrix, 'rhs': rhs, 'raw': raw,
            'theta': [clip(v, -1., 1.) for v in raw], 'records': size}


class Learner:
    """Only observable o/action and later r enter this class, never world labels."""
    def __init__(self, variant):
        assert variant in VARIANTS
        self.variant = variant
        self.teaching = variant not in ('no_teaching', 'disconnected')
        self.feedback_on = variant not in ('no_feedback', 'disconnected')
        self.theta = THETA0.copy()
        self.prior, self.d = None, 0.
        self.buffer, self.pending = [], None
        self.costs = {k: 0 for k in (
            'gain_calls', 'gain_clips', 'loop_gain_clips', 'local_clips',
            'coefficient_clips', 'fits', 'fit_rows', 'online_updates',
            'local_updates', 'selection_scores', 'resets')}

    def start_episode(self):
        assert self.pending is None
        self.prior, self.d = None, 0.
        self.costs['resets'] += 1

    def model_gain(self, theta, x):
        raw = dot(theta, phi(x))
        self.costs['gain_calls'] += 1
        self.costs['gain_clips'] += int(raw < .1 or raw > 1.)
        return clip(raw, .1, 1.)

    def state(self):
        return {'theta': self.theta.copy(), 'prior': self.prior, 'd': self.d,
                'buffer_size': len(self.buffer)}

    def predict(self, observation, action, evaluation=False, candidate=None):
        assert self.pending is None
        xhat = observation if self.prior is None else self.prior + .5*(observation-self.prior)
        z = xhat if self.teaching else observation
        query = xhat + (math.pi if evaluation and self.variant == 'misaligned' else 0.)
        baseline = self.model_gain(self.theta, query) if self.feedback_on else .55
        raw_loop = baseline + self.d
        self.costs['loop_gain_clips'] += int(raw_loop < .1 or raw_loop > 1.)
        pred = .2 * clip(raw_loop, .1, 1.) * action
        result = {'xhat': xhat, 'z': z, 'b': baseline, 'loop_prediction': pred,
                  'curve_prediction': .2*self.model_gain(self.theta, xhat)*action}
        if candidate is not None:
            result['selection_incumbent'] = .2*self.model_gain(self.theta, z)*action
            result['selection_candidate'] = .2*self.model_gain(candidate, z)*action
            self.costs['selection_scores'] += 2
        self.pending = {**result, 'action': action, 'evaluation': evaluation}
        return result

    def observe_target(self, target, stage):
        assert self.pending is not None
        row = self.pending
        assert row['evaluation'] == (stage == 'evaluation')
        self.prior = row['xhat'] + row['loop_prediction']
        raw_d = .8*self.d + .2*(row['action']*target/.2-row['b'])
        self.costs['local_clips'] += int(abs(raw_d) > .4)
        self.d = clip(raw_d, -.4, .4)
        self.costs['local_updates'] += 1
        if stage == 'main':
            assert len(self.buffer) < 480
            self.buffer.append([row['z'], row['action'], target])
        if self.variant == 'online' and stage != 'evaluation':
            f = [.2*row['action']*v for v in phi(row['z'])]
            residual = dot(f, self.theta)-target
            scale = .05/(1+dot(f, f))
            raw = [w-scale*(2*f[i]*residual+2*RIDGE*(w-THETA0[i]))
                   for i, w in enumerate(self.theta)]
            self.costs['coefficient_clips'] += sum(abs(w) > 1. for w in raw)
            self.theta = [clip(w, -1., 1.) for w in raw]
            self.costs['online_updates'] += 1
        self.pending = None
        assert all(math.isfinite(v) for v in self.theta + [self.d, self.prior])

    def propose(self):
        assert self.pending is None and self.variant != 'online'
        proposal = fit(self.buffer)
        self.costs['fits'] += 1
        self.costs['fit_rows'] += len(self.buffer)
        self.costs['coefficient_clips'] += sum(abs(w) > 1 for w in proposal['raw'])
        return proposal

    def select(self, proposal, predictions, targets):
        e0 = statistics.mean((p['selection_incumbent']-r)**2 for p, r in zip(predictions, targets))
        e1 = statistics.mean((p['selection_candidate']-r)**2 for p, r in zip(predictions, targets))
        accepted = e1 <= .99*e0 and e0-e1 > 1e-6
        if accepted:
            self.theta = proposal['theta'].copy()
        return {'incumbent_mse': e0, 'candidate_mse': e1,
                'gain': e0-e1, 'accepted': accepted}


def world(seed):
    base = 100000+10000*seed
    layout, actions, process, position, motion = [random.Random(base+i) for i in range(1, 6)]
    starts = list(range(20)); layout.shuffle(starts)
    regimes = list(REGIMES)*5; layout.shuffle(regimes)
    s_starts = list(range(4)); layout.shuffle(s_starts)
    s_regimes = list(REGIMES); layout.shuffle(s_regimes)
    e_starts = [0, 2, 5, 7, 10, 12, 15, 17]; layout.shuffle(e_starts)
    e_regimes = list(REGIMES)*2; layout.shuffle(e_regimes)
    schedule = []
    for i in range(20):
        schedule.append(('main', i, 2*math.pi*starts[i]/20, regimes[i]))
        if (i+1) % 5 == 0:
            j = i//5
            schedule.append(('selection', j, 2*math.pi*(s_starts[j]+.25)/4, s_regimes[j]))
    schedule.extend(('evaluation', i, 2*math.pi*(e_starts[i]+.5)/20, e_regimes[i])
                    for i in range(8))
    episodes = []
    for stage, index, x0, regime in schedule:
        action_list = []
        for _ in range(2):
            block = [-1]*6 + [1]*6
            actions.shuffle(block)
            action_list.extend(block)
        x, records = x0, []
        for t, a in enumerate(action_list):
            eps = process.gauss(0, .002)
            eta = position.gauss(0, .01 if regime[0] == 'L' else .12)
            zeta = motion.gauss(0, .005 if regime[1] == 'L' else .04)
            next_x = x+.2*true_gain(x)*a+eps
            records.append({'t': t, 'x': x, 'next_x': next_x,
                            'o': x+eta, 'a': a, 'r': next_x-x+zeta,
                            'epsilon': eps, 'eta': eta, 'zeta': zeta})
            x = next_x
        episodes.append({'stage': stage, 'index': index, 'regime': regime,
                         'x0': x0, 'records': records})
    return episodes


def errors(events, records):
    return {
        'position_mse': statistics.mean((e['prediction']['xhat']-r['x'])**2
                                        for e, r in zip(events, records)),
        'loop_mse': statistics.mean((e['prediction']['loop_prediction']-r['r'])**2
                                    for e, r in zip(events, records)),
        'curve_motion_mse': statistics.mean((e['prediction']['curve_prediction']-r['r'])**2
                                            for e, r in zip(events, records)),
        'max_position_error': max(abs(e['prediction']['xhat']-r['x'])
                                  for e, r in zip(events, records))}


def run(episodes, seed, variant):
    learner = Learner(variant)
    logs, final_theta, final_buffer = [], None, None
    for episode in episodes:
        stage = episode['stage']
        if stage == 'evaluation' and final_theta is None:
            final_theta, final_buffer = learner.theta.copy(), copy.deepcopy(learner.buffer)
        proposal = learner.propose() if stage == 'selection' and variant != 'online' else None
        learner.start_episode()
        log = {'stage': stage, 'index': episode['index'], 'before': learner.state(),
               'proposal': proposal, 'events': []}
        for row in episode['records']:
            before = learner.state()
            prediction = learner.predict(row['o'], row['a'], stage == 'evaluation',
                                         proposal['theta'] if proposal else None)
            learner.observe_target(row['r'], stage)
            log['events'].append({'before': before, 'prediction': prediction, 'after': learner.state()})
            if stage == 'evaluation':
                assert learner.theta == final_theta and learner.buffer == final_buffer
        log['decision'] = (learner.select(proposal, [e['prediction'] for e in log['events']],
                                         [r['r'] for r in episode['records']]) if proposal else None)
        log['after'] = learner.state()
        log['metrics'] = errors(log['events'], episode['records'])
        logs.append(log)
    grid = []
    for i in range(32):
        x = 2*math.pi*(i+.5)/32
        grid.append({'x': x, 'truth': true_gain(x), 'prediction': gain(learner.theta, x),
                     'initial': gain(THETA0, x)})
    by_regime = {}
    for regime in REGIMES:
        pairs = [(log, ep) for log, ep in zip(logs, episodes)
                 if ep['stage'] == 'evaluation' and ep['regime'] == regime]
        by_regime[regime] = errors([e for log, _ in pairs for e in log['events']],
                                   [r for _, ep in pairs for r in ep['records']])
    test_logs = [log for log in logs if log['stage'] == 'evaluation']
    test_eps = [ep for ep in episodes if ep['stage'] == 'evaluation']
    metrics = errors([e for log in test_logs for e in log['events']],
                     [r for ep in test_eps for r in ep['records']])
    metrics.update({'by_regime': by_regime,
                    'noisy_position_mse': statistics.mean(by_regime[k]['position_mse'] for k in ('HL','HH')),
                    'gain_mse': statistics.mean((r['prediction']-r['truth'])**2 for r in grid),
                    'initial_gain_mse': statistics.mean((r['initial']-r['truth'])**2 for r in grid),
                    'accepted': sum(bool(log['decision'] and log['decision']['accepted']) for log in logs)})
    return {'seed': seed, 'variant': variant, 'episodes': logs, 'theta': learner.theta,
            'grid': grid, 'metrics': metrics, 'costs': learner.costs,
            'final_buffer': learner.buffer}


def comparisons(runs):
    rows = []
    for seed in range(5):
        m = {r['variant']: r['metrics'] for r in runs if r['seed'] == seed}
        f, nf, nt, dc = (m[k] for k in ('full','no_feedback','no_teaching','disconnected'))
        checks = {
            'feedback': f['noisy_position_mse'] <= .9*nf['noisy_position_mse'],
            'teaching': f['gain_mse'] <= .9*nt['gain_mse'],
            'joint': all(f['by_regime']['HH']['loop_mse'] <= .9*c['by_regime']['HH']['loop_mse']
                         for c in (nf, nt))}
        interaction = {k: nf[k]+nt[k]-f[k]-dc[k]
                       for k in ('position_mse','loop_mse','curve_motion_mse','gain_mse')}
        rows.append({'seed': seed, 'criteria': checks, 'all_three': all(checks.values()),
                     'interaction': interaction})
    means = {}
    for name in VARIANTS:
        ms = [r['metrics'] for r in runs if r['variant'] == name]
        means[name] = {k: statistics.mean(m[k] for m in ms)
                       for k in ('position_mse','loop_mse','curve_motion_mse','gain_mse','noisy_position_mse')}
        means[name]['LL_loop_mse'] = statistics.mean(m['by_regime']['LL']['loop_mse'] for m in ms)
        means[name]['HH_loop_mse'] = statistics.mean(m['by_regime']['HH']['loop_mse'] for m in ms)
    f,nf,nt,dc = (means[k] for k in ('full','no_feedback','no_teaching','disconnected'))
    pooled = {'feedback': f['noisy_position_mse'] <= .9*nf['noisy_position_mse'],
              'teaching': f['gain_mse'] <= .9*nt['gain_mse'],
              'joint': f['HH_loop_mse'] <= .9*nf['HH_loop_mse'] and f['HH_loop_mse'] <= .9*nt['HH_loop_mse'],
              'clean_guard': f['LL_loop_mse'] <= 1.05*dc['LL_loop_mse']}
    counts = {k: sum(r['criteria'][k] for r in rows) for k in ('feedback','teaching','joint')}
    return {'per_seed': rows, 'means': means, 'pooled': pooled, 'pass_counts': counts,
            'all_three_count': sum(r['all_three'] for r in rows),
            'complementarity_pass': all(pooled.values()) and all(v >= 4 for v in counts.values())}


def hashes():
    files = ('experiments/complementary_roles_protocol.md','experiments/complementary_roles.py',
             'experiments/plot_complementary_roles.py','checks/test_complementary_roles.py',
             'checks/audit_complementary_roles.py')
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files}


def report(runs, comparison):
    lines = ['# Experiment 007 results', '',
             'All errors below are mean squared errors. Lower is better. No tuning.', '',
             '| Condition | Seed | Position | Motion | Curve-only motion | Retained curve | Accepted |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in runs:
        m = r['metrics']
        lines.append(f"| {r['variant']} | {r['seed']} | {m['position_mse']:.8f} | "
                     f"{m['loop_mse']:.8f} | {m['curve_motion_mse']:.8f} | {m['gain_mse']:.8f} | {m['accepted']} |")
    lines += ['', '## Registered criteria', '',
              f"Full complementarity criterion: **{comparison['complementarity_pass']}**.", '',
              '| Criterion | Seeds passing | Pooled criterion |', '| --- | ---: | --- |']
    for k in ('feedback','teaching','joint'):
        lines.append(f"| {k} | {comparison['pass_counts'][k]}/5 | {comparison['pooled'][k]} |")
    lines += ['', f"Clean-regime pooled guard: {comparison['pooled']['clean_guard']}.",
              f"Seeds passing all three directional/joint conditions: {comparison['all_three_count']}/5.", '',
              '## Sensor strata', '',
              '| Condition | Regime | Position MSE | Motion MSE | Curve-only MSE |',
              '| --- | --- | ---: | ---: | ---: |']
    for name in VARIANTS:
        for regime in REGIMES:
            ms = [r['metrics']['by_regime'][regime] for r in runs if r['variant'] == name]
            values = [statistics.mean(m[k] for m in ms) for k in ('position_mse','loop_mse','curve_motion_mse')]
            lines.append(f"| {name} | {regime} | " + ' | '.join(f'{v:.8f}' for v in values) + ' |')
    lines += ['', '## Factorial interaction, per seed', '',
              'Positive values indicate superadditive loss reduction on that metric.', '',
              '| Seed | Position | Motion | Curve-only motion | Retained curve |',
              '| --- | ---: | ---: | ---: | ---: |']
    for row in comparison['per_seed']:
        lines.append(f"| {row['seed']} | " + ' | '.join(f'{v:.8g}' for v in row['interaction'].values()) + ' |')
    lines += ['', '## Costs and clipping', '',
              '| Condition | Fits | Rows replayed | Online updates | Gain calls | Gain clips | Loop clips | Local clips | Coefficient clips |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for name in VARIANTS:
        totals = {k: sum(r['costs'][k] for r in runs if r['variant'] == name) for k in runs[0]['costs']}
        keys = ('fits','fit_rows','online_updates','gain_calls','gain_clips','loop_gain_clips','local_clips','coefficient_clips')
        lines.append(f'| {name} | ' + ' | '.join(str(totals[k]) for k in keys) + ' |')
    lines += ['', '23,040 transitions and motion outcomes; 23,040 position measurements.',
              '960 final and 960 initial-reference curve queries are evaluator-only.',
              'See findings.md for interpretation and verification; metrics.json for every stratum and cost.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'results/complementary-roles-v1')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    provenance = hashes()
    worlds = [{'seed': seed, 'episodes': world(seed)} for seed in range(5)]
    runs = [run(w['episodes'], w['seed'], variant) for w in worlds for variant in VARIANTS]
    comparison = comparisons(runs)
    assert provenance == hashes()
    result = {'hashes': provenance, 'worlds': worlds, 'runs': runs, 'comparisons': comparison,
              'transitions': 23040, 'position_measurements': 23040,
              'final_curve_queries': 960, 'reference_curve_queries': 960}
    (args.output/'results.json').write_text(json.dumps(result, separators=(',',':'))+'\n')
    metrics = {'runs': [{k:r[k] for k in ('seed','variant','theta','metrics','costs','grid')} for r in runs],
               'comparisons': comparison}
    (args.output/'metrics.json').write_text(json.dumps(metrics, indent=2)+'\n')
    (args.output/'report.md').write_text(report(runs, comparison))
    print(f'Saved 30 runs, 23,040 transitions to {args.output}')
    print(json.dumps({'pass_counts': comparison['pass_counts'], 'pooled':comparison['pooled'],
                      'complementarity_pass':comparison['complementarity_pass']}))


if __name__ == '__main__':
    main()
