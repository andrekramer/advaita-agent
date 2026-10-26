# Experiment 019: fresh-world replication and extended recovery

Specified 2026-10-26 before reserved-world generation. This is a new bounded
test round of the unchanged consolidated learner, not a continuation of C2's
budget or a repair of its policy. Preserve all earlier code, protocols and
results. No threshold, candidate language, memory rule or parameter changes.

## Questions and fixed comparisons

1. Do prediction and structural findings recur on fresh simulator seeds?
2. Does more experience after return produce a stable, sufficient and minimal
   representation, or only correct predictions with unnecessary exposure?
3. Does retained memory help during return, compared with deleting it?

Use the existing 018 generator, runner and independent reference interpreter.
Environment seeds 800–804, proposal seeds 800 and 801; retain their existing
RNG namespaces. Five environments with two proposal draws each give ten paired
runs per history/variant, not ten independent environments. Report all pairs
and environment means. These are new realizations of the same task families,
not evidence of generalization to a new family.

Use `forms`, `detail`, `reversed` and all four existing controls: `integrated`,
`delete`, `raw`, `fixed`. The acquisition curriculum and 10% label noise remain
unchanged. Main records 1–240 use the initial regime, 241–528 simplify it, and
529–1280 restore it (or reverse the detailed target). Thus only the final
regime lasts longer: 752 rather than 240 records. Review every 64 on 32 fresh
contexts, for 20 reviews. Boundaries are never supplied to the learner.

Each world is generated once, with all 1280 main records preceding selection
generation. This changes the random selection-stream position relative to a
separately generated 768-record world. The first-768 analysis is a fresh
distributional replication, not a literal replay or an independently randomized
short-duration treatment. All variants share exactly the same world and
proposal seeds. Detail/reversed histories share experience through record 528.
No reset, retrospective checkpoint selection or early stopping on success.

## Frozen evaluations and criteria

Reuse the 018 full enumeration of 32 contexts, latent Bernoulli(.9/.1) loss,
oracle information sufficiency/minimality and exact local partitions up to
renaming. Transfer uses the 24 unseen compositions. Truth and oracle queries
are evaluation only. Keep first-768 metrics under `reference_768`; they do
not include later evidence or replace the earlier published results.

Report checkpoints 768, 1024, 1280 separately. Predictive validity requires
all modal targets correct and expected-loss regret <=.10. Full validity also
requires exact lower partitions. Structural validity additionally requires a
sufficient/minimal interface and the expected specification: group/group for
forms after return, affected raw/other group for detail and reversed.

The primary representation criterion is transfer validity plus structural
validity at EVERY one of reviews 1024,1088,1152,1216,1280. Require >=8/10
integrated runs separately in each history. Report prediction-only and full
validity over the same five reviews separately; a single final success does
not establish stability. Report first-768 complete trajectories and endpoint
counts unchanged, including acquisition failures in all denominators.

The separate memory criterion uses observed composite loss over ALL return
records 529–1280: delete minus integrated mean >=.02 nats in detail, strict
gain in >=8/10 pairs, and mean reversed-return cost <=.02. Also report latent
loss, the original early-return window 529–656 and late window 1025–1280,
complete prediction-sequence equality, archive captures and retrieval counts.
Do not call memory useful solely because it was captured or selected.

Report raw-input reads during the late window, and paired savings relative
to the raw control. This is a resource diagnostic, not an added success gate.
Record capture times and construction-ID ranges, including whether a snapshot
captured during simplification contains any pre-simplification evidence.
These are provenance diagnostics, not an oracle intervention or causal test.
No p-values or population claims from the small, dependent seed sample.

## Bounded resources and audit

120 runs = 5 environments ×2 proposals ×3 histories ×4 variants. Per run:
6784 used labels for integrated/delete, 5504 fixed, 2304 raw. Allocation is
814080 presentations; actual use 641280; 101760 generated labels across 15
worlds. Each world supplies 512 local-main, 256 local-selection, 256 composition,
3840 joint-main and 1920 joint-selection labels. No extra benchmark seeds.

Ceilings: 26040 candidate fits (including acquisition), 5000000 selection/
ranking probability queries; 153600 main composite, 230400 local predictions,
91200 evaluation predictions. At most 460800 oracle context queries; count
actual queries from saved evaluations. Existing buffer192, pending and archive
bounds remain unchanged. Limit benchmark and independent audit to 600 seconds
each. Persist each world, run and full checkpoint, and keep incomplete records
on engineering/resource failure. An empirical failure completes the round
without tuning or rerunning it.

Harness tests use fabricated summaries and saved evidence, with no new learning
labels and no reserved worlds. Freeze source/dependency hashes and a passing
fixture record before generating seed800. The audit independently reconstructs
worlds, every learning step and checkpoint using the existing separate reference
implementation; independently recompute the new metrics and summary too.
Audit replays are not new learning evidence. Inspectability, reliable general
learning, meta-learning and safety advantages are not established by this test.
