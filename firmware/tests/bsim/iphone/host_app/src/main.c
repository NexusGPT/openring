/*
 * Stand-in iPhone of the iPhone test (BabbleSim, the simulated ring chip nrf54lm20bsim, real encryption: see run.sh).
 *
 * A Bluetooth central that
 *  - finds the ring by the HID service in its advertising data, pairs with the passkey the ring shows
 *    (read from the file the ring writes) and reaches security level 4, like the step 2 stand-in host
 *    (tests/bsim/control/host_app), and runs the HID over GATT client so the ring's keys arrive;
 *  - serves Apple's three services from a GATT server, with the real UUIDs and data formats:
 *      Apple Notification Center Service (ANCS): Notification Source, Control Point, Data Source
 *      Apple Media Service (AMS): Remote Command, Entity Update, Entity Attribute
 *      Current Time Service (CTS): Current Time
 *    The services can be removed and added while linked (the GATT server then indicates Service Changed);
 *  - is driven by a script (script_n, script_r, script_p below) in simulated time, measured from the moment
 *    the ring subscribes to the Notification Source (scenario P: from the HID client being ready).
 *
 * Where each data format comes from (the code under test shares none of this file's constants; the UUIDs and
 * layouts are written out here from the documents, not taken from the kit headers the ring uses):
 *   ANCS UUIDs: ADG (adg.txt:16872, saved excerpt step3/apple/adg-excerpt-16868-16873.txt) for the service; characteristics from the Apple ANCS
 *     specification (firmware/build-logs/step3/apple/ancs-spec.txt), also listed in kit ancs_client.h lines 26-40.
 *   Notification Source message, 8 bytes: EventID, EventFlags, CategoryID, CategoryCount, NotificationUID u32 LE:
 *     ancs-spec.txt:102 (Figure 2-1 is a picture; the field list is in the text), kit ancs_client.c lines 26-35, 60-110.
 *   EventID values 0 added, 1 modified, 2 removed; flags bits 0 silent, 1 important, 2 pre-existing, 3 positive,
 *     4 negative: ancs-appendix.txt:99-107 (also kit ancs_client.h lines 68-87, 130-138).
 *   Get Notification Attributes request: CommandID 0, uid u32 LE, attribute ids, each of Title(1), Subtitle(2),
 *     Message(3) followed by a u16 LE maximum length: ancs-spec.txt:106, ancs-appendix.txt:116.
 *   Its answer: CommandID 0, uid, then tuples (attribute id, u16 LE length, data, not NUL terminated) in the order
 *     of the request; split into fragments by the MTU: ancs-spec.txt:106.
 *   Perform Notification Action: CommandID 2, uid u32 LE, ActionID (0 positive, 1 negative): ancs-spec.txt:112-125,
 *     ancs-appendix.txt:114, 124. Errors 0xA2 invalid parameter, 0xA3 action failed: ancs-spec.txt:151-152.
 *   AMS UUIDs: ams-spec.txt:99 (service), 117-119 (characteristics). Remote Command: one byte RemoteCommandID,
 *     values play 0, pause 1, toggle 2, next 3, previous 4, volume up 5, volume down 6: kit ams_client.h lines 83-90
 *     (the Apple appendix page is not saved in step3/apple).
 *   Entity Update: write EntityID + AttributeIDs, notify EntityID, AttributeID, flags, value: ams-spec.txt:147-175.
 *     Entity ids player 0, queue 1, track 2; player attribute PlaybackInfo 1; track attributes artist 0, album 1,
 *     title 2, duration 3: kit ams_client.h lines 100-142. PlaybackInfo value "<state>,<rate>,<elapsed>", "1,1.0,0.014"
 *     playing, "0,0.0,0.000" paused: kit samples/bluetooth/peripheral_ams_client/README.rst (music setup, playback).
 *   Writing Entity Update before subscribing to its notifications: error 0xA0: ams-spec.txt:206.
 *   CTS: service 0x1805, characteristic Current Time 0x2A2B (Bluetooth SIG numbers, as in the kit's
 *     BT_UUID_CTS_VAL and BT_UUID_CTS_CURRENT_TIME in zephyr/bluetooth/uuid.h); value 10 bytes: year u16 LE, month,
 *     day, hours, minutes, seconds, day of week (1 Monday .. 7 Sunday), fractions256, adjust reason:
 *     kit cts_client.c lines 19-25 and 103-135 (day of week 1..7 is the SIG definition, not in a kit file).
 *   Local Time Information (SIG characteristic 0x2A0F, 2 bytes: zone int8 in 15-minute units, daylight offset uint8; the
 *     author's reading of the SIG specification, NOT from a saved document: docs/iphone-notes.md section 3) is served
 *     next to Current Time (scenario W leaves it out). Not served: Battery Service.
 *
 * Output lines: "PHONE CHECK <name> PASS|FAIL" and one "PHONE RESULT PASS|FAIL". Times are simulated ms.
 * Environment: RING_SCENARIO (N, R, P, L, D, Z or W), RING_PASSFILE.
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

static char scen;
static int fails;
static int checks;

#define CHECK(label, cond)                                                                          \
	do {                                                                                        \
		bool ok_ = (cond);                                                                  \
		checks++;                                                                           \
		fails += ok_ ? 0 : 1;                                                               \
		printk("PHONE CHECK %s %s (t=%lld)\n", label, ok_ ? "PASS" : "FAIL", k_uptime_get()); \
	} while (0)

/* ======================================================================== notification model */

struct nrec {
	bool used;
	bool ignore_max;      /* the iPhone sends the whole text although the client gave a maximum length */
	uint8_t cat;
	uint8_t flags;
	uint32_t uid;
	uint16_t msg_len;
	char app[96];
	char title[96];
	uint8_t msg[256];
	char date[24];
};

#define MODEL_MAX 40
static struct nrec model[MODEL_MAX];

/* the iPhone's notification order: the order of adding */
static struct nrec *model_find(uint32_t uid)
{
	for (int i = 0; i < MODEL_MAX; i++) {
		if (model[i].used && model[i].uid == uid) {
			return &model[i];
		}
	}
	return NULL;
}

static struct nrec *model_set(uint32_t uid, uint8_t cat, uint8_t flags, const char *app, const char *title,
			      const void *msg, size_t msg_len, const char *date, bool ignore_max)
{
	struct nrec *n = model_find(uid);

	if (n == NULL) {
		for (int i = 0; i < MODEL_MAX && n == NULL; i++) {
			if (!model[i].used) {
				n = &model[i];
			}
		}
	}
	__ASSERT(n != NULL, "model full");
	memset(n, 0, sizeof(*n));
	n->used = true;
	n->uid = uid;
	n->cat = cat;
	n->flags = flags;
	n->ignore_max = ignore_max;
	strncpy(n->app, app, sizeof(n->app) - 1);
	strncpy(n->title, title, sizeof(n->title) - 1);
	memcpy(n->msg, msg, msg_len);
	n->msg_len = (uint16_t)msg_len;
	strncpy(n->date, date, sizeof(n->date) - 1);
	return n;
}


/* ======================================================================== the connection */

static struct bt_conn *conn;
static int64_t t0;              /* script start, 0 until set */
static int ns_sub_count;        /* times the ring wrote the Notification Source's CCC with notify on */
static int ns_unsub_count;
static bool ns_on, ds_on, eu_on, ct_on;
static bt_security_t ns_sub_level;
static int ds_sub_count, eu_sub_count, ct_sub_count, ct_reads;
static bool apple = true;       /* serve Apple's services (false: scenario P, a plain host like the step 2 stand-in) */

