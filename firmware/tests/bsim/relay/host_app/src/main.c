/*
 * Stand-in helper of the relay test (BabbleSim, the simulated ring chip nrf54lm20bsim, real encryption: see run.sh).
 *
 * The stand-in is the GATT client the Android helper app will be. It is written for this project and shares no constant with the code
 * under test: the UUIDs, the opcodes, the codes and the record layout below are written out from design/firmware.md section 7.7.
 *
 *   H  finds the ring by the HID service in its advertising data (the ring advertises while its pairing window is open), finds the relay
 *      service BEFORE the link is secure and tries to write, subscribe and read (all three must fail), pairs with the passkey the ring shows,
 *      reads Info, subscribes to Out, and then plays the helper: HELLO, notifications in pieces of 11 bytes (20-byte frames, the smallest ATT
 *      payload), a replace, actions arriving as ACTION frames, REMOVE, frames during RECORDING, 21 malformed frames, a record left
 *      unfinished, a dropped link, the reconnect with a new HELLO and the rebuilt notifications (with frames of 244 bytes)
 *   I  the stand-in is an iPhone: it serves a reduced Notification Center Service (the real UUIDs and data formats), the ring finds it, and
 *      the stand-in also writes relay frames, which must all be refused with code 7
 *
 * It hands stage numbers to the ring through files (HELPER_SYNC written here, RING_SYNC written by the ring).
 *
 * Output lines: "HELPER CHECK <name> PASS|FAIL" and one "HELPER RESULT PASS|FAIL". Times are simulated ms.
 * Environment: RING_SCENARIO (H or I), RING_PASSFILE, RING_SYNC, HELPER_SYNC.
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

#include "hosttools.h"

static char scen;
static int fails;
static int checks;

#define CHECK(label, cond)                                                                            \
	do {                                                                                          \
		bool ok_ = (cond);                                                                    \
		checks++;                                                                             \
		fails += ok_ ? 0 : 1;                                                                 \
		printk("HELPER CHECK %s %s (t=%lld)\n", label, ok_ ? "PASS" : "FAIL", k_uptime_get()); \
	} while (0)

/* A wait for the other program's stage is not a check: it is printed as "HELPER WAIT", it is not counted in the checks, and a wait that times
 * out fails the run. */
#define WAIT(label, cond)                                                                             \
	do {                                                                                          \
		bool ok_ = (cond);                                                                    \
		fails += ok_ ? 0 : 1;                                                                 \
		printk("HELPER WAIT %s %s (t=%lld)\n", label, ok_ ? "PASS" : "FAIL", k_uptime_get()); \
	} while (0)

/* ======================================================================== files shared with the ring */

static void write_file(const char *env, const char *text, int n)
{
	char *path = nsi_host_getenv(env);

	if (path != NULL) {
		int fd = nsi_host_open(path, HT_O_WRONLY | HT_O_TRUNC);

		if (fd >= 0) {
			(void)nsi_host_write(fd, text, (unsigned long)n);
			(void)nsi_host_close(fd);
		}
	}
}

static int read_stage(const char *env)
{
	char buf[16] = { 0 };
	char *path = nsi_host_getenv(env);
	int fd, v = -1;

	if (path == NULL) {
		return -1;
	}
	fd = nsi_host_open(path, HT_O_RDONLY);
	if (fd >= 0) {
		long n = nsi_host_read(fd, buf, sizeof(buf) - 1);

		(void)nsi_host_close(fd);
		if (n >= 2 && buf[n - 1] == '\n') {
			v = atoi(buf);
		}
	}
	return v;
}

static int ring_seen;

static void helper_stage(int n)
{
	char buf[16];
	int len = snprintk(buf, sizeof(buf), "%d\n", n);

	write_file("HELPER_SYNC", buf, len);
	printk("HELPER INFO stage %d (t=%lld)\n", n, k_uptime_get());
}

static bool wait_ring(int n, int64_t timeout_ms)
{
	int64_t end = k_uptime_get() + timeout_ms;

	while (k_uptime_get() < end) {
		int v = read_stage("RING_SYNC");

		if (v > ring_seen) {
			ring_seen = v;
		}
		if (ring_seen >= n) {
			printk("HELPER INFO ring stage %d seen (t=%lld)\n", n, k_uptime_get());
			return true;
		}
		k_sleep(K_MSEC(20));
	}
	return ring_seen >= n;
}

/* ======================================================================== the relay service, as the design says */

static struct bt_uuid_128 u_relay = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0xa3c20000, 0x5b7e, 0x4f2a, 0x9c1d, 0x7e2b6f4d8a90));
static struct bt_uuid_128 u_in = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0xa3c20001, 0x5b7e, 0x4f2a, 0x9c1d, 0x7e2b6f4d8a90));
static struct bt_uuid_128 u_out = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0xa3c20002, 0x5b7e, 0x4f2a, 0x9c1d, 0x7e2b6f4d8a90));
static struct bt_uuid_128 u_info = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0xa3c20003, 0x5b7e, 0x4f2a, 0x9c1d, 0x7e2b6f4d8a90));

static uint16_t h_in, h_out, h_out_ccc, h_info;

/* ======================================================================== the connection */

static struct bt_conn *conn;
static bool connecting;
static bool bonded;
static bt_addr_le_t bond_addr;
static int pairings;
static K_SEM_DEFINE(conn_sem, 0, 1);
static K_SEM_DEFINE(disc_sem, 0, 1);
static K_SEM_DEFINE(sec_sem, 0, 1);
static K_SEM_DEFINE(op_sem, 0, 1);
static K_SEM_DEFINE(dm_sem, 0, 1);
static K_SEM_DEFINE(mtu_sem, 0, 1);
static int sec_err;
static bt_security_t sec_level;
static int dm_res;
static struct k_work_delayable scan_work;

static void scan_start(void);

static void on_connected(struct bt_conn *c, uint8_t err)
{
	connecting = false;
	if (err != 0) {
		printk("HELPER connect failed 0x%02x\n", err);
		if (conn != NULL) {
			bt_conn_unref(conn);
			conn = NULL;
		}
		k_work_reschedule(&scan_work, K_MSEC(300));
		return;
	}
	printk("HELPER connected (t=%lld), bonded=%d\n", k_uptime_get(), bonded);
	ARG_UNUSED(c);
	k_sem_give(&conn_sem);
}

static void on_disconnected(struct bt_conn *c, uint8_t reason)
{
	ARG_UNUSED(c);
	printk("HELPER disconnected reason 0x%02x (t=%lld)\n", reason, k_uptime_get());
	if (conn != NULL) {
		bt_conn_unref(conn);
		conn = NULL;
	}
	k_sem_give(&disc_sem);
	k_work_reschedule(&scan_work, K_MSEC(300));
}

static void on_security(struct bt_conn *c, bt_security_t level, enum bt_security_err err)
{
	ARG_UNUSED(c);
	sec_err = (int)err;
	sec_level = level;
	printk("HELPER security level %u err %d (t=%lld)\n", level, (int)err, k_uptime_get());
	k_sem_give(&sec_sem);
}

BT_CONN_CB_DEFINE(helper_conn_cb) = {
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
	CHECK("passkey read from the ring's display", got);
	if (got) {
		(void)bt_conn_auth_passkey_entry(c, pk);
	}
}

static void on_auth_cancel(struct bt_conn *c)
{
	ARG_UNUSED(c);
	printk("HELPER pairing cancelled\n");
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
	printk("HELPER pairing failed %d\n", reason);
	CHECK("pairing with the passkey completed and bonded", false);
}

static struct bt_conn_auth_info_cb info_cb = {
	.pairing_complete = on_pairing_complete,
	.pairing_failed = on_pairing_failed,
};

