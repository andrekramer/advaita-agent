# Round 2: retention, transient errors, and selective consolidation

Fixed before execution on 2026-10-14. Small isolated four-category simulations,
not an increase in model size. No parameter tuning or additional seed search.
Use seeds 0–4 and the input/output encodings, reference-logit model, mappings,
and four controls from Experiment 002. All comparisons are paired within seed.
Mappings A and B differ for every input. Targets are revealed after prediction.
All blocks have balanced inputs in independently seeded shuffled orders.

## Shared measurements and boundaries

Use natural log loss and accuracy; ties follow 00,10,01,11. Evaluate each of the
four input types exactly once at each checkpoint: repetition would add no
information for these deterministic mappings. Evaluation never changes weights,
decay, diagnostic state, or counters, and its targets never enter learning or
selection. These are fresh presentations of known categories, not unseen-input
generalization. Log every training prediction, target, and post-update state.

Recovery is the first trailing-40 pre-update accuracy >=90%, considering only
the designated recovery block. Null means not reached within that block; retain
nulls rather than dropping them from comparisons. Acquisition/reacquisition
checks use >=90% accuracy and loss <0.9, inherited from Experiment 002. These
checks are distinct from the comparative IVSR criteria below. Report every seed,
including failures. Five seeds support descriptive comparisons, not significance
claims. Preserve finite probabilities, normalization, bounds, and all counts.

## 003: retention and interference

Four original variants: fast/slow, fast only, slow only, frozen. Per run:

1. Train A for 240 pairs; evaluate A.
2. Apply 100 decay-only ticks with no input, target, gradients, or consolidation;
   evaluate A. These ticks are not missing inputs encoded as state 00.
3. Train B for 240 pairs; evaluate B and, separately, the overwritten mapping A.
4. Train A again for 240 pairs; evaluate A and measure recovery within this block.

Report loss increase across the gap; A accuracy/loss after B; reacquisition
loss/recovery; and all checkpoints. The comparative retention claim is supported
in this setup only if dual learning has at least 0.02 lower A loss after the gap
than fast-only in every seed. This does not imply superiority over slow-only.
Relearning A is not evidence of storing two context-addressable memories: the
input provides no context telling the learner which of two conflicting maps to use.

Budget: 20 runs × (720 training + 20 evaluation) = 14,800 labelled presentations,
plus 2,000 decay-only ticks. No selection data.

## 004: transient wrong targets versus lasting change

For each of four original variants and five seeds, use two fresh paired runs:

- Both streams: A for 240 pairs, then B for 40 pairs.
- Transient stream: return to A for 200 pairs. The 40 B labels are a correlated
  burst of incorrect targets relative to the unchanged underlying A task.
- Persistent stream: continue B for 200 pairs. B is now the desired mapping.

The streams share identical input order and labels through trial 280 and diverge
only in subsequent targets. The model receives no stream label or change flag.
Evaluate A after warmup. At trial 280 evaluate A in the transient stream and B
in the persistent stream. Evaluate the current desired map at the end. Report
the transient A-loss increase over warmup, final loss and tail recovery in each
stream, and persistent-tail pre-update loss. This specifically tests a correlated
error burst, not IID label noise or a general noise detector.

The proposed dual-timescale noise/change tradeoff is supported here only if, in
every seed, dual learning has no larger transient A-loss increase than slow-only
and no larger persistent-tail mean log loss than slow-only, with at least one
strict improvement per seed. Also report fast-only and frozen results. This is a
test of outcomes, not a claim that either learner explicitly classifies noise.

Budget: 40 runs × (480 training + 12 evaluation) = 19,680 labelled presentations.

## 005: fast-to-slow consolidation

One stream per seed: A240, B40 (transient corruption), A200 (recovery), B240
(lasting change), then 100 decay-only ticks. Checkpoints after each training
block and after the gap. Evaluate combined and slow-only heads on the current
desired map (A at the transient checkpoint, B at the final two checkpoints).
The slow-only head of a model without slow weights is uniform; it is only a
diagnostic. Main performance comparisons always use the combined head.

Ten variants:

