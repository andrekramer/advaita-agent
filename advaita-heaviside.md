Advaita Agent (Heaviside) experiment handoff

Does retained evidence strength predict how far a learner turns?

Objective. Test one downstream binary prediction for a familiar category. Two agents can give the same odds for different reasons. Does retaining the amount of evidence behind those odds protect a good prediction during a misleading streak, at an acceptable cost when the odds genuinely reverse?

Unit of description. One vector summarises the evidence available to a population for one distinction. A and B below are the two possible outcomes. The letters do not denote the agent’s adaptive and normative channels. The current finite-table agent can test the learning dynamics. A later neural-network experiment can test whether the same quantities can be decoded from distributed state.

1. Model and mathematical controls

Let (y_t=1) for outcome A and (0) for B. Immediately before observing (y_t), the predictor holds (c_t=(a_t,b_t)), two nonnegative evidence tallies. Define

[
S_t=a_t+b_t,\quad p_t=a_t/S_t,\quad
r_t=\sqrt{a_t^2+b_t^2},\quad \theta_t=\operatorname{atan2}(b_t,a_t).
]

(p_t) predicts A. (S_t) measures retained evidence mass. At a fixed direction a longer arrow means more evidence. Across different directions (r_t=S_t\sqrt{p_t^2+(1-p_t)^2}), so use (S_t) for comparisons of strength. Discount applies once per observed outcome for this category. Predicting or inspecting has no effect on state.

[
c_{t+1}=\rho c_t+(y_t,1-y_t),\qquad 0<\rho\leq1.
]

Grossberg reading. Summing the two components and dividing the new A tally by the new total gives the exact scalar implementation

[
S_{t+1}=\rho S_t+1,\qquad
p_{t+1}=p_t+\frac{y_t-p_t}{S_{t+1}}.
]

The scalar pair ((p,S)) and the evidence vector are equivalent representations. Their per-event forecasts must agree to numerical precision. For constant (\rho<1), (S) approaches (1/(1-\rho)). Starting at that mass makes the fixed gain (g=1-\rho) exact from the first observation. For (\rho=1) the gain instead continues to shrink.

R-rule reading. Let (\phi_t=0) for A and (\pi/2) for B, and (\delta_t=\phi_t-\theta_t). The exact turn follows from resolving the new unit observation parallel and perpendicular to the old vector.

[
\Delta\theta_t=\operatorname{atan2}(\sin\delta_t,\rho r_t+\cos\delta_t)
\ \simeq\ \frac{\sin\delta_t}{\rho r_t}\quad(\rho r_t\gg1).
]

The sine dependence recovers the local form of the R-rule. The finite evidence update specifies its own gain. The original rotor’s separate drive and constraint terms lie outside this prediction test. The Heaviside observation motivating the comparison was that a fixed-target continuous rotor obeying (\dot\delta=-k\sin\delta) has a coordinate (u=\tan(\delta/2)) obeying (\dot u=-ku), the same form as a fixed-input instar mismatch. The experiment below uses discrete outcomes.

2. First run a deterministic test

Give two copies identical odds with short and long support. Set (c=(5,5)) and (c=(500,500)), use full retention, and give each one A. Expected next predictions are (6/11) and (501/1001). A learner retaining direction alone must give identical updates across the two starts. Repeat with B and check symmetry. In a second check use initial mass (1/(1-\rho)) and compare the vector against a constant-gain predictor at every step.

This Python 3 acceptance test has no third-party dependencies. It also checks the exact angular equation. Run once as supplied, then substitute the agent adapter’s actual predictions and states for the reference values.

from math import atan2, cos, isclose, pi, sin

def check(actual, expected):
    assert isclose(actual, expected, rel_tol=0, abs_tol=1e-12), (actual, expected)

def update(c, y, rho):
    a, b = c
    return rho * a + y, rho * b + (1 - y)

def read(c):
    return c[0] / sum(c)

for n in (5, 500):
    for y in (0, 1):
        check(read(update((n, n), y, 1)), (n + y) / (2*n + 1))

for rho, initial in ((1, (5, 5)), (.9, (4, 6)), (.99, (500, 500))):
    c = initial
    p, mass = read(c), sum(c)
    fixed = p
    for y in (1, 1, 0, 1, 0, 0, 0, 1) * 4:
        theta = atan2(c[1], c[0])
        delta = (0 if y else pi/2) - theta
        radius = (c[0]**2 + c[1]**2)**.5
        turn = atan2(sin(delta), rho * radius + cos(delta))
        c = update(c, y, rho)
        mass = rho * mass + 1
        p += (y - p) / mass
        check(read(c), p)
        check(atan2(c[1], c[0]) - theta, turn)
        if rho == .9:  # Initial mass is 10, its steady value.
            fixed += (1 - rho) * (y - fixed)
            check(p, fixed)

3. Compare predictors on identical futures

Arm

Specification

What it answers

Agent reference

Existing downstream predictor, with the reference configuration recorded at the tested commit

Does the candidate improve the agent’s final forecast?

Existing selective weakening

Reuse the published configuration with permissive admission and selective weakening. Preserve its admission and discount semantics.

Does the simple candidate add value beside a mechanism already tested for contradiction?

Direction only

