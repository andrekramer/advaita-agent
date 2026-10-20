# advaita-agent

The aspiration: **can learn; can be interpreted; can be steered.** The approach
combines autonomous learning with construction and revision by AI agents and
humans. These are research aims to evaluate, not established properties.

**Inertial Variation, Selection, and Retention (IVSR)** is the organizing
learning pattern. Existing structure constrains variation; differences between
fast adaptation and slower retained responses identify candidates for change;
selection determines what should persist. The
[fast/slow consolidation proposal](maths-v1-consolidation.md) defines this
response differential and how selected fast learning can enter slow memory.

V1 learns from external input/output discrepancies using predictive-error
updates. The proposed extension adds a distinct driver for consolidation: the
measured difference between fast and slow predictions across contexts and time.
That internal difference determines when to consider retention; external
consequences determine whether the proposed retained change is useful. Targets
may be later observations from an isolated simulator, rather than human labels.
Disagreement alone is not evidence of improvement, and agreement alone is not
evidence of correctness.

A research system for exploring differences that matter by changing, creating,
and collapsing distinctions. Non-dualism is the overarching philosophy behind
the name advaita-agent. Distinctions are revisable ways of representing experience;
opposites and dualities are possible representations, not the aim of the system.
The research combines adaptive capabilities with explicit logic, named
structures, and controlled evaluation and modification in simulation.

The immediate mathematical focus is the space of opposites and the fast/slow
learning rule: how current activity, traces, and retained relations influence
one another across timescales. Exploring this representation is compatible with
the broader aim of revising distinctions within a non-dual philosophy.

Experiments are small scale and carefully limited in scope. All AI risks and
safety concerns remain applicable. Whether this approach offers greater safety
or controllability is an open question. Scaling or applying the method or any
resulting system requires a separate, deliberate risk and safety assessment;
successful experiments alone do not justify that step.

