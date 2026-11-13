#!/bin/bash
# read-only search of the SDK for stock encrypted-link tests and samples
cd /ws
echo "## zephyr tests/bsim bluetooth host security"
ls zephyr/tests/bsim/bluetooth/host/security 2>&1
ls zephyr/tests/bsim/bluetooth/host/security/* 2>&1 | head -60
echo "## nrf tests/bsim"
ls nrf/tests/bsim 2>&1; ls nrf/tests/bsim/bluetooth 2>&1
echo "## bsim built bins"
ls /ws/tools/bsim/bin 2>&1 | head -30
echo "## zephyr samples bluetooth"
ls zephyr/samples/bluetooth | head -60
echo "## ncs version"; cat nrf/VERSION 2>&1
