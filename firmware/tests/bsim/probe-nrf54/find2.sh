#!/bin/bash
cd /ws
ls zephyr/tests/bsim/bluetooth/host/security
echo "## samples after peripheral_hr"
ls zephyr/samples/bluetooth | sed -n '60,200p'
echo "## prj.conf and sample.yaml of peripheral_sc_only / peripheral_hr / central_hr"
for s in peripheral_sc_only peripheral_hr central_hr; do
  echo "--- $s"; ls zephyr/samples/bluetooth/$s
  echo "-- prj.conf"; sed 's/^/   /' zephyr/samples/bluetooth/$s/prj.conf
  echo "-- sample.yaml"; head -30 zephyr/samples/bluetooth/$s/sample.yaml
done
echo "## bsim tests naming nrf54 boards"
grep -rl "nrf54l15bsim\|nrf54lm20bsim" zephyr/tests/bsim 2>&1 | head -20
echo "## sdk-nrf samples/tests bluetooth"
ls nrf/samples/bluetooth | head -80
ls nrf/tests/bluetooth 2>&1 | head -30
