"""The bounded first learning experiment; Python standard library only.

Run from the repository root: python3 experiments/tiny_mapping.py
The model receives a cue before its external target is revealed. No actions,
phase learning, delay, or consolidation are enabled in this experiment.
"""

import argparse
from dataclasses import asdict, dataclass, field
import json
import math
from pathlib import Path
import random
import statistics


@dataclass(frozen=True)
class Parameters:
    rho_fast: float = 0.95
    rho_slow: float = 0.999
    eta_fast: float = 0.20
    eta_slow: float = 0.02
    component_bound: float = 8.0


def cue_index(cue):
    return ("A", "B").index(cue)


def sigmoid(value):
    return 1.0 / (1.0 + math.exp(-value))


def log_loss(probability_p, target):
    return -math.log(probability_p if target == 1 else 1 - probability_p)


@dataclass
class FastSlowLearner:
    parameters: Parameters = field(default_factory=Parameters)
    fast: list = field(default_factory=lambda: [0.0, 0.0])
    slow: list = field(default_factory=lambda: [0.0, 0.0])

    def state(self):
        return {"fast": self.fast.copy(), "slow": self.slow.copy()}

    def predict(self, cue):
        i = cue_index(cue)
        return sigmoid(self.fast[i] + self.slow[i])

    def observe(self, cue, target):
        """One target reveal, followed by one simultaneous retained update."""
        if target not in (0, 1):
            raise ValueError("The external target must be 0 (Q) or 1 (P)")
        i = cue_index(cue)
        probability = self.predict(cue)
        gradient = [0.0, 0.0]
        gradient[i] = target - probability
        p = self.parameters

        def clip(value):
            return max(-p.component_bound, min(p.component_bound, value))

        # Inactive relations also decay, as in v1 with all gates open.
        self.fast = [clip(p.rho_fast * w + p.eta_fast * g)
                     for w, g in zip(self.fast, gradient)]
        self.slow = [clip(p.rho_slow * w + p.eta_slow * g)
                     for w, g in zip(self.slow, gradient)]
        return probability


def external_target(cue):
    """The offline teaching environment; not called by FastSlowLearner."""
    return {"A": 0, "B": 1}[cue]