static bool ad_parse(struct bt_data *d, void *user)
{
	bool *hid = user;

	if (d->type == BT_DATA_UUID16_ALL || d->type == BT_DATA_UUID16_SOME) {
		for (int i = 0; i + 2 <= d->data_len; i += 2) {
			if (sys_get_le16(&d->data[i]) == BT_UUID_HIDS_VAL) {
				*hid = true;
			}
		}
	}
	return true;
}

static void scan_cb(const bt_addr_le_t *addr, int8_t rssi, uint8_t type, struct net_buf_simple *ad)
{
	bool hid = false;

	ARG_UNUSED(rssi);
	if (conn != NULL || connecting || type != BT_GAP_ADV_TYPE_ADV_IND) {
		return;
	}
	bt_data_parse(ad, ad_parse, &hid);
	if (!hid || (bonded && !bt_addr_le_eq(addr, &bond_addr))) {
		return;
	}
	connecting = true;
	(void)bt_le_scan_stop();
	if (bt_conn_le_create(addr, BT_CONN_LE_CREATE_CONN, BT_LE_CONN_PARAM_DEFAULT, &conn) != 0) {
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
		printk("HELPER scan start failed %d\n", err);
	}
}

static void scan_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	if (conn != NULL || connecting) {
		return;
	}
	scan_start();
}

static bool wait_connected(int64_t ms)
{
	return k_sem_take(&conn_sem, K_MSEC(ms)) == 0 && conn != NULL;
}

/* raise the security to level 4; the passkey (first time) or the stored key (bonded) */
static bool secure(void)
{
	int err;

	k_sem_reset(&sec_sem);
	err = bt_conn_set_security(conn, BT_SECURITY_L4);
	if (err != 0) {
		printk("HELPER set security failed %d\n", err);
		return false;
	}
	if (k_sem_take(&sec_sem, K_SECONDS(40)) != 0) {
		return false;
	}
	return sec_err == 0 && sec_level == BT_SECURITY_L4;
}

static void mtu_done(struct bt_conn *c, uint8_t err, struct bt_gatt_exchange_params *p)
{
	ARG_UNUSED(p);
	printk("HELPER INFO MTU exchange %u, MTU %u\n", err, bt_gatt_get_mtu(c));
	k_sem_give(&mtu_sem);
}

static struct bt_gatt_exchange_params mtu_params = { .func = mtu_done };

static bool exchange_mtu(void)
{
	k_sem_reset(&mtu_sem);
	if (bt_gatt_exchange_mtu(conn, &mtu_params) != 0) {
		return false;
	}
	return k_sem_take(&mtu_sem, K_SECONDS(10)) == 0 && bt_gatt_get_mtu(conn) == 247;
}

/* ======================================================================== finding the relay service */

static void dm_completed(struct bt_gatt_dm *dm, void *ctx)
{
	const struct bt_gatt_dm_attr *chrc, *val, *ccc;

	ARG_UNUSED(ctx);
	h_in = h_out = h_out_ccc = h_info = 0;
	chrc = bt_gatt_dm_char_by_uuid(dm, &u_in.uuid);
	val = chrc != NULL ? bt_gatt_dm_desc_by_uuid(dm, chrc, &u_in.uuid) : NULL;
	h_in = val != NULL ? val->handle : 0;
	chrc = bt_gatt_dm_char_by_uuid(dm, &u_out.uuid);
	val = chrc != NULL ? bt_gatt_dm_desc_by_uuid(dm, chrc, &u_out.uuid) : NULL;
	ccc = chrc != NULL ? bt_gatt_dm_desc_by_uuid(dm, chrc, BT_UUID_GATT_CCC) : NULL;
	h_out = val != NULL ? val->handle : 0;
	h_out_ccc = ccc != NULL ? ccc->handle : 0;
	chrc = bt_gatt_dm_char_by_uuid(dm, &u_info.uuid);
	val = chrc != NULL ? bt_gatt_dm_desc_by_uuid(dm, chrc, &u_info.uuid) : NULL;
	h_info = val != NULL ? val->handle : 0;
	(void)bt_gatt_dm_data_release(dm);
	dm_res = (h_in != 0 && h_out != 0 && h_out_ccc != 0 && h_info != 0) ? 0 : -ENOENT;
	k_sem_give(&dm_sem);
}

static void dm_missing(struct bt_conn *c, void *ctx)
{
	ARG_UNUSED(c);
	ARG_UNUSED(ctx);
	dm_res = -ENODEV;
	k_sem_give(&dm_sem);
}

static void dm_error(struct bt_conn *c, int err, void *ctx)
{
	ARG_UNUSED(c);
	ARG_UNUSED(ctx);
	dm_res = err;
	k_sem_give(&dm_sem);
}

static const struct bt_gatt_dm_cb dm_cb = {
	.completed = dm_completed,
	.service_not_found = dm_missing,
	.error_found = dm_error,
};

/* 0 when the relay service is there with In, Out (and its CCC) and Info */
static int find_relay(void)
{
	int err;

	k_sem_reset(&dm_sem);
	err = bt_gatt_dm_start(conn, &u_relay.uuid, &dm_cb, NULL);
	if (err != 0) {
		return err;
	}
	if (k_sem_take(&dm_sem, K_SECONDS(20)) != 0) {
		return -ETIMEDOUT;
	}
	return dm_res;
}

/* ======================================================================== frames: write, read, subscribe, Out log */

static uint8_t g_err;

static void write_cb(struct bt_conn *c, uint8_t err, struct bt_gatt_write_params *p)
{
	ARG_UNUSED(c);
	ARG_UNUSED(p);
	g_err = err;
	k_sem_give(&op_sem);
}

static struct bt_gatt_write_params wp;

/* one write with response to In: the ATT error (0 = accepted), or a negative errno when it was not sent */
static int gwrite(const uint8_t *d, size_t n)
{
	int e;

	k_sem_reset(&op_sem);
	g_err = 0xFF;
	wp.func = write_cb;
	wp.handle = h_in;
	wp.offset = 0;
	wp.data = d;
	wp.length = (uint16_t)n;
	e = bt_gatt_write(conn, &wp);
	if (e != 0) {
		return e;
	}
	if (k_sem_take(&op_sem, K_SECONDS(20)) != 0) {
		return -ETIMEDOUT;
	}
	return g_err;
}

static uint8_t info_buf[16];
static int info_len;

static uint8_t read_cb(struct bt_conn *c, uint8_t err, struct bt_gatt_read_params *p, const void *data, uint16_t length)
{
	ARG_UNUSED(c);
	ARG_UNUSED(p);
	g_err = err;
	if (err == 0 && data != NULL && length <= sizeof(info_buf)) {
		memcpy(info_buf, data, length);
		info_len = length;
	}
	k_sem_give(&op_sem);
	return BT_GATT_ITER_STOP;
}

static struct bt_gatt_read_params rp;

static int gread_info(void)
{
	int e;

	k_sem_reset(&op_sem);
	g_err = 0xFF;
	info_len = 0;
	rp.func = read_cb;
	rp.handle_count = 1;
	rp.single.handle = h_info;
	rp.single.offset = 0;
	e = bt_gatt_read(conn, &rp);
	if (e != 0) {
		return e;
	}
	if (k_sem_take(&op_sem, K_SECONDS(20)) != 0) {
		return -ETIMEDOUT;
	}
	return g_err;
}

struct outf {
	uint8_t d[8];
	uint8_t n;
	int64_t t;
};
static struct outf outs[96];
static int nouts;
static int out_taken;
static int n_action_frames; /* ACTION frames that arrived */

