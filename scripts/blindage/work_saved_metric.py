"""Work-saved-over-human metric (R2 indirect, P1-cost-benefit, RSM checklist 2.1).

Canonical metrics in SRMA for LLM-assisted screening:
    1. Inference time per abstract (mean, sum)
    2. Hours saved vs human baseline (literature: 50-100 abstracts/day/reviewer)
    3. Cost per abstract
    4. Time-to-screen the full 500-abstract corpus

Uses analysis/timing_and_costs.json (already computed).

Output: analysis/blindage/work_saved.json
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TIMING = ROOT / "analysis" / "timing_and_costs.json"
OUT = ROOT / "analysis" / "blindage" / "work_saved.json"

# Human baseline estimates from literature (Shemilt 2016, Wang 2023)
HUMAN_ABSTRACTS_PER_HOUR_LOW = 50   # careful screening, dual
HUMAN_ABSTRACTS_PER_HOUR_HIGH = 120  # fast single-reviewer screening
HUMAN_EXTRACTIONS_PER_HOUR_LOW = 6   # full-text extraction
HUMAN_EXTRACTIONS_PER_HOUR_HIGH = 15

# Typical SR corpus
TYPICAL_SR_ABSTRACTS = 2000
TYPICAL_SR_INCLUDED = 100


def main() -> None:
    timing = json.loads(TIMING.read_text())

    out = {
        "method": (
            "Work saved = (human time - LLM time) for equivalent task. "
            "Human baselines from Shemilt 2016 (J Biomed Inform) and Wang 2023 (JMIR)."
        ),
        "human_baselines": {
            "screening_abstracts_per_hour": {
                "low": HUMAN_ABSTRACTS_PER_HOUR_LOW,
                "high": HUMAN_ABSTRACTS_PER_HOUR_HIGH,
            },
            "extraction_articles_per_hour": {
                "low": HUMAN_EXTRACTIONS_PER_HOUR_LOW,
                "high": HUMAN_EXTRACTIONS_PER_HOUR_HIGH,
            },
        },
        "per_model": {},
        "for_typical_SR": {
            "assumptions": {
                "abstracts_to_screen": TYPICAL_SR_ABSTRACTS,
                "articles_to_extract_from": TYPICAL_SR_INCLUDED,
            },
        },
    }

    for model, d in timing["models"].items():
        stages = d["stages"]
        scr = stages.get("screening", {})
        ext = stages.get("extraction", {})
        # Timing per call
        scr_mean_ms = scr.get("timing", {}).get("mean_duration_per_call_ms", 0)
        ext_mean_ms = ext.get("timing", {}).get("mean_duration_per_call_ms", 0)
        scr_wall_sec = scr.get("wall_clock", {}).get("total_seconds", 0)
        ext_wall_sec = ext.get("wall_clock", {}).get("total_seconds", 0)

        # LLM abstracts per hour (using mean per-call)
        llm_scr_per_hour = (3600 / (scr_mean_ms / 1000)) if scr_mean_ms else 0
        llm_ext_per_hour = (3600 / (ext_mean_ms / 1000)) if ext_mean_ms else 0

        # Corpus-level: 500 abstracts screening, 100 extraction — single pass
        llm_scr_corpus_hrs = 500 * (scr_mean_ms / 1000) / 3600 if scr_mean_ms else 0
        llm_ext_corpus_hrs = 100 * (ext_mean_ms / 1000) / 3600 if ext_mean_ms else 0

        # Human corpus time (500 abstracts, 100 extractions)
        human_scr_hrs_low = 500 / HUMAN_ABSTRACTS_PER_HOUR_HIGH  # lower bound on human time
        human_scr_hrs_high = 500 / HUMAN_ABSTRACTS_PER_HOUR_LOW  # upper bound
        human_ext_hrs_low = 100 / HUMAN_EXTRACTIONS_PER_HOUR_HIGH
        human_ext_hrs_high = 100 / HUMAN_EXTRACTIONS_PER_HOUR_LOW

        out["per_model"][model] = {
            "screening": {
                "llm_mean_sec_per_abstract": round(scr_mean_ms / 1000, 2) if scr_mean_ms else None,
                "llm_abstracts_per_hour": round(llm_scr_per_hour, 0),
                "llm_hours_500_abstracts": round(llm_scr_corpus_hrs, 2),
                "human_hours_500_abstracts_range": [round(human_scr_hrs_low, 2),
                                                    round(human_scr_hrs_high, 2)],
                "hours_saved_range": [
                    round(human_scr_hrs_low - llm_scr_corpus_hrs, 2),
                    round(human_scr_hrs_high - llm_scr_corpus_hrs, 2),
                ],
                "speedup_vs_human_range": [
                    round(human_scr_hrs_low / llm_scr_corpus_hrs, 1) if llm_scr_corpus_hrs else None,
                    round(human_scr_hrs_high / llm_scr_corpus_hrs, 1) if llm_scr_corpus_hrs else None,
                ],
            },
            "extraction": {
                "llm_mean_sec_per_article": round(ext_mean_ms / 1000, 2) if ext_mean_ms else None,
                "llm_articles_per_hour": round(llm_ext_per_hour, 0),
                "llm_hours_100_articles": round(llm_ext_corpus_hrs, 2),
                "human_hours_100_articles_range": [round(human_ext_hrs_low, 2),
                                                   round(human_ext_hrs_high, 2)],
                "hours_saved_range": [
                    round(human_ext_hrs_low - llm_ext_corpus_hrs, 2),
                    round(human_ext_hrs_high - llm_ext_corpus_hrs, 2),
                ],
                "speedup_vs_human_range": [
                    round(human_ext_hrs_low / llm_ext_corpus_hrs, 1) if llm_ext_corpus_hrs else None,
                    round(human_ext_hrs_high / llm_ext_corpus_hrs, 1) if llm_ext_corpus_hrs else None,
                ],
            },
        }

        # Typical SR scenario (2000 abstracts × single-pass LLM vs dual-human)
        if scr_mean_ms:
            sr_llm_scr = TYPICAL_SR_ABSTRACTS * (scr_mean_ms / 1000) / 3600
            sr_human_scr = TYPICAL_SR_ABSTRACTS / HUMAN_ABSTRACTS_PER_HOUR_LOW
            sr_human_scr_dual = 2 * sr_human_scr
            out["per_model"][model]["typical_SR_scenario"] = {
                "screening_llm_hours": round(sr_llm_scr, 2),
                "screening_human_single_hours": round(sr_human_scr, 2),
                "screening_human_dual_hours": round(sr_human_scr_dual, 2),
                "screening_hours_saved_vs_dual_human": round(sr_human_scr_dual - sr_llm_scr, 2),
            }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))

    # Summary table
    print(f"{'Model':<20} {'Scr sec/abs':>13} {'LLM 500 hrs':>13} {'Human hrs (hi-lo)':>20} {'Speedup':>12}")
    for m, d in out["per_model"].items():
        scr = d["screening"]
        llm_hrs = scr["llm_hours_500_abstracts"]
        hum_lo, hum_hi = scr["human_hours_500_abstracts_range"]
        sp_lo, sp_hi = scr["speedup_vs_human_range"]
        if sp_lo:
            print(f"{m:<20} {scr['llm_mean_sec_per_abstract']:>13.2f} {llm_hrs:>13.2f} {hum_lo:>9.1f}-{hum_hi:<9.1f} {sp_lo:>5.1f}-{sp_hi:<5.1f}×")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
