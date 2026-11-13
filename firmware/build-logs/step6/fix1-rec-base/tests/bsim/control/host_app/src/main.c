/*
 * Stand-in host of the two-device tests (BabbleSim, the simulated ring chip nrf54lm20bsim by default, with real encryption: see run.sh).
 *
 * A Bluetooth central with a HID host role (the SDK's HID over GATT client,
 * bt_hogp): it finds the ring by the HID service in the advertising data,
 * pairs with the passkey the ring displays (read from the file the ring
 * writes), discovers the HID service and subscribes to the input reports.
 * Everything it receives is recorded with its time and compared at the end
 * with expected reports written in this file. The expected values are
 * literals here, not read from the ring's headers, so a wrong key in the ring
 * fails the test.
 *
 * Environment: HOST_ID (1 or 2), RING_SCENARIO (A, B or C), RING_PASSFILE.
 * Output lines start with "HOST H<id>": CHECK <name> PASS|FAIL and one
 * "HOST H<id> RESULT PASS|FAIL" at the end. Times are simulated ms.
 */

#include <errno.h>
#include <stdlib.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/byteorder.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/hci.h>
#include <zephyr/bluetooth/uuid.h>
#include <bluetooth/gatt_dm.h>
#include <bluetooth/services/hogp.h>

#include "hosttools.h"

#define EVAL_MS 70000

static char name[4] = "H?";
static char scen;
static int host_id;
static int fails;
static int checks;

#define CHECK(label, cond)                                                                          \
	do {                                                                                        \
		bool ok_ = (cond);                                                                  \
		checks++;                                                                           \
		fails += ok_ ? 0 : 1;                                                               \
		printk("HOST %s CHECK %s %s (t=%lld)\n", name, label, ok_ ? "PASS" : "FAIL",        \
		       k_uptime_get());                                                             \
	} while (0)

/* ---- recorded reports ---- */

struct rec {
	int64_t t;
	uint8_t id;
	uint8_t len;
	uint8_t d[8];
};
static struct rec recs[128];
static int nrec;

/* ---- expected reports ---- */

struct xrep {
	uint8_t id;
	uint8_t len;
	uint8_t d[8];
};
struct xstep {
	const char *name;
	uint8_t n;        /* number of reports */
	struct xrep r[2];
	uint8_t rep_min;  /* > 0: r[0] repeats at least this many times (a held direction) */
	uint8_t rep_max;  /* with rep_min: and at most this many times */
};

/* consumer control: report id 2, 2 bytes, usage little endian; release is usage 0 */
#define CONS(nm, u) { nm, 2, { { 2, 2, { (u) & 0xFF, (u) >> 8 } }, { 2, 2, { 0, 0 } } }, 0, 0 }
/* keyboard: report id 1, 8 bytes; the key is byte 2; release is all zero */
#define KEY(nm, k) { nm, 2, { { 1, 8, { 0, 0, (k), 0, 0, 0, 0, 0 } }, { 1, 8, { 0 } } }, 0, 0 }
/* pointer: report id 3, 3 bytes: buttons, dx, dy */
#define MOVE(nm, dx, dy) { nm, 1, { { 3, 3, { 0, (uint8_t)(dx), (uint8_t)(dy) } } }, 0, 0 }
#define CLICK(nm) { nm, 2, { { 3, 3, { 1, 0, 0 } }, { 3, 3, { 0, 0, 0 } } }, 0, 0 }
#define NOKEY(nm) { nm, 0, { { 0 } }, 0, 0 }
#define HELD(nm, dx, dy, min, max) { nm, 1, { { 3, 3, { 0, (uint8_t)(dx), (uint8_t)(dy) } } }, (min), (max) }

