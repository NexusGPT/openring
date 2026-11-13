#!/bin/sh
# Host fallback of the ring core tests: compiles the module and the same test
# bodies as the Zephyr suite with the Mac's cc through a ztest shim, runs them,
# and checks the generated table against a fresh run of the generator.
# Prints "RESULT PASS tests=<n>" or "RESULT FAIL". Exit 0 on PASS, 1 on FAIL.
#
# Usage: sh run_host_tests.sh [MODULE_DIR]
#   MODULE_DIR defaults to firmware/modules/ring_core (the broken copy passes its own).
# Writes only into firmware/tests/core/host/build/.

HOST_DIR=$(cd "$(dirname "$0")" && pwd)
TESTS_DIR=$(cd "$HOST_DIR/.." && pwd)
FW_DIR=$(cd "$TESTS_DIR/../.." && pwd)
MODULE_DIR=${1:-$FW_DIR/modules/ring_core}
BUILD_DIR=${HOST_BUILD_DIR:-$HOST_DIR/build}
CC=${CC:-cc}

mkdir -p "$BUILD_DIR"
echo "host tests $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "module: $MODULE_DIR"
echo "compiler: $($CC --version 2>&1 | head -1)"

STATUS=0

# 1. generated table against a fresh run (only when Python is present)
if command -v python3 > "$BUILD_DIR/which-python.log" 2>&1; then
	mkdir -p "$BUILD_DIR/fresh"
	if python3 "$MODULE_DIR/tools/gen_table.py" --doc "$FW_DIR/../design/firmware.md" --out-dir "$BUILD_DIR/fresh" >"$BUILD_DIR/fresh/gen.log" 2>&1; then
		cat "$BUILD_DIR/fresh/gen.log"
		OLD_ROWS=$(grep '^#define RC_TABLE_ROWS' "$MODULE_DIR/src/state_table.inc" | awk '{print $3}')
		NEW_ROWS=$(grep '^#define RC_TABLE_ROWS' "$BUILD_DIR/fresh/state_table.inc" | awk '{print $3}')
		OLD_SUM=$(grep '^#define RC_TABLE_FNV1A' "$MODULE_DIR/src/state_table.inc" | awk '{print $3}')
		NEW_SUM=$(grep '^#define RC_TABLE_FNV1A' "$BUILD_DIR/fresh/state_table.inc" | awk '{print $3}')
		echo "generated table: committed rows=$OLD_ROWS checksum=$OLD_SUM, fresh rows=$NEW_ROWS checksum=$NEW_SUM"
		if [ "$OLD_ROWS" = "$NEW_ROWS" ] && [ "$OLD_SUM" = "$NEW_SUM" ] && \
		   cmp "$MODULE_DIR/src/state_table.inc" "$BUILD_DIR/fresh/state_table.inc" > "$BUILD_DIR/cmp.log" 2>&1; then
			echo "PASS generator.fresh_run_matches_committed_table"
		else
			echo "FAIL generator.fresh_run_matches_committed_table"
			cat "$BUILD_DIR/cmp.log"
			STATUS=1
		fi
	else
		cat "$BUILD_DIR/fresh/gen.log"
		echo "FAIL generator.fresh_run"
		STATUS=1
	fi
else
	echo "SKIP generator check: python3 not found"
fi

# 2. compile the module and the tests
if ! $CC -std=c11 -Wall -Wextra -Werror -Wno-unused-parameter -O1 -g \
	-I "$MODULE_DIR/include" -I "$HOST_DIR/shim" -I "$TESTS_DIR/src" \
	"$MODULE_DIR"/src/*.c "$TESTS_DIR"/src/*.c "$HOST_DIR/shim/runner.c" \
	-o "$BUILD_DIR/core_tests" > "$BUILD_DIR/compile.log" 2>&1; then
	cat "$BUILD_DIR/compile.log"
	echo "compile failed"
	echo "RESULT FAIL"
	exit 1
fi
cat "$BUILD_DIR/compile.log"

# 3. run
"$BUILD_DIR/core_tests" > "$BUILD_DIR/run.log" 2>&1
RUN=$?
grep -v '^RESULT' "$BUILD_DIR/run.log"
N=$(grep -c '^PASS ' "$BUILD_DIR/run.log")
if [ "$RUN" -eq 0 ] && [ "$STATUS" -eq 0 ]; then
	echo "RESULT PASS tests=$N"
	exit 0
fi
echo "RESULT FAIL"
exit 1
