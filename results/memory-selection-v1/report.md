# Experiment 022: complete numerical report

Completed 2026-10-26. All 80 runs independently audited. Primary criterion: **failed**. No tuning or rerunning.

Five environment realizations, with two proposal draws per environment. The two histories share evidence through 528. Losses are in nats; gains mean control loss minus treatment loss. These policy contrasts are not additive decompositions of individual learning events. See [findings](findings.md), [protocol](../../experiments/memory_selection_protocol.md) and [audit](audit.json).

## Validity and raw access

| branch | policy | runs | transfer valid | final full | stable full | stable structure | raw reads |
| --- | --- | --- | --- | --- | --- | --- | --- |
| detail | shadow | 10 | 10 | 10 | 10 | 10 | 1139.200000 |
| detail | veto | 10 | 10 | 10 | 10 | 10 | 1139.200000 |
| detail | joint | 10 | 10 | 10 | 10 | 10 | 1139.200000 |
| detail | separate | 10 | 10 | 10 | 10 | 10 | 1152 |
| reversed | shadow | 10 | 10 | 10 | 10 | 10 | 1152 |
| reversed | veto | 10 | 10 | 10 | 10 | 10 | 1152 |
| reversed | joint | 10 | 10 | 10 | 10 | 10 | 1152 |
| reversed | separate | 10 | 10 | 10 | 10 | 10 | 1152 |

Validity counts are out of ten. Stable measures require all five late reviews, 1024–1280. Raw reads are means per run.

## Observed losses

| branch | policy | pre observed | early observed | returned observed | late observed |
| --- | --- | --- | --- | --- | --- |
| detail | shadow | 0.570234 | 0.811878 | 0.441752 | 0.347223 |
| detail | veto | 0.572068 | 0.819588 | 0.443065 | 0.347223 |
| detail | joint | 0.572068 | 0.818205 | 0.442833 | 0.347217 |
| detail | separate | 0.570234 | 0.765882 | 0.431592 | 0.347217 |
| reversed | shadow | 0.570234 | 0.812671 | 0.441782 | 0.347223 |
| reversed | veto | 0.572068 | 0.818535 | 0.442780 | 0.347223 |
| reversed | joint | 0.572068 | 0.818467 | 0.442768 | 0.347223 |
| reversed | separate | 0.570234 | 0.825787 | 0.449196 | 0.347223 |

## Latent losses

| branch | policy | pre latent | early latent | returned latent | late latent |
| --- | --- | --- | --- | --- | --- |
| detail | shadow | 0.565668 | 0.813340 | 0.442915 | 0.353820 |
| detail | veto | 0.567566 | 0.820930 | 0.444207 | 0.353820 |
| detail | joint | 0.567566 | 0.820371 | 0.444112 | 0.353824 |
| detail | separate | 0.565668 | 0.767835 | 0.432177 | 0.353824 |
| reversed | shadow | 0.565668 | 0.818078 | 0.441503 | 0.353820 |
| reversed | veto | 0.567566 | 0.824067 | 0.442522 | 0.353820 |
| reversed | joint | 0.567566 | 0.824037 | 0.442517 | 0.353820 |
| reversed | separate | 0.565668 | 0.830385 | 0.448706 | 0.353820 |

Windows: pre 1–528; early 529–656; returned 529–1280; late 1025–1280.

## Mean paired contrasts

