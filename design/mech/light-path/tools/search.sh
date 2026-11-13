#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: search.sh <name> <query words...>   plain curl to the DuckDuckGo html page; saves raw html and the result links
L=$REPO_ROOT/design/mech/light-path/logs
N="$1"; shift
Q=$(printf '%s' "$*" | sed 's/ /+/g')
curl -sS -L --max-time 40 -A "Mozilla/5.0" "https://html.duckduckgo.com/html/?q=$Q" -o "$L/search_$N.html" > "$L/search_$N.curl.log" 2>&1
echo "query: $*" > "$L/search_$N.txt"
echo "curl exit=$?" >> "$L/search_$N.txt"
$REPO_ROOT/design/.venv/bin/python -I $REPO_ROOT/design/mech/light-path/tools/ddg_parse.py "$L/search_$N.html" >> "$L/search_$N.txt" 2>&1
cat "$L/search_$N.txt"