/* Test A: the four modes in the order the ring injects them. */
static const struct xstep steps_a[] = {
	CONS("media.centre play/pause", 0x00CD),
	CONS("media.up volume up", 0x00E9),
	CONS("media.down volume down", 0x00EA),
	CONS("media.left previous", 0x00B6),
	CONS("media.right next", 0x00B5),
	NOKEY("presenter.centre nothing"),
	KEY("presenter.up previous slide (Left Arrow)", 0x50),
	KEY("presenter.down next slide (Right Arrow)", 0x4F),
	KEY("presenter.left previous slide (Left Arrow)", 0x50),
	KEY("presenter.right next slide (Right Arrow)", 0x4F),
	NOKEY("presenter pages.centre nothing"),
	KEY("presenter pages.up (Page Up)", 0x4B),
	KEY("presenter pages.down (Page Down)", 0x4E),
	KEY("presenter pages.left (Page Up)", 0x4B),
	KEY("presenter pages.right (Page Down)", 0x4E),
	CLICK("pointer.centre click"),
	MOVE("pointer.up", 0, -16),
	MOVE("pointer.down", 0, 16),
	MOVE("pointer.left", -16, 0),
	MOVE("pointer.right", 16, 0),
	KEY("agent.centre Return", 0x28),
	KEY("agent.up Up Arrow", 0x52),
	KEY("agent.down Down Arrow", 0x51),
	KEY("agent.left Escape", 0x29),
	KEY("agent.right Return", 0x28),
	HELD("pointer held right", 16, 0, 4, 8),
	/* screen off and the double press send nothing: nothing is expected for them */
	KEY("after a drop and reconnect: agent.centre Return", 0x28),
};

/* Test B: host 1 gets phases 1 and 3, host 2 gets phases 2 and 4. */
static const struct xstep steps_b1[] = {
	CONS("P1 media.centre", 0x00CD),
	CONS("P1 media.right", 0x00B5),
	CONS("P2a media.centre (host 2 has paired; host 1 is still the active device)", 0x00CD),
	CONS("P2a media.left", 0x00B6),
	CONS("P3 media.up (after the switch back)", 0x00E9),
	CONS("P3 media.down", 0x00EA),
};
static const struct xstep steps_b2[] = {
	CONS("P2 media.centre", 0x00CD),
	CONS("P2 media.left", 0x00B6),
	CONS("P4 media.right (after the second switch)", 0x00B5),
};

/* Test D: only the retried release shows: every recording gesture and host write was silent. */
static const struct xstep steps_d1[] = {
	KEY("failed release sent later: agent.centre Return", 0x28),
};

/* Test F: host 1 gets one key before its drop and one after host 2 tried to pair. */
static const struct xstep steps_f1[] = {
	CONS("before the drop media.centre", 0x00CD),
	CONS("after host 2 tried media.centre", 0x00CD),
};

/* Test G: three devices; each host gets only its own keys. */
static const struct xstep steps_g1[] = {
	CONS("G host 1: media.centre", 0x00CD),
	CONS("G host 1: media.up (after the switch to it)", 0x00E9),
};
static const struct xstep steps_g2[] = {
	CONS("G host 2: media.left", 0x00B6),
	CONS("G host 2: media.down (after the switch to it)", 0x00EA),
};
static const struct xstep steps_g3[] = {
	CONS("G host 3: media.right", 0x00B5),
	CONS("G host 3: media.centre (after the switch to it)", 0x00CD),
	CONS("G host 3: media.up (after the fourth host tried)", 0x00E9),
};

/* Trial T: both hosts are linked at the same time; each gets only its own keys. */
static const struct xstep steps_t1[] = {
	CONS("T host 1: media.centre", 0x00CD),
	CONS("T host 1: media.down", 0x00EA),
};
static const struct xstep steps_t2[] = {
	CONS("T host 2: media.right", 0x00B5),
	CONS("T host 2: media.up", 0x00E9),
};

/* Test C: one key before the removal, one after the new pairing. */
static const struct xstep steps_c1[] = {
	CONS("before removal media.centre", 0x00CD),
	CONS("after new pairing media.centre", 0x00CD),
};

