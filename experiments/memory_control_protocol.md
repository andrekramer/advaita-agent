# Experiment 026: memory control for continuing form learning

Specified 2026-10-30 before reserved worlds. Experiment 025 was the conditional
role confirmation and was not opened; it remains unused. No prior source or
result is changed. This round tests an explicit fast/slow evidence mechanism,
not a learned memory controller or human/AI steering.

## Hypothesis and scope

Can selective migration into revisable slow evidence preserve useful forms
through a gap, while permitting revision when old predictions/forms become
wrong? Separate transfer selection, slow decay and the clock used for decay.
Do not infer usefulness from fast/slow agreement alone. The slow store contains
evidence supporting representations; it is not a second autonomous category
learner or an archive of named old forms.

Keep the original integrated StructuralLearner as a reference anchor. The new
family uses the same finite partitions, local-before-upper reviews, four random
proposal slots, appended upper reductions, selection thresholds and two-witness
collapse rules. All active tables refit on current weighted evidence. Candidate
ranking uses that evidence, rather than the old last-64/local and last-192/upper
windows. No archive retrieval is added to this family. Comparisons WITHIN the
new family isolate memory policies; comparisons with the original include
these stated implementation changes. Neither implementation is promoted here.

## Evidence mathematics

Each local channel has four raw-state bins of [positive,total] evidence; the
upper channel has 32 (x0,x1,action) bins. Each has fast F and slow S tables.
Raw sufficient statistics are retained even when the active prediction uses a
coarse interface. This supplied, finite raw vocabulary is a limitation and a
memory resource, not learned information hiding. Both stores use the same bins.

Each elapsed main tick decays F and S; a labelled observation subsequently adds
one unit to F only. Prediction precedes adding that observation. Half-lives:
fast64 ticks, slow1024 ticks. The base predictor has Beta(1,1) smoothing. Thus
zero evidence means uncertainty (.5), not an observed negative outcome.

At every64th labelled main tick, after ordinary structural review, propose
C=.25F for each of the three channels, limited proportionally by slow total
capacity512. Move accepted mass by F'=F-C and S'=S+C. F+S and all current
predictions are unchanged at that instant. Future decay differs. Fit/score the
slow-only predictor before/after the proposed transfer using the current local
partition or current upper interface and its actual local meanings. Gate each
channel separately: candidate slow loss <=.55 and improvement >.005 on that
review's32 fresh channel labels. No direct observations enter S. Main evidence
can change residence without being added twice. Selection labels never fit a
table. Selection is shared with structural decisions and is not an independent
second confirmation; subsequent online outcomes evaluate usefulness.

Policies (all acquisition identical):

* baseline: original integrated learner, reviews64, hard windows and archive.
* fast: new evidence learner, fast decay, no transfers.
* slow: one evidence store using half-life1024, no transfers.
* always: fast/slow decay, all nonzero proposed transfers accepted.
* selective: fast/slow decay and the specified external selection gate.
* permanent: selective, but slow decay factor1.
* activity: selective, but neither store decays on unlabelled ticks.

Fast/slow stores start from the last192 main acquisition records per channel;
S starts empty. Initial learned partitions/interfaces come from original
acquisition. Weighted-family tables refit these imported statistics before the
initial transfer probe. Acquisition failure remains in all denominators.
A single slow store is not capped at512; its mass is bounded by decay and the
finite horizon and is fully reported. Limiting its capacity could manufacture
a dual-store advantage. All other choices are fixed, not optimized here.

## Worlds and schedule

Seeds1600–1604; proposals1600,1601; five histories; seven policies:350 runs.
Reserve these seeds until fixtures and source freeze. Layout RNG201000+seed;
input RNG202000+seed; separate label-flip RNGs203000,204000,205000+seed.
Two shuffled four-state binary forms; representatives first in each half.
After both forms, draw an affected node; its alternative form swaps the middle
two states of its saved shuffled order (a new partition, not just new names).

Acquisition:256 local main observations per node; review every64 on32 fresh
labels per node; then256 composite observations restricted to representatives.
All targets are original local forms; composite is f0 XOR f1 XOR action. Ten
percent independent label flips. Balanced shuffled blocks of local states,
representative combinations or all32 joint contexts, as applicable.

Main clock1280 ticks; each labelled tick supplies both local labels and one
composite label. Selection:32 new joint rows at each labelled multiple of64.
Generate acquisition, main blocks, then selection blocks. No gap rows or gap
selection labels are generated. Each active segment starts a fresh shuffle
block. Histories share streams through their first divergence.

* stable: original forms and targets throughout, no gap.
* burst: invert affected local target and composite target at257–320, then
  restore; the correct local partition is unchanged. No gap.
* return: ticks257–768 are blank; original knowledge returns at769.
* reversal: same blank interval; from769 invert affected local and composite
  target, retaining the old partition.
