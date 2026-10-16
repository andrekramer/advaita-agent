# Experiment 008: collapse a distinction when its consequences become equivalent

Fixed before benchmark execution, 2026-10-16. Small point test following
[form acquisition](forms_protocol.md). This tests selective structural
simplification, not the fast/slow complementarity hypothesis. Seeds 0–4,
one run per condition; no tuning, extra seeds or automatic next experiment.

## Conditions and world

Use the same three binary features, two actions, binary outcomes, and cube-based
recognition language as Experiment 006. Start with one undifferentiated form.
No category labels, relevant-feature index, phase label, or change flag enter
the learner. Each seed shuffles feature positions with Random(seed).

For main trials 1–96 the world obeys y=s XOR a. Then branch into:

- **Changed:** trials 97–192 obey y=a. Both previously distinguished groups now
  have the same action consequences, while actions remain consequential.
- **Unchanged:** continue y=s XOR a through trial 192.

Compare **merge_enabled** and **merge_disabled** in each branch. Both can learn
new splits. Disabled omits every candidate that reduces the number of forms;
it does not disable parameter learning or force incorrect predictions.

Neither learner is initialised with the desired two forms. It must acquire
them in the first phase. If acquisition fails, report failure without inserting
a hand-built representation or rerunning the seed.

Exclude contexts 000 and 111 from main training, selection, and learning probes.
The other six contexts, each under both actions, yield 12 admissible pairs.
Generate 16 balanced shuffled passes with Random(8000+seed). Generate four
independently shuffled balanced selection batches with Random(9000+seed).
Each batch has 12 pairs and follows main trials 48,96,144,192. Labels follow
the current branch's world. Pair feature encoding, all input/action sequences,
and selection orders across learners and branches; labels diverge only after 96.
This deterministic, balanced setup does not test rare cases or observation noise.

## Fixed recent-evidence window and learning

Use the single structural learner, retaining only the most recent **48 main
observations**. This window applies from the first observation in both branches
and both variants. It is never cleared at the change point. Predict first,
reveal y, append the record, expire the oldest record if necessary, and refit
counts for the current structure from exactly that window. This removes expired
observations from the sufficient statistics as well as from storage. Window
expiration updates counts but never changes the recognition structure itself.

Retain the Experiment 006 estimator p(y=1|form k,a)=(r_ka+1)/(n_ka+2), its
split/merge operations, sibling collapse, canonical ordering, caps of four
forms/eight leaves, objective and selection margin:

J(M;B)=mean binary log loss on B +0.01 K(M)+0.005 L(M).

At each 48-trial boundary enumerate the incumbent structure and legal one-step
neighbours, omitting form-count reductions for merge_disabled. Refit all
candidates on the current window. Advance only the lowest-training-objective
candidate, with canonical structure breaking exact ties. The incumbent is
already fitted on that same window. Maximum 31 unique candidates per review.

Evaluate the winner and incumbent on all 12 selection pairs before any structural
change. Accept iff J(incumbent;V)-J(candidate;V)>0.001. Selection examples never
enter the window or its counts. No evaluation label is used for proposing,
ranking, selecting, or fitting. Record predictive loss and complexity penalty
separately, so a preference for fewer forms is not reported as a prediction gain.

Merge proposals and a complexity preference are constructed mechanisms. The
question is whether they are used when appropriate while preserving predictive
competence, not whether a motivation for simplicity emerges spontaneously.
The phase change happens at a review boundary for this point test; its timing
is known to the evaluator only. Detection at arbitrary times is not established.

## Evaluation and criteria fixed before execution

After the reviews at trials 96 and 192, freeze all state and predict both actions
on all eight contexts. Reveal outcomes only for the four withheld context/action
pairs. The other 12 predictions are unlabelled invariance diagnostics. Check
snapshot equality before and after evaluation. Category identities are arbitrary;
compare the induced partition, not identifier names. Diagnostic latent partitions
belong only to the evaluator.

Acquisition at 96, in every run: two forms/two leaves, partition exactly matching
the simulator's relevant bit, 100% withheld accuracy, log loss <0.25, no nuisance
bit effect (>1e-12), and relevant-bit probability effect >=0.5. Both learners must
pass before claiming that a previously learned distinction was collapsed.

Changed branch, in every seed:

1. merge_enabled accepts an actual form-count reduction after acquisition,
   ends with one form and one all-wildcard leaf, and does not re-expand at a
   later review after reaching one form. Record first collapse trial and delay
   from the change, rather than assuming immediate collapse.
2. Its withheld accuracy remains 100% at the final checkpoint, loss <0.25,
   prediction is invariant to every context bit (<=1e-12), and changing action
   changes the probability by >=0.5. This excludes a constant-output collapse.
3. merge_disabled ends with two forms/two leaves and also achieves 100%
   withheld accuracy and loss <0.25. Thus its ability to adapt is not disabled.
4. Final enabled log loss is no more than 0.01 above disabled log loss. This
   is a preservation criterion, not a claim that merging must improve accuracy.

Unchanged branch, in every seed: both variants retain the correct two-form
partition at the final checkpoint and every review after trial 96, accept no
merge, and meet the acquisition prediction/invariance criteria. Explicitly
record whether an available merge candidate loses in training ranking or is
externally rejected; these are different events.

Overall success requires all of the above in all five seeds. Report every run,
including failed acquisition. Log pre-update losses and all review structures;
do not interpret correct final predictions as proof of structural collapse.

## Budget, audit, and stopping boundary

5 seeds *2 branches *2 learners *(192 main +48 selection +8 held-out outcomes)
= **4,960 allocated and accessed outcome-bearing presentations**. There are
480 additional unlabelled checkpoint predictions. Candidate scoring reuses
stored records and selection labels; log candidate counts and replayed rows
separately. All full runs are allocated even though their prefixes are paired.
This is a new budget; no previous benchmark is rerun or modified.

Write the protocol and source hashes before execution. Synthetic tests must
check rolling expiration, candidate exclusion, real merge accounting, selection
isolation and harmful-merge rejection, immutable evaluation, and chronology.
An independent saved-record audit must reconstruct the paired streams, rolling
windows, current/candidate counts, predictions, selection gains, checkpoints,
criteria, budgets and hashes. Reuse the immutable structural operations from
forms.py; record its hash and leave prior experiment sources/results untouched.

Stop for invalid arithmetic, data leakage or failed audits; disclose any genuine
implementation correction. No parameter tuning or additional benchmark runs.
All actions stay in the isolated simulator. This experiment does not establish
when to forget rare distinctions, whether collapsed forms can be recovered,
or the safety of collapsing distinctions in other settings.
