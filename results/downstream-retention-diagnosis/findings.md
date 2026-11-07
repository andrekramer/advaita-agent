# Diagnosis before study 035

2026-11-06. Read-only analysis of all 20 changing seed/proposal pairs in frozen
034, comparing downstream plasticity D with protection alone P. No new labels,
learner updates or fitted models. The script scores saved grid predictions against
both original and changed mappings; these counterfactual targets are evaluator-only.

At tick 1024, category-change expected losses (original / changed) are
P .876730 / .391853 and D .991253 / .354563. For polarity reversal they are
P .955642 / .547330 and D 1.540272 / .362567. D therefore fits the changed task
better while predicting the original mapping worse. Composite slow mass is lower
in D: 57.40 versus 121.21 for categories, 56.50 versus 109.71 for polarity.
Lower mass alone is not evidence that a particular useful memory was erased.

Local partitions match P in every paired saved review from 512 through 1536.
Upper interface specifications differ at some point in 18/20 pairs. Thus local
partition divergence cannot explain the between-policy differences here; upper
interface choices and numerical evidence remain intertwined.

At the first review after return (1088), original-map losses are .574921 versus
.563132 for category change, and .734688 versus .630850 for reversal (D versus P).
By 1536 all 40 endpoints are fully valid. This is a recovery-trajectory cost,
not demonstrated irreversible forgetting. Saved snapshots do not isolate the
causal contribution of decay from upper search. No new correctness defect was
identified by this descriptive analysis; the previous independent audit remains
necessary evidence of implementation correctness.

Proceed with the planned duration comparison. Do not add archive capacity yet.
Detailed records, masses, interface counts and first divergence times are in
[diagnosis.json](diagnosis.json); reproduction script is
[diagnose_downstream_retention.py](../../experiments/diagnose_downstream_retention.py).
