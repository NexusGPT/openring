/*
 * Ring side of the relay test (BabbleSim, the simulated ring chip nrf54lm20bsim, real encryption: see run.sh).
 *
 * The real ring_devices, ring_control, ring_glue, ring_inbox, ring_time, ring_iphone, ring_relay and ring_core modules run here, and
 * ring_screens with its memory display. The stand-in helper (host_app) pairs with the ring through the passkey the screen shows, finds the
 * relay service and writes frames to it. Everything the wearer does is a joystick edge into rglue_input(). Every expected value is a literal
 * written here from design/firmware.md section 7.7.
 *
 *   H  the helper: Info, HELLO, notifications in pieces of 11 bytes, the screens, actions, REMOVE, RECORDING, malformed frames, a dropped
 *      link and the rebuilt store, a write before security level 4 (the stand-in's side)
 *   I  one source per link: the stand-in is an iPhone (it serves the notification service) and also writes relay frames: every one is
 *      refused with code 7, the iPhone's notification stays, and a dismiss on the ring reaches the iPhone's service
 *
 * The two programs hand each other stage numbers through files (RING_SYNC written here, HELPER_SYNC written by the stand-in): simulated time
 * is shared, so a stage written by one is seen by the other at its next poll.
 *
 * Output lines contain "RING": CHECK <name> PASS|FAIL, one "RING RESULT PASS|FAIL". Times are simulated ms.
 */

#include <errno.h>
#include <stdlib.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/bluetooth/bluetooth.h>

#include <ring_core/rc_core.h>
#include <ring_devices/rdev.h>
#include <ring_control/rctl.h>
#include <ring_glue/rglue.h>
#include <ring_iphone/rip.h>
#include <ring_relay/rrl_bt.h>
#include <ring_screens/rmd.h>
#include <ring_screens/rscr.h>
#include "hosttools.h"

static int fails;
static int checks;

/* A wait for the other program's stage is not a check: it is printed as "RING WAIT", it is not counted in the checks, and a wait that times out
 * fails the run. */
#define WAIT(name, cond)                                                                           \
	do {                                                                                       \
		bool ok_ = (cond);                                                                 \
		fails += ok_ ? 0 : 1;                                                              \
		printk("RING WAIT %s %s (t=%lld)\n", name, ok_ ? "PASS" : "FAIL", k_uptime_get()); \
	} while (0)

#define CHECK(name, cond)                                                                          \
	do {                                                                                       \
		bool ok_ = (cond);                                                                 \
		checks++;                                                                          \
		fails += ok_ ? 0 : 1;                                                              \
		printk("RING CHECK %s %s (t=%lld)\n", name, ok_ ? "PASS" : "FAIL", k_uptime_get()); \
	} while (0)

/* ------------------------------------------------------------------ files shared with the stand-in */

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

static void write_passkey(uint32_t passkey)
{
	char buf[16];
	int n = snprintk(buf, sizeof(buf), "%06u\n", passkey);

	write_file("RING_PASSFILE", buf, n);
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

static int helper_seen;

static void stage(int n)
{
	char buf[16];
	int len = snprintk(buf, sizeof(buf), "%d\n", n);

	write_file("RING_SYNC", buf, len);
	printk("RING INFO stage %d (t=%lld)\n", n, k_uptime_get());
}

/* wait until the stand-in has written a stage of at least n */
static bool wait_helper(int n, int64_t timeout_ms)
{
	int64_t end = k_uptime_get() + timeout_ms;

	while (k_uptime_get() < end) {
		int v = read_stage("HELPER_SYNC");

		if (v > helper_seen) {
			helper_seen = v;
		}
		if (helper_seen >= n) {
			return true;
		}
		k_sleep(K_MSEC(20));
	}
	return helper_seen >= n;
}

/* ------------------------------------------------------------------ the devices part's callbacks go to the screens, as in the product */

static uint32_t shown_passkey;
static int passkey_calls;
static struct rrl_stats stats_at_passkey;
static int rec_starts, rec_stops;

static void on_passkey(uint8_t slot, uint32_t passkey)
{
	shown_passkey = passkey;
	passkey_calls++;
	printk("RING PASSKEY slot %u %06u\n", slot, passkey);
	/* what the relay part has seen so far: the stand-in tried to write before the link was secure */
	rrl_stats_get(&stats_at_passkey);
	rscr_on_passkey(slot, passkey);
	write_passkey(passkey);
}

static void on_paired(uint8_t slot)
{
	printk("RING EVENT paired slot %u\n", slot);
	rscr_on_paired(slot);
}

static void on_window_closed(void)
{
	rscr_on_window_closed();
}

static void on_removed(uint8_t slot)
{
	rscr_on_removed(slot);
}

static void on_active(uint8_t slot)
{
	rscr_on_active_changed(slot);
}

static void on_link(uint8_t slot, bool up)
{
	printk("RING EVENT link slot %u %s\n", slot, up ? "up" : "down");
	rscr_poke();
}

static const struct rdev_callbacks cbs = {
	.passkey_show = on_passkey,
	.paired = on_paired,
	.window_closed = on_window_closed,
	.removed = on_removed,
	.active_changed = on_active,
	.link = on_link,
};

static void recording_hook(enum rc_action a, rc_ms_t t)
{
	if (a == RC_ACT_OPEN) {
		rec_starts++;
		printk("RING EVENT recording start (t=%lld)\n", t);
	} else if (a == RC_ACT_CLOSE) {
		rec_stops++;
		printk("RING EVENT recording stop (t=%lld)\n", t);
	}
}

static const struct rglue_ops glue_ops = {
	.action = recording_hook,
	.after = rscr_glue_after,
	.screen_fact = rscr_lock_fact_now,
};

/* A fault hook for the broken copy "relay_reaches_core": a broken ring_relay calls this when a frame arrives, so that the frame reaches
 * the joystick path (a centre hold, a long press), only while a recording runs. */
static struct k_work_delayable fault_release;
static void fault_release_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	rglue_input(RC_SW_CENTRE, false);
}
void bsim_fault_hook(void)
{
	if (rglue_state() == RC_ST_RECORDING) {
		rglue_input(RC_SW_CENTRE, true);
		k_work_reschedule(&fault_release, K_MSEC(1200));
	}
}

