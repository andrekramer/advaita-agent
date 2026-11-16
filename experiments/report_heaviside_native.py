"""Generate the audited native comparison report and standalone forecast plot."""
import gzip
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/heaviside-native-v1'


def main():
    assert not (OUT/'findings.md').exists()
    audit=json.loads((OUT/'audit.json').read_text());assert audit['status']=='pass'
    result=json.loads((OUT/'results.json').read_text());s=result['summary']
    table=['| Candidate minus control | Stable 1–512 | Post-streak 5–20 | Reversal 129–256 |','| --- | ---: | ---: | ---: |']
    for name,vs in s['contrasts'].items():
        table.append('| '+name+' | '+' | '.join(f"{vs[f]['mean']:+.6f} [{vs[f]['low']:+.6f}, {vs[f]['high']:+.6f}]" for f in ('stable','streak','reversal'))+' |')
    by=['| Contrast | History | Stable | Post-streak | Late reversal |','| --- | --- | ---: | ---: | ---: |']
    for name,vs in s['contrasts'].items():
        for h in ('short','long'):by.append('| '+name+' | '+h+' | '+' | '.join(f"{vs[f]['by_history'][h]:+.6f}" for f in ('stable','streak','reversal'))+' |')
    weak=s['accepted_future_weakenings'];weak_table=['| History | Future | All accepted weakenings | Composite weakenings | First composite effect observation |','| --- | --- | ---: | ---: | ---: |']
    for h in ('short','long'):
        for f in ('stable','streak','reversal'):
            es=[e for e in weak if e['history']==h and e['future']==f and e['backbone']=='combined'];cs=[e for e in es if e['channel']==2]
            weak_table.append(f"| {h} | {f} | {len(es)} | {len(cs)} | {min(e['relative_tick'] for e in cs)+1 if cs else 'none'} |")
    colors=dict(reference='#444444',combined='#009E73',vector='#0072B2',fixed='#D55E00',window='#CC79A7')
    means={(h,f,a):[0.]*512 for h in ('short','long') for f in ('streak','reversal') for a in colors}
    counts={k:0 for k in means};recovery={};early={}
    with gzip.open(OUT/'runs.jsonl.gz','rt') as stream:
        for line in stream:
            r=json.loads(line)
            for arm,ps in r['predictions'].items():
                label=r['backbone'] if arm=='native' else arm
                include=(arm=='native' and r['backbone'] in ('reference','combined')) or (r['backbone']=='reference' and arm in ('vector','fixed','window'))
                if not include:continue
                key=r['history'],r['future'],label
                if key in means:
                    counts[key]+=1
                    for i,p in enumerate(ps):means[key][i]+=1-p if r['mirrored'] else p
                if r['future']=='reversal':
                    recovery.setdefault((r['history'],label),[]).append(r['metrics'][arm])
                    early.setdefault((r['history'],label),[]).append(r['metrics'][arm]['early'])
    assert set(counts.values())=={40}
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1320" height="970" viewBox="0 0 1320 970">',
         '<rect width="1320" height="970" fill="white"/><g font-family="Arial, sans-serif" font-size="15" fill="#222">',
         '<text x="60" y="35" font-size="25">Native comparison: one familiar supplied context</text>',
         '<text x="60" y="62">40 fresh outcome seeds · label mirroring undone · native reviews every 64 future observations</text>']
    for i,(label,color) in enumerate(colors.items()):
        x=60+i*235;svg.append(f'<line x1="{x}" x2="{x+25}" y1="90" y2="90" stroke="{color}" stroke-width="3"/><text x="{x+32}" y="95">{label}</text>')
    for row,f in enumerate(('streak','reversal')):
        for col,h in enumerate(('short','long')):
            x0,y0,width,height=85+640*col,150+380*row,535,280
            svg.append(f'<text x="{x0}" y="{y0-18}" font-size="19">{f} · {h} prefix</text>')
            lo,hi=(4,20) if f=='streak' else (128,256)
            svg.append(f'<rect x="{x0+width*lo/511:.2f}" y="{y0}" width="{width*(hi-lo)/511:.2f}" height="{height}" fill="#edf3fa"/>')
            for v in (0,.2,.4,.6,.8,1.):
                y=y0+height*(1-v);svg.append(f'<line x1="{x0}" x2="{x0+width}" y1="{y}" y2="{y}" stroke="#ddd"/><text x="{x0-35}" y="{y+5}">{v:.1f}</text>')
            for v in (0,64,128,256,384,511):
                x=x0+width*v/511;svg.append(f'<text x="{x-8}" y="{y0+height+23}">{v}</text>')
            for label,color in colors.items():
                points=' '.join(f'{x0+width*i/511:.2f},{y0+height*(1-p/40):.2f}' for i,p in enumerate(means[h,f,label]))
                svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.2" points="{points}"/>')
            svg.append(f'<rect x="{x0}" y="{y0}" width="{width}" height="{height}" fill="none" stroke="#666"/><text x="{x0+130}" y="{y0+height+48}">Future observations already seen</text>')
            svg.append(f'<text transform="translate({x0-52},{y0+height-10}) rotate(-90)">P(originally favoured outcome)</text>')
    svg+=['<text x="60" y="920">Blue shading marks the primary post-streak or post-two-review reversal interval.</text>',
          '<text x="60" y="946">Curves are descriptive means, not confidence bands. Scalar twin and additional controls are in the data.</text></g></svg>']
    (OUT/'mean-forecasts.svg').write_text('\n'.join(svg)+'\n');ET.parse(OUT/'mean-forecasts.svg')
    recovery_table=['| Output | History | Early reversal Brier | Capped recovery delay | Censored fraction |','| --- | --- | ---: | ---: | ---: |']
    for (h,label),ms in recovery.items():
        recovery_table.append(f"| {label} | {h} | {sum(m['early'] for m in ms)/40:.6f} | {sum(m['recovery_capped'] for m in ms)/40:.3f} | {sum(m['censored'] for m in ms)/40:.3f} |")
    native='passed' if s['native_pass'] else 'failed';attribution='passed' if s['attribution_pass'] else 'failed'
    text=f'''# Heaviside Stage 2 — native-context comparison

Completed 2026-11-13. **The native improvement criterion {native}; the separate
fixed-gain attribution criterion {attribution}.** All 240 prefixes and 720 native
future trajectories passed independent forecast, decision and learning-state
reconstruction. These yield 4,320 output records from 40 fresh outcome seeds.

This tests a contextual output intervention for one supplied familiar input.
It does not replace or improve the complete architecture by construction.

## What was compared

The [frozen protocol](../../experiments/heaviside_native_protocol.md) keeps the
ordinary native observation and review entry points: reference with its existing
archive-deleting variant, relaxed admission, and combined admission/weakening.
No native learning equations, review thresholds or proposal rules were changed.
Original native post-review inspection limitations remain; scoring uses the actual
pre-label probability returned by observation.

The same acquired state supplies one target context. Five optional readouts
(vector, scalar twin, fixed gain, window and fixed-prior counts) receive the same
main outcomes and override only that context's final probability. The address is
supplied raw input, not a newly learned category. Outside it, output remains native.
All native state evolves identically regardless of which readout is reported;
actions and future observations are exogenous. The numerical readouts also agree
across all three backbones because their inputs and initialization match.

Rho .9, gain .1 and the 192-observation window were fixed from Stage 1; there was
no further development or tuning. Short/long prefixes contain 10/1000 outcomes,
then each state branches into 512-observation stable, four-observation streak and
lasting-reversal futures. Label mirroring is a reversible input/output renaming,
not a rewrite of the acquired model. Prefixes and branches preserve pending state.

## Paired forecast effects

Candidate-minus-control Brier loss: negative is better for the named candidate.
Intervals are 95% percentile intervals from 10,000 paired seed-bootstrap samples,
averaging the two histories equally within each seed. Primary native success
requires post-streak upper bounds below zero and stable/reversal upper bounds
below +.01 against both reference and combined. Attribution additionally requires
the same comparison against fixed gain. `combined_vs_relaxed` tests the native
weakening mechanism rather than the contextual adapter.

{chr(10).join(table)}

History-specific descriptive differences:

{chr(10).join(by)}

## Did slow revision have a chance to act?

Reviews occur after future observations 64,128,...,512. The primary reversal
window129–256 follows two review opportunities, without resetting pending evidence
at the branch. Qualifying weakening is not forced. Accepted native changes were:

{chr(10).join(weak_table)}

The first-effect column is the observation after the earliest accepted composite
weakening; it is not an estimated recovery time or a guarantee of benefit. Native
structural changes also continue. Consult the combined-versus-relaxed comparison
to distinguish the usefulness of selective weakening from an adapter advantage.

## Early cost, recovery and trajectories

{chr(10).join(recovery_table)}

Recovery means the first forecast starting four consecutive predictions on the
new side of .5, counted in observations already seen. Censored delays are capped
at512 for the mean, never presented as observed recoveries.

![Mean native-context forecasts](mean-forecasts.svg)

The vector/scalar maximum per-event difference was {s['scalar_max_error']:.3g},
below 1e-12. Equality checks the representation identity; it is not evidence for
an advantage of geometric coordinates.

## Evidence budgets, verification and boundaries

Every alternative is allocated the same main and independent review rows. Native
engines fit main observations and use review labels through their existing policies.
Adapter heads fit only main outcomes; review losses are recorded without fitting
or selection. Thus available evidence is matched, while evidence use differs.
Native engines also receive the two supplied local labels. The acquired snapshot
and initial 32 target-row outcomes are reused evidence, not fresh observations.

There were 489,840 native main-row updates and 249,600 review rows across physical
backbone replays, respectively 1,469,520 and 748,800 scalar-label presentations.
Five heads perform 2,449,200 numerical updates on those same main outcomes.
The 40 worlds contain 154,320 materialized composite-label entries; 123,760 distinct
constructed positions remain after accounting for shared stable/streak data.
These presentations and output alternatives are not independent statistical samples.

Three deterministic fixture tests checked routing, active-state parity, mirrored
labels, read-only head reviews, continuation and independent native references.
The runner checked 1,440 exact checkpoint round trips. The auditor separately
reconstructed forecasts, native review decisions, final learning state, metrics
and bootstrap intervals using the earlier independent reference implementations.
It does not independently rebuild all runtime ledger metadata. The runner took
{result['elapsed_seconds']:.3f}s; independent audit took {audit['elapsed_seconds']:.3f}s.

This is one acquired/proposal state and one fixed input context with 40 fresh
outcome streams. It does not test category transfer, context discovery, policy
learning, safe steering or general superiority. Any gain can include the effect
of an explicitly addressed output alternative; the matched fixed/window controls
are essential to interpreting that gain. Earlier native and Stage 1 results are
unchanged. No architecture default is promoted and no further test is automatic.

Artifacts: [summary](results.json), [audit](audit.json), [metrics](metrics.csv),
[worlds](worlds.json), [initial state](initial.json), [manifest](manifest.json),
[prefix traces](prefixes.jsonl.gz), [native and output traces](runs.jsonl.gz),
[standalone plot](mean-forecasts.svg).
'''
    (OUT/'findings.md').write_text(text)
    files=['findings.md','mean-forecasts.svg','audit.json','artifact-hashes.json']
    (OUT/'completion.json').write_text(json.dumps(dict(status='complete',date='2026-11-13',
        native_pass=s['native_pass'],attribution_pass=s['attribution_pass'],default_changed=False,
        verification_hashes={p:hashlib.sha256((OUT/p).read_bytes()).hexdigest() for p in files}),indent=2)+'\n')
    print(OUT/'findings.md')


if __name__=='__main__':main()
