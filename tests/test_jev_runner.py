"""Offline tests for the Jev runner: payload shape, criteria parity, response parsing."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from models.jev_runner import (  # noqa: E402
    build_payload, parse_response, screening_criteria_from_prompt,
)

PROMPT = (ROOT / "configs" / "prompts" / "screening.txt").read_text()


def test_criteria_keep_both_lists_and_drop_output_format():
    text = screening_criteria_from_prompt(PROMPT)
    assert text.startswith("## Inclusion Criteria")
    assert "## Exclusion Criteria" in text
    assert "Animal or in-vitro studies" in text
    assert "JSON" not in text and "{title}" not in text


def test_payload_is_pinned_to_typesafe_with_three_options():
    p = build_payload("state", "instr")
    q = p["questions"]["screening"]
    assert p["model"] == "typesafe-ai/jev"
    assert q["type"] == "choice"
    assert set(q["criteria"]) == {"include", "exclude", "uncertain"}
    assert p["providerOptions"]["gateway"]["only"] == ["typesafe-ai"]


def test_parse_response_reads_answer_usage_and_routing():
    resp = {
        "model": "typesafe-ai/jev",
        "answers": {"screening": {"type": "choice", "choice": "include",
                                  "probabilities": {"include": 0.9, "exclude": 0.08,
                                                    "uncertain": 0.02}}},
        "usage": {"inputTokens": 500, "outputTokens": 3},
        "providerMetadata": {"gateway": {"routing": {"finalProvider": "typesafe-ai"},
                                         "cost": "0.000021", "generationId": "gen_x"}},
    }
    r = parse_response(resp)
    assert r["choice"] == "include"
    assert r["probabilities"]["include"] == 0.9
    assert r["final_provider"] == "typesafe-ai"
    assert (r["input_tokens"], r["output_tokens"]) == (500, 3)
    assert r["cost_usd"] == "0.000021"
