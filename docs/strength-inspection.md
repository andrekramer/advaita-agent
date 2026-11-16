# Inspecting prediction direction and retained strength

The [research adapter](../experiments/strength_inspection.py) adds a read-only
description around the existing `ControlledLearner`. It does not change the
learner's equations or production inspection API. The experiment uses shadow
recall, so its predictions come from the active model.

The existing inspection reports prediction-table counts and total fast/slow mass
per channel. That does not fully specify each prediction's fast/slow allocation.
The adapter aggregates a copied checkpoint's raw evidence into the current
prediction cells, exposing successes and total mass separately for both banks.
This additional information is distinguished from the choice of notation.

For each bank with successes `u` and retained mass `n`, the named view reports
direction `u/n` and strength `n`. Empty banks have zero strength and a null
direction. This is an invertible encoding of two counts, not additional evidence
or a calibrated measure of confidence. The current prediction includes the
learner's fixed unit success/failure priors:

\[
p=\frac{u_f+u_s+1}{n_f+n_s+2}.
\]

At the next tick, before an incoming label, the probability for the same
prediction cell is

\[
p^- = \frac{d_f u_f+d_s u_s+1}{d_f n_f+d_s n_s+2},
\qquad d_f=2^{-1/64},\quad d_s=2^{-1/h_s}.
\]

After one label `y` enters that cell, its diagnostic probability is

\[
p^+ = \frac{d_f u_f+d_s u_s+y+1}{d_f n_f+d_s n_s+3}.
\]

These expressions are conditional on a specified incoming context/label and
unchanged partition membership during that observation. They account for the
actual decay-before-prediction clock. Labels used to name groups can reorder;
the grouped raw evidence and membership remain the relevant quantities. Reviews
can change representations, invalidate a frozen-cell forecast, and migrate or
weaken evidence. A single aggregate `(p, strength)` cannot replace both banks.

The existing plasticity command changes selected slow half-life from 1024 to128.
It does not immediately edit the prediction. Release restores the ordinary rate;
it does not recover forgotten evidence. The adapter adds no new command.

The supplied controller projects 64 steps using recent empirical visit/outcome
rates and fixed representations. This approximation omits structural search and
future review decisions; exact one-step arithmetic does not imply accurate
longer-term control-effect forecasts. Counts and direction/strength versions use
the same calculation and must give equivalent decisions.

See the [frozen experiment protocol](../experiments/strength_inspection_protocol.md)
and [findings](../results/strength-inspection-v1/findings.md). Separate reader
tasks are required to assess whether the notation improves human or AI
understanding. Scripted reconstruction alone does not establish that claim.
