"""038 exact saved-run replay and deterministic composition contracts.

Run directly to save a numbered verification attempt; imports never run a study.
"""
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import signal
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from advaita.controlled import ControlledLearner
from advaita.memory_control import fit_local, fit_upper
from advaita.preserved_prediction import ports
from advaita.state import canonical, fingerprint
from advaita.structural import StructuralLearner

PARENT = ROOT / 'results/recall-withdrawal-v1'
SOURCES = ['advaita/controlled.py', 'checks/test_controlled_learner.py',
           'experiments/control_consolidation_protocol.md', 'docs/controlled-learner.md']
COUNTS = dict(replayed_runs=0, reused_scalar_labels=0, synthetic_scalar_labels=0,
              observations=0, reviews=0, restores=0, frozen_files=0)


def frozen():
    manifest = json.loads((PARENT / 'manifest.json').read_text())
    completion = json.loads((PARENT / 'completion.json').read_text())
    expected = dict(manifest, **completion['verification_hashes'])
    for name, digest in expected.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise AssertionError('Frozen file changed: ' + name)
    COUNTS['frozen_files'] = len(expected)
    return expected


def saved_first():
    with gzip.open(PARENT / 'runs.jsonl.gz', 'rt') as stream:
        return json.loads(next(stream))


def acquired():
    return StructuralLearner.restore(canonical(saved_first()['acquisition_checkpoint']))


def synthetic_base(*, bad_archive=False, policy='command', dependent=False):
    """Explicit state fixture, not an acquired or empirically discovered memory."""
    learner = ControlledLearner(acquired(), recall_policy=policy)
    state = json.loads(learner.checkpoint())
    e = state['engine']
    e['tick'] = 512
    e['main_ids'] = [512]
    e['selection_ids'] = [512]
    # Large opposite evidence separates recall and active losses reliably.
    for bank in ('fast', 'slow'):
        for table in e[bank]:
            for cell in table:
                cell[:] = [0. if bad_archive else 1000., 1000.]
    raw = [[[f[k] + s[k] for k in (0, 1)] for f, s in zip(ft, st)]
           for ft, st in zip(e['fast'], e['slow'])]
    e['locals'] = [fit_local([0, 0, 1, 1], raw[j]) for j in (0, 1)]
    e['upper'] = fit_upper([1, 1], raw[2], e['locals'])
    spec = [1, 0] if dependent else [0, 0]
    counts = ({f'{g}|{a}': [999. if bad_archive else 0., 1000.]
               for g in (0, 1) for a in (0, 1)} if dependent else
              {str(a): [999. if bad_archive else 0., 1000.] for a in (0, 1)})
    slot = dict(upper=dict(spec=spec, counts=counts),
                locals=[dict(groups=m['groups'].copy()) for m in e['locals']],
                ports=ports(e['locals'], spec),
                dependency=fingerprint(ports(e['locals'], spec)))
    e['memory'].update(slot=slot, confirmed=True, passes=2,
                       attempt_complete=True, route=True)
    return ControlledLearner.restore(canonical(state))


ROW = dict(x=[0, 0], a=0, local=[0, 0], y=0)


def advance(learner, n=1, row=ROW):
    result = None
    for _ in range(n):
        COUNTS['synthetic_scalar_labels'] += 0 if row is None else 3
        result = learner.observe(learner.tick + 1, row)
    return result


def review(learner):
    COUNTS['synthetic_scalar_labels'] += 3 * 16
    return learner.review(learner.tick, [copy.deepcopy(ROW) for _ in range(16)])


