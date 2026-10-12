from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
HISTORY_PATH = (
    ROOT
    / "outputs"
    / "mfea-native290002-training-20260806-5seeds-2026080501-2026080505-earlystop20-5-javaw"
    / "candidate-selection-top5"
    / "generation-best-history.csv"
)
OUT_DIR = ROOT / "vault" / "Writing" / "figures"
PNG_PATH = OUT_DIR / "evolutionary_config_search_trace.png"
SVG_PATH = OUT_DIR / "evolutionary_config_search_trace.svg"
CSV_PATH = OUT_DIR / "evolutionary_config_search_trace_data.csv"
NUM_TRAINING_SCENES = 4


def trim_svg_whitespace(svg_path: Path) -> None:
    text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8")


def parse_history(history_path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with history_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for source_row in csv.DictReader(handle):
            config = "[" + ",".join(part.strip() for part in source_row["bestConfig"].split(",")) + "]"
            best_fitness = float(source_row["bestFitness"])
            rows.append(
                {
                    "outer_seed": source_row["outerSeed"],
                    "generation": int(source_row["generation"]),
                    "best_fitness": best_fitness,
                    "mean_normalized_percent": best_fitness / NUM_TRAINING_SCENES * 100.0,
                    "best_config": config,
                }
            )
    if len(rows) != 100:
        raise RuntimeError(f"Expected 100 generation records, found {len(rows)}")
    return rows


def mark_improvements(rows: list[dict[str, object]]) -> None:
    previous_by_seed: dict[str, float] = {}
    for row in sorted(rows, key=lambda item: (str(item["outer_seed"]), int(item["generation"]))):
        seed = str(row["outer_seed"])
        current = float(row["best_fitness"])
        row["is_improvement"] = seed not in previous_by_seed or current > previous_by_seed[seed] + 1e-12
        previous_by_seed[seed] = current


def write_csv(rows: list[dict[str, object]], csv_path: Path) -> None:
    fieldnames = [
        "outer_seed",
        "generation",
        "best_fitness",
        "mean_normalized_percent",
        "best_config",
        "is_improvement",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda item: (str(item["outer_seed"]), int(item["generation"]))))


def plot_trace(rows: list[dict[str, object]]) -> None:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["outer_seed"])].append(row)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 6.4,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.2,
            "svg.fonttype": "none",
        }
    )
    colors = ["#0072B2", "#009E73", "#E69F00", "#CC79A7", "#D55E00"]
    fig, ax = plt.subplots(figsize=(3.6, 2.4), constrained_layout=True)
    all_values: list[float] = []
    for color, seed in zip(colors, sorted(grouped)):
        seed_rows = sorted(grouped[seed], key=lambda item: int(item["generation"]))
        generations = [int(row["generation"]) for row in seed_rows]
        values = [float(row["mean_normalized_percent"]) for row in seed_rows]
        improvements = [row for row in seed_rows if row["is_improvement"]]
        all_values.extend(values)
        label = f"Outer seed {seed[-2:]}"
        ax.plot(generations, values, marker="o", markersize=2.2, color=color, label=label)
        ax.scatter(
            [int(row["generation"]) for row in improvements],
            [float(row["mean_normalized_percent"]) for row in improvements],
            color=color,
            edgecolor="white",
            linewidth=0.25,
            s=14,
            zorder=3,
        )

    ax.set_xlabel("Generation")
    ax.set_ylabel("Mean normalized fitness (%)")
    ax.set_xlim(1, 20)
    ax.set_xticks([1, 5, 10, 15, 20])
    ax.set_ylim(min(all_values) - 0.04, max(all_values) + 0.04)
    ax.grid(True, axis="y", color="#d8d8d8", linewidth=0.55, alpha=0.8)
    ax.grid(False, axis="x")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, loc="lower right", ncol=1)
    fig.savefig(PNG_PATH, dpi=450)
    fig.savefig(SVG_PATH)
    trim_svg_whitespace(SVG_PATH)
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = parse_history(HISTORY_PATH)
    mark_improvements(rows)
    write_csv(rows, CSV_PATH)
    plot_trace(rows)
    print(PNG_PATH)
    print(SVG_PATH)
    print(CSV_PATH)


if __name__ == "__main__":
    main()
