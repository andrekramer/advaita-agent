# Current evidence map

Updated 13 November 2026 after the direction/strength confirmation. The working
architecture for the next bounded round exposes fast and slow evidence for each
distinction and steers one cell until its meaning changes or the command expires.
[Architecture decision](../docs/direction-strength-architecture.md)

The first cell trial found that the uncapped command met its target benefit
and preservation limits. Fresh confirmation covered 12 environments, 240
instructions and 1,200 paired continuations. All 12 environments met the
acquisition criterion. A supplied script predicted the direction of 187 of 222
material effects using cell-specific evidence, compared with 105 using channel
totals to estimate the allocation. Uncapped steering improved target Brier by
0.001636 over abstention (95% paired interval 0.001223–0.002135) and met every
preservation limit. The 25% mass budget and 63-tick command met the declared
practical equivalence margins on this schedule. [First trial](direction-strength-v1/findings.md) ·
[Confirmation](cell-duration-confirmation-v1/findings.md) · [Scoring audit](cell-duration-confirmation-v1/audit.json)

Recovery of predictions and recovery of earlier forms are separate diagnostics.
At 128 observations after polarity return, upper modal accuracy averaged 69.7%
and both original local partitions were present in 22.9% of uncapped cases.
The endpoint leaves the relative contributions of fast and slow memory open.

