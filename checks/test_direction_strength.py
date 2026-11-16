"""Command scope, exact debit, semantic changes and restart on deterministic fixtures."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'checks')]
from advaita.controlled import ControlledLearner
from advaita.direction_strength import DirectionStrengthLearner
from test_controlled_learner import synthetic_base


class CellControls(unittest.TestCase):
    def setUp(self):
        native = synthetic_base(policy='shadow')
        self.learner = DirectionStrengthLearner.restore(json.dumps(dict(
            schema='direction-strength-1', native=json.loads(native.checkpoint()),
            cell_command=None, cell_events=[])))

    def start(self, budget, duration=16):
        self.learner.open_cell(0,[0,0],0,budget=budget,through_tick=512+duration,reason='fixture')

    def test_scope_cap_restore_and_empty_tick(self):
        learner=self.learner
        self.start(.25)
        before=learner.checkpoint()
        with self.assertRaises(ValueError):
            learner.observe(513,dict(x=[8,0],a=0,y=0,local=[0,1]))
        self.assertEqual(learner.checkpoint(),before)
        twin=DirectionStrengthLearner.restore(before)
        control=ControlledLearner.restore(json.dumps(json.loads(before)['native']))
        for b in (learner,twin,control):
            b.observe(513,None)
        self.assertEqual(learner.checkpoint(),twin.checkpoint())
        self.assertEqual(learner.cell_events[-1]['reason'],'exhausted')
        self.assertAlmostEqual(learner.cell_events[-1]['spent'],.25)
        ordinary=control._engine.slow
        actual=learner._engine.slow
        self.assertEqual(actual[1:],ordinary[1:])
        self.assertEqual(actual[0][2:],ordinary[0][2:])
        self.assertAlmostEqual(sum(ordinary[0][i][1]-actual[0][i][1] for i in (0,1)),.25)

    def test_release_expiry_and_invalid_budget(self):
        b=self.learner
        for value in (-1,0,float('nan'),float('inf'),True):
            with self.assertRaises(ValueError):
                self.start(value)
        saved=b.checkpoint()
        self.start(None,1)
        b.observe(513,None)
        self.assertEqual(b.cell_events[-1]['reason'],'expired')
        self.learner=DirectionStrengthLearner.restore(saved)
        self.start(None)
        self.learner.release_cell('operator')
        self.assertIsNone(self.learner.cell_command)
        self.assertEqual(self.learner.cell_events[-1]['spent'],0)

    def test_semantic_binding(self):
        b=self.learner
        b.open_cell(2,[0,0],0,budget=None,through_tick=640,reason='fixture')
        # Synthetic post-review meanings isolate invalidation from proposal luck.
        with patch.object(ControlledLearner,'review',return_value={}):
            groups=b._engine.locals[0]['groups']
            b._engine.locals[0]['groups']=[1-g for g in groups]
            b.review(512,[])
            self.assertIsNotNone(b.cell_command)
            b._engine.locals[0]['groups']=[0,1,1,0]
            b.review(512,[])
            self.assertIsNone(b.cell_command)
            self.assertEqual(b.cell_events[-1]['reason'],'meaning changed')


if __name__=='__main__':
    unittest.main()
