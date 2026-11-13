#!/bin/bash
echo "## test_connect1.c 225-300"; sed -n 225,300p /ws/zephyr/tests/bsim/bluetooth/ll/conn/src/test_connect1.c
echo "## RealEncryption in hw models and zephyr (read only)"
grep -rn "RealEncryption\|real_encryption\|RealEnc" /ws/tools/bsim/components/ext_nRF54L_hw_models /ws/modules/bsim_hw_models /ws/zephyr/boards/native 2>&1 | head -40
ls /ws/modules/bsim_hw_models 2>&1
