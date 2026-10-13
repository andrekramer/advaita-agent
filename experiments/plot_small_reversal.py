"""Plot saved results without rerunning training. Requires matplotlib."""

import argparse
import json
import math
from pathlib import Path
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path,
                        default=Path(__file__).resolve().parents[1] / "results" / "small-reversal-v1")
    args = parser.parse_args()
    data = json.loads((args.results / "results.json").read_text())
    names = ("fast_slow", "fast_only", "slow_only", "frozen")
    labels = ("Fast + slow", "Fast only", "Slow only", "Frozen")
    colors = ("#1765ba", "#d77820", "#12806a", "#777777")
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False})
    fig = plt.figure(figsize=(12, 8), layout="constrained")
    grid = fig.add_gridspec(2, 2, height_ratios=(1.3, 1))
    ax = fig.add_subplot(grid[0, :])
    evaluation_ax = fig.add_subplot(grid[1, 0])
    recovery_ax = fig.add_subplot(grid[1, 1])
    for index, (name, label, color) in enumerate(zip(names, labels, colors)):
        runs = [r for r in data["runs"] if r["variant"] == name]
        for phase in (1, 2):
            trajectories = []
            for run in runs:
                losses = [r["loss"] for r in run["training"] if r["phase"] == phase]
                smooth = [statistics.mean(losses[max(0, i - 39):i + 1]) for i in range(400)]
                trajectories.append(smooth)
                ax.plot(range(1 + (phase - 1) * 400, phase * 400 + 1), smooth,
                        color=color, alpha=0.18, lw=0.9)
            mean = [statistics.mean(values) for values in zip(*trajectories)]
            ax.plot(range(1 + (phase - 1) * 400, phase * 400 + 1), mean, color=color,
                    lw=2, label=label if phase == 1 else None)
        for p, marker, offset in ((0, "o", -0.12), (1, "s", 0.12)):
            values = [r["evaluations"][p]["mean_log_loss"] for r in runs]
            evaluation_ax.scatter([index + offset + (s - 2) * 0.018 for s in range(5)], values,
                                  color=color, marker=marker, s=35, alpha=0.8)
        for s, run in enumerate(runs):
            recovery = run["recovery_trial"]
            recovery_ax.scatter(index + (s - 2) * 0.04, recovery if recovery is not None else 425,
                                color=color, marker="o" if recovery is not None else "x", s=35)
    ax.axvline(400.5, color="#333333", ls="--", lw=1)
    ax.set(title="Prediction loss · trailing 40 pairs, reset at mapping change",
           xlabel="Training pairs (mapping changes after 400)", ylabel="Natural log loss", xlim=(1, 800))
    ax.legend(ncols=4, frameon=False)
    evaluation_ax.axhline(0.9, color="#999999", ls=":", label="Pass loss threshold")
    evaluation_ax.set(title="Frozen evaluation · circles phase 1, squares phase 2",
                      ylabel="Natural log loss", ylim=(0, math.log(4) + 0.15))
    evaluation_ax.legend(frameon=False, fontsize=9)
    recovery_ax.axhline(400, color="#999999", ls=":")
    recovery_ax.set(title="Recovery · each dot is one seed", ylabel="Post-change training pairs",
                    ylim=(0, 455), yticks=[0, 100, 200, 300, 400, 425],
                    yticklabels=["0", "100", "200", "300", "400", "Not reached"])
    for bottom in (evaluation_ax, recovery_ax):
        bottom.set_xticks(range(4), labels)
    for axis in (ax, evaluation_ax, recovery_ax):
        axis.grid(alpha=0.12)
    fig.suptitle("Four-state learning and reversal\nFive seeds per model · thin curves individual, thick curves mean",
                 fontsize=16, fontweight="bold")
    fig.savefig(args.results / "learning-curves.png", dpi=170)
    fig.savefig(args.results / "learning-curves.svg")
    print(args.results / "learning-curves.png")


if __name__ == "__main__":
    main()