/* A fault hook for the broken copy "relay_wakes_screen": a broken ring_relay calls this when a frame arrives, so that the frame turns the screen
 * on (a joystick event) while it is off. */
void bsim_wake_hook(void)
{
	struct rscr sn;

	rscr_snapshot(&sn);
	if (sn.screen == SCR_OFF) {
		rglue_input(RC_SW_DOWN, true);
		rglue_input(RC_SW_DOWN, false);
	}
}

static void press(enum rc_switch sw)
{
	rglue_input(sw, true);
	k_sleep(K_MSEC(80));
	rglue_input(sw, false);
	k_sleep(K_MSEC(700));
}

static void hold(enum rc_switch sw, int ms)
{
	rglue_input(sw, true);
	k_sleep(K_MSEC(ms));
	rglue_input(sw, false);
	k_sleep(K_MSEC(700));
}

static enum rscr_screen screen(void)
{
	struct rscr s;

	rscr_sync();
	rscr_snapshot(&s);
	return (enum rscr_screen)s.screen;
}

static uint64_t frame_hash(void)
{
	rscr_sync();
	return rmd_hash();
}

/* The screen turns off 5 s after the last input (RSCR_OFF_MS). While the ring waits for the stand-in on the notification list, Up is pressed
 * every 3 s: on the list it only keeps the selection at or moves it towards the first entry, and it keeps the screen on. */
static bool wait_awake(bool (*cond)(intptr_t), intptr_t arg, int64_t timeout_ms)
{
	int64_t end = k_uptime_get() + timeout_ms;
	int64_t next_touch = k_uptime_get() + 3000;

	while (k_uptime_get() < end) {
		if (cond(arg)) {
			return true;
		}
		if (k_uptime_get() >= next_touch) {
			rglue_input(RC_SW_UP, true);
			k_sleep(K_MSEC(80));
			rglue_input(RC_SW_UP, false);
			next_touch = k_uptime_get() + 3000;
		}
		k_sleep(K_MSEC(20));
	}
	return cond(arg);
}

static bool wait_arg(bool (*cond)(intptr_t), intptr_t arg, int64_t timeout_ms)
{
	int64_t end = k_uptime_get() + timeout_ms;

	while (k_uptime_get() < end) {
		if (cond(arg)) {
			return true;
		}
		k_sleep(K_MSEC(20));
	}
	return cond(arg);
}

/* ------------------------------------------------------------------ the store, as the screens read it */

static bool item_is(uint8_t at, uint32_t uid, uint8_t cat, uint8_t flags, const char *app, const char *title, const char *msg,
		    const char *date)
{
	struct rinbox_item it;

	if (!rip_inbox_get(at, &it)) {
		return false;
	}
	return it.uid == uid && it.category == cat && it.flags == flags && it.text_ready && strcmp(it.app, app) == 0 &&
	       strcmp(it.title, title) == 0 && strcmp(it.msg, msg) == 0 && strcmp(it.date, date) == 0;
}

static bool item_read(uint8_t at)
{
	struct rinbox_item it;

	return rip_inbox_get(at, &it) && it.read;
}

static bool no_item_read(void)
{
	for (uint8_t i = 0; i < rip_inbox_count(); i++) {
		if (item_read(i)) {
			return false;
		}
	}
	return true;
}

static int find_uid(uint32_t uid)
{
	for (uint8_t i = 0; i < rip_inbox_count(); i++) {
		struct rinbox_item it;

		if (rip_inbox_get(i, &it) && it.uid == uid) {
			return i;
		}
	}
	return -1;
}

/* the ids in the store, newest first, as a list of the given length */
static bool ids_are(const uint32_t *ids, uint8_t n)
{
	if (rip_inbox_count() != n) {
		return false;
	}
	for (uint8_t i = 0; i < n; i++) {
		struct rinbox_item it;

		if (!rip_inbox_get(i, &it) || it.uid != ids[i]) {
			return false;
		}
	}
	return true;
}

/* a digest of the whole store: every field of every entry */
static uint64_t store_digest(void)
{
	uint64_t h = 1469598103934665603ULL;
	uint8_t cnt = rip_inbox_count();

#define MIX(p, n)                                                                                  \
	do {                                                                                       \
		const uint8_t *q_ = (const uint8_t *)(p);                                          \
		for (size_t i_ = 0; i_ < (n); i_++) {                                              \
			h = (h ^ q_[i_]) * 1099511628211ULL;                                       \
		}                                                                                  \
	} while (0)
	for (uint8_t i = 0; i < cnt; i++) {
		struct rinbox_item it;

		if (rip_inbox_get(i, &it)) {
			MIX(&it.uid, sizeof(it.uid));
			MIX(&it.category, 1);
			MIX(&it.flags, 1);
			MIX(&it.read, 1);
			MIX(it.app, strlen(it.app) + 1);
			MIX(it.title, strlen(it.title) + 1);
			MIX(it.msg, strlen(it.msg) + 1);
			MIX(it.date, strlen(it.date) + 1);
		}
	}
	MIX(&cnt, 1);
#undef MIX
	return h;
}

