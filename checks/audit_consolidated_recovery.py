"""019 independent replay and metrics; no learner or experiment imports."""
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import signal
from statistics import mean
import time

from audit_structural_consolidation import verify_world, verify_run, verify_metrics, good, label, close, logloss

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/consolidated-recovery-v1'
BRANCHES = ('forms', 'detail', 'reversed')
VARIANTS = ('integrated', 'delete', 'raw', 'fixed')


def verify_recovery(r, w):
    saved = r['recovery']
    short = dict(r, predictions=r['predictions'][:768], raw_reads=r['raw_reads'][:768],
        reviews=[v for v in r['reviews'] if v['index'] <= 768], metrics=saved['reference_768'])
    verify_metrics(short, dict(w, main=w['main'][:768]))
    cs = []
    for v in r['reviews']:
        e = v['evaluation']
        spec = [1, 1]
        if w['branch'] == 'forms' and 241 <= v['index'] <= 528: spec[w['affected']] = 0
        if w['branch'] != 'forms' and not 241 <= v['index'] <= 528: spec[w['affected']] = 2
        cs.append(dict(index=v['index'], predictive=e['accuracy'] == 1 and e['regret'] <= .10,
            full=good(e), structural=good(e) and e['spec'] == spec and e['sufficient_minimal']))
    tail = [c for c in cs if c['index'] >= 1024]
    assert [c['index'] for c in tail] == [1024, 1088, 1152, 1216, 1280]
    captures, retrieves = [], []
    for v in r['reviews']:
        u = v['upper']
        if u is None: continue
        if u['action'] == 'retrieved': retrieves.append(v['index'])
        if u['captured'] is not None and u['archive_after'] is not None:
            ids = u['archive_after']['record_ids']
            indices = sorted(int(i.split('/')[1]) for i in ids if i.startswith('main/'))
            captures.append(dict(index=v['index'], main_first=indices[0] if indices else None,
                main_last=indices[-1] if indices else None, construction_labels=len(ids),
                contains_pre_simplification=bool(indices and indices[0] <= 240) or any(i.startswith('composition/') for i in ids)))
    expected = dict(reference_768=saved['reference_768'], checkpoints=[c for c in cs if c['index'] in (768, 1024, 1280)],
        stable_predictive=all(c['predictive'] for c in tail), stable_full=all(c['full'] for c in tail),
        stable_structural=good(r['transfer']) and all(c['structural'] for c in tail),
        late_raw_reads=sum(r['raw_reads'][1024:]), captures=captures, retrievals=retrieves)
    for name, start in [('return', 529), ('late', 1025)]:
        observed, latent = [], []
        for t in range(start, 1281):
            p, row = r['predictions'][t-1], w['main'][t-1]
            y = label(w, row['x'], row['a'], t)
            observed.append(logloss(p, row['y']))
            latent.append(.9*logloss(p, y)+.1*logloss(p, 1-y))
        expected[name+'_observed'], expected[name+'_latent'] = mean(observed), mean(latent)
    close(saved, expected)


def verify_summary(runs, saved):
    groups = []
    for b, v in itertools.product(BRANCHES, VARIANTS):
        ms = [r['recovery'] for r in runs if r['branch'] == b and r['variant'] == v]
        assert len(ms) == 10
        g = dict(branch=b, variant=v, runs=10)
        for field in ('stable_predictive', 'stable_full', 'stable_structural'):
            g[field] = sum(m[field] for m in ms)
        for field, source in [('transfer_valid', 'transfer_valid'), ('trajectory_768', 'trajectory')]:
            g[field] = sum(m['reference_768'][source] for m in ms)
        g['checkpoints'] = []
        for i, t in enumerate((768, 1024, 1280)):
            g['checkpoints'].append(dict(index=t, **{k: sum(m['checkpoints'][i][k] for m in ms)
                for k in ('predictive', 'full', 'structural')}))
        for field in ('return_observed', 'return_latent', 'late_observed', 'late_latent', 'late_raw_reads'):
            g[field] = mean(m[field] for m in ms)
        for field in ('captures', 'retrievals'): g[field] = sum(len(m[field]) for m in ms)
        groups.append(g)
    pairs = []
    for s, p, b in sorted(set((r['seed'], r['proposal_seed'], r['branch']) for r in runs)):
        rs = {r['variant']: r for r in runs if (r['seed'], r['proposal_seed'], r['branch']) == (s, p, b)}
        a, d = rs['integrated']['recovery'], rs['delete']['recovery']
        item = dict(seed=s, proposal_seed=p, branch=b,
            identical_predictions=all(x == y for x, y in zip(rs['integrated']['predictions'], rs['delete']['predictions'])),
            early_return_gain=d['reference_768']['return_observed']-a['reference_768']['return_observed'],
            late_read_saving=rs['raw']['recovery']['late_raw_reads']-a['late_raw_reads'])
        for field in ('return_observed', 'return_latent', 'late_observed', 'late_latent'):
            item[field+'_gain'] = d[field]-a[field]
        pairs.append(item)
    envs = []
    for s, b in sorted(set((r['seed'], r['branch']) for r in runs)):
        gains = [p['return_observed_gain'] for p in pairs if (p['seed'], p['branch']) == (s, b)]
        structural = [r['recovery']['stable_structural'] for r in runs if (r['seed'], r['branch'], r['variant']) == (s, b, 'integrated')]
        envs.append(dict(seed=s, branch=b, proposals=len(gains), return_gain=mean(gains), stable_structural=sum(structural)))
    representation = {b: sum(r['recovery']['stable_structural'] for r in runs if r['branch'] == b and r['variant'] == 'integrated') >= 8 for b in BRANCHES}
    ds = [p['return_observed_gain'] for p in pairs if p['branch'] == 'detail']
    rs = [p['return_observed_gain'] for p in pairs if p['branch'] == 'reversed']
    memory = dict(mean_gain=mean(ds) >= .02, improving_pairs=sum(x > 0 for x in ds) >= 8, reversed_cost=mean(rs) >= -.02)
    close(saved, dict(groups=groups, paired=pairs, environments=envs,
        representation_checks=representation, representation_pass=all(representation.values()),
        memory_checks=memory, memory_pass=all(memory.values())))


