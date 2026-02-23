"""
OpenAI GPT-4.1 runner (OpenAI API).

Uses urllib-based HTTPS POST — no SDK dependency.
Follows the same pattern as claude_runner.py and gemini_runner.py.
"""

import json
import os
import signal
import time
import urllib.request
from typing import Optional

API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4.1"
TOTAL_TIMEOUT_MULTIPLIER = 3


def run_inference(
    prompt: str,
    input_text: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
    max_tokens: int = 2048,
    seed: Optional[int] = 42,
    api_key: Optional[str] = None,
    timeout: int = 90,
) -> dict:
    """Run single inference via OpenAI Chat Completions API."""
    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    full_prompt = f"{prompt}\n\n{input_text}"

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": full_prompt}],
    }
    if seed is not None:
        payload["seed"] = seed

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    total_timeout = timeout * TOTAL_TIMEOUT_MULTIPLIER
    old_handler = signal.getsignal(signal.SIGALRM)

    def _alarm_handler(signum, frame):
        raise TimeoutError(f"Total request timeout ({total_timeout}s) exceeded")

    t0 = time.time()
    signal.signal(signal.SIGALRM, _alarm_handler)
    signal.alarm(total_timeout)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode())
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
    duration_ms = (time.time() - t0) * 1000

    # Extract text from choices
    output_text = ""
    choices = result.get("choices", [])
    if choices:
        output_text = choices[0].get("message", {}).get("content", "")

    usage = result.get("usage", {})
    finish_reason = choices[0].get("finish_reason") if choices else None
    system_fingerprint = result.get("system_fingerprint")

    return {
        "output_text": output_text,
        "model_id": result.get("model", model),
        "provider": "openai",
        "inference_duration_ms": round(duration_ms, 1),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "finish_reason": finish_reason,
        "system_fingerprint": system_fingerprint,
        "response_id": result.get("id"),
    }


def get_model_info(model: str = DEFAULT_MODEL) -> dict:
    """Return model metadata (no weights hash available for API models)."""
    return {
        "model_id": model,
        "provider": "openai",
        "weights_hash": "proprietary-not-available",
        "model_source": "openai-api",
    }
