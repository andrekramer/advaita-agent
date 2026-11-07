# First steering round — closure synthesis

Completed 2026-11-06. **The first steering round is closed.** All 240 runs in the
final study passed independent verification. The original reference remains the
default; no further experiment is scheduled. Review the findings and choose the
next goals with the user before extending the system.

The round demonstrates inspectable, selective control with useful effects in
small constructed tasks. It also identifies limits in downstream propagation,
retention, meaning compatibility and withdrawal timing. It does not establish a
generally reliable controller.

## What this round asks

Can an inspectable instruction selectively change learning or prediction,
produce an intended effect, limit harm elsewhere, and relinquish control?
Execution, usefulness and limits are different findings. An obeyed instruction
can be harmful; a useful local change need not improve downstream prediction.

This round brings together existing component studies 031–036 and the final
037 comparison. They are successive optional variants, not one configuration
that has demonstrated every positive finding simultaneously. Their fresh seeds,
shared histories and proposal draws are not independent samples of intelligence.
Earlier failed criteria remain failed.

## Evidence and decisions

| Study | Execution / local evidence | Utility and preservation | Decision |
| --- | --- | --- | --- |
| [031](memory-steering-v1/findings.md), 60 runs | Scripted selective weakening executes. | Composite mean gain .008889 nats, 4/10 changing pairs; full steering gate failed. Local confidence changes often did not propagate through categorical upper interfaces. | Retain as mechanism evidence; do not promote the target-selection heuristic. |
| [032](introspection-v1/findings.md), 30 decision trunks / 120 continuations | Future-effect forecasts correct in 28/29 versus 17/29 from disagreement; inspection exposed stale upper tables. | Full gate failed; control benefit in 4/20, with 15 ties and one loss. Some apparent immediate effects were refitting effects. | Keep dependency-aware diagnostics; require coherent snapshots for further steering. Human/LLM interpretation remains untested. |
| [033](selective-steering-v1/findings.md), 180 runs | Coherent post-review refresh preserved original online predictions. Local partition protection and flexible-local adaptation worked; wrong-target and release controls exposed limits. | Flexible-local gain .076595 nats in 20/20 pairs, but composite loss worsened .013170 on average and preservation failed. | Retain lock/plasticity/release as experimental operators; assess effects at the intended output. |
| [034](coordinated-steering-v1/findings.md), 150 runs | Local versus composite plasticity isolated under fixed protection. | Downstream-only gained .096068 nats over protection alone in 20/20. Added local plasticity gave 16 ties/four losses; full gate and interaction criterion failed. | Retain downstream plasticity as a targeted experimental option. No evidence for obligatory joint plasticity. |
| [035](temporary-plasticity-v1/findings.md), 250 runs | Fixed durations and evidence-responsive closure executed and restored rates. | G retained adaptation but worsened early recovery .023147 nats versus the long boost; no duration policy passed. | Set aside this closure rule as a retention solution. Ending a boost does not restore prior knowledge. |
| [036](preserved-prediction-v1/findings.md), 180 runs | Immutable snapshots confirmed in all pairs; actual recall isolated from active learning and selection blocking. | Early-return gain .011777 nats, 6/20; full gate failed. Delayed meanings limited early use; stale recall caused .099819-nat later polarity cost. | Keep frozen prediction reuse experimental. Preserve the distinction between active learning and routed output. |
| [037](recall-withdrawal-v1/findings.md), 240 runs | All 60 explicit block/release runs obeyed their commands; 120 commands, no blocked archive outputs, and no stale authorization revived on release. Active learning matched exactly across arms. | Evidence withdrawal gained .246703 nats on immediate rechange. Ten pairs improved, ten tied, none worsened; the 14/20 consistency gate failed. Preserved recall, collateral costs and validity passed. | Retain the permission operator and the evidence-withdrawal rule as experimental. No default promotion or automatic follow-up. |

## Final study: what improved and what remains limited

The evidence rule used 16 consecutive recalled predictions and their observed
labels to compare archived and active losses. It did not see world truth or a
change marker. The separate explicit arm used a supplied schedule, so its success
must not be described as autonomous detection.

Immediate-rechange loss fell by .246703 nats on average relative to current recall.
Whole-return gain over shadow was .021621 nats, positive in all 20 returning pairs.
The tighter guards against losing useful recall and every general collateral
preservation guard passed. Active and deployed endpoint validity were 9/10 per
history; exact active learning-state parity establishes that the difference was
in output authorization, not extra learning or blocked structural updates.

The full empirical criterion nevertheless failed: 10/20 immediate-rechange gains
rather than the required 14/20. A post-outcome inspection found that the other ten
pairs had no current recall in that window. In all ten exposed pairs, current
recall supplied 64 predictions while evidence withdrawal supplied 16, stopping
at tick 1552. This explains the ties but does not change the declared denominator
or turn the test into a primary pass.

Withdrawal retained a detection cost. Relative to shadow, immediate-rechange
mean costs were .018434 nats in category-return tasks and .095295 in polarity-
return tasks, despite passing the longer-window preservation limits. The evidence
monitor also withdrew 25 times in stable tasks; it is a recent-performance rule,
not a perfect detector of environmental change. The supplied command and evidence
rule had identical immediate-rechange gains on this batch, whose changes aligned
with review boundaries. New timings and task families remain untested.