/* ---- UUIDs, written out from the documents (see the header comment) ---- */
static const struct bt_uuid_128 u_ancs = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0x7905f431, 0xb5ce, 0x4e99, 0xa40f, 0x4b1e122d00d0));
static const struct bt_uuid_128 u_ns = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0x9fbf120d, 0x6301, 0x42d9, 0x8c58, 0x25e699a21dbd));
static const struct bt_uuid_128 u_cp = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0x69d1d8f3, 0x45e1, 0x49a8, 0x9821, 0x9bbdfdaad9d9));
static const struct bt_uuid_128 u_ds = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0x22eac6e9, 0x24d6, 0x4bb5, 0xbe44, 0xb36ace7c7bfb));
static const struct bt_uuid_128 u_ams = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0x89d3502b, 0x0f36, 0x433a, 0x8ef4, 0xc502ad55f8dc));
static const struct bt_uuid_128 u_rc = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0x9b3c81d8, 0x57b1, 0x4a8a, 0xb8df, 0x0e56f7ca51c2));
static const struct bt_uuid_128 u_eu = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0x2f7cabce, 0x808d, 0x411f, 0x9a0c, 0xbb92ba96c102));
static const struct bt_uuid_128 u_ea = BT_UUID_INIT_128(BT_UUID_128_ENCODE(0xc6b2f38c, 0x23ab, 0x46d8, 0xa6ab, 0xa3a870bbd5d7));
static const struct bt_uuid_16 u_cts = BT_UUID_INIT_16(0x1805);
static const struct bt_uuid_16 u_ct = BT_UUID_INIT_16(0x2A2B);
static const struct bt_uuid_16 u_lti = BT_UUID_INIT_16(0x2A0F);

static ssize_t ns_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value);
static ssize_t ds_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value);
static ssize_t eu_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value);
static ssize_t ct_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value);
static ssize_t rc_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value);
static ssize_t cp_write(struct bt_conn *c, const struct bt_gatt_attr *attr, const void *buf, uint16_t len,
			uint16_t offset, uint8_t flags);
static ssize_t rc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, const void *buf, uint16_t len,
			uint16_t offset, uint8_t flags);
static ssize_t eu_write(struct bt_conn *c, const struct bt_gatt_attr *attr, const void *buf, uint16_t len,
			uint16_t offset, uint8_t flags);
static ssize_t ea_write(struct bt_conn *c, const struct bt_gatt_attr *attr, const void *buf, uint16_t len,
			uint16_t offset, uint8_t flags);
static ssize_t ea_read(struct bt_conn *c, const struct bt_gatt_attr *attr, void *buf, uint16_t len, uint16_t offset);
static ssize_t ct_read(struct bt_conn *c, const struct bt_gatt_attr *attr, void *buf, uint16_t len, uint16_t offset);
static ssize_t lti_read(struct bt_conn *c, const struct bt_gatt_attr *attr, void *buf, uint16_t len, uint16_t offset);

#define AUTH_RW (BT_GATT_PERM_READ_AUTHEN | BT_GATT_PERM_WRITE_AUTHEN)

/* ANCS: [0] service, [1,2] Notification Source, [3] its CCC, [4,5] Control Point, [6,7] Data Source, [8] its CCC */
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

/* AMS: [0] service, [1,2] Remote Command, [3] its CCC, [4,5] Entity Update, [6] its CCC, [7,8] Entity Attribute */
static struct bt_gatt_attr ams_attrs[] = {
	BT_GATT_PRIMARY_SERVICE(&u_ams),
	BT_GATT_CHARACTERISTIC(&u_rc.uuid, BT_GATT_CHRC_WRITE | BT_GATT_CHRC_NOTIFY, BT_GATT_PERM_WRITE_AUTHEN, NULL,
			       rc_write, NULL),
	BT_GATT_CCC_WITH_WRITE_CB(NULL, rc_ccc_write, AUTH_RW),
	BT_GATT_CHARACTERISTIC(&u_eu.uuid, BT_GATT_CHRC_WRITE | BT_GATT_CHRC_NOTIFY, BT_GATT_PERM_WRITE_AUTHEN, NULL,
			       eu_write, NULL),
	BT_GATT_CCC_WITH_WRITE_CB(NULL, eu_ccc_write, AUTH_RW),
	BT_GATT_CHARACTERISTIC(&u_ea.uuid, BT_GATT_CHRC_READ | BT_GATT_CHRC_WRITE, AUTH_RW, ea_read, ea_write, NULL),
};
#define A_EU_VAL 5
static struct bt_gatt_service ams_svc = BT_GATT_SERVICE(ams_attrs);

/* CTS: [0] service, [1,2] Current Time, [3] its CCC, [4,5] Local Time Information */
static struct bt_gatt_attr cts_attrs[] = {
	BT_GATT_PRIMARY_SERVICE(&u_cts),
	BT_GATT_CHARACTERISTIC(&u_ct.uuid, BT_GATT_CHRC_READ | BT_GATT_CHRC_NOTIFY, BT_GATT_PERM_READ_AUTHEN, ct_read,
			       NULL, NULL),
	BT_GATT_CCC_WITH_WRITE_CB(NULL, ct_ccc_write, AUTH_RW),
	BT_GATT_CHARACTERISTIC(&u_lti.uuid, BT_GATT_CHRC_READ, BT_GATT_PERM_READ_AUTHEN, lti_read, NULL, NULL),
};
#define A_CT_VAL 2
static struct bt_gatt_service cts_svc = BT_GATT_SERVICE(cts_attrs);
/* scenario W: the same service without the Local Time Information characteristic (its first four attributes) */
static struct bt_gatt_service cts_svc_nolti = { .attrs = cts_attrs, .attr_count = 4 };

/* ======================================================================== ANCS */

/* command and request logs, for the checks at the end */
static uint8_t cp_log[48][24];
static uint8_t cp_log_len[48];
static int ncp;
struct action {
	uint32_t uid;
	uint8_t action;
};
static struct action actions[16];
static int nactions;
static struct action cmds[16];  /* every action command that arrived, accepted or refused */
static int ncmds;
static int flagless_cmds;       /* commands for a notification that does not have that action */
static uint8_t rc_cmds[16];
static int nrc;
static uint8_t eu_writes[8][8];
static uint8_t eu_write_len[8];
static int neu;
static int eu_bad_state;        /* Entity Update writes refused with 0xA0: not subscribed */

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
	printk("PHONE INFO NS event %u uid %u flags 0x%02x (%d)\n", evt, uid, flags, err);
}

/* the ring subscribes; the iPhone then sends what it holds, flagged pre-existing (flag bit 2) */
static struct k_work_delayable replay_work;
static int replay_idx;

static void replay_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	while (replay_idx < MODEL_MAX && !model[replay_idx].used) {
		replay_idx++;
	}
	if (replay_idx >= MODEL_MAX || !ns_on) {
		return;
	}
	ns_send(0, model[replay_idx].flags | 0x04, model[replay_idx].cat, model[replay_idx].uid);
	replay_idx++;
	k_work_reschedule(&replay_work, K_MSEC(60));
}