static struct rrl_stats rst(void)
{
	struct rrl_stats s;

	rrl_stats_get(&s);
	return s;
}

static struct rip_stats ist(void)
{
	struct rip_stats s;

	rip_stats_get(&s);
	return s;
}

/* ---- conditions for wait_arg() ---- */
static bool c_passkey(intptr_t a)
{
	ARG_UNUSED(a);
	return passkey_calls > 0;
}

static bool c_paired_active(intptr_t a)
{
	ARG_UNUSED(a);
	return rdev_active() == 0 && rdev_link_up();
}

static bool c_ancs_ready(intptr_t a)
{
	ARG_UNUSED(a);
	return rip_ancs_ready();
}

static bool c_hello(intptr_t n)
{
	return rst().hellos >= (uint32_t)n;
}

static bool c_count(intptr_t n)
{
	return rip_inbox_count() == (uint8_t)n;
}

static bool c_gone(intptr_t uid)
{
	return find_uid((uint32_t)uid) < 0;
}

static bool c_relay_actions(intptr_t n)
{
	return ist().relay_actions >= (uint32_t)n;
}

static bool c_link_ends(intptr_t n)
{
	return rst().link_ends >= (uint32_t)n;
}

static bool c_sessions(intptr_t n)
{
	return ist().sessions >= (uint32_t)n;
}

static bool c_sc(intptr_t n)
{
	return ist().sc_indications >= (uint32_t)n;
}

static bool c_one_with_text(intptr_t a)
{
	struct rinbox_item it;

	ARG_UNUSED(a);
	return rip_inbox_count() == 1 && rip_inbox_get(0, &it) && it.text_ready;
}

static bool c_replaced(intptr_t a)
{
	ARG_UNUSED(a);
	return item_is(2, 1002, 3, 0x18, "com.example.chat", "Reply", "Second text", "20261112T110000");
}

/* the texts of the test notifications (UTF-8 written out in bytes) */
#define EUR4 "\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC"
#define EUR16 EUR4 EUR4 EUR4 EUR4
#define EAC8 "\xC3\xA9\xC3\xA9\xC3\xA9\xC3\xA9\xC3\xA9\xC3\xA9\xC3\xA9\xC3\xA9"
#define EAC80 EAC8 EAC8 EAC8 EAC8 EAC8 EAC8 EAC8 EAC8 EAC8 EAC8
#define A10 "aaaaaaaaaa"
#define A47 A10 A10 A10 A10 "aaaaaaa"
#define T10 "TTTTTTTTTT"
#define T48 T10 T10 T10 T10 "TTTTTTTT"
#define M10 "MMMMMMMMMM"
#define M160 M10 M10 M10 M10 M10 M10 M10 M10 M10 M10 M10 M10 M10 M10 M10 M10
#define AA10 "AAAAAAAAAA"
#define A48 AA10 AA10 AA10 AA10 "AAAAAAAA"

static bool c_rebuilt(intptr_t a)
{
	ARG_UNUSED(a);
	return rip_inbox_count() == 8 &&
	       item_is(0, 0x000100a5, 4, 0x12, "com.example.chat", "Anna", "Lunch at 12? \xF0\x9F\x8D\x9C", "20261112T191500") &&
	       item_is(1, 3007, 11, 0x00, "", "", "", "") && item_is(2, 3006, 8, 0x14, A48, T48, M160, "20") &&
	       item_is(3, 3005, 5, 0x04, "app.five", A47, "", "");
}

/* the pairing, the way the wearer does it: menu, Pair device, the passkey on the screen */
static void pair_through_the_screens(const char *p)
{
	char n[160];

	k_sleep(K_MSEC(1000));
	press(RC_SW_DOWN);
	snprintk(n, sizeof(n), "%s: the first joystick event turns the screen on: SCR_STATUS", p);
	CHECK(n, screen() == SCR_STATUS);
	press(RC_SW_RIGHT);
	snprintk(n, sizeof(n), "%s: Right opens the menu", p);
	CHECK(n, screen() == SCR_MENU);
	press(RC_SW_DOWN);
	press(RC_SW_DOWN);
	press(RC_SW_DOWN);
	press(RC_SW_RIGHT);
	snprintk(n, sizeof(n), "%s: Pair device opens SCR_PAIR and the pairing window", p);
	CHECK(n, screen() == SCR_PAIR && rdev_pair_window_open());
	snprintk(n, sizeof(n), "%s: the passkey arrives from the pairing", p);
	CHECK(n, wait_arg(c_passkey, 0, 40000));
	snprintk(n, sizeof(n), "%s: the stand-in paired and is the active device (slot 0)", p);
	CHECK(n, wait_arg(c_paired_active, 0, 40000));
	k_sleep(K_MSEC(500));
	snprintk(n, sizeof(n), "%s: after the pairing the screen shows SCR_DEVICES", p);
	CHECK(n, screen() == SCR_DEVICES);
	press(RC_SW_LEFT);
	press(RC_SW_LEFT);
	snprintk(n, sizeof(n), "%s: back on the status screen", p);
	CHECK(n, screen() == SCR_STATUS);
}

/* ------------------------------------------------------------------ scenario H */

