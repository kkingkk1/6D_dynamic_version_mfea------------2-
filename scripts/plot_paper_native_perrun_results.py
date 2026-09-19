#!/usr/bin/env python3
"""Generate manuscript Fig. 6 and Fig. 9 from the corrected native perRun evidence."""

from __future__ import annotations

import csv
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pubfig as pf


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = (
    ROOT
    / "vault"
    / "Results"
    / "Evidence"
    / "paired-native-perrun0-4-10scene-20260724-r01"
    / "data.csv"
)
OUTPUT_DIR = ROOT / "vault" / "Writing" / "images"

SCENE_ORDER = [f"ID{index}" for index in range(1, 11)]
REGIONAL_SCENES = ["ID1", "ID3", "ID5", "ID7", "ID9", "ID10"]
GLOBAL_SCENES = ["ID2", "ID4", "ID6", "ID8"]
ALGORITHM_ORDER = ["hybrid-410000", "parent-4", "parent-1"]
ALGORITHM_LABELS = {
    "hybrid-410000": "RK-HMA",
    "parent-4": "DE/rand/1",
    "parent-1": "PSO",
}
ALGORITHM_COLORS = {
    "hybrid-410000": "#0072B2",
    "parent-4": "#009E73",
    "parent-1": "#D55E00",
}
BASELINE_ORDER = ["R-ALNS", "A-ALNS", "RK-HMA"]
BASELINE_COLORS = ["#999999", "#E69F00", "#0072B2"]
PAPER_THEME = replace(pf.themes.get_theme("nature"), font_family=["DejaVu Sans"])
PAPER_SPEC = pf.FigureSpec(name="rk-hma", font_family="DejaVu Sans")
EXTERNAL_PROFIT_RATES = {
    "ID1": [96.52, 96.29],
    "ID2": [99.89, 99.89],
    "ID3": [38.79, 39.91],
    "ID4": [92.47, 92.58],
    "ID5": [66.81, 71.69],
    "ID6": [98.17, 98.43],
    "ID7": [56.59, 62.71],
    "ID8": [99.35, 99.92],
    "ID9": [42.45, 43.41],
    "ID10": [28.44, 29.61],
}


def load_rows() -> list[dict[str, str]]:
    with DATA_PATH.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 200:
        raise ValueError(f"Expected 200 canonical rows, found {len(rows)}")
    if set(row["scene_id"] for row in rows) != set(SCENE_ORDER):
        raise ValueError("Unexpected scene set in canonical data")
    return rows


def values_for(
    rows: list[dict[str, str]], scene_id: str, config_key: str
) -> list[float]:
    selected = [
        row
        for row in rows
        if row["scene_id"] == scene_id and row["config_key"] == config_key
    ]
    selected.sort(key=lambda row: int(row["per_run"]))
    if len(selected) != 5:
        raise ValueError(f"Expected five runs for {scene_id}/{config_key}")
    return [float(row["profit_ratio"]) for row in selected]


def fifth_rk_hma(rows: list[dict[str, str]], scene_id: str) -> float:
    selected = [
        row
        for row in rows
        if row["scene_id"] == scene_id
        and row["config_key"] == "hybrid-410000"
        and row["per_run"] == "4"
    ]
    if len(selected) != 1:
        raise ValueError(f"Missing unique fifth RK-HMA run for {scene_id}")
    return float(selected[0]["profit_ratio"])


def export(fig: plt.Figure, stem: str, height_mm: float) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pf.batch_export(
        fig,
        OUTPUT_DIR / stem,
        formats=("png", "svg"),
        spec=PAPER_SPEC,
        width="double",
        height_mm=height_mm,
        dpi=400,
        transparent=False,
        trim=False,
        svg_fonttype="none",
    )


