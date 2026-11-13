/*
 * Ring iPhone part, Bluetooth side. See rip.h.
 *
 * Flow per link of the active device (the ring is the GATT client, the iPhone the server):
 *   security level 4 reached -> session starts (rdev_active_conn() names the link)
 *   P_GATTP  find the GATT service, subscribe to Service Changed        (kit gattp)
 *   P_ANCS   find the Notification Center Service, subscribe to the Data Source (own) and to the
 *            Notification Source (kit); the iPhone then sends what it holds
 *   P_AMS    find the Media Service, subscribe to Entity Update, ask for the player's playback info
 *            and the track's artist and title                          (kit ams)
 *   P_CTS    find the Current Time Service, subscribe, read             (kit cts)
 *   Service Changed indicated -> stop the three services (the inbox is emptied: a notification session
 *            ends when the client unsubscribes), then look for the services again from P_ANCS.
 *   link ends -> everything stored from the iPhone is emptied.
 * A service that is not found is "missing": not an error.
 *
 * Locks: one mutex (lk) guards the inbox, the media record and the flags. No Bluetooth call is made
 * while it is held, except bt_conn_ref bookkeeping that cannot block.
 */

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/uuid.h>
#include <bluetooth/gatt_dm.h>
#include <bluetooth/services/ancs_client.h>
#include <bluetooth/services/ams_client.h>
#include <bluetooth/services/cts_client.h>
#include <bluetooth/services/gattp.h>

#include <ring_devices/rdev.h>
#include <ring_inbox/rinbox.h>
#include <ring_iphone/rip.h>
#include <ring_iphone/ripl.h>
#include <ring_time/rtime.h>

/* design/firmware.md 7.1: ATT MTU 247. An application that does not include modules/ring_iphone/ring_iphone_link.conf cannot build. */
BUILD_ASSERT(CONFIG_BT_L2CAP_TX_MTU >= 247, "ring_iphone needs CONFIG_BT_L2CAP_TX_MTU >= 247 (include modules/ring_iphone/ring_iphone_link.conf)");

#define FETCH_Q CONFIG_RING_IPHONE_FETCH_QUEUE
#define FETCH_TIMEOUT_MS 3000
#define DM_RETRY_MAX 5
#define READY_TRIES_MAX 10

enum phase { P_IDLE, P_GATTP, P_ANCS, P_AMS, P_CTS, P_DONE };

static K_MUTEX_DEFINE(lk);
static bool inited;

static struct bt_conn *sconn;    /* the session's link (a reference), NULL when no session */
static enum phase phase;
static bool dm_busy;
static uint8_t dm_retries;
static bool sc_pending;
static uint32_t session_gen; /* number of the current session: a discovery of an older one is stale */
static uint8_t ready_tries;

static struct bt_gattp gattp;
static bool gattp_ready;
static struct bt_ancs_client ancs_c;
static bool ancs_ready;
static bool ds_subscribed;
static struct bt_gatt_subscribe_params ds_params;
static struct bt_ams_client ams_c;
static bool ams_ready;
static struct bt_cts_client cts_c;
static bool cts_ready;

static struct rinbox inbox;
static struct ripl_media media;
static struct rip_stats st;

/* attributes fetch */
static uint32_t fq[FETCH_Q];
static uint8_t fq_try[FETCH_Q]; /* 0: first request, 1: the retry */
static uint8_t fq_head, fq_n;
static bool fetch_busy;
static uint32_t cur_uid;  /* the request in flight */
static uint8_t cur_try;
static struct ripl_ds ds;
static uint8_t req[RIPL_REQ_LEN];
static struct bt_gatt_write_params fetch_wp;

static struct k_work_delayable ready_work;
static struct k_work_delayable step_work;
static struct k_work_delayable fetch_work;
static struct k_work_delayable fetch_to_work;

/* ---------------------------------------------------------------- helpers */

static void fq_clear(void)
{
	fq_head = 0;
	fq_n = 0;
	fetch_busy = false;
}

static bool fq_has(uint32_t uid)
{
	for (uint8_t i = 0; i < fq_n; i++) {
		if (fq[(fq_head + i) % FETCH_Q] == uid) {
			return true;
		}
	}
	return false;
}

static void fq_push(uint32_t uid)
{
	if (fq_has(uid)) {
		return;
	}
	if (fq_n >= FETCH_Q) {
		st.fetch_overflow++;
		return;
	}
	fq[(fq_head + fq_n) % FETCH_Q] = uid;
	fq_try[(fq_head + fq_n) % FETCH_Q] = 0;
	fq_n++;
}

/* The request in flight failed (no answer in time, a wrong answer, a failed write). A request that failed once is
 * asked for again, at the front of the queue, once; a second failure gives it up (counted). Called with lk held. */
static void fetch_failed_locked(void)
{
	fetch_busy = false;
	if (cur_try == 0 && !fq_has(cur_uid) && fq_n < FETCH_Q && rinbox_find(&inbox, cur_uid) >= 0) {
		fq_head = (uint8_t)((fq_head + FETCH_Q - 1) % FETCH_Q);
		fq[fq_head] = cur_uid;
		fq_try[fq_head] = 1;
		fq_n++;
		st.fetch_retries++;
	} else {
		st.fetch_failed++;
	}
}

