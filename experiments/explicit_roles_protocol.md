# Experiment 024: explicit roles versus timing, updating and history controls

Specified 2026-10-28 before reserved seeds. The [plan](explicit_roles_test_plan.md)
and [R0 contract](explicit_roles_spec.md) define scope. R0 must pass first.
No change to prior benchmarks, thresholds or artifacts is permitted.

## Policies and observations

B64 and B128 preserve original predictive behavior, reviewing structure every64
or128 main records. U64/U128 refit all upper tables at every observation, with
original probability-ordered local exports. R128 adds stable export ownership;
H128 additionally uses the declared bounded adaptation-history proposal rule.
All acquisition reviews occur every64, unchanged:256 main plus128 selection
labels per local module, then256 representative-only composite labels. Each
policy receives1280 main joint records with two local labels and one composite
label. Allocate32 joint selection rows every64. The128 policies use only current
batches at multiples of128, never skipped labels or pooled batches.

Use seeds1200–1204 and proposals1200,1201, five histories and six policies:
300 runs. Proposal seeds remain94000+2*p+j locally and95000+p above. The original
four-state binary partitions and upper specifications are unchanged. All failed
acquisitions stay in denominators. Five layouts with two proposal draws are
five environmental realizations, not ten independent worlds.

## Exact simulator

Use layout RNG151000+seed, input RNG152000+seed. Draw one shuffled four-state
partition per local node, representatives from the two halves, then affected
node as before. Separate flip RNGs153000+seed (local0),154000+seed (local1),
155000+seed (composite). Each draw flips the latent binary target with probability
.1, exactly once. Generate all acquisition, then main, then selection records;
selection uses the regime at its review index. Histories share streams where
possible. No labels are generated from predictions.

Let f_j(x_j) be the original group, a the action, and j the affected node.
At acquisition time0 all local targets are f_j, and the composite target is
f_0 XOR f_1 XOR a. Main regimes are1–240,241–528,529–1280.

* stable: same targets throughout.
* probability: in the middle regime invert the affected local binary target
  and the composite binary target; restore both afterwards. The two local
  equivalence classes and sufficient group/group interface remain unchanged.
  This changes probabilities (.1 versus .9) and their order, not the partition.
* forms: in the middle regime the affected local target is0 for every state;
  omit its term from the composite XOR. Restore afterwards.
* detail: outside the middle regime, XOR the composite with the indicator that
  x_j differs from its group's acquisition representative. Locals stay fixed.
* reversed: same as detail, but also complement the composite after528.

No additional noise or intermediate probabilities are introduced. Targets are
known only to simulation/evaluation. Semantic label alignment is reported
separately from equality of local partitions up to renaming.

## Evaluation and fixed gates

All variants are evaluated, without state changes, on the common64 grid after
any scheduled review, plus boundaries240 and528. Transfer uses the24 unseen
compositions immediately after acquisition. Other evaluations enumerate32
contexts. Accuracy1 and latent Bernoulli(.9/.1) loss regret<=.10 give predictive
validity. Full validity additionally requires correct local partitions.

Structural appropriateness requires correct local partitions and an oracle
sufficient/minimal selected interface: optimal encoded-table regret<=.10;
removing any included port costs>.02, and upgrading an absent/group port to raw
improves optimal loss by<=.02. No unique encoding or probability-ordered group
IDs are required. Record structural errors at every common review256–1280 for
the form-return and detail-return histories, including transitions.

Measure observed/latent composite loss over all1–1280, adaptation241–496 and
529–784, and late1025–1280. Record local predictive losses, group/partition
changes, raw reads, raw bypass of an incorrect lower form, archive provenance,
retrievals, incompatibilities, and stability at all reviews1024–1280.

For recovery after240, find the second consecutive full-valid common evaluation
within256–512. After528 use576–1280. No pair of witnesses crosses regimes.
Retain null if no confirmation; compare censored times using592 and1344,
respectively. Report censored counts rather than implying actual recovery.

R128 passes only if ALL hold:
1. Against U128, total representation errors in forms+detail fall by>=25%,
   with strictly fewer errors in>=8/10 seed/proposal pairs aggregated across
   those two histories. A zero-error control does not establish benefit.
2. R128 and U128 each achieve>=8/10 transfer and final full validity per history.
3. Against EACH of U128 and B64, mean R128 observed/latent costs<=.02 in every
   history for whole and both adaptation windows. In every history and regime,
   mean confirmed recovery delay<=64. Every individual paired observed cost
   in either adaptation window<=.10.

H128's separate history gate requires mean observed adaptation-window gain
versus R128>=.02 and positive gain in>=8/10 seed/proposal pairs. Each paired
value equally averages both adaptation windows and four changing histories.
Also require H128 and its controls to meet transfer/final gates and the same
mean loss, recovery and worst-pair guards against R128,U128,B64. History-only
success cannot establish role separation if the R128 primary gate fails.

Report all six policy groups, all paired contrasts and per-environment means.
Timing contrasts are B128–B64 and U128–U64; updating contrasts U64–B64 and
U128–B128; roles R128–U128; history H128–R128; also compare both candidates toB64.
No significance claim from these small, dependent samples. No threshold tuning,
extra seeds or exclusion of failures follows results.

## Confirmation and resources

If and only if R128 passes, use the identical frozen code on seeds1300–1304,
proposals1300,1301. Compare U128 with H128 if its additional gate passed,
otherwise with R128. This is100 runs (proposed025). Repeat representation,
validity, mean-cost, recovery and individual-cost gates against U128. Preserve
R1's B64 comparison separately. A failure leaves adoption unsupported.

R1 allocates2,035,200 labels (300×6784); actual use is1,843,200 because200 slower
runs skip960 selection labels each. Generate169,600 labels across25 worlds.
Ceilings:99,600 candidate fits;15,000,000 scoring queries including history
feature predictions;3,000,000 candidate/history-row visits;384,000 composite
and768,000 local online predictions;218,400 evaluation predictions;1,104,000
oracle context queries. History holds at most192 records; ordinary pending and
archive limits remain (local1 cell, upper8, archive16). Counts and history
arithmetic are reported separately, not hidden behind equal label allocations.

Confirmation allocates678,400 labels, uses582,400 and generates169,600. Ceilings:
33,200 candidate fits;5,000,000 scoring queries;3,000,000 history-row visits;
128,000 composite,256,000 local,72,800 evaluation predictions;368,000 oracle
context queries. History overhead applies only if H128 is selected.

R0 new synthetic labels capped at5000 across all attempts, using3990 or explicit
records. Saved replay is separate. Preserve unsuccessful fixture attempts.
Freeze runtime, simulator, metrics, auditor, tests, spec, protocol, plan and prior
hashes before generating any reserved world. Benchmark and independent audit
limits900 seconds per stage. Persist full traces/checkpoints progressively.
Independent reconstruction imports no runtime/experiment policy code. Audit
or resource failure leaves an incomplete record; empirical failure completes
the bounded comparison. No steering experiment or deployment is run here.
