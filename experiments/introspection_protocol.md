# 032 — Can inspection predict the consequences of memory control?

2026-11-03. Follow-up to the failed full steering gate in 031. Freeze this
protocol, controller, runner, metrics, independent auditor and passing fixtures
before generating reserved seeds 2100–2104 (proposal seeds 2100/2101).
No learning engine, threshold, interface or default is changed.

## Design

Use the frozen 030 generator/acquisition and the optional combined memory engine:
stable, repeated polarity reversal and changing forms; 2048 ticks; reviews every
64. Five independent environments, two proposal replicates, three histories =
30 trunks. At the first completed review at or before 1024 with a qualifying but
not automatically accepted weakening candidate, stop the trunk. If none, stop
at 1024. Eligibility and ranking are exactly those used in 031.

Before looking at ANY counterfactual outcome, serialize an inspection packet and
all decisions/forecasts. Fork the identical checkpoint into four continuations:
no intervention, weaken local0, weaken local1, weaken composite2. Each action
halves slow evidence once with the existing API; all branches receive identical
future main and selection rows through 2048. Forced actions are diagnostic
counterfactuals, not actions chosen by the controllers. Include no-trigger cases.

The intended output is explicitly composite channel2. Three scripted policies:
* disagreement: highest eligible slow-minus-fast loss gap, tie lower channel;
* dependency-aware: choose channel2 if eligible, otherwise abstain;
* rotated: rotate the disagreement choice by one; abstain if no candidate.
No-op is also a control. All policies decide at the SAME checkpoint. The aware
controller does not wait for a later opportunity. This isolates a limited value
of knowing the interface, not an optimal intervention planner.

## Observation versus inference

The read-only adapter exposes the runtime's copied inspection state plus current
structural and weakening pending decisions from its checkpoint. It exposes no
raw fast/slow tables, RNG, world identity, phase/change marker, simulator truth,
future examples or counterfactual results. Current review losses were computed
before final migration and are marked historical diagnostics, not exact current
counterfactual estimates. Controller receives only a JSON copy of this packet.

A separate inference records each upper port as absent, group membership or raw
state. The upper predictor does not consume local confidence. With unchanged
partitions, refitting after a local weakening only possibly renames group IDs;
it does not change the immediate composite probabilities. This invariant also
holds for absent/raw ports. It does NOT guarantee no effect on later structural
learning: weakening also clears pending decisions. Faithfulness checks compare
all observed fields and dependencies to independent reconstructed state, verify
copy isolation/read-only behavior, and audit exact control state changes.

For each eligible channel, record an immediate composite forecast: no change for
local0/1, change for upper2. Record a FUTURE loss-direction hypothesis over the
next256 observations: local weakening has no composite effect; upper weakening
improves composite prediction. The disagreement-only forecast is improvement for
all eligible channels. Both predict an improvement in the selected channel's own
loss. Ineligible actions are explicitly uncertain, with coverage reported. These
are falsifiable scripted hypotheses, not claims of the learner's self-awareness.
For future classification, gain>.005 nats means improvement, gain<-.005 harm,
otherwise no meaningful effect. Immediate probability tolerance is 1e-12.

## Outcomes and frozen criteria

Primary utility window: next256 ticks after the decision, identical for all
branches of a trunk. This may cross a world transition; do not realign or drop it.
Also report post-decision through2048, fixed return1025–1536 and later1537–2048,
observed losses for ALL three outputs, expected composite loss (simulator truth
used only by evaluator), and final full validity (correct local partitions,
all modal composite predictions correct, expected regret<=.10).

Report three separate gates and a conjunction, retaining failures:
1. Mechanical faithfulness: all packets, state changes, checkpoints, forecasts'
   derivation and immediate eligible-action effect predictions verified.
2. Forecast usefulness: at least8 eligible actions across at least3 independent
   environments in the two changing histories; >=80% future direction accuracy;
   >=20 percentage-point improvement over the disagreement-only forecast on
   those SAME eligible actions. Report counts by channel/history, abstentions,
   coverage, own-channel accuracy, and environment means.
3. Steering utility: aware mean future observed composite gain over disagreement
   >=.005 nats, positive in>=12/20 changing-history paired runs; mean gain over
   no-op>=0. Preservation against no-op: separately for each history and each
   return/later window, all three observed-output mean costs<=.02, each individual
   cost<=.10, and expected composite mean cost<=.02. Aware final full validity
   >=8/10 in EACH history. No-trigger runs stay in denominators.

Observed means do not establish universal benefit. Two proposal replicates are
not independent environments. Compare rotated as well, report same-input causal
contrasts and persistent/collateral effects. No human/LLM usability, new goals,
learned controller, meta-learning or safety advantage is tested.

## Validation, resources and closure

Fixtures reuse the already used 031 small fixture world (7990); no fresh labels.
Synthetic fixtures cover eligible/ineligible decisions, port modes, detached
inspection, no-op and all three interventions, stale-control rejection, forecast
classification, and both passing/failing summary gates. Reserve at most8 fixture
attempts; account for replay presentations. Independent audit imports no new
controller/runtime/runner/metrics. Reuse the frozen independent arithmetic and
world reconstruction, replay every prediction/review and exact final state.

Maximum30 trunks and120 continuations. 153600 generated scalar labels. Actual
label presentations are acquisition+prefix once per trunk plus four future
suffixes, <=1228800. At most200000 candidate fits,15m scoring queries,60m raw-bin
visits,50000 oracle contexts. Count immediate96-probability grids separately.
Runner and auditor each <=900s. Save partial artifacts on failure. Freeze a
recursive manifest of 031 and its ancestors plus all new source/fixtures before
outcomes. Report all results even if gates fail; no tuning, resampling or new
architecture promotion. New follow-up requires a separately declared study.
