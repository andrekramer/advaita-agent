"""016: replay saved worlds through the shared core; never generate new worlds."""
import argparse
import copy
import gzip
import hashlib
import importlib
import io
import json
from pathlib import Path
import sys
import time
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'experiments'), str(ROOT/'checks')]
from advaita import local, models, policies, projection
from advaita.runtime import NestedLearner
from advaita.state import canonical

FOLDERS = ('interfaces-v1', 'nested-abstractions-v1', 'reclosure-v1', 'form-retention-v1')
MODULES = ('interfaces', 'nested_abstractions', 'reclosure', 'form_retention')
EXPECTED_COUNTS = (90, 120, 80, 90)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def verify_old_manifests():
    for folder in ('bundles-v1', 'bundle-retention-v1')+FOLDERS:
        for name, sha in json.loads((ROOT/'results'/folder/'manifest.json').read_text()).items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == sha, name


def source_hashes():
    files = list((ROOT/'advaita').glob('*.py'))
    files += [ROOT/p for p in ('experiments/consolidation_core_spec.md',
              'experiments/consolidation_round_plan.md', 'checks/consolidation_compatibility.py',
              'checks/audit_consolidation_core.py', 'checks/test_consolidation_core.py')]
    # Freeze the old code used by drivers/auditors and the exact saved references.
    for folder in ('bundles-v1', 'bundle-retention-v1')+FOLDERS:
        manifest = ROOT/'results'/folder/'manifest.json'
        files.append(manifest)
        files += [ROOT/p for p in json.loads(manifest.read_text())]
    files += [ROOT/'results'/f/'results.json' for f in FOLDERS]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files))}


def no_generator(*args, **kwargs):
    raise AssertionError('C0 must use saved observations, not generate benchmarks')


def bind_driver(module, overrides):
    """Clone pure driver functions into a private namespace; originals untouched."""
    namespace = dict(vars(module))
    for name, value in vars(module).items():
        if isinstance(value, types.FunctionType) and value.__module__ == module.__name__:
            namespace[name] = types.FunctionType(value.__code__, namespace, value.__name__,
                                                 value.__defaults__, value.__closure__)
    namespace.update(overrides)
    namespace['generate'] = no_generator
    return namespace


def drivers():
    old = [importlib.import_module(n) for n in MODULES]
    nested = bind_driver(old[1], dict(LocalModel=models.LocalModel, LocalLearner=local.LocalLearner,
        Upper=models.Upper, InterfaceView=models.InterfaceView, view_for=models.view_for,
        upper_review=policies.upper_review))
    interface = bind_driver(old[0], dict(Model=models.ProjectionModel, Acquisition=projection.AcquisitionLearner,
        VisibleInput=models.VisibleInput, Boundary=projection.Boundary, Learner=projection.MemoryLearner))
    reclosure = bind_driver(old[2], dict(LocalLearner=local.LocalLearner, Upper=models.Upper,
        upper_review=policies.upper_review, view_for=models.view_for, Reclosure=policies.Reclosure,
        restore_upper=models.restore_upper, evaluate=nested['evaluate']))
    retention = bind_driver(old[3], dict(Learner=local.ProtectedLearner, LocalModel=models.LocalModel,
        LocalLearner=local.LocalLearner, Retention=policies.Retention, restore=models.restore_local))
    for namespace, names in ((interface, ('Model', 'Acquisition', 'Learner')),
                             (nested, ('LocalModel', 'LocalLearner', 'Upper')),
                             (reclosure, ('LocalLearner', 'Upper', 'Reclosure')),
                             (retention, ('Learner', 'Retention', 'LocalModel'))):
        for name in names:
            assert namespace[name].__module__.startswith('advaita.'), name
    return interface, nested, reclosure, retention