def draw_figure_6(rows: list[dict[str, str]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.25), sharey=True)
    for axis, scene_ids, panel_label in (
        (axes[0], REGIONAL_SCENES, "(a) Regional scenarios"),
        (axes[1], GLOBAL_SCENES, "(b) Global scenarios"),
    ):
        values = np.asarray(
            [
                EXTERNAL_PROFIT_RATES[scene_id] + [fifth_rk_hma(rows, scene_id)]
                for scene_id in scene_ids
            ],
            dtype=float,
        )
        pf.bar(
            values,
            category_names=scene_ids,
            series_names=BASELINE_ORDER,
            category_spacing=0.88,
            x_label="Scenario",
            y_label="Profit rate (%)",
            color_palette=BASELINE_COLORS,
            grouped_total_span=0.72,
            grouped_bar_width_ratio=0.88,
            grouped_bar_edgecolor="#333333",
            grouped_bar_line_width=0.25,
            legend_show=False,
            show_x_grid=False,
            show_y_grid=True,
            theme=PAPER_THEME,
            ax=axis,
        )
        axis.set_ylim(0.0, 105.0)
        axis.set_title(panel_label, fontsize=9.5, pad=5)
        axis.tick_params(axis="x", labelsize=8.2)
    axes[1].set_ylabel("")
    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor="#333333", linewidth=0.25)
        for color in BASELINE_COLORS
    ]
    fig.legend(
        handles,
        BASELINE_ORDER,
        loc="upper center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, 1.03),
        fontsize=8.3,
    )
    fig.subplots_adjust(left=0.08, right=0.99, top=0.77, bottom=0.17, wspace=0.12)
    export(fig, "fig6_profit_rate_by_distribution", height_mm=84)
    plt.close(fig)


def local_limits(series: list[list[float]]) -> tuple[float, float]:
    values = [value for group in series for value in group]
    span = max(values) - min(values)
    pad = max(0.04, span * 0.10)
    return max(0.0, min(values) - pad), min(100.2, max(values) + pad)


def draw_figure_9(rows: list[dict[str, str]]) -> None:
    fig, axes = plt.subplots(3, 2, figsize=(7.2, 8.0))
    colors = [ALGORITHM_COLORS[key] for key in ALGORITHM_ORDER]
    offsets = np.asarray([-0.10, -0.05, 0.0, 0.05, 0.10])
    panel_letters = "abcdef"
    for panel_index, scene_id in enumerate(REGIONAL_SCENES):
        axis = axes.flat[panel_index]
        series = [
            np.asarray(values_for(rows, scene_id, config_key), dtype=float)
            for config_key in ALGORITHM_ORDER
        ]
        pf.box(
            series,
            category_names=[ALGORITHM_LABELS[key] for key in ALGORITHM_ORDER],
            category_spacing=1.0,
            color_palette=colors,
            box_face_alpha=0.28,
            box_width=0.52,
            line_color="#333333",
            show_means=False,
            show_fliers=False,
            tick_direction="out",
            show_full_box=False,
            show_x_grid=False,
            show_y_grid=True,
            theme=PAPER_THEME,
            ax=axis,
        )
        for position, (config_key, run_values) in enumerate(
            zip(ALGORITHM_ORDER, series), start=1
        ):
            axis.scatter(
                position + offsets,
                run_values,
                s=12,
                marker="o",
                facecolor=ALGORITHM_COLORS[config_key],
                edgecolor="white",
                linewidth=0.35,
                zorder=4,
            )
        axis.set_ylim(*local_limits(series))
        axis.set_title(f"({panel_letters[panel_index]}) {scene_id}", fontsize=9.5, pad=5)
        axis.tick_params(axis="x", labelsize=7.8)
        axis.tick_params(axis="y", labelsize=8.0)
        axis.set_ylabel("Profit rate (%)" if panel_index % 2 == 0 else "")
    fig.subplots_adjust(left=0.10, right=0.99, top=0.98, bottom=0.07, wspace=0.28, hspace=0.42)
    export(fig, "fig9_hybrid_parent_profit_distributions", height_mm=205)
    plt.close(fig)


def main() -> int:
    rows = load_rows()
    draw_figure_6(rows)
    draw_figure_9(rows)
    print(f"pubfig={pf.__version__}")
    for stem in (
        "fig6_profit_rate_by_distribution",
        "fig9_hybrid_parent_profit_distributions",
    ):
        for suffix in (".png", ".svg"):
            output = OUTPUT_DIR / f"{stem}{suffix}"
            if not output.exists() or output.stat().st_size == 0:
                raise ValueError(f"Missing output: {output}")
            print(output.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
