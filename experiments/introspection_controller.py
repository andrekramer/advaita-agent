"""032 read-only inspection adapter and explicitly hand-written controller.

The controller gets only the packet. The adapter can read current checkpoint
metadata to expose pending decisions omitted from the original inspection API.
"""
import copy
import json

PORTS=('absent','group_membership','raw_state')

def packet(runtime):
    observed=runtime.inspect()
    state=json.loads(runtime.learning_checkpoint())
    observed['pending']=copy.deepcopy(state['pending'])
    observed['revision_pending']=copy.deepcopy(state['revision_pending'])
    return dict(observed=observed,inferred=dict(
        upper_ports=[PORTS[s] for s in observed['upper']['spec']],
        upper_consumes_local_confidence=False,
        review_losses_are_pre_final_migration=True))

def decide(view):
    obs=view['observed'];events=obs['last_review']['weakenings']
    eligible=[e for e in events if e['qualifies'] and not e['accepted']]
    channels=[e['channel'] for e in eligible]
    selected=max(eligible,key=lambda e:(e['losses'][0]-e['losses'][1],-e['channel']))['channel'] if eligible else None
    # This assertion encodes a documented property of the frozen interface.
    assert view['inferred']['upper_consumes_local_confidence'] is False
    assert view['inferred']['upper_ports']==[PORTS[s] for s in obs['upper']['spec']]
    forecasts=[dict(channel=j,immediate=('no_change' if j<2 else 'change') if j in channels else 'uncertain',
        future=('no_effect' if j<2 else 'improvement') if j in channels else 'uncertain',
        disagreement_future='improvement' if j in channels else 'uncertain',
        own_future='improvement' if j in channels else 'uncertain') for j in range(3)]
    return dict(target_output=2,eligible=channels,choices=dict(no_op=None,disagreement=selected,
        aware=2 if 2 in channels else None,rotated=(selected+1)%3 if selected is not None else None),forecasts=forecasts)