1. The four original controls, unchanged.
2. `hybrid`: original fast/slow updates plus selected consolidation.
3. `transfer_only`: eta_f=0.22, eta_s=0; only consolidation can add slow weight.
4. `transfer_disabled`: same parameters as transfer_only, with transfer off.
5. `no_trigger`: hybrid with differential trigger removed, external selection kept.
6. `no_selection`: hybrid with differential trigger kept, external selection removed.
7. `parallel_extra`: original fast/slow learner also trains on the reserved
   selection pairs. This gives an additional comparison using all available labels
   for gradient learning, including their ordinary decay updates.

Consolidation implements maths-v1-consolidation.md:

- Every K=20 main training updates, after ordinary updates and with no pending
  feedback; never during gaps or evaluation. Maximum 36 boundaries per run.
- U contains all four input states, without targets. Compute signed gaps between
  combined A and slow-only N, per-input TV distances and their mean D.
- EMA starts at zero: Dbar'=0.75 Dbar+0.25 D. Trigger requires both D>0.05 and
  Dbar>0.05. Never reset at a mapping change; the model is not told about it.
- kappa=0.25; all transfer masks one. Clip the proposed transfer to the interval
  feasible for both F and S, each bounded by 8. No independent post-transfer clip.
- Fresh selection batch: eight pairs (two per input), independently shuffled,
  from the current observed target process. At a burst boundary the selection
  labels are also corrupted B labels; at a lasting-change boundary they are B.
  No future labels, evaluation labels, or training records enter selection.
- Accept the whole feasible transfer only if the gate opens and slow-only mean
  selection loss improves by strictly more than delta=0.001. Subtract accepted
  C from F and add it to S. Verify immediate combined predictions are conserved
  within 1e-12. Log candidates, gains, decisions, conservation errors, F/S states,
  and data use. No_selection uses only the differential gate; no_trigger considers
  external selection at every boundary.

Reserve the same eight selection pairs at every boundary for every variant.
Gated models access them only when triggered; unused slots are logged separately
by the experiment harness, not fed to the model. Baselines ignore them except
parallel_extra, which trains on all eight. Thus allocation is matched, actual
label use differs and is reported. Selection is training information, not test
data. In a deterministic four-input task new records repeat known associations;
they do not constitute independent evidence about latent ground truth.

Primary hybrid criterion, in every seed: post-gap combined loss at least 0.02
below original parallel fast/slow, final B accuracy >=90%, and average loss over
the 240 lasting-change training pairs at most 0.05 above the parallel model.
The latter declares the tolerated adaptation cost. Also compare parallel_extra
and both single-rate controls; passing this criterion is not overall superiority.

Transfer-only mechanism criterion, in every seed: accepted transfer and nonzero S,
with post-gap slow-only loss at least 0.02 below transfer_disabled's slow-only
loss. All S additions must come from transfer. This demonstrates useful transfer
in this task, not that external selection or the differential gate is necessary.
Report paired losses, recovery and selection costs for both ablations without
assuming they will improve outcomes or imposing a post hoc success threshold.

Budget: 50 runs × (720 main training + 288 reserved selection + 40 evaluation)
= 52,400 allocated labelled presentations, plus 5,000 decay-only ticks.
Parallel_extra adds 1,440 gradient updates from its allocated selection slots,
not extra data. Four consolidation variants × five seeds ×36 boundaries ×4
contexts = 2,880 unlabelled probe contexts, each evaluated with two heads.

## Total and stopping rule

Exactly 86,880 allocated labelled presentations and 7,000 decay-only ticks.
There are 2,880 unlabelled differential-probe contexts. Extra counterfactual
predictions for selection and conservation checks are computations on these
same contexts, not new data. Run each registered condition once, with no tuning
or extension based on results. Correctness tests use synthetic fixtures, not
additional benchmark seeds. Stop on invalid arithmetic, failed conservation or
budget violations; fix implementation errors transparently before continuing.
Save protocol/source hashes, parameters, full traces, selection-access counts,
per-seed tables and plots. No real-world actuation, structural growth, phase
learning, deployment, or automatic follow-on experiments.
