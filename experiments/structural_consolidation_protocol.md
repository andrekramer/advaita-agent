# Experiment 018 / C2: continuing structural learning

Design fixed before reserved-seed execution, 2026-10-23. C1's independently
verified immediate/reclosure reference passed the progression gate. Preserve
all C0/C1 source and results. This experiment uses new files and the shared
conditional tables, restricted views and evidence contracts.

## Worlds and pairing

Environment seeds 700–704; proposal seeds 700,701. RNG namespaces: layout
91000+environment, inputs 92000+environment, outcome noise 93000+environment,
local proposals 94000+2*proposal+j, upper proposals 95000+proposal.
Use the 013 acquisition curriculum: 256 balanced observations per lower
module, four 32-label local reviews, 256 upper labels on representative/action
combinations. Local acquisition uses the unchanged immediate rule. Transfer
is evaluated on the other 24 combinations. All acquisition histories are
paired; failed acquisitions remain in denominators.

Adapt continuously for 768 records, reviewing every 64 on 32 fresh balanced
contexts. Three outcomes per record: two local and one composite. Independent
10% bit-flip noise throughout. Phase boundaries follow records 240 and 528,
between reviews; each selection batch uses the regime at its review index.
The learner receives observations and review calls, never a regime signal.
Layout, input order and noise draws match across histories/variants. Generate
main data before selection; local draws precede each composite draw.

* `forms`: original local forms/XOR-with-action for records 1–240; affected
  local effect becomes constant zero and its upper dependency disappears at
  241–528; original forms and relationship return at 529–768.
* `detail`: affected raw detail matters at 1–240, disappears at 241–528,
  returns at 529–768. Local forms remain original. The detailed target is
  original XOR-with-action XOR whether the affected raw state differs from
  the representative of its local group.
* `reversed`: identical to `detail` through 528; the entire detailed target is
  complemented after 528. Local forms remain unchanged.

## Learner and supplied choices

Two lower four-state modules; fixed binary action. Upper input specification
is a pair from {0=absent,1=group,2=raw}, excluding (2,2) except in the raw control.
The action is always included. Conditional counts use the shared Beta(1,1)
estimator. A missing input contributes no key coordinate. Prediction views
permit only the selected ports. Architecture and candidate language are fixed.

After upper initialization, local reviews reserve one of four proposal slots
for the collapsed partition when the incumbent has two groups; the other
three come from the existing shuffled partition deck. A collapsed incumbent
gets four split proposals. Rank non-reducing proposals by last-64-main loss,
then group count and partition; immediate acceptance requires fresh gain >.005.
Otherwise consider the frozen collapsed challenger: two consecutive fresh
batches with loss <=.55 and disadvantage <=.02 against the live incumbent.
Ordinary accepted improvement clears pending reduction; a failed witness clears
it. Main counts still update. This is an explicit extension of C0's local rule.

Upper reviews draw four non-incumbent specifications from a shuffled deck of
all eight allowed specifications and add every strict coordinatewise reduction
of the current specification. Deduplicate; at most seven fits per review.
This reserves reductions while retaining stochastic coverage of joint changes.
Fit on the 192-row main buffer. Rank non-reducing fitted candidates and an
eligible archive by main-buffer loss, then number of cells, number of raw
ports, lexicographic specification, then fitted before archive on an exact tie.
If no non-reducing candidate is available, skip ordinary replacement.
Only that winner is otherwise tested for ordinary replacement: incumbent fresh loss >.55
and fresh gain >.02. No selection labels enter fitting or ranking.

If ordinary replacement is not accepted, review one frozen reduction. Start
with the smallest main-adequate candidate (main loss <=.55), ordered by cells,
raw-port count, main loss, specification. If none is main-adequate, start none.
Require two consecutive fresh adequate witnesses (loss <=.55, disadvantage
<=.02). A changed fingerprint of its consumed ports invalidates pending
comparison. Ordinary acceptance has priority and clears pending reduction.
Local reviews precede upper preparation. Reuse of the same selection labels
for improvement/reduction decisions is declared in the ledger.

Upper predictors containing raw ports refit after each main update; group-only
or absent-port predictors stay frozen until accepted replacement/reduction.
Local meaning changes may leave a deployed upper predictor stale; record this
without granting an automatic repaired fit. Frozen reduction candidates and
archived tables never update.

On accepted coordinatewise reduction, capture the displaced upper predictor,
its ORIGINAL fitted input-meaning fingerprint, construction IDs and capture
event, replacing a single previous entry. Capture is not at a world boundary.
The archive competes only if its consumed port meanings match current meanings
and its specification is not a reduction of the incumbent. It is scored on
main data and competes for fresh improvement evidence as described above.
A new revision with restored meanings is compatible; matching numeric labels
with changed membership is not. Acquisition and reduction timing are supplied
rules; memory quality at capture is an empirical question.