class Contracts(unittest.TestCase):
    def unchanged_on_error(self, learner, call):
        before = learner.checkpoint()
        with self.assertRaises(ValueError):
            call()
        self.assertEqual(before, learner.checkpoint())

    def test_validation_is_atomic(self):
        a = ControlledLearner(acquired())
        for call in (
            lambda: a.observe(True, ROW), lambda: a.observe(2, ROW),
            lambda: a.observe(1, dict(ROW, y=2)),
            lambda: a.review(0, [ROW]),
            lambda: a.set_recall_block(True, reason='test', source='fixture'),
            lambda: a.configure(lock=[0], plastic=[2], reason='test', source='fixture'),
            lambda: a.predict([0, 4], 0),
        ):
            self.unchanged_on_error(a, call)
        advance(a)
        for rows in ([], [ROW, dict(ROW, local=[0, 2])], None):
            self.unchanged_on_error(a, lambda: a.review(a.tick, rows))
        review(a)
        for lock, plastic in (([2], []), ([0], [0]), ([], [3]),
                              ([0, 0], []), ([], [2, 2]), ([True], [])):
            self.unchanged_on_error(a, lambda: a.configure(
                lock=lock, plastic=plastic, reason='test', source='fixture'))
        self.unchanged_on_error(a, lambda: a.configure(
            lock=[], plastic=[], reason='test', source=''))
        for blocked in (1, 'yes', None):
            self.unchanged_on_error(a, lambda: a.set_recall_block(
                blocked, reason='test', source='fixture'))
        a.configure(lock=[0], plastic=[2], reason='test', source='fixture')
        self.unchanged_on_error(a, lambda: a.configure(
            lock=[], plastic=[], reason='again', source='fixture'))
        a.set_recall_block(True, reason='test', source='fixture')
        self.unchanged_on_error(a, lambda: a.set_recall_block(
            False, reason='again', source='fixture'))
        advance(a, row=None)
        self.unchanged_on_error(a, lambda: a.review(a.tick, [ROW]))
        self.unchanged_on_error(a, lambda: a.set_recall_block(
            False, reason='missing', source='fixture'))

    def test_inspection_coherence_detachment_and_future_parity(self):
        a = synthetic_base()
        b = ControlledLearner.restore(a.checkpoint())
        for i in range(1, 66):
            self.assertEqual(advance(a), advance(b))
            if i % 16 == 0:
                self.assertEqual(review(a), review(b))
            before = a.checkpoint()
            view = a.inspect()
            state = json.loads(a.native_checkpoint())
            raw = [[[f[k] + s[k] for k in (0, 1)] for f, s in zip(ft, st)]
                   for ft, st in zip(state['fast'], state['slow'])]
            locals_ = [fit_local(m['partition'], raw[j]) for j, m in enumerate(state['locals'])]
            self.assertEqual(view['learning']['locals'], locals_)
            self.assertEqual(view['learning']['upper'], fit_upper(state['upper']['spec'], raw[2], locals_))
            packet = a.predict([0, 0], 0)
            packet['active'][0] = -1
            view['learning']['locals'][0]['groups'][0] = 99
            view['memory']['slot']['upper']['counts'].clear()
            view['commands'].append('detached')
            self.assertEqual(before, a.checkpoint())
            self.assertEqual(a.checkpoint(), b.checkpoint())

    def test_protection_plasticity_release_and_restore(self):
        a = synthetic_base()
        event = a.configure(lock=[0], plastic=[1, 2], reason='protect and adapt', source='fixture')
        held = a.inspect()['learning']['locals'][0]['partition']
        self.assertEqual(event['native']['half_lives'], [1024, 128, 128])
        before = a.checkpoint()
        b = ControlledLearner.restore(before)
        self.assertEqual(before, b.checkpoint())
        for _ in range(64):
            self.assertEqual(advance(a), advance(b))
        self.assertEqual(review(a), review(b))
        self.assertEqual(a.inspect()['learning']['locals'][0]['partition'], held)
        self.assertEqual(a.checkpoint(), b.checkpoint())
        native_before = json.loads(a.native_checkpoint())
        a.configure(lock=[], plastic=[], reason='release', source='fixture')
        native_after = json.loads(a.native_checkpoint())
        for k in ('fast', 'slow', 'locals', 'upper'):
            self.assertEqual(native_before[k], native_after[k])
        self.assertEqual(a.inspect()['learning']['half_lives'], [1024] * 3)
        self.assertEqual(a.inspect()['learning']['locked'], {})
        # Released locks no longer suppress the channel's ordinary review.
        advance(a, 64)
        self.assertNotEqual(review(a)['channels'][0]['action'], 'locked')

    def test_block_over_real_admission_release_and_readmission(self):
        a = synthetic_base()
        a.configure(lock=[0], plastic=[2], reason='joint controls', source='fixture')
        a.set_recall_block(True, reason='hold recall', source='fixture')
        for _ in range(64):
            advance(a)
            self.assertEqual(a.inspect()['last_prediction']['source'], 'active')
        review(a)
        v = a.inspect()
        self.assertTrue(v['recall']['steering']['reviews'][-1]['ordinary_route'])
        self.assertFalse(v['memory']['route'])
        a = ControlledLearner.restore(a.checkpoint())
        a.set_recall_block(False, reason='fresh consideration', source='fixture')
        self.assertEqual(a.predict([0, 0], 0)['source'], 'active')
        advance(a)
        self.assertEqual(a.inspect()['last_prediction']['source'], 'active')
        review(a)
        self.assertTrue(a.inspect()['memory']['route'])
        advance(a)
        self.assertEqual(a.inspect()['last_prediction']['source'], 'archive')

    def test_meaning_compatibility_gates_output(self):
        a = synthetic_base(dependent=True)
        self.assertEqual(a.predict([0, 0], 0)['source'], 'archive')
        state = json.loads(a.checkpoint())
        original = copy.deepcopy(state['engine']['locals'][0]['groups'])
        # Deliberately substitute another meaning to isolate the dependency gate.
        state['engine']['locals'][0]['groups'] = [1 - g for g in original]
        b = ControlledLearner.restore(canonical(state))
        self.assertFalse(b.inspect()['recall']['compatible'])
        self.assertEqual(b.predict([0, 0], 0)['source'], 'active')
        state['engine']['locals'][0]['groups'] = original
        c = ControlledLearner.restore(canonical(state))
        self.assertEqual(c.predict([0, 0], 0)['source'], 'archive')
        c.set_recall_block(True, reason='permission still matters', source='fixture')
        self.assertTrue(c.inspect()['recall']['compatible'])
        self.assertEqual(c.predict([0, 0], 0)['source'], 'active')

    def test_partial_monitor_restore_and_causal_withdrawal(self):
        a = synthetic_base(bad_archive=True, policy='evidence')
        advance(a, 8)
        self.assertEqual(len(a.inspect()['recall']['steering']['window']), 8)
        b = ControlledLearner.restore(a.checkpoint())
        for _ in range(8):
            self.assertEqual(advance(a), advance(b))
        self.assertEqual(a.checkpoint(), b.checkpoint())
        v = a.inspect()
        self.assertEqual(v['last_prediction']['source'], 'archive')
        self.assertEqual(v['current_output_source'], 'active')
        self.assertEqual(v['recall']['steering']['withdrawals'], 1)
        advance(a)
        self.assertEqual(a.inspect()['last_prediction']['source'], 'active')


