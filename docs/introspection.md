# Inspection, explanation and control consequences

The optional continuing runtime exposes a copied snapshot through `inspect()`.
Experiment 032 adds a read-only research adapter in
[the controller module](../experiments/introspection_controller.py) that includes
current pending decisions. No learning-engine change is involved.

The packet separates observations (forms, counts, memory masses, pending decisions,
review records) from a supplied interpretation (which upper ports consume group
membership, raw state or nothing). Review loss estimates precede final migration;
they are historical diagnostics, not exact post-review intervention forecasts.
The controller gets a JSON copy, without simulator truth or future data. The
adapter reads checkpoint metadata to obtain pending state; it does not expose
raw fast/slow banks or RNG state to the controller. This is a testable data-flow
boundary, not a security boundary.

For a specified composite output, the tested script chooses an eligible composite
memory intervention, otherwise abstains. It can predict many irrelevant local
confidence changes correctly because the upper model does not consume those
confidence values. It does not infer new causal rules or learn its control policy.
Local changes can still affect future structural learning.

The [032 results](../results/introspection-v1/findings.md) distinguish three claims:

- Stored-state reporting and independent replay passed.
- Forecasts of future composite-loss direction improved over disagreement alone.
- Immediate-effect and reliable-steering criteria failed.

A concrete limitation emerged: after a local form changes during review, the
stored upper table can remain stale until the next refit. A control that refits
all models can then appear to have an immediate downstream effect that is fully
reproduced by refreshing alone. Interpretation of a stored snapshot therefore
needs a freshness/consistency contract, not just readable labels and dependencies.
No fix or additional refresh operation has been added to the frozen runtime.

Before broader human/LLM steering, define and test that contract, attribute
refresh effects separately from evidence changes, and preserve the fresh-outcome
comparisons, collateral measurements and abstention controls used here.

Update, 2026-11-05: [033](../results/selective-steering-v1/findings.md) adds a
post-review refit in a separate experimental subclass. Refresh-only preserved
all online predictions and ordinary review choices in 30 fresh pairs; snapshots
were independently verified. The frozen runtime described above is unchanged.
The same study found useful local protection/plasticity but failed its full
steering criteria. See [the new controls and boundaries](selective-steering.md).
