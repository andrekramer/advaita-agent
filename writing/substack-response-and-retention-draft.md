# Advaita-agent: a (non-)dual enquiry into learning

*Distinctions, retained history, and the first small experiments in how
experience becomes a reusable form.*

My work on attention expanded quickly. What began as a way to investigate
learning became an architectural programme larger than I could reasonably pursue
alone, even with AI assistance. There were more mechanisms to build, more
interactions to understand, and more experiments needed to tell whether the
complexity was justified. I've experienced that previously in my career in software 
and I suspect AI researchers in the commercial labs can get caught up like this too.

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

The first experiments fixed the distinctions so that their role could be
inspected. A subsequent experiment lets the learner discover a useful grouping
from action consequences and recognise it in new combinations of features.
The perceptual features and possible operations are still supplied. Changes
supplied by a designer must remain distinguishable from learning achieved by
the running system.

## Name, form, and action

Name, form, and action, drawn from Vedanta, provide a way of approaching this
enquiry. My engineering interpretation is provisional: a name identifies a
distinction; a form organises recognition across variations in experience; and
action exposes consequences that can support or challenge that organisation.
This correspondence is an inspiration, not a claim to have formalised Vedanta.

By the slower level of learning, I have in mind something like **“I know that”**:
a situation becomes recognisable through something retained from previous
experience. There is no claim of consciousness here. The question is whether
experience becomes a form that can be used again, and whether that form remains
open to correction. A lower learning rate alone does not establish either.

This also connects recognition with how causes and effects are represented.
Two situations that look alike may need distinguishing because an action has
different consequences. Different-looking situations may belong together
because the same action-consequence relationship applies. Our first test uses
that limited sense of form: a grouping useful for predicting action outcomes.
It does not attempt general causal discovery.

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

The first implementation below learns predictions from externally supplied
examples and redistributes learned weights between two timescales. The later
structural experiment asks what changes when the grouping of experiences can
also be learned. Neither implementation chooses its own actions or generates
its own concerns. Calling the project an agent does not establish those capacities.

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

## The experiments with fixed distinctions

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

## Can the learner discover a form?

The next experiment changes the question. Instead of supplying the categories
whose associations must be learned, we supply simple perceptual features and
ask the learner to discover which combinations belong together through their
action consequences.

The isolated simulator presents three binary features \(x=(s,t,c)\), an action
\(a\in\{0,1\}\), and then a binary outcome \(y\). Its hidden rule is

\[
y=s\mathbin{\mathrm{XOR}}a.
\]

XOR is one when its two arguments differ. Thus when \(s=0\), action 0 produces
outcome 0 and action 1 produces outcome 1. When \(s=1\), those consequences
reverse. Features \(t\) and \(c\) make no difference. The learner is not told
this rule or which feature matters; the feature positions are shuffled per seed.

We withhold contexts 000 and 111 entirely from learning and selection. The
remaining six feature combinations, each under both actions, supply experience.
After learning, the withheld contexts test whether a discovered rule can be
reused beyond the exact combinations encountered. Actions follow an externally
balanced schedule, so this tests learning from action consequences, not deciding
when or how to explore.

The learner begins with one form covering every context. Its recognition rules
can test supplied features, split a group, or merge groups. For example,
“feature 0 is zero, whatever the other features” describes a reusable group.
Different recognition rules may also lead to the same form. We cap the system
at eight recognition leaves and four response forms; the desired number of
forms is not supplied to the learner.

For a model \(M\), let \(g_M(x)=k\) identify the form recognised in context
\(x\). For each form and action, retain the number of observations \(n_{ka}\)
and the number with outcome one, \(r_{ka}\). Its prediction is

\[
q_M(1\mid x,a)=\frac{r_{g_M(x),a}+1}{n_{g_M(x),a}+2},
\qquad q_M(0\mid x,a)=1-q_M(1\mid x,a).
\]

An unobserved form/action pair starts at probability one half. An observation
increments \(n_{ka}\) by one and \(r_{ka}\) by \(y\). The added counts keep
predictions away from zero and one. This simple estimator handles uncertainty
within a proposed form; the creation and selection of the grouping require
additional operations.

Every 48 main observations, enumerate the current structure and its permitted
single-split or single-merge alternatives. Refit each candidate from the stored
main observations, so a split never invents observations for its children.
For a batch \(B\), score a model by

