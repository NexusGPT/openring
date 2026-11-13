#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../.." && pwd)"  # the repository root, found from this script
# usage: getpdf.sh <url> <name.pdf>   saves into design/datasheets and prints page count
D=$REPO_ROOT/design
curl -sS -L --max-time 90 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36" -o "$D/datasheets/$2" "$1"; EC=$?
echo "curl exit=$EC"; file "$D/datasheets/$2"; ls -la "$D/datasheets/$2"
