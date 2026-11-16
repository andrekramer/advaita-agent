"""One bounded development/confirmation run; refuses to overwrite outputs."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'experiments'))
from heaviside_predictors import ARMS_A, ARMS_B, GRIDS, HISTORIES, parameter, simulate, summarize, world

OUT = ROOT/'results/heaviside-prediction-v1'
SOURCES = ['advaita-heaviside.md', 'experiments/heaviside_review.md',
           'checks/test_heaviside_feasibility.py', 'results/heaviside-feasibility-v1/attempt-01.json',
           'experiments/heaviside_prediction_protocol.md', 'experiments/heaviside_predictors.py',
           'experiments/heaviside_prediction.py', 'checks/test_heaviside_prediction.py',
           'results/heaviside-prediction-fixtures/attempt-01.json',
           'checks/audit_heaviside_prediction.py', 'experiments/report_heaviside_prediction.py']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    start = time.monotonic()
    OUT.mkdir(exist_ok=False)
    def timeout(*_):
        raise TimeoutError('Stage1 runner 900-second ceiling')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(900)
    try:
        fixture = json.loads((ROOT/'results/heaviside-prediction-fixtures/attempt-01.json').read_text())
        assert fixture['status'] == 'pass'
        for p, digest in fixture['sources'].items():
            assert sha(ROOT/p) == digest, p
        prior = ROOT/'results/control-consolidation-v1'
        frozen = json.loads((prior/'manifest.json').read_text())
        frozen.update(json.loads((prior/'completion.json').read_text())['verification_hashes'])
        for p, digest in frozen.items():
            assert sha(ROOT/p) == digest, p
        sources = {p: sha(ROOT/p) for p in SOURCES}
        write('manifest.json', dict(date='2026-11-13', sources=sources,
              frozen_dependencies=frozen, commit=subprocess.check_output(
                  ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              configuration='isolated_row; no native agent; no structural/memory review or recall'))
        development = [world(seed) for seed in range(32)]
        write('development-worlds.json', development)
        scores, selection = {}, {}
        with (OUT/'development-metrics.csv').open('x', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=['seed', 'history', 'future', 'arm', 'parameter', 'brier'])
            writer.writeheader()
            for arm, grid in GRIDS.items():
                values = []
                for value in grid:
                    losses = []
                    for w in development:
                        for h in HISTORIES:
                            for r in simulate(w, 'B', h, arm, value):
                                losses.append(r['metrics']['brier'])
                                writer.writerow({k: r[k] for k in ('seed', 'history', 'future', 'arm', 'parameter')} |
                                                dict(brier=r['metrics']['brier']))
                    values.append(sum(losses)/len(losses))
                scores[arm] = [dict(parameter=p, objective=v) for p, v in zip(grid, values)]
                selection[arm] = grid[min(range(len(grid)), key=lambda i: (values[i], i))]
        write('selection.json', dict(chosen=selection, scores=scores,
              development_world_sha256=sha(OUT/'development-worlds.json'),
              development_metrics_sha256=sha(OUT/'development-metrics.csv'), sources=sources))
        selection_hash = sha(OUT/'selection.json')
        print('Development selection frozen:', selection, flush=True)
        confirmation = [world(seed) for seed in range(1000, 1200)]
        write('confirmation-worlds.json', confirmation)
        records = []
        writer = None
        with gzip.open(OUT/'runs.jsonl.gz', 'xt') as stream, (OUT/'metrics.csv').open('x', newline='') as csv_stream:
            for w in confirmation:
                for suite, arms in [('A', ARMS_A), ('B', ARMS_B)]:
                    for h in HISTORIES:
                        for arm in arms:
                            for r in simulate(w, suite, h, arm, parameter(arm, selection), traces=w['seed'] in (1000, 1001)):
                                stream.write(json.dumps(r, separators=(',', ':'))+'\n')
                                row = {k: r[k] for k in ('seed', 'mirrored', 'suite', 'history', 'future', 'arm', 'parameter', 'first_turn')}
                                row.update({f'initial_{k}': v for k, v in r['initial'].items()})
                                row.update(r['metrics'])
                                row.update(row='category0|action0', output_source='isolated_row',
                                           effective_updates=(len(w['prefixes'][h]) if suite == 'B' else 0)+128)
                                if writer is None:
                                    writer = csv.DictWriter(csv_stream, fieldnames=list(row))
                                    writer.writeheader()
                                writer.writerow(row)
                                r.pop('events')
                                records.append(r)
                if (w['seed']-999) % 40 == 0:
                    print(f"Confirmation: {w['seed']-999}/200 seeds", flush=True)
        assert len(records) == 18000
        result = summarize(records)
        assert sha(OUT/'selection.json') == selection_hash
        for p, digest in {**frozen, **sources}.items():
            assert sha(ROOT/p) == digest, p
        counts = dict(development_runs=2304, confirmation_runs=len(records),
                      development_prefix_updates=32*12*1010, development_future_updates=2304*128,
                      confirmation_prefix_updates=200*9*1010,
                      confirmation_future_updates=len(records)*128,
                      materialized_label_entries=232*(1010+384),
                      distinct_constructed_labels_including_forced=232*(1010+256+4))
        write('results.json', dict(status='completed_pending_audit', selection=selection,
              summary=result, counts=counts, elapsed_seconds=time.monotonic()-start,
              selection_sha256=selection_hash))
        artifacts = ['development-worlds.json', 'development-metrics.csv', 'selection.json',
                     'confirmation-worlds.json', 'runs.jsonl.gz', 'metrics.csv', 'results.json', 'manifest.json']
        write('artifact-hashes.json', {p: sha(OUT/p) for p in artifacts})
        print('Trade-off gate:', result['tradeoff_pass'], flush=True)
    except BaseException as exc:
        write('incomplete.json', dict(error=repr(exc), elapsed_seconds=time.monotonic()-start))
        raise
    finally:
        signal.alarm(0)


if __name__ == '__main__':
    main()
