/* Ring relay, Bluetooth part: see rrl_bt.h and design/firmware.md section 7.7. */

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/init.h>
#include <zephyr/sys/printk.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/uuid.h>

#include <ring_iphone/rip.h>
#include <ring_relay/rrl.h>
#include <ring_relay/rrl_bt.h>

#define ATT_ERR_REFUSED 0x80 /* application error: a frame that was refused */
#define OUTQ            8
#define OUT_RETRIES     5

static struct bt_uuid_128 u_svc = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0xa3c20000, 0x5b7e, 0x4f2a, 0x9c1d, 0x7e2b6f4d8a90));
static const struct bt_uuid_128 u_in = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0xa3c20001, 0x5b7e, 0x4f2a, 0x9c1d, 0x7e2b6f4d8a90));
static const struct bt_uuid_128 u_out = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0xa3c20002, 0x5b7e, 0x4f2a, 0x9c1d, 0x7e2b6f4d8a90));
static const struct bt_uuid_128 u_info = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0xa3c20003, 0x5b7e, 0x4f2a, 0x9c1d, 0x7e2b6f4d8a90));

static K_MUTEX_DEFINE(rl);
static struct rrl sess;           /* the session of rl_conn */
static struct bt_conn *rl_conn;   /* the link of the session (a reference), NULL when none */
static struct rrl_stats st;

static struct {
	uint8_t d[6];
	uint8_t n;
} outq[OUTQ];
static uint8_t out_head, out_n;
static uint32_t out_epoch; /* changes whenever the queue is emptied at once: a frame in flight then belongs to a queue that is gone */
#ifdef CONFIG_RING_RELAY_TEST_HOOKS
static volatile bool test_block_out; /* test ring only: Out is blocked, as when the controller has no buffer for a notification */
#endif
static uint8_t out_try;
static struct k_work_delayable out_work;

static ssize_t in_write(struct bt_conn *conn, const struct bt_gatt_attr *attr, const void *buf, uint16_t len, uint16_t offset,
			uint8_t flags);
static ssize_t info_read(struct bt_conn *conn, const struct bt_gatt_attr *attr, void *buf, uint16_t len, uint16_t offset);
static void out_ccc_changed(const struct bt_gatt_attr *attr, uint16_t value);

/* Every characteristic needs an encrypted, authenticated link: the permissions make the host refuse below that, and each
 * handler asks for security level 4 itself (design/firmware.md 7.4). */
BT_GATT_SERVICE_DEFINE(relay_svc,
	BT_GATT_PRIMARY_SERVICE(&u_svc),
	BT_GATT_CHARACTERISTIC(&u_in.uuid, BT_GATT_CHRC_WRITE, BT_GATT_PERM_WRITE_AUTHEN, NULL, in_write, NULL),
	BT_GATT_CHARACTERISTIC(&u_out.uuid, BT_GATT_CHRC_NOTIFY, BT_GATT_PERM_NONE, NULL, NULL, NULL),
	BT_GATT_CCC(out_ccc_changed, BT_GATT_PERM_READ_AUTHEN | BT_GATT_PERM_WRITE_AUTHEN),
	BT_GATT_CHARACTERISTIC(&u_info.uuid, BT_GATT_CHRC_READ, BT_GATT_PERM_READ_AUTHEN, info_read, NULL, NULL));

#define OUT_ATTR (&relay_svc.attrs[4]) /* the value of Out: service, In (2), Out declaration, Out value */

/* ---------------------------------------------------------------- Out

 * Frames are queued under the relay lock and sent from the system workqueue (never from the Bluetooth receive thread).
 * A frame is notified only while the helper is subscribed to Out. */

/* every frame that still waits is dropped (a new link, a HELLO, the end of a link) */
static void out_reset_locked(void)
{
	out_n = 0;
	out_head = 0;
	out_try = 0;
	out_epoch++;
}

/* count_drop: a frame that does not fit is counted as dropped (READY, ERROR); an ACTION that does not fit is not a dropped frame, it is a refused
 * action and relay_action counts it once, in actions_refused */
static bool q_push_locked(const uint8_t *d, uint8_t n, bool count_drop)
{
	if (out_n >= OUTQ) {
		if (count_drop) {
			st.out_dropped++;
		}
		return false;
	}
	memcpy(outq[(out_head + out_n) % OUTQ].d, d, n);
	outq[(out_head + out_n) % OUTQ].n = n;
	out_n++;
	return true;
}

