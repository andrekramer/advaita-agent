"""Experimental direction/strength interface for the shadow-recall learner."""
import copy
import json
import math

from .controlled import ControlledLearner
from .state import canonical


class DirectionStrengthLearner(ControlledLearner):
    """A single expiring command binds to the members of one learned cell."""

    def __init__(self, acquired):
        super().__init__(acquired, recall_policy='shadow')
        self.cell_command = None
        self.cell_events = []

    def _binding(self, channel, x, action):
        self.predict(x, action)  # Validate the public input without advancing time.
        if type(channel) is not int or channel not in (0, 1, 2):
            raise ValueError('channel must be 0, 1 or 2')
        engine = self._engine
        if channel < 2:
            part = engine.locals[channel]['partition']
            members = [i for i in range(4) if part[i] == part[x[channel]]]
            return dict(channel=channel, members=members, ports=[], source='active')
        spec = list(engine.upper['spec'])
        # Canonical membership survives a permutation of numeric group names.
        ports = []
        for j, mode in enumerate(spec):
            groups = engine.locals[j]['groups']
            if mode == 1:
                ports.append([min(i for i in range(4) if groups[i] == g) for g in groups])
            elif mode == 2:
                ports.append(list(range(4)))
            else:
                ports.append([0] * 4)
        members = [i for i in range(32) if i % 2 == action
                   and ports[0][i // 8] == ports[0][x[0]]
                   and ports[1][i // 2 % 4] == ports[1][x[1]]]
        return dict(channel=channel, members=members, ports=ports, spec=spec, source=self._source())

    def inspect_cell(self, channel, x, action):
        binding = self._binding(channel, x, action)
        result = dict(tick=self.tick, binding=binding, poles=[0, 1],
                      fast_half_life=64, slow_half_life=self._engine.half_lives[channel],
                      probability=self.predict(x, action)['active'][channel])
        for name in ('fast', 'slow'):
            table = getattr(self._engine, name)[channel]
            successes, mass = [sum(table[i][k] for i in binding['members']) for k in (0, 1)]
            result[name] = dict(direction=successes / mass if mass else None, strength=mass)
        result['command'] = copy.deepcopy(self.cell_command)
        return result

    def configure(self, **kwargs):
        if self.cell_command or any(e['kind'] == 'open' and e['tick'] == self.tick for e in self.cell_events):
            raise ValueError('cell command occupies this control opportunity')
        return super().configure(**kwargs)

    def open_cell(self, channel, x, action, *, budget, through_tick, reason):
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('reason required')
        if budget is not None and (type(budget) not in (float, int) or not math.isfinite(budget) or budget <= 0):
            raise ValueError('budget must be positive and finite, or None for uncapped')
        if type(through_tick) is not int or through_tick <= self.tick:
            raise ValueError('expiry must be a future tick')
        if self.tick not in self._engine.selection_ids or self.cell_command:
            raise ValueError('opening requires a completed review and a free command slot')
        if self._engine.half_lives != [1024]*3 or self._engine.locked:
            raise ValueError('cell plasticity requires ordinary native control rates')
        if any(e['tick'] == self.tick for e in self._engine.control_events + self.cell_events if e.get('kind', 'open') == 'open'):
            raise ValueError('one command per review')
        binding = self._binding(channel, x, action)
        self.cell_command = dict(binding=binding, x=list(x), action=action, budget=budget,
                                 spent=0., remaining=budget, through_tick=through_tick)
        self.cell_events.append(dict(kind='open', tick=self.tick, reason=reason, **copy.deepcopy(self.cell_command)))

    def release_cell(self, reason):
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('release reason required')
        if self.cell_command:
            self.cell_events.append(dict(kind='close', tick=self.tick, reason=reason,
                                         **copy.deepcopy(self.cell_command)))
            self.cell_command = None

    def observe(self, tick, row):
        cmd = self.cell_command
        if cmd is None:
            return super().observe(tick, row)
        if type(tick) is not int or tick != self.tick + 1:
            raise ValueError('ticks must be consecutive')
        if row is not None:
            from .continuing import ContinuingLearner
            ContinuingLearner._row(row)
        binding = cmd['binding']
        cells = [self._engine.slow[binding['channel']][i] for i in binding['members']]
        mass = sum(cell[1] for cell in cells)
        ordinary, faster = 2**(-1/1024), 2**(-1/128)
        debit = (ordinary - faster) * mass
        if cmd['remaining'] is not None:
            debit = min(debit, cmd['remaining'])
        # Native observe subsequently applies ordinary decay to every raw bin.
        scale = 1 - debit / (ordinary * mass) if mass else 1.
        for cell in cells:
            cell[0] *= scale
            cell[1] *= scale
        result = super().observe(tick, row)
        cmd['spent'] += debit
        if cmd['remaining'] is not None:
            cmd['remaining'] -= debit
        self.cell_events.append(dict(kind='debit', tick=tick, before=mass, after=sum(c[1] for c in cells),
                                     debit=debit, spent=cmd['spent'], remaining=cmd['remaining']))
        if cmd['remaining'] == 0:
            self.release_cell('exhausted')
        elif tick == cmd['through_tick']:
            self.release_cell('expired')
        return result

    def review(self, tick, rows):
        result = super().review(tick, rows)
        cmd = self.cell_command
        if cmd and self._binding(cmd['binding']['channel'], cmd['x'], cmd['action']) != cmd['binding']:
            self.release_cell('meaning changed')
        return result

    def checkpoint(self):
        return canonical(dict(schema='direction-strength-1', native=json.loads(super().checkpoint()),
                              cell_command=self.cell_command, cell_events=self.cell_events))

    @classmethod
    def restore(cls, serialized):
        data = json.loads(serialized)
        if data.get('schema') != 'direction-strength-1':
            raise ValueError('unexpected direction/strength schema')
        native = ControlledLearner.restore(canonical(data['native']))
        if native.recall_policy != 'shadow':
            raise ValueError('this prototype requires shadow recall')
        obj = cls.__new__(cls)
        obj.__dict__.update(native.__dict__)
        obj.cell_command = data['cell_command']
        obj.cell_events = data['cell_events']
        return obj
