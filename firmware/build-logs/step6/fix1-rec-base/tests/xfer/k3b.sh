Z=/ws/zephyr
echo "== overlay of tests/subsys/usb/device_next for native_sim: counts"
O=$Z/tests/subsys/usb/device_next/boards/native_sim.overlay
for n in 'zephyr,udc-virtual' 'zephyr,uhc-virtual' 'zephyr,uvb' ; do printf '%s %s\n' "$n" $(grep -c "$n" $O); done
echo "== file names in tests/subsys/usb/device_next/src"; ls $Z/tests/subsys/usb/device_next/src
echo "== file names in tests/subsys/usb/host and its boards"; ls $Z/tests/subsys/usb/host $Z/tests/subsys/usb/host/boards $Z/tests/subsys/usb/host/src
echo "== subsys/usb names"; ls $Z/subsys/usb; ls $Z/subsys/usb/uvb $Z/subsys/usb/host
echo "== include/zephyr/usb names"; ls $Z/include/zephyr/usb
echo "== counts in the device_next test source of uhc and usbh calls"
for f in $Z/tests/subsys/usb/device_next/src/*.c; do printf '%s uhc:%s usbh:%s\n' $(basename $f) $(grep -c 'uhc_' $f) $(grep -c 'usbh_' $f); done
echo "== Kconfig names with UVB"; grep -l 'config UVB' $Z/subsys/usb/uvb/Kconfig $Z/drivers/usb/uhc/Kconfig.virtual $Z/drivers/usb/udc/Kconfig.virtual 2>&1
echo "== prj.conf option names of that test (names only, no values)"; grep -o 'CONFIG_[A-Z0-9_]*' $Z/tests/subsys/usb/device_next/prj.conf $Z/tests/subsys/usb/device_next/boards/native_sim.conf 2>&1 | sort -u
echo "== host test prj.conf option names"; grep -o 'CONFIG_[A-Z0-9_]*' $Z/tests/subsys/usb/host/prj.conf | sort -u
