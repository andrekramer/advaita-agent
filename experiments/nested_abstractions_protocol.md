# Experiment 013: learned abstractions and nested interfaces

Fixed before execution, 2026-10-20. This follows the user's request to round out
interfaces, abstractions and nesting before meta-learning. Run once and stop
after the findings. No tuning after results.

## Question and constructed parts

Can lower learners group different situations by their observed local effects,
and can a higher learner reuse those groups in previously unseen combinations?
Can a lower grouping change while the higher predictor remains useful? When a
hidden difference becomes relevant, can prediction failure prompt reopening
the appropriate interface?

This is a two-level supervised composition experiment. Two modules, four raw
states per module, at most two local groups, and the wiring and depth are
supplied. Group membership and response probabilities are learned. The learner
receives noisy local effects as well as a composite outcome. These are extra
observations, not inferred latent causes or oracle category labels. Group IDs
are aligned by their fitted local-effect probabilities; the correspondence
problem between arbitrary category names is not being solved.

The upper interface normally transmits only group IDs. The supplied reopening
operation exposes the raw identity of one module instead. It does not invent
new primitives or discover arbitrary architecture, temporal folds or depth.
No meta-learning, active action selection, or full R-rule dynamics are tested.

## World and stages

Five environment seeds 300–304 and two learner seeds 300,301. For each module,
shuffle four raw identities; the first two have latent form 0 and the other
two form 1. Pick one representative per form (first in each shuffled pair).
The other member is its alternative realization. Pick an affected module
randomly per environment; the learner never receives this choice.

A local probe outcome is the module's latent form with an independent 10%
flip. A composite outcome is form0 XOR form1 XOR action, again with an
independent 10% flip. Actions are balanced binary inputs, not chosen by a policy.

1. **Local acquisition:** 256 main local observations for each module, reviews
   every 64, and 32 fresh local selection observations per module per review.
   Raw identities are balanced within shuffled four-record blocks.
2. **Composition training:** freeze the acquired lower models. Present 256
   composite observations, balanced over the four representative pairs and
   both actions, shuffled in eight-record blocks. Fit the initial upper table
   to all 256 records using learned group IDs (raw IDs for flat). Retain only
   the latest 192 records for subsequent adaptation. No local labels are
   supplied in this stage.
3. **Transfer evaluation:** freeze all learning. Evaluate the other 12 raw
   pairs under both actions, none of which appeared in composition training.
   These states were seen separately during local acquisition. This is
   transfer across compositions, not learning unseen raw primitives.
4. **Adaptation:** 512 main records, balanced over all 16 raw pairs and both
   actions in shuffled 32-record blocks. Each contains two independent local
   effects and one composite outcome. Review every 64 with 32 new, balanced
   selection records. Evaluate all 32 contexts after each review.

Three paired adaptation branches:

* **persistent:** no change.
* **remap:** invert the latent form of both representatives in the affected
  module; its alternative realizations stay unchanged. This changes group
  membership, not merely the names of two groups. Local effects and composite
  outcomes both follow the new forms. The relation between form IDs and the
  composite outcome remains unchanged.
* **breach:** local effects and forms stay unchanged. The composite outcome
  additionally XORs whether the affected raw state is an alternative realization.
  The old local abstraction is now insufficient for the upper task.

Branches share raw inputs, actions and noise draws. Acquisition and composition
training are identical across branches. Neither branch labels, true forms,
representatives, affected-module identity, nor evaluation outcomes enter learning.
Stage boundaries and separate local supervision are supplied.

## Learning and controls

Local candidate partitions are the eight maps (0,b1,b2,b3), with each b binary:
one collapsed partition and seven unordered two-group partitions. Each group
predicts its noisy local effect using Beta(1,1) counts. At each review draw four
distinct non-incumbent partitions from a seeded shuffled deck, refilling as
needed. Fit to the latest 192 main local records, rank by log loss on the latest
64, and advance only the winner to independent selection. Accept for a mean
log-loss improvement greater than .005. Ties prefer fewer groups then the
partition tuple. Refit the incumbent on the rolling buffer after each main
observation. A group's exported ID is its rank in ascending fitted probability
of local effect 1. Local randomness is in proposal ordering, not in labels.

The upper estimator is a Beta(1,1) table. Its modes are coarse (group,group),
fine0 (raw0,group1), fine1 (group0,raw1), and flat (raw0,raw1), always conditioned
on action. An access-restricting view checks raw reads; the coarse prediction
object has no direct raw-state access. Lower modules and search still see raw
inputs. This is information hiding at the prediction call, not secure isolation
or reduced sensing.

Compare four variants with identical shared acquisition and training:

