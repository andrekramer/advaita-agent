# Direction and strength in the working learner

16 November 2026 · Mathematical specification of the active learner used in the cell-steering confirmation

For a learned distinction, **direction** says which binary outcome its evidence favours. **Strength** says how much of that evidence is retained. Keep one pair for fast memory and one for slow memory. The same quantities determine the prediction, how far a new observation moves it, and what a temporary change in plasticity can do.

## The state behind one prediction

A *cell* $C$ is the set of fine input addresses that the current distinction treats alike. A local cell groups raw input states. An upper cell groups combinations of two inputs and an action according to the detail its interface consumes. For each fine address $i$ and bank $b\in\{f,s\}$, keep two nonnegative tallies $E_{bi}=(e_{bi0},e_{bi1})$, one per outcome. Pool by addition:

$$
E_b(C)=\sum_{i\in C}E_{bi},\qquad
S_b=E_{b0}(C)+E_{b1}(C),\qquad
q_b=\frac{E_{b1}(C)}{S_b}.
$$

An inspector sees strength $S_b$ and direction $q_b$. With zero strength the direction is undefined and that bank contributes zero. Given the pair, its tallies are $S_b(1-q_b,q_b)$ whenever $S_b>0$. The two coordinates carry the same information as the counts. Strength records weighted observations, including repeats.

With one fixed prior count for each outcome, the probability of outcome 1 is

$$
p(C)=\frac{1+E_{f1}(C)+E_{s1}(C)}{2+S_f+S_s}.
$$

Apply the prior **once per prediction**, after pooling. When a partition changes, the learner can sum the same fine-address tallies under the new grouping. Storing only the old pooled pair would discard the information needed to split it again.

## One labelled tick

1. **Decay.** Multiply both tallies in each bank by $d_b=2^{-1/h_b}$ per tick. Ordinary half-lives are $h_f=64$ and $h_s=1024$. Resolve the input's cell under the current representation and emit $p^-$ from the decayed evidence.
2. **Observe.** For external label $y\in\{0,1\}$, add $(1-y,y)$ to the visited fine address in fast memory. The simulator supplies labels for two local outputs and the composite output. Apply this rule once for each of them. An unlabelled tick only advances decay.

Let $M^-=S_f^-+S_s^-$ be the cell's total evidence after decay and before the label. With the same cell membership, its updated prediction obeys

$$
\boxed{\displaystyle p^+=p^-+\frac{y-p^-}{3+M^-}.}
$$

The denominator contains the two fixed prior counts and the one incoming observation. For example, if both outcomes have equal support and $M^-=7$, observing 1 moves the probability from 0.50 to 0.55. At the same odds with $M^-=97$, it moves to 0.505. This is an exact answer an inspector can give before learning the outcome, conditional on each possible label.

One pair for the combined banks would suffice to read the current probability. It would omit information needed at the next tick. Exchange a fast bank with 18 successes out of 20 and a slow bank with 2 out of 20. Both allocations give $p=1/2$ today. At the next decay the former allocation favours outcome 0 and the exchanged allocation favours outcome 1. They have identical total strength and opposite responses to elapsed time.

## What a review changes

Every 64 ticks in the confirmed experiment, separate labelled review observations evaluate candidate local partitions and upper interfaces. The review selects a representation, can weaken contradicted slow evidence, and can admit a fraction of fast evidence into slow memory. For each fine address in a channel, the two memory operations have one expression:

$$
(E_f,E_s)\longmapsto\big((1-\lambda)E_f,\; wE_s+\lambda E_f\big).
$$

Here both quantities on the right refer to the evidence before the review's memory operations. Ordinarily $w=1$. An accepted weakening sets $w=1/2$ after corroboration across reviews. An accepted migration uses $0<\lambda\leq 1/4$, subject to the slow store's capacity and an improvement on review evidence. Otherwise $\lambda=0$. With $w=1$, migration conserves combined evidence, hence the immediate prediction for a fixed cell. More of that evidence will now survive future ticks.

The equations take **the partition, interface and review decisions as inputs**. Candidate generation, selection by review loss, pending decisions and semantic binding are parts of the working architecture. The short evidence law alone cannot select a useful abstraction. This is the boundary of the simplicity claim. [Structural proposals](advaita/memory_control.py) · [Weakening and migration criteria](advaita/memory_revision.py)

## What steering changes

An instruction binds one cell by its contributing addresses and dependencies. While active, it changes the slow half-life for those addresses from 1024 to 128 ticks. Fast learning continues. Opening the command leaves the current prediction intact. In the tested schedule the command ends on release, a change of bound meaning at review, or expiry after 256 ticks.

Its immediate effect has a sign as well as a magnitude. Let $p^-$ and $M^-$ denote the ordinary pre-label prediction and mass above. Extra decay removes slow mass $e=(d_s-2^{-1/128})S_s$, where $S_s$ is the selected cell's slow mass **before** decay. It removes successes in proportion to the slow direction $q_s$. Subtracting the two readouts for the same cell gives

$$
p^-_{\mathrm{steered}}-p^-=
\frac{e(p^--q_s)}{2+M^--e}.
$$

If the slow bank favours outcome 1 more than the combined prediction does, faster forgetting lowers the next probability of 1. If their directions agree, the next pre-label prediction is unchanged, but the smaller mass gives the incoming label more influence. An empty slow bank has zero steering effect. Later effects depend on new labels and structural reviews. [Cell command](advaita/direction_strength.py)

## What supports the three claims

| Claim in the tested simulations | Evidence |
| --- | --- |
| **Can learn from experience** | In all 12 fresh environments, at least one acquisition produced a useful local split and met the upper transfer criterion. Continued learning improved mean Brier loss by 0.26607 over a frozen acquired predictor in the changed histories. |
| **Can be inspected by a script** | A script using each cell's fast and slow evidence correctly forecast the direction of 187 of 222 material intervention effects. Estimating each cell's allocation from channel totals gave 105 of 222. |
| **Can be steered selectively** | The uncapped cell command improved mean target Brier loss by 0.001636 over abstention (95% paired interval 0.001223–0.002135) and met every declared preservation limit. |

These results cover the implemented learner, its supplied representation language and a scripted controller. Prediction recovery and form recovery remain distinct diagnostics. At 128 observations after polarity return, both original local partitions had reappeared in 22.9% of uncapped cases. That endpoint leaves the timescale of recovery open. [Confirmation and scope](results/cell-duration-confirmation-v1/findings.md)

**Equation check.** A separate two-tally calculation replayed four previously tested paths from their acquisition buffers, using the recorded command schedule and the runtime's review choices. Across 4,608 ticks it reproduced emitted probabilities within $8.9\times10^{-16}$. The replay included 72 reviews, 20 changes of partition or interface, 8 accepted weakenings, 110 accepted transfers and 128 steered ticks. It checks the evidence algebra through those events. The earlier paired confirmation supplies the behavioural evidence. Reproduce with `python3 checks/check_direction_strength_maths.py`. [Replay check](checks/check_direction_strength_maths.py)

**When another experiment is needed.** This specification describes the current code with fewer quantities. If a future implementation also removes state or rules, compare it with the current learner on identical observations. First check predictions, interpretations and command lifetimes on saved paths. If behaviour changes, freeze the simplification and retest the affected learn, inspect and steer criteria on fresh worlds, including preservation on return. That would test whether the simpler *learner* retains the capabilities described here.
