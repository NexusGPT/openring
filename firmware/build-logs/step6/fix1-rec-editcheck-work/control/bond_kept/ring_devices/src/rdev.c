/*
 * Ring devices: Bluetooth part. Pairing with a displayed passkey, three local
 * identities (one per paired device), the active device, switching,
 * reconnect, removal.
 *
 * Model (design.md section 3 "Devices"; nRF Desktop ble_bond.rst lines 48-58):
 * slot n is local identity n. A device pairs on the identity of the slot
 * the ring advertised with, so each identity holds one bond. To switch device
 * the ring ends the link, changes identity and advertises to the chosen one.
 *
 * All decisions are made by rdev_plan_next() (rdev_logic.c) from one state
 * record; update_fn() runs the plan. State changes happen under one mutex.
 */

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/gap.h>
#include <zephyr/bluetooth/hci.h>
#include <zephyr/bluetooth/uuid.h>
#include <zephyr/settings/settings.h>

#include <ring_devices/rdev.h>

#define FAST_ADV_MS   (CONFIG_RING_DEVICES_FAST_ADV_S * 1000)
#define ADV_FAST_UNIT 160   /* 100 ms in 0.625 ms units: pairing window and the first seconds after a drop */
#define ADV_SLOW_UNIT 1600  /* 1,000 ms: FW 7.3 */

static K_MUTEX_DEFINE(lk);
static struct rdev_callbacks cb;
static struct rdev_list list;
static bool window;
static uint8_t window_slot = RDEV_NONE;

static struct bt_conn *cur_conn;
static uint8_t link_slot = RDEV_NONE;
static bool link_secure;
static bool link_reported;
static bool disconnecting;

static bool inited;
static bool stopped;   /* rdev_stop() (ship mode step 1): no advertising and no link from now on */
static bool adv_on;
static uint8_t adv_slot = RDEV_NONE;
static bool adv_open;
static int64_t fast_until;

static struct k_work_delayable update_work;
static struct k_work_delayable window_work;
static struct k_work_delayable slow_work;

static const struct bt_data ad[] = {
	BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
	BT_DATA_BYTES(BT_DATA_GAP_APPEARANCE, (CONFIG_BT_DEVICE_APPEARANCE & 0xff),
		      (CONFIG_BT_DEVICE_APPEARANCE >> 8)),
	/* Apple: "the accessory shall advertise the HID Service in the Advertising Data" */
	BT_DATA_BYTES(BT_DATA_UUID16_ALL, BT_UUID_16_ENCODE(BT_UUID_HIDS_VAL)),
};
static const struct bt_data sd[] = {
	BT_DATA(BT_DATA_NAME_COMPLETE, CONFIG_BT_DEVICE_NAME, sizeof(CONFIG_BT_DEVICE_NAME) - 1),
};

/* ---- helpers ---- */

struct peer_find {
	bt_addr_le_t addr;
	bool found;
};

static void bond_cb(const struct bt_bond_info *info, void *user)
{
	struct peer_find *p = user;

	if (!p->found) {
		p->addr = info->addr;
		p->found = true;
	}
}

int rdev_slot_peer(uint8_t slot, bt_addr_le_t *addr)
{
	struct peer_find p = { .found = false };

	if (slot >= RDEV_SLOTS) {
		return -EINVAL;
	}
	bt_foreach_bond(slot, bond_cb, &p);
	if (!p.found) {
		return -ENOENT;
	}
	if (addr != NULL) {
		*addr = p.addr;
	}
	return 0;
}

/* The paired mask follows the Bluetooth bonds: a slot is paired when its identity has a bond. */
static void refresh_paired(void)
{
	list.paired = 0;
	for (uint8_t i = 0; i < RDEV_SLOTS; i++) {
		if (rdev_slot_peer(i, NULL) == 0) {
			list.paired |= (uint8_t)(1U << i);
		}
	}
}

static void save_active(void)
{
#if IS_ENABLED(CONFIG_SETTINGS)
	uint8_t a = list.active;

	(void)settings_save_one("ring/dev/active", &a, sizeof(a));
#endif
}

static void submit_update(k_timeout_t delay)
{
	(void)k_work_reschedule(&update_work, delay);
}

