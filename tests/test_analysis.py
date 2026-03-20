"""
Tests for core analysis functions used in the LLM Evidence Synthesis
Reproducibility project.

Covers:
  - run_analysis.py: EMR computation, bootstrap CIs, accuracy, field variation
  - analysis/run_semantic_and_meta.py: text normalization, Levenshtein,
    meta-analysis, SE from CI, normal CDF
"""

import math
import sys
from pathlib import Path

import numpy as np
import pytest

# ── Path setup (no package structure) ─────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "analysis"))

from run_analysis import (
    bootstrap_emr,
    compute_extraction_emr,
    compute_extraction_field_variation,
    compute_screening_accuracy,
    compute_screening_emr,
)
from run_semantic_and_meta import (
    inverse_variance_meta,
    levenshtein_ratio,
    normal_cdf,
    normalize_text,
    se_from_ci,
)


# ======================================================================
#  SCREENING EMR
# ======================================================================

class TestComputeScreeningEMR:
    """Tests for compute_screening_emr()."""

    def test_perfect_determinism(self):
        """All runs return the same decision for every abstract → EMR = 1.0."""
        runs = {
            1: [
                {"corpus_id": "A1", "output": {"decision": "include"}},
                {"corpus_id": "A2", "output": {"decision": "exclude"}},
            ],
            2: [
                {"corpus_id": "A1", "output": {"decision": "include"}},
                {"corpus_id": "A2", "output": {"decision": "exclude"}},
            ],
            3: [
                {"corpus_id": "A1", "output": {"decision": "include"}},
                {"corpus_id": "A2", "output": {"decision": "exclude"}},
            ],
        }
        result = compute_screening_emr(runs)
        assert result["emr"] == 1.0
        assert result["flip_rate"] == 0.0
        assert result["n_abstracts"] == 2
        assert result["n_runs"] == 3
        assert result["exact_matches"] == 2
        assert result["mean_agreement"] == 1.0

    def test_complete_non_determinism(self):
        """Every abstract flips at least once → EMR = 0.0."""
        runs = {
            1: [
                {"corpus_id": "A1", "output": {"decision": "include"}},
                {"corpus_id": "A2", "output": {"decision": "exclude"}},
            ],
            2: [
                {"corpus_id": "A1", "output": {"decision": "exclude"}},
                {"corpus_id": "A2", "output": {"decision": "include"}},
            ],
        }
        result = compute_screening_emr(runs)
        assert result["emr"] == 0.0
        assert result["flip_rate"] == 1.0

    def test_partial_match(self):
        """One abstract deterministic, one flips → EMR = 0.5."""
        runs = {
            1: [
                {"corpus_id": "A1", "output": {"decision": "include"}},
                {"corpus_id": "A2", "output": {"decision": "exclude"}},
            ],
            2: [
                {"corpus_id": "A1", "output": {"decision": "include"}},
                {"corpus_id": "A2", "output": {"decision": "include"}},
            ],
        }
        result = compute_screening_emr(runs)
        assert result["emr"] == 0.5
        assert result["flip_rate"] == 0.5
        assert result["exact_matches"] == 1

    def test_error_in_output(self):
        """Outputs with 'error' key are recorded as ERROR decisions."""
        runs = {
            1: [{"corpus_id": "A1", "output": {"error": "timeout"}}],
            2: [{"corpus_id": "A1", "output": {"error": "timeout"}}],
        }
        result = compute_screening_emr(runs)
        # Both runs have ERROR → exact match
        assert result["emr"] == 1.0
        assert result["decisions"]["A1"] == ["ERROR", "ERROR"]

    def test_missing_decision_field(self):
        """Output without 'decision' key uses ERROR fallback."""
        runs = {
            1: [{"corpus_id": "A1", "output": {}}],
            2: [{"corpus_id": "A1", "output": {"decision": "include"}}],
        }
        result = compute_screening_emr(runs)
        # "ERROR" vs "include" → no match
        assert result["emr"] == 0.0

    def test_single_run(self):
        """With only one run, everything is an exact match."""
        runs = {
            1: [
                {"corpus_id": "A1", "output": {"decision": "include"}},
                {"corpus_id": "A2", "output": {"decision": "exclude"}},
            ],
        }
        result = compute_screening_emr(runs)
        assert result["emr"] == 1.0
        assert result["n_runs"] == 1

    def test_abstract_not_in_all_runs_excluded(self):
        """Abstracts not present in ALL runs are excluded from EMR."""
        runs = {
            1: [
                {"corpus_id": "A1", "output": {"decision": "include"}},
                {"corpus_id": "A2", "output": {"decision": "exclude"}},
            ],
            2: [
                {"corpus_id": "A1", "output": {"decision": "include"}},
                # A2 missing from run 2
            ],
        }
        result = compute_screening_emr(runs)
        assert result["n_abstracts"] == 1  # Only A1 valid
        assert result["emr"] == 1.0

    def test_empty_runs(self):
        """Empty runs dict returns zero EMR with n_abstracts=0."""
        result = compute_screening_emr({})
        assert result["emr"] == 0.0
        assert result["n_abstracts"] == 0

    def test_mean_agreement_partial(self):
        """Mean agreement reflects majority-vote proportion."""
        runs = {
            1: [{"corpus_id": "A1", "output": {"decision": "include"}}],
            2: [{"corpus_id": "A1", "output": {"decision": "include"}}],
            3: [{"corpus_id": "A1", "output": {"decision": "exclude"}}],
        }
        result = compute_screening_emr(runs)
        # Most common count = 2/3
        assert abs(result["mean_agreement"] - 2.0 / 3.0) < 1e-9


