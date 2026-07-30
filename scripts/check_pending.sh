#!/usr/bin/env bash
# Fails while any placeholder remains in the submission package.
#
# Nothing that depends on data still being collected should be able to reach a
# submission by accident. Run this before tagging a submission version:
#
#     bash scripts/check_pending.sh
#
# Exit status 0 means the package carries no unresolved placeholder.
set -uo pipefail
cd "$(dirname "$0")/.."

fail=0
report() {  # report <label> <pattern> <files...>
  local label="$1" pattern="$2"; shift 2
  local hits
  hits=$(grep -rn --binary-files=without-match -E "$pattern" "$@" 2>/dev/null || true)
  if [[ -n "$hits" ]]; then
    echo "FAIL — $label:"
    echo "$hits" | sed 's/^/    /'
    fail=1
  else
    echo "ok   — $label"
  fi
}

MANUSCRIPT=(article/main.tex article/supplementary.tex)
SUBMISSION=(article/main.tex article/supplementary.tex docs/cover_letter_rsm.md
            osf_package/CITATIONS.md)

echo "== placeholders that must never ship =="
report "\\pending{} markers in the manuscript" '\\pending\{' "${MANUSCRIPT[@]}"
report "XXXXX / YYYYY DOI placeholders" 'XXXXX|YYYYY' "${SUBMISSION[@]}"
report "TODO / TBD / FIXME" '\bTODO\b|\bTBD\b|\bFIXME\b' "${SUBMISSION[@]}"
report "camera-ready promises" 'camera-ready|to be reported|will be reported|in progress at the time of submission' "${SUBMISSION[@]}"
report "internal notes addressed to the authors" 'Confirm with|check email sent items|acknowledgment to be completed' "${SUBMISSION[@]}"

echo
echo "== consistency checks =="
# The tie-breaker must match the registration (senior author). If a future edit moves
# the role to the first author, that becomes a pre-registration deviation and has to be
# disclosed as one — this check refuses the silent version of that change.
if grep -qiE 'reassigned to the first author|tie-break(er)? = *(L\.R\.|Lucas)' \
     article/main.tex article/supplementary.tex data/dual_labeling/protocols/labeling_protocol.md 2>/dev/null \
   | grep -qv 'reverted\|SUPERSEDED\|reconsidered'; then
  echo "FAIL — tie-breaker appears reassigned away from the registered senior author;"
  echo "       if intended, it is a deviation from OSF fgn3e and must be declared as such"
  fail=1
elif grep -q "senior author (Y.d.S.T.) as tie-breaker" article/main.tex; then
  echo "ok   — tie-breaker matches the registration (senior author)"
else
  echo "FAIL — main.tex does not state who breaks ties; the registration specifies the senior author"
  fail=1
fi

# The registration DOI must be cited wherever pre-commitment is claimed.
if grep -q "pre-registered" article/main.tex && ! grep -q "OSF.IO/FGN3E" article/main.tex; then
  echo "FAIL — main.tex claims pre-registration without citing the registration DOI"
  fail=1
else
  echo "ok   — registration DOI cited alongside the pre-registration claim"
fi

# A post-recalibration coefficient must never be PRESENTED as a kappa. Prose that
# explicitly forbids it (the protocol amendment, the script docstrings) is the fix,
# not a violation, so negated mentions are excluded from the match.
if grep -rniE 'secondary kappa|post-recalibration kappa|kappa pós-recalibração' \
     "${MANUSCRIPT[@]}" scripts/dual_labeling/ data/dual_labeling/protocols/ 2>/dev/null \
   | grep -viE 'not?( a| emit| report| present)|never|NÃO|deliberately|forbid'; then
  echo "FAIL — a post-recalibration figure is being called a kappa (see protocol v1.2 §0)"
  fail=1
else
  echo "ok   — no post-recalibration figure presented as a kappa"
fi

echo
if [[ $fail -eq 0 ]]; then
  echo "PASS — no unresolved placeholders; package may be tagged for submission."
else
  echo "BLOCKED — resolve the items above before tagging a submission version."
fi
exit $fail