def balanced_cues(count, seed):
    if count <= 0 or count % 2:
        raise ValueError("Use a positive even number of examples")
    cues = ["A"] * (count // 2) + ["B"] * (count // 2)
    random.Random(seed).shuffle(cues)
    return cues


def evaluate(model, cues):
    before = model.state()
    records = []
    for cue in cues:
        probability = model.predict(cue)
        target = external_target(cue)
        records.append({
            "cue": cue,
            "target_p": target,
            "probability_p": probability,
            "predicted_p": int(probability >= 0.5),
            "loss": log_loss(probability, target),
        })
    assert model.state() == before, "Evaluation must not update retained state"
    return {
        "accuracy": statistics.mean(r["predicted_p"] == r["target_p"] for r in records),
        "mean_log_loss": statistics.mean(r["loss"] for r in records),
        "examples": records,
    }


def run_seed(seed):
    model = FastSlowLearner()
    initial_state = model.state()
    history = []
    for trial, cue in enumerate(balanced_cues(200, seed), start=1):
        # Record a forecast before consulting the teaching environment.
        probability = model.predict(cue)
        target = external_target(cue)
        loss = log_loss(probability, target)
        used_probability = model.observe(cue, target)
        assert probability == used_probability
        assert all(math.isfinite(w) and abs(w) <= 8
                   for w in model.fast + model.slow)
        history.append({
            "trial": trial,
            "cue": cue,
            "target_p": target,
            "probability_p_before_target": probability,
            "loss_before_update": loss,
            "fast_after": model.fast.copy(),
            "slow_after": model.slow.copy(),
        })

    evaluation_cues = balanced_cues(40, 10000 + seed)
    trained = evaluate(model, evaluation_cues)
    frozen = evaluate(FastSlowLearner(), evaluation_cues)
    assert frozen["accuracy"] == 0.5
    assert abs(frozen["mean_log_loss"] - math.log(2)) < 1e-12
    passed = trained["accuracy"] >= 0.90 and trained["mean_log_loss"] < 0.5
    return {
        "seed": seed,
        "initial_state": initial_state,
        "training": history,
        "final_state": model.state(),
        "final_probability_p": {cue: model.predict(cue) for cue in ("A", "B")},
        "evaluation": trained,
        "frozen_baseline_evaluation": frozen,
        "passed": passed,
    }


def make_report(result):
    rows = [
        "# Experiment 001: can the fast/slow learner learn a mapping?",
        "",
        "**Result: " + ("PASS" if result["all_seeds_passed"] else "FAIL") + "**",
        "",
        "The fixed protocol is [protocol.md](../../experiments/tiny_mapping_protocol.md). "
        "No hyperparameter search or changes to the pass criteria were performed.",
        "",
        "| Seed | Evaluation accuracy | Mean log loss | P(P given A) | P(P given B) | Pass |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for run in result["runs"]:
        e, p = run["evaluation"], run["final_probability_p"]
        rows.append(f'| {run["seed"]} | {e["accuracy"]:.0%} | {e["mean_log_loss"]:.6f} '
                    f'| {p["A"]:.6f} | {p["B"]:.6f} | {"yes" if run["passed"] else "no"} |')
    rows += [
        "",
        "The frozen zero-weight control has 50% accuracy and log loss "
        f"{math.log(2):.6f} on every balanced evaluation set. Ties predict P.",
        "",
        "The trained model's mean evaluation log loss across seeds is "
        f'{result["mean_evaluation_log_loss"]:.6f}. Passing requires at least '
        "90% accuracy and log loss strictly below 0.5 on each seed.",
        "",
        "Each run has 200 training pairs and 40 evaluation pairs. There are 1,000 "
        "learning updates total, plus 200 read-only evaluations for each model "
        "condition. Evaluation weights remain frozen. Inputs are one-hot cues, "
        "and each target is revealed only after its forecast.",
        "",
        "![Learning and retained weight trajectories](learning-curves.png)",
        "",
        "The upper panel shows loss before each target-driven update, smoothed "
        "over the most recent 20 examples. The lower panels show separate fast "
        "and slow weights. All five seeds are shown; smoothing is for display only.",
        "",
        "## Interpretation and limits",
        "",
        "This tests acquisition and retention during frozen evaluation of a "
        "two-cue deterministic mapping. Evaluation repeats the same two input "
        "types; it does not test generalization to unseen inputs. The model and "
        "two input features are constructed; the mapping is supplied only in "
        "the external targets. No architecture search was performed.",
        "",
        "This experiment does not establish an advantage over a single-rate "
        "learner, fast-to-slow consolidation, delayed credit assignment, phase "
        "coordination, or learning new distinctions. It also does not test "
        "retention during a long period of continued decay without feedback.",
        "",
        "## Reproduce",
        "",
        "```sh",
        "python3 experiments/tiny_mapping.py",
        "python3 experiments/plot_tiny_mapping.py  # requires matplotlib",
        "```",
        "",
        "[Complete predictions, weights, parameters, and metrics](results.json).",
        "",
    ]
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parents[1] / "results" / "tiny-mapping-v1")
    args = parser.parse_args()
    runs = [run_seed(seed) for seed in range(5)]
    result = {
        "experiment": "tiny-mapping-v1",
        "mapping": {"A": "Q", "B": "P"},
        "output_encoding": {"Q": 0, "P": 1},
        "parameters": asdict(Parameters()),
        "seeds": list(range(5)),
        "training_examples_per_seed": 200,
        "evaluation_examples_per_seed": 40,
        "ties_predict": "P",
        "pass_criteria": {"minimum_accuracy": 0.90, "maximum_log_loss_exclusive": 0.5},
        "enabled": {"phase_learning": False, "input_delay": False,
                    "actions": False, "consolidation": False},
        "all_seeds_passed": all(r["passed"] for r in runs),
        "mean_evaluation_log_loss": statistics.mean(r["evaluation"]["mean_log_loss"] for r in runs),
        "runs": runs,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (args.output / "report.md").write_text(make_report(result))
    summary = {"all_seeds_passed": result["all_seeds_passed"],
               "mean_evaluation_log_loss": result["mean_evaluation_log_loss"],
               "per_seed": [{"seed": r["seed"], "accuracy": r["evaluation"]["accuracy"],
                             "log_loss": r["evaluation"]["mean_log_loss"]} for r in runs],
               "results_directory": str(args.output)}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
