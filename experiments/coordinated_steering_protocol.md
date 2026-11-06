# 034 — Does downstream plasticity need local coordination?

2026-11-05. Follow-up authorized after033 demonstrated local benefits but failed
composite/preservation gates. Freeze protocol, sources, independent audit and
passing fixtures before reserved seeds2300–2304, proposal seeds2300/2301.
No earlier source or outcomes are changed. No default promotion or retuning.

## Factorial design

Keep033's worlds, acquisition, misleading protected-channel burst, coherent
post-review refit, reviews and control schedule exactly. Both channel roles are
supplied task instructions, not discovered goals. Use stable, forms and repeated
histories with2048 observations. Commands after review512, release after1024.

Add one capability in a new subclass: channel2 (composite slow evidence) may have
its half-life shortened from1024 to128, exactly as the local plasticity control.
Composite structure is not locked. All update, proposal, transfer and weakening
rules stay fixed; no new feedback or hidden-truth access is supplied to learning.

Five policies, ten seed/proposal pairs per history,150 runs:
U unsteered: ordinary memory and structural learning (033 refreshed variant).
P protected: lock stable local p; ordinary memory elsewhere.
L local: lock p; slow half-life128 in changing local q.
D downstream: lock p; slow half-life128 in composite2.
C coordinated: lock p; slow half-life128 in q and composite2.

P,L,D,C form a2×2 comparison with protection constant. U separately measures
whether the entire instruction helps. Every policy uses identical examples and
selection rows. At release all half-lives return to1024 and locks clear, without
restoring lost evidence or undoing proposal history. Checkpoint/restore at768.
Stable controls measure the cost of unnecessary plasticity.

## Questions and frozen criteria

Use033's independent expected/observed losses for all three channels and windows:
active513–1024; burst513–640; settled641–1024; returning1025–1536; later1537–2048.
Latent truth is evaluation-only and excludes the misleading burst. Final full
validity retains correct local partitions, all modal composite predictions
correct and expected regret<=.10. Retain failures and all acquisitions.

Let L_X denote policy X's active expected COMPOSITE loss; lower is better.
Primary incremental comparison: L_D−L_C. This directly asks whether adding local
plasticity helps when the downstream learner is already plastic. Report also
L_L−L_C (adding downstream plasticity), L_U−L_C, L_P−L_D, L_P−L_L and L_P−L_C.
The factorial interaction is (L_D−L_C)−(L_P−L_L): positive means local plasticity
adds more benefit with downstream plasticity than without it. Interaction is
reported separately; beating D alone is not proof of super-additive synergy.

Full usefulness gate requires ALL:
1. Audit and controls correct; coherent snapshots, local lock invariants,
   targeted decay, release and identical checkpoint continuation verified.
2. P/L/D/C protected-form burst correctness>=.95 in EACH changing history.
3. C versus D pooled changing-history expected composite gain>=.005 nats,
   positive in>=12/20 pairs (positive means>1e-12).
4. C versus L same mean and consistency thresholds.
5. C versus U same mean and consistency thresholds.
6. Preservation: C against BOTH U and D, separately for each history and each
   returning/later window, all3 expected-output mean costs<=.02 and every
   individual<=.10. Same guards for stable active window. Also mean active
   expected composite cost<=.02 in each changing history against U and D,
   preventing favorable pooling from concealing a substantial history-level cost.
7. C final full validity>=8/10 in EACH history.

Report the primary C-versus-D result separately from full conjunction. Interaction
support is a secondary declared criterion: pooled mean>=.005 and positive in
>=12/20 pairs. Report all five environment means and per-history results, guard
failures, raw-interface use and local correctness. Two proposal seeds are not
independent environments. Include observed losses and release endpoints; no
additional success rule may be invented after outcomes. A failed comparison
cannot by itself prove a single downstream bottleneck or explain every failure.
This tests scheduled joint plasticity, not a learned coordination controller.

## Validation, resources and closure

Reuse the transformed7990 fixture from033, at most8 attempts with<=8 small runs
per attempt; no fresh random fixture labels. Independent audit imports no new
runtime/runner/metrics code and builds on frozen033 independent arithmetic.
Validate all five policies, composite decay, config failure atomicity, restore
while active, release and all metric gates. Compare U/P/L against033 counterparts
on the SAME reused fixture to verify behavioral compatibility (schema/control
reasons differ); fixture replays are charged separately.

153600 generated scalar labels;1536000 training presentations;150 runs. Caps:
250000 candidate fits,18m scoring queries,90m fit-related raw-bin visits,
200000 grid predictions. Count extra selective-decay cell visits separately:
1105920 in this design, excluding the inherited ordinary decay. Runner and
auditor<=900s each. Save partial failures. Manifest protects033 and ancestors,
new sources and all fixtures before outcomes. Do not overwrite or rerun reserved
outcomes, change controls, or promote an architecture to rescue failed gates.