static bool rec_matches(const struct rec *r, const struct xrep *x)
{
	return r->id == x->id && r->len == x->len && memcmp(r->d, x->d, x->len) == 0;
}

static void evaluate(const struct xstep *steps, size_t nsteps)
{
	int pos = 0;

	for (size_t i = 0; i < nsteps; i++) {
		const struct xstep *s = &steps[i];
		bool ok = true;

		if (s->rep_min > 0) {
			int cnt = 0;

			while (pos < nrec && rec_matches(&recs[pos], &s->r[0])) {
				pos++;
				cnt++;
			}
			printk("HOST %s INFO %s: %d reports\n", name, s->name, cnt);
			{
				char nm[96];

				snprintk(nm, sizeof(nm), "%s repeats (at least %d reports)", s->name, s->rep_min);
				CHECK(nm, cnt >= s->rep_min);
				snprintk(nm, sizeof(nm), "%s repeats (at most %d reports)", s->name, s->rep_max);
				CHECK(nm, cnt <= s->rep_max);
			}
			continue;
		} else {
			for (int k = 0; k < s->n; k++) {
				ok = ok && (pos + k < nrec) && rec_matches(&recs[pos + k], &s->r[k]);
			}
			pos += s->n;
		}
		CHECK(s->name, ok);
	}
	CHECK("no other report received", pos == nrec);
	printk("HOST %s INFO %d report(s) received in total\n", name, nrec);
}

/* ---- Bluetooth ---- */

static struct bt_conn *conn;
static struct bt_hogp hogp;
static bool bonded;
static bt_addr_le_t bond_addr;
static bool scan_hold;           /* scenario C: wait before reconnecting */
static int64_t hold_until;
static bool stale_refused;
static int pairings;
static int64_t link_t0;        /* when the current link opened */
static int64_t max_link_ms;   /* the longest link that ended */
static int attempts;          /* links that opened */
static int64_t resume_at;     /* scenario F: host 1 stays away until then */
static bool connecting;
static struct k_work_delayable scan_work;
static struct k_work ready_work;

static void scan_start(void);

static uint8_t notify_cb(struct bt_hogp *h, struct bt_hogp_rep_info *rep, uint8_t err, const uint8_t *data)
{
	ARG_UNUSED(h);
	if (data == NULL) {
		return BT_GATT_ITER_CONTINUE;
	}
	if (err == 0 && nrec < (int)ARRAY_SIZE(recs)) {
		struct rec *r = &recs[nrec++];
		uint8_t sz = bt_hogp_rep_size(rep);

		r->t = k_uptime_get();
		r->id = bt_hogp_rep_id(rep);
		r->len = sz > sizeof(r->d) ? sizeof(r->d) : sz;
		memcpy(r->d, data, r->len);
		printk("HOST %s REPORT t=%lld id=%u len=%u data=", name, r->t, r->id, r->len);
		for (int i = 0; i < r->len; i++) {
			printk("%02x", r->d[i]);
		}
		printk("\n");
	}
	return BT_GATT_ITER_CONTINUE;
}

static void ready_fn(struct k_work *w)
{
	struct bt_hogp_rep_info *rep = NULL;
	int subs = 0;

	ARG_UNUSED(w);
	while ((rep = bt_hogp_rep_next(&hogp, rep)) != NULL) {
		if (bt_hogp_rep_type(rep) == BT_HIDS_REPORT_TYPE_INPUT) {
			int err = bt_hogp_rep_subscribe(&hogp, rep, notify_cb);

			if (err == 0) {
				subs++;
			} else {
				printk("HOST %s subscribe error %d\n", name, err);
			}
		}
	}
	printk("HOST %s INFO subscribed to %d input reports (t=%lld)\n", name, subs, k_uptime_get());
}

static void hogp_ready(struct bt_hogp *h)
{
	ARG_UNUSED(h);
	k_work_submit(&ready_work);
}

