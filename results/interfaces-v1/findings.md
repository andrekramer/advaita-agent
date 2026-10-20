# Experiment 012: hiding detail without forgetting it

Completed 2026-10-20. **The fixed primary criterion passed.** Within a supplied
feature-projection language, retaining a learned detailed predictor behind a
simpler prediction interface improved recovery when the old relationship
returned. It did not help when the relationship returned with opposite outcomes.
The continuously exposed control adapted better to that novel transition.

This establishes a bounded benefit from separating predictive visibility from
stored knowledge. It does not establish general fold learning, meta-learning,
or the necessity of the full R-rule/IVSR dynamics.

## What was tested

Following Experiments 010 and 011, all variants first used the unchanged
shuffled-deck learner to discover a relationship between supplied binary
features. After 384 observations, each kept its own learned feature set K.
The subsequent interface could expose K or a subset of K. No failed discovery
was repaired with the true features.

The world had six observed features, random binary actions and 10% outcome
noise. The relevant relationship initially depended on two features and action.
Three branches then tested:

* **Return:** the relationship became simpler, requiring one feature, then the
  original two-feature relationship returned.
* **Novel:** the same simplification occurred, then the two-feature relationship
  returned with its outcomes inverted.
* **Persistent:** the original relationship remained useful throughout.

Three variants shared the same acquisition history and paired observations:

* **Retain:** select a smaller prediction interface while keeping a frozen
  detailed snapshot available for evidence-tested retrieval.
* **Delete:** use the same interface choices but erase the snapshot on the
  first simplification. Keep the feature identities and permission to rebuild.
* **Open:** keep the acquired feature set exposed and refit continuously.

Fresh estimates used the latest 192 main observations. At reviews every 64
observations, candidate interfaces competed on recent outcomes and the winner
faced 32 new selection outcomes. A retrieved snapshot stayed frozen until a
review replaced it; it was not silently overwritten on the next main update.

The [protocol](../../experiments/interfaces_protocol.md), implementation,
tests and independent auditor were hashed before the single benchmark run.
There was no tuning, rerun, or implementation correction after seeing results.

## Declared results

All figures include the acquisition failure. Lower log loss is better.
The complete-trajectory requirement included correct acquisition, appropriate
middle-phase exposure, final predictive recovery, and final sensitivity to
both relevant inputs.

| Fixed criterion | Observed | Result |
| --- | --- | --- |
| At least 8/10 retain trajectories in each branch | 9/10 return, 9/10 novel, 9/10 persistent | Pass |
| Lower return-transition loss than delete in at least 8/10 pairs | 9/10 lower, 1/10 equal | Pass |
| Mean return-transition improvement at least .02 nats | .078165 nats | Pass |
| Novel-transition cost versus delete at most .02 nats | .000000 nats | Pass |
| Persistent post-acquisition cost versus open at most .02 nats | −.000273 nats | Pass |

These are practical thresholds fixed in advance, not statistical significance
or formal noninferiority tests. There are five environments crossed with two
proposal seeds, not ten independent task families. Many trajectories converge
to identical models across the two proposal seeds.

| Branch and measure | Retain | Delete | Open |
| --- | ---: | ---: | ---: |
| Return: main loss over observations 769–960 | .569511 | .647676 | .593616 |
| Novel: main loss over observations 769–960 | .663578 | .663578 | .600678 |
| Persistent: main loss over observations 385–1152 | .382445 | .382445 | .382718 |
| Return: complete trajectories | 9/10 | 9/10 | 0/10 |
| Novel: complete trajectories | 9/10 | 9/10 | 0/10 |
| Persistent: complete trajectories | 9/10 | 9/10 | 9/10 |

The open control's zero complete trajectories in changing worlds is expected:
the criterion requires simplifying the visible interface, which open cannot
do. It is a prediction and exposure control, not a contender for that structural
criterion. Retain and delete reached the same final endpoints; the principal
retention benefit was during adaptation.

## What retention contributed

In all nine successfully acquired return runs, retain retrieved the old pair
at review 832: 64 main observations after its return, plus the review's 32
selection observations. Its evaluation immediately met the predictive recovery
criterion. Delete and open recovered at review 896 in two of those runs and
960 in seven. Recovery is sampled at reviews, not measured continuously.

Across all ten runs, retained memory reduced early return log loss by
**12.1% relative to delete**. The nine useful retrievals were deployed for
64–192 subsequent main predictions before replacement by fresh estimates.
This is stronger evidence for reusable predictive memory than merely observing
that a two-feature structure reappeared.

