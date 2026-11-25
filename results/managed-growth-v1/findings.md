# Inspecting and steering growth in active prediction groups

**Decision, 25 November 2026.** The external inspector met the managed-growth pilot criteria on these two constructed histories. It used recent fine-address evidence to decide whether the learner could afford to share predictions. This supports a one-time, supervised allocation of representational capacity. The cost of carrying a split after its usefulness changes is visible on return.

Twenty-four independent seeds each supplied both histories. At acquisition all 48 runs pooled A/B and learned the correct C/D distinction. B then changed from .9 to .1. C and D either stayed different or both became .5. The inspector observed 128 ticks of this changed history before choosing. It received neither the condition name nor the true rates. Both continuations forked at that decision and received the same review batch, proposals from matched initial RNG states, and subsequent observations. The recommendation was computed before the decision review. The selected policy is scored by taking its chosen continuation in each pair.

| During the next 256 observations | C/D still distinct | C/D now redundant |
|---|---:|---:|
| Recommended a fourth group | 24/24 | 0/24 |
| Mean predicted Brier cost to C/D if pooled | .09552 | .00633 |
| Fourth group used when available | 6144/6144 ticks | 1664/6144 ticks (9/24 runs) |
| Fixed minus four-group Brier, mean [95% seed bootstrap interval] | .04136 [.03708, .04577] | −.00049 [−.00097, −.00011] |
| Fixed minus inspector-selected Brier | .04136 | .00000 |

Positive differences favour permitting growth. The inspector's decision matched whether the future paired gain exceeded the preset .01 threshold in 48/48 cases (24 paired seeds). It correctly identified which channel spent a majority of the changed window pooled under the fixed budget in 18/24 valuable and 24/24 redundant cases. Thus even a correct permission decision could have an incorrect forecast about where the fixed learner would absorb the cost.

**Where the gain came from.** Below are paired mean Brier improvements from permitting four groups over keeping three. The fixed learner pooled the C/D channel on 5504/6144 changed ticks in the valuable condition and on every changed tick in the redundant condition. The main benefit in the valuable worlds was preserving C and D while adapting to B.

| Condition and window | A | B | C | D |
|---|---:|---:|---:|---:|
| Valuable, changed | .00474 | .01351 | .07888 | .06895 |
| Redundant, changed | .00000 | .00000 | −.00042 | −.00157 |
| Valuable, B returns | .01080 | −.03782 | .04008 | .03867 |
| Redundant, B returns | .00285 | −.00784 | −.00078 | −.00094 |

**Return exposed a limitation.** In the valuable condition the selected arm still gained .01330 [.00966, .01707] overall across 192 return ticks. On B alone its loss was .26626 versus .22844 at fixed capacity. At the final review all 24 fixed learners again pooled A/B, and all 24 four-group learners still split A/B. The pilot's average return guard passed in both conditions, but that average masks a source-specific recovery cost. In the redundant condition the trainer always kept three groups, so its paired return cost relative to fixed was zero. The fourth group was available for the entire continuation once permitted; this study did not test withdrawal.

**Scope.** The decision allowed capacity; the trainer did not order a split. Each learner stored the same fast and slow evidence at the same fine addresses. The budget applied only to the two local prediction tables. Its experiment-only rule resolved collisions between two proposed splits by pooling the less costly channel on fresh review observations. The unlimited-by-this-rule branch followed the ordinary learner. Before the decision, the fixed learner had already split A/B in 13/24 valuable and all 24 redundant cases. This tests permission to preserve or reacquire distinctions as well as permission to add one. These were large contrasts, sampled equally often, with one scheduled decision after a known observation window. Ambiguous changes, trainer learning, memory-byte growth and autonomous timing remain open.

[Protocol](../../experiments/managed_growth_protocol.md) · [Runner](../../experiments/managed_growth.py) · [Per-case forecasts, partitions and scores](cases.jsonl) · [Summary with intervals](summary.json) · [Replay and scoring check](../../checks/check_managed_growth.py)

From the repository root run `python3 experiments/managed_growth.py` to regenerate the compact outputs and `python3 checks/check_managed_growth.py` to verify them.
