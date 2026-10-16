# Experiment 007 results

All errors below are mean squared errors. Lower is better. No tuning.

| Condition | Seed | Position | Motion | Curve-only motion | Retained curve | Accepted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| full | 0 | 0.00210512 | 0.00094492 | 0.00089477 | 0.00031386 | 3 |
| no_feedback | 0 | 0.00219732 | 0.00113930 | 0.00089444 | 0.00030865 | 3 |
| no_teaching | 0 | 0.00210506 | 0.00094475 | 0.00089512 | 0.00032635 | 3 |
| disconnected | 0 | 0.00219732 | 0.00113930 | 0.00089494 | 0.00032635 | 3 |
| online | 0 | 0.00212917 | 0.00096816 | 0.00103087 | 0.00477527 | 0 |
| misaligned | 0 | 0.00239992 | 0.00162325 | 0.00089430 | 0.00031386 | 3 |
| full | 1 | 0.00306319 | 0.00085494 | 0.00080313 | 0.00051525 | 2 |
| no_feedback | 1 | 0.00310588 | 0.00104298 | 0.00080256 | 0.00050968 | 2 |
| no_teaching | 1 | 0.00306997 | 0.00085512 | 0.00082067 | 0.00087995 | 2 |
| disconnected | 1 | 0.00310588 | 0.00104298 | 0.00082018 | 0.00087995 | 2 |
| online | 1 | 0.00305574 | 0.00087982 | 0.00098610 | 0.00487974 | 0 |
| misaligned | 1 | 0.00304737 | 0.00161153 | 0.00080365 | 0.00051525 | 2 |
| full | 2 | 0.00252127 | 0.00094294 | 0.00086866 | 0.00028183 | 2 |
| no_feedback | 2 | 0.00251475 | 0.00117300 | 0.00087079 | 0.00028378 | 2 |
| no_teaching | 2 | 0.00252109 | 0.00094327 | 0.00087250 | 0.00030366 | 2 |
| disconnected | 2 | 0.00251475 | 0.00117300 | 0.00087486 | 0.00030366 | 2 |
| online | 2 | 0.00250661 | 0.00097905 | 0.00110626 | 0.00435877 | 0 |
| misaligned | 2 | 0.00261796 | 0.00171372 | 0.00087290 | 0.00028183 | 2 |
| full | 3 | 0.00200588 | 0.00088306 | 0.00083772 | 0.00018810 | 3 |
| no_feedback | 3 | 0.00214358 | 0.00098027 | 0.00083710 | 0.00018756 | 3 |
| no_teaching | 3 | 0.00201597 | 0.00088241 | 0.00084740 | 0.00012347 | 3 |
| disconnected | 3 | 0.00214358 | 0.00098027 | 0.00084644 | 0.00012347 | 3 |
| online | 3 | 0.00203713 | 0.00087478 | 0.00096717 | 0.00524806 | 0 |
| misaligned | 3 | 0.00243479 | 0.00138312 | 0.00083652 | 0.00018810 | 3 |
| full | 4 | 0.00215957 | 0.00102987 | 0.00089171 | 0.00014623 | 2 |
| no_feedback | 4 | 0.00219822 | 0.00120634 | 0.00089053 | 0.00014182 | 2 |
| no_teaching | 4 | 0.00216181 | 0.00103043 | 0.00090132 | 0.00008364 | 2 |
| disconnected | 4 | 0.00219822 | 0.00120634 | 0.00089954 | 0.00008364 | 2 |
| online | 4 | 0.00216486 | 0.00104811 | 0.00101166 | 0.00425606 | 0 |
| misaligned | 4 | 0.00239446 | 0.00162450 | 0.00088944 | 0.00014623 | 2 |

## Registered criteria

Full complementarity criterion: **False**.

| Criterion | Seeds passing | Pooled criterion |
| --- | ---: | --- |
| feedback | 0/5 | False |
| teaching | 1/5 | True |
| joint | 0/5 | False |

Clean-regime pooled guard: True.
Seeds passing all three directional/joint conditions: 0/5.

