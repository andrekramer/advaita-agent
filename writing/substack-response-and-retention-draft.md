# Advaita-agent: a more minimal enquiry into learning

*Distinctions, retained history, and the first small experiments in how a response becomes something that lasts.*

My work on attention expanded quickly. What began as a way to investigate
learning became an architectural programme larger than I could reasonably pursue
alone, even with AI assistance. There were more mechanisms to build, more
interactions to understand, and more experiments needed to tell whether the
complexity was justified. I've experienced that in my career in software and I 
suspect AI researchers in the commercial labs can get caught up too.

Advaita-agent is a consolidation of that enquiry at a smaller scale. I want to
keep the philosophical questions close to the mathematics, and keep the
mathematics close enough to an implementation that its consequences can be
examined.

The aspiration remains a system that **can learn, can be interpreted, and can be
steered**. Those are three separate things to investigate. So far, the experiments
address a small part of the first.

The question running through the project is this:

**How does what a system has retained shape its present response, and how can
present experience change what it retains?**

## Why call it advaita-agent?

Non-dualism is the philosophical starting point. A distinction can help us
investigate experience without establishing that the things distinguished are
fundamentally separate.

The aim is to explore differences that matter. Sometimes that may require a new
distinction. Sometimes it may require changing a distinction, combining several,
or letting one go. Increasing the number of oppositions is not an objective.

This leaves some questions deliberately open. What makes a difference matter to
a system? How much of that significance comes from the system, and how much from
the person who supplied its categories and goals? What would count as the system
revising its own distinctions?

For a first experiment, I have fixed the distinctions. This makes their role
easier to inspect, while postponing the harder question of how they might change.
Humans and AI agents can construct the initial representation and propose later
revisions. Changes supplied by a designer must remain distinguishable from
learning achieved by the running system.

## A response and its history

I use **R-rule** as a name for a perspective on agency and learning: a system
reorients through the interaction of its tendencies, the constraints it
encounters, and its present state. A changed state then affects how the system
can respond again. This perspective leaves room for different mathematical
implementations.

**Inertial Variation, Selection, and Retention—IVSR—** brings the history of that
process into view:

- **Inertia:** retained structure biases what can happen next.
- **Variation:** experience or a proposal makes a change available.
- **Selection:** consequences provide grounds for keeping or rejecting a change.
- **Retention:** something of the change persists and shapes later possibilities.

Together, these suggest a common scheme: current responses develop within
retained constraints, while their consequences can revise those constraints.
The terms describe interacting functions. Fast processes retain information;
slow processes can vary. Neither timescale has a monopoly on inertia or learning.

The implementation below makes one part of this scheme concrete. It learns
predictions from externally supplied examples and redistributes learned weights
between two timescales. It does not yet choose actions, generate its own concerns,
or revise its vocabulary. Calling the project an agent does not establish that
this first learner has those capacities.

## Starting with four states

Take two named tendencies, X and Y. Let each be either participating or absent.
Their joint state is

\[
s=(x,y)\in\mathcal K=\{00,10,01,11\}.
\]

| State | Meaning |
| --- | --- |
| 00 | Neither X nor Y participates |
| 10 | X participates alone |
| 01 | Y participates alone |
| 11 | Both participate |

Y is not defined as the logical negation of X. Both may participate, and both
may be absent. Observing “neither” is also different from receiving no observation.

The experiment uses one such variable for the input and a separate one for the
output. It learns a mapping between them. At this stage, the four states are
treated as four categories: the model has not learned a compositional logic of
“both” or “neither.” Their names do not confer that ability.

## From an external example to a prediction

Each training example is a pair \((u,z)\): input \(u\) and target output \(z\),
both drawn from \(\mathcal K\). The learner sees \(u\), records a prediction,
and only then receives \(z\). The target comes from an isolated teaching
environment, not from the learner's own prediction.

For input category \(j\), define an indicator

\[
a_j(u)=\begin{cases}1,&u=j,\\0,&u\ne j.\end{cases}
\]

This is a one-hot encoding: exactly one of the four input features is active.
In particular, input 00 has its own active feature; it is not an empty input vector.

Let \(W_{jk}\) be a learned weight connecting input category \(j\) to output
category \(k\). We fix output 00 as a reference with score zero. The other three
outputs have scores

\[
h_{00}(u)=0,\qquad
h_k(u)=\sum_{j\in\mathcal K}a_j(u)W_{jk},
\quad k\in\{10,01,11\}.
\]

