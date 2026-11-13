/*
 * Ring side of the iPhone test (BabbleSim, the simulated ring chip nrf54lm20bsim, real encryption: see run.sh).
 *
 * The real ring_devices, ring_control, ring_glue (which starts the iPhone part, ring_iphone), ring_inbox,
 * ring_time and ring_core modules run here. The stand-in iPhone (host_app) pairs with the ring and serves Apple's
 * three services; it is driven by its own script. The scenario (RING_SCENARIO) is the script of this ring:
 *   N  notifications, change, removal, the 17th, actions, media, time, events during RECORDING and STANDBY
 *   R  a dropped link and a reconnect; the Notification Center Service removed and added again (Service Changed)
 *   P  a host without Apple's services (the step 2 kind): no error, keys work, the inbox stays empty
 * Every expected value below is a literal written in this file (not read from the stand-in or from the modules).
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
#include <ring_time/rtime.h>
#include "hosttools.h"

static int fails;
static int checks;
static int passkey_shown;
static int rec_starts;
static int rec_stops;
static int link_down_events;
static int link_up_events;

#define CHECK(name, cond)                                                                          \
	do {                                                                                       \
		bool ok_ = (cond);                                                                 \
		checks++;                                                                          \
		fails += ok_ ? 0 : 1;                                                              \
		printk("RING CHECK %s %s (t=%lld)\n", name, ok_ ? "PASS" : "FAIL", k_uptime_get()); \
	} while (0)

#define CHECKF(cond, ...)                                                                          \
	do {                                                                                       \
		char nm_[128];                                                                     \
		snprintk(nm_, sizeof(nm_), __VA_ARGS__);                                           \
		CHECK(nm_, cond);                                                                  \
	} while (0)

static uint32_t reports(void)
{
	struct rctl_stats st;

	rctl_stats_get(&st);
	return st.reports;
}

/* ---- the passkey goes to a file the stand-in reads (the screens part is not built yet) ---- */

static void on_passkey_show(uint8_t slot, uint32_t passkey)
{
	char buf[16];
	char *path = nsi_host_getenv("RING_PASSFILE");
	int n = snprintk(buf, sizeof(buf), "%06u\n", passkey);

	passkey_shown++;
	printk("RING PASSKEY slot %u %06u\n", slot, passkey);
	if (path != NULL) {
		int fd = nsi_host_open(path, HT_O_WRONLY | HT_O_TRUNC);

		if (fd >= 0) {
			(void)nsi_host_write(fd, buf, (unsigned long)n);
			(void)nsi_host_close(fd);
		}
	}
}

static void on_link(uint8_t slot, bool up)
{
	link_down_events += up ? 0 : 1;
	link_up_events += up ? 1 : 0;
	printk("RING EVENT link slot %u %s\n", slot, up ? "up" : "down");
}

static const struct rdev_callbacks cbs = {
	.passkey_show = on_passkey_show,
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
};

static void inject(enum rc_switch sw, int hold_ms)
{
	rglue_input(sw, true);
	k_sleep(K_MSEC(hold_ms));
	rglue_input(sw, false);
	k_sleep(K_MSEC(600));
}

/* A fault hook for the broken copy "core_touch": a broken ring_iphone calls this when the iPhone's time arrives, so
 * the time change reaches the joystick path (a centre hold) - only while a recording runs. */
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

static void sleep_until(int64_t t_ms)
{
	if (k_uptime_get() < t_ms) {
		k_sleep(K_MSEC(t_ms - k_uptime_get()));
	}
}

