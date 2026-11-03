# 032 — Inspection predicts relevance better than disagreement alone

Completed 2026-11-03. **Future-effect forecasting passed; the full experiment
failed.** A fixed controller informed by the interface predicted the direction
of future composite loss correctly for 28/29 eligible interventions (96.6%),
versus 17/29 (58.6%) when every strong disagreement was taken to imply downstream
improvement. This is a bounded result for a hand-written explanation of the
existing architecture, not learned introspection or human/LLM interpretability.

All 30 decision-point trajectories and 120 counterfactual continuations passed
independent replay. The learner, interfaces, memory rules and original default
remain unchanged. [Frozen protocol](../../experiments/introspection_protocol.md),
[full measurements](results.json), [audit](audit.json),
[saved traces](runs.jsonl.gz), [worlds](worlds.json), [source manifest](manifest.json).

## What was tested

Five fresh environments, two proposal seeds each, and three histories: stable,
repeated polarity reversal, and changing local forms. Both local nodes occurred
as the affected node: node0 in one environment and node1 in four. Two proposal
replicates are not independent environments.

The intended output was always the composite prediction. At the first qualifying
unaccepted memory-weakening diagnostic (or review 1024 if absent), a copied packet
reported fitted forms, interface ports, evidence masses, pending decisions and
review diagnostics. Observed state was separated from a supplied explanation of
what the interface consumes. Future observations, simulator truth, raw memory
banks and world/change identifiers were unavailable to the controller.

Decisions and forecasts were recorded before four clones continued with the same
future inputs: no intervention, or one halving of slow evidence in channels 0, 1, 2.
The disagreement controller chose the largest eligible fast/slow loss gap. The
interface-informed controller chose an eligible composite-channel intervention,
or abstained. A rotated-channel control was also evaluated. All policies used
the same decision point; none could wait for a later diagnostic.

The forecast hypothesis was deliberately limited: local confidence changes need
not reach an upper predictor that consumes category membership, while weakening
contradicted composite evidence should improve that output. Future direction was
classified over the next 256 observations, using a .005-nat tolerance. All three
outputs, later return/reversal behavior and final representation validity were
also evaluated. These are interventions in a supplied finite architecture, not
an unrestricted planner or a self-selected goal system.

## Results

| Fixed criterion | Result |
| --- | --- |
| Independent state, prediction, decision and accounting replay | Passed:30 trunks, 120 continuations |
| Immediate effect predictions | Failed: 24/29 eligible actions correct |
| Future forecast coverage | Passed: 29 eligible actions across all 5 environments |
| Future composite direction accuracy | Passed:28/29, versus 17/29 disagreement-only |
| Future forecast advantage | Passed: +37.9 percentage points; required 20 |
| Mean aware-controller gain over disagreement | Passed: .005957 nats; required .005 |
| Consistency of that gain | Failed: 4/20 improved, 15 tied, 1 worsened; required 12 improvements |
| Mean gain over no intervention | Passed: .023939 nats; 16/20 improved, 4 tied |
| Return/later collateral guards | Passed for all 3 outputs and expected composite loss |
| Final full validity | Failed:stable 10/10, repeated 7/10, forms 10/10; required 8/10 each |

The forecast sample includes 16 upper interventions, all predicting and producing
improvement, and 13 local interventions: 12 had no meaningful composite effect;
one improved it. Own-channel improvement was correctly forecast for all 29.
That single local exception matters: no immediate downstream effect does not
imply that a local intervention cannot alter subsequent structural learning.

The aware policy acted 16 times in the 20 changing trajectories; disagreement
acted 20 times. Both abstained on all 10 stable trajectories. The 16 aware actions
were positive against no intervention, but mostly matched what the disagreement
controller already chose. Relative to disagreement, environment mean gains were
0, .002166, .002750, -.001995 and .026864 nats. The mean benefit therefore does
not establish consistent superiority. Against rotated control, the overall mean
gain was only .000940 nats; rotated did better in the repeated-history mean.

