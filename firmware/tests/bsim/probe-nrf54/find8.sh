#!/bin/bash
F=/ws/modules/bsim_hw_models/nrf_hw_models/src/HW_models/BLECrypt_if.c
echo "## BLECrypt_if.c 95-180"; sed -n 95,180p $F
echo "## default of the option"; grep -n "bt_encryption\|real_enc\|fake\|Fake" $F | head -40
echo "## who uses it in nRF54 CCM"; grep -rln "BLECrypt_if" /ws/modules/bsim_hw_models/nrf_hw_models/src | head
