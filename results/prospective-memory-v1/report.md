# Experiment 021: complete numerical report

Completed 2026-10-26; 60 independently audited runs. **Primary criterion failed.** This report is derived from frozen results and saved traces; no additional learning or evaluation was run.

There are five environment realizations with two proposal draws each. Histories share evidence through record 528. Gains below mean control loss minus reserve loss; positive values favor reserve. Loss is in nats. See [findings](findings.md), [protocol](../../experiments/prospective_memory_protocol.md) and [audit](audit.json).

## Validity and raw access

| History | Policy | runs | transfer_valid | final_full | stable_full | stable_structure | raw_reads |
| --- | --- | --- | --- | --- | --- | --- | --- |
| detail | legacy | 10 | 10 | 10 | 10 | 10 | 1177.600000 |
| detail | reserve | 10 | 10 | 10 | 10 | 10 | 1164.800000 |
| detail | discard | 10 | 10 | 10 | 10 | 10 | 1177.600000 |
| reversed | legacy | 10 | 10 | 10 | 10 | 10 | 1177.600000 |
| reversed | reserve | 10 | 10 | 10 | 10 | 10 | 1164.800000 |
| reversed | discard | 10 | 10 | 10 | 10 | 10 | 1177.600000 |

Validity entries are counts out of ten. Stable measures require every late review at 1024, 1088, 1152, 1216 and 1280. Raw reads are means per run.

## Observed losses

| History | Policy | pre | early | returned | late |
| --- | --- | --- | --- | --- | --- |
| detail | legacy | 0.564522 | 0.724525 | 0.429953 | 0.373801 |
| detail | reserve | 0.573503 | 0.695909 | 0.425082 | 0.373801 |
| detail | discard | 0.564522 | 0.724525 | 0.429953 | 0.373801 |
| reversed | legacy | 0.564522 | 0.736291 | 0.435530 | 0.373801 |
| reversed | reserve | 0.573503 | 0.715342 | 0.431964 | 0.373801 |
| reversed | discard | 0.564522 | 0.736291 | 0.435530 | 0.373801 |

## Latent losses

| History | Policy | pre | early | returned | late |
| --- | --- | --- | --- | --- | --- |
| detail | legacy | 0.559622 | 0.734366 | 0.425749 | 0.360273 |
| detail | reserve | 0.570699 | 0.705875 | 0.420899 | 0.360273 |
| detail | discard | 0.559622 | 0.734366 | 0.425749 | 0.360273 |
| reversed | legacy | 0.559622 | 0.751818 | 0.431251 | 0.360273 |
| reversed | reserve | 0.570699 | 0.729266 | 0.427413 | 0.360273 |
| reversed | discard | 0.559622 | 0.751818 | 0.431251 | 0.360273 |

Windows: pre 1–528; early 529–656; returned 529–1280; late 1025–1280.

## Snapshot and retrieval events

| History | Policy | captures | pre_simplification_captures | early_confirmations | retrievals | incompatible | qualification_queries |
| --- | --- | --- | --- | --- | --- | --- | --- |
| detail | legacy | 3 | 0 | 0 | 0 | 0 | 0 |
| detail | reserve | 10 | 8 | 7 | 6 | 4 | 1184 |
| detail | discard | 10 | 8 | 7 | 0 | 0 | 1184 |
| reversed | legacy | 3 | 0 | 0 | 0 | 0 | 0 |
| reversed | reserve | 10 | 8 | 7 | 2 | 4 | 1248 |
| reversed | discard | 10 | 8 | 7 | 0 | 0 | 1248 |

The `captures` field counts legacy captures or prospective confirmations. For discard, all confirmed snapshots are destroyed: none is retained. Early confirmations occur by record 240. Containing some pre-simplification evidence does not establish that a snapshot represents the old task correctly.

## Qualification work

| History | Policy | nominations | failures | invalidations | confirmations |
| --- | --- | --- | --- | --- | --- |
| detail | reserve | 23 | 13 | 0 | 10 |
| detail | discard | 23 | 13 | 0 | 10 |
| reversed | reserve | 25 | 15 | 0 | 10 |
| reversed | discard | 25 | 15 | 0 | 10 |

## All paired comparisons

