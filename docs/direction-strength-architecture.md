# Direction and strength in Advaita Agent

Working architecture for the next bounded research round · Adopted 13 November 2026

The [mathematical specification](../maths-direction-strength.md) gives the evidence equations for the adopted learner and the scripted check against its behaviour.

**Use direction and strength as the organising pair for learning, interpretation and steering.** Each learned distinction has a meaning and carries the pair separately in fast and slow memory. The adopted command makes one distinction more plastic without imposing a mass cap. It closes when the bound meaning changes or the scheduled 256 observations elapse. The design and initial budget proposal below led to this choice. [Confirmed research pivot](#confirmed-research-pivot)

## What a learned distinction contains

Consider two predictions that both give an outcome probability of one half. In the first, fast memory contains 18 successes in 20 observations and slow memory contains 2 in 20. In the second, the banks are exchanged. The current probability and total support agree exactly. At the next tick, fast evidence decays more quickly. Before either learner sees another label, the first prediction moves below one half and the second moves above it. An interface that exposes the direction and strength of each bank can explain that difference while hiding the individual observations.

For a binary outcome, store two nonnegative tallies per bank. Let \(u_b\) be success mass and \(s_b\) total mass, where \(b\) is fast or slow. Expose **direction** \(q_b=u_b/s_b\) towards the named positive pole and **strength** \(s_b\). A bank with zero mass has an undefined direction and contributes zero evidence. Exchanging the pole names complements the direction and preserves strength. Strength measures retained support. Repeated correlated observations can increase it, so its interpretation as confidence would need a separate calibration test.

Each prediction also has an address. A local address identifies a learned group of inputs. A relationship address identifies an upper prediction cell and the interface through which it reads its inputs. Include the output's pole names, group membership and consumed dependencies in that address. A change to a numeric group ID alone says little about whether the same distinction still exists.

## Learn

Given an input and action, resolve the active cells, decay their evidence for elapsed time, and predict the external outcome before incorporating its label. Under the existing unit priors the emitted probability for an active cell is

\[
p^- = \frac{1+d_f u_f+d_s u_s}{2+d_f s_f+d_s s_s},
\qquad d_b=2^{-1/h_b}.
\]

Decay applies to all banks on the native clock. When a label \(y\) arrives, add \((y,1)\) to the decayed fast pair \((u_f,s_f)\) of each visited, labelled output. For this cell the post-observation probability has the extra \(y\) in the numerator and 1 in the denominator. Preserve the native fast and slow half-lives of 64 and 1024 ticks as the starting configuration.

At review, the learner can propose a different partition, collapse a group, or change which information an upper interface consumes. Fit each candidate by grouping the retained evidence under the proposed meanings. This requires retaining sufficient statistics at the finer input resolution behind the public interface. Summing the underlying tallies lets a merged form inherit its evidence once and lets a split recover support for each child without duplicating the parent's strength. Evaluate proposals on fresh selection outcomes. Two banks can agree and both predict poorly, so external outcomes must remain available to challenge the current form.

This gives IVSR concrete operations. Candidate changes supply variation, slow evidence supplies inertia, external observations test selection, and accepted transfers consolidate fast evidence into slow memory. Moving a fraction of both tallies together conserves the current combined evidence while changing how long it persists. Direction and strength describe each timescale. Each timescale can contribute to both prediction and structural review. [Existing structural capabilities](../results/consolidated-learner-test-round-synthesis.md) · [Memory and review contract](controlled-learner.md)

## Interpret

Make the existing research adapter's information available directly for a requested prediction. Return its meaning, evidence in each bank, output source, active half-lives and the tick at which they were read. A scripted inspector can then answer a concrete question such as “If the next observation for this group contradicts the prediction, how far will it move?” It can give the pre-label and post-label probabilities, name the contributing stores, and state which future review could change the mapping. A multi-step forecast must also specify its assumptions about incoming evidence and structural change.

The audited one-observation probes agreed with actual learner clones within \(3.33\times10^{-16}\). Among 31 material short-term intervention effects, the supplied script forecast the direction correctly in 25 with row-specific evidence and 12 using a proportional allocation estimated from channel totals. Equivalent raw counts and named direction/strength pairs produced the same decisions. The design value lies in which information crosses the interface. This round's interpretation criterion is scripted and behavioural. [Inspection findings](../results/strength-inspection-v1/findings.md) · [Material-effect breakdown](../results/strength-inspection-v1/descriptive-diagnostics.json)

## Steer

The existing command makes a whole channel more plastic. The proposed alternative lets an operator select **one meaningful prediction cell**, preview the effect of faster slow decay and give that command a budget of slow evidence it may remove. The operator supplies the intention, protected outputs and expiry. This gives strength a second role as the unit in which an intervention can be limited and audited.

For a first prototype, bind the command at a completed review to the cell's contributing raw inputs and semantic dependencies. Give it budget \(B\) in retained-mass units. On each tick let \(s\) be the targeted slow mass before decay, \(d_0\) the ordinary slow decay and \(d_1\) the requested faster decay. Apply ordinary decay plus the following extra removal,

\[
e=\min\{B_{\rm remaining},(d_0-d_1)s\}.
\]

For \(s>0\), scale both slow tallies of each contributing raw bin by \(d_0-e/s\), then debit \(e\). For zero mass, debit zero. This preserves the targeted slow bank's direction during that operation. The combined prediction can move because the fast bank now has a different relative weight. Report automatic weakening and migration separately. The budget bounds only extra forgetting caused directly by the command. Subsequent reviews and relearning can still produce larger downstream effects.

Close the command at exhaustion or expiry, on release, or when a review changes the bound meaning or output route. Rebinding requires an explicit decision. Log the reason, before/after bank masses, budget spent and affected dependencies. Offer abstention whenever the forecast benefit is small or the binding cannot be verified. Releasing a command ends extra decay. Measuring performance on return is how we find out what was lost.

## Criteria set before the trials

| Project aim | Acceptance check on the candidate | Evidence today |
| --- | --- | --- |
| Can learn | With commands off, replay the existing learner's predictions and structural decisions. On fresh paired worlds, improve held-out prediction over a frozen acquired state and demonstrate a useful form created or collapsed and a usable upper interface. Score structural recovery separately from output accuracy. | The reference has learned generalisations within its supplied language. The proposed architecture still needs its own compatibility and learning checks. |
| Can interpret | Reconstruct emitted predictions, both one-step outcomes and command expenditure independently. Forecast intervention effects before revealing the future. Compare against aggregate-only information and equivalent raw counts. | Conditional arithmetic and improved scripted forecasting passed on the current learner. Meaning changes, expiry and budget accounting are new obligations. |
| Can steer | Apply a supplied instruction, show a useful target effect against abstention, and keep protected outputs and returning knowledge within declared bounds. Measure preservation per case as well as on average. | Richer inspection improved active-window Brier loss by 0.002126 over the existing-view controller, with positive means in 9 of 12 environments. Three preservation checks failed on return. The proposed budget has yet to be tested. |

The first decision experiment should compare cloned learners on identical observations under four conditions. Use abstention, existing channel plasticity, uncapped cell plasticity, and budgeted cell plasticity. The middle two isolate the effect of narrowing the address. The last two isolate the budget. Include stable histories, misleading bursts, lasting changes and returns. Vary local and composite targets within each proposal seed. Give every controller the same past evidence and command opportunities, freeze its choices before scoring the future, and report how often the budget actually binds.

Start with the existing return-cost allowances of 0.01 mean and 0.05 worst case in Brier units against abstention for each protected output and history. Fix the budget fraction, expiry, minimum useful target effect and minimum action coverage before confirmation. Coverage and a positive target effect make permanent abstention insufficient to pass. A lower overall loss ranking is compatible with a pivot if the candidate learns useful distinctions, explains their revisions and gives selective control within those bounds. A preservation failure would support carrying the inspection interface forward while keeping the steering proposal experimental.

## First decision

The implemented cell controls passed all preservation limits in the first eight-environment comparison. Scripted interpretation passed. The budgeted candidate fell just below the required mean target benefit, and acquisition transfer missed its floor in one environment. The uncapped meaning-bound comparator cleared the target-benefit floor and merits a fresh confirmation. All 74 budgeted commands exhausted after 63 ticks, leaving the value of a mass budget beyond a duration limit open. The full architecture pivot is deferred. [Results and decision](../results/direction-strength-v1/findings.md)

## Confirmed research pivot

The uncapped, meaning-bound cell command met all three project criteria on twelve fresh simulated environments. Use the per-bank direction/strength view and this command as the working architecture for the next research round. Keep expiry and semantic closure explicit. The fixed 63-tick command and the 25% budget met the practical equivalence criteria under the tested review schedule. Reliable recovery of prior forms after a reversal remains open. [Confirmation, scope and measurements](../results/cell-duration-confirmation-v1/findings.md)

Treat recovery as a diagnostic. At 128 observations after the polarity returned, 22.9% of cases under the adopted command had recovered both original local partitions. That endpoint is compatible with slower structural recovery or with reorganisation. Distinguishing them requires observing the form and its predictions over time.