static bool link_is_up(void)
{
	return cur_conn != NULL && rdev_link_usable(link_slot, link_secure, list.active);
}

/* Called with lk held; fires the link callback outside the lock through the returned flag. */
static bool link_changed(bool *up)
{
	bool now = link_is_up();

	if (now == link_reported) {
		return false;
	}
	link_reported = now;
	*up = now;
	return true;
}

static void fire_link(uint8_t slot, bool changed, bool up)
{
	if (changed && cb.link != NULL) {
		cb.link(slot, up);
	}
}

static void adv_stop(void)
{
	if (adv_on) {
		int err = bt_le_adv_stop();

		if (err != 0) {
			printk("rdev: adv stop failed %d\n", err);
		}
		adv_on = false;
	}
}

static void adv_start(uint8_t slot, bool open)
{
	bool fast = open || k_uptime_get() < fast_until;
	uint16_t unit = fast ? ADV_FAST_UNIT : ADV_SLOW_UNIT;
	struct bt_le_adv_param prm = BT_LE_ADV_PARAM_INIT(BT_LE_ADV_OPT_CONN, unit, unit, NULL);
	int err;

	prm.id = slot;
	err = bt_le_adv_start(&prm, ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));
	if (err != 0) {
		printk("rdev: adv start failed %d (slot %u), retry\n", err, slot);
		submit_update(K_MSEC(500));
		return;
	}
	adv_on = true;
	adv_slot = slot;
	adv_open = open;
	printk("rdev: advertising slot %u %s, interval %u ms\n", slot, open ? "open (pairing)" : "to the bonded device",
	       fast ? 100U : 1000U);
	if (!open && fast) {
		(void)k_work_reschedule(&slow_work, K_MSEC(MAX(fast_until - k_uptime_get(), 1)));
	}
}

static void update_fn(struct k_work *w)
{
	struct rdev_state st;
	struct rdev_plan p;

	ARG_UNUSED(w);
	k_mutex_lock(&lk, K_FOREVER);
	if (stopped) {
		adv_stop();
		k_mutex_unlock(&lk);
		return;
	}
	st.active = list.active;
	st.window = window;
	st.window_slot = window_slot;
	st.link_slot = cur_conn != NULL ? link_slot : RDEV_NONE;
	p = rdev_plan_next(&st);
	switch (p.step) {
	case RDEV_STEP_DISCONNECT:
		adv_stop();
		if (!disconnecting && cur_conn != NULL) {
			int err = bt_conn_disconnect(cur_conn, BT_HCI_ERR_REMOTE_USER_TERM_CONN);

			printk("rdev: disconnect link of slot %u (%d)\n", link_slot, err);
			disconnecting = (err == 0);
		}
		break;
	case RDEV_STEP_ADVERTISE:
		if (adv_on && (adv_slot != p.slot || adv_open != p.open)) {
			adv_stop();
		}
		if (!adv_on) {
			adv_start(p.slot, p.open);
		}
		break;
	case RDEV_STEP_IDLE:
	case RDEV_STEP_STAY:
	default:
		adv_stop();
		break;
	}
	k_mutex_unlock(&lk);
}

static void slow_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	k_mutex_lock(&lk, K_FOREVER);
	if (adv_on && !adv_open) {
		adv_stop();  /* restart with the slow interval */
	}
	k_mutex_unlock(&lk);
	submit_update(K_NO_WAIT);
}

static void window_fn(struct k_work *w)
{
	bool was;

	ARG_UNUSED(w);
	k_mutex_lock(&lk, K_FOREVER);
	was = window;
	window = false;
	window_slot = RDEV_NONE;
	fast_until = k_uptime_get() + FAST_ADV_MS;
	k_mutex_unlock(&lk);
	if (was) {
		printk("rdev: pairing window closed (time)\n");
		if (cb.passkey_hide != NULL) {
			cb.passkey_hide(RDEV_NONE);
		}
		if (cb.window_closed != NULL) {
			cb.window_closed();
		}
	}
	submit_update(K_NO_WAIT);
}

/* ---- connection callbacks ---- */