## Sensor strata

| Condition | Regime | Position MSE | Motion MSE | Curve-only MSE |
| --- | --- | ---: | ---: | ---: |
| full | LL | 0.00003937 | 0.00003402 | 0.00003693 |
| full | LH | 0.00008299 | 0.00186948 | 0.00172690 |
| full | HL | 0.00393434 | 0.00004034 | 0.00004874 |
| full | HH | 0.00542733 | 0.00178074 | 0.00162423 |
| no_feedback | LL | 0.00007140 | 0.00016420 | 0.00003651 |
| no_feedback | LH | 0.00011917 | 0.00201980 | 0.00172720 |
| no_feedback | HL | 0.00398643 | 0.00026362 | 0.00004889 |
| no_feedback | HH | 0.00555081 | 0.00198589 | 0.00162374 |
| no_teaching | LL | 0.00003970 | 0.00003418 | 0.00004085 |
| no_teaching | LH | 0.00008204 | 0.00186599 | 0.00171371 |
| no_teaching | HL | 0.00393715 | 0.00004234 | 0.00006130 |
| no_teaching | HH | 0.00544023 | 0.00178227 | 0.00165375 |
| disconnected | LL | 0.00007140 | 0.00016420 | 0.00004013 |
| disconnected | LH | 0.00011917 | 0.00201980 | 0.00171405 |
| disconnected | HL | 0.00398643 | 0.00026362 | 0.00006167 |
| disconnected | HH | 0.00555081 | 0.00198589 | 0.00165292 |
| online | LL | 0.00004340 | 0.00005130 | 0.00013342 |
| online | LH | 0.00008612 | 0.00188332 | 0.00182508 |
| online | HL | 0.00393175 | 0.00006672 | 0.00027312 |
| online | HH | 0.00545354 | 0.00179859 | 0.00185004 |
| misaligned | LL | 0.00014051 | 0.00045375 | 0.00003630 |
| misaligned | LH | 0.00022398 | 0.00247777 | 0.00172812 |
| misaligned | HL | 0.00414735 | 0.00085041 | 0.00004997 |
| misaligned | HH | 0.00580377 | 0.00258296 | 0.00162307 |

## Factorial interaction, per seed

Positive values indicate superadditive loss reduction on that metric.

| Seed | Position | Motion | Curve-only motion | Retained curve |
| --- | ---: | ---: | ---: | ---: |
| 0 | -5.1890326e-08 | -1.655245e-07 | -1.4585189e-07 | -5.2096746e-06 |
| 1 | 6.7774138e-06 | 1.7514403e-07 | -7.1630239e-08 | -5.5707547e-06 |
| 2 | -1.7986272e-07 | 3.2674293e-07 | -2.276835e-07 | 1.9514104e-06 |
| 3 | 1.0083739e-05 | -6.511879e-07 | 3.3710869e-07 | -5.3812117e-07 |
| 4 | 2.2339455e-06 | 5.5740014e-07 | 5.8875915e-07 | -4.4114568e-06 |

## Costs and clipping

| Condition | Fits | Rows replayed | Online updates | Gain calls | Gain clips | Loop clips | Local clips | Coefficient clips |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full | 20 | 6000 | 0 | 8640 | 0 | 10 | 0 | 0 |
| no_feedback | 20 | 6000 | 0 | 4800 | 0 | 0 | 11 | 0 |
| no_teaching | 20 | 6000 | 0 | 8640 | 0 | 10 | 0 | 0 |
| disconnected | 20 | 6000 | 0 | 4800 | 0 | 0 | 11 | 0 |
| online | 0 | 0 | 2880 | 7680 | 0 | 6 | 0 | 0 |
| misaligned | 20 | 6000 | 0 | 8640 | 0 | 10 | 149 | 0 |

23,040 transitions and motion outcomes; 23,040 position measurements.
960 final and 960 initial-reference curve queries are evaluator-only.
See findings.md for interpretation and verification; metrics.json for every stratum and cost.
