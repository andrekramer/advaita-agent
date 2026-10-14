"""Verify saved observations and transitions; does not run new experiments."""

import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
STATES = ("00", "10", "01", "11")


def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-11, abs_tol=1e-12), (a, b)


def prediction(state, cue):
    i = STATES.index(cue)
    logits = [0.0] + [sum(matrix[i][k] for matrix in state.values()) for k in range(3)]
    terms = [math.exp(x - max(logits)) for x in logits]
    return [x / sum(terms) for x in terms]


def check_prediction(record, state):
    p = prediction(state, record["cue"])
    for a, b in zip(p, record["probabilities"]):
        close(a, b)
    close(record["loss"], -math.log(p[STATES.index(record["target"])]))
    assert record["predicted"] == STATES[max(range(4), key=p.__getitem__)]
    assert record["correct"] == (record["target"] == record["predicted"])


def check_update(record, before, parameters):
    check_prediction(record, before)
    after = record["weights_after"]
    for name, matrix in before.items():
        rho, eta, bound = parameters[name]
        for i, row in enumerate(matrix):
            for k, w in enumerate(row):
                g = (float(record["target"] == STATES[k + 1]) - record["probabilities"][k + 1]
                     if record["cue"] == STATES[i] else 0)
                close(after[name][i][k], max(-bound, min(bound, rho * w + eta * g)))
    return after


def main():
    data = json.loads((ROOT / "results/round2-v1/results.json").read_text())
    for filename, expected in data["source_sha256"].items():
        assert hashlib.sha256((ROOT / "experiments" / filename).read_bytes()).hexdigest() == expected
    total_main = total_selection = total_eval = total_gaps = accessed = 0
    for run in data["runs"]:
        state = {name: [[0.0] * 3 for _ in STATES] for name in run["parameters"]}
        boundaries = {b["trial"]: b for b in run["boundaries"]}
        gap_applied = False
        def check_gap(before):
            nonlocal total_gaps
            for tick in run["gap_ticks"]:
                after = tick["weights_after"]
                for name, matrix in before.items():
                    for i, row in enumerate(matrix):
                        for k, w in enumerate(row):
                            close(after[name][i][k], run["parameters"][name][0] * w)
                before = after
                total_gaps += 1
            return before
        for record in run["training"]:
            if run["suite"] == "retention" and record["block"] == "interference" and not gap_applied:
                state = check_gap(state)
                gap_applied = True
            state = check_update(record, state, run["parameters"])
            total_main += 1
            boundary = boundaries.get(record["trial"])
            if boundary is not None:
                pairs = boundary["allocated_pairs"]
                assert len(pairs) == 8 and all(sum(c == cue for c, _ in pairs) == 2 for cue in STATES)
                # All selection targets come from the current observed process.
                mapping_index = 0 if record["block"] in ("warmup", "return") else 1
                assert all(y == run["mappings"][mapping_index][c] for c, y in pairs)
                total_selection += len(pairs)
                accessed += boundary["labels_accessed"]
                d = boundary.get("decision")
                if d is not None:
                    assert d["weights_before_transfer"] == state
                    if d["gain"] is not None:
                        close(d["gain"], statistics.mean(r["gain"] for r in d["selection_predictions"]))
                        assert d["accepted"] == (d["gate"] and d["gain"] > .001)
                    else:
                        assert d["labels_accessed"] == 0
                        assert d["accepted"] == (d["gate"] and run["variant"] == "no_selection")
                    after = d["weights_after_transfer"]
                    for i in range(4):
                        for k in range(3):
                            c = d["proposal"][i][k] if d["accepted"] else 0
                            close(after["fast"][i][k], state["fast"][i][k] - c)
                            close(after["slow"][i][k], state["slow"][i][k] + c)
                            assert abs(after["fast"][i][k]) <= 8 and abs(after["slow"][i][k]) <= 8
                    state = after
                for extra in boundary["extra_updates"]:
                    state = check_update(extra, state, run["parameters"])
        if run["gap_ticks"] and not gap_applied:
            state = check_gap(state)
        for heads in run["checkpoints"].values():
            for checkpoint in heads.values():
                records = checkpoint["examples"]
                assert {r["cue"] for r in records} == set(STATES)
                close(checkpoint["loss"], statistics.mean(r["loss"] for r in records))
                close(checkpoint["accuracy"], statistics.mean(r["correct"] for r in records))
                total_eval += len(records)
    for suite in ("retention", "noise", "consolidation"):
        streams = ("transient", "persistent") if suite == "noise" else ("single",)
        for stream in streams:
            for seed in range(5):
                group = [r for r in data["runs"] if (r["suite"], r["stream"], r["seed"]) == (suite, stream, seed)]
                pairs = [[(e["cue"], e["target"]) for e in r["training"]] for r in group]
                assert all(p == pairs[0] for p in pairs)
    for seed in range(5):
        for variant in ("fast_slow", "fast_only", "slow_only", "frozen"):
            pair = [r for r in data["runs"] if r["suite"] == "noise" and r["seed"] == seed and r["variant"] == variant]
            assert pair[0]["training"][:280] == pair[1]["training"][:280]
    assert (total_main, total_selection, total_eval, total_gaps, accessed) == (69600, 14400, 2880, 7000, 5576)
    print("Saved-data audit passed: hashes, forecasts, 69,600 main updates, extra updates, transfers, decay,")
    print("balanced reserved selection, evaluation metrics, budgets, identical control inputs, and paired-stream isolation.")


if __name__ == "__main__":
    main()
