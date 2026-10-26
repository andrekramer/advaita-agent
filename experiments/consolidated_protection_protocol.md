# Experiment 020: preserving established forms without blocking change

Specified 2026-10-26 before reserved-world generation. New bounded experiment
following 019. Preserve earlier source, protocols and results. No tuning or
additional seeds follow empirical failure.

## Fixed intervention

Compare the unchanged integrated `StructuralLearner` with `CorroboratedLearner`.
The upper proposal, reduction, raw-interface, dependency and archive rules are
identical. All acquisition decisions are identical and remain immediate.
After upper initialization, each local form earns protection after two reviews
without accepted replacement and with incumbent loss <=.55. Protection latches
until an accepted replacement; poor evidence resets the adequacy counter but
does not remove already earned protection. Truth never determines protection.

For an unprotected form, ordinary fresh gain >.005 is accepted immediately.
For a protected form, that same ordinary replacement becomes a frozen pending
challenger. At the next review it must again beat the live incumbent by >.005
on a fresh selection batch. Success adopts the frozen model; failure discards
it. That review never falls through to a different replacement. Current counts
continue updating while the challenger stays frozen. Acceptance resets earned
protection and adequacy. Existing collapse proposals already require two
witnesses; preserve that rule without adding another confirmation layer.

Implementation runs the baseline local search and records its hypothetical
decision on every review, consuming the same RNG/candidate work. A pending
ordinary revision takes precedence over that hypothetical result. Starting or
resolving it clears the pending collapse; discarded work still counts. No
hypothetical change reaches the upper learner. Exported-group revision counters
reflect actual adopted states only. Protection concerns replacement decisions;
it does not freeze count updates or guarantee fixed exported numeric meanings.
Checkpoint schema20 wraps the complete schema2 core with both protection states
and costs. Separate fresh selection IDs and declared reuse are audited.

## Worlds, pairing and scale

Reuse the 017 generator with environment seeds900–904 and its existing RNG
namespaces. Local proposal seeds are 94000+2*p+j and upper seed95000+p for
p=900,901. Three histories use identical layouts, inputs and noise draws:

* `persistent`: stable local forms and composite XOR-with-action throughout.
* `burst`: records129–192 provide misleading labels only to the affected local
  channel; latent forms and composite outcomes do not change.
* `remap`: after128 the affected local form changes permanently and composite
  outcomes follow it. Flip the two representative memberships as in017.

Acquisition: 256 main labels per local node, four32-label local reviews, then
256 representative-only composition labels. Evaluate transfer on24 unseen
compositions. Continue for1280 main records, reviewing every64 on32 fresh joint
rows. Independent10% label noise. Each joint row supplies two local labels and
one composite label. Generate all main rows before selection rows. No change
markers, reset, truth, evaluations or selected checkpoint restoration reach
the learner. All acquisition failures remain in denominators.

60 runs: 5 environments ×2 proposal seeds ×3 histories ×2 policies. Ten paired
runs per condition represent five environment realizations, not ten independent
environments. Report all pairs and environment aggregates. These are the same
finite task families, not a test of new-family generalization or meta-learning.

## Metrics and frozen decision criteria

Evaluate every review plus records128,192,320,512,1280 (endpoint evaluations
are separately recorded even when they coincide with reviews). Modal composite
accuracy must be1 and Bernoulli(.9/.1) loss regret <=.10 for predictive validity.
Full validity additionally requires exact local partitions up to renaming;
report exported effect-label alignment separately. Appropriate structure also
requires group/group, oracle sufficiency and minimality. Report stability over
every review1024–1280, actual local replacements, harmful correct-to-incorrect
replacements, incorrect establishments, raw reads, and pre-step raw bypass of
an incorrect local partition. These are evaluation-only diagnostics.

Affected-local error checkpoints: persistent reviews192–1280; burst192–512.
For EACH condition, baseline must have nonzero errors; protection must reduce
their total by >=25% and strictly improve >=2/10 pairs. A zero-error baseline
leaves benefit untested and does not pass that criterion. Also report both-node
errors and late errors separately, so the affected-node focus cannot conceal
damage elsewhere.

Require BOTH policies to have transfer and final full validity >=8/10 in each
history. Primary protection success additionally requires:

* Persistent: mean protected-minus-baseline composite observed, composite latent
  and affected-local latent loss costs <=.02 over all1280 main records.
* Burst: composite and affected-local latent costs <=.02 over129–320, alongside
  the error benefit above.
* Remap: mean composite observed, composite latent and affected-local latent
  costs <=.05 over129–512. First pair of consecutive fully valid post128 reviews
  defines confirmed recovery; use the second review time. Preserve null for
  unconfirmed runs; assign1344 only for the mean delay comparison. Mean added
  confirmation delay must be <=64 records.

Primary pass is the conjunction of all these criteria. Stable appropriate
interfaces and retained-memory events are reported separately, not silently
included or dropped from that criterion. A local-protection pass would not by
itself establish reliability of the complete combined learner. No significance
claims from these small dependent samples.

## Resources, fixtures and verification

Exactly6784 used/allocated labels per run: total407040 presentations;101760
generated across15 paired worlds. At most19920 candidate fits: acquisition32
per run plus20×(8 local+7 upper). Scoring-query ceiling3000000, including extra
confirmation queries. Main composite predictions76800, local153600; evaluation
predictions49440; oracle context-query ceiling249600. Buffer192 and original
pending/archive limits remain; additionally at most two pending revision models
of two cells each. Record actual costs and all provenance.

New synthetic fixtures use only seed1990 or hand-built records, capped at2000
charged generation/use labels. Save every attempt, including corrections before
freezing. Freeze protocol, runtime extension, driver, metrics, tests and separate
auditor plus all earlier dependency hashes before generating seed900. Benchmark
and independent replay each have a600-second wall-clock limit. Persist worlds,
full traces and checkpoints progressively. Resource or correctness failures
leave incomplete records; empirical failures complete the bounded experiment.
No real-world connections or larger architecture. Memory-capture redesign is
outside this experiment.
