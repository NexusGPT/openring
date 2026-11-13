/* Ring control: HID over GATT glue (HID service, report sending). */

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <bluetooth/services/hids.h>

#include <ring_devices/rdev.h>
#include <ring_control/rctl.h>

/* The report lengths sum for the link context: keyboard 8, consumer 2, pointer 3. */
BT_HIDS_DEF(hids_obj, RCTL_LEN_KEYBOARD, RCTL_LEN_CONSUMER, RCTL_LEN_POINTER);

static enum rctl_mode mode = RCTL_MEDIA;
static struct rctl_options options;
static struct rctl_stats stats;
static bool active;
static K_MUTEX_DEFINE(send_lock);

/* Releases that could not be sent yet. */
static struct rctl_report pend[RCTL_MAX_REPORTS];
static struct rctl_wait wait_state;
static struct k_work_delayable retry_work;

#if IS_ENABLED(CONFIG_RING_CONTROL_TEST_HOOKS)
static int fail_releases;
void rctl_test_fail_releases(int n)
{
	fail_releases = n;
}
#endif

static void hids_connected(struct bt_conn *conn, uint8_t err)
{
	if (err == 0) {
		(void)bt_hids_connected(&hids_obj, conn);
	}
}

static void hids_disconnected(struct bt_conn *conn, uint8_t reason)
{
	ARG_UNUSED(reason);
	(void)bt_hids_disconnected(&hids_obj, conn);
}

BT_CONN_CB_DEFINE(rctl_conn_cb) = {
	.connected = hids_connected,
	.disconnected = hids_disconnected,
};

static void rctl_retry_fn(struct k_work *w);

/* A host wrote the HID control point (suspend, exit suspend). It is counted and nothing else:
 * no host write is ever a joystick input, and nothing here calls the core. */
static void cp_event(enum bt_hids_cp_evt evt, struct bt_conn *conn)
{
	ARG_UNUSED(conn);
	ARG_UNUSED(evt);
	stats.host_writes++;
}

int rctl_init(void)
{
	struct bt_hids_init_param p = { 0 };
	static const uint8_t len[RCTL_REPORT_COUNT] = { RCTL_LEN_KEYBOARD, RCTL_LEN_CONSUMER, RCTL_LEN_POINTER };
	static const uint8_t rid[RCTL_REPORT_COUNT] = { RCTL_RID_KEYBOARD, RCTL_RID_CONSUMER, RCTL_RID_POINTER };

	k_work_init_delayable(&retry_work, rctl_retry_fn);
	p.rep_map.data = rctl_report_map;
	p.rep_map.size = (uint16_t)rctl_report_map_len;
	p.info.bcd_hid = 0x0111;
	p.info.b_country_code = 0x00;
	p.info.flags = BT_HIDS_REMOTE_WAKE | BT_HIDS_NORMALLY_CONNECTABLE;
	p.conn_cp_evt_handler = cp_event;
	for (int i = 0; i < RCTL_REPORT_COUNT; i++) {
		p.inp_rep_group_init.reports[i].size = len[i];
		p.inp_rep_group_init.reports[i].id = rid[i];
		p.inp_rep_group_init.cnt++;
	}
	return bt_hids_init(&hids_obj, &p);
}

void rctl_set_mode(enum rctl_mode m)
{
	if ((unsigned int)m < RCTL_MODE_COUNT) {
		mode = m;
		printk("rctl: mode %s\n", rctl_mode_name(m));
	}
}

enum rctl_mode rctl_get_mode(void)
{
	return mode;
}

void rctl_set_options(const struct rctl_options *opt)
{
	options = *opt;
}

void rctl_set_active(bool a)
{
	active = a;
	printk("rctl: control %s\n", a ? "active" : "not active");
}

bool rctl_is_active(void)
{
	return active;
}

static bool subscribed(struct bt_conn *conn, int idx)
{
	const struct bt_gatt_attr *a = &hids_obj.gp.svc.attrs[hids_obj.inp_rep_group.reports[idx].att_ind];

	return bt_gatt_is_subscribed(conn, a, BT_GATT_CCC_NOTIFY);
}

bool rctl_ready(void)
{
	struct bt_conn *conn = rdev_active_conn();
	bool ok = false;

	if (conn != NULL) {
		ok = true;
		for (int i = 0; i < RCTL_REPORT_COUNT; i++) {
			ok = ok && subscribed(conn, i);
		}
		bt_conn_unref(conn);
	}
	return ok;
}