| branch | treatment | control | improved | ties | worse | identical | early observed gain | early latent gain | pre observed gain | pre latent gain | returned observed gain | late observed gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| detail | joint | veto | 1 | 7 | 2 | 6 | 0.001383 | 0.000560 | 0.000000 | 0.000000 | 0.000232 | 0.000007 |
| detail | separate | joint | 4 | 6 | 0 | 5 | 0.052323 | 0.052536 | 0.001834 | 0.001899 | 0.011241 | 0.000000 |
| detail | separate | shadow | 4 | 5 | 1 | 5 | 0.045996 | 0.045506 | 0.000000 | 0.000000 | 0.010160 | 0.000007 |
| detail | veto | shadow | 0 | 9 | 1 | 8 | -0.007710 | -0.007590 | -0.001834 | -0.001899 | -0.001312 | 0.000000 |
| reversed | joint | veto | 1 | 9 | 0 | 9 | 0.000068 | 0.000030 | 0.000000 | 0.000000 | 0.000012 | 0.000000 |
| reversed | separate | joint | 1 | 8 | 1 | 7 | -0.007321 | -0.006347 | 0.001834 | 0.001899 | -0.006428 | 0.000000 |
| reversed | separate | shadow | 1 | 8 | 1 | 8 | -0.013116 | -0.012307 | 0.000000 | 0.000000 | -0.007415 | 0.000000 |
| reversed | veto | shadow | 0 | 9 | 1 | 8 | -0.005863 | -0.005989 | -0.001834 | -0.001899 | -0.000998 | 0.000000 |

## Memory and selection events

| branch | policy | captures | early confirmations | retrievals | incompatible | nominations | failures | invalidations | qualification queries | fit blocked reviews |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| detail | shadow | 10 | 4 | 0 | 3 | 25 | 14 | 1 | 1248 | 0 |
| detail | veto | 10 | 4 | 0 | 3 | 25 | 14 | 1 | 1248 | 2 |
| detail | joint | 10 | 4 | 5 | 3 | 25 | 14 | 1 | 1248 | 2 |
| detail | separate | 10 | 4 | 8 | 3 | 25 | 14 | 1 | 1248 | 0 |
| reversed | shadow | 10 | 4 | 0 | 3 | 25 | 14 | 1 | 1248 | 0 |
| reversed | veto | 10 | 4 | 0 | 3 | 25 | 14 | 1 | 1248 | 2 |
| reversed | joint | 10 | 4 | 1 | 3 | 25 | 14 | 1 | 1248 | 2 |
| reversed | separate | 10 | 4 | 2 | 3 | 25 | 14 | 1 | 1248 | 0 |

All policies store confirmed snapshots; shadow ignores them in decisions and veto never reinstates them. `fit blocked reviews` counts an archive winning joint main-buffer ranking while a passing fitted candidate is not deployed. It includes a separate-policy choice of a better archive, so it is not by itself a harmful veto.

## All paired comparisons

