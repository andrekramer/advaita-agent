"""Read-only evidence descriptions and a supplied, approximate control model.

No learner mutation, world generator, random draws or future-state access here.
"""
import copy
import itertools
import json

CONTEXTS = list(itertools.product(range(4), range(4), range(2)))
ACTIONS = ('none', '0', '1', '2')
VIEWS = ('existing', 'raw_banks', 'direction_strength')


def address(models, channel, x, action):
    if channel < 2:
        return str(models['locals'][channel]['partition'][x[channel]])
    return '|'.join(map(str, [x[j] if s == 2 else models['locals'][j]['groups'][x[j]]
                             for j, s in enumerate(models['upper']['spec']) if s] + [action]))


def packet(learner, recent, target, protected):
    """Additional row-bank data are explicit; copied checkpoint is read-only."""
    before = learner.checkpoint()
    view = learner.inspect()['learning']
    state = json.loads(learner.native_checkpoint())
    models = dict(locals=view['locals'], upper=view['upper'])
    cells = []
    for j, model in enumerate(view['locals'] + [view['upper']]):
        table = {k: dict(total=list(v), fast=[0., 0.], slow=[0., 0.], recent=[0, 0])
                 for k, v in model['counts'].items()}
        for i in range(4 if j < 2 else 32):
            x = [i, i] if j < 2 else [i // 8, (i // 2) % 4]
            key = address(models, j, x, 0 if j < 2 else i % 2)
            for bank in ('fast', 'slow'):
                for k in (0, 1):
                    table[key][bank][k] += state[bank][j][i][k]
        for row in recent:
            cell = table[address(models, j, row['x'], row['a'])]
            cell['recent'][0] += row['local'][j] if j < 2 else row['y']
            cell['recent'][1] += 1
        cells.append(table)
    out = dict(models=models, cells=cells, mass=view['evidence_mass'],
               half_lives=view['half_lives'], recent_n=len(recent), target=target,
               protected=protected, review_losses=[x['losses'] for x in learner.inspect()['last_review']['weakenings']])
    assert before == learner.checkpoint()
    return copy.deepcopy(out)


def describe(full, mode):
    result = copy.deepcopy(full)
    result['encoding'] = mode
    for table in result['cells']:
        for cell in table.values():
            if mode in ('existing', 'prediction_only'):
                cell.pop('fast'); cell.pop('slow')
                if mode == 'prediction_only':
                    y, n = cell.pop('total'); cell['probability'] = (y + 1) / (n + 2)
            elif mode == 'direction_strength':
                for bank in ('fast', 'slow'):
                    y, n = cell.pop(bank)
                    cell[bank] = dict(direction=y / n if n else None, strength=n)
            elif mode != 'raw_banks':
                raise ValueError(mode)
    if mode == 'prediction_only':
        # Model counts would otherwise leak the evidence mass into this ablation.
        for m in result['models']['locals'] + [result['models']['upper']]:
            m.pop('counts')
        result.pop('mass')
    return result


def decode(view, j, cell):
    mode = view['encoding']
    if mode == 'direction_strength':
        return [[(cell[b]['direction'] or 0.) * cell[b]['strength'], cell[b]['strength']]
                for b in ('fast', 'slow')]
    if mode == 'raw_banks':
        return [cell['fast'].copy(), cell['slow'].copy()]
    if mode == 'existing':
        f, s = view['mass']['fast'][j], view['mass']['slow'][j]
        share = f / (f + s) if f + s else .5
        return [[z * share for z in cell['total']], [z * (1 - share) for z in cell['total']]]
    raise ValueError(mode)


def probe(view, action, x, a, labels):
    before, after = [], []
    for j in range(3):
        c = view['cells'][j][address(view['models'], j, x, a)]
        if view['encoding'] == 'prediction_only':
            before.append(c['probability']); after.append(c['probability']); continue
        f, s = decode(view, j, c)
        rf = 2 ** (-1 / 64); rs = 2 ** (-1 / (128 if action == str(j) else view['half_lives'][j]))
        successes, total = f[0] * rf + s[0] * rs, f[1] * rf + s[1] * rs
        before.append((successes + 1) / (total + 2))
        after.append((successes + labels[j] + 1) / (total + 3))
    return dict(before=before, after=after)


def project(view, action):
    """Plug-in expectation, not exact expected stochastic loss or native replay."""
    losses = []
    for j in range(3):
        loss = 0.
        for cell in view['cells'][j].values():
            f, s = decode(view, j, cell)
            visit = cell['recent'][1] / view['recent_n']
            q = (cell['recent'][0] + 1) / (cell['recent'][1] + 2)
            rf = 2 ** (-1 / 64); rs = 2 ** (-1 / (128 if action == str(j) else view['half_lives'][j]))
            for _ in range(64):
                f = [z * rf for z in f]; s = [z * rs for z in s]
                p = (f[0] + s[0] + 1) / (f[1] + s[1] + 2)
                loss += visit * (q * (1 - p) ** 2 + (1 - q) * p ** 2) / 64
                f[0] += visit * q; f[1] += visit
        losses.append(loss)
    return losses


def decide(view):
    losses = {a: project(view, a) for a in ACTIONS}
    t, p = view['target'], view['protected']
    eligible = [a for a in ACTIONS if losses[a][p] - losses['none'][p] <= .001]
    best = 'none'
    for a in eligible:
        if losses[a][t] < losses[best][t] - 1e-12:
            best = a
    if losses['none'][t] - losses[best][t] <= .0005:
        best = 'none'
    return dict(choice=best, losses=losses,
                gains={a: losses['none'][t] - losses[a][t] for a in ACTIONS})


def decisions(full):
    result = {mode: decide(describe(full, mode)) for mode in VIEWS}
    t = full['target']; slow, fast = full['review_losses'][t][:2]
    chosen = result['raw_banks']['choice']
    result['no_op'] = dict(choice='none')
    result['disagreement'] = dict(choice=str(t) if fast <= .55 and slow - fast > .05 else 'none')
    result['rotated'] = dict(choice='none' if chosen == 'none' else str((int(chosen) + 1) % 3))
    assert result['raw_banks']['choice'] == result['direction_strength']['choice']
    assert max(abs(result['raw_banks']['losses'][a][j] - result['direction_strength']['losses'][a][j])
               for a in ACTIONS for j in range(3)) <= 1e-12
    return result
