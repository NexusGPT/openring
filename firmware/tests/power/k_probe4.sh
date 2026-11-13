#!/bin/bash
# k_probe4.sh: the kit names the real file (rpw_hw_real.c) uses, counted (no kit source line is printed).
# Container, workspace /ws. A count of 0 means the name is not in that file.
set -u
M=/ws/zephyr/include/zephyr/drivers/mfd/npm13xx.h
S=/ws/zephyr/include/zephyr/drivers/sensor.h
R=/ws/zephyr/include/zephyr/drivers/regulator.h
FG=/ws/nrfxlib/nrf_fuel_gauge/include/nrf_fuel_gauge.h
c() { echo "$1 in $(basename "$2"): $(grep -c -- "$1" "$2")"; }
for n in mfd_npm13xx_reg_read mfd_npm13xx_reg_write mfd_npm13xx_add_callback NPM13XX_EVENT_VBUS_DETECTED NPM13XX_EVENT_VBUS_REMOVED NPM13XX_EVENT_CHG_ERROR NPM13XX_EVENT_CHG_COMPLETED NPM13XX_EVENT_SHIPHOLD_PRESS; do c $n $M; done
for n in SENSOR_CHAN_GAUGE_VOLTAGE SENSOR_CHAN_GAUGE_AVG_CURRENT SENSOR_CHAN_GAUGE_TEMP SENSOR_CHAN_DIE_TEMP sensor_sample_fetch sensor_channel_get; do c $n $S; done
for n in regulator_enable regulator_disable regulator_is_enabled; do c $n $R; done
for n in nrf_fuel_gauge_init nrf_fuel_gauge_process nrf_fuel_gauge_tte_get nrf_fuel_gauge_ttf_get 'struct nrf_fuel_gauge_init_parameters' 'struct battery_model' 'v0;' 'i0;' 't0;' 'model;'; do c "$n" $FG; done
echo "battery model headers under include/battery_models (names):"
find /ws/nrfxlib/nrf_fuel_gauge/include/battery_models -type f | sed 's#^/ws/##' | sort | head
echo "events enum members of the nPM13xx MFD header (counts of 'NPM13XX_EVENT_' lines): $(grep -c 'NPM13XX_EVENT_' $M)"