| seed | proposal seed | branch | treatment | control | identical predictions | early observed gain | early latent gain | pre observed gain | pre latent gain | returned observed gain | returned latent gain | late observed gain | late latent gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1100 | 1100 | detail | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1100 | 1100 | detail | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1100 | 1100 | detail | separate | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1100 | 1100 | detail | separate | joint | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1100 | 1100 | reversed | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1100 | 1100 | reversed | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1100 | 1100 | reversed | separate | shadow | no | -0.131837 | -0.123361 | 0.000000 | 0.000000 | -0.074264 | -0.072080 | 0.000000 | 0.000000 |
| 1100 | 1100 | reversed | separate | joint | no | -0.131837 | -0.123361 | 0.000000 | 0.000000 | -0.074264 | -0.072080 | 0.000000 | 0.000000 |
| 1100 | 1101 | detail | veto | shadow | no | 0.000000 | 0.000000 | -0.018337 | -0.018986 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1100 | 1101 | detail | joint | veto | no | 0.018741 | 0.009868 | 0.000000 | 0.000000 | 0.003190 | 0.001680 | 0.000000 | 0.000000 |
| 1100 | 1101 | detail | separate | shadow | no | 0.018741 | 0.009868 | 0.000000 | 0.000000 | 0.003190 | 0.001680 | 0.000000 | 0.000000 |
| 1100 | 1101 | detail | separate | joint | no | 0.000000 | 0.000000 | 0.018337 | 0.018986 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1100 | 1101 | reversed | veto | shadow | no | 0.000000 | 0.000000 | -0.018337 | -0.018986 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1100 | 1101 | reversed | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1100 | 1101 | reversed | separate | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1100 | 1101 | reversed | separate | joint | no | 0.000000 | 0.000000 | 0.018337 | 0.018986 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1101 | 1100 | detail | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1101 | 1100 | detail | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1101 | 1100 | detail | separate | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1101 | 1100 | detail | separate | joint | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1101 | 1100 | reversed | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1101 | 1100 | reversed | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1101 | 1100 | reversed | separate | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1101 | 1100 | reversed | separate | joint | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1101 | 1101 | detail | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1101 | 1101 | detail | joint | veto | no | 0.000000 | 0.000000 | 0.000000 | 0.000000 | -0.000036 | -0.000007 | 0.000066 | -0.000039 |
| 1101 | 1101 | detail | separate | shadow | no | 0.148944 | 0.133234 | 0.000000 | 0.000000 | 0.025317 | 0.022671 | 0.000066 | -0.000039 |
| 1101 | 1101 | detail | separate | joint | no | 0.148944 | 0.133234 | 0.000000 | 0.000000 | 0.025352 | 0.022678 | 0.000000 | 0.000000 |
| 1101 | 1101 | reversed | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1101 | 1101 | reversed | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1101 | 1101 | reversed | separate | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1101 | 1101 | reversed | separate | joint | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1102 | 1100 | detail | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1102 | 1100 | detail | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1102 | 1100 | detail | separate | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1102 | 1100 | detail | separate | joint | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1102 | 1100 | reversed | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1102 | 1100 | reversed | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1102 | 1100 | reversed | separate | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1102 | 1100 | reversed | separate | joint | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1102 | 1101 | detail | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1102 | 1101 | detail | joint | veto | no | -0.003168 | -0.002783 | 0.000000 | 0.000000 | -0.000539 | -0.000474 | 0.000000 | 0.000000 |
| 1102 | 1101 | detail | separate | shadow | no | -0.003168 | -0.002783 | 0.000000 | 0.000000 | -0.000539 | -0.000474 | 0.000000 | 0.000000 |
| 1102 | 1101 | detail | separate | joint | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1102 | 1101 | reversed | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1102 | 1101 | reversed | joint | veto | no | 0.000680 | 0.000295 | 0.000000 | 0.000000 | 0.000116 | 0.000050 | 0.000000 | 0.000000 |
| 1102 | 1101 | reversed | separate | shadow | no | 0.000680 | 0.000295 | 0.000000 | 0.000000 | 0.000116 | 0.000050 | 0.000000 | 0.000000 |
| 1102 | 1101 | reversed | separate | joint | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1100 | detail | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1100 | detail | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1100 | detail | separate | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1100 | detail | separate | joint | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1100 | reversed | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1100 | reversed | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1100 | reversed | separate | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1100 | reversed | separate | joint | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1101 | detail | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1101 | detail | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1101 | detail | separate | shadow | no | 0.120897 | 0.137820 | 0.000000 | 0.000000 | 0.020578 | 0.023459 | 0.000000 | 0.000000 |
| 1103 | 1101 | detail | separate | joint | no | 0.120897 | 0.137820 | 0.000000 | 0.000000 | 0.020578 | 0.023459 | 0.000000 | 0.000000 |
| 1103 | 1101 | reversed | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1101 | reversed | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1101 | reversed | separate | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1103 | 1101 | reversed | separate | joint | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1104 | 1100 | detail | veto | shadow | no | -0.077099 | -0.075904 | 0.000000 | 0.000000 | -0.013123 | -0.012920 | 0.000000 | 0.000000 |
| 1104 | 1100 | detail | joint | veto | no | -0.001743 | -0.001487 | 0.000000 | 0.000000 | -0.000297 | -0.000253 | 0.000000 | 0.000000 |
| 1104 | 1100 | detail | separate | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1104 | 1100 | detail | separate | joint | no | 0.078842 | 0.077391 | 0.000000 | 0.000000 | 0.013420 | 0.013173 | 0.000000 | 0.000000 |
| 1104 | 1100 | reversed | veto | shadow | no | -0.058631 | -0.059887 | 0.000000 | 0.000000 | -0.009980 | -0.010194 | 0.000000 | 0.000000 |
| 1104 | 1100 | reversed | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1104 | 1100 | reversed | separate | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1104 | 1100 | reversed | separate | joint | no | 0.058631 | 0.059887 | 0.000000 | 0.000000 | 0.009980 | 0.010194 | 0.000000 | 0.000000 |
| 1104 | 1101 | detail | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1104 | 1101 | detail | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1104 | 1101 | detail | separate | shadow | no | 0.174549 | 0.176916 | 0.000000 | 0.000000 | 0.053058 | 0.060047 | 0.000000 | 0.000000 |
| 1104 | 1101 | detail | separate | joint | no | 0.174549 | 0.176916 | 0.000000 | 0.000000 | 0.053058 | 0.060047 | 0.000000 | 0.000000 |
| 1104 | 1101 | reversed | veto | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1104 | 1101 | reversed | joint | veto | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1104 | 1101 | reversed | separate | shadow | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1104 | 1101 | reversed | separate | joint | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Environment aggregates

