from __future__ import annotations

import csv
import statistics
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "vault" / "Results" / "Evidence" / "mfea-native200042-final-all10-20260831" / "data.csv"
OUT_DIR = ROOT / "vault" / "Writing" / "figures"
PNG_PATH = OUT_DIR / "auto_hybrid_distribution_comparison.png"
SVG_PATH = OUT_DIR / "auto_hybrid_distribution_comparison.svg"
REGIONAL_SCENES = ["ID1", "ID3", "ID5", "ID7", "ID9", "ID10"]
GLOBAL_SCENES = ["ID2", "ID4", "ID6", "ID8"]
METHOD_ORDER = ["R-ALNS", "A-ALNS", "RK-HMA", "Auto-Hybrid"]
METHOD_COLORS = ["#999999", "#E69F00", "#0072B2", "#D55E00"]

# R-ALNS and A-ALNS values synchronized with the source RK-HMA paper [25],
# Table 4; RK-HMA values remain the reported comparison values.
REPORTED_PROFIT_RATES = {
    "ID1": [96.52, 96.29, 99.60],
    "ID2": [99.89, 99.89, 99.89],
    "ID3": [38.79, 39.91, 47.50],
    "ID4": [92.47, 92.58, 92.59],
    "ID5": [66.81, 71.69, 78.51],
    "ID6": [98.17, 98.43, 98.44],
    "ID7": [56.59, 62.71, 63.95],
    "ID8": [99.35, 99.92, 100.00],
    "ID9": [42.45, 43.41, 51.22],
    "ID10": [28.44, 29.61, 34.08],
}


def trim_svg_whitespace(svg_path: Path) -> None:
    text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8")


def display_scenario_label(scene_id: str) -> str:
    return f"Scenario\n{scene_id[2:]}"


def load_statistics() -> dict[str, float]:
    with DATA_PATH.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 50:
        raise ValueError(f"Expected 50 replay rows, found {len(rows)}")
    grouped: dict[str, list[float]] = {}
    for row in rows:
        grouped.setdefault(row["scene_id"], []).append(float(row["profit_ratio"]))
    if set(grouped) != set(REGIONAL_SCENES + GLOBAL_SCENES) or any(len(values) != 5 for values in grouped.values()):
        raise ValueError("Unexpected scene set or replicate count")
    result: dict[str, float] = {}
    for scene_id, values in grouped.items():
        mean = statistics.mean(values)
        result[scene_id] = mean
    return result


def draw_panel(
    ax: plt.Axes,
    scene_ids: list[str],
    stats: dict[str, float],
    title: str,
    ylim: tuple[float, float],
) -> None:
    x = np.arange(len(scene_ids), dtype=float)
    bar_width = 0.82 / len(METHOD_ORDER)
    offsets = (np.arange(len(METHOD_ORDER)) - (len(METHOD_ORDER) - 1) / 2) * bar_width
    for method_index, method in enumerate(METHOD_ORDER):
        positions = x + offsets[method_index]
        if method == "Auto-Hybrid":
            means = np.asarray([stats[scene_id] for scene_id in scene_ids])
            ax.bar(
                positions,
                means,
                width=bar_width * 0.92,
                color=METHOD_COLORS[method_index],
                edgecolor="#333333",
                linewidth=0.45,
                label=method,
            )
        else:
            values = np.asarray(
                [REPORTED_PROFIT_RATES[scene_id][method_index] for scene_id in scene_ids]
            )
            ax.bar(
                positions,
                values,
                width=bar_width * 0.92,
                color=METHOD_COLORS[method_index],
                edgecolor="#333333",
                linewidth=0.45,
                label=method,
            )
    ax.set_xticks(x)
    ax.set_xticklabels([display_scenario_label(scene_id) for scene_id in scene_ids], fontsize=6.3)
    ax.set_title(title)
    ax.set_ylim(*ylim)
    ax.grid(True, axis="y", color="#d5d5d5", linestyle="--", linewidth=0.55, alpha=0.85)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def main() -> None:
    stats = load_statistics()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.titlesize": 8.8,
            "axes.labelsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 7.4,
            "axes.linewidth": 0.8,
            "svg.fonttype": "none",
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.15))
    draw_panel(axes[0], REGIONAL_SCENES, stats, "Regional distribution", (0, 100))
    axes[0].set_ylabel("Profit rate (%)")
    axes[0].set_yticks([0, 20, 40, 60, 80, 100])
    draw_panel(axes[1], GLOBAL_SCENES, stats, "Global distribution", (92, 100.2))
    axes[1].set_ylabel("")
    axes[1].set_yticks(np.arange(92, 101, 1))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.995), fontsize=7.0)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.78, bottom=0.11, wspace=0.18)
    fig.savefig(PNG_PATH, dpi=450)
    fig.savefig(SVG_PATH)
    trim_svg_whitespace(SVG_PATH)
    plt.close(fig)
    print(PNG_PATH)
    print(SVG_PATH)


if __name__ == "__main__":
    main()