static void hogp_prep_error(struct bt_hogp *h, int err)
{
	ARG_UNUSED(h);
	printk("HOST %s HID client preparation failed %d\n", name, err);
}

static void hogp_pm(struct bt_hogp *h)
{
	ARG_UNUSED(h);
}

static const struct bt_hogp_init_params hogp_params = {
	.ready_cb = hogp_ready,
	.prep_error_cb = hogp_prep_error,
	.pm_update_cb = hogp_pm,
};

static void dm_done(struct bt_gatt_dm *dm, void *ctx)
{
	int err = bt_hogp_handles_assign(dm, &hogp);

	ARG_UNUSED(ctx);
	if (err != 0) {
		printk("HOST %s HID handles not assigned %d\n", name, err);
	}
	(void)bt_gatt_dm_data_release(dm);
}

static void dm_missing(struct bt_conn *c, void *ctx)
{
	ARG_UNUSED(c);
	ARG_UNUSED(ctx);
	printk("HOST %s HID service not found\n", name);
}

static void dm_error(struct bt_conn *c, int err, void *ctx)
{
	ARG_UNUSED(c);
	ARG_UNUSED(ctx);
	printk("HOST %s discovery failed %d\n", name, err);
}

static const struct bt_gatt_dm_cb dm_cb = {
	.completed = dm_done,
	.service_not_found = dm_missing,
	.error_found = dm_error,
};

static void on_connected(struct bt_conn *c, uint8_t err)
{
	connecting = false;
	if (err != 0) {
		printk("HOST %s connect failed 0x%02x\n", name, err);
		if (conn != NULL) {
			bt_conn_unref(conn);
			conn = NULL;
		}
		k_work_reschedule(&scan_work, K_MSEC(300));
		return;
	}
	attempts++;
	link_t0 = k_uptime_get();
	printk("HOST %s connected (t=%lld), bonded=%d\n", name, k_uptime_get(), bonded);
	(void)bt_conn_set_security(c, BT_SECURITY_L4);
}

static void on_disconnected(struct bt_conn *c, uint8_t reason)
{
	printk("HOST %s disconnected reason 0x%02x (t=%lld)\n", name, reason, k_uptime_get());
	if (link_t0 > 0 && k_uptime_get() - link_t0 > max_link_ms) {
		max_link_ms = k_uptime_get() - link_t0;
	}
	(void)k_work_cancel(&ready_work);
	if (bt_hogp_assign_check(&hogp)) {
		bt_hogp_release(&hogp);
	}
	if (conn != NULL) {
		bt_conn_unref(conn);
		conn = NULL;
	}
	k_work_reschedule(&scan_work, K_MSEC(300));
}

