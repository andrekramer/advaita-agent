# Experiment 013: learned abstractions and nested interfaces

Completed 2026-10-20. **The combined primary criterion failed**, although the
experiment demonstrated three restricted capabilities: transfer through learned
groups, lower-level revision with a frozen higher relationship, and reopening
when a hidden difference became relevant.

The failure concerns choosing and preserving the appropriate level of detail.
During lower remapping, the adaptive system sometimes opened an interface to
compensate for a temporary local error, then kept it open after the lower
abstraction recovered. Only 7/10 runs finished with exact lower forms and valid
prediction behind the coarse interface; the fixed requirement was 8/10.

The [protocol](../../experiments/nested_abstractions_protocol.md), source, tests
and independent auditor were fixed and hashed before the single benchmark run.
No tuning, rerun or implementation correction followed the results.

## What was learned, and what was supplied

Each of two lower modules received four raw situations and noisy local effects.
It searched a supplied space of eight possible partitions, learning which
situations could share a predictive group. The higher learner then fitted a
table using only the two exported group IDs and a binary action.

For example, two different raw situations could both have the same local
effect distribution. Grouping them let the upper learner reuse its response
when an alternative realization appeared. The actual group memberships were
learned from observations, rather than given as category labels.

The two modules, their wiring, depth, maximum group count and local feedback
channels were supplied. Exported group IDs were aligned by increasing fitted
probability of local effect 1. This stable observable meaning is an important
part of the construction; the experiment does not solve arbitrary alignment
between independently named categories.

Local acquisition preceded composition training. The latter used one
representative per local form, covering all form combinations. Evaluation then
used the other 12 raw pairs under both actions: 24 contexts never seen by the
upper learner. Their constituent raw states had already been seen separately
by the lower learners. The representative curriculum was constructed using
the world's forms, not discovered by the learner.

After transfer evaluation, three paired branches tested continued learning:

* **Persistent:** neither the local nor composite relationships changed.
* **Remap:** group membership changed in one randomly selected lower module.
  Local effects and composite outcomes followed the new membership, preserving
  the relationship between exported forms and the composite outcome.
* **Breach:** local effects stayed the same, but the composite outcome now
  depended on a distinction hidden within one lower group.

The variants were **reopen** (adaptive lower learners and evidence-tested
upper reopening), **closed** (adaptive lower learners with the upper table
frozen), **frozen** (both levels frozen), and **flat** (a continuously updated
table over raw identities and action).

## Fixed criteria and results

All ten environment/learner-seed pairs remain in every denominator. They share
five environments; they are not ten independent task families.

| Requirement | Observed | Result |
| --- | --- | --- |
| Exact lower groups and valid withheld-composition prediction in at least 8/10 | 10/10 | Pass |
| Withheld loss improvement over flat at least .15 nats | .351079 nats | Pass |
| Remap recovery with a frozen upper table in at least 8/10 | 9/10; upper unchanged in all 10 | Pass |
| Frozen control challenged by remapping | 50% final accuracy in all 10 | Pass |
| Adaptive remap recovery through a coarse interface in at least 8/10 | **7/10** | **Fail** |
| Correct breach reopening and final exactness/prediction in at least 8/10 | 9/10 | Pass |
| Closed control challenged by breach | 50% final accuracy in all 10 | Pass |
| Breach final loss improvement over closed at least .15 nats | .691651 nats | Pass |
| Persistent interface stays coarse, with correct final forms/prediction, in at least 8/10 | 8/10 | Pass |
| Persistent mean prediction cost versus closed at most .02 nats | −.001731 nats | Pass |

“Valid prediction” requires accuracy 1 against the most probable outcome and
expected log-loss regret at most .10 nats above the 10% noise oracle. It does
not mean perfectly predicting random outcome flips. These are fixed practical
thresholds, not statistical significance tests.

## Abstraction transferred beyond the upper training examples

All ten nested learners acquired the correct local groups and reached 100%
modal-outcome accuracy on withheld compositions. Mean expected loss was
**.342068**, against the noise oracle's **.325083**.

The flat table assigned probability .5 to every withheld context, giving
expected loss **.693147** and accuracy 50%. It had no data for those raw table
cells. The result shows useful reuse of locally learned equivalence classes
within the supplied composition architecture. It does not establish superiority
over other flat models capable of sharing parameters or discovering structure.
The nested model also benefits from separately observed local effects.

## Nesting allowed local change without upper relearning

In the remap branch, closed recovered exact local groups and valid prediction
in 9/10 runs while preserving every entry of its initial upper table. All ten
reached a valid review at least once: seven at adaptation review 64 and three
at 128. One later lost a correct local partition, leaving 9/10 valid at the
final review.

The fully frozen control stayed at 50% accuracy. This distinguishes useful
local adaptation from a task that never challenged the representation.

Preserving the upper table was an imposed control. The evidence establishes
that the learned relationship *can remain useful through changed lower
membership*, not that the learner discovered when or what to consolidate.

## Reopening helped when a hidden difference became consequential