static uint8_t out_notify(struct bt_conn *c, struct bt_gatt_subscribe_params *p, const void *data, uint16_t length)
{
	ARG_UNUSED(c);
	ARG_UNUSED(p);
	if (data == NULL) {
		return BT_GATT_ITER_STOP;
	}
	if (nouts < (int)ARRAY_SIZE(outs)) {
		struct outf *o = &outs[nouts++];

		o->n = (uint8_t)MIN(length, sizeof(o->d));
		memcpy(o->d, data, o->n);
		o->t = k_uptime_get();
		if (o->d[0] == 0x82) {
			n_action_frames++;
		}
		printk("HELPER OUT t=%lld op=0x%02x len=%u %02x %02x %02x %02x %02x %02x\n", o->t, o->d[0], length, o->d[1], o->d[2], o->d[3],
		       o->d[4], o->d[5], o->d[6]);
	}
	return BT_GATT_ITER_CONTINUE;
}

static struct bt_gatt_subscribe_params sub;

static void sub_done(struct bt_conn *c, uint8_t err, struct bt_gatt_subscribe_params *p)
{
	ARG_UNUSED(c);
	ARG_UNUSED(p);
	g_err = err;
	k_sem_give(&op_sem);
}

/* subscribe to Out: the ATT error of the CCC write (0 = on), or a negative errno */
static int gsubscribe(void)
{
	int e;

	memset(&sub, 0, sizeof(sub));
	sub.notify = out_notify;
	sub.subscribe = sub_done;
	sub.value_handle = h_out;
	sub.ccc_handle = h_out_ccc;
	sub.value = BT_GATT_CCC_NOTIFY;
	atomic_set_bit(sub.flags, BT_GATT_SUBSCRIBE_FLAG_VOLATILE);
	k_sem_reset(&op_sem);
	g_err = 0xFF;
	e = bt_gatt_subscribe(conn, &sub);
	if (e != 0) {
		return e;
	}
	if (k_sem_take(&op_sem, K_SECONDS(20)) != 0) {
		return -ETIMEDOUT;
	}
	return g_err;
}

/* the next frame on Out that has not been looked at */
static bool next_out(struct outf *o, int64_t timeout_ms)
{
	int64_t end = k_uptime_get() + timeout_ms;

	while (k_uptime_get() < end && out_taken >= nouts) {
		k_sleep(K_MSEC(20));
	}
	if (out_taken >= nouts) {
		return false;
	}
	*o = outs[out_taken++];
	return true;
}

/* ======================================================================== records and frames */

struct rb {
	uint8_t b[600];
	size_t n;
};

static void rb_init(struct rb *r, uint8_t cat, uint8_t flags)
{
	r->b[0] = cat;
	r->b[1] = flags;
	r->n = 2;
}

static void rb_field(struct rb *r, uint8_t type, const void *s, size_t len)
{
	r->b[r->n++] = type;
	r->b[r->n++] = (uint8_t)len;
	memcpy(&r->b[r->n], s, len);
	r->n += len;
}

static void rb_str(struct rb *r, uint8_t type, const char *s)
{
	rb_field(r, type, s, strlen(s));
}

static size_t put_frame(uint8_t *f, uint32_t id, uint16_t total, uint16_t off, const uint8_t *d, size_t dl)
{
	f[0] = 0x02;
	sys_put_le32(id, &f[1]);
	sys_put_le16(total, &f[5]);
	sys_put_le16(off, &f[7]);
	memcpy(&f[9], d, dl);
	return 9 + dl;
}

/* a whole record as PUT frames of at most frame_max bytes; the first write error, or 0 */
static int put_record(uint32_t id, const uint8_t *rec, size_t total, size_t frame_max)
{
	size_t off = 0;

	while (off < total) {
		uint8_t f[256];
		size_t dl = MIN(total - off, frame_max - 9);
		size_t n = put_frame(f, id, (uint16_t)total, (uint16_t)off, &rec[off], dl);
		int e = gwrite(f, n);

		if (e != 0) {
			return e;
		}
		off += dl;
	}
	return 0;
}

/* the first `pieces` pieces of a record, then stop */
static int put_first_pieces(uint32_t id, const uint8_t *rec, size_t total, size_t frame_max, int pieces)
{
	size_t off = 0;

	for (int i = 0; i < pieces && off < total; i++) {
		uint8_t f[256];
		size_t dl = MIN(total - off, frame_max - 9);
		size_t n = put_frame(f, id, (uint16_t)total, (uint16_t)off, &rec[off], dl);
		int e = gwrite(f, n);

		if (e != 0) {
			return e;
		}
		off += dl;
	}
	return 0;
}

static size_t id_frame(uint8_t *f, uint8_t op, uint32_t id)
{
	f[0] = op;
	sys_put_le32(id, &f[1]);
	return 5;
}

/* a frame that the ring must refuse: ATT error 0x80 on the write, and ERROR (0x83, code, id) on Out */
static int refusals_seen;

static void expect_refused(const uint8_t *f, size_t n, uint8_t code, uint32_t id, const char *label)
{
	char name[160];
	struct outf o;
	int e = gwrite(f, n);
	bool got = next_out(&o, 4000);
	bool frame_ok = got && o.n == 6 && o.d[0] == 0x83 && o.d[1] == code && sys_get_le32(&o.d[2]) == id;

	snprintk(name, sizeof(name), "%s: refused with ATT error 0x80 and ERROR code %u, id %u", label, code, id);
	CHECK(name, e == 0x80 && frame_ok);
	refusals_seen++;
}

static void expect_accepted(const uint8_t *f, size_t n, const char *label)
{
	char name[160];
	int e = gwrite(f, n);

	snprintk(name, sizeof(name), "%s: accepted", label);
	CHECK(name, e == 0);
}

static bool expect_ready(const char *label)
{
	char name[160];
	struct outf o;
	bool got = next_out(&o, 4000);
	bool ok = got && o.n == 3 && o.d[0] == 0x81 && o.d[1] == 1 && o.d[2] == 16;

	snprintk(name, sizeof(name), "%s: READY (version 1, store size 16) notified", label);
	CHECK(name, ok);
	return ok;
}

static void send_hello(const char *label)
{
	static const uint8_t f[2] = { 0x01, 0x01 };

	expect_accepted(f, 2, label);
	(void)expect_ready(label);
}

/* ======================================================================== the notifications of the test (the texts are UTF-8 bytes) */

static void build_n1(struct rb *r, uint8_t extra_flags)
{
	rb_init(r, 4, (uint8_t)(0x18 | extra_flags));
	rb_str(r, 1, "com.example.mail");
	rb_str(r, 2, "Hello");
	rb_str(r, 3, "First message");
	rb_str(r, 4, "20261112T101500");
}

/* title: 20 euro signs (60 bytes, limit 48), message: 100 e-acute (200 bytes, limit 160) */
static void build_n2(struct rb *r, uint8_t extra_flags)
{
	uint8_t t[200];

	rb_init(r, 2, (uint8_t)(0x18 | extra_flags));
	rb_str(r, 1, "com.example.chat");
	for (int k = 0; k < 20; k++) {
		memcpy(&t[3 * k], "\xE2\x82\xAC", 3);
	}
	rb_field(r, 2, t, 60);
	for (int k = 0; k < 100; k++) {
		memcpy(&t[2 * k], "\xC3\xA9", 2);
	}
	rb_field(r, 3, t, 200);
	rb_str(r, 4, "20261112T102000");
}

static void build_n2_replace(struct rb *r)
{
	rb_init(r, 3, 0x18);
	rb_str(r, 1, "com.example.chat");
	rb_str(r, 2, "Reply");
	rb_str(r, 3, "Second text");
	rb_str(r, 4, "20261112T110000");
}

