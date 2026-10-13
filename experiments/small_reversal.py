"""Bounded four-state reversal experiment. Python standard library only."""

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import statistics

STATES = ("00", "10", "01", "11")
# (retention, step size, absolute bound) for each independently retained array.
VARIANTS = {
    "fast_slow": {"fast": (0.95, 0.20, 8), "slow": (0.999, 0.02, 8)},
    "fast_only": {"fast": (0.95, 0.22, 16)},
    "slow_only": {"slow": (0.999, 0.22, 16)},
    "frozen": {},
}


def softmax(logits):
    maximum = max(logits)
    values = [math.exp(v - maximum) for v in logits]
    total = sum(values)
    return [v / total for v in values]


class Learner:
    def __init__(self, variant):
        self.parameters = VARIANTS[variant]
        self.weights = {name: [[0.0] * 3 for _ in STATES]
                        for name in self.parameters}
        self.clipping_count = 0

    def state(self):
        return {name: [row.copy() for row in matrix]
                for name, matrix in self.weights.items()}

    def predict(self, cue):
        i = STATES.index(cue)
        logits = [0.0] + [sum(matrix[i][k] for matrix in self.weights.values())
                          for k in range(3)]
        return softmax(logits)

    def observe(self, cue, target):
        """The target enters only here, after an external forecast is recorded."""
        i, y = STATES.index(cue), STATES.index(target)
        prediction = self.predict(cue)
        # One pre-update gradient shared by both timescales.
        for name, (rho, eta, bound) in self.parameters.items():
            matrix = self.weights[name]
            for j in range(4):
                for k in range(3):
                    gradient = (float(y == k + 1) - prediction[k + 1]) if j == i else 0.0
                    raw = rho * matrix[j][k] + eta * gradient
                    self.clipping_count += int(abs(raw) > bound)
                    matrix[j][k] = max(-bound, min(bound, raw))
        return prediction

    def validate(self):
        for name, matrix in self.weights.items():
            bound = self.parameters[name][2]
            assert all(math.isfinite(w) and abs(w) <= bound for row in matrix for w in row)


