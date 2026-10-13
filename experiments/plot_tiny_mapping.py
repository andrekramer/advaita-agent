"""Plot saved experiment results without rerunning training. Requires matplotlib."""

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
                        default=Path(__file__).resolve().parents[1] / "results" / "tiny-mapping-v1")
    args = parser.parse_args()
    data = json.loads((args.results / "results.json").read_text())
    colors = ("#185abc", "#087f8c", "#a34b16", "#8553a0", "#ad3955")
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.facecolor": "#fafafa"})
    fig = plt.figure(figsize=(12, 8.2), layout="constrained")
    grid = fig.add_gridspec(2, 2, height_ratios=(1.25, 1))
    loss_ax = fig.add_subplot(grid[0, :])
    fast_ax = fig.add_subplot(grid[1, 0])
    slow_ax = fig.add_subplot(grid[1, 1])
    for color, run in zip(colors, data["runs"]):
        history = run["training"]
        trials = [row["trial"] for row in history]
        losses = [row["loss_before_update"] for row in history]
        smooth = [statistics.mean(losses[max(0, i - 19):i + 1]) for i in range(len(losses))]
        loss_ax.plot(trials, smooth, color=color, lw=1.6, label=f'Seed {run["seed"]}')
        for ax, field, initial in ((fast_ax, "fast_after", "fast"),
                                   (slow_ax, "slow_after", "slow")):
            for i, style in ((0, "-"), (1, "--")):
                values = [run["initial_state"][initial][i]] + [row[field][i] for row in history]
                ax.plot([0] + trials, values, color=color, ls=style, lw=1.3)
    loss_ax.axhline(math.log(2), color="#555555", ls=":", lw=1.5, label="Frozen baseline: log(2)")
    loss_ax.set(title="Prediction loss before learning from each target · trailing 20-example mean",
                xlabel="Training examples seen", ylabel="Natural log loss", xlim=(1, 200), ylim=(0, 0.75))
    loss_ax.legend(ncols=3, loc="lower left", frameon=False, fontsize=10)
    for ax, title in ((fast_ax, "Fast retained weights F"), (slow_ax, "Slow retained weights S")):
        ax.set(title=title + " · solid A, dashed B", xlabel="Training examples seen",
               ylabel="Weight", xlim=(0, 200), ylim=(-1, 1))
        ax.axhline(0, color="#aaaaaa", lw=0.7)
    for ax in (loss_ax, fast_ax, slow_ax):
        ax.grid(alpha=0.15)
    accuracies = [run["evaluation"]["accuracy"] for run in data["runs"]]
    accuracy_text = (f"{accuracies[0]:.0%} accuracy in all {len(accuracies)} seeds"
                     if min(accuracies) == max(accuracies)
                     else f"{min(accuracies):.0%}–{max(accuracies):.0%} accuracy")
    fig.suptitle("Can it learn?  A → Q, B → P\n"
                 f"Frozen evaluation: {accuracy_text}; "
                 f'mean log loss {data["mean_evaluation_log_loss"]:.3f}',
                 fontsize=17, fontweight="bold")
    fig.savefig(args.results / "learning-curves.png", dpi=170)
    fig.savefig(args.results / "learning-curves.svg")
    print(args.results / "learning-curves.png")


if __name__ == "__main__":
    main()