static void inbox_empty_locked(void)
{
	if (rinbox_count(&inbox) > 0) {
		st.inbox_cleared++;
	}
	rinbox_clear(&inbox);
	fq_clear();
}

/* ---------------------------------------------------------------- notification source */

static void ns_cb(struct bt_ancs_client *c, int err, const struct bt_ancs_evt_notif *n)
{
	bool fetch = false;

	ARG_UNUSED(c);
	k_mutex_lock(&lk, K_FOREVER);
	if (err != 0) {
		st.ns_bad++;
		k_mutex_unlock(&lk);
		return;
	}
	{
		uint8_t flags = 0;
		uint32_t dropped = 0;

		flags |= n->evt_flags.silent ? RINBOX_F_SILENT : 0;
		flags |= n->evt_flags.important ? RINBOX_F_IMPORTANT : 0;
		flags |= n->evt_flags.pre_existing ? RINBOX_F_PREEXISTING : 0;
		flags |= n->evt_flags.positive_action ? RINBOX_F_POSITIVE : 0;
		flags |= n->evt_flags.negative_action ? RINBOX_F_NEGATIVE : 0;
		switch (n->evt_id) {
		case BT_ANCS_EVENT_ID_NOTIFICATION_ADDED:
			st.ns_added++;
			if (rinbox_add(&inbox, n->notif_uid, (uint8_t)n->category_id, flags, &dropped) != 0) {
				st.inbox_dropped++;
			}
			fetch = true;
			break;
		case BT_ANCS_EVENT_ID_NOTIFICATION_MODIFIED:
			if (rinbox_modify(&inbox, n->notif_uid, (uint8_t)n->category_id, flags) == 0) {
				st.ns_modified++;
				fetch = true;
			} else {
				/* not held (pushed out by newer ones, or never added): ignored */
				st.ns_modified_unknown++;
			}
			break;
		case BT_ANCS_EVENT_ID_NOTIFICATION_REMOVED:
			st.ns_removed++;
			(void)rinbox_remove(&inbox, n->notif_uid);
			break;
		default:
			st.ns_bad++;
			break;
		}
		if (fetch) {
			fq_push(n->notif_uid);
		}
	}
	k_mutex_unlock(&lk);
	if (fetch) {
		(void)k_work_reschedule(&fetch_work, K_NO_WAIT);
	}
}

/* ---------------------------------------------------------------- data source and fetch */

static uint8_t ds_notify(struct bt_conn *conn, struct bt_gatt_subscribe_params *params, const void *data,
			 uint16_t length)
{
	enum ripl_ds_result r;
	bool next = false;
	uint32_t skipped_before;

	ARG_UNUSED(conn);
	ARG_UNUSED(params);
	if (data == NULL) {
		return BT_GATT_ITER_STOP; /* unsubscribed */
	}
	k_mutex_lock(&lk, K_FOREVER);
	if (!fetch_busy) {
		k_mutex_unlock(&lk);
		return BT_GATT_ITER_CONTINUE; /* a late fragment of an abandoned request */
	}
	skipped_before = ds.skipped;
	r = ripl_ds_feed(&ds, data, length);
	st.ds_skipped += ds.skipped - skipped_before;
	if (r == RIPL_DS_DONE) {
		st.fetch_done++;
		(void)rinbox_set_text(&inbox, ds.uid, ds.app, ds.kept[0], ds.title, ds.kept[1], ds.msg, ds.kept[2],
				      ds.date, ds.kept[3]);
		fetch_busy = false;
		next = true;
	} else if (r == RIPL_DS_ERROR) {
		st.fetch_errors++;
		fetch_failed_locked();
		next = true;
	}
	k_mutex_unlock(&lk);
	if (next) {
		(void)k_work_cancel_delayable(&fetch_to_work);
		(void)k_work_reschedule(&fetch_work, K_NO_WAIT);
	}
	return BT_GATT_ITER_CONTINUE;
}

static void fetch_write_cb(struct bt_conn *conn, uint8_t err, struct bt_gatt_write_params *params)
{
	ARG_UNUSED(conn);
	ARG_UNUSED(params);
	if (err != 0) {
		k_mutex_lock(&lk, K_FOREVER);
		st.fetch_errors++;
		fetch_failed_locked();
		k_mutex_unlock(&lk);
		(void)k_work_cancel_delayable(&fetch_to_work);
		(void)k_work_reschedule(&fetch_work, K_MSEC(100));
	}
}

