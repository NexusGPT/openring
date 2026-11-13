#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: ds.sh <name without .pdf>   prints the text of design/datasheets/<name>.pdf and saves it in logs/<name>.txt
R=$REPO_ROOT
"$R/design/.venv/bin/python" "$R/design/tools/pdftext.py" "$R/design/datasheets/$1.pdf" > "$R/design/mech/light-path/logs/$1.txt" 2> "$R/design/mech/light-path/logs/$1.err"
echo "pdftext exit=$?"
grep -v '^ *$' "$R/design/mech/light-path/logs/$1.txt"
