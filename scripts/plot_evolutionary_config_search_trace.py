from __future__ import annotations

import csv
import re
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "outputs" / "mfea-multiscene-full-20260616" / "mfea_multiscene_full.log"
OUT_DIR = ROOT / "vault" / "Writing" / "figures"
PNG_PATH = OUT_DIR / "evolutionary_config_search_trace.png"
SVG_PATH = OUT_DIR / "evolutionary_config_search_trace.svg"
CSV_PATH = OUT_DIR / "evolutionary_config_search_trace_data.csv"

NUM_TRAINING_SCENES = 4

LINE_RE = re.compile(
    r"\[MultiScene\]\[Gen\s+(\d+)/(\d+)\]\s+"
    r"bestFitness=([0-9.]+),\s+genBest=([0-9.]+),\s+"
    r"bestConfig=\[([^\]]+)\]"
)


def parse_trace(log_path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = LINE_RE.search(line)
        if not match:
            continue
        generation = int(match.group(1))
        best_fitness = float(match.group(3))
        gen_best = float(match.group(4))
        config = "[" + ",".join(part.strip() for part in match.group(5).split(",")) + "]"
        rows.append(
            {
                "generation": generation,
                "best_fitness": best_fitness,
                "gen_best": gen_best,
                "mean_normalized_percent": best_fitness / NUM_TRAINING_SCENES * 100.0,
                "best_config": config,
            }
        )
    if not rows:
        raise RuntimeError(f"No evolutionary search generation lines found in {log_path}")
    return rows


def mark_improvements(rows: list[dict[str, object]]) -> None:
    previous = None
    for row in rows:
        current = float(row["best_fitness"])
        row["is_improvement"] = previous is None or current > previous + 1e-12
        previous = current


def write_csv(rows: list[dict[str, object]], csv_path: Path) -> None:
    fieldnames = [
        "generation",
        "best_fitness",
        "mean_normalized_percent",
        "gen_best",
        "best_config",
        "is_improvement",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_trace(rows: list[dict[str, object]]) -> None:
    generations = [int(row["generation"]) for row in rows]
    mean_fitness = [float(row["mean_normalized_percent"]) for row in rows]
    improvement_rows = [row for row in rows if row["is_improvement"]]

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.6,
        }
    )

    fig, ax = plt.subplots(figsize=(3.5, 2.35), constrained_layout=True)
    ax.plot(
        generations,
        mean_fitness,
        color="#1f77b4",
        marker="o",
        markersize=3.4,
        label="Best-so-far",
    )
    ax.scatter(
        [int(row["generation"]) for row in improvement_rows],
        [float(row["mean_normalized_percent"]) for row in improvement_rows],
        color="#d55e00",
        s=18,
        zorder=3,
        label="Improvement",
    )

    selected = next(row for row in rows if row["best_config"] == "[2,9,0,0,0,2]")
    selected_generation = int(selected["generation"])
    ax.axvline(selected_generation, color="#666666", linestyle="--", linewidth=0.8, alpha=0.75)

    annotation_specs = {
        1: {"text": "G1\n[2,0,0,0,5,2]", "xytext": (1.5, 72.985), "ha": "left"},
        5: {"text": "G5\n[2,6,0,0,0,2]", "xytext": (5.65, 72.835), "ha": "left"},
        6: {"text": "G6\n[2,9,0,0,5,0]", "xytext": (5.0, 73.055), "ha": "right"},
        9: {"text": "G9\n[9,2,0,0,0,0]", "xytext": (8.15, 73.245), "ha": "right"},
        12: {"text": "G12 selected\n[2,9,0,0,0,2]", "xytext": (12.8, 73.305), "ha": "left"},
    }
    row_by_generation = {int(row["generation"]): row for row in rows}
    for generation, spec in annotation_specs.items():
        row = row_by_generation[generation]
        ax.annotate(
            spec["text"],
            xy=(generation, float(row["mean_normalized_percent"])),
            xytext=spec["xytext"],
            arrowprops={"arrowstyle": "->", "linewidth": 0.65, "color": "#333333"},
            ha=spec["ha"],
            va="bottom",
            fontsize=5.9,
            color="#333333",
            linespacing=1.05,
        )

    ax.set_xlabel("Generation")
    ax.set_ylabel("Mean normalized fitness (%)")
    ax.set_xlim(1, 20)
    ax.set_xticks([1, 5, 10, 15, 20])
    y_margin = 0.05
    ax.set_ylim(min(mean_fitness) - y_margin, max(mean_fitness) + 0.22)
    ax.grid(True, axis="y", color="#d8d8d8", linewidth=0.55, alpha=0.8)
    ax.grid(False, axis="x")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, loc="lower right")

    fig.savefig(PNG_PATH, dpi=450)
    fig.savefig(SVG_PATH)
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = parse_trace(LOG_PATH)
    mark_improvements(rows)
    write_csv(rows, CSV_PATH)
    plot_trace(rows)
    print(PNG_PATH)
    print(SVG_PATH)
    print(CSV_PATH)


if __name__ == "__main__":
    main()
