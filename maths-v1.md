# Mathematics v1: oppositions, traces, and fast/slow learning

Status: proposed mathematical design, 2026-10-12. Mathematical identities and
small numerical checks are distinguished below from the larger learning
experiments specified here, which have not yet been run. A subsequent
[restricted mapping experiment](results/tiny-mapping-v1/report.md) tests the
basic update alone and passed in all five seeds. A subsequent
[four-state reversal experiment](results/small-reversal-v1/report.md) also passed
for fast/slow learning, but the slow-only control achieved lower loss and earlier
recovery. Neither experiment enables consolidation or phase learning.
This specification implements a bounded first part of
[initial-spec](initial-spec) and [roadmap.md](roadmap.md).

## 1. Question and decisions

Can a small, explicitly represented space of opposites learn useful predictive
relations across time, expose how those relations affect its predictions, and
respond intelligibly to controlled interventions?

The proposed answer to investigate is a conditional probabilistic model with
phase-dependent communication, activity traces, and two rates of retained
adaptation. Humans or AI agents construct its initial vocabulary, allowed
relations, constraints, and concerns. Experience changes its retained weights.

For v1:

- Use at most three oppositions, enumerating their joint configurations exactly.
- Keep the vocabulary, allowed relations, and evaluation rules fixed per run.
- Separate probabilities, participation, phase, memory, and valuation.
- Learn to predict consequences conditional on an action, then choose actions
  using those predictions. Do not initially learn a separate reward-driven actor.
- Allow one outstanding prediction at a time. This makes delayed attribution
  explicit without introducing an unverified multi-step credit algorithm.
- Study small, isolated synthetic environments. No live external actuation,
  structural growth, LLM training, or autonomous changes to experiment limits.

Oppositions are the mathematical representation under investigation. They are
not assertions of fundamental separation, nor is producing more oppositions an
objective. The overarching philosophy remains non-dualism. Learning,
interpretability, steerability, and any safety benefit remain separate empirical
questions.

## 1a. External input, predicted output, and supplied target

The external learning data must be explicit. In ordinary supervised learning,
the learner receives pairs (u_r,z_r): input u_r and target output z_r. In the
action-conditioned experiment, the record is (u_r,a_r,z_r), with a_r either
supplied in the dataset or chosen by the agent before the target arrives.
An external signal here is supplied by an offline dataset or isolated simulator;
it does not require connection to a real-world operational system.

The model's prediction and the externally supplied target are different:

\[
u_r\ \longrightarrow\ \operatorname{encode}(u_r)
\ \longrightarrow\ e_r
\ \longrightarrow\ p_W(z\mid e_r,a_r),
\qquad z_r\ \longrightarrow\ \text{loss and update}.
\]

For the first experiment, the input already identifies an observed local
configuration. A constructed encoder maps the visible cue to that configuration:

\[
\xi_i(u_r)\in\{00,10,01,11\},\qquad
q^{\mathrm{in}}_{i,r}(k)=\mathbf1[\xi_i(u_r)=k].
\]

This externally driven input belief loads the source trace through (6). The
symbol q in that equation is q_in at an input event. Noisy inputs can instead
use the known input sensor likelihood and a cue prior to calculate q_in. The
encoder is initially supplied by humans or AI construction; it does not learn
the desired input/output relationship for the agent.

In (9), p_r(s|a) is shorthand for p_W(s|e_r,a,phi_r), where e_r comes from the
external input history. If only the output subset O of the configuration is
supervised, its predictive distribution is

\[
p_W^{\mathrm{out}}(z\mid u_r,a_r)
=\sum_{s:s_O=z}p_W(s\mid e(u_r),a_r,\phi_r).
\]

Here e(u_r) includes the specified cue-to-action delay; in a stream it depends
on the available input history. Sum over unobserved variables rather than
silently supplying their labels. The supervised loss is

\[
\ell_r=-\log p_W^{\mathrm{out}}(z_r\mid u_r,a_r).
\]

The target z_r enters (10) through L(z_r|s)=1[s_O=z_r]. For a directly observed
output opposition i, its posterior marginal is therefore
q_i^*(k)=1[z_{i,r}=k]. The corresponding input-to-output relation learns by

