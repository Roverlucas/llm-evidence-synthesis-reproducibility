"""
Jev runner (TypeSafe decision model, served through Vercel AI Gateway).

Jev does not generate text. It answers typed questions about a shared state and
returns a choice together with the probability of every option. The screening
question therefore carries the same inclusion/exclusion criteria as the text
prompt, and the answer is a choice over the same three labels the LLM stacks use.

Uses urllib-based HTTPS POST — no SDK dependency, like the other runners.
"""

import json
import os
import time
import urllib.request
from typing import Optional

API_URL = "https://ai-gateway.vercel.sh/v1/evaluate"
DEFAULT_MODEL = "typesafe-ai/jev"
PROVIDER = "typesafe-ai"

SCREENING_OPTIONS = {
    "include": "The record meets every inclusion criterion and no exclusion criterion.",
    "exclude": "The record fails at least one inclusion criterion or meets an exclusion criterion.",
    "uncertain": "The title and abstract do not give enough information to decide.",
}


def screening_criteria_from_prompt(prompt: str) -> str:
    """Keep the criteria sections of the text prompt and drop the output-format part.

    The criteria wording is shared verbatim with the LLM stacks; only the JSON
    instructions, which have no meaning for a decision model, are removed.
    """
    start = prompt.index("## Inclusion Criteria")
    end = prompt.index("## Input")
    return prompt[start:end].strip()


def build_payload(state: str, instructions: str, model: str = DEFAULT_MODEL) -> dict:
    """Request body for one screening decision, pinned to TypeSafe with no fallback."""
    return {
        "model": model,
        "state": state,
        "questions": {
            "screening": {
                "type": "choice",
                "instructions": instructions,
                "criteria": SCREENING_OPTIONS,
            }
        },
        # Pin the provider so no other model can answer, and keep fallbacks off.
        "providerOptions": {"gateway": {"only": [PROVIDER]}},
    }


def parse_response(result: dict) -> dict:
    """Pull the answer, usage and routing metadata out of a /v1/evaluate response."""
    answer = result["answers"]["screening"]
    gateway = result.get("providerMetadata", {}).get("gateway", {})
    routing = gateway.get("routing", {})
    usage = result.get("usage", {})
    return {
        "choice": answer.get("choice"),
        "probabilities": answer.get("probabilities"),
        "model_id": result.get("model"),
        "final_provider": routing.get("finalProvider"),
        "input_tokens": usage.get("inputTokens"),
        "output_tokens": usage.get("outputTokens"),
        "cost_usd": gateway.get("cost"),
        "generation_id": gateway.get("generationId"),
    }


def run_decision(
    state: str,
    instructions: str,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    timeout: int = 60,
) -> dict:
    """Run a single screening decision through the AI Gateway."""
    if api_key is None:
        api_key = os.environ.get("AI_GATEWAY_API_KEY")
    if not api_key:
        raise ValueError("AI_GATEWAY_API_KEY not set")

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(build_payload(state, instructions, model)).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        result = json.loads(resp.read().decode())
    parsed = parse_response(result)
    parsed["inference_duration_ms"] = round((time.time() - t0) * 1000, 1)
    return parsed


def get_model_info(model: str = DEFAULT_MODEL) -> dict:
    """Return model metadata (closed weights, hosted only)."""
    return {
        "model_id": model,
        "provider": PROVIDER,
        "weights_hash": "proprietary-not-available",
        "model_source": "vercel-ai-gateway",
    }
