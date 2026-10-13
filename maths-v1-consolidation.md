# Proposed extension: fast/slow IVSR with consolidation

Status: mathematical proposal, 2026-10-13. This extends
[maths-v1.md](maths-v1.md); it does not silently replace its parallel-learning
baseline or its experiment plan.

## 1. What needs to change

V1 has W=W^0+F+S. Fast and slow retained components learn from the same external
prediction error, but S does not receive what F has learned. Different rates
alone do not create that relationship.

The proposed extension adds selected transfer from fast to slow retention.
Both timescales can use inertial variation, selection, and retention (IVSR),
with different update intervals and evidence windows:

| Function | Fast timescale | Slow timescale |
| --- | --- | --- |
| Inertia | Current relations and traces bias the next prediction and candidate update | Retained relations bias later learning and which fast changes are worth preserving |
| Variation | New input/target discrepancies propose changes; sampled actions expose new consequences | Fast learning supplies candidate persistent changes; several histories can supply alternatives |
| Selection | Prediction loss supplies an error-directed update | External evaluation selects fast changes that improve a predictor using slow weights |
| Retention | F and activity traces carry effects across nearby events | S preserves selected changes for longer |

These are operational roles, not a claim that gradient learning is identical to
population evolution. Explicit random parameter proposals are optional future
variants; encountering variation through data and actions already occurs in v1.
Inertia still means history dependence, not an added momentum variable.

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

Every K completed trials, with no pending feedback, propose transferring part
of the fast residual. Let 0<=kappa<=1 be the transfer fraction and R in [0,1]^L
an external transfer mask. R_l must be zero if either retained component of
that relation is locked. Start with

\[
T^{\mathrm{raw}}=\kappa R\odot\widetilde F.
\]

Construct a feasible transfer T using the bounds below. Let a selection gate
m in {0,1} accept or reject the whole proposed transfer, and set C=mT. Then

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
D_k=\mathcal L_{V_k}(W^0+\widetilde S)
 -\mathcal L_{V_k}(W^0+\widetilde S+T),\qquad
m=\mathbf1[D_k>\delta],\quad\delta\geq0.
\]

This is a proposed selection rule: accept only when the feasible transfer
improves external prediction by more than the declared margin. Evaluate the
whole vector T; separately beneficial edits need not be beneficial together.
The combined predictor cannot select a transfer by immediate loss improvement,
because its prediction is exactly conserved by that transfer.

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
new run, specify the transfer interval, fraction, margin, selection-data
budget, and total trial cap. Compare parallel learning with and without
consolidation under matched data budgets. Include a consolidation-only slow
variant to identify whether useful fast learning reaches S, and an ungated
transfer control to test whether selection matters.

Check exact immediate prediction conservation at fixed context and phase.
Evaluate slow-weight prediction on untouched probes, retention after fast
memory decays, and revision after an environmental reversal. The mechanism is
supported only if useful retention improves without unacceptable loss of
adaptability under the declared criteria. More transfers or longer persistence
alone are not evidence of better learning.

This same proposal-selection-retention organization can later be applied to
more timescales or structural changes. It does not require identical state
variables or identical evidence windows at every level. No such extension or
additional learning experiment has been run here.
