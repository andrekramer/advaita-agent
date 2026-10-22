"""Check saved C0 replay artifacts independently; do not import learner code."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/consolidation-core-v1'
COUNTS = {'interfaces-v1': 90, 'nested-abstractions-v1': 120, 'reclosure-v1': 80, 'form-retention-v1': 90}


def identity(r):
    return r['seed'], r['branch'], r['variant'], r['proposal_seed']


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def main():
    for name, expected in json.loads((OUT/'manifest.json').read_text()).items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected, name
    summary = json.loads((OUT/'compatibility.json').read_text())
    assert summary['status'] == 'pass'
    references = {}
    for folder, count in COUNTS.items():
        saved = json.loads((ROOT/'results'/folder/'results.json').read_text())
        assert len(saved['runs']) == count
        for r in saved['runs']:
            references[(folder,)+identity(r)] = r
    records = {(r['experiment'],)+identity(r): r for r in summary['runs']}
    assert len(records) == len(summary['runs']) == 380
    assert records.keys() == references.keys()
    seen, label_counts = set(), {folder: 0 for folder in COUNTS}
    with gzip.open(OUT/'replayed-runs.jsonl.gz', 'rt') as stream:
        for line in stream:
            item = json.loads(line)
            r, folder = item['run'], item['experiment']
            key = (folder,)+identity(r)
            assert key not in seen
            seen.add(key)
            assert r == references[key], key
            sha = digest(r)
            assert records[key]['reference_sha256'] == records[key]['replay_sha256'] == sha
            if folder == 'interfaces-v1':
                labels = len(r['main_predictions'])+r['costs']['selection_outcomes']
            elif folder == 'form-retention-v1':
                labels = r['costs']['used_labels']
            else:
                labels = r['costs']['feedback_labels']
            label_counts[folder] += labels
            if folder == 'reclosure-v1':
                evidence = records[key]['runtime_evidence']
                assert evidence == dict(main_labels=3072, selection_labels=1408,
                    selection_reuses=384 if r['variant'] == 'reclose' else 0,
                    events=813)
    assert seen == set(references)
    assert summary['replay_file_sha256'] == hashlib.sha256((OUT/'replayed-runs.jsonl.gz').read_bytes()).hexdigest()
    assert len(summary['groups']) == 4
    for group in summary['groups']:
        folder = group['experiment']
        assert group == dict(experiment=folder, runs=COUNTS[folder], exact_matches=COUNTS[folder],
                             replayed_used_label_presentations=label_counts[folder])
    assert summary['replayed_used_label_presentations'] == sum(label_counts.values())
    assert summary['new_benchmark_labels'] == 0
    assert summary['fixture_labels_including_development'] <= 20000
    assert summary['fixture_labels_including_development'] == 2*summary['fixture_labels_this_invocation']
    log = (OUT/'tests.txt').read_text()
    assert f"Ran {summary['tests']} tests" in log and '\nOK\n' in log
    print(f'PASS: {len(seen)} full replay traces, coverage, provenance, costs and runtime evidence records verified.')


if __name__ == '__main__':
    main()