| seed | branch | treatment | control | proposals | early gain | early latent gain |
| --- | --- | --- | --- | --- | --- | --- |
| 1100 | detail | joint | veto | 2 | 0.009370 | 0.004934 |
| 1100 | detail | separate | joint | 2 | 0.000000 | 0.000000 |
| 1100 | detail | separate | shadow | 2 | 0.009370 | 0.004934 |
| 1100 | detail | veto | shadow | 2 | 0.000000 | 0.000000 |
| 1100 | reversed | joint | veto | 2 | 0.000000 | 0.000000 |
| 1100 | reversed | separate | joint | 2 | -0.065918 | -0.061681 |
| 1100 | reversed | separate | shadow | 2 | -0.065918 | -0.061681 |
| 1100 | reversed | veto | shadow | 2 | 0.000000 | 0.000000 |
| 1101 | detail | joint | veto | 2 | 0.000000 | 0.000000 |
| 1101 | detail | separate | joint | 2 | 0.074472 | 0.066617 |
| 1101 | detail | separate | shadow | 2 | 0.074472 | 0.066617 |
| 1101 | detail | veto | shadow | 2 | 0.000000 | 0.000000 |
| 1101 | reversed | joint | veto | 2 | 0.000000 | 0.000000 |
| 1101 | reversed | separate | joint | 2 | 0.000000 | 0.000000 |
| 1101 | reversed | separate | shadow | 2 | 0.000000 | 0.000000 |
| 1101 | reversed | veto | shadow | 2 | 0.000000 | 0.000000 |
| 1102 | detail | joint | veto | 2 | -0.001584 | -0.001391 |
| 1102 | detail | separate | joint | 2 | 0.000000 | 0.000000 |
| 1102 | detail | separate | shadow | 2 | -0.001584 | -0.001391 |
| 1102 | detail | veto | shadow | 2 | 0.000000 | 0.000000 |
| 1102 | reversed | joint | veto | 2 | 0.000340 | 0.000148 |
| 1102 | reversed | separate | joint | 2 | 0.000000 | 0.000000 |
| 1102 | reversed | separate | shadow | 2 | 0.000340 | 0.000148 |
| 1102 | reversed | veto | shadow | 2 | 0.000000 | 0.000000 |
| 1103 | detail | joint | veto | 2 | 0.000000 | 0.000000 |
| 1103 | detail | separate | joint | 2 | 0.060449 | 0.068910 |
| 1103 | detail | separate | shadow | 2 | 0.060449 | 0.068910 |
| 1103 | detail | veto | shadow | 2 | 0.000000 | 0.000000 |
| 1103 | reversed | joint | veto | 2 | 0.000000 | 0.000000 |
| 1103 | reversed | separate | joint | 2 | 0.000000 | 0.000000 |
| 1103 | reversed | separate | shadow | 2 | 0.000000 | 0.000000 |
| 1103 | reversed | veto | shadow | 2 | 0.000000 | 0.000000 |
| 1104 | detail | joint | veto | 2 | -0.000872 | -0.000743 |
| 1104 | detail | separate | joint | 2 | 0.126695 | 0.127154 |
| 1104 | detail | separate | shadow | 2 | 0.087274 | 0.088458 |
| 1104 | detail | veto | shadow | 2 | -0.038549 | -0.037952 |
| 1104 | reversed | joint | veto | 2 | 0.000000 | 0.000000 |
| 1104 | reversed | separate | joint | 2 | 0.029316 | 0.029944 |
| 1104 | reversed | separate | shadow | 2 | 0.000000 | 0.000000 |
| 1104 | reversed | veto | shadow | 2 | -0.029316 | -0.029944 |

