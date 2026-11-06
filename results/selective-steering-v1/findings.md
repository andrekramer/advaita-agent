# 033 — Selective steering works locally; overall benefit remains conditional

Completed 2026-11-05. **The controls worked as specified, but the full usefulness
criteria failed.** Holding one category boundary fixed protected a correct
learned distinction through misleading evidence. Making the other local slow
memory more plastic improved that predictor in all 20 changing-condition pairs.
Those local benefits did not reliably improve the composite task; repeated
reversal performance worsened and some costs persisted after releasing controls.

All 180 runs passed independent reconstruction. The original learner remains the
default. This study adds an experimental subclass and explicit controls; it does
not promote the tested setting or establish generally beneficial steering.

[Protocol](../../experiments/selective_steering_protocol.md) ·
[Complete measurements](results.json) · [Independent audit](audit.json) ·
[Saved trajectories](runs.jsonl.gz) · [Worlds](worlds.json) ·
[Protected sources](manifest.json) · [API semantics](../../docs/selective-steering.md)

## The instruction and comparisons

After 512 observations, protect one local partition and shorten the other local
slow-memory half-life from 1024 to 128 ticks. Keep learning the probabilities in
both channels. Release both controls after 1024, without restoring old evidence.
The composite channel retains its existing learning rules throughout.

The protected/flexible channel mapping was supplied by the experimenter with
knowledge of the task design. The learner did not infer where intervention was
needed or choose a goal. Five fresh environments and two proposal seeds each
covered stable data, category remapping, and repeated polarity reversal. In the
two changing histories, the supposedly stable channel also received a 128-tick
misleading category remap; its latent truth stayed unchanged. Observed labels
and expected losses against clean latent truth were reported separately.

Six matched policies made 180 runs: original combined memory, refreshed snapshots
only, lock only, plasticity only, both controls, and controls on swapped channels.
Both channel positions occurred in each role. The proposal replicates and related
histories are correlated; they do not constitute 180 independent environments.
The task vocabulary, two local channels, composite wiring and control schedule
remain supplied. This is a limited demonstration of obeying a known instruction.

## The consistency prerequisite passed

The new subclass refits fitted models at the end of each review. This is separate
from steering. Across all 30 original-versus-refresh-only pairs, pre-update
probabilities were exactly identical, and every ordinary review decision matched.
Independent state replay verified the declared extra refit costs and coherent
post-review models. The five saved 032 anomalies also disappeared once pure
refresh was separated from subsequent local weakening, using no new labels.

This fixes the snapshot boundary in the experimental subclass. It does not change
within-review comparisons or silently repair the old frozen runtime. Mid-run
restore, control histories, lock invariants, selective decay and release all
passed replay. Inspection returns a detached copy. A locked partition continues
to accumulate evidence and update probabilities; it is not a frozen predictor.

## Local benefits

The protected distinction was correct at all 40 burst review checks under the
combined controls, versus 2/40 without controls (100% versus 5%). All anchors were
correct at the time of locking in this cohort. Protection preserves what is
locked; it does not certify it as correct or provide a reason to lock it.

Increasing plasticity, with protection held constant, reduced active-window
expected flexible-local loss by **.076595 nats on average**, positive in 20/20
pairs and every environment mean. Category-remapping benefit was .068919 nats;
polarity-reversal benefit was .084272. Both fixed plasticity gates passed.

| Changing history | Refreshed: protected loss | Selective: protected loss | Lock only: flexible loss | Selective: flexible loss |
| --- | ---: | ---: | ---: | ---: |
| Category remapping | .447459 | .358893 | .551395 | .482477 |
| Polarity reversal | .447459 | .358893 | .654360 | .570088 |

These are expected local losses over 513–1024, including the misleading burst.
In stable data, faster slow-memory decay slightly increased the flexible local
loss (.328164 to .329736). More plastic is not intrinsically better.

## Composite outcomes and the failed criteria

| Criterion | Outcome |
| --- | --- |
| State/control correctness and refresh-only parity | Passed |
| Protect the intended distinction | Passed: 100% burst correctness in both changing histories |
| Flexible-local gain and consistency | Passed: .076595 nats, 20/20 positive |
| Composite gain over refreshed baseline | Failed:mean gain **−.013170 nats**, requiring +.005 |
| Composite consistency | Failed: 10/20 positive, 6 worse, 4 ties; required 12 positive |
| Preservation after release | Failed:individual local costs and repeated-history mean composite cost exceeded limits |
| Final full validity | Failed: stable 10/10, remapping 10/10, repeated 6/10; required 8/10 each |