* remap: same blank interval; from769 replace the affected local form by its
  alternative, and compute the composite using that new form.

Blank ticks carry elapsed time only, not a zero input or negative observation.
Runtime sees no branch, future targets, change marker or true partition.
Actions are scheduled, not autonomously selected.

## Measurements and decision gates

Evaluate without learning on all32 contexts every64 clock ticks, including
blanks, plus24 unseen combinations immediately after acquisition. During gaps
the latent task remains the old task. At each online observation save all three
pre-update predictions; report observed and expected Bernoulli(.9/.1) loss.
Measure early return769–896, late1153–1280, burst257–320, recovery321–448 and
whole observed stream. Full validity: correct local partitions, composite
modal accuracy1 and expected regret<=.10. Structural validity: correct local
partitions and sufficient/minimal selected interface using the existing .10/.02
oracle tests. Semantic numeric label order is not required.

Record at256 and768: fast/slow mass, fast+slow and slow-only loss, forms and
interface. Report memory transfers, acceptance fractions, change counts and
all costs. Slow-only probes use current forms, not oracle encodings. Recovery
from769 is the second consecutive full-valid evaluation from832 through1280;
null is censored, compared at1344. Report censorship explicitly.

Primary selective-memory support requires ALL:
1. On return, selective improves mean early-return observed loss over fast by
   >=.02, with strictly positive gains in>=8/10 paired seed/proposal runs.
2. At end of gap, selective improves latent loss over fast by>=.02 and has
   full validity in>=8/10 return runs. At final1280, selective has>=8/10 full
   validity for EACH history. No exclusion of unsuccessful acquisition.
3. Against BOTH fast and baseline, selective's mean observed/latent loss cost
   <=.02 in each of: stable whole, burst interval, burst recovery, reversal
   early return, remap early return. Every individual paired observed cost in
   these windows<=.10; mean reversal/remap recovery delay<=64.
4. A distinct selection benefit over always: mean observed gain>=.01 averaged
   equally over burst recovery, reversal early return and remap early return,
   and positive in>=8/10 aggregated pairs. Same safety-of-performance guards
   as item3 against always. These are prediction costs, not safety validation.

Report separately (not pooled into primary): selective versus single slow,
permanent versus selective, activity versus selective. A dual-store advantage
against slow requires return noninferiority<=.02 and mean revision gain>=.02
across reversal/remap early return, positive in>=8/10 pairs, and the same item3
guards against slow. Do not claim necessity when the single-store control
matches/exceeds the richer learner. No automatic confirmation, tuning or extra
seeds. An empirical failure completes the round; engineering failure stops it.

## Resource, provenance and verification

Fixture seed4990; at most5000 new learning-label presentations across preserved
attempts. Saved deterministic replays are separate. Freeze protocol, new
runtime, simulator, metrics, independent reference/auditor and fixture evidence
before generating reserved worlds. Keep prior026-reserved results absent before
freeze. Independent audit imports no new runtime or experiment policy code.

Each full-history run allocates6784 labels; each gap run4480. Total allocated
and used labels:1,890,560 (140 full +210 gap runs). Generated labels across25
worlds:135,040. Main online predictions:1,021,440 across three channels (340,480 labelled joint
observations). Counts are derived from exact world lengths, not additional labels.

Ceilings:250,000 candidate fits,15m loss-scoring queries,100m raw-bin fit visits;
232,400 grid/transfer composite predictions (350*(20*32+24)), plus19,200
slow-only composite and4,800 slow-local diagnostic predictions;1.3m oracle context
visits; memory two tables of40 raw bins, maximum80 [positive,total] pairs per
new learner, plus bounded active/pending tables and audit logs. Main replay
baseline retains its original192-row buffers and one archive. Benchmark and
independent audit each<=900 seconds. Preserve partial outputs on failure.
Store worlds, full decision traces, checkpoints, run and paired measurements,
hashes, audits and a report separating evidence retention from form retention
and future interpretability/steering questions.

All new-family policies score the same counterfactual transfer proposals,
including the nontransferring controls, to match query opportunities; only the
declared policy uses the gate. Acquisition and the original baseline use the
frozen original implementation. Baseline main identities use consecutive
labelled-observation indices; its saved clock mapping restores blank intervals
for evaluation. No learner update is called for its blank ticks.

Evaluation accounting also records12,000 legacy auxiliary predictions (original
baseline endpoints and acquisition checks), and7,680 reused baseline gap-grid
predictions. The232,400 grid allocation includes those reused values; actual
grid/auxiliary composite computations equal236,720. Slow probes add19,200
composite and4,800 local computations. Oracle accounting conservatively charges
all allocated grid entries plus legacy auxiliary evaluations.