| seed | proposal_seed | branch | control | identical_predictions | pre_observed_gain | pre_latent_gain | early_observed_gain | early_latent_gain | returned_observed_gain | returned_latent_gain | late_observed_gain | late_latent_gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 1000 | detail | discard | no | -0.056566 | -0.057304 | 0.127094 | 0.120215 | 0.021633 | 0.020462 | 0.000000 | 0.000000 |
| 1000 | 1000 | detail | legacy | no | -0.056566 | -0.057304 | 0.127094 | 0.120215 | 0.021633 | 0.020462 | 0.000000 | 0.000000 |
| 1000 | 1000 | reversed | discard | no | -0.056566 | -0.057304 | 0.040577 | 0.054994 | 0.006907 | 0.009361 | 0.000000 | 0.000000 |
| 1000 | 1000 | reversed | legacy | no | -0.056566 | -0.057304 | 0.040577 | 0.054994 | 0.006907 | 0.009361 | 0.000000 | 0.000000 |
| 1000 | 1001 | detail | discard | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1000 | 1001 | detail | legacy | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1000 | 1001 | reversed | discard | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1000 | 1001 | reversed | legacy | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1001 | 1000 | detail | discard | no | 0.009088 | 0.010169 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1001 | 1000 | detail | legacy | no | 0.009088 | 0.010169 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1001 | 1000 | reversed | discard | no | 0.009088 | 0.010169 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1001 | 1000 | reversed | legacy | no | 0.009088 | 0.010169 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1001 | 1001 | detail | discard | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1001 | 1001 | detail | legacy | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1001 | 1001 | reversed | discard | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1001 | 1001 | reversed | legacy | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1002 | 1000 | detail | discard | no | -0.003895 | -0.005773 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1002 | 1000 | detail | legacy | no | -0.003895 | -0.005773 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1002 | 1000 | reversed | discard | no | -0.003895 | -0.005773 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1002 | 1000 | reversed | legacy | no | -0.003895 | -0.005773 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1002 | 1001 | detail | discard | no | -0.027136 | -0.023648 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1002 | 1001 | detail | legacy | no | -0.027136 | -0.023648 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1002 | 1001 | reversed | discard | no | -0.027136 | -0.023648 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1002 | 1001 | reversed | legacy | no | -0.027136 | -0.023648 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1003 | 1000 | detail | discard | no | 0.007103 | 0.001604 | -0.000220 | -0.000078 | -0.000037 | -0.000013 | 0.000000 | 0.000000 |
| 1003 | 1000 | detail | legacy | no | 0.007103 | 0.001604 | -0.000220 | -0.000078 | -0.000037 | -0.000013 | 0.000000 | 0.000000 |
| 1003 | 1000 | reversed | discard | no | 0.007103 | 0.001604 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1003 | 1000 | reversed | legacy | no | 0.007103 | 0.001604 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1003 | 1001 | detail | discard | no | -0.017245 | -0.024960 | 0.052695 | 0.054624 | 0.008969 | 0.009298 | 0.000000 | 0.000000 |
| 1003 | 1001 | detail | legacy | no | -0.017245 | -0.024960 | 0.052695 | 0.054624 | 0.008969 | 0.009298 | 0.000000 | 0.000000 |
| 1003 | 1001 | reversed | discard | no | -0.017245 | -0.024960 | 0.045513 | 0.039767 | 0.007747 | 0.006769 | 0.000000 | 0.000000 |
| 1003 | 1001 | reversed | legacy | no | -0.017245 | -0.024960 | 0.045513 | 0.039767 | 0.007747 | 0.006769 | 0.000000 | 0.000000 |
| 1004 | 1000 | detail | discard | no | -0.001156 | -0.010849 | 0.106596 | 0.110147 | 0.018144 | 0.018748 | 0.000000 | 0.000000 |
| 1004 | 1000 | detail | legacy | no | -0.001156 | -0.010849 | 0.106596 | 0.110147 | 0.018144 | 0.018748 | 0.000000 | 0.000000 |
| 1004 | 1000 | reversed | discard | no | -0.001156 | -0.010849 | 0.123395 | 0.130756 | 0.021003 | 0.022256 | 0.000000 | 0.000000 |
| 1004 | 1000 | reversed | legacy | no | -0.001156 | -0.010849 | 0.123395 | 0.130756 | 0.021003 | 0.022256 | 0.000000 | 0.000000 |
| 1004 | 1001 | detail | discard | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1004 | 1001 | detail | legacy | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1004 | 1001 | reversed | discard | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1004 | 1001 | reversed | legacy | yes | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Environment aggregates across two proposal draws