/* scenario D: the link ends while the ring is still looking for the three services */
static bool drop_in_discovery;
static bool dropped;
static int eu_at_drop, ct_at_drop;
static struct k_work_delayable drop_work;
static int64_t resume_at;     /* the stand-in stays away until then (also used by scenario R) */

static void drop_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	if (conn != NULL) {
		eu_at_drop = eu_sub_count;
		ct_at_drop = ct_sub_count;
		dropped = true;
		printk("PHONE INFO the link is ended while the ring is discovering: Entity Update subscriptions %d, Current Time "
		       "subscriptions %d (t=%lld)\n", eu_at_drop, ct_at_drop, k_uptime_get());
		resume_at = k_uptime_get() + 3000;
		(void)bt_conn_disconnect(conn, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
	}
}

static ssize_t ns_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value)
{
	ARG_UNUSED(attr);
	if (value & BT_GATT_CCC_NOTIFY) {
		ns_sub_count++;
		ns_sub_level = bt_conn_get_security(c);
		ns_on = true;
		if (t0 == 0) {
			t0 = k_uptime_get();
		}
		printk("PHONE INFO Notification Source subscribed (#%d, security level %u, t=%lld)\n", ns_sub_count,
		       ns_sub_level, k_uptime_get());
		replay_idx = 0;
		k_work_reschedule(&replay_work, K_MSEC(300));
	} else {
		ns_unsub_count++;
		ns_on = false;
		printk("PHONE INFO Notification Source unsubscribed\n");
	}
	return sizeof(value);
}

static ssize_t ds_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value)
{
	ARG_UNUSED(c);
	ARG_UNUSED(attr);
	ds_on = (value & BT_GATT_CCC_NOTIFY) != 0;
	ds_sub_count += ds_on ? 1 : 0;
	if (drop_in_discovery && ds_on) {
		/* scenario D: the ring has found the Notification Center Service and has not yet looked for the Media and
		 * Current Time services: the link ends now (once) */
		drop_in_discovery = false;
		k_work_reschedule(&drop_work, K_MSEC(60));
	}
	return sizeof(value);
}

/* answers wait in a queue and go out one after the other, fragment by fragment: two answers never interleave */
#define OUTQ 8
static struct {
	uint8_t d[400];
	size_t len;
} outq[OUTQ];
static int out_head, out_n;
static size_t out_off;
static uint8_t resp[400];
static size_t resp_len;
static struct k_work_delayable ds_work;
/* scenario L: answers can be held before they are sent. hold[i]: the answers to requests for uid are held for ms; with
 * once, only the first answer to that uid is held; with copies 2 the held answer is sent twice, 200 ms apart (a late answer
 * that arrives while later requests are in flight). */
#define HOLDS 3
static struct {
	uint32_t uid;
	int ms;
	bool once;
	int copies;
	int taken; /* answers held so far */
} hold[HOLDS];
#define PENDING 6
static struct {
	struct k_work_delayable w;
	uint8_t buf[400];
	size_t len;
	int copies;
	bool busy;
} pend[PENDING];
static int late_held;

static void out_push(const uint8_t *d, size_t len)
{
	if (out_n < OUTQ) {
		int at = (out_head + out_n) % OUTQ;

		memcpy(outq[at].d, d, len);
		outq[at].len = len;
		out_n++;
	}
	k_work_reschedule(&ds_work, K_MSEC(1));
}

static void late_fn(struct k_work *w)
{
	int i = (int)(CONTAINER_OF(k_work_delayable_from_work(w), __typeof__(pend[0]), w) - &pend[0]);

	printk("PHONE INFO the held answer is sent now (t=%lld)\n", k_uptime_get());
	out_push(pend[i].buf, pend[i].len);
	if (--pend[i].copies > 0) {
		k_work_reschedule(&pend[i].w, K_MSEC(200));
	} else {
		pend[i].busy = false;
	}
}
static int frag = 20;                 /* bytes per Data Source notification: a fragment, smaller than the MTU allows */
static struct k_work_delayable removal_work;
static uint32_t removal_uid;

static void ds_fn(struct k_work *w)
{
	size_t n;
	int err;

	ARG_UNUSED(w);
	if (conn == NULL || out_n == 0) {
		return;
	}
	n = MIN((size_t)frag, outq[out_head].len - out_off);
	err = bt_gatt_notify(conn, &ancs_attrs[A_DS_VAL], &outq[out_head].d[out_off], n);
	if (err == 0) {
		out_off += n;
		if (out_off >= outq[out_head].len) {
			out_off = 0;
			out_head = (out_head + 1) % OUTQ;
			out_n--;
		}
	}
	if (out_n > 0) {
		k_work_reschedule(&ds_work, K_MSEC(err == 0 ? 3 : 15));
	}
}

static void removal_fn(struct k_work *w)
{
	struct nrec *n = model_find(removal_uid);

	ARG_UNUSED(w);
	if (n != NULL) {
		uint8_t cat = n->cat, fl = n->flags;

		n->used = false;
		ns_send(2, fl, cat, removal_uid);
	}
}

static ssize_t cp_write(struct bt_conn *c, const struct bt_gatt_attr *attr, const void *buf, uint16_t len,
			uint16_t offset, uint8_t flags)
{
	const uint8_t *d = buf;

	ARG_UNUSED(c);
	ARG_UNUSED(attr);
	ARG_UNUSED(flags);
	if (offset != 0 || len < 1) {
		return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
	}
	if (ncp < 48) {
		cp_log_len[ncp] = (uint8_t)MIN(len, 24);
		memcpy(cp_log[ncp], d, cp_log_len[ncp]);
		ncp++;
	}
	if (d[0] == 0 && len >= 6) {
		/* Get Notification Attributes */
		uint32_t uid = sys_get_le32(&d[1]);
		struct nrec *n = model_find(uid);
		size_t i = 5, o = 0;

		if (n == NULL) {
			return BT_GATT_ERR(0xA2); /* invalid parameter */
		}
		resp[o++] = 0;
		sys_put_le32(uid, &resp[o]);
		o += 4;
		while (i < len) {
			uint8_t id = d[i++];
			uint16_t max = 0xFFFF;
			const uint8_t *val = NULL;
			size_t vl = 0;

			if (id == 1 || id == 2 || id == 3) {
				if (i + 2 > len) {
					return BT_GATT_ERR(0xA1);
				}
				max = sys_get_le16(&d[i]);
				i += 2;
			}
			switch (id) {
			case 0:
				val = (const uint8_t *)n->app;
				vl = strlen(n->app);
				break;
			case 1:
				val = (const uint8_t *)n->title;
				vl = strlen(n->title);
				break;
			case 3:
				val = n->msg;
				vl = n->msg_len;
				break;
			case 5:
				val = (const uint8_t *)n->date;
				vl = strlen(n->date);
				break;
			default:
				break; /* attributes the stand-in does not hold: length 0 */
			}
			if ((id == 1 || id == 2 || id == 3) && !n->ignore_max && vl > max) {
				vl = max; /* the iPhone cuts at the maximum length the client gave, in bytes */
			}
			resp[o++] = id;
			sys_put_le16((uint16_t)vl, &resp[o]);
			o += 2;
			if (val != NULL) {
				memcpy(&resp[o], val, vl);
				o += vl;
			}
		}
		resp_len = o;
		int h, slot = -1;

		for (h = 0; h < HOLDS; h++) {
			if (hold[h].ms > 0 && hold[h].uid == uid && (!hold[h].once || hold[h].taken == 0)) {
				break;
			}
		}
		for (int k = 0; k < PENDING && h < HOLDS; k++) {
			if (!pend[k].busy) {
				slot = k;
				break;
			}
		}
		if (h < HOLDS && slot >= 0) {
			/* scenario L: this answer is held back, then sent (once or twice) */
			hold[h].taken++;
			late_held++;
			pend[slot].busy = true;
			memcpy(pend[slot].buf, resp, resp_len);
			pend[slot].len = resp_len;
			pend[slot].copies = hold[h].copies > 0 ? hold[h].copies : 1;
			printk("PHONE INFO the answer for %u is held for %d ms (t=%lld)\n", uid, hold[h].ms, k_uptime_get());
			k_work_reschedule(&pend[slot].w, K_MSEC(hold[h].ms));
		} else {
			out_push(resp, resp_len);
		}
		return len;
	}
	if (d[0] == 2 && len == 6) {
		/* Perform Notification Action */
		uint32_t uid = sys_get_le32(&d[1]);
		uint8_t act = d[5];
		struct nrec *n = model_find(uid);

		/* every command is recorded BEFORE it can be refused, so a command for a notification without that
		 * action is seen even though the stand-in refuses it */
		if (ncmds < 16) {
			cmds[ncmds].uid = uid;
			cmds[ncmds].action = act;
			ncmds++;
		}
		if (n == NULL || (act == 0 && !(n->flags & 0x08)) || (act == 1 && !(n->flags & 0x10)) || act > 1) {
			flagless_cmds++;
			printk("PHONE INFO action %u for notification %u: it has no such action (refused)\n", act, uid);
		}
		if (n == NULL) {
			return BT_GATT_ERR(0xA2);
		}
		if ((act == 0 && !(n->flags & 0x08)) || (act == 1 && !(n->flags & 0x10)) || act > 1) {
			return BT_GATT_ERR(0xA3); /* action failed */
		}
		if (nactions < 16) {
			actions[nactions].uid = uid;
			actions[nactions].action = act;
			nactions++;
		}
		printk("PHONE INFO action %u for notification %u\n", act, uid);
		if (act == 1) {
			/* a dismissed notification is removed by the iPhone, which says so */
			removal_uid = uid;
			k_work_reschedule(&removal_work, K_MSEC(300));
		}
		return len;
	}
	return BT_GATT_ERR(0xA0); /* unknown command */
}