* **reopen:** update both local learners during adaptation. Preserve the upper
  table until a review accepts its replacement. At reviews, first select local
  candidates using only fresh local effects. Then fit upper candidates for
  coarse, fine0 and fine1 to the last 192 composite main records, re-encoding
  them through the current local models. Rank on all those main records; ties
  prefer coarse, then fine0, then fine1. Advance one winner.
  Measure current upper loss on the fresh composite selection batch. Only when
  it exceeds .55 nats, and the winner improves it by more than .02 nats, accept
  the new table/interface. Once a fine mode is deployed, refit it after each
  main record; a coarse table stays frozen between accepted reviews.
* **closed:** update local learners identically but keep the initial coarse
  upper table exactly frozen. This isolates whether changed lower forms can
  preserve the higher relationship without higher relearning.
* **frozen:** freeze both levels after training.
* **flat:** use raw identities and the action directly; update its table on the
  last 192 composite main records. It does not use learned local effects for
  prediction. Shared local acquisition is still performed and counted.

All upper candidates are fit before accessing composite selection outcomes;
local selection uses independently noisy local effects, not composite labels.
Selection observations never fit counts or enter the main buffers.

The objective is predictive log loss alone, without an added complexity utility
or goals/preferences. Capacity limits, gates, windows, stage boundaries and
available operations remain designer choices. The .55 gate is a fixed failure
threshold, not a learned consolidation mechanism or a guarantee of calibration.
The flat comparison does not establish superiority over all flat learners:
the nested architecture exploits additional local supervision and supplied wiring.

## Fixed criteria

All runs, including failed acquisition, remain in denominators. Lower exactness
means exported groups match current true local forms. Predictive validity means
accuracy 1 against the most probable outcome and expected log-loss regret at
most .10 nats relative to the 10% noise oracle. Evaluation uses true probabilities
only outside learning and checks state purity.

Primary success requires all of:

1. Transfer: closed has exact lower forms and valid prediction on the 24
   withheld composition/action contexts in at least 8/10 seed pairs. Its mean
   expected loss is at least .15 nats below flat on those contexts.
2. Remap: closed finishes with exact new lower forms and valid full-context
   prediction in at least 8/10 pairs; its upper table is unchanged in all runs.
   Frozen finishes at accuracy <=.80 in at least 8/10, confirming a consequential
   change. Reopen also finishes coarse with exact forms and valid prediction
   in at least 8/10, rather than needlessly retaining finer exposure.
3. Breach: reopen finishes in the fine mode of the affected module with exact
   local forms and valid prediction in at least 8/10. Closed finishes at accuracy
   <=.75 in at least 8/10. Mean final expected-loss improvement over closed is
   at least .15 nats.
4. Persistence: reopen stays coarse at every adaptation review, with exact
   final lower forms and valid final predictions, in at least 8/10. Its mean
   adaptation pre-feedback log loss is no more than .02 nats above closed.

These are practical thresholds, not significance tests. Ten seed pairs share
five environments. No result conditional on successful acquisition replaces
the unconditional criterion.

Report every partition change, upper candidate and gate decision; held-out
transfer, pre-feedback adaptation loss, recovery reviews, exposed raw reads,
upper table sizes, fitting work and all failures. Distinguish preserving a
frozen upper relationship by construction from learning when to freeze it.

## Budget, provenance and stopping

5 environments *2 learner seeds *3 branches *4 variants =120 runs.
Per run allocate 768 local-acquisition labels, 256 composition labels,
1,536 adaptation main labels, and 768 adaptation selection labels =3,328.
Total: **399,360 allocated outcome-label presentations**. A record with two
local effects and one composite outcome counts as three labels.
15 branch streams contain 49,920 generated labels, including repeated paired
acquisition; these are not independent evidence.

Count labels actually used for fitting, candidate construction or selection:
reopen 3,328/run, closed 2,560/run, frozen 1,024/run, flat 1,536/run;
total 253,440. Outcomes read only to score frozen predictions are evaluation,
not additional learner feedback. Shared acquisition is executed for every run,
including flat, rather than giving it cost-free learned parts.

Maximum main buffers are 192 records per local module and 192 composite
records. The largest upper table has 32 possible cells; lower tables have at
most two each. No archived growing dataset is available to learners. Full
output traces are for external audit. At most 11,520 local candidate fits
(a conservative 120 runs *12 reviews *2 modules *4 candidates) and 720 upper
candidate fits (30 reopen runs *8 reviews *3 modes). Count actual work.

Save protocol, implementation, tests and independent-audit hashes before the
benchmark, and verify all manifests from 010–012 unchanged. Refuse overwrite.
Use synthetic tests for grouping, transfer, boundaries, local-versus-upper
feedback isolation, lower remapping with frozen upper state, relevant reopening,
and evaluator purity. Independently reconstruct worlds and replay all learning
decisions and metrics. Report failure without tuning. Stop after findings;
no further experiment, scaling or meta-learning run is automatic.