In the breach branch, all ten reopen runs selected the affected module at the
first review, after 64 main records and 32 fresh selection records. They exposed
that module's raw identity while leaving the other behind its learned interface.

Nine finished with exact local groups and valid prediction. Mean final expected
loss was **.380493**, versus **1.072144** for closed. Closed could not distinguish
the newly different outcomes and remained at 50% accuracy.

The remaining reopen run had initially recovered, but a later error in the
other, still-hidden module reduced final accuracy to 75%. Only one raw module
could be exposed by the supplied fine modes, so this also exposes a capacity
limit: the existing interface repair did not protect against a second local
failure.

The flat control is informative here. Once all raw contexts received adaptation
data, its mean pre-feedback loss was lower than reopen's:

| Adaptation branch: mean main log loss | Reopen | Closed | Frozen | Flat |
| --- | ---: | ---: | ---: | ---: |
| Persistent | .355432 | .357163 | .353609 | .419521 |
| Remap | .469580 | .466690 | 1.073267 | .498005 |
| Breach | .463270 | 1.078503 | 1.074949 | .419521 |

Nesting helped transfer and selective repair, but did not dominate every
prediction comparison. The flat control passed final predictive criteria in
8/10 persistent, 6/10 remap, and 8/10 breach runs. Its frozen local models are
unused, so composite “exact lower forms plus prediction” metrics should not
be interpreted as its standalone predictive quality.

## Why the combined criterion failed

Three reopen runs ended unnecessarily fine in the remap branch:

* **Environment 301, learner seed 301:** at review 64, the correct new lower
  partition was absent from the four proposals. A partial repair was selected,
  and upper failure triggered `fine0`. Local grouping recovered at 128, but
  the fine interface persisted.
* **Environment 304, learner seed 300:** the same pattern occurred: the correct
  partition was not proposed at 64, grouping recovered at 128, and `fine0`
  remained exposed.
* **Environment 304, learner seed 301:** at the final review, noisy local
  selection replaced the correct partition in the *unaffected* module.
  Reopening that module as `fine1` restored upper prediction to 100% accuracy,
  but the local abstraction itself remained wrong.

The first two had lower frozen-upper recovery at 128 versus reopen's full
exactness/prediction recovery at 192. Opening more detail was not invariably
the faster route.

Related false openings occurred in two persistent runs. Environment 303,
learner seed 300 briefly adopted a wrong local partition at review 64 from
a selection batch containing 8/32 flipped local outcomes. It repaired the
partition at 128 but kept the fine upper interface. Environment 304, learner
seed 301 made its final wrong local change on a batch with 7/32 flips.
The configured generating noise rate was still 10%; these are realized
fluctuations, not separate high-noise conditions.

The rule permits upper revision only when current selection loss exceeds
.55 nats. Once a fine predictor is adequate, there is no dedicated reason to
reconsider hiding detail; candidate ranking also uses training loss and only
prefers coarse structure on exact ties. This is a limitation of the present
mechanism. It is not evidence that arbitrary goals or an elaborate utility
function must be added.

The failure separates two questions: *can a finer interface restore prediction?*
and *was reopening the appropriate lasting response?* Simple error-based
selection answered the first more reliably than the second.

## Information access, cost and verification

A coarse upper table has eight possible cells and reads no raw identities.
A fine table has sixteen cells and reads one module's identity; flat has
thirty-two cells and reads both. Lower modules still observe their own raw
states. This demonstrates restricted parent access, not reduced environmental
sensing or secure encapsulation.

Across the breach branch, reopen averaged .875 upper raw reads per main
prediction: none before the first review and one thereafter. Flat used two.
Across remapping, the average was .175, reflecting the three finer deployments.
The architecture includes two additional local tables, bounded buffers and
candidate search; upper table size alone is not total system cost.

The 120 runs used 399,360 allocated outcome-label presentations and 253,440
labels for fitting or selection. A record containing two local effects and
one composite effect counts as three labels. The 15 paired streams contained
49,920 generated labels, including duplicated acquisition across branches.
There were 7,680 local candidate fits, 720 upper candidate fits and 33,600
external evaluation predictions. Controls use different feedback and compute
budgets, explicitly recorded rather than assumed equal.

Eight targeted synthetic tests passed. The independent auditor reconstructed
all worlds and replayed all 120 runs, including grouping, canonical IDs,
upper fitting, interface choices, every selection decision, predictions,
metrics and costs. All four manifests, including Experiments 010–012, passed.

This round now has evidence for **learned abstraction and two-level composition
within supplied operations**, alongside the earlier hiding-versus-deleting
result. Reliable decisions about *where to revise* and *when to hide again*
remain unresolved. Learned depth, general folds, progressive evidence-based
consolidation, and meta-learning have not been demonstrated.

The fixed experiment is complete. No additional run or tuning follows
automatically.

Full records: [report](report.md), [metrics](metrics.json), [traces](results.json),
[manifest](manifest.json). Verification:
`python3 -m unittest discover -s checks -p 'test_nested_abstractions.py' -v`
and `python3 checks/audit_nested_abstractions.py`.