# ======================================================================
#  EXTRACTION EMR
# ======================================================================

class TestComputeExtractionEMR:
    """Tests for compute_extraction_emr()."""

    def test_perfect_determinism(self):
        runs = {
            1: [{"corpus_id": "P1", "output_hash": "abc123"}],
            2: [{"corpus_id": "P1", "output_hash": "abc123"}],
        }
        result = compute_extraction_emr(runs)
        assert result["emr"] == 1.0
        assert result["n_articles"] == 1
        assert result["exact_matches"] == 1

    def test_complete_non_determinism(self):
        runs = {
            1: [{"corpus_id": "P1", "output_hash": "abc123"}],
            2: [{"corpus_id": "P1", "output_hash": "def456"}],
        }
        result = compute_extraction_emr(runs)
        assert result["emr"] == 0.0

    def test_multiple_articles_mixed(self):
        """Two articles: one matches, one does not → EMR = 0.5."""
        runs = {
            1: [
                {"corpus_id": "P1", "output_hash": "aaa"},
                {"corpus_id": "P2", "output_hash": "bbb"},
            ],
            2: [
                {"corpus_id": "P1", "output_hash": "aaa"},
                {"corpus_id": "P2", "output_hash": "ccc"},
            ],
        }
        result = compute_extraction_emr(runs)
        assert result["emr"] == 0.5
        assert result["n_articles"] == 2

    def test_empty_runs(self):
        result = compute_extraction_emr({})
        assert result["emr"] == 0.0
        assert result["n_articles"] == 0

    def test_missing_hash_treated_as_empty(self):
        """Missing output_hash defaults to empty string."""
        runs = {
            1: [{"corpus_id": "P1"}],
            2: [{"corpus_id": "P1"}],
        }
        result = compute_extraction_emr(runs)
        # Both default to "" → match
        assert result["emr"] == 1.0


# ======================================================================
#  BOOTSTRAP EMR
# ======================================================================