static int send_one(struct bt_conn *conn, const struct rctl_report *r, bool is_release)
{
#if IS_ENABLED(CONFIG_RING_CONTROL_TEST_HOOKS)
	if (is_release && fail_releases > 0) {
		fail_releases--;
		return -EIO;
	}
#else
	ARG_UNUSED(is_release);
#endif
	stats.wire_sends++;
	return bt_hids_inp_rep_send(&hids_obj, conn, r->index, r->data, r->len, NULL);
}

/* Try to send the waiting releases to the active device, in order. Called with send_lock held. */
static void flush_pending(void)
{
	struct bt_conn *conn;

	if (wait_state.npend == 0) {
		return;
	}
	conn = rdev_active_conn();
	if (conn == NULL) {
		/* the link is gone: the host drops a key that was down when the link ends */
		stats.release_lost += (uint32_t)wait_state.npend;
		rctl_wait_start(&wait_state, 0);
		return;
	}
	while (wait_state.npend > 0) {
		if (send_one(conn, &pend[0], true) != 0) {
			break;
		}
		stats.release_retries++;
		stats.reports++;
		rctl_wait_released(&wait_state, 1);
		memmove(&pend[0], &pend[1], sizeof(pend[0]) * (size_t)wait_state.npend);
	}
	bt_conn_unref(conn);
}

static void rctl_retry_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	k_mutex_lock(&send_lock, K_FOREVER);
	flush_pending();
	switch (rctl_wait_retry(&wait_state)) {
	case RCTL_RETRY_AGAIN:
		(void)k_work_reschedule(&retry_work, K_MSEC(RCTL_RETRY_MS));
		break;
	case RCTL_RETRY_GIVE_UP:
		stats.release_lost++;
		printk("rctl: release given up after %d tries\n", RCTL_RETRY_MAX);
		break;
	default:
		break;
	}
	k_mutex_unlock(&send_lock);
}

bool rctl_release_pending(void)
{
	return !rctl_wait_admit(&wait_state);
}

static int send_action(struct bt_conn *conn, enum rctl_action action)
{
	struct rctl_report r[RCTL_MAX_REPORTS];
	size_t n = rctl_build(mode, action, &options, r);
	int sent = 0;

	if (n == 0) {
		return 0;
	}
	if (!subscribed(conn, r[0].index)) {
		stats.dropped++;
		return -EACCES;
	}
	for (size_t i = 0; i < n; i++) {
		int err = send_one(conn, &r[i], i > 0);

		if (err != 0) {
			stats.errors++;
			printk("rctl: send failed %d (%s %s, report %zu)\n", err, rctl_mode_name(mode),
			       rctl_action_name(action), i);
			if (i > 0) {
				/* the press went out: the release must follow, later */
				memcpy(pend, &r[i], sizeof(r[0]) * (n - i));
				rctl_wait_start(&wait_state, (int)(n - i));
				(void)k_work_reschedule(&retry_work, K_MSEC(RCTL_RETRY_MS));
			}
			return sent > 0 ? sent : err;
		}
		sent++;
		stats.reports++;
	}
	return sent;
}

int rctl_action(enum rctl_action action)
{
	struct bt_conn *conn;
	int r;

	k_mutex_lock(&send_lock, K_FOREVER);
	stats.actions++;
	if (!active) {
		k_mutex_unlock(&send_lock);
		return -EPERM;
	}
	flush_pending();
	if (!rctl_wait_admit(&wait_state)) {
		stats.dropped++;
		k_mutex_unlock(&send_lock);
		return -EBUSY;
	}
	conn = rdev_active_conn();
	if (conn == NULL) {
		stats.dropped++;
		k_mutex_unlock(&send_lock);
		return -ENOTCONN;
	}
	r = send_action(conn, action);
	bt_conn_unref(conn);
	k_mutex_unlock(&send_lock);
	return r;
}

int rctl_core_actions(const struct rc_actions *a)
{
	int total = 0;

	for (uint8_t i = 0; i < a->n; i++) {
		enum rctl_action act;

		if (rctl_core_filter(active, a->a[i], &act)) {
			int r = rctl_action(act);

			if (r > 0) {
				total += r;
			}
		}
	}
	return total;
}

void rctl_stats_get(struct rctl_stats *s)
{
	*s = stats;
}

#if IS_ENABLED(CONFIG_RING_CONTROL_TEST_HOOKS)
int rctl_test_send_to(struct bt_conn *conn, enum rctl_action action)
{
	int r;

	k_mutex_lock(&send_lock, K_FOREVER);
	r = send_action(conn, action);
	k_mutex_unlock(&send_lock);
	return r;
}
#endif