static void on_connected(struct bt_conn *conn, uint8_t err)
{
	struct bt_conn_info info;
	bt_addr_le_t bonded;
	bool stranger = false;

	if (!inited) {
		return;
	}
	if (err != 0) {
		printk("rdev: connect failed 0x%02x\n", err);
		k_mutex_lock(&lk, K_FOREVER);
		adv_on = false;
		k_mutex_unlock(&lk);
		submit_update(K_MSEC(100));
		return;
	}
	if (bt_conn_get_info(conn, &info) != 0) {
		/* the link is not known to this module: end it, and ask again so that advertising
		 * restarts once the link is gone (the retry in adv_start waits for a free link) */
		(void)bt_conn_disconnect(conn, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
		k_mutex_lock(&lk, K_FOREVER);
		adv_on = false;
		k_mutex_unlock(&lk);
		submit_update(K_MSEC(200));
		return;
	}
	k_mutex_lock(&lk, K_FOREVER);
	adv_on = false;
	if (cur_conn != NULL) {
		k_mutex_unlock(&lk);  /* one link at a time: not expected with BT_MAX_CONN 1 */
		return;
	}
	cur_conn = bt_conn_ref(conn);
	link_slot = info.id;
	link_secure = false;
	disconnecting = false;
	/* Outside the pairing window only the device of this slot may stay. */
	if (!(window && window_slot == link_slot)) {
		stranger = !(rdev_slot_peer(link_slot, &bonded) == 0 &&
			     bt_addr_le_eq(&bonded, bt_conn_get_dst(conn)));
	}
	printk("rdev: connected on slot %u%s\n", link_slot, stranger ? ", not the bonded device: refused" : "");
	if (stranger) {
		/* the flag is set only when the call worked, so update_fn tries again after a failure */
		disconnecting = (bt_conn_disconnect(cur_conn, BT_HCI_ERR_REMOTE_USER_TERM_CONN) == 0);
	}
	k_mutex_unlock(&lk);
	submit_update(K_NO_WAIT);
}

static void on_disconnected(struct bt_conn *conn, uint8_t reason)
{
	uint8_t slot;
	bool ch, up = false;

	k_mutex_lock(&lk, K_FOREVER);
	if (conn != cur_conn) {
		k_mutex_unlock(&lk);
		return;
	}
	slot = link_slot;
	printk("rdev: disconnected slot %u, reason 0x%02x\n", slot, reason);
	bt_conn_unref(cur_conn);
	cur_conn = NULL;
	link_slot = RDEV_NONE;
	link_secure = false;
	disconnecting = false;
	adv_on = false;
	fast_until = k_uptime_get() + FAST_ADV_MS;  /* reconnect: advertise fast first */
	ch = link_changed(&up);
	k_mutex_unlock(&lk);
	fire_link(slot, ch, up);
	if (cb.passkey_hide != NULL) {
		cb.passkey_hide(slot);
	}
	submit_update(K_NO_WAIT);
}

static void on_security_changed(struct bt_conn *conn, bt_security_t level, enum bt_security_err err)
{
	uint8_t slot;
	bool ch, up = false;

	k_mutex_lock(&lk, K_FOREVER);
	if (conn != cur_conn) {
		k_mutex_unlock(&lk);
		return;
	}
	slot = link_slot;
	printk("rdev: security slot %u level %u err %d\n", slot, level, err);
	link_secure = (err == 0 && level >= BT_SECURITY_L4);
	ch = link_changed(&up);
	k_mutex_unlock(&lk);
	fire_link(slot, ch, up);
}

BT_CONN_CB_DEFINE(rdev_conn_cb) = {
	.connected = on_connected,
	.disconnected = on_disconnected,
	.security_changed = on_security_changed,
};

/* ---- pairing ---- */

static enum bt_security_err on_pairing_accept(struct bt_conn *conn, const struct bt_conn_pairing_feat *const feat)
{
	bool ok;

	ARG_UNUSED(feat);
	k_mutex_lock(&lk, K_FOREVER);
	ok = window && conn == cur_conn && link_slot == window_slot;
	k_mutex_unlock(&lk);
	printk("rdev: pairing request %s\n", ok ? "accepted" : "refused (window closed)");
	return ok ? BT_SECURITY_ERR_SUCCESS : BT_SECURITY_ERR_PAIR_NOT_ALLOWED;
}

static void on_passkey_display(struct bt_conn *conn, unsigned int passkey)
{
	uint8_t slot;

	k_mutex_lock(&lk, K_FOREVER);
	slot = (conn == cur_conn) ? link_slot : RDEV_NONE;
	k_mutex_unlock(&lk);
	printk("rdev: passkey for slot %u shown: %06u\n", slot, passkey);
	if (cb.passkey_show != NULL) {
		cb.passkey_show(slot, passkey);
	}
}

static void on_pairing_cancel(struct bt_conn *conn)
{
	uint8_t slot;

	k_mutex_lock(&lk, K_FOREVER);
	slot = (conn == cur_conn) ? link_slot : RDEV_NONE;
	k_mutex_unlock(&lk);
	printk("rdev: pairing cancelled slot %u\n", slot);
	if (cb.passkey_hide != NULL) {
		cb.passkey_hide(slot);
	}
}

static struct bt_conn_auth_cb auth_cb = {
	.pairing_accept = on_pairing_accept,
	.passkey_display = on_passkey_display,
	.cancel = on_pairing_cancel,
};

static void on_pairing_complete(struct bt_conn *conn, bool bonded)
{
	uint8_t slot = RDEV_NONE;
	bool ok = false, ch, up = false, took = false;

	k_mutex_lock(&lk, K_FOREVER);
	if (conn == cur_conn && window && link_slot == window_slot && bonded) {
		slot = link_slot;
		refresh_paired();
		if (rdev_list_is_paired(&list, slot)) {
			/* the new device becomes the active one only when no device is active; otherwise the active device
			 * stays and no active_changed fires (the link of the new device ends: the plan advertises to the
			 * active device again) */
			if (list.active == RDEV_NONE) {
				list.active = slot;
				took = true;
				save_active();
			}
			window = false;
			window_slot = RDEV_NONE;
			ok = true;
		}
	}
	ch = link_changed(&up);
	k_mutex_unlock(&lk);
	printk("rdev: pairing complete bonded=%d slot %u %s\n", bonded, slot, ok ? (took ? "paired, active" : "paired, the active device stays") : "(not a new pairing)");
	if (ok) {
		(void)k_work_cancel_delayable(&window_work);
		if (cb.passkey_hide != NULL) {
			cb.passkey_hide(slot);
		}
		if (cb.paired != NULL) {
			cb.paired(slot);
		}
		if (took && cb.active_changed != NULL) {
			cb.active_changed(slot);
		}
	}
	fire_link(slot, ch, up);
	submit_update(K_NO_WAIT);
}

static void on_pairing_failed(struct bt_conn *conn, enum bt_security_err reason)
{
	uint8_t slot;

	k_mutex_lock(&lk, K_FOREVER);
	slot = (conn == cur_conn) ? link_slot : RDEV_NONE;
	k_mutex_unlock(&lk);
	printk("rdev: pairing failed slot %u reason %d\n", slot, reason);
	if (cb.passkey_hide != NULL) {
		cb.passkey_hide(slot);
	}
	if (cb.pairing_failed != NULL) {
		cb.pairing_failed(slot, reason);
	}
}

static struct bt_conn_auth_info_cb info_cb = {
	.pairing_complete = on_pairing_complete,
	.pairing_failed = on_pairing_failed,
};

/* ---- settings: the active slot survives a reset ---- */

static int saved_active = RDEV_NONE;

#if IS_ENABLED(CONFIG_SETTINGS)
static int settings_set_cb(const char *name, size_t len, settings_read_cb read_cb, void *cb_arg)
{
	uint8_t a;

	if (strcmp(name, "active") == 0 && len == sizeof(a) && read_cb(cb_arg, &a, sizeof(a)) == sizeof(a)) {
		saved_active = a;
	}
	return 0;
}
SETTINGS_STATIC_HANDLER_DEFINE(ring_dev, "ring/dev", NULL, settings_set_cb, NULL, NULL);
#endif

/* ---- public API ---- */

/* Step 6 fix round 1 (review finding R6-02, FW l.937 "close ... radio"): ship mode step 1. Advertising stops, the link
 * is ended, and nothing advertises again (update_fn returns at once). Advertising of another part (the factory ship
 * beacon of ruling R20, rhw_beacon) is not touched: adv_stop() acts only on this part's own advertising. */
int rdev_stop(void)
{
	int err = 0;

	k_mutex_lock(&lk, K_FOREVER);
	stopped = true;
	adv_stop();
	if (cur_conn != NULL && !disconnecting) {
		err = bt_conn_disconnect(cur_conn, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
		disconnecting = (err == 0);
	}
	k_mutex_unlock(&lk);
	return err;
}

int rdev_init(const struct rdev_callbacks *callbacks)
{
	bt_addr_le_t addrs[RDEV_SLOTS];
	size_t count = RDEV_SLOTS;
	int err;

	memset(&cb, 0, sizeof(cb));
	if (callbacks != NULL) {
		cb = *callbacks;
	}
	rdev_list_init(&list);
	k_work_init_delayable(&update_work, update_fn);
	k_work_init_delayable(&window_work, window_fn);
	k_work_init_delayable(&slow_work, slow_fn);

	err = bt_conn_auth_cb_register(&auth_cb);
	if (err != 0) {
		return err;
	}
	err = bt_conn_auth_info_cb_register(&info_cb);
	if (err != 0) {
		return err;
	}
	err = bt_enable(NULL);
	if (err != 0) {
		printk("rdev: bt_enable failed %d\n", err);
		return err;
	}
	if (IS_ENABLED(CONFIG_BT_SETTINGS)) {
		(void)settings_load();
	}

	/* One identity per slot: identity 0 is the default; 1 and 2 are made once and kept in settings. */
	bt_id_get(addrs, &count);
	for (size_t i = count; i < RDEV_SLOTS; i++) {
		int id = bt_id_create(NULL, NULL);

		if (id < 0 || (size_t)id != i) {
			printk("rdev: identity %zu not created (%d)\n", i, id);
			return id < 0 ? id : -EIO;
		}
	}

	k_mutex_lock(&lk, K_FOREVER);
	refresh_paired();
	if (saved_active < RDEV_SLOTS && rdev_list_is_paired(&list, (uint8_t)saved_active)) {
		list.active = (uint8_t)saved_active;
	} else {
		for (uint8_t i = 0; i < RDEV_SLOTS; i++) {
			if (rdev_list_is_paired(&list, i)) {
				list.active = i;
				break;
			}
		}
	}
	fast_until = k_uptime_get() + FAST_ADV_MS;
	inited = true;
	printk("rdev: ready, paired mask 0x%02x, active %u\n", list.paired, list.active);
	k_mutex_unlock(&lk);
	submit_update(K_NO_WAIT);
	return 0;
}

int rdev_pair_open(uint8_t slot, uint32_t timeout_ms)
{
	int s;

	k_mutex_lock(&lk, K_FOREVER);
	refresh_paired();
	s = rdev_list_choose_pair_slot(&list, slot);
	if (s < 0) {
		k_mutex_unlock(&lk);
		return s;
	}
	window = true;
	window_slot = (uint8_t)s;
	k_mutex_unlock(&lk);
	(void)k_work_reschedule(&window_work, K_MSEC(timeout_ms));
	printk("rdev: pairing window open for slot %d, %u ms\n", s, timeout_ms);
	submit_update(K_NO_WAIT);
	return 0;
}

void rdev_pair_cancel(void)
{
	bool was;

	k_mutex_lock(&lk, K_FOREVER);
	was = window;
	window = false;
	window_slot = RDEV_NONE;
	fast_until = k_uptime_get() + FAST_ADV_MS;
	k_mutex_unlock(&lk);
	(void)k_work_cancel_delayable(&window_work);
	if (was) {
		printk("rdev: pairing window cancelled\n");
		if (cb.passkey_hide != NULL) {
			cb.passkey_hide(RDEV_NONE);
		}
		if (cb.window_closed != NULL) {
			cb.window_closed();
		}
	}
	submit_update(K_NO_WAIT);
}

bool rdev_pair_window_open(void)
{
	return window;
}

int rdev_switch(uint8_t slot)
{
	enum rdev_switch d;
	bool ch, up = false, closed_window = false;
	uint8_t old;

	k_mutex_lock(&lk, K_FOREVER);
	refresh_paired();
	old = list.active;
	d = rdev_list_switch(&list, slot);
	if (d == RDEV_SWITCH_REFUSE_RANGE) {
		k_mutex_unlock(&lk);
		return -EINVAL;
	}
	if (d == RDEV_SWITCH_REFUSE_EMPTY) {
		k_mutex_unlock(&lk);
		return -ENOENT;
	}
	if (window) {
		window = false;
		window_slot = RDEV_NONE;
		closed_window = true;
	}
	if (d == RDEV_SWITCH_GO) {
		save_active();
		fast_until = k_uptime_get() + FAST_ADV_MS;
	}
	ch = link_changed(&up);
	k_mutex_unlock(&lk);
	printk("rdev: switch to slot %u from %u: %s\n", slot, old, d == RDEV_SWITCH_GO ? "go" : "no change");
	if (closed_window) {
		(void)k_work_cancel_delayable(&window_work);
		if (cb.passkey_hide != NULL) {
			cb.passkey_hide(RDEV_NONE);
		}
		if (cb.window_closed != NULL) {
			cb.window_closed();
		}
	}
	fire_link(old, ch, up);
	if (d == RDEV_SWITCH_GO && cb.active_changed != NULL) {
		cb.active_changed(slot);
	}
	submit_update(K_NO_WAIT);
	return 0;
}

int rdev_switch_next(void)
{
	uint8_t n;

	k_mutex_lock(&lk, K_FOREVER);
	refresh_paired();
	n = rdev_list_next(&list, list.active == RDEV_NONE ? 0 : list.active);
	if (n == RDEV_NONE && list.active == RDEV_NONE && rdev_list_is_paired(&list, 0)) {
		n = 0;
	}
	k_mutex_unlock(&lk);
	if (n == RDEV_NONE) {
		return -ENOENT;
	}
	return rdev_switch(n);
}

int rdev_remove(uint8_t slot)
{
	bt_addr_le_t peer;
	uint8_t before, after;
	int err, guard = 0;
	bool ch, up = false;

	if (slot >= RDEV_SLOTS) {
		return -EINVAL;
	}
	k_mutex_lock(&lk, K_FOREVER);
	refresh_paired();
	if (!rdev_list_is_paired(&list, slot)) {
		k_mutex_unlock(&lk);
		return -ENOENT;
	}
	before = list.active;
	/* bt_unpair() ends a link with the peer and deletes the bond: the keys of both sides, the peer's
	 * and the ring's own (one record in the Bluetooth host), and the stored notification settings. */
	while (rdev_slot_peer(slot, &peer) == 0 && guard++ < RDEV_SLOTS) {
		err = 0;
		if (err != 0) {
			printk("rdev: bt_unpair slot %u failed %d\n", slot, err);
			k_mutex_unlock(&lk);
			return err;
		}
	}
	(void)rdev_list_remove(&list, slot);
	refresh_paired();
	after = list.active;
	if (after != before) {
		save_active();
	}
	fast_until = k_uptime_get() + FAST_ADV_MS;
	ch = link_changed(&up);
	k_mutex_unlock(&lk);
	printk("rdev: slot %u removed, active %u -> %u\n", slot, before, after);
	fire_link(slot, ch, up);
	if (cb.removed != NULL) {
		cb.removed(slot);
	}
	if (after != before && cb.active_changed != NULL) {
		cb.active_changed(after);
	}
	submit_update(K_NO_WAIT);
	return 0;
}

uint8_t rdev_active(void)
{
	uint8_t a;

	k_mutex_lock(&lk, K_FOREVER);
	a = list.active;
	k_mutex_unlock(&lk);
	return a;
}

uint8_t rdev_paired_mask(void)
{
	uint8_t m;

	k_mutex_lock(&lk, K_FOREVER);
	refresh_paired();
	m = list.paired;
	k_mutex_unlock(&lk);
	return m;
}

bool rdev_link_up(void)
{
	bool up;

	k_mutex_lock(&lk, K_FOREVER);
	up = link_is_up();
	k_mutex_unlock(&lk);
	return up;
}

struct bt_conn *rdev_active_conn(void)
{
	struct bt_conn *c = NULL;

	k_mutex_lock(&lk, K_FOREVER);
	if (link_is_up() && bt_conn_get_security(cur_conn) >= BT_SECURITY_L4) {
		c = bt_conn_ref(cur_conn);
	}
	k_mutex_unlock(&lk);
	return c;
}