def main():
    started = time.monotonic()
    def timeout(*_): raise TimeoutError('600-second 019 audit limit')
    signal.signal(signal.SIGALRM, timeout); signal.alarm(600)
    try:
        manifest = json.loads((OUT/'manifest.json').read_text())
        for name, digest in manifest.items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
        data = json.loads((OUT/'results.json').read_text())
        assert data['hashes'] == manifest and data['status'] == 'completed_pending_audit'
        worlds = json.loads((OUT/'worlds.json').read_text())
        lookup = {(w['seed'], w['branch']): w for w in worlds}
        assert len(worlds) == 15 and set(lookup) == set(itertools.product(range(800, 805), BRANCHES))
        for w in worlds:
            assert list(map(len, w['local_main'])) == [256]*2 and len(w['local_selection']) == 4
            assert all(list(map(len, b)) == [32]*2 for b in w['local_selection'])
            assert len(w['composition']) == 256 and len(w['main']) == 1280 and list(map(len, w['selection'])) == [32]*20
            verify_world(w)
        with gzip.open(OUT/'runs.jsonl.gz', 'rt') as stream: runs = [json.loads(line) for line in stream]
        assert len(runs) == 120 and {(r['seed'], r['proposal_seed'], r['branch'], r['variant']) for r in runs} == set(itertools.product(range(800, 805), (800, 801), BRANCHES, VARIANTS))
        for i, r in enumerate(runs, 1):
            with gzip.open(OUT/r['checkpoint_file'], 'rt') as stream: checkpoint = json.load(stream)
            verify_run(r, lookup[r['seed'], r['branch']], checkpoint, measure=False)
            verify_recovery(r, lookup[r['seed'], r['branch']])
            assert r['costs']['feedback_labels'] == {'integrated': 6784, 'delete': 6784, 'fixed': 5504, 'raw': 2304}[r['variant']]
            if i % 24 == 0: print(f'{i}/120 extended traces, checkpoints and metrics verified', flush=True)
        for seed in range(800, 805):
            d, rev = lookup[seed, 'detail'], lookup[seed, 'reversed']
            assert d['main'][:528] == rev['main'][:528] and d['selection'][:8] == rev['selection'][:8]
            for ps in (800, 801):
                rs = [r for r in runs if (r['seed'], r['proposal_seed']) == (seed, ps)]
                assert all(r['warmup'] == rs[0]['warmup'] for r in rs)
        verify_summary(runs, data['summary'])
        es = [e for r in runs for e in [r['transfer'], *r['endpoints'], *(v['evaluation'] for v in r['reviews'])]]
        totals = dict(runs=120, allocated_labels=814080, generated_labels=101760,
            used_labels=sum(r['costs']['feedback_labels'] for r in runs),
            candidate_fits=sum(r['costs']['candidate_fits']+r['costs']['upper_candidate_fits'] for r in runs),
            scoring_queries=sum(r['costs']['scoring_queries'] for r in runs), composite_predictions=153600,
            local_predictions=230400, evaluation_predictions=sum(e['contexts'] for e in es),
            oracle_context_queries=sum(32*(1+len(e['removal_costs'])+len(e['raw_addition_gains'])) for e in es))
        close(totals, data['totals'])
        assert totals['used_labels'] == 641280 and totals['candidate_fits'] <= 26040 and totals['scoring_queries'] <= 5000000
        assert totals['evaluation_predictions'] == 91200 and totals['oracle_context_queries'] <= 460800
        assert data['elapsed_seconds'] < 600
        fixture = json.loads((ROOT/'results/consolidated-recovery-fixtures.json').read_text())
        assert fixture['status'] == 'pass' and fixture['new_learning_labels'] == 0
        result = dict(status='pass', runs=120, independently_replayed_labels=totals['used_labels'],
            elapsed_seconds=time.monotonic()-started,
            artifact_sha256={name: hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ('results.json', 'runs.jsonl.gz', 'worlds.json')})
        (OUT/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
        print('PASS: all 120 extended runs independently reconstructed and verified.')
    except Exception as exc:
        (OUT/'audit-incomplete.json').write_text(json.dumps(dict(error=repr(exc), elapsed_seconds=time.monotonic()-started), indent=2)+'\n')
        raise
    finally:
        signal.alarm(0)


if __name__ == '__main__': main()