class TestBootstrapEMR:
    """Tests for bootstrap_emr()."""

    def test_perfect_agreement(self):
        """All identical → EMR=1.0, CI=[1.0, 1.0]."""
        data = {
            "A1": ["include", "include", "include"],
            "A2": ["exclude", "exclude", "exclude"],
            "A3": ["include", "include", "include"],
        }
        result = bootstrap_emr(data, n_bootstrap=1000)
        assert result["emr"] == 1.0
        assert result["ci_lower"] == 1.0
        assert result["ci_upper"] == 1.0
        assert result["n_items"] == 3

    def test_zero_agreement(self):
        """All items differ → EMR=0.0, CI=[0.0, 0.0]."""
        data = {
            "A1": ["include", "exclude"],
            "A2": ["exclude", "include"],
            "A3": ["include", "exclude"],
        }
        result = bootstrap_emr(data, n_bootstrap=1000)
        assert result["emr"] == 0.0
        assert result["ci_lower"] == 0.0
        assert result["ci_upper"] == 0.0

    def test_partial_agreement_ci_within_bounds(self):
        """CI must be between 0 and 1 and bracket the point estimate."""
        data = {f"A{i}": ["include", "include"] for i in range(50)}
        data.update({f"B{i}": ["include", "exclude"] for i in range(50)})
        result = bootstrap_emr(data, n_bootstrap=5000)
        assert 0.0 <= result["ci_lower"] <= result["emr"]
        assert result["emr"] <= result["ci_upper"] <= 1.0
        assert result["emr"] == 0.5

    def test_single_item(self):
        """Single item: EMR is 0 or 1, bootstrap still works."""
        data = {"A1": ["include", "include"]}
        result = bootstrap_emr(data, n_bootstrap=500)
        assert result["emr"] == 1.0
        assert result["n_items"] == 1

    def test_n_bootstrap_propagated(self):
        data = {"A1": ["a", "a"]}
        result = bootstrap_emr(data, n_bootstrap=200)
        assert result["n_bootstrap"] == 200


# ======================================================================
#  SCREENING ACCURACY
# ======================================================================

class TestComputeScreeningAccuracy:
    """Tests for compute_screening_accuracy()."""

    def test_perfect_accuracy(self):
        runs = {
            1: [
                {"corpus_id": "A1", "output": {"decision": "include"}},
                {"corpus_id": "A2", "output": {"decision": "exclude"}},
            ],
        }
        gold = {"A1": "include", "A2": "exclude"}
        result = compute_screening_accuracy(runs, gold)
        assert result["mean_accuracy"] == 1.0
        assert result["mean_sensitivity"] == 1.0
        assert result["mean_specificity"] == 1.0

    def test_zero_accuracy(self):
        """All predictions wrong."""
        runs = {
            1: [
                {"corpus_id": "A1", "output": {"decision": "exclude"}},
                {"corpus_id": "A2", "output": {"decision": "include"}},
            ],
        }
        gold = {"A1": "include", "A2": "exclude"}
        result = compute_screening_accuracy(runs, gold)
        assert result["mean_accuracy"] == 0.0
        assert result["mean_sensitivity"] == 0.0
        assert result["mean_specificity"] == 0.0

    def test_multiple_runs_averaged(self):
        """Accuracy is averaged across runs."""
        runs = {
            1: [
                {"corpus_id": "A1", "output": {"decision": "include"}},
                {"corpus_id": "A2", "output": {"decision": "exclude"}},
            ],
            2: [
                {"corpus_id": "A1", "output": {"decision": "exclude"}},
                {"corpus_id": "A2", "output": {"decision": "exclude"}},
            ],
        }
        gold = {"A1": "include", "A2": "exclude"}
        result = compute_screening_accuracy(runs, gold)
        # Run 1: 2/2 correct, Run 2: 1/2 correct → mean = 0.75
        assert result["mean_accuracy"] == 0.75

    def test_gold_missing_corpus_id_skipped(self):
        """Predictions for IDs not in gold are ignored."""
        runs = {
            1: [
                {"corpus_id": "A1", "output": {"decision": "include"}},
                {"corpus_id": "UNKNOWN", "output": {"decision": "include"}},
            ],
        }
        gold = {"A1": "include"}
        result = compute_screening_accuracy(runs, gold)
        assert result["per_run"][1]["tp"] == 1
        assert result["per_run"][1]["fp"] == 0

    def test_empty_runs(self):
        """No runs → empty per_run dict; np.mean([]) returns NaN."""
        result = compute_screening_accuracy({}, {"A1": "include"})
        assert result["per_run"] == {}
        # np.mean of empty list yields NaN
        assert math.isnan(result["mean_accuracy"])


