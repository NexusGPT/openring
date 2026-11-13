Z=/ws/zephyr; D=$Z/include/zephyr/audio/dmic.h; C=$Z/include/zephyr/drivers/clock_control/nrf_clock_control.h; P=$Z/include/zephyr/drivers/pinctrl.h; N=$Z/drivers/audio/dmic_nrfx_pdm.c; K=$Z/drivers/clock_control/clock_control_nrf.c
cnt() { echo "count $(basename $1) '$2' = $(grep -c -- "$2" $1)"; }
cnt $D "struct dmic_driver_api"; cnt $D "__subsystem"
cnt $P PINCTRL_DT_DEFINE; cnt $P PINCTRL_DT_DEV_CONFIG_GET; cnt $P PINCTRL_DT_DEV_CONFIG_DECLARE
cnt $C NRF54L; cnt $K NRF54L; cnt $K "nrf_clock_control_request"; cnt $K "z_nrf_clock_control_get_onoff"
echo "files in $Z/drivers/clock_control with 54L in name or text: $(grep -l -i 'nrf54l' $Z/drivers/clock_control/*.c $Z/drivers/clock_control/Kconfig.nrf | wc -l)"
cnt $Z/drivers/clock_control/Kconfig.nrf "NRF54L"
cnt $N "PM_DEVICE"; cnt $N "pm_device"; cnt $N "pinctrl"
echo "pdm20 node in the simulated chip's devicetree files: $(grep -rl 'pdm20' $Z/../nrf/boards 2>&1 | wc -l)"
echo "pdm20 in dts include nrf54lm20a: $(grep -rl 'pdm20' /ws/zephyr/dts/vendor/nordic 2>&1 | grep -c 54lm20)"
