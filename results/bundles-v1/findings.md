# Experiment 010: useful relationships, unreliable random discovery

Completed 2026-10-20. This is the first experiment of the new round,
**learning distinctions → learning relationships → learning interfaces →
learning how to learn**. It is separate from the earlier experiment directory
named `round2-v1`.

**The predeclared primary criterion failed.** The stochastic learner passed all
endpoint requirements in 5/10 reversible runs and 7/10 persistent runs. The
requirement was at least 8/10 in each branch. Deterministic search, with the same
four-candidate review budget, met the same endpoint checks in 5/5 environments
in each branch. This run does not support an advantage for random proposals.

The results nevertheless demonstrate a limited capability: joint conditioning
on a learned pair of supplied distinctions can support noisy action-outcome
prediction, and the selected representation can lose and regain a member.
This is feature-subset structure learning, not a general relational learner.

## What was tested

Six binary observed features, a binary action, and 10% independent outcome
flips. The useful relation initially depends on two features jointly. Neither
feature alone predicts the outcome in that phase. In the reversible branch,
only one feature matters during the middle phase; the pair dependency then
returns. In the persistent control, the pair remains useful throughout.

Learners receive no relevant-feature identities, world-change signals, or
noiseless targets. All start without a selected feature except the fixed
full-context control. The environment supplies random observations, actions,
and outcome errors. Internal randomness is confined to bounded candidate
generation; selection uses fresh outcomes and a fixed complexity penalty.

The four variants are stochastic subset proposals, deterministic cyclic
proposals, stochastic single-feature-or-empty proposals, and a fixed
six-feature table. The singleton control is not a general additive or neural
baseline. The full table has more parameters and sparse counts; it is not a
capacity-matched alternative architecture.

Five environments are crossed with two proposal seeds for stochastic variants.
Deterministic and full-context controls run only once per environment/branch.
There are five distinct feature permutations but only four distinct unordered
relevant pairs; seeds 0 and 1 both use pair {0,1}. The branches reuse noise and
input draws. Neither the 60 runs nor the 20 stochastic runs are independent
task families.

## Prediction and relationship use

Expected future log loss at phase endpoints, averaged across the relevant runs:

| Branch | Learner | Initial pair | Middle phase | Final pair |
| --- | --- | ---: | ---: | ---: |
| Reversible | Stochastic | 0.410547 | 0.335205 | 0.412981 |
| Reversible | Deterministic | 0.338195 | 0.333527 | 0.340098 |
| Reversible | Singleton-limited | 0.698647 | 0.333527 | 0.695660 |
| Reversible | Full context | 0.533203 | 0.523596 | 0.527681 |
| Persistent | Stochastic | 0.410547 | 0.341285 | 0.378014 |
| Persistent | Deterministic | 0.338195 | 0.341285 | 0.340098 |
| Persistent | Singleton-limited | 0.698647 | 0.699474 | 0.695660 |
| Persistent | Full context | 0.533203 | 0.523596 | 0.527681 |

The noise-aware oracle loss is 0.325083 nats. These are evaluator-only expected
losses over all contexts/actions under the known noisy distribution. They
measure predictive quality on future draws, not transfer to unseen contexts,
new task families, or novel perceptual primitives.

All deterministic runs select the right pair, single, pair at reversible
endpoints and the right pair at persistent endpoints. They predict the most
probable outcome correctly for every evaluated context/action at those times.
This does not mean 100% accuracy on realised noisy outcomes.

At the two pair endpoints, deterministic joint models improve expected loss
over their paired singleton controls by 0.347835–0.377189 nats. Cutting either
relevant input by averaging its two values raises expected loss by
0.348680–0.359695 nats. This verifies joint predictive use. The cut is a frozen
predictor ablation, not a causal intervention in the environment.

## Why stochastic runs failed

The saved traces separate several failure modes:

* **Missing a useful proposal.** In environment 2, neither proposal seed
  proposes the relevant pair {1,2} during either pair phase of the reversible
  branch. Their first-phase model remains empty and their final models use
  irrelevant or incomplete subsets. The available observations cannot improve
  a model that search never proposes. This is a bounded coverage failure, not
  evidence that the relationship is unlearnable.
