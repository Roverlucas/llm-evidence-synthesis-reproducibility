#!/usr/bin/env python3
"""
Reprocess Mistral 7B extraction results: fix JSON parse failures.

The raw LLM output is already saved. This script applies improved JSON
cleaning (strip JS comments, fix bracket mismatches) to recover the 16
articles that failed parsing in each run.

No new LLM calls are made — only post-processing of existing data.
"""
import json
import os
import re
from pathlib import Path

BASE = Path("data/raw_outputs/mistral-7b/extraction")
N_RUNS = 10


def clean_json_text(text: str) -> str:
    """Clean common LLM JSON mistakes."""
    # Remove JS-style line comments: // ... (but not inside strings)
    # Strategy: remove // followed by non-quote chars until end of line
    text = re.sub(r'//[^\n"]*(?=\n|$)', '', text)

    # Remove trailing commas before } or ]
    text = re.sub(r',\s*([}\]])', r'\1', text)

    return text


def fix_bracket_mismatch(text: str) -> str:
    """Fix bracket/brace mismatches using stack-based repair."""
    # First try: stack-based repair of ] vs } mismatches
    # The model sometimes closes { with ] instead of }
    stack = []
    chars = list(text)
    in_string = False
    escape_next = False

    for i, ch in enumerate(chars):
        if escape_next:
            escape_next = False
            continue
        if ch == '\\' and in_string:
            escape_next = True
            continue
        if ch == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue

        if ch in ('{', '['):
            stack.append(ch)
        elif ch == '}':
            if stack and stack[-1] == '{':
                stack.pop()
            elif stack and stack[-1] == '[':
                # } closing a [ — fix to ]
                chars[i] = ']'
                stack.pop()
        elif ch == ']':
            if stack and stack[-1] == '[':
                stack.pop()
            elif stack and stack[-1] == '{':
                # ] closing a { — fix to }
                chars[i] = '}'
                stack.pop()

    text = ''.join(chars)

    # Add missing closers at end
    open_c = text.count('{')
    close_c = text.count('}')
    open_b = text.count('[')
    close_b = text.count(']')

    if open_c > close_c:
        text = text.rstrip()
        for _ in range(open_c - close_c):
            text += '\n}'
    if open_b > close_b:
        text = text.rstrip()
        for _ in range(open_b - close_b):
            text += '\n]'

    return text


def extract_json(text: str) -> dict | None:
    """Extract JSON with improved cleaning."""
    text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Extract from markdown code block
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
    else:
        # Find first { ... } block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            candidate = match.group()
        else:
            return None

    # Try raw
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    # Try with cleaning
    cleaned = clean_json_text(candidate)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try with bracket fix
    fixed = fix_bracket_mismatch(cleaned)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    return None


def main():
    total_recovered = 0
    total_still_failed = 0

    for run_id in range(1, N_RUNS + 1):
        run_dir = BASE / f"run_{run_id:03d}"
        results_path = run_dir / "results.json"
        run_card_path = run_dir / "run_card.json"

        if not results_path.exists():
            print(f"  SKIP: run_{run_id:03d} (no results.json)")
            continue

        with open(results_path) as f:
            results = json.load(f)

        with open(run_card_path) as f:
            run_card = json.load(f)

        recovered = 0
        still_failed = 0

        for item in results:
            output = item.get("output", {})
            if "error" not in output:
                continue  # Already successful

            raw = output.get("raw", "")
            if not raw:
                still_failed += 1
                continue

            parsed = extract_json(raw)
            if parsed is not None:
                item["output"] = parsed
                item["valid"] = True  # Parsed successfully
                recovered += 1
            else:
                still_failed += 1

        # Update run_card stats
        successful = sum(1 for item in results if "error" not in item.get("output", {}))
        failed = len(results) - successful

        old_success = run_card["execution"]["successful_calls"]
        run_card["execution"]["successful_calls"] = successful
        run_card["execution"]["failed_calls"] = failed

        # Save updated files
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)

        with open(run_card_path, "w") as f:
            json.dump(run_card, f, indent=2)

        print(f"  run_{run_id:03d}: {old_success}→{successful}/100 (+{recovered} recovered, {still_failed} still failed)")

        total_recovered += recovered
        total_still_failed += still_failed

    print(f"\n  TOTAL: {total_recovered} recovered, {total_still_failed} still failed across {N_RUNS} runs")


if __name__ == "__main__":
    print("Reprocessing Mistral 7B extraction (JSON cleaning)...")
    print("=" * 60)
    main()
    print("=" * 60)
    print("Done. No LLM calls were made — only re-parsed existing raw output.")