# ======================================================================
#  EXTRACTION FIELD VARIATION
# ======================================================================

class TestComputeExtractionFieldVariation:
    """Tests for compute_extraction_field_variation()."""

    def test_perfect_field_determinism(self):
        """All fields identical across runs → all field EMRs = 1.0."""
        item = {
            "corpus_id": "P1",
            "output": {
                "study_design": "cohort",
                "study_location": "Brazil",
                "study_period": "2020-2021",
                "population": "adults",
                "sample_size": "500",
                "estimates": [{"effect_measure": "RR", "effect_estimate": 1.2}],
            },
        }
        runs = {1: [item], 2: [item], 3: [item]}
        result = compute_extraction_field_variation(runs)
        for field, emr_val in result["field_emr"].items():
            assert emr_val == 1.0, f"Field {field} EMR should be 1.0"
        assert result["estimate_count_stability"] == 1.0

    def test_complete_field_variation(self):
        """Every field differs across runs → all field EMRs = 0.0."""
        runs = {
            1: [{"corpus_id": "P1", "output": {
                "study_design": "cohort", "study_location": "Brazil",
                "study_period": "2020", "population": "children",
                "sample_size": "100", "estimates": [],
            }}],
            2: [{"corpus_id": "P1", "output": {
                "study_design": "case-control", "study_location": "USA",
                "study_period": "2021", "population": "adults",
                "sample_size": "200", "estimates": [],
            }}],
        }
        result = compute_extraction_field_variation(runs)
        for field, emr_val in result["field_emr"].items():
            assert emr_val == 0.0, f"Field {field} should be 0.0"

    def test_estimate_count_varies(self):
        """Different number of estimates across runs flagged."""
        runs = {
            1: [{"corpus_id": "P1", "output": {
                "study_design": "cohort", "study_location": "Brazil",
                "study_period": "2020", "population": "adults",
                "sample_size": "100",
                "estimates": [{"effect_measure": "RR"}],
            }}],
            2: [{"corpus_id": "P1", "output": {
                "study_design": "cohort", "study_location": "Brazil",
                "study_period": "2020", "population": "adults",
                "sample_size": "100",
                "estimates": [{"effect_measure": "RR"}, {"effect_measure": "OR"}],
            }}],
        }
        result = compute_extraction_field_variation(runs)
        assert result["n_estimates_count_varies"] == 1
        assert result["estimate_count_stability"] == 0.0

    def test_error_outputs_skipped(self):
        """Outputs with 'error' key are skipped in field analysis."""
        runs = {
            1: [{"corpus_id": "P1", "output": {"error": "timeout"}}],
            2: [{"corpus_id": "P1", "output": {"error": "timeout"}}],
        }
        result = compute_extraction_field_variation(runs)
        # No valid outputs → all EMRs are 0.0 (0/0 guarded)
        for field, emr_val in result["field_emr"].items():
            assert emr_val == 0.0


# ======================================================================
#  NORMALIZE TEXT
# ======================================================================

