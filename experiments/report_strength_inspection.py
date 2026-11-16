"""Report frozen findings and unscored reader tasks; no empirical selection."""
import gzip,hashlib,json,random,sys
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
from strength_inspection import describe
OUT=ROOT/'results/strength-inspection-v1'


def reader_tasks(rs):
    folder=OUT/'reader-tasks';folder.mkdir(exist_ok=False)
    rng=random.Random(991);seeds=sorted({r['seed'] for r in rs});rng.shuffle(seeds);answers={};files=[]
    for i,seed in enumerate(seeds,1):
        choices=[r for r in rs if r['seed']==seed];r=choices[rng.randrange(len(choices))]
        mode='raw_banks' if i%2 else 'direction_strength'
        view=describe(r['packet'],mode)
        p=r['probes'][rng.randrange(128)];task=f'task-{i:02d}'
        # No decisions, outcomes, true world forms, branch label or original seed.
        data=dict(task=task,view=view,probe=dict(action=p['action'],incoming=p['row']),
                  questions=['Predict the three emitted probabilities before the incoming labels are added (elapsed-time decay does occur).',
                             'Predict the three diagnostic probabilities after those labels are added.',
                             'Choose none, 0, 1 or 2 for a temporary plasticity command to improve the instructed target while protecting the supplied other output.',
                             'For each command predict target Brier improvement over no intervention during the next64 observations; describe assumptions and uncertainty.'])
        filename=task+'.json';(folder/filename).write_text(json.dumps(data,indent=2)+'\n');files.append(filename)
        answers[task]=dict(seed=seed,history=r['history'],proposal_seed=r['proposal_seed'],encoding=mode,
                           probe=p['actual'],future_gains={a:r['metrics']['branches']['none']['early'][r['metrics']['target']]-m['early'][r['metrics']['target']] for a,m in r['metrics']['branches'].items()},
                           active_losses={a:m['active'][r['metrics']['target']] for a,m in r['metrics']['branches'].items()})
    (OUT/'reader-answer-key.json').write_text(json.dumps(answers,indent=2)+'\n')
    links='\n'.join(f'- [{p}]({p})' for p in files)
    (folder/'README.md').write_text('''# Unscored inspection tasks

These twelve tasks are preparation for a separate reader study, not evidence of
human/AI understanding. One case per environment; six raw-count and six equivalent
direction/strength reports, assigned before looking at task difficulty. There are
no scored reader answers yet. Do not consult results or the separate answer key
until submitting responses. A later confirmation study should use fresh tasks.

Counts are [successes,total]. Named bank direction is successes/total (null for
zero mass); strength is retained mass, not calibrated confidence. Add fixed unit
success/failure priors when predicting. Fast half-life is64 ticks; slow is1024,
or128 while the selected channel is plastic. Commands affect one channel; none
leaves all rates unchanged. Each tick decays first, predicts, adds the outcome,
then refits. Group ports consume membership, not local probability. Structural
reviews occur every64 ticks. Recent rows are previous training observations.

For each task return numerical answers, a chosen command, and uncertainty. The
one-step question specifies an incoming observation. The future question does not
reveal future labels; its answer can legitimately be uncertain. All four command
choices are available, with the same instructions under both encodings.

'''+links+'\n')


