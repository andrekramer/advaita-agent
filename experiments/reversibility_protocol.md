# Experiment 009: acquire, collapse, and reacquire a distinction

Fixed before benchmark execution, 2026-10-16. This closes one gap in the
[collapse point test](collapse_protocol.md). It tests reversible structural
revision within the supplied language, not meta-learning, hierarchy, memory
retrieval, or fast/slow complementarity. Five seeds (0–4), two variants, one
execution, no tuning or automatic further experiments.

## World, pairing, and evidence

Reuse the Experiment 008 `Learner` without modification, including its
48-main-observation rolling window, count estimator, candidate language,
training ranking, external selection, 0.001 acceptance margin, complexity
penalties, and four-form/eight-leaf caps. Both variants start with one form.
`merge_enabled` allows the existing merge operation; `merge_disabled` excludes
form-count reductions but otherwise learns identically. Reuse Experiment 006
structural primitives unchanged. No learner reset or saved-form restoration.

Three phases of one continuous run:

| Main observations | World | Purpose |
| --- | --- | --- |
| 1–108 | y = s XOR a | Acquire a consequential distinction |
| 109–228 | y = a | Make the distinction unnecessary |
| 229–336 | y = s XOR a | Make it consequential again |

Here s is one of three binary observed features and a is a binary action.
The learner receives only observed features, action, and subsequently outcome;
it receives no relevant-feature index, phase label, change flag, or target
category. Evaluation alone uses the phase schedule and latent partition.

Reviews remain fixed at 48, 96, 144, 192, 240, 288, and 336. The first review
after collapse-world onset therefore has 36 new / 12 old window records; the
first review after the return has 12 new / 36 old records. Counts expire
normally; nothing is cleared or restored at either change. These are two fixed
offsets, still aligned with balanced input passes, not broad random timing.

Withhold contexts 000 and 111 under both actions from all learning. The other
six contexts under both actions make 12 admissible pairs. Shuffle feature
positions with Random(seed). Generate 28 independently shuffled balanced main
passes using Random(10000+seed), and seven shuffled balanced selection batches
of 12 using Random(11000+seed). Input orders, outcomes, and feature encoding are
paired between variants. Label each main observation under its current phase;
each selection batch uses the world at its review boundary. Freeze the world
during each batch. Selection never enters fitting or the rolling window.

## Evaluation and fixed criteria

After every review, freeze state and predict both actions for all eight
contexts. Reveal only the four withheld outcomes. Use the remaining 12
predictions for unlabelled invariance diagnostics. Check state and buffer
immutability. Evaluation never controls a subsequent update or stopping rule.

Use the existing acquisition criterion: exactly two forms/two recognition
leaves, partition matching the relevant bit up to naming, 100% withheld accuracy,
log loss <0.25, nuisance-feature effect <=1e-12, and relevant-feature probability
effect >=0.5. The useful-one-form criterion is one form/one all-wildcard leaf,
100% withheld accuracy, loss <0.25, all context effects <=1e-12, and action
probability effect >=0.5.

Every seed must meet all of these conditions:

1. Both variants satisfy acquisition at review 96 and accept no merge during
   the initial phase. Failure is reported; no constructed starting forms.
2. At review 192, enabled meets the useful-one-form criterion and has accepted
   a real form-count reduction during phase B. Once it first reaches one form
   during B, it remains one at all remaining B reviews. Disabled still has two
   forms/two leaves, 100% withheld accuracy, loss <0.25, context effect <=1e-12,
   and action effect >=0.5. Enabled loss is no more than disabled loss +0.01.
3. Enabled accepts a form-count increase after the return, following its actual
   collapse, and satisfies acquisition by review 336. Once it first satisfies
   acquisition in phase A2, it continues to do so at all remaining reviews.
   Disabled also satisfies acquisition at 336 and has accepted no merge anywhere.
   Enabled final loss is no more than disabled final loss +0.01.

Overall success requires all conditions in all five seeds. Do not require a
particular first-collapse or recovery review. Record both first structural
changes and first successful evaluation, keeping these distinct. Time to
recover is measured only at scheduled reviews; report main observations and
selection outcomes since the corresponding world change. A candidate split
alone is not successful recovery. Also report disabled prediction-recovery time.

Report every review's forms, leaves, accuracy, and log loss, plus all accepted
structural changes. Report mean pre-feedback main loss separately in A1, B, A2,
and over the first 48 observations after each change. Those transition losses
are diagnostics, without a retrospectively chosen superiority criterion.
Include predictive and complexity components of each accepted structural gain.
No fresh-start comparison or saved-form retrieval is included: reacquisition
cannot establish memory, faster relearning, or a benefit over learning anew.

## Verification, budget, and stopping

5 seeds *2 variants *(336 main +84 selection +28 withheld outcomes)
= **4,480 outcome-bearing presentations**. Seven checkpoints add **840
unlabelled predictions** across all runs. Candidate scoring reuses stored data;
report candidate fits, replayed rows, current-count refits, and selection use.
Storage remains at 48 main records; no larger model or additional learner.

Save protocol and source hashes before running. Synthetic tests check phase
boundaries, paired evidence, mixed windows, reacquisition from a collapsed
structure, evaluation isolation, and metric chronology without piloting the
benchmark. Independently audit saved streams, candidate enumeration/ranking,
window expiration, counts, pre-feedback predictions, selection decisions,
checkpoints, metrics, paired controls, budgets, and hashes without importing
learner code. The independent arithmetic helpers from the Experiment 008 audit
may be reused unchanged and hashed.

Refuse to overwrite results. Stop for arithmetic errors, leakage, or failed
audit; disclose any implementation correction. Do not tune after seeing the
benchmark. Leave previous experiments and their hashed sources unchanged.
Stop after the bounded run and consolidate results, including failure if any.
Rare distinctions, noisy equivalence, interference resistance, hierarchical
categories, and changes to the learning rules remain separate open questions.