* **Predicting correctly while retaining unnecessary detail.** Four reversible
  runs finish the middle phase with a pair containing the useful feature and
  a nuisance feature, rather than the required singleton. All four have 100%
  most-probable-outcome accuracy and expected loss between 0.331780 and
  0.337356. They fail the simplification criterion, not prediction at that
  checkpoint. This is why prediction and selective ignorance are measured
  separately.
* **Discarding useful structure on misleading evidence.** In environment 1's
  persistent branch, the selection batch at review 832 contains 10 flipped
  outcomes out of 32. Both stochastic learners replace the correct pair with
  a wrong pair, and the deterministic learner replaces it with an irrelevant
  singleton. The world has not changed. Stochastic proposal seed 1 restores
  the correct pair by review 896; deterministic search restores it at review
  1152. Stochastic proposal seed 0 does not restore it before the run ends.

The deterministic endpoint successes therefore do not demonstrate continuous
preservation. The transient failure under noise remains visible even though
the final criterion passes. A single noisy selection batch and the current
retention rule do not reliably distinguish environmental change from noise.

Mean pre-feedback main loss is also lower for deterministic than stochastic
search in both branches: 0.508781 versus 0.555861 in the reversible world, and
0.421563 versus 0.436626 in the persistent world. Random proposals sometimes
discover earlier, but this fixed run does not show an overall benefit.
This comparison concerns these two proposal schemes, not randomness in
learning in general.

## Information hiding: what this does and does not show

Prediction reads only the selected feature coordinates. Synthetic tests use an
input object that raises an error if an unselected feature is accessed.
Structural selection can therefore determine which observations the deployed
predictor ignores.

Over main predictions, stochastic learners read an average of 1.238889 features
in the reversible branch and 1.522222 in the persistent branch, versus six for
the full-context table. Deterministic means are 1.422222 and 1.600000. These
counts exclude the action, which every predictor receives.

Lower read counts are not inherently better: missing the useful pair can
also reduce reads. All six feature values remain sensed and stored in a
192-record buffer. Fitting and proposal search inspect that buffer; their
separate access costs are recorded. There is no claim of reduced sensing,
raw-data storage savings, a learned fold, or autonomous investigation.

This establishes a modest starting point for the interface enquiry: selecting
which distinctions participate in prediction is learnable, but the access
mechanism itself is constructed. Hiding an internal trajectory behind a
learned interface remains a different experiment.

## Verification, resources, and stopping

Eight synthetic tests passed before execution. The independent audit imports
no learner code and reconstructed all 60 traces: world RNG streams, counts,
pre-feedback predictions, candidate sampling/cycling, rankings, selection
decisions, frozen evaluations, ablations, summary metrics, budgets, and source
hashes. It passed. No benchmark rerun, tuning, or post-result source correction
was needed.

The run used 103,680 allocated outcome-bearing presentations, of which 97,920
were used by the algorithms. There were 17,280 generated records across paired
world streams, 138,240 base evaluation predictions, 261,632 additional ablation
predictions, and 3,600 candidate fits. Pairing and repeated use by different
learners are explicitly accounted for; these are not independent samples.
The report contains full fitting/search and feature-access costs.

This experiment is complete. The broader next round has begun but is not
complete. Its immediate unresolved questions are proposal coverage, evidence
for retention under noisy challenges, and reliable removal of unnecessary
distinctions. No new benchmark or parameter adjustment is authorised by these
findings. Folds, Markov interfaces, and meta-learning remain conditional stages
in the plan.

## Records

* [Fixed protocol](../../experiments/bundles_protocol.md)
* [Next-round plan](../../experiments/next_round_plan.md)
* [All-run report](report.md)
* [Metrics and costs](metrics.json)
* [Complete paired streams and traces](results.json)
* [Pre-run source hashes](manifest.json)
* [Implementation](../../experiments/bundles.py)
* [Synthetic tests](../../checks/test_bundles.py)
* [Independent audit](../../checks/audit_bundles.py)