- [Initial research brief](initial-spec)
- [Mathematics v1: oppositions, traces, and fast/slow learning](maths-v1.md)
- [Proposed extension: fast/slow IVSR with consolidation](maths-v1-consolidation.md)
- [Example input/action/target pairs](examples/input-output-v1.json)
- [First learning experiment: protocol](experiments/tiny_mapping_protocol.md)
- [First learning experiment: results and plots](results/tiny-mapping-v1/report.md)
- [Small four-state reversal experiment: protocol](experiments/small_reversal_protocol.md)
- [Small four-state reversal experiment: results and plots](results/small-reversal-v1/report.md)
- [Round 2: retention, transient errors, and consolidation protocol](experiments/round2_protocol.md)
- [Round 2: findings, limitations, and full results](results/round2-v1/findings.md)
- [Next enquiry: discovering, retaining, and revising forms](experiments/forms_research_plan.md)
- [Form acquisition: fixed protocol](experiments/forms_protocol.md)
- [Form acquisition: findings, learned rules, and results](results/forms-v1/findings.md)
- [Follow-on design: complementary situated and retained learning](experiments/complementary_roles_design.md)
- [Complementary roles: fixed protocol](experiments/complementary_roles_protocol.md)
- [Complementary roles: findings, curves, and verification](results/complementary-roles-v1/findings.md)
- [Collapsing distinctions: fixed protocol](experiments/collapse_protocol.md)
- [Collapsing distinctions: findings and all-seed results](results/collapse-v1/findings.md)
- [Reversible distinctions: fixed protocol](experiments/reversibility_protocol.md)
- [Reversible distinctions: findings and transition costs](results/reversibility-v1/findings.md)
- [Research consolidation: evidence, limits, and no meta-learning claim](results/research-synthesis.md)
- [Four influences: Grossberg, Friston, QBism, and Kelso](roadmap.md#four-influences-for-consolidation)
- [Future roadmap: evolving distinctions and relations](roadmap.md)
- [Next round: relationships, interfaces, and learning how to learn](experiments/next_round_plan.md)
- [Experiment 010: stochastic minimal bundles, fixed protocol](experiments/bundles_protocol.md)
- [Experiment 010: findings, failure modes, and verification](results/bundles-v1/findings.md)
- [Experiment 011: proposal coverage and corroboration protocol](experiments/bundle_retention_protocol.md)
- [Experiment 011: findings and adaptation tradeoffs](results/bundle-retention-v1/findings.md)
- [Experiment 012: retained and deleted interface detail, fixed protocol](experiments/interfaces_protocol.md)
- [Experiment 012: findings, retrieval benefits, and limits](results/interfaces-v1/findings.md)
- [Experiment 013: learned abstractions and nesting, fixed protocol](experiments/nested_abstractions_protocol.md)
- [Experiment 013: transfer, local repair, reopening, and failure modes](results/nested-abstractions-v1/findings.md)
- [Experiment 014: returning to abstraction, fixed protocol](experiments/reclosure_protocol.md)
- [Experiment 014: reclosure, evidence limits, and verification](results/reclosure-v1/findings.md)
- [Experiment 015: earned protection for forms, fixed protocol](experiments/form_retention_protocol.md)
- [Experiment 015: protection benefits and adaptation costs](results/form-retention-v1/findings.md)
- [Capability consolidation: relationships, abstractions, interfaces and limits](results/relationships-interfaces-synthesis.md)

The form-learning enquiry moves from supplied associations to reusable groups
of contexts that share action consequences. In the first small simulator, both
the single structural learner and provisional/retained learner discovered the
relevant feature and passed all acquisition criteria in all five seeds: 100%
accuracy on withheld combinations, log loss 0.0202, and exact learned grouping.
Their final results were identical, so this does not establish a need for two
timescales. A fixed-feature predictor also achieved 100% accuracy. Fast/slow
disagreement was zero before the first useful split, which was discovered by
scheduled search. Retention, revision, collapse, and deliberate exploration
were separated from acquisition. The acquisition run used exactly 4,880
outcome-bearing presentations, without tuning or follow-on experiments.

The subsequent complementary-roles experiment learned a smooth action-response
relationship in a continuous world, but **failed its declared complementarity
criterion**. Learned feedback reduced pooled motion error by about 16% compared
with cutting that feedback path, while noisy-position tracking improved only
1.84% (required 10%). State teaching improved the retained curve inconsistently:
only one of five seeds met its criterion. Cutting state teaching left deployed
motion prediction almost unchanged. The fixed run used 23,040 transitions; nine
correctness tests and an independent full-trace audit passed, without tuning
or expansion of that run.

The subsequent collapse point test passed in all five seeds. Both learners
first acquired two forms; when their action consequences became equivalent,
the merge-enabled learner reduced them to one at the first post-change review
(48 new main observations plus 12 selection observations), preserving 100%
withheld accuracy. It kept both forms when the world was unchanged. The no-merge
control also predicted correctly but retained two redundant forms. All conditions
used the same rolling 48-observation window, with no change-point reset. Six
correctness tests and an independent audit passed; the fixed run used 4,960
outcome-bearing presentations. This supports selective simplification within
the supplied rule language, not a general rule for when distinctions are safe
to discard.

The acquire–collapse–reacquire follow-up also passed in all five seeds, using
the unchanged learner with no reset and world changes between scheduled reviews.
It split back into two forms before its predictions fully recovered: 50%
withheld accuracy at review 240, then 100% at reviews 288 and 336. The no-merge
control recovered by the same review. During the first 48 main observations
after the distinction returned, the merged learner had approximately 16% higher
mean log loss (0.594797 versus 0.512499). Reversible simplification therefore
carried a transition cost. Six tests and an independent trace audit passed;
the fixed run used 4,480 outcome-bearing presentations without tuning.

These results support learning and revising distinctions within a supplied
language. **No meta-learning or learned category hierarchy has been demonstrated.**
Learning rules, structural operators, review schedules, and hyperparameters
remain constructed and fixed. Fast and retained roles are supplied functional
roles, and their reciprocal complementarity remains unestablished. The studies
use different implementations; they are not one integrated demonstration of
every capability. This first bounded stage concluded with a pause for writing.

The next round began on 2026-10-20 with Experiment 010: stochastic discovery
and revision of a useful relationship between two supplied distinctions, under
10% outcome noise. **Its primary reliability criterion failed:** stochastic
search passed all endpoint checks in 5/10 changing-world runs and 7/10
persistent-world runs, against a requirement of 8/10 in each. An equally
budgeted deterministic search met the same endpoint checks in 5/5 environments
in each branch, although noisy evidence temporarily caused it to discard a
useful relationship. Some stochastic failures missed the useful candidate;
others predicted well while retaining an unnecessary feature. Eight synthetic
tests and an independent full-trace audit passed. The 60-run benchmark used
103,680 allocated outcome-bearing presentations without tuning or rerunning.
This establishes a restricted joint-feature learning capability, not a benefit
from random proposals, learned folds, or meta-learning. Prediction ignores
unselected features, but search retains access to all six observed features.
Experiment 011 then tested shuffled proposal decks and split-evidence acceptance
separately and together on fresh seeds. **The combined primary criterion failed:**
6/10 changing-world runs and 9/10 persistent-world runs passed, requiring 8/10 in
each. Decks improved initial coverage of the relevant pair from 7/10 to 10/10;
deck proposals with the original acceptance rule passed 7/10 and 10/10.
No persistent-world control discarded a successfully acquired pair, leaving
no observed protection benefit for the stricter gate. That gate instead vetoed
useful discoveries in two persistent runs. Six new tests and an independent
audit passed; all 80 runs used 138,240 outcome presentations without tuning or
rerunning. These two relationship experiments are complete.

Experiment 012 then compared hiding learned detail while retaining its predictor,
deleting that predictor, and keeping detail always exposed. **Its fixed primary
criterion passed:** retain completed the required trajectory in 9/10 runs in
each of the return, novel, and persistent branches. When the original relationship
returned, retention reduced early prediction loss by 12.1% versus rebuilding
after deletion, improving 9/10 paired runs. When the relationship returned with
opposite outcomes, no stale prototype was accepted; retain and delete behaved
identically during that final phase. Keeping detail always exposed adapted
better to this novel transition. One acquisition failure remained unrecoverable
within the restricted feature set. Eight tests and an independent audit of all
90 runs passed; the fixed benchmark used 155,520 allocated and 144,000 actual
outcome presentations without tuning or rerunning. This supports reversible
information hiding within supplied feature projections, at extra memory and
selection cost. Snapshot timing and interface operations remain constructed;
all raw features remain available to search. General folds and meta-learning
remain untested.

Experiment 013 tested abstractions composed through two supplied interface
levels. All ten seed pairs learned local groups that transferred to unseen
upper-level compositions: expected loss .342068 versus .693147 for a raw-state
table. Updating lower group membership recovered prediction with a frozen upper
table in 9/10 runs. When a hidden distinction became relevant, all ten adaptive
runs reopened the affected module, and nine met final exactness and prediction
criteria. **The combined primary criterion nevertheless failed:** only 7/10
lower-remapping runs finished correctly behind the coarse interface, requiring
8/10. Temporary local errors could trigger finer exposure that persisted after
the abstraction recovered. Eight tests and an independent replay of all 120
runs passed; the benchmark used 399,360 allocated label presentations without
tuning or rerunning. Group memberships and predictions were learned, but local
feedback channels, wiring, depth, operators and failure thresholds were supplied.
This supports restricted abstraction and nesting, not learned architecture,
reliable choice of repair level, or meta-learning.

Experiment 014 added a separate reclosure operation: a fixed coarse challenger
must remain adequate on two successive fresh batches before detail is hidden
again. All ten remap runs finished with valid coarse interfaces, versus four
under the original rule, while all ten persistent-breach runs kept needed
detail and identical predictions. **The combined criterion failed:** initial
transfer passed only 7/10 fresh seed pairs, and temporary-breach reclosure
completed in 7/10, requiring 8/10. Late parent raw-state accesses fell by 40%
on average; mean post-change prediction loss rose by .002952 nats. Eight tests
and an independent replay of all 80 runs passed, using 358,400 label presentations
without tuning or rerunning. This adds a bounded return-to-abstraction capability;
reliable acquisition, evidence timing and learned consolidation remain open.
The [capability consolidation](results/relationships-interfaces-synthesis.md)
summarizes this round without treating its separate studies as one general
learner or claiming meta-learning.

Experiment 015 isolated local form retention, comparing immediate replacement,
uniform corroboration and corroboration only after a form earns support.
Earned protection prevented a temporary misleading burst from displacing a
correct form in all ten runs and preserved initial acquisition at review 64;
uniform corroboration delayed acquisition to 128. **The combined criterion
failed:** protection delayed recovery after a lasting change by one review and
raised post-change loss by .054309 nats, exceeding the fixed .05 allowance.
All variants ultimately met final validity in all conditions. Eight tests and
an independent replay of all 90 runs passed, using 138,240 label presentations
without tuning or rerunning. This supports separating discovery from protection,
with an explicit adaptation cost. It has not been integrated into the nested
learner and does not establish a learned retention policy.

The first restricted mapping experiment passed in all five seeds: 100% accuracy
on balanced evaluation with learning frozen, and mean log loss 0.296 versus
the frozen control's 0.693. This establishes learning the two supplied cue/output
associations in this setup. It does not establish generalization to new inputs
or an advantage from multiple timescales or consolidation.

The small four-state reversal experiment also passed for fast/slow learning in
all five seeds, with 100% frozen-evaluation accuracy before and after the mapping
change. However, the slow-only control performed better: final mean log loss
0.126 versus 0.699, and median recovery 114 versus 227 post-change pairs. Fast-only
recovered fastest (50 pairs) but had higher final loss (0.968), missing the fixed
loss criterion despite 100% final accuracy. Recovery means first reaching 90%
accuracy over the preceding 40 post-change predictions. This bounded comparison
supports learning and relearning categorical associations, not an advantage for
two timescales. Both timescales in that experiment learn directly from external
targets; consolidation is disabled there. No parameters were tuned after
seeing results, and all 20,000 presentations remained within the fixed protocol.

Round 2 tested retention, a transient error burst versus lasting change, and
fast-to-slow consolidation. Selected transfer improved post-gap loss over the
parallel fast/slow model (0.656 versus 1.111) in all five seeds, and useful slow
weights emerged with direct slow learning disabled. However, slow-only still
performed better (0.213 post-gap loss), and the noise/change comparison failed.
External selection rejected no hybrid candidates; removing it gave identical
trajectories. These results support useful transfer in this small task, not the
necessity of selection or general superiority of IVSR. The fixed round used
86,880 allocated labelled presentations without tuning or further expansion.
