Z=/ws/zephyr
echo "== symbols defined in drivers/usb/udc/Kconfig.virtual"; grep -o '^config [A-Z0-9_]*' $Z/drivers/usb/udc/Kconfig.virtual
echo "== count of DT_HAS_ZEPHYR_UDC_VIRTUAL_ENABLED in Kconfig.virtual"; grep -c 'DT_HAS_ZEPHYR_UDC_VIRTUAL_ENABLED' $Z/drivers/usb/udc/Kconfig.virtual
echo "== symbols in drivers/usb/udc/Kconfig"; grep -o '^\(menuconfig\|config\) [A-Z0-9_]*' $Z/drivers/usb/udc/Kconfig | head -40
echo "== zephyr_udc0 in native_sim.dts: count of status lines near it"; grep -c 'status' $Z/boards/native/native_sim/native_sim.dts
