# When should the trainer give back the fourth group?

**25 November 2026. The one-way release rule failed its full criterion.** It improved B after a lasting return and protected both tasks during a persistent shift. It withdrew permission prematurely in some temporary returns, with a measurable cost to the other task. Retain the external monitor as an experimental comparison.

On 24 new seeds the same growth inspector granted a fourth active local prediction group at tick 384 in all cases. We branched each seed into three possible futures for B. C/D remained valuable throughout. Within each history, continuations either kept permission, relinquished it at the preassigned tick 768, or inspected recent evidence every 64 ticks. Two successive inspections predicting at most .01 mean benefit from the fourth group triggered release. Withdrawing permission left the learner's ordinary proposals and budget-constrained review to determine which distinction would be pooled. Commands affect active predictions; fine-address memory is retained.

| B history | Monitored release | Target or protected source outcome versus keeping four | Overall Brier improvement, monitor / timer |
|---|---|---|---:|
| Lasting return | 9 at tick 768; 15 at 832 | B improved .00546, A worsened .00356, C/D tied | +.00046 / +.00041 |
| Persistent shift | None of 24 | All four sources tied. The timer cost .05935 on C and .05831 on D. | .00000 / −.03028 |
| Return for 128 ticks, then shift again | 9 at 768; 15 never | After the shift resumed, B worsened .00197, C .02172 and D .02107 | −.01155 / −.03778 |

The first two rows cover ticks 641–1024. The last covers 769–1024. Positive gains indicate lower Brier loss. In the lasting return, the monitored B gain exceeded the .005 target and the paired 95% seed-bootstrap interval was [.00358, .00747]. The interval supports a positive effect; it includes gains below .005. The timer improved B more (.00759) at greater cost to A (.00584). The monitor's worst individual source cost across that window was .01151 on A; the prespecified guard was on source means.

**Why the short return mattered.** The short and lasting returns shared every observation and review label through tick 768. The same nine seeds therefore released in both histories. In the short world their next observation came from a regime in which A and B again benefited from separate predictions. Across their combined 2,304 remaining prediction ticks, the released learners pooled A/B for 768 and C/D for 1,536. The keep arm retained both splits for all of those ticks. The mean C and D costs each exceeded the .01 guard across all 24 seeds. The worst individual post-resumption source cost was .07474 on D. Keeping permission after a lasting return could also coexist with ordinary collapse: the keep arm pooled A/B for 1,152 of 6,144 ticks in the same late window.

The opening pilot showed the advantage of admitting an extra distinction when two tasks compete. This follow-up isolates a different decision. A history can justify pooling *now* without telling the trainer how long the saving will last. Here withdrawal committed the trainer to three groups for the remainder. The traces identify a bounded follow-up: once permission has been released, can the same external inspector re-grant it when fresh evidence again supports both distinctions? Re-granting is untested. There is no learned controller in this study.

**Reproduction.** Run `python3 experiments/managed_growth_release.py` and `python3 checks/check_managed_growth_release.py` from the repository root. The audit replays grants and releases, rescoring all 216 continuations and checking that equal history prefixes produced equal decisions. The keep branch replays with the native engine after the common acquisition.

[Prospective protocol](../../experiments/managed_growth_release_protocol.md) · [Runner](../../experiments/managed_growth_release.py) · [Per-review records and source score totals](cases.jsonl) · [Window results and worst individual costs](summary.json) · [Replay check](../../checks/check_managed_growth_release.py)