## All runs

| seed | proposal seed | branch | policy | transfer valid | final full | stable full | stable structure | pre observed | early observed | returned observed | late observed | capture indices | retrievals | raw reads |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1100 | 1100 | detail | shadow | yes | yes | yes | yes | 0.596687 | 0.740842 | 0.413840 | 0.356321 | 384 | — | 1216 |
| 1100 | 1100 | detail | veto | yes | yes | yes | yes | 0.596687 | 0.740842 | 0.413840 | 0.356321 | 384 | — | 1216 |
| 1100 | 1100 | detail | joint | yes | yes | yes | yes | 0.596687 | 0.740842 | 0.413840 | 0.356321 | 384 | — | 1216 |
| 1100 | 1100 | detail | separate | yes | yes | yes | yes | 0.596687 | 0.740842 | 0.413840 | 0.356321 | 384 | — | 1216 |
| 1100 | 1101 | detail | shadow | yes | yes | yes | yes | 0.553329 | 0.759803 | 0.417067 | 0.356321 | 192 | — | 1216 |
| 1100 | 1101 | detail | veto | yes | yes | yes | yes | 0.571666 | 0.759803 | 0.417067 | 0.356321 | 192 | — | 1216 |
| 1100 | 1101 | detail | joint | yes | yes | yes | yes | 0.571666 | 0.741062 | 0.413877 | 0.356321 | 192 | 576 | 1216 |
| 1100 | 1101 | detail | separate | yes | yes | yes | yes | 0.553329 | 0.741062 | 0.413877 | 0.356321 | 192 | 576 | 1216 |
| 1100 | 1100 | reversed | shadow | yes | yes | yes | yes | 0.596687 | 0.744317 | 0.417079 | 0.356321 | 384 | — | 1216 |
| 1100 | 1100 | reversed | veto | yes | yes | yes | yes | 0.596687 | 0.744317 | 0.417079 | 0.356321 | 384 | — | 1216 |
| 1100 | 1100 | reversed | joint | yes | yes | yes | yes | 0.596687 | 0.744317 | 0.417079 | 0.356321 | 384 | — | 1216 |
| 1100 | 1100 | reversed | separate | yes | yes | yes | yes | 0.596687 | 0.876153 | 0.491342 | 0.356321 | 384 | 576 | 1216 |
| 1100 | 1101 | reversed | shadow | yes | yes | yes | yes | 0.553329 | 0.838752 | 0.433153 | 0.356321 | 192 | — | 1216 |
| 1100 | 1101 | reversed | veto | yes | yes | yes | yes | 0.571666 | 0.838752 | 0.433153 | 0.356321 | 192 | — | 1216 |
| 1100 | 1101 | reversed | joint | yes | yes | yes | yes | 0.571666 | 0.838752 | 0.433153 | 0.356321 | 192 | — | 1216 |
| 1100 | 1101 | reversed | separate | yes | yes | yes | yes | 0.553329 | 0.838752 | 0.433153 | 0.356321 | 192 | — | 1216 |
| 1101 | 1100 | detail | shadow | yes | yes | yes | yes | 0.593852 | 0.856912 | 0.422980 | 0.288833 | 448 | — | 1088 |
| 1101 | 1100 | detail | veto | yes | yes | yes | yes | 0.593852 | 0.856912 | 0.422980 | 0.288833 | 448 | — | 1088 |
| 1101 | 1100 | detail | joint | yes | yes | yes | yes | 0.593852 | 0.856912 | 0.422980 | 0.288833 | 448 | — | 1088 |
| 1101 | 1100 | detail | separate | yes | yes | yes | yes | 0.593852 | 0.856912 | 0.422980 | 0.288833 | 448 | — | 1088 |
| 1101 | 1101 | detail | shadow | yes | yes | yes | yes | 0.557279 | 0.856912 | 0.422980 | 0.288833 | 192 | — | 1088 |
| 1101 | 1101 | detail | veto | yes | yes | yes | yes | 0.557279 | 0.856912 | 0.422980 | 0.288833 | 192 | — | 1088 |
| 1101 | 1101 | detail | joint | yes | yes | yes | yes | 0.557279 | 0.856912 | 0.423015 | 0.288766 | 192 | 768, 1152 | 1088 |
| 1101 | 1101 | detail | separate | yes | yes | yes | yes | 0.557279 | 0.707969 | 0.397663 | 0.288766 | 192 | 576, 768, 1152 | 1088 |
| 1101 | 1100 | reversed | shadow | yes | yes | yes | yes | 0.593852 | 0.752360 | 0.411819 | 0.288833 | 448 | — | 1088 |
| 1101 | 1100 | reversed | veto | yes | yes | yes | yes | 0.593852 | 0.752360 | 0.411819 | 0.288833 | 448 | — | 1088 |
| 1101 | 1100 | reversed | joint | yes | yes | yes | yes | 0.593852 | 0.752360 | 0.411819 | 0.288833 | 448 | — | 1088 |
| 1101 | 1100 | reversed | separate | yes | yes | yes | yes | 0.593852 | 0.752360 | 0.411819 | 0.288833 | 448 | — | 1088 |
| 1101 | 1101 | reversed | shadow | yes | yes | yes | yes | 0.557279 | 0.752360 | 0.411819 | 0.288833 | 192 | — | 1088 |
| 1101 | 1101 | reversed | veto | yes | yes | yes | yes | 0.557279 | 0.752360 | 0.411819 | 0.288833 | 192 | — | 1088 |
| 1101 | 1101 | reversed | joint | yes | yes | yes | yes | 0.557279 | 0.752360 | 0.411819 | 0.288833 | 192 | — | 1088 |
| 1101 | 1101 | reversed | separate | yes | yes | yes | yes | 0.557279 | 0.752360 | 0.411819 | 0.288833 | 192 | — | 1088 |
| 1102 | 1100 | detail | shadow | yes | yes | yes | yes | 0.588552 | 0.786311 | 0.450455 | 0.325531 | 384 | — | 1216 |
| 1102 | 1100 | detail | veto | yes | yes | yes | yes | 0.588552 | 0.786311 | 0.450455 | 0.325531 | 384 | — | 1216 |
| 1102 | 1100 | detail | joint | yes | yes | yes | yes | 0.588552 | 0.786311 | 0.450455 | 0.325531 | 384 | — | 1216 |
| 1102 | 1100 | detail | separate | yes | yes | yes | yes | 0.588552 | 0.786311 | 0.450455 | 0.325531 | 384 | — | 1216 |
| 1102 | 1101 | detail | shadow | yes | yes | yes | yes | 0.499803 | 0.896028 | 0.469130 | 0.325531 | 384 | — | 1216 |
| 1102 | 1101 | detail | veto | yes | yes | yes | yes | 0.499803 | 0.896028 | 0.469130 | 0.325531 | 384 | — | 1216 |
| 1102 | 1101 | detail | joint | yes | yes | yes | yes | 0.499803 | 0.899196 | 0.469670 | 0.325531 | 384 | 576 | 1216 |
| 1102 | 1101 | detail | separate | yes | yes | yes | yes | 0.499803 | 0.899196 | 0.469670 | 0.325531 | 384 | 576 | 1216 |
| 1102 | 1100 | reversed | shadow | yes | yes | yes | yes | 0.588552 | 0.785509 | 0.454165 | 0.325531 | 384 | — | 1216 |
| 1102 | 1100 | reversed | veto | yes | yes | yes | yes | 0.588552 | 0.785509 | 0.454165 | 0.325531 | 384 | — | 1216 |
| 1102 | 1100 | reversed | joint | yes | yes | yes | yes | 0.588552 | 0.785509 | 0.454165 | 0.325531 | 384 | — | 1216 |
| 1102 | 1100 | reversed | separate | yes | yes | yes | yes | 0.588552 | 0.785509 | 0.454165 | 0.325531 | 384 | — | 1216 |
| 1102 | 1101 | reversed | shadow | yes | yes | yes | yes | 0.499803 | 0.879599 | 0.470180 | 0.325531 | 384 | — | 1216 |
| 1102 | 1101 | reversed | veto | yes | yes | yes | yes | 0.499803 | 0.879599 | 0.470180 | 0.325531 | 384 | — | 1216 |
| 1102 | 1101 | reversed | joint | yes | yes | yes | yes | 0.499803 | 0.878919 | 0.470065 | 0.325531 | 384 | 576 | 1216 |
| 1102 | 1101 | reversed | separate | yes | yes | yes | yes | 0.499803 | 0.878919 | 0.470065 | 0.325531 | 384 | 576 | 1216 |
| 1103 | 1100 | detail | shadow | yes | yes | yes | yes | 0.577740 | 0.807089 | 0.427934 | 0.356950 | 448 | — | 1088 |
| 1103 | 1100 | detail | veto | yes | yes | yes | yes | 0.577740 | 0.807089 | 0.427934 | 0.356950 | 448 | — | 1088 |
| 1103 | 1100 | detail | joint | yes | yes | yes | yes | 0.577740 | 0.807089 | 0.427934 | 0.356950 | 448 | — | 1088 |
| 1103 | 1100 | detail | separate | yes | yes | yes | yes | 0.577740 | 0.807089 | 0.427934 | 0.356950 | 448 | — | 1088 |
| 1103 | 1101 | detail | shadow | yes | yes | yes | yes | 0.544418 | 0.807089 | 0.427934 | 0.356950 | 192 | — | 1088 |
| 1103 | 1101 | detail | veto | yes | yes | yes | yes | 0.544418 | 0.807089 | 0.427934 | 0.356950 | 192 | — | 1088 |
| 1103 | 1101 | detail | joint | yes | yes | yes | yes | 0.544418 | 0.807089 | 0.427934 | 0.356950 | 192 | — | 1088 |
| 1103 | 1101 | detail | separate | yes | yes | yes | yes | 0.544418 | 0.686192 | 0.407356 | 0.356950 | 192 | 576, 640 | 1088 |
| 1103 | 1100 | reversed | shadow | yes | yes | yes | yes | 0.577740 | 0.846494 | 0.434488 | 0.356950 | 448 | — | 1088 |
| 1103 | 1100 | reversed | veto | yes | yes | yes | yes | 0.577740 | 0.846494 | 0.434488 | 0.356950 | 448 | — | 1088 |
| 1103 | 1100 | reversed | joint | yes | yes | yes | yes | 0.577740 | 0.846494 | 0.434488 | 0.356950 | 448 | — | 1088 |
| 1103 | 1100 | reversed | separate | yes | yes | yes | yes | 0.577740 | 0.846494 | 0.434488 | 0.356950 | 448 | — | 1088 |
| 1103 | 1101 | reversed | shadow | yes | yes | yes | yes | 0.544418 | 0.846494 | 0.434488 | 0.356950 | 192 | — | 1088 |
| 1103 | 1101 | reversed | veto | yes | yes | yes | yes | 0.544418 | 0.846494 | 0.434488 | 0.356950 | 192 | — | 1088 |
| 1103 | 1101 | reversed | joint | yes | yes | yes | yes | 0.544418 | 0.846494 | 0.434488 | 0.356950 | 192 | — | 1088 |
| 1103 | 1101 | reversed | separate | yes | yes | yes | yes | 0.544418 | 0.846494 | 0.434488 | 0.356950 | 192 | — | 1088 |
| 1104 | 1100 | detail | shadow | yes | yes | yes | yes | 0.599066 | 0.767503 | 0.475897 | 0.408483 | 448 | — | 1216 |
| 1104 | 1100 | detail | veto | yes | yes | yes | yes | 0.599066 | 0.844601 | 0.489020 | 0.408483 | 448 | — | 1216 |
| 1104 | 1100 | detail | joint | yes | yes | yes | yes | 0.599066 | 0.846345 | 0.489317 | 0.408483 | 448 | 576 | 1216 |
| 1104 | 1100 | detail | separate | yes | yes | yes | yes | 0.599066 | 0.767503 | 0.475897 | 0.408483 | 448 | — | 1216 |
| 1104 | 1101 | detail | shadow | yes | yes | yes | yes | 0.591616 | 0.840294 | 0.489307 | 0.408483 | 192 | — | 960 |
| 1104 | 1101 | detail | veto | yes | yes | yes | yes | 0.591616 | 0.840294 | 0.489307 | 0.408483 | 192 | — | 960 |
| 1104 | 1101 | detail | joint | yes | yes | yes | yes | 0.591616 | 0.840294 | 0.489307 | 0.408483 | 192 | — | 960 |
| 1104 | 1101 | detail | separate | yes | yes | yes | yes | 0.591616 | 0.665745 | 0.436248 | 0.408483 | 192 | 576 | 1088 |
| 1104 | 1100 | reversed | shadow | yes | yes | yes | yes | 0.599066 | 0.841279 | 0.486623 | 0.408483 | 448 | — | 1216 |
| 1104 | 1100 | reversed | veto | yes | yes | yes | yes | 0.599066 | 0.899910 | 0.496603 | 0.408483 | 448 | — | 1216 |
| 1104 | 1100 | reversed | joint | yes | yes | yes | yes | 0.599066 | 0.899910 | 0.496603 | 0.408483 | 448 | — | 1216 |
| 1104 | 1100 | reversed | separate | yes | yes | yes | yes | 0.599066 | 0.841279 | 0.486623 | 0.408483 | 448 | — | 1216 |
| 1104 | 1101 | reversed | shadow | yes | yes | yes | yes | 0.591616 | 0.839552 | 0.464001 | 0.408483 | 192 | — | 1088 |
| 1104 | 1101 | reversed | veto | yes | yes | yes | yes | 0.591616 | 0.839552 | 0.464001 | 0.408483 | 192 | — | 1088 |
| 1104 | 1101 | reversed | joint | yes | yes | yes | yes | 0.591616 | 0.839552 | 0.464001 | 0.408483 | 192 | — | 1088 |
| 1104 | 1101 | reversed | separate | yes | yes | yes | yes | 0.591616 | 0.839552 | 0.464001 | 0.408483 | 192 | — | 1088 |

