"""Render verified Stage-1 results, including standalone vector plots."""
import gzip
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/heaviside-prediction-v1'


def plot():
    # Standalone SVG uses only standard-library serialization; no plotting
    # dependency is installed in this workspace. Every vertex is a saved mean.
    colors = dict(vector='#0072B2', fixed='#D55E00', rotor='#CC79A7',
                  prior_selected='#009E73', window='#444444', full='#E69F00')
    means = {(h, f, a): [0.]*128 for h in ('short', 'long')
             for f in ('streak', 'reversal') for a in colors}
    counts = {k: 0 for k in means}
    with gzip.open(OUT/'runs.jsonl.gz', 'rt') as stream:
        for line in stream:
            r = json.loads(line)
            key = r['history'], r['future'], r['arm']
            if r['suite'] != 'B' or key not in means: continue
            counts[key] += 1
            for i, p in enumerate(r['predictions']):
                means[key][i] += 1-p if r['mirrored'] else p
    assert set(counts.values()) == {200}
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1320" height="970" viewBox="0 0 1320 970">',
           '<rect width="1320" height="970" fill="white"/>',
           '<g font-family="Arial, sans-serif" font-size="15" fill="#222">',
           '<text x="60" y="35" font-size="25">Direction and strength: held-out fixed-row forecasts</text>',
           '<text x="60" y="61">Suite B · 200 seeds · mirroring undone before averaging · lower panels show lasting reversal</text>']
    for n, (arm, color) in enumerate(colors.items()):
        x = 60+n*205
        svg.append(f'<line x1="{x}" x2="{x+22}" y1="91" y2="91" stroke="{color}" stroke-width="3"/>')
        svg.append(f'<text x="{x+28}" y="96">{html.escape(arm)}</text>')
    for row, future in enumerate(('streak', 'reversal')):
        for col, history in enumerate(('short', 'long')):
            x0, y0, width, height = 85+col*640, 150+row*380, 535, 280
            svg.append(f'<text x="{x0}" y="{y0-18}" font-size="19">{future} · {history} prefix</text>')
            if future == 'streak':
                svg.append(f'<rect x="{x0}" y="{y0}" width="{width*4/127:.2f}" height="{height}" fill="#eee"/>')
            for value in (0, .2, .4, .6, .8, 1.):
                y = y0+height*(1-value)
                svg.append(f'<line x1="{x0}" x2="{x0+width}" y1="{y}" y2="{y}" stroke="#ddd"/>')
                svg.append(f'<text x="{x0-35}" y="{y+5}">{value:.1f}</text>')
            for value in (0, 32, 64, 96, 127):
                x = x0+width*value/127
                svg.append(f'<text x="{x-8}" y="{y0+height+23}">{value}</text>')
            target = .8 if future == 'streak' else .2
            y = y0+height*(1-target)
            svg.append(f'<line x1="{x0}" x2="{x0+width}" y1="{y}" y2="{y}" stroke="#777" stroke-dasharray="5,5"/>')
            for a, color in colors.items():
                points = ' '.join(f'{x0+width*i/127:.2f},{y0+height*(1-p/200):.2f}' for i, p in enumerate(means[history, future, a]))
                svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.3" points="{points}"/>')
            svg.append(f'<rect x="{x0}" y="{y0}" width="{width}" height="{height}" fill="none" stroke="#666"/>')
            svg.append(f'<text x="{x0+125}" y="{y0+height+48}">Future observations already seen</text>')
            svg.append(f'<text transform="translate({x0-52},{y0+height-10}) rotate(-90)">P(originally favoured outcome)</text>')
    svg += ['<text x="60" y="920">Gray band: four forced contrary outcomes. Dashed line: resumed or reversed generating probability.</text>',
            '<text x="60" y="945">Scalar twin omitted because it matches vector. Curves are descriptive means, not confidence bands.</text>', '</g></svg>']
    (OUT/'mean-forecasts.svg').write_text('\n'.join(svg)+'\n')


