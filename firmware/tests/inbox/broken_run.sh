#!/bin/bash
# broken_run.sh: proof that the logic suite of ring_inbox can fail. Runs inside the
# ring-os-toolchain container, firmware at /ws/firmware.
#
# Usage, from the Mac: sh firmware/tools/remote.sh inbox-broken "tests/inbox/broken_run.sh"
#
# Copies modules/ring_inbox to the output folder, makes one fault in the copy (the id reported as dropped is the newest, not the oldest), runs the suite against the copy
# with west twister on native_sim and on the simulated ring chip
# (nrf54lm20bsim/nrf54lm20a/cpuapp), and passes only when, on each board, the suite ran and
# the one named case failed (a build error or a timeout does not count). The real files are not
# touched. Last line: "RESULT PASS" or "RESULT FAIL <what>".

set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-inbox-broken}
mkdir -p "$OUT"
rm -rf "$OUT/broken_ring_inbox"
cp -r "$FW/modules/ring_inbox" "$OUT/broken_ring_inbox"
F=$OUT/broken_ring_inbox/src/rinbox.c
python3 -I - "$F" <<'PY'
import sys, pathlib
f = pathlib.Path(sys.argv[1])
s = f.read_text()
old = '*dropped = b->items[RINBOX_MAX - 1].uid;'
new = '*dropped = b->items[0].uid;'
if s.count(old) != 1:
	print("the edit did not match exactly once", s.count(old))
	sys.exit(1)
f.write_text(s.replace(old, new))
PY
if [ $? -ne 0 ]; then
	echo "RESULT FAIL the edit could not be made"
	exit 1
fi
diff -u "$FW/modules/ring_inbox/src/rinbox.c" "$F" > "$OUT/broken.diff"
cat "$OUT/broken.diff"
if [ ! -s "$OUT/broken.diff" ]; then
	echo "RESULT FAIL the edit changed nothing"
	exit 1
fi
NAMED="FAIL - [ring_inbox.test_full_drops_oldest]"
FAILED=""
for P in native_sim nrf54lm20bsim/nrf54lm20a/cpuapp; do
	T=$(echo "$P" | tr '/' '_')
	west twister -T "$FW/tests/inbox" -p "$P" -O "$OUT/twister-$T" --inline-logs -v \
		--extra-args RING_INBOX_DIR="$OUT/broken_ring_inbox" > "$OUT/twister-$T.log" 2>&1
	RC=$?
	grep -E "FAIL|PASS|passed|failed|Assertion" "$OUT/twister-$T.log" | head -30
	echo "twister exit code on the broken copy, $P: $RC (log $OUT/twister-$T.log)"
	NFAIL=$(grep -c -F -e " - FAIL - [" "$OUT/twister-$T.log")
	if grep -q "PROJECT EXECUTION FAILED" "$OUT/twister-$T.log" && grep -q -F "$NAMED" "$OUT/twister-$T.log"; then
		echo "$P: the named case failed, as required: $(grep -F "$NAMED" "$OUT/twister-$T.log" | head -1) (failed cases listed: $NFAIL)"
	else
		echo "$P: the named case did not fail (twister exit $RC): $NAMED"
		FAILED="$FAILED $P"
	fi
done
if [ -z "$FAILED" ]; then
	echo "RESULT PASS"
	exit 0
fi
echo "RESULT FAIL$FAILED"
exit 1
