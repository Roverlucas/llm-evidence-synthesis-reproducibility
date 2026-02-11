"""
Gemini 2.5 Pro runner (Google AI API).

Uses urllib-based HTTPS POST — no SDK dependency.
Adapted from JAIR paper infrastructure.

Note: Gemini 2.5 Pro is a "thinking" model — thinking tokens consume
the maxOutputTokens budget. Set maxOutputTokens=8192 to leave room.
"""

import json
import os
import time
import urllib.request
from typing import Optional

API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-2.5-pro"


def run_inference(
    prompt: str,
    input_text: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
    max_output_tokens: int = 8192,
    seed: Optional[int] = 42,
    api_key: Optional[str] = None,
    timeout: int = 90,
) -> dict:
    """Run single inference via Gemini generateContent API."""
    if api_key is None:
        api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    full_prompt = f"{prompt}\n\n{input_text}"

    generation_config = {
        "temperature": temperature,
        "maxOutputTokens": max_output_tokens,
    }
    if seed is not None:
        generation_config["seed"] = seed

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": generation_config,
    }

    url = f"{API_BASE}/{model}:generateContent?key={api_key}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        result = json.loads(resp.read().decode())
    duration_ms = (time.time() - t0) * 1000

    # Extract text from candidates
    output_text = ""
    candidates = result.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            if "text" in part:
                output_text += part["text"]

    usage = result.get("usageMetadata", {})
    finish_reason = candidates[0].get("finishReason") if candidates else None

    return {
        "output_text": output_text,
        "model_id": result.get("modelVersion", model),
        "provider": "google",
        "inference_duration_ms": round(duration_ms, 1),
        "input_tokens": usage.get("promptTokenCount"),
        "output_tokens": usage.get("candidatesTokenCount"),
        "thoughts_tokens": usage.get("thoughtsTokenCount"),
        "finish_reason": finish_reason,
    }


def get_model_info(model: str = DEFAULT_MODEL) -> dict:
    """Return model metadata (no weights hash available for API models)."""
    return {
        "model_id": model,
        "provider": "google",
        "weights_hash": "proprietary-not-available",
        "model_source": "google-ai-studio",
    }