static void build_n3(struct rb *r)
{
	rb_init(r, 1, 0x0C); /* positive action and pre-existing */
	rb_str(r, 1, "com.example.cal");
	rb_str(r, 2, "Meeting");
	rb_str(r, 3, "At noon");
	rb_str(r, 4, "20261112T103000");
}

static void build_n4(struct rb *r, uint8_t extra_flags)
{
	rb_init(r, 0, (uint8_t)(0x01 | extra_flags)); /* silent, no action; no message field */
	rb_str(r, 1, "com.example.news");
	rb_str(r, 2, "Headline");
	rb_str(r, 4, "20261112T104500");
}

/* ======================================================================== scenario I: a reduced notification service of an iPhone */

static const struct bt_uuid_128 u_ancs = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0x7905f431, 0xb5ce, 0x4e99, 0xa40f, 0x4b1e122d00d0));
static const struct bt_uuid_128 u_ns = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0x9fbf120d, 0x6301, 0x42d9, 0x8c58, 0x25e699a21dbd));
static const struct bt_uuid_128 u_cp = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0x69d1d8f3, 0x45e1, 0x49a8, 0x9821, 0x9bbdfdaad9d9));
static const struct bt_uuid_128 u_ds = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0x22eac6e9, 0x24d6, 0x4bb5, 0xbe44, 0xb36ace7c7bfb));

static K_SEM_DEFINE(ns_sem, 0, 1);
static bool ns_on, ds_on;
static uint8_t cp_cmds[8][8];
static int n_cp;
static int n_actions_ancs;
static uint32_t action_uid;
static uint8_t action_id = 0xFF;
static struct k_work ds_work;
static uint8_t resp[160];
static size_t resp_len;

static ssize_t ns_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value);
static ssize_t ds_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value);
static ssize_t cp_write(struct bt_conn *c, const struct bt_gatt_attr *attr, const void *buf, uint16_t len, uint16_t offset,
			uint8_t flags);

#define AUTH_RW (BT_GATT_PERM_READ_AUTHEN | BT_GATT_PERM_WRITE_AUTHEN)

/* [0] service, [1,2] Notification Source, [3] its CCC, [4,5] Control Point, [6,7] Data Source, [8] its CCC */
static struct bt_gatt_attr ancs_attrs[] = {
	BT_GATT_PRIMARY_SERVICE(&u_ancs),
	BT_GATT_CHARACTERISTIC(&u_ns.uuid, BT_GATT_CHRC_NOTIFY, BT_GATT_PERM_NONE, NULL, NULL, NULL),
	BT_GATT_CCC_WITH_WRITE_CB(NULL, ns_ccc_write, AUTH_RW),
	BT_GATT_CHARACTERISTIC(&u_cp.uuid, BT_GATT_CHRC_WRITE, BT_GATT_PERM_WRITE_AUTHEN, NULL, cp_write, NULL),
	BT_GATT_CHARACTERISTIC(&u_ds.uuid, BT_GATT_CHRC_NOTIFY, BT_GATT_PERM_NONE, NULL, NULL, NULL),
	BT_GATT_CCC_WITH_WRITE_CB(NULL, ds_ccc_write, AUTH_RW),
};
#define A_NS_VAL 2
#define A_DS_VAL 7
static struct bt_gatt_service ancs_svc = BT_GATT_SERVICE(ancs_attrs);

/* the one notification the iPhone holds */
static bool ip_has;
static const uint8_t ip_flags = 0x18;
static const uint8_t ip_cat = 1;
static const uint32_t ip_uid = 301;
static const char ip_app[] = "com.example.phone";
static const char ip_title[] = "Call";
static const char ip_msg[] = "Missed call";
static const char ip_date[] = "20261112T111500";

static void ns_send(uint8_t evt, uint8_t flags, uint8_t cat, uint32_t uid)
{
	uint8_t m[8];
	int err;

	m[0] = evt;
	m[1] = flags;
	m[2] = cat;
	m[3] = 1;
	sys_put_le32(uid, &m[4]);
	if (conn == NULL || !ns_on) {
		return;
	}
	err = bt_gatt_notify(conn, &ancs_attrs[A_NS_VAL], m, sizeof(m));
	printk("HELPER INFO NS event %u uid %u flags 0x%02x (%d)\n", evt, uid, flags, err);
}

static ssize_t ns_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value)
{
	ARG_UNUSED(c);
	ARG_UNUSED(attr);
	ns_on = (value & BT_GATT_CCC_NOTIFY) != 0;
	if (ns_on) {
		k_sem_give(&ns_sem);
	}
	printk("HELPER INFO Notification Source %s (t=%lld)\n", ns_on ? "subscribed" : "unsubscribed", k_uptime_get());
	return sizeof(value);
}

static ssize_t ds_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value)
{
	ARG_UNUSED(c);
	ARG_UNUSED(attr);
	ds_on = (value & BT_GATT_CCC_NOTIFY) != 0;
	return sizeof(value);
}

static void ds_fn(struct k_work *w)
{
	size_t off = 0;

	ARG_UNUSED(w);
	while (conn != NULL && off < resp_len) {
		size_t n = MIN((size_t)(bt_gatt_get_mtu(conn) - 3), resp_len - off);
		int err = bt_gatt_notify(conn, &ancs_attrs[A_DS_VAL], &resp[off], (uint16_t)n);

		if (err != 0) {
			k_sleep(K_MSEC(10));
			continue;
		}
		off += n;
	}
}

static ssize_t cp_write(struct bt_conn *c, const struct bt_gatt_attr *attr, const void *buf, uint16_t len, uint16_t offset,
			uint8_t flags)
{
	const uint8_t *d = buf;

	ARG_UNUSED(c);
	ARG_UNUSED(attr);
	ARG_UNUSED(flags);
	if (offset != 0 || len < 1) {
		return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
	}
	if (n_cp < 8) {
		memset(cp_cmds[n_cp], 0, 8);
		memcpy(cp_cmds[n_cp], d, MIN(len, 8));
		n_cp++;
	}
	if (d[0] == 0 && len >= 6) {
		/* Get Notification Attributes: the attributes asked for, in the order asked, each as id, length u16, data */
		uint32_t uid = sys_get_le32(&d[1]);
		size_t i = 5, o = 0;

		if (!ip_has || uid != ip_uid) {
			return BT_GATT_ERR(0xA2);
		}
		resp[o++] = 0;
		sys_put_le32(uid, &resp[o]);
		o += 4;
		while (i < len) {
			uint8_t id = d[i++];
			const char *val = "";

			if (id == 1 || id == 2 || id == 3) {
				i += 2; /* the maximum length: the texts here are short */
			}
			switch (id) {
			case 0:
				val = ip_app;
				break;
			case 1:
				val = ip_title;
				break;
			case 3:
				val = ip_msg;
				break;
			case 5:
				val = ip_date;
				break;
			default:
				break;
			}
			resp[o++] = id;
			sys_put_le16((uint16_t)strlen(val), &resp[o]);
			o += 2;
			memcpy(&resp[o], val, strlen(val));
			o += strlen(val);
		}
		resp_len = o;
		k_work_submit(&ds_work);
		return len;
	}
	if (d[0] == 2 && len == 6) {
		/* Perform Notification Action */
		action_uid = sys_get_le32(&d[1]);
		action_id = d[5];
		n_actions_ancs++;
		printk("HELPER INFO action %u for notification %u\n", action_id, action_uid);
		return len;
	}
	return BT_GATT_ERR(0xA0);
}

/* ======================================================================== script H */

static void connect_and_find(const char *label, bool first)
{
	char name[160];
	int r;

	snprintk(name, sizeof(name), "%s: connected to the ring", label);
	CHECK(name, wait_connected(first ? 150000 : 90000));
	r = find_relay();
	snprintk(name, sizeof(name), "%s: the relay service is found with In, Out (with its CCC) and Info (before the link is secure)", label);
	CHECK(name, r == 0);
}

