"""One-shot capacity withdrawal in three paired histories."""
import copy
import json
import statistics

import managed_growth as pilot

OUT = pilot.ROOT / 'results/managed-growth-release-v1'
END = 1024
HISTORIES = ('lasting_return', 'persistent_shift', 'short_return')
ARMS = ('keep', 'timer', 'monitor')
WINDOWS = dict(prior=(385, 640), early=(641, 832), late=(833, END),
               entire_return=(641, END), after_short=(769, END))


def world_rows(history, maps, stream, batches):
    """Complement B's binary draw to couple .9 and .1 futures."""
    def adjust(t, row):
        flip = (history == 'persistent_shift' and t > 640 or
                history == 'short_return' and t > 768)
        if not flip or not maps[0][row['x'][0]]:
            return row
        return dict(row, local=[1-row['local'][0], row['local'][1]], y=1-row['y'])
    return ({t: adjust(t, r) for t, r in stream.items()},
            {t: [adjust(t, r) for r in rs] for t, rs in batches.items()})


def branch(prefix, opening, arm, maps, stream, batches):
    engine = copy.deepcopy(prefix)
    engine.budget = 4 if opening else 3
    streak = 0
    release = None
    reviews = []
    blocks = []
    for tick in range(pilot.DECIDE, END+1):
        if tick > pilot.DECIDE:
            row = stream[tick]
            ps = engine.observe(tick, row)
            for j in (0, 1):
                source = 2*j + maps[j][row['x'][j]]
                blocks[-1]['sums'][source] += (ps[j]-row['local'][j])**2
                blocks[-1]['counts'][source] += 1
        if tick % 64:
            continue
        gain = None
        if tick > pilot.DECIDE and engine.budget == 3 and arm == 'reversible' and release is not None:
            gain = pilot.inspection(engine)['predicted_gain']
            if gain > .01:
                engine.budget = 4
                streak = 0
        elif tick > pilot.DECIDE and engine.budget == 4:
            if arm in ('monitor', 'reversible'):
                gain = pilot.inspection(engine)['predicted_gain']
                streak = streak + 1 if gain <= .01 else 0
            if (arm == 'timer' and tick == 768) or (arm in ('monitor', 'reversible') and streak == 2):
                engine.budget = 3
                release = tick
        engine.review(tick, batches[tick])
        memberships = pilot.parts(engine)
        assert sum(len(set(part)) for part in memberships) <= engine.budget
        reviews.append(dict(tick=tick, budget=engine.budget, gain=gain, partitions=memberships))
        if tick < END:
            blocks.append(dict(start=tick+1, sums=[0.]*4, counts=[0]*4))
    return dict(release=release, reviews=reviews, blocks=blocks)


def cases(seed, arms=ARMS, histories=HISTORIES):
    maps, stream, batches = pilot.make_world(seed, True, end=END)
    core = pilot.StructuralLearner([3*seed, 3*seed+1], 3*seed+2)
    core.train_upper([], [])
    prefix = pilot.BudgetLearner(core, 'shadow')
    for t in range(1, pilot.DECIDE+1):
        prefix.observe(t, stream[t])
        if t in batches and t < pilot.DECIDE:
            prefix.review(t, batches[t])
    opening = pilot.inspection(prefix)
    for history in histories:
        main, selection = world_rows(history, maps, stream, batches)
        branches = {arm:branch(prefix, opening['permit'], arm, maps, main, selection) for arm in arms}
        yield dict(seed=seed, history=history, maps=maps, opening=opening, arms=branches)


def scores(arm, window):
    lo, hi = WINDOWS[window]
    blocks = [b for b in arm['blocks'] if lo <= b['start'] <= hi]
    sums = [sum(b['sums'][i] for b in blocks) for i in range(4)]
    counts = [sum(b['counts'][i] for b in blocks) for i in range(4)]
    assert sum(counts[:2]) == sum(counts[2:]) == hi-lo+1
    return [s/n for s,n in zip(sums,counts)] + [sum(sums)/sum(counts)]


def summarize(records):
    out = {}
    for history in HISTORIES:
        rows = [c for c in records if c['history'] == history]
        result = dict(grants=sum(c['opening']['permit'] for c in rows))
        for arm in ('monitor','timer'):
            events = [c['arms'][arm]['release'] for c in rows]
            data = dict(release_ticks={str(t): events.count(t) for t in events})
            for window in WINDOWS:
                gains = [[a-b for a,b in zip(scores(c['arms']['keep'],window),
                                             scores(c['arms'][arm],window))] for c in rows]
                fields = {}
                for i, name in enumerate(('A','B','C','D','overall')):
                    values = [g[i] for g in gains]
                    fields[name] = dict(mean=statistics.mean(values), worst=min(values))
                    if window in ('entire_return','after_short') and name in ('B','overall'):
                        fields[name]['interval'] = pilot.interval(values)[1:]
                data[window] = fields
            result[arm] = data
        out[history] = result
    return out


if __name__ == '__main__':
    records = [c for seed in range(4200,4224) for c in cases(seed)]
    OUT.mkdir(exist_ok=True)
    (OUT/'cases.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in records))
    (OUT/'summary.json').write_text(json.dumps(summarize(records),indent=2)+'\n')