def balanced_cues(count, seed):
    if count <= 0 or count % 4:
        raise ValueError("Example count must be positive and divisible by four")
    cues = list(STATES) * (count // 4)
    random.Random(seed).shuffle(cues)
    return cues


def teacher_mappings(seed):
    rng = random.Random(seed)
    first = list(STATES)
    rng.shuffle(first)
    changed = [p for p in itertools.permutations(STATES)
               if all(a != b for a, b in zip(first, p))]
    second = rng.choice(changed)
    return [dict(zip(STATES, first)), dict(zip(STATES, second))]


def score(cue, probabilities, target):
    assert all(math.isfinite(p) and 0 < p < 1 for p in probabilities)
    assert math.isclose(sum(probabilities), 1, abs_tol=1e-12)
    predicted = STATES[max(range(4), key=probabilities.__getitem__)]
    return {"cue": cue, "target": target, "probabilities": probabilities,
            "predicted": predicted, "correct": predicted == target,
            "loss": -math.log(probabilities[STATES.index(target)])}


def evaluate(model, cues, mapping):
    before, clips = model.state(), model.clipping_count
    examples = []
    for cue in cues:
        probabilities = model.predict(cue)
        examples.append(score(cue, probabilities, mapping[cue]))
    assert model.state() == before and model.clipping_count == clips
    accuracy = statistics.mean(row["correct"] for row in examples)
    loss = statistics.mean(row["loss"] for row in examples)
    return {"accuracy": accuracy, "mean_log_loss": loss,
            "passed": accuracy >= 0.9 and loss < 0.9, "examples": examples}


def recovery_trial(history):
    for end in range(40, len(history) + 1):
        if sum(r["correct"] for r in history[end - 40:end]) >= 36:
            return end
    return None


def run_seed(seed, variant):
    mappings = teacher_mappings(seed)
    model = Learner(variant)
    history, evaluations = [], []
    for phase in (1, 2):
        mapping = mappings[phase - 1]
        for trial, cue in enumerate(balanced_cues(400, phase * 1000 + seed), 1):
            probabilities = model.predict(cue)
            # The teacher, outside the learner, reveals the target afterwards.
            target = mapping[cue]
            record = score(cue, probabilities, target)
            assert model.observe(cue, target) == probabilities
            model.validate()
            record.update(phase=phase, phase_trial=trial,
                          trial=(phase - 1) * 400 + trial, weights_after=model.state())
            history.append(record)
        evaluations.append(evaluate(model, balanced_cues(100, (phase + 2) * 1000 + seed), mapping))
    return {"seed": seed, "variant": variant, "mappings": mappings,
            "training": history, "evaluations": evaluations,
            "phase_training_log_loss": [statistics.mean(r["loss"] for r in history if r["phase"] == p)
                                        for p in (1, 2)],
            "recovery_trial": recovery_trial(history[400:]),
            "clipping_count": model.clipping_count, "final_state": model.state(),
            "passed": all(e["passed"] for e in evaluations)}


def summarize(runs):
    summary = {}
    for variant in VARIANTS:
        group = [r for r in runs if r["variant"] == variant]
        recoveries = [r["recovery_trial"] for r in group if r["recovery_trial"] is not None]
        summary[variant] = {
            "seeds_passed": sum(r["passed"] for r in group),
            "evaluation_accuracy": [statistics.mean(r["evaluations"][p]["accuracy"] for r in group)
                                    for p in (0, 1)],
            "evaluation_log_loss": [statistics.mean(r["evaluations"][p]["mean_log_loss"] for r in group)
                                    for p in (0, 1)],
            "phase_training_log_loss": [statistics.mean(r["phase_training_log_loss"][p] for r in group)
                                        for p in (0, 1)],
            "recovered_seeds": len(recoveries),
            "median_recovery_trial": statistics.median(recoveries) if recoveries else None,
            "clipping_count": sum(r["clipping_count"] for r in group),
        }
    return summary


def make_report(result):
    lines = ["# Experiment 002: four-state learning and reversal", "",
             "**Primary fast/slow result: " + ("PASS" if result["all_fast_slow_passed"] else "FAIL") + "**", "",
             "[Fixed protocol](../../experiments/small_reversal_protocol.md). "
             "Parameters and criteria were fixed before the run; no tuning was performed.", "",
             "The target mapping changes after training pair 400. Each evaluation freezes all "
             "state and contains 25 examples of each of the four known inputs.", "",
             "| Model | Phase 1 accuracy | Phase 1 loss | Phase 2 accuracy | Phase 2 loss | Median recovery trial | Seeds passing both |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for name, s in result["summary"].items():
        a, loss = s["evaluation_accuracy"], s["evaluation_log_loss"]
        recovery = s["median_recovery_trial"]
        lines.append(f'| {name} | {a[0]:.0%} | {loss[0]:.4f} | {a[1]:.0%} | {loss[1]:.4f} | '
                     f'{recovery if recovery is not None else "not reached"} | {s["seeds_passed"]}/5 |')
    lines += ["", "Accuracy and loss above are means across seeds. Recovery counts post-change training "
              "pairs to the first trailing-40 accuracy of at least 90%; it does not guarantee sustained recovery.", "",
              "![Learning curves and evaluation comparisons](learning-curves.png)", "",
              "## Every seed", "",
              "| Model | Seed | Phase 1 accuracy / loss | Phase 2 accuracy / loss | Phase 2 training loss | Recovery | Pass |",
              "| --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for r in result["runs"]:
        first, second = r["evaluations"]
        lines.append(f'| {r["variant"]} | {r["seed"]} | {first["accuracy"]:.0%} / {first["mean_log_loss"]:.4f} | '
                     f'{second["accuracy"]:.0%} / {second["mean_log_loss"]:.4f} | '
                     f'{r["phase_training_log_loss"][1]:.4f} | '
                     f'{r["recovery_trial"] if r["recovery_trial"] is not None else "not reached"} | '
                     f'{"yes" if r["passed"] else "no"} |')
    lines += ["", "## Paired comparisons", "",
              "Differences are fast/slow minus control on the same seed and data. Negative "
              "loss differences favor fast/slow. Negative recovery differences mean earlier threshold crossing.", "",
              "| Control | Seed | Phase 2 evaluation loss difference | Phase 2 training loss difference | Recovery difference |",
              "| --- | ---: | ---: | ---: | ---: |"]
    for seed in range(5):
        dual = next(r for r in result["runs"] if r["seed"] == seed and r["variant"] == "fast_slow")
        for variant in ("fast_only", "slow_only"):
            control = next(r for r in result["runs"] if r["seed"] == seed and r["variant"] == variant)
            delta = (dual["recovery_trial"] - control["recovery_trial"]
                     if dual["recovery_trial"] is not None and control["recovery_trial"] is not None else "unavailable")
            lines.append(f'| {variant} | {seed} | '
                         f'{dual["evaluations"][1]["mean_log_loss"] - control["evaluations"][1]["mean_log_loss"]:+.4f} | '
                         f'{dual["phase_training_log_loss"][1] - control["phase_training_log_loss"][1]:+.4f} | {delta} |')
    lines += ["", "## Checks and limits", "",
              f'All probabilities were finite and normalized, and all weights remained within bounds. '
              f'Total clipping events: {sum(r["clipping_count"] for r in result["runs"])}. '
              'Evaluation preserved all weights and counters.', "",
              "Exactly 20,000 presentations: 16,000 training presentations (12,000 update events "
              "and 4,000 frozen-control presentations), plus 4,000 evaluation presentations.", "",
              "Passing requires at least 90% accuracy and loss below 0.9 in both frozen "
              "evaluations for every fast/slow seed. Uniform baseline loss is log(4), about 1.3863.", "",
              "This tests four categorical associations and relearning after a mapping change. "
              "The one-hot input representation and all output categories are constructed. "
              "It does not test compositional use of both/neither, unseen-input generalization, "
              "evolving distinctions, phase coordination, consolidation, interpretability, "
              "steering, or safety. Both timescales learn directly from external targets.", "",
              "The controls match the initial effective step and possible weight range, but "
              "are not tuned; the dual model stores twice as many parameters. Five seeds "
              "on one deterministic task do not establish general superiority. Frozen "
              "evaluations do not test long-term retention under continued decay.", "",
              "## Reproduce", "", "```sh", "python3 experiments/small_reversal.py",
              "python3 experiments/plot_small_reversal.py  # requires matplotlib", "```", "",
              "[Complete data](results.json) include the protocol and implementation SHA-256 "
              "hashes, mappings, parameters, every forecast and target, weight trajectories, and evaluations.", ""]
    return "\n".join(lines)


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=root / "results" / "small-reversal-v1")
    args = parser.parse_args()
    runs = [run_seed(seed, variant) for variant in VARIANTS for seed in range(5)]
    assert sum(len(r["training"]) + sum(len(e["examples"]) for e in r["evaluations"]) for r in runs) == 20000
    result = {
        "experiment": "small-reversal-v1", "states": STATES, "parameters": VARIANTS,
        "seeds": list(range(5)), "presentations": 20000, "weight_update_events": 12000,
        "pass_criteria": {"minimum_accuracy": 0.9, "maximum_log_loss_exclusive": 0.9,
                          "required": "both phases, every fast_slow seed"},
        "enabled": {"consolidation": False, "phase_learning": False, "actions": False},
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                          (Path(__file__), root / "experiments" / "small_reversal_protocol.md")},
        "all_fast_slow_passed": all(r["passed"] for r in runs if r["variant"] == "fast_slow"),
        "summary": summarize(runs), "runs": runs,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (args.output / "report.md").write_text(make_report(result))
    print(json.dumps({"all_fast_slow_passed": result["all_fast_slow_passed"],
                      "summary": result["summary"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