The result supports an explicit permission boundary and a useful bounded
withdrawal mechanism. It does not settle delayed restoration of compatible
meanings, eliminate transient errors, or justify learning a control policy yet.

The 035 independent audit required a disclosed serialization-only correction:
log/log1p rounding affected checkpoint hashes, not decisions. Its frozen sources,
worlds and outcomes remain intact. The correction and original failure are linked
from that study's findings, not omitted from this synthesis.

## Control inventory and implementation map

| Operator / capability | What it affects | Conditions and persistence | Release / principal limitation | Optional implementation |
| --- | --- | --- | --- | --- |
| Inspect current state and evidence | Read-only forms, predictions, masses, pending decisions and history | Detached snapshots at the declared boundary | Older inspection boundaries can expose stale upper tables; subsequent variants refit coherently | [ContinuingLearner](../advaita/continuing.py); coherent [SteerableMemory](../advaita/selective_steering.py) descendants |
| Discount a slow channel | Halves one entire slow evidence table, with pending-state clearing and refit | Explicit operation after a completed review, with reason and state hashes | Irreversible loss of evidence within that trajectory; stopping the command cannot restore it | [ContinuingLearner](../advaita/continuing.py), tested in 031–032 |
| Lock a local distinction | Holds a local partition; probabilities and evidence still update | Replaces configuration after review; persists until release | Wrong locks prevent needed category change. Group label ordering can still change | [SteerableMemory](../advaita/selective_steering.py), schema 33 |
| Change selected plasticity | Changes slow-evidence half-life from 1024 to 128 for selected channels | Explicit review-boundary configuration, with history and checkpoint continuity | Whole-channel decay, not arbitrary relation editing. Restoring the rate does not restore memory | [CoordinatedMemory](../advaita/coordinated_steering.py), schema 34, adds composite channel 2 |
| End a boost using evidence | Restores ordinary composite decay after adequate recent reviews | Fixed threshold/controller and supplied opening/deadline | Tested 035 rule did not improve returning knowledge reliably | [TemporaryPlasticity](../advaita/temporary_plasticity.py), schema-35 wrapper; not in the 036/037 path |
| Preserve and use a predictor | One frozen composite output alternative with bound input meanings | Supplied capture time; fresh confirmation and admission; active learning continues unchanged | Meanings may be unavailable until relearned; admission may outlive usefulness | [PreservedPrediction](../advaita/preserved_prediction.py), schema 36 |
| Block and release recall permission | Whether the preserved predictor may supply output | Explicit reason/source after a labelled observation; block overrides ordinary admission | Release allows a future fresh admission, not automatic reinstatement | [RecallWithdrawal](../advaita/recall_withdrawal.py), schema 37; 037 |
| Withdraw recall from observed performance | Ends current authorization after a full 16-observation loss comparison | Uses pre-label predictions and observed labels; can reauthorize at a later fresh review | Detection lag and noisy monitoring; a fixed controller, not learned regulation | [RecallWithdrawal](../advaita/recall_withdrawal.py), `evidence` policy; 037 |

The original `ContinuingLearner` default still uses the original reference.
The experimental path extends the coherent control class with a preserved
predictor and then recall permission. It does not incorporate every earlier
wrapper, heuristic or archive policy. No API promises arbitrary locking of an
entire long-term core, upper partition locks, or control of individual relations.

## What the evidence can support

The system has explicit, inspectable intervention points. Tests can distinguish
changes in a representation, probability estimate, memory mass and deployed
prediction. Control requests and subsequent state can be reconstructed, including
checkpoint continuation. These are useful foundations for studying steering.

They do not yet establish reliable general steering. Local success may not
propagate downstream; protecting a distinction can obstruct correction; recently
adequate recall can become harmful. The constructed task roles, capture schedule,
representation language, thresholds, available commands and feedback channels
remain supplied. No experiment here evaluates a person's understanding of the
inspection record or an LLM's choice of interventions.

We have not shown that all R-rule/IVSR dynamics are necessary, that these controls
make the learner safer, or that it discovers its own goals. Adaptive behavior
under fixed rules is not meta-learning. Controls support scrutiny and experiments;
they do not by themselves guarantee benign behavior.

## Decisions that remain for the goals review

Keep the original default. Retain the coherent lock/plasticity operators and
immutable-prediction pathway as experimental capabilities with explicit limits.
Do not promote the 031 target-selection heuristic, 035 closure rule, or 036 recall
policy to generally reliable steering methods. Retain the 037 block/release operator as an execution-tested experimental
control. Retain its evidence-withdrawal rule as a promising bounded option, with
the failed consistency criterion, transient costs and fixed timing prominently
recorded. No policy is promoted to the default.

Review candidate next goals with the user before more experiments:

1. A coherent operator-facing inspection/control interface, followed by a bounded
   human or LLM study of choosing interventions from the available evidence.
2. A small independent task family that challenges the current positive results.
3. Memory research separating reconstruction of input meanings from admission,
   withdrawal and preservation of a predictor.
4. Consolidation of a supported optional configuration with explicit contracts.
5. Learning control policies and evaluating their transfer, only if the earlier
   evidence warrants a separate meta-learning programme.

Choose among these after reviewing the completed round. No additional threshold
search, memory extension, confirmation batch or benchmark is scheduled by closure.
