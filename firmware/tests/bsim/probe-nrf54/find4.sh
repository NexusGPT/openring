#!/bin/bash
cd /ws/zephyr/tests/bsim/bluetooth/host/security/security_changed_callback
echo "## listing"; ls -R . | head -30
echo "## prj.conf"; cat prj.conf
echo "## testcase.yaml"; cat testcase.yaml
echo "## test_scripts"; for f in test_scripts/*; do echo "--- $f"; cat $f; done
echo "## src"; wc -l src/*; cat src/main.c
echo "## nrf54l15 tests file"
cat /ws/zephyr/tests/bsim/bluetooth/tests.nrf54l15bsim_nrf54l15_cpuapp.txt
