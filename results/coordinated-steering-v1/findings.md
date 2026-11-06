# 034 — Downstream plasticity helped; adding local plasticity did not help more

Completed 2026-11-05. **The primary coordination hypothesis was not supported.**
With protection held constant, increasing both local and downstream plasticity
never improved active-window expected composite loss over increasing downstream
plasticity alone: 16/20 pairs tied and four worsened. Mean incremental gain was
−.001692 nats. The required positive benefit and consistency both failed.

Downstream plasticity itself was useful: it improved over protection alone by
.096068 nats, positive in all 20 changing-condition pairs. Coordinated plasticity
also beat local-only plasticity and the unsteered reference, but those comparisons
do not establish an added benefit from coordinating both levels. The full gate
failed on the primary incremental comparison and preservation after release.

All **150 runs passed independent replay**. No default changed and no outcome was
rerun or tuned. This is evidence about one scheduled memory-control intervention
in supplied small worlds, not a general claim about coordination or intelligence.

[Protocol](../../experiments/coordinated_steering_protocol.md) ·
[Full results](results.json) · [Audit](audit.json) · [Traces](runs.jsonl.gz) ·
[Worlds](worlds.json) · [Manifest](manifest.json) ·
[Control semantics](../../docs/coordinated-steering.md)

## The controlled comparison

Five fresh environments, two proposal seeds each, and three histories (stable,
category remapping, repeated polarity reversal) used exactly the 033 task design.
In changing histories the protected local channel received a misleading category
burst while its latent truth remained stable; the other channel genuinely
changed. Channel roles and the intervention schedule were supplied instructions,
not discovered goals. Both local positions occurred in each role, although the
flexible channel was node1 in four of the five environments.

After review 512, the protected distinction was locked where specified, while
selected slow stores changed from a 1024-tick to a 128-tick half-life. All other
rules stayed fixed. Controls released after review 1024, without restoring lost
evidence. Data continued through 2048, including return and another change.

| Policy | Protect stable local partition | More plastic local learner | More plastic composite learner |
| --- | --- | --- | --- |
| U: unsteered | No | No | No |
| P: protection only | Yes | No | No |
| L: local | Yes | Yes | No |
| D: downstream | Yes | No | Yes |
| C: coordinated | Yes | Yes | Yes |

All five policies used the coherent snapshot boundary from 033. The only new
capability was changing composite slow-memory retention. The whole composite
store changes; the test does not isolate particular downstream relations.
“Coordination” means a simultaneous supplied instruction, not an adaptive policy
that discovers when or where coordination is necessary.

## The decisive comparisons

Positive gain means lower expected composite log loss over 513–1024. Primary
thresholds were at least .005 nats and at least 12 positive pairs among the 20
changing-condition pairs. The stable history was evaluated separately.

| Comparison | Mean gain | Better / tied / worse | Interpretation |
| --- | ---: | ---: | --- |
| C over D | **−.001692** | 0 / 16 / 4 | Adding local plasticity did not help the primary outcome |
| C over L | .090372 | 20 / 0 / 0 | Adding downstream plasticity helped |
| C over U | .075915 | 20 / 0 / 0 | The combined instruction helped active composite prediction |
| D over P | .096068 | 20 / 0 / 0 | Downstream plasticity helped with protection unchanged |
| L over P | .004004 | 4 / 16 / 0 | Local plasticity alone had a small composite effect |
| C over P | .094375 | 20 / 0 / 0 | The combination helped, without outperforming D |

The factorial interaction, `(D−C)−(P−L)`, was **−.005696 nats**, positive in zero
pairs. The separately declared interaction criterion also failed. The results
support neither added active-window benefit nor a positive interaction from
simultaneously increasing both plasticities.

C-versus-D gains by environment were 0, −.001890, −.001417, −.005156 and 0. The
incremental benefit was absent in both histories: −.000756 nats for remapping
and −.002629 for reversal. Two proposal replicates and related histories are
correlated; these are five independent environment layouts, not 20 independent
worlds. No statistical significance claim is made.

Local adaptation still improved under C relative to D: expected flexible-local
loss fell from .488726 to .465149 in remapping and from .609411 to .534478 in reversal.
Those local improvements did not deliver extra composite benefit in the primary
window. This again separates a useful local change from a useful global change.

## Retention and later behavior

