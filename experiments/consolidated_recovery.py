"""019: unchanged structural learner on fresh worlds with extended recovery."""
import gzip
import hashlib
import json
from pathlib import Path
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from advaita.state import canonical
from structural_consolidation import generate, run, BRANCHES, VARIANTS
from consolidated_recovery_metrics import score, summarize

OUT = ROOT/'results/consolidated-recovery-v1'
FILES = ('experiments/consolidated_recovery_protocol.md', 'experiments/consolidated_recovery.py',
    'experiments/consolidated_recovery_metrics.py', 'checks/audit_consolidated_recovery.py',
    'checks/test_consolidated_recovery.py')


def hashes():
    previous = json.loads((ROOT/'results/structural-consolidation-v1/manifest.json').read_text())
    for name, expected in previous.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected, name
    names = set(previous) | set(FILES) | {'results/consolidated-recovery-fixtures.json'}
    names.update('results/structural-consolidation-v1/'+n for n in
        ('manifest.json', 'results.json', 'audit.json', 'runs.jsonl.gz', 'worlds.json'))
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(names)}


def totals(runs):
    evaluations = [e for r in runs for e in [r['transfer'], *r['endpoints'],
        *(v['evaluation'] for v in r['reviews'])]]
    return dict(runs=len(runs), allocated_labels=814080, generated_labels=101760,
        used_labels=sum(r['costs']['feedback_labels'] for r in runs),
        candidate_fits=sum(r['costs']['candidate_fits']+r['costs']['upper_candidate_fits'] for r in runs),
        scoring_queries=sum(r['costs']['scoring_queries'] for r in runs),
        composite_predictions=sum(len(r['predictions']) for r in runs),
        local_predictions=sum(2*sum(p is not None for p in r['local_predictions']) for r in runs),
        evaluation_predictions=sum(e['contexts'] for e in evaluations),
        oracle_context_queries=32*sum(1+len(e['removal_costs'])+len(e['raw_addition_gains']) for e in evaluations))


def main():
    fixture = json.loads((ROOT/'results/consolidated-recovery-fixtures.json').read_text())
    assert fixture['status'] == 'pass' and fixture['new_learning_labels'] == 0
    for name, expected in fixture['sources'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected, name
    OUT.mkdir(exist_ok=False)
    (OUT/'checkpoints').mkdir()
    provenance = hashes()
    (OUT/'manifest.json').write_text(json.dumps(provenance, indent=2)+'\n')
    def timeout(*_): raise TimeoutError('600-second 019 benchmark limit')
    signal.signal(signal.SIGALRM, timeout); signal.alarm(600)
    started, worlds, runs = time.monotonic(), [], []
    try:
        for seed in range(800, 805):
            for branch in BRANCHES:
                w = generate(seed, branch, sizes=(256, 4, 256, 1280, 32, 20))
                worlds.append(w)
                (OUT/'worlds.json').write_text(json.dumps(worlds)+'\n')
                for ps in (800, 801):
                    for variant in VARIANTS:
                        r, checkpoint = run(w, variant, ps, measure=False)
                        r['recovery'] = score(r, w)
                        path = f'checkpoints/{seed}-{branch}-{ps}-{variant}.json.gz'
                        with gzip.open(OUT/path, 'wt') as stream: stream.write(checkpoint)
                        r['checkpoint_file'] = path
                        runs.append(r)
                        with gzip.open(OUT/'runs.jsonl.gz', 'at') as stream: stream.write(canonical(r)+'\n')
                print(f'{seed} {branch}: {len(runs)}/120 saved', flush=True)
        assert hashes() == provenance
        resources = totals(runs)
        assert resources['used_labels'] == 641280
        assert resources['candidate_fits'] <= 26040 and resources['scoring_queries'] <= 5000000
        assert resources['composite_predictions'] == 153600 and resources['local_predictions'] == 230400
        assert resources['evaluation_predictions'] == 91200 and resources['oracle_context_queries'] <= 460800
        result = dict(status='completed_pending_audit', summary=summarize(runs), totals=resources,
            hashes=provenance, elapsed_seconds=time.monotonic()-started)
        (OUT/'results.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps({k: v for k, v in result['summary'].items() if k.endswith('_pass') or k.endswith('_checks')}, indent=2))
    except Exception as exc:
        (OUT/'incomplete.json').write_text(json.dumps(dict(error=repr(exc), completed_runs=len(runs),
            elapsed_seconds=time.monotonic()-started), indent=2)+'\n')
        raise
    finally:
        signal.alarm(0)


if __name__ == '__main__': main()