| seed | branch | control | proposals | early_gain | early_latent_gain |
| --- | --- | --- | --- | --- | --- |
| 1000 | detail | discard | 2 | 0.063547 | 0.060107 |
| 1000 | detail | legacy | 2 | 0.063547 | 0.060107 |
| 1000 | reversed | discard | 2 | 0.020289 | 0.027497 |
| 1000 | reversed | legacy | 2 | 0.020289 | 0.027497 |
| 1001 | detail | discard | 2 | 0.000000 | 0.000000 |
| 1001 | detail | legacy | 2 | 0.000000 | 0.000000 |
| 1001 | reversed | discard | 2 | 0.000000 | 0.000000 |
| 1001 | reversed | legacy | 2 | 0.000000 | 0.000000 |
| 1002 | detail | discard | 2 | 0.000000 | 0.000000 |
| 1002 | detail | legacy | 2 | 0.000000 | 0.000000 |
| 1002 | reversed | discard | 2 | 0.000000 | 0.000000 |
| 1002 | reversed | legacy | 2 | 0.000000 | 0.000000 |
| 1003 | detail | discard | 2 | 0.026237 | 0.027273 |
| 1003 | detail | legacy | 2 | 0.026237 | 0.027273 |
| 1003 | reversed | discard | 2 | 0.022757 | 0.019884 |
| 1003 | reversed | legacy | 2 | 0.022757 | 0.019884 |
| 1004 | detail | discard | 2 | 0.053298 | 0.055073 |
| 1004 | detail | legacy | 2 | 0.053298 | 0.055073 |
| 1004 | reversed | discard | 2 | 0.061697 | 0.065378 |
| 1004 | reversed | legacy | 2 | 0.061697 | 0.065378 |

## All runs