Full validity requires correct local partitions, all modal composite predictions
correct, and expected regret<=.10. The primary empirical conjunction remains
failed. Audit passing confirms the measurements; it does not turn these failed
performance criteria into success.

| History / policy | Active composite loss | Return composite loss | Later composite loss | Final full validity |
| --- | ---: | ---: | ---: | ---: |
| Stable, refreshed | .334181 | .336130 | .335919 | 10/10 |
| Stable, selective | .334181 | .339318 | .336536 | 10/10 |
| Remapping, refreshed | .604480 | .485963 | .505519 | 9/10 |
| Remapping, lock only | .602782 | .479493 | .506821 | 9/10 |
| Remapping, plasticity only | .589457 | .493840 | .504496 | 10/10 |
| Remapping, selective | .585140 | .489408 | .504770 | 10/10 |
| Remapping, swapped | .634485 | .454817 | .517325 | 9/10 |
| Reversal, refreshed | .788693 | .530739 | .657515 | 9/10 |
| Reversal, lock only | .821523 | .486688 | .702335 | 6/10 |
| Reversal, plasticity only | .801589 | .515095 | .669341 | 8/10 |
| Reversal, selective | .834374 | .481928 | .710585 | 6/10 |
| Reversal, swapped | .816379 | .538306 | .646542 | 9/10 |

Category remapping improved under selective control, but reversal worsened enough
to outweigh it. All local partitions were correct at the final reversal endpoint
under both refreshed and selective conditions, yet full composite validity fell
from 9/10 to 6/10. Correct local distinctions are insufficient to ensure that the
composite predictor has adapted appropriately.

The selective repeated-history later composite cost was .053070 nats on average,
with a worst individual cost of .169349. Other failed guards concerned local
outputs; [descriptive results](descriptive.json) list every violation. Returning
composite loss improved on average in the repeated history, but this did not
prevent worse performance on the next reversal. Restoring control settings does
not undo changes to evidence, proposals or learning history.

## Misdirection and release

Swapping the instruction in the category-remapping task locked the distinction
that actually needed to change. Its active-window form correctness was 0%, and
full validity at 1024 was 0/10, versus 10/10 under selective control. Its local
expected loss was .788706, versus .482477 under selective control. By 1536, after
release and return of the original task, flexible-form correctness was 10/10 and
full validity 9/10. This demonstrates a cost of an inappropriate instruction and
recovery under the subsequent data; release alone is not established as its cause.

Polarity reversal changes outcome orientation without changing the correct
partition. A lock on that channel is therefore not intrinsically misdirected at
the representation level. The swapped policy is not a universal negative control
and sometimes outperformed the supposedly appropriate policy downstream.

Skipping structural proposals while locked also changes the later proposal
sequence. The observed post-release effects combine altered evidence and search
history; this experiment does not identify their separate contributions.

## What this supports

We can deliberately preserve a local distinction while allowing its predictions
to learn, independently change another channel's memory plasticity, inspect those
settings, and release them. In this constructed task those controls produced
useful local protection and adaptation. This is stronger than merely exposing
control knobs, but narrower than reliable steering of the learner as a whole.

The main unresolved issue is coordination: changes that help local representations
can leave composite learning worse. The ablations show costs from protection as
well as plasticity; they do not establish one universal remedy. A later study
could ask which downstream mechanisms must adapt with a protected or more plastic
local form. No such follow-up, additional tuning or automatic policy selection
was run here. No learned goals, meta-learning, arbitrary core locking, human/LLM
usability or safety advantage is claimed.

## Validation and resources

Five pre-outcome fixture tests passed on the first attempt. They reconstructed
all six policies on transformed reused 7990 data (1344 label presentations),
verified control semantics, checkpoint continuation and passing/failing metrics,
and replayed the five saved 032 refresh anomalies. No new random fixture labels.

Fresh outcomes used 153600 generated scalar labels and 1843200 presentations,
184348 candidate fits,6344800 scoring queries and 32296376 fit-related raw-bin
visits. The new selective decay adds 184320 cell visits, reported separately from
the inherited fit counter. All caps passed. Runner 109.28s; independent audit 91.33s.
All 1485 protected files remained unchanged. No reserved outcome was rerun or tuned.

Reconstruct the saved audit and descriptive tables:

```sh
python3 checks/audit_selective_steering.py
python3 experiments/report_selective_steering.py
```

The benchmark refuses to overwrite its results. The experiment is complete;
failed criteria remain failed, and no new default is selected.
