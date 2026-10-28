# Experiment 024: explicit learning roles and matched controls

Completed 2026-10-28. All **300 runs** passed independent reconstruction of worlds, predictions, structural decisions, evidence identities, full checkpoints, measurements and resource counts. The code and protocol were frozen before reserved-world generation. No benchmark tuning or repetition followed results.

## What was compared

This tests a concrete, minimal form of the proposed division of labour: prediction updates can change probabilities; accepted structural reviews own changes in exported group meanings. It does not replace the local and upper learners with a wholly new pair of neural or general-purpose learners.

| Policy | Predictive updates | Structural reviews | Exported meanings |
| --- | --- | --- | --- |
| B64 | Original: local updates; upper refits when raw ports are present | Every 64 records | Probability-ordered |
| B128 | Same as B64 | Every 128 | Probability-ordered |
| U64 | Also refit group-only upper tables after every record | Every 64 | Probability-ordered |
| U128 | Same as U64 | Every 128 | Probability-ordered |
| R128 | Same as U128 | Every 128 | Stable between accepted partition changes |
| H128 | Same as R128 | Every 128 | Same stable ownership; one proposal slot uses bounded adaptation history |

All use the same acquisition, candidate languages, acceptance thresholds and original archive policy. H128 changes proposal priority using residual and post-update-prediction history; it does not learn that priority rule, and does not add predictive candidate fits. Its extra arithmetic is charged. Slower variants skip alternate selection batches, so identical label allocations do not mean identical label use.

Five histories cover stability, changed probabilities without changed equivalence classes, form collapse and return, detail disappearance and return, and reversed detail. Five fresh environment seeds with two proposal draws give ten paired trajectories per history. They are five environmental realizations, not ten independent worlds or new task families.

## Prespecified decision

R128 primary gate: **fail**. H128 additional history gate: **fail**.

| R128 criterion | Outcome |
| --- | --- |
| representation reduction | Fail |
| representation pairs | Fail |
| validity | Pass |
| mean cost | Fail |
| recovery | Fail |
| worst pair | Fail |

Across form-return and detail-return, R128 had **113** structurally inappropriate evaluations versus **113** for U128: a 0.00% reduction. It improved **0/10** aggregated pairs. The gates require at least 25% reduction and eight improving pairs. These counts include all common reviews from 256 to 1280, including transitions.

An evaluation is structurally appropriate only when local partitions are correct and the selected interface is sufficient and minimal according to the fixed oracle checks. Matching a particular numeric group label is not required. Full predictive validity requires correct local partitions, all modal predictions correct and latent-loss regret at most .10. Oracle results are evaluation-only and never reach the learner.

## What explains the outcome

R128 and U128 had identical local predictive traces in all 50 paired runs.
Their composite predictions were identical in every stable, detail-return and
reversed-detail pair, in nine probability-shift pairs and in seven form-return
pairs. Stable ownership reduced exported-meaning changes from 61 to 30 across
the ten probability-shift trajectories and from 80 to 35 across form-return.
It stabilized labels without improving the primary representation measure.

The large costs against B64 chiefly accompany slower structural review/search.
For environment 1200, proposal 1201, reversed detail, B64 restored interface
[2,1] at record 576. U128 and R128 both waited until 896. Their observed
return-adaptation loss was .820046 versus .538064 for B64, a .281982-nat cost;
confirmed recovery was at 960 versus 768. H128 restored [2,1] at 640 in this
case. These traces illustrate the timing/search effect, not a failure caused
uniquely by stable exported meanings.

History guidance was not uniformly beneficial. In environment 1203, proposal
1201, reversed detail, H128's return loss was .624242 versus .520586 for
R128/U128: a .103656-nat cost, just above the .10 guard. H128's average return
costs against B64 also exceeded .02 in both detail histories (.033417 and
.028705). Its positive mean adaptation gain therefore does not pass the full
history criterion.

U64, the simpler continuous-update control with the original review frequency,
had lower mean whole-run loss than B64 in all five histories. That is a useful
unconfirmed lead; this protocol did not designate it for promotion.

**Decision:** retain the original integrated learner. R128 failed its primary
gate, so the conditional confirmation was not run and its seeds remain unused.
Steering and meta-learning were not tested.

## All-policy outcomes

Loss is pre-update observed composite log loss in nats. Lower is better. Structural errors count inappropriate common evaluations from 256 onward; the primary representation comparison uses only the forms and detail histories. Transfer/final values are successful trajectories out of ten.

