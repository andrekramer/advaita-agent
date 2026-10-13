# Proposed extension: fast/slow IVSR with consolidation

Status: mathematical proposal, 2026-10-13. This extends
[maths-v1.md](maths-v1.md); it does not silently replace its parallel-learning
baseline or its experiment plan.

## 1. What needs to change

V1 has W=W^0+F+S. Fast and slow retained components learn from the same external
prediction error, but S does not receive what F has learned. Different rates
alone do not create that relationship.

The proposed extension adds selected transfer from fast to slow retention.
**IVSR means Inertial Variation, Selection, and Retention.** Both timescales can
use this pattern, with different update intervals and evidence windows:

| Function | Fast timescale | Slow timescale |
| --- | --- | --- |
| Inertia | Current relations and traces bias the next prediction and candidate update | Retained relations bias later learning and which fast changes are worth preserving |
| Variation | New input/target discrepancies propose changes; sampled actions expose new consequences | Fast learning supplies candidate persistent changes; several histories can supply alternatives |
| Selection | Prediction loss supplies an error-directed update; the fast/slow response gap exposes candidate changes | Current and smoothed response differences trigger consideration; external evaluation selects changes that improve the slow-weight predictor |
| Retention | F and activity traces carry effects across nearby events | S preserves selected changes for longer |

These are operational roles, not a claim that gradient learning is identical to
population evolution. Explicit random parameter proposals are optional future
variants; encountering variation through data and actions already occurs in v1.
Inertia still means history dependence, not an added momentum variable.

The slow component is an important source of inertia, but inertia is not
exclusive to it; fast activity and traces also have history. Likewise, slow
learning can vary, and fast learning can retain. The differential is the
interface between these relative timescales, not a separate source of truth.

## 1a. Define the fast/slow response differential

Compare responses to the same available input and action, not the magnitudes of
F and S in isolation. At consolidation boundary k, freeze the preliminary
weights and use a predeclared finite probe set U of contexts c=(e(u),a). Each
context contains only available input history. Use identical phases, feature
schema, allowed output support, base measure, and attention in both responses:

\[
\begin{aligned}
N_k(z\mid c)&=p^{\mathrm{out}}_{W^0+\widetilde S}(z\mid c),\\
A_k(z\mid c)&=p^{\mathrm{out}}_{W^0+\widetilde S+\widetilde F}(z\mid c).
\end{aligned}
\]

N is the slow-weight response; A is the fast-adapted response built on that
background. A is not a predictor made from F alone. These are two evaluations
of the same conditional model, not two newly introduced architectures.

Keep the signed prediction gap for interpretation:

\[
\Delta_k(z\mid c)=A_k(z\mid c)-N_k(z\mid c),\qquad
\sum_z\Delta_k(z\mid c)=0.
\]

Use total variation distance as the first scalar measure of tension:

\[
\boxed{
D_k(c)=\frac12\sum_z|\Delta_k(z\mid c)|,\qquad
D_k=\frac{1}{|U|}\sum_{c\in U}D_k(c).
}
\]

Both are in [0,1]. Zero means identical output predictions on the compared
contexts. For a binary output, D_k(c)=|A_k(success|c)-N_k(success|c)|. This has
a direct probability interpretation and requires no normalization of weight
vectors. Unlike the signed gap, it loses which outcome the fast response favors,
so retain both quantities in the logs. This scalar measures predictive
disagreement, not desirability or the importance of an outcome. A rare but
important difference can be diluted by the context average; inspect individual
contexts and test probe coverage rather than treating a threshold as universal
relevance. Phase divergence is not a second metric in this proposal: v1 has a
shared phase state, held common in these comparisons.

Track the differential across successive consolidation boundaries:

\[
\overline D_k=(1-\nu)\overline D_{k-1}+\nu D_k,
\qquad 0<\nu\leq1,\qquad\overline D_0=0.
\]

This is a smoothed diagnostic, not a posterior probability or a count of
independent evidence. Use the same probe contexts to make changes comparable;
version and reset the diagnostic if their distribution, schema, or action set
changes. The probe set has no targets and cannot certify usefulness. Record
its coverage: a nonzero F can be invisible on these probes.

With a declared threshold 0<tau_D<1, define a candidate-trigger gate

\[
b_k=\mathbf1[D_k>\tau_D]\,
     \mathbf1[\overline D_k>\tau_D].
\]

The first factor requires a current difference; the second favors an accumulated
difference. An exponential average does not guarantee a fixed number of
consecutive disagreements. K, nu, tau_D, and the probe contexts are fixed
experiment settings. Lowering the threshold because no candidate passed would
be a documented change to the experiment, not an automatic learner action.

