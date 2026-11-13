#!/bin/bash
cd /ws
echo "## compile.nrf54l15bsim script"
cat zephyr/tests/bsim/bluetooth/compile.nrf54l15bsim_nrf54l15_cpuapp.sh
echo "## ci.bt.sh grep nrf54"
grep -n "nrf54\|nrf52_bsim\|BOARD" zephyr/tests/bsim/ci.bt.sh | head -30
echo "## nrf/tests/bluetooth/bsim"
find nrf/tests/bluetooth/bsim -maxdepth 3 | head -60
echo "## zephyr/tests/bsim/bluetooth/host/security/*/testcase.yaml platforms"
grep -rn "platform_allow\|nrf" zephyr/tests/bsim/bluetooth/host/security/*/testcase.yaml | head -30
echo "## zephyr tests/bsim/bluetooth/host (dirs)"
ls zephyr/tests/bsim/bluetooth/host
ls zephyr/tests/bsim/bluetooth/host/smp 2>&1
