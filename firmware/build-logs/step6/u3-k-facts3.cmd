Z=/ws/zephyr; K=$Z/drivers/clock_control
echo "files naming nrf54l in drivers/clock_control:"; grep -l -i 'nrf54l' $K/*.c $K/Kconfig.nrf
echo "files in drivers/clock_control that define nrf_clock_control_request or the onoff getter: $(grep -l 'z_nrf_clock_control_get_onoff' $K/*.c | tr '\n' ' ')"
for f in $(grep -l -i 'nrf54l' $K/*.c); do echo "$(basename $f): z_nrf_clock_control_get_onoff=$(grep -c z_nrf_clock_control_get_onoff $f) HFCLK=$(grep -c HFCLK $f) TYPE_HFCLK=$(grep -c CLOCK_CONTROL_NRF_TYPE_HFCLK $f)"; done
echo "nrf_clock_control.h: TYPE_HFCLK enum member count $(grep -c 'CLOCK_CONTROL_NRF_TYPE_HFCLK' $Z/include/zephyr/drivers/clock_control/nrf_clock_control.h), nrf_clock_control_request lines $(grep -c 'nrf_clock_control_request' $Z/include/zephyr/drivers/clock_control/nrf_clock_control.h)"
echo "dmic.h lines with 'api' (count): $(grep -c -i 'api' $Z/include/zephyr/audio/dmic.h)"