static void fetch_fn(struct k_work *w)
{
	struct bt_conn *c;
	uint32_t uid = 0;
	uint16_t handle;
	bool have = false;
	int err;

	ARG_UNUSED(w);
	k_mutex_lock(&lk, K_FOREVER);
	if (!ancs_ready || !ds_subscribed || fetch_busy || sconn == NULL) {
		k_mutex_unlock(&lk);
		return;
	}
	while (fq_n > 0 && !have) {
		uid = fq[fq_head];
		cur_try = fq_try[fq_head];
		fq_head = (uint8_t)((fq_head + 1) % FETCH_Q);
		fq_n--;
		if (rinbox_find(&inbox, uid) >= 0) {
			have = true;
		} else {
			st.fetch_skipped++; /* removed or pushed out while it waited */
		}
	}
	if (!have) {
		k_mutex_unlock(&lk);
		return;
	}
	ripl_ds_start(&ds, uid);
	cur_uid = uid;
	fetch_busy = true;
	st.fetch_requests++;
	(void)ripl_build_get_attrs(req, uid);
	c = sconn;
	handle = ancs_c.handle_cp;
	k_mutex_unlock(&lk);

	fetch_wp.func = fetch_write_cb;
	fetch_wp.handle = handle;
	fetch_wp.offset = 0;
	fetch_wp.data = req;
	fetch_wp.length = RIPL_REQ_LEN;
	err = bt_gatt_write(c, &fetch_wp);
	if (err != 0) {
		k_mutex_lock(&lk, K_FOREVER);
		st.fetch_errors++;
		fetch_failed_locked();
		k_mutex_unlock(&lk);
		(void)k_work_reschedule(&fetch_work, K_MSEC(200));
		return;
	}
	(void)k_work_reschedule(&fetch_to_work, K_MSEC(FETCH_TIMEOUT_MS));
}

static void fetch_to_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	k_mutex_lock(&lk, K_FOREVER);
	if (fetch_busy) {
		st.fetch_timeouts++;
		fetch_failed_locked();
	}
	k_mutex_unlock(&lk);
	(void)k_work_reschedule(&fetch_work, K_NO_WAIT);
}

/* ---------------------------------------------------------------- media and time callbacks */

static void eu_cb(struct bt_ams_client *c, const struct bt_ams_entity_update_notif *n, int err)
{
	uint8_t attr;
	int r;

	ARG_UNUSED(c);
	if (err != 0) {
		return;
	}
	attr = n->ent_attr.entity == BT_AMS_ENTITY_ID_TRACK ? (uint8_t)n->ent_attr.attribute.track
							    : (uint8_t)n->ent_attr.attribute.player;
	k_mutex_lock(&lk, K_FOREVER);
	r = ripl_media_apply(&media, (uint8_t)n->ent_attr.entity, attr, n->data, n->len);
	if (r == 1) {
		st.media_reports++;
	} else {
		st.media_ignored++;
	}
	k_mutex_unlock(&lk);
}

static const enum bt_ams_player_attribute_id player_attrs[] = { BT_AMS_PLAYER_ATTRIBUTE_ID_PLAYBACK_INFO };
static const enum bt_ams_track_attribute_id track_attrs[] = { BT_AMS_TRACK_ATTRIBUTE_ID_ARTIST,
							      BT_AMS_TRACK_ATTRIBUTE_ID_TITLE };

static void eu_write_track_cb(struct bt_ams_client *c, uint8_t err)
{
	ARG_UNUSED(c);
	if (err != 0) {
		printk("rip: AMS track subscription write failed 0x%02x\n", err);
	}
}

static void eu_write_player_cb(struct bt_ams_client *c, uint8_t err)
{
	struct bt_ams_entity_attribute_list l = {
		.entity = BT_AMS_ENTITY_ID_TRACK,
		.attribute.track = track_attrs,
		.attribute_count = ARRAY_SIZE(track_attrs),
	};
	int e;

	if (err != 0) {
		printk("rip: AMS player subscription write failed 0x%02x\n", err);
	}
	e = bt_ams_write_entity_update(c, &l, eu_write_track_cb);
	if (e != 0) {
		printk("rip: AMS track subscription not sent %d\n", e);
	}
}

/* Time zone of the iPhone: Local Time Information is read next to Current Time. The pure state (ripl_clock) holds the last
 * Current Time value with the uptime at which it ARRIVED and the last zone of this link; the clock is set from it as UTC =
 * local time - zone - daylight offset. A zone read that comes back later is applied to that same arrival uptime, so it
 * cannot move the clock. A failed or unreadable zone read keeps the last known zone and is counted (zone_errors); "zone not
 * known" follows only from unknown values or from a link without the characteristic (rtime_zone_known()). */
static uint16_t lti_handle;
static bool lti_busy;
static struct ripl_clock clk; /* guarded by lk */
static struct bt_gatt_read_params lti_rp;

static void cts_read_cb(struct bt_cts_client *c, struct bt_cts_current_time *t, int err);

/* lk held: set the clock record from clk */
static bool clock_apply_locked(void)
{
	struct rtime_rec r;

	rtime_rec_init(&r);
	if (!ripl_clock_apply(&clk, &r)) {
		return false;
	}
	rtime_set_rec(&r);
	st.time_sets++;
	st.zone_known_sets += clk.zone_known ? 1 : 0;
	return true;
}

static void cts_apply(const struct bt_cts_current_time *t, int64_t arrived_ms)
{
	int64_t ms;
	const struct bt_cts_exact_time_256 *e = &t->exact_time_256;

	if (ripl_cts_to_ms(e->year, e->month, e->day, e->hours, e->minutes, e->seconds, e->fractions256, &ms)) {
		k_mutex_lock(&lk, K_FOREVER);
		ripl_clock_time(&clk, ms, arrived_ms);
		(void)clock_apply_locked();
		k_mutex_unlock(&lk);
	}
}