static void script_h(void)
{
	uint8_t f[256];
	struct rb r;
	struct outf o;
	int e;
	size_t n;
	static const uint8_t info_want[6] = { 0x01, 0x10, 0x30, 0x30, 0xA0, 0x0F };

	connect_and_find("H", true);

	/* A write before the link reaches security level 4 fails: write, subscribe and read are each answered with an ATT security error */
	f[0] = 0x01;
	f[1] = 0x01;
	e = gwrite(f, 2);
	CHECK("H: a write to In before security level 4 fails (ATT insufficient authentication or encryption)", e == 0x05 || e == 0x0F);
	e = gsubscribe();
	CHECK("H: a subscription to Out before security level 4 fails", e == 0x05 || e == 0x0F);
	e = gread_info();
	CHECK("H: a read of Info before security level 4 fails", e == 0x05 || e == 0x0F);

	CHECK("H: pairing with the passkey reaches security level 4", secure());
	e = gread_info();
	CHECK("H: Info is 6 bytes: version 1, store 16, application identifier 48, title 48, message 160, date 15",
	      e == 0 && info_len == 6 && memcmp(info_buf, info_want, 6) == 0);
	e = gsubscribe();
	CHECK("H: Out notifications are on", e == 0);

	/* frames before HELLO */
	n = put_frame(f, 1900, 2, 0, (const uint8_t[]){ 1, 0 }, 2);
	expect_refused(f, n, 2, 1900, "H: PUT before HELLO");
	n = id_frame(f, 0x03, 1901);
	expect_refused(f, n, 2, 1901, "H: REMOVE before HELLO");
	f[0] = 0x04;
	expect_refused(f, 1, 2, 0, "H: CLEAR before HELLO");
	f[0] = 0x01;
	f[1] = 0x02;
	expect_refused(f, 2, 6, 0, "H: HELLO with version 2");

	WAIT("H: wait for the ring - the ring shows the list screen (stage 5)", wait_ring(5, 120000));
	send_hello("H: HELLO");

	/* four notifications at the smallest ATT payload: 20-byte frames, 11 data bytes each */
	build_n1(&r, 0);
	CHECK("H: PUT 1001 (59 bytes in 6 frames of at most 20 bytes) accepted", put_record(1001, r.b, r.n, 20) == 0);
	build_n2(&r, 0);
	CHECK("H: PUT 1002 (301 bytes in 28 frames of at most 20 bytes; title and message longer than their limits) accepted",
	      put_record(1002, r.b, r.n, 20) == 0);
	build_n3(&r);
	CHECK("H: PUT 1003 accepted", put_record(1003, r.b, r.n, 20) == 0);
	build_n4(&r, 0);
	CHECK("H: PUT 1004 accepted", put_record(1004, r.b, r.n, 20) == 0);
	CHECK("H: nothing but READY and the 4 refusals came on Out so far", nouts == 5 && nouts == out_taken);

	/* the replace, after the ring has read 1002 */
	WAIT("H: wait for the ring - the ring opened 1002 (stage 10)", wait_ring(10, 120000));
	build_n2_replace(&r);
	CHECK("H: PUT 1002 again (a replace) accepted", put_record(1002, r.b, r.n, 20) == 0);
	WAIT("H: wait for the ring - the ring checked the replace (stage 20)", wait_ring(20, 120000));

	/* an action the notification does not have: nothing arrives */
	WAIT("H: wait for the ring - the ring pressed dismiss and positive on 1004 (stage 30)", wait_ring(30, 120000));
	k_sleep(K_MSEC(3000));
	CHECK("H: no ACTION frame arrived for an action 1004 does not have", n_action_frames == 0 && nouts == out_taken);
	helper_stage(31);
	WAIT("H: wait for the ring - the ring pressed dismiss on 1003, which has no negative action (stage 40)", wait_ring(40, 120000));
	k_sleep(K_MSEC(3000));
	CHECK("H: no ACTION frame arrived for the dismiss on 1003", n_action_frames == 0 && nouts == out_taken);
	helper_stage(41);

	/* the positive action */
	WAIT("H: wait for the ring - the ring pressed the positive action on 1003 (stage 50)", wait_ring(50, 120000));
	CHECK("H: ACTION arrived: id 1003, positive (0)", next_out(&o, 15000) && o.n == 6 && o.d[0] == 0x82 && sys_get_le32(&o.d[1]) == 1003 &&
	      o.d[5] == 0);
	helper_stage(51);

	/* the dismiss: ACTION negative, then REMOVE */
	WAIT("H: wait for the ring - the ring pressed dismiss on 1002 (stage 60)", wait_ring(60, 120000));
	CHECK("H: ACTION arrived: id 1002, negative (1)", next_out(&o, 15000) && o.n == 6 && o.d[0] == 0x82 && sys_get_le32(&o.d[1]) == 1002 &&
	      o.d[5] == 1);
	helper_stage(61);
	WAIT("H: wait for the ring - the ring saw the entry still in its store (stage 62)", wait_ring(62, 120000));
	n = id_frame(f, 0x03, 1002);
	expect_accepted(f, n, "H: REMOVE 1002");
	WAIT("H: wait for the ring - the ring saw the entry leave (stage 70)", wait_ring(70, 120000));

	/* no subscription to Out: the ring refuses the action itself */
	(void)bt_gatt_unsubscribe(conn, &sub); /* Out notifications off; the proof that nothing is notified is the ring's count of frames dropped on Out */
	k_sleep(K_MSEC(700));
	f[0] = 0x7E;
	e = gwrite(f, 1);
	k_sleep(K_MSEC(700));
	CHECK("H: with no subscription to Out a refused frame is still answered with ATT error 0x80", e == 0x80);
	helper_stage(71);
	WAIT("H: wait for the ring - the ring tried an action with no subscription (stage 80)", wait_ring(80, 120000));
	k_sleep(K_MSEC(3000));
	e = gsubscribe();
	CHECK("H: Out notifications are on again", e == 0);
	helper_stage(81);

	/* RECORDING */
	WAIT("H: wait for the ring - the ring is recording (stage 90)", wait_ring(90, 120000));
	rb_init(&r, 7, 0x10);
	rb_str(&r, 1, "com.example.rec");
	rb_str(&r, 2, "During recording");
	CHECK("H: PUT 1005 during RECORDING accepted", put_record(1005, r.b, r.n, 20) == 0);
	n = id_frame(f, 0x03, 1001);
	expect_accepted(f, n, "H: REMOVE 1001 during RECORDING");
	n = put_frame(f, 1006, 2, 0, (const uint8_t[]){ 1, 0x40 }, 2);
	expect_refused(f, n, 5, 1006, "H: a malformed PUT during RECORDING");
	f[0] = 0x7E;
	expect_refused(f, 1, 1, 0, "H: an unknown opcode during RECORDING");
	helper_stage(91);

	/* a new session by HELLO, then three notifications */
	WAIT("H: wait for the ring - the ring stopped the recording (stage 110)", wait_ring(110, 120000));
	send_hello("H: HELLO (a new session)");
	rb_init(&r, 1, 0x00);
	rb_str(&r, 1, "app.a");
	rb_str(&r, 2, "First");
	CHECK("H: PUT 2001 accepted", put_record(2001, r.b, r.n, 20) == 0);
	rb_init(&r, 2, 0x00);
	rb_str(&r, 1, "app.b");
	rb_str(&r, 2, "Second");
	CHECK("H: PUT 2002 accepted", put_record(2002, r.b, r.n, 20) == 0);
	rb_init(&r, 3, 0x08);
	rb_str(&r, 1, "app.c");
	rb_str(&r, 2, "Third");
	CHECK("H: PUT 2003 accepted", put_record(2003, r.b, r.n, 20) == 0);
	helper_stage(111);

	/* 21 malformed frames, each with its code */
	WAIT("H: wait for the ring - the ring took its snapshot of the store (stage 120)", wait_ring(120, 120000));
	{
		static const uint8_t bad_op[5] = { 0x7E, 1, 2, 3, 4 };
		static const uint8_t hello1[1] = { 0x01 };
		static const uint8_t hello3[3] = { 0x01, 0x01, 0x00 };
		static const uint8_t hello_v0[2] = { 0x01, 0x00 };
		static const uint8_t hello_v2[2] = { 0x01, 0x02 };
		static const uint8_t rem4[4] = { 0x03, 1, 0, 0 };
		static const uint8_t rem6[6] = { 0x03, 2, 0, 0, 0, 0 };
		static const uint8_t clr2[2] = { 0x04, 0x00 };
		static const uint8_t put9[9] = { 0x02, 7, 0, 0, 0, 10, 0, 0, 0 };
		static const uint8_t d3[3] = { 1, 0, 0 };

		expect_refused(bad_op, 5, 1, 0, "H: M1 unknown opcode 0x7E");
		expect_refused(hello1, 1, 1, 0, "H: M2 HELLO of 1 byte");
		expect_refused(hello3, 3, 1, 0, "H: M3 HELLO of 3 bytes");
		expect_refused(hello_v0, 2, 6, 0, "H: M4 HELLO version 0");
		expect_refused(hello_v2, 2, 6, 0, "H: M5 HELLO version 2");
		expect_refused(rem4, 4, 1, 0, "H: M6 REMOVE of 4 bytes");
		expect_refused(rem6, 6, 1, 2, "H: M7 REMOVE of 6 bytes");
		expect_refused(clr2, 2, 1, 0, "H: M8 CLEAR of 2 bytes");
		expect_refused(put9, 9, 1, 7, "H: M9 PUT with no data byte");
		n = put_frame(f, 8, 1, 0, (const uint8_t[]){ 1 }, 1);
		expect_refused(f, n, 4, 8, "H: M10 PUT with total 1");
		n = put_frame(f, 9, 513, 0, d3, 3);
		expect_refused(f, n, 4, 9, "H: M11 PUT with total 513");
		n = put_frame(f, 10, 0, 0, d3, 3);
		expect_refused(f, n, 4, 10, "H: M12 PUT with total 0");
		n = put_frame(f, 11, 10, 5, d3, 3);
		expect_refused(f, n, 3, 11, "H: M13 PUT at offset 5 with no record in progress");
		n = put_frame(f, 12, 30, 0, (const uint8_t[]){ 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 }, 10);
		expect_accepted(f, n, "H: M14a first piece of a record of 30 bytes");
		n = put_frame(f, 12, 30, 12, d3, 3);
		expect_refused(f, n, 3, 12, "H: M14 next piece at offset 12 after 10 bytes (a gap)");
		n = put_frame(f, 13, 5, 0, (const uint8_t[]){ 1, 0, 0, 0, 0, 0 }, 6);
		expect_refused(f, n, 3, 13, "H: M15 6 bytes for a total of 5");
		n = put_frame(f, 14, 5, 0, (const uint8_t[]){ 1, 0, 3, 9, 'a' }, 5);
		expect_refused(f, n, 5, 14, "H: M16 a field that runs past the end");
		n = put_frame(f, 15, 4, 0, (const uint8_t[]){ 1, 0, 9, 0 }, 4);
		expect_refused(f, n, 5, 15, "H: M17 an unknown field type 9");
		n = put_frame(f, 16, 8, 0, (const uint8_t[]){ 1, 0, 1, 1, 'a', 1, 1, 'b' }, 8);
		expect_refused(f, n, 5, 16, "H: M18 a repeated field type");
		n = put_frame(f, 17, 2, 0, (const uint8_t[]){ 1, 0x20 }, 2);
		expect_refused(f, n, 5, 17, "H: M19 flag bit 5 set");
		n = put_frame(f, 2003, 2, 0, (const uint8_t[]){ 1, 0x80 }, 2); /* the id of a notification the ring holds */
		expect_refused(f, n, 5, 2003, "H: M20 flag bit 7 set");
		n = put_frame(f, 19, 3, 0, (const uint8_t[]){ 1, 0, 2 }, 3);
		expect_refused(f, n, 5, 19, "H: M21 a field type with no length byte");
	}
	CHECK("H: nothing but those refusals came on Out", nouts == out_taken);
	helper_stage(121);

	/* a record left unfinished, then the link drops */
	WAIT("H: wait for the ring - the screen is off on the ring (stage 130)", wait_ring(130, 120000));
	f[0] = 0x04;
	expect_accepted(f, 1, "H: CLEAR");
	helper_stage(131);
	WAIT("H: wait for the ring - the ring saw the store empty (stage 132)", wait_ring(132, 120000));
	rb_init(&r, 1, 0x00);
	rb_str(&r, 1, "app.d");
	rb_str(&r, 2, "Fourth");
	CHECK("H: PUT 2004 accepted", put_record(2004, r.b, r.n, 20) == 0);
	helper_stage(133);
	WAIT("H: wait for the ring - the ring checked the store and the screen (stage 134)", wait_ring(134, 120000));
	build_n2(&r, 0);
	CHECK("H: the first two pieces of a record of 301 bytes accepted", put_first_pieces(2999, r.b, r.n, 20, 2) == 0);
	helper_stage(135);
	WAIT("H: wait for the ring - the ring is ready for the link to drop (stage 140)", wait_ring(140, 120000));
	k_sem_reset(&disc_sem);
	CHECK("H: the stand-in ends the link", bt_conn_disconnect(conn, BT_HCI_ERR_REMOTE_USER_TERM_CONN) == 0);
	CHECK("H: the link is down", k_sem_take(&disc_sem, K_SECONDS(10)) == 0);

	/* the reconnect: the notifications of the old session are gone; a new HELLO is needed */
	k_sem_reset(&conn_sem);
	connect_and_find("H: reconnect", false);
	CHECK("H: reconnect: security level 4 again with the stored key (no passkey)", secure());
	nouts = out_taken = 0;
	e = gsubscribe();
	CHECK("H: reconnect: Out notifications are on", e == 0);
	build_n2(&r, 0);
	n = put_frame(f, 2999, (uint16_t)r.n, 0, r.b, 11);
	expect_refused(f, n, 2, 2999, "H: reconnect: PUT before the new HELLO");
	n = put_frame(f, 2999, (uint16_t)r.n, 22, &r.b[22], 11);
	expect_refused(f, n, 2, 2999, "H: reconnect: the next piece of the old record before the new HELLO");
	send_hello("H: reconnect: HELLO");
	n = put_frame(f, 2999, (uint16_t)r.n, 22, &r.b[22], 11);
	expect_refused(f, n, 3, 2999, "H: reconnect: after HELLO the next piece of the old record (the unfinished record was dropped)");
	build_n1(&r, 0x04);
	CHECK("H: reconnect: PUT 1001 (pre-existing) accepted", put_record(1001, r.b, r.n, 20) == 0);
	build_n2(&r, 0x04);
	CHECK("H: reconnect: PUT 1002 (pre-existing) accepted", put_record(1002, r.b, r.n, 20) == 0);
	build_n3(&r);
	CHECK("H: reconnect: PUT 1003 accepted", put_record(1003, r.b, r.n, 20) == 0);
	build_n4(&r, 0x04);
	CHECK("H: reconnect: PUT 1004 (pre-existing) accepted", put_record(1004, r.b, r.n, 20) == 0);
	CHECK("H: the ATT MTU is 247 after the exchange (frames of 244 bytes)", exchange_mtu());
	{
		uint8_t t[100];

		/* 3005: a title of 47 letters and two euro signs (53 bytes): the limit 48 falls inside the first sign */
		rb_init(&r, 5, 0x04);
		rb_str(&r, 1, "app.five");
		memset(t, 'a', 47);
		memcpy(&t[47], "\xE2\x82\xAC\xE2\x82\xAC", 6);
		rb_field(&r, 2, t, 53);
		CHECK("H: reconnect: PUT 3005 (title longer than its limit, cut inside a character) accepted", put_record(3005, r.b, r.n, 244) == 0);
	}
	{
		uint8_t a[200], t[100], m[200];

		/* 3006: a record of exactly 512 bytes in 3 frames of at most 244 bytes */
		memset(a, 'A', sizeof(a));
		memset(t, 'T', sizeof(t));
		memset(m, 'M', sizeof(m));
		rb_init(&r, 8, 0x14);
		rb_field(&r, 1, a, sizeof(a));
		rb_field(&r, 2, t, sizeof(t));
		rb_field(&r, 3, m, sizeof(m));
		rb_field(&r, 4, "20", 2);
		CHECK("H: reconnect: PUT 3006 (512 bytes in frames of 244 bytes) accepted", put_record(3006, r.b, r.n, 244) == 0);
	}
	rb_init(&r, 11, 0x00);
	CHECK("H: reconnect: PUT 3007 (a record of exactly 2 bytes) accepted", put_record(3007, r.b, r.n, 244) == 0);
	/* the worked example of the helper specification (design/software/os/android-helper-example.py), byte for byte: six frames at a write of
	 * 20 bytes, REMOVE, and the same record as one frame of 71 bytes */
	{
		static const uint8_t f20[6][20] = {
			{ 0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x00, 0x00, 0x04, 0x12, 0x01, 0x10, 0x63, 0x6f, 0x6d, 0x2e, 0x65, 0x78, 0x61 },
			{ 0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x0b, 0x00, 0x6d, 0x70, 0x6c, 0x65, 0x2e, 0x63, 0x68, 0x61, 0x74, 0x02, 0x04 },
			{ 0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x16, 0x00, 0x41, 0x6e, 0x6e, 0x61, 0x03, 0x11, 0x4c, 0x75, 0x6e, 0x63, 0x68 },
			{ 0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x21, 0x00, 0x20, 0x61, 0x74, 0x20, 0x31, 0x32, 0x3f, 0x20, 0xf0, 0x9f, 0x8d },
			{ 0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x2c, 0x00, 0x9c, 0x04, 0x0f, 0x32, 0x30, 0x32, 0x36, 0x31, 0x31, 0x31, 0x32 },
			{ 0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x37, 0x00, 0x54, 0x31, 0x39, 0x31, 0x35, 0x30, 0x30 },
		};
		static const size_t f20_len[6] = { 20, 20, 20, 20, 20, 16 };
		static const uint8_t f244[71] = {
			0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x00, 0x00, 0x04, 0x12, 0x01, 0x10, 0x63, 0x6f, 0x6d, 0x2e, 0x65, 0x78, 0x61, 0x6d, 0x70,
			0x6c, 0x65, 0x2e, 0x63, 0x68, 0x61, 0x74, 0x02, 0x04, 0x41, 0x6e, 0x6e, 0x61, 0x03, 0x11, 0x4c, 0x75, 0x6e, 0x63, 0x68, 0x20, 0x61,
			0x74, 0x20, 0x31, 0x32, 0x3f, 0x20, 0xf0, 0x9f, 0x8d, 0x9c, 0x04, 0x0f, 0x32, 0x30, 0x32, 0x36, 0x31, 0x31, 0x31, 0x32, 0x54, 0x31,
			0x39, 0x31, 0x35, 0x30, 0x30,
		};
		static const uint8_t rem[5] = { 0x03, 0xa5, 0x00, 0x01, 0x00 };
		int e6 = 0;

		helper_stage(136);
		WAIT("H: wait for the ring - the ring checked the 7 entries before the example (stage 141)", wait_ring(141, 120000));
		for (int i = 0; i < 6 && e6 == 0; i++) {
			e6 = gwrite(f20[i], f20_len[i]);
		}
		CHECK("H: the example of the helper specification: its 6 PUT frames of at most 20 bytes accepted", e6 == 0);
		helper_stage(137);
		WAIT("H: wait for the ring - the ring checked entry 0x000100a5 field by field (stage 142)", wait_ring(142, 120000));
		expect_accepted(rem, 5, "H: the example's REMOVE");
		helper_stage(138);
		WAIT("H: wait for the ring - the ring checked that 0x000100a5 is gone (stage 143)", wait_ring(143, 120000));
		expect_accepted(f244, sizeof(f244), "H: the example's PUT as one frame of 71 bytes");
	}
	CHECK("H: nothing but the refusals and READY came on Out after the reconnect", nouts == out_taken);
	helper_stage(139);

	/* a dismiss chosen on the ring for the example's notification must arrive as exactly 82 a5 00 01 00 01 (the example's ACTION negative) */
	WAIT("H: wait for the ring's dismiss on the example's notification (stage 145)", wait_ring(145, 120000));
	{
		static const uint8_t want[6] = { 0x82, 0xa5, 0x00, 0x01, 0x00, 0x01 };

		CHECK("H: the dismiss arrived as exactly the ACTION of the example: 82 a5 00 01 00 01",
		      next_out(&o, 15000) && o.n == 6 && memcmp(o.d, want, 6) == 0);
	}
	helper_stage(146);

	/* the end */
	WAIT("H: wait for the ring - the ring finished (stage 150)", wait_ring(150, 120000));
	k_sleep(K_MSEC(3000));
}