static void run_h(void)
{
	struct rrl_stats r0, r1, rl;
	struct rip_stats i0;
	uint64_t h_empty, h_list, h_detail, d0;
	uint32_t link_ends0;
	struct rmd_stats ms;
	static const uint32_t ids_a[] = { 1004, 1003, 1002, 1001 };
	static const uint32_t ids_b[] = { 1004, 1003, 1001 };
	static const uint32_t ids_c[] = { 1005, 1004, 1003 };
	static const uint32_t ids_d[] = { 2003, 2002, 2001 };

	pair_through_the_screens("H");
	CHECK("H: before the link was secure no frame of the stand-in reached the relay part (it tried to write, read and subscribe)",
	      stats_at_passkey.writes == 0 && stats_at_passkey.sec_refused == 0 && stats_at_passkey.hellos == 0);
	CHECK("H: the iPhone part did not take the helper for an iPhone: no notification service found", !rip_ancs_ready() &&
	      ist().ancs_up == 0);
	press(RC_SW_UP);
	CHECK("H: Up opens the notification list (empty)", screen() == SCR_NOTIFS && rip_inbox_count() == 0);
	h_empty = frame_hash();
	stage(5);

	/* B: HELLO */
	CHECK("H: HELLO was accepted (READY went out)", wait_awake(c_hello, 1, 40000));
	r1 = rst();
	CHECK("H: before HELLO three frames were refused with code 2 and one HELLO with code 6, and the store stayed empty",
	      r1.by_code[2] == 3 && r1.by_code[6] == 1 && r1.refused == 4 && rip_inbox_count() == 0 && ist().relay_opens == 1);

	/* C: four notifications in pieces of 11 bytes (20-byte frames at the smallest ATT payload) */
	CHECK("H: four notifications arrive", wait_awake(c_count, 4, 60000));
	k_sleep(K_MSEC(300));
	r1 = rst();
	CHECK("H: 4 records stored in 40 pieces (11 data bytes per 20-byte frame; 6, 28, 5 and 5 frames)",
	      r1.puts == 4 && r1.pieces == 40 && r1.refused == 4 && r1.by_code[2] == 3);
	CHECK("H: the store holds the 4 notifications exactly, newest first: 1004 (flags silent), 1003, 1002 (title cut to 16 characters of "
	      "3 bytes, message cut to 80 of 2 bytes), 1001",
	      ids_are(ids_a, 4) && item_is(0, 1004, 0, 0x01, "com.example.news", "Headline", "", "20261112T104500") &&
		      item_is(1, 1003, 1, 0x0C, "com.example.cal", "Meeting", "At noon", "20261112T103000") &&
		      item_is(2, 1002, 2, 0x18, "com.example.chat", EUR16, EAC80, "20261112T102000") &&
		      item_is(3, 1001, 4, 0x18, "com.example.mail", "Hello", "First message", "20261112T101500") && no_item_read());
	CHECK("H: the iPhone part counts 4 relay puts and no iPhone event", ist().relay_puts == 4 && ist().ns_added == 0);

	/* D: the screens show them */
	k_sleep(K_MSEC(500));
	CHECK("H: the list screen follows the store (still SCR_NOTIFS)", screen() == SCR_NOTIFS);
	h_list = frame_hash();
	CHECK("H: the list with the notifications is another frame than the empty list", h_list != h_empty);
	press(RC_SW_DOWN);
	press(RC_SW_DOWN);
	press(RC_SW_RIGHT);
	CHECK("H: Right opens the detail of the third entry (1002)", screen() == SCR_NOTIF);
	h_detail = frame_hash();
	CHECK("H: the detail frame differs from the list frame", h_detail != h_list);
	CHECK("H: opening it set its read mark on the ring (and no other)", item_read(2) && !item_read(0) && !item_read(1) && !item_read(3));
	press(RC_SW_CENTRE);
	CHECK("H: Centre goes back to the list", screen() == SCR_NOTIFS);
	stage(10);

	/* E: a PUT for a held id replaces it and keeps place and read mark */
	CHECK("H: the replace of 1002 arrives (new category, flags and text)", wait_awake(c_replaced, 0, 60000));
	CHECK("H: the replace kept the place (third) and the read mark, and added no entry",
	      ids_are(ids_a, 4) && item_read(2) && !item_read(0) && !item_read(1) && !item_read(3) &&
		      item_is(3, 1001, 4, 0x18, "com.example.mail", "Hello", "First message", "20261112T101500"));
	stage(20);

	/* F: an action the notification does not have sends nothing (to the first entry: Up three times, it stops at the first) */
	press(RC_SW_UP);
	press(RC_SW_UP);
	press(RC_SW_UP);
	press(RC_SW_RIGHT);
	CHECK("H: the detail of 1004 (it has no action) opens", screen() == SCR_NOTIF);
	press(RC_SW_LEFT);   /* dismiss: it has no negative action */
	press(RC_SW_RIGHT);  /* positive: it has no positive action */
	CHECK("H: the screen did not call the iPhone part for either (no action flag)", ist().actions_refused == 0 && ist().relay_actions == 0);
	CHECK("H: a dismiss and a positive action for 1004 called directly are refused on the ring (-ENOTSUP) and send nothing",
	      rip_dismiss(1004) == -ENOTSUP && rip_action(1004, RIP_ACTION_POSITIVE) == -ENOTSUP && ist().relay_actions == 0 &&
		      rst().actions_sent == 0 && ist().actions_refused == 2);
	stage(30);
	WAIT("H: wait for the stand-in's stage 31 (the stand-in confirmed it received nothing)", wait_helper(31, 30000));
	press(RC_SW_CENTRE);
	press(RC_SW_UP);
	press(RC_SW_UP);
	press(RC_SW_DOWN);
	press(RC_SW_RIGHT);
	CHECK("H: the detail of 1003 (positive action only) opens", screen() == SCR_NOTIF);
	press(RC_SW_LEFT);   /* dismiss: 1003 has no negative action */
	CHECK("H: a dismiss on 1003 (it has no negative action) sends nothing", rst().actions_sent == 0 && ist().relay_actions == 0);
	stage(40);
	WAIT("H: wait for the stand-in's stage 41 (the stand-in confirmed it received nothing for the dismiss on 1003)", wait_helper(41, 30000));

	/* the positive action */
	press(RC_SW_RIGHT);
	CHECK("H: the positive action on 1003 went out through the relay part once", wait_arg(c_relay_actions, 1, 5000) &&
	      ist().relay_actions == 1 && rst().actions_sent == 1);
	stage(50);
	WAIT("H: wait for the stand-in's stage 51 (the stand-in received ACTION positive for 1003)", wait_helper(51, 30000));
	CHECK("H: the positive action changed nothing in the store", ids_are(ids_a, 4) && item_is(1, 1003, 1, 0x0C, "com.example.cal", "Meeting",
	      "At noon", "20261112T103000"));

	/* the dismiss: ACTION negative, the entry stays until the helper sends REMOVE */
	press(RC_SW_CENTRE);
	press(RC_SW_UP);
	press(RC_SW_UP);
	press(RC_SW_DOWN);
	press(RC_SW_DOWN);
	press(RC_SW_RIGHT);
	CHECK("H: the detail of 1002 opens", screen() == SCR_NOTIF);
	press(RC_SW_LEFT);
	CHECK("H: the dismiss went out through the relay part (2 actions in all)", wait_arg(c_relay_actions, 2, 5000) &&
	      ist().relay_actions == 2 && rst().actions_sent == 2);
	stage(60);
	WAIT("H: wait for the stand-in's stage 61 (the stand-in received ACTION negative for 1002)", wait_helper(61, 30000));
	k_sleep(K_MSEC(1000));
	CHECK("H: the ring changed nothing: 1002 is still in the store until REMOVE", ids_are(ids_a, 4) && screen() == SCR_NOTIF);
	stage(62);
	CHECK("H: REMOVE arrived: 1002 left the store", wait_arg(c_gone, 1002, 30000));
	k_sleep(K_MSEC(500));
	CHECK("H: the screens went back to the list and the store holds 1004, 1003, 1001", screen() == SCR_NOTIFS && ids_are(ids_b, 3));
	stage(70);

	/* G: no subscription to Out: the action is refused on the ring */
	WAIT("H: wait for the stand-in's stage 71 (the stand-in switched Out notifications off)", wait_helper(71, 30000));
	i0 = ist();
	CHECK("H: with no subscription to Out an action is refused on the ring (-ENOTCONN) and sends nothing",
	      rip_action(1001, RIP_ACTION_NEGATIVE) == -ENOTCONN && ist().relay_actions == i0.relay_actions && rst().actions_sent == 2 &&
		      rst().actions_refused == 1 && ids_are(ids_b, 3));
	CHECK("H: the frame refused while Out was off was dropped on Out (not notified) and counted once", rst().out_dropped == 1);
	stage(80);
	WAIT("H: wait for the stand-in's stage 81 (the stand-in confirmed it received nothing, and subscribed again)", wait_helper(81, 30000));

	/* H: RECORDING (the screen may have turned off: the first event only turns it on, then the long press is made) */
	if (screen() == SCR_OFF) {
		press(RC_SW_DOWN);
	}
	hold(RC_SW_CENTRE, 1200);
	CHECK("H: a long press starts a recording", rglue_state() == RC_ST_RECORDING && rec_starts == 1 && rec_stops == 0);
	r0 = rst();
	i0 = ist();
	stage(90);
	WAIT("H: wait for the stand-in's stage 91 (the stand-in sent its frames during RECORDING)", wait_helper(91, 60000));
	k_sleep(K_MSEC(1500));
	r1 = rst();
	CHECK("H: during RECORDING the relay frames were handled as usual (1 PUT stored, 1 REMOVE, a malformed PUT refused with code 5 and an "
	      "unknown opcode with code 1)",
	      r1.puts - r0.puts == 1 && r1.removes - r0.removes == 1 && r1.refused - r0.refused == 2 && r1.by_code[5] - r0.by_code[5] == 1 &&
		      r1.by_code[1] - r0.by_code[1] == 1 && ids_are(ids_c, 3) &&
		      item_is(0, 1005, 7, 0x10, "com.example.rec", "During recording", "", ""));
	CHECK("H: the core is still RECORDING, no recording started or stopped by the relay frames",
	      rglue_state() == RC_ST_RECORDING && rec_starts == 1 && rec_stops == 0);
	hold(RC_SW_CENTRE, 1200);
	CHECK("H: a long press stops the recording", rglue_state() == RC_ST_STANDBY && rec_starts == 1 && rec_stops == 1);
	stage(110);

	/* I: malformed frames refuse with their codes and leave the store unchanged */
	WAIT("H: wait for the stand-in's stage 111 (the stand-in sent HELLO and three notifications)", wait_helper(111, 60000));
	CHECK("H: the store holds 2003, 2002, 2001 (HELLO emptied what was there)", wait_arg(c_count, 3, 5000) && ids_are(ids_d, 3) &&
	      item_is(0, 2003, 3, 0x08, "app.c", "Third", "", "") && item_is(2, 2001, 1, 0x00, "app.a", "First", "", ""));
	d0 = store_digest();
	r0 = rst();
	i0 = ist();
	stage(120);
	WAIT("H: wait for the stand-in's stage 121 (the stand-in sent 21 malformed frames and got each refusal)", wait_helper(121, 90000));
	r1 = rst();
	CHECK("H: 21 frames were refused: 7 with code 1, 3 with code 3, 3 with code 4, 6 with code 5, 2 with code 6, none with code 2 or 7",
	      r1.refused - r0.refused == 21 && r1.by_code[1] - r0.by_code[1] == 7 && r1.by_code[2] - r0.by_code[2] == 0 &&
		      r1.by_code[3] - r0.by_code[3] == 3 && r1.by_code[4] - r0.by_code[4] == 3 && r1.by_code[5] - r0.by_code[5] == 6 &&
		      r1.by_code[6] - r0.by_code[6] == 2 && r1.by_code[7] - r0.by_code[7] == 0);
	CHECK("H: the malformed frames changed nothing: no put, remove, clear or HELLO accepted, the store digest is the same",
	      r1.puts == r0.puts && r1.removes == r0.removes && r1.clears == r0.clears && r1.hellos == r0.hellos &&
		      ist().relay_puts == i0.relay_puts && ist().relay_removes == i0.relay_removes && store_digest() == d0 && ids_are(ids_d, 3));
	CHECK("H: the one accepted first piece of the out of order test is counted as a piece", r1.pieces - r0.pieces == 1);
	stage(130);

	/* J: CLEAR and a PUT with the screen off, then an unfinished PUT, then the link drops */
	for (int w = 0; w < 100 && screen() != SCR_OFF; w++) {
		k_sleep(K_MSEC(100));
	}
	CHECK("H: the screen is off (5 s after the last input)", screen() == SCR_OFF);
	stage(130);
	WAIT("H: wait for the stand-in's stage 131 (the stand-in sent CLEAR)", wait_helper(131, 60000));
	CHECK("H: CLEAR emptied the store (one CLEAR accepted in all)", rip_inbox_count() == 0 && rst().clears == 1 && ist().relay_clears == 1);
	stage(132);
	WAIT("H: wait for the stand-in's stage 133 (the stand-in sent PUT 2004)", wait_helper(133, 60000));
	CHECK("H: the store holds 2004 only", wait_arg(c_count, 1, 5000) && item_is(0, 2004, 1, 0x00, "app.d", "Fourth", "", ""));
	rmd_stats_get(&ms);
	CHECK("H: relay frames (CLEAR, PUT) did not wake the screen: it is still off and the panel is blanked", screen() == SCR_OFF && ms.blanked);
	d0 = store_digest();
	r0 = rst();
	stage(134);
	WAIT("H: wait for the stand-in's stage 135 (the stand-in sent two pieces of a record and no more)", wait_helper(135, 60000));
	r1 = rst();
	CHECK("H: two more pieces were taken, nothing was stored", r1.pieces - r0.pieces == 2 && r1.puts == r0.puts && store_digest() == d0);
	link_ends0 = r1.link_ends;
	stage(140);
	CHECK("H: the link dropped", wait_arg(c_link_ends, link_ends0 + 1, 60000));
	CHECK("H: the link dropped: the store is empty", rip_inbox_count() == 0);
	rl = rst();
	CHECK("H: the relay session ended with the link", rl.link_ends == link_ends0 + 1);

	/* K: the reconnect: a new HELLO, the store is rebuilt */
	WAIT("H: wait for the stand-in's stage 136 (the stand-in sent its 7 notifications after the reconnect)", wait_helper(136, 90000));
	CHECK("H: after the reconnect and a new HELLO the 7 notifications are in the store (the example is not there yet)",
	      rip_inbox_count() == 7 && find_uid(0x000100a5) < 0 && item_is(0, 3007, 11, 0x00, "", "", "", "") &&
		      item_is(6, 1001, 4, 0x1C, "com.example.mail", "Hello", "First message", "20261112T101500"));
	stage(141);
	WAIT("H: wait for the stand-in's stage 137 (the stand-in sent the example's six 20-byte frames)", wait_helper(137, 60000));
	CHECK("H: the example's six frames stored entry 0x000100a5 field by field: category 4, flags 0x12, com.example.chat, Anna, the 17-byte message with the noodle bowl, 20261112T191500, in front",
	      rip_inbox_count() == 8 &&
		      item_is(0, 0x000100a5, 4, 0x12, "com.example.chat", "Anna", "Lunch at 12? \xF0\x9F\x8D\x9C", "20261112T191500"));
	stage(142);
	WAIT("H: wait for the stand-in's stage 138 (the stand-in sent the example's REMOVE)", wait_helper(138, 60000));
	CHECK("H: the example's REMOVE took the entry out: 0x000100a5 is gone and the count fell from 8 to 7", rip_inbox_count() == 7 &&
	      find_uid(0x000100a5) < 0 && item_is(0, 3007, 11, 0x00, "", "", "", ""));
	stage(143);
	WAIT("H: wait for the stand-in's stage 139 (the stand-in sent the example's 71-byte frame)", wait_helper(139, 60000));
	CHECK("H: all 8 entries are in the store again", wait_arg(c_count, 8, 10000));
	k_sleep(K_MSEC(300));
	r1 = rst();
	CHECK("H: the store was rebuilt exactly: 3007 (record of 2 bytes), 3006 (record of 512 bytes, texts cut), 3005 (title cut at 47 bytes "
	      "before a 3-byte character), 1004, 1003, 1002, 1001 (flags with the pre-existing bit)",
	      c_rebuilt(0) && item_is(4, 1004, 0, 0x05, "com.example.news", "Headline", "", "20261112T104500") &&
		      item_is(5, 1003, 1, 0x0C, "com.example.cal", "Meeting", "At noon", "20261112T103000") &&
		      item_is(6, 1002, 2, 0x1C, "com.example.chat", EUR16, EAC80, "20261112T102000") &&
		      item_is(7, 1001, 4, 0x1C, "com.example.mail", "Hello", "First message", "20261112T101500") && no_item_read());
	CHECK("H: after the reconnect, before HELLO: two frames refused with code 2; after HELLO the dropped record's next piece with code 3",
	      r1.by_code[2] - rl.by_code[2] == 2 && r1.by_code[3] - rl.by_code[3] == 1 && r1.refused - rl.refused == 3 &&
		      r1.hellos - rl.hellos == 1 && r1.puts - rl.puts == 9 && r1.removes - rl.removes == 1);
	/* a dismiss chosen with the joystick for the example's notification (its flags 0x12 have the negative action): it must reach the stand-in as
	 * exactly 82 a5 00 01 00 01 */
	if (screen() == SCR_OFF) {
		press(RC_SW_DOWN);
	}
	press(RC_SW_UP);
	CHECK("H: Up opens the list with the example's notification first", screen() == SCR_NOTIFS && item_is(0, 0x000100a5, 4, 0x12, "com.example.chat", "Anna", "Lunch at 12? \xF0\x9F\x8D\x9C", "20261112T191500"));
	press(RC_SW_RIGHT);
	CHECK("H: Right opens the detail of the example's notification", screen() == SCR_NOTIF);
	press(RC_SW_LEFT);
	CHECK("H: the dismiss on the example's notification went out through the relay part (3 actions in all)", wait_arg(c_relay_actions, 3, 5000) &&
	      ist().relay_actions == 3);
	stage(145);
	WAIT("H: wait for the stand-in's stage 146 (it compared the ACTION bytes)", wait_helper(146, 60000));
	stage(150);
}