| History | Policy | Transfer / final | Whole loss | Adaptation 1 | Adaptation 2 | Mean structure errors |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| stable | B128 | 10 / 10 | 0.349729 | 0.353634 | 0.331603 | 0.8 |
| stable | B64 | 10 / 10 | 0.353712 | 0.353634 | 0.331793 | 1.2 |
| stable | H128 | 10 / 10 | 0.348239 | 0.358665 | 0.317574 | 0.6 |
| stable | R128 | 10 / 10 | 0.348483 | 0.358665 | 0.318825 | 0.8 |
| stable | U128 | 10 / 10 | 0.348483 | 0.358665 | 0.318825 | 0.8 |
| stable | U64 | 10 / 10 | 0.350275 | 0.358665 | 0.317574 | 1.2 |
| probability | B128 | 10 / 10 | 0.537294 | 0.829923 | 0.776144 | 4.6 |
| probability | B64 | 10 / 10 | 0.529048 | 0.799063 | 0.758924 | 5.1 |
| probability | H128 | 10 / 10 | 0.487747 | 0.662091 | 0.704040 | 2.8 |
| probability | R128 | 10 / 10 | 0.502982 | 0.713681 | 0.705877 | 4.6 |
| probability | U128 | 10 / 10 | 0.501733 | 0.707915 | 0.705877 | 4.6 |
| probability | U64 | 10 / 10 | 0.490249 | 0.676017 | 0.696926 | 5.1 |
| forms | B128 | 10 / 9 | 0.448628 | 0.600242 | 0.547073 | 6.9 |
| forms | B64 | 10 / 10 | 0.437276 | 0.554038 | 0.559104 | 5.7 |
| forms | H128 | 10 / 10 | 0.432436 | 0.545731 | 0.544720 | 6.5 |
| forms | R128 | 10 / 9 | 0.435245 | 0.535661 | 0.540166 | 7.0 |
| forms | U128 | 10 / 9 | 0.436446 | 0.535779 | 0.545735 | 7.0 |
| forms | U64 | 10 / 10 | 0.430551 | 0.521894 | 0.546696 | 5.7 |
| detail | B128 | 10 / 9 | 0.597026 | 0.524219 | 0.714673 | 4.5 |
| detail | B64 | 10 / 10 | 0.502761 | 0.495557 | 0.574321 | 1.8 |
| detail | H128 | 10 / 9 | 0.505255 | 0.496112 | 0.607737 | 1.6 |
| detail | R128 | 10 / 9 | 0.562418 | 0.488939 | 0.715257 | 4.3 |
| detail | U128 | 10 / 9 | 0.562418 | 0.488939 | 0.715257 | 4.3 |
| detail | U64 | 10 / 10 | 0.492136 | 0.493349 | 0.569523 | 1.7 |
| reversed | B128 | 10 / 9 | 0.596847 | 0.524219 | 0.713777 | 4.5 |
| reversed | B64 | 10 / 10 | 0.502792 | 0.495557 | 0.574475 | 1.8 |
| reversed | H128 | 10 / 9 | 0.504344 | 0.496112 | 0.603180 | 1.6 |
| reversed | R128 | 10 / 9 | 0.560309 | 0.488939 | 0.704714 | 4.3 |
| reversed | U128 | 10 / 9 | 0.560309 | 0.488939 | 0.704714 | 4.3 |
| reversed | U64 | 10 / 10 | 0.491293 | 0.493349 | 0.565307 | 1.7 |

Adaptation windows are records 241–496 and 529–784. Final validity is measured at 1280. The saved results also include latent loss, local losses in the run records, late prediction and structure stability, recovery censoring, raw bypasses, meaning changes, retrievals, every paired contrast and per-environment means.

## Separating roles from timing and updating

Positive paired cost means the first policy was worse. These are whole-trajectory comparisons: review timing, form revisions and subsequent predictions interact, so the gains should not be treated as additive causal components.

