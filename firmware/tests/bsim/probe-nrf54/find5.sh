#!/bin/bash
cd /ws/zephyr/tests/bsim/bluetooth/ll/conn
ls -R . | head -40
echo "## prj_split.conf"; cat prj_split.conf
echo "## prj.conf"; cat prj.conf
echo "## script"; cat tests_scripts/basic_conn_encrypted_split.sh
echo "## testcase.yaml"; cat testcase.yaml 2>&1
echo "## compile.source"; cat /ws/zephyr/tests/bsim/compile.source
echo "## grep encrypt in src"; grep -n -i "encrypt\|security\|pair\|set_security" src/main.c | head -40
echo "## env"; env | grep -i "bsim\|ZEPHYR\|BOARD"
echo "## west boards ok?"; ls /ws/zephyr/boards/native/nrf_bsim
