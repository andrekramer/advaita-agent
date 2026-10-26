# Closing the consolidated-learner test round: 019–022

Closed 2026-10-26. **All 320 runs are complete and independently audited.**
This closes the follow-on tests of the consolidated learner. The original
C0–C2 consolidation round, 016–018, remains separately closed, with its
[original findings](consolidation-round-synthesis.md) unchanged.

The round established useful mechanisms and specific failure modes. It did
not establish a consistently superior combined policy. No failed criterion
was relaxed, no benchmark was tuned or repeated, and closure requires no
additional experiment. The [current evidence map](evidence-map.md) separates
demonstrated capabilities from unresolved reliability and supplied assumptions.

## What the four experiments add

| Experiment | Main evidence | Limit at closure |
| --- | --- | --- |
| [019: extended recovery](consolidated-recovery-v1/findings.md), 120 runs | The unchanged integrated learner maintained valid late predictions in 10/10 pairs per history. | Stable structure passed in 6/10 form-return and 9/10 in each detail history. Representation and memory-benefit criteria failed; extra experience did not prevent all later regressions. |
| [020: established-form protection](consolidated-protection-v1/findings.md), 60 runs | Corroboration reduced affected-form error checkpoints from 9 to 1 under ordinary noise and from 23 to 4 during misleading bursts. | Genuine-change recovery was 89.6 records slower on average, and composite-loss costs exceeded their allowances. The combined criterion failed. |
| [021: prospective preservation](prospective-memory-v1/findings.md), 60 runs | Early snapshots were preserved in 7/10 pairs per history; mean early-return loss improved by .028616 nats against both controls. | Only 3/10 pairs improved, requiring eight. Archive availability could block fresh adaptation without retrieval, so benefit could not be attributed solely to recall. |
| [022: competition versus reinstatement](memory-selection-v1/findings.md), 80 runs | Independent admission of memory and the best fresh candidate improved mean early-return loss by .045996 nats versus ignoring memory. All four improving pairs had early preserved snapshots. | Only 4/10 pairs improved, requiring eight. Reversal cost met the mean allowance but included a .131837-nat individual setback. The combined criterion failed. |

Each experiment used five environment realizations with two proposal draws.
Paired histories share initial evidence, and the studies use the same small
supplied task families. The 320 runs are not 320 independent tasks. Results
across fresh seed sets are not a controlled ranking of all policy revisions.

## The connected finding

Prediction recovery, representation recovery and useful memory are distinct
achievements. A parent can regain correct output by exposing raw detail while
a lower form remains wrong or an unnecessary interface remains open. Protecting
that form can resist misleading evidence, but also delay genuine revision.

Memory adds another distinction: preserving a predictor and making it useful
later are separate operations. Capturing only when detail is hidden can occur
after earlier knowledge has been overwritten. Prospective preservation partly
addresses this, but an archive also changes candidate competition. Experiment
022 provides clearer evidence for beneficial reinstatement: separate admission
matched the memory-ignoring control until retrieval, and the policies retained
identical snapshots within each seed pair. Competition without retrieval gave
no early-return benefit on those worlds.

The benefit includes restoring an interface choice. Raw predictors still refit
after each main observation, so durable reuse of archived parameters has not
been isolated. A fresh selection gate can also accept an unhelpful intermediate
snapshot. The result supports useful memory access in some cases, with capture
quality and recall reliability unresolved.

## Baseline and claim at closure

The reference remains the original
[`StructuralLearner` in integrated mode](../advaita/structural.py), tested
unchanged in 019: immediate local replacement, evidence-tested reductions and
interface revision, with capture at reduction and compatible archive selection.
It remains a reproducible reference despite its documented failures.

The [corroboration](../advaita/corroboration.py),
[prospective-memory](../advaita/prospective_memory.py) and
[memory-selection](../advaita/memory_selection.py) extensions remain separately
identified experimental alternatives. None is promoted to a new default.
Their strongest results are not combined into a claim about an untested learner.

The supported claim is **a small constructed framework that can learn and revise
generalisations within supplied representation languages, with inspectable
evidence and explicit failure cases**. Reliable beneficial memory, reliable
structural recovery and superiority or necessity of the full dynamics remain
unestablished. Inspectable records prepare for interpretation and intervention;
they do not establish effective user interpretation, steering or safer behavior.

## Boundary for the next enquiry

Carry forward three mechanism questions: capture quality and timing; the
relative contributions of restored interfaces and fitted parameters; and
coordination between provisional local changes and upper interfaces. Resolving
these is not a requirement for closing this round.

Interpretability and controlled modification are a possible next bounded
enquiry: can a reader predict a change's consequences from the saved evidence,
then make a useful limited intervention? Meta-learning requires a separate
evaluation of improved subsequent learning on held-out task families. Learned
depth, temporal folds, autonomous exploration and scaling remain outside this
round. No next experiment is scheduled by this closure.

## Record and verification

The four studies used **1,998,080** learning-label presentations from an
allocation of **2,170,880**. Fixtures charged **4,625** new-learning/fixture
labels in total; 019's fixture checks used saved evidence and added none.
Independent audit replay is separate from fresh learning evidence.

Each linked findings report preserves its protocol, results, full traces,
checkpoints, source hashes, audit and completion record. This closure adds
documentation only. Historical protocols and benchmark artifacts remain frozen;
the README, roadmap and current evidence map provide the updated status.
