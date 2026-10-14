"""Plot saved Round 2 metrics without running training. Requires matplotlib."""

import argparse
import json
from pathlib import Path
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path,
                        default=Path(__file__).resolve().parents[1] / "results" / "round2-v1")
    args = parser.parse_args()
    runs = json.loads((args.results / "metrics.json").read_text())
    base = ("fast_slow", "fast_only", "slow_only", "frozen")
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), layout="constrained")
    def panel(ax, suite, stream, names, metrics, title):
        colors = ("#1765ba", "#d77820", "#12806a")
        for k, (metric, label) in enumerate(metrics):
            offset = (k - (len(metrics) - 1) / 2) * .22
            for index, name in enumerate(names):
                values = [r["metrics"][metric] for r in runs
                          if (r["suite"], r["stream"], r["variant"]) == (suite, stream, name)]
                ax.scatter([index + offset + (j - 2) * .015 for j in range(5)], values,
                           color=colors[k], alpha=.55, s=24)
                ax.scatter(index + offset, statistics.mean(values), marker="_", s=200,
                           color=colors[k], label=label if index == 0 else None)
        ax.set_xticks(range(len(names)), [n.replace("_", " ") for n in names], rotation=35, ha="right")
        ax.set(title=title, ylabel="Natural log loss / loss increase")
        ax.grid(axis="y", alpha=.15)
        ax.legend(frameon=False, fontsize=9)
    panel(axes[0, 0], "retention", "single", base,
          [("warmup_combined_loss", "Before gap"), ("gap_combined_loss", "After 100 decay ticks"),
           ("interference_old_combined_loss", "Old map after learning B")], "003 · Retention and interference")
    panel(axes[0, 1], "noise", "transient", base,
          [("transient_loss_increase", "Clean loss increase after error burst"),
           ("tail_combined_loss", "Clean loss after recovery")], "004 · Transient wrong targets")
    selected = ("fast_slow", "slow_only", "hybrid", "transfer_only", "transfer_disabled", "no_trigger", "no_selection", "parallel_extra")
    panel(axes[1, 0], "consolidation", "single", selected,
          [("gap_combined_loss", "Combined head after gap"), ("gap_slow_loss", "Slow head after gap")],
          "005 · Consolidation and retention")
    panel(axes[1, 1], "consolidation", "single", selected,
          [("reversal_training_loss", "Mean loss during lasting change")], "005 · Cost of adapting to lasting change")
    fig.suptitle("Small IVSR experiments · five seeds per condition\nDots: individual seeds; bars: means; lower loss is better", fontsize=17)
    fig.savefig(args.results / "comparisons.png", dpi=160)
    fig.savefig(args.results / "comparisons.svg")
    print(args.results / "comparisons.png")


if __name__ == "__main__":
    main()