A softmax converts these scores into probabilities:

\[
p_W(k\mid u)=
\frac{\exp(h_k(u))}{\sum_{v\in\mathcal K}\exp(h_v(u))}.
\]

The probabilities are positive and sum to one. Setting one score to zero avoids
an unnecessary parameter: adding the same constant to every score would leave
the probabilities unchanged. There are four input rows and three learned output
scores, giving twelve effective weights.

Once the target arrives, prediction loss is

\[
\ell(W;u,z)=-\log p_W(z\mid u).
\]

The logarithm is natural. Lower loss means assigning more probability to the
observed target. Accuracy only asks whether the most probable output was correct;
loss also distinguishes tentative correct predictions from confident ones.

The error-driven learning signal for each learned weight is

\[
g_{jk}=a_j(u)\bigl(\mathbf1[z=k]-p_W(k\mid u)\bigr).
\]

Here \(\mathbf1[z=k]\) is one when the target is \(k\), and zero otherwise.
This is the negative gradient of the loss with respect to \(W_{jk}\). Only the
observed input row receives an error-driven update. If the target is the reference
output 00, the other scores receive downward updates, increasing its relative
probability.

## Two timescales of retained learning

Split each effective weight into fast and slow components:

\[
W=F+S.
\]

Both are retained weights. “Fast” does not mean a transient activation, and
“slow” does not mean a protected truth or a moral norm. Each component starts
at zero, so the initial output probabilities are all one quarter.

After a prediction and target, apply

\[
\widetilde F=\operatorname{clip}(\rho_f F+\eta_f g,-8,8),
\qquad
\widetilde S=\operatorname{clip}(\rho_s S+\eta_s g,-8,8).
\]

These operations act separately on every weight. Clipping restricts a value to
the stated interval. The tildes mean “after the ordinary update, before any
transfer.” Both components use the same gradient computed from the prediction
made before either component changed.

The learning rates \(\eta_f,\eta_s\) determine responsiveness to error. The
retention factors \(\rho_f,\rho_s\) determine how much prior weight survives
each update. For the baseline experiments they are

\[
\rho_f=0.95,\quad\rho_s=0.999,
\qquad\eta_f=0.20,\quad\eta_s=0.02.
\]

Thus fast weights respond more strongly and decay more quickly. Inactive input
rows receive no gradient but still decay. Inertia here means dependence on
retained history; the model has no separate momentum variable.

This already learns, but slow weights learn directly from external targets.
Different rates alone do not make slow learning inherit fast learning.

## Measuring the difference between responses

Every \(K\) training examples, compare two predictions on the same input:

\[
P_{\mathrm{slow}}(k\mid u)=p_{\widetilde S}(k\mid u),
\qquad
P_{\mathrm{combined}}(k\mid u)=p_{\widetilde F+\widetilde S}(k\mid u).
\]

The combined response is the slow background plus fast learning, not fast weights
on their own. Define their signed difference and its total variation distance:

\[
\Delta(k\mid u)=P_{\mathrm{combined}}(k\mid u)-P_{\mathrm{slow}}(k\mid u),
\qquad
D(u)=\frac12\sum_{k\in\mathcal K}|\Delta(k\mid u)|.
\]

The signed differences sum to zero. The distance lies between zero and one;
zero means the responses agree. Average it over a fixed set \(U\) of probe
inputs, which contains all four input categories in these experiments:

\[
D=\frac1{|U|}\sum_{u\in U}D(u).
\]

These probes contain no targets. They reveal disagreement, not correctness.
A large distance may reflect useful adaptation or a fast learner's mistake.
Agreement can also occur between two wrong responses.

Keep an exponentially smoothed distance across successive review boundaries:

\[
\overline D\leftarrow(1-\nu)\overline D+\nu D,
\qquad \overline D_{\mathrm{initial}}=0.
\]

Consider a transfer only when both current and smoothed distances exceed a
threshold \(\tau\):

\[
b=\mathbf1[D>\tau]\mathbf1[\overline D>\tau].
\]

The switch \(b\) is either zero or one. Smoothing makes history relevant to the
decision, but does not guarantee several consecutive disagreements or prove
that a change is lasting.

## Moving learning into slower memory

The proposed transfer is a fraction \(\kappa\) of the fast weights:

