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
- [Future roadmap: evolving distinctions and relations](roadmap.md)

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
every capability. This bounded stage is now complete and pauses for writing.

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