| History and policy | Next256 composite loss | Return loss | Later loss | Final valid |
| --- | ---: | ---: | ---: | ---: |
| Stable, all policies | .318942 | identical | identical | 10/10 |
| Repeated, no-op | .594726 | .556654 | .662444 | 7/10 |
| Repeated, disagreement | .578375 | .557946 | .662314 | 7/10 |
| Repeated, interface-informed | .567561 | .566246 | .660331 | 7/10 |
| Repeated, rotated | .549828 | .590054 | .645965 | 7/10 |
| Forms, no-op | .465709 | .491797 | .516305 | 10/10 |
| Forms, disagreement | .446095 | .484722 | .521759 | 10/10 |
| Forms, interface-informed | .444995 | .484743 | .521686 | 10/10 |
| Forms, rotated | .464609 | .491818 | .516232 | 10/10 |

Full validity combines correct local partitions, all modal composite predictions
correct and expected regret<=.10. Costs passing their guards does not mean zero
cost: the aware repeated-history mean return cost was .009592 nats against
no-op; the largest individual guarded observed-output cost was .070293 nats.
The protocol's full conjunction remains failed.

## Why five immediate predictions failed

Inspection accurately exposed the stored state, but our immediate-effect
explanation assumed that the upper table already matched the current local
forms. In five eligible local interventions, that assumption was false just
after review. A local form had changed and the upper model was kept; its stored
probability table had not yet been refreshed for the current representation.
The control operation refits all active models, so even a local intervention
could change the displayed composite probabilities at that moment.

A **post-outcome diagnostic using only saved states** applied a refit without
weakening evidence. It reproduced all five composite changes exactly. An
independent fit from the audited evidence confirmed the diagnostic. Maximum
probability differences were .085891–.283329. In all five cases the next 256
composite predictions were exactly identical to no intervention: the ordinary
next observation also performs a refit. No additional labels, new learning
trials or changed primary criteria were introduced.
See [diagnostics](diagnostics.json) and
[reproduction script](../../experiments/report_introspection.py).

This is a state-consistency issue for inspection and control at review boundaries,
not evidence that local confidence is an input to the upper predictor. The
failed immediate-effect gate is retained. It should be addressed before richer
steering: define a coherent post-review snapshot and separate a pure refresh
from an evidence-changing intervention. A repair could alter subsequent review
behavior and must be compared explicitly; it has not been applied here.

## Scope, resources and reproduction

The packet's observation fields matched independently reconstructed state, and
fixture tests verified that inspection is detached and does not mutate learning.
The explanation of dependency behavior and the policy remain supplied code.
In particular, the controller uses the fixed fact that no upper port consumes
local confidence; it has not learned a causal model or demonstrated understanding
of an arbitrary dependency graph. Eligibility uses historical review losses,
not a current exact counterfactual estimate after migration.

29/90 possible channel interventions were eligible and forecast; all were in the
changing histories. Ineligible actions were explicitly uncertain, not silently
counted as correct. Counterfactual actions share checkpoints and data, and are
correlated. The five environment layouts and supplied task family bound the
claim. No user study, meta-learning, general steerability or safety advantage.

Six fixture tests passed before fresh outcomes. Both saved fixture attempts
passed (the second followed removal of a redundant fixture assignment); together
they replayed 1024 presentations from the already used 7990 fixture, with 0 new
labels. The main study generated 153600 scalar labels and used 811776 presentations
across shared prefixes and four continuations. It made 86599 candidate fits,
2893248 scoring queries and15135968 raw-bin visits; all frozen caps passed.
Runner 52.08s; independent audit 39.72s. All 1470 protected files remained intact.

To audit saved results, without new learning experiments:

```sh
python3 checks/audit_introspection.py
python3 experiments/report_introspection.py
```

The benchmark command `python3 experiments/introspection.py` refuses to overwrite
its output directory. Do not delete the results to rerun reserved seeds or tune
this test. The next bounded step is post-review state consistency and explicit
refresh attribution, followed by another declared steering comparison if needed.