\[
\boxed{
g_{j k'\to i k,r}
=e_{jk',r}c_{ji}(\phi_r)
\left[\mathbf1[z_{i,r}=k]-p_{i,r}(k\mid e_r,a_r)\right]
}
\]

for the selected action. The supplied target is withheld from the encoder,
source traces, and forecast until the prediction has been recorded. It must not
be replaced by the model's own predicted output. Ordinary supervised pairs use
a single dummy action; action selection is unnecessary for that first check.

Four concrete action-conditioned pairs are provided in
[examples/input-output-v1.json](examples/input-output-v1.json):

| External input u | Action a | External target z |
| --- | --- | --- |
| Cue X alone: 10 | left | Success: 10 |
| Cue X alone: 10 | right | Failure: 01 |
| Cue Y alone: 01 | left | Failure: 01 |
| Cue Y alone: 01 | right | Success: 10 |

Cue X/Y and outcome success/failure are different named oppositions, even though
both use two-bit configurations. These rows define a separate deterministic
teaching example for inspecting the learning interface; they are not samples
from, or a change to, the noisy reversal experiment in section 13. Their mapping
is supplied through training examples, not preloaded into W^0. They do not
demonstrate generalization. The learning pipeline first records a prediction
from the input/action fields, then reveals the target field for the update.

Thus the full supervised chain is: external input -> source participation and
trace -> predicted output -> comparison with external target -> fast/slow
relation update. In an interactive trial, the chosen action changes which
target the simulator subsequently supplies.

## 2. Space of opposites

Opposition i has named tendencies X_i and Y_i. A local configuration is

\[
s_i=(x_i,y_i)\in\{00,10,01,11\}.
\tag{1}
\]

These are participation indicators: neither, X alone, Y alone, or both. Y is not
defined as logical NOT-X. The absence of X is the separate condition x_i=0.

For n oppositions, the joint configuration space is

\[
\Omega_0=\{00,10,01,11\}^{n},\qquad |\Omega_0|=4^n.
\tag{2}
\]

An explicitly constructed logical constraint C(s) can restrict an experiment's
support to Omega={s in Omega_0 : C(s)=true}. Constraint changes are external,
logged interventions. Task stages may use different predefined supports; for
example, a result can be absent at cue time and success/failure at outcome time.
An empty support or impossible observation is an experiment failure to inspect,
not permission to silently discard a constraint.

The current belief q(s) is a probability distribution over configurations. It is
uncertainty about the named variables of the current observation or prediction
packet, not a distribution over actions and not a measure of desirability.

Define local indicators and marginals:

\[
f_{ik}(s)=\mathbf1[s_i=k],\quad
q_i(k)=\sum_s q(s)f_{ik}(s),\qquad k\in\{10,01,11\}.
\tag{3}
\]

The omitted 00 indicator is 1 minus the other three. This reference convention
avoids a redundant fourth logit. Pole participations are

\[
m_{iX}=q_i(10)+q_i(11),\quad
m_{iY}=q_i(01)+q_i(11).
\tag{4}
\]

Attention alpha_i in [0,1] makes effective participation alpha_i m_i. It does not
make an event more likely merely because the agent attends to or desires it.
V1 attention is a specified control, not yet a learned policy.

## 3. State, clocks, and phase meaning

The state comprises (q, phi, e, F, S, P). Fixed constructed parameters are W^0.

| Symbol | Meaning | Clock |
| --- | --- | --- |
| q | Belief over the current packet's configurations | Observation / optional internal settling |
| phi_i in the circle | Coordination phase of opposition i | One update after each trial |
| e_ik in [0,1] | Trace of attended local participation | Each simulator tick |
| F_l | Fast retained change to relation l | Each trial boundary |
| S_l | Slow retained change to relation l | Each trial boundary |
| P | Pending prediction and attribution record, or empty | Issue / resolve a prediction |
| W^0_l | Constructed baseline relation | External construction or intervention |

Use t for simulator ticks, r for prediction trials, and u for optional internal
settling time. A trial includes its cue, delay, action, and outcome. Trial-based
retention is a deliberate first choice: doubling an outcome delay does not
automatically double F/S forgetting. Tick-based retention is a later variant.

One phase per opposition controls communication between oppositions:

\[
c_{ij}(\phi)=\frac{1+\cos(\phi_i-\phi_j)}{2},\qquad c_{ii}=1.
\tag{5}
\]

Aligned phases pass a relation fully, a quarter turn passes half, and opposite
phases close it. A relation's sign is in its weight; anti-phase does not itself
mean negative evidence. These are internal coordination phases, not claims
about physical oscillations or the timing of X versus Y within one opposition.

Adding the same angle to all phases changes nothing. One phase can be chosen
as an angular reference. Phase gates and weights can partly compensate for one
another, so their separate meanings require interventions, not just observing
the predictions.

V1 uses a probability simplex and a phase circle, rather than a complex matrix
with an independent phase for each of its four entries. A local matrix of
sqrt(q_i(k)) would only repackage its probabilities. No amplitude interference,
unitary dynamics, or quantum interpretation is assumed.

## 4. Activity traces

For each local non-reference configuration, use

\[
e_{ik,t+1}=(1-\beta_{i,t})\lambda_i e_{ik,t}
             +\beta_{i,t}\alpha_{i,t}q_{i,t}(k),
\quad 0\leq\beta,\alpha\leq1,\quad 0\leq\lambda_i<1.
\tag{6}
\]

The trace remains in [0,1]. beta determines whether this event supplies a new
source to remember. beta=1 loads the attended marginal; beta=0 lets the existing
trace decay. Intermediate values mix old and new participation. Protocol gates
are constructed and logged; they may depend on event type, never a future answer.

With a fully observed cue loaded once, d blank ticks leave lambda^d times its
trace. Missing input has beta=0; it must not be confused with observing state 00.
Reset traces at episode boundaries unless the experiment explicitly tests
cross-episode memory. These traces provide memory of context. A separate
prediction record below preserves attribution after an action has been issued.

## 5. A shared family of predictive relations

The effective relation parameters at trial r are

\[
W_r=W^0+F_r+S_r.
\tag{7}
\]

The source trace e_r is loaded from the external input as defined in section 1a.
For an allowed action a, build a fixed, labelled feature dictionary
Psi(s;e,a,phi). Its possible entries are:

\[
\begin{aligned}
\text{bias: }&\mathbf1[a=b]f_{ik}(s),\\
\text{directed history relation: }&
 \mathbf1[a=b]e_{jk'}c_{ji}(\phi)f_{ik}(s),\\
\text{joint target relation: }&
 \mathbf1[a=b]c_{ij}(\phi)f_{ik}(s)f_{jk'}(s),\quad i<j.
\end{aligned}
\tag{8}
\]

Here b ranges over actions, k and k' over 10,01,11. Include only entries in the
experiment's fixed relation mask; absent entries have no weight. Self-history
relations are allowed. Every entry is in [0,1]. Each named weight has a specific
source, target, action context, and relation type. Intercepts and history effects
can still be statistically confounded in insufficiently varied data.

For a constructed base measure mu_r(s)>0 on the allowed support, define

\[
H_r(s,a)=\langle W_r,\Psi(s;e_r,a,\phi_r)\rangle,
\qquad
p_r(s\mid a)=\frac{\mu_r(s)\exp H_r(s,a)}{Z_r(a)},
\tag{9}
\]

where Z sums the numerator over the allowed support. mu is uniform by default.
It can encode a specified prior, but cannot contain the unknown answer. Use
log-sum-exp in numerical work.

This is a conditional forecast of a later configuration given the available
trace, action, and coordination state. It is not a full hidden-state model of an
arbitrary environment. Traces are a lossy history summary. Using posterior
marginals as source features also loses uncertainty and dependence within the
source history; it is not exact integration over uncertain past states. Exact enumeration
retains joint target dependencies rather than multiplying local marginals;
the selected unary and pairwise log-potentials do not represent every possible
distribution, especially for three or more oppositions.

Retained relations change the probability landscape over a fixed state space.
V1 does not learn a metric, add dimensions, or claim geometric-algebra rotors.

## 6. Evidence and fast inference

An observation o has a specified sensor likelihood L(o|s). After action a_r,
its predictive probability and posterior are

\[
P_r(o)=\sum_s p_r(s\mid a_r)L(o\mid s),\qquad
q_r^*(s)=\frac{p_r(s\mid a_r)L(o\mid s)}{P_r(o)}.
\tag{10}
\]

This is exact Bayes conditioning under the specified conditional model, with
its parameters and source trace fixed. It is not Bayesian inference over W.
Fully observed outcomes use L(o|s)=1[s=o]. Uninformative missing observations
use L=1, giving q*=p and zero learning signal. A deadline at which an expected
event fails to occur can be evidence only if that event/deadline is modelled.

New cues at episode start use a constructed cue prior and the same conditioning
rule, but do not train outcome relations. They load the input traces. This
separates sensing the cue from learning what an action will cause afterwards.

Exact enumeration gives q* immediately. To study fast settling, hold p, L, W,
e, and phi fixed and minimize D_KL(q || q*) with the simplex-preserving flow

\[
\tau_q\dot q_s=q_s\left[
 \log\frac{q_s^*}{q_s}
 -\sum_v q_v\log\frac{q_v^*}{q_v}\right].
\tag{11}
\]

For strictly positive distributions on the same support,

\[
q_s(u)\propto q_s(0)^{\exp(-u/\tau_q)}
                    q_s^{*\,1-\exp(-u/\tau_q)},\quad
\frac{d}{du}D_{KL}(q\Vert q^*)
=-\frac{1}{\tau_q}\operatorname{Var}_q\!\left[\log(q/q^*)\right]\leq0.
\tag{12}
\]

If evidence rules out states exactly, restrict and renormalize to its support
before using this flow. V1 learning uses the exact q*, not a partially settled q.
Internal iterations never multiply by the same likelihood again, advance a
trace, or trigger another weight update. A genuinely new independent sensor
measurement is a new observation even when its numerical value repeats.

## 7. Delayed evidence and the learning signal

At action time, retain one packet

\[
\mathcal P_r=(\mathrm{id},a_r,e_r,\phi_r,W_r,\mu_r,
              \Psi_r(\cdot),p_r(\cdot),\mathrm{deadline}).
\tag{13}
\]

This preserves what the agent actually predicted, with which participating
relations. Until this packet is resolved or cancelled, issue no other forecast
and do not change W, phi, or the feature schema. Simulator ticks may advance and
activity traces may decay; learning uses the saved source trace. External edits
cancel the packet rather than silently assigning its consequence to new weights.

For the returned observation, compute the loss ell_r=-log P_r(o) and the score

\[
g_{l,r}=-\frac{\partial\ell_r}{\partial W_l}
       =\mathbb E_{q_r^*}[\Psi_{l,r}]
        -\mathbb E_{p_r}[\Psi_{l,r}].
\tag{14}
\]

Derivation: differentiate log sum_s mu(s) exp(H(s)) L(o|s) minus log Z.
mu, L, e, and phi are fixed for this derivative. This is an exact gradient of
this conditional prediction's log likelihood; it does not differentiate through
how prior learning generated e. It is not a full gradient through agent history.

For a history relation j,k' -> i,k and the selected action, the score is

\[
g_l=e_{jk'}c_{ji}(\phi)\,[q_i^*(k)-p_i(k)].
\tag{15}
\]

Earlier participation gates a later prediction discrepancy. Mere co-activity
does not produce reinforcement when the prediction is already correct. A
surprising failure can teach as much as a surprising success; desirability is
not multiplied into this probabilistic update.

Resolve each packet once. Store a consumed ID to prevent duplicate learning.
After an uninformative timeout set g=0 and record missing feedback. A variant
may multiply g by a declared delay discount chi(d) in [0,1]; v1 uses chi=1 for
delivered packets. This exact saved-record mechanism handles one delayed
consequence, not general causal credit assignment or multi-step planning.

## 8. Fast and slow retained learning

Choose 0<=rho_f<rho_s<=1, 0<eta_s<eta_f, bounded component boxes B_f and B_s,
and per-relation gates M^f_l,M^s_l in [0,1]. At each resolved trial:

\[
\boxed{\begin{aligned}
F_{r+1}&=\Pi_{B_f}\left(F_r+M^f\odot[(\rho_f-1)F_r+\eta_f g_r]\right),\\
S_{r+1}&=\Pi_{B_s}\left(S_r+M^s\odot[(\rho_s-1)S_r+\eta_s g_r]\right),\\
W_{r+1}&=W^0+F_{r+1}+S_{r+1}.
\end{aligned}}
\tag{16}
\]

Projection clips each component to its declared interval. A zero gate freezes
both learning and decay for that component. W^0 is changed only by a logged
construction edit. To lock an effective relation, freeze both retained parts
and its constructed baseline. Masks and bounds are not learned in v1.

F and S learn from the same discrepancy in parallel. F reacts more strongly and
forgets faster; S reacts less strongly and persists longer. There is no assumed
transfer of F into S and no claim that two rates are always better than one.
Fast belief settling, an activity trace, and fast retained learning are three
different mechanisms.

A subsequent [consolidation proposal](maths-v1-consolidation.md) adds selected
fast-to-slow transfer. The equations here remain the parallel-learning baseline.

The rule has a direct optimization derivation. With the source trace and phase
held fixed, define

\[
\begin{aligned}
\mathcal J_r(F,S)&=\ell_r(W^0+F+S)
       +\frac{\gamma_f}{2}\|F\|^2+\frac{\gamma_s}{2}\|S\|^2,\\
\gamma_f&=(1-\rho_f)/\eta_f,\qquad
\gamma_s=(1-\rho_s)/\eta_s.
\end{aligned}
\tag{16a}
\]

Then grad_F J=-g+gamma_f F and grad_S J=-g+gamma_s S. Taking a gated,
projected gradient step with step sizes eta_f and eta_s gives (16) exactly.
Decay therefore regularizes retained changes toward the constructed baseline.
Learning rate and retention are separate choices; the regularization strengths
need not be equal. Adding V gives the phase objective used in section 9. This
is one coupled objective for a fixed prediction packet, not a proof that the
whole adaptive action loop optimizes a single unchanging objective.

With open gates, no projection, and missing feedback, after k no-feedback trials
F_{r+k}=rho_f^k F_r and S_{r+k}=rho_s^k S_r. If rho_s=1, slow memory persists
without feedback. Silent trials must be explicitly scheduled; ordinary blank
ticks inside a pending trial only advance the activity trace.

With zero decay and open gates, the effective update is
Delta W=(eta_f+eta_s)g. If the two retention factors are also equal, the effective
weights follow a single-rate rule. Thus splitting a weight into two components
alone supplies no behavioral advantage; different retention and history matter.

For a binary target with p=sigmoid(w x), g=x(y-p). Holding x fixed, its negative
log likelihood has curvature x^2 p(1-p)<=x^2/4. An unprojected single effective
gradient step with 0<eta_f+eta_s<8/x^2 decreases this scalar loss unless its
gradient is zero. This is a restricted sanity check, not a convergence theorem
for joint phase/weight learning, partial observations, decay, or the action loop.

The scalar fast/slow subsystem also admits a local stability check. At an
interior stationary point with fixed x and loss curvature h>=0, open gates,
and no active projection, its linearized update matrix is

\[
A=\begin{pmatrix}
\rho_f-\eta_f h&-\eta_f h\\
-\eta_s h&\rho_s-\eta_s h
\end{pmatrix}.
\tag{16b}
\]

For rho_f,rho_s<1, a sufficient contraction condition is
(1-rho_f)+(1-rho_s)+(eta_f+eta_s)h<2. To see this, rescale the two coordinates
by their square-root step sizes: I-A becomes similar to a symmetric positive
definite matrix with that trace. A trace below 2 puts both its eigenvalues
between 0 and 2. For the declared scalar settings and |x|<=1, the trace is at
most 0.106. This check covers a stationary scalar subsystem, not all coupled
features or the nonstationary experiment.

## 9. Coordination and its coupling to inference

Let the constructed coordination potential be

\[
V(\phi)=-\sum_{i<j}\kappa_{ij}
                  \cos(\phi_i-\phi_j-\delta_{ij}),\quad\kappa_{ij}\geq0.
\tag{17}
\]

delta=0 prefers alignment; delta=pi prefers separation by half a cycle. More
than two nodes can have incompatible preferred offsets, so coordination does
not require universal agreement. V is a stated coordination preference, not
external sensory evidence. Its parameters are constructed in v1.

The prediction supplies a phase score at the saved phi_r and W_r:

\[
h_{i,r}=\mathbb E_{q_r^*}[\partial_{\phi_i}H_r]
        -\mathbb E_{p_r}[\partial_{\phi_i}H_r].
\tag{18}
\]

Because d c_ij / d phi_i = -sin(phi_i-phi_j)/2, this is explicit from the
feature dictionary. After computing all scores at the old state, update

\[
\phi_{r+1}=\operatorname{wrap}\left(
 \phi_r+\eta_\phi A^\phi\odot[h_r-\nabla V(\phi_r)]\right).
\tag{19}
\]

A^phi in [0,1]^n is a phase gate. A zero gate freezes that phase. With missing
feedback h=0, the constructed potential can still relax the phases. For a pure
no-feedback weight-retention probe, freeze phases so their drift does not
confound the result.

This is the explicit two-way coupling: phase changes future predictive
relations through c; an inferred discrepancy changes subsequent coordination
through h. It is not repeated use of the same evidence as independent data.
The update is a partial gradient step on ell+V at fixed weights and trace.
Simultaneous finite steps in weights and phase have no general monotonic-loss
guarantee. Record the step sizes and inspect failures.

With h=0, two nodes, delta=0, and open gates, their phase difference obeys
Delta'=Delta-2 eta_phi kappa sin(Delta). Alignment is locally stable when
0<eta_phi kappa<1. Exactly anti-aligned phases have zero first derivative and
can remain stuck there in exact arithmetic; use a declared nondegenerate
initial phase for the main experiment. Freeze c=1 in the no-phase baseline.

Inertia here means retained state and persistence, not momentum. Noise is absent
from the core updates; controlled action sampling provides behavioral variation.
Phase noise, explicit momentum, and learned preferred offsets are deferred.

## 10. Significance, action, and the environment

Construct bounded concern functions U_d(s,a), an ordered list of priorities,
and a nonempty allowed action set A_ok. Preserve the vector

\[
v_d(a)=\sum_s p_r(s\mid a)U_d(s,a).
\tag{20}
\]

Use lexicographic maximization of this vector as the initial arbitration rule.
Let B be the tied maximizers. The action policy is

\[
\pi(a)=(1-\epsilon)\operatorname{Unif}(B)(a)
                  +\epsilon\operatorname{Unif}(A_{ok})(a).
\tag{21}
\]

Exploration never leaves A_ok. A fixed priority order is a constructed choice,
not a learned resolution of values. V1's first task has only one concern. The
vector form leaves room for conflicting concerns without treating probabilities
as utilities. A difference matters operationally when it changes a forecast,
a concern expectation, or a selected action under specified conditions.

The isolated simulator generates an outcome from its own mechanism
s_out ~ T_env(.|context,a), then an observation from its sensor. T_env is not
available to the learner. The model forecasts the outcome, chooses an action,
receives its consequence, and changes its later forecasts and choices. This is
an action loop with a learned predictor and constructed decision rule, not a
general reinforcement-learning or causal-discovery algorithm.

Randomized action exploration makes the first toy action comparisons possible.
It does not establish that every internal predictive relation is causal.

## 11. One complete trial and a worked update

1. Receive external input u_r from a dataset or simulator. Reset episode traces;
   encode the input into q_in directly, or condition a specified cue prior.
2. Load attended cue marginals using (6); let traces decay during blank ticks.
3. Enumerate p(s|a) for each allowed action using the current F, S, and phi.
4. For a supplied training pair, use its action (or a dummy action). For an
   interactive trial, choose an action with (21) and issue it to the simulator.
   Save the prediction packet before revealing the target.
5. Receive the external target z_r or reach the deadline; do not update
   parameters while the target is pending.
6. Resolve the packet using (10), then compute g and h from its saved quantities.
7. Update F, S, and phi once using those old-state scores, log the result, and
   mark the packet consumed. Subsequent packets use the new parameters.

For a fully observed binary outcome, let x=1, W^0=F=S=0, so p=0.5. Observe y=1.
Then g=0.5. With eta_f=0.20 and eta_s=0.02, open gates and inactive bounds,
F'=0.10, S'=0.01, and the next prediction in the same context is
sigmoid(0.11)=0.5274723. Decay makes no contribution on this first zero-state
step. This illustrates the algebra, not evidence of useful learning.

If this was the left action's sole active outcome feature and the right
action's forecast remains 0.5, the same context now favors left. With success
as the concern and epsilon=0.1, the next action probabilities are left=0.95,
right=0.05. Thus retained evidence changes a forecast and, through the stated
decision rule, changes subsequent action.

If the history feature is x=lambda^d c, the same initial observation gives
g=lambda^d c/2. No surviving source trace means no update to that history
relation, though a bias may still learn. A delay after issuing the prediction
does not erase its stored feature; this distinguishes remembering the cue before
action from assigning feedback to a forecast after action.

## 12. Geometry, interpretation, and controlled construction

The state space is a probability simplex over allowed configurations, phase
circles, bounded trace coordinates, and boxes of fast/slow weights. The support
and allowed feature graph are fixed geometry. Retained weights change the
predictive landscape; they do not alter the underlying dimensions in v1.

For configurations s and v with positive base measure,

\[
\log\frac{p(s)}{p(v)}
=\log\frac{\mu(s)}{\mu(v)}
 +\sum_l W_l[\Psi_l(s)-\Psi_l(v)].
\tag{22}
\]

This is an exact, inspectable decomposition of conditional log odds. Its terms
can be labelled, plotted, and changed in isolation. It supports a limited form
of interpretation, not a guarantee of uniquely identifying mechanisms or
understanding all behavior. Inspectability does not establish safety.

Expose interventions between trials: freeze F or S; edit a baseline weight;
clamp a phase; disable an allowed relation; change attention; or revise concern
priorities. Log actor (human/AI), reason, old/new values, and predicted effect.
Recompute forecasts and test the effect. Construction and experience are both
valid routes, but report their contributions separately.

## 13. Analytic checks and bounded experiments

### Mathematical checks

- Enumerated probabilities and posteriors sum to one and respect support.
- One observation with prior (0.5,0.5) and likelihood (0.8,0.2) gives (0.8,0.2).
  Additional settling approaches that target, not (0.941176,0.058824).
- Finite differences agree with (14) and (18), including an informative noisy
  sensor case. Check both source and target phase signs.
- Traces remain bounded; blank ticks decay memory without asserting state 00.
- Zero learning gates freeze their components, and no-feedback retention follows
  the geometric powers stated above.
- A common phase rotation changes neither probabilities nor V.
- A pair interaction can create a dependent joint distribution even when the
  marginals alone would miss that dependence.
- For a fixed state, editing one relation changes log odds exactly by (22).

The reproducible standard-library audit is
[checks/maths_v1_audit.py](checks/maths_v1_audit.py), run with
`python3 checks/maths_v1_audit.py`. On 2026-10-12 it passed the numerical checks
for normalization, exact gradients under full/noisy/missing observations,
anchored settling and KL dissipation, trace bounds, retention and frozen gates,
phase invariance and local pair stability, joint dependence, and log-odds
interventions. Across 102 feature parameters on 16 joint configurations, the
largest checked gradient discrepancy was below 2e-10. The worked update gave
0.5274723043. These checks audit identities; they do not test useful learning,
general convergence, or the proposed experiment's success criteria.

### First learning experiment: cue, gap, choice, consequence

Use two named oppositions: cue (X/Y) and outcome (success/failure). Each uses only
10 or 01 when present; both/neither remain available in the general model.
The task protocol, not a universal law of opposites, supplies this restriction.

A trial samples cue X or Y uniformly, shows it once, inserts d=2 blank ticks,
then asks for action left or right. After two further ticks, the simulator emits
success with probability 0.9 for (X,left) or (Y,right), and 0.1 otherwise.
After 200 trials, reverse the mapping for 200 trials. The learner sees only the
cue, event timing, its action, and the success/failure observation. It is not
given the mapping, success probabilities, or reversal flag.

For outcome forecasts, allow cue configurations freely with fixed uniform base
measure and restrict the outcome to success/failure. Include only an
outcome-success bias and cue-trace -> outcome-success weights, separately per
action; failure has reference score zero. This also removes the redundant
success/failure logits on the restricted support. Cue variables in the
forecast are nuisance variables summed out; no present or hidden cue may be
inserted into the base measure after the gap. Construct the success concern
U=1 for success and 0 for failure. Cue events load cue traces; outcome events do
not overwrite them. There are no outcome-to-cue or joint-target learned edges
in this first task. Both/neither and joint dependencies get separate math probes.

Use W^0=F=S=0; lambda=0.8; alpha=1; beta=1 at the cue and 0 during gaps;
rho_f=0.95; rho_s=0.999; eta_f=0.20; eta_s=0.02; each component bound [-8,8];
open weight gates; phi_C=0, phi_O=pi/2; eta_phi=0.05; kappa_CO=0.1;
delta_CO=0; epsilon=0.10. These are declared starting values, not tuned results.
The deadline is four ticks after the action; ordinary outcomes arrive after two.

Predeclare seeds 0 through 4, five variants, and one conventional comparator:

1. Full model.
2. No activity trace: erase cue memory before action, keeping other settings.
3. Frozen weights: F=S=0 throughout.
4. No phase: c=1 throughout; no phase update, otherwise identical.
5. One learning timescale, with the full model's phase mechanism: replace F+S
   by one retained component, rho=0.999, eta=0.22, bounds [-16,16].
6. Conventional logistic predictor with the same cue traces, per-action biases
   and cue coefficients, one retained weight set, rho=0.999, eta=0.22, bounds
   [-16,16], and the same action policy. It has no phase dynamics.

This budget is 12,000 training trials. Use paired simulator randomness where
possible and report all five seeds. At trials 0, 200, and 400, evaluate frozen
snapshots for every variant with 100 balanced-cue trials each, fixed weights and
phases, and epsilon=0. These 9,000 probe trials make the total cap 21,000.
Probe the pre-reversal mapping at trials 0 and 200 and the reversed mapping at
trial 400. Probes do not alter training state or consume its random stream.
No hyperparameter search is
included. Failed numerical invariants stop a run. Unexpected behavior or a
need for additional variants requires a recorded revision of the experiment.

Report prequential outcome log loss, success rate, phase/gate trajectories,
fast/slow weight trajectories, and performance in each 50-trial block after
reversal. Primary learning evidence: for at least four of five seeds, the full
model's final-50-trial loss in each regime is below log(2) and the corresponding
frozen probe has success rate at least 0.70. Compare the same metrics against
all baselines; these thresholds are small-experiment criteria, not significance
claims or evidence of broader capability.

An activity-trace contribution requires better delayed-task performance than
the no-trace ablation. A phase contribution requires a reproducible benefit
over c=1, not just visible phase movement. A two-timescale contribution requires
benefit over the matched-phase one-timescale variant. The conventional predictor
also removes phase and tests the value of the combined design. Comparing one
declared single-rate setting cannot establish superiority over all such models.
If the full model learns but does not outperform simpler controls, report that
result and prefer the simpler explanation. Five seeds do not settle robustness.

For steering, use frozen snapshots to set a selected relation to zero and compare
the forecast change with (22); restore it afterwards. For delayed attribution,
verify that the same issued packet produces the same update when its observation
arrives later, within the deadline. Cancelled, missing, or duplicate packets
must not create another learning event.

## 14. Correspondences, limitations, and next decisions

| Connection | Status in this v1 |
| --- | --- |
| Bayes conditioning | Exact equation (10), conditional on the chosen model and fixed parameters |
| Exponential-family moment matching | Exact score (14); full-target loss is convex in W at fixed features, noisy partial-target loss need not be |
| Error-modulated association | Equation (15) is an exact special case here; it is not a derived Grossberg or Weber–Hebb rule |
| Fast/slow adaptation | Design motivated by parallel error-sensitive processes with different retention; no biological identification |
| Phase oscillator | Exact two-node sine-coupling restriction of (19); no claimed HKB reduction |
| Eligibility traces | Activity traces plus a saved prediction record; no claim of TD(lambda) equivalence or general causal credit |
| ART, R-rule, geometric algebra, Friston | No correspondence established; their inclusion is deferred pending precise definitions and useful derivations |

The fast/slow design has a primary-source precedent in Smith, Ghazizadeh, and
Shadmehr (2006), who studied two adaptive processes with different error
sensitivities and retention. Their task and error model differ from ours; this
is motivation for a testable design, not evidence for this agent. See
[Interacting Adaptive Processes with Different Timescales Underlie Short-Term Motor Learning](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.0040179).

V1 leaves open: whether phase earns its additional complexity; whether two
retention rates improve this task; how to learn attention and concerns; how to
assign unlabelled delayed feedback among many earlier actions; and how to change
the distinctions themselves. A finite dictionary and known sensor model supply
substantial structure. Success would establish only that this specified small
learner works under its tested conditions. It would not establish a new LLM,
general intelligence, a formalization of non-dualism, or safe scaling.

The next implementation should reproduce the equations and the declared tests.
Change the specification explicitly when evidence calls for a different model.
