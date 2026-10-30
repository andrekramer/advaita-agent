# Memory-control engineering checks

2026-10-30. Six contracts passed for the original and corrected entry points.
They check independent stream reconstruction and regime boundaries, all seven
policies on ordinary and blank-interval streams, full checkpoint reconstruction
and restoration, rejection of duplicate ticks/reviews, transfer conservation,
slow-store capacity, fast/slow decay and blank-clock behavior, rejection of
conflicting transfers, frozen two-witness reduction, and paired metric/gate
arithmetic. These checks establish implementation consistency, not efficacy.

The initial fixtures used one eight-context composition block and missed an
exhausted-generator bug on longer draws. The first benchmark attempt stopped
before its first complete world or fitted learner. It is retained as incomplete
in memory-control-v1. The corrected fixtures require two composition blocks;
all tests passed again. No learning policy or empirical gate changed.

Attempt01 charged2,368 labels; attempt02 charged2,520. **Cumulative4,888** is
within the5,000 cap. Both attempt records remain available. The expanded fixture
and the sampler repair were completed before any benchmark outcome existed.
See the [restart record](../../experiments/memory_control_restart.md).