/* ------------------------------------------------------------------ scenario I */

static void run_i(void)
{
	struct rrl_stats r1;
	struct rip_stats i1;
	static const uint32_t ids_1[] = { 301 };

	pair_through_the_screens("I");
	CHECK("I: the notification service of the stand-in iPhone is found and subscribed", wait_arg(c_ancs_ready, 0, 40000));
	CHECK("I: the iPhone's notification arrives with its text", wait_arg(c_one_with_text, 0, 30000));
	CHECK("I: the store holds the iPhone's notification 301",
	      ids_are(ids_1, 1) && item_is(0, 301, 1, 0x18, "com.example.phone", "Call", "Missed call", "20261112T111500") && !item_read(0));
	stage(10);
	WAIT("I: wait for the stand-in's stage 11 (the stand-in wrote 5 relay frames and got 5 refusals)", wait_helper(11, 60000));
	r1 = rst();
	i1 = ist();
	CHECK("I: every relay frame was refused with code 7 (5 in all) and none was accepted",
	      r1.by_code[7] == 5 && r1.refused == 5 && r1.hellos == 0 && r1.puts == 0 && r1.removes == 0 && r1.clears == 0);
	CHECK("I: the iPhone part took no relay session, entry or removal", i1.relay_opens == 0 && i1.relay_puts == 0 && i1.relay_removes == 0 &&
	      i1.relay_clears == 0);
	CHECK("I: the iPhone's notifications are untouched: 301 with its text, unread",
	      ids_are(ids_1, 1) && item_is(0, 301, 1, 0x18, "com.example.phone", "Call", "Missed call", "20261112T111500") && !item_read(0));
	/* a dismiss chosen on the ring goes to Apple's service, the source of the entry */
	press(RC_SW_UP);
	CHECK("I: Up opens the list with the iPhone's notification", screen() == SCR_NOTIFS && rip_inbox_count() == 1);
	press(RC_SW_RIGHT);
	CHECK("I: Right opens the detail", screen() == SCR_NOTIF);
	press(RC_SW_LEFT);
	i1 = ist();
	r1 = rst();
	CHECK("I: the dismiss went to Apple's service (actions_sent 1) and not to the relay (no ACTION, no relay action)",
	      i1.actions_sent == 1 && i1.relay_actions == 0 && r1.actions_sent == 0);
	CHECK("I: the stand-in iPhone removed it: the store is empty", wait_arg(c_count, 0, 20000));
	stage(20);
}