\[
T^{\mathrm{raw}}=\kappa\widetilde F.
\]

To keep both components within their bounds, constrain each proposed transfer
before deciding whether to accept it. For a particular weight, let \(f\) and
\(s\) be its provisional fast and slow values. The allowed interval is

\[
L=\max(-8-s,\ f-8),\qquad
H=\min(8-s,\ f+8),
\qquad T=\operatorname{clip}(\kappa f,L,H).
\]

This ensures that both \(f-T\) and \(s+T\) remain feasible. Independently
clipping them after transfer could break the conservation we want to preserve.
Applying this calculation to all weights gives the transfer array \(T\).

When the disagreement gate opens, a separate selection batch \(V\) supplies
external input/target pairs. Define its mean prediction loss as

\[
\mathcal L_V(B)=-\frac1{|V|}\sum_{(u,z)\in V}\log p_B(z\mid u),
\]

where \(B\) denotes whichever weight array is being evaluated. The gain from
adding the proposed transfer to the slow component is

\[
G=\mathcal L_V(\widetilde S)-\mathcal L_V(\widetilde S+T).
\]

Accept the whole transfer only if its gain exceeds a fixed margin \(\delta\):

\[
m=b\,\mathbf1[G>\delta],\qquad C=mT,
\qquad
F^+=\widetilde F-C,\quad S^+=\widetilde S+C.
\]

When \(b=0\), we skip selection and set \(C=0\). The superscript + denotes
the state after this decision. Selection data influence learning through the
decision, so they are not an untouched test set. Final evaluation uses separate
examples and freezes all state changes.

The paired subtraction and addition give an exact identity:

\[
F^++S^+=\widetilde F+\widetilde S.
\]

The immediate combined prediction is unchanged. The information is now
distributed differently between components that decay at different rates.

Compare the transferred state with an otherwise identical state without transfer.
After \(d\) decay-only ticks, with no new learning or transfer, their effective
weights differ by

\[
W_{\mathrm{transfer}}(d)-W_{\mathrm{control}}(d)
=(\rho_s^d-\rho_f^d)C.
\]

At \(d=0\) there is no difference. Later, the transferred contribution persists
longer. That can preserve something useful or prolong an error. The algebra
guarantees neither correctness nor desirability.

In the tested scheme, \(K=20\), \(\nu=0.25\), \(\tau=0.05\),
\(\kappa=0.25\), and \(\delta=0.001\). Each selection batch has eight pairs,
two per input category. These settings remain fixed throughout a run.

To isolate learning from transfer, one variant sets \(\eta_s=0\) and
\(\eta_f=0.22\). Slow weights still decay, but every addition to them must
come from accepted fast learning. Another variant has the same parameters with
transfer disabled. These are experiments on a mechanism, rather than assumptions
that every part of it is necessary.

## What we actually tested

The first question was simply whether the learner could acquire two supplied
associations. It could. The next experiment used all four categories and changed
their mapping halfway through. Across five seeds, the fast/slow learner reached
100% accuracy in frozen evaluations before and after that change.

Those results concern known input categories. They do not establish generalization
to unfamiliar inputs, learning new distinctions, or an advantage over a simpler
learner. A slow-only control also learned and achieved lower prediction loss.

For the four-state comparisons, fast-only and slow-only controls use a learning
rate of 0.22, matching the initial effective step of the parallel model, with
retention factors 0.95 and 0.999 respectively. Their weights are bounded by 16,
matching the possible combined range of \(F+S\). A frozen control remains
uniform, giving 25% accuracy on balanced mappings and loss \(\log 4\), about
1.386. The controls are not separately tuned, and the dual model stores twice
as many parameters.

A further fixed round tested retention, transient errors, and consolidation:

| Question | Experimental arrangement | Finding |
| --- | --- | --- |
| What survives inactivity and interference? | Learn mapping A, allow 100 decay-only ticks, learn conflicting B, then return to A. | Fast/slow retained more than fast-only after the gap; slow-only retained substantially more than either. Learning B interfered with A. |
| Does the learner handle temporary error differently from lasting change? | Learn A, receive 40 pairs supporting B, then either return to A or continue B. | Fast/slow failed the declared joint comparison against slow-only in all five seeds. |
| Can fast learning become useful slow memory? | Combine a short error burst, recovery, lasting reversal, and a final decay gap; compare transfer and its ablations. | Transfer improved retention over parallel fast/slow learning. Useful slow weights also emerged with direct slow learning disabled. |

