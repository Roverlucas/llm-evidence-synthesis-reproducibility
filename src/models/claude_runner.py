"""
Claude Sonnet runner (Anthropic API).

Uses urllib-based HTTPS POST — no SDK dependency.
Adapted from JAIR paper infrastructure.
"""

import json
import os
import threading
import time
import urllib.request
from typing import Optional

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
API_VERSION = "2023-06-01"
TOTAL_TIMEOUT_MULTIPLIER = 3


def _urlopen_with_hard_timeout(req, socket_timeout, total_timeout):
    """HTTP request with thread-based total timeout (reliable on macOS)."""
    result_box = [None]
    error_box = [None]

    def _worker():
        try:
            with urllib.request.urlopen(req, timeout=socket_timeout) as resp:
                result_box[0] = json.loads(resp.read().decode())
        except Exception as e:
            error_box[0] = e

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    t.join(timeout=total_timeout)

    if t.is_alive():
        raise TimeoutError(f"Total request timeout ({total_timeout}s) exceeded")
    if error_box[0] is not None:
        raise error_box[0]
    return result_box[0]


def run_inference(
    prompt: str,
    input_text: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
    max_tokens: int = 2048,
    api_key: Optional[str] = None,
    timeout: int = 60,
) -> dict:
    """Run single inference via Anthropic Messages API."""
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    full_prompt = f"{prompt}\n\n{input_text}"

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": full_prompt}],
    }
    # Send temperature unconditionally. The previous guard (`if temperature > 0.0`)
    # silently dropped the field for temperature=0.0 — the setting this study runs
    # under — so requests inherited the provider default of 1.0 while the run card
    # recorded 0.0. Every other runner in this package sends it unconditionally.
    # NOTE: the deposited data in data/raw_outputs/claude-sonnet-4-5/ was generated
    # BEFORE this fix and therefore ran at the provider default. It has not been
    # regenerated; the manuscript declares this explicitly.
    payload["temperature"] = temperature

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": API_VERSION,
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    total_timeout = timeout * TOTAL_TIMEOUT_MULTIPLIER
    t0 = time.time()
    result = _urlopen_with_hard_timeout(req, timeout, total_timeout)
    duration_ms = (time.time() - t0) * 1000

    # Extract text from content blocks
    output_text = ""
    for block in result.get("content", []):
        if block.get("type") == "text":
            output_text += block.get("text", "")

    usage = result.get("usage", {})

    return {
        "output_text": output_text,
        "model_id": result.get("model", model),
        "provider": "anthropic",
        "inference_duration_ms": round(duration_ms, 1),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "stop_reason": result.get("stop_reason"),
        "response_id": result.get("id"),
    }


def get_model_info(model: str = DEFAULT_MODEL) -> dict:
    """Return model metadata (no weights hash available for API models)."""
    return {
        "model_id": model,
        "provider": "anthropic",
        "weights_hash": "proprietary-not-available",
        "model_source": "anthropic-api",
    }