In the novel branch, retain and delete had identical main predictions throughout
the final phase. The archived prototype appeared among 18 post-change candidate
sets but was never accepted. Only one reached the independent selection batch;
that was from the failed-acquisition run, and it was rejected. The other
archived candidates lost the preliminary ranking. Thus evidence screening
avoided stale retrieval in these conditions; this is not a general guarantee.

Novel adaptation nevertheless exposes a cost of simplification. Both retain
and delete had .062900 nats higher early transition loss than open. Retaining
the wrong old relationship did not solve a genuinely new predictive problem.
The final-phase expected losses were the same for retain and delete.

In the persistent branch, all nine successfully acquired pairs remained exposed
at every subsequent review. Retain and delete behaved identically. The tiny
aggregate advantage over open came from the failed-acquisition run's subsequent
simplification, not from useful retrieval or improved retention of a correct pair.
The reported “predictive recovery” field is simply the first valid evaluation
after 768 in this branch; there was no actual world change to recover from.

## Failures and intermediate behaviour

Environment 204 with proposal seed 200 acquired only feature `[3]`, instead of
the relevant pair `[2,3]`. Since subsequent proposals were restricted to subsets
of acquired K, all three variants lacked the missing coordinate permanently.
That run failed in all branches and remains in every aggregate.

Simplification was not perfectly stable between endpoints. In environment 200,
both proposal seeds briefly reopened detail at review 704, then hid it again
at 768. The failed-acquisition retain run also retrieved its inadequate
singleton at 704 and hid it at 768. That accounts for the one recorded retrieval
in the novel branch: it occurred before the novel change, not after it.
The return branch's ten retrieval events consist of nine useful final-phase
retrievals and this earlier event.

These intermediate changes matter: passing the endpoint criterion does not
mean every structural decision was useful or stable.

## Information hidden and resources retained

Ordinary prediction accesses only coordinates exposed by its interface; the
access wrapper rejects other coordinate requests. The prediction-interface
object has no archive. This is a tested software boundary, not a security
isolation claim.

At the middle endpoint, the nine successful retain runs exposed one feature
and four probability-table cells while privately retaining eight cells for
the learned pair. The delete runs exposed the same four cells and kept no
archive. Open kept two features and eight visible cells.

Across the entire post-acquisition return branch, retain read an average
1.383 features per prediction versus open's 1.900, a **27.2% reduction in
prediction feature accesses**. However, all six features were still observed
and up to 192 raw records remained available to search. There is no demonstrated
sensing saving or reduction in total stored information.

Retain used up to 16 visible-plus-archived table cells. Archive storage and
candidate scoring are extra costs. For the return branch, retain performed
595 candidate fits and 62 archived-candidate scores, versus delete's 576 fits
and no archived scores; open used only the 240 shared-acquisition fits.
Thus neither memory, compute, nor used selection feedback is perfectly matched
across all controls.

The complete benchmark comprised:

* 90 runs; 155,520 allocated and 144,000 used outcome-bearing presentations.
* 25,920 generated records across 15 paired streams; repeated presentations
  are not independent environmental evidence.
* 4,196 candidate fits, 138 archived-candidate scores, and 1,280 main predictions
  made using frozen retrieved snapshots.
* 207,360 base evaluation predictions and 304,512 additional input-cut calls.

## Verification and interpretation

Eight targeted synthetic tests passed. An independent implementation replayed
all 90 traces: world generation, shared acquisition, candidate fitting and
ranking, selections, hidden/deleted memory, frozen deployments, predictions,
evaluations, metrics and costs. The manifests for Experiments 010 and 011 also
remained unchanged.

The supplied snapshot time coincides with the end of acquisition. The allowable
interface operations, feature language, rolling window, selection rules and
review schedule are constructed and fixed. The experiment does not learn when
to create durable memories, discover arbitrary interfaces, hide temporal
trajectories, form Markov folds, or optimize future learning across tasks.

The supported step is narrower and useful: **a learner can selectively stop
using detail without erasing its learned predictive content, then recover that
content when new evidence supports it.** Hiding and deleting are experimentally
different operations here. Whether this becomes a general mechanism for folds
or learning how to learn remains open.

The fixed experiment is complete. No additional benchmark or scaling run
follows automatically.

Full records: [report](report.md), [metrics](metrics.json), [traces](results.json),
[manifest](manifest.json). Verification:
`python3 -m unittest discover -s checks -p 'test_interfaces.py' -v`
and `python3 checks/audit_interfaces.py`.