/* ======================================================================== AMS */

/* what the iPhone's player is doing; the stand-in changes it only by its script, never because of a command */
static char pl_info[24] = "0,0.0,0.000";
static char tr_title[80] = "Bohemian Rhapsody";
static char tr_artist[80] = "Queen";
static bool reg_playback, reg_artist, reg_title;
static struct k_work_delayable eu_work;
static bool pend_player, pend_track;

static void eu_send(uint8_t entity, uint8_t attr, const char *val)
{
	uint8_t p[3 + 100];
	size_t vl = strlen(val);
	size_t maxv;

	if (conn == NULL || !eu_on) {
		return;
	}
	maxv = bt_gatt_get_mtu(conn) - 3 - 3;
	p[0] = entity;
	p[1] = attr;
	p[2] = vl > maxv ? 1 : 0; /* EntityUpdateFlags bit 0: truncated to fit */
	if (vl > maxv) {
		vl = maxv;
	}
	memcpy(&p[3], val, vl);
	for (int tries = 0; tries < 50; tries++) {
		int err = bt_gatt_notify(conn, &ams_attrs[A_EU_VAL], p, 3 + vl);

		if (err != -ENOMEM) {
			printk("PHONE INFO EU %u/%u '%s' (%d)\n", entity, attr, val, err);
			return;
		}
		k_sleep(K_MSEC(10));
	}
}

static void eu_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	if (pend_player) {
		pend_player = false;
		if (reg_playback) {
			eu_send(0, 1, pl_info);
		}
	}
	if (pend_track) {
		pend_track = false;
		if (reg_artist) {
			eu_send(2, 0, tr_artist);
		}
		if (reg_title) {
			eu_send(2, 2, tr_title);
		}
	}
}

static ssize_t rc_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value)
{
	ARG_UNUSED(c);
	ARG_UNUSED(attr);
	return sizeof(value);
}

static ssize_t eu_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value)
{
	ARG_UNUSED(c);
	ARG_UNUSED(attr);
	eu_on = (value & BT_GATT_CCC_NOTIFY) != 0;
	eu_sub_count += eu_on ? 1 : 0;
	return sizeof(value);
}

static ssize_t rc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, const void *buf, uint16_t len,
			uint16_t offset, uint8_t flags)
{
	ARG_UNUSED(c);
	ARG_UNUSED(attr);
	ARG_UNUSED(flags);
	if (offset != 0 || len != 1) {
		return BT_GATT_ERR(0xA1); /* invalid command */
	}
	if (nrc < 16) {
		rc_cmds[nrc++] = ((const uint8_t *)buf)[0];
	}
	printk("PHONE INFO remote command %u\n", ((const uint8_t *)buf)[0]);
	/* the player's state is NOT changed here: a written command is not a proof that the player acted */
	return len;
}

static ssize_t eu_write(struct bt_conn *c, const struct bt_gatt_attr *attr, const void *buf, uint16_t len,
			uint16_t offset, uint8_t flags)
{
	const uint8_t *d = buf;

	ARG_UNUSED(c);
	ARG_UNUSED(attr);
	ARG_UNUSED(flags);
	if (!eu_on) {
		eu_bad_state++;
		return BT_GATT_ERR(0xA0); /* Invalid State: not subscribed to Entity Update (ams-spec.txt:206) */
	}
	if (offset != 0 || len < 2) {
		return BT_GATT_ERR(0xA1);
	}
	if (neu < 8) {
		eu_write_len[neu] = (uint8_t)MIN(len, 8);
		memcpy(eu_writes[neu], d, eu_write_len[neu]);
		neu++;
	}
	for (int i = 1; i < len; i++) {
		if (d[0] == 0 && d[i] == 1) {
			reg_playback = true;
			pend_player = true;
		} else if (d[0] == 2 && d[i] == 0) {
			reg_artist = true;
			pend_track = true;
		} else if (d[0] == 2 && d[i] == 2) {
			reg_title = true;
			pend_track = true;
		}
	}
	/* "the MR will immediately start getting the values of the entity/attribute pairs it registered" */
	k_work_reschedule(&eu_work, K_MSEC(40));
	return len;
}

static ssize_t ea_write(struct bt_conn *c, const struct bt_gatt_attr *attr, const void *buf, uint16_t len,
			uint16_t offset, uint8_t flags)
{
	ARG_UNUSED(c);
	ARG_UNUSED(attr);
	ARG_UNUSED(buf);
	ARG_UNUSED(offset);
	ARG_UNUSED(flags);
	return len;
}

static ssize_t ea_read(struct bt_conn *c, const struct bt_gatt_attr *attr, void *buf, uint16_t len, uint16_t offset)
{
	return bt_gatt_attr_read(c, attr, buf, len, offset, "", 0);
}

/* the script reports a new state or track: sent for the registered pairs only */
static void media_report_state(const char *info)
{
	strncpy(pl_info, info, sizeof(pl_info) - 1);
	if (reg_playback) {
		eu_send(0, 1, pl_info);
	}
}

