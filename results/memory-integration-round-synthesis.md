# Optional memory integration and follow-on tests: 029–031

Completed 2026-11-02. **The optional architecture is integrated and verified;
the original reference remains the default.** All three authorized stages are
complete. No old source, protocol or result was rewritten and no policy was
promoted after seeing the results.

| Stage | Evidence | Decision |
| --- | --- | --- |
| [029 integration](memory-integration-v1/findings.md) | All 350 saved 028 traces reproduced every prediction/review and exact native final checkpoint, including costs. Mid-run restore passed. Artifact audit passed. | Common runtime and explicit memory choice are available. Engineering compatibility, not a fresh learning result. |
| [030 lifecycle](memory-lifecycle-v1/findings.md) | 120 fresh runs independently audited. Settled gain .043923 nats against admission-only in 10/10 pairs; rare-context gain .180382 against fast-only in 10/10. | Full gate failed: repeated-change final validity4/10 and rare-history7/10; early adaptation costs exceeded limits. Keep memory optional. |
| [031 steering](memory-steering-v1/findings.md) | 60 fresh runs independently audited. One diagnostic-led intervention gained .008889 nats on the composite outcome, positive4/10. Stable histories triggered no controls; collateral-cost guards passed. | Full steering gate failed. The API works, but this scripted target-selection rule is not reliably useful for the intended composite outcome. |

The implemented API is [ContinuingLearner](../advaita/continuing.py), documented
in [memory runtime](../docs/memory-runtime.md). Acquisition still uses the
existing StructuralLearner. The default preserves the original windows/archive;
explicit memory choices use the frozen fast/slow evidence rules. These are
alternative backends, not a newly unified archive-plus-weighted-memory algorithm.
Inspection returns copies and shows forms, interfaces, mass and review decisions.
Checkpoints preserve the engine and wrapper state. A bounded external operation
can halve one slow channel after a review, recording rationale and state hashes.
No protection/freeze operator was added in this minimal version.

The stress tests strengthen the retention/adaptation distinction. Slow memory
helps retain rare information, but it can obstruct recurring changes. Even
when later predictions improve, correct representations and quick readjustment
are not guaranteed. The simpler controls remain meaningful alternatives.

The steering diagnostics are especially useful for the next question. Four
interventions selected the composite channel and improved composite prediction.
Six selected a local channel and improved its probability estimates, while
composite probabilities were unchanged in the primary window. This is a
post-audit finding, not a replacement criterion. The upper interface consumes
category membership, not local confidence: a useful local adjustment need not
propagate to the output the controller is meant to influence. All five steering
environments happened to change node0; node coverage is another limitation.

A future steering study should first specify the intended output and test whether
inspection can identify interventions with the relevant downstream effect. That
would be a new preregistered experiment, not a retuning or rerun of031. No further
experiment was started. Human/LLM interpretation, protection controls, learned
memory policies, general agency and a safety advantage remain untested.

Resource accounting: 1,890,560 saved-label presentations for compatibility plus
294 saved-label fixture presentations; 1,228,800 new benchmark presentations for
030 and614,400 for031, with1792 and672 fixture presentations respectively. All
fixed benchmark/audit budgets passed. Full source manifests, worlds, traces,
checkpoints, per-pair data and audits are linked from the stage findings.
