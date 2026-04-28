"""OpenRouter runner — multi-provider LLM access via single API.

Used to run LLaMA 3 8B Instruct via cloud (P0.1 desconfound experiment).
OpenRouter routes to Together.ai / DeepInfra / Fireworks transparently and
serves the EXACT meta-llama/llama-3-8b-instruct (matching local Ollama llama3:8b).

Pricing (2026-04): ~$0.18/1M tokens combined for llama-3-8b-instruct.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Optional


DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "meta-llama/llama-3-8b-instruct"
DEFAULT_TIMEOUT = 60


def run_inference(
    prompt: str,
    input_text: str,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    temperature: float = 0.0,
    seed: Optional[int] = 42,
    max_tokens: int = 2048,
    timeout: int = DEFAULT_TIMEOUT,
    provider_preferences: Optional[list[str]] = None,
) -> dict:
    if api_key is None:
        api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    full_prompt = f"{prompt}\n\n{input_text}"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if seed is not None:
        payload["seed"] = seed
    # Pin to specific provider for reproducibility (default: Together for LLaMA)
    if provider_preferences:
        payload["provider"] = {"order": provider_preferences, "allow_fallbacks": False}

    req = urllib.request.Request(
        DEFAULT_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "llm-evidence-synthesis-reproducibility/1.0 (research)",
            "HTTP-Referer": "https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility",
            "X-Title": "llm-evidence-synthesis-reproducibility",
            "Accept": "application/json",
        },
        method="POST",
    )

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenRouter HTTP {e.code}: {err_body[:500]}") from e
    duration_ms = (time.time() - t0) * 1000

    parsed = json.loads(body)
    if "choices" not in parsed:
        raise RuntimeError(f"OpenRouter unexpected response: {json.dumps(parsed)[:500]}")
    choice = parsed["choices"][0]
    content = choice["message"]["content"]
    usage = parsed.get("usage", {})
    return {
        "output_text": content,
        "duration_ms": duration_ms,
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "finish_reason": choice.get("finish_reason"),
        "provider": parsed.get("provider"),  # OpenRouter reports which underlying provider served
        "raw_response": parsed,
    }
