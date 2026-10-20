# Experiment 014: reopening is not the end of abstraction

Completed 2026-10-20. **The primary criterion failed.** The added reclosure
operation nevertheless demonstrated a useful capability: a nested learner
could return to a smaller interface after detail stopped being necessary,
while preserving detail when it remained consequential.

All ten remapping runs finished with valid coarse interfaces, versus four
under the original failure-only rule. All ten persistent-breach runs kept
the relevant fine interface, with identical predictions under both variants.
But only seven of ten temporary-breach runs completed the required return to
abstraction. Initial transfer also passed in only seven of ten fresh seed
pairs, below the fixed requirement of eight.

The [protocol](../../experiments/reclosure_protocol.md), implementation, tests
and independent auditor were hashed before the single benchmark run. There
was no tuning, rerun or implementation correction after observing results.

## The added operation

Experiment 013 could restore prediction by bypassing a faulty lower abstraction,
then leave the bypass in place after the lower learner recovered. Its upper
revision rule acted only when prediction loss was high.

Experiment 014 preserves that rule and adds a separate test while detail is
exposed. A coarse challenger must be adequately predictive on **two successive
fresh selection batches**. The same challenger table remains frozen between
tests. Failed evidence clears it; a change in exported lower groups invalidates
its accumulated support. If both tests pass, the coarse predictor replaces
the fine interface.

The comparison is predictive log loss, without a weighted complexity reward.
Adequacy means loss <=.55 nats and at most .02 nats worse than the incumbent
on each batch. Preferring the smaller interface within this tolerance is a
supplied structural preference. The two-witness rule is constructed, not learned.
It is not a statistical noninferiority test or a general consolidation theory.

Both variants receive the same data, use identical local learners and fit the
same three upper candidates. The new rule reuses a prepared coarse candidate,
adding scoring and up to eight pending table cells, but no observations or fits.
The same selection batch serves the original failure decision and the extra
comparison; that adaptive use of evidence is part of the policy being tested.

## Conditions and fixed results

Fresh environments 400–404 were crossed with learner seeds 400 and 401.
Each run retained the 013 acquisition and composition stages, followed by
768 adaptation records and twelve reviews. The four paired branches were:

* **Persistent:** no change.
* **Remap:** lower group membership changes while the upper form relationship
  remains valid.
* **Breach:** a formerly hidden detail becomes relevant and stays relevant.
* **Transient:** the same detail matters through record 384, then ceases to
  matter. The learner receives no switch signal and retains its buffers.

Validity requires exact local groups, accuracy 1 against the most probable
outcome, and expected loss within .10 nats of the 10% noise oracle. All
acquisition failures remain in the reported denominators.

| Fixed criterion | Observed | Result |
| --- | --- | --- |
| Transfer valid in at least 8/10 seed pairs for both variants | 7/10 each | **Fail** |
| Persistent: valid coarse final interface in at least 8/10 | 8/10, versus 2/10 control | Pass |
| Remap: valid coarse final interface in at least 8/10 | 10/10, versus 4/10 control | Pass |
| Persistent prediction cost <=.02 nats | −.001424 mean main loss | Pass |
| Breach: correct fine interface and valid prediction in at least 8/10 | 10/10 | Pass |
| Breach prediction cost <=.02 nats | Zero; identical predictions | Pass |
| Transient: complete fine-to-coarse trajectory in at least 8/10 | 7/10 | **Fail** |
| Fewer late raw-state accesses in at least 8/10 transient pairs | 7/10 lower, 3/10 equal | **Fail** |
| At least 25% mean reduction in late raw-state accesses | 40% | Pass |
| Transient post-change prediction cost <=.02 nats | +.002952 nats | Pass |

Five environments crossed with two proposal seeds are not ten independent
task families. These are descriptive results against practical thresholds,
not significance claims.

## Returning to abstraction

In the remap branch, the new rule accepted seven reclosures across six runs;
four other runs needed no such operation to finish coarse. All ten ended with
exact local groups and valid coarse prediction. Mean main log loss was
.426315, compared with .432492 under failure-only revision.

In the persistent branch, the new rule accepted ten reclosures across six
runs. Some runs reopened and reclosed more than once following local errors.
Two others stayed coarse throughout. The remaining two opened detail at
review 704 and still exposed it at the end, despite correct final predictions.
Endpoint success therefore does not imply an absence of structural oscillation
or unnecessary intermediate exposure.

All 24 accepted reclosures across the whole benchmark were valid at their
immediate post-decision evaluations. This is a retrospective check on these
traces, not a guarantee that the evidence rule always preserves prediction.

