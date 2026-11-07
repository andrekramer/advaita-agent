# 036 — one preserved downstream predictor

2026-11-06. A separately authorized follow-up to
[035](../results/temporary-plasticity-v1/findings.md). Freeze sources, fixtures
and this protocol before generating seeds 2500–2504. Original default unchanged.

## Question and what changes

Can an explicitly preserved earlier predictor improve recovery while ongoing
learning continues? Experiments 021–022 confounded some memory availability with
selection blocking, and ordinary refitting could overwrite restored parameters.
035 found that ending plasticity did not remove retention costs. This test uses
an immutable output alternative, with no archive veto, evidence injection,
parameter restoration, replay training or change to active structural decisions.
It tests durable prediction reuse, not improvement of active representations.

Every arm uses 034 downstream-only steering: stable local partition locked after
512 to after 1024, composite slow half-life 128 over that interval, ordinary
1024 elsewhere. Local slow half-lives remain 1024 and fast half-lives 64.

After review 384, nominate the current composite predictor once. Copy its exact
numerical table, specification, and the local group meanings it consumes.
Record acquisition-checkpoint hash, main/selection record IDs, evidence mass,
model hash and capture tick. This is a supplied capture opportunity before the
planned intervention, not autonomous discovery of what will matter later.
No recapture, replacement or parameter update is allowed.

Score this same frozen predictor before reviews 448 and 512 on their fresh
32-row batches. Both losses must be <= .55 nats; its input meanings must match
before and after each review. A failure resets corroboration. With only these
two opportunities, any failure prevents confirmation. Failed nominations are
removed at 512; never omit them from the analysis. Confirmation data cannot also
admit the predictor: deployment eligibility starts at 576.

## Three conditions

- **Discard:** same nomination and qualification, then discard at 512. Later
  diagnostic work uses a second active predictor score as an explicit dummy.
- **Shadow:** keep the confirmed predictor and score it, but never use its output
  or let it influence active learning.
- **Recall:** keep and score it; route the composite output through it when fresh
  evidence qualifies it. Local predictions always come from the active learner.

At every review from 576 onwards, score the frozen archive and a frozen view of
the pre-review active predictor on the same fresh batch. Archive loss must be
<= .55 and at least .02 lower than active loss. Its meanings must be compatible
both before and after ordinary review. All ordinary learning decisions proceed
unchanged. The comparator can improve during that review; admission is based on
the specified pre-review comparison, not a fitted-on-selection estimate.

Admission lasts only until the next review, which independently reauthorizes or
ends it. Check meaning compatibility at EVERY main prediction, after the usual
decay/refit and before adding its label. Incompatible predictions fall back to
the active model; no old category ID may acquire a new meaning silently.
There is no hysteresis or independent second admission witness in this test.
A noisy batch may therefore authorize unhelpful recall; measure that risk.

For abstract ports, compatibility fingerprints the complete state-to-group map,
including group labels. For raw ports it fingerprints the fixed raw alphabet;
omitted ports add no dependency. The action alphabet is also fingerprinted.
Raw symbol identities are supplied and fixed throughout these worlds. This does
not test changes in perceptual grounding. Frozen parameters survive ordinary
refits, but eligibility can disappear and return as local meanings change.

All arms perform two composite diagnostic scores on each of the 26 reviews from
448 through 2048. Query counts match, not memory capacity or every scalar
operation. Discard holds no deployable archive after 512; its audit logs are
never consulted as predictive memory. All capture/qualification/selection scores
are logged. Reusing selection batches for normal learning is disclosed; utility
is measured on subsequent main predictions. No world truth enters admission.

Checkpoint schema 36 contains the unchanged continuing state and archive state.
Restore at 448 (during qualification) and 1152 (during potential recall).
Serialization uses exactly -log(p) or -log(1-p) for stored controller losses;
the independent auditor must use those same operations for exact hash checks.

## Worlds and allocation

