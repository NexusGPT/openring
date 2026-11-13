/*
 * Trial (plan: "two devices at the same time ... is tried in step 2 and kept only if the
 * simulation holds"). Ring side, BabbleSim.
 *
 * Two hosts pair in turn on two local identities (0 and 1) and stay connected together
 * (CONFIG_BT_MAX_CONN=2). After both are linked and subscribed the ring sends a key to each, then
 * two more keys; each host must receive exactly its own keys. The product's ring_devices keeps
 * one link (its plan disconnects the other), so this app does not use rdev_init(); it uses the
 * HID service of ring_control and the test hook rctl_test_send_to().
 */

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/hci.h>
#include <zephyr/bluetooth/uuid.h>

#include <ring_control/rctl.h>
#include "hosttools.h"

static struct bt_conn *links[2];
static int fails;
static int checks;

#define CHECK(name, cond)                                                                          \
	do {                                                                                       \
		bool ok_ = (cond);                                                                 \
		checks++;                                                                          \
		fails += ok_ ? 0 : 1;                                                              \
		printk("RING CHECK %s %s (t=%lld)\n", name, ok_ ? "PASS" : "FAIL", k_uptime_get()); \
	} while (0)

static const struct bt_data ad[] = {
	BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
	BT_DATA_BYTES(BT_DATA_UUID16_ALL, BT_UUID_16_ENCODE(BT_UUID_HIDS_VAL)),
};

static struct k_work adv_work;

static void adv_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	for (int id = 0; id < 2; id++) {
		if (links[id] == NULL) {
			struct bt_le_adv_param p = BT_LE_ADV_PARAM_INIT(BT_LE_ADV_OPT_CONN, 160, 160, NULL);
			int err;

			p.id = (uint8_t)id;
			err = bt_le_adv_start(&p, ad, ARRAY_SIZE(ad), NULL, 0);
			printk("RING advertising on identity %d: %d\n", id, err);
			return;
		}
	}
}

static void on_connected(struct bt_conn *conn, uint8_t err)
{
	struct bt_conn_info info;

	if (err != 0 || bt_conn_get_info(conn, &info) != 0 || info.id > 1) {
		return;
	}
	links[info.id] = bt_conn_ref(conn);
	printk("RING link %u up (t=%lld)\n", info.id, k_uptime_get());
	k_work_submit(&adv_work); /* advertise on the other identity while this link stays */
}

static void on_disconnected(struct bt_conn *conn, uint8_t reason)
{
	for (int i = 0; i < 2; i++) {
		if (links[i] == conn) {
			bt_conn_unref(conn);
			links[i] = NULL;
			printk("RING link %d down, reason 0x%02x\n", i, reason);
		}
	}
}

BT_CONN_CB_DEFINE(trial_conn_cb) = {
	.connected = on_connected,
	.disconnected = on_disconnected,
};

static void on_passkey(struct bt_conn *conn, unsigned int passkey)
{
	char buf[16];
	char *path = nsi_host_getenv("RING_PASSFILE");
	int n = snprintk(buf, sizeof(buf), "%06u\n", passkey);

	ARG_UNUSED(conn);
	if (path != NULL) {
		int fd = nsi_host_open(path, HT_O_WRONLY | HT_O_TRUNC);

		if (fd >= 0) {
			(void)nsi_host_write(fd, buf, (unsigned long)n);
			(void)nsi_host_close(fd);
		}
	}
	printk("RING PASSKEY %06u\n", passkey);
}

static void on_cancel(struct bt_conn *conn)
{
	ARG_UNUSED(conn);
}

static struct bt_conn_auth_cb auth_cb = {
	.passkey_display = on_passkey,
	.cancel = on_cancel,
};

int main(void)
{
	int err;
	int r0, r1;

	printk("RING START scenario T (two devices at the same time)\n");
	k_work_init(&adv_work, adv_fn);
	CHECK("HID service registered", rctl_init() == 0);
	(void)bt_conn_auth_cb_register(&auth_cb);
	err = bt_enable(NULL);
	CHECK("Bluetooth up", err == 0);
	CHECK("identity 1 created", bt_id_create(NULL, NULL) == 1);
	k_work_submit(&adv_work);

	k_sleep(K_MSEC(45000));
	CHECK("both hosts are linked at the same time", links[0] != NULL && links[1] != NULL);
	rctl_set_mode(RCTL_MEDIA);
	if (links[0] != NULL && links[1] != NULL) {
		r0 = rctl_test_send_to(links[0], RCTL_CENTRE);
		r1 = rctl_test_send_to(links[1], RCTL_RIGHT);
		CHECK("key to host 1 sent", r0 == 2);
		CHECK("key to host 2 sent", r1 == 2);
		k_sleep(K_MSEC(1000));
		r1 = rctl_test_send_to(links[1], RCTL_UP);
		r0 = rctl_test_send_to(links[0], RCTL_DOWN);
		CHECK("second key to host 2 sent", r1 == 2);
		CHECK("second key to host 1 sent", r0 == 2);
	}
	printk("RING SCRIPT DONE t=%lld checks=%d fails=%d\n", k_uptime_get(), checks, fails);
	printk("RING RESULT %s\n", fails == 0 ? "PASS" : "FAIL");
	while (1) {
		k_sleep(K_SECONDS(1));
	}
	return 0;
}
