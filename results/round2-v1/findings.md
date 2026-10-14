# Round 2 findings: useful transfer, limited evidence for IVSR selection

The three registered experiments are complete. They show useful retention from
fast-to-slow transfer in this four-input task, but do not establish an advantage
over the slow-only learner or a benefit from external selection. All parameters
and criteria were fixed before the run; there was no tuning afterwards.

[Protocol](../../experiments/round2_protocol.md) · [Full report and plots](report.md)
· [Every seed's metrics](metrics.json) · [Complete recorded data](results.json)

## 1. Retention and interference

After learning A and applying 100 decay-only ticks, mean loss was:

| Model | Before gap | After gap |
| --- | ---: | ---: |
| Fast/slow | 0.731 | 1.028 |
| Fast only | 0.946 | 1.383 |
| Slow only | 0.174 | 0.216 |
| Frozen | 1.386 | 1.386 |

Fast/slow retained more predictive information than fast-only in all five seeds,
meeting the declared comparison. Slow-only retained substantially more than
either. Learning the conflicting B mapping impaired predictions of A; returning
to A allowed relearning. The old-map loss after B was 1.567 for fast/slow and
2.772 for slow-only, but this does not make slow-only generally worse: confident
learning of B is incompatible with predicting A on these identical inputs.
The model has no contextual cue permitting simultaneous retrieval of both maps.

## 2. Transient errors versus lasting change

Fast/slow had a slightly smaller *increase* in A loss after the error burst
than slow-only: 0.533 versus 0.565. However, its starting loss was much higher,
so its absolute clean-task loss after the burst was also higher. A smaller loss
increase alone is not evidence of a better noise detector; frozen weights have
zero increase while learning nothing.

During adaptation to the lasting change, fast/slow's mean tail loss was 0.894
versus slow-only's 0.390. It failed the registered joint noise/change comparison
in every seed. We have not demonstrated the proposed tradeoff advantage.
The disturbance was a 40-pair correlated burst, not IID label noise.

## 3. Consolidation

After transient corruption, recovery, a lasting reversal, and 100 decay ticks:

| Model | Combined loss after gap | Mean loss during lasting change | Final accuracy |
| --- | ---: | ---: | ---: |
| Parallel fast/slow | 1.111 | 0.977 | 75% |
| Hybrid selected transfer | 0.656 | 0.899 | 100% |
| Transfer-only slow learning | 0.791 | 0.956 | 75% |
| Transfer disabled, same rates | 1.383 | 1.001 | 100% |
| Differential trigger removed | 0.661 | 0.914 | 100% |
| External selection removed | 0.656 | 0.899 | 100% |
| Parallel trained on extra selection pairs | 1.017 | 0.944 | 75% |
| Slow only | 0.213 | 0.601 | 100% |

Final accuracy in this table is after the gap; means cover all five seeds.
The hybrid met its registered retention/adaptation criterion in every seed.
It improved both loss measures over the original parallel model and the control
that used all reserved selection pairs for additional gradient learning.
The extra-pair control also applies extra decay updates, so it is not a pure
isolation of information quantity. Slow-only still had much lower loss.

With direct slow learning disabled, transfer produced nonzero useful slow
weights: post-gap slow-only-head loss was 0.792 versus the disabled-transfer
control's uniform 1.386. This met the narrow transfer-mechanism criterion in all
five seeds. Its combined final accuracy was only 75%, so the criterion must not
be interpreted as passing the original 90% acquisition threshold or achieving
fully successful adaptation. Loss and accuracy measure different properties.

### What the ablations reveal

External selection rejected **none** of the triggered hybrid candidates:
163 of 163 were accepted across the five seeds. Removing external selection
produced identical training trajectories and checkpoint predictions in every
seed. Thus this experiment does not demonstrate a benefit from the external
selection gate, even though synthetic correctness fixtures verify that the
implementation can reject harmful candidates. Selection sees the same observed
target process, including corrupted labels; it is not an independent clean oracle.

Removing the differential trigger increased proposals from 163 to 180 and
selection-label use from 1,304 to 1,440 across the five hybrid runs. The triggered
variant had slightly lower mean post-gap loss (0.656 versus 0.661) and mean
lasting-change loss (0.899 versus 0.914). This is a small observed difference
on one fixed stream, not a general validation of the trigger or its threshold.

## Verification and scope

All 19 learner unit checks and nine mathematical consolidation checks passed.
The saved-data audit independently checked logged predictions and state
transitions, including gradient updates, paired transfer, decay, source hashes,
balanced selection allocation, and identical training data across controls.
Paired transient/persistent runs were identical until their targets diverged.
Evaluation never changed retained state or diagnostics.

There were exactly 86,880 allocated labelled presentations, including 14,400
reserved selection pairs. Learners actually accessed 5,576 of those reserved
pairs; unused slots were not fed to the model. There were 7,000 decay-only ticks
and 2,880 unlabelled probe contexts. No bounds were hit. Maximum immediate
prediction change from consolidation was 2.22e-16, within floating-point error.

The next useful question is whether selection can reject misleading fast
changes under a separately specified task with informative but imperfect
selection evidence. No further experiment has been started. These results do
not justify increasing scale or claim improved safety, interpretability,
steerability, or generalization.
