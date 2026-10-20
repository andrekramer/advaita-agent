# Experiment 015: earning inertia for a learned form

Fixed before execution, 2026-10-20. Follow-up authorized after 014 to isolate
local abstraction stability. Run one fresh benchmark, independently audit it,
record failures, and stop. Do not tune or rerun earlier experiments.

## Question and scope

Can protecting an established form reduce destructive replacement without
blocking initial discovery or adaptation to a lasting change? Experiment 011
found that uniformly stronger acceptance could block useful discoveries.
Experiment 014 exposed both acquisition failures and loss of a correct local
form. Test a fixed, evidence-dependent replacement rule at one local module
before considering integration into the nested system.

Reuse the unchanged 013 partition model: four observed raw states, eight
unordered partitions into at most two groups, Beta(1,1) predictive counts,
192 main-record memory, four shuffled-deck proposals per review. Rank fitted
proposals on the latest 64 main records; compare the winner on 32 fresh
selection records. Review every 64 main observations. Selection labels never
fit a table. Predictions precede feedback.

There is no upper module in this point test. No learned depth, new objectives,
meta-learning, or claim of necessity for the full R-rule/IVSR dynamics.
The learning rules, proposal vocabulary, tolerances and budgets remain supplied.

## Worlds and pairing

Five environment seeds 500–504 crossed with learner seeds 500,501.
Layout RNG 71000+environment shuffles raw states. Form A assigns zero to the
first two and one to the last two; form B flips membership of the first and
third shuffled states (one from each group). Both forms are balanced.
Input RNG 72000+environment shuffles blocks containing all four raw states.
Noise RNG 73000+environment independently flips each supplied binary label
with probability .1. Learner RNG is 74000+learner_seed.

Generate 1,024 main observations first, then sixteen 32-record selection
batches in review order. Each selection batch uses the observation regime
at its review index. The learner receives raw state and observed outcome,
never branch, time-of-change signal, true form or evaluator probabilities.
All branches share input order and noise draws; variants share each stream.

Three branches:

* `persistent`: form A throughout.
* `remap`: A through main/review 512, B from 513 onward. Both true outcomes
  and observations follow this lasting change.
* `transient`: true form remains A; observations follow B only for main
  513–576 and selection review 576, then return to A. This is structured
  temporary observation corruption, not merely extra independent label noise.

The evaluator uses .9/.1 around the true form; in the transient corruption
window this deliberately differs from the observation channel. Report observed
pre-feedback loss and latent expected loss separately. In real use, the learner
cannot know whether that temporary discrepancy is corruption or a real change.

## Three acceptance policies

`immediate` is exactly the 013 local rule: replace if winner improvement
on the fresh batch exceeds .005 nats.

`uniform` requires two successive fresh-batch improvements >.005 for the
same frozen challenger before every replacement.

`earned` uses immediate replacement until the incumbent is established.
An unchanged incumbent becomes established after two consecutive review
batches with its mean loss <=.55 nats and no accepted replacement.
Any failed adequacy batch resets this consecutive count. Once established,
the flag remains latched until replacement; it then requires the same
two-witness replacement rule as `uniform`. Every replacement clears
establishment and its counter. No oracle validates establishment: a wrong
form may earn protection.

For both corroborated policies:

1. Fit and rank the ordinary four proposals before reading selection labels.
   Continue doing so even if a challenger is already pending.
2. When no challenger is pending, a winning improvement >.005 either causes
   immediate replacement (if permitted) or starts a frozen challenger with
   its first witness. Store its partition and counts, at most two cells.
3. At the next review, compare that frozen challenger against the current
   incumbent on the new selection batch. Incumbent counts continue to refit
   on main observations; pending counts never refit. Accept on gain >.005,
   otherwise discard. In either case do not start a different challenger
   in that same review. Pending evidence takes priority over the fresh winner.
4. If no replacement occurs, update the incumbent's adequacy count/flag from
   its current selection loss. The current batch also served candidate
   comparison; this is adaptive reuse, not an independent confirmation of
   policy choice or a calibrated statistical test.

All variants compute establishment diagnostics; only `earned` uses the flag.
Prediction consults only the deployed model. Establishment concerns retention
of a partition, not freezing its numerical estimates or guaranteeing that
its semantic group labels cannot reverse. All three have identical label and
candidate-fit budgets. Pending scoring/memory adds cost, and decisions can
alter subsequent proposal decks through the nonincumbent exclusion.

## Fixed evaluation and success criteria

Evaluate all four raw states before training and after every review without
mutating the learner. Validity requires exact exported groups matching the
true form, modal predictive accuracy 1, and expected log-loss regret <=.10
above the 10% noise oracle. Report exactness separately from this conjunction.

Initial acquisition is validity at 256 (count once per seed pair, not three
times for shared branches). First acquisition is the first valid review up to
512, using 576 as a failure sentinel. Stable remap recovery is the first of
two successive valid post-change reviews, using 1088 if none within budget.
Include all acquisition failures in all comparisons.

Primary success for `earned` requires all:

1. At least 8/10 initially valid runs; no more than one fewer than `immediate`,
   and mean first-acquisition index no more than 64 later.
2. In both persistent and transient, at least 8/10 final-valid runs.
3. Across persistent and transient, fewer invalid post-review checkpoints
   (indices 320–1024) than immediate: at least 25% fewer in total, a positive
   control count, and strict reductions in at least two of the 20 paired runs.
4. Persistent mean observed main loss <=.02 above immediate; transient mean
   latent expected loss over records 513–768 <=.02 above immediate.
5. Remap final validity >=8/10; mean stable recovery index <=64 later than
   immediate; mean observed loss over records 513–1024 <=.05 above immediate.

Compare uniform corroboration descriptively; no claim of its inferiority is
required or assumed. These are fixed practical margins, not statistical
significance. Five environments crossed with two proposal seeds are not ten
independent tasks. A zero-error immediate control leaves a protection benefit
undemonstrated. Record all replacements, establishment of incorrect forms,
pending failures, loss of exactness, and latency costs.

## Budget, freezing and audit

5 environments *2 proposal seeds *3 branches *3 policies =90 runs.
Each uses 1,024 main +512 selection labels: **138,240 allocated and used
label presentations**, from 23,040 labels in 15 generated branch streams
(including duplicated shared histories). Exactly 5,760 candidate fits.
6,120 checkpoint prediction queries; latent loss also scores the 92,160
already-made main predictions without additional model queries.
At most 30,720 extra pending selection predictions. Buffers remain 192
main records, with at most two additional pending cells.

Before the single benchmark, hash this protocol, new source, tests and
independent auditor plus reused 013 source and independent audit helpers.
Verify every manifest from 010–014. Refuse output overwrite. Test immediate
equivalence, initial freedom, earned protection, frozen evidence, failed
witness priority, establishment reset, world pairing and evaluation isolation.
Independently reconstruct streams, tables, decisions, predictions, metrics,
criteria and costs without importing the experimental implementation.
