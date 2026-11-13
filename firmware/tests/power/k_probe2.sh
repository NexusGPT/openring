#!/bin/bash
# k_probe2.sh: K5/K6 follow-up, counts only (no kit source line is printed). Container, workspace /ws.
set -u
H=/ws/nrfxlib/nrf_fuel_gauge/include/nrf_fuel_gauge.h
S=/ws/nrf/samples/pmic/native/npm13xx_fuel_gauge/src/fuel_gauge.c
echo "## K6: lines of the library header that hold both words (counts)"
echo "negative+discharg $(grep -i 'negative' $H | grep -c -i 'discharg')"
echo "positive+discharg $(grep -i 'positive' $H | grep -c -i 'discharg')"
echo "negative+charg(not discharg) $(grep -i 'negative' $H | grep -i 'charg' | grep -c -v -i 'discharg')"
echo "positive+charg(not discharg) $(grep -i 'positive' $H | grep -i 'charg' | grep -c -v -i 'discharg')"
echo "## K6: the kit sample for the same chip family: where the current comes from and whether it is negated (counts)"
echo "sample lines with SENSOR_CHAN_GAUGE_AVG_CURRENT $(grep -c 'SENSOR_CHAN_GAUGE_AVG_CURRENT' $S)"
echo "sample lines with nrf_fuel_gauge_process $(grep -c 'nrf_fuel_gauge_process' $S)"
echo "sample lines with a minus sign directly before a name holding 'curr' $(grep -c -E '(^|[^A-Za-z0-9_])-[ ]*[A-Za-z_]*curr' $S)"
echo "sample lines with nrf_fuel_gauge_process and a minus sign inside the call $(grep 'nrf_fuel_gauge_process' $S | grep -c -E '\(.*-')"
echo "sample lines with 'negative' $(grep -c -i negative $S) with 'discharg' $(grep -c -i discharg $S) with 'sign' $(grep -c -i sign $S)"
echo "## K5: charger binding files, property-name counts (the names with hyphens, as the devicetree reads them)"
B=/ws/zephyr/dts/bindings
for pat in 'term-microvolt' 'current-microamp' 'term-current-percent' 'trickle-microvolt' 'vbus-limit-microamp' 'thermistor-ohms' 'thermistor-beta' 'dietemp-stop-millidegrees' 'dietemp-resume-millidegrees' 'charging-enable' 'thermistor-cold-millidegrees' 'term-warm-microvolt'; do
	echo "$pat in nordic,npm13xx-charger-common.yaml $(grep -c -- "$pat" $B/sensor/nordic,npm13xx-charger-common.yaml)"
done
for pat in 'soft-start-microamp' 'active-discharge' 'regulator-boot-off' 'regulator-initial-mode'; do
	echo "$pat in nordic,npm13xx-regulator-common.yaml $(grep -c -- "$pat" $B/regulator/nordic,npm13xx-regulator-common.yaml) in nordic,npm1304-regulator.yaml $(grep -c -- "$pat" $B/regulator/nordic,npm1304-regulator.yaml)"
done
echo "## K5: the call that writes a task register: names in the MFD header (counts)"
M=/ws/zephyr/include/zephyr/drivers/mfd/npm13xx.h
for pat in 'mfd_npm13xx_reg_write' 'mfd_npm13xx_reg_write2' 'mfd_npm13xx_reg_update' 'mfd_npm13xx_reg_read' 'mfd_npm13xx_add_callback' 'mfd_npm13xx_set_timer' 'mfd_npm13xx_hibernate' 'mfd_npm13xx_reset'; do
	echo "$pat $(grep -c -- "$pat" $M)"
done
echo "## K5: charger header names (counts)"
C=/ws/zephyr/include/zephyr/drivers/sensor/npm13xx_charger.h
for pat in 'SENSOR_CHAN_NPM13XX_CHARGER_STATUS' 'SENSOR_CHAN_NPM13XX_CHARGER_ERROR' 'SENSOR_CHAN_NPM13XX_CHARGER_VBUS_STATUS' 'SENSOR_ATTR_NPM13XX_CHARGER_CHARGING_ENABLE' 'SENSOR_ATTR_NPM13XX_CHARGER_CURRENT_LIMIT'; do
	echo "$pat $(grep -c -- "$pat" $C)"
done
