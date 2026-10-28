# Explicit roles: R0 implementation contract (023)

Specified 2026-10-28 before reserved-world generation, following the
[comparison plan](explicit_roles_test_plan.md). Earlier files remain frozen.

`RoleLearner` separates observation-time predictive updating from local form
reviews and upper interface/relation reviews. B64 preserves original behavior;
`CompatibilityLearner` exposes the original schema2 checkpoint for exact replay
of all 30 integrated traces from019. Other variants use schema24, preserving
core state plus policy, stable-export flags, bounded history and its costs.

R128/H128 hold exported group membership fixed between accepted partition
changes. A new partition is assigned an injective mapping into IDs0,1 that
maximizes agreement with the preceding four-state membership vector; ties use
the lexicographically smallest vector. Collapse may retain ID1 if overlap
requires it. Counts remain indexed by partition labels; exported IDs are a
separate view. Acquisition uses original probability-ordered meanings, frozen
at upper initialization. Accepted form changes install compatible local counts
and the mapped export together; upper review retains original lower-first order.
No automatic oracle upper repair follows a local change.

U64/U128/R128/H128 refit every active upper table after each main observation,
including group-only tables, on the last192 main records. B variants preserve
raw-only refitting. Local predictive updates are unchanged. Archive capture,
compatibility, selection and reduction rules remain the original ones.

H128 alone retains one history entry per recent main record, capped at192:
input, action, outcome vector, two pre-update local predictions and the recorded
composite prediction, three post-update predictions, exported meanings and ID.
Five extra feature predictions per record are charged. Both successful and
unsuccessful predictions remain available. Other variants retain no such history.

At a review, draw the original four local or upper proposals using the same
deck rules. Preserve the first three. Replace only the fourth with a history-
prioritized alternative not already in the first three or equal to the current
representation. Local collapse remains in its reserved slot; upper reductions
are appended as before. No additional predictive model is fitted.

For each available representation, partition history by its current encoding
(local candidate group, or upper candidate input tuple plus action). Compute
S_r = sum_b (sum_in_b(y-p_before))^2 / (n_b N), and
S_q = sum_b (sum_in_b p_after)^2 / (n_b N).
Prefer larger S_r, then larger S_q; use the original deterministic partition
order for local ties and upper complexity order for upper ties. This is a fixed
proposal heuristic, not a new acceptance objective. It can favor noise or fine
representations; there is no claim of optimality. Candidate fitting and fresh
acceptance remain ordinary predictive-loss tests. Every candidate/history-row
visit is counted. Three ordinary proposal slots preserve search when agreement
or success yields no useful history signal.

Frozen main and selection identities remain distinct. Old raw observations
can be re-encoded under new forms but never become new independent evidence.
No simulator truth, regime markers or evaluations reach any runtime API.
