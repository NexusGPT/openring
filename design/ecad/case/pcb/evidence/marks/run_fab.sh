#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../.." && pwd)"  # the repository root, found from this script
# remakes the fabrication files of both case boards with the project's script, then the parts lists; logs and exit files in evidence/marks
P=$REPO_ROOT/design/ecad/case/pcb
E=$P/evidence/marks
cd "$P" || exit 9
for T in pins main; do
  nice -n 19 bash "$P/export_fab.sh" $T > "$E/fab_export_$T.log" 2>&1; echo "export_fab.sh $T exit $?" >> "$E/fab_exits.txt"
done
nice -n 19 python3 "$P/make_bom.py" > "$E/fab_bom.log" 2>&1; echo "make_bom.py exit $?" >> "$E/fab_exits.txt"
echo done > "$E/fab_all.done"