| seed | proposal_seed | branch | policy | transfer_valid | final_full | stable_full | stable_structure | pre_observed | early_observed | returned_observed | late_observed | capture_indices | retrievals | raw_reads |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 1000 | detail | legacy | yes | yes | yes | yes | 0.529512 | 0.829637 | 0.443089 | 0.354931 | — | — | 1216 |
| 1000 | 1000 | detail | reserve | yes | yes | yes | yes | 0.586079 | 0.702544 | 0.421456 | 0.354931 | 192 | 640 | 1216 |
| 1000 | 1000 | detail | discard | yes | yes | yes | yes | 0.529512 | 0.829637 | 0.443089 | 0.354931 | 192 | — | 1216 |
| 1000 | 1001 | detail | legacy | yes | yes | yes | yes | 0.581625 | 0.741657 | 0.428113 | 0.354931 | — | — | 1216 |
| 1000 | 1001 | detail | reserve | yes | yes | yes | yes | 0.581625 | 0.741657 | 0.428113 | 0.354931 | 512 | — | 1216 |
| 1000 | 1001 | detail | discard | yes | yes | yes | yes | 0.581625 | 0.741657 | 0.428113 | 0.354931 | 512 | — | 1216 |
| 1000 | 1000 | reversed | legacy | yes | yes | yes | yes | 0.529512 | 0.757948 | 0.430859 | 0.354931 | — | — | 1216 |
| 1000 | 1000 | reversed | reserve | yes | yes | yes | yes | 0.586079 | 0.717370 | 0.423952 | 0.354931 | 192 | — | 1216 |
| 1000 | 1000 | reversed | discard | yes | yes | yes | yes | 0.529512 | 0.757948 | 0.430859 | 0.354931 | 192 | — | 1216 |
| 1000 | 1001 | reversed | legacy | yes | yes | yes | yes | 0.581625 | 0.737938 | 0.427453 | 0.354931 | — | — | 1216 |
| 1000 | 1001 | reversed | reserve | yes | yes | yes | yes | 0.581625 | 0.737938 | 0.427453 | 0.354931 | 512 | — | 1216 |
| 1000 | 1001 | reversed | discard | yes | yes | yes | yes | 0.581625 | 0.737938 | 0.427453 | 0.354931 | 512 | — | 1216 |
| 1001 | 1000 | detail | legacy | yes | yes | yes | yes | 0.571722 | 0.645946 | 0.414518 | 0.346875 | — | — | 1216 |
| 1001 | 1000 | detail | reserve | yes | yes | yes | yes | 0.562635 | 0.645946 | 0.414518 | 0.346875 | 192 | — | 1216 |
| 1001 | 1000 | detail | discard | yes | yes | yes | yes | 0.571722 | 0.645946 | 0.414518 | 0.346875 | 192 | — | 1216 |
| 1001 | 1001 | detail | legacy | yes | yes | yes | yes | 0.667369 | 0.645946 | 0.414518 | 0.346875 | — | — | 1216 |
| 1001 | 1001 | detail | reserve | yes | yes | yes | yes | 0.667369 | 0.645946 | 0.414518 | 0.346875 | 704 | — | 1216 |
| 1001 | 1001 | detail | discard | yes | yes | yes | yes | 0.667369 | 0.645946 | 0.414518 | 0.346875 | 704 | — | 1216 |
| 1001 | 1000 | reversed | legacy | yes | yes | yes | yes | 0.571722 | 0.736996 | 0.432755 | 0.346875 | — | — | 1216 |
| 1001 | 1000 | reversed | reserve | yes | yes | yes | yes | 0.562635 | 0.736996 | 0.432755 | 0.346875 | 192 | — | 1216 |
| 1001 | 1000 | reversed | discard | yes | yes | yes | yes | 0.571722 | 0.736996 | 0.432755 | 0.346875 | 192 | — | 1216 |
| 1001 | 1001 | reversed | legacy | yes | yes | yes | yes | 0.667369 | 0.763997 | 0.451209 | 0.346875 | — | — | 1216 |
| 1001 | 1001 | reversed | reserve | yes | yes | yes | yes | 0.667369 | 0.763997 | 0.451209 | 0.346875 | 832 | — | 1216 |
| 1001 | 1001 | reversed | discard | yes | yes | yes | yes | 0.667369 | 0.763997 | 0.451209 | 0.346875 | 832 | — | 1216 |
| 1002 | 1000 | detail | legacy | yes | yes | yes | yes | 0.570089 | 0.770612 | 0.454667 | 0.454159 | — | — | 1216 |
| 1002 | 1000 | detail | reserve | yes | yes | yes | yes | 0.573984 | 0.770612 | 0.454667 | 0.454159 | 192 | 256 | 1216 |
| 1002 | 1000 | detail | discard | yes | yes | yes | yes | 0.570089 | 0.770612 | 0.454667 | 0.454159 | 192 | — | 1216 |
| 1002 | 1001 | detail | legacy | yes | yes | yes | yes | 0.554807 | 0.770612 | 0.454667 | 0.454159 | — | — | 1216 |
| 1002 | 1001 | detail | reserve | yes | yes | yes | yes | 0.581944 | 0.770612 | 0.454667 | 0.454159 | 192 | 256 | 1216 |
| 1002 | 1001 | detail | discard | yes | yes | yes | yes | 0.554807 | 0.770612 | 0.454667 | 0.454159 | 192 | — | 1216 |
| 1002 | 1000 | reversed | legacy | yes | yes | yes | yes | 0.570089 | 0.705376 | 0.450992 | 0.454159 | — | — | 1216 |
| 1002 | 1000 | reversed | reserve | yes | yes | yes | yes | 0.573984 | 0.705376 | 0.450992 | 0.454159 | 192 | 256 | 1216 |
| 1002 | 1000 | reversed | discard | yes | yes | yes | yes | 0.570089 | 0.705376 | 0.450992 | 0.454159 | 192 | — | 1216 |
| 1002 | 1001 | reversed | legacy | yes | yes | yes | yes | 0.554807 | 0.705376 | 0.450992 | 0.454159 | — | — | 1216 |
| 1002 | 1001 | reversed | reserve | yes | yes | yes | yes | 0.581944 | 0.705376 | 0.450992 | 0.454159 | 192 | 256 | 1216 |
| 1002 | 1001 | reversed | discard | yes | yes | yes | yes | 0.554807 | 0.705376 | 0.450992 | 0.454159 | 192 | — | 1216 |
| 1003 | 1000 | detail | legacy | yes | yes | yes | yes | 0.553304 | 0.685941 | 0.442074 | 0.363528 | 448 | — | 1088 |
| 1003 | 1000 | detail | reserve | yes | yes | yes | yes | 0.546201 | 0.686161 | 0.442112 | 0.363528 | 192 | 640 | 1088 |
| 1003 | 1000 | detail | discard | yes | yes | yes | yes | 0.553304 | 0.685941 | 0.442074 | 0.363528 | 192 | — | 1088 |
| 1003 | 1001 | detail | legacy | yes | yes | yes | yes | 0.528956 | 0.738856 | 0.451081 | 0.363528 | — | — | 1216 |
| 1003 | 1001 | detail | reserve | yes | yes | yes | yes | 0.546201 | 0.686161 | 0.442112 | 0.363528 | 192 | 640 | 1088 |
| 1003 | 1001 | detail | discard | yes | yes | yes | yes | 0.528956 | 0.738856 | 0.451081 | 0.363528 | 192 | — | 1216 |
| 1003 | 1000 | reversed | legacy | yes | yes | yes | yes | 0.553304 | 0.650263 | 0.437146 | 0.363528 | 448 | — | 1088 |
| 1003 | 1000 | reversed | reserve | yes | yes | yes | yes | 0.546201 | 0.650263 | 0.437146 | 0.363528 | 192 | — | 1088 |
| 1003 | 1000 | reversed | discard | yes | yes | yes | yes | 0.553304 | 0.650263 | 0.437146 | 0.363528 | 192 | — | 1088 |
| 1003 | 1001 | reversed | legacy | yes | yes | yes | yes | 0.528956 | 0.695776 | 0.444893 | 0.363528 | — | — | 1216 |
| 1003 | 1001 | reversed | reserve | yes | yes | yes | yes | 0.546201 | 0.650263 | 0.437146 | 0.363528 | 192 | — | 1088 |
| 1003 | 1001 | reversed | discard | yes | yes | yes | yes | 0.528956 | 0.695776 | 0.444893 | 0.363528 | 192 | — | 1216 |
| 1004 | 1000 | detail | legacy | yes | yes | yes | yes | 0.508602 | 0.761320 | 0.407473 | 0.349511 | 448 | — | 1088 |
| 1004 | 1000 | detail | reserve | yes | yes | yes | yes | 0.509757 | 0.654724 | 0.389329 | 0.349511 | 192 | 1280 | 1088 |
| 1004 | 1000 | detail | discard | yes | yes | yes | yes | 0.508602 | 0.761320 | 0.407473 | 0.349511 | 192 | — | 1088 |
| 1004 | 1001 | detail | legacy | yes | yes | yes | yes | 0.579235 | 0.654724 | 0.389329 | 0.349511 | 448 | — | 1088 |
| 1004 | 1001 | detail | reserve | yes | yes | yes | yes | 0.579235 | 0.654724 | 0.389329 | 0.349511 | 448 | — | 1088 |
| 1004 | 1001 | detail | discard | yes | yes | yes | yes | 0.579235 | 0.654724 | 0.389329 | 0.349511 | 448 | — | 1088 |
| 1004 | 1000 | reversed | legacy | yes | yes | yes | yes | 0.508602 | 0.866316 | 0.425003 | 0.349511 | 448 | — | 1088 |
| 1004 | 1000 | reversed | reserve | yes | yes | yes | yes | 0.509757 | 0.742921 | 0.403999 | 0.349511 | 192 | — | 1088 |
| 1004 | 1000 | reversed | discard | yes | yes | yes | yes | 0.508602 | 0.866316 | 0.425003 | 0.349511 | 192 | — | 1088 |
| 1004 | 1001 | reversed | legacy | yes | yes | yes | yes | 0.579235 | 0.742921 | 0.403999 | 0.349511 | 448 | — | 1088 |
| 1004 | 1001 | reversed | reserve | yes | yes | yes | yes | 0.579235 | 0.742921 | 0.403999 | 0.349511 | 448 | — | 1088 |
| 1004 | 1001 | reversed | discard | yes | yes | yes | yes | 0.579235 | 0.742921 | 0.403999 | 0.349511 | 448 | — | 1088 |