static uint8_t lti_read_cb(struct bt_conn *conn, uint8_t err, struct bt_gatt_read_params *params, const void *data,
			   uint16_t length)
{
	const uint8_t *d = data;
	bool have;
	int16_t m = 0;
	bool known = false;
	bool ok = (err == 0 && d != NULL && length == 2);

	ARG_UNUSED(conn);
	ARG_UNUSED(params);
	if (ok) {
		known = ripl_cts_zone((int8_t)d[0], d[1], &m);
	}
	k_mutex_lock(&lk, K_FOREVER);
	lti_busy = false;
	st.zone_reads++;
	st.zone_errors += ok ? 0 : 1;
	ripl_clock_zone(&clk, ok, known, m, k_uptime_get());
	have = clk.have_time;
	if (have) {
		(void)clock_apply_locked(); /* at the uptime the time arrived, not now */
	}
	k_mutex_unlock(&lk);
	if (!have && bt_cts_read_current_time(&cts_c, cts_read_cb) != 0) {
		printk("rip: Current Time read not started\n");
	}
	return BT_GATT_ITER_STOP;
}

/* read the zone; its callback sets the clock (reading Current Time first when we hold none) */
static void lti_refresh(void)
{
	int err;

	k_mutex_lock(&lk, K_FOREVER);
	if (lti_handle == 0 || lti_busy || !cts_ready) {
		k_mutex_unlock(&lk);
		return;
	}
	lti_busy = true;
	k_mutex_unlock(&lk);
	lti_rp.func = lti_read_cb;
	lti_rp.handle_count = 1;
	lti_rp.single.handle = lti_handle;
	lti_rp.single.offset = 0;
	err = bt_gatt_read(cts_c.conn, &lti_rp);
	if (err != 0) {
		k_mutex_lock(&lk, K_FOREVER);
		lti_busy = false;
		k_mutex_unlock(&lk);
	}
}

static void cts_read_cb(struct bt_cts_client *c, struct bt_cts_current_time *t, int err)
{
	ARG_UNUSED(c);
	if (err == 0) {
		cts_apply(t, k_uptime_get());
	}
}

static void cts_notify_cb(struct bt_cts_client *c, struct bt_cts_current_time *t)
{
	ARG_UNUSED(c);
	cts_apply(t, k_uptime_get());
	lti_refresh();
}

/* ---------------------------------------------------------------- discovery */

static void step_submit(k_timeout_t d)
{
	(void)k_work_reschedule(&step_work, d);
}

static void phase_next(enum phase from)
{
	k_mutex_lock(&lk, K_FOREVER);
	dm_busy = false;
	dm_retries = 0;
	if (sconn != NULL && phase == from) {
		phase = (enum phase)(from + 1);
	}
	k_mutex_unlock(&lk);
	step_submit(K_NO_WAIT);
}

static void sc_indicated(struct bt_gattp *g, const struct bt_gattp_handle_range *range, int err)
{
	ARG_UNUSED(g);
	ARG_UNUSED(range);
	if (err == 0) {
		k_mutex_lock(&lk, K_FOREVER);
		st.sc_indications++;
		sc_pending = true;
		k_mutex_unlock(&lk);
		step_submit(K_MSEC(50));
	}
}

static void gattp_found(struct bt_gatt_dm *dm, void *ctx)
{
	int err = -ENOENT;

	ARG_UNUSED(ctx);
	if (bt_gatt_dm_attr_cnt(dm) > 1) {
		err = bt_gattp_handles_assign(dm, &gattp);
	}
	(void)bt_gatt_dm_data_release(dm);
	k_mutex_lock(&lk, K_FOREVER);
	if (err == 0) {
		gattp_ready = true;
		st.gattp_found++;
	} else {
		st.gattp_missing++;
	}
	k_mutex_unlock(&lk);
	if (err == 0) {
		err = bt_gattp_subscribe_service_changed(&gattp, sc_indicated);
	}
	phase_next(P_GATTP);
}

static void ancs_found(struct bt_gatt_dm *dm, void *ctx)
{
	int err;
	bool ok = false;

	ARG_UNUSED(ctx);
	err = bt_ancs_handles_assign(dm, &ancs_c);
	(void)bt_gatt_dm_data_release(dm);
	if (err == 0) {
		/* the Data Source first, so the answers to the pre-existing notifications are heard */
		memset(&ds_params, 0, sizeof(ds_params));
		ds_params.notify = ds_notify;
		ds_params.value = BT_GATT_CCC_NOTIFY;
		ds_params.value_handle = ancs_c.handle_ds;
		ds_params.ccc_handle = ancs_c.handle_ds_ccc;
		atomic_set_bit(ds_params.flags, BT_GATT_SUBSCRIBE_FLAG_VOLATILE);
		k_mutex_lock(&lk, K_FOREVER);
		inbox_empty_locked();
		ancs_ready = true; /* before the subscription, so a pre-existing notification is not missed */
		k_mutex_unlock(&lk);
		err = bt_gatt_subscribe(ancs_c.conn, &ds_params);
		k_mutex_lock(&lk, K_FOREVER);
		ds_subscribed = (err == 0);
		k_mutex_unlock(&lk);
		if (err == 0) {
			err = bt_ancs_subscribe_notification_source(&ancs_c, ns_cb);
		}
		ok = (err == 0);
		k_mutex_lock(&lk, K_FOREVER);
		ancs_ready = ok;
		if (ok) {
			st.ancs_up++;
		} else {
			st.dm_errors++;
		}
		k_mutex_unlock(&lk);
	} else {
		k_mutex_lock(&lk, K_FOREVER);
		st.ancs_missing++;
		k_mutex_unlock(&lk);
	}
	phase_next(P_ANCS);
}

