# Consolidation round: shared implementation, tested interactions, unresolved reliability

The bounded C0–C2 round concluded on 2026-10-23. **Execution and independent
verification are complete; reliable integration of every intended capability
was not established.** No failed criterion was relaxed, no benchmark was tuned
or repeated. At that round's close, no additional experimental stage had begun.

A separately specified follow-on completed on 2026-10-26:
[Experiment 019](consolidated-recovery-v1/findings.md) tests the unchanged
learner on fresh worlds with extended recovery. It strengthens the prediction
evidence while identifying later abstraction regressions and continuing
memory limitations; it does not change the C0–C2 results below.

The subsequent 019–022 test round is now separately
[closed with 320 audited runs](consolidated-learner-test-round-synthesis.md).
Its synthesis and the [current evidence map](evidence-map.md) record the later
protection, preservation and memory-selection evidence without revising the
historical C0–C2 conclusions below.

## What each stage established

| Stage | Result | Claim boundary |
| --- | --- | --- |
| [C0 / 016](consolidation-core-v1/findings.md) | Shared core exactly reproduced 380 saved 012–015 traces; 13 contract tests passed. | Engineering compatibility, not improved learning. |
| [C1 / 017](protection-interfaces-v1/findings.md) | All 120 runs audited. Protection reduced misleading-burst local errors from 12 to 2 checkpoints but exceeded the lasting-change loss and recovery-delay allowances. | Protection and interface revision coexist, with a measured adaptation cost. Primary criterion failed; the preselected reference passed the C2 gate. |
| [C2 / 018](structural-consolidation-v1/findings.md) | All 120 runs audited. Complete integrated trajectories: 0/10 forms, 3/10 detail, 3/10 reversed detail; memory added no prediction benefit. | Operators coexist in one continuing learner, but reliable structural simplification and useful retained memory remain unresolved. Primary criterion failed. |

## Capabilities in the actual combined learner

The implementation shares conditional-count prediction across forms and joint
relationships. It has restricted prediction interfaces, selected dependencies,
ordinary improvement and adequate reduction, a single immutable archive,
semantic compatibility checks, evidence identities and resumable state. These
are concrete components, rather than a collection of scripts selected for their
best separate results.

The empirical findings are narrower. In C2, all ten integrated seed pairs
learned local forms supporting transfer to unseen compositions. Four of ten
form-history runs collapsed and recreated a local distinction; four removed
and restored its dependency, but only two performed both and none completed
the required minimal trajectory. Detail-history prediction and the appropriate
final detailed interface recovered in all ten runs, but only three simplified
successfully in the intervening phase. Those same three cases were shared
across the paired detail and reversed histories.

Capture, compatibility checking and evidence-based archive selection executed,
but no archived predictor was accepted. Retained and deleted variants produced
identical prediction paths. C2 therefore does not reproduce the earlier 012
memory benefit when capture is driven by an accepted structural reduction.

## The central lesson

Prediction recovery, useful representation and useful retained memory are
different achievements. A parent can predict correctly by exposing raw detail
while a lower abstraction is wrong, redundant or no longer used. It can also
continue exposing detail after the lower abstraction has recovered. Output
accuracy alone does not establish that the learner has retained the distinctions
that matter and removed those that do not.

Likewise, freezing a table at an accepted reduction does not guarantee that it
still contains the earlier useful knowledge. C2's detail-history archives were
captured after their fitting windows consisted entirely of no-detail experience.
That provenance identifies capture timing and preservation during adaptation as
specific questions. It does not justify changing the rule retrospectively or
claiming that a different rule would necessarily succeed.

The current claim is a small, constructed framework that can learn and revise
generalisations within supplied languages, with inspectable evidence and
explicit failure cases. It is not a reliable general learning system, and the
necessity of its full dynamics remains unestablished.

## Resources and reproducibility

C1 and C2 used **833,280** new labelled presentations from an allocation of
**936,960**, with **30,456** candidate fits against the planned ceiling of
47,040. Synthetic fixtures charged **19,728 of 20,000** labels. C0's 894,080
saved-label compatibility presentations and subsequent independent audit
replays are recorded separately; they are not fresh learning evidence.

All completed benchmark traces, source hashes and independent audit records
are retained. C0 and earlier source files were preserved; C2 uses a separate
extension. The original plan remains frozen as a planning/provenance document;
this synthesis and the stage findings record completion status.

## What remains open

The next design discussion can focus on three concrete issues:

* preserving an informative predictor before adaptation removes its earlier
  distinctions, while avoiding oracle capture timing;
* attributing successful parent prediction to useful lower abstraction versus
  a raw bypass, and reliably returning to abstraction;
* distinguishing resistance to misleading evidence from delayed adaptation
  when change is real.

These are questions for a separately specified follow-on, not extra tests
within the completed budget. Interpretation and design-led modification can
be explored against the saved traces, but successful user interpretation or
steering has not been measured. Meta-learning still requires improvements in
subsequent learning on held-out task families against fixed-policy controls.
Learned depth, temporal folds and eigenform recovery remain outside the tested
system. Inspectability provides no automatic safety advantage or basis for
scaling or real-world deployment.