\[
J(M;B)=-\frac1{|B|}\sum_{(x,a,y)\in B}\log q_M(y\mid x,a)
+0.01\,C(M)+0.005\,R(M),
\]

where \(C(M)\) counts forms and \(R(M)\) counts recognition leaves. The
penalties express a supplied preference for fewer distinctions when extra
complexity adds insufficient predictive value. They are fixed before the run.

Choose the candidate \(M_*\) with the lowest training score, using a fixed
ordering to break ties. Test only that candidate on a fresh selection batch
\(V\). Replace the current deployed model \(M_0\) when

\[
J(M_0;V)-J(M_*;V)>0.001.
\]

Selection outcomes do not fit the candidate or enter its future counts. The
withheld-context test set is separate from both fitting and selection.

Two structural learners use exactly this candidate language and selection rule.
The **single learner** updates its response counts continuously. The
**provisional/retained learner** updates a provisional model \(A\), while a
retained model \(N\) supplies its deployed predictions. Accepted candidates
replace \(N\). After each review, \(A\) uses the current structure with counts
refitted from all main observations. Here, slower retention means less frequent
accepted replacement of a model, rather than a smaller gradient step.

This changes the implementation. A structural replacement need not conserve
immediate predictions, and the earlier additive \(F+S\) transfer identity does
not apply. We are testing another concrete instance of variation, selection,
and retention, not treating the earlier equations as already sufficient for
category creation.

## What the form-learning experiment found

Both structural learners selected the relevant feature at the first review,
after 48 main observations. They created two forms and ignored the two nuisance
features. Their final predictions assigned probability 0.98 to the correct
outcome under each action, including for the withheld combinations.

The comparison included an exact-context lookup table and a fixed-feature
logistic learner. The lookup table uses the same smoothed counting rule but
stores each context/action pair separately. It has no rule for reusing learning
on an unseen context.

The logistic learner has no explicit category creation. It receives signed
features \(u_i=2x_i-1\) and action \(b=2a-1\), with the fixed vector

\[
\phi=(1,b,u_0,u_1,u_2,bu_0,bu_1,bu_2),\qquad
q=\frac1{1+\exp(-w^\top\phi)}.
\]

Starting from zero weights, it updates after feedback by

\[
w\leftarrow\operatorname{clip}\bigl(w+0.1(y-q)\phi,-8,8\bigr).
\]

The supplied interactions let it express the simulator's rule. It therefore
provides a control for whether explicit forms are necessary for prediction.
Mean frozen-evaluation results across five seeds were:

| Learner | Accuracy on withheld combinations | Prediction loss |
| --- | ---: | ---: |
| Exact-context lookup | 50% | 0.693 |
| Single structural learner | 100% | 0.020 |
| Provisional/retained structural learner | 100% | 0.020 |
| Fixed-feature logistic learner | 100% | 0.173 |

Both structural learners passed all declared acquisition criteria in every
seed. These required correct withheld predictions with loss below 0.25,
exactly two forms and two recognition leaves, the correct grouping independently
of its assigned names, no prediction change when a nuisance feature changed,
and a probability change of at least 0.5 when the relevant feature changed.
The observed relevant-feature change was 0.96.

This is a small instance of learning reusable forms within a supplied language.
It is also an instance that a single learner handles equally well. The two
structural models ended with identical rules and predictions. The fixed-feature
learner also classified every withheld case correctly, so explicit categories
were not necessary for that success. Its probabilities still varied with
nuisance features; those of the structural learners did not.

The run used 192 main observations, 48 selection observations, and four final
test outcomes per learner and seed: **4,880 outcome-bearing presentations** in
total. Structural learners used selection data only to select; the two baselines
learned directly from those pairs. Both structural variants scored 22 candidates
per run. Eight correctness tests and an independent audit of the saved traces
passed. There was no tuning after results.

The task is deterministic and very small. Balanced observations explain the
identical final structural scores across seeds; the shuffled feature positions
happened to cover only two distinct permutations. These are descriptive results
on one task, not evidence of broad robustness. Nor have we yet shown retained
forms surviving distraction, being revised after change, or being collapsed
when no longer useful. No merge was accepted in this experiment.