The model was never told whether a disturbance would be temporary. In the
consolidation runs, selection pairs supplied during the error burst contained
the same kind of wrong targets as training data. Selection had no privileged
access to a clean answer.

For consolidation, the hybrid's declared criterion required, in every seed,
post-gap loss at least 0.02 below parallel fast/slow, final accuracy of at least
90%, and average loss during lasting change no more than 0.05 worse. It met
that criterion. The means after the final gap were:

| Model | Combined prediction loss | Accuracy |
| --- | ---: | ---: |
| Parallel fast/slow | 1.111 | 75% |
| Hybrid with selected transfer | 0.656 | 100% |
| Slow learns through transfer alone | 0.791 | 75% |
| Slow-only control | 0.213 | 100% |

The transfer-only variant demonstrated a narrower result: slow memory acquired
useful predictive information. Its 75% accuracy did not meet the original
acquisition threshold. The simpler slow-only learner remained better on loss.

We also reserved equal selection-data budgets for all variants and included a
parallel learner that trained directly on every reserved pair. The hybrid
outperformed that control on post-gap loss, although the extra training also
introduces extra decay updates. Actual data use was logged separately from the
reserved budget.

## A result that limits the story

The external selection gate rejected none of the hybrid's triggered candidates.
Across five seeds, all 163 were accepted. Removing external selection produced
identical training trajectories and checkpoint predictions.

So the retention gain cannot be credited to that gate distinguishing good
proposals from bad ones in this task. Transfer helped; evidence-based acceptance
added no observed benefit. Synthetic checks show that the implementation can
reject a harmful proposal, but that is different from demonstrating its value
during learning.

Removing the disagreement trigger produced a small deterioration in mean loss
and used more selection examples. This is a limited observation on one stream,
not evidence that the threshold or trigger is generally effective.

The second round allocated 86,880 labelled presentations across its conditions,
including reserved selection pairs, and 7,000 decay-only ticks. Protocols were
fixed beforehand, every seed was reported, and there was no tuning afterwards.
Correctness tests and an audit of the saved predictions and weight changes passed.
The largest immediate prediction change from transfer was about
\(2.22\times10^{-16}\), consistent with floating-point rounding.

## Keeping the philosophical questions open

The implementation makes the origin of significance quite visible. The designer
supplies the categories, the teaching environment supplies targets, and the loss
function specifies what counts as improvement. These experiments do not show
the learner developing its own concerns. They give us a concrete place to ask
what would have to change for that question to become experimentally meaningful.

Retention also has an ambiguous role. A prior success becomes a disposition to
respond similarly again. That continuity can support learning, but it can also
make an obsolete response harder to revise. The slow component is not right
because it is slow; the fast component is not insightful because it is new.

The distinction between fast and slow is itself constructed and relative. Both
contribute to one prediction, and transfer changes how that contribution is
carried forward. This is one way to explore distinctions without treating them
as absolute divisions. It does not prove a philosophical position about
non-duality.

Later, changing the distinctions themselves could bring another question into
view: what is preserved when a system changes the categories through which it
learns? A label, a parameter, a pattern of behavior, and a commitment are different
things to preserve. Inspectable names and weights may help us investigate that
question; they do not answer it in advance.

I want to keep this enquiry small enough that those questions remain visible.
The current work offers a functioning learning mechanism, a measurable benefit
from transfer against one baseline, and clear limits on stronger claims.

All of this remains within isolated experiments. No connection to real-world
operational systems is recommended. Scaling or applying the method would need
its own deliberate assessment. Interpretability, steerability, and safety are
still aspirations to test, including the possibility that the approach offers
no advantage in some or all of those respects.

For now, the next question is specific: under what conditions can selection
preserve a useful fast change while rejecting a misleading one, and does that
ability justify its cost compared with a simpler learner?

---

*Draft preparation note: the article is self-contained. The following local
research records support checking and reproduction; replace their locations
with public repository links before publication.*

- [Mathematical specification](../maths-v1.md)
- [Consolidation specification](../maths-v1-consolidation.md)
- [First mapping experiment](../results/tiny-mapping-v1/report.md)
- [Four-state reversal experiment](../results/small-reversal-v1/report.md)
- [Round 2 protocol](../experiments/round2_protocol.md)
- [Round 2 findings and limitations](../results/round2-v1/findings.md)