static void out_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	for (;;) {
		uint8_t d[6];
		uint8_t n;
		struct bt_conn *c;
		uint32_t ep;
		int err;

#ifdef CONFIG_RING_RELAY_TEST_HOOKS
		if (test_block_out) {
			/* test ring only: the frames stay queued and no retry is used up while Out is blocked */
			(void)k_work_reschedule(&out_work, K_MSEC(50));
			return;
		}
#endif
		k_mutex_lock(&rl, K_FOREVER);
		if (out_n == 0 || rl_conn == NULL) {
			k_mutex_unlock(&rl);
			return;
		}
		c = bt_conn_ref(rl_conn);
		if (c == NULL) {
			k_mutex_unlock(&rl);
			return;
		}
		memcpy(d, outq[out_head].d, outq[out_head].n);
		n = outq[out_head].n;
		if (!bt_gatt_is_subscribed(c, OUT_ATTR, BT_GATT_CCC_NOTIFY)) {
			/* "when the helper has subscribed to Out": no subscription, no frame */
			out_head = (out_head + 1) % OUTQ;
			out_n--;
			st.out_dropped++;
			k_mutex_unlock(&rl);
			bt_conn_unref(c);
			continue;
		}
		ep = out_epoch;
		k_mutex_unlock(&rl);
		err = bt_gatt_notify(c, OUT_ATTR, d, n);
		bt_conn_unref(c);
		k_mutex_lock(&rl, K_FOREVER);
		if (ep != out_epoch) {
			/* the queue was emptied while this frame was being sent: whatever is at the head now was queued later and is not this
			 * frame, and the retry count of the old queue is gone */
			k_mutex_unlock(&rl);
			continue;
		}
		if (err == 0 || out_try >= OUT_RETRIES) {
			if (out_n > 0) {
				out_head = (out_head + 1) % OUTQ;
				out_n--;
			}
			out_try = 0;
			if (err == 0) {
				st.out_sent++;
			} else {
				st.out_dropped++;
			}
			k_mutex_unlock(&rl);
			continue;
		}
		out_try++;
		st.out_retries++;
		k_mutex_unlock(&rl);
		(void)k_work_reschedule(&out_work, K_MSEC(50));
		return;
	}
}

/* ---------------------------------------------------------------- In */

static void refuse_locked(struct rrl_res *r, uint8_t code, uint32_t id)
{
	r->act = RRL_ACT_ERROR;
	r->err = code;
	r->id = id;
}

static ssize_t in_write(struct bt_conn *conn, const struct bt_gatt_attr *attr, const void *buf, uint16_t len, uint16_t offset,
			uint8_t flags)
{
	struct rrl_res res;
	uint8_t o[6];
	bool apple;
	int r;

	ARG_UNUSED(attr);
	if (bt_conn_get_security(conn) < BT_SECURITY_L4) {
		k_mutex_lock(&rl, K_FOREVER);
		st.sec_refused++;
		k_mutex_unlock(&rl);
		return BT_GATT_ERR(BT_ATT_ERR_AUTHENTICATION);
	}
	if (offset != 0 || (flags & BT_GATT_WRITE_FLAG_PREPARE) != 0) {
		return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET); /* a frame is one write, never a long write */
	}
	k_mutex_lock(&rl, K_FOREVER);
	if (conn != rl_conn) {
		/* the first frame of a new link: a new session */
		if (rl_conn != NULL) {
			bt_conn_unref(rl_conn);
		}
		rl_conn = bt_conn_ref(conn);
		rrl_init(&sess);
		out_reset_locked();
	}
	st.writes++;
	apple = (rip_src_of(conn) == RIP_SRC_APPLE);
	rrl_frame(&sess, apple, buf, len, &res);
	switch (res.act) {
	case RRL_ACT_HELLO:
		r = rip_relay_open(conn);
		if (r != 0) {
			/* Apple's service was found between the check and the claim: the link is an iPhone's */
			sess.hello = false;
			refuse_locked(&res, RRL_E_SOURCE, 0);
		} else {
			st.hellos++;
			/* an accepted HELLO drops every frame that still waits for Out from before it, so READY always has room */
			out_reset_locked();
			(void)q_push_locked(o, rrl_out_ready(o), true);
		}
		break;
	case RRL_ACT_PUT:
		r = rip_relay_put(conn, res.id, res.rec.category, res.rec.flags, (const char *)res.rec.text[0], res.rec.len[0],
				  (const char *)res.rec.text[1], res.rec.len[1], (const char *)res.rec.text[2], res.rec.len[2],
				  (const char *)res.rec.text[3], res.rec.len[3]);
		if (r != 0) {
			sess.hello = false;
			refuse_locked(&res, r == -EPERM ? RRL_E_SOURCE : RRL_E_NO_HELLO, res.id);
		} else {
			st.puts++;
		}
		break;
	case RRL_ACT_REMOVE:
		r = rip_relay_remove(conn, res.id);
		if (r != 0) {
			sess.hello = false;
			refuse_locked(&res, r == -EPERM ? RRL_E_SOURCE : RRL_E_NO_HELLO, res.id);
		} else {
			st.removes++;
		}
		break;
	case RRL_ACT_CLEAR:
		r = rip_relay_clear(conn);
		if (r != 0) {
			sess.hello = false;
			refuse_locked(&res, r == -EPERM ? RRL_E_SOURCE : RRL_E_NO_HELLO, 0);
		} else {
			st.clears++;
		}
		break;
	case RRL_ACT_NONE:
		st.pieces++;
		break;
	case RRL_ACT_ERROR:
	default:
		break;
	}
	if (res.act == RRL_ACT_ERROR) {
		st.refused++;
		if (res.err >= 1 && res.err <= 7) {
			st.by_code[res.err]++;
		}
		(void)q_push_locked(o, rrl_out_error(o, res.err, res.id), true);
	}
	k_mutex_unlock(&rl);
	(void)k_work_reschedule(&out_work, K_NO_WAIT);
	if (res.act == RRL_ACT_ERROR) {
		return BT_GATT_ERR(ATT_ERR_REFUSED);
	}
	return len;
}