static void media_report_track(const char *title, const char *artist)
{
	strncpy(tr_title, title, sizeof(tr_title) - 1);
	strncpy(tr_artist, artist, sizeof(tr_artist) - 1);
	if (reg_artist) {
		eu_send(2, 0, tr_artist);
	}
	if (reg_title) {
		eu_send(2, 2, tr_title);
	}
}

/* ======================================================================== CTS */

/* the time the iPhone shows (its local time): clock_offset_ms + uptime */
static int64_t clock_offset_ms;

static void civil_from_days(int64_t z, int *y, int *m, int *d)
{
	int64_t era, doe, yoe, doy, mp, yy;

	z += 719468;
	era = (z >= 0 ? z : z - 146096) / 146097;
	doe = z - era * 146097;
	yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
	yy = yoe + era * 400;
	doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
	mp = (5 * doy + 2) / 153;
	*d = (int)(doy - (153 * mp + 2) / 5 + 1);
	*m = (int)(mp + (mp < 10 ? 3 : -9));
	*y = (int)(yy + (*m <= 2 ? 1 : 0));
}

static void ct_value(uint8_t out[10], uint8_t reason)
{
	int64_t ms = clock_offset_ms + k_uptime_get();
	int64_t days = ms / 86400000LL;
	int64_t rem = ms % 86400000LL;
	int y, m, d;

	civil_from_days(days, &y, &m, &d);
	sys_put_le16((uint16_t)y, &out[0]);
	out[2] = (uint8_t)m;
	out[3] = (uint8_t)d;
	out[4] = (uint8_t)(rem / 3600000);
	out[5] = (uint8_t)((rem / 60000) % 60);
	out[6] = (uint8_t)((rem / 1000) % 60);
	out[7] = (uint8_t)(((days + 3) % 7) + 1); /* 1 Monday .. 7 Sunday; 1970-01-01 was a Thursday */
	out[8] = (uint8_t)((rem % 1000) * 256 / 1000);
	out[9] = reason;
}

static ssize_t ct_read(struct bt_conn *c, const struct bt_gatt_attr *attr, void *buf, uint16_t len, uint16_t offset)
{
	uint8_t v[10];

	ct_value(v, 0);
	ct_reads++;
	return bt_gatt_attr_read(c, attr, buf, len, offset, v, sizeof(v));
}

/* Local Time Information, 2 bytes: time zone int8 in 15-minute units east of UTC (-128 unknown), daylight saving offset
 * uint8 (0, 2, 4, 8 = 0, +0.5, +1, +2 h; 255 unknown). The author's reading of the Bluetooth SIG specification: NOT from
 * a saved document or a kit file (docs/iphone-notes.md section 3). */
static int8_t lti_tz = -128;
static uint8_t lti_dst = 255;
static int lti_reads;
static int lti_fail_next; /* the next read of Local Time Information fails with an ATT error */

static ssize_t lti_read(struct bt_conn *c, const struct bt_gatt_attr *attr, void *buf, uint16_t len, uint16_t offset)
{
	uint8_t v[2] = { (uint8_t)lti_tz, lti_dst };

	lti_reads++;
	if (lti_fail_next > 0) {
		lti_fail_next--;
		printk("PHONE INFO the Local Time Information read is refused (t=%lld)\n", k_uptime_get());
		return BT_GATT_ERR(BT_ATT_ERR_UNLIKELY);
	}
	return bt_gatt_attr_read(c, attr, buf, len, offset, v, sizeof(v));
}

static ssize_t ct_ccc_write(struct bt_conn *c, const struct bt_gatt_attr *attr, uint16_t value)
{
	ARG_UNUSED(c);
	ARG_UNUSED(attr);
	ct_on = (value & BT_GATT_CCC_NOTIFY) != 0;
	ct_sub_count += ct_on ? 1 : 0;
	return sizeof(value);
}

/* the iPhone's time changed (the wearer set it, or the zone changed); the reason byte stays 0 */
static void time_change(int64_t delta_ms)
{
	uint8_t v[10];

	clock_offset_ms += delta_ms;
	if (conn != NULL && ct_on) {
		ct_value(v, 0); /* the ADG: the iPhone gives no Adjust Reason when the current time changes */
		(void)bt_gatt_notify(conn, &cts_attrs[A_CT_VAL], v, sizeof(v));
	}
}

/* ======================================================================== HID client (the ring's keys) */

struct rec {
	int64_t t;
	uint8_t id;
	uint8_t len;
	uint8_t d[8];
};
static struct rec recs[32];
static int nrec;
static struct bt_hogp hogp;
static bool bonded;
static bt_addr_le_t bond_addr;
static bool connecting;
static int64_t hid_ready_t;
static int pairings;
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
		printk("PHONE REPORT t=%lld id=%u len=%u data=%02x%02x\n", r->t, r->id, r->len, r->d[0], r->d[1]);
	}
	return BT_GATT_ITER_CONTINUE;
}

static void ready_fn(struct k_work *w)
{
	struct bt_hogp_rep_info *rep = NULL;
	int subs = 0;

	ARG_UNUSED(w);
	while ((rep = bt_hogp_rep_next(&hogp, rep)) != NULL) {
		if (bt_hogp_rep_type(rep) == BT_HIDS_REPORT_TYPE_INPUT && bt_hogp_rep_subscribe(&hogp, rep, notify_cb) == 0) {
			subs++;
		}
	}
	hid_ready_t = k_uptime_get();
	printk("PHONE INFO HID client subscribed to %d input reports (t=%lld)\n", subs, k_uptime_get());
}

static void hogp_ready(struct bt_hogp *h)
{
	ARG_UNUSED(h);
	k_work_submit(&ready_work);
}

static void hogp_prep_error(struct bt_hogp *h, int err)
{
	ARG_UNUSED(h);
	printk("PHONE HID client preparation failed %d\n", err);
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
		printk("PHONE HID handles not assigned %d\n", err);
	}
	(void)bt_gatt_dm_data_release(dm);
}

static void dm_missing(struct bt_conn *c, void *ctx)
{
	ARG_UNUSED(c);
	ARG_UNUSED(ctx);
	printk("PHONE HID service not found\n");
}

static void dm_error(struct bt_conn *c, int err, void *ctx)
{
	ARG_UNUSED(c);
	ARG_UNUSED(ctx);
	printk("PHONE discovery failed %d\n", err);
}

static const struct bt_gatt_dm_cb dm_cb = {
	.completed = dm_done,
	.service_not_found = dm_missing,
	.error_found = dm_error,
};

static void mtu_done(struct bt_conn *c, uint8_t err, struct bt_gatt_exchange_params *p)
{
	ARG_UNUSED(c);
	ARG_UNUSED(p);
	printk("PHONE INFO MTU exchange %u, MTU %u\n", err, bt_gatt_get_mtu(c));
}

static struct bt_gatt_exchange_params mtu_params = { .func = mtu_done };

static void on_connected(struct bt_conn *c, uint8_t err)
{
	connecting = false;
	if (err != 0) {
		printk("PHONE connect failed 0x%02x\n", err);
		if (conn != NULL) {
			bt_conn_unref(conn);
			conn = NULL;
		}
		k_work_reschedule(&scan_work, K_MSEC(300));
		return;
	}
	printk("PHONE connected (t=%lld), bonded=%d\n", k_uptime_get(), bonded);
	(void)bt_gatt_exchange_mtu(c, &mtu_params);
	(void)bt_conn_set_security(c, BT_SECURITY_L4);
}