All latent per-run losses, construction IDs, snapshot timings and checkpoints remain in [full traces](runs.jsonl.gz). [Trace diagnostics](diagnostics.json) record first divergence, qualification costs and capture provenance for every reserve run.

## Frozen checks

| Check | Passed |
| --- | --- |
| detail_final | yes |
| reversed_final | yes |
| discard_early_gain | yes |
| discard_improving_pairs | no |
| discard_reversed_cost | yes |
| discard_detail_pre_observed | yes |
| discard_detail_pre_latent | yes |
| discard_reversed_pre_observed | yes |
| discard_reversed_pre_latent | yes |
| legacy_early_gain | yes |
| legacy_improving_pairs | no |
| legacy_reversed_cost | yes |
| legacy_detail_pre_observed | yes |
| legacy_detail_pre_latent | yes |
| legacy_reversed_pre_observed | yes |
| legacy_reversed_pre_latent | yes |

## Resource use

| Resource | Used |
| --- | --- |
| runs | 60 |
| allocated_labels | 407040 |
| generated_labels | 67840 |
| used_labels | 407040 |
| candidate_fits | 18718 |
| scoring_queries | 2534112 |
| composite_predictions | 76800 |
| local_predictions | 153600 |
| evaluation_predictions | 45600 |
| oracle_context_queries | 186240 |
| qualification_queries | 4864 |

All resource ceilings passed. Fixtures: 6 checks, 854/2500 charged labels. Benchmark: 99.60 seconds; independent audit: 77.72 seconds (600-second ceiling each).

The frozen `results.json` retains its pre-audit status field. [completion.json](completion.json) and [audit.json](audit.json) record the subsequent completion without rewriting that audited artifact.