static void ams_found(struct bt_gatt_dm *dm, void *ctx)
{
	int err;

	ARG_UNUSED(ctx);
	err = bt_ams_handles_assign(dm, &ams_c);
	(void)bt_gatt_dm_data_release(dm);
	if (err == 0) {
		struct bt_ams_entity_attribute_list l = {
			.entity = BT_AMS_ENTITY_ID_PLAYER,
			.attribute.player = player_attrs,
			.attribute_count = ARRAY_SIZE(player_attrs),
		};

		err = bt_ams_subscribe_entity_update(&ams_c, eu_cb);
		if (err == 0) {
			k_mutex_lock(&lk, K_FOREVER);
			ams_ready = true;
			st.ams_up++;
			k_mutex_unlock(&lk);
			err = bt_ams_write_entity_update(&ams_c, &l, eu_write_player_cb);
			if (err != 0) {
				printk("rip: AMS player subscription not sent %d\n", err);
			}
		} else {
			k_mutex_lock(&lk, K_FOREVER);
			st.dm_errors++;
			k_mutex_unlock(&lk);
		}
	} else {
		k_mutex_lock(&lk, K_FOREVER);
		st.ams_missing++;
		k_mutex_unlock(&lk);
	}
	phase_next(P_AMS);
}

static void cts_found(struct bt_gatt_dm *dm, void *ctx)
{
	int err;

	ARG_UNUSED(ctx);
	uint16_t lti = 0;

	err = bt_cts_handles_assign(dm, &cts_c);
	if (err == 0) {
		const struct bt_gatt_dm_attr *chrc = bt_gatt_dm_char_by_uuid(dm, BT_UUID_GATT_LTI);
		const struct bt_gatt_dm_attr *val = chrc != NULL ? bt_gatt_dm_desc_by_uuid(dm, chrc, BT_UUID_GATT_LTI) : NULL;

		lti = val != NULL ? val->handle : 0; /* absent: no zone is known */
	}
	(void)bt_gatt_dm_data_release(dm);
	if (err == 0) {
		k_mutex_lock(&lk, K_FOREVER);
		lti_handle = lti;
		ripl_clock_init(&clk);
		lti_busy = false;
		cts_ready = true; /* before the reads: lti_refresh() needs it */
		k_mutex_unlock(&lk);
		err = bt_cts_subscribe_current_time(&cts_c, cts_notify_cb);
		if (err == 0) {
			if (lti != 0) {
				lti_refresh(); /* the zone first; its callback reads Current Time */
			} else {
				err = bt_cts_read_current_time(&cts_c, cts_read_cb);
			}
		}
		k_mutex_lock(&lk, K_FOREVER);
		cts_ready = (err == 0);
		if (err == 0) {
			st.cts_up++;
		} else {
			st.dm_errors++;
		}
		k_mutex_unlock(&lk);
	} else {
		k_mutex_lock(&lk, K_FOREVER);
		st.cts_missing++;
		k_mutex_unlock(&lk);
	}
	phase_next(P_CTS);
}

/* The discovery context holds the phase that started it (low 8 bits) and the number of the session (the rest). The
 * answer of a discovery that belongs to a session that has ended (the link ended while the kit's discovery was still
 * running) is dropped: it must not count a service as missing, attach a kit client to a dead link, or move the phase
 * of the next session. */
#define DM_CTX(p, gen) ((void *)(uintptr_t)((uint32_t)(p) | ((gen) << 8)))
#define DM_PHASE(ctx)  ((enum phase)((uintptr_t)(ctx) & 0xff))

static bool dm_stale(struct bt_conn *link, void *ctx)
{
	bool stale;
	struct bt_conn_info info;
	/* The Bluetooth host ends a running discovery when the link goes down and calls the discovery's callback (as
	 * "not found") before the disconnected callback of this module runs, so the link itself is asked too. */
	bool gone = (link == NULL) || (bt_conn_get_info(link, &info) != 0) || (info.state != BT_CONN_STATE_CONNECTED);

	k_mutex_lock(&lk, K_FOREVER);
	stale = gone || (sconn == NULL) || (((uintptr_t)ctx >> 8) != session_gen);
	if (stale) {
		st.dm_stale++;
		dm_busy = false;
	}
	k_mutex_unlock(&lk);
	return stale;
}

static void dm_not_found(struct bt_conn *c, void *ctx)
{
	enum phase p = DM_PHASE(ctx);

	if (dm_stale(c, ctx)) {
		return;
	}
	k_mutex_lock(&lk, K_FOREVER);
	if (p == P_GATTP) {
		st.gattp_missing++;
	} else if (p == P_ANCS) {
		st.ancs_missing++;
	} else if (p == P_AMS) {
		st.ams_missing++;
	} else if (p == P_CTS) {
		st.cts_missing++;
	}
	k_mutex_unlock(&lk);
	phase_next(p);
}

