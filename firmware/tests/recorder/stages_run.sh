#!/bin/bash
# stages_run.sh: runs the stages that step 6 added or changed in tools/build_all.sh ALONE, from the text of build_all.sh
# itself (the blocks are cut out of the delivered script and run with its own run_stage), so the proof is of the delivered
# code. Runs inside the ring-os-toolchain container, firmware at /ws/firmware.
# Usage, from the Mac:
#   RING_REMOTE_SRC=/root/ring-os/src-u-join sh firmware/tools/remote.sh u-join "bash tests/recorder/stages_run.sh <what>"
#   what: search = the stages recorder-one-mic-path, recorder-no-start-path, recorder-no-raw-pins (each with its self test);
#         all    = stage 1 (dk build, memory report, stack-report), stage 2 (bsim build, the 2 s run, the start line and the
#                  recorder's line), then the three search stages and recorder-product-drivers.
# Last line: "STAGES PASS" or "STAGES FAIL <stages>".
set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
JOBS=${RING_JOBS:-8}
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-recorder-stages}
WHAT=${1:-search}
mkdir -p "$OUT"
FAILED=""
S=$FW/tools/build_all.sh

# the definitions build_all.sh uses (cut from its text: variables, run_stage, size_report)
sed -n '/^DK_BOARD=/,/^START_LINE=/p;/^RECORDER_LINE=/p' "$S" > "$OUT/head.sh"
sed -n '/^run_stage() {/,/^}/p;/^size_report() {/,/^}/p' "$S" >> "$OUT/head.sh"
# shellcheck disable=SC1091
source "$OUT/head.sh"
# the step 6 block: the function definitions only (the "if ! run_stage ..." lines are left out and called below)
sed -n '/^STEP6_MODS=/,/^# Stage 5: broken copies/p' "$S" |
	awk '/^if ! run_stage recorder-/ {skip=3} skip>0 {skip--; next} {print}' > "$OUT/step6.sh"
# shellcheck disable=SC1091
source "$OUT/step6.sh"

if [ "$WHAT" = "all" ]; then
	sed -n '/^# Stage 1: development kit build./,/^# Stage 2: simulated chip build/p' "$S" > "$OUT/stage1.sh"
	sed -n '/^# Stage 2: simulated chip build/,/^# Stage 3: tests./p' "$S" > "$OUT/stage2.sh"
	# shellcheck disable=SC1091
	source "$OUT/stage1.sh"
	# shellcheck disable=SC1091
	source "$OUT/stage2.sh"
fi
for st in recorder_one_mic_path recorder_no_start_path recorder_no_raw_pins; do
	n=$(echo "$st" | tr '_' '-')
	if ! run_stage "$n" "$st"; then
		FAILED="$FAILED $n"
	fi
done
if [ "$WHAT" = "all" ]; then
	if ! run_stage recorder-product-drivers recorder_product_drivers; then
		FAILED="$FAILED recorder-product-drivers"
	fi
fi
echo "stages_run: logs in $OUT"
if [ -z "$FAILED" ]; then
	echo "STAGES PASS"
	exit 0
fi
echo "STAGES FAIL$FAILED"
exit 1
