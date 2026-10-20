import copy
import itertools as it
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'experiments'))
from nested_abstractions import (
    InterfaceView, LocalLearner, LocalModel, Upper, current_forms, evaluate,
    generate, target, upper_review, view_for)


def fixture():
    return {'forms': [[0, 1, 1, 0], [1, 0, 1, 0]],
            'representatives': [[0, 1], [1, 0]], 'affected': 1, 'branch': 'persistent'}


def locals_for(w, adaptation=False):
    result = []
    for forms in current_forms(w, adaptation):
        # Canonical partition labels need not equal semantic group IDs.
        partition = tuple(int(y != forms[0]) for y in forms)
        rows = [{'x': x, 'y': forms[x]} for _ in range(32) for x in range(4)]
        result.append(LocalModel(partition, rows))
    return result


def joint(w, representatives=False, adaptation=False):
    axes = w['representatives'] if representatives else [range(4), range(4)]
    return [{'x': [l, r], 'a': a, 'y': target(w, [l, r], a, adaptation)}
            for _ in range(8) for l, r, a in it.product(*axes, (0, 1))]


class NestedTests(unittest.TestCase):
    def test_local_search_discovers_shared_effect_groups(self):
        learner = LocalLearner(909)
        forms = [0, 1, 1, 0]
        rows = [{'x': x, 'y': forms[x]} for _ in range(64) for x in range(4)]
        for i, row in enumerate(rows, 1):
            learner.update(row)
            if i % 64 == 0:
                learner.review(rows[:32])
        self.assertEqual(learner.model.state()['groups'], forms)
        self.assertEqual(learner.model.group(0), learner.model.group(3))
        self.assertNotEqual(learner.model.group(0), learner.model.group(1))

    def test_composition_transfers_to_unseen_raw_pairs(self):
        w = fixture()
        models = locals_for(w)
        data = joint(w, representatives=True)
        coarse, flat = Upper('coarse', data, models), Upper('flat', data, models)
        self.assertEqual(evaluate(coarse, models, w, False)['accuracy'], 1)
        flat_evaluation = evaluate(flat, models, w, False)
        self.assertEqual(flat_evaluation['contexts'], 24)
        self.assertEqual(set(flat_evaluation['predictions']), {.5})

    def test_prediction_boundary_restricts_raw_identity(self):
        view = InterfaceView([0, 1], [3, 2], 'coarse')
        self.assertEqual(view.group(1), 1)
        for j in range(2):
            with self.assertRaises(PermissionError):
                view.raw(j)
        fine = InterfaceView([0, 1], [3, 2], 'fine1')
        self.assertEqual(fine.raw(1), 2)
        with self.assertRaises(PermissionError):
            fine.raw(0)
        self.assertEqual(fine.raw_reads, 1)
        self.assertFalse(hasattr(Upper(), 'models'))

    def test_lower_remapping_preserves_frozen_upper_relationship(self):
        w = fixture()
        old_models = locals_for(w)
        upper = Upper('coarse', joint(w, True), old_models)
        state = upper.state()
        w['branch'] = 'remap'
        self.assertEqual(evaluate(upper, old_models, w, True)['accuracy'], .5)
        self.assertEqual(evaluate(upper, locals_for(w, True), w, True)['accuracy'], 1)
        self.assertEqual(state, upper.state())
        self.assertNotEqual(old_models[1].partition, locals_for(w, True)[1].partition)

    def test_upper_failure_reopens_relevant_module(self):
        w = fixture()
        models = locals_for(w)
        upper = Upper('coarse', joint(w, True), models)
        w['branch'] = 'breach'
        observations = joint(w, adaptation=True)
        result, review = upper_review(upper, observations[:192], models, observations[192:])
        self.assertTrue(review['accepted'])
        self.assertEqual(result.mode, 'fine1')
        self.assertEqual(evaluate(result, models, w, True)['accuracy'], 1)

    def test_selection_cannot_fit_candidates_or_modify_lower_models(self):
        w = fixture()
        models = locals_for(w)
        upper = Upper('coarse', joint(w, True), models)
        w['branch'] = 'breach'
        rows = joint(w, adaptation=True)
        before = [m.state() for m in models]
        altered = [dict(r, y=1-r['y']) for r in rows[192:]]
        _, a = upper_review(upper, rows[:192], models, rows[192:])
        _, b = upper_review(upper, rows[:192], models, altered)
        self.assertEqual(a['candidates'], b['candidates'])
        self.assertEqual(a['winner'], b['winner'])
        self.assertEqual(before, [m.state() for m in models])
        self.assertNotEqual(a['accepted'], b['accepted'])

    def test_world_branches_share_inputs_noise_and_acquisition(self):
        worlds = [generate(909, b) for b in ('persistent', 'remap', 'breach')]
        for w in worlds[1:]:
            for field in ('forms', 'representatives', 'affected', 'local_main',
                          'local_selection', 'composition'):
                self.assertEqual(w[field], worlds[0][field])
            for old, new in zip(worlds[0]['main'], w['main']):
                self.assertEqual((old['x'], old['a']), (new['x'], new['a']))
                self.assertEqual(old['y'] ^ target(worlds[0], old['x'], old['a']),
                                 new['y'] ^ target(w, new['x'], new['a']))
                for j in range(2):
                    self.assertEqual(old['local'][j] ^ current_forms(worlds[0])[j][old['x'][j]],
                                     new['local'][j] ^ current_forms(w)[j][new['x'][j]])

    def test_evaluation_pure_and_export_labels_follow_effects(self):
        w = fixture()
        models = locals_for(w)
        upper = Upper('coarse', joint(w, True), models)
        before = copy.deepcopy((upper.__dict__, [m.__dict__ for m in models]))
        evaluate(upper, models, w, False)
        evaluate(upper, models, w, True)
        self.assertEqual(before, (upper.__dict__, [m.__dict__ for m in models]))
        self.assertEqual(models[1].partition[0], 0)
        self.assertEqual(models[1].group(0), 1)
        self.assertEqual(upper.predict(view_for([0, 1], models, 'coarse'), 0) < .5, True)


if __name__ == '__main__':
    unittest.main()