/* ------------------------------------------------------------------ scenario B */

/* One source per link, the other way round: the stand-in has Apple's notification service too, but its relay HELLO comes first. The link's
 * source is the relay from then on: the ring finds the service, does not subscribe to it, and keeps the relay's notification. */
static void run_b(void)
{
	struct rip_stats i1;
	static const uint32_t ids_1[] = { 401 };
	static const uint32_t ids_2[] = { 402, 401 };

	/* test hook: the iPhone part's session start waits, so the relay HELLO and its entries come before it (rip.c, the guard of ready_fn) */
	rip_test_hold_session_start(true);
	pair_through_the_screens("B");
	CHECK("B: HELLO was accepted", wait_arg(c_hello, 1, 40000));
	CHECK("B: the relay's notification 401 is in the store: the PUT was accepted before the subscription to Out", wait_arg(c_count, 1, 40000));
	CHECK("B: the iPhone part's session has not started yet (held by the test hook)", ist().sessions == 0);
	rip_test_hold_session_start(false);
	WAIT("B: wait for the iPhone part's session start", wait_arg(c_sessions, 1, 10000));
	k_sleep(K_MSEC(300));
	CHECK("B: the session start after a relay HELLO kept the entries: the session started and 401 is still in the store",
	      ist().sessions == 1 && ids_are(ids_1, 1) && item_is(0, 401, 1, 0x18, "com.example.chat2", "Both", "HELLO came first", ""));
	CHECK("B: with no subscription READY was dropped on Out and counted (1 frame dropped), and no frame was refused with code 2",
	      rst().out_dropped == 1 && rst().by_code[2] == 0 && rst().out_sent == 0);
	k_sleep(K_MSEC(8000)); /* the iPhone part has looked for the services by now */
	i1 = ist();
	CHECK("B: Apple's notification service was found on the relay's link and was not used (relay_blocked 1, not subscribed)",
	      i1.relay_blocked == 1 && i1.ancs_up == 0 && !rip_ancs_ready() && i1.ns_added == 0);
	CHECK("B: the relay's notification is still the only entry, exactly as sent",
	      ids_are(ids_1, 1) && item_is(0, 401, 1, 0x18, "com.example.chat2", "Both", "HELLO came first", ""));
	stage(10);
	WAIT("B: wait for the stand-in's stage 11 (it sent PUT 402)", wait_helper(11, 60000));
	CHECK("B: a relay frame is still accepted after Apple's service was found, and the Apple notification 999 offered by the stand-in did not reach the store",
	      ids_are(ids_2, 2) && item_is(0, 402, 1, 0x18, "com.example.chat2", "Second", "after Apple's service was found", "") &&
		      find_uid(999) < 0 &&
		      rst().by_code[7] == 0 && ist().ns_added == 0 && ist().ancs_up == 0);
	stage(12);
	WAIT("B: wait for the stand-in's stage 13 (it removed its notification service)", wait_helper(13, 60000));
	CHECK("B: Service Changed was indicated", wait_arg(c_sc, 1, 30000));
	k_sleep(K_MSEC(3000)); /* the iPhone part stops the services and looks for them again */
	CHECK("B: Service Changed was indicated and the ring still holds the relay's entries (402 and 401)",
	      ist().sc_indications >= 1 && ids_are(ids_2, 2) && item_is(1, 401, 1, 0x18, "com.example.chat2", "Both", "HELLO came first", ""));
	CHECK("B: a dismiss goes to the helper (the source of the entry), not to Apple's service",
	      rip_dismiss(401) == 0 && ist().relay_actions == 1 && ist().actions_sent == 0);
	stage(20);
	k_sleep(K_MSEC(1000));
}

