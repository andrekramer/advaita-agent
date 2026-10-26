# Experiment 022: archive competition versus reinstatement

Specified 2026-10-26 before reserved-world generation. This follows 021's
finding that an archive can block a fresh candidate without being retrieved.
Preserve all earlier sources, protocols and results; no protected-local rule
from 020 is included.

## Four policies and the intervention

Every policy uses 021's prospective qualification and permanent one-slot
preservation: freeze an active detailed predictor, require loss <=.55 on two
consecutive fresh batches, then install it after the confirming review. No
regime marker or oracle information reaches learning. Local learning, candidate
proposals, compatibility, reduction and online refitting remain unchanged.

Every review ranks the same supplied fitted candidate set on the recent main
buffer. It identifies the best non-reducing fitted candidate and, if compatible
and non-reducing, the archive. Every policy scores the incumbent and both
available challengers on the fresh selection batch. Scores unused by a policy
are recorded diagnostics; they cannot change that policy's decision.

| Policy | Choice and acceptance |
| --- | --- |
| shadow | Ignore archive for decisions; test the best fitted candidate. Retain and score the archive only for matched bookkeeping. |
| veto | Rank fitted candidates and archive together as in 021. If archive wins, suppress ordinary replacement even if its fresh loss would pass. No fallback to the fitted candidate. |
| joint | The original 021 reserve behavior: test only the joint ranking winner, with no fallback. Additional recorded scores cannot change decisions. |
| separate | Independently admit the best fitted candidate and the eligible archive if each passes the existing fresh gate. Choose the lower fresh-loss admitted candidate; exact ties favor the fit. |

The unchanged fresh gate requires incumbent loss >.55 and improvement >.02.
If no ordinary replacement is accepted, run the original reduction process,
including in veto. An archive cannot cause an ordinary replacement in shadow
or veto. Subsequent raw refitting remains unchanged; reinstated parameters
may therefore be short-lived. All four retain a snapshot: shadow is a control
for use of stored information, not a memory-storage-cost control.

Separate tests at most two challengers on one batch. This is an explicit
increase in selection opportunities, not an extra independent confirmation.
Actual online loss, computed before updating from each new target, measures
whether this generalizes. All scores count against resource bounds.

Prespecified contrasts (control loss minus treatment loss): veto minus shadow
isolates competition without reinstatement; joint minus veto adds reinstatement
under joint competition; separate minus shadow tests memory access without
joint-ranking exclusion; separate minus joint tests independent admission.
These are policy interventions. Once trajectories diverge, later captures and
proposals can differ; they are not additive decompositions of individual gains.

## Worlds, outcomes and stopping

Use the unchanged 018 generator, environment seeds1100–1104, proposal seeds1100
and1101, histories detail and reversed. Same acquisition and 1280-record
schedule as 021: detail matters1–240, disappears241–528 and returns529–1280;
reversed complements the detailed target on return. Local forms remain fixed,
noise is10%, reviews every64 use32 fresh joint contexts. Five environments
with two proposal draws give ten pairs per history, not ten independent worlds.
The histories share evidence through528. Total80 runs; acquisition failures
remain in denominators.

Primary criterion: separate reduces mean observed detail early-return loss
(records529–656) by >=.02 nats versus shadow and strictly improves >=8/10 pairs.
Require mean observed early-return cost versus joint <=.02 in both histories,
and versus shadow <=.02 in reversed. Require separate's mean pre-return cost
(records1–528), observed and latent, <=.02 versus both shadow and joint in each
history. Require final full validity >=8/10 for every policy in both histories.
Primary pass is the conjunction. No failure triggers tuning or additional seeds.

Report all four contrasts, environment aggregates, all runs, observed/latent
losses over pre1–528, early529–656, returned529–1280 and late1025–1280, raw reads,
qualification/capture provenance, incompatibilities and retrieval times.
Report joint-ranking archive winners with a passing fitted alternative that
was not deployed (`fit_blocked_reviews`); this descriptive count also includes
separate choosing an even better archive, so it is not itself a harmful veto.
Report transfer, final and stable late full validity and appropriate structure
at reviews1024,1088,1152,1216,1280. Reuse 021's exact definitions: full validity
requires both exact local partitions, all32 modal outputs correct and latent
loss regret <=.10. Appropriate structure additionally requires sufficient,
minimal interfaces matching the known simulated task. Oracle diagnostics do
not enter learning. No general memory, meta-learning or safety claim follows.

## Resources and verification

Exactly80 runs ×6784 used/allocated labels =542720 presentations;67840 generated
labels across10 worlds. Ceilings:26560 candidate fits,4200000 scoring queries,
102400 main composite predictions,204800 local predictions,60800 evaluation
predictions,307200 oracle context queries. Maximum buffer192; one pending
prospective model and one archive of at most16 cells each. Existing local and
upper pending bounds remain. No additional learner-level retention buffer.
Benchmark and independent audit each limited to600 seconds.

Synthetic fixtures use seed2992 or explicit constructed records, capped at3500
charged labels across attempts. Preserve each attempt. Before reserved-world
generation, require passing tests of policy separation, blocked/accepted archive
cases, compatibility exclusion, checkpoint continuation, shadow equivalence to
021 discard, joint equivalence to021 reserve, independent replay and metric
boundaries. Freeze fixture, runtime, driver, metrics, auditor, reference and
prior-artifact hashes. Persist all worlds, traces and full schema22 checkpoints.
Independent replay imports no experiment or runtime policy code. Report any
engineering/resource failure as incomplete; do not silently replace a run.