class SavedReplay(unittest.TestCase):
    def test_all_240_saved_trajectories(self):
        worlds = {(w['seed'], w['branch']): w for w in json.loads((PARENT / 'worlds.json').read_text())}
        groups = {}
        with gzip.open(PARENT / 'runs.jsonl.gz', 'rt') as stream:
            for line in stream:
                r = json.loads(line)
                key = (r['seed'], r['history'], r['proposal_seed'])
                with self.subTest(key=key, policy=r['policy']):
                    w = worlds[key[:2]]
                    core = StructuralLearner.restore(canonical(r['acquisition_checkpoint']))
                    before = core.checkpoint()
                    a = ControlledLearner(core, recall_policy=r['policy'])
                    self.assertEqual(before, core.checkpoint())
                    configs = {e['tick']: e for e in r['controls']}
                    commands = {e['tick']: e for e in r['steering_commands']}
                    checkpoints = {e['tick']: e['sha256'] for e in r['restore_checks']}
                    active = []
                    review_index = 0
                    for t, row in enumerate(w['main'], 1):
                        self.assertEqual(a.observe(t, row), r['predictions'][t - 1])
                        COUNTS['observations'] += 1
                        COUNTS['reused_scalar_labels'] += 3
                        # Exercise the full unified inspection during replay.
                        snapshot = a.inspect()
                        last = snapshot['last_prediction']
                        active.append(last['active'])
                        self.assertEqual(last['active'], r['active_predictions'][t - 1])
                        self.assertEqual({k: v for k, v in last.items() if k not in ('tick', 'deployed')},
                                         r['prediction_events'][t - 1])
                        if str(t) in w['selection']:
                            rows = w['selection'][str(t)]
                            self.assertEqual(a.review(t, rows), r['reviews'][review_index])
                            COUNTS['reviews'] += 1
                            COUNTS['reused_scalar_labels'] += 3 * len(rows)
                        if t in configs:
                            c = configs[t]
                            event = a.configure(lock=list(map(int, c['locked'])),
                                                plastic=[j for j, h in enumerate(c['half_lives']) if h == 128],
                                                reason=c['reason'], source='saved 037 schedule')
                            self.assertEqual(event['native'], c)
                        if t in commands:
                            c = commands[t]
                            self.assertEqual(a.set_recall_block(c['blocked'], reason=c['reason'], source=c['source'])['native'], c)
                        if str(t) in w['selection']:
                            self.assertEqual(a.inspect()['learning'], r['inspections'][review_index])
                            review_index += 1
                        if t in checkpoints:
                            self.assertEqual(hashlib.sha256(a.native_checkpoint().encode()).hexdigest(), checkpoints[t])
                            saved = a.checkpoint()
                            a = ControlledLearner.restore(saved)
                            self.assertEqual(saved, a.checkpoint())
                            COUNTS['restores'] += 1
                    native = json.loads(a.native_checkpoint())
                    self.assertEqual(native, r['checkpoint'])
                    # Exclude output-only state and whole-engine hash-bearing logs.
                    learning = {k: v for k, v in native.items()
                                if k not in ('schema', 'recall', 'memory', 'steering', 'control_events')}
                    signature = (hashlib.sha256(canonical(active).encode()).hexdigest(),
                                 hashlib.sha256(canonical(r['reviews']).encode()).hexdigest(),
                                 hashlib.sha256(canonical(learning).encode()).hexdigest())
                    if key in groups:
                        self.assertEqual(signature, groups[key])
                    else:
                        groups[key] = signature
                    COUNTS['replayed_runs'] += 1
                if COUNTS['replayed_runs'] % 40 == 0:
                    print(f"Replay: {COUNTS['replayed_runs']}/240", flush=True)
        self.assertEqual(COUNTS['replayed_runs'], 240)
        self.assertEqual(len(groups), 60)


