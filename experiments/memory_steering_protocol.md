# 031 — One evidence-led memory intervention

2026-11-02, after the 030 audit. 030 improved some predictions/retention but
failed its full lifecycle gate. This stage tests the already integrated control
API, without tuning the learner or claiming the broader failure is resolved.
Freeze before fresh seeds2000–2004, proposals2000/2001: stable/repeated histories,
three control policies, ten pairs =60 runs. Use the exact030 generator, acquisition
and2048-tick horizon; stable keeps original truth, repeated alternates polarity
every512 ticks. Five independent environments, two proposal replicates each.

Every run uses the frozen combined memory engine through ContinuingLearner.
After each completed review up to tick1024, examine its observed weakening
records. Eligible: `qualifies` true and automatic `accepted` false. Pick the
largest slow-minus-fast loss gap, ties favor smaller channel index. Select only
the first eligible review, regardless of its time; no latent truth or change
marker enters selection. At most one external action in the entire run.

* unsteered: record the proposed trigger, take no action.
* targeted: halve slow evidence for the selected channel once.
* rotated: halve slow evidence for (selected channel+1) modulo3 instead.

All three are identical until that trigger. The intervention uses the029 API,
clears the affected channel's pending decisions, refits, and logs rationale,
review identity, removed mass and before/after hashes. No new labels are added.
All conditions receive identical observations and selection batches. Shared
review evidence supports the diagnosis; future observations evaluate utility.
Rotated is a specificity control, not guaranteed to be an irrelevant channel.
No-trigger runs remain in every denominator. This is a scripted external
controller, not a test of a human or LLM's ability to interpret and steer.

Primary benefit window577–1024 is fixed, covering all outcomes after the first
possible review of the changed phase. Do not align it to actual trigger time.
Report whole1–2048, early513–576, returning1025–1536 and later1537–2048 too.
Measure observed and expected composite loss, the observed loss of the local
channel whose truth never changes, final full validity, triggers and controls.
Full validity remains correct local partitions, all modal composite predictions
correct and expected regret<=.10; grid every64 ticks plus transfer24.

ALL primary conditions required:
1. Targeted mean observed benefit over unsteered >=.01 in repeated history,
   strictly positive in>=8/10 paired runs.
2. Same benefit threshold and consistency over rotated, testing specificity.
3. Targeted final full validity>=8/10 in EACH history.
4. Against unsteered, mean observed/expected cost<=.02 on stable whole and repeated
   early/returning/later windows; every observed pair cost<=.10.
5. Against unsteered, unchanged local channel mean whole loss cost<=.02 separately
   in each history and every individual cost<=.10.

Report environment means and all controls, including harmful or absent actions.
No default promotion, extra seeds or tuning. Failing the gate completes this
bounded study. Protection/freeze controls and user interpretation are not tested.

Fixtures use seed7990: at most1000 new label presentations across saved attempts,
plus synthetic state arithmetic. Verify replay, intervention state/hash accounting,
metrics and gate failures before freeze. Independent audit imports no runtime or
experiment policy. Budget:102400 generated labels;614400 presentations;60 runs;
150000 candidate fits;10m loss queries;40m raw-bin visits;330000 oracle contexts.
368640 main predictions;62880 grid/transfer predictions;1440 auxiliary acquisition
predictions. No slow probes. Each benchmark/audit<=900s; save partial failures.