/* ======================================================================== script I */

static void script_i(void)
{
	uint8_t f[64];
	size_t n;
	int e;
	struct outf o;

	CHECK("I: connected to the ring", wait_connected(150000));
	CHECK("I: the ATT MTU is 247", exchange_mtu());
	CHECK("I: pairing with the passkey reaches security level 4", secure());
	CHECK("I: the ring subscribed to the Notification Source", k_sem_take(&ns_sem, K_SECONDS(60)) == 0);
	k_sleep(K_MSEC(500));
	ip_has = true;
	ns_send(0, ip_flags, ip_cat, ip_uid);
	WAIT("I: wait for the ring - the ring has the notification with its text (stage 10)", wait_ring(10, 120000));
	CHECK("I: the relay service is found on the iPhone's link", find_relay() == 0);
	e = gsubscribe();
	CHECK("I: Out notifications are on", e == 0);
	f[0] = 0x01;
	f[1] = 0x01;
	expect_refused(f, 2, 7, 0, "I: HELLO on an iPhone's link");
	n = put_frame(f, 302, 5, 0, (const uint8_t[]){ 1, 0, 2, 1, 'x' }, 5);
	expect_refused(f, n, 7, 302, "I: PUT on an iPhone's link");
	n = id_frame(f, 0x03, 301);
	expect_refused(f, n, 7, 301, "I: REMOVE of the iPhone's notification on an iPhone's link");
	f[0] = 0x04;
	expect_refused(f, 1, 7, 0, "I: CLEAR on an iPhone's link");
	f[0] = 0x7E;
	expect_refused(f, 1, 7, 0, "I: an unknown opcode on an iPhone's link");
	CHECK("I: no READY or other frame came on Out: only the 5 refusals", nouts == 5 && !next_out(&o, 1000));
	helper_stage(11);
	/* the dismiss chosen on the ring goes to this service, the source of the entry */
	{
		int64_t end = k_uptime_get() + 60000;

		while (n_actions_ancs == 0 && k_uptime_get() < end) {
			k_sleep(K_MSEC(20));
		}
	}
	CHECK("I: the dismiss chosen on the ring arrived through the notification service: negative action (1) for 301",
	      n_actions_ancs == 1 && action_uid == 301 && action_id == 1);
	k_sleep(K_MSEC(300));
	ns_send(2, ip_flags, ip_cat, ip_uid);
	CHECK("I: no ACTION frame came on the relay's Out", n_action_frames == 0);
	WAIT("I: wait for the ring - the ring finished (stage 20)", wait_ring(20, 120000));
	k_sleep(K_MSEC(3000));
}