static void on_security(struct bt_conn *c, bt_security_t level, enum bt_security_err err)
{
	if (err == 0) {
		printk("HOST %s security level %u (t=%lld)\n", name, level, k_uptime_get());
		CHECK("link encrypted and authenticated (security level 4)", level == BT_SECURITY_L4);
		(void)bt_gatt_dm_start(c, BT_UUID_HIDS, &dm_cb, NULL);
		return;
	}
	printk("HOST %s security failed err %d %s (t=%lld)\n", name, err, bt_security_err_to_str(err), k_uptime_get());
	if (bonded && err == BT_SECURITY_ERR_PIN_OR_KEY_MISSING) {
		/* the ring has deleted the pairing: our stored keys no longer work */
		stale_refused = true;
		scan_hold = true;
		hold_until = k_uptime_get() + 10000;
		CHECK("old keys refused by the ring after removal (pin or key missing)", true);
	}
	(void)bt_conn_disconnect(c, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
}

BT_CONN_CB_DEFINE(host_conn_cb) = {
	.connected = on_connected,
	.disconnected = on_disconnected,
	.security_changed = on_security,
};

static void on_passkey_entry(struct bt_conn *c)
{
	char buf[16] = { 0 };
	char *path = nsi_host_getenv("RING_PASSFILE");
	unsigned int pk = 0;
	bool got = false;

	for (int tries = 0; tries < 50 && path != NULL && !got; tries++) {
		int fd = nsi_host_open(path, HT_O_RDONLY);

		if (fd >= 0) {
			long n = nsi_host_read(fd, buf, sizeof(buf) - 1);

			(void)nsi_host_close(fd);
			if (n >= 6) {
				pk = (unsigned int)strtoul(buf, NULL, 10);
				got = true;
			}
		}
		if (!got) {
			k_sleep(K_MSEC(20));
		}
	}
	printk("HOST %s passkey entry asked, read %s (t=%lld)\n", name, got ? "ok" : "nothing", k_uptime_get());
	CHECK("passkey read from the ring's display", got);
	if (got) {
		(void)bt_conn_auth_passkey_entry(c, pk);
	}
}

static void on_auth_cancel(struct bt_conn *c)
{
	ARG_UNUSED(c);
	printk("HOST %s pairing cancelled\n", name);
}

static struct bt_conn_auth_cb auth_cb = {
	.passkey_entry = on_passkey_entry,
	.cancel = on_auth_cancel,
};

static void on_pairing_complete(struct bt_conn *c, bool b)
{
	pairings++;
	if (b) {
		bond_addr = *bt_conn_get_dst(c);
		bonded = true;
	}
	CHECK("pairing with the passkey completed and bonded", b);
}

static void on_pairing_failed(struct bt_conn *c, enum bt_security_err reason)
{
	ARG_UNUSED(c);
	printk("HOST %s pairing failed %d %s (t=%lld)\n", name, reason, bt_security_err_to_str(reason), k_uptime_get());
	if (!((scen == 'F' && host_id == 2) || (scen == 'G' && host_id == 4))) { /* host 2 of test F is meant to be refused */
		CHECK("pairing with the passkey completed and bonded", false);
	}
}

static struct bt_conn_auth_info_cb info_cb = {
	.pairing_complete = on_pairing_complete,
	.pairing_failed = on_pairing_failed,
};

/* ---- scanning ---- */

struct adv_info {
	bool hid;
};

static bool ad_parse(struct bt_data *d, void *user)
{
	struct adv_info *ai = user;

	if (d->type == BT_DATA_UUID16_ALL || d->type == BT_DATA_UUID16_SOME) {
		for (int i = 0; i + 2 <= d->data_len; i += 2) {
			if (sys_get_le16(&d->data[i]) == BT_UUID_HIDS_VAL) {
				ai->hid = true;
			}
		}
	}
	return true;
}

static void scan_cb(const bt_addr_le_t *addr, int8_t rssi, uint8_t type, struct net_buf_simple *ad)
{
	struct adv_info ai = { false };
	int err;

	ARG_UNUSED(rssi);
	if (conn != NULL || connecting || type != BT_GAP_ADV_TYPE_ADV_IND) {
		return;
	}
	if (k_uptime_get() < resume_at) {
		return; /* this host stays away for now */
	}
	bt_data_parse(ad, ad_parse, &ai);
	if (!ai.hid) {
		return;
	}
	if (bonded && !bt_addr_le_eq(addr, &bond_addr)) {
		return; /* a bonded host talks only to the identity it paired with */
	}
	connecting = true;
	(void)bt_le_scan_stop();
	err = bt_conn_le_create(addr, BT_CONN_LE_CREATE_CONN, BT_LE_CONN_PARAM_DEFAULT, &conn);
	if (err != 0) {
		printk("HOST %s connect create failed %d\n", name, err);
		connecting = false;
		k_work_reschedule(&scan_work, K_MSEC(300));
	}
}

static void scan_start(void)
{
	struct bt_le_scan_param sp = {
		.type = BT_LE_SCAN_TYPE_PASSIVE,
		.options = BT_LE_SCAN_OPT_NONE,
		.interval = 0x0020,
		.window = 0x0020,
	};
	int err = bt_le_scan_start(&sp, scan_cb);

	if (err != 0 && err != -EALREADY) {
		printk("HOST %s scan start failed %d\n", name, err);
	}
}

static void scan_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	if (conn != NULL || connecting) {
		return;
	}
	if (k_uptime_get() < resume_at) {
		k_work_reschedule(&scan_work, K_MSEC(500));
		return;
	}
	if (scan_hold) {
		if (k_uptime_get() < hold_until) {
			k_work_reschedule(&scan_work, K_MSEC(500));
			return;
		}
		/* scenario C: drop the old keys and pair again */
		if (bonded) {
			int err = bt_unpair(BT_ID_DEFAULT, &bond_addr);

			printk("HOST %s drops the old keys (%d) and will pair again (t=%lld)\n", name, err,
			       k_uptime_get());
			bonded = false;
		}
		scan_hold = false;
	}
	scan_start();
}