static void on_disconnected(struct bt_conn *c, uint8_t reason)
{
	ARG_UNUSED(c);
	printk("PHONE disconnected reason 0x%02x (t=%lld)\n", reason, k_uptime_get());
	(void)k_work_cancel(&ready_work);
	(void)k_work_cancel_delayable(&ds_work);
	(void)k_work_cancel_delayable(&replay_work);
	(void)k_work_cancel_delayable(&eu_work);
	(void)k_work_cancel_delayable(&removal_work);
	if (bt_hogp_assign_check(&hogp)) {
		bt_hogp_release(&hogp);
	}
	/* the link's subscriptions are gone; the iPhone keeps its notifications */
	ns_on = ds_on = eu_on = ct_on = false;
	reg_playback = reg_artist = reg_title = false;
	pend_player = pend_track = false;
	out_n = 0;
	out_off = 0;
	for (int k = 0; k < PENDING; k++) {
		(void)k_work_cancel_delayable(&pend[k].w);
		pend[k].busy = false;
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
		printk("PHONE security level %u (t=%lld)\n", level, k_uptime_get());
		CHECK("link encrypted and authenticated (security level 4)", level == BT_SECURITY_L4);
		(void)bt_gatt_dm_start(c, BT_UUID_HIDS, &dm_cb, NULL);
		return;
	}
	printk("PHONE security failed err %d (t=%lld)\n", err, k_uptime_get());
	(void)bt_conn_disconnect(c, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
}

BT_CONN_CB_DEFINE(phone_conn_cb) = {
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
	printk("PHONE pairing cancelled\n");
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
	printk("PHONE pairing failed %d\n", reason);
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
	if (conn != NULL || connecting || type != BT_GAP_ADV_TYPE_ADV_IND || k_uptime_get() < resume_at) {
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
		printk("PHONE scan start failed %d\n", err);
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
	scan_start();
}

/* ======================================================================== script */

#define BASE_MS 1794434746000LL /* 2026-11-11T22:05:46Z: the time the iPhone shows when the stand-in starts */

static void rel_to(int64_t base, int64_t t_ms)
{
	int64_t at = base + t_ms;

	if (k_uptime_get() < at) {
		k_sleep(K_MSEC(at - k_uptime_get()));
	}
}

static void rel(int64_t t_ms)
{
	rel_to(t0, t_ms);
}

static bool wait_for(bool (*cond)(void), int64_t timeout_ms)
{
	int64_t end = k_uptime_get() + timeout_ms;

	while (k_uptime_get() < end) {
		if (cond()) {
			return true;
		}
		k_sleep(K_MSEC(50));
	}
	return cond();
}

static bool have_t0(void)
{
	return t0 != 0;
}

static bool second_subscription(void)
{
	return ns_sub_count >= 2;
}

static bool third_subscription(void)
{
	return ns_sub_count >= 3;
}

static void add(uint32_t uid, uint8_t cat, uint8_t flags, const char *app, const char *title, const void *msg,
		size_t msg_len, const char *date, bool ignore_max)
{
	(void)model_set(uid, cat, flags, app, title, msg, msg_len, date, ignore_max);
	ns_send(0, flags, cat, uid);
}

static void modify(uint32_t uid, uint8_t flags, const char *msg)
{
	struct nrec *n = model_find(uid);

	if (n != NULL) {
		n->flags = flags;
		if (msg != NULL) {
			n->msg_len = (uint16_t)strlen(msg);
			memcpy(n->msg, msg, n->msg_len);
		}
		ns_send(1, flags, n->cat, uid);
	}
}

static void remove_n(uint32_t uid)
{
	struct nrec *n = model_find(uid);

	if (n != NULL) {
		uint8_t cat = n->cat, fl = n->flags;

		n->used = false;
		ns_send(2, fl, cat, uid);
	}
}

/* 66 times U+20AC (E2 82 AC) and "xy": 200 bytes; a byte limit of 160 falls inside a character */
static uint8_t euro200[200];

static void script_n(void)
{
	char t[32], m[48], d[24];

	wait_for(have_t0, 120000);
	rel(2000);
	add(101, 4, 0x1A, "com.apple.MobileSMS", "Anna", "Hello, are you there?", 21, "20261111T220546", false);
	rel(3000);
	add(102, 6, 0x10, "com.apple.mobilemail", "Weekly report", "The numbers are in. Please review before Friday.", 48,
	    "20261111T220612", false);
	rel(4000);
	add(103, 4, 0x11, "com.example.chat.messenger.with.a.very.long.identifier.0123456789",
	    "Long title: 0123456789 0123456789 0123456789 0123456789", euro200, 200, "20261111T220701", false);
	rel(5000);
	add(104, 0, 0x00, "com.apple.reminders", "Buy milk", "", 0, "20261111T220710", false);
	rel(6000);
	add(105, 11, 0x10, "com.spotify.client", "New release", euro200, 200, "20261111T220733", true);
	/* the iPhone changes the text and takes the positive action away */
	rel(9000);
	modify(101, 0x12, "Hello, are you there? Please answer.");
	rel(11000);
	remove_n(102);
	/* thirteen more: the 17th notification in the ring's store pushes the oldest out */
	for (int i = 0; i < 13; i++) {
		rel(13000 + 500 * i);
		snprintk(t, sizeof(t), "Bulk %d", 110 + i);
		snprintk(m, sizeof(m), "Bulk message %d", 110 + i);
		snprintk(d, sizeof(d), "20261111T2210%02d", i);
		add(110 + i, 4, 0x18, "com.example.bulk", t, m, strlen(m), d, false);
	}
	/* the iPhone's player: a new track and the player starts; the ring sends six commands meanwhile (no change of state) */
	rel(28000);
	media_report_track("Under Pressure", "Queen and David Bowie");
	media_report_state("1,1.0,0.000");
	rel(38000);
	media_report_state("0,0.0,5.000");
	/* the iPhone's time moves two hours */
	rel(40000);
	time_change(7200000LL);
	/* a notification whose zone read fails (the ring must keep the zone it knows) */
	rel(42500);
	lti_fail_next = 1;
	time_change(0);
	/* during the ring's RECORDING (the ring starts it at 45 s and stops it at 57 s) */
	rel(48000);
	add(130, 4, 0x10, "com.example.rec", "During recording", "added", 5, "20261111T221800", false);
	rel(49000);
	modify(130, 0x10, "changed while recording");
	rel(50000);
	media_report_track("In recording", "Artist R");
	media_report_state("1,1.0,9.000");
	rel(51000);
	time_change(60000LL);
	rel(52000);
	remove_n(130);
	/* during STANDBY after the recording */
	rel(60000);
	add(131, 4, 0x10, "com.example.standby", "During standby", "added", 5, "20261111T222000", false);
	rel(61000);
	modify(131, 0x10, "changed in standby");
	rel(62000);
	media_report_track("In standby", "Artist S");
	media_report_state("0,0.0,10.000");
	rel(63000);
	time_change(60000LL);
	rel(64000);
	remove_n(131);
}

static void script_r(void)
{
	int64_t b;

	wait_for(have_t0, 120000);
	rel(2000);
	add(201, 4, 0x18, "com.example.one", "First", "first message", 13, "20261111T230000", false);
	rel(3000);
	add(202, 6, 0x10, "com.example.two", "Second", "second message", 14, "20261111T230010", false);
	/* the link drops; the stand-in stays away for 9 s; meanwhile the iPhone's notifications change */
	rel(9000);
	if (conn != NULL) {
		printk("PHONE INFO the link is ended (a drop) (t=%lld)\n", k_uptime_get());
		resume_at = k_uptime_get() + 9000;
		(void)bt_conn_disconnect(conn, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
	}
	rel(10000);
	{
		struct nrec *n = model_find(202);

		if (n != NULL) {
			n->used = false; /* gone while away: no event can be sent */
		}
		n = model_find(201);
		if (n != NULL) {
			strncpy((char *)n->msg, "first message, edited while away", sizeof(n->msg) - 1);
			n->msg_len = (uint16_t)strlen((const char *)n->msg);
		}
		(void)model_set(203, 0, 0x00, "com.example.three", "Third", "third message", 13, "20261111T230100", false);
	}
	/* the ring comes back (ns_sub_count 2): it holds what is sent again */
	wait_for(second_subscription, 60000);
	b = k_uptime_get();
	/* the Notification Center Service disappears (Service Changed), then comes back */
	rel_to(b, 8000);
	printk("PHONE INFO the Notification Center Service is removed (t=%lld)\n", k_uptime_get());
	ns_on = ds_on = false;
	(void)bt_gatt_service_unregister(&ancs_svc);
	rel_to(b, 16000);
	printk("PHONE INFO the Notification Center Service is added again (t=%lld)\n", k_uptime_get());
	(void)bt_gatt_service_register(&ancs_svc);
	wait_for(third_subscription, 30000);
	b = k_uptime_get();
	rel_to(b, 4000);
	add(204, 5, 0x18, "com.example.four", "Fourth", "fourth message after the service came back", 42, "20261111T230200", false);
}

static bool chk_request(int i, uint32_t *uid)
{
	static const uint8_t tail[8] = { 0x00, 0x01, 0x30, 0x00, 0x03, 0xA0, 0x00, 0x05 };

	if (cp_log_len[i] != 13 || cp_log[i][0] != 0 || memcmp(&cp_log[i][5], tail, 8) != 0) {
		return false;
	}
	*uid = sys_get_le32(&cp_log[i][1]);
	return true;
}

static void eval_n(void)
{
	static const uint32_t want[] = { 101, 102, 103, 104, 105, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
					 120, 121, 122, 130, 131 };
	int gets = 0, bad = 0, distinct = 0;
	bool seen[ARRAY_SIZE(want)] = { false };

	CHECK("ring subscribed to the Notification Source once, on a level 4 link", ns_sub_count == 1 && ns_sub_level == BT_SECURITY_L4);
	CHECK("ring subscribed to the Data Source once", ds_sub_count == 1);
	for (int i = 0; i < ncp; i++) {
		uint32_t uid;

		if (cp_log[i][0] != 0) {
			continue;
		}
		gets++;
		if (!chk_request(i, &uid)) {
			bad++;
			continue;
		}
		for (size_t k = 0; k < ARRAY_SIZE(want); k++) {
			if (want[k] == uid && !seen[k]) {
				seen[k] = true;
				distinct++;
			}
		}
	}
	printk("PHONE INFO %d Get Notification Attributes requests, %d malformed, %d distinct ids\n", gets, bad, distinct);
	CHECK("every Get Notification Attributes request is the 13 bytes Apple's format and the kit's encoder give", bad == 0 && gets > 0);
	CHECK("attributes were requested for each of the 20 notifications", distinct == (int)ARRAY_SIZE(want));
	CHECK("23 attribute requests (20 added, 3 modified)", gets == 23);
	CHECK("two actions arrived: negative for 122, positive for 121, and no other",
	      nactions == 2 && actions[0].uid == 122 && actions[0].action == 1 && actions[1].uid == 121 &&
		      actions[1].action == 0);
	CHECK("the six media commands arrived: play, pause, next, previous, volume up, volume down (ids 0,1,3,4,5,6), "
	      "then play again (id 0)",
	      nrc == 7 && rc_cmds[0] == 0 && rc_cmds[1] == 1 && rc_cmds[2] == 3 && rc_cmds[3] == 4 && rc_cmds[4] == 5 &&
		      rc_cmds[5] == 6 && rc_cmds[6] == 0);
	CHECK("no action command arrived for a notification that does not have that action (every command is recorded "
	      "before it can be refused)", ncmds == 2 && flagless_cmds == 0);
	CHECK("the ring read Local Time Information", lti_reads >= 1);
	CHECK("the ring wrote Entity Update twice: player playback info, track artist and title",
	      neu == 2 && eu_write_len[0] == 2 && eu_writes[0][0] == 0 && eu_writes[0][1] == 1 && eu_write_len[1] == 3 &&
		      eu_writes[1][0] == 2 && eu_writes[1][1] == 0 && eu_writes[1][2] == 2);
	CHECK("the ring never wrote Entity Update before subscribing to it", eu_bad_state == 0 && eu_sub_count == 1);
	CHECK("the ring subscribed to Current Time and read it", ct_sub_count == 1 && ct_reads >= 1);
	CHECK("the ring's key arrived once (media centre: usage 0x00CD, then release)",
	      nrec == 2 && recs[0].id == 2 && recs[0].len == 2 && recs[0].d[0] == 0xCD && recs[0].d[1] == 0x00 &&
		      recs[1].id == 2 && recs[1].d[0] == 0 && recs[1].d[1] == 0);
}

static void script_l(void)
{
	wait_for(have_t0, 120000);
	/* The answer for 401 is held 3.5 s, past the ring's 3 s timeout, and then sent twice (200 ms apart). The answers to
	 * requests for 402 (every one) are held 1 s. So when the ring has given up 401 and asked again, and has gone on to
	 * 402, the late answers for 401 arrive INSIDE the request for 402 (at about 3.5 s and 3.7 s). A parser that takes bytes
	 * that are not its answer as an error spoils the request twice (the first attempt and its retry), and 402 gets no text. */
	hold[0].uid = 401;
	hold[0].ms = 3500;
	hold[0].once = true;
	hold[0].copies = 2;
	hold[1].uid = 402;
	hold[1].ms = 1000;
	hold[1].once = false;
	rel(2000);
	add(401, 4, 0x18, "com.example.l1", "Late one", "message one", 11, "20261111T231000", false);
	add(402, 4, 0x18, "com.example.l2", "Late two", "message two", 11, "20261111T231001", false);
	add(403, 4, 0x18, "com.example.l3", "Late three", "message three", 13, "20261111T231002", false);
	add(404, 4, 0x18, "com.example.l4", "Late four", "message four", 12, "20261111T231003", false);
	/* later notifications must still get their own text */
	rel(14000);
	add(405, 4, 0x18, "com.example.l5", "Late five", "message five", 12, "20261111T231004", false);
}

static void script_d(void)
{
	int64_t b;

	drop_in_discovery = true;
	/* the first link ends 60 ms after the ring subscribed to the Data Source (drop_fn), so the ring is still discovering */
	while (!dropped) {
		k_sleep(K_MSEC(100));
	}
	/* wait for the ring's next session: the Notification Source is subscribed on a new link */
	k_sleep(K_MSEC(1000));
	while (conn == NULL || !ns_on) {
		k_sleep(K_MSEC(100));
	}
	b = k_uptime_get();
	rel_to(b, 3000);
	add(301, 4, 0x18, "com.example.d1", "After the drop", "found in the next session", 25, "20261111T231100", false);
}

static void eval_d(void)
{
	CHECK("the link ended before the ring had subscribed to Media and Time (the drop came during discovery)",
	      eu_at_drop == 0 && ct_at_drop == 0);
	CHECK("in the next session the ring subscribed to the Notification Source, Entity Update and Current Time",
	      ns_sub_count >= 1 && eu_sub_count == 1 && ct_sub_count == 1);
	CHECK("the ring never wrote Entity Update before subscribing to it", eu_bad_state == 0);
}

static void eval_l(void)
{
	int gets = 0, g401 = 0, bad = 0;

	for (int i = 0; i < ncp; i++) {
		uint32_t uid;

		if (cp_log[i][0] != 0) {
			continue;
		}
		gets++;
		if (!chk_request(i, &uid)) {
			bad++;
		} else if (uid == 401) {
			g401++;
		}
	}
	printk("PHONE INFO %d requests, %d for 401, %d malformed\n", gets, g401, bad);
	CHECK("the answer for 401 was held past the timeout and sent twice, and the answers for 402 were held",
	      hold[0].taken == 1 && hold[1].taken >= 1);
	CHECK("the ring asked for 401 twice (the timeout, then one retry) and once for each other notification",
	      g401 == 2 && gets == 6 && bad == 0);
}

/* scenario Z: the zone changes while linked. The iPhone's local time jumps with it; the UTC time does not. */
static void script_z(void)
{
	wait_for(have_t0, 120000);
	rel(10000);
	lti_tz = 8;  /* +2 h */
	lti_dst = 4; /* and +1 h daylight saving: 180 minutes */
	time_change(7200000LL); /* local time: +2 h (60 -> 180 minutes), UTC unchanged */
}

static void eval_z(void)
{
	CHECK("the ring read Local Time Information at the start and again after the zone change", lti_reads >= 2);
}

/* scenario W: the iPhone has the Current Time Service but not Local Time Information */
static void script_w(void)
{
	wait_for(have_t0, 120000);
	rel(6000);
	time_change(3600000LL);
}

static void eval_w(void)
{
	CHECK("the ring subscribed to Current Time and never read Local Time Information (there is none)",
	      ct_sub_count == 1 && lti_reads == 0);
}

static void eval_r(void)
{
	CHECK("the ring subscribed to the Notification Source three times (start, after the drop, after Service Changed)",
	      ns_sub_count == 3);
	CHECK("the ring subscribed to Entity Update and Current Time four times (start, after the drop, and after each of the two Service Changed)", eu_sub_count == 4 && ct_sub_count == 4);
	CHECK("the ring never wrote Entity Update before subscribing to it", eu_bad_state == 0);
}

static void eval_p(void)
{
	CHECK("no Apple service was served", !apple && ns_sub_count == 0 && eu_sub_count == 0 && ct_sub_count == 0);
	CHECK("the ring's key arrived once (media centre: usage 0x00CD, then release)",
	      nrec == 2 && recs[0].id == 2 && recs[0].len == 2 && recs[0].d[0] == 0xCD && recs[0].d[1] == 0x00 &&
		      recs[1].id == 2 && recs[1].d[0] == 0 && recs[1].d[1] == 0);
}

int main(void)
{
	char *s = nsi_host_getenv("RING_SCENARIO");
	int err;

	scen = s != NULL ? s[0] : '?';
	apple = (scen != 'P');
	printk("PHONE START scenario %c\n", scen);
	for (int i = 0; i < 66; i++) {
		euro200[3 * i] = 0xE2;
		euro200[3 * i + 1] = 0x82;
		euro200[3 * i + 2] = 0xAC;
	}
	euro200[198] = 'x';
	euro200[199] = 'y';
	clock_offset_ms = BASE_MS;
	if (scen == 'N') {
		lti_tz = 4;  /* +1 h */
		lti_dst = 4; /* +1 h daylight saving: the local time is UTC + 2 h */
	}
	if (scen == 'Z') {
		lti_tz = 4;  /* +1 h, standard time */
		lti_dst = 0;
	}

	k_work_init_delayable(&scan_work, scan_fn);
	k_work_init_delayable(&replay_work, replay_fn);
	k_work_init_delayable(&ds_work, ds_fn);
	for (int k = 0; k < PENDING; k++) {
		k_work_init_delayable(&pend[k].w, late_fn);
	}
	k_work_init_delayable(&drop_work, drop_fn);
	k_work_init_delayable(&removal_work, removal_fn);
	k_work_init_delayable(&eu_work, eu_fn);
	k_work_init(&ready_work, ready_fn);
	bt_hogp_init(&hogp, &hogp_params);
	(void)bt_conn_auth_cb_register(&auth_cb);
	(void)bt_conn_auth_info_cb_register(&info_cb);
	err = bt_enable(NULL);
	CHECK("Bluetooth up", err == 0);
	if (err != 0) {
		printk("PHONE RESULT FAIL\n");
		return 0;
	}
	if (apple) {
		CHECK("the three Apple services are registered",
		      bt_gatt_service_register(&ancs_svc) == 0 && bt_gatt_service_register(&ams_svc) == 0 &&
			      bt_gatt_service_register(scen == 'W' ? &cts_svc_nolti : &cts_svc) == 0);
	}
	k_sleep(K_MSEC(500));
	scan_start();

	if (scen == 'N') {
		script_n();
		k_sleep(K_MSEC(t0 + 95000 - k_uptime_get())); /* long after the ring's script, also in a broken copy that waits out its timeouts */
		printk("PHONE EVAL t=%lld\n", k_uptime_get());
		eval_n();
	} else if (scen == 'R') {
		script_r();
		k_sleep(K_MSEC(15000));
		printk("PHONE EVAL t=%lld\n", k_uptime_get());
		eval_r();
	} else if (scen == 'L') {
		script_l();
		k_sleep(K_MSEC(t0 + 75000 - k_uptime_get())); /* long after the ring's script, also in a broken copy that waits out its timeouts */
		printk("PHONE EVAL t=%lld\n", k_uptime_get());
		eval_l();
	} else if (scen == 'Z') {
		script_z();
		k_sleep(K_MSEC(t0 + 30000 - k_uptime_get()));
		printk("PHONE EVAL t=%lld\n", k_uptime_get());
		eval_z();
	} else if (scen == 'W') {
		script_w();
		k_sleep(K_MSEC(t0 + 30000 - k_uptime_get()));
		printk("PHONE EVAL t=%lld\n", k_uptime_get());
		eval_w();
	} else if (scen == 'D') {
		script_d();
		k_sleep(K_MSEC(15000));
		printk("PHONE EVAL t=%lld\n", k_uptime_get());
		eval_d();
	} else if (scen == 'P') {
		wait_for(have_t0, 1); /* t0 is never set: no Apple service */
		while (hid_ready_t == 0) {
			k_sleep(K_MSEC(100));
		}
		k_sleep(K_MSEC(hid_ready_t + 40000 - k_uptime_get()));
		printk("PHONE EVAL t=%lld\n", k_uptime_get());
		eval_p();
	} else {
		CHECK("known scenario", false);
	}
	printk("PHONE RESULT %s checks=%d fails=%d\n", fails == 0 ? "PASS" : "FAIL", checks, fails);
	while (1) {
		k_sleep(K_SECONDS(1));
	}
	return 0;
}