## Preserving consequential detail

Neither variant reclosed in the persistent-breach branch, and all ten pairs
had exactly identical main predictions. All ten finished with the affected
module exposed and valid prediction. The added rule therefore had no observed
prediction cost in this negative control.

No new reclosure occurred during the first, detail-requiring half of the
transient branch either. Every run had the correct fine interface and valid
prediction at review 384. This matters: later simplification was a genuine
return from useful exposure, rather than never learning to expose the detail.

The supplied group-change invalidation rule was covered by a synthetic test,
but **no pending challenger was invalidated that way in the benchmark**.
Failed witnesses and ordinary replacements cleared evidence before that case
arose. The run cannot establish its empirical benefit.

## Temporary need for detail: useful, incomplete reclosure

When the original coarse relationship returned, seven runs reclosed:
two at review 576 and five at 640. That is 192 or 256 main observations after
the switch, together with the scheduled selection evidence.

During main records 513–768, mean parent raw-state reads fell from 1.0 per
prediction under failure-only revision to .6 under reclosure: a **40% reduction**.
The original rule never finished coarse in these ten runs. All twenty runs
nevertheless finished with exact local groups and valid predictions.
The distinction is representational simplification, not final predictive
success versus failure.

Over records 385–768, mean pre-feedback loss rose from .466741 to .469692,
a cost of .002952 nats. The mean guard passed, but the two environment-401
runs each paid .025851 nats, exceeding the .02 group margin individually.
We did not require every individual run to meet that margin.

Three runs failed to reclose within the budget:

* **Environment 402, both learner seeds:** a challenger passed at review 576
  but was .0354 nats worse than the fine incumbent on the next batch, exceeding
  the .02 tolerance. Later attempts also failed; the final difference was
  .0236 nats. Prediction was already correct with the finer interface.
* **Environment 404, learner seed 401:** successive candidates passed then
  failed their second comparisons. At review 704, the gap was .0228 nats.
  A new candidate passed at 768, leaving only one witness when the run ended.

These are finite-budget evidence failures, not absence of the coarse operation.
We did not extend the runs or loosen the margin. Requiring repeated evidence
can avoid premature changes while also delaying useful simplification.

## Fresh-seed transfer exposed an earlier weakness

The new policy begins only during adaptation, so it cannot explain the initial
transfer failures shared by both variants:

* Environment 403, learner seed 401 acquired the correct local grouping, then
  lost one partition at acquisition review 192 and did not recover it by 256.
  Withheld-composition accuracy was 2/3.
* Environment 404, both learner seeds failed to acquire one correct grouping
  by the end of acquisition. Withheld accuracy was 1/2.

Mean transfer expected loss across all ten was .460207. The seven successful
runs had exact groups and accuracy 1. All runs later attained valid final
prediction in every adaptation branch.

Experiment 013's 10/10 transfer result therefore remains a capability
demonstration on its fixed sample, not evidence of reliable acquisition across
fresh seeds. The new run preserves that limitation rather than conditioning
the interface comparison on successful initial learning.

## Costs, verification and interpretation

The 80 runs used 358,400 allocated and consumed outcome-label presentations;
each record's two local effects and composite effect count as three labels.
Twenty paired branch streams contained 89,600 generated labels, including
repeated acquisition across branches. These repetitions are not independent
environmental evidence.

There were 10,240 local candidate fits, 2,880 upper candidate fits and 32,640
external evaluation predictions. Reclosure added 7,840 challenger-selection
predictions and at most eight pending cells per run. Raw inputs remained
available to lower learners and search. Reduced parent access is not a sensing
saving, and extra candidate memory is not free.

Eight synthetic tests passed. An independent auditor reconstructed all worlds
and replayed all 80 runs, including the original failure rule, frozen challengers,
consecutive evidence, resets, predictions, interface access, metrics and costs.
All five manifests, including 010–013, remained unchanged.

This adds an explicit **reopen → evaluate → re-hide** capability to the nested
representation. It does not make the whole system reliable: acquisition,
retention under noise, decision timing and interface stability remain uneven.
Nor does it demonstrate learned consolidation, learned depth, general folds
or meta-learning.

The fixed experiment is complete. The accompanying
[capability consolidation](../relationships-interfaces-synthesis.md) separates
what this round demonstrated from what remains constructed or unresolved.

Full records: [report](report.md), [metrics](metrics.json), [traces](results.json),
[manifest](manifest.json). Verification:
`python3 -m unittest discover -s checks -p 'test_reclosure.py' -v`
and `python3 checks/audit_reclosure.py`.