All per-run latent losses, snapshot provenance and checkpoint references are also in [full traces](runs.jsonl.gz).

## Frozen checks

| check | passed |
| --- | --- |
| early_gain | yes |
| improving_pairs | no |
| detail_final | yes |
| detail_shadow_pre_observed | yes |
| detail_shadow_pre_latent | yes |
| detail_joint_pre_observed | yes |
| detail_joint_pre_latent | yes |
| detail_joint_early_cost | yes |
| reversed_final | yes |
| reversed_shadow_pre_observed | yes |
| reversed_shadow_pre_latent | yes |
| reversed_shadow_early_cost | yes |
| reversed_joint_pre_observed | yes |
| reversed_joint_pre_latent | yes |
| reversed_joint_early_cost | yes |

## Resource use

| resource | used |
| --- | --- |
| runs | 80 |
| allocated_labels | 542720 |
| generated_labels | 67840 |
| used_labels | 542720 |
| candidate_fits | 24943 |
| scoring_queries | 3543552 |
| composite_predictions | 102400 |
| local_predictions | 204800 |
| evaluation_predictions | 60800 |
| oracle_context_queries | 249920 |
| qualification_queries | 9984 |

Fixtures: 6 checks; 2156/3500 charged labels. Benchmark: 138.60s; independent audit: 105.76s (600s limit each). All resource ceilings passed.

The frozen summary retains its pre-audit status. [completion.json](completion.json) and [audit.json](audit.json) record completion without rewriting the audited results.
