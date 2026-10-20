# Experiment 011: coverage helps; corroboration can obstruct discovery

Completed 2026-10-20. This follow-up separates two responses to
[Experiment 010](../bundles-v1/findings.md): retaining random proposals while
reducing repeated omissions, and requiring corroboration before structural
revision. It uses fresh environment and proposal seeds, with the same model
capacity and per-learner observation and candidate budgets.

**The combined primary criterion failed.** Shuffled-deck proposals with the
split-evidence gate passed 6/10 changing-world runs and 9/10 persistent-world
runs. At least 8/10 were required in each branch.

Coverage improved, but the stronger acceptance gate did not establish a
retention benefit in this sample. It sometimes blocked useful discoveries.
This is a fixed follow-up result, not justification for adjusting the gate
until the benchmark passes.

## The factorial comparison

Each learner proposes four candidates per review. Independent sampling may
repeat candidates before visiting others; a deck visits its shuffled list
before reshuffling. The single gate uses all 32 fresh selection outcomes.
The split gate requires positive penalised gains in both independent
16-outcome halves of that same batch. Neither gate has extra data.

| Proposal / acceptance | Changing-world passes | Persistent-world passes | Mean main loss: changing | Mean main loss: persistent |
| --- | ---: | ---: | ---: | ---: |
| Independent / single | 3/10 | 7/10 | 0.548178 | 0.465743 |
| Shuffled deck / single | 7/10 | 10/10 | 0.532717 | 0.409042 |
| Independent / split | 3/10 | 6/10 | 0.543877 | 0.487944 |
| Shuffled deck / split | 6/10 | 9/10 | 0.540538 | 0.425060 |

Passes require correct feature choices and predictive quality at all three
endpoints, plus predictive input-cut effects at the pair endpoints.
Persistent passes additionally require that the correct pair is never replaced
after successful acquisition. This stronger preservation requirement means
the pass fractions are not directly interchangeable with Experiment 010's.

Main loss is measured before feedback throughout each trajectory. The deck's
mean improvements were not uniform: with the single gate it lowered main loss
in 5/10 paired changing-world runs and raised it in the other five. In the
persistent branch it lowered loss in five, tied in two, and raised it in three.
These are descriptive results from five environments crossed with two
proposal seeds, not a significance claim or multiple task families.

## What improved: coverage

Both deck variants visited the entire 22-subset pool during the first six
reviews, counting candidates and the incumbent. Independent schemes visited
about 74% on average. The relevant pair was reached in 10/10 initial phases
with decks versus 7/10 with independent sampling.

In the returning-pair phase, the relevant pair was reached in 9/10 reversible
runs with either deck gate, versus 8/10 with independent/single and 9/10 with
independent/split. In persistent worlds, a previously learned incumbent also
counts as covered: this is not always a fresh proposal.

Decks do not reset at world changes. Completing each shuffled traversal
therefore does not guarantee revisiting a newly useful candidate within every
phase. In environment 104, proposal seed 101, both deck variants end the
returning-pair phase with an empty subset and 50% most-probable-outcome accuracy.

The result supports investigating memory of search coverage as a way of
organising stochastic variation. It does not establish an advantage over
deterministic coverage, which was not included in this factorial follow-up.

## What was not established: protection from misleading evidence

No variant discarded a successfully acquired pair in these persistent-world
runs. The independent variants each had one run that never acquired the pair;
that run is not counted as protected. The absence of harmful revisions among
the remaining runs leaves no observed retention failure for the split gate
to prevent.

The split gate instead vetoed a correct pair proposal once in each proposal
scheme's persistent runs:

* Independent/split, environment 100, proposal seed 100, review 256: the
  half-batch gains were approximately +0.5023 and -0.0376 nats.
* Deck/split, environment 104, proposal seed 101, review 64: the gains were
  approximately -0.2024 and +0.3465 nats.

Both pooled gains were positive. In the deck case, vetoing the early proposal
left the learner without the useful pair at the first endpoint; it acquired
the pair later. The gate cannot distinguish a useful discovery from harmful
forgetting merely by requiring agreement between two small noisy samples.

In persistent worlds the split gate raised mean main loss for both proposal
schemes. Within each scheme, nine paired trajectories had identical main loss
and one was worse under the split gate. No protective benefit was demonstrated.
This is not evidence that corroboration is never useful; a targeted comparison
with controlled transient corruption and genuine changes remains open.

## Simplification remains distinct from prediction

The deck/single learner failed three reversible runs: two retained an
unnecessary feature at the middle endpoint, and one missed the returning pair.
The deck/split learner failed four: three retained unnecessary middle-phase
detail, and one failed the initial and returning pair endpoints.

The middle-phase failures still predicted the most probable outcome correctly
for every context/action. Their expected log losses were 0.337062–0.356294,
close to the 0.325083 noise oracle. Keeping an unnecessary coordinate can
therefore be predictively adequate while failing the explicit simplification
goal. Rejecting structural change too readily may preserve that excess detail.

The test still uses joint feature tables and a supplied subset language.
Prediction ignores unselected features, while all six observations remain in
the search buffer. It does not learn an interface, reduce sensing, or learn
the proposal or acceptance rules.

## Verification and budget

Six new synthetic tests passed, covering deck traversal and shuffle boundaries,
split-gate decisions, evidence isolation, evaluation isolation, and detection
of a transient departure despite endpoint recovery.

The independent audit imported no learner code. It replayed all 80 runs,
including fresh world RNG streams, proposal RNG/decks, fitted counts,
pre-feedback predictions, half-batch decisions, evaluations, ablations,
continuous-preservation metrics, paired comparisons, and costs. It passed.
The Experiment 010 manifest was also verified unchanged.

The benchmark ran once without tuning or post-result source corrections:

* 138,240 allocated and used outcome-bearing presentations.
* 17,280 generated records across ten paired world streams.
* 184,320 base evaluation predictions and 264,064 additional ablation calls.
* 5,760 candidate fits; all refitting and feature-access costs are in the report.

Five fresh feature permutations gave five different relevant pairs. Branches
share random draws; learners share world streams; two proposal seeds do not
double the number of environments.

## Consequence for the programme

The result favours coverage-aware stochastic proposals in this bounded task,
while leaving the split gate unsupported. The combined mechanism is not yet a
reliable solution to acquire–simplify–reacquire.

The next unresolved design question is whether creating a possibility,
temporarily hiding it, and deleting it should have different retention
mechanisms and evidence requirements. This is relevant to the user's interface
and information-hiding enquiry, but it is a hypothesis for a separately fixed
experiment, not a finding of this one.

This experiment is complete. Folds, temporal Markov interfaces, and
meta-learning remain untested. No further benchmark was run automatically.

## Records

* [Fixed protocol](../../experiments/bundle_retention_protocol.md)
* [All-run report](report.md)
* [Metrics and paired comparisons](metrics.json)
* [Complete streams and traces](results.json)
* [Pre-run source hashes](manifest.json)
* [Implementation](../../experiments/bundle_retention.py)
* [Synthetic tests](../../checks/test_bundle_retention.py)
* [Independent audit](../../checks/audit_bundle_retention.py)
