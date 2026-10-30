# 028 — Fresh confirmation of selective memory revision

Specified before generating reserved outcomes. Follow-up to experiment 027,
authorized after its timing limitation and secondary benefits were reported.
This is a new confirmation, not a replacement or repair of the saved 027 result.
The original reference architecture remains unchanged.

## What changes, and what stays fixed

Use the exact frozen 027 RevisionLearner, original baseline, world generator,
seven policies, acquisition, 1280-tick horizon, noise, evidence capacities,
half-lives, two-review weakening rule, migration rules and structural operators.
No parameter, representation language or learning policy changes. Reuse the
independent reference implementation and verify all traces again.

The primary benefit window is now **897–1280 inclusive**, all 384 predictions
after the earliest possible two-review intervention at tick 896. Every paired
run uses this fixed clock window, even if it weakens later or never weakens.
Do not align windows to observed acceptance times or select favorable segments.
Keep the first 128 return observations (769–896) as an adaptation-cost guard.
Keep the previous late window (1153–1280) as secondary, not the primary.

Fresh environment seeds 1800–1804 and proposal seeds 1800/1801. Five histories
times ten paired runs times seven policies = 350 runs. Five environments with
two proposal replicates are not ten independent environment samples. No
exclusion of acquisition or structural failures. Report environment averages.
Original histories: stable; brief true reversal at 257–320; a blank interval
257–768 followed by familiar return, permanent reversal or partition remap.
The learner receives only present observations and elapsed ticks, no truth,
future data or change markers. The same labels are supplied to paired policies.

## Primary hypothesis and gates

Candidate `combined` = relaxed admission plus selective weakening. Control
`relaxed` = the same admission without weakening. A boost here means improved
prediction after an opportunity to act, while retaining useful knowledge; it
does not mean faster learning than every simpler control.

All conditions must pass:

1. Mean observed log-loss gain over relaxed admission in 897–1280, equally
   weighting reversal and remap within each pair, at least .02 nats. Strictly
   positive gain in at least 8/10 pairs.
2. Final full validity in at least 8/10 runs for EACH history; familiar-return
   gap full validity in at least 8/10. Full validity means correct local
   partitions, all composite modal predictions correct, expected regret<=.10.
3. Against BOTH selective and relaxed: mean observed AND expected cost<=.02
   in stable whole, familiar early return, burst interval and burst recovery;
   each individual observed cost<=.10. Familiar end-of-gap expected-loss
   mean cost<=.02. These are the unchanged 027 preservation guards.
4. Against relaxed: mean observed AND expected early cost<=.02 separately for
   reversal/remap, every individual observed early cost<=.10, and no increased
   number of censored recoveries in either history. Recovery still requires
   two consecutive full-valid evaluations from 832 through 1280.
5. Added protection against pooling away harm: separately in reversal/remap,
   mean observed AND expected cost in the primary 897–1280 window<=.02;
   each individual observed cost in that window<=.10.

No automatic promotion, horizon extension, additional seeds or tuning after
outcomes. A failed gate completes the confirmation with a qualified/null result.
Preserve all prior criteria and failed results as historical records.

Secondary comparisons remain weaken-selective, combined-selective,
relaxed-selective, combined-uniform, combined-fast and combined-baseline.
The separate selectivity-benefit test against uniform weakening remains a
mean gain>=.01 over stable whole, familiar early return and burst recovery,
positive in>=8/10 pairs. Uniform removal is not matched in removed mass.
Report all policy results, early/post/late losses, full validity, censored
recovery, structural failures, transfer and weakening counts. Also report
the primary gain averaged over the two proposal replicates per environment.

## Frozen execution and verification

New code changes measurement and orchestration only. Before reserved worlds,
check synthetic window boundaries, both success and failure of the gates,
and the independent metric/summary reconstruction. Replay one already saved
027 trace to check the unchanged runtime/reference adapter. Fixtures generate
zero new learning labels and use no reserved seed. Store their evidence and
source hashes. Freeze these sources, this protocol, 027's full manifest and
artifacts, and fixtures before generating any 028 outcome.

Same resource limits as 027: 350 runs; 135040 generated labels; 1890560 label
presentations; 350000 candidate fits; 20 million scoring queries; 100 million
raw-bin visits; 1.3 million oracle context queries. Main predictions 1021440;
grid/transfer allocation 232400; slow probes 24000; legacy auxiliary predictions
12000; reused baseline gap predictions 7680. The new window uses already saved
predictions, creating no additional labels, fits or oracle queries. Benchmark
and independent audit each limited to 900 seconds. Preserve partial outputs on
engineering failure. Never overwrite an existing output directory.

Independent audit verifies world generation, all policies/decisions/checkpoints,
old and new measurements, paired summaries, coverage, provenance and budgets.
The auditor imports no experiment or runtime policy code. Report the outcome
without treating secondary gains as a substitute for the primary criterion.