| History / policy | Active composite loss | Return loss | Later loss | Final full validity |
| --- | ---: | ---: | ---: | ---: |
| Stable U | .336203 | .333490 | .334546 | 10/10 |
| Stable P | .336203 | .333329 | .334751 | 10/10 |
| Stable L | .333002 | .333329 | .334751 | 10/10 |
| Stable D | .342230 | .338853 | .335857 | 10/10 |
| Stable C | .338944 | .338853 | .335857 | 10/10 |
| Remapping U | .587613 | .491807 | .507063 | 10/10 |
| Remapping P | .590284 | .493443 | .509923 | 10/10 |
| Remapping L | .589845 | .490738 | .517183 | 10/10 |
| Remapping D | .553622 | .492012 | .512393 | 10/10 |
| Remapping C | .554377 | .490763 | .519401 | 10/10 |
| Reversal U | .840070 | .514641 | .719275 | 4/10 |
| Reversal P | .874320 | .511768 | .714876 | 4/10 |
| Reversal L | .866752 | .522249 | .715342 | 3/10 |
| Reversal D | .718848 | .590336 | .668494 | 8/10 |
| Reversal C | .721476 | .580771 | .660529 | 8/10 |

All protected policies preserved the intended partition at 100% of burst checks
in each changing history. C achieved final full validity 10/10 in stable data,
10/10 in remapping and 8/10 in reversal, passing that endpoint gate. Every final
local partition was correct in every policy, even when composite validity failed.
Raw inputs remained in the final composite interface in 6/10 coordinated reversal
runs, versus 8/10 downstream-only and 8/10 unsteered; correct local forms do not
imply that the composite learner exclusively uses them.

Preservation nevertheless failed. C's mean reversal return cost over U was
**.066130 nats**, exceeding the .02 allowance; the largest individual cost was
.170885, exceeding .10. The returning task was ultimately recovered: all policies
had full validity 10/10 at 1536 in the changing histories. The cost is in the
recovery trajectory, not evidence of irreversible loss.

Additional failures involved later local prediction costs: one remapping case
cost .112443 nats against both U and D; reversal local-channel1 costs averaged
.027209 against U and.026847 against D, with maximum .121619. All failed guards
are listed in [descriptive tables](descriptive.json). Stable active guards passed,
although unnecessary downstream plasticity raised stable composite loss slightly.

C sometimes had lower *later* composite loss than D, including both return and
later windows in reversal. Those secondary differences are retained in the table;
they do not overturn the failed primary active-window comparison or collateral
guards. The full conjunction stays failed even though several components passed.

## What we can infer

In these tasks, increasing downstream plasticity was sufficient for the measured
active composite benefit; adding local plasticity was unnecessary for that
benefit. This is consistent with a downstream adaptation bottleneck. It does not
prove that every failure was caused by the same bottleneck, or that coordination
would be useless with other interfaces, tasks, timings or control mechanisms.

The narrower question now concerns adaptation versus retention: downstream
plasticity improves response to change but can increase the cost of recovering
earlier knowledge. Neither a globally faster learner nor this fixed joint
schedule is established as a reliable default. The study did not learn when to
open or close plasticity, preserve a separately retrievable composite model, or
infer which relationships should be protected. No further experiment was run.

## Validation and resources

Four fixture tests passed on the first attempt. They reconstructed all five
policies, verified exact U/P/L behavior against 033 counterparts on reused 7990
data, checked composite-only decay, active checkpoint restoration, release,
atomic rejection of invalid commands and the factorial metric gates. Fixtures
used 1792 transformed replay presentations plus one synthetic labelled step;
no new random fixture labels were generated.

The fresh study used 153600 generated scalar labels and 1536000 presentations,
152380 candidate fits,5257568 scoring queries,26942520 fit-related raw-bin visits,
153600 grid predictions and 1105920 additional selective-decay cell visits.
All frozen caps passed. Runner 83.79s; independent audit 74.64s. The audit rebuilt
all predictions, reviews, control events, snapshots, checkpoints and measurements.
All 1500 protected source and historical files remained unchanged.

Saved-data reproduction, without generating new outcomes:

```sh
python3 checks/audit_coordinated_steering.py
python3 experiments/report_coordinated_steering.py
```

The benchmark refuses to overwrite results. Original and earlier experimental
classes remain frozen; the optional schema 34 extension does not promote a policy.
