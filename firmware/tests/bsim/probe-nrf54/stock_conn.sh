#!/bin/bash
# stock_conn.sh <board> : build Zephyr's own BabbleSim test tests/bsim/bluetooth/ll/conn
# (prj_split.conf, unmodified) for <board> and run its unmodified script
# tests_scripts/basic_conn_encrypted_split.sh (central_encrypted: the central calls
# bt_conn_set_security(BT_SECURITY_L2) and the test checks the bond/encryption).
# Runs in the container (/ws = SDK workspace, read only for this script; all output under
# /ws/out/probe54). Own BabbleSim dir so the shared /ws/tools/bsim/bin is not written.
set -u
BOARD=$1
TAG=$(printf '%s' "$BOARD" | tr -c 'A-Za-z0-9' _)
P=/ws/out/probe54
export ZEPHYR_BASE=/ws/zephyr
export BOARD
export BSIM_OUT_PATH=$P/bsim-$TAG
export BSIM_COMPONENTS_PATH=$BSIM_OUT_PATH/components
export WORK_DIR=$P/work-$TAG
rm -rf "$BSIM_OUT_PATH" "$WORK_DIR"
mkdir -p "$BSIM_OUT_PATH/bin" "$BSIM_OUT_PATH/results" "$WORK_DIR"
ln -s /ws/tools/bsim/lib "$BSIM_OUT_PATH/lib"
ln -s /ws/tools/bsim/components "$BSIM_OUT_PATH/components"
ln -s /ws/tools/bsim/bin/bs_2G4_phy_v1 "$BSIM_OUT_PATH/bin/bs_2G4_phy_v1"
echo "probe: board=$BOARD BSIM_OUT_PATH=$BSIM_OUT_PATH"
echo "probe: SDK $(grep -E 'VERSION_(MAJOR|MINOR)|PATCHLEVEL' /ws/nrf/VERSION | tr -d ' ' | tr '\n' ' ')"
source "$ZEPHYR_BASE/tests/bsim/compile.source"
cd "$ZEPHYR_BASE" || exit 3
app=tests/bsim/bluetooth/ll/conn conf_file=prj_split.conf compile
wait_for_background_jobs
echo "probe: build done, exit $?"
ls -l "$BSIM_OUT_PATH/bin"
echo "probe: running stock script"
bash "$ZEPHYR_BASE/tests/bsim/bluetooth/ll/conn/tests_scripts/basic_conn_encrypted_split.sh"
RC=$?
echo "probe: stock script exit code $RC (board $BOARD)"
exit $RC
