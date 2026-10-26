# Experiment 021: preserving a predictor before adaptation erases it

Specified 2026-10-26 before reserved-world generation. Test prospective memory
separately from 020's local protection. All local learning, ordinary upper
ranking, fresh-loss gates, interface reduction and dependency checks remain
the original integrated rules. Preserve all prior source and results.

## One-slot capture and preservation policy

The current policy captures the displaced predictor only when a reduction is
accepted, potentially after its fitting window has lost the earlier detail.
Compare it with the following bounded alternative:

* Before an ordinary upper review, after local reviews, nominate the current
  predictor if it has a raw port and its original fitted port meanings still
  match current meanings. Freeze its parameters, port fingerprint and main
  construction IDs before reading the upper selection labels.
* That frozen predictor must achieve loss <=.55 on two consecutive fresh upper
  selection batches. Current fitted counts continue adapting independently.
  A failed witness or incompatible meaning discards the pending snapshot;
  no replacement nominee uses that same batch.
* The first confirmed snapshot occupies the sole archive slot permanently for
  this run. It is installed after the ordinary review, so confirmation evidence
  cannot also deploy it. Later retrieval must pass the unchanged main-ranking,
  compatibility and fresh improvement gates. An incompatible archive stays
  stored but cannot compete. There is no oracle capture time or regime signal.
* Disable reduction-triggered overwriting of this slot. Record those displaced
  predictors as discarded audit events. No second confirmed memory is retained.

This changes a **capture-and-preservation policy**, not timing alone: early
nomination, corroboration and preservation against later eviction form the
specified intervention. It is deliberately limited and can reserve the wrong
predictor or fail to confirm one at all. These outcomes remain in denominators.

Three policies: `legacy` is the unchanged integrated learner; `reserve` uses
the alternative above; `discard` does identical prospective qualification work
but destroys the confirmed predictor and locks further nominations. The latter
has no deployable archive, isolating the benefit of retained parameters from
the qualification work. The protected-local policy from020 is not included.

## Paired worlds

Use the 018 generator with environment seeds1000–1004 and proposal seeds1000,
1001, retaining its RNG namespaces. Two histories: `detail` and `reversed`.
Acquire two local four-state forms on256 observations and four32-label reviews
each, then256 representative-only composition labels. Test transfer on24
unseen combinations. Adapt for1280 joint records with32-row reviews every64.
Noise remains independent10% label flips, and each joint row supplies two
local outcomes and one composite outcome.

Raw detail matters at1–240, disappears at241–528 and returns at529–1280.
`reversed` complements the entire detailed target on return. Local latent forms
stay fixed. Generate all main records before selection. Inputs, noise draws,
initial evidence and proposals are paired; the two histories share all evidence
through528. No reset, stage marker, truth or evaluation enters the learner.

60 runs =5 environments ×2 proposals ×2 histories ×3 policies. This is five
environment realizations, not ten independent pairs or two independent initial
histories. Report every run and environment aggregate. It tests these supplied
finite task families, not new-family generalization or meta-learning.

## Frozen outcome criteria

The primary memory target is observed composite loss over early return529–656.
Require reserve to improve mean loss by >=.02 nats and strictly improve >=8/10
detail pairs against EACH of discard and legacy. For each comparison, reversed
early-return mean cost must be <=.02. Also require mean observed and latent
pre-return cost (records1–528) <=.02 in each history and final full validity
>=8/10 for all three policies in both histories. Primary pass is their
conjunction; failure never triggers extra seeds or threshold changes.

Full validity requires all32 modal targets correct, expected Bernoulli(.9/.1)
loss regret <=.10 and both local partitions exact up to renaming. Separately
report transfer, final and stable late validity (every review1024–1280), and
appropriate sufficient/minimal interfaces using the existing oracle diagnostics.
Report observed/latent loss for pre-return, early return, full return529–1280,
and late1025–1280; raw reads; captures, confirmations, failed qualifications,
incompatible archive reviews and retrievals; complete online prediction equality
against discard. Late success cannot replace the early-return criterion.

For each candidate and confirmed archive, preserve construction IDs, nomination
and confirmation events, and immutable parameters. Report whether confirmed
snapshots actually contain pre-simplification records. Capture or retrieval
counts are mechanisms, not learning-benefit evidence. Oracle predictions and
losses never nominate or rank a memory. A useful archive here would not establish
general episodic memory, category invention or a safety advantage.

## Budget, contracts and audit

Exactly6784 used/allocated labels per run:407040 presentations;67840 generated
across10 worlds. At most19920 candidate fits,3000000 ranking/selection queries
including prospective qualification. Main composite predictions76800, local
153600; evaluation predictions45600; oracle context-query ceiling230400.
Existing buffer192, local pending, upper reduction and archive bounds remain.
Add one prospective pending predictor of at most16 cells; it is cleared on
confirmation, failure or incompatible meanings. The archive remains one slot
of at most16 cells. Qualifying selection reuse is declared in the evidence
ledger; construction IDs must be main evidence only. Schema21 wraps the
complete core checkpoint with policy, pending snapshot and qualification costs.

Synthetic fixtures use seed2990 or hand-built records, capped at2500 charged
generation/use labels. Save fixture attempts; freeze a passing record and all
runtime, driver, metrics, auditor and prior dependency hashes before seed1000
generation. Benchmark and independent audit each have a600-second limit.
Persist worlds, traces and complete checkpoints progressively; preserve any
engineering/resource failure as incomplete. Independent replay reconstructs
all state and decisions without importing runtime or experiment code. No
benchmark tuning, rerunning, larger architecture or real-world connection.
