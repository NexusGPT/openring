Z=/ws/zephyr
echo "== ls /ws"; ls /ws
echo "== native_sim boards dir"; ls $Z/boards/native/native_sim
echo "== count of udc and uhc words in native_sim.dts"; grep -c -i 'udc' $Z/boards/native/native_sim/native_sim.dts; grep -c -i 'uhc' $Z/boards/native/native_sim/native_sim.dts; grep -c -i 'zephyr_udc0' $Z/boards/native/native_sim/native_sim.dts
echo "== usb bindings with virtual in the name"; ls $Z/dts/bindings/usb | grep -i virtual
echo "== usb bindings (file names with udc or uhc)"; ls $Z/dts/bindings/usb | grep -i -E 'udc|uhc'
echo "== tests/subsys/usb"; ls $Z/tests/subsys/usb
echo "== tests/subsys/usb/device_next"; ls $Z/tests/subsys/usb/device_next
echo "== subsys/usb/device_next/class"; ls $Z/subsys/usb/device_next/class
echo "== drivers/usb/udc virtual"; ls $Z/drivers/usb/udc | grep -i virt
echo "== drivers/usb/uhc virtual"; ls $Z/drivers/usb/uhc | grep -i virt
echo "== samples with virtual host"; ls $Z/samples/subsys/usb 2>&1 | head -30
echo "== K4 counts in usbd.h"
for n in USBD_DEFINE_CLASS usbd_add_configuration usbd_bus_speed usbd_enable usbd_disable usbd_init usbd_msg_register_cb usbd_ep_enqueue usbd_register_class USBD_SPEED_FS USBD_SPEED_HS; do printf '%s %s\n' $n $(grep -c "$n" $Z/include/zephyr/usb/usbd.h); done
echo "== K4 counts in usbd_msg.h"
for n in USBD_MSG_VBUS_READY USBD_MSG_VBUS_REMOVED USBD_MSG_CONFIGURATION USBD_MSG_SUSPEND USBD_MSG_RESUME USBD_MSG_RESET; do printf '%s %s\n' $n $(grep -c "$n" $Z/include/zephyr/usb/usbd_msg.h); done
echo "== loopback class"; ls $Z/subsys/usb/device_next/class | grep -i loop; grep -c 'usbd_bus_speed' $Z/subsys/usb/device_next/class/usbd_loopback.c
echo "== samples using device_next with virtual host (file names)"; grep -l -r 'uhc_virtual\|uhc-virtual' $Z/samples $Z/tests 2>&1 | head
echo "== usbd_bus_speed in loopback"; grep -l -r 'usbd_bus_speed' $Z/subsys/usb/device_next/class
