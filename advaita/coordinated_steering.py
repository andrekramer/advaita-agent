"""034 extension: allow composite slow-memory plasticity, with local locks.

All learning and snapshot rules are inherited unchanged from frozen033.
"""
import copy
import json
from .selective_steering import SteerableMemory
from .state import canonical


class CoordinatedMemory(SteerableMemory):
    def configure(self, *, lock, plastic, reason):
        if not isinstance(plastic, (list, tuple)):
            raise ValueError('Plastic channels must be a list or tuple')
        if any(type(j) is not int or j not in (0, 1, 2) for j in plastic):
            raise ValueError('Plastic channels must be 0, 1 or 2')
        if len(set(plastic)) != len(plastic):
            raise ValueError('Plastic channels must be distinct')
        # Parent validates the complete lock and all other preconditions before
        # mutation. Composite2 is never a legal lock target in either class.
        super().configure(lock=lock, plastic=[j for j in plastic if j != 2], reason=reason)
        self.half_lives[2] = 128 if 2 in plastic else 1024
        self.control_events[-1]['half_lives'] = self.half_lives.copy()
        return copy.deepcopy(self.control_events[-1])

    def checkpoint(self):
        state = json.loads(super().checkpoint())
        state['schema'] = 34
        return canonical(state)

    @classmethod
    def restore(cls, serialized):
        state = json.loads(serialized)
        if state['schema'] != 34:
            raise ValueError('Unsupported coordinated checkpoint')
        state['schema'] = 33
        return super().restore(canonical(state))