static void dm_error(struct bt_conn *c, int err, void *ctx)
{
	enum phase p = DM_PHASE(ctx);

	if (dm_stale(c, ctx)) {
		return;
	}
	printk("rip: discovery in phase %d failed %d\n", p, err);
	k_mutex_lock(&lk, K_FOREVER);
	st.dm_errors++;
	k_mutex_unlock(&lk);
	phase_next(p);
}

static void dm_completed(struct bt_gatt_dm *dm, void *ctx)
{
	if (dm_stale(bt_gatt_dm_conn_get(dm), ctx)) {
		(void)bt_gatt_dm_data_release(dm);
		return;
	}
	switch (DM_PHASE(ctx)) {
	case P_GATTP:
		gattp_found(dm, ctx);
		break;
	case P_ANCS:
		ancs_found(dm, ctx);
		break;
	case P_AMS:
		ams_found(dm, ctx);
		break;
	case P_CTS:
		cts_found(dm, ctx);
		break;
	default:
		(void)bt_gatt_dm_data_release(dm);
		break;
	}
}

static const struct bt_gatt_dm_cb dm_cb = {
	.completed = dm_completed,
	.service_not_found = dm_not_found,
	.error_found = dm_error,
};

/* Stop the three services of the link (not the Service Changed subscription). The inbox and the media
 * record are emptied: the sessions of the services end. */
static void stop_services(struct bt_conn *c)
{
	bool a, m, t, d;

	k_mutex_lock(&lk, K_FOREVER);
	a = ancs_ready;
	d = ds_subscribed;
	m = ams_ready;
	t = cts_ready;
	ancs_ready = false;
	ds_subscribed = false;
	ams_ready = false;
	cts_ready = false;
	if (a) {
		st.ancs_down++;
	}
	if (m) {
		st.ams_down++;
	}
	if (t) {
		st.cts_down++;
	}
	inbox_empty_locked();
	ripl_media_init(&media);
	ripl_clock_init(&clk);
	lti_handle = 0;
	k_mutex_unlock(&lk);
	(void)k_work_cancel_delayable(&fetch_to_work);
	if (c == NULL) {
		return;
	}
	if (a) {
		(void)bt_ancs_unsubscribe_notification_source(&ancs_c);
	}
	if (d) {
		(void)bt_gatt_unsubscribe(c, &ds_params);
	}
	if (m) {
		(void)bt_ams_unsubscribe_entity_update(&ams_c);
	}
	if (t) {
		(void)bt_cts_unsubscribe_current_time(&cts_c);
	}
}

static const struct bt_uuid_16 uuid_gatt = BT_UUID_INIT_16(BT_UUID_GATT_VAL);
static const struct bt_uuid_128 uuid_ancs = BT_UUID_INIT_128(BT_UUID_ANCS_VAL);
static const struct bt_uuid_128 uuid_ams = BT_UUID_INIT_128(BT_UUID_AMS_VAL);
static const struct bt_uuid_16 uuid_cts = BT_UUID_INIT_16(BT_UUID_CTS_VAL);

static void start_dm(struct bt_conn *c, enum phase p)
{
	const struct bt_uuid *u;
	uint32_t gen;
	int err;

	switch (p) {
	case P_GATTP:
		u = &uuid_gatt.uuid;
		break;
	case P_ANCS:
		u = &uuid_ancs.uuid;
		break;
	case P_AMS:
		u = &uuid_ams.uuid;
		break;
	default:
		u = &uuid_cts.uuid;
		break;
	}
	k_mutex_lock(&lk, K_FOREVER);
	dm_busy = true;
	gen = session_gen;
	k_mutex_unlock(&lk);
	err = bt_gatt_dm_start(c, u, &dm_cb, DM_CTX(p, gen));
	if (err != 0) {
		bool give_up;

		k_mutex_lock(&lk, K_FOREVER);
		dm_busy = false;
		st.dm_errors++;
		give_up = ++dm_retries >= DM_RETRY_MAX;
		k_mutex_unlock(&lk);
		printk("rip: discovery start failed %d (phase %d)\n", err, p);
		if (give_up) {
			phase_next(p);
		} else {
			step_submit(K_MSEC(300));
		}
	}
}

static void step_fn(struct k_work *w)
{
	struct bt_conn *c;
	enum phase p;
	bool sc;

	ARG_UNUSED(w);
	k_mutex_lock(&lk, K_FOREVER);
	c = sconn;
	if (c == NULL || dm_busy) {
		bool busy = (c != NULL);

		k_mutex_unlock(&lk);
		if (busy) {
			step_submit(K_MSEC(100));
		}
		return;
	}
	sc = sc_pending;
	sc_pending = false;
	if (sc) {
		phase = P_ANCS;
	}
	p = phase;
	k_mutex_unlock(&lk);
	if (sc) {
		printk("rip: Service Changed: the services are stopped and looked for again\n");
		stop_services(c);
	}
	if (p == P_GATTP || p == P_ANCS || p == P_AMS || p == P_CTS) {
		start_dm(c, p);
	}
}

