"""Tests for the screening/extraction pipeline and model runners."""

import json
import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.provenance.hasher import (
    compute_call_hash,
    compute_output_hash,
    create_call_record,
    create_run_card,
)
from src.screening.runner import _extract_json, run_screening
from src.extraction.runner import run_extraction


# ── Provenance Tests ────────────────────────────────────────

class TestProvenance:
    """Test provenance hashing and run cards."""

    def test_call_hash_deterministic(self):
        h1 = compute_call_hash("prompt", "input", "model", 0.0, 42)
        h2 = compute_call_hash("prompt", "input", "model", 0.0, 42)
        assert h1 == h2

    def test_call_hash_different_inputs(self):
        h1 = compute_call_hash("prompt", "input_a", "model", 0.0, 42)
        h2 = compute_call_hash("prompt", "input_b", "model", 0.0, 42)
        assert h1 != h2

    def test_call_hash_different_seeds(self):
        h1 = compute_call_hash("prompt", "input", "model", 0.0, 42)
        h2 = compute_call_hash("prompt", "input", "model", 0.0, 99)
        assert h1 != h2

    def test_output_hash_deterministic(self):
        h1 = compute_output_hash("test output")
        h2 = compute_output_hash("test output")
        assert h1 == h2

    def test_output_hash_sha256(self):
        text = "test output"
        expected = hashlib.sha256(text.encode()).hexdigest()
        assert compute_output_hash(text) == expected

    def test_create_call_record(self):
        record = create_call_record(
            corpus_id="ABS-0001",
            call_hash="abc123",
            output_hash="def456",
            model_id="test-model",
            provider="test",
            stage="screening",
            run_id=1,
            inference_result={
                "inference_duration_ms": 150.0,
                "input_tokens": 100,
                "output_tokens": 50,
                "stop_reason": "end_turn",
            },
        )
        assert record["corpus_id"] == "ABS-0001"
        assert record["stage"] == "screening"
        assert record["run_id"] == 1
        assert record["inference_duration_ms"] == 150.0
        assert "timestamp" in record

    def test_create_run_card(self):
        records = [
            {"output_hash": "hash1", "inference_duration_ms": 100},
            {"output_hash": "hash2", "inference_duration_ms": 200},
        ]
        card = create_run_card(
            run_id=1,
            model_id="test-model",
            provider="test",
            stage="screening",
            total_calls=2,
            successful_calls=2,
            failed_calls=0,
            call_records=records,
            model_info={"weights_hash": "test"},
            config={"temperature": 0, "seed": 42},
            start_time="2026-01-01T00:00:00Z",
            end_time="2026-01-01T00:01:00Z",
        )
        assert card["run_id"] == 1
        assert card["execution"]["total_calls"] == 2
        assert card["execution"]["mean_duration_ms"] == 150.0
        assert "aggregate_output_hash" in card["provenance"]


# ── JSON Extraction Tests ───────────────────────────────────

class TestJsonExtraction:
    """Test JSON extraction from LLM responses."""

    def test_plain_json(self):
        text = '{"decision": "include", "confidence": 0.9}'
        result = _extract_json(text)
        assert result["decision"] == "include"

    def test_json_in_code_block(self):
        text = '```json\n{"decision": "exclude", "confidence": 0.8}\n```'
        result = _extract_json(text)
        assert result["decision"] == "exclude"

    def test_json_with_surrounding_text(self):
        text = 'Here is the result:\n{"decision": "include"}\nDone.'
        result = _extract_json(text)
        assert result["decision"] == "include"

    def test_invalid_json(self):
        text = "This is not JSON at all."
        result = _extract_json(text)
        assert result is None

    def test_json_with_code_block_no_lang(self):
        text = '```\n{"decision": "uncertain"}\n```'
        result = _extract_json(text)
        assert result["decision"] == "uncertain"


# ── Screening Pipeline Tests (Mocked) ──────────────────────

