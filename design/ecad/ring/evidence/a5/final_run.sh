#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
R=$REPO_ROOT/design/ecad/ring
cd "$R" || exit 9
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc --severity-all --exit-code-violations -o erc-report.txt ring.kicad_sch > evidence/a5/erc_cmd.log 2>&1
echo "erc exit $?" >> evidence/a5/erc_cmd.log
../../.venv/bin/python check_netlist.py > evidence/a5/check_final_run.log 2>&1
echo "check exit $?" >> evidence/a5/check_final_run.log