/* ------------------------------------------------------------------ scenario Q */

/* A full Out queue and an accepted HELLO (test hook: Out is blocked as when the controller has no buffer for a notification). */
static void run_q(void)
{
	struct rrl_stats r1;
	struct rip_stats i1;

	pair_through_the_screens("Q");
	CHECK("Q: HELLO was accepted", wait_arg(c_hello, 1, 40000));
	WAIT("Q: wait for the stand-in's stage 1 (it sent PUT 5001)", wait_helper(1, 60000));
	CHECK("Q: the store holds 5001", wait_arg(c_count, 1, 5000));
	rrl_test_block_out(true);
	stage(2);
	WAIT("Q: wait for the stand-in's stage 3 (it sent 12 unknown opcodes)", wait_helper(3, 60000));
	r1 = rst();
	CHECK("Q: 12 frames were refused with code 1; the Out queue holds 8 and 4 were dropped; nothing was sent while Out was blocked (only READY before)",
	      r1.by_code[1] == 12 && r1.out_dropped == 4 && r1.out_sent == 1);
	CHECK("Q: with the Out queue full an action is refused on the ring (-EBUSY) and is not counted as sent",
	      rip_dismiss(5001) == -EBUSY && ist().relay_actions == 0 && rst().actions_sent == 0 && rst().actions_refused == 1);
	CHECK("Q: the refused action is counted once, in actions_refused (1), and not as a dropped Out frame (out_dropped stays 4)",
	      rst().actions_refused == 1 && rst().out_dropped == 4);
	i1 = ist();
	CHECK("Q: the refused action changed nothing in the store", rip_inbox_count() == 1 && i1.relay_removes == 0);
	stage(4);
	WAIT("Q: wait for the stand-in's stage 5 (it sent the second HELLO)", wait_helper(5, 60000));
	CHECK("Q: the second HELLO was accepted although the queue was full", wait_arg(c_hello, 2, 5000) && rip_inbox_count() == 0);
	rrl_test_block_out(false);
	stage(6);
	WAIT("Q: wait for the stand-in's stage 7 (it saw READY first and no old frame)", wait_helper(7, 60000));
	r1 = rst();
	CHECK("Q: only the two READY frames were sent in all", r1.out_sent == 2);
	stage(8);
	k_sleep(K_MSEC(1000));
}