class TestScreeningPipeline:
    """Test screening pipeline with mocked model runners."""

    MOCK_SCREENING_RESPONSE = {
        "output_text": json.dumps({
            "decision": "include",
            "confidence": 0.95,
            "rationale": "PM2.5 exposure with respiratory hospitalization outcome",
            "exposure": "PM2.5",
            "outcome": "respiratory_hospitalization",
            "study_design": "time_series",
            "has_effect_estimate": True,
        }),
        "model_id": "test-model",
        "provider": "test",
        "inference_duration_ms": 150.0,
        "input_tokens": 500,
        "output_tokens": 100,
        "stop_reason": "end_turn",
    }

    SAMPLE_CORPUS = [
        {
            "corpus_id": "ABS-0001",
            "pmid": "12345678",
            "title": "PM2.5 and respiratory hospitalizations in Beijing",
            "abstract": "We studied the effect of PM2.5 on respiratory hospitalizations "
                       "using a time-series design. RR=1.023 (95% CI: 1.005-1.042).",
            "gold_category": "include",
        },
        {
            "corpus_id": "ABS-0002",
            "pmid": "87654321",
            "title": "Review of air pollution studies",
            "abstract": "This systematic review summarizes evidence on PM2.5 health effects.",
            "gold_category": "exclude",
        },
    ]

    SAMPLE_PROMPT = (
        "You are an expert. Screen this abstract.\n\n"
        "Title: {title}\n\nAbstract: {abstract}"
    )

    @patch("src.screening.runner._get_runner")
    def test_screening_returns_results(self, mock_get_runner):
        mock_runner = MagicMock()
        mock_runner.run_inference.return_value = self.MOCK_SCREENING_RESPONSE
        mock_get_runner.return_value = mock_runner

        config = {"id": "test-model", "provider": "test", "temperature": 0.0}
        results, records, stats = run_screening(
            corpus=self.SAMPLE_CORPUS,
            model_config=config,
            run_id=1,
            prompt_template=self.SAMPLE_PROMPT,
        )

        assert len(results) == 2
        assert len(records) == 2
        assert stats["total"] == 2
        assert stats["successful"] == 2

    @patch("src.screening.runner._get_runner")
    def test_screening_records_have_provenance(self, mock_get_runner):
        mock_runner = MagicMock()
        mock_runner.run_inference.return_value = self.MOCK_SCREENING_RESPONSE
        mock_get_runner.return_value = mock_runner

        config = {"id": "test-model", "provider": "test", "temperature": 0.0}
        results, records, stats = run_screening(
            corpus=self.SAMPLE_CORPUS[:1],
            model_config=config,
            run_id=1,
            prompt_template=self.SAMPLE_PROMPT,
        )

        record = records[0]
        assert record["corpus_id"] == "ABS-0001"
        assert record["stage"] == "screening"
        assert record["run_id"] == 1
        assert len(record["call_hash"]) == 64  # SHA-256 hex
        assert len(record["output_hash"]) == 64

    @patch("src.screening.runner._get_runner")
    def test_screening_handles_invalid_json(self, mock_get_runner):
        mock_runner = MagicMock()
        mock_runner.run_inference.return_value = {
            "output_text": "I cannot parse this abstract properly.",
            "model_id": "test",
            "provider": "test",
            "inference_duration_ms": 100,
        }
        mock_get_runner.return_value = mock_runner

        config = {"id": "test-model", "provider": "test", "temperature": 0.0}
        results, records, stats = run_screening(
            corpus=self.SAMPLE_CORPUS[:1],
            model_config=config,
            run_id=1,
            prompt_template=self.SAMPLE_PROMPT,
        )

        assert stats["failed"] == 1
        assert "error" in results[0]["output"]


# ── Extraction Pipeline Tests (Mocked) ─────────────────────