/* ======================================================================== script B */

/* an iPhone-like stand-in whose relay HELLO comes first (right after security level 4, before the ring has looked for Apple's service) */
static void script_b(void)
{
	struct rb r;
	struct outf o;
	static const uint8_t hello_f[2] = { 0x01, 0x01 };

	CHECK("B: connected to the ring", wait_connected(150000));
	CHECK("B: the relay service is found before the link is secure", find_relay() == 0);
	CHECK("B: pairing with the passkey reaches security level 4", secure());
	/* HELLO starts the session although the helper has not subscribed to Out (READY is then dropped on the ring), and a PUT is accepted */
	expect_accepted(hello_f, 2, "B: HELLO right after security level 4, before the subscription to Out");
	rb_init(&r, 1, 0x18);
	rb_str(&r, 1, "com.example.chat2");
	rb_str(&r, 2, "Both");
	rb_str(&r, 3, "HELLO came first");
	CHECK("B: PUT 401 accepted before the subscription to Out (not code 2)", put_record(401, r.b, r.n, 20) == 0);
	CHECK("B: Out notifications are on", gsubscribe() == 0);
	CHECK("B: the ring did not subscribe to the notification service within 8 s (the link's source is the relay)",
	      k_sem_take(&ns_sem, K_SECONDS(8)) != 0);
	/* the ring has found Apple's service on this link by now: a relay frame is still accepted */
	WAIT("B: wait for the ring's stage 10 (it checked that Apple's service was found and not used)", wait_ring(10, 120000));
	{
		/* the stand-in, an iPhone too, offers one Apple notification (added, uid 999): it cannot be delivered because the ring never subscribed
		 * to the Notification Source; the ring checks that nothing of it is in the store */
		uint8_t m[8] = { 0, 0x18, 1, 1, 0xe7, 0x03, 0, 0 };
		int ne = bt_gatt_notify(conn, &ancs_attrs[A_NS_VAL], m, sizeof(m));

		CHECK("B: the Apple notification 999 could not be sent (the ring did not subscribe to the Notification Source)", ne != 0 && !ns_on);
	}
	rb_init(&r, 1, 0x18);
	rb_str(&r, 1, "com.example.chat2");
	rb_str(&r, 2, "Second");
	rb_str(&r, 3, "after Apple's service was found");
	CHECK("B: PUT 402 accepted after the ring found Apple's service on the link (the first user fixed the source)", put_record(402, r.b, r.n, 20) == 0);
	helper_stage(11);
	/* the service goes away: the GATT server indicates Service Changed */
	WAIT("B: wait for the ring's stage 12", wait_ring(12, 120000));
	CHECK("B: the stand-in's notification service is removed (Service Changed is indicated)", bt_gatt_service_unregister(&ancs_svc) == 0);
	helper_stage(13);
	CHECK("B: ACTION arrived: id 401, negative (1)", next_out(&o, 60000) && o.n == 6 && o.d[0] == 0x82 && sys_get_le32(&o.d[1]) == 401 &&
	      o.d[5] == 1);
	WAIT("B: wait for the ring - the ring finished (stage 20)", wait_ring(20, 120000));
	k_sleep(K_MSEC(3000));
}

