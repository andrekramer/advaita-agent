"""Synthetic fixtures only; no benchmark performance pilots."""
import copy
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'experiments'))
from complementary_roles import Learner, RIDGE, THETA0, dot, fit, gain, phi


class ComplementaryTests(unittest.TestCase):
    def test_ridge_normal_equations(self):
        rows = [[x, a, .07*math.cos(x)+.03*a]
                for x in (-2., -.1, .7, 1.4, 3.1) for a in (-1, 1)]
        candidate = fit(rows)
        for row, target in zip(candidate['matrix'], candidate['rhs']):
            self.assertAlmostEqual(dot(row, candidate['raw']), target, places=12)
        self.assertTrue(all(-1 <= w <= 1 for w in candidate['theta']))
        # An unexcited basis direction remains finite because ridge makes A SPD.
        repeated = fit([[0., 1, .2]]*3)
        self.assertTrue(all(math.isfinite(w) for w in repeated['raw']))

    def test_predict_before_feedback_and_local_update(self):
        m = Learner('full'); m.start_episode()
        pred = m.predict(1., 1)
        self.assertEqual(pred['xhat'], 1.)
        self.assertAlmostEqual(pred['loop_prediction'], .11)
        with self.assertRaises(AssertionError):
            m.predict(2., -1)
        m.observe_target(.04, 'main')
        self.assertAlmostEqual(m.prior, 1.11)
        self.assertAlmostEqual(m.d, .2*(.04/.2-.55))
        self.assertEqual(m.buffer[0], [1.,1,.04])
        with self.assertRaises(AssertionError):
            m.observe_target(.5, 'main')

    def test_cuts_are_different_and_do_not_use_excluded_signals(self):
        m = Learner('no_feedback'); m.start_episode()
        m.theta = [.9,.5,.2,.1,.3]
        pred = m.predict(.7, 1)
        self.assertEqual(pred['b'], .55)
        m.observe_target(.1, 'main')
        for variant, raw_context in [('full',False),('no_teaching',True)]:
            m = Learner(variant); m.start_episode(); m.prior = 0.
            pred = m.predict(2., -1)
            self.assertEqual(pred['xhat'], 1.)
            self.assertEqual(pred['z'], 2. if raw_context else 1.)
            m.observe_target(.02, 'main')
            self.assertEqual(m.buffer[0][0], pred['z'])

    def test_reset_preserves_retained_knowledge(self):
        m = Learner('full'); m.start_episode()
        m.predict(0., 1); m.observe_target(.3,'main')
        m.theta = [.6,.1,0.,0.,0.]
        before_theta, before_buffer = m.theta.copy(), copy.deepcopy(m.buffer)
        m.start_episode()
        self.assertIsNone(m.prior); self.assertEqual(m.d, 0.)
        self.assertEqual(m.theta,before_theta); self.assertEqual(m.buffer,before_buffer)

    def test_selection_acceptance_and_rejection(self):
        m = Learner('full')
        proposed = {'theta':[.7,0.,0.,0.,0.]}
        decision = m.select(proposed,[{'selection_incumbent':.1,'selection_candidate':.14}],[.14])
        self.assertTrue(decision['accepted']); self.assertEqual(m.theta,proposed['theta'])
        retained = m.theta.copy()
        decision = m.select({'theta':THETA0},[{'selection_incumbent':.14,'selection_candidate':.1}],[.14])
        self.assertFalse(decision['accepted']); self.assertEqual(m.theta,retained)

    def test_candidate_and_buffer_isolation(self):
        m = Learner('full'); m.start_episode()
        m.predict(.5,1); m.observe_target(.08,'main')
        candidate = m.propose(); saved = copy.deepcopy(candidate); old = copy.deepcopy(m.buffer)
        m.start_episode(); m.predict(3.,-1,candidate=candidate['theta'])
        m.observe_target(-.6,'selection')
        self.assertEqual(candidate,saved); self.assertEqual(m.buffer,old)
        self.assertEqual(m.theta,THETA0)

    def test_online_gradient_and_evaluation_freeze(self):
        m = Learner('online'); m.start_episode()
        pred=m.predict(.7,-1)
        f=[-.2*v for v in phi(.7)]
        r=.03
        expected=[w-.05*(2*f[i]*(dot(f,THETA0)-r))/(1+dot(f,f)) for i,w in enumerate(THETA0)]
        m.observe_target(r,'selection')
        for a,b in zip(m.theta,expected): self.assertAlmostEqual(a,b,places=14)
        self.assertEqual(len(m.buffer),0)
        frozen=m.theta.copy(); m.start_episode()
        m.predict(-1.,1,evaluation=True); m.observe_target(-.4,'evaluation')
        self.assertEqual(m.theta,frozen); self.assertEqual(len(m.buffer),0)
        self.assertNotEqual(m.d,0.)

    def test_misalignment_applies_only_in_test_observer(self):
        m=Learner('misaligned'); m.theta=[.5,.2,0.,0.,0.]; m.start_episode()
        normal=m.predict(.5,1)
        self.assertAlmostEqual(normal['b'],gain(m.theta,.5))
        m.observe_target(.05,'main'); m.start_episode()
        shifted=m.predict(.5,1,evaluation=True)
        self.assertAlmostEqual(shifted['b'],gain(m.theta,.5+math.pi))
        self.assertAlmostEqual(shifted['curve_prediction'],.2*gain(m.theta,.5))

    def test_local_cap_and_feedback_update_uses_preupdate_gain(self):
        m=Learner('online'); m.start_episode()
        p=m.predict(.1,1); m.observe_target(100.,'main')
        self.assertEqual(m.d,.4)
        self.assertEqual(m.costs['local_clips'],1)
        self.assertAlmostEqual(m.prior,.1+p['loop_prediction'])
        self.assertTrue(all(-1 <= w <= 1 for w in m.theta))


if __name__ == '__main__':
    unittest.main()