class TestExtractionPipeline:
    """Test extraction pipeline with mocked model runners."""

    MOCK_EXTRACTION_RESPONSE = {
        "output_text": json.dumps({
            "study_id": "Wang_2019",
            "study_location": "Beijing, China",
            "study_period": "2013-2017",
            "study_design": "time_series",
            "population": "general",
            "sample_size": None,
            "estimates": [{
                "effect_measure": "RR",
                "effect_estimate": 1.023,
                "ci_lower": 1.005,
                "ci_upper": 1.042,
                "ci_level": 95,
                "exposure_increment": "per 10 µg/m³",
                "lag": "lag0-1",
                "outcome_specific": "all_respiratory",
                "covariates": ["temperature", "humidity", "trend"],
            }],
        }),
        "output_text_raw": "...",
        "model_id": "test-model",
        "provider": "test",
        "inference_duration_ms": 200.0,
        "input_tokens": 600,
        "output_tokens": 150,
        "stop_reason": "end_turn",
    }

    SAMPLE_INCLUDED = [
        {
            "corpus_id": "ABS-0001",
            "pmid": "12345678",
            "title": "PM2.5 and respiratory hospitalizations in Beijing",
            "abstract": "We studied PM2.5 effects on respiratory hospitalizations "
                       "using time-series. RR=1.023 (95% CI: 1.005-1.042) per 10 µg/m³.",
        },
    ]

    SAMPLE_PROMPT = (
        "Extract data from this abstract.\n\n"
        "Title: {title}\n\nAbstract: {abstract}"
    )

    @patch("src.extraction.runner._get_runner")
    def test_extraction_returns_results(self, mock_get_runner):
        mock_runner = MagicMock()
        mock_runner.run_inference.return_value = self.MOCK_EXTRACTION_RESPONSE
        mock_get_runner.return_value = mock_runner

        config = {"id": "test-model", "provider": "test", "temperature": 0.0}
        results, records, stats = run_extraction(
            articles=self.SAMPLE_INCLUDED,
            model_config=config,
            run_id=1,
            prompt_template=self.SAMPLE_PROMPT,
        )

        assert len(results) == 1
        assert stats["successful"] == 1
        assert results[0]["output"]["estimates"][0]["effect_estimate"] == 1.023

    @patch("src.extraction.runner._get_runner")
    def test_extraction_with_schema_validation(self, mock_get_runner):
        mock_runner = MagicMock()
        mock_runner.run_inference.return_value = self.MOCK_EXTRACTION_RESPONSE
        mock_get_runner.return_value = mock_runner

        schema_path = Path("configs/schemas/extraction_output.json")
        if schema_path.exists():
            with open(schema_path) as f:
                schema = json.load(f)
        else:
            schema = None

        config = {"id": "test-model", "provider": "test", "temperature": 0.0}
        results, records, stats = run_extraction(
            articles=self.SAMPLE_INCLUDED,
            model_config=config,
            run_id=1,
            prompt_template=self.SAMPLE_PROMPT,
            schema=schema,
        )

        assert stats["valid"] == 1


# ── Model Runner Tests (Unit) ──────────────────────────────

class TestModelRunnerImports:
    """Test that model runner modules can be imported."""

    def test_import_ollama_runner(self):
        from src.models import ollama_runner
        assert hasattr(ollama_runner, "run_inference")
        assert hasattr(ollama_runner, "get_model_info")

    def test_import_claude_runner(self):
        from src.models import claude_runner
        assert hasattr(claude_runner, "run_inference")
        assert hasattr(claude_runner, "get_model_info")

    def test_import_gemini_runner(self):
        from src.models import gemini_runner
        assert hasattr(gemini_runner, "run_inference")
        assert hasattr(gemini_runner, "get_model_info")

    def test_claude_model_info(self):
        from src.models.claude_runner import get_model_info
        info = get_model_info()
        assert info["provider"] == "anthropic"
        assert info["weights_hash"] == "proprietary-not-available"

    def test_gemini_model_info(self):
        from src.models.gemini_runner import get_model_info
        info = get_model_info()
        assert info["provider"] == "google"


# ── Integration-style Tests ─────────────────────────────────

class TestOrchestrator:
    """Test the experiment orchestrator components."""

    def test_corpus_loads(self):
        path = Path("data/corpus/corpus_500.json")
        if not path.exists():
            pytest.skip("Corpus not built yet")
        with open(path) as f:
            data = json.load(f)
        assert len(data["corpus"]) == 500

    def test_prompts_load(self):
        for path in [SCREENING_PROMPT_PATH, EXTRACTION_PROMPT_PATH]:
            p = Path(path)
            assert p.exists(), f"Prompt not found: {path}"
            text = p.read_text()
            assert "{title}" in text
            assert "{abstract}" in text

    def test_schemas_load(self):
        for path in [SCREENING_SCHEMA_PATH, EXTRACTION_SCHEMA_PATH]:
            p = Path(path)
            assert p.exists(), f"Schema not found: {path}"
            with open(p) as f:
                schema = json.load(f)
            assert "$schema" in schema


SCREENING_PROMPT_PATH = "configs/prompts/screening.txt"
EXTRACTION_PROMPT_PATH = "configs/prompts/extraction.txt"
SCREENING_SCHEMA_PATH = "configs/schemas/screening_output.json"
EXTRACTION_SCHEMA_PATH = "configs/schemas/extraction_output.json"
