"""Registered small IVSR experiments 003–005; standard library only."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

from small_reversal import (Learner, STATES, VARIANTS, balanced_cues,
                            recovery_trial, score, softmax, teacher_mappings)

BASE = tuple(VARIANTS)
CONSOLIDATORS = ("hybrid", "transfer_only", "no_trigger", "no_selection")
ALL = BASE + CONSOLIDATORS + ("transfer_disabled", "parallel_extra")
SETTINGS = {"K": 20, "nu": 0.25, "threshold": 0.05, "fraction": 0.25,
            "margin": 0.001, "selection_batch": 8}


def matrix_prediction(matrix, cue):
    return softmax([0.0] + matrix[STATES.index(cue)])


class Model(Learner):
    def __init__(self, variant):
        super().__init__(variant if variant in BASE else "fast_slow")
        self.variant = variant
        self.parameters = self.parameters.copy()
        if variant in ("transfer_only", "transfer_disabled"):
            self.parameters = {"fast": (0.95, 0.22, 8), "slow": (0.999, 0.0, 8)}
        self.smoothed = 0.0

    def slow_prediction(self, cue):
        return matrix_prediction(self.weights.get("slow", [[0.0] * 3 for _ in STATES]), cue)

    def decay(self):
        for name, matrix in self.weights.items():
            rho = self.parameters[name][0]
            self.weights[name] = [[rho * w for w in row] for row in matrix]
        self.validate()

    def proposal(self):
        fast, slow = self.weights["fast"], self.weights["slow"]
        transfer = []
        for fs, ss in zip(fast, slow):
            row = []
            for f, s in zip(fs, ss):
                low, high = max(-8 - s, f - 8), min(8 - s, f + 8)
                row.append(max(low, min(high, SETTINGS["fraction"] * f)))
            transfer.append(row)
        return transfer

    def prepare(self):
        """Unlabelled diagnostics; the caller supplies no selection targets yet."""
        if self.variant not in CONSOLIDATORS:
            return None
        gaps = [[a - n for a, n in zip(self.predict(cue), self.slow_prediction(cue))]
                for cue in STATES]
        distances = [0.5 * sum(abs(g) for g in row) for row in gaps]
        current = statistics.mean(distances)
        self.smoothed = (1 - SETTINGS["nu"]) * self.smoothed + SETTINGS["nu"] * current
        opened = self.variant == "no_trigger" or (
            current > SETTINGS["threshold"] and self.smoothed > SETTINGS["threshold"])
        assert 0 <= current <= 1 and all(abs(sum(row)) < 1e-12 for row in gaps)
        return {"signed_gaps": gaps, "tv_per_input": distances, "D": current,
                "Dbar": self.smoothed, "gate": opened, "proposal": self.proposal()}

    def consolidate(self, prepared, selection):
        """Selection is None when its labels are not accessed by this learner."""
        record = dict(prepared)
        gain = None
        if not record["gate"]:
            assert selection is None
            accepted = False
        elif self.variant == "no_selection":
            assert selection is None
            accepted = True
        else:
            assert selection is not None and len(selection) == 8
            proposed_slow = [[s + c for s, c in zip(sr, cr)]
                             for sr, cr in zip(self.weights["slow"], record["proposal"])]
            details = []
            for cue, target in selection:
                before = self.slow_prediction(cue)
                after = matrix_prediction(proposed_slow, cue)
                y = STATES.index(target)
                details.append({"cue": cue, "target": target, "before": before, "after": after,
                                "gain": math.log(after[y]) - math.log(before[y])})
            gain = statistics.mean(r["gain"] for r in details)
            record["selection_predictions"] = details
            accepted = gain > SETTINGS["margin"]
        before = [self.predict(cue) for cue in STATES]
        record["weights_before_transfer"] = self.state()
        if accepted:
            for i in range(4):
                for k in range(3):
                    c = record["proposal"][i][k]
                    self.weights["fast"][i][k] -= c
                    self.weights["slow"][i][k] += c
        after = [self.predict(cue) for cue in STATES]
        error = max(abs(a - b) for old, new in zip(before, after) for a, b in zip(old, new))
        assert error < 1e-12
        self.validate()
        record.update(gain=gain, accepted=accepted, conservation_error=error,
                      weights_after_transfer=self.state(), labels_accessed=0 if selection is None else len(selection))
        return record


def evaluate(model, mapping, head="combined"):
    before = (model.state(), model.smoothed, model.clipping_count)
    predictor = model.predict if head == "combined" else model.slow_prediction
    examples = []
    for cue in STATES:
        prediction = predictor(cue)
        examples.append(score(cue, prediction, mapping[cue]))
    assert before == (model.state(), model.smoothed, model.clipping_count)
    return {"accuracy": statistics.mean(r["correct"] for r in examples),
            "loss": statistics.mean(r["loss"] for r in examples), "examples": examples}


def blocks_for(suite, stream):
    # name, number of events, observed map index (None means decay), evaluation maps
    if suite == "retention":
        return [("warmup", 240, 0, [0]), ("gap", 100, None, [0]),
                ("interference", 240, 1, [1, 0]), ("return", 240, 0, [0])]
    if suite == "noise":
        desired = 0 if stream == "transient" else 1
        return [("warmup", 240, 0, [0]), ("disturbance", 40, 1, [desired]),
                ("tail", 200, desired, [desired])]
    return [("warmup", 240, 0, [0]), ("disturbance", 40, 1, [0]),
            ("return", 200, 0, [0]), ("reversal", 240, 1, [1]), ("gap", 100, None, [1])]


def run(suite, seed, variant, stream="single"):
    model, mappings = Model(variant), teacher_mappings(seed)
    training, checkpoints, gaps, boundaries = [], {}, [], []
    main_count = selection_accessed = extra_updates = 0
    for index, (name, count, mapping_index, evaluations) in enumerate(blocks_for(suite, stream)):
        if mapping_index is None:
            for tick in range(1, count + 1):
                model.decay()
                gaps.append({"block": name, "tick": tick, "weights_after": model.state()})
        else:
            mapping = mappings[mapping_index]
            for local, cue in enumerate(balanced_cues(count, seed * 10000 + index), 1):
                prediction = model.predict(cue)
                target = mapping[cue]
                event = score(cue, prediction, target)
                assert model.observe(cue, target) == prediction
                main_count += 1
                model.validate()
                event.update(block=name, local_trial=local, trial=main_count,
                             weights_after=model.state())
                training.append(event)
                if suite == "consolidation" and main_count % SETTINGS["K"] == 0:
                    # A fresh batch from the CURRENT observed process, never the desired test map.
                    selection = [(c, mapping[c]) for c in balanced_cues(8, 500000 + seed * 1000 + main_count)]
                    boundary = {"trial": main_count, "block": name, "allocated_pairs": selection,
                                "labels_accessed": 0, "extra_updates": []}
                    prepared = model.prepare()
                    if prepared is not None:
                        use_labels = prepared["gate"] and variant != "no_selection"
                        decision = model.consolidate(prepared, selection if use_labels else None)
                        boundary["decision"] = decision
                        boundary["labels_accessed"] = decision["labels_accessed"]
                    elif variant == "parallel_extra":
                        for c, y in selection:
                            p = model.predict(c)
                            extra = score(c, p, y)
                            assert model.observe(c, y) == p
                            model.validate()
                            extra["weights_after"] = model.state()
                            boundary["extra_updates"].append(extra)
                        boundary["labels_accessed"] = len(selection)
                        extra_updates += len(selection)
                    selection_accessed += boundary["labels_accessed"]
                    boundaries.append(boundary)
        for desired in evaluations:
            key = name + ("_old" if name == "interference" and desired == 0 else "")
            checkpoints[key] = {"combined": evaluate(model, mappings[desired])}
            if suite == "consolidation":
                checkpoints[key]["slow"] = evaluate(model, mappings[desired], "slow")
    metrics = {}
    for name, heads in checkpoints.items():
        for head, values in heads.items():
            metrics[f"{name}_{head}_loss"] = values["loss"]
            metrics[f"{name}_{head}_accuracy"] = values["accuracy"]
    for name, _, _, _ in blocks_for(suite, stream):
        records = [r for r in training if r["block"] == name]
        if records:
            metrics[f"{name}_training_loss"] = statistics.mean(r["loss"] for r in records)
            metrics[f"{name}_recovery"] = recovery_trial(records)
    if suite == "retention":
        metrics["gap_loss_increase"] = metrics["gap_combined_loss"] - metrics["warmup_combined_loss"]
    if suite == "noise" and stream == "transient":
        metrics["transient_loss_increase"] = metrics["disturbance_combined_loss"] - metrics["warmup_combined_loss"]
    decisions = [b["decision"] for b in boundaries if "decision" in b]
    metrics.update(accepted_transfers=sum(d["accepted"] for d in decisions),
                   selection_labels_accessed=selection_accessed,
                   slow_norm=sum(abs(w) for row in model.weights.get("slow", []) for w in row))
    return {"suite": suite, "stream": stream, "seed": seed, "variant": variant,
            "mappings": mappings, "parameters": model.parameters, "training": training,
            "checkpoints": checkpoints, "gap_ticks": gaps, "boundaries": boundaries,
            "metrics": metrics, "clipping_count": model.clipping_count,
            "counts": {"main_pairs": main_count, "reserved_selection_pairs": 8 * len(boundaries),
                       "evaluation_pairs": 4 * sum(len(h) for h in checkpoints.values()),
                       "decay_ticks": len(gaps), "extra_gradient_updates": extra_updates,
                       "unlabelled_contexts": 4 * len(decisions)},
            "max_conservation_error": max((d["conservation_error"] for d in decisions), default=0)}


def criteria(runs):
    def m(suite, seed, variant, stream="single"):
        return next(r["metrics"] for r in runs if
                    (r["suite"], r["seed"], r["variant"], r["stream"]) == (suite, seed, variant, stream))
    rows = []
    for seed in range(5):
        dual, fast = m("retention", seed, "fast_slow"), m("retention", seed, "fast_only")
        transient, slow_transient = [m("noise", seed, v, "transient") for v in ("fast_slow", "slow_only")]
        lasting, slow_lasting = [m("noise", seed, v, "persistent") for v in ("fast_slow", "slow_only")]
        hybrid, parallel = [m("consolidation", seed, v) for v in ("hybrid", "fast_slow")]
        transfer, disabled = [m("consolidation", seed, v) for v in ("transfer_only", "transfer_disabled")]
        noise_delta = transient["transient_loss_increase"] - slow_transient["transient_loss_increase"]
        lasting_delta = lasting["tail_training_loss"] - slow_lasting["tail_training_loss"]
        retention_gain = fast["gap_combined_loss"] - dual["gap_combined_loss"]
        hybrid_gain = parallel["gap_combined_loss"] - hybrid["gap_combined_loss"]
        hybrid_cost = hybrid["reversal_training_loss"] - parallel["reversal_training_loss"]
        transfer_gain = disabled["gap_slow_loss"] - transfer["gap_slow_loss"]
        rows.append({"seed": seed, "retention_supported": retention_gain >= 0.02,
                     "retention_gain": retention_gain,
                     "noise_tradeoff_supported": noise_delta <= 0 and lasting_delta <= 0 and min(noise_delta, lasting_delta) < 0,
                     "transient_penalty_delta": noise_delta, "persistent_training_loss_delta": lasting_delta,
                     "hybrid_supported": hybrid_gain >= 0.02 and hybrid["gap_combined_accuracy"] >= 0.9 and hybrid_cost <= 0.05,
                     "hybrid_retention_gain": hybrid_gain, "hybrid_adaptation_cost": hybrid_cost,
                     "transfer_only_supported": transfer["accepted_transfers"] > 0 and transfer["slow_norm"] > 0 and transfer_gain >= 0.02,
                     "transfer_only_slow_gain": transfer_gain})
    return rows


def report(data):
    lines = ["# Round 2: small IVSR experiments 003–005", "",
             "[Protocol fixed before execution](../../experiments/round2_protocol.md). "
             "No tuning or extra benchmark seeds. Lower loss is better. All results concern "
             "four known categorical inputs; this is not a generalization or safety evaluation.", "",
             "## Registered comparisons", "",
             "| Criterion | Seeds meeting criterion |", "| --- | ---: |"]
    labels = {"retention_supported": "003: retention versus fast-only",
              "noise_tradeoff_supported": "004: noise/change tradeoff versus slow-only",
              "hybrid_supported": "005: hybrid retention gain within adaptation-cost limit",
              "transfer_only_supported": "005: useful slow learning from transfer alone"}
    for key, label in labels.items():
        lines.append(f'| {label} | {sum(r[key] for r in data["criteria"])}/5 |')
    lines += ["", "A criterion is supported here only if all five seeds meet it. These comparisons "
              "have different baselines and do not establish overall superiority.", "",
              "![Comparative results](comparisons.png)", ""]
    tables = [
        ("retention", "single", ["warmup_combined_loss", "gap_combined_loss", "interference_old_combined_loss", "return_combined_loss", "return_recovery"]),
        ("noise", "transient", ["transient_loss_increase", "tail_combined_loss", "tail_recovery"]),
        ("noise", "persistent", ["disturbance_combined_loss", "tail_training_loss", "tail_combined_loss", "tail_recovery"]),
        ("consolidation", "single", ["gap_combined_loss", "gap_slow_loss", "reversal_training_loss", "reversal_recovery", "accepted_transfers", "selection_labels_accessed"]),
    ]
    for suite, stream, keys in tables:
        lines += [f"## {suite}: {stream}", "", "Means across seeds; recovery shows median among reached runs "
                  "and the count reached, so censored runs remain visible.", "",
                  "| Model | " + " | ".join(keys) + " |", "| --- | " + " | ".join("---:" for _ in keys) + " |"]
        variants = ALL if suite == "consolidation" else BASE
        for variant in variants:
            group = [r for r in data["runs"] if (r["suite"], r["stream"], r["variant"]) == (suite, stream, variant)]
            cells = []
            for key in keys:
                vals = [r["metrics"][key] for r in group if r["metrics"][key] is not None]
                cells.append((f'{statistics.median(vals):g} ({len(vals)}/5 reached)' if vals else 'not reached (0/5)')
                             if key.endswith("recovery") else f'{statistics.mean(vals):.4f}')
            lines.append("| " + variant + " | " + " | ".join(cells) + " |")
    lines += ["", "## Every seed and paired criterion differences", "",
              "Positive retention/transfer gains favor the tested mechanism. Positive adaptation "
              "costs and noise loss differences favor its control.", "",
              "| Seed | Retention gain | Transient penalty delta | Persistent loss delta | Hybrid retention gain | Hybrid adaptation cost | Transfer-only slow gain |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for c in data["criteria"]:
        keys = ["retention_gain", "transient_penalty_delta", "persistent_training_loss_delta",
                "hybrid_retention_gain", "hybrid_adaptation_cost", "transfer_only_slow_gain"]
        lines.append(f'| {c["seed"]} | ' + " | ".join(f'{c[k]:+.4f}' for k in keys) + " |")
    lines += ["", "[Every per-seed metric and checkpoint accuracy](metrics.json). "
              "[Complete forecasts, states, selection records and hashes](results.json).", "",
              "## Accounting and limits", "", "```json", json.dumps(data["counts"], indent=2), "```", "",
              f'Maximum immediate prediction change from transfer: {data["max_conservation_error"]:.3g}. '
              f'Total clipping events: {sum(r["clipping_count"] for r in data["runs"])}.', "",
              "Selection pairs are reserved equally but accessed only by triggered selectors or "
              "parallel_extra; actual use is reported above. Parallel_extra trains on every reserved "
              "pair and applies decay on those updates. It controls for using extra labels directly, "
              "but has more update/decay events. Selection labels share the current corruption; "
              "they are not a clean oracle. No-selection transfer uses no extra targets.", "",
              "Transient errors are one correlated burst, not IID noise. The gap applies explicit "
              "decay without feedback; frozen evaluation applies neither. Old and new mappings "
              "conflict on the same input, so the model cannot identify both without context. "
              "Comparisons of four ablations cannot establish general mechanism necessity. "
              "Differential-probe contexts cover the full four-input domain here.", "",
              "```sh", "python3 experiments/round2.py", "python3 experiments/plot_round2.py  # matplotlib", "```", ""]
    return "\n".join(lines)


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=root / "results" / "round2-v1")
    args = parser.parse_args()
    # Fixed registered conditions only; no adaptive runs.
    runs = [run("retention", seed, v) for v in BASE for seed in range(5)]
    runs += [run("noise", seed, v, stream) for stream in ("transient", "persistent") for v in BASE for seed in range(5)]
    runs += [run("consolidation", seed, v) for v in ALL for seed in range(5)]
    counts = {key: sum(r["counts"][key] for r in runs) for key in runs[0]["counts"]}
    counts["allocated_labelled_presentations"] = sum(counts[k] for k in ("main_pairs", "reserved_selection_pairs", "evaluation_pairs"))
    counts["selection_labels_accessed"] = sum(r["metrics"]["selection_labels_accessed"] for r in runs)
    assert counts["allocated_labelled_presentations"] == 86880
    assert counts["decay_ticks"] == 7000 and counts["unlabelled_contexts"] == 2880
    assert counts["extra_gradient_updates"] == 1440
    files = [Path(__file__), root / "experiments" / "small_reversal.py", root / "experiments" / "round2_protocol.md"]
    data = {"experiment": "round2-v1", "settings": SETTINGS, "counts": counts,
            "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            "criteria": criteria(runs), "runs": runs,
            "max_conservation_error": max(r["max_conservation_error"] for r in runs)}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "results.json").write_text(json.dumps(data, separators=(",", ":"), allow_nan=False) + "\n")
    (args.output / "metrics.json").write_text(json.dumps([{k: r[k] for k in ("suite", "stream", "seed", "variant", "metrics", "counts")} for r in runs], indent=2) + "\n")
    (args.output / "report.md").write_text(report(data))
    print(json.dumps({"counts": counts, "criteria": data["criteria"],
                      "max_conservation_error": data["max_conservation_error"]}, indent=2))


if __name__ == "__main__":
    main()