## Controls

`integrated`: immediate local improvement plus adequate reduction, upper
revision/reduction, one retained archive.
`delete`: identical structural rules but discard the displaced predictor;
no fitted archive parameters remain available to prediction or search. Audit
events can retain historical tables in every variant; learners never read them.
`raw`: same allocated curriculum, raw/raw upper from initialization, refitted
on every main record; no adaptive local updates or reviews and no upper search.
`fixed`: freeze lower partitions after acquisition but update their counts;
no adaptive local selection; upper learning and archive as in integrated.

All are continuing states without resets or selected checkpoint restoration.
Allocated feedback is matched, actual use and computation are reported.
Raw uses 1,792 labels/run, fixed 3,712, integrated/delete 4,480 each.

## Evaluations and frozen criteria

Evaluate after main records 240,528,768 and at ordinary reviews, with no learner
mutation. Full predictive validity: all 32 modal targets correct, expected
Bernoulli(.9/.1) log-loss regret <=.10. Local partition exactness is assessed up
to group renaming; separately report exported effect-label alignment and audit
fingerprints using actual maps. Full validity requires exact local partitions
and valid upper prediction, not an assumed orientation of arbitrary group IDs.
Transfer uses 24 unseen compositions and the original forms.

Endpoint sufficient/minimal interface: forms history uses group/group at 240
and 768, absent affected/group other at 528; detail histories use raw affected/
group other at 240 and 768 and group/group at 528. At each endpoint independently
compute the oracle conditional-entropy risk for the visible partition: risk
regret <=.10, removal of each selected module worsens risk by >.02, and adding
raw information to each non-raw port improves risk by <=.02. These diagnostic
counterfactuals are not learner feedback and do not establish causal discovery.

A complete integrated trajectory requires transfer validity and all three full,
minimal, sufficient endpoints with the declared specifications. In forms,
require an actual local collapse during 241–528 and recreation after 528,
and an upper dependency removal during 241–528 and restoration after 528.
In detail/reversed, require an accepted exposure reduction with capture during
241–528 and later reopening after 528. A reduction is the capture trigger even
if the captured predictor proves useless. Require >=8/10 complete integrated
trajectories separately in EVERY history.

Separate memory targets: integrated versus delete observed composite loss over
records 529–656 improves by >=.02 nats on mean in `detail`, with strict
improvement in >=8/10 paired runs; reversed-return mean cost <=.02 over the same
window. Report latent expected losses alongside these criteria. Integrated
must have lower mean parent raw reads than raw control during 241–528 in every
history. Primary pass is the conjunction of all trajectory, memory and read
criteria. No post-result redefinition. Report acquisitions, structural failures,
archive eligibility/acceptance/eviction, stale bindings, all variants and pairs.

## Resources, provenance and stop rules

120 runs: 5 environments ×2 proposals ×3 histories ×4 variants. Exactly
537,600 allocated label presentations, 433,920 actually used; 67,200 generated
labels including paired histories. This is the remaining planned benchmark,
not an increase. At most 17,160 candidate fits (C1+C2 <=47,040); buffers192;
at most two local pending tables (one cell each), one upper pending (<=8 cells),
one archive (<=16), deployed upper<=16 except raw32. Count table maxima and
all scoring/refit work separately. Candidate/selection probability-query ceiling
3,000,000; main queries 92,160 composite, 138,240 local for the three local-
updating variants; upper evaluation 60,480 predictions (24 +15×32 per run),
including separately recorded endpoint768 even when it coincides with review.
Oracle-risk enumeration is bounded by five 32-context calculations per
evaluation, at most307,200 context queries over 1,920 evaluations; count actual
queries from the saved removal/addition dictionaries. Local map diagnostics
compare the fixed four-state membership maps, not labelled feedback. Audit reuses saved evidence.

C0+C1 charged19,216 of20,000 fixture labels. C2 fixtures charge at most720,
using only synthetic seed990 and deterministic small records; do not rerun the
suite silently or search seeds. Record fixture timing before freezing.
Wall-clock limits: 600 seconds for benchmark and 600 for independent audit.
A resource or correctness failure leaves an incomplete record with preserved
outputs. Freeze protocol, runtime, driver, metrics, tests, auditor and dependency
hashes before generating any reserved world. No tuning or additional runs after
empirical failure. A negative result can complete the bounded round but cannot
be relabelled successful consolidation. No live-world connection or scaling.