This makes the differential operational: it drives whether consolidation is
considered. It does not replace v1's externally grounded fast learning signal.
No human supervisor is required when later observations supply the targets;
some informative interaction or data is still needed to test a hypothesis.

## 1b. What the differential does and does not establish

Prediction error compares a model with an external observation. The response
differential compares two timescales within the model. They have different
jobs: the latter identifies unsettled learning; the former grounds adaptation
and evaluates whether a retained change helps.

A large differential can indicate adaptation, a transient disturbance,
misspecification, or a fast learner's mistake. A small differential can mean
agreement between two correct responses or between two wrong ones. The absence
of a slow response is not evidence that an input is noise, and persistent
disagreement does not by itself prove a lasting environmental shift.

Therefore stable resonance, persistence, or reduced disagreement alone cannot
select a useful change. Constant wrong outputs could eliminate disagreement.
The paired transfer below naturally brings slow weights toward the fast-adapted
weights, but it is retained only with supporting external evidence. No blanket
claim is made that conventional learning always uses human labels or a static
loss, or that this proposal eliminates prediction-error learning.

Differences between timescales remain relative, operational distinctions. Their
use is consistent with the project's non-dual framing; this metric does not
itself create or collapse dimensions, which remain later investigations.

## 2. Learn from external pairs, then consolidate

First perform the original per-trial updates, including its gates and bounds:

\[
\begin{aligned}
\widetilde F&=\Pi_{B_f}\bigl(F+M^f\odot[(\rho_f-1)F+\eta_f g]\bigr),\\
\widetilde S&=\Pi_{B_s}\bigl(S+M^s\odot[(\rho_s-1)S+\eta_s g]\bigr),
\end{aligned}
\]

where, for an input-to-output relation, the externally driven score remains

