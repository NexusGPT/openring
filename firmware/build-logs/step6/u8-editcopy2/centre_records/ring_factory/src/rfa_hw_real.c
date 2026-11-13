/*
 * rfa_hw_real.c: the real beacon of the factory unit (software step 6, unit U8): not-connectable advertising through the
 * Bluetooth host, registered with ring_rhw as the beacon instance. Development kit build only (CONFIG_RING_RHW_SIM off,
 * CONFIG_BT on): NOT PROVEN on the real chip. tests/bsim/factory runs it on the simulated chip against a scanner.
 *
 * Kit fact K13 (docs/factory-notes.md): bt_le_adv_start() with no connectable option and no scan data gives a
 * not-connectable, not-scannable advertiser (ADV_NONCONN_IND); the interval is in 0.625 ms units; the host has one legacy
 * advertiser at a time, and the devices part does not advertise in FACTORY_TEST (FW l.765), so no second advertising set
 * is used here: a start while another advertiser runs answers -EALREADY and the factory request fails. The TX power
 * is the controller's setting (CONFIG_BT_CTLR_TX_PWR_0 gives 0 dBm): any other value is refused (-ENOTSUP).
 * "FW l.N" = line N of design/firmware.md.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/init.h>
#include <zephyr/kernel.h>

#include <ring_rhw/rhw.h>

#define NAME_MAX_BYTES 29

static int real_start(const char *name, uint16_t interval_ms, int8_t tx_dbm, bool connectable)
{
	size_t len;
	uint32_t units;
	struct bt_data ad[1];
	struct bt_le_adv_param prm;
	int err;

	if (name == NULL) {
		return -EINVAL;
	}
	len = strlen(name);
	if (len == 0 || len > NAME_MAX_BYTES || interval_ms == 0) {
		return -EINVAL;
	}
	if (tx_dbm != 0) {
		return -ENOTSUP; /* 0 dBm is the controller's Kconfig setting (FW l.1031, l.1057) */
	}
	units = ((uint32_t)interval_ms * 8u) / 5u; /* 0.625 ms units */
	ad[0].type = BT_DATA_NAME_COMPLETE;
	ad[0].data_len = (uint8_t)len;
	ad[0].data = (const uint8_t *)name;
	memset(&prm, 0, sizeof(prm));
	prm.id = BT_ID_DEFAULT;
	prm.options = connectable ? BT_LE_ADV_OPT_CONN : BT_LE_ADV_OPT_NONE;
	prm.interval_min = (uint16_t)units;
	prm.interval_max = (uint16_t)units;
	(void)bt_le_adv_stop(); /* "A running beacon is replaced" (rhw.h) */
	err = bt_le_adv_start(&prm, ad, ARRAY_SIZE(ad), NULL, 0);
	return err;
}

static int real_stop(void)
{
	int err = bt_le_adv_stop();

	return err == -EALREADY ? 0 : err; /* "no error when none runs" (rhw.h) */
}

static const struct rhw_beacon_api real_api = {
	.start = real_start,
	.stop = real_stop,
};

static int rfa_real_register(void)
{
	return rhw_register_beacon(&real_api);
}

SYS_INIT(rfa_real_register, APPLICATION, 90);
