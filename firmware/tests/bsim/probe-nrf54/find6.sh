#!/bin/bash
cat /ws/zephyr/tests/bsim/sh_common.source
echo "## ZEPHYR_BASE"; echo "ZEPHYR_BASE=${ZEPHYR_BASE:-unset}"; ls -d /ws/zephyr
ls /ws/tools/bsim; ls /ws/tools/bsim/lib | head; ls /ws/out | head -30
echo "## ll/conn CMakeLists"; cat /ws/zephyr/tests/bsim/bluetooth/ll/conn/CMakeLists.txt
echo "## central_encrypted"; grep -n -i "encrypt\|security" /ws/zephyr/tests/bsim/bluetooth/ll/conn/src/test_connect*.c | head -30
