#!/bin/sh
# Proof that the bench can fail: three broken copies of the ring netlist (see expected-failures.md).
# Usage: sh prove_fail.sh        Output: results/prove_fail.log, last line "PROOF RESULT OK" or "PROOF RESULT FAILED".
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$HERE/../../.venv/bin/python"
mkdir -p "$HERE/results"
cd "$HERE" && "$PY" prove_fail.py > "$HERE/results/prove_fail.log" 2>&1
code=$?
cat "$HERE/results/prove_fail.log"
exit $code
