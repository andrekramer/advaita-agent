"""Deterministic pre-run contracts. Does not use development/confirmation seeds."""
from pathlib import Path
import copy
import math
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'experiments'))
from heaviside_predictors import Predictor, gate, metrics, percentile


class Contracts(unittest.TestCase):
    def test_twin_and_fixed_limit(self):
        for rho in (.9, .97, .99, 1.):
            v = Predictor('vector', rho, 'A', 'long', False)
            s = Predictor('scalar', rho, 'A', 'long', False)
            for y in [1, 0, 0, 1, 1]*50:
                self.assertAlmostEqual(v.predict(), s.predict(), places=12)
                v.update(y); s.update(y)
        v = Predictor('vector', .9, 'A', 'short', False)
        f = Predictor('fixed', .1, 'A', 'short', False)
        for y in [0, 0, 1, 1, 0]*50:
            self.assertAlmostEqual(v.predict(), f.predict(), places=12)
            v.update(y); f.update(y)

    def test_read_only_and_mirror(self):
        for arm, value in [('vector', .97), ('scalar', .97), ('full', 1), ('fixed', .03),
                           ('matched', .03), ('rotor', .20), ('prior_matched', .97),
                           ('prior_selected', .9), ('window', 192)]:
            a = Predictor(arm, value, 'B', 'short', False)
            b = Predictor(arm, value, 'B', 'short', True)
            for y in [1, 1, 0, 1]*60:
                before = copy.deepcopy(a.__dict__)
                for _ in range(3): a.predict(); a.state()
                self.assertEqual(before, a.__dict__)
                self.assertAlmostEqual(a.predict()+b.predict(), 1., places=12)
                a.update(y); b.update(1-y)

    def test_strength_and_window(self):
        short = Predictor('vector', 1, 'A', 'short', False)
        long = Predictor('vector', 1, 'A', 'long', False)
        self.assertEqual(short.predict(), long.predict())
        self.assertGreater(short.predict()-short.update(0), long.predict()-long.update(0))
        window = Predictor('window', 192, 'B', 'short', False)
        for _ in range(192): window.update(1)
        window.update(0)
        self.assertEqual(window.predict(), 192/194)
        self.assertEqual(len(window.buffer), 192)
        prior = Predictor('prior_matched', .9, 'B', 'short', False)
        prior.raw_a, prior.raw_b = 8., 2.
        self.assertAlmostEqual(prior.predict(), 8.2/11)

    def test_windows_recovery_and_gates(self):
        ps = [.8]*4+[.2]*124
        m = metrics(ps, [0]*128, 'streak', False)
        self.assertAlmostEqual(m['brier'], .04)
        self.assertAlmostEqual(m['forced_brier'], .64)
        self.assertEqual(metrics(ps, [0]*128, 'reversal', False)['recovery_seen'], 4)
        self.assertEqual(metrics([.8]*125+[.2]*3, [0]*128, 'reversal', False)['recovery_capped'], 128)
        self.assertEqual(metrics([.8]*124+[.2]*4, [0]*128, 'reversal', False)['recovery_seen'], 124)
        self.assertEqual(percentile([0, 1, 2, 3], .25), .75)
        c = {a: {f: dict(high=-.01) for f in ('stable', 'streak', 'reversal')} for a in ('window', 'fixed')}
        self.assertTrue(gate(c))
        c['fixed']['streak']['high'] = 0.
        self.assertFalse(gate(c))
        c['fixed']['streak']['high'] = -.01
        c['window']['reversal']['high'] = .01
        self.assertFalse(gate(c))


if __name__ == '__main__':
    unittest.main(verbosity=2)
