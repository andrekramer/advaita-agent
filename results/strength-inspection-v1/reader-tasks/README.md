# Unscored inspection tasks

These twelve tasks are preparation for a separate reader study, not evidence of
human/AI understanding. One case per environment; six raw-count and six equivalent
direction/strength reports, assigned before looking at task difficulty. There are
no scored reader answers yet. Do not consult results or the separate answer key
until submitting responses. A later confirmation study should use fresh tasks.

Counts are [successes,total]. Named bank direction is successes/total (null for
zero mass); strength is retained mass, not calibrated confidence. Add fixed unit
success/failure priors when predicting. Fast half-life is64 ticks; slow is1024,
or128 while the selected channel is plastic. Commands affect one channel; none
leaves all rates unchanged. Each tick decays first, predicts, adds the outcome,
then refits. Group ports consume membership, not local probability. Structural
reviews occur every64 ticks. Recent rows are previous training observations.

For each task return numerical answers, a chosen command, and uncertainty. The
one-step question specifies an incoming observation. The future question does not
reveal future labels; its answer can legitimately be uncertain. All four command
choices are available, with the same instructions under both encodings.

- [task-01.json](task-01.json)
- [task-02.json](task-02.json)
- [task-03.json](task-03.json)
- [task-04.json](task-04.json)
- [task-05.json](task-05.json)
- [task-06.json](task-06.json)
- [task-07.json](task-07.json)
- [task-08.json](task-08.json)
- [task-09.json](task-09.json)
- [task-10.json](task-10.json)
- [task-11.json](task-11.json)
- [task-12.json](task-12.json)