## Both models can agree and still miss the form

The most revealing result appeared just before the first category was created.
The provisional and retained models agreed exactly.

For binary outcomes, the response distance reduces to

\[
D_{\mathrm{form}}=\frac1{|U|}\sum_{(x,a)\in U}
\left|q_A(1\mid x,a)-q_N(1\mid x,a)\right|,
\]

where \(U\) contains the twelve observed context/action combinations, without
their outcomes. We also recorded the same exponential smoothing as before,
with coefficient 0.25. Neither diagnostic controlled reviews in this experiment;
reviews occurred on the fixed schedule.

At the first review, both models predicted one half for every case, giving
\(D_{\mathrm{form}}=0\). One half was the correct aggregate frequency in the
balanced observations. But both models missed the distinction that made each
individual action outcome predictable. They were equally inadequate for that
task, despite agreeing with each other.

The scheduled search proposed a split. Separate selection feedback supported
it, improving the penalised score by about 0.604. The useful distinction was
discovered while the existing models' response difference was zero.

So yes: **two models can be equally wrong—or share the same missing
distinction—and therefore agree just before a new form is created.** A gate
requiring nonzero disagreement would have blocked consideration of this split
at that review. We did not run a separate gated counterfactual, and this does
not establish that such a learner could never discover it later.

This qualifies the role I originally gave the difference between timescales.
It can reveal a conflict between current responses. It cannot, by itself,
reveal what their shared representation leaves out. Here, systematic variation
of the representation supplied a possibility that neither current response
expressed; external consequences then supported retaining it.

The wider scheme therefore needs a route to proposing distinctions even when
its current models agree. We supplied scheduled search in this experiment.
Persistent prediction error or deliberate exploratory action are other routes
to investigate, not results already established here. Error alone would not
prove that a new category is needed either: noise, missing observations, or an
inappropriate task could also make predictions fail.

## Keeping the philosophical questions open

The implementations make the origin of significance quite visible. In the first
experiments the designer supplied the categories. In the form-learning experiment
the grouping was learned, but its perceptual vocabulary, available actions,
candidate operations, and standards of improvement were supplied. Neither
experiment shows the learner developing its own concerns. They give us a concrete
place to ask what would have to change for that question to become meaningful.

Retention also has an ambiguous role. A prior success becomes a disposition to
respond similarly again. That continuity can support learning, but it can also
make an obsolete response harder to revise. The slow component is not right
because it is slow; the fast component is not insightful because it is new.

The distinction between fast and slow is itself constructed and relative. In
the weight-transfer model, both contribute to one prediction. In the structural
model, provisional learning can support replacement of a retained organisation.
Neither arrangement makes its two parts absolute divisions or proves a
philosophical position about non-duality. The single structural learner's success
also leaves open whether the functions I am interested in require two explicit
models at all.

Beginning to change the distinctions brings another question into view: what is
preserved when a system changes the categories through which it learns? A label,
a parameter, a pattern of behavior, and a commitment are different things to
preserve. The first split gives us an inspectable example of a useful grouping
being acquired. It does not yet explain how an established form remains useful
while being open to revision.

I want to keep this enquiry small enough that those questions remain visible.
The current work offers learning within supplied distinctions, a measurable
benefit from transfer against one baseline, and an initial example of discovering
reusable forms. It also exposes a limit: agreement between retained and
provisional responses can coexist with a missing distinction.

All of this remains within isolated experiments. No connection to real-world
operational systems is recommended. Scaling or applying the method would need
its own deliberate assessment. Interpretability, steerability, and safety are
still aspirations to test, including the possibility that the approach offers
no advantage in some or all of those respects.

For now, the next question is specific: can an acquired form survive distraction,
yet be reopened when its consequences change? Selection must preserve something
useful without turning prior success into an obstacle to learning. Whether two
timescales help with that, compared with a single learner, remains an experiment
to do.

Andre with ChatGPT-6-Astra, October 2026

The advaita-agent code and results are here: https://github.com/andrekramer/advaita-agent

---

*Draft research references: [form-learning protocol](../experiments/forms_protocol.md),
[findings and verification](../results/forms-v1/findings.md), and
[all seeds and learned rules](../results/forms-v1/report.md). These local links
should be replaced with published repository links before posting.*