def main():
    output = ROOT / 'results/control-consolidation-v1'
    output.mkdir(exist_ok=True)
    attempt = len(list(output.glob('attempt-*.json'))) + 1
    path = output / f'attempt-{attempt:02d}.json'
    if path.exists():
        raise FileExistsError(path)
    start = time.monotonic()
    log = io.StringIO()
    status = 'failed'
    error = None
    result = None
    def timeout(*_):
        raise TimeoutError('038 verification 900-second ceiling')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(900)
    try:
        initial = frozen()
        suite = unittest.TestSuite([
            unittest.defaultTestLoader.loadTestsFromTestCase(Contracts),
            unittest.defaultTestLoader.loadTestsFromTestCase(SavedReplay)])
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
        assert frozen() == initial
        status = 'pass' if result.wasSuccessful() else 'failed'
    except BaseException as exc:
        error = repr(exc)
    finally:
        signal.alarm(0)
        data = dict(status=status, error=error, date='2026-11-10',
                    scope='engineering compatibility and contracts, not new utility evidence',
                    fresh_random_labels=0, counts=COUNTS, log=log.getvalue(),
                    tests_run=None if result is None else result.testsRun,
                    elapsed_seconds=time.monotonic() - start,
                    sources={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES})
        path.write_text(json.dumps(data, indent=2) + '\n')
        print(log.getvalue())
        print(f'{status}: {path}', flush=True)
    return status != 'pass'


if __name__ == '__main__':
    sys.exit(main())
