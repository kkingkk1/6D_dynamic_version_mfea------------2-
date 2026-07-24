from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "vault" / "Writing" / "figures"
PNG_PATH = OUT_DIR / "auto_hybrid_distribution_comparison.png"
SVG_PATH = OUT_DIR / "auto_hybrid_distribution_comparison.svg"

METHODS = ["R-ALNS", "A-ALNS", "DRL-PASA", "RK-HMA", "Auto-Hybrid"]
COLORS = ["#0072B2", "#009E73", "#E69F00", "#CC79A7", "#D55E00"]

SCENARIOS = [
    {"id": "ID1", "distribution": "Regional", "values": [99.05, 98.95, 99.60, 99.40, 99.62]},
    {"id": "ID2", "distribution": "Global", "values": [99.75, 99.89, 99.89, 99.89, 99.89]},
    {"id": "ID3", "distribution": "Regional", "values": [39.60, 40.20, 44.35, 47.09, 48.29]},
    {"id": "ID4", "distribution": "Global", "values": [92.57, 92.51, 92.59, 92.59, 92.59]},
    {"id": "ID5", "distribution": "Regional", "values": [56.31, 70.21, 76.35, 78.04, 79.03]},
    {"id": "ID6", "distribution": "Global", "values": [98.27, 98.37, 98.40, 98.44, 98.44]},
    {"id": "ID7", "distribution": "Regional", "values": [57.54, 62.44, 62.58, 64.05, 66.99]},
    {"id": "ID8", "distribution": "Global", "values": [99.93, 99.96, 99.98, 100.00, 100.00]},
    {"id": "ID9", "distribution": "Regional", "values": [27.12, 34.26, 37.18, 51.17, 51.46]},
    {"id": "ID10", "distribution": "Regional", "values": [20.38, 29.25, 33.95, 34.08, 34.24]},
]


def grouped_values(distribution: str) -> tuple[list[str], np.ndarray]:
    rows = [row for row in SCENARIOS if row["distribution"] == distribution]
    return [row["id"] for row in rows], np.array([row["values"] for row in rows], dtype=float)


def draw_grouped_bars(ax, labels: list[str], values: np.ndarray, ylim: tuple[float, float]) -> None:
    x = np.arange(len(labels), dtype=float)
    width = 0.15
    offsets = (np.arange(len(METHODS)) - (len(METHODS) - 1) / 2) * width

    for method_index, (method, color) in enumerate(zip(METHODS, COLORS)):
        ax.bar(
            x + offsets[method_index],
            values[:, method_index],
            width=width,
            label=method,
            color=color,
            edgecolor="#000000",
            linewidth=0.35,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(*ylim)
    ax.grid(True, axis="y", color="#d5d5d5", linestyle="--", linewidth=0.55, alpha=0.85)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.titlesize": 8.8,
            "axes.labelsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 7.4,
            "legend.fontsize": 7.2,
            "axes.linewidth": 0.8,
            "svg.fonttype": "none",
        }
    )

    regional_labels, regional_values = grouped_values("Regional")
    global_labels, global_values = grouped_values("Global")

    fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.75))

    draw_grouped_bars(axes[0], regional_labels, regional_values, (0, 100))
    axes[0].set_title("Regional distribution")
    axes[0].set_ylabel("Profit rate (%)")
    axes[0].set_yticks([0, 20, 40, 60, 80, 100])

    draw_grouped_bars(axes[1], global_labels, global_values, (92, 100.6))
    axes[1].set_title("Global distribution")
    axes[1].set_yticks(np.arange(92, 101, 1))

    handles, labels = axes[0].get_legend_handles_labels()
    fig.subplots_adjust(left=0.08, right=0.99, top=0.84, bottom=0.25, wspace=0.18)
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=len(METHODS),
        frameon=False,
        bbox_to_anchor=(0.5, 0.015),
        columnspacing=0.95,
        handlelength=1.2,
    )

    fig.savefig(PNG_PATH, dpi=450)
    fig.savefig(SVG_PATH)
    plt.close(fig)
    print(PNG_PATH)
    print(SVG_PATH)


if __name__ == "__main__":
    main()
