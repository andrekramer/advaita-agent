# Experiment 026: slow memory retains knowledge, but struggles to revise it

Completed 2026-10-30. **350 runs passed independent reconstruction.** Selective transfer into slow memory improved retention through a quiet interval and improved early adaptation compared with unconditional transfer. The full primary criterion nevertheless failed: outdated slow evidence caused costly adaptation and incomplete recovery after reversal. The original integrated learner remains the reference.

## What was tested

The question was whether recent learning can migrate into longer-lived memory, whether that memory should also decay, and whether forgetting should follow elapsed time or new observations. This returns to the earlier fast/slow consolidation idea while allowing the current finite forms and interfaces to be revised.

The new family holds fast and slow weighted evidence over four raw states for each local channel and 32 raw joint input/action contexts above. Predictions use the current learned partitions and selected interface. Main outcomes enter only fast evidence. An accepted transfer moves a fraction of fast evidence into slow evidence, conserving the total immediately; its influence then survives longer. Selection observations are never fitted as evidence.

Fast and slow half-lives are 64 and 1024 ticks. Every 64 labelled ticks, a quarter of the fast evidence is proposed for transfer, subject to slow capacity. Each channel uses fresh outcomes to compare its slow predictor before and after transfer. Selective transfer requires an improvement greater than .005 nats and candidate loss at most .55. These rules are supplied, not learned.

| Policy | Memory behavior |
| --- | --- |
| baseline | Original integrated learner: recent-data windows and frozen archive. |
| fast | One rapidly decaying evidence store; no transfers. |
| slow | One slowly decaying store; no transfers. |
| always | Two timescales, with unconditional transfer. |
| selective | Two timescales, with the external transfer gate. |
| permanent | Selective transfer, with no decay of slow evidence. |
| activity | Selective transfer; both stores freeze during blank ticks. |

All new-family policies use the same prediction and structural machinery. The original reference is an anchor, not a matched single-change control: the new family also uses weighted sufficient statistics, continuous refitting, weighted candidate ranking and no archive retrieval. Comparisons within that family isolate the memory choices more closely.

Five fresh environments and two proposal draws per environment give ten paired trajectories per history. Histories are stable, a brief 64-tick outcome reversal, familiar knowledge returning after a 512-tick blank interval, reversed outcomes after that gap, and a changed local partition after the gap. No input or target is supplied during blank ticks. Actions are scheduled. These are five environmental realizations, not ten independent worlds or new task families.

## Retention improved; the simpler controls matter

Selective memory reduced early-return observed loss against fast-only by **.070879 nats**, with **10/10** pairs improving. End-of-gap expected loss fell from **.677726 to .351462**; full validity rose from **0/10 to 10/10**. This demonstrates a retention benefit after fast evidence fades.

The original learner and the single slow store also retained the task. Selective memory did not beat them on familiar return: early loss was .333392, compared with .327224 for the reference and .319678 for the single slow store. The result does not establish that two stores are necessary for retention.

| Policy | Gap-end expected loss | Familiar early return loss | Reversal early loss | Reversal final full validity | Remap final full validity |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 0.338286 | 0.327224 | 1.350267 | 9/10 | 9/10 |
| fast | 0.677726 | 0.404271 | 0.409153 | 10/10 | 10/10 |
| slow | 0.331891 | 0.319678 | 1.237573 | 0/10 | 6/10 |
| always | 0.346603 | 0.330466 | 0.926070 | 0/10 | 10/10 |
| selective | 0.351462 | 0.333392 | 0.879046 | 0/10 | 10/10 |
| permanent | 0.339936 | 0.326843 | 1.004854 | 0/10 | 2/10 |
| activity | 0.333525 | 0.324651 | 1.081283 | 0/10 | 7/10 |

Early return covers ticks 769–896; final validity is at 1280. Full validity requires correct local partitions, every modal composite prediction correct and expected-loss regret at most .10. Lower loss is better. All unsuccessful trajectories remain in the denominators.

## Selection helps admission, but does not solve revision

Against unconditional transfer, selective transfer improved the declared average across burst recovery, reversal and remapping by **.023749 nats**, with **9/10** paired gains. Its specified mean-cost, individual-cost and recovery guards against that control all passed. This is evidence for useful selection within this memory mechanism.

Against fast-only, however, selective memory incurred .227420 nats of mean cost during the temporary outcome reversal, .469892 during early reversal and .078100 during early remapping. One reversal pair cost .510904 nats. Recovery guards failed, and **none of the ten selective reversal runs reached full validity by the horizon**. The early reversal loss was better than the original reference, but the reference recovered much more completely later. An early improvement is not sufficient evidence of successful revision.

Selective memory also improved mean early revision loss versus the single slow store by .254228 nats in 10/10 pairs. The separate dual-store criterion still failed: post-burst recovery was worse by .035511 nats on average, with a .141381 individual cost. The richer learner did not pass all its comparison requirements.