| Candidate − control | History | Mean whole-loss cost | Mean first-adaptation cost | Mean second-adaptation cost | Worst individual adaptation cost |
| --- | --- | ---: | ---: | ---: | ---: |
| B128 − B64 | stable | -0.003983 | +0.000000 | -0.000190 | +0.000000 |
| B128 − B64 | probability | +0.008247 | +0.030860 | +0.017220 | +0.251271 |
| B128 − B64 | forms | +0.011352 | +0.046204 | -0.012031 | +0.174534 |
| B128 − B64 | detail | +0.094265 | +0.028662 | +0.140352 | +0.252919 |
| B128 − B64 | reversed | +0.094055 | +0.028662 | +0.139302 | +0.259038 |
| U64 − B64 | stable | -0.003438 | +0.005031 | -0.014220 | +0.027895 |
| U64 − B64 | probability | -0.038799 | -0.123047 | -0.061998 | +0.019691 |
| U64 − B64 | forms | -0.006724 | -0.032144 | -0.012408 | +0.019367 |
| U64 − B64 | detail | -0.010624 | -0.002207 | -0.004797 | +0.026033 |
| U64 − B64 | reversed | -0.011498 | -0.002207 | -0.009168 | +0.026627 |
| U128 − B128 | stable | -0.001246 | +0.005031 | -0.012778 | +0.027895 |
| U128 − B128 | probability | -0.035561 | -0.122008 | -0.070267 | +0.019099 |
| U128 − B128 | forms | -0.012182 | -0.064463 | -0.001338 | +0.044211 |
| U128 − B128 | detail | -0.034608 | -0.035279 | +0.000584 | +0.024436 |
| U128 − B128 | reversed | -0.036538 | -0.035279 | -0.009064 | +0.024047 |
| U128 − U64 | stable | -0.001792 | +0.000000 | +0.001252 | +0.012516 |
| U128 − U64 | probability | +0.011485 | +0.031899 | +0.008951 | +0.103882 |
| U128 − U64 | forms | +0.005895 | +0.013885 | -0.000961 | +0.071781 |
| U128 − U64 | detail | +0.070282 | -0.004410 | +0.145733 | +0.279786 |
| U128 − U64 | reversed | +0.069016 | -0.004410 | +0.139406 | +0.282526 |
| R128 − U128 | stable | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| R128 − U128 | probability | +0.001249 | +0.005765 | +0.000000 | +0.057654 |
| R128 − U128 | forms | -0.001201 | -0.000117 | -0.005568 | +0.000000 |
| R128 − U128 | detail | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| R128 − U128 | reversed | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| H128 − R128 | stable | -0.000244 | +0.000000 | -0.001252 | +0.000000 |
| H128 − R128 | probability | -0.015235 | -0.051590 | -0.001837 | +0.041065 |
| H128 − R128 | forms | -0.002809 | +0.010070 | +0.004554 | +0.070709 |
| H128 − R128 | detail | -0.057163 | +0.007172 | -0.107519 | +0.086771 |
| H128 − R128 | reversed | -0.055965 | +0.007172 | -0.101533 | +0.103656 |
| R128 − B64 | stable | -0.005230 | +0.005031 | -0.012968 | +0.027895 |
| R128 − B64 | probability | -0.026066 | -0.085383 | -0.053047 | +0.024410 |
| R128 − B64 | forms | -0.002031 | -0.018376 | -0.018938 | +0.055705 |
| R128 − B64 | detail | +0.059657 | -0.006617 | +0.140936 | +0.277355 |
| R128 − B64 | reversed | +0.057518 | -0.006617 | +0.130238 | +0.281982 |
| H128 − B64 | stable | -0.005473 | +0.005031 | -0.014220 | +0.027895 |
| H128 − B64 | probability | -0.041300 | -0.136972 | -0.054884 | +0.027545 |
| H128 − B64 | forms | -0.004840 | -0.008307 | -0.014384 | +0.069602 |
| H128 − B64 | detail | +0.002495 | +0.000555 | +0.033417 | +0.091802 |
| H128 − B64 | reversed | +0.001552 | +0.000555 | +0.028705 | +0.094827 |
| H128 − U128 | stable | -0.000244 | +0.000000 | -0.001252 | +0.000000 |
| H128 − U128 | probability | -0.013986 | -0.045824 | -0.001837 | +0.041065 |
| H128 − U128 | forms | -0.004010 | +0.009952 | -0.001014 | +0.052035 |
| H128 − U128 | detail | -0.057163 | +0.007172 | -0.107519 | +0.086771 |
| H128 − U128 | reversed | -0.055965 | +0.007172 | -0.101533 | +0.103656 |

## History and recovery

H128's observed adaptation gain against R128 was **+0.029189 nats**, averaging both adaptation windows and four changing histories within each pair. **8/10** pairs improved. Required: at least .02 nats and eight positive pairs, plus all validity and cost guards.

| History criterion | Outcome |
| --- | --- |
| mean gain | Pass |
| positive pairs | Pass |
| validity | Pass |
| mean cost | Fail |
| recovery | Pass |
| worst pair | Fail |

Recovery requires two consecutive full-valid evaluations within the same regime. A missing confirmation remains censored; numerical comparisons use the declared caps, not invented recovery dates. The complete censored counts are in results.json. History-only success could not promote role separation if the R128 gate failed.

## Audit, cost and limits

The benchmark used **1,843,200** label presentations from **2,035,200** allocated, across **169,600** generated labels. It performed 64,473 candidate fits, 8,693,056 scoring queries, 1,113,600 history/candidate-row visits and 320,000 extra history feature predictions. All declared ceilings passed. Benchmark time was 326.0s; independent audit 309.8s, each below 900s.

R0 reproduced 30 saved integrated traces and used 3,516 new fixture-label presentations across preserved attempts. Its repairs preceded reserved-world generation. The new independent replay reconstructs the six policies without importing runtime or experiment policy code. Earlier frozen artifacts remain unchanged.

This remains a bounded supervised experiment with supplied raw states, two local outcome channels, candidate partitions, interface vocabulary, topology, action schedule and review rules. It does not test autonomous exploration, unrestricted category creation, learned goals, meta-learning, full R-rule/IVSR necessity, steerability or safety. A failed gate for this implementation does not rule out every possible complementary-role architecture.

[Protocol](../../experiments/explicit_roles_protocol.md) · [R0 engineering findings](../explicit-roles-r0/findings.md) · [Results and paired measurements](results.json) · [Independent audit](audit.json) · [Architecture decision](../explicit-roles-architecture-decision.md)
