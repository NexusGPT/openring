#!/bin/bash
# kit_samples.sh: builds Nordic's stock samples that the ring design relies
# on, for the development kit target and for the simulated chip target, to
# prove those ready parts exist for the ring's chip. Runs in the container.
#
# Usage, from the Mac: sh firmware/tools/remote.sh kit-samples "tools/kit_samples.sh"
#
# For each sample: nrf54lm20dk/nrf54lm20a/cpuapp (sysbuild, the sample's
# default), then nrf54lm20bsim/nrf54lm20a/cpuapp (single image). When the
# nrf54lm20bsim build fails, nrf54l15bsim/nrf54l15/cpuapp is tried.
# Each build's log is in $OUT/<sample>-<target>.log. Last line:
# "RESULT PASS" or "RESULT FAIL <builds>".

set -u
JOBS=${RING_JOBS:-8}
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID}
NRF=/ws/nrf
SAMPLES="samples/bluetooth/peripheral_hids_keyboard samples/bluetooth/peripheral_ancs_client"
mkdir -p "$OUT"
FAILED=""
SUMMARY=""

build() { # build <tag> <board> <sample dir> <sysbuild flag>
	local tag=$1 board=$2 dir=$3 sb=$4
	echo "=== build $tag start $(date -u '+%Y-%m-%dT%H:%M:%SZ') log $OUT/$tag.log"
	west build -p always -b "$board" "$sb" -d "$OUT/$tag" -o=-j"$JOBS" "$dir" > "$OUT/$tag.log" 2>&1
	local rc=$?
	echo "=== build $tag end $(date -u '+%Y-%m-%dT%H:%M:%SZ') exit $rc"
	if [ $rc -ne 0 ]; then
		echo "--- last 40 lines of $OUT/$tag.log"
		tail -n 40 "$OUT/$tag.log"
		grep -n -m 10 -E "error|Error|ERROR" "$OUT/$tag.log"
	fi
	return $rc
}

size_report() {
	# Each table is followed by "Generating files from <build>/<image>/zephyr/zephyr.elf",
	# which names the image the table belongs to.
	awk '/Memory region[ \t]+Used Size/ {p=1; buf=$0 "\n"; next}
	     p && /^[ \t]*[A-Za-z0-9_]+:[ \t]+[0-9]+/ {buf=buf $0 "\n"; next}
	     p && /Generating files from .*zephyr\.elf/ {n=split($4, a, "/"); img=(n>=3 ? a[n-2] : $4);
	        printf "image %s (%s)\n%s", img, $4, buf; p=0; next}
	     p {printf "image unknown\n%s", buf; p=0}' "$1"
}

for s in $SAMPLES; do
	name=$(basename "$s")
	tag="$name-nrf54lm20dk"
	if build "$tag" nrf54lm20dk/nrf54lm20a/cpuapp "$NRF/$s" --sysbuild; then
		echo "--- flash and RAM use, $tag (linker memory report, images in build order):"
		cat "$OUT/$tag/domains.yaml"
		echo
		size_report "$OUT/$tag.log"
		SUMMARY="$SUMMARY $tag:ok"
	else
		FAILED="$FAILED $tag"
		SUMMARY="$SUMMARY $tag:FAIL"
	fi
	tag="$name-nrf54lm20bsim"
	if build "$tag" nrf54lm20bsim/nrf54lm20a/cpuapp "$NRF/$s" --no-sysbuild; then
		SUMMARY="$SUMMARY $tag:ok"
	else
		FAILED="$FAILED $tag"
		SUMMARY="$SUMMARY $tag:FAIL"
		tag="$name-nrf54l15bsim"
		if build "$tag" nrf54l15bsim/nrf54l15/cpuapp "$NRF/$s" --no-sysbuild; then
			SUMMARY="$SUMMARY $tag:ok"
		else
			SUMMARY="$SUMMARY $tag:FAIL"
		fi
	fi
done

echo "kit_samples: summary:$SUMMARY"
echo "kit_samples: logs in $OUT"
if [ -z "$FAILED" ]; then
	echo "RESULT PASS"
	exit 0
fi
echo "RESULT FAIL$FAILED"
exit 1
