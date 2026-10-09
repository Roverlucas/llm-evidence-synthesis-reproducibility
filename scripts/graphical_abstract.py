"""Graphical abstract for the journal submission.

Every number drawn comes from analysis/reproducibility_results.json (frozen in FREEZE.yaml).
Output: article/graphical_abstract.pdf and article/graphical_abstract.png. The journal asks
for 531 x 1328 px (h x w) or proportionally more, readable at 5 x 13 cm; the figure is drawn
at exactly 5 x 13 cm and the PNG is rendered at 600 dpi (1181 x 3070 px).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "analysis" / "reproducibility_results.json"
OUT = ROOT / "article" / "graphical_abstract"

STACKS = [  # (key, label, local)
    ("llama3-8b", "LLaMA 3 8B", True),
    ("mistral-7b", "Mistral 7B", True),
    ("gemma2-9b", "Gemma 2 9B", True),
    ("claude-sonnet-4-5-t0", "Claude Sonnet 4.5", False),
    ("gemini-2.5-pro", "Gemini 2.5 Pro", False),
    ("gpt-4.1", "GPT-4.1", False),
]
LOCAL, API = "#2196F3", "#FF9800"   # colours of the article's EMR figure
CM = 1 / 2.54


def main() -> None:
    res = json.loads(RESULTS.read_text())
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 6.5})
    fig = plt.figure(figsize=(13 * CM, 5 * CM))

    # Left: what was done.
    txt = fig.add_axes([0.0, 0.0, 0.42, 1.0])
    txt.axis("off")
    txt.text(0.06, 0.82, "Same prompt, same input, temperature 0", fontsize=7.5, weight="bold", va="top")
    lines = [
        "500 abstracts, PM$_{2.5}$ and respiratory health",
        "screening + structured extraction",
        "6 deployment stacks $\\times$ 10 identical runs",
        "every call hashed (SHA-256) and logged",
    ]
    for i, s in enumerate(lines):
        txt.text(0.06, 0.70 - i * 0.12, "• " + s, va="top")
    txt.text(0.06, 0.16, "Local stacks reproduced exactly;\nAPI-served stacks did not.",
             fontsize=7.5, weight="bold", va="top")

    # Right: extraction EMR with 95% bootstrap CI.
    ax = fig.add_axes([0.64, 0.26, 0.33, 0.56])
    for y, (key, label, local) in enumerate(STACKS[::-1]):
        e = res[key]["extraction"]
        ax.barh(y, e["emr"], color=LOCAL if local else API, height=0.62)
        ax.errorbar(e["emr"], y, xerr=[[e["emr"] - e["ci_lower"]], [e["ci_upper"] - e["emr"]]],
                    fmt="none", ecolor="black", elinewidth=0.6, capsize=1.5)
        ax.text(min(e["ci_upper"], 1.0) + 0.03, y, f"{e['emr']:.3f}", va="center", fontsize=6)
    ax.set_yticks(range(len(STACKS)))
    ax.set_yticklabels([s[1] for s in STACKS[::-1]])
    ax.set_xlim(0, 1.18)
    ax.set_xticks([0, 0.5, 1.0])
    ax.set_xlabel("Extraction exact match rate\n(10 runs, 95% CI)")
    ax.spines[["top", "right"]].set_visible(False)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=LOCAL, label="local (Ollama, one device)"),
                       Patch(color=API, label="API-served")],
              loc="lower left", bbox_to_anchor=(-0.45, 1.02), ncol=2, frameon=False,
              fontsize=6, handlelength=1, columnspacing=1.2)

    fig.savefig(OUT.with_suffix(".pdf"))
    fig.savefig(OUT.with_suffix(".png"), dpi=600)


if __name__ == "__main__":
    main()
