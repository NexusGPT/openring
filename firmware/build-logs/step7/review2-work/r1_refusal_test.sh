#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# R1 self test of remote.sh's netlist refusal, in a scratch copy, with ssh and rsync replaced on PATH by a trap
# that only records a call (no network). Expected for every case: exit 2, a REFUSED line, no trap call.
W=$REPO_ROOT/firmware/build-logs/step7/review2-work
S=$W/scratch
ORIG=$REPO_ROOT/design/ecad/ring/netlist.csv
export PATH="$S/bin:$PATH"
export RING_LOG_DIR="$W/r1-logs"
mkdir -p "$RING_LOG_DIR"
restore() {
	cp "$ORIG" "$S/firmware/boards/ringrec/netlist.csv"
	cp "$ORIG" "$S/design/ecad/ring/netlist.csv"
}
run_case() {
	echo "=== case $1: $2"
	echo "expected: exit 2, REFUSED, no FAKE-NETWORK-CALL"
	before=$(cat "$W/network-calls.txt" 2>&1 | grep -c FAKE-NETWORK-CALL)
	sh "$S/firmware/tools/remote.sh" "r1$1" "true" 2>&1
	rc=$?
	after=$(cat "$W/network-calls.txt" 2>&1 | grep -c FAKE-NETWORK-CALL)
	echo "exit=$rc network_calls_before=$before network_calls_after=$after"
	restore
}
restore
# A: one row of the board copy changed (row 181, the LCD_TE row per the first review: P1.14 -> P1.15)
python3 -I - "$S/firmware/boards/ringrec/netlist.csv" <<'PY'
import sys
p=sys.argv[1]; L=open(p).read().split("\n")
print("row 181 before:", L[180])
L[180]=L[180].replace("P1.14","P1.15",1)
print("row 181 after: ", L[180])
open(p,"w").write("\n".join(L))
PY
run_case A "one row of firmware/boards/ringrec/netlist.csv changed"
# B: one row of the design copy changed
python3 -I - "$S/design/ecad/ring/netlist.csv" <<'PY'
import sys
p=sys.argv[1]; L=open(p).read().split("\n")
L[180]=L[180].replace("P1.14","P1.15",1)
open(p,"w").write("\n".join(L))
PY
run_case B "one row of design/ecad/ring/netlist.csv changed"
# C: board copy missing
mv "$S/firmware/boards/ringrec/netlist.csv" "$S/firmware/boards/ringrec/netlist.csv.away"
run_case C "board copy missing"
mv "$S/firmware/boards/ringrec/netlist.csv.away" "$W/scratch-netlist-away-kept.csv"
restore
# D: one byte appended to the board copy
printf ' ' >> "$S/firmware/boards/ringrec/netlist.csv"
run_case D "one trailing byte added to the board copy"
echo "=== end; final network-calls file:"
cat "$W/network-calls.txt" 2>&1
