# Experiment 001: learn a tiny input/output mapping

Protocol written before running the experiment. This is the narrower first
experiment authorized after the mathematical design; it does not run or replace
the larger cue-gap-action-reversal experiment in maths-v1.md.

## Question and model

Can the externally driven fast/slow update acquire a two-cue mapping and retain
it during evaluation with learning disabled?

The offline teaching data maps A -> Q and B -> P. Input cue and output category
are distinct variables. Inputs are one-hot vectors x=(1,0) for A and (0,1) for B.
The learner predicts p(P|x)=sigmoid((F+S) dot x). The teacher supplies target y=0
for Q or y=1 for P only after the prediction is recorded. The update is
g=x(y-p), F'=rho_f F+eta_f g, S'=rho_s S+eta_s g, with componentwise clipping.
The teacher's mapping is not part of the learner's initialization or prediction
function. W^0, F, and S start at zero.

## Fixed parameters and limits

- rho_f=0.95, rho_s=0.999, eta_f=0.20, eta_s=0.02, inherited from v1.
- Each fast/slow component is bounded to [-8,8], with all learning gates open.
- Both active and inactive relations decay on each training trial.
- No bias term, input delay, action selection, phase learning, or consolidation.
- Directly visible input features correspond to a fully loaded trace with no
  gap; communication gates are fixed at 1.
- Seeds 0 through 4. Each shuffles 100 A and 100 B training cues independently.
- Evaluate on 20 A and 20 B cues, shuffled with seed 10000+training_seed.
- Evaluation performs no learning, decay, phase updates, or other state changes.
- Compare with an untouched zero-weight model on the same evaluation inputs.
- Predict P at p>=0.5, including a tie, and Q otherwise. The balanced frozen
  control therefore has exactly 50% accuracy and log loss log(2).
- Exactly 1,000 training updates across five seeds, and 200 read-only evaluation
  examples per model condition. No hyperparameter search or additional variants.

## Pass criteria and reporting

Each seed must achieve at least 90% frozen-evaluation accuracy and mean natural
log loss strictly below 0.5. Report every seed, including failures. Report the
frozen baseline's log loss log(2), approximately 0.693147.

Save every pre-update prediction and loss, external target, post-update fast
and slow weight vector, final state, and evaluation record. Plot a trailing
20-example average of pre-update loss and unsmoothed weight trajectories for
all seeds. The display smoothing does not enter learning or scoring.

The evaluation uses fresh presentations of the same two cue types. Success
shows learning the supplied mapping, not generalization to unseen inputs or
superiority of two timescales. Consolidation and differential-trigger claims
require separate experiments. Keep the selected parameters if the run fails;
record any later design changes separately.