class TestNormalizeText:
    """Tests for normalize_text()."""

    def test_lowercase_and_strip(self):
        assert normalize_text("  Hello World  ") == "hello world"

    def test_trailing_punctuation_removed(self):
        assert normalize_text("New York.") == "new york"
        assert normalize_text("London;") == "london"
        assert normalize_text("Tokyo,") == "tokyo"

    def test_whitespace_normalized(self):
        assert normalize_text("São   Paulo\t  Brazil") == "são paulo brazil"

    def test_usa_abbreviations(self):
        # normalize_text strips trailing punctuation BEFORE doing replacements,
        # so "U.S.A." → "u.s.a" and "U.S." → "u.s" — the .replace() patterns
        # that include trailing dots ("u.s.a.", "u.s.") won't match.
        # Only bare "usa" (no dots) triggers the replacement chain.
        assert normalize_text("USA") == "united states"
        assert normalize_text("usa") == "united states"
        # These are quirks of the rstrip-before-replace ordering:
        assert normalize_text("U.S.") == "u.s"
        assert normalize_text("U.S.A.") == "united statesa"  # "u.s." matches inside "u.s.a"

    def test_uk_abbreviation(self):
        # "U.K." → lower → "u.k." → rstrip(".") → "u.k" — .replace("u.k.", ...) misses
        assert normalize_text("U.K.") == "u.k"  # actual behavior (no match)
        assert normalize_text("UK") == "united kingdom"

    def test_the_prefix_removed(self):
        assert normalize_text("The Netherlands") == "netherlands"

    def test_none_returns_empty(self):
        assert normalize_text(None) == ""

    def test_numeric_input(self):
        assert normalize_text(42) == "42"

    def test_already_normalized(self):
        assert normalize_text("cohort study") == "cohort study"


# ======================================================================
#  LEVENSHTEIN RATIO
# ======================================================================

class TestLevenshteinRatio:
    """Tests for levenshtein_ratio()."""

    def test_identical_strings(self):
        assert levenshtein_ratio("hello", "hello") == 1.0

    def test_completely_different(self):
        assert levenshtein_ratio("abc", "xyz") == 0.0

    def test_empty_strings(self):
        assert levenshtein_ratio("", "") == 1.0

    def test_one_empty(self):
        assert levenshtein_ratio("hello", "") == 0.0
        assert levenshtein_ratio("", "hello") == 0.0

    def test_single_char_difference(self):
        # "cat" vs "bat" → distance 1, max_len 3 → ratio = 1 - 1/3 = 0.667
        ratio = levenshtein_ratio("cat", "bat")
        assert abs(ratio - 2.0 / 3.0) < 1e-9

    def test_symmetry(self):
        r1 = levenshtein_ratio("kitten", "sitting")
        r2 = levenshtein_ratio("sitting", "kitten")
        assert abs(r1 - r2) < 1e-9

    def test_substring(self):
        # "abc" vs "abcd" → distance 1, max_len 4 → ratio = 0.75
        assert levenshtein_ratio("abc", "abcd") == 0.75

    def test_high_similarity(self):
        ratio = levenshtein_ratio("retrospective cohort", "retrospective cohoort")
        assert ratio >= 0.90


# ======================================================================
#  INVERSE VARIANCE META-ANALYSIS
# ======================================================================

