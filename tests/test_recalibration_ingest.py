"""Tests for the v1.2 recalibration ingestor.

The decision table in protocol v1.2 §4 is the part worth testing: the round-1
kappa of 0.529 was traced to a table that did not cover single-criterion failure,
so a table encoded in code and never exercised would repeat the original defect
in a new place.
"""

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

_SPEC = importlib.util.spec_from_file_location(
    "ingest_recalibration_xlsx",
    Path(__file__).resolve().parents[1] / "scripts" / "dual_labeling" / "ingest_recalibration_xlsx.py",
)
ingest = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ingest)


class TestDecisionTable:
    """Every row of protocol v1.2 §4, applied literally."""

    def test_no_failure_includes(self):
        assert ingest.decision_from_table([]) == "INCLUDE"

    @pytest.mark.parametrize("criterion", ["1", "2", "3", "6"])
    def test_single_structural_failure_excludes(self, criterion):
        assert ingest.decision_from_table([criterion]) == "EXCLUDE"

    def test_criterion_4_alone_is_uncertain(self):
        assert ingest.decision_from_table(["4"]) == "UNCERTAIN"

    def test_5b_alone_is_uncertain(self):
        """Abstract says an effect was estimated but omits the values."""
        assert ingest.decision_from_table(["5b"]) == "UNCERTAIN"

    def test_5c_alone_excludes(self):
        """No estimate and no mention of one — absence is itself evidence."""
        assert ingest.decision_from_table(["5c"]) == "EXCLUDE"

    def test_5b_and_5c_diverge(self):
        """The v1.2 fix: same criterion, opposite decisions."""
        assert ingest.decision_from_table(["5b"]) != ingest.decision_from_table(["5c"])

    @pytest.mark.parametrize("failed", [["4", "5b"], ["2", "5c"], ["2", "3", "5c"], ["1", "4"]])
    def test_two_or_more_failures_exclude(self, failed):
        assert ingest.decision_from_table(failed) == "EXCLUDE"

    def test_structural_beats_conditional(self):
        """Precedence EXCLUDE > UNCERTAIN: criterion 2 plus case 5b is EXCLUDE."""
        assert ingest.decision_from_table(["2", "5b"]) == "EXCLUDE"


class TestNormaliseCriteria:
    def test_semicolon_separator_canonicalised(self):
        assert ingest.normalise_criteria("2; 5c") == "2,5c"

    def test_excel_float_artefact_stripped(self):
        """Excel stores a lone 4 as 4.0; that is a spreadsheet artefact."""
        assert ingest.normalise_criteria("4.0") == "4"
        assert ingest.normalise_criteria(4.0) == "4"

    def test_float_artefact_inside_a_list(self):
        assert ingest.normalise_criteria("4.0; 5b") == "4,5b"

    def test_blank_passes_through(self):
        assert pd.isna(ingest.normalise_criteria(float("nan")))


def _frame(decision, criteria, prefix="labeler1"):
    return pd.DataFrame([{
        "labeling_id": "LBL-001",
        "title": "t", "abstract": "a",
        f"{prefix}_decision_v12": decision,
        f"{prefix}_confidence_v12": "HIGH",
        f"{prefix}_rationale_v12": "a rationale long enough",
        f"{prefix}_criteria_failed_v12": criteria,
    }])


def _template():
    return pd.DataFrame([{"labeling_id": "LBL-001", "title": "t", "abstract": "a"}])


class TestValidate:
    def test_consistent_row_passes(self):
        assert ingest.validate(_frame("UNCERTAIN", "5b"), _template(), "labeler1") == []

    def test_decision_contradicting_the_table_fails(self):
        errors = ingest.validate(_frame("INCLUDE", "5c"), _template(), "labeler1")
        assert any("contradicts protocol v1.2 §4" in e for e in errors)

    def test_bare_5_is_rejected_not_guessed(self):
        """The ambiguity that produced kappa = 0.529 must not be resolved silently."""
        errors = ingest.validate(_frame("EXCLUDE", "5"), _template(), "labeler1")
        assert any("5b or 5c" in e for e in errors)

    def test_5a_is_not_a_failure(self):
        errors = ingest.validate(_frame("EXCLUDE", "5a"), _template(), "labeler1")
        assert any("criterion met" in e for e in errors)

    def test_edited_abstract_is_caught(self):
        df = _frame("UNCERTAIN", "5b")
        df.loc[0, "abstract"] = "edited"
        errors = ingest.validate(df, _template(), "labeler1")
        assert any("abstract was edited" in e for e in errors)

    def test_other_labeler_columns_break_blinding(self):
        df = _frame("UNCERTAIN", "5b")
        df["labeler2_decision_v12"] = "INCLUDE"
        errors = ingest.validate(df, _template(), "labeler1")
        assert any("blinding broken" in e for e in errors)

    def test_vocabulary_outside_protocol_fails(self):
        errors = ingest.validate(_frame("MAYBE", "5b"), _template(), "labeler1")
        assert any("outside protocol vocabulary" in e for e in errors)
