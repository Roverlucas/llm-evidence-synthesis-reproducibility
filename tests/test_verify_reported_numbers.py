"""Tests for the manuscript number verifier.

A verifier that silently accepts everything is worse than no verifier, since it
converts an unchecked claim into an apparently checked one. These tests pin the
discrimination: faithful renderings pass, wrong values fail, and the tolerances do
not quietly swallow a changed digit.
"""
from __future__ import annotations

import pathlib

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts/verify_reported_numbers.py"


@pytest.fixture(scope="module")
def fns() -> dict:
    """Load the pure helpers without executing main() or the JSON reads."""
    source = SCRIPT.read_text().split("if __name__")[0]
    namespace = {"__file__": str(SCRIPT)}
    exec(compile(source, str(SCRIPT), "exec"), namespace)  # noqa: S102
    return namespace


@pytest.mark.parametrize("value,form", [
    (0.5287, "0.529"),        # rounds to the stated precision
    (0.5562, "0.556"),
    (0.75, "75.0"),           # proportion stated as a percentage
    (0.75, "75%"),
    (0.660, "66\\%"),         # LaTeX percent escape
    (-3.6497, "-3.65"),       # ASCII hyphen
    (-3.6497, "−3.65"),  # U+2212 typographic minus
    (15.38, "15.4"),
])
def test_accepts_faithful_renderings(fns, value, form):
    assert fns["rendered"](value, [form])


@pytest.mark.parametrize("value,form", [
    (0.5287, "0.629"),   # transposed digits
    (0.5287, "0.628"),
    (0.75, "85.0"),
    (0.359, "0.459"),
    (-3.65, "3.65"),     # sign dropped
    (0.660, "0.560"),
    (15.38, "16.4"),
])
def test_rejects_wrong_values(fns, value, form):
    assert not fns["rendered"](value, [form])


def test_renderings_do_not_span_to_a_different_value(fns):
    """0.359 must not be satisfiable by writing 0.459, at any precision."""
    forms = fns["renderings"](0.359, 3)
    assert "0.359" in forms
    assert not any(f.startswith("0.45") or f.startswith("0.46") for f in forms)


def test_normalise_collapses_only_presentation(fns):
    normalise = fns["normalise"]
    assert normalise("−3.65") == "-3.65"
    assert normalise("75\\%") == "75%"
    assert normalise("$\\kappa{-}$") == "$\\kappa-$"
    # Digits themselves are never rewritten.
    assert "529" in normalise("0.529")


def test_states_requires_the_value_to_be_present(fns, tmp_path):
    doc = tmp_path / "doc.tex"
    doc.write_text("Agreement was 75.0\\% with $\\kappa{=}0.529$.")
    assert fns["states"](doc, ["0.529"], 0.5287)
    assert fns["states"](doc, ["75.0"], 0.75)
    assert not fns["states"](doc, ["0.674"], 0.674)