class TestInverseVarianceMeta:
    """Tests for inverse_variance_meta()."""

    def test_single_study(self):
        """Single study: pooled effect = that study."""
        log_rr = math.log(1.5)
        se = 0.2
        pooled_eff, pooled_se, z, p = inverse_variance_meta([(log_rr, se)])
        assert abs(pooled_eff - 1.5) < 1e-6
        assert abs(pooled_se - se) < 1e-6
        assert z is not None
        assert p is not None

    def test_two_identical_studies(self):
        """Two identical studies: pooled SE decreases by sqrt(2)."""
        log_rr = math.log(2.0)
        se = 0.3
        pooled_eff, pooled_se, z, p = inverse_variance_meta([
            (log_rr, se), (log_rr, se)
        ])
        assert abs(pooled_eff - 2.0) < 1e-6
        # SE_pooled = 1/sqrt(2*w) = se/sqrt(2)
        expected_se = se / math.sqrt(2)
        assert abs(pooled_se - expected_se) < 1e-6

    def test_null_effect_not_significant(self):
        """RR=1.0 (log=0) should yield high p-value (not significant)."""
        estimates = [(0.0, 0.5), (0.0, 0.3), (0.0, 0.4)]
        pooled_eff, pooled_se, z, p = inverse_variance_meta(estimates)
        assert abs(pooled_eff - 1.0) < 1e-6
        assert p > 0.9  # Far from significant

    def test_empty_input(self):
        result = inverse_variance_meta([])
        assert result == (None, None, None, None)

    def test_zero_se_skipped(self):
        """Studies with SE <= 0 are skipped."""
        estimates = [(math.log(1.5), 0.0), (math.log(1.5), -0.1)]
        result = inverse_variance_meta(estimates)
        assert result == (None, None, None, None)

    def test_significant_effect(self):
        """Large log-RR with small SE → significant p-value."""
        log_rr = math.log(3.0)  # ~1.099
        se = 0.1
        pooled_eff, pooled_se, z, p = inverse_variance_meta([(log_rr, se)])
        assert p < 0.001


# ======================================================================
#  SE FROM CI
# ======================================================================

class TestSeFromCI:
    """Tests for se_from_ci()."""

    def test_known_95ci(self):
        """SE from 95% CI: SE = (log_upper - log_lower) / (2 * 1.96)."""
        log_lo = math.log(0.8)
        log_hi = math.log(1.5)
        se = se_from_ci(log_lo, log_hi, ci_level=95)
        expected = (log_hi - log_lo) / (2 * 1.96)
        assert abs(se - expected) < 1e-10

    def test_99ci(self):
        log_lo = math.log(0.5)
        log_hi = math.log(2.0)
        se = se_from_ci(log_lo, log_hi, ci_level=99)
        expected = (log_hi - log_lo) / (2 * 2.576)
        assert abs(se - expected) < 1e-10

    def test_symmetric_ci_around_null(self):
        """CI symmetric on log scale around 0 (RR=1)."""
        delta = 0.5
        se = se_from_ci(-delta, delta)
        expected = (2 * delta) / (2 * 1.96)
        assert abs(se - expected) < 1e-10

    def test_narrow_ci_small_se(self):
        """Very narrow CI → very small SE."""
        se = se_from_ci(0.0, 0.01)
        assert se < 0.01

    def test_unknown_ci_defaults_to_95(self):
        """Unrecognized CI level falls back to z=1.96."""
        se_default = se_from_ci(0.0, 1.0, ci_level=90)
        se_95 = se_from_ci(0.0, 1.0, ci_level=95)
        assert abs(se_default - se_95) < 1e-10


# ======================================================================
#  NORMAL CDF
# ======================================================================

class TestNormalCDF:
    """Tests for normal_cdf()."""

    def test_cdf_at_zero(self):
        assert abs(normal_cdf(0) - 0.5) < 1e-10

    def test_cdf_at_large_positive(self):
        assert abs(normal_cdf(10) - 1.0) < 1e-6

    def test_cdf_at_large_negative(self):
        assert abs(normal_cdf(-10) - 0.0) < 1e-6

    def test_cdf_symmetry(self):
        """CDF(x) + CDF(-x) = 1."""
        for x in [0.5, 1.0, 1.96, 2.576, 3.0]:
            assert abs(normal_cdf(x) + normal_cdf(-x) - 1.0) < 1e-10

    def test_cdf_at_196(self):
        """CDF(1.96) ≈ 0.975."""
        assert abs(normal_cdf(1.96) - 0.975) < 0.001

    def test_cdf_at_1(self):
        """CDF(1) ≈ 0.8413."""
        assert abs(normal_cdf(1.0) - 0.8413) < 0.001

    def test_monotonically_increasing(self):
        vals = [normal_cdf(x) for x in [-3, -2, -1, 0, 1, 2, 3]]
        for i in range(len(vals) - 1):
            assert vals[i] < vals[i + 1]
