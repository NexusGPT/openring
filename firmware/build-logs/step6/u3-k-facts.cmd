Z=/ws/zephyr; D=$Z/include/zephyr/audio/dmic.h; C=$Z/include/zephyr/drivers/clock_control/nrf_clock_control.h; P=$Z/include/zephyr/drivers/pinctrl.h; M=$Z/include/zephyr/pm/device.h; N=$Z/drivers/audio/dmic_nrfx_pdm.c
for f in $D $C $P $M $N; do if [ -f $f ]; then echo "exists $f"; else echo "MISSING $f"; fi; done
cnt() { echo "count $(basename $1) '$2' = $(grep -c -- "$2" $1)"; }
for s in dmic_configure dmic_trigger DMIC_TRIGGER_START DMIC_TRIGGER_STOP dmic_read "struct dmic_cfg" dmic_build_channel_map DEVICE_API; do cnt $D "$s"; done
for s in onoff nrf_clock_control_request nrf_clock_control_release z_nrf_clock_control_get_onoff NRF_CLOCK_CONTROL_SPEC_INIT CLOCK_CONTROL_NRF_TYPE_HFCLK; do cnt $C "$s"; done
echo "clock_control files with nrf in name:"; ls $Z/drivers/clock_control | grep -i nrf
echo "files in drivers/clock_control naming hfxo or hf: $(grep -l -i 'hfxo' $Z/drivers/clock_control/*.c | wc -l)"
for s in pinctrl_apply_state PINCTRL_STATE_SLEEP PINCTRL_STATE_DEFAULT; do cnt $P "$s"; done
for s in pm_device_action_run PM_DEVICE_ACTION_SUSPEND pm_device_runtime_get; do cnt $M "$s"; done
for s in PM_DEVICE_ACTION_SUSPEND PM_DEVICE_ACTION_RESUME pm_device_driver_init PM_DEVICE_DT_INST_DEFINE pinctrl_apply_state PINCTRL_STATE_SLEEP PINCTRL_STATE_DEFAULT; do cnt $N "$s"; done