Five environment seeds 2500–2504, proposals 2500/2501, six histories, three arms:
180 runs. Horizon 2048, reviews every 64, ten percent independent label noise,
and the misleading protected-channel burst at 513–640 match 035.

Histories: stable; category remapping then familiar return then rechange;
polarity reversal then familiar return then rechange; persistent category change;
persistent polarity change; category remapping followed by a DIFFERENT balanced
partition at 1025–1536, then the first changed mapping again at 1537. The third
partition is the unique remaining balanced bipartition (canonical first bit 0),
not the initial or first changed partition up to label exchange. It challenges
recall when the old meanings should not be reused.

Related histories share input/noise draws and initial trajectories. The five
world seeds, two proposal draws, and shared histories are not independent
replications. Report environment means, every pair, missing captures, eligibility
and deployment counts. Do not prune failures or expand seeds after outcomes.
No oracle deployment arm or parameter sweep is included.

## Prespecified outcome

Recall versus shadow is primary. Discard versus shadow must have identical
online predictions. Active predictors, ordinary reviews and underlying final
learning state must match exactly across all three arms (excluding archive and
audit metadata). This rules out selection blocking as the source of benefit.

Report expected and observed losses on all three outputs, and active predictor
expected loss separately. Windows: active 513–1024; early return 1025–1280;
whole return/post-release 1025–1536; later 1537–2048. Clean targets are used only
for evaluation. Report deployed and active validity separately. A routed correct
prediction is not evidence that the active representation recovered sooner.

Full success requires:

1. On the two familiar-return histories, pooled early-return expected composite
   gain >= .02 nats and positive in >= 14/20 pairs; each history has positive
   mean gain (> 1e-12). Missing or incompatible archives remain in denominators.
2. In EACH history, ALL four windows and ALL three outputs: recall expected mean
   cost versus shadow <= .02 and every individual cost <= .10. This includes
   unchanged, permanently changed, and altered-return controls, not just averages.
3. Final active and deployed full validity >= 8/10 in every history. Full validity
   requires correct local partitions up to relabeling, all 32 modal composite
   predictions correct, and expected regret <= .10.
4. Control parity, independent arithmetic/provenance reconstruction, checkpoint
   continuation, frozen-slot immutability, prediction-before-label ordering,
   meaning gates and resource checks pass.

No capture-rate gate is substituted for usefulness. Report acquisition, capture,
qualification failure, incompatible exclusion, admission and actual use distinctly.
A primary failure stays failed even if one subset benefits.

## Resources and verification

30 generated world histories, 307200 scalar labels, 1843200 training presentations.
Main active/routed outputs share the active computation: 1105920 scalar active
predictions plus at most 122880 archived main predictions (60 recall runs ×2048).
Count actual archive calls separately. Review evaluations count 368640 contexts
across active and deployed outputs, each returning three channels. Memory
review diagnostics: 299520 composite scores, separate from ordinary scoring.
Extra selective-decay visits: 2949120. One candidate/confirmed slot, at most
32 upper probability cells and eight local group labels. Metadata is not replay
training or an additional learning buffer. Acquisition evaluation stays logged
in acquisition records.

Caps: 350000 candidate fits, 22000000 ordinary scoring queries, 110000000
fit-related raw-bin visits, 400000 review-grid contexts; 900 seconds each for
runner and independent auditor. At most eight fixture attempts, reused released
2400 data only and explicitly charged synthetic tests. The altered-return fixture
relabels existing draws deterministically, without fresh random outcomes.
Freeze passing fixtures and recursive 035 artifacts, including its disclosed
auditor correction. Never overwrite results or silently repair frozen files.

A pass would justify fresh confirmation with capture/return timing variation,
not automatic promotion or a larger archive. A failure should identify whether
capture, meaning compatibility, admission or actual prediction utility limits
recall. End this round after reporting; no automatic parameter search or new
memory design. No meta-learning, autonomous agency or safety claim.