int main(void)
{
	char *scen = nsi_host_getenv("RING_SCENARIO");
	int err;

	printk("RING START scenario %s\n", scen != NULL ? scen : "(none)");
	k_work_init_delayable(&fault_release, fault_release_fn);
	err = rctl_init();
	CHECK("HID service registered", err == 0);
	err = rdev_init(&cbs);
	CHECK("Bluetooth up, devices ready", err == 0);
	err = rscr_start(&rscr_real_ops);
	CHECK("screens started (LVGL on the memory display)", err == 0);
	rglue_init(&glue_ops, RC_ST_STANDBY);
	if (err != 0 || scen == NULL) {
		printk("RING RESULT FAIL\n");
		return 0;
	}
	if (strcmp(scen, "H") == 0) {
		run_h();
	} else if (strcmp(scen, "I") == 0) {
		run_i();
	} else if (strcmp(scen, "B") == 0) {
		run_b();
	} else if (strcmp(scen, "Q") == 0) {
		run_q();
	} else {
		CHECK("known scenario", false);
	}
	printk("RING SCRIPT DONE t=%lld checks=%d fails=%d\n", k_uptime_get(), checks, fails);
	printk("RING RESULT %s\n", fails == 0 ? "PASS" : "FAIL");
	while (1) {
		k_sleep(K_SECONDS(1));
	}
	return 0;
}
