"""
Extraction Pipeline (Stage B).

Processes included abstracts through the extraction prompt for a given model.
Validates output against JSON schema, records provenance per call.

Usage:
    from src.extraction.runner import run_extraction
    results, records, stats = run_extraction(articles, model_config, run_id, prompt)
"""

import json
import re
import time
from datetime import datetime, timezone
from typing import Optional

import jsonschema

from src.provenance.hasher import (
    compute_call_hash,
    compute_output_hash,
    create_call_record,
)


def _get_runner(provider: str):
    """Import the appropriate model runner."""
    if provider == "ollama":
        from src.models import ollama_runner
        return ollama_runner
    elif provider == "anthropic":
        from src.models import claude_runner
        return claude_runner
    elif provider == "google":
        from src.models import gemini_runner
        return gemini_runner
    else:
        raise ValueError(f"Unknown provider: {provider}")


def _extract_json(text: str) -> Optional[dict]:
    """Extract JSON from LLM response, handling markdown code blocks."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def _run_single_extraction(
    runner,
    prompt: str,
    title: str,
    abstract: str,
    model_config: dict,
    schema: Optional[dict] = None,
    max_retries: int = 2,
) -> tuple[dict, dict, bool]:
    """
    Run extraction for a single abstract.
    Returns (parsed_result, raw_inference, valid).
    """
    input_text = f"Title: {title}\n\nAbstract: {abstract}"
    provider = model_config["provider"]

    kwargs = {"prompt": prompt, "input_text": input_text}

    if provider == "ollama":
        kwargs["model"] = model_config.get("model", "llama3:8b")
        kwargs["endpoint"] = model_config.get("endpoint", "http://localhost:11434")
        kwargs["temperature"] = model_config.get("temperature", 0.0)
        kwargs["seed"] = model_config.get("seed", 42)
        kwargs["num_predict"] = model_config.get("num_predict", 2048)
    elif provider == "anthropic":
        kwargs["model"] = model_config.get("model", "claude-sonnet-4-5-20250929")
        kwargs["temperature"] = model_config.get("temperature", 0.0)
        kwargs["max_tokens"] = model_config.get("max_tokens", 2048)
    elif provider == "google":
        kwargs["model"] = model_config.get("model", "gemini-2.5-pro")
        kwargs["temperature"] = model_config.get("temperature", 0.0)
        kwargs["max_output_tokens"] = model_config.get("max_output_tokens", 8192)
        kwargs["seed"] = model_config.get("seed", 42)

    for attempt in range(max_retries + 1):
        try:
            result = runner.run_inference(**kwargs)
            parsed = _extract_json(result["output_text"])

            if parsed is None:
                if attempt < max_retries:
                    time.sleep(1)
                    continue
                return {"error": "json_parse_failed", "raw": result["output_text"]}, result, False

            # Validate against schema
            valid = True
            if schema:
                try:
                    jsonschema.validate(parsed, schema)
                except jsonschema.ValidationError as e:
                    parsed["_validation_error"] = str(e.message)
                    valid = False

            return parsed, result, valid

        except Exception as e:
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue
            return {"error": str(e)}, {}, False

    return {"error": "max_retries_exceeded"}, {}, False


def run_extraction(
    articles: list[dict],
    model_config: dict,
    run_id: int,
    prompt_template: str,
    schema: Optional[dict] = None,
    progress_callback=None,
) -> tuple[list[dict], list[dict], dict]:
    """
    Run extraction for all articles (included abstracts only).

    Args:
        articles: List of article dicts (only those labeled 'include')
        model_config: Model configuration dict
        run_id: Run number (1-30)
        prompt_template: Extraction prompt (with {title} and {abstract} placeholders)
        schema: Optional JSON schema for validation
        progress_callback: Optional callable(current, total)

    Returns:
        (results, call_records, stats)
    """
    provider = model_config["provider"]
    model_id = model_config["id"]
    runner = _get_runner(provider)

    results = []
    call_records = []
    successful = 0
    failed = 0
    valid_count = 0

    start_time = datetime.now(timezone.utc).isoformat()

    for i, article in enumerate(articles):
        prompt = prompt_template.replace("{title}", article["title"])
        prompt = prompt.replace("{abstract}", article["abstract"])

        parsed, raw_result, valid = _run_single_extraction(
            runner=runner,
            prompt=prompt,
            title=article["title"],
            abstract=article["abstract"],
            model_config=model_config,
            schema=schema,
        )

        call_hash = compute_call_hash(
            prompt=prompt_template,
            input_text=f"{article['title']}\n{article['abstract']}",
            model_id=model_id,
            temperature=model_config.get("temperature", 0.0),
            seed=model_config.get("seed"),
        )
        output_hash = compute_output_hash(raw_result.get("output_text", ""))

        record = create_call_record(
            corpus_id=article["corpus_id"],
            call_hash=call_hash,
            output_hash=output_hash,
            model_id=model_id,
            provider=provider,
            stage="extraction",
            run_id=run_id,
            inference_result=raw_result,
        )
        call_records.append(record)

        result_entry = {
            "corpus_id": article["corpus_id"],
            "pmid": article["pmid"],
            "run_id": run_id,
            "model_id": model_id,
            "output": parsed,
            "valid": valid,
            "output_hash": output_hash,
        }
        results.append(result_entry)

        if "error" not in parsed:
            successful += 1
            if valid:
                valid_count += 1
        else:
            failed += 1

        if progress_callback:
            progress_callback(i + 1, len(articles))

    end_time = datetime.now(timezone.utc).isoformat()

    stats = {
        "run_id": run_id,
        "model_id": model_id,
        "stage": "extraction",
        "total": len(articles),
        "successful": successful,
        "failed": failed,
        "valid": valid_count,
        "start_time": start_time,
        "end_time": end_time,
    }

    return results, call_records, stats
