"""Groq runner for LLaMA 3 8B served via Groq LPU cloud (P0.1 desconfound experiment).

Uses urllib.request (matches the rest of the project — no external SDK).
Pricing (2026-04 Groq publicly listed): llama-3.1-8b-instant is on free tier
with rate limits; if paid, ~$0.05/1M input, $0.08/1M output.

Key design: identical prompt + identical seed as local Ollama LLaMA 3 8B,
so any EMR difference is attributable to deployment infrastructure, not
model/prompt.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Optional


DEFAULT_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.1-8b-instant"  # Closest Groq-served LLaMA 3 8B variant
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
) -> dict:
    """Run single inference via Groq OpenAI-compatible Chat Completions endpoint."""
    if api_key is None:
        api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    full_prompt = f"{prompt}\n\n{input_text}"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if seed is not None:
        payload["seed"] = seed

    req = urllib.request.Request(
        DEFAULT_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "llm-evidence-synthesis-reproducibility/1.0 (research)",
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
        raise RuntimeError(f"Groq HTTP {e.code}: {err_body[:500]}") from e
    duration_ms = (time.time() - t0) * 1000

    parsed = json.loads(body)
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
        "raw_response": parsed,
    }
