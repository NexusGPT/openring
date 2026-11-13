Z=/ws/zephyr
cnt() { printf '%s %s\n' "$2" "$(grep -c -w "$2" "$1" 2>&1)"; }
echo "== usbd.h names (counts of lines holding the word)"
for n in USBD_DEVICE_DEFINE USBD_DESC_LANG_DEFINE USBD_DESC_MANUFACTURER_DEFINE USBD_DESC_PRODUCT_DEFINE USBD_DESC_CONFIG_DEFINE USBD_CONFIGURATION_DEFINE usbd_add_descriptor usbd_register_class usbd_register_all_classes usbd_msg_register_cb usbd_init usbd_enable usbd_disable usbd_shutdown usbd_ep_enqueue usbd_ep_buf_alloc usbd_ep_dequeue usbd_device_set_code_triple usbd_device_set_bcd_usb usbd_bus_speed USBD_DEFINE_CLASS usbd_class_get_private usbd_class_api USBD_DESC_SERIAL_NUMBER_DEFINE usbd_caps_speed usbd_class_get_ctx; do cnt $Z/include/zephyr/usb/usbd.h $n; done
echo "== udc_buf.h"; ls $Z/include/zephyr/drivers/usb | head -20
for n in udc_get_buf_info udc_buf_info; do cnt $Z/include/zephyr/drivers/usb/udc_buf.h $n; done
echo "== usbh.h names"
for n in USBH_CONTROLLER_DEFINE usbh_init usbh_enable usbh_disable usbh_shutdown usbh_xfer_alloc usbh_xfer_buf_alloc usbh_xfer_enqueue usbh_xfer_free usbh_xfer_buf_free usbh_req_desc_dev usbh_req_set_cfg usbh_req_desc_cfg usbh_device_alloc usbh_dev_by_addr usbh_bulk_transfer usbh_xfer_buf_add usbh_req_setup struct_usbh_context usbh_device_get; do cnt $Z/include/zephyr/usb/usbh.h $n; done
echo "== host private headers (file names with class and device)"; ls $Z/subsys/usb/host | grep -E 'class|device|host'
echo "== USBH_DEFINE_CLASS location (file names)"; grep -l -w USBH_DEFINE_CLASS $Z/subsys/usb/host/*.h $Z/include/zephyr/usb/*.h 2>&1
echo "== usbh_class_api file"; grep -l 'usbh_class_api' $Z/subsys/usb/host/*.h $Z/include/zephyr/usb/*.h 2>&1
echo "== uhc include names"; ls $Z/include/zephyr/drivers/usb
echo "== device_next test main.c count of words"
M=$Z/tests/subsys/usb/device_next/src/main.c
for n in USBH_CONTROLLER_DEFINE USBH_DEFINE_CLASS usbh_init usbh_enable usbh_xfer_alloc usbh_xfer_enqueue usbh_req_desc_dev usbh_dev_by_addr usbh_class_api uhc_xfer_alloc usbd_init usbd_enable USBD_DEVICE_DEFINE; do cnt $M $n; done
echo "== host test CMake include names (word counts)"; for n in subsys/usb/host include_directories; do printf '%s %s\n' $n $(grep -c "$n" $Z/tests/subsys/usb/host/CMakeLists.txt $Z/tests/subsys/usb/device_next/CMakeLists.txt | tr '\n' ' '); done