def runtime_reclosure(w, variant, ps, driver):
    """Replay 014 through the new continuing coordinator, not the old run loop."""
    learner = NestedLearner([64000+2*ps+j for j in range(2)], reclose=variant == 'reclose')
    warm = []
    for i in range(256):
        for j in range(2):
            learner.observe_local(j, f'warm/{j}/{i}', w['local_main'][j][i])
        if (i+1) % 64 == 0:
            warm.append([learner.review_local(j, [f'warm-select/{j}/{i}/{k}' for k in range(32)],
                                               w['local_selection'][i//64][j]) for j in range(2)])
    learner.train_upper([f'composition/{i}' for i in range(256)], w['composition'])
    initial = learner.upper.state()
    transfer = driver['evaluate'](learner.upper, learner.models(), w, False)
    predictions, reads, reviews = [], [], []
    for t, row in enumerate(w['main'], 1):
        p, raw = learner.step(f'main/{t}', row)
        predictions.append(p)
        reads.append(raw)
        if t % 64 == 0:
            rev = dict(index=t, **learner.review(f'select/{t}', w['selection'][t//64-1]))
            before = (learner.upper.state(), [n.model.state() for n in learner.nodes])
            rev['evaluation'] = driver['evaluate'](learner.upper, learner.models(), driver['effective_world'](w, t), True)
            assert before == (learner.upper.state(), [n.model.state() for n in learner.nodes])
            reviews.append(rev)
    costs = {k: sum(n.costs[k] for n in learner.nodes) for k in learner.nodes[0].costs}
    costs.update(upper_refits=learner.costs['upper_refits'], upper_refit_rows=learner.costs['upper_refit_rows'],
                 upper_candidate_fits=learner.costs['upper_candidate_fits'],
                 upper_candidate_rows=learner.costs['upper_candidate_rows'],
                 feedback_labels=len(learner.ledger.main)+len(learner.ledger.selection),
                 prediction_raw_reads=learner.costs['raw_reads'])
    costs.update(learner.reclosure.costs)
    r = dict(seed=w['seed'], branch=w['branch'], variant=variant, proposal_seed=ps,
        warmup=warm, initial_upper=initial, transfer=transfer, predictions=predictions,
        raw_reads=reads, reviews=reviews, final_upper=learner.upper.state(),
        final_local=[n.model.state() for n in learner.nodes], pending=learner.reclosure.state(), costs=costs)
    r['metrics'] = driver['metrics'](r, w)
    evidence = dict(main_labels=len(learner.ledger.main), selection_labels=len(learner.ledger.selection),
        selection_reuses=sum(len(u['reused']) for u in learner.ledger.uses if u['kind'] == 'selection'),
        events=len(learner.events))
    return r, evidence


def mismatch(a, b, path='run'):
    if type(a) != type(b) and not isinstance(a, (int, float)):
        return f'{path}: types {type(a).__name__} / {type(b).__name__}'
    if isinstance(a, dict):
        if a.keys() != b.keys():
            return f'{path}: keys differ'
        for key in a:
            result = mismatch(a[key], b[key], path+'/'+str(key))
            if result:
                return result
    elif isinstance(a, list):
        if len(a) != len(b):
            return f'{path}: lengths {len(a)} / {len(b)}'
        for i, (x, y) in enumerate(zip(a, b)):
            result = mismatch(x, y, path+'/'+str(i))
            if result:
                return result
    elif a != b:
        return f'{path}: {a!r} / {b!r}'
    return None


def label_use(folder, r):
    if folder == 'interfaces-v1':
        return 1152+r['costs']['selection_outcomes']
    return r['costs'].get('feedback_labels', r['costs'].get('used_labels'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'results/consolidation-core-v1')
    args = parser.parse_args()
    verify_old_manifests()
    args.output.mkdir(parents=True, exist_ok=False)
    provenance = source_hashes()
    (args.output/'manifest.json').write_text(json.dumps(provenance, indent=2)+'\n')
    import test_consolidation_core as tests
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
    (args.output/'tests.txt').write_text(stream.getvalue())
    assert result.wasSuccessful(), stream.getvalue()
    assert tests.FIXTURE_LABELS*2 <= 20000  # Includes the preceding development test invocation.
    summary = dict(status='running', tests=result.testsRun,
                   fixture_labels_this_invocation=tests.FIXTURE_LABELS,
                   fixture_labels_including_development=tests.FIXTURE_LABELS*2,
                   new_benchmark_labels=0, compatibility_attempt=1, groups=[], runs=[])
    bound = drivers()
    start = time.monotonic()
    try:
        with gzip.open(args.output/'replayed-runs.jsonl.gz', 'wt') as output:
            for folder, driver, count in zip(FOLDERS, bound, EXPECTED_COUNTS):
                data = json.loads((ROOT/'results'/folder/'results.json').read_text())
                worlds = {(w['seed'], w['branch']): w for w in data['worlds']}
                assert len(data['runs']) == count
                used = 0
                for saved in data['runs']:
                    world = worlds[saved['seed'], saved['branch']]
                    evidence = None
                    if folder == 'reclosure-v1':
                        replayed, evidence = runtime_reclosure(world, saved['variant'], saved['proposal_seed'], driver)
                    else:
                        replayed = driver['run'](world, saved['variant'], saved['proposal_seed'])
                    error = mismatch(saved, replayed)
                    assert error is None, (folder, saved['seed'], saved['proposal_seed'], saved['variant'], error)
                    output.write(canonical(dict(experiment=folder, run=replayed))+'\n')
                    record = dict(experiment=folder, seed=saved['seed'], branch=saved['branch'],
                                  variant=saved['variant'], proposal_seed=saved['proposal_seed'],
                                  reference_sha256=digest(saved), replay_sha256=digest(replayed))
                    if evidence is not None:
                        record['runtime_evidence'] = evidence
                    summary['runs'].append(record)
                    used += label_use(folder, saved)
                summary['groups'].append(dict(experiment=folder, runs=count, exact_matches=count,
                                              replayed_used_label_presentations=used))
                print(f'{folder}: {count}/{count} complete traces exactly equal', flush=True)
        verify_old_manifests()
        assert source_hashes() == provenance
        summary.update(status='pass', elapsed_seconds=time.monotonic()-start,
            replayed_used_label_presentations=sum(g['replayed_used_label_presentations'] for g in summary['groups']),
            replay_file_sha256=hashlib.sha256((args.output/'replayed-runs.jsonl.gz').read_bytes()).hexdigest())
    except Exception as exc:
        summary.update(status='failed', error=str(exc), elapsed_seconds=time.monotonic()-start)
        raise
    finally:
        (args.output/'compatibility.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(f"PASS: {len(summary['runs'])} exact traces, {summary['tests']} tests, no new benchmark labels", flush=True)


if __name__ == '__main__':
    main()
