#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# STAND-IN (copied rule, not remote.sh itself): remote.sh lines 82 to 84 run with a PATH that has no shasum, on two
# netlists that differ. Expected if the rule fails open: NET_A equals NET_B (both the shell's error word), so no refusal.
W=$REPO_ROOT/firmware/build-logs/step7/review2-work
NET_COPY=$W/scratch/firmware/boards/ringrec/netlist.csv
NET_SRC=$W/scratch/design/ecad/ring/netlist.csv
printf ' ' >> "$NET_COPY"
echo "files differ: $(cmp "$NET_COPY" "$NET_SRC" 2>&1)"
PATH=/bin
NET_A=$(shasum -a 256 "$NET_COPY" 2>&1 | /usr/bin/cut -d' ' -f1)
NET_B=$(shasum -a 256 "$NET_SRC" 2>&1 | /usr/bin/cut -d' ' -f1)
echo "NET_A=[$NET_A] NET_B=[$NET_B]"
if [ "$NET_A" != "$NET_B" ]; then echo "would REFUSE"; else echo "would PASS (no refusal) although the files differ"; fi
/bin/cp $REPO_ROOT/design/ecad/ring/netlist.csv "$NET_COPY"
