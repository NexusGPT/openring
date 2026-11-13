# U8 kit fact K13: counts and file names only (no kit lines printed). Run on the server with
#   RING_REMOTE_SRC=/root/ring-os/src-u-factory sh firmware/tools/remote.sh u8-k13 "bash tests/factory/kfacts.sh"
Z=/ws/zephyr
B=$Z/include/zephyr/bluetooth
echo "== K13 names in the Bluetooth headers (count of lines mentioning each name; 0 = absent)"
for n in bt_le_adv_start bt_le_adv_stop bt_le_ext_adv_create bt_le_ext_adv_start bt_le_ext_adv_stop BT_LE_ADV_OPT_CONN BT_LE_ADV_PARAM_INIT BT_LE_ADV_OPT_USE_TX_POWER BT_LE_ADV_OPT_EXT_ADV BT_LE_ADV_OPT_USE_NAME BT_DATA_NAME_COMPLETE; do
  echo "bluetooth.h/gap.h $n $(cat $B/bluetooth.h $B/gap.h | grep -c "$n")"
done
echo "gap.h BT_GAP_ADV_TYPE_ADV_NONCONN_IND $(grep -c BT_GAP_ADV_TYPE_ADV_NONCONN_IND $B/gap.h)"
echo "bluetooth.h bt_le_scan_start $(grep -c bt_le_scan_start $B/bluetooth.h)"
echo "== K13 Kconfig names (count of 'config <name>' lines in the Bluetooth Kconfig files; list of files)"
for n in BT_EXT_ADV BT_EXT_ADV_MAX_ADV_SET BT_CTLR_TX_PWR_0 BT_CTLR_TX_PWR_DYNAMIC_CONTROL BT_CTLR_ADV_EXT BT_CTLR_ADV_SET BT_LL_SW_SPLIT BT_LL_SOFTDEVICE BT_HCI_VS BT_CTLR_TX_PWR_ANTENNA; do
  echo "$n declared in $(grep -rl "^config $n\$" $Z/subsys/bluetooth $Z/drivers/bluetooth 2>&1 | wc -l) files"
done
echo "== K13 HCI vendor commands for the TX power (hci_vs.h; sdc_hci_vs.h of the controller library)"
echo "hci_vs.h BT_HCI_OP_VS_WRITE_TX_POWER $(grep -c BT_HCI_OP_VS_WRITE_TX_POWER $B/hci_vs.h)"
echo "hci_vs.h BT_HCI_VS_LL_HANDLE_TYPE_ADV $(grep -c BT_HCI_VS_LL_HANDLE_TYPE_ADV $B/hci_vs.h)"
echo "sdc_hci_vs.h files named: $(find /ws -name sdc_hci_vs.h 2>&1 | wc -l)"
echo "== K13 which controller the simulated chip board builds (count of mentions)"
echo "nrf54lm20bsim files naming BT_LL_SW_SPLIT: $(grep -rl BT_LL_SW_SPLIT $Z/boards/native/nrf_bsim 2>&1 | wc -l)"
echo "nrf54lm20bsim files naming BT_CTLR: $(grep -rl BT_CTLR $Z/boards/native/nrf_bsim 2>&1 | wc -l)"
echo "== K13 how the ring's devices part advertises now (project file, counts)"
D=/ws/firmware/modules/ring_devices/src/rdev.c
echo "rdev.c bt_le_adv_start calls: $(grep -c bt_le_adv_start $D)"
echo "rdev.c bt_le_ext_adv calls: $(grep -c bt_le_ext_adv $D)"
echo "== K13 HWINFO device id on the simulated chip: names"
echo "hwinfo.h hwinfo_get_device_id $(grep -c hwinfo_get_device_id $Z/include/zephyr/drivers/hwinfo.h)"
echo "hwinfo drivers for nrf: $(ls $Z/drivers/hwinfo 2>&1 | grep -c nrf)"
