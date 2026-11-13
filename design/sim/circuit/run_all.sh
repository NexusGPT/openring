#!/bin/sh
# Runs the whole circuit bench: builds every deck from design/ecad/ring and design/ecad/case (netlist.csv, parts.csv),
# runs every test through libngspice, compares each result with the pass lines of pass-lines.md by script and prints
# one line per test, then `RESULT PASS` (exit 0) or `RESULT FAIL` (exit 1).
# Usage: sh run_all.sh          Output also in results/run_all.log, results/rows.csv, results/info.txt.
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$HERE/../../.venv/bin/python"
mkdir -p "$HERE/results"
cd "$HERE" && "$PY" run_tests.py --out "$HERE/results" > "$HERE/results/run_all.log" 2>&1
code=$?
cat "$HERE/results/run_all.log"
exit $code