/* ---------------------------------------------------------------- session */

static void end_session(void)
{
	struct bt_conn *c;
	enum phase phase_was;

	k_mutex_lock(&lk, K_FOREVER);
	c = sconn;
	sconn = NULL;
	phase_was = phase;
	phase = P_IDLE;
	dm_busy = false;
	sc_pending = false;
	gattp_ready = false;
	if (c != NULL) {
		st.sessions_ended++;
		if (phase_was != P_DONE && phase_was != P_IDLE) {
			st.ended_in_discovery++;
		}
	}
	k_mutex_unlock(&lk);
	(void)k_work_cancel_delayable(&step_work);
	(void)k_work_cancel_delayable(&fetch_work);
	(void)k_work_cancel_delayable(&fetch_to_work);
	/* the link is gone: no unsubscribe is sent; everything stored from the iPhone is emptied */
	stop_services(NULL);
	if (c != NULL) {
		bt_conn_unref(c);
		printk("rip: session ended, inbox and media emptied\n");
	}
}

static void ready_fn(struct k_work *w)
{
	struct bt_conn *c = rdev_active_conn();
	bool had;

	ARG_UNUSED(w);
	if (c == NULL) {
		/* the link is not yet the active device's secure link (the pairing may still be being
		 * recorded by the devices part): ask again, a few times */
		if (ready_tries++ < READY_TRIES_MAX) {
			(void)k_work_reschedule(&ready_work, K_MSEC(300));
		}
		return;
	}
	ready_tries = 0;
	k_mutex_lock(&lk, K_FOREVER);
	if (sconn == c) {
		k_mutex_unlock(&lk);
		bt_conn_unref(c);
		return;
	}
	had = (sconn != NULL);
	k_mutex_unlock(&lk);
	if (had) {
		end_session();
	}
	k_mutex_lock(&lk, K_FOREVER);
	sconn = c; /* keeps the reference rdev_active_conn() took */
	session_gen++;
	phase = P_GATTP;
	dm_busy = false;
	dm_retries = 0;
	sc_pending = false;
	rinbox_clear(&inbox);
	fq_clear();
	ripl_media_init(&media);
	st.sessions++;
	k_mutex_unlock(&lk);
	printk("rip: link ready, looking for the iPhone's services\n");
	step_submit(K_NO_WAIT);
}

static void trigger_ready(void)
{
	ready_tries = 0;
	(void)k_work_reschedule(&ready_work, K_MSEC(20));
}

static void on_security(struct bt_conn *conn, bt_security_t level, enum bt_security_err err)
{
	ARG_UNUSED(conn);
	if (inited && err == 0 && level >= BT_SECURITY_L4) {
		trigger_ready();
	}
}

static void on_disconnected(struct bt_conn *conn, uint8_t reason)
{
	bool mine;

	ARG_UNUSED(reason);
	if (!inited) {
		return;
	}
	k_mutex_lock(&lk, K_FOREVER);
	mine = (conn == sconn);
	k_mutex_unlock(&lk);
	if (mine) {
		end_session();
	}
	(void)k_work_cancel_delayable(&ready_work);
}

BT_CONN_CB_DEFINE(rip_conn_cb) = {
	.security_changed = on_security,
	.disconnected = on_disconnected,
};

static void on_pairing_complete(struct bt_conn *conn, bool bonded)
{
	ARG_UNUSED(conn);
	ARG_UNUSED(bonded);
	if (inited) {
		trigger_ready();
	}
}

static struct bt_conn_auth_info_cb info_cb = {
	.pairing_complete = on_pairing_complete,
};

/* ---------------------------------------------------------------- public */

int rip_init(void)
{
	int err;

	if (inited) {
		return 0;
	}
	rinbox_init(&inbox);
	ripl_media_init(&media);
	(void)bt_ancs_client_init(&ancs_c);
	(void)bt_ams_client_init(&ams_c);
	(void)bt_cts_client_init(&cts_c);
	(void)bt_gattp_init(&gattp);
	k_work_init_delayable(&ready_work, ready_fn);
	k_work_init_delayable(&step_work, step_fn);
	k_work_init_delayable(&fetch_work, fetch_fn);
	k_work_init_delayable(&fetch_to_work, fetch_to_fn);
	err = bt_conn_auth_info_cb_register(&info_cb);
	if (err != 0) {
		return err;
	}
	inited = true;
	return 0;
}

bool rip_ancs_ready(void)
{
	bool r;

	k_mutex_lock(&lk, K_FOREVER);
	r = ancs_ready;
	k_mutex_unlock(&lk);
	return r;
}

bool rip_ams_ready(void)
{
	bool r;

	k_mutex_lock(&lk, K_FOREVER);
	r = ams_ready;
	k_mutex_unlock(&lk);
	return r;
}

bool rip_cts_ready(void)
{
	bool r;

	k_mutex_lock(&lk, K_FOREVER);
	r = cts_ready;
	k_mutex_unlock(&lk);
	return r;
}

