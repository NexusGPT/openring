#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../.." && pwd)"  # the repository root, found from this script
# maker files US 7 to 13 (export_parts.py runs out/v9/export/export_size.py per size at nice -n 19, one after another), then the fresh-process read-back (item 104)
D=$REPO_ROOT/design
V=$D/mech/thin/out/v9
PY=$D/.venv/bin/python
cd $D/mfg/parts || exit 9
( date; shasum $D/mech/thin/thin.py; nice -n 19 $PY export_parts.py 7 8 9 10 11 12 13; echo "exit $?"; date ) > $V/export/export_parts_v9.log 2>&1
e1=$(tail -2 $V/export/export_parts_v9.log | awk '/^exit /{print $2}')
( date; nice -n 19 $PY $V/item104/maker_readback.py; echo "exit $?"; date ) > $V/item104/maker_readback.log 2>&1
e2=$(tail -2 $V/item104/maker_readback.log | awk '/^exit /{print $2}')
echo "export exit $e1; readback exit $e2; $(date)" > $V/export/run_export.done