static ssize_t info_read(struct bt_conn *conn, const struct bt_gatt_attr *attr, void *buf, uint16_t len, uint16_t offset)
{
	uint8_t d[RRL_INFO_LEN];

	if (bt_conn_get_security(conn) < BT_SECURITY_L4) {
		k_mutex_lock(&rl, K_FOREVER);
		st.sec_refused++;
		k_mutex_unlock(&rl);
		return BT_GATT_ERR(BT_ATT_ERR_AUTHENTICATION);
	}
	(void)rrl_info(d);
	return bt_gatt_attr_read(conn, attr, buf, len, offset, d, sizeof(d));
}

static void out_ccc_changed(const struct bt_gatt_attr *attr, uint16_t value)
{
	ARG_UNUSED(attr);
	printk("relay: Out notifications %s\n", value == BT_GATT_CCC_NOTIFY ? "on" : "off");
}

/* ---------------------------------------------------------------- actions (from the iPhone part, no lock of its held) */

static int relay_action(uint32_t uid, enum rip_action action)
{
	uint8_t o[6];
	int r = 0;

	k_mutex_lock(&rl, K_FOREVER);
	if (rl_conn == NULL || !sess.hello || !bt_gatt_is_subscribed(rl_conn, OUT_ATTR, BT_GATT_CCC_NOTIFY)) {
		/* no session, or the helper is not subscribed to Out: refused on the ring, nothing is sent */
		st.actions_refused++;
		r = -ENOTCONN;
	} else if (!q_push_locked(o, rrl_out_action(o, uid, action == RIP_ACTION_POSITIVE ? RRL_ACTION_POSITIVE
											   : RRL_ACTION_NEGATIVE), false)) {
		st.actions_refused++;
		r = -EBUSY;
	} else {
		st.actions_sent++;
	}
	k_mutex_unlock(&rl);
	if (r == 0) {
		(void)k_work_reschedule(&out_work, K_NO_WAIT);
	}
	return r;
}

#ifdef CONFIG_RING_RELAY_TEST_HOOKS
void rrl_test_block_out(bool on)
{
	test_block_out = on;
	if (!on) {
		(void)k_work_reschedule(&out_work, K_NO_WAIT);
	}
}
#endif

static const struct rip_relay_ops relay_ops = {
	.action = relay_action,
};

/* ---------------------------------------------------------------- the end of a link */

static void on_disconnected(struct bt_conn *conn, uint8_t reason)
{
	ARG_UNUSED(reason);
	k_mutex_lock(&rl, K_FOREVER);
	if (conn == rl_conn) {
		/* the relay's notifications live for one link; the iPhone part empties the store at the same event. A PUT that was
		 * not finished is dropped with the session. */
		st.link_ends++;
		rrl_init(&sess);
		bt_conn_unref(rl_conn);
		rl_conn = NULL;
		out_reset_locked();
	}
	k_mutex_unlock(&rl);
	(void)k_work_cancel_delayable(&out_work);
}

BT_CONN_CB_DEFINE(rrl_conn_cb) = {
	.disconnected = on_disconnected,
};

void rrl_stats_get(struct rrl_stats *out)
{
	k_mutex_lock(&rl, K_FOREVER);
	*out = st;
	k_mutex_unlock(&rl);
}

static int rrl_sys_init(void)
{
	k_work_init_delayable(&out_work, out_fn);
	rip_relay_register(&relay_ops);
	return 0;
}

SYS_INIT(rrl_sys_init, APPLICATION, 91);
