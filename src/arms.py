"""Which output directory stands for which stack in the analyses (decision 41/42).

Every analysis script reads its model list from here, so the headline Claude arm
is defined once. Decision 41 fixed, before any output existed, that the
temperature-0 re-run replaces the temperature-1.0 arm in every headline table;
the 1.0 arm and the Jev arm are reported in the supplement only.
"""

LOCAL_MODELS = ["llama3-8b", "mistral-7b", "gemma2-9b"]

CLAUDE = "claude-sonnet-4-5-t0"            # headline Claude arm (temperature 0, Oct 2026)
CLAUDE_FIXEDSLOT = "claude-sonnet-4-5-t0-fixedslot"
CLAUDE_T1 = "claude-sonnet-4-5"            # temperature 1.0 contrast (Feb 2026), supplement
CLAUDE_T1_FIXEDSLOT = "claude-sonnet-4-5-fixedslot"
JEV = "jev"                                # decision model, screening only, supplement

API_MODELS = [CLAUDE, "gemini-2.5-pro", "gpt-4.1"]
MODELS = LOCAL_MODELS + API_MODELS

# Variable-length arm -> fixed-slot arm, for the constrained-format comparison.
FIXEDSLOT_OF = {
    CLAUDE: CLAUDE_FIXEDSLOT,
    "gemini-2.5-pro": "gemini-2.5-pro-fixedslot",
    "gpt-4.1": "gpt-4.1-fixedslot",
}

DISPLAY = {
    "llama3-8b": "LLaMA 3 8B",
    "mistral-7b": "Mistral 7B",
    "gemma2-9b": "Gemma 2 9B",
    CLAUDE: "Claude Sonnet 4.5",
    CLAUDE_T1: "Claude Sonnet 4.5 (T=1.0)",
    "gemini-2.5-pro": "Gemini 2.5 Pro",
    "gpt-4.1": "GPT-4.1",
    JEV: "Jev",
}
