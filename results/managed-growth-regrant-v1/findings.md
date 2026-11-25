# Can the external trainer re-grant useful capacity?

**Decision, 25 November 2026.** Reversible permission met the prospective criteria on the fresh seeds. Carry it forward as the comparator for externally managed growth. Its clearest benefit was preserving an already correct distinction when a different task again needed room. This study concerns four active prediction groups sharing a fixed store of fine-address evidence.

All 24 fresh seeds received an initial grant. Within each seed, three histories and three policies shared the acquisition, observation stream and review samples wherever the histories agreed. The reversible policy used the original inspector: two consecutive low estimates released permission and one later estimate above the opening threshold restored it before the next structural review. Every decision used evidence observed up to that tick. The controller received neither the regime nor future labels.

| Fresh history (24 seeds each) | Capacity decisions | Predictive consequences |
|---|---|---|
| Lasting return | All released; none reopened | Same scores as one-way release. Against keeping four, B improved .00502 (95% paired interval [.00358, .00647]); A worsened .00360; C and D tied. |
| Persistent shift | None released | All three policies produced identical scores. |
| Short return | Eight released at tick 768 and reopened at 832. Sixteen kept permission throughout. | After the shift resumed, reversible improved mean C/D Brier by .01740 [.00774, .02813] versus one-way; C and D individually tied keeping four across every seed. |

The short-return scores include all 24 seeds and all 256 ticks after the shift resumed (769–1024, one observation per channel per tick). The C/D contrast weights C and D equally. Relative to one-way release, the overall Brier gain was .01058. Relative to keeping permission, A and B incurred mean costs of .00261 and .00285, respectively. The worst individual source cost versus keep was .02286 on A; the prespecified guards applied to means. All source mean costs were below .01 in their designated windows. B's lasting-return mean narrowly exceeded the previous .005 benchmark, while its interval includes smaller gains.

**What changed at the review.** The eight early releases occurred at the end of a 128-tick return that was observationally identical to the lasting return. In each case the initial three-group allocation pooled A/B and preserved the correct C/D split. After 64 new observations the reversible inspector reopened permission in all eight. Ordinary review immediately used all four groups in each case. C/D stayed correct; at that same review the one-way branch lost the correct C/D distinction in five of the eight. The reopened A/B partition matched the underlying source grouping immediately in six cases, one review later in one, and two reviews later in one. Permission, use, and recovering the correct representation are distinct outcomes.

**Replay of the earlier failure.** Separately, all nine premature releases in the previous 24 short-return histories reopened at tick 832. Their keep and one-way paths reproduced the saved runs exactly. Across those 24 seeds the mean C/D gain over one-way was .02139; both source scores again tied keeping the original grant. These are reused histories and do not enter the fresh interval.

The trainer could correct a reversible resource decision once evidence changed. The learner retained fine-address tallies during pooling, so it could reuse that evidence when a split returned. The experiment observed at most one re-grant per trajectory, with large shifts and regular reviews. It leaves open the cost of repeated cycling, weaker evidence and discarded fine-address memory. The external controller and its thresholds were fixed.

[Prospective protocol](../../experiments/managed_growth_regrant_protocol.md) · [Experiment](../../experiments/managed_growth_regrant.py) · [Per-review decisions, partitions and scores](cases.jsonl) · [Summary and intervals](summary.json) · [Independent reversible replay](../../checks/check_managed_growth_regrant.py)

Run `python3 experiments/managed_growth_regrant.py` and `python3 checks/check_managed_growth_regrant.py` from the repository root.
