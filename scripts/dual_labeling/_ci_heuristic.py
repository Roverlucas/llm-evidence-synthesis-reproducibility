"""Heuristic detection of a numeric 95% interval inside an abstract.

Supports the criterion-5 level distinction introduced in protocol v1.2 §2.1:
level 5a requires a numeric point estimate *and* numeric 95% CI in the abstract,
while a bare mention of the effect is level 5b. This is decision support only —
it flags abstracts for human review and never decides inclusion on its own.

Validation against the labeler1 round-1 labels: of the 46 abstracts where the
labeler recorded criterion 5 as failed, the heuristic finds a numeric interval in
only 7 (85% agreement); of the 28 consensus INCLUDEs, it flags none.
"""
from __future__ import annotations

import re

# Abstracts write intervals in wildly different shapes: "95% CI: 1.005-1.042",
# "95%CI 1.01 to 1.04", "95% CI = 16%-13%", "95% credible interval", negative
# bounds for percent-change estimates.
CI_MENTION = re.compile(
    r"95\s*%\s*(?:\(?\s*(?:confidence|credible)\s+interval\s*\)?\s*)?(?:c\.?i\.?)?",
    re.IGNORECASE,
)

# A bound is a decimal or a percentage — plain integers are excluded so that year
# ranges ("2016 to 2020") are not mistaken for an interval.
_BOUND = r"-?\d+(?:\.\d+)?\s*%|-?\d+\.\d+"
NUM_PAIR = re.compile(
    rf"(?:{_BOUND})\s*(?:[-–—,]|to)\s*(?:{_BOUND})",
    re.IGNORECASE,
)


def has_numeric_ci(abstract: object, window: int = 220) -> bool:
    """True when a 95% interval mention is followed by a numeric lower/upper pair.

    The window is generous because abstracts routinely separate the mention from
    the values ("Rate ratios (95% credible interval) per 10-ug/m3 increase in
    PM2.5 and all respiratory ED visits were 1.024 (1.018-1.029)").
    """
    text = str(abstract or "")
    return any(
        NUM_PAIR.search(text[m.end(): m.end() + window])
        for m in CI_MENTION.finditer(text)
    )
