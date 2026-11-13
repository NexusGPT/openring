#!/bin/bash
# k_probe.sh: kit facts K5 and K6 of step6-plan.md section 8, answered by file-name listings and counts only
# (no kit source line is printed). Runs in the ring-os-toolchain container; the workspace is /ws.
set -u
echo "## K5: files named npm13 (names only)"
find /ws/zephyr/dts/bindings /ws/zephyr/drivers /ws/zephyr/include /ws/zephyr/samples /ws/zephyr/tests -iname '*npm13*' 2>&1 | sed 's#^/ws/##' | sort | head -80
echo "## K5: counts of names in the kit's nPM13xx charger files (grep -c, number of matching lines)"
CH=/ws/zephyr/drivers/sensor/nordic/npm13xx_charger
ls "$CH" 2>&1
for f in "$CH"/*.c; do
	b=$(basename "$f")
	for pat in 'npm1304' 'SENSOR_CHAN_GAUGE_VOLTAGE' 'SENSOR_CHAN_GAUGE_AVG_CURRENT' 'SENSOR_CHAN_GAUGE_TEMP' 'SENSOR_CHAN_DIE_TEMP' 'CHARGER_STATUS' 'CHARGER_ERROR' 'SENSOR_ATTR_CONFIGURATION' 'VBUS_STATUS'; do
		echo "$b $pat $(grep -c -- "$pat" "$f")"
	done
done
echo "## K5: regulator driver counts"
R=/ws/zephyr/drivers/regulator/regulator_npm13xx.c
for pat in 'npm1304' 'soft-start' 'soft_start' 'active-discharge' 'active_discharge' 'NPM13XX_LDSW'; do
	echo "regulator_npm13xx.c $pat $(grep -c -- "$pat" $R)"
done
echo "## K5: mfd driver files (names)"
ls /ws/zephyr/drivers/mfd | grep -i npm
echo "## K5: mfd counts"
for pat in 'npm1304' 'mfd_npm13xx_reg_write' 'mfd_npm13xx_reg_read' 'mfd_npm13xx_reg_update' 'mfd_npm13xx_add_callback'; do
	echo "$pat in mfd_npm13xx.c $(grep -c -- "$pat" /ws/zephyr/drivers/mfd/mfd_npm13xx.c), in include/zephyr/drivers/mfd/npm13xx.h $(grep -c -- "$pat" /ws/zephyr/include/zephyr/drivers/mfd/npm13xx.h)"
done
echo "## K5: emulator files of the chip in the kit (names)"
find /ws/zephyr -ipath '*emul*' -iname '*npm13*' 2>&1 | sed 's#^/ws/##'
echo "## K5: binding files that name npm1304 (names)"
grep -l -r 'npm1304' /ws/zephyr/dts/bindings | sed 's#^/ws/##' | sort
echo "## K6: fuel gauge library, file names"
FG=/ws/nrfxlib/nrf_fuel_gauge
find "$FG" -maxdepth 3 | sed 's#^/ws/##' | sort | head -60
echo "## K6: name counts in the library header"
for pat in 'nrf_fuel_gauge_init' 'nrf_fuel_gauge_process' 'nrf_fuel_gauge_tte_get' 'nrf_fuel_gauge_ttf_get' 'nrf_fuel_gauge_ext_state_update' 'nrf_fuel_gauge_param_set' 'nrf_fuel_gauge_battery_model'; do
	echo "$pat $(grep -c -- "$pat" $FG/include/nrf_fuel_gauge.h)"
done
echo "## K6: header word counts about the current sign (counts only)"
for pat in 'discharg' 'negative' 'positive' 'charging'; do
	echo "$pat $(grep -c -i -- "$pat" $FG/include/nrf_fuel_gauge.h)"
done
echo "## K6: kit modules that use the library (file names)"
grep -l -r 'nrf_fuel_gauge_process' /ws/nrf/samples /ws/nrf/subsys /ws/nrf/include 2>&1 | sed 's#^/ws/##' | sort | head -20