def main():
    assert not (OUT/'findings.md').exists()
    audit = json.loads((OUT/'audit.json').read_text())
    assert audit['status'] == 'pass'
    result = json.loads((OUT/'results.json').read_text())
    summary = result['summary']
    chosen = result['selection']
    plot()
    table = ['| Control | Stable difference [95% interval] | Post-streak difference [95% interval] | Reversal difference [95% interval] |',
             '| --- | ---: | ---: | ---: |']
    for arm, values in summary['contrasts'].items():
        cells = [f"{values[f]['mean']:+.6f} [{values[f]['low']:+.6f}, {values[f]['high']:+.6f}]" for f in ('stable', 'streak', 'reversal')]
        table.append('| '+arm+' | '+' | '.join(cells)+' |')
    history_table = ['| Control | History | Stable | Post-streak | Reversal |', '| --- | --- | ---: | ---: | ---: |']
    for arm, values in summary['contrasts'].items():
        for h in ('short', 'long'):
            history_table.append('| '+arm+' | '+h+' | '+' | '.join(f"{values[f]['by_history'][h]:+.6f}" for f in ('stable', 'streak', 'reversal'))+' |')
    recovery = ['| Arm | History | Capped recovery delay | Censored fraction |', '| --- | --- | ---: | ---: |']
    for r in summary['aggregates']:
        if r['suite'] == 'B' and r['future'] == 'reversal':
            recovery.append(f"| {r['arm']} | {r['history']} | {r['recovery_capped']:.3f} | {r['censored']:.3f} |")
    first = {}
    with gzip.open(OUT/'runs.jsonl.gz', 'rt') as stream:
        for line in stream:
            r = json.loads(line)
            if r['suite'] == 'A' and r['future'] == 'streak':
                k = r['arm'], r['history']
                first.setdefault(k, []).append(-r['first_turn'] if r['mirrored'] else r['first_turn'])
    turns = ['| Arm | Short-support first turn | Long-support first turn |', '| --- | ---: | ---: |']
    for a in ('vector', 'scalar', 'full', 'fixed', 'matched', 'rotor'):
        turns.append('| '+a+' | '+' | '.join(f'{sum(first[a,h])/200:+.8f}' for h in ('short', 'long'))+' |')
    passed = summary['tradeoff_pass']
    conclusion = ('The declared isolated-prediction trade-off criterion passed against both the rolling-window and selected fixed-gain controls.'
                  if passed else 'The declared isolated-prediction trade-off criterion failed. A benefit from retained strength cannot be claimed from the primary comparison as a whole.')
    text = f'''# Heaviside Stage 1 — isolated direction/strength comparison

Completed 2026-11-13. **{conclusion}** Independent reconstruction passed for all
2,304 development runs and 18,000 confirmation runs. No native-agent superiority
or architecture change is established by this fixed-row study.

## Design and selected settings

The [protocol](../../experiments/heaviside_prediction_protocol.md) was saved before
development. Seeds0–31 selected parameters using suite B only; seeds1000–1199
were used once for confirmation. Suite A imposes identical odds with short/long
support; suite B replays identical shuffled prefixes, whose final odds can differ
between algorithms. Confirmation streams are shared across arms and histories,
with half the seeds label-mirrored. No further tuning was performed.

Selected rho for vector/scalar: **{chosen['vector']}**; matched gain:
**{1-chosen['vector']:.2f}**; separately selected fixed gain: **{chosen['fixed']}**;
rotor eta: **{chosen['rotor']}**; separately selected fixed-prior rho:
**{chosen['prior_selected']}**. Full retention uses rho1; the rolling window holds192
observations. The fixed-prior controls retain their unit priors and forecast after
elapsed-event discount. These are numerical controls, not the native review-based
learner or its selective-weakening policy.

## Held-out comparison

Values are **vector minus control Brier loss**: negative is better for vector.
The two histories receive equal weight within each seed. Intervals use10,000
paired seed-bootstrap samples. Stable measures observations1–128, post-streak5–20,
and reversal1–64. The primary gate requires post-streak upper bounds below0 and
stable/reversal upper bounds below+.01 against **both window and fixed**.

{chr(10).join(table)}

History-specific differences below are descriptive, without separate confidence
claims. Equal pooled weights must not conceal opposing short/long effects.

{chr(10).join(history_table)}

## Mechanism and exact-equivalence check

The maximum scalar/vector per-event forecast difference was
**{summary['scalar_max_error']:.3g}**, below the declared1e-12 tolerance.
Their equality verifies the coordinate identity; it cannot establish a geometric
performance advantage. At fixed rho, retained mass follows a deterministic
history-length recurrence, not a learned estimate of evidence quality.

Suite A first turns after the forced contrary outcome, with mirroring undone:

{chr(10).join(turns)}

These imposed states demonstrate history sensitivity. They do not show that all
long-support states are reachable under the chosen discount's stationary mass.
The existing native count tables already have the same support-sensitive property.

## Recovery and trajectories

Suite B delay counts observations already seen at the first forecast starting four
consecutive predictions on the reversed side of .5. Unrecovered runs are capped
at128 for the mean and separately marked censored; the cap is not an observed
recovery time.

{chr(10).join(recovery)}

![Mean pre-outcome forecasts](mean-forecasts.svg)

Mirroring is undone before plotting. Curves show means, not uncertainty bands.
Forced-four losses, generating-probability comparisons and per-run first turns
are included in [metrics.csv](metrics.csv). The initial fixed-row probability
is also the emitted output; no native agent output routing is simulated here.

## Verification and limits

Four pre-run contract tests passed. The [independent checker](../../checks/audit_heaviside_prediction.py)
imports no predictor, runner or metric implementation. It reconstructed worlds,
parameter selection, forecasts, metrics, trace samples and bootstrap intervals.
The [audit](audit.json) passed in{audit['elapsed_seconds']:.3f}s; the runner took
{result['elapsed_seconds']:.3f}s. Frozen consolidation files remained unchanged.

There were2,304,000 confirmation future updates and1,818,000 prefix updates;
development used294,912 future and387,840 prefix updates. Prefix states were
cloned for the three futures. There are323,408 materialized label entries, including
shared stable/streak observations; distinct constructed labels, counting the
forced outcomes separately, total294,640. These reuse counts are not independent
samples: the inferential unit is the200 confirmation seeds.

The observed result concerns one finite binary prediction under constructed
histories. The original native-reference comparison from the handoff remains
untested: its review timing, fixed priors, structural changes and selective
weakening need the separate Stage2 protocol identified in the review. The default
architecture is unchanged. No further benchmark starts automatically.

Artifacts: [selection](selection.json), [summary](results.json), [manifest](manifest.json),
[all forecasts and sampled event traces](runs.jsonl.gz), [confirmation worlds](confirmation-worlds.json),
[development metrics](development-metrics.csv), [standalone plot](mean-forecasts.svg).
'''
    # Keep prose spacing readable without changing numeric or measured content.
    import re
    text = re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', text)
    (OUT/'findings.md').write_text(text)
    files = ['audit.json', 'findings.md', 'mean-forecasts.svg', 'artifact-hashes.json']
    (OUT/'completion.json').write_text(json.dumps(dict(status='complete',
        stage='isolated prediction only', date='2026-11-13', tradeoff_pass=passed,
        default_changed=False, native_comparison_started=False,
        verification_hashes={p: hashlib.sha256((OUT/p).read_bytes()).hexdigest() for p in files}), indent=2)+'\n')
    print(OUT/'findings.md')


if __name__ == '__main__':
    main()
