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
- [Future roadmap: evolving distinctions and relations](roadmap.md)

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
two timescales. Both timescales still learn directly from external targets;
fast-to-slow consolidation remains untested. No parameters were tuned after
seeing results, and all 20,000 presentations remained within the fixed protocol.