Unit vector with angle (\theta). Read (p=\cos\theta/(\cos\theta+\sin\theta)). Use (\theta'=\theta+\eta\sqrt{p(1-p)}\sin(\phi-\theta)).

Does retaining strength help beyond an uncertainty-gated turn with the corrected probability readout?

Fixed-gain instar

(p'=p+g(y-p)). Include the matched (g=1-\rho) comparator and a development-selected fixed gain.

Would a simple learning rate suffice?

Evidence vector

Two discounted tallies as in §1. Include (\rho=1) as a full-retention diagnostic.

Does history-dependent gain improve the stability/reversal trade-off?

Exact scalar twin

Track ((p,S)) using §1 with identical initialisation and discount.

Implementation oracle. Any performance difference from the vector is a bug.

A. Controlled initial state. For the synthetic predictor comparison, start at (p=.8) with short support ((8,2)) or long support ((800,200)). Set the direction-only and fixed-gain arms to the identical forecast. For the rotor initialise the angle as (\operatorname{atan2}(1-p,p)). These are deliberate state interventions. They isolate retained support without confounding it with event order. Mirror outcome labels on half the seeds, including initial states and scoring targets.

B. Advaita Agent replay. Use one already-recognised category and its downstream binary output row. Use the ordinary prediction and observation entry points. Establish a common category snapshot, then replay a shuffled prefix of exactly 8 A and 2 B, or 800 A and 200 B. Replay the same prefix per seed and history length for every arm, with balanced initial pseudocounts ((1,1)) for new evidence predictors. Start the direction-only and fixed-gain arms at .5 before replay. Let native arms initialise and learn normally. Discounting and native memory rules can give different odds at the end of replay. Log those odds and the strength available to each arm. Use A for exact matched-odds claims and B for agent performance. Never infer an exact history effect from unmatched predictions.

Keep the category mapping fixed for this first test. Take a coherent snapshot of lower and downstream tables before branching. Check that changing the chosen row changes the emitted probability for the chosen input. Score both the local row and the final agent output, and log which predictor supplied the answer. Use active output with archive recall disabled across arms in this controlled replay. If the existing selective-weakening configuration operates on a different table or requires a full-task run, reproduce it through its native benchmark and report that result separately. Record the commit, actual configuration, predictor entry points and effective update count in the run manifest.

Three futures. Clone each post-prefix state for each future. Use 128 scored observations per future. For an A-favouring prefix:

Future

Observations 1–128

Question

Stable

Independent A with probability .8

How well does the learner preserve calibrated odds?

Misleading streak

Force B on observations 1–4, then resume the same .8 stream as the stable branch at indices 5–128

How much does a brief streak spoil subsequent forecasts?

Lasting reversal

Independent A with probability .2 from observation 1 onward

How quickly does the learner accept a real change?

For the mirrored branches exchange A and B throughout. Use the same future across both support levels for each seed. Only the evaluator knows the stream type. Materialise paired streams once per seed, separately from learner randomness. For every observation, predict → log → reveal outcome → update once. Give all arms the same observations. If the agent has a stochastic decision path, replay exogenous evidence so that differences in actions cannot select different training examples.

4. Metrics and decision

The following numbers are proposed design defaults, to be frozen before confirmation. Use development seeds 0–31 and fresh confirmation seeds 1000–1199. Use the same seeds across arms. Tune on development only, searching (\rho\in{.90,.97,.99}), (g\in{.01,.03,.10}) and (\eta\in{.02,.06,.20}) in their respective arms. Minimise the equal-weighted mean of the three loss windows below, weighted equally across history lengths. Break ties by listed order. Keep native published settings fixed and report full retention separately.

Forecast loss. Use pre-outcome Brier loss ((p_t-y_t)^2), lower is better. Report per-future means for stable 1–128, post-streak 5–20 and reversal 1–64. Show the forced four trials separately. Also report mean forecast against the known generating probability and both history lengths separately.

Recovery. On reversal, record the first prediction on the new side of .5 that begins four consecutive predictions on that side. Count observations already seen at that prediction. Treat unrecovered runs as censored and report their fraction alongside a mean delay capped at 128. Show mean trajectories and the first post-observation turn.

Primary comparison. Compare the evidence vector with the native reference on final output in B, averaging the two history lengths equally within each seed. Compute candidate minus reference. Use 10,000 paired seed-bootstrap resamples (bootstrap seed 77), preserving all branches within a seed. Claim an improved trade-off only if the upper endpoints of the 95% percentile intervals are below 0 for post-streak Brier and below +.01 for both stable and reversal Brier. Report actual differences and intervals even on failure. The +.01 margin is a proposed practical tolerance in squared-probability units.

Attribution. Apply the same comparison to the development-selected fixed-gain arm before claiming a benefit from tracking mass. Show selective weakening and direction-only results alongside it. A win against the native reference alone supports a change to that configuration. Scalar-twin equality supports the identity derived above. Neither result by itself establishes a special advantage for geometric coordinates.

Return from the implementing run. Deliver the manifest, the deterministic checks, one row per seed × arm × history × future with the metrics above, a paired comparison table, and a plot of mean pre-outcome forecasts through streak and reversal. Include a few paired event traces with (p,S,\theta,\Delta p), row identity, and final output source where applicable. Classify the outcome as implementation failure, demonstrated history sensitivity, or demonstrated predictive improvement, stating which controls support each claim.

5. Later population-level test

With an independently trained network on the same task, record distributed state before the new observation. Fit a simple decoder of retained strength on development histories. On held-out networks or histories, predict the observed revision using pre-update odds and incoming outcome, then assess the additional predictive value of decoded strength. At matched odds and outcome, larger decoded strength predicts smaller revision. Compare with a history-length baseline and a strength-shuffled control within matched-odds groups. A relationship measured in a network would support the population interpretation. Reading the explicit counter in the two-tally agent only verifies its construction.

Starting material. R-rule · Advaita Agent overview · Repository · Memory confirmation findings · Steering synthesis