/* ======================================================================== script Q: a full Out queue, an accepted HELLO */

static void script_q(void)
{
	static const uint8_t hello_f[2] = { 0x01, 0x01 };
	static const uint8_t bad[1] = { 0x7E };
	struct rb r;
	struct outf o;
	int refused = 0;

	CHECK("Q: connected to the ring", wait_connected(150000));
	CHECK("Q: the relay service is found before the link is secure", find_relay() == 0);
	CHECK("Q: pairing with the passkey reaches security level 4", secure());
	CHECK("Q: Out notifications are on", gsubscribe() == 0);
	send_hello("Q: HELLO");
	rb_init(&r, 1, 0x18);
	rb_str(&r, 1, "app.q");
	rb_str(&r, 2, "Queue");
	CHECK("Q: PUT 5001 accepted", put_record(5001, r.b, r.n, 20) == 0);
	helper_stage(1);
	WAIT("Q: wait for the ring's stage 2 (it blocked Out)", wait_ring(2, 120000));
	/* twelve refused frames: the ring queues 8 ERROR frames and drops 4; none is delivered while Out is blocked */
	for (int i = 0; i < 12; i++) {
		refused += gwrite(bad, 1) == 0x80 ? 1 : 0;
	}
	CHECK("Q: 12 unknown opcodes were each refused with ATT error 0x80", refused == 12);
	helper_stage(3);
	WAIT("Q: wait for the ring's stage 4 (it tried an action with the queue full)", wait_ring(4, 120000));
	expect_accepted(hello_f, 2, "Q: the second HELLO (the ring's Out queue is full)");
	helper_stage(5);
	WAIT("Q: wait for the ring's stage 6 (it unblocked Out)", wait_ring(6, 120000));
	/* the frames that waited from before the HELLO are gone: the first frame on Out is READY, and nothing else comes */
	CHECK("Q: after the second HELLO the first frame on Out is READY (81 01 10)", next_out(&o, 10000) && o.n == 3 && o.d[0] == 0x81 &&
	      o.d[1] == 1 && o.d[2] == 16);
	k_sleep(K_MSEC(3000));
	CHECK("Q: after the second HELLO no ERROR frame from before it was delivered (2 frames in all: both READY)", nouts == 2 && out_taken == 2);
	helper_stage(7);
	WAIT("Q: wait for the ring - the ring finished (stage 8)", wait_ring(8, 120000));
	k_sleep(K_MSEC(2000));
}

int main(void)
{
	char *s = nsi_host_getenv("RING_SCENARIO");
	int err;

	scen = s != NULL ? s[0] : '?';
	printk("HELPER START scenario %c\n", scen);
	k_work_init_delayable(&scan_work, scan_fn);
	k_work_init(&ds_work, ds_fn);
	(void)bt_conn_auth_cb_register(&auth_cb);
	(void)bt_conn_auth_info_cb_register(&info_cb);
	err = bt_enable(NULL);
	CHECK("Bluetooth up", err == 0);
	if (err != 0) {
		printk("HELPER RESULT FAIL\n");
		return 0;
	}
	if (scen == 'I' || scen == 'B') {
		CHECK("the iPhone's notification service is registered", bt_gatt_service_register(&ancs_svc) == 0);
	}
	k_sleep(K_MSEC(500));
	scan_start();

	if (scen == 'H') {
		script_h();
	} else if (scen == 'I') {
		script_i();
	} else if (scen == 'B') {
		script_b();
	} else if (scen == 'Q') {
		script_q();
	} else {
		CHECK("known scenario", false);
	}
	printk("HELPER EVAL t=%lld\n", k_uptime_get());
	CHECK("every frame on Out was looked at", out_taken == nouts);
	printk("HELPER RESULT %s checks=%d fails=%d\n", fails == 0 ? "PASS" : "FAIL", checks, fails);
	while (1) {
		k_sleep(K_SECONDS(1));
	}
	return 0;
}
