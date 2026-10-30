# 026 engineering restart, before any benchmark outcome

2026-10-30. The first attempt stopped inside generation of its first world,
before any run, model fit, outcome measurement or complete world was saved.
Its context sampler received a generator of eight representative combinations;
trying to draw256 observations exhausted that generator after the first block
and made the loop empty forever. The one-block fixture did not exercise this.
The independent world reconstructor had the same generator-exhaustion issue.

The failed attempt, its manifest and all original sources remain unchanged.
New `_v2` entry points materialize reusable context lists once in both generator
and independent verifier. Small fixtures now use16 composite observations,
forcing a second shuffle block. No runtime policy, parameter, threshold,
reserved seed, sample size or primary criterion changes.

Repeat all six contracts under the original5000-label cumulative fixture
budget. Save the completed comparison to memory-control-v2; leave v1 incomplete.
The aborted attempt generated768 acquisition labels internally, none presented
to a learner or inspected as outcomes. The completed attempt generates135,040;
total generation across both attempts is135,808. Learning-label presentations
remain1,890,560. The900-second benchmark/audit limits apply to the new attempt;
the original attempt was interrupted before its900-second limit. This is an
engineering restart, not performance-guided tuning or a rerun of evaluated seeds.
