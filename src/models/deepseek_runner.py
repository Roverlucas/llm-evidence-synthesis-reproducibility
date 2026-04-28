"""DeepSeek runner — DeepSeek-R1 (reasoning) and DeepSeek-V3 (chat).

Used for silver-external gold standard generation: a model from a DIFFERENT
provider family than the 6 models in the main study, providing an
INDEPENDENT extraction reference. R1 is a reasoning model — different
paradigm from the standard chat models.

Pricing (2026-04 DeepSeek API):
    - deepseek-chat (V3): $0.14/1M input, $0.28/1M output
    - deepseek-reasoner (R1): $0.55/1M input, $2.19/1M output (reasoning tokens)

For 500 calls × ~1500 input + ~3000 output (R1 reasoning): ~$2-4 total.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Optional


DEFAULT_ENDPOINT = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-reasoner"  # R1 reasoning model
DEFAULT_TIMEOUT = 180  # R1 takes longer due to reasoning tokens


def run_inference(
    prompt: str,
    input_text: str,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    temperature: float = 0.0,
    seed: Optional[int] = 42,
    max_tokens: int = 4096,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    if api_key is None:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY not set")

    full_prompt = f"{prompt}\n\n{input_text}"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": full_prompt}],
        "max_tokens": max_tokens,
    }
    # R1 doesn't accept temperature/top_p; only chat (V3) does
    if model == "deepseek-chat":
        payload["temperature"] = temperature
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
        raise RuntimeError(f"DeepSeek HTTP {e.code}: {err_body[:500]}") from e
    duration_ms = (time.time() - t0) * 1000

    parsed = json.loads(body)
    if "choices" not in parsed:
        raise RuntimeError(f"DeepSeek unexpected response: {json.dumps(parsed)[:500]}")
    choice = parsed["choices"][0]
    msg = choice["message"]
    content = msg.get("content", "")
    reasoning = msg.get("reasoning_content", "")  # R1 only
    usage = parsed.get("usage", {})
    return {
        "output_text": content,
        "reasoning_text": reasoning,
        "duration_ms": duration_ms,
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "reasoning_tokens": usage.get("completion_tokens_details", {}).get("reasoning_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "finish_reason": choice.get("finish_reason"),
        "raw_response": parsed,
    }
