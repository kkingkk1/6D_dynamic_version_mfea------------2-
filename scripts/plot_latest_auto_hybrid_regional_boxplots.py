from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RK_HMA_DATA_PATH = (
    ROOT
    / "vault"
    / "Results"
    / "Evidence"
    / "paired-native-perrun0-4-10scene-20260724-r01"
    / "data.csv"
)
AUTO_HYBRID_DATA_PATH = (
    ROOT
    / "vault"
    / "Results"
    / "Evidence"
    / "mfea-native200042-final-all10-20260831"
    / "data.csv"
)
OUT_DIR = ROOT / "vault" / "Writing" / "figures"
DATA_OUT_PATH = OUT_DIR / "rk_hma_auto_hybrid_regional_boxplot_data.csv"
PNG_PATH = OUT_DIR / "rk_hma_auto_hybrid_regional_boxplots.png"
SVG_PATH = OUT_DIR / "rk_hma_auto_hybrid_regional_boxplots.svg"
REGIONAL_SCENES = ["ID1", "ID3", "ID5", "ID7", "ID9", "ID10"]
SCENE_METADATA = {
    "ID1": ("500-5-0-0-24", 500, 5),
    "ID3": ("1000-10-0-0-12", 1000, 10),
    "ID5": ("1000-20-0-0-12", 1000, 20),
    "ID7": ("4000-40-0-0-6", 4000, 40),
    "ID9": ("8000-80-0-0-12", 8000, 80),
    "ID10": ("10000-100-0-6-12", 10000, 100),
}
RK_HMA_CONFIG_KEY = "hybrid-410000"


def trim_svg_whitespace(svg_path: Path) -> None:
    text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8")


def load_values(path: Path, *, config_key: str | None = None) -> dict[str, list[float]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    grouped: dict[str, list[float]] = {scene_id: [] for scene_id in REGIONAL_SCENES}
    rows.sort(key=lambda row: (row["scene_id"], int(row.get("per_run", 0))))
    for row in rows:
        if row["scene_id"] in grouped and (
            config_key is None or row.get("config_key") == config_key
        ):
            grouped[row["scene_id"]].append(float(row["profit_ratio"]))
    if any(len(values) != 5 for values in grouped.values()):
        source = f" for {config_key}" if config_key else ""
        raise ValueError(f"Expected five regional replay values per scene{source}: {path}")
    return grouped


def local_limits(values: list[list[float]]) -> tuple[float, float]:
    flattened = [value for group in values for value in group]
    low, high = min(flattened), max(flattened)
    pad = max(0.04, (high - low) * 0.35)
    return max(0.0, low - pad), min(100.2, high + pad)


def write_source_data(
    rk_hma: dict[str, list[float]], auto_hybrid: dict[str, list[float]]
) -> None:
    with DATA_OUT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["scene_id", "scene_name", "n", "m", "rk_hma_runs", "auto_hybrid_runs"]
        )
        for scene_id in REGIONAL_SCENES:
            scene_name, task_count, satellite_count = SCENE_METADATA[scene_id]
            writer.writerow(
                [
                    scene_id,
                    scene_name,
                    task_count,
                    satellite_count,
                    ";".join(f"{value:.2f}" for value in rk_hma[scene_id]),
                    ";".join(f"{value:.2f}" for value in auto_hybrid[scene_id]),
                ]
            )


def main() -> None:
    # RK-HMA values are the five plotted points in [25], Fig. 9. The local
    # paired-native evidence is the source used to reproduce that figure.
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rk_hma = load_values(RK_HMA_DATA_PATH, config_key=RK_HMA_CONFIG_KEY)
    auto_hybrid = load_values(AUTO_HYBRID_DATA_PATH)
    rk_hma = {
        scene_id: [round(value, 2) for value in values]
        for scene_id, values in rk_hma.items()
    }
    auto_hybrid = {
        scene_id: [round(value, 2) for value in values]
        for scene_id, values in auto_hybrid.items()
    }
    write_source_data(rk_hma, auto_hybrid)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.titlesize": 9.2,
            "axes.labelsize": 8,
            "xtick.labelsize": 7.6,
            "ytick.labelsize": 7.4,
            "axes.linewidth": 0.8,
            "svg.fonttype": "none",
        }
    )
    fig, axes = plt.subplots(3, 2, figsize=(7.2, 7.6))
    offsets = np.linspace(-0.12, 0.12, 5)
    methods = [("RK-HMA", rk_hma, "#0072B2"), ("Auto-Hybrid", auto_hybrid, "#D55E00")]
    for index, scene_id in enumerate(REGIONAL_SCENES):
        ax = axes.flat[index]
        series = [values[scene_id] for _, values, _ in methods]
        for position, (label, values_by_scene, color) in enumerate(methods, start=1):
            values = values_by_scene[scene_id]
            ax.boxplot(
                [values],
                positions=[position],
                widths=0.48,
                patch_artist=True,
                showfliers=False,
                whis=(0, 100),
                boxprops={
                    "facecolor": color,
                    "alpha": 0.28,
                    "edgecolor": color,
                    "linewidth": 0.8,
                },
                medianprops={"color": "#222222", "linewidth": 0.9},
                whiskerprops={"color": "#333333", "linewidth": 0.8},
                capprops={"color": "#333333", "linewidth": 0.8},
            )
            ax.scatter(
                position + offsets,
                values,
                s=18,
                color=color,
                edgecolor="white",
                linewidth=0.35,
                zorder=4,
            )
        ax.set_xlim(0.55, 2.45)
        ax.set_xticks([1, 2])
        ax.set_xticklabels([label for label, _, _ in methods])
        ax.set_title(scene_id)
        ax.set_ylim(*local_limits(series))
        ax.set_ylabel("Profit rate (%)" if index % 2 == 0 else "")
        ax.grid(True, axis="y", color="#d5d5d5", linestyle="--", linewidth=0.55, alpha=0.85)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.text(0.5, 0.01, "Five run-level values per regional scenario", ha="center", fontsize=7.4)
    fig.subplots_adjust(left=0.10, right=0.99, top=0.97, bottom=0.06, wspace=0.25, hspace=0.45)
    fig.savefig(PNG_PATH, dpi=450)
    fig.savefig(SVG_PATH)
    trim_svg_whitespace(SVG_PATH)
    plt.close(fig)
    print(PNG_PATH)
    print(SVG_PATH)


if __name__ == "__main__":
    main()
