#!/bin/bash
# stock_conn_plain.sh <board> : same as stock_conn.sh, but the run command of the stock script
# is used with ONE change: the two "-RealEncryption=1" arguments are removed (a sed copy of
# basic_conn_encrypted_split.sh in /ws/out/probe54; the stock script itself is not edited).
# Without the flag BabbleSim uses its default: "send everything in plain text" (no real AES).
# The binaries are the same unmodified stock test as in stock_conn.sh (rebuilt here).
set -u
BOARD=$1
TAG=$(printf '%s' "$BOARD" | tr -c 'A-Za-z0-9' _)
P=/ws/out/probe54
export ZEPHYR_BASE=/ws/zephyr
export BOARD
export BSIM_OUT_PATH=$P/bsim-$TAG
export BSIM_COMPONENTS_PATH=$BSIM_OUT_PATH/components
export WORK_DIR=$P/work-$TAG
mkdir -p "$BSIM_OUT_PATH/bin" "$BSIM_OUT_PATH/results"
[ -e "$BSIM_OUT_PATH/lib" ] || ln -s /ws/tools/bsim/lib "$BSIM_OUT_PATH/lib"
[ -e "$BSIM_OUT_PATH/components" ] || ln -s /ws/tools/bsim/components "$BSIM_OUT_PATH/components"
[ -e "$BSIM_OUT_PATH/bin/bs_2G4_phy_v1" ] || ln -s /ws/tools/bsim/bin/bs_2G4_phy_v1 "$BSIM_OUT_PATH/bin/bs_2G4_phy_v1"
EXE=$BSIM_OUT_PATH/bin/bs_${TAG}_tests_bsim_bluetooth_ll_conn_prj_split_conf
if [ ! -x "$EXE" ]; then
	source "$ZEPHYR_BASE/tests/bsim/compile.source"
	cd "$ZEPHYR_BASE" || exit 3
	app=tests/bsim/bluetooth/ll/conn conf_file=prj_split.conf compile
	wait_for_background_jobs
fi
ls -l "$BSIM_OUT_PATH/bin"
S=$ZEPHYR_BASE/tests/bsim/bluetooth/ll/conn/tests_scripts/basic_conn_encrypted_split.sh
COPY=$P/plain-$TAG.sh
sed 's/ -RealEncryption=1//' "$S" | sed 's#^source \${ZEPHYR_BASE}#source ${ZEPHYR_BASE}#' > "$COPY"
echo "probe: diff stock script vs plain copy"
diff "$S" "$COPY"
echo "probe: running plain-text copy (no -RealEncryption)"
bash "$COPY"
RC=$?
echo "probe: plain-text run exit code $RC (board $BOARD)"
exit $RC
