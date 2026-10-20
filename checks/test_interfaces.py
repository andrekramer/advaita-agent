"""Synthetic fixtures only; no benchmark trajectories."""
import copy
import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from interfaces import Acquisition, Boundary, Learner, Model, VisibleInput, evaluate, generate


def rows(pair=True, invert=False):
    return [{'x':[s,t,0,0,0,0],'a':a,'y':s^a^(t if pair else 0)^int(invert)}
            for s,t,a in itertools.product((0,1),repeat=3)]*4


def learner(variant):
    data = rows()*4
    return Learner(variant,Model((0,1),data),data,Acquisition('deck_single',909).costs)


class InterfaceTests(unittest.TestCase):
    def test_prediction_access_and_boundary_contains_no_archive(self):
        view = VisibleInput([1,0,1,0,1,0],(0,))
        self.assertEqual(view[0],1)
        with self.assertRaises(PermissionError):
            _ = view[1]
        boundary = Boundary(Model((0,),rows(False)))
        self.assertEqual(set(boundary.__dict__),{'model'})
        _,reads = boundary.predict([1,0,1,0,1,0],0)
        self.assertEqual(reads,1)

    def test_hide_retains_or_deletes_only_predictive_detail(self):
        keep,drop = learner('retain'),learner('delete')
        prototype = keep.prototype.state()
        candidate = Model((0,),rows(False)*4)
        for m in (keep,drop):
            before_buffer = copy.deepcopy(m.buffer)
            self.assertTrue(m.select(('fresh',candidate),rows(False))['accepted'])
            self.assertEqual(m.buffer,before_buffer)
            self.assertEqual(m.parent,(0,1))
            self.assertEqual(m.model.subset,(0,))
        self.assertEqual(keep.prototype.state(),prototype)
        self.assertIsNone(drop.prototype)

    def test_hidden_prototype_does_not_learn_from_new_records(self):
        m = learner('retain')
        m.select(('fresh',Model((0,),rows(False)*4)),rows(False))
        old = m.prototype.state()
        for r in rows(False)*8:
            m.update(r)
        self.assertEqual(m.prototype.state(),old)
        self.assertEqual(len(m.buffer),192)

    def test_retrieval_is_frozen_until_explicit_replacement(self):
        m = learner('retain')
        m.select(('fresh',Model((0,),rows(False)*4)),rows(False))
        archive = m.prototype.state()
        self.assertTrue(m.select(('prototype',m.prototype),rows())['accepted'])
        before = copy.deepcopy(m.model.state())
        count = m.costs['count_refits']
        m.predict([0]*6,0)
        m.update(rows(False)[0])
        self.assertEqual(m.model.state(),before)
        self.assertEqual(m.prototype.state(),archive)
        self.assertEqual(m.costs['count_refits'],count)
        self.assertEqual(m.costs['main_prototype_steps'],1)
        _,review = m.prepare()
        self.assertIn(('fresh',[0,1]),[(c['source'],c['state']['subset']) for c in review['candidates']])

    def test_stale_memory_is_not_accepted_against_opposite_consequences(self):
        m = learner('retain')
        m.select(('fresh',Model((0,),rows(False)*4)),rows(False))
        before = m.state()
        decision = m.select(('prototype',m.prototype),rows(True,True))
        self.assertFalse(decision['accepted'])
        self.assertEqual(m.state(),before)

    def test_proposal_selection_and_evaluation_isolation(self):
        m = learner('retain')
        m.select(('fresh',Model((0,),rows(False)*4)),rows(False))
        _,review = m.prepare()
        self.assertLessEqual(len(review['candidates']),4)
        snapshot = copy.deepcopy((m.state(),m.buffer,m.costs))
        for branch,index in (('return',768),('novel',1152),('persistent',768)):
            ev = evaluate(m.model,{'permutation':list(range(6)),'branch':branch},index,m.source,m.prototype)
            self.assertEqual(ev['archive_cells'],8)
            self.assertEqual(len(ev['predictions']),128)
        self.assertEqual((m.state(),m.buffer,m.costs),snapshot)

    def test_new_world_branch_pairing(self):
        returning,novel = generate(909,'return'),generate(909,'novel')
        for i,(a,b) in enumerate(zip(returning['main'],novel['main']),1):
            self.assertEqual((a['x'],a['a']),(b['x'],b['a']))
            self.assertEqual(a['y']^b['y'],int(i>768))
        for j,(aa,bb) in enumerate(zip(returning['selection'],novel['selection']),1):
            self.assertTrue(all(a['y']^b['y']==int(j>12) for a,b in zip(aa,bb)))

    def test_empty_acquisition_does_not_receive_a_constructed_pair(self):
        m = Learner('retain',Model(()),[],Acquisition('deck_single',909).costs)
        candidate,review = m.prepare()
        self.assertIsNone(candidate)
        self.assertEqual(review['candidates'],[])
        self.assertIsNone(m.select(candidate,rows()))
        self.assertEqual(m.costs['selection_outcomes'],0)


if __name__=='__main__':
    unittest.main()
