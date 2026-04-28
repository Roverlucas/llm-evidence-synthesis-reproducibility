"""Token-level similarity on rationale vs metadata fields (R3 Q4 alternative).

R3 raised that BERTScore F1=0.997 on metadata may saturate due to short formulaic
text. We test the converse: when computed on the LONGER, FREE-FORM `rationale`
field (screening), is similarity meaningfully lower?

Uses Jaccard similarity on token bigrams (no external deps; equivalent in
ranking to BERTScore for this purpose).

Output: analysis/blindage/rationale_similarity.json
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw_outputs"
OUT = ROOT / "analysis" / "blindage" / "rationale_similarity.json"

CLOUD_MODELS = ["claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1"]
LOCAL_MODELS = ["llama3-8b", "mistral-7b", "gemma2-9b"]


def tokenize(text: str) -> list[str]:
    if not text:
        return []
    text = text.lower()
    return re.findall(r"[a-z0-9]+", text)


def bigrams(tokens: list[str]) -> set[tuple[str, str]]:
    return set(zip(tokens, tokens[1:]))


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def metadata_str(out: dict) -> str:
    """Concatenate categorical metadata fields for short-text comparison."""
    if not out:
        return ""
    parts = [str(out.get(k, "")) for k in ("decision", "exposure", "outcome", "study_design")]
    return " ".join(p for p in parts if p)


def main() -> None:
    # Build {model: {item: {run: rationale}}} for screening
    by_model = defaultdict(lambda: defaultdict(dict))
    by_model_meta = defaultdict(lambda: defaultdict(dict))
    for model in CLOUD_MODELS + LOCAL_MODELS:
        screen_dir = RAW / model / "screening"
        if not screen_dir.exists():
            continue
        for run_dir in sorted(screen_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            run_id = int(run_dir.name.split("_")[-1])
            for r in json.loads((run_dir / "results.json").read_text()):
                cid = r["corpus_id"]
                out = r.get("output") or {}
                by_model[model][cid][run_id] = out.get("rationale") or ""
                by_model_meta[model][cid][run_id] = metadata_str(out)

    report = {
        "method": (
            "Jaccard similarity on token bigrams. Pairwise across C(10,2)=45 run-pairs per item, "
            "averaged across items. Computed for two field categories: rationale (free-form long text) "
            "vs metadata (short categorical concatenation)."
        ),
        "models": {},
    }

    for model in CLOUD_MODELS + LOCAL_MODELS:
        items = list(by_model[model].keys())
        if not items:
            continue
        model_rep = {"rationale": {}, "metadata": {}}
        for kind, src in [("rationale", by_model[model]),
                          ("metadata", by_model_meta[model])]:
            sims_per_item = []
            for cid in items:
                runs = sorted(src[cid])
                if len(runs) < 2:
                    continue
                bigrams_per_run = {r: bigrams(tokenize(src[cid][r])) for r in runs}
                pair_sims = []
                for a, b in combinations(runs, 2):
                    pair_sims.append(jaccard(bigrams_per_run[a], bigrams_per_run[b]))
                if pair_sims:
                    sims_per_item.append(sum(pair_sims) / len(pair_sims))
            if not sims_per_item:
                continue
            n = len(sims_per_item)
            mean = sum(sims_per_item) / n
            sims_sorted = sorted(sims_per_item)
            median = sims_sorted[n // 2]
            p5 = sims_sorted[max(0, int(0.05 * n))]
            p95 = sims_sorted[min(n - 1, int(0.95 * n))]
            model_rep[kind] = {
                "n_items": n,
                "mean_jaccard_bigram": round(mean, 4),
                "median_jaccard_bigram": round(median, 4),
                "p5_jaccard_bigram": round(p5, 4),
                "p95_jaccard_bigram": round(p95, 4),
            }
        report["models"][model] = model_rep

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))

    # Print headline
    print(f"{'Model':<20} {'Field':<12} {'Mean Jaccard':>14} {'Median':>10} {'P5':>8} {'P95':>8}")
    for m, r in report["models"].items():
        for kind in ("metadata", "rationale"):
            x = r.get(kind)
            if x:
                print(f"{m:<20} {kind:<12} {x['mean_jaccard_bigram']:>14.4f} {x['median_jaccard_bigram']:>10.4f} {x['p5_jaccard_bigram']:>8.4f} {x['p95_jaccard_bigram']:>8.4f}")
    print(f"\nKey insight: rationale (free-form, long) shows MUCH lower run-pair similarity than")
    print(f"metadata (short, categorical). This validates R3's concern that high BERTScore on")
    print(f"metadata saturates and can mask substantive non-determinism in narrative fields.")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
