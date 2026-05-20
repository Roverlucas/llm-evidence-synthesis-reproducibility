"""Generate a friendly flowchart PNG for the dual-labeling quick-start guide.

Saves to: data/dual_labeling/protocols/flowchart.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parents[2] / "data" / "dual_labeling" / "protocols" / "flowchart.png"

# Palette
COLOR_START = "#4A90E2"     # blue
COLOR_QUESTION = "#F5A623"  # orange
COLOR_INCLUDE = "#7ED321"   # green
COLOR_EXCLUDE = "#D0021B"   # red
COLOR_UNCERTAIN = "#F8E71C" # yellow
COLOR_END = "#9013FE"       # purple
COLOR_TEXT = "#1A1A1A"

WIDTH, HEIGHT = 14, 18

fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT), dpi=150)
ax.set_xlim(0, 14)
ax.set_ylim(0, 18)
ax.axis("off")


def box(x, y, w, h, text, color, text_color="white", fontsize=11, weight="bold"):
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.08,rounding_size=0.25",
        linewidth=1.5,
        edgecolor="#333",
        facecolor=color,
    )
    ax.add_patch(patch)
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=text_color,
        weight=weight,
        wrap=True,
    )


def diamond(x, y, w, h, text, fontsize=10):
    pts = [(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)]
    poly = plt.Polygon(pts, facecolor=COLOR_QUESTION, edgecolor="#333", linewidth=1.5)
    ax.add_patch(poly)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, color="white", weight="bold", wrap=True)


def arrow(x1, y1, x2, y2, label=None, label_offset=(0.2, 0)):
    ar = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="-|>",
        mutation_scale=18,
        linewidth=1.6,
        color="#333",
    )
    ax.add_patch(ar)
    if label:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, fontsize=10, color="#333", weight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#999"))


# ---------- TITLE ----------
ax.text(7, 17.4, "Como decidir cada abstract — Fluxograma de Labeling",
        ha="center", fontsize=16, weight="bold", color=COLOR_TEXT)
ax.text(7, 16.95, "PM2.5 × Hospitalização Respiratória — Dual-Labeling Protocol",
        ha="center", fontsize=11, color="#555", style="italic")

# ---------- START ----------
box(7, 16, 4.5, 0.7, "Abrir CSV no Google Sheets / Rayyan", COLOR_START, fontsize=12)
arrow(7, 15.65, 7, 15.05)

box(7, 14.7, 4.5, 0.7, "Ler título + abstract (1 linha)", COLOR_START, fontsize=12)
arrow(7, 14.35, 7, 13.75)

# ---------- 6 QUESTIONS (in chain) ----------
# Q1
diamond(7, 13.2, 5.5, 1.0, "1) É estudo original?\n(não é review/meta/editorial)", fontsize=10)
arrow(7, 12.7, 7, 12.15, "SIM", label_offset=(0.35, 0))
arrow(9.75, 13.2, 12, 13.2, "NÃO", label_offset=(0, 0.3))
box(12.7, 13.2, 1.6, 0.55, "EXCLUDE\ncrit. 1", COLOR_EXCLUDE, fontsize=9)

# Q2
diamond(7, 11.6, 5.5, 1.0, "2) Mede PM2.5?\n(não só PM10)", fontsize=10)
arrow(7, 11.1, 7, 10.55, "SIM", label_offset=(0.35, 0))
arrow(9.75, 11.6, 12, 11.6, "NÃO", label_offset=(0, 0.3))
box(12.7, 11.6, 1.6, 0.55, "EXCLUDE\ncrit. 2", COLOR_EXCLUDE, fontsize=9)

# Q3
diamond(7, 10.0, 5.5, 1.0, "3) Outcome respiratório?\n(hospital/ED, não mortalidade)", fontsize=10)
arrow(7, 9.5, 7, 8.95, "SIM", label_offset=(0.35, 0))
arrow(9.75, 10.0, 12, 10.0, "NÃO", label_offset=(0, 0.3))
box(12.7, 10.0, 1.6, 0.55, "EXCLUDE\ncrit. 3", COLOR_EXCLUDE, fontsize=9)

# Q4
diamond(7, 8.4, 5.5, 1.0, "4) Design: time-series\nou case-crossover?", fontsize=10)
arrow(7, 7.9, 7, 7.35, "SIM", label_offset=(0.35, 0))
arrow(9.75, 8.4, 12, 8.4, "BORDERLINE\n(cohort etc.)", label_offset=(0, 0.4))
box(12.7, 8.4, 1.7, 0.6, "UNCERTAIN\ncrit. 4", COLOR_UNCERTAIN, text_color="#333", fontsize=9)

# Q5
diamond(7, 6.8, 5.5, 1.0, "5) Tem efeito quantitativo\n(RR/OR/HR) + IC 95%?", fontsize=10)
arrow(7, 6.3, 7, 5.75, "SIM", label_offset=(0.35, 0))
arrow(9.75, 6.8, 12, 6.8, "NÃO", label_offset=(0, 0.3))
box(12.7, 6.8, 1.6, 0.55, "EXCLUDE\ncrit. 5", COLOR_EXCLUDE, fontsize=9)

# Q6
diamond(7, 5.2, 5.5, 1.0, "6) Está em inglês?", fontsize=10)
arrow(7, 4.7, 7, 4.15, "SIM", label_offset=(0.35, 0))
arrow(9.75, 5.2, 12, 5.2, "NÃO", label_offset=(0, 0.3))
box(12.7, 5.2, 1.6, 0.55, "EXCLUDE\ncrit. 6", COLOR_EXCLUDE, fontsize=9)

# ---------- DECISION ----------
box(7, 3.65, 4.5, 0.7, "INCLUDE  (passou nos 6 critérios)", COLOR_INCLUDE, fontsize=13)
arrow(7, 3.3, 7, 2.75)

# ---------- WRITE 4 COLUMNS ----------
box(7, 2.35, 9, 0.9,
    "Preencher 4 colunas no CSV:\n"
    "labeler2_decision  •  labeler2_confidence  •  labeler2_rationale  •  labeler2_criteria_failed",
    COLOR_END, fontsize=10)
arrow(7, 1.85, 7, 1.3)

box(7, 0.95, 4.5, 0.6, "→ Próximo abstract", COLOR_START, fontsize=11)

# ---------- LEGEND BOX (top-left) ----------
ax.text(0.4, 17.4, "Legenda", fontsize=11, weight="bold", color=COLOR_TEXT)
box(1.5, 16.85, 2.5, 0.4, "Ação / Etapa", COLOR_START, fontsize=9)
diamond(1.5, 16.3, 2.5, 0.55, "Pergunta", fontsize=9)
box(1.5, 15.7, 2.5, 0.4, "INCLUDE", COLOR_INCLUDE, fontsize=9)
box(1.5, 15.2, 2.5, 0.4, "EXCLUDE", COLOR_EXCLUDE, fontsize=9)
box(1.5, 14.7, 2.5, 0.4, "UNCERTAIN", COLOR_UNCERTAIN, text_color="#333", fontsize=9)

# ---------- CONFIDENCE LEGEND (bottom-left) ----------
ax.text(0.4, 4.5, "Escala de confiança", fontsize=11, weight="bold", color=COLOR_TEXT)
ax.text(0.5, 4.0, "HIGH (0.8-1.0): match/mismatch claro", fontsize=9, color="#333")
ax.text(0.5, 3.65, "MEDIUM (0.5-0.79): provável c/ ambiguidade", fontsize=9, color="#333")
ax.text(0.5, 3.3, "LOW (0.0-0.49): genuinamente incerto", fontsize=9, color="#333")

# ---------- RULES BOX ----------
ax.text(0.4, 2.5, "Regra de ouro", fontsize=11, weight="bold", color=COLOR_TEXT)
ax.text(0.5, 2.1,
        "• Atende aos 6 → INCLUDE\n"
        "• Falha clara em ≥1 → EXCLUDE\n"
        "• Borderline em 1 → UNCERTAIN\n"
        "• Se ler 3× sem decidir → UNCERTAIN",
        fontsize=9, color="#333", verticalalignment="top")

# ---------- FOOTER ----------
ax.text(7, 0.25,
        "Lucas Rover — PPGSAU/UTFPR  •  lucasrover@alunos.utfpr.edu.br  •  Protocolo v1.1 (2026-04-25)  •  Quick-start v1.0 (2026-05-19)",
        ha="center", fontsize=8, color="#666", style="italic")

plt.tight_layout()
plt.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
print(f"Saved: {OUT}")
print(f"Size: {OUT.stat().st_size / 1024:.1f} KB")
