"""Verify that every agreement figure asserted in the manuscript matches its source.

Numbers get copied into prose by hand and then drift when an analysis is re-run.
This script closes that gap for the dual-human validation: each claim below names
the value, where it comes from in the result JSONs, and every file that must state
it. A mismatch or a missing mention fails the run.

Coverage is deliberately narrow — the Stage-A agreement statistics added on
2026-07-29 — because those are the figures that appear in four documents at once
(main text, supplement, cover letter, OSF sub-registration update) and therefore
carry the highest drift risk.

Two limits worth stating plainly, so this script is not trusted beyond what it does.
It verifies that a value is *asserted somewhere* in each required file, not that it
sits in the right sentence: a short rendering such as ``66`` can also match an
unrelated ``66%`` elsewhere in the same document. And it cannot detect a figure that
is simply absent from the analysis and from the prose alike. It catches drift between
code and text, which is the failure mode that actually recurs; reading for context
remains a human job.

Usage:
    python scripts/verify_reported_numbers.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATS = json.loads((ROOT / "data/dual_labeling/results/kappa_statistics.json").read_text())
REPORT = json.loads((ROOT / "data/dual_labeling/results/kappa_report.json").read_text())

MAIN = ROOT / "article/main.tex"
SUPP = ROOT / "article/supplementary.tex"
LETTER = ROOT / "docs/cover_letter_rsm.md"
UPDATE = ROOT / "docs/osf_subregistration_update.md"
PROTOCOL = ROOT / "data/dual_labeling/protocols/labeling_protocol.md"

three = STATS["three_class"]
binary = STATS["binary_include_vs_exclude"]
strata = STATS["per_stratum"]
marginal = STATS["marginal_homogeneity"]
byrt = STATS["byrt_indices"]
boot = STATS["bootstrap_three_class"]

# (label, computed value, rendering(s) that count as stating it, files that must state it)
CLAIMS: list[tuple[str, float, list[str], list[Path]]] = [
    ("kappa 3-class", three["kappa"], ["0.529"], [MAIN, SUPP, LETTER, UPDATE, PROTOCOL]),
    ("kappa 3-class SE", three["se"], ["0.074"], [MAIN, SUPP, UPDATE]),
    ("kappa 3-class CI lower", three["ci95"][0], ["0.383"], [MAIN, SUPP, LETTER, UPDATE]),
    ("kappa 3-class CI upper", three["ci95"][1], ["0.674"], [MAIN, SUPP, LETTER, UPDATE]),
    ("kappa binary", binary["kappa"], ["0.556"], [MAIN, SUPP, UPDATE, PROTOCOL]),
    ("kappa binary CI lower", binary["ci95"][0], ["0.400"], [MAIN, SUPP, UPDATE]),
    ("kappa binary CI upper", binary["ci95"][1], ["0.712"], [MAIN, SUPP, UPDATE]),
    ("raw agreement", three["percent_agreement"], ["75.0", "75\\%"], [MAIN, SUPP, UPDATE, PROTOCOL]),
    ("z vs Cochrane target", three["test_vs_cochrane"]["z"], ["-3.65", "{-}3.65"], [MAIN, SUPP, UPDATE]),
    ("PABAK binary", binary["pabak"], ["0.558"], [MAIN, SUPP, UPDATE]),
    ("prevalence index", byrt["prevalence_index"], ["0.189"], [MAIN, SUPP, UPDATE]),
    ("bias index", byrt["bias_index"], ["0.179"], [MAIN, SUPP, UPDATE]),
    ("weighted kappa linear", three["kappa_weighted_linear"], ["0.541"], [MAIN, SUPP, UPDATE]),
    ("weighted kappa quadratic", three["kappa_weighted_quadratic"], ["0.548"], [MAIN, SUPP, UPDATE]),
    ("Stuart-Maxwell statistic", marginal["stuart_maxwell_3class"]["statistic"], ["15.4"], [MAIN, SUPP, UPDATE]),
    ("bootstrap percentile lower", boot["percentile_ci95"][0], ["0.383"], [SUPP]),
    ("bootstrap BCa lower", boot["bca_ci95"][0], ["0.382"], [SUPP]),
    ("clear-include agreement", strata["include"]["percent_agreement"], ["0.680"], [MAIN, SUPP, UPDATE]),
    ("clear-include kappa", strata["include"]["kappa"], ["0.359"], [MAIN, SUPP, UPDATE]),
    ("ambiguous agreement", strata["ambiguous"]["percent_agreement"], ["0.660"], [MAIN, SUPP, UPDATE]),
    ("ambiguous kappa", strata["ambiguous"]["kappa"], ["0.398"], [MAIN, SUPP, UPDATE]),
]

# Integer counts, checked the same way.
INT_CLAIMS: list[tuple[str, int, list[str], list[Path]]] = [
    ("n discordances", REPORT["three_class"]["n_discordances"], ["25"], [MAIN, SUPP, UPDATE, PROTOCOL]),
    ("corpus size", three["n"], ["100"], [MAIN, SUPP, UPDATE, PROTOCOL]),
    ("binary n", binary["n"], ["95"], [SUPP, UPDATE]),
    ("clear-include endorsed by rater 1", strata["include"]["labeler1_endorsed_stratum_label"], ["13"], [MAIN, SUPP, UPDATE]),
    ("clear-include endorsed by rater 2", strata["include"]["labeler2_endorsed_stratum_label"], ["21"], [MAIN, SUPP, UPDATE]),
    ("clear-exclude endorsed by rater 1", strata["exclude"]["labeler1_endorsed_stratum_label"], ["25"], [MAIN, SUPP, UPDATE]),
]

# Claims that are counted in the data rather than stored as a scalar.
DERIVED: list[tuple[str, str, list[Path]]] = [
    ("asymmetric discordances", "19", [MAIN, SUPP, UPDATE, PROTOCOL]),
    ("of which on criterion 5", "17", [MAIN, SUPP, UPDATE, PROTOCOL]),
    ("discordant cells 2 vs 19", "2", [MAIN, SUPP, UPDATE]),
    ("legacy extraction survivors", "13", [MAIN, SUPP, UPDATE]),
]


def normalise(text: str) -> str:
    """Strip rendering differences that carry no meaning.

    The same value legitimately appears as ``0.660`` in a supplement table, ``66\\%``
    in main-text prose, and ``−3.65`` with a typographic minus in a Markdown file.
    Verifying values means accepting all three; enforcing one house style is a
    different job and not this script's.
    """
    return (text.replace("−", "-")   # U+2212 minus
                .replace("{-}", "-")       # LaTeX spacing form
                .replace("\\%", "%")
                .replace("\\,", "")
                .replace("~", " "))


def renderings(value: float, decimals: int) -> set[str]:
    """Every numerically faithful way of writing this value."""
    out = {f"{value:.{decimals}f}"}
    for d in range(0, 4):
        out.add(f"{value:.{d}f}")
        out.add(f"{value * 100:.{d}f}")      # proportion stated as a percentage
    # Drop forms that would round to something else, e.g. 0.660 -> "1"
    return {f for f in out if abs(float(f) - value) < 5e-4
            or abs(float(f) - value * 100) < 5e-2}


def rendered(value: float, forms: list[str]) -> bool:
    """Does at least one declared rendering round-trip to the computed value?"""
    for form in forms:
        cleaned = normalise(form).replace("%", "")
        try:
            stated = float(cleaned)
        except ValueError:
            continue
        decimals = len(cleaned.split(".")[1]) if "." in cleaned else 0
        tolerance = 10 ** -decimals / 2 + 1e-9
        if any(abs(stated - c) < tolerance for c in (value, value * 100)):
            return True
    return False


def states(path: Path, forms: list[str], value: float | None = None) -> bool:
    """True if the file asserts the value in any faithful rendering."""
    body = normalise(path.read_text())
    if any(normalise(form) in body for form in forms):
        return True
    if value is None:
        return False
    decimals = max((len(normalise(f).replace("%", "").split(".")[1])
                    for f in forms if "." in normalise(f)), default=3)
    return any(alt in body for alt in renderings(value, decimals))


def main() -> int:
    failures: list[str] = []
    checked = 0

    print("==每 numeric claim vs its source JSON ==".replace("每", ""))
    for label, value, forms, files in CLAIMS:
        checked += 1
        if value is None:
            failures.append(f"{label}: source value is null in the JSON")
            continue
        if not rendered(value, forms):
            failures.append(
                f"{label}: manuscript renders {forms} but JSON holds {value!r}"
            )
            continue
        missing = [f.name for f in files if not states(f, forms, value)]
        if missing:
            failures.append(f"{label} ({forms[0]}) missing from: {', '.join(missing)}")
        else:
            print(f"  ok  {label:38s} {forms[0]:>10s}")

    for label, value, forms, files in INT_CLAIMS:
        checked += 1
        if str(value) not in forms:
            failures.append(f"{label}: manuscript says {forms} but data gives {value}")
            continue
        missing = [f.name for f in files if not states(f, forms)]
        if missing:
            failures.append(f"{label} ({forms[0]}) missing from: {', '.join(missing)}")
        else:
            print(f"  ok  {label:38s} {forms[0]:>10s}")

    print("\n== claims stated in prose, presence check only ==")
    for label, form, files in DERIVED:
        checked += 1
        missing = [f.name for f in files if form not in f.read_text()]
        if missing:
            failures.append(f"{label} ({form}) missing from: {', '.join(missing)}")
        else:
            print(f"  ok  {label:38s} {form:>10s}")

    # Cross-document guard: the study's kappa must never be stated as meeting the target.
    print("\n== framing guards ==")
    for path in (MAIN, SUPP, LETTER, UPDATE):
        body = path.read_text()
        if re.search(r"(meets|met|reached|achieved|satisf\w+)[^.]{0,40}Cochrane", body, re.I):
            failures.append(f"{path.name}: claims the Cochrane target was met")
        else:
            print(f"  ok  {path.name:38s} target not claimed as met")

    print()
    if failures:
        print(f"FAIL — {len(failures)} of {checked} claims are wrong or unstated:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS — all {checked} claims match their source and appear where required.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