def main():
    assert not (OUT/'findings.md').exists()
    audit=json.loads((OUT/'audit.json').read_text());assert audit['status']=='pass'
    data=json.loads((OUT/'results.json').read_text());s=data['summary']
    with gzip.open(OUT/'runs.jsonl.gz','rt') as f:rs=[json.loads(line) for line in f]
    reader_tasks(rs)
    f=lambda v:f"{v['mean']:+.6f} [{v['low']:+.6f}, {v['high']:+.6f}]"
    comparisons='\n'.join(f"| {k} | {f(v)} | {v['positive']}/12 |" for k,v in s['steering_gains'].items())
    groups='\n'.join(f"| {g['history']} | {g['task']} | {g['policy']} | {g['gain']:+.6f} | {g['actions']}/{g['n']} | {g['unnecessary']} | {g['missed']} |" for g in s['groups'] if g['policy'] in ('existing','raw_banks','disagreement'))
    checks='\n'.join(f'- {k}: **{v}**' for k,v in s['gates'].items())
    probes='\n'.join(f'| {k} | {v:.9g} |' for k,v in s['probe_mean_errors'].items())
    guards='\n'.join(f"| {g['history']} | {g['window']} | {g['channel']} | {g['mean']:+.6f} | {g['maximum']:+.6f} |" for g in s['guards'] if not g['passed']) or '| none | — | — | — | — |'
    text=f'''# Strength inspection and bounded steering

Completed2026-11-13. Mechanical contract: **{s['gates']['mechanical']}**;
information/forecast criterion: **{s['information_pass']}**;
steering criterion: **{s['steering_pass']}**. Presentation comprehension was
**not tested**. Native reconstruction passed for72 acquired trunks and288 command
continuations, across12 environment seeds, three histories and two proposal seeds.

## What this tests

The unchanged consolidated learner uses combined memory and shadow recall.
At tick640 a supplied controller chooses no intervention or temporary plasticity
for one channel. All four possibilities are replayed on identical future data;
controls release at896 and evaluation ends1152. Target/protected outputs are
supplied task instructions. Forms, reviews, automatic weakening and migration
continue normally. No goals or control policy were learned.

The ordinary inspection supplies row totals and channel-wide bank masses. The
existing-view controller approximates each row's bank allocation proportionally.
An additional read-only adapter supplies actual row-specific fast/slow counts.
The named description represents those same counts as bank direction and retained
strength. Raw and named descriptions produced identical commands and numerically
equivalent forecasts. This verifies an encoding; it does not show that a reader
understands the named version better. The extra bank information, rather than
geometry, is the substantive information intervention.

All evaluators are supplied scripts. The64-step control model uses recent empirical
rates and fixed representations, omitting future structural reviews and memory
decisions. It is a plug-in approximation, not an exact expected future loss.
Recent64 observations are reused training data, not an independent validation set.

## Mechanical effect forecasts

All32 input contexts and all4 commands were probed from each decision state on
isolated clones, using a supplied contrary outcome. Mean absolute probability
error, pooling emitted pre-label and diagnostic post-label predictions:

| Inspection | Mean absolute error |
| --- | ---: |
{probes}

Maximum errors with row-bank information: raw {s['mechanical_maxima']['raw_banks']:.3g},
named {s['mechanical_maxima']['direction_strength']:.3g}, against tolerance1e-10.
These conditional predictions account for decay and fixed priors; they do not
predict which outcome will arrive or establish calibrated uncertainty.

## Forecasting future control effects

Bank-minus-existing mean absolute error in64-observation target Brier effects:
**{f(s['future_error_difference'])}** (negative favors bank information).
Bank effect-direction accuracy was **{s['future_accuracy']:.1%}**, with
{s['nonnegligible_effects']}/216 actual command effects exceeding .001 in magnitude.
All commands count, including actions the controller declined to take. Small/no
effects can inflate aggregate direction accuracy; coverage is separately required.

Intervals use5000 paired environment-cluster bootstrap samples. Outcomes within
an environment are averaged before resampling;72 states and288 branches are not
independent environment samples. Twelve environments give limited precision.

## Selecting controls

Positive differences below mean that bank-informed selection reduced target
Brier loss over the256-observation active window, relative to the named control.

| Control | Mean improvement [95% interval] | Positive environment means |
| --- | ---: | ---: |
{comparisons}

Descriptive breakdowns; raw/named outcomes are identical. Unnecessary means an
action yielded no more than .001 actual target improvement; missed means abstaining
when one of the four tested commands would have improved by more than .001.
These classifications use hindsight only for evaluation, never for selection.

| History | Task | Policy | Gain vs no-op | Actions | Unnecessary | Missed |
| --- | --- | --- | ---: | ---: | ---: | ---: |
{groups}

Target type is paired with proposal seed, so differences between local/composite
strata are descriptive, not a causal comparison of target types.

Failed preservation guards (mean cost>.01 or any case cost>.05 vs no-op):

| History | Window | Output | Mean cost | Maximum case cost |
| --- | --- | ---: | ---: | ---: |
{guards}

## Frozen criteria

{checks}

Exact contracts and information/steering usefulness are separate claims. No
failed criterion is repaired through new thresholds or a post-outcome rerun.
The [protocol](../../experiments/strength_inspection_protocol.md) specifies all
windows, instructions, baselines and limits.

## Verification, budgets and reader tasks

Three preflight fixture tests checked hidden allocation, empty banks, fixed priors,
clock alignment, equivalent encodings, read-only inspection and release/restore.
An independent implementation reconstructed worlds, acquisition, native forecasts,
reviews, final learning state, inspection quantities, commands and metrics.
The controller's iterative projection was checked with a closed-form recurrence.
Wrapper ledger metadata receives runtime round-trip checks, not a separately
implemented schema38 validator. There were{s['gates']['mechanical'] and 9216} isolated
synthetic probe clones and576 trajectory checkpoint round trips.

Generated scalar labels: {data['totals']['generated_scalar_labels']:,}, including
materialized world futures beyond the evaluation horizon. Training label
presentations across reused acquisitions and branches:
{data['totals']['training_label_presentations']:,}. Controller recent-data reuse:
{data['totals']['controller_reused_scalar_labels']:,} scalar labels; synthetic
probe labels:{data['totals']['synthetic_probe_scalar_labels']:,}. These counts
are not independent evidence. Runner:{data['elapsed_seconds']:.2f}s;
audit:{audit['elapsed_seconds']:.2f}s.

[Twelve blinded reader tasks](reader-tasks/README.md) are prepared but unscored.
They compare equivalent raw/named information, not unequal evidence access.
The assignment is a pilot task pack, not a completed randomized reader study;
future confirmation requires a fixed evaluator and fresh tasks.

The architecture/defaults and prior Heaviside failures remain unchanged. This is
not evidence of human/LLM comprehension, generally reliable steering, safety or
meta-learning. No further benchmark starts automatically.

Artifacts: [summary](results.json), [independent audit](audit.json),
[traces](runs.jsonl.gz), [worlds](worlds.json), [source manifest](manifest.json).
'''
    (OUT/'findings.md').write_text(text)
    paths=['findings.md','audit.json','artifact-hashes.json','reader-answer-key.json']+[str(p.relative_to(OUT)) for p in (OUT/'reader-tasks').iterdir()]
    (OUT/'completion.json').write_text(json.dumps(dict(status='complete',presentation_tested=False,default_changed=False,verification_hashes={p:hashlib.sha256((OUT/p).read_bytes()).hexdigest() for p in sorted(paths)}),indent=2)+'\n')
    print(OUT/'findings.md')


if __name__=='__main__':main()