| Question | Evidence available | Current boundary |
| --- | --- | --- |
| Can useful distinctions be learned, collapsed and recreated? | [006–009 synthesis](research-synthesis.md): bounded acquisition, collapse and reacquisition within supplied languages. [018](structural-consolidation-v1/findings.md) exercised these operations in the integrated learner, with incomplete trajectories. | The operations are demonstrated; reliable integrated lifecycles and discovery of new perceptual primitives are not. |
| Can relationships and reusable abstractions be learned? | [010–015 synthesis](relationships-interfaces-synthesis.md): joint dependencies, transfer to unseen compositions, two supplied interface levels and return to abstraction. | Candidate language, wiring, depth and local feedback are constructed. Acquisition and reclosure were not consistently reliable. |
| Do these operations coexist in a continuing implementation? | [016–018 synthesis](consolidation-round-synthesis.md): shared-core parity on 380 saved traces, then audited protection/interface and structural-integration experiments. | Engineering integration passed; the empirical criteria for reliable combined behavior did not. |
| Does longer recovery produce stable generalisations? | [019](consolidated-recovery-v1/findings.md): stable late prediction in 10/10 integrated pairs per history; stable structure in 6/10 form-return and 9/10 per detail history. | Correct output can conceal damaged forms or raw bypasses. Recovery can be followed by regression. |
| Does protection distinguish misleading evidence from lasting change? | [020](consolidated-protection-v1/findings.md): fewer noise/burst errors, with delayed genuine-change recovery and excess loss. | A measured stability/adaptation trade-off, not reliable discrimination or a learned protection rule. |
| Can useful earlier knowledge survive adaptation? | [021](prospective-memory-v1/findings.md): early preserved snapshots in 7/10 pairs per history, but inconsistent benefit and selection effects without recall. | Snapshot preservation is partly demonstrated; provenance and retrieval counts alone do not establish usefulness. |
| Does reinstatement add value beyond blocking fresh updates? | [022](memory-selection-v1/findings.md): independent admission improved mean early-return loss by .045996 nats versus ignoring memory; 4/10 pairs improved, all with early snapshots. | Stronger evidence of useful memory access in some cases. The 8/10 consistency criterion failed; one reversed pair incurred a .131837-nat cost. Interface restoration versus parameter reuse is not isolated. |
| Does explicit ownership of predictions and meanings improve learning? | [024](explicit-roles-v1/findings.md): 300 audited runs with timing/update controls. R128 reduced meaning changes but had 113 primary structure errors versus 113 for U128, with zero improving pairs. | No measured representation benefit from this minimal role implementation. Slower reviews also delayed detail recovery. The original reference remains in use. |
| Does adaptation history improve structural search? | [024](explicit-roles-v1/findings.md): H128 improved mean adaptation loss by .029189 nats against R128 in 8/10 pairs. | Full gate failed: mean return costs against B64 exceeded .02 in both detail histories, and one individual cost against R128/U128 exceeded .10. This fixed proposal heuristic is not meta-learning. |
| Does migration into slow memory preserve useful learning? | [026](memory-control-v2/findings.md): 350 audited runs. Selective memory improved familiar early-return loss by .070879 nats against fast-only in 10/10 pairs; gap validity improved from 0/10 to 10/10. | Single slow memory and the original reference also retained the task. The new family stores raw sufficient statistics supporting forms, not autonomous abstract-form memory. |
| Does selective admission adequately control memory? | [026](memory-control-v2/findings.md): selection improved the declared adaptation average by .023749 nats against unconditional transfer in 9/10 pairs; guards against that control passed. All 80 improving upper transfer proposals after reversal were rejected by the adequacy gate. | Overall criteria failed. Selective reversal had 0/10 final full validity despite 10/10 correct local partitions. Admission control did not adequately revise contradicted retained evidence. No policy promotion. |
| Does weakening old evidence help beyond admitting new evidence? | [027](memory-revision-v1/findings.md): secondary benefits with a mistimed primary window. [028 confirmation](memory-confirmation-v1/findings.md): unchanged learner, 350 fresh audited runs, all primary gates passed. Mean post-intervention gain .033904 nats in 10/10 pairs and 5/5 environment means; final reversal validity 3/10 to 10/10. | A confirmed benefit against admission alone in these constructed tasks. Remapping improved in 6/10 pairs and tied in four; faster-forgetting controls and the original baseline still had lower adaptation loss. No universal superiority or policy promotion. |
| Can selective weakening preserve useful memory? | [027](memory-revision-v1/findings.md): no selective weakening in stable, brief-reversal or familiar-return histories; combined gap validity 10/10. Retention-oriented gain against uniform weakening was .022737 nats in 10/10 pairs. | Uniform removal was not matched in removed mass. Fast-only adapted better but lost confidence across the gap. Two proposal replicates still ended with an incorrect local form and accurate raw-bypass output. No universal benefit or learned controller is established. |
| Is optional memory control integrated without behavior changes? | [029](memory-integration-v1/findings.md): common runtime reproduced all 350 saved traces and exact native checkpoints, including midway restore. | Integration by composition around alternative frozen engines; the original remains default. No new archive-plus-weighted-memory algorithm. |
| Does memory control handle recurring changes and rare knowledge? | [030](memory-lifecycle-v1/findings.md): 120 audited runs. Settled gain .043923 nats over admission-only and rare-context gain .180382 over fast-only, both in 10/10 pairs. | Full criterion failed: final validity 4/10 in repeated reversals and 7/10 in rare history; early revision costs exceeded limits. Rare-history combined and admission-only behavior matched. |
| Can an explicit controller use inspection to steer learning? | [031](memory-steering-v1/findings.md): 60 audited runs; one diagnostic-led weakening action gained .008889 nats on composite prediction in 4/10 changing pairs. Stable controls were inactive; collateral guards passed. | Full steering gate failed. Six local interventions improved local probability estimates without changing primary-window composite predictions. This was a scripted controller, not a human/LLM interpretability study; all changed environments happened to affect node0. |
| Can inspection forecast intervention relevance? | [032](introspection-v1/findings.md): 30 audited decision trajectories, 120 continuations. Future-effect direction 28/29 correct versus 17/29 from disagreement alone; aware control gained .005957 nats on average over disagreement. | Full gate failed: 4/20 gains, 15 ties, 1 loss; repeated-history validity 7/10. Five immediate-effect failures were entirely reproduced by refitting stale upper tables. Supplied dependency knowledge and a hand-written controller, not learned introspection. Post-review consistency needs attention before broader steering. |
| Can we protect one distinction while making another more plastic? | [033](selective-steering-v1/findings.md): 180 audited runs. Locked partitions remained correct at all burst checks; faster local slow-memory decay improved the flexible predictor by .076595 nats in all 20 changing pairs. Refresh-only preserved all baseline online predictions and ordinary decisions. | Full gate failed: mean composite loss worsened by .013170 nats; final reversal validity fell from 9/10 to 6/10 and post-release costs exceeded limits. Controls obey supplied instructions; correct local steering is not reliably beneficial global steering. |
| Must local and downstream plasticity increase together? | [034](coordinated-steering-v1/findings.md): 150 audited runs. Downstream plasticity gained .096068 nats over protection-only in all 20 changing pairs. Joint plasticity beat local-only and unsteered controls. | Joint plasticity added no active-window benefit over downstream-only: 16 ties, four losses; mean gain −.001692 nats. Full gate and interaction criterion failed; reversal return cost over unsteered was .066130 nats. Supplied scheduled controls, not learned coordination or a universal bottleneck claim. |
| Does ending plasticity after adequate prediction improve retention? | [035](temporary-plasticity-v1/findings.md): 250 audited runs. Evidence-based closure retained active adaptation: .075449-nat gain over protection-only in all 40 changing records (20 distinct matched pre-return trajectories). Protected forms and final validity passed. | Full criterion failed: early return worsened by .023147 nats versus the long boost, with 2/20 positive pairs; reversal preservation guards failed. The shortest pulse improved pooled return by .011814 nats but lost too much adaptation. No tested duration policy passed. A fixed closure rule, not meta-learning or restored prior knowledge. |
| Can a preserved predictor help without blocking ongoing learning or losing its parameters? | [036](preserved-prediction-v1/findings.md): 180 audited runs; all pairs confirmed immutable snapshots, with exact active-prediction and review parity across discard/shadow/recall. Familiar-return gain .011777 nats in 6/20 pairs; all 20 eventually used recall. | Full criterion failed: mean gain and consistency below target; polarity rechange incurred .099819-nat later cost from the first 64-record authorization interval. Delayed compatible meanings and stale admission limit recall. Output reuse, not faster active representation repair or learned memory control. |
| Can recall be blocked, released and withdrawn from fresh performance evidence? | [037](recall-withdrawal-v1/findings.md): 240 audited runs; all 60 explicit block/release runs obeyed commands. Evidence withdrawal gained .246703 nats on immediate rechange, retained useful recall and passed preservation/validity guards with exact active-learning parity. | Full gate failed on 10/20 gains versus 14 required (ten ties, no losses). Tied pairs had no recall active in that window; this post-outcome explanation does not change the denominator. Transient costs and stable-task withdrawals remain; explicit timing is supplied and the evidence controller is fixed, not learned. |
| Does it learn how to learn? | No experiment in these rounds adapts its learning rules through experience and validates improved learning on held-out families. | No meta-learning claim. Changes in protection or evidence state under fixed rules do not suffice. |
| Are the full R-rule/IVSR dynamics necessary, or is this safer? | Earlier controls sometimes matched or outperformed richer learners; [019–022](consolidated-learner-test-round-synthesis.md) identify further benefits and costs of individual rules. | Necessity, general superiority, formal unification of the conceptual influences and a safety advantage remain unestablished. |

