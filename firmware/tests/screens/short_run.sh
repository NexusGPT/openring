#!/bin/bash
# U9 short run: the screens suites alone (no broken copies) on both boards, with the pictures written and the manifest checked
# (the same commands as stage 3 of tools/build_all.sh). Runs in the container, firmware at /ws/firmware.
set -u
FW=/ws/firmware
OUT=/ws/out/$(date -u +%Y%m%d-%H%M%S)-u9-short
mkdir -p "$OUT/pictures/native_sim" "$OUT/pictures/nrf54lm20bsim_nrf54lm20a_cpuapp"
echo "OUT $OUT"
RC=0
env RING_PICS="$OUT/pictures/native_sim" west twister -T "$FW/tests/screens" -p native_sim -O "$OUT/twister-native_sim" -j 8 --inline-logs -v > "$OUT/tw-native_sim.log" 2>&1
echo "twister native_sim exit $?"; tail -12 "$OUT/tw-native_sim.log"
python3 "$FW/tools/pictures_manifest.py" "$(find "$OUT/twister-native_sim" -path '*tests/screens/ring_screens.all/handler.log' | head -1)" "$OUT/pictures/native_sim" "$OUT/pictures/manifest-native_sim.md" > "$OUT/pm-native_sim.log" 2>&1
echo "manifest native_sim exit $?"; tail -5 "$OUT/pm-native_sim.log"
env RING_PICS="$OUT/pictures/nrf54lm20bsim_nrf54lm20a_cpuapp" west twister -T "$FW/tests/screens" -p nrf54lm20bsim/nrf54lm20a/cpuapp -O "$OUT/twister-bsim" -j 8 --inline-logs -v > "$OUT/tw-bsim.log" 2>&1
echo "twister bsim exit $?"; tail -12 "$OUT/tw-bsim.log"
python3 "$FW/tools/pictures_manifest.py" "$(find "$OUT/twister-bsim" -path '*tests/screens/ring_screens.all/handler.log' | head -1)" "$OUT/pictures/nrf54lm20bsim_nrf54lm20a_cpuapp" "$OUT/pictures/manifest-bsim.md" > "$OUT/pm-bsim.log" 2>&1
echo "manifest bsim exit $?"; tail -5 "$OUT/pm-bsim.log"
echo "=== manifest native_sim"; cat "$OUT/pictures/manifest-native_sim.md"
echo "=== manifest bsim"; cat "$OUT/pictures/manifest-bsim.md"
echo "=== case lines native_sim"; grep -E " - (PASS|FAIL) - \[screens_(table|draw)\.test_(ilim|factory|start_during|sign_start_during)" "$OUT/pm-native_sim.log"
echo "=== case lines bsim"; grep -E " - (PASS|FAIL) - \[screens_(table|draw)\.test_(ilim|factory|start_during|sign_start_during)" "$OUT/pm-bsim.log"
echo "=== suite lines"; grep -hE "SUITE|SCREENS_TABLE|CROSSCHECK" "$OUT/pm-native_sim.log" "$OUT/pm-bsim.log"