static bool wait_ready(uint8_t slot, int64_t timeout_ms)
{
	int64_t end = k_uptime_get() + timeout_ms;

	while (k_uptime_get() < end) {
		if (rdev_active() == slot && rctl_ready()) {
			k_sleep(K_MSEC(3000));
			return rdev_active() == slot && rctl_ready();
		}
		k_sleep(K_MSEC(100));
	}
	return false;
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

/* ---- reading the inbox ---- */

static bool item_at(uint8_t i, struct rinbox_item *it)
{
	return rip_inbox_get(i, it);
}

static int index_of(uint32_t uid)
{
	struct rinbox_item it;

	for (uint8_t i = 0; item_at(i, &it); i++) {
		if (it.uid == uid) {
			return i;
		}
	}
	return -1;
}

static bool has_text(uint32_t uid)
{
	struct rinbox_item it;
	int i = index_of(uid);

	return i >= 0 && item_at((uint8_t)i, &it) && it.text_ready;
}

static bool ancs_ready(void)
{
	return rip_ancs_ready();
}

static bool ancs_not_ready(void)
{
	return !rip_ancs_ready();
}

static bool ams_cts_ready(void)
{
	return rip_ams_ready() && rip_cts_ready();
}

static bool all_text_ready(void)
{
	struct rinbox_item it;

	for (uint8_t i = 0; item_at(i, &it); i++) {
		if (!it.text_ready) {
			return false;
		}
	}
	return true;
}

/* one entry: every field must be exactly this */
static bool entry_is(int index, uint32_t uid, uint8_t cat, uint8_t flags, const char *app, const char *title,
		     const char *msg, const char *date)
{
	struct rinbox_item it;

	if (!item_at((uint8_t)index, &it)) {
		return false;
	}
	if (it.uid != uid || it.category != cat || it.flags != flags || !it.text_ready || strcmp(it.app, app) != 0 ||
	    strcmp(it.title, title) != 0 || strcmp(it.msg, msg) != 0 || strcmp(it.date, date) != 0) {
		size_t ml = strlen(it.msg);

		/* the message is printed as a length and its last bytes in hex: a raw cut character in the log would
		 * make the line unreadable */
		printk("RING INFO entry %d differs: uid %u cat %u flags 0x%02x app '%s' title '%s' msg length %u, last bytes "
		       "%02x %02x %02x, date '%s'\n",
		       index, it.uid, it.category, it.flags, it.app, it.title, (unsigned int)ml,
		       ml > 2 ? (uint8_t)it.msg[ml - 3] : 0, ml > 1 ? (uint8_t)it.msg[ml - 2] : 0,
		       ml > 0 ? (uint8_t)it.msg[ml - 1] : 0, it.date);
		return false;
	}
	return true;
}

/* the message of 53 characters U+20AC: the stand-in has 66 of them and "xy" (200 bytes); 160 bytes cut on a
 * character boundary is 53 characters, 159 bytes */
#define EURO53 "\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC" \
	       "\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC" \
	       "\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC" \
	       "\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC" \
	       "\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC" \
	       "\xE2\x82\xAC\xE2\x82\xAC\xE2\x82\xAC"

static struct rip_stats stats(void)
{
	struct rip_stats s;

	rip_stats_get(&s);
	return s;
}

/* the iPhone's time (BASE + uptime, set in the stand-in) against the ring's clock */
#define BASE_MS 1794434746000LL
#define ZONE_MS 7200000LL /* scenario N: the iPhone's zone is +1 h and daylight saving +1 h: local time = UTC + 2 h */

/* the clock should show UTC = the iPhone's local time minus the zone (scenario N) */
static bool clock_is(int64_t offset_ms)
{
	int64_t want = BASE_MS - ZONE_MS + offset_ms + k_uptime_get();
	int64_t have = rtime_utc_ms();
	int64_t d = have - want;

	return rtime_is_set() && d > -100 && d < 100;
}

/* no zone given (scenarios R and others): the clock should show the iPhone's local time as it is */
static bool clock_is_local(int64_t offset_ms)
{
	int64_t want = BASE_MS + offset_ms + k_uptime_get();
	int64_t have = rtime_utc_ms();
	int64_t d = have - want;

	return rtime_is_set() && d > -100 && d < 100;
}

/* the clock should show UTC for an iPhone whose zone is zone_ms (scenarios Z): its local time is BASE + uptime + local_shift */
static int64_t zshift_ms; /* how far the iPhone's local time has been moved by time changes, in scenario Z */

static bool clock_is_zone(int64_t zone_ms, int64_t local_shift)
{
	int64_t want = BASE_MS + local_shift - zone_ms + k_uptime_get();
	int64_t d = rtime_utc_ms() - want;

	return rtime_is_set() && d > -100 && d < 100;
}

static bool clock_z1(void)
{
	return clock_is_zone(3600000LL, 0) && rtime_zone_known() && rtime_tz_min() == 60;
}

static bool clock_z2(void)
{
	return clock_is_zone(10800000LL, 7200000LL) && rtime_zone_known() && rtime_tz_min() == 180;
}

static bool clock_plus_2h(void)
{
	return clock_is(7200000LL);
}

/* strict UTF-8 check, written here independently of the inbox: every sequence is complete and well formed */
static bool utf8_ok(const char *s)
{
	const uint8_t *p = (const uint8_t *)s;

	while (*p != 0) {
		int n = (*p < 0x80) ? 0 : ((*p & 0xE0) == 0xC0) ? 1 : ((*p & 0xF0) == 0xE0) ? 2 : ((*p & 0xF8) == 0xF0) ? 3 : -1;

		if (n < 0) {
			return false;
		}
		p++;
		for (int k = 0; k < n; k++, p++) {
			if ((*p & 0xC0) != 0x80) {
				return false;
			}
		}
	}
	return true;
}

/* every entry: application identifier at most 48 bytes, title at most 48, message at most 160, all complete UTF-8 */
static bool all_entries_within_limits(void)
{
	struct rinbox_item it;
	int n = 0;

	for (uint8_t i = 0; item_at(i, &it); i++) {
		n++;
		if (strlen(it.app) > 48 || strlen(it.title) > 48 || strlen(it.msg) > 160 || !utf8_ok(it.app) ||
		    !utf8_ok(it.title) || !utf8_ok(it.msg)) {
			printk("RING INFO entry %u breaks a limit or ends inside a character\n", i);
			return false;
		}
	}
	return n > 0;
}

static bool pairing_and_services(void)
{
	return rip_ancs_ready() && rip_ams_ready() && rip_cts_ready();
}

/* ---- scenario N ---- */

static bool media_paired_first(void)
{
	struct ripl_media m;

	rip_media_get(&m);
	return m.state == RIPL_PLAYER_PAUSED && strcmp(m.title, "Bohemian Rhapsody") == 0 && strcmp(m.artist, "Queen") == 0;
}

static bool media_new_track_playing(void)
{
	struct ripl_media m;

	rip_media_get(&m);
	return m.state == RIPL_PLAYER_PLAYING && strcmp(m.title, "Under Pressure") == 0 &&
	       strcmp(m.artist, "Queen and David Bowie") == 0;
}

static bool media_paused_again(void)
{
	struct ripl_media m;

	rip_media_get(&m);
	return m.state == RIPL_PLAYER_PAUSED;
}

static bool count_is_5(void)
{
	return rip_inbox_count() == 5 && all_text_ready();
}

static bool change_arrived(void)
{
	struct rinbox_item it;
	int i = index_of(101);

	return i >= 0 && item_at((uint8_t)i, &it) && strcmp(it.msg, "Hello, are you there? Please answer.") == 0;
}

static bool count_is_4(void)
{
	return rip_inbox_count() == 4;
}

static bool count_is_16_full(void)
{
	return rip_inbox_count() == 16 && has_text(122);
}

static bool count_is_15(void)
{
	return rip_inbox_count() == 15;
}

static void run_n(void)
{
	struct rinbox_item it;
	struct ripl_media m;
	struct rip_stats s0, s1;
	uint32_t rep0, st_core;
	int r;
	int64_t t0;

	rctl_set_active(true);
	CHECK("pairing window opens", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	/* the script's zero is the moment the ring has subscribed to the Notification Source (the stand-in's zero is
	 * the moment it sees that subscription: a few hundred ms later) */
	CHECK("the iPhone pairs; the ring finds and subscribes to the notification service at security level 4",
	      wait_for(ancs_ready, 40000));
	t0 = k_uptime_get();
	CHECK("nothing in the inbox before the iPhone sends", rip_inbox_count() == 0);
	CHECK("the three services are found and subscribed", wait_for(pairing_and_services, 20000));
	CHECK("the link is ready for keys too", rdev_active() == 0 && wait_ready(0, 20000));

	/* media: the iPhone's first report (registered pairs are sent at once) */
	CHECK("the player state and track follow the iPhone's first report (paused, Bohemian Rhapsody, Queen)",
	      wait_for(media_paired_first, 8000));
	/* time (g): the ring's clock equals the iPhone's time after the link is ready */
	CHECK("the ring's clock equals the iPhone's time within 1 s, as UTC (the iPhone's zone +2 h taken off)", clock_is(0));
	CHECK("the zone is known and is +120 minutes", rtime_zone_known() && rtime_tz_min() == 120);
	CHECK("the clock was set from the iPhone (at least once)", rtime_updates() >= 1);

	/* (a) five notifications */
	CHECK("five notifications arrived with their text", wait_for(count_is_5, 14000));
	CHECK("a: newest first (105, 104, 103, 102, 101)",
	      index_of(105) == 0 && index_of(104) == 1 && index_of(103) == 2 && index_of(102) == 3 && index_of(101) == 4);
	CHECK("a: 101 exact (SMS: category 4, flags important+positive+negative)",
	      entry_is(4, 101, 4, 0x1A, "com.apple.MobileSMS", "Anna", "Hello, are you there?", "20261111T220546"));
	CHECK("a: 102 exact (mail: category 6, negative action)",
	      entry_is(3, 102, 6, 0x10, "com.apple.mobilemail", "Weekly report",
		       "The numbers are in. Please review before Friday.", "20261111T220612"));
	CHECK("a: 103 exact: identifier cut at 48 bytes, title at 48, the 200-byte message cut to 159 bytes on a character",
	      entry_is(2, 103, 4, 0x11, "com.example.chat.messenger.with.a.very.long.iden",
		       "Long title: 0123456789 0123456789 0123456789 012", EURO53, "20261111T220701"));
	CHECK("a: 104 exact (no actions, empty message)",
	      entry_is(1, 104, 0, 0x00, "com.apple.reminders", "Buy milk", "", "20261111T220710"));
	CHECK("a: 105 exact (the iPhone sent all 200 bytes: kept 160 and cut at a character)",
	      entry_is(0, 105, 11, 0x10, "com.spotify.client", "New release", EURO53, "20261111T220733"));
	CHECK("a: no message is longer than 160 bytes and none ends inside a character (every entry)",
	      all_entries_within_limits() && item_at(0, &it) && strlen(it.msg) == 159 && item_at(2, &it) &&
		      strlen(it.msg) == 159);

	/* (b) a change replaces the stored text; a removal deletes the entry */
	CHECK("b: the change arrived", wait_for(change_arrived, 12000));
	CHECK("b: the changed notification keeps its place and has the new flags (positive action gone)",
	      entry_is(4, 101, 4, 0x12, "com.apple.MobileSMS", "Anna", "Hello, are you there? Please answer.",
		       "20261111T220546"));
	CHECK("b: the removal deletes the entry", wait_for(count_is_4, 12000) && index_of(102) == -1);
	CHECK("b: order after the removal 105, 104, 103, 101",
	      index_of(105) == 0 && index_of(104) == 1 && index_of(103) == 2 && index_of(101) == 3);

	/* (b) the 17th drops the oldest */
	CHECK("b: thirteen more arrive: the store holds 16", wait_for(count_is_16_full, 25000));
	CHECK("b: the 17th notification dropped the oldest (101) and only that one",
	      index_of(101) == -1 && index_of(103) == 15 && index_of(122) == 0 && stats().inbox_dropped == 1);
	CHECK("b: all 16 entries have their text", all_text_ready());

	/* (c) actions */
	sleep_until(t0 + 23000);
	s0 = stats();
	CHECK("c: dismiss chosen on the ring for 122 is sent", rip_dismiss(122) == 0);
	CHECK("c: the inbox does not change on the ring's own command (122 is still there)",
	      rip_inbox_count() == 16 && index_of(122) == 0);
	k_sleep(K_MSEC(500));
	CHECK("c: positive action for 121 is sent", rip_action(121, RIP_ACTION_POSITIVE) == 0);
	k_sleep(K_MSEC(500));
	CHECK("c: an action without its flag is refused: dismiss of 104 (no actions)", rip_dismiss(104) == -ENOTSUP);
	CHECK("c: an action without its flag is refused: positive action of 103 (negative only)",
	      rip_action(103, RIP_ACTION_POSITIVE) == -ENOTSUP);
	CHECK("c: an unknown id is refused", rip_dismiss(999) == -ENOENT);
	s1 = stats();
	CHECK("c: two commands were sent and three were refused", s1.actions_sent - s0.actions_sent == 2 &&
	      s1.actions_refused - s0.actions_refused == 3 && s1.action_failed == s0.action_failed);
	CHECK("c: the iPhone reports the dismissed notification removed: 122 leaves the inbox",
	      wait_for(count_is_15, 5000) && index_of(122) == -1 && index_of(121) == 0);

	/* (f) media: the iPhone's report, then six commands that change nothing by themselves */
	CHECK("f: a new track and the playing state arrive from the iPhone", wait_for(media_new_track_playing, 20000));
	for (int c = 0; c < RIP_MEDIA_CMD_COUNT; c++) {
		CHECKF(rip_media_command((enum rip_media_cmd)c) == 0, "f: media command %d is sent", c);
		k_sleep(K_MSEC(500));
	}
	rip_media_get(&m);
	CHECK("f: the stored state did not change on the commands alone (pause was sent, the state is still playing)",
	      m.state == RIPL_PLAYER_PLAYING && strcmp(m.title, "Under Pressure") == 0 &&
		      strcmp(m.artist, "Queen and David Bowie") == 0);
	CHECK("f: six commands counted", stats().media_sent == 6);
	CHECK("f: the stored state follows the iPhone's next report (paused)", wait_for(media_paused_again, 10000));
	CHECK("f: play is sent while the player is paused", rip_media_command(RIP_MEDIA_PLAY) == 0);
	k_sleep(K_MSEC(800));
	rip_media_get(&m);
	CHECK("f: the stored state did not change on a play command either (paused stays paused)",
	      m.state == RIPL_PLAYER_PAUSED && stats().media_sent == 7);

	/* (g) a time change */
	CHECK("g: the ring's clock follows the iPhone's time change (two hours)", wait_for(clock_plus_2h, 10000));
	CHECK("g: the clock was set again (at least twice in all)", rtime_updates() >= 2);
	CHECK("g: the zone stays known and +120 minutes", rtime_zone_known() && rtime_tz_min() == 120);
	/* the stand-in refuses the next zone read (42.5 s): the zone the ring knows stays */
	sleep_until(t0 + 44000);
	CHECK("g: a zone read that failed changed nothing: the clock is still UTC (+2 h taken off) and the zone known",
	      clock_is(7200000LL) && rtime_zone_known() && rtime_tz_min() == 120 && stats().zone_errors == 1);

	/* (i) during RECORDING: events change no core state and start or stop no recording */
	sleep_until(t0 + 45000);
	inject(RC_SW_CENTRE, 1200);
	CHECK("i: a long press starts a recording", rglue_state() == RC_ST_RECORDING && rec_starts == 1 && rec_stops == 0);
	rep0 = reports();
	s0 = stats();
	sleep_until(t0 + 56000);
	s1 = stats();
	st_core = rglue_state();
	CHECK("i: events arrived during RECORDING (one added, one modified, one removed, a track, a state, a time)",
	      s1.ns_added - s0.ns_added == 1 && s1.ns_modified - s0.ns_modified == 1 && s1.ns_removed - s0.ns_removed == 1 &&
		      s1.media_reports - s0.media_reports >= 2 && s1.time_sets - s0.time_sets >= 1);
	rip_media_get(&m);
	CHECK("i: the media record shows the report", strcmp(m.title, "In recording") == 0 && m.state == RIPL_PLAYER_PLAYING);
	CHECK("i: the clock shows the iPhone's time (+2 h 1 min)", clock_is(7260000LL));
	CHECK("i: the core is still RECORDING, no recording started or stopped, no key sent",
	      st_core == RC_ST_RECORDING && rec_starts == 1 && rec_stops == 0 && reports() == rep0);
	inject(RC_SW_CENTRE, 1200);
	CHECK("i: a long press stops the recording", rglue_state() == RC_ST_STANDBY && rec_starts == 1 && rec_stops == 1);

	/* (i) during STANDBY */
	rep0 = reports();
	s0 = stats();
	sleep_until(t0 + 66000);
	s1 = stats();
	CHECK("i: events arrived during STANDBY (one added, one modified, one removed, a track, a state, a time)",
	      s1.ns_added - s0.ns_added == 1 && s1.ns_modified - s0.ns_modified == 1 && s1.ns_removed - s0.ns_removed == 1 &&
		      s1.media_reports - s0.media_reports >= 2 && s1.time_sets - s0.time_sets >= 1);
	rip_media_get(&m);
	CHECK("i: the media record shows the report (standby)", strcmp(m.title, "In standby") == 0 && m.state == RIPL_PLAYER_PAUSED);
	CHECK("i: the clock shows the iPhone's time (+2 h 2 min)", clock_is(7320000LL));
	CHECK("i: the core is still STANDBY, no recording started or stopped, no key sent",
	      rglue_state() == RC_ST_STANDBY && rec_starts == 1 && rec_stops == 1 && reports() == rep0);

	/* h (keys of step 2 still work with the iPhone as the active device) */
	rctl_set_mode(RCTL_MEDIA);
	rep0 = reports();
	inject(RC_SW_CENTRE, 100);
	CHECK("keys still go to the active device: media centre sends 2 reports", reports() - rep0 == 2);
	CHECK("no error was counted by the iPhone part",
	      stats().dm_errors == 0 && stats().fetch_errors == 0 && stats().fetch_timeouts == 0 &&
		      stats().action_errors == 0 && stats().action_failed == 0 && stats().media_errors == 0);
	(void)r;
}

/* ---- scenario R ---- */

static bool count_is_2_text(void)
{
	return rip_inbox_count() == 2 && all_text_ready();
}

static bool clock_local_now(void)
{
	return clock_is_local(0);
}

static int downs0;

static bool link_went_down(void)
{
	return link_down_events > downs0;
}

static bool has_204(void)
{
	return has_text(204);
}

static void run_r(void)
{
	struct rip_stats s;

	rctl_set_active(true);
	CHECK("pairing window opens", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	CHECK("the iPhone pairs; the notification service is found and subscribed", wait_for(ancs_ready, 40000));
	downs0 = link_down_events;
	CHECK("R: two notifications arrive", wait_for(count_is_2_text, 15000));
	CHECK("R: the iPhone gave no zone: the clock holds its local time and says the zone is not known",
	      wait_for(ams_cts_ready, 10000) && wait_for(clock_local_now, 6000) && !rtime_zone_known() && rtime_tz_min() == 0);
	CHECK("R: 202 then 201, flags exact, no pre-existing mark",
	      entry_is(0, 202, 6, 0x10, "com.example.two", "Second", "second message", "20261111T230010") &&
		      entry_is(1, 201, 4, 0x18, "com.example.one", "First", "first message", "20261111T230000"));

	/* (d) the link drops: the store is emptied */
	CHECK("d: the link drops", wait_for(link_went_down, 30000));
	k_sleep(K_MSEC(100));
	CHECK("d: the inbox is empty when the link has ended", rip_inbox_count() == 0);
	CHECK("d: the notification service is no longer ready", !rip_ancs_ready());
	CHECK("d: the clock stays set (time is not lost with the link)", rtime_is_set());

	/* (d) the iPhone comes back and sends again what it holds: 202 is gone, 203 is new, 201 was edited */
	CHECK("d: after the reconnect the service is subscribed again", wait_for(ancs_ready, 40000));
	CHECK("d: the inbox holds what the iPhone sends again", wait_for(count_is_2_text, 15000));
	CHECK("d: rebuilt from the iPhone: 203 then 201 with the pre-existing mark, the edited text; 202 is gone",
	      entry_is(0, 203, 0, 0x04, "com.example.three", "Third", "third message", "20261111T230100") &&
		      entry_is(1, 201, 4, 0x1C, "com.example.one", "First", "first message, edited while away",
			       "20261111T230000") &&
		      index_of(202) == -1);

	/* (e) the Notification Center Service is removed while linked (Service Changed) */
	CHECK("e: the ring stops when the service goes away", wait_for(ancs_not_ready, 20000));
	CHECK("e: the inbox is emptied when the service ends", rip_inbox_count() == 0);
	s = stats();
	CHECK("e: Service Changed was indicated and the services were stopped (twice: the drop and the removal)",
	      s.sc_indications >= 1 && s.ancs_down == 2);
	CHECK("e: the media and time services were stopped and found again with it", wait_for(ams_cts_ready, 20000));
	CHECK("e: the ring subscribes again when the service is back", wait_for(ancs_ready, 30000));
	CHECK("e: a new notification arrives and is stored exactly",
	      wait_for(has_204, 15000) &&
		      entry_is(index_of(204), 204, 5, 0x18, "com.example.four", "Fourth",
			       "fourth message after the service came back", "20261111T230200"));
	CHECK("e: what the iPhone still holds came again too (204, 203, 201)",
	      rip_inbox_count() == 3 && index_of(204) == 0 && index_of(203) == 1 && index_of(201) == 2);
	s = stats();
	CHECK("e: subscribed three times in all (start, after the drop, after Service Changed)", s.ancs_up == 3);
	CHECK("e: the sessions counted: two links", s.sessions == 2);
	CHECK("no error was counted by the iPhone part", s.dm_errors == 0 && s.fetch_errors == 0 && s.action_errors == 0);
}

/* ---- scenario L: an answer that comes after the ring's timeout ---- */

static bool l_four_texts(void)
{
	return rip_inbox_count() == 4 && all_text_ready();
}

static bool l_five_texts(void)
{
	return rip_inbox_count() == 5 && all_text_ready();
}

static void run_l(void)
{
	struct rip_stats s;

	rctl_set_active(true);
	CHECK("pairing window opens", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	CHECK("the iPhone pairs; the notification service is found and subscribed", wait_for(ancs_ready, 40000));
	CHECK("L: the four notifications all get their text, although the answer for the first is late",
	      wait_for(l_four_texts, 25000));
	CHECK("L: each of the four holds its own text (none shifted to its neighbour)",
	      entry_is(0, 404, 4, 0x18, "com.example.l4", "Late four", "message four", "20261111T231003") &&
		      entry_is(1, 403, 4, 0x18, "com.example.l3", "Late three", "message three", "20261111T231002") &&
		      entry_is(2, 402, 4, 0x18, "com.example.l2", "Late two", "message two", "20261111T231001") &&
		      entry_is(3, 401, 4, 0x18, "com.example.l1", "Late one", "message one", "20261111T231000"));
	s = stats();
	CHECK("L: the late answers for 401 arrived inside later requests and the ring skipped their bytes",
	      s.ds_skipped > 0);
	printk("RING INFO L: skipped %u bytes of the Data Source\n", s.ds_skipped);
	CHECK("L: one request timed out and was asked for once more, nothing was given up",
	      s.fetch_timeouts == 1 && s.fetch_retries == 1 && s.fetch_failed == 0);
	CHECK("L: a later notification gets its own text too", wait_for(l_five_texts, 20000) &&
	      entry_is(0, 405, 4, 0x18, "com.example.l5", "Late five", "message five", "20261111T231004"));
	s = stats();
	CHECK("L: no wrong answer was counted and no request was given up", s.fetch_errors == 0 && s.fetch_failed == 0);
}

/* ---- scenarios Z and W: the zone ---- */

static void run_z(void)
{
	rctl_set_active(true);
	CHECK("pairing window opens", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	CHECK("the iPhone pairs; the notification service is found and subscribed", wait_for(ancs_ready, 40000));
	int64_t t0 = k_uptime_get();

	CHECK("Z: zone +60 minutes: the clock shows UTC (within 100 ms)", wait_for(ams_cts_ready, 10000) &&
	      wait_for(clock_z1, 6000));
	sleep_until(t0 + 12500);
	CHECK("Z: the zone changed to +180 minutes while linked and the local time moved by 2 h: the clock still shows the same "
	      "UTC (within 100 ms) and the new zone", wait_for(clock_z2, 4000));
	CHECK("Z: the zone was read again", stats().zone_reads >= 2 && stats().zone_errors == 0);
	(void)zshift_ms;
}

static void run_w(void)
{
	rctl_set_active(true);
	CHECK("pairing window opens", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	CHECK("the iPhone pairs; the notification service is found and subscribed", wait_for(ancs_ready, 40000));
	int64_t t0 = k_uptime_get();

	CHECK("W: no Local Time Information: the clock holds the iPhone's local time (within 100 ms) and says the zone is not "
	      "known", wait_for(ams_cts_ready, 10000) && wait_for(clock_local_now, 6000) && !rtime_zone_known() &&
	      rtime_tz_min() == 0);
	sleep_until(t0 + 8500);
	CHECK("W: the local time moved by 1 h: the clock follows (within 100 ms), the zone is still not known",
	      clock_is_local(3600000LL) && !rtime_zone_known());
	CHECK("W: no zone was read and no error was counted", stats().zone_reads == 0 && stats().zone_errors == 0 &&
	      stats().dm_errors == 0 && stats().cts_up == 1);
}

/* ---- scenario D: the link ends while the ring is discovering ---- */

static bool d_one_text(void)
{
	return rip_inbox_count() == 1 && all_text_ready();
}

static void run_d(void)
{
	struct rip_stats s;

	rctl_set_active(true);
	CHECK("pairing window opens", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	downs0 = link_down_events;
	CHECK("D: the first link ends (the stand-in ends it while the ring is discovering)", wait_for(link_went_down, 40000));
	k_sleep(K_MSEC(200));
	s = stats();
	CHECK("D: the ring counted a session that ended in discovery", s.ended_in_discovery >= 1);
	CHECK("D: the three services are found in the next session", wait_for(pairing_and_services, 40000));
	CHECK("D: a notification sent in the next session arrives with its text", wait_for(d_one_text, 20000) &&
	      entry_is(0, 301, 4, 0x18, "com.example.d1", "After the drop", "found in the next session",
		       "20261111T231100"));
	s = stats();
	CHECK("D: the Media and Current Time services were each subscribed once (in the next session), the Notification "
	      "Center service at least once, and Service Changed was found",
	      s.ancs_up >= 1 && s.ams_up == 1 && s.cts_up == 1 && s.gattp_found >= 1);
	printk("RING INFO D: missing %u/%u/%u (ancs/ams/cts), dm_errors %u, dm_stale %u, sessions %u, ended in discovery %u\n",
	       s.ancs_missing, s.ams_missing, s.cts_missing, s.dm_errors, s.dm_stale, s.sessions, s.ended_in_discovery);
	CHECK("D: a discovery was running when the link ended and its answer was dropped as stale", s.dm_stale >= 1);
	CHECK("D: no service was reported missing (the answer of the ended session's discovery was not counted)",
	      s.ancs_missing == 0 && s.ams_missing == 0 && s.cts_missing == 0);
}

/* ---- scenario P: a host without Apple's services ---- */

static void run_p(void)
{
	struct rip_stats s;
	struct ripl_media m;
	uint32_t rep0;

	rctl_set_active(true);
	CHECK("pairing window opens", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	CHECK("the host pairs and its link is ready", wait_ready(0, 40000));
	k_sleep(K_MSEC(12000)); /* the iPhone part has looked for the services by now */
	s = stats();
	CHECK("h: the ring looked: a session started", s.sessions == 1);
	CHECK("h: Service Changed was looked for and found (the host has the GATT service), the three Apple services were "
	      "looked for and not found (not an error)",
	      s.gattp_found == 1 && s.gattp_missing == 0 && s.ancs_missing == 1 && s.ams_missing == 1 &&
		      s.cts_missing == 1 && s.dm_errors == 0);
	CHECK("h: no service is up", !rip_ancs_ready() && !rip_ams_ready() && !rip_cts_ready() && s.ancs_up == 0 &&
	      s.ams_up == 0 && s.cts_up == 0);
	CHECK("h: the inbox stays empty", rip_inbox_count() == 0);
	CHECK("h: an action finds nothing (-ENOENT), a media command says there is no media service (-ENOTCONN)",
	      rip_dismiss(1) == -ENOENT && rip_media_command(RIP_MEDIA_PLAY) == -ENOTCONN);
	rip_media_get(&m);
	CHECK("h: the player state stays unknown", m.state == RIPL_PLAYER_UNKNOWN && m.title[0] == '\0');
	CHECK("h: the clock is not set by a host without the time service", !rtime_is_set());
	rctl_set_mode(RCTL_MEDIA);
	rep0 = reports();
	inject(RC_SW_CENTRE, 100);
	CHECK("h: keys still work: media centre sends 2 reports", reports() - rep0 == 2);
	CHECK("h: the keys did not touch the inbox", rip_inbox_count() == 0);
}

int main(void)
{
	char *scen = nsi_host_getenv("RING_SCENARIO");
	int err;

	printk("RING START scenario %s\n", scen != NULL ? scen : "(none)");
	k_work_init_delayable(&fault_release, fault_release_fn);
	rglue_init(&glue_ops, RC_ST_STANDBY);
	rglue_set_screen_on(true);

	err = rctl_init();
	CHECK("HID service registered", err == 0);
	err = rdev_init(&cbs);
	CHECK("Bluetooth up, devices ready", err == 0);
	if (err != 0 || scen == NULL) {
		printk("RING RESULT FAIL\n");
		return 0;
	}
	if (strcmp(scen, "N") == 0) {
		run_n();
	} else if (strcmp(scen, "R") == 0) {
		run_r();
	} else if (strcmp(scen, "L") == 0) {
		run_l();
	} else if (strcmp(scen, "Z") == 0) {
		run_z();
	} else if (strcmp(scen, "W") == 0) {
		run_w();
	} else if (strcmp(scen, "D") == 0) {
		run_d();
	} else if (strcmp(scen, "P") == 0) {
		run_p();
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
