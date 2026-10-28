# Architecture decision after the explicit-role comparison

2026-10-28 · Experiments 023–024 · Retain the original integrated reference.

The bounded comparison is complete: 30 saved-trace compatibility checks and
300 new independently audited runs. **Do not adopt R128 or H128.** The primary
role-separation gate failed, so the conditional 100-run confirmation was not
opened. Its seeds remain unused. The current post continues to describe the
existing architecture.

## What the comparison decided

The proposed distinction was between updating predictions within a form and
revising the form itself. This implementation made that ownership explicit:
local exported meanings stayed fixed between accepted partition changes, while
predictive counts could change at every observation. It retained the existing
local/upper hierarchy and candidate language. It is a concrete test of one
minimal implementation of the idea, not a test of every architecture with
complementary learning roles.

Against the control with identical updates and review timing, R128 produced
**113 versus 113** inappropriate representation evaluations over the two
primary histories. **None of the ten pairs improved.** Local predictive traces
were identical in all 50 pairs across five histories. Stable ownership changed
the naming/binding behavior, but did not improve the measured representations.
It reduced meaning changes from 61 to 30 in the probability-shift history and
from 80 to 35 in the form-change history. Those are useful engineering effects,
but were insufficient to establish a learning benefit.

The slower review schedule also carried a cost. Relative to B64, R128 increased
mean return-adaptation loss by .140936 nats for detail return and .130238 for
reversed detail, with mean confirmed recovery delays of 76.8 and 83.2 records.
These exceed the declared .02-nat and 64-record limits. Its worst individual
adaptation cost was .281982 nats. The timing controls show similar costs;
R128 and U128 had identical predictions in both detail histories. This does
not implicate stable meaning ownership alone as the cause of those costs.

History-guided proposals were more promising. H128 improved mean adaptation
loss against R128 by **.029189 nats**, with **8/10** paired gains. However,
its mean return costs against B64 were .033417 and .028705 nats in the two
detail histories, above .02. One reversed pair cost .103656 nats against
R128/U128, exceeding the .10 individual safeguard. The full history gate failed.
Successful average improvement does not erase those failures, and cannot
establish the independent role-separation claim.

A simpler control, U64, reduced mean whole-run loss against B64 in all five
histories while retaining the original review schedule. That is a useful
follow-up lead. It was a diagnostic control, with no preregistered promotion
or independent confirmation stage of its own here. It is not automatically
the new baseline.

## Consequence for the research

Keep `advaita.structural.StructuralLearner` with the integrated policy and
64-record reviews as the reference. Preserve the new role implementation and
all comparison results as experimental artifacts. No earlier experiment,
policy, threshold or artifact was overwritten; no model was deployed.

The result sharpens the hypothesis: **holding meanings steady is different
from learning better forms**. A future form-learning architecture would need
to improve structural decisions, not merely stabilize exported IDs. Bounded
adaptation history may help proposal search, but its costs and the simpler
continuous-update alternative need separate, predeclared evaluation before
promotion. This round supplies no meta-learning result.

The next planned question can now be steerability of the retained reference:
can an intended, bounded intervention improve a specified behavior without
unacceptable collateral change, and can that effect be anticipated from the
available evidence? That needs its own protocol and controls. It has not been
executed by this comparison. Checkpoints, traceability and stable naming are
engineering affordances, not evidence that the learner is safe or controllable.

[Full findings](explicit-roles-v1/findings.md) ·
[Comparison protocol](../experiments/explicit_roles_protocol.md) ·
[Independent audit](explicit-roles-v1/audit.json) ·
[R0 contracts](explicit-roles-r0/findings.md)
