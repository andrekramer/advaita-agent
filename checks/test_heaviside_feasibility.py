"""Side-quest algebra and native-entry-point probes; no predictive benchmark."""
import copy
import hashlib
import io
import json
from math import atan2, cos, isclose, pi, sin
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from advaita.continuing import ContinuingLearner
from advaita.memory_control import RF, RS, prob
from advaita.models import CountTable, LocalModel
from advaita.structural import JointModel, StructuralLearner

OBSERVATIONS = {}


def core_fixture():
    core = StructuralLearner([0, 1], 2)
    for node in core.nodes:
        node.buffer = [dict(x=x, y=int(x >= 2)) for _ in range(5) for x in range(4)]
        node.model = LocalModel((0, 0, 1, 1), node.buffer)
    rows = [dict(x=[0, 0], a=0, local=[0, 0], y=int(i < 8)) for i in range(10)]
    core.train_upper([f'fixture/{i}' for i in range(10)], rows)
    return core


class Feasibility(unittest.TestCase):
    def test_a_supplied_acceptance_once(self):
        # The supplied mathematical acceptance code, unchanged except indentation.
        def check(actual, expected):
            assert isclose(actual, expected, rel_tol=0, abs_tol=1e-12), (actual, expected)

        def update(c, y, rho):
            a, b = c
            return rho * a + y, rho * b + (1 - y)

        def read(c):
            return c[0] / sum(c)

        for n in (5, 500):
            for y in (0, 1):
                check(read(update((n, n), y, 1)), (n + y) / (2*n + 1))

        for rho, initial in ((1, (5, 5)), (.9, (4, 6)), (.99, (500, 500))):
            c = initial
            p, mass = read(c), sum(c)
            fixed = p
            for y in (1, 1, 0, 1, 0, 0, 0, 1) * 4:
                theta = atan2(c[1], c[0])
                delta = (0 if y else pi/2) - theta
                radius = (c[0]**2 + c[1]**2)**.5
                turn = atan2(sin(delta), rho * radius + cos(delta))
                c = update(c, y, rho)
                mass = rho * mass + 1
                p += (y - p) / mass
                check(read(c), p)
                check(atan2(c[1], c[0]) - theta, turn)
                if rho == .9:
                    fixed += (1 - rho) * (y - fixed)
                    check(p, fixed)

    def test_b_native_counts_already_retain_strength(self):
        outcomes = []
        for n in (5, 500):
            for y in (0, 1):
                table = CountTable(['row'])
                # Native cells store [successes, total], excluding the unit priors.
                table.counts['row'] = [n - 1, 2*n - 2]
                self.assertEqual(table.probability('row'), .5)
                table.add('row', y)
                expected = (n + y)/(2*n + 1)
                self.assertAlmostEqual(table.probability('row'), expected, places=14)
                outcomes.append(dict(effective_mass=2*n, y=y, after=expected))
        OBSERVATIONS['native_strength'] = outcomes

    def test_c_stationary_prior_is_not_discounted_prior(self):
        raw = [8., 10.]
        rho = .9
        # Before the next observed outcome, native decay refits a fixed unit prior.
        native = prob([rho*v for v in raw])
        effective = [raw[0] + 1, raw[1] - raw[0] + 1]
        proposal = rho*effective[0]/sum(rho*v for v in effective)
        self.assertNotAlmostEqual(native, proposal, places=12)
        OBSERVATIONS['prior_and_prediction_clock'] = dict(
            initial=prob(raw), native_after_decay_before_label=native,
            proposed_after_uniform_decay_before_label=proposal)

    def test_d_same_odds_and_mass_need_not_determine_two_bank_revision(self):
        # Identical total evidence, placed entirely in fast or slow memory.
        values = []
        for rho in (RF, RS):
            before = prob([8., 10.])
            after = prob([rho*8., rho*10. + 1])  # New B outcome.
            values.append(dict(before=before, effective_mass=12., rho=rho, after=after))
        self.assertEqual(values[0]['before'], values[1]['before'])
        self.assertNotAlmostEqual(values[0]['after'], values[1]['after'], places=12)
        OBSERVATIONS['two_bank_age_counterexample'] = values

    def test_e_native_reference_update_path(self):
        core = core_fixture()
        row = dict(x=[0, 0], a=0, local=[0, 0], y=0)
        reference = ContinuingLearner(core)
        before = reference.engine.predict(row['x'], row['a'])[0]
        table_before = copy.deepcopy(reference.engine.upper.state())
        emitted = reference.observe(1, row)[2]
        after = reference.engine.predict(row['x'], row['a'])[0]
        self.assertEqual(before, emitted)
        self.assertEqual(before, after)
        self.assertEqual(table_before, reference.engine.upper.state())
        # Holding meanings fixed is not enough to make a coarse table refit.
        # The raw-port comparison is explicitly a diagnostic configuration.
        core.deploy(JointModel((2, 1), core.buffer, core.models()),
                    core.dependencies((2, 1)), core.buffer_ids)
        raw = ContinuingLearner(core)
        raw_emitted = raw.observe(1, row)[2]
        raw_after = raw.engine.predict(row['x'], row['a'])[0]
        self.assertEqual(raw_emitted, before)
        self.assertLess(raw_after, before)
        OBSERVATIONS['native_entry_points'] = dict(
            coarse_before=before, coarse_observe_return=emitted, coarse_after=after,
            raw_port_observe_return=raw_emitted, raw_port_after=raw_after)

    def test_f_weighted_native_prediction_is_post_decay_pre_label(self):
        a = ContinuingLearner(core_fixture(), memory='combined')
        before = a.engine.predictions([0, 0], 0)[2]
        counts = a.engine.upper['counts']['0|0|0']
        expected = prob([v*RF for v in counts])  # Initial slow store is empty.
        emitted = a.observe(1, dict(x=[0, 0], a=0, local=[0, 0], y=0))[2]
        self.assertAlmostEqual(emitted, expected, places=14)
        self.assertNotAlmostEqual(before, emitted, places=12)
        OBSERVATIONS['weighted_entry_point'] = dict(
            diagnostic_before_tick=before, emitted_after_decay=emitted,
            after_label=a.engine.predictions([0, 0], 0)[2])


def main():
    out = ROOT/'results/heaviside-feasibility-v1'
    out.mkdir(exist_ok=True)
    path = out/f"attempt-{len(list(out.glob('attempt-*.json')))+1:02d}.json"
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Feasibility))
    sources = ['advaita-heaviside.md', 'checks/test_heaviside_feasibility.py',
               'advaita/continuing.py', 'advaita/models.py', 'advaita/structural.py',
               'advaita/memory_control.py', 'advaita/memory_revision.py']
    data = dict(status='pass' if result.wasSuccessful() else 'failed',
                date='2026-11-13', scope='deterministic feasibility; no development or confirmation seeds',
                tests=result.testsRun, observations=OBSERVATIONS, log=log.getvalue(),
                commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                sources={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})
    with path.open('x') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')
    print(log.getvalue())
    print(path)
    return not result.wasSuccessful()


if __name__ == '__main__':
    sys.exit(main())
