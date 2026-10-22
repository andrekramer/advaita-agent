"""Meaning compatibility, immutable predictive memory and evidence provenance."""
from dataclasses import dataclass
import hashlib
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def fingerprint(ports):
    """Revision counters are deliberately absent; exported meanings are present."""
    normalized = sorted(ports, key=lambda p: p['name'])
    if len({p['name'] for p in normalized}) != len(normalized):
        raise ValueError('Duplicate dependency port')
    if any(set(p) != {'name', 'domain', 'meaning'} for p in normalized):
        raise ValueError('A port needs name, domain and meaning only')
    return hashlib.sha256(canonical(normalized).encode()).hexdigest()


@dataclass(frozen=True)
class FrozenPredictor:
    payload: str
    dependency: str
    capture_event: str
    record_ids: tuple

    @classmethod
    def capture(cls, model_state, ports, event, record_ids):
        return cls(canonical(model_state), fingerprint(ports), event, tuple(record_ids))

    def compatible(self, ports):
        return self.dependency == fingerprint(ports)

    def candidate(self, ports):
        if not self.compatible(ports):
            raise ValueError('Archived predictor has incompatible meanings')
        return json.loads(self.payload)

    def state(self):
        return dict(payload=self.payload, dependency=self.dependency,
                    capture_event=self.capture_event, record_ids=list(self.record_ids))

    @classmethod
    def from_state(cls, value):
        return cls(value['payload'], value['dependency'], value['capture_event'], tuple(value['record_ids']))


class Archive:
    """One frozen entry; capture replaces and returns the displaced entry."""
    def __init__(self):
        self.entry = None

    def capture(self, entry):
        if not isinstance(entry, FrozenPredictor):
            raise TypeError('Archive requires an immutable snapshot')
        displaced, self.entry = self.entry, entry
        return displaced

    def clear(self):
        displaced, self.entry = self.entry, None
        return displaced

    def state(self):
        return None if self.entry is None else self.entry.state()


class EvidenceLedger:
    """Audit metadata; it supplies no observations to prediction or fitting."""
    def __init__(self):
        self.main = set()
        self.selection = set()
        self.uses = []

    @staticmethod
    def _ids(ids):
        ids = list(ids)
        if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
            raise ValueError('Evidence IDs must be unique nonempty strings within a call')
        return ids

    def validate_main(self, ids):
        ids = self._ids(ids)
        if set(ids) & (self.main | self.selection):
            raise ValueError('Main evidence identity already used')
        return ids

    def add_main(self, ids):
        self.main.update(self.validate_main(ids))

    def fit(self, ids, operation):
        ids = self._ids(ids)
        if not set(ids) <= self.main:
            raise ValueError('Fitting requires registered main evidence only')
        self.uses.append(dict(kind='fit', operation=operation, ids=ids))

    def validate_selection(self, ids, operation):
        ids = self._ids(ids)
        if set(ids) & self.main:
            raise ValueError('Selection evidence overlaps fitting evidence')
        if any(u['kind'] == 'selection' and u['operation'] == operation
               and set(ids) & set(u['ids']) for u in self.uses):
            raise ValueError('A decision cannot treat reused labels as a fresh witness')
        return ids

    def select(self, ids, operation):
        ids = self.validate_selection(ids, operation)
        reused = sorted(set(ids) & self.selection)
        self.selection.update(ids)
        self.uses.append(dict(kind='selection', operation=operation, ids=ids, reused=reused))

    def state(self):
        return json.loads(canonical(dict(main=sorted(self.main), selection=sorted(self.selection), uses=self.uses)))

    @classmethod
    def from_state(cls, value):
        result = cls()
        result.main, result.selection = set(value['main']), set(value['selection'])
        if result.main & result.selection:
            raise ValueError('Checkpoint contains overlapping main and selection evidence')
        result.uses = json.loads(canonical(value['uses']))
        return result
