from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "vault" / "Writing" / "figures"
PNG_PATH = OUT_DIR / "automatic_hybrid_design_flow.png"
SVG_PATH = OUT_DIR / "automatic_hybrid_design_flow.svg"


def add_box(ax, xy, width, height, text, facecolor, edgecolor="#253244"):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.025,rounding_size=0.035",
        linewidth=1.2,
        edgecolor=edgecolor,
        facecolor=facecolor,
        zorder=2,
    )
    ax.add_patch(patch)
    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=8.4,
        color="#172033",
        linespacing=1.18,
        zorder=3,
    )
    return patch


def add_arrow(ax, start, end, rad=0.0, label=None, label_offset=(0, 0)):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=1.25,
        color="#44536a",
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=6,
        shrinkB=6,
        zorder=1,
    )
    ax.add_patch(arrow)
    if label:
        mx = (start[0] + end[0]) / 2 + label_offset[0]
        my = (start[1] + end[1]) / 2 + label_offset[1]
        ax.text(
            mx,
            my,
            label,
            ha="center",
            va="center",
            fontsize=7.8,
            color="#4a5668",
            zorder=4,
        )


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.linewidth": 0.8,
            "svg.fonttype": "none",
        }
    )

    fig, ax = plt.subplots(figsize=(7.6, 3.15))
    ax.set_xlim(0, 14.8)
    ax.set_ylim(0, 5.05)
    ax.axis("off")

    design_color = "#e9f1fb"
    eval_color = "#eef6ec"
    replay_color = "#fff4df"
    selected_color = "#f3eaf7"

    boxes = {
        "library": add_box(
            ax,
            (0.3, 3.22),
            2.1,
            0.95,
            "Component\nlibraries",
            design_color,
        ),
        "chromosome": add_box(
            ax,
            (3.0, 3.22),
            2.25,
            0.95,
            "Semantic optimizer\nchromosome",
            design_color,
        ),
        "search": add_box(
            ax,
            (5.95, 3.22),
            2.15,
            0.95,
            "Evolutionary\nsearch stage",
            design_color,
        ),
        "hybcec": add_box(
            ax,
            (3.0, 1.34),
            2.25,
            0.95,
            "Decoded HybCec\noptimizer",
            eval_color,
        ),
        "schedule": add_box(
            ax,
            (5.95, 1.34),
            2.35,
            0.95,
            "Scheduling\nwith dynamic\nreassignment",
            eval_color,
        ),
        "fitness": add_box(
            ax,
            (9.0, 1.34),
            1.85,
            0.95,
            "Normalized\nprofit",
            eval_color,
        ),
        "selected": add_box(
            ax,
            (9.0, 3.22),
            1.85,
            0.95,
            "Selected\noptimizer",
            selected_color,
        ),
        "replay": add_box(
            ax,
            (12.0, 1.34),
            2.25,
            0.95,
            "Full-budget replay\non ten scenarios",
            replay_color,
        ),
    }

    add_arrow(ax, (2.4, 3.7), (3.0, 3.7))
    add_arrow(ax, (5.25, 3.7), (5.95, 3.7))
    add_arrow(ax, (7.05, 3.22), (4.1, 2.29), rad=0.08, label="decode", label_offset=(-0.05, -0.05))
    add_arrow(ax, (5.25, 1.81), (5.95, 1.81))
    add_arrow(ax, (8.3, 1.81), (9.0, 1.81))
    add_arrow(ax, (9.92, 2.29), (7.05, 3.22), rad=0.08, label="fitness feedback", label_offset=(0.05, 0.0))
    add_arrow(ax, (8.1, 3.7), (9.0, 3.7))
    add_arrow(ax, (10.85, 3.7), (12.0, 1.81), rad=-0.08)

    ax.text(
        0.35,
        4.62,
        "Automatic design stage",
        ha="left",
        va="center",
        fontsize=9.4,
        fontweight="bold",
        color="#263449",
    )
    ax.text(
        11.95,
        2.85,
        "Verification stage",
        ha="left",
        va="center",
        fontsize=9.4,
        fontweight="bold",
        color="#263449",
    )

    ax.text(
        3.0,
        0.55,
        "Each chromosome is evaluated by running the complete scheduling pipeline,\n"
        "not by optimizing a task sequence directly.",
        ha="left",
        va="center",
        fontsize=8.2,
        color="#5b6678",
    )

    fig.tight_layout(pad=0.2)
    fig.savefig(PNG_PATH, dpi=450)
    fig.savefig(SVG_PATH)
    plt.close(fig)


if __name__ == "__main__":
    main()
