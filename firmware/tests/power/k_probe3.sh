#!/bin/bash
# k_probe3.sh: K5/K6 follow-up 2, counts only (no kit source line is printed). Container, workspace /ws.
set -u
S=/ws/nrf/samples/pmic/native/npm13xx_fuel_gauge/src/fuel_gauge.c
D=/ws/zephyr/drivers/sensor/nordic/npm13xx_charger/npm13xx_charger.c
echo "## K6: kit sample, unary minus applied to a current value after '=', '(' or ',' (count)"
echo "sample unary-minus-curr $(grep -c -E '[=(,][ ]*-[ ]*[A-Za-z_]*curr' $S)"
echo "sample unary-minus-curr or on the sensor current variable (any spelling) $(grep -c -E '[=(,][ ]*-[ ]*[A-Za-z_]*(curr|ibat|_i)' $S)"
echo "## K6: kit charger driver, negation of the battery current channel (count of lines with '= -' near ibat/current)"
echo "driver lines with ibat $(grep -c -i 'ibat' $D)"
echo "driver lines with ibat and a unary minus after = $(grep -i 'ibat' $D | grep -c -E '=[ ]*-')"
echo "driver lines with 'discharg' $(grep -c -i 'discharg' $D) with 'negative' $(grep -c -i 'negative' $D)"
echo "## K5: charger bindings holding the settings of FW 8.1 (counts per file)"
B=/ws/zephyr/dts/bindings/sensor
for f in nordic,npm13xx-charger-common.yaml nordic,npm1304-charger.yaml; do
	for pat in 'term-microvolt' 'current-microamp' 'term-current-percent' 'term-warm-microvolt' 'thermistor-cool-millidegrees' 'thermistor-warm-millidegrees' 'thermistor-hot-millidegrees'; do
		echo "$pat in $f $(grep -c -- "$pat" $B/$f)"
	done
done
echo "## K5: binding files that hold current-microamp (names)"
grep -l -r 'current-microamp' /ws/zephyr/dts/bindings | sed 's#^/ws/##' | sort | head
echo "## K5: does the binding of the nPM1304 charger name the property 'charging-enable' in the 1304 file"
echo "$(grep -c -- 'charging-enable' $B/nordic,npm1304-charger.yaml)"
