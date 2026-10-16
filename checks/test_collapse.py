"""Synthetic checks for rolling-window structural collapse; no benchmark pilots."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from collapse import Learner, evaluate
from forms import FormModel, ROOT

SPLIT=(((0,-1,-1),0),((1,-1,-1),1))


class CollapseTests(unittest.TestCase):
    def test_expiration_removes_old_counts_without_resetting_structure(self):
        m=Learner(True); m.model=FormModel(SPLIT)
        for _ in range(48): m.update((0,0,1),0,1)
        old=m.state()
        for _ in range(48): m.update((1,0,1),0,0)
        self.assertEqual(m.model.structure,SPLIT)
        self.assertEqual(m.model.counts,[[[0,0],[0,0]],[[0,48],[0,0]]])
        self.assertEqual(m.state()['window_start'],49)
        self.assertEqual(old['model']['counts'][0][0],[48,48])
        self.assertEqual(len(m.buffer),48)

    def test_disabled_excludes_reductions_but_can_change_counts(self):
        for enabled in (False,True):
            m=Learner(enabled); m.model=FormModel(SPLIT)
            for i in range(12): m.update((i%2,0,1),0,1)
            candidate,prep=m.prepare()
            counts=[len(c['state']['counts']) for c in prep['candidates']]
            self.assertEqual(1 in counts,enabled)
            self.assertGreater(m.predict((0,0,1),0),.5)

    def test_merge_pools_real_observations(self):
        m=Learner(True); m.model=FormModel(SPLIT)
        for i in range(12): m.update((i%2,0,1),i%2,1)
        candidate=FormModel.fit(ROOT,m.buffer)
        before=copy.deepcopy(m.buffer)
        d=m.select(candidate,[{'x':[0,0,1],'a':0,'y':1},{'x':[1,0,1],'a':1,'y':1}])
        self.assertTrue(d['merge'])
        self.assertEqual(m.model.structure,ROOT)
        self.assertEqual(m.model.counts,[[[6,6],[6,6]]])
        self.assertEqual(m.buffer,before)

    def test_harmful_merge_rejected(self):
        m=Learner(True); m.model=FormModel(SPLIT)
        for _ in range(10):
            m.update((0,0,1),0,0); m.update((1,0,1),0,1)
        before=m.state(); candidate=FormModel.fit(ROOT,m.buffer)
        d=m.select(candidate,[{'x':[0,0,1],'a':0,'y':0},{'x':[1,0,1],'a':0,'y':1}])
        self.assertFalse(d['accepted']); self.assertFalse(d['merge'])
        self.assertLess(d['prediction_gain'],0)
        self.assertEqual(m.state(),before)

    def test_selection_does_not_enter_window_or_candidate(self):
        m=Learner(True)
        for _ in range(8): m.update((0,1,0),1,1)
        candidate,prepared=m.prepare(); saved=copy.deepcopy(prepared); buffer=copy.deepcopy(m.buffer)
        m.select(candidate,[{'x':[1,0,1],'a':0,'y':0}])
        self.assertEqual(m.buffer,buffer); self.assertEqual(prepared,saved)
        self.assertEqual(m.seen,8)

    def test_frozen_evaluation_and_snapshot_independence(self):
        m=Learner(True)
        m.update((0,1,0),1,1)
        before=m.state(); buffer=copy.deepcopy(m.buffer)
        for changed in (False,True):
            ev=evaluate(m,1,changed)
            self.assertEqual(ev['before'],ev['after'])
            self.assertEqual(m.state(),before); self.assertEqual(m.buffer,buffer)
            self.assertEqual(len(ev['withheld']),4)
        m.update((1,0,0),1,0)
        self.assertEqual(before['model']['counts'][0][1],[1,1])


if __name__=='__main__': unittest.main()
