#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# Final W1 measurement run: every generator and every check, in order, each with its own log in w1-evidence/.
# usage: bash run_final.sh <tag>      (all paths absolute; no stderr is thrown away)
T=${1:-final}
D=$REPO_ROOT/design
R=$D/ecad/ring
P=$R/pcb
E=$P/w1-evidence
PY=$D/.venv/bin/python
KP=$P/run_kipy.sh
cd "$R" || exit 9
run() { # name, command...
  n=$1; shift
  "$@" > "$E/${T}_$n.log" 2>&1
  echo "exit $?" >> "$E/${T}_$n.log"
}
run make_netlist "$PY" -I "$R/make_netlist.py"
cd "$P" || exit 9
run make_footprints "$PY" -I "$P/make_footprints.py"
run measure_u1 "$PY" -I "$P/measure_u1.py"
run measure_passives "$PY" -I "$P/measure_passives.py"
run measure_hirose_mp "$PY" -I "$P/measure_hirose_mp.py"
cd "$R" || exit 9
bash "$R/run_all.sh" "$T" > "$E/${T}_run_all.log" 2>&1
echo "exit $?" >> "$E/${T}_run_all.log"
cp "$R/evidence/check_$T.log" "$E/${T}_check_netlist_full.log"
cp "$R/evidence/erc-report_$T.txt" "$E/${T}_erc_report.txt"
cd "$P" || exit 9
run check_footprints_good "$KP" "$P/check_footprints.py"
run courtyard "$KP" "$E/courtyard_area.py" "$P/OpenRing.pretty"
run check_band "$KP" "$R/../band/check_band.py"
run make_broken "$PY" -I "$P/make_broken_fp.py"
run check_footprints_broken_ball "$KP" "$P/check_footprints.py" "$E/broken_ball.pretty"
run check_footprints_broken_missing "$KP" "$P/check_footprints.py" "$E/broken_missing.pretty"
mkdir -p "$E/empty_band.pretty"
run check_footprints_band_absent "$KP" "$P/check_footprints.py" "$P/OpenRing.pretty" "$R/netlist.csv" "$P/footprint-sources.csv" "$E/empty_band.pretty"
file -b "$D"/datasheets/slim_cs-csnp32gcr01-bow.pdf "$D"/datasheets/slim_knowles-*.pdf "$D"/datasheets/nrf54lm20a_szlcsc.pdf > "$E/datasheet_types.log" 2>&1
diff -u "$E/check_netlist_before.py" "$R/check_netlist.py" > "$E/check_netlist.diff"
diff -u "$E/make_netlist_before.py" "$R/make_netlist.py" > "$E/make_netlist.diff"
diff -u "$E/bom_before.csv" "$D/bom.csv" > "$E/bom.diff"
diff -u "$E/bom-notes_before.md" "$D/bom-notes.md" > "$E/bom-notes.diff"
diff -u "$E/parts_before.csv" "$R/parts.csv" > "$E/parts.diff"
cd "$D" || exit 9
run check_bom_after "$PY" "$D/tools/check_bom.py"
echo done
