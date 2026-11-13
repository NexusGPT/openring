#!/bin/bash
# check_link_settings.sh <product .config> <test ring .config> [name]
# The iPhone part's link and stack settings must be the same in the product's built settings file and in the test
# ring's (both come from modules/ring_iphone/ring_iphone_link.conf). Prints each value; exit 1 on any difference or
# a missing value. Pure shell; no change to either file.
set -u
P=$1
R=$2
NAME=${3:-product}
BAD=0
for k in CONFIG_BT_L2CAP_TX_MTU CONFIG_BT_BUF_ACL_RX_SIZE CONFIG_BT_BUF_ACL_TX_SIZE CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE CONFIG_BT_GATT_DM_MAX_ATTRS; do
	pv=$(grep -E "^$k=" "$P" | head -1 | cut -d= -f2)
	rv=$(grep -E "^$k=" "$R" | head -1 | cut -d= -f2)
	echo "link-settings: $NAME $k=${pv:-unset} test-ring $k=${rv:-unset}"
	if [ -z "$pv" ] || [ -z "$rv" ] || [ "$pv" != "$rv" ]; then
		echo "link-settings: DIFFERENT $k ($NAME ${pv:-unset}, test ring ${rv:-unset})"
		BAD=1
	fi
done
# the MTU is pinned to design/firmware.md 7.1 (247): two equal wrong values fail
for f in "$P" "$R"; do
	v=$(grep -E "^CONFIG_BT_L2CAP_TX_MTU=" "$f" | head -1 | cut -d= -f2)
	if [ "${v:-0}" -lt 247 ]; then
		echo "link-settings: DIFFERENT CONFIG_BT_L2CAP_TX_MTU below 247 in $f (${v:-unset}; design/firmware.md 7.1 asks for 247)"
		BAD=1
	fi
done
exit $BAD