## What is learned and what is supplied

The structural experiments learn predictive estimates, local context groupings,
selected dependencies and which available ports a prediction interface uses.
They can preserve and select frozen predictors under explicit policies.

Raw inputs, action alphabets, local outcome channels, possible groupings and
connections, architecture, memory capacity, proposal machinery, review schedules,
thresholds and update rules remain supplied. Scheduled actions do not demonstrate
autonomous exploration. Withheld compositions test generalisation within the
constructed process; fresh seeds do not constitute new task families.

Predictive log loss supplies the principal evidence for selection. Adequacy
and reduction rules still impose explicit structural preferences. The work
does not eliminate design choices by avoiding a composite utility function.

## How to read the results

Separate prediction, representation, memory utility and resource cost. Report
whole trajectories as well as endpoints, mean gains alongside pairwise failures,
and actual comparisons rather than combining favorable results from different
variants. A failed primary criterion remains failed even when a component helps.

The original integrated reference is retained by the
[023–024 architecture decision](explicit-roles-architecture-decision.md), following
the earlier [closure record](consolidated-learner-test-round-synthesis.md#baseline-and-claim-at-closure).
No new policy is promoted. Conditional role confirmation was not opened because
the primary role gate failed. The subsequent [memory-control round](memory-control-v2/findings.md)
is also complete with benefits and failed full criteria. The subsequent
[revision round](memory-revision-v1/findings.md) found later benefits from
selective weakening, alongside a misaligned primary window and remaining
structural failures. The [fresh confirmation](memory-confirmation-v1/findings.md)
passed its properly timed primary test and preservation guards with unchanged
learning rules. This supports selective revision of retained evidence within
the tested tasks, while preserving the earlier failures and simpler-control
advantages. [029–031](memory-integration-round-synthesis.md) subsequently integrated
the optional variant and tested recurring changes, rare distinctions and one
scripted control. The new API passed compatibility, but the two broader empirical
gates failed. [032](introspection-v1/findings.md) then demonstrated better future-effect
forecasts with supplied dependency knowledge, while failing full immediate-effect
and steering criteria. [033](selective-steering-v1/findings.md) then supplied a coherent post-review
snapshot in an experimental subclass and tested selective local locks, plasticity
and release. Local benefits passed, but composite usefulness and preservation
failed. Coordination with downstream learning, human/LLM interpretation and
reliable steering remain open. No default promotion.

[034](coordinated-steering-v1/findings.md) subsequently isolated local and downstream
plasticity. Downstream changes provided the measured active composite benefit;
adding local plasticity did not improve it further. Preserving returning knowledge
remained a problem. [035](temporary-plasticity-v1/findings.md) then tested boost
duration and evidence-based closure. Adaptation remained useful, but no tested
duration met the adaptation/retention bundle. The first audit encountered a
log/log1p serialization discrepancy; a disclosed supplement reconstructed all
250 runs without changing any decision or frozen result. A separate preserved-
predictor integration study followed as [036](preserved-prediction-v1/findings.md).
All snapshots were confirmed and active learning was unchanged, isolating actual
prediction reuse. However, early usefulness was inconsistent and stale recall
harmed the next reversal. Faster withdrawal is tested in 037 below; independently
usable archived encodings remain untested. The default is unchanged.

[037](recall-withdrawal-v1/findings.md) completes the bounded first steering round.
Its withdrawal rule improved exposed rechange cases while preserving useful
recall, with a failed prespecified consistency criterion and remaining limits.
The [closure synthesis](steering-round-one-synthesis.md) separates command
execution, usefulness and limitations. Further experiments stop for the user
goals review; no default or safety claim is promoted.

[038](control-consolidation-v1/findings.md) subsequently implements the
user-authorized consolidation of memory, inspection and steering. An optional
common interface over the existing schema-37 path reproduced all 240 saved
trajectories exactly and passed six deterministic interaction/contract tests.
This is engineering compatibility evidence: no new random worlds, policy tuning,
human/LLM comprehension finding or empirical usefulness result. The original
default and previous failed criteria remain unchanged. Fixed memory timing and
excluded combinations are documented in the
[architecture contract](../docs/controlled-learner.md).

The [Heaviside Stage 1 side quest](heaviside-prediction-v1/findings.md), completed
2026-11-13, tests direction and retained strength in an isolated binary predictor.
An independent implementation reconstructed all 2,304 development and 18,000
confirmation run records (200 fresh confirmation seeds). Vector and scalar
forecasts agreed within 5.55e-16. Larger imposed support reduced revision, a
property already present in native count tables. The selected vector achieved
the declared trade-off against selected fixed gain, with small short-prefix
benefits and no meaningful long-prefix difference, but failed the combined gate
against the rolling-window control: it adapted faster to reversal while suffering
greater post-streak loss. This is a fixed-row retention-policy comparison, not
evidence of geometric-coordinate superiority or improved native-agent learning.
The native reference and selective-weakening comparison follows as Stage 2 below;
the architecture and defaults are unchanged.

The [Heaviside Stage 2 comparison](heaviside-native-v1/findings.md), also completed
2026-11-13, evaluates alternative output predictors for one supplied familiar
context while native learning and reviews continue. Forty fresh outcome histories
produce 240 prefixes, 720 native future trajectories and 4,320 output records,
all independently reconstructed. One acquired state and proposal state are reused;
the output records are not independent experimental samples.

The direction/strength predictor failed the prespecified native-improvement
criterion. It adapted faster to reversal but incurred greater stable and
post-streak loss. Against the native combined admission/weakening learner, paired
Brier differences were +0.007270 (stable), +0.017776 (post-streak) and -0.028918
(reversal observations 129–256). Negative differences favor the predictor.
The separate fixed-gain comparison passed, with post-streak benefit confined to
short histories and no meaningful long-history difference. Vector/scalar
forecasts remained equivalent within 5.55e-16; this is not geometric superiority.

Selective weakening did act: 53 accepted composite weakenings occurred in
long-history reversals, with the earliest forecast effect at observation 193.
Combined admission/weakening improved reversal loss over admission alone by
0.003294 averaged across histories (95% paired interval: improvement of
0.002071–0.004549). No weakening occurred in the other history/future conditions.
This supports a bounded retention-policy trade-off, not a replacement of the
architecture. The supplied output address, differing uses of review evidence,
and single acquired state limit the comparison; category discovery, transfer and
broader competence were not tested. No defaults changed and no further benchmark
is scheduled by this result.

The [strength-inspection follow-up](strength-inspection-v1/findings.md), completed
2026-11-13, tests an additional read-only description of each prediction cell's
fast/slow evidence. The existing inspection supplies row totals and channel-wide
bank masses; the new adapter exposes the allocation for each row. Raw counts and
direction/strength are equivalent encodings of that additional information, and
produced the same commands. No learning equations or defaults changed.

Independent reconstruction passed for 72 fresh acquired trunks and 288 controlled
continuations across 12 environment seeds. Conditional one-observation effect
forecasts were exact to numerical precision. A supplied 64-step approximation
using bank allocation reduced mean absolute future-effect error from 0.000530
to 0.000359 Brier units relative to the existing-view proportional-allocation
approximation. Overall effect-direction accuracy was 209/216 versus 197/216;
among the 31 effects exceeding .001 in magnitude it was 25/31 versus 12/31.
The latter is a [descriptive breakdown](strength-inspection-v1/descriptive-diagnostics.json),
not a new criterion. Most tested effects
were negligible, so the aggregate accuracy alone is insufficient evidence.

Bank-informed selection reduced active-window target Brier by 0.002126 relative
to existing-view selection (95% environment-cluster interval 0.001027–0.003517),
with positive means in 9/12 environments; its improvement over no intervention
was 0.010560. But the full steering criterion failed preservation: three
output/history guards failed when earlier conditions returned, with maximum
case cost 0.081746. The richer view also caused more actions (38 versus 24),
including more hindsight-unnecessary actions (6 versus 2). These results support
better bounded effect prediction and short-term selection by this supplied script,
not uniformly beneficial control.

This is additional-information evidence, not evidence that geometric notation
is superior or easier for a human/LLM to understand. The
[blinded reader task pack](strength-inspection-v1/reader-tasks/README.md) compares
equivalent raw/named information but remains unscored. No reader-comprehension,
general safety or meta-learning claim is established.