int main(void)
{
	char *e = nsi_host_getenv("HOST_ID");
	char *s = nsi_host_getenv("RING_SCENARIO");
	int err;
	int64_t start_ms;
	int64_t eval_ms;

	host_id = e != NULL ? atoi(e) : 1;
	scen = s != NULL ? s[0] : '?';
	snprintk(name, sizeof(name), "H%d", host_id);
	printk("HOST %s START scenario %c\n", name, scen);

	k_work_init_delayable(&scan_work, scan_fn);
	k_work_init(&ready_work, ready_fn);
	bt_hogp_init(&hogp, &hogp_params);
	(void)bt_conn_auth_cb_register(&auth_cb);
	(void)bt_conn_auth_info_cb_register(&info_cb);
	err = bt_enable(NULL);
	CHECK("Bluetooth up", err == 0);
	if (err != 0) {
		printk("HOST %s RESULT FAIL\n", name);
		return 0;
	}

	/* host 2 of test B starts at 25 s, after the first pairing; the others at once */
	start_ms = ((scen == 'B' || scen == 'T' || scen == 'G') && host_id == 2) ? 25000 : (scen == 'G' && host_id == 3) ? 50000 : (scen == 'G' && host_id == 4) ? 103000 : (scen == 'F' && host_id == 2) ? 14000 : 500;
	if (k_uptime_get() < start_ms) {
		k_sleep(K_MSEC(start_ms - k_uptime_get()));
	}
	scan_start();

	if (scen == 'A') {
		/* test A: end the link at 40 s (a drop); the host reconnects by itself */
		k_sleep(K_MSEC(40000 - k_uptime_get()));
		if (conn != NULL) {
			printk("HOST %s ends the link (a drop) (t=%lld)\n", name, k_uptime_get());
			(void)bt_conn_disconnect(conn, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
		}
	}
	if (scen == 'F' && host_id == 1) {
		/* test F: end the link at 12 s and stay away until 32 s, so the ring advertises to a bonded
		 * device that is not there, with the pairing window closed */
		k_sleep(K_MSEC(12000 - k_uptime_get()));
		resume_at = 32000;
		if (conn != NULL) {
			printk("HOST %s ends the link and stays away (t=%lld)\n", name, k_uptime_get());
			(void)bt_conn_disconnect(conn, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
		}
	}
	if (scen == 'G' && (host_id == 1 || host_id == 2)) {
		/* test G: after the switches, hosts 1 and 2 stay away from 90 s to 140 s, so that only host 4
		 * is there to try the fourth pairing */
		k_sleep(K_MSEC(90000 - k_uptime_get()));
		resume_at = 140000;
	}
	if (scen == 'G' && host_id == 3) {
		/* test G: end the link at 102 s and stay away until 122 s: the ring advertises with the pairing
		 * window closed while host 4 tries to pair */
		k_sleep(K_MSEC(102000 - k_uptime_get()));
		resume_at = 122000;
		if (conn != NULL) {
			printk("HOST %s ends the link and stays away (t=%lld)\n", name, k_uptime_get());
			(void)bt_conn_disconnect(conn, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
		}
	}
	if (scen == 'D') {
		/* test D: write to the ring at 45 s: HID control point (suspend, exit suspend) and
		 * the protocol mode. Nothing a host writes may start or stop a recording. */
		k_sleep(K_MSEC(45000 - k_uptime_get()));
		if (bt_hogp_ready_check(&hogp)) {
			int e1 = bt_hogp_suspend(&hogp);
			int e2 = bt_hogp_exit_suspend(&hogp);
			int e3 = bt_hogp_pm_write(&hogp, BT_HIDS_PM_REPORT);

			printk("HOST %s INFO host writes sent: suspend %d, exit suspend %d, protocol mode %d (t=%lld)\n",
			       name, e1, e2, e3, k_uptime_get());
			CHECK("host writes were sent", e1 == 0 && e2 == 0);
		} else {
			CHECK("host writes were sent", false);
		}
	}
	/* B pairs a second device and switches (round 2: the first device stays active until the wearer chooses Use) */
	eval_ms = (scen == 'G') ? 150000 : (scen == 'B') ? 125000 : EVAL_MS;
	k_sleep(K_MSEC(eval_ms - k_uptime_get()));
	printk("HOST %s EVAL t=%lld\n", name, k_uptime_get());
	switch (scen) {
	case 'A':
		evaluate(steps_a, ARRAY_SIZE(steps_a));
		break;
	case 'B':
		if (host_id == 1) {
			evaluate(steps_b1, ARRAY_SIZE(steps_b1));
		} else {
			evaluate(steps_b2, ARRAY_SIZE(steps_b2));
		}
		break;
	case 'C':
		CHECK("old keys were refused after the removal", stale_refused);
		CHECK("paired twice (before the removal and again)", pairings == 2);
		evaluate(steps_c1, ARRAY_SIZE(steps_c1));
		break;
	case 'T':
		if (host_id == 1) {
			evaluate(steps_t1, ARRAY_SIZE(steps_t1));
		} else {
			evaluate(steps_t2, ARRAY_SIZE(steps_t2));
		}
		break;
	case 'G':
		if (host_id == 1) {
			evaluate(steps_g1, ARRAY_SIZE(steps_g1));
		} else if (host_id == 2) {
			evaluate(steps_g2, ARRAY_SIZE(steps_g2));
		} else if (host_id == 3) {
			evaluate(steps_g3, ARRAY_SIZE(steps_g3));
		} else {
			CHECK("host 4 tried to pair", attempts >= 1);
			CHECK("pairing over a fourth slot is refused", pairings == 0 && !bonded);
			CHECK("host 4: no stranger link lasts longer than 1 s", max_link_ms <= 1000);
			printk("HOST %s INFO longest link %lld ms\n", name, max_link_ms);
			evaluate(NULL, 0);
		}
		break;
	case 'D':
		evaluate(steps_d1, ARRAY_SIZE(steps_d1));
		break;
	case 'F':
		if (host_id == 1) {
			evaluate(steps_f1, ARRAY_SIZE(steps_f1));
		} else {
			CHECK("host 2 tried to pair outside the window", attempts >= 1);
			CHECK("pairing outside the window is refused", pairings == 0 && !bonded);
			CHECK("no stranger link lasts longer than 1 s", max_link_ms <= 1000);
			printk("HOST %s INFO longest link %lld ms\n", name, max_link_ms);
			evaluate(NULL, 0);
		}
		break;
	default:
		CHECK("known scenario", false);
	}
	printk("HOST %s RESULT %s checks=%d fails=%d\n", name, fails == 0 ? "PASS" : "FAIL", checks, fails);
	while (1) {
		k_sleep(K_SECONDS(1));
	}
	return 0;
}
