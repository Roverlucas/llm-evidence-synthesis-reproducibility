"""Generate pipeline diagram for the article."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(14, 7))
ax.set_xlim(0, 14)
ax.set_ylim(0, 7)
ax.axis('off')

# Colors
c_corpus = '#2E86AB'
c_models = '#A23B72'
c_screen = '#F18F01'
c_extract = '#C73E1D'
c_analysis = '#3B1F2B'
c_bg = '#F5F5F5'
c_arrow = '#555555'
c_repeat = '#E8D5B7'

def add_box(ax, x, y, w, h, color, text, fontsize=9, text_color='white', alpha=0.95):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                          facecolor=color, edgecolor='none', alpha=alpha, zorder=2)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fontsize, color=text_color, fontweight='bold', zorder=3,
            linespacing=1.4)

def add_arrow(ax, x1, y1, x2, y2, color=c_arrow):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=2),
                zorder=4)

# ── Background box for repeated runs ──
repeat_box = FancyBboxPatch((3.8, 0.3), 7.0, 5.4, boxstyle="round,pad=0.15",
                             facecolor=c_repeat, edgecolor='#B8976A', alpha=0.3,
                             linestyle='--', linewidth=2, zorder=1)
ax.add_patch(repeat_box)
ax.text(7.3, 6.2, '× 10 Repeated Runs per Model', ha='center', va='bottom',
        fontsize=11, color='#6B4F2E', fontweight='bold', fontstyle='italic', zorder=3)

# ── Column 1: Corpus ──
add_box(ax, 0.3, 1.8, 2.8, 2.4, c_corpus,
        'PubMed Corpus\n━━━━━━━━━━━━\n500 Abstracts\n100 Include\n100 Exclude\n300 Ambiguous',
        fontsize=9)

# ── Column 2: Models ──
add_box(ax, 4.2, 4.0, 2.4, 1.2, '#2D6A4F',
        'LLaMA 3 8B\n(Local, Ollama)', fontsize=8.5)
add_box(ax, 4.2, 2.4, 2.4, 1.2, '#7B2D8E',
        'Claude Sonnet 4.5\n(Anthropic API)', fontsize=8.5)
add_box(ax, 4.2, 0.8, 2.4, 1.2, '#1A6FC4',
        'Gemini 2.5 Pro\n(Google AI API)', fontsize=8.5)

# ── Column 3: Screening ──
add_box(ax, 7.2, 2.2, 2.0, 1.8, c_screen,
        'Stage A\nScreening\n━━━━━━━━\n500 abstracts\nInclude / Exclude',
        fontsize=8.5)

# ── Column 4: Extraction ──
add_box(ax, 7.2, 4.3, 2.0, 1.3, c_extract,
        'Stage B\nExtraction\n━━━━━━━━\n100 articles → JSON',
        fontsize=8.5, text_color='white')

# ── Column 5: Analysis ──
add_box(ax, 11.2, 1.5, 2.4, 3.2, c_analysis,
        'Analysis\n━━━━━━━━━━━\nExact Match Rate\nBootstrap CIs\n(10,000 resamples)\nField-level EMR\nProvenance Audit',
        fontsize=8.5)

# ── Arrows ──
# Corpus → Models
add_arrow(ax, 3.1, 3.0, 4.2, 4.6)
add_arrow(ax, 3.1, 3.0, 4.2, 3.0)
add_arrow(ax, 3.1, 3.0, 4.2, 1.4)

# Models → Screening
add_arrow(ax, 6.6, 4.6, 7.2, 3.5)
add_arrow(ax, 6.6, 3.0, 7.2, 3.1)
add_arrow(ax, 6.6, 1.4, 7.2, 2.7)

# Screening → Extraction (included articles)
ax.annotate('', xy=(7.8, 4.3), xytext=(7.8, 4.0),
            arrowprops=dict(arrowstyle='->', color=c_arrow, lw=1.5),
            zorder=4)
ax.text(8.5, 4.15, '100\nincluded', ha='center', va='center',
        fontsize=7, color='#666', fontstyle='italic', zorder=3)

# Screening → Analysis
add_arrow(ax, 9.2, 3.1, 11.2, 3.1)

# Extraction → Analysis
add_arrow(ax, 9.2, 4.9, 11.2, 3.8)

# ── Stats annotation ──
ax.text(7.3, 0.55, '60 experiment runs  •  18,000 LLM calls  •  SHA-256 provenance hashing',
        ha='center', va='center', fontsize=9, color='#6B4F2E',
        fontstyle='italic', zorder=3)

plt.tight_layout()
plt.savefig('/Users/lucasrover/llm-evidence-synthesis-reproducibility/analysis/figures/pipeline_diagram.pdf',
            bbox_inches='tight', dpi=300, facecolor='white')
plt.savefig('/Users/lucasrover/llm-evidence-synthesis-reproducibility/analysis/figures/pipeline_diagram.png',
            bbox_inches='tight', dpi=300, facecolor='white')
print("Pipeline diagram saved.")