uint8_t rip_inbox_count(void)
{
	uint8_t n;

	k_mutex_lock(&lk, K_FOREVER);
	n = rinbox_count(&inbox);
	k_mutex_unlock(&lk);
	return n;
}

bool rip_inbox_get(uint8_t index, struct rinbox_item *out)
{
	const struct rinbox_item *it;
	bool ok = false;

	k_mutex_lock(&lk, K_FOREVER);
	it = rinbox_get(&inbox, index);
	if (it != NULL) {
		*out = *it;
		ok = true;
	}
	k_mutex_unlock(&lk);
	return ok;
}

int rip_inbox_mark_read(uint32_t uid)
{
	int r;

	k_mutex_lock(&lk, K_FOREVER);
	r = rinbox_mark_read(&inbox, uid);
	k_mutex_unlock(&lk);
	return r;
}

static void action_write_cb(struct bt_ancs_client *c, uint8_t err)
{
	ARG_UNUSED(c);
	if (err != 0) {
		k_mutex_lock(&lk, K_FOREVER);
		st.action_failed++;
		k_mutex_unlock(&lk);
		printk("rip: the iPhone refused the action, ATT error 0x%02x\n", err);
	}
}

int rip_action(uint32_t uid, enum rip_action action)
{
	int at, err;
	uint8_t need = action == RIP_ACTION_POSITIVE ? RINBOX_F_POSITIVE : RINBOX_F_NEGATIVE;

	if (action != RIP_ACTION_POSITIVE && action != RIP_ACTION_NEGATIVE) {
		return -EINVAL;
	}
	k_mutex_lock(&lk, K_FOREVER);
	at = rinbox_find(&inbox, uid);
	if (at < 0) {
		st.actions_refused++;
		k_mutex_unlock(&lk);
		return -ENOENT;
	}
	if ((rinbox_get(&inbox, (uint8_t)at)->flags & need) == 0) {
		st.actions_refused++;
		k_mutex_unlock(&lk);
		return -ENOTSUP;
	}
	if (!ancs_ready || sconn == NULL) {
		st.actions_refused++;
		k_mutex_unlock(&lk);
		return -ENOTCONN;
	}
	k_mutex_unlock(&lk);
	err = bt_ancs_notification_action(&ancs_c, uid,
					  action == RIP_ACTION_POSITIVE ? BT_ANCS_ACTION_ID_POSITIVE
									: BT_ANCS_ACTION_ID_NEGATIVE,
					  action_write_cb);
	k_mutex_lock(&lk, K_FOREVER);
	if (err == 0) {
		st.actions_sent++;
	} else {
		st.action_errors++;
	}
	k_mutex_unlock(&lk);
	return err;
}

int rip_dismiss(uint32_t uid)
{
	return rip_action(uid, RIP_ACTION_NEGATIVE);
}

void rip_media_get(struct ripl_media *out)
{
	k_mutex_lock(&lk, K_FOREVER);
	*out = media;
	k_mutex_unlock(&lk);
}

static void rc_write_cb(struct bt_ams_client *c, uint8_t err)
{
	ARG_UNUSED(c);
	if (err != 0) {
		k_mutex_lock(&lk, K_FOREVER);
		st.media_errors++;
		k_mutex_unlock(&lk);
	}
}

int rip_media_command(enum rip_media_cmd cmd)
{
	/* Apple Media Service RemoteCommandID values (kit ams_client.h lines 83-90) */
	static const enum bt_ams_remote_command_id map[RIP_MEDIA_CMD_COUNT] = {
		[RIP_MEDIA_PLAY] = BT_AMS_REMOTE_COMMAND_ID_PLAY,
		[RIP_MEDIA_PAUSE] = BT_AMS_REMOTE_COMMAND_ID_PAUSE,
		[RIP_MEDIA_NEXT] = BT_AMS_REMOTE_COMMAND_ID_NEXT_TRACK,
		[RIP_MEDIA_PREVIOUS] = BT_AMS_REMOTE_COMMAND_ID_PREVIOUS_TRACK,
		[RIP_MEDIA_VOLUME_UP] = BT_AMS_REMOTE_COMMAND_ID_VOLUME_UP,
		[RIP_MEDIA_VOLUME_DOWN] = BT_AMS_REMOTE_COMMAND_ID_VOLUME_DOWN,
	};
	int err;

	if ((unsigned int)cmd >= RIP_MEDIA_CMD_COUNT) {
		return -EINVAL;
	}
	k_mutex_lock(&lk, K_FOREVER);
	if (!ams_ready || sconn == NULL) {
		st.media_refused++;
		k_mutex_unlock(&lk);
		return -ENOTCONN;
	}
	k_mutex_unlock(&lk);
	err = bt_ams_write_remote_command(&ams_c, map[cmd], rc_write_cb);
	k_mutex_lock(&lk, K_FOREVER);
	if (err == 0) {
		st.media_sent++;
		if (cmd == RIP_MEDIA_PLAY) {
			media.state = RIPL_PLAYER_PLAYING;
		}
	} else {
		st.media_errors++;
	}
	k_mutex_unlock(&lk);
	return err;
}

void rip_stats_get(struct rip_stats *out)
{
	k_mutex_lock(&lk, K_FOREVER);
	*out = st;
	k_mutex_unlock(&lk);
}