## The recorded decisions expose a specific obstruction

After reversal, all **80/80 upper-channel proposals** improved slow-predictor loss by more than .005, yet all were rejected because the proposed predictor remained above the .55 adequacy threshold. For environment 1600/proposal 1600 at tick 832, proposed transfer reduced fresh slow loss from 1.383 to 1.125. It was an improvement, but not yet adequate under the fixed rule. At 1280, that comparison was still 1.272 versus .868, and still rejected.

The gate can therefore block incremental correction of an already-wrong slow store. Admission control and revision of retained evidence are distinct problems. The current policy admits useful-looking new evidence but supplies no targeted mechanism for weakening contradicted old evidence; its main removal mechanism is elapsed-time decay.

This diagnosis is descriptive, based on audited decisions. It does not prove that removing the adequacy condition would improve the full trajectory: accepting those proposals would change later states and decisions. That requires a fresh, predeclared comparison. No threshold was adjusted after these results.

The failure is also more specific than losing every learned form. All ten selective reversal runs ended with correct local partitions; 6/10 predicted every modal target correctly. None met the full accuracy-and-loss requirement, and mean expected regret was 0.191789. Retained evidence was still distorting the predictive estimates.

## Forgetting clocks and permanent memory

Freezing memory during the gap improved familiar early return (.324651 for activity versus .333392 for selective), but worsened early reversal (1.081283 versus .879046). Eliminating slow decay gave .326843 on familiar return and 1.004854 on reversal; only 2/10 permanent-memory runs reached final validity after remapping, versus 10/10 selective runs.

These comparisons show a task-dependent trade-off. A quiet interval supplies no evidence that the world changed, but preserving stronger old evidence can become costly if it did. Neither elapsed-time forgetting nor preservation during silence is uniformly preferable here.

## Prespecified outcomes

| Primary check | Result |
| --- | --- |
| return mean gain | Pass |
| return pairs | Pass |
| gap gain | Pass |
| gap validity | Pass |
| final validity | Fail |
| mean cost | Fail |
| worst pair | Fail |
| recovery | Fail |
| selection mean gain | Pass |
| selection pairs | Pass |
| selection mean cost | Pass |
| selection worst pair | Pass |
| selection recovery | Pass |

The overall primary gate and the separate dual-store gate both failed. Component benefits remain reportable; they do not promote a new baseline.

## Scope, cost and reproducibility

This is **evidence memory supporting learned forms**, not a second autonomous form learner or an archive of enduring named forms. Raw sufficient statistics remain available even when prediction uses a coarse interface. The experiment therefore does not show that abstract forms alone preserve everything needed for later revision. It also does not measure human/AI interpretation quality, steering, learned memory rules, general agency or a safety advantage.

The completed comparison used **1,890,560 label presentations**, 110,093 candidate fits, 5,296,256 scoring queries and 28,374,688 raw-bin fit visits. It completed in 91.5s; independent replay took 78.2s, each within 900s. The audit reconstructs worlds, every decision, evidence transfer, decay, checkpoints, measurements and gates without importing the new policy or experiment code. All frozen prior hashes are intact.

There was one engineering restart. The original sampler could not repeat a generator of representative contexts beyond its first block; the independent verifier had the same issue. The first attempt was stopped before any complete world, fitted learner or benchmark outcome. Its source manifest and incomplete record remain in memory-control-v1. Corrected `_v2` entry points materialize the context list, and expanded fixtures exercise two blocks. Cumulative fixture charge was **4,888/5,000**. The discarded attempt generated 768 acquisition labels internally; total generation across attempts was 135,808, with no additional learner presentations. No policy, threshold, seed or empirical gate changed.

To audit the saved results: `python3 checks/audit_memory_control_v2.py`. The benchmark entry point is `python3 experiments/memory_control_v2.py`; it refuses to overwrite its output. Replaying the fixture suite again would exceed the original cumulative budget and is deliberately blocked.

## What this changes in the enquiry

The memory question was useful: selective migration can retain knowledge and filter transfers, while the recorded evidence makes a revision failure identifiable. The next memory-control question is how to weaken, retire or replace retained evidence when current outcomes contradict it, while preserving rare but still useful knowledge. An interpretation-guided proposal could identify the affected relations and their supporting evidence; later outcomes must establish whether the intervention helped.

That follow-up needs fresh worlds and matched controls. It has not been run here. The current learner remains the reference, and the completed memory family remains an experimental alternative.

[Protocol](../../experiments/memory_control_protocol.md) · [Engineering restart](../../experiments/memory_control_restart.md) · [Results and paired measurements](results.json) · [Audit](audit.json) · [Diagnostic decisions](diagnostics.json)
