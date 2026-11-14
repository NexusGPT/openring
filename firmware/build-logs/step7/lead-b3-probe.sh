#!/bin/bash
# Lead's probe for review bar B3: plant faults the review could not run, and see what check_ring_pins.py says.
set -u
FW=/ws/firmware; OUT=/ws/out/lead-b3; B=ringrec/nrf54lm20a/cpuapp; NL="$FW/boards/ringrec/netlist.csv"
rm -rf "$OUT"; mkdir -p "$OUT"
conf() {  # name root
	west build -p always --cmake-only -b "$B" --no-sysbuild -d "$OUT/$1" "$FW/app" -- -DBOARD_ROOT="$2" > "$OUT/$1.log" 2>&1
}
case_() {  # name file old new
	local root="$OUT/root-$1"; mkdir -p "$root"; cp -r "$FW/boards" "$root/boards"
	python3 - "$root/boards/ringrec/$2" "$3" "$4" <<'PY' || { echo "CASE $1: planted text not found"; return; }
import sys
p, old, new = sys.argv[1:4]
s = open(p).read()
if old not in s: sys.exit(1)
open(p, "w").write(s.replace(old, new, 1))
PY
	if ! conf "$1" "$root"; then echo "CASE $1: did not configure: $(grep -m2 -i 'error' "$OUT/$1.log" | tr '\n' ' ' | cut -c1-200)"; return; fi
	python3 "$FW/tools/check_ring_pins.py" "$OUT/$1/zephyr/zephyr.dts" "$NL" > "$OUT/$1-check.log" 2>&1; rc=$?
	echo "CASE $1: check exit $rc: $(grep -E '^(DIFFERENT|NO NODE|UNEXPECTED|UNLISTED) ' "$OUT/$1-check.log" | tr '\n' '|' | cut -c1-300) $(grep RESULT "$OUT/$1-check.log" | cut -c1-200)"
}
if conf base "$FW"; then
	python3 "$FW/tools/check_ring_pins.py" "$OUT/base/zephyr/zephyr.dts" "$NL" > "$OUT/base-check.log" 2>&1; echo "CASE base: check exit $?: $(grep RESULT "$OUT/base-check.log" | cut -c1-200)"
else echo "CASE base: did not configure"; exit 1; fi
case_ wrong-port ringrec_nrf54lm20a_cpuapp.dts 'gpios = <&gpio3 1 GPIO_ACTIVE_HIGH>;' 'gpios = <&gpio2 1 GPIO_ACTIVE_HIGH>;'
case_ disabled-node ringrec_nrf54lm20a_cpuapp.dts 'label = "MOTOR, enable of the motor regulator U11";' 'label = "MOTOR, enable of the motor regulator U11"; status = "disabled";'
case_ extra-pin ringrec_nrf54lm20a_cpuapp.dts 'spare-p3-04-gpios = <&gpio3 4 0>;' 'spare-p3-04-gpios = <&gpio3 4 0>, <&gpio3 6 0>;'
case_ wrong-flag ringrec_nrf54lm20a_cpuapp.dts 'gpios = <&gpio0 6 (GPIO_PULL_UP | GPIO_ACTIVE_LOW)>;' 'gpios = <&gpio0 6 GPIO_ACTIVE_HIGH>;'
sed 's/^MOTOR,U1,F6,P3.01,/MOTOR,U1,F6,P3.02,/' "$NL" > "$OUT/netlist-changed.csv"
python3 "$FW/tools/check_ring_pins.py" "$OUT/base/zephyr/zephyr.dts" "$OUT/netlist-changed.csv" > "$OUT/changed-netlist-check.log" 2>&1; rc=$?
echo "CASE changed-netlist: check exit $rc: $(grep -E '^(DIFFERENT|NO NODE|UNEXPECTED|UNLISTED) ' "$OUT/changed-netlist-check.log" | tr '\n' '|' | cut -c1-300) $(grep RESULT "$OUT/changed-netlist-check.log" | cut -c1-200)"
rm -rf "$OUT"
echo "PROBE END"