\[
g_{j k'\to i k}
=e_{jk'}c_{ji}(\phi)
\bigl(\mathbf1[z_i=k]-p_i(k\mid u,a)\bigr).
\]

Every K completed trials, with no pending feedback, calculate the response
differential. When b_k=1, propose transferring part of the fast residual; when
b_k=0, set C=0 and do not spend a selection batch on that boundary.
Let 0<=kappa<=1 be the transfer fraction and let R in [0,1]^L be
an external transfer mask. R_l must be zero if either retained component of
that relation is locked. Start with

\[
T^{\mathrm{raw}}=\kappa R\odot\widetilde F.
\]

Construct a feasible transfer T using the bounds below. Let a selection gate
m_k in {0,1} accept or reject the whole proposed transfer, and set C=m_k T. Then

\[
\boxed{
S^+=\widetilde S+C,\qquad
F^+=\widetilde F-C.
}
\]

On other trials set C=0. K and kappa are specified before an experiment; they
do not adapt themselves in this proposal. Larger K makes selection and transfer
less frequent. Smaller kappa makes the transfer more gradual.

The two transfer terms cancel in the effective relation:

\[
W^+=W^0+F^++S^+=W^0+\widetilde F+\widetilde S.
\]

Thus the slow component learns from the fast component without immediately
counting that learning twice. At a fixed input trace, phase, and action,
consolidation leaves the combined prediction unchanged. The change is in how
long the learned relation will persist. Copying F into S while leaving F
unchanged would instead change the effective predictor immediately.

This conservation concerns consolidation only. The preceding external-error
updates, phase updates, future decay, or later interventions may change the
prediction. Transfer changes the allocation of memory, so it is not claimed to
be a gradient descent step on v1's original regularized objective.

## 3. Select transfers using external evidence

A fast change is a candidate for retention, not an independently verified
target. Its magnitude, repetition, or agreement with itself is insufficient.

At a transfer boundary, freeze the proposed weights and phases. On a separate,
finite selection set V_k of external input/action/target records, calculate

\[
\mathcal L_{V_k}(W)
=-\frac{1}{|V_k|}\sum_{(u,a,z)\in V_k}
\log p_W^{\mathrm{out}}(z\mid u,a).
\]

Use the same input encodings, traces, phases, and base measures for both
evaluated predictors. Source features must be built without the target. Compare
the slow-weight predictor before and after the proposed transfer:

\[
G_k=\mathcal L_{V_k}(W^0+\widetilde S)
 -\mathcal L_{V_k}(W^0+\widetilde S+T),\qquad
m_k=b_k\,\mathbf1[G_k>\delta],\quad\delta\geq0.
\]

Here D is internal response disagreement and G is externally measured selection
gain; they must not share a name or be treated as interchangeable quantities.
This is a proposed selection rule: accept only when the differential gate is
open and the feasible transfer improves external prediction by more than the
declared margin. When b_k=0, set m_k=0 without evaluating G_k. Evaluate the
whole vector T; separately beneficial edits need not be beneficial together.
The combined predictor cannot select a transfer by immediate loss improvement,
because its prediction is exactly conserved by that transfer.

For example, let N(success)=0.5. Fast responses A(success)=0.8 and 0.2 both
have D=0.3. In a one-context binary logistic model, transferring half the fast
logit residual produces slow success probabilities 2/3 and 1/3, respectively.
On a selection example whose external target is success, their gains are
log(4/3)>0 and log(2/3)<0. With an open differential gate and delta=0, the first
transfer is accepted and the second rejected despite identical disagreement.
This is an algebraic illustration, not an adequately sized validation dataset.

Selection data must not be the same examples just used to fit the candidate
fast change. They still influence learning through acceptance and therefore are
not an untouched test set. Use separate final probes, report selection costs,
and bound the number of proposals. Finite selection evidence can still be noisy
or fail to represent future conditions; no generalization guarantee follows.

For isolating this mechanism, a declared consolidation-only variant can set
eta_s=0 while retaining slow decay. Then every new slow-weight change comes from
selected fast learning. A hybrid variant keeps direct slow learning eta_s>0.
This is an explicit extension of v1's positive-rate assumptions.

## 4. Respect bounds without breaking conservation

Independent clipping after transfer can break F+S conservation. Instead clip
the transfer itself to an interval feasible for both components. If the bounds
are F_l in [-b_f,b_f] and S_l in [-b_s,b_s], define

\[
\begin{aligned}
L_l&=\max(-b_s-\widetilde S_l,\ \widetilde F_l-b_f),\\
U_l&=\min( b_s-\widetilde S_l,\ \widetilde F_l+b_f),\\
T_l&=\operatorname{clip}(T_l^{\mathrm{raw}},L_l,U_l).
\end{aligned}
\]

Since the preliminary components are already feasible, zero belongs to each
interval. A locked component therefore remains untouched when R_l=0. Evaluate
this clipped proposal before accepting it. The final paired transfer needs no
further clipping.

## 5. Why the change matters later

With open decay gates, no new error updates or further transfers, and unchanged
retention factors, compare a consolidated state with its untransferred control.
After d trial boundaries their effective weights differ by

\[
\boxed{
W_{\mathrm{consolidated}}(d)-W_{\mathrm{control}}(d)
=(\rho_s^d-\rho_f^d)C.
}
\]

At d=0 the difference is zero. With rho_s>rho_f, the transferred part persists
longer in its signed direction. That can preserve a useful relationship or
preserve a mistaken or obsolete one; reversal experiments are essential.

For example, let F=0.4 and S=0.1 after the external-error update. An accepted
quarter transfer gives C=0.1, F^+=0.3, and S^+=0.2. Both states initially sum
to 0.5. With rho_f=0.95 and rho_s=0.999, one no-feedback trial gives 0.4848
after consolidation, compared with 0.4799 without it. The difference 0.0049
is exactly (rho_s-rho_f)C. These are memory calculations, not learning results.

## 6. What would establish a useful extension

Keep the fixed distinction space and isolated, small-scale scope. Before any
new run, specify the transfer interval, fraction, selection margin, probe set,
smoothing rate, differential threshold, selection-data budget, and total trial
cap. Compare parallel learning with and without
consolidation under matched data budgets. Include a consolidation-only slow
variant to identify whether useful fast learning reaches S. Remove only the
differential trigger in one control while keeping external selection unchanged;
this tests whether the new trigger adds value. An external-selection-free
transfer control tests whether evidence-based selection matters. Account for
differences in data usage when a gate skips selection batches.

Check exact immediate prediction conservation at fixed context and phase.
Check the differential's range, zero for identical responses, signed-gap
normalization, and response to both transient and repeated disagreement. Use
cases where equally large differentials support opposite correct/incorrect
directions, and cases where both timescales agree but are wrong. These prevent
mistaking disagreement for learning or agreement for correctness.
Evaluate slow-weight prediction on untouched probes, retention after fast
memory decays, and revision after an environmental reversal. The mechanism is
supported only if useful retention improves without unacceptable loss of
adaptability under the declared criteria. More transfers or longer persistence
alone are not evidence of better learning.

This same proposal-selection-retention organization can later be applied to
more timescales or structural changes. It does not require identical state
variables or identical evidence windows at every level. No such extension or
additional learning experiment has been run here.

## 7. Mathematical audit

Run `python3 checks/ivsr_consolidation_audit.py` for the reproducible checks of
the differential, smoothing and trigger, external-selection counterexample,
bounded transfer, prediction conservation, and delayed retention identity.
These are mathematical checks, not a learning experiment or evidence that the
proposed trigger improves adaptation.
