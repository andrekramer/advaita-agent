# 030 — Repeated changes, returning forms and rare distinctions

2026-11-02. Run only after 029 exact compatibility passes. Freeze this protocol
and all new sources/fixtures before seeds 1900–1904; proposals 1900/1901.
Three histories, four policies (baseline, fast, relaxed, combined), ten paired
runs: 120 runs. No changes to the frozen engines or 029 common runtime.

Use the same four raw states per node, binary local forms, XOR composite,
action, independent 10% label flips and acquisition as 026–028. Local training
256/node, four selections of32/node, then256 representative compositions.
RNGs: layout201000+seed, input202000+seed, local/composite noise203000,
204000,205000+seed. Generate acquisition, all main rows, then all selection.
Balanced shuffled blocks, with independent fresh selection32 every64 ticks.

Main horizon2048, four512-tick phases; no blank ticks. Histories:
* repeated: original, inverted affected local/composite outcome, original,
  inverted again. Partition identity unchanged by polarity inversion.
* forms: original, the same alternative partition construction as026, original,
  alternative again. Composite follows the currently applicable local form.
* rare: unchanged truth throughout. Uniform contexts for first/final512 ticks.
  During513–1536, each32-row block has30 examples from affected form's original
  zero class and2 from its one class; selection has exactly the same imbalance.
  Draw each stratum by repeated shuffled context blocks, then shuffle the mixed
  block. Rare group is supplied only to the simulator/evaluator, never learner.

Uniform context grids every64 ticks and transfer24 immediately after acquisition.
Use the existing oracle structure tests and full validity: correct local
partitions, modal composite accuracy1, expected regret<=.10. Save all three
pre-update probabilities. Retain slow probes at256/768 for comparability.
The rare-group probe is expected composite loss averaged over the16 rare contexts
at1536. It uses saved grid probabilities, no additional observations or fitting.

Primary candidate combined, control relaxed. Settled revision window is the
union641–1024,1153–1536,1665–2048, fixed in advance and including returns to old
knowledge. Early windows513–640,1025–1152,1537–1664 are reported separately.
Other windows: whole, initial1–512, rare513–1536, return1537–2048. Endpoints at
512/1024/1536/2048; every failure remains in denominators.

ALL primary gates required:
1. Mean observed settled gain against relaxed, equally weighting repeated/forms
   per pair, >=.02 and positive in>=8/10 pairs.
2. Final full validity>=8/10 in EACH history.
3. Rare-group expected loss gain at1536 against fast>=.02, positive>=8/10 pairs.
4. Against relaxed AND baseline, mean observed/expected cost<=.02 for initial
   window in every history, rare whole and rare return; each observed pair<=.10.
5. Against relaxed, mean observed/expected settled cost<=.02 separately in
   repeated/forms and every observed pair<=.10. Same limits on early windows.

Report all policies, expected/observed losses, full endpoint validity, rare-group
loss, counts of automatic weakening, cost totals and environment-averaged gains.
No general-superiority claim, no promotion, extra seeds or tuning. Failure still
completes this stage; 031 can test a bounded intervention without claiming this
broader gate passed.

Fixtures: synthetic arithmetic and at most2000 learning-label presentations on
seed6990, all attempts preserved. Independent generator and policy arithmetic
replay; no runtime/policy imports in the auditor. Freeze prior028/029 artifacts.
Budget:153600 generated labels,1228800 presentations,120 runs;200000 candidate
fits,15m scores,60m raw-bin visits,800000 oracle context queries;900s per benchmark
and audit. Main predictions737280; grid125760; slow probes7200; auxiliary5040.
The baseline uses frozen legacy execution; weighted trials run through the
common API and save its outer checkpoint as well as the native engine state.
