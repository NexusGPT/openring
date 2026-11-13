#!/bin/bash
# static_checks.sh: searches of unit U4's files for what the plan forbids. Run on the Mac, from anywhere:
#   bash firmware/tests/xfer/static_checks.sh   (prints each search, its hits, and a verdict line per search)
# Each search lists every hit; "0 hits" is the result of the search over the named files only.
set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
M=$FW/modules/ring_xfer
T=$FW/tests/xfer
n=0
search() {	# search <label> <extended regex> <files...>
	local label=$1 re=$2
	shift 2
	echo "=== $label"
	echo "files: $*"
	local out rc
	out=$(grep -n -E "$re" "$@" 2>&1)
	rc=$?
	[ -n "$out" ] && echo "$out"
	if [ $rc -eq 1 ]; then echo "RESULT $label: 0 hits"; else echo "RESULT $label: hits listed above (grep exit $rc)"; fi
}
SRC="$M/src/rxf_proto.c $M/src/rxf_proto.h $M/src/rxf_desc.c $M/src/rxf_desc.h $M/src/rxf_class.c $M/CMakeLists.txt $M/Kconfig"
search "C21 no core input call and no long press in the unit (module sources)" 'rc_|RC_EV|rcore|ring_core|long[ _-]?press|CENTRE|JOY|rec_start|rec_stop|rau_|rst_open|rst_close' $SRC
search "pure parts make no kernel call (rxf_proto.c, rxf_desc.c and their headers)" '\bk_[a-z_]+\(|zephyr/kernel|zephyr/device|zephyr/sys/(atomic|mutex)|\birq_|printk|\bLOG_(ERR|WRN|INF|DBG|MODULE)' $M/src/rxf_proto.c $M/src/rxf_proto.h $M/src/rxf_desc.c $M/src/rxf_desc.h
search "pure parts include list" '#include' $M/src/rxf_proto.c $M/src/rxf_desc.c
search "no chip pin by number (P0.xx, P1.xx, GPIO, pin) in module sources and tests" 'P[0-9]\.[0-9]+|[Pp]in [0-9]|gpio|GPIO|PIN\(' $SRC $T/src/*.c $T/src/*.h
search "hardware only through rhw.h in the thin part: no kit driver include" '#include <zephyr/(drivers|usb|device)' $M/src/rxf_class.c
search "no use of the server address or a key in files of the unit" '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+|BEGIN [A-Z ]*PRIVATE|ssh-|<platform>-secrets' $M/src/*.c $M/src/*.h $M/CMakeLists.txt $M/Kconfig $T/src/*.c $T/src/*.h $T/short_run.sh $T/broken_run.sh $T/broken_edit.py $T/CMakeLists.txt $T/prj.conf $T/testcase.yaml
