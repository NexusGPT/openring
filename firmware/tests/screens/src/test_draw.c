/*
 * Suite screens_draw: the drawing part on the memory display. A scripted scene drives the real core (ring_core gestures and
 * state table) and the screens thread; the other modules are their own data structures (ring_inbox, ring_time, the media
 * decoder of ring_iphone, the device list of ring_devices) behind struct rscr_ops. Each scene ends with a picture read back
 * from the frame the display driver received (the 120 x 240 panel memory, turned back) and pixel checks on it: a blank or
 * wrong-screen frame fails. Every expected region and count is a literal written here.
 *
 * Time: the screens' clock is k_uptime_get() plus a skew that the test moves forward (the recording timer shows 00:12:47
 * without waiting 767 s).
 */

#include <stdio.h>
#include <string.h>
#include <zephyr/kernel.h>
#include <zephyr/ztest.h>

#include <ring_core/rc_core.h>
#include <ring_devices/rdev_logic.h>
#include <ring_inbox/rinbox.h>
#include <ring_iphone/ripl.h>
#include <ring_screens/rmd.h>
#include <ring_screens/rscr.h>
#include <ring_time/rtime.h>
#include <ring_time/rtime_logic.h>

char *nsi_host_getenv(const char *name);

/* ---- the other modules, as data ---- */

static struct rinbox inbox;
static struct ripl_media media;
static struct rdev_list devs;
static bool link_up = true;
static bool ams_up = true;
static int64_t skew;

static struct {
	int dismiss, positive, read, pair_open, pair_cancel, dev_use, dev_remove, control, power_off, vibration;
	k_tid_t power_off_thread;
	uint32_t last_uid;
	uint8_t last_slot;
	bool control_on;
	int mode;
} calls;

static int64_t t_now(void)
{
	return k_uptime_get() + skew;
}

static uint8_t o_inbox_count(void)
{
	return rinbox_count(&inbox);
}

static bool o_inbox_get(uint8_t i, struct rinbox_item *o)
{
	const struct rinbox_item *it = rinbox_get(&inbox, i);

	if (it == NULL) {
		return false;
	}
	*o = *it;
	return true;
}

static void o_media_get(struct ripl_media *o)
{
	*o = media;
}

static bool o_ams_ready(void)
{
	return ams_up;
}

static uint8_t o_paired(void)
{
	return devs.paired;
}

static uint8_t o_active(void)
{
	return devs.active;
}

static bool o_link(void)
{
	return link_up;
}

static int o_dismiss(uint32_t uid)
{
	calls.dismiss++;
	calls.last_uid = uid;
	return 0;
}

static int o_positive(uint32_t uid)
{
	calls.positive++;
	calls.last_uid = uid;
	return 0;
}

static int o_read(uint32_t uid)
{
	calls.read++;
	return rinbox_mark_read(&inbox, uid);
}

static int o_pair_open(uint8_t slot)
{
	calls.pair_open++;
	calls.last_slot = slot;
	return 0;
}

static void o_pair_cancel(void)
{
	calls.pair_cancel++;
}

static int o_dev_use(uint8_t slot)
{
	calls.dev_use++;
	calls.last_slot = slot;
	return rdev_list_switch(&devs, slot) == RDEV_SWITCH_GO ? 0 : 0;
}

static int o_dev_remove(uint8_t slot)
{
	calls.dev_remove++;
	calls.last_slot = slot;
	return rdev_list_remove(&devs, slot);
}

static void o_control(bool on)
{
	calls.control++;
	calls.control_on = on;
}

static void o_mode(enum rctl_mode m)
{
	calls.mode = m;
}

static K_MUTEX_DEFINE(fake_glue);   /* stands for the glue's lock: the real power off must not wait for it */
static int power_off_busy_seen;

static int o_power_off(void)
{
	if (k_mutex_lock(&fake_glue, K_NO_WAIT) != 0) {
		power_off_busy_seen++;
		return -EBUSY;
	}
	calls.power_off++;
	calls.power_off_thread = k_current_get();
	k_mutex_unlock(&fake_glue);
	return 0;
}

static void o_vibration(bool on)
{
	calls.vibration++;
	ARG_UNUSED(on);
}

static struct rc_core core;

static const struct rscr_ops ops = {
	.inbox_count = o_inbox_count, .inbox_get = o_inbox_get, .media_get = o_media_get, .ams_ready = o_ams_ready,
	.paired_mask = o_paired, .active = o_active, .link_up = o_link, .dismiss = o_dismiss, .positive = o_positive,
	.mark_read = o_read, .pair_open = o_pair_open, .pair_cancel = o_pair_cancel, .dev_use = o_dev_use,
	.dev_remove = o_dev_remove, .control_active = o_control, .set_mode = o_mode, .power_off = o_power_off,
	.vibration = o_vibration, .now_ms = t_now,
};

/* ---- the scripted joystick: the real core, then the screens' glue entry (what rglue does) ---- */

static int seen_screen_actions, seen_screen_on, seen_mt;

static void after(struct rc_actions *a)
{
	enum rc_event last = a->last_row > 0 ? rscr_row_event(a->last_row) : RC_EV_COUNT;

	for (uint8_t i = 0; i < a->n; i++) {
		seen_screen_actions += a->a[i] >= RC_ACT_SCREEN_CENTRE && a->a[i] <= RC_ACT_SCREEN_RIGHT;
		seen_screen_on += a->a[i] == RC_ACT_SCREEN_ON;
		seen_mt += a->a[i] == RC_ACT_MT;
	}
	(void)rscr_glue_after(a, last, rc_core_state(&core), t_now());
}

/* what the glue does before every core call: read the lock fact from the screens, under one lock */
static void fact(void)
{
	core.facts.screen_on = rscr_lock_fact_now();
}

static void tick_to(int64_t t)
{
	struct rc_actions a;

	rc_actions_clear(&a);
	fact();
	rc_core_tick(&core, t, &a);
	after(&a);
}

static void run_for(int ms)
{
	int64_t end = t_now() + ms;

	for (int64_t t = t_now() + 50; t <= end; t += 50) {
		skew += 50;
		tick_to(t);
	}
}

static void edge(enum rc_switch sw, bool down)
{
	struct rc_actions a;

	rc_actions_clear(&a);
	fact();
	rc_core_input(&core, sw, down, t_now(), &a);
	after(&a);
}

static void joy_dir(enum rc_switch sw)
{
	run_for(300);
	edge(sw, true);
	run_for(60);
	edge(sw, false);
	run_for(100);
}

static void joy_short(void)
{
	run_for(300);
	edge(RC_SW_CENTRE, true);
	run_for(100);
	edge(RC_SW_CENTRE, false);
	run_for(450);
}

static void joy_double(void)
{
	run_for(300);
	edge(RC_SW_CENTRE, true);
	run_for(100);
	edge(RC_SW_CENTRE, false);
	run_for(150);
	edge(RC_SW_CENTRE, true);
	run_for(100);
	edge(RC_SW_CENTRE, false);
	run_for(500);
}

static void joy_long(void)
{
	run_for(300);
	edge(RC_SW_CENTRE, true);
	run_for(1050);
	edge(RC_SW_CENTRE, false);
	run_for(100);
}

static void core_event(enum rc_event ev)
{
	struct rc_actions a;

	rc_actions_clear(&a);
	fact();
	rc_core_event(&core, ev, t_now(), &a);
	after(&a);
}

static void core_battery(enum rc_batt b)
{
	struct rc_actions a;

	rc_actions_clear(&a);
	fact();
	rc_core_battery(&core, b, t_now(), &a);
	after(&a);
}

/* ---- the picture and the pixel checks ---- */

static uint8_t pic[RSCR_W * RSCR_H * 3];
static int pic_count;

static void grab(void)
{
	rscr_sync();
	rscr_capture_rgb(pic);
}

static int count_px(int x0, int y0, int x1, int y1, bool (*pred)(uint8_t, uint8_t, uint8_t))
{
	int n = 0;

	for (int y = y0; y <= y1 && y < RSCR_H; y++) {
		for (int x = x0; x <= x1 && x < RSCR_W; x++) {
			const uint8_t *p = &pic[(y * RSCR_W + x) * 3];

			n += pred(p[0], p[1], p[2]) ? 1 : 0;
		}
	}
	return n;
}

static bool lit(uint8_t r, uint8_t g, uint8_t b)
{
	return r > 60 || g > 60 || b > 60;
}

static bool light(uint8_t r, uint8_t g, uint8_t b)
{
	return r >= 225 && r <= 247 && g >= 218 && g <= 240 && b >= 205 && b <= 230;   /* the light pill fill (236, 230, 218), not the white text */
}

static bool red(uint8_t r, uint8_t g, uint8_t b)
{
	return r > 200 && g < 100 && b < 100;
}

static bool green(uint8_t r, uint8_t g, uint8_t b)
{
	return g > 160 && r < 120 && b < 140;
}

static bool amber(uint8_t r, uint8_t g, uint8_t b)
{
	return r > 200 && g > 120 && g < 200 && b < 60;
}

static bool white(uint8_t r, uint8_t g, uint8_t b)
{
	return r > 200 && g > 200 && b > 200;
}

static uint64_t pic_hash(void)
{
	uint64_t h = 1469598103934665603ULL;

	for (size_t i = 0; i < sizeof(pic); i++) {
		h = (h ^ pic[i]) * 1099511628211ULL;
	}
	return h;
}

#define LIT(x0, y0, x1, y1) count_px(x0, y0, x1, y1, lit)

#include "test_refs.h"

/* Save the picture (when RING_PICS names a folder) and print its manifest line. The manifest line carries the scene. */
static void save(const char *name, const char *scene)
{
	char path[200];
	const char *dir = nsi_host_getenv("RING_PICS");
	int total = LIT(0, 0, RSCR_W - 1, RSCR_H - 1);
	int rc = 0;

	pic_count++;
	if (dir != NULL && dir[0] != '\0') {
		snprintf(path, sizeof(path), "%s/%s.png", dir, name);
		rc = rscr_capture_png(path, 1);
		snprintf(path, sizeof(path), "%s/%s-4x.png", dir, name);
		rc |= rscr_capture_png(path, 4);
	}
	printk("SCREENPIC %s | scene: %s | 240x120 | hash %016llx | lit px %d | files %s\n", name, scene, pic_hash(),
	       total, dir != NULL && dir[0] != '\0' ? (rc == 0 ? "written" : "WRITE FAILED") : "not written (no RING_PICS)");
	zassert_equal(rc, 0, "writing the picture %s failed", name);
	{
		int i = scene_index(name);

		zassert_true(i >= 0, "scene %s is not in the table", name);
		memcpy(scene_pic[i], pic, sizeof(pic));
		scene_have[i] = true;
		/* the key values (time, timer, digits, percent, count, text) are in the frame: compared with the same text drawn alone */
		zassert_true(scene_ok(i, pic), "%s: a key value is not what the scene says", name);
		rscr_sync();   /* the reference drawing used the display: the screens draw their frame again */
	}
}

static int64_t civil_ms(int y, int mo, int d, int h, int mi)
{
	int64_t days;

	zassert_equal(rtime_days_from_civil(y, mo, d, &days), 0, "date");
	return days * 86400000LL + ((int64_t)h * 60 + mi) * 60000LL;
}

static void put_notif(uint32_t uid, uint8_t flags, const char *app, const char *title, const char *msg)
{
	uint32_t dropped;

	zassert_equal(rinbox_add(&inbox, uid, 4, flags, &dropped), 0, "add");
	zassert_equal(rinbox_set_text(&inbox, uid, app, strlen(app), title, strlen(title), msg, strlen(msg),
				      "20261112T104200", 15), 0, "text");
}

/* ---- the suite ---- */

static void *suite_setup(void)
{
	static bool started;

	if (!started) {
		rinbox_init(&inbox);
		ripl_media_init(&media);
		rdev_list_init(&devs);
		rc_core_init(&core, RC_CENTRE_SW2, RC_ST_STANDBY, 0);
		rtime_set(civil_ms(2026, 11, 12, 10, 42), 0, true);
		zassert_equal(rscr_start(&ops), 0, "screens start (LVGL on the memory display)");
		started = true;
	}
	return NULL;
}

/* the scenes run in this order (ztest runs the tests of a suite in definition order) */

ZTEST(screens_draw, test_01_status_from_the_clock)
{
	struct rmd_stats ms;

	rscr_sync();
	rmd_stats_get(&ms);
	zassert_true(ms.blanked, "the panel starts dark, STANDBY with no input");
	joy_short();   /* screen off: a short press turns it on, status screen */
	grab();
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY, "standby");
	/* the time "10:42" in the top left, the word "Ready" under it, nothing red, mostly black */
	zassert_true(LIT(18, 12, 110, 48) > 150, "time digits: %d lit px", LIT(18, 12, 110, 48));
	zassert_true(LIT(18, 56, 80, 76) > 30, "Ready: %d lit px", LIT(18, 56, 80, 76));
	zassert_equal(count_px(0, 0, 239, 119, red), 0, "no red on the status screen");
	zassert_equal(LIT(130, 0, 239, 119), 0, "right half empty");
	rmd_stats_get(&ms);
	zassert_false(ms.blanked, "the panel is on");
	save("status", "STANDBY, screen off, short press of the centre; clock set to 2026-11-12 10:42 UTC (rtime_set)");
	/* the time comes from the clock: one minute later the time of the scene is no longer in the frame (10:43, not 10:42) */
	rtime_set(civil_ms(2026, 11, 12, 10, 43), 0, true);
	grab();
	zassert_false(scene_ok(scene_index("status"), pic), "a wrong time fails the status scene");
	rscr_sync();
	rtime_set(civil_ms(2026, 11, 12, 10, 42), 0, true);
}

ZTEST(screens_draw, test_02_menu_highlight_moves_with_down)
{
	uint64_t h[3];
	int band[3][2];

	joy_dir(RC_SW_RIGHT);
	grab();
	{
		struct rscr s;

		rscr_snapshot(&s);
		zassert_equal(s.screen, SCR_MENU, "menu open: %s", rscr_screen_name(s.screen));
	}
	band[0][0] = count_px(12, 14, 228, 41, light);
	band[0][1] = count_px(12, 44, 228, 71, light);
	zassert_true(band[0][0] > 1500 && band[0][1] < 50, "item 0 highlighted: %d / %d", band[0][0], band[0][1]);
	/* text of the first items is there (white text on the dark rows), the sixth is not shown yet */
	zassert_true(LIT(18, 44, 200, 71) > 100, "the second item's text");
	save("menu", "SCR_MENU, first item highlighted (Right from the status screen)");
	h[0] = pic_hash();
	joy_dir(RC_SW_DOWN);
	grab();
	band[1][0] = count_px(12, 14, 228, 41, light);
	band[1][1] = count_px(12, 44, 228, 71, light);
	zassert_true(band[1][1] > 1500 && band[1][0] < 50, "after Down the highlight is on item 1: %d / %d", band[1][0],
		     band[1][1]);
	h[1] = pic_hash();
	joy_dir(RC_SW_DOWN);
	grab();
	h[2] = pic_hash();
	zassert_true(h[0] != h[1] && h[1] != h[2], "each Down changes the frame");
	/* the sixth item "Power off" is reached with three more Downs, and Down at the end does not move */
	for (int i = 0; i < 4; i++) {
		joy_dir(RC_SW_DOWN);
	}
	{
		struct rscr s;

		rscr_snapshot(&s);
		zassert_equal(s.menu_sel, MENU_POWER_OFF, "bottom of the menu");
	}
	for (int i = 0; i < 5; i++) {
		joy_dir(RC_SW_UP);
	}
}

ZTEST(screens_draw, test_03_settings_screen)
{
	joy_dir(RC_SW_DOWN);
	joy_dir(RC_SW_DOWN);
	joy_dir(RC_SW_DOWN);
	joy_dir(RC_SW_DOWN);   /* Settings is the fifth item */
	joy_dir(RC_SW_RIGHT);
	grab();
	{
		struct rscr s;

		rscr_snapshot(&s);
		zassert_equal(s.screen, SCR_SETTINGS, "settings: %s", rscr_screen_name(s.screen));
	}
	zassert_true(count_px(12, 30, 228, 53, light) > 1000, "first setting highlighted");
	zassert_true(LIT(150, 30, 222, 53) > 20, "its value is shown");
	save("settings", "SCR_SETTINGS, Screen brightness highlighted");
	/* vibration off through the screen reaches the core's setting */
	joy_dir(RC_SW_DOWN);
	joy_dir(RC_SW_RIGHT);
	zassert_equal(calls.vibration, 1, "vibration setting changed once");
	joy_dir(RC_SW_RIGHT);
	zassert_equal(calls.vibration, 2, "and back");
	joy_dir(RC_SW_LEFT);   /* back to the menu */
	joy_dir(RC_SW_LEFT);   /* and to the status screen */
}

ZTEST(screens_draw, test_04_recording_screens_and_sign)
{
	struct rmd_stats m0, m1;
	struct rscr_stats rs;
	struct rscr s;
	int64_t want;

	rmd_stats_get(&m0);
	joy_long();
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING, "recording");
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_RECORDING, "SCR_RECORDING right after the start");
	/* jump to 00:12:47 of elapsed time with no input: the screen dimmed after 3 s */
	want = 767000;
	skew += want - (t_now() - s.rec_start);
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_REC_DIM, "dimmed: %s", rscr_screen_name(s.screen));
	/* only the red dot and the timer: the dot's pixels, the timer's pixels, black elsewhere */
	zassert_true(count_px(14, 84, 30, 100, red) >= 40, "red dot: %d px", count_px(14, 84, 30, 100, red));
	zassert_true(LIT(140, 82, 222, 100) > 60, "the timer text: %d", LIT(140, 82, 222, 100));
	zassert_equal(LIT(0, 0, 239, 80), 0, "nothing above the dot and the timer");
	zassert_equal(LIT(32, 81, 139, 119), 0, "nothing between them");
	/* finding 1: SCR_REC_DIM is driven at the lowest of the three levels (85), never at 0 */
	rmd_stats_get(&m1);
	zassert_equal(m1.brightness, 85, "the brightness the display received while SCR_REC_DIM is shown: %u", m1.brightness);
	save("recording-idle", "RECORDING, 3 s after the last input, 00:12:47 elapsed (SCR_REC_DIM)");
	/* an input (the lock: it only brings the full picture) */
	joy_dir(RC_SW_RIGHT);
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_RECORDING, "full picture after input");
	zassert_true(count_px(14, 84, 30, 100, red) >= 40, "red dot");
	zassert_true(LIT(18, 6, 222, 70) > 200, "waveform lines: %d", LIT(18, 6, 222, 70));
	zassert_true(LIT(36, 82, 120, 100) > 60, "the word Recording");
	zassert_true(LIT(140, 82, 222, 100) > 60, "the timer");
	rmd_stats_get(&m1);
	zassert_equal(m1.brightness, 255, "the full picture is driven at the setting's level (the third of three: 255): %u", m1.brightness);
	save("recording", "RECORDING, a joystick direction 0 s ago, 00:12:47 elapsed (SCR_RECORDING)");
	{
		/* a second later (the screen is still the full picture) the timer reads 00:12:48: the scene's timer is gone */
		skew += 1000;
		grab();
		zassert_true(count_px(14, 84, 30, 100, red) >= 40, "red dot still there");
		zassert_false(scene_ok(scene_index("recording"), pic), "a wrong timer fails the recording scene");
	}
	/* a short press is a highlight: the count shows */
	joy_short();
	grab();
	zassert_true(LIT(140, 60, 222, 78) > 20, "the highlight count line");
	save("recording-highlight", "RECORDING, one highlight marked (short press), SCR_RECORDING with the count");
	/* a second highlight: the count and the timer are no longer those of the scene */
	joy_short();
	grab();
	zassert_false(scene_ok(scene_index("recording-highlight"), pic), "a wrong highlight count fails its scene");
	rmd_stats_get(&m1);
	rscr_stats_get(&rs);
	zassert_equal(m1.blank_on, m0.blank_on, "the display was never blanked during the recording (%u)",
		      m1.blank_on - m0.blank_on);
	zassert_equal(rs.sign_missing, 0, "no frame in RECORDING without the sign");
	zassert_equal(rs.draw_errors, 0, "no refused draw");
	/* stop: back to the status screen */
	joy_long();
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY, "stopped");
}

ZTEST(screens_draw, test_05_rsign_display_refusal_leaves_the_microphone_off)
{
	struct rmd_stats m;
	int rc;

	run_for(6000);   /* the screen is off again */
	rscr_sync();
	rmd_stats_get(&m);
	zassert_true(m.blanked, "dark in STANDBY");
	/* a recording starts (the core is in RECORDING when the recorder carries out RC_ACT_OPEN): the recorder calls
	 * rscr_sign_start() before it switches the microphone supply on */
	joy_long();
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING, "recording");
	rmd_inject_fail(-1);
	rc = rscr_sign_start(t_now());
	zassert_true(rc != 0, "the display refused the frame: the sign is not drawn (%d)", rc);
	rmd_inject_fail(0);
	rc = rscr_sign_start(t_now());
	zassert_equal(rc, 0, "the display accepted the frame");
	rmd_stats_get(&m);
	zassert_false(m.blanked, "and is on");
	grab();
	zassert_true(count_px(14, 84, 30, 100, red) >= 40, "the red dot is in the frame at 00:00:00");
	zassert_true(LIT(140, 82, 222, 100) > 60, "and the timer");
	/* the panel blanked (a fault) before the sign is drawn: the sign start unblanks it and draws */
	zassert_equal(rscr_panel(false, 0), 0, "blank the panel");
	rc = rscr_sign_start(t_now());
	zassert_equal(rc, 0, "the sign start brings the panel back on");
	rmd_stats_get(&m);
	zassert_false(m.blanked, "unblanked");
	joy_long();
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY, "stopped");
	run_for(6000);
}

ZTEST(screens_draw, test_06_notifications_list_and_detail)
{
	uint64_t h_empty, h_one;
	struct rscr s;

	joy_dir(RC_SW_UP);   /* wake */
	joy_dir(RC_SW_UP);   /* open the list */
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_NOTIFS, "list: %s", rscr_screen_name(s.screen));
	zassert_true(LIT(18, 10, 200, 26) > 40, "the heading");
	zassert_true(LIT(18, 50, 120, 70) > 30, "None");
	save("notifications-empty", "SCR_NOTIFS with an empty inbox");
	h_empty = pic_hash();
	put_notif(100, RINBOX_F_POSITIVE | RINBOX_F_NEGATIVE, "com.apple.MobileSMS", "Grace Lin",
		  "Any update on the hero shot?");
	put_notif(101, RINBOX_F_NEGATIVE, "com.example.mail", "Weekly report", "The numbers for the week are attached.");
	rscr_poke();
	grab();
	h_one = pic_hash();
	zassert_true(h_one != h_empty, "the list with notifications differs from the empty list");
	zassert_true(count_px(12, 30, 228, 53, light) > 1000, "first notification highlighted (newest first)");
	zassert_true(count_px(14, 36, 30, 47, green) > 10, "unread mark");
	save("notifications", "SCR_NOTIFS, two notifications in the inbox, newest first, the first highlighted");
	joy_dir(RC_SW_RIGHT);
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_NOTIF, "detail: %s", rscr_screen_name(s.screen));
	/* newest first: uid 101 is first. Open 100 (the second) with Down in the detail. */
	joy_dir(RC_SW_DOWN);
	rscr_snapshot(&s);
	zassert_equal(s.notif_uid, 100, "the neighbour (second) notification");
	grab();
	zassert_true(LIT(44, 8, 222, 30) > 80, "title");
	zassert_true(LIT(18, 36, 222, 70) > 120, "message");
	zassert_true(LIT(18, 76, 60, 106) > 60, "dismiss at the left edge");
	zassert_true(LIT(180, 76, 222, 106) > 40, "the positive action at the right edge");
	save("notification", "SCR_NOTIF, 'Grace Lin' with both actions (dismiss left, positive right)");
	{
		uint64_t h = pic_hash();

		/* the dismiss-only notification shows no positive action */
		joy_dir(RC_SW_UP);
		grab();
		zassert_equal(LIT(180, 76, 222, 106), 0, "no positive action for a notification that has none");
		zassert_true(pic_hash() != h, "another notification, another frame");
		joy_dir(RC_SW_DOWN);
	}
	/* dismiss chosen with the joystick: the negative action goes to the iPhone part for this uid */
	calls.dismiss = 0;
	joy_dir(RC_SW_LEFT);
	zassert_equal(calls.dismiss, 1, "dismiss called once");
	zassert_equal(calls.last_uid, 100, "for the notification shown");
	zassert_equal(rinbox_count(&inbox), 2, "the inbox changes only when the iPhone reports the removal");
	calls.positive = 0;
	joy_dir(RC_SW_RIGHT);
	zassert_equal(calls.positive, 1, "positive action called once");
	/* the iPhone reports the removal */
	zassert_equal(rinbox_remove(&inbox, 100), 0, "removed");
	rscr_poke();
	rscr_sync();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_NOTIFS, "back to the list when the notification is gone: %s", rscr_screen_name(s.screen));
	joy_dir(RC_SW_LEFT);
}

ZTEST(screens_draw, test_07_modes_and_the_four_control_screens)
{
	static const char *const names[4] = { "control-media", "control-presenter", "control-pointer", "control-agent" };
	struct rscr s;

	/* the media record from the iPhone part's decoder */
	zassert_equal(ripl_media_apply(&media, RIPL_AMS_ENTITY_TRACK, RIPL_AMS_TRACK_ATTR_TITLE, (const uint8_t *)"Night Drive", 11), 1, "");
	zassert_equal(ripl_media_apply(&media, RIPL_AMS_ENTITY_PLAYER, RIPL_AMS_PLAYER_ATTR_PLAYBACK_INFO, (const uint8_t *)"1,1.0,0.0", 9), 1, "");
	joy_dir(RC_SW_DOWN);   /* wake (status), then open the menu */
	joy_dir(RC_SW_RIGHT);
	joy_dir(RC_SW_DOWN);   /* Control */
	joy_dir(RC_SW_RIGHT);
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_MODES, "modes: %s", rscr_screen_name(s.screen));
	zassert_equal(s.mode_sel, RCTL_MEDIA, "Media highlighted the first time");
	zassert_true(count_px(12, 30, 228, 53, light) > 1000, "Media highlighted");
	save("modes", "SCR_MODES, Media highlighted (first time)");
	for (int m = 0; m < 4; m++) {
		uint64_t before;

		if (m > 0) {
			/* back to the mode list with a double press, move down, open */
			joy_double();
			rscr_snapshot(&s);
			zassert_equal(s.screen, SCR_MODES, "double press closes the session and shows the modes");
			zassert_false(s.session, "closed");
			joy_dir(RC_SW_DOWN);
		}
		calls.control = 0;
		joy_dir(RC_SW_RIGHT);
		zassert_true(calls.control_on, "control is active in the session");
		zassert_equal(calls.mode, m, "mode set");
		grab();
		rscr_snapshot(&s);
		zassert_equal(s.screen, SCR_CONTROL, "control screen");
		zassert_equal(s.mode, m, "mode");
		zassert_true(LIT(18, 8, 110, 30) > 40, "mode name");
		zassert_true(LIT(18, 86, 200, 104) > 50, "Press twice to leave");
		zassert_equal(count_px(18, 30, 222, 52, amber), 0, "connected: no amber warning");
		before = pic_hash();
		switch (m) {
		case RCTL_MEDIA:
			zassert_true(LIT(18, 32, 222, 52) > 100, "track title");
			zassert_true(count_px(160, 60, 188, 88, light) > 300, "the play-state circle");
			save(names[m], "SCR_CONTROL Media: track 'Night Drive', playing (decoder of ring_iphone)");
			/* paused: the glyph differs */
			zassert_equal(ripl_media_apply(&media, RIPL_AMS_ENTITY_PLAYER, RIPL_AMS_PLAYER_ATTR_PLAYBACK_INFO,
						       (const uint8_t *)"0,0.0,0.0", 9), 1, "");
			rscr_poke();
			grab();
			zassert_true(pic_hash() != before, "the pause glyph differs from the play glyph");
			zassert_equal(ripl_media_apply(&media, RIPL_AMS_ENTITY_TRACK, RIPL_AMS_TRACK_ATTR_TITLE,
						       (const uint8_t *)"Other Song", 10), 1, "");
			rscr_poke();
			grab();
			zassert_true(pic_hash() != before, "a new title changes the frame");
			zassert_equal(ripl_media_apply(&media, RIPL_AMS_ENTITY_TRACK, RIPL_AMS_TRACK_ATTR_TITLE,
						       (const uint8_t *)"Night Drive", 11), 1, "");
			zassert_equal(ripl_media_apply(&media, RIPL_AMS_ENTITY_PLAYER, RIPL_AMS_PLAYER_ATTR_PLAYBACK_INFO,
						       (const uint8_t *)"1,1.0,0.0", 9), 1, "");
			rscr_poke();
			grab();
			zassert_equal(pic_hash(), before, "back to the same frame");
			break;
		case RCTL_PRESENTER:
			zassert_true(LIT(18, 32, 100, 52) > 40, "Slides");
			zassert_true(count_px(160, 60, 188, 88, light) > 300, "the next-slide circle");
			save(names[m], "SCR_CONTROL Presenter");
			break;
		case RCTL_POINTER:
			zassert_true(LIT(100, 62, 222, 86) > 60, "four arrows");
			save(names[m], "SCR_CONTROL Pointer");
			break;
		default:
			zassert_true(count_px(18, 60, 110, 90, red) > 40, "Decline in red at the left");
			zassert_true(count_px(130, 60, 222, 90, green) > 40, "Accept in green at the right");
			save(names[m], "SCR_CONTROL Agent, words Accept and Decline only");
			/* no link: the screen says so */
			link_up = false;
			rscr_poke();
			grab();
			zassert_true(count_px(18, 30, 222, 52, amber) > 30, "Not connected in amber: %d",
				     count_px(18, 30, 222, 52, amber));
			link_up = true;
			rscr_poke();
			break;
		}
	}
	joy_double();
}

ZTEST(screens_draw, test_08_devices_device_confirm)
{
	struct rscr s;
	uint64_t h0;

	zassert_equal(rdev_list_add(&devs, 0), 0, "");
	zassert_equal(rdev_list_add(&devs, 1), 0, "");
	zassert_equal(rdev_list_add(&devs, 2), 0, "");
	zassert_equal(rdev_list_switch(&devs, 1) == RDEV_SWITCH_GO || devs.active == 1, true, "the second device active");
	rscr_set_device_name(0, "Phone");
	rscr_set_device_name(1, "Laptop");
	rscr_set_device_name(2, "Tablet");
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_MODES, "from the modes screen");
	joy_dir(RC_SW_LEFT);   /* menu */
	joy_dir(RC_SW_UP);     /* menu_sel back from Control to Recordings... */
	joy_dir(RC_SW_DOWN);
	joy_dir(RC_SW_DOWN);   /* Devices */
	joy_dir(RC_SW_RIGHT);
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_DEVICES, "devices: %s", rscr_screen_name(s.screen));
	/* three pills; the active one (the second) is the light one, the cursor ring is on the first */
	zassert_true(count_px(86, 52, 150, 76, light) > 400, "the active device is the light pill: %d",
		     count_px(86, 52, 150, 76, light));
	zassert_true(count_px(16, 52, 80, 76, light) < 60, "the others are dark");
	zassert_true(count_px(14, 50, 82, 78, white) > 60, "the cursor ring on the first");
	zassert_true(LIT(158, 52, 222, 76) > 20, "third device's name");
	save("devices", "SCR_DEVICES, three devices Phone, Laptop (active, light pill), Tablet (neutral names set with rscr_set_device_name); cursor on the first");
	h0 = pic_hash();
	joy_dir(RC_SW_DOWN);
	grab();
	zassert_true(pic_hash() != h0, "the cursor moves with Down");
	joy_dir(RC_SW_RIGHT);
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_DEVICE, "device: %s", rscr_screen_name(s.screen));
	zassert_equal(s.dev_slot, 1, "the second device");
	zassert_true(LIT(18, 8, 140, 30) > 40, "the device name");
	zassert_true(count_px(12, 40, 228, 66, light) > 1000, "Use highlighted");
	save("device", "SCR_DEVICE, Laptop, 'Use' highlighted");
	joy_dir(RC_SW_DOWN);
	joy_dir(RC_SW_RIGHT);
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_CONFIRM, "confirm: %s", rscr_screen_name(s.screen));
	zassert_true(count_px(18, 54, 200, 72, green) > 80, "the Yes line in green");
	zassert_true(LIT(18, 10, 222, 30) > 80, "the question");
	save("confirm", "SCR_CONFIRM, 'Remove Laptop?'");
	calls.dev_remove = 0;
	joy_dir(RC_SW_LEFT);   /* No */
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_DEVICE, "No goes back");
	zassert_equal(calls.dev_remove, 0, "nothing removed");
	joy_dir(RC_SW_UP);
	joy_dir(RC_SW_RIGHT);   /* Use */
	zassert_equal(calls.dev_use, 1, "Use called");
	zassert_equal(calls.last_slot, 1, "for slot 1");
	joy_dir(RC_SW_LEFT);
	joy_dir(RC_SW_LEFT);
}

ZTEST(screens_draw, test_09_pairing_passkey)
{
	struct rscr s;
	int a, b;

	/* free a slot: remove the third device */
	zassert_equal(rdev_list_remove(&devs, 2), 0, "");
	rscr_poke();
	joy_dir(RC_SW_RIGHT);  /* the status screen: Right opens the menu */
	joy_dir(RC_SW_DOWN);
	joy_dir(RC_SW_DOWN);
	joy_dir(RC_SW_DOWN);   /* Pair device */
	calls.pair_open = 0;
	joy_dir(RC_SW_RIGHT);
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_PAIR, "pairing screen: %s", rscr_screen_name(s.screen));
	zassert_equal(calls.pair_open, 1, "the pairing window is opened");
	zassert_equal(calls.last_slot, 2, "the lowest free slot");
	/* the screen stays on while pairing: 10 s later it is still there */
	run_for(10000);
	rscr_sync();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_PAIR, "still on after 10 s");
	rscr_on_passkey(2, 482913);
	grab();
	a = LIT(18, 34, 150, 74);
	zassert_true(a > 200, "the six digits: %d lit px", a);
	zassert_true(LIT(18, 10, 80, 28) > 20, "the word Pair");
	zassert_true(LIT(180, 86, 222, 104) > 20, "the time left");
	save("pairing", "SCR_PAIR, passkey 482 913 from the devices callback, about 50 s left");
	rscr_on_passkey(2, 135790);
	grab();
	b = LIT(18, 34, 150, 74);
	zassert_false(scene_ok(scene_index("pairing"), pic), "another passkey: the digits of the scene are no longer in the frame");
	zassert_true(b > 200, "digits of the second passkey");
	rscr_sync();
	/* the 60 s window runs out */
	calls.pair_cancel = 0;
	run_for(55000);
	rscr_sync();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_MENU, "back to the menu when the window closes: %s", rscr_screen_name(s.screen));
	zassert_true(calls.pair_cancel >= 1, "the window is closed");
}

ZTEST(screens_draw, test_10_charging_and_messages)
{
	struct rscr s;

	run_for(6000);
	rscr_set_battery(64, true, false, 38);
	core_event(RC_EV_VBUS_IN);
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_CHARGING, "charging: %s", rscr_screen_name(s.screen));
	zassert_true(LIT(18, 8, 100, 44) > 100, "64 %% in big digits");
	zassert_true(LIT(18, 48, 110, 70) > 60, "Charging");
	zassert_true(count_px(18, 86, 48, 102, green) > 100, "green battery mark");
	save("charging", "CHARGING, 64 %, 38 min to full (VBUS in)");
	rscr_set_battery(65, true, false, 38);
	grab();
	zassert_false(scene_ok(scene_index("charging"), pic), "a wrong percent fails the charging scene");
	rscr_set_battery(64, true, false, 38);
	rscr_sync();
	/* a long press is refused with the message "In case" */
	joy_long();
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_MESSAGE, "message: %s", rscr_screen_name(s.screen));
	zassert_true(LIT(18, 28, 140, 52) > 60, "In case");
	save("message", "SCR_MESSAGE 'In case' (long press refused in CHARGING)");
	run_for(4000);
	core_event(RC_EV_VBUS_OUT);
	run_for(6000);
	/* a long press at B5: the message 'Battery low' in amber */
	core_battery(RC_BATT_B5);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_BATTERY_LOW, "battery low state");
	joy_long();
	grab();
	zassert_true(count_px(18, 28, 140, 52, amber) > 60, "Battery low in amber: %d", count_px(18, 28, 140, 52, amber));
	save("message-battery-low", "SCR_MESSAGE 'Battery low' (long press at B5)");
}

/* ---- round 2 ---- */

static void reset_to_standby(void)
{
	core_battery(RC_BATT_OK);
	if (rc_core_state(&core) != RC_ST_STANDBY) {
		core_event(RC_EV_VBUS_IN);
		run_for(200);
		core_event(RC_EV_VBUS_OUT);
	}
	run_for(6000);
	rscr_sync();
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY, "back in STANDBY");
}

ZTEST(screens_draw, test_11_sign_start_is_drawn_by_the_screens_thread)
{
	struct rscr_stats rs0, rs1;
	int bad = 0, on_caller = 0;

	reset_to_standby();
	joy_long();
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING, "recording");
	rscr_stats_get(&rs0);
	/* the simulation has one CPU and no preemption between the draw and its caller, so the proof is who writes to the display:
	 * with a draw already asked for (the poke), every rscr_sign_start is answered by the screens thread, never by the caller */
	for (int i = 0; i < 30; i++) {
		rscr_poke();
		bad += rscr_sign_start(t_now()) != 0;
		on_caller += rmd_last_writer() == k_current_get();
	}
	rscr_sync();
	rscr_stats_get(&rs1);
	TC_PRINT("SIGNSTART 30 calls with a draw already asked for, %d errors, %d draws on the caller's thread, draws %u\n", bad,
		 on_caller, rs1.draws - rs0.draws);
	zassert_equal(bad, 0, "every rscr_sign_start returned 0");
	zassert_equal(on_caller, 0, "the display was never written by the caller's thread: the screens thread draws");
	zassert_equal(rs1.draw_errors, rs0.draw_errors, "no refused draw");
	zassert_equal(rs1.sign_missing, 0, "no frame in RECORDING without the sign");
	/* rscr_start failed or the display is not ready: the sign cannot be drawn and the call says so */
	rscr_test_force_down(true);
	zassert_equal(rscr_sign_start(t_now()), -ENODEV, "no screens: -ENODEV");
	rscr_test_force_down(false);
	zassert_equal(rscr_sign_start(t_now()), 0, "and 0 again when they run");
	joy_long();
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY, "stopped");
}

ZTEST(screens_draw, test_12_power_off_is_queued_and_runs_after_the_core_step)
{
	struct rscr s;

	reset_to_standby();
	calls.power_off = 0;
	joy_dir(RC_SW_RIGHT);   /* wake */
	joy_dir(RC_SW_RIGHT);   /* menu */
	for (int i = 0; i < 5; i++) {
		joy_dir(RC_SW_DOWN);
	}
	rscr_snapshot(&s);
	zassert_equal(s.menu_sel, MENU_POWER_OFF, "Power off");
	joy_dir(RC_SW_RIGHT);
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_CONFIRM, "confirm");
	joy_short();   /* Yes */
	rscr_sync();
	zassert_equal(calls.power_off, 1, "Power off was carried out once");
	zassert_true(calls.power_off_thread == rscr_thread_id(),
		     "it ran on the screens thread itself (its id), after the core step returned, not nested inside it");
	zassert_true(calls.power_off_thread != k_current_get(), "and not on the thread that ran the core step");
}

ZTEST(screens_draw, test_13_lock_fact_is_read_when_the_core_needs_it)
{
	reset_to_standby();
	joy_long();
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING, "recording");
	/* the screens thread dims the screen with no core step in between */
	skew += 4000;
	rscr_sync();
	zassert_false(rscr_lock_fact_now(), "SCR_REC_DIM: the fact is false at once, nothing stored is out of date");
	seen_screen_actions = seen_screen_on = seen_mt = 0;
	joy_dir(RC_SW_RIGHT);
	zassert_equal(seen_screen_on, 1, "the first direction from the dimmed screen only turns the screen on");
	zassert_equal(seen_screen_actions, 0, "and is not acted on");
	zassert_equal(seen_mt, 0, "no tick MT (the lock fact as built)");
	zassert_true(rscr_lock_fact_now(), "now lit: the fact is true at once");
	joy_dir(RC_SW_RIGHT);
	zassert_equal(seen_screen_actions, 1, "the second is acted on");
	zassert_equal(seen_mt, 1, "with a tick");
	joy_long();
}

ZTEST(screens_draw, test_14_battery_b15_in_standby_shows_battery_low_for_5s)
{
	struct rscr s;

	reset_to_standby();
	zassert_true(rscr_lock_fact_now() == false, "panel off");
	core_battery(RC_BATT_B15);
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_MESSAGE, "B15: %s", rscr_screen_name(s.screen));
	zassert_equal(s.msg, MSG_BATTERY_LOW, "Battery low");
	zassert_true(count_px(18, 28, 140, 52, amber) > 60, "in amber: %d", count_px(18, 28, 140, 52, amber));
	run_for(4800);
	rscr_sync();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_MESSAGE, "still shown at 4.8 s");
	run_for(400);
	rscr_sync();
	rscr_snapshot(&s);
	zassert_true(s.screen != SCR_MESSAGE, "gone after 5 s");
	core_battery(RC_BATT_OK);
}

static struct vref v_menu5[] = {
	VR("Devices", 16, WHITE, BLK, 22, 19, 196, 0, false, 22, 19, 150, 38),
	VR("Pair device", 16, WHITE, BLK, 22, 49, 196, 0, false, 22, 49, 150, 68),
	VR("Settings", 16, BLK, PILLON, 22, 79, 196, 0, false, 22, 79, 150, 98),
};

ZTEST(screens_draw, test_15_menu_has_five_items_outside_standby)
{
	struct rscr s;

	reset_to_standby();
	core_battery(RC_BATT_B5);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_BATTERY_LOW, "battery low state");
	run_for(6000);
	joy_dir(RC_SW_RIGHT);   /* wake */
	joy_dir(RC_SW_RIGHT);   /* menu */
	for (int i = 0; i < 7; i++) {
		joy_dir(RC_SW_DOWN);
	}
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_MENU, "menu");
	zassert_equal(s.menu_sel, MENU_SETTINGS, "the last item is Settings: Down does not reach a sixth item");
	grab();
	for (unsigned i = 0; i < ARRAY_SIZE(v_menu5); i++) {
		zassert_true(vmatch(pic, &v_menu5[i]), "five-item menu, row %u", i);
	}
	rscr_sync();
	reset_to_standby();
}

ZTEST(screens_draw, test_16_notification_without_a_title_shows_the_word_notification)
{
	static struct vref list_row = VR("Notification", 16, BLK, PILLON, 28, 33, 190, 0, false, 28, 33, 150, 52);
	static struct vref detail_title = VR("Notification", 16, WHITE, BLK, 44, 11, 178, 0, false, 44, 11, 150, 30);
	struct rscr s;

	reset_to_standby();
	put_notif(300, RINBOX_F_NEGATIVE, "com.apple.MobileSMS", "", "Body of a notification with no title");
	rscr_poke();
	joy_dir(RC_SW_UP);   /* wake */
	joy_dir(RC_SW_UP);   /* the list */
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_NOTIFS, "list");
	grab();
	zassert_true(vmatch(pic, &list_row), "list: the word Notification, not the app identifier");
	joy_dir(RC_SW_RIGHT);
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_NOTIF, "detail");
	zassert_true(vmatch(pic, &detail_title), "detail: the word Notification, not the app identifier");
	zassert_equal(rinbox_remove(&inbox, 300), 0, "removed");
	rscr_poke();
	rscr_sync();
}

/* ---- round 3 ---- */

ZTEST(screens_draw, test_17_a_timed_out_sign_start_is_cancelled_and_never_drawn_later)
{
	struct rscr s;
	int rc;

	reset_to_standby();
	rscr_snapshot(&s);
	zassert_true(s.screen != SCR_RECORDING && s.screen != SCR_REC_DIM, "no recording screen while not recording");
	/* hold the draw lock (a test hook): the screens thread cannot draw, so the call times out (the wait is
	 * CONFIG_RING_SCREENS_SIGN_WAIT_MS, set short in prj.conf) */
	rscr_draw_lock();
	rc = rscr_sign_start(t_now());
	zassert_equal(rc, -ETIMEDOUT, "no answer in time: -ETIMEDOUT (%d)", rc);
	rscr_draw_unlock();
	rscr_sync();   /* the thread runs: the cancelled request must not be drawn */
	rscr_snapshot(&s);
	zassert_true(s.screen != SCR_RECORDING && s.screen != SCR_REC_DIM,
		     "no recording screen after the timeout, the ring is not recording: %s", rscr_screen_name(s.screen));
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY, "the core is not recording");
	/* the next call is drawn and returns its own answer */
	{
		struct rmd_stats a, b;

		rmd_stats_get(&a);
		rc = rscr_sign_start(t_now());
		rmd_stats_get(&b);
		zassert_equal(rc, 0, "the next call is drawn and returns 0 (%d)", rc);
		zassert_true(b.writes > a.writes, "it drew");
	}
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_RECORDING, "SCR_RECORDING for the accepted call");
	joy_long();   /* leave the screens as a stop leaves them: start and stop a recording */
	joy_long();
	run_for(6000);
	rscr_sync();
}

ZTEST(screens_draw, test_18_sign_start_on_the_screens_thread_and_under_the_glue_lock_with_a_power_off_queued)
{
	struct rscr s;
	int rc;

	/* (a) on the screens thread: an error at once, no wait (the test runs the call on that thread through a work item) */
	reset_to_standby();
	zassert_equal(rscr_thread_id() != k_current_get(), true, "the test thread is not the screens thread");
	/* the call from the screens thread is made by the screens' own ops: power_off runs there */
	{
		rc = rscr_test_sign_start_from_thread();
		zassert_equal(rc, -EDEADLK, "on the screens thread: -EDEADLK at once (%d)", rc);
	}
	/* (b) the glue's lock is held by the caller (a core step) while a power off is queued: the screens thread must not wait for
	 * that lock; the sign is drawn and the call returns 0 */
	calls.power_off = 0;
	power_off_busy_seen = 0;
	k_mutex_lock(&fake_glue, K_FOREVER);
	joy_dir(RC_SW_RIGHT);   /* wake */
	joy_dir(RC_SW_RIGHT);   /* menu */
	for (int i = 0; i < 5; i++) {
		joy_dir(RC_SW_DOWN);
	}
	joy_dir(RC_SW_RIGHT);   /* confirm */
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_CONFIRM, "confirm");
	joy_short();            /* Yes: the power off is queued, the screens thread cannot take the lock */
	rscr_sync();
	zassert_true(power_off_busy_seen >= 1, "the screens thread found the glue's lock busy and did not wait for it");
	zassert_equal(calls.power_off, 0, "not carried out yet");
	{
		int64_t t0 = k_uptime_get();

		rc = rscr_sign_start(t_now());
		zassert_equal(rc, 0, "under the glue's lock with a power off queued: drawn, 0 (%d)", rc);
		zassert_true(k_uptime_get() - t0 < CONFIG_RING_SCREENS_SIGN_WAIT_MS, "and without the timeout");
	}
	k_mutex_unlock(&fake_glue);
	run_for(100);
	rscr_sync();
	zassert_equal(calls.power_off, 1, "the queued power off runs once the lock is free");
	joy_long();
	joy_long();
	run_for(6000);
	rscr_sync();
}

/* ---- software step 6 (unit U9): the factory frames and the current limit on the display (design/firmware.md 8.7, 9.3) ---- */

/* the real core, from STANDBY into FACTORY_TEST: VBUS in, USB configured, the factory flag set, the factory ENTER */
static void enter_factory(void)
{
	reset_to_standby();
	core_event(RC_EV_VBUS_IN);
	run_for(200);
	core_event(RC_EV_USB_CONFIGURED);
	run_for(200);
	zassert_equal(rc_core_state(&core), RC_ST_TRANSFER, "TRANSFER");
	core.facts.factory_flag = true;
	core_event(RC_EV_FACTORY_ENTER);
	run_for(200);
	zassert_equal(rc_core_state(&core), RC_ST_FACTORY_TEST, "FACTORY_TEST");
	rscr_sync();
}

/* FACTORY_EXIT reboots (BOOT); the start-up then ends in STANDBY with no VBUS and the flag clear */
static void leave_factory(void)
{
	core_event(RC_EV_FACTORY_EXIT);
	run_for(100);
	zassert_equal(rc_core_state(&core), RC_ST_BOOT, "BOOT after FACTORY_EXIT");
	core.facts.vbus = false;
	core.facts.factory_flag = false;
	core_event(RC_EV_INIT_DONE);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY, "STANDBY after the start-up");
	run_for(6000);
	rscr_sync();
}

static int count_rgb(uint8_t r, uint8_t g, uint8_t b)
{
	int n = 0;

	for (int i = 0; i < RSCR_W * RSCR_H; i++) {
		n += pic[i * 3] == r && pic[i * 3 + 1] == g && pic[i * 3 + 2] == b;
	}
	return n;
}

ZTEST(screens_draw, test_factory_colours)
{
	static const struct {
		enum rscr_fac_frame f;
		const char *name;
		uint8_t r, g, b;
	} col[] = {
		{ FAC_RED, "red", 255, 0, 0 }, { FAC_GREEN, "green", 0, 255, 0 }, { FAC_BLUE, "blue", 0, 0, 255 },
		{ FAC_WHITE, "white", 255, 255, 255 }, { FAC_BLACK, "black", 0, 0, 0 },
	};
	struct rmd_stats m;
	struct rscr s;

	enter_factory();
	for (unsigned i = 0; i < ARRAY_SIZE(col); i++) {
		zassert_equal(rscr_factory_frame(col[i].f), 0, "%s accepted", col[i].name);
		grab();
		rscr_snapshot(&s);
		zassert_equal(s.screen, SCR_FACTORY, "on SCR_FACTORY");
		zassert_equal(count_rgb(col[i].r, col[i].g, col[i].b), RSCR_W * RSCR_H, "%s: every one of the 28,800 pixels is (%u, %u, %u), found %d",
			      col[i].name, col[i].r, col[i].g, col[i].b, count_rgb(col[i].r, col[i].g, col[i].b));
		rmd_stats_get(&m);
		zassert_false(m.blanked, "the panel is on for the %s frame", col[i].name);
	}
	/* the grid: white lines of one pixel every 20 pixels from 0 and the last column and row, on black */
	zassert_equal(rscr_factory_frame(FAC_GRID), 0, "grid accepted");
	grab();
	zassert_equal(count_rgb(255, 255, 255), 3149, "13 columns x 120 + 7 rows x 240 - 91 crossings = 3149 white pixels, found %d",
		      count_rgb(255, 255, 255));
	zassert_equal(count_rgb(0, 0, 0), RSCR_W * RSCR_H - 3149, "every other pixel is black, found %d", count_rgb(0, 0, 0));
	for (int x = 0; x < RSCR_W; x++) {
		zassert_equal(pic[(0 * RSCR_W + x) * 3], 255, "first row, x %d", x);
		zassert_equal(pic[((RSCR_H - 1) * RSCR_W + x) * 3], 255, "last row, x %d", x);
	}
	for (int y = 0; y < RSCR_H; y++) {
		zassert_equal(pic[(y * RSCR_W + 0) * 3], 255, "first column, y %d", y);
		zassert_equal(pic[(y * RSCR_W + 20) * 3], 255, "column 20, y %d", y);
		zassert_equal(pic[(y * RSCR_W + (RSCR_W - 1)) * 3], 255, "last column, y %d", y);
	}
	zassert_equal(pic[(10 * RSCR_W + 10) * 3], 0, "inside a cell: black");
	/* back to the plain screen */
	zassert_equal(rscr_factory_frame(FAC_NONE), 0, "plain accepted");
	grab();
	zassert_true(LIT(18, 20, 222, 50) > 20, "the words Factory test");
	zassert_equal(count_rgb(255, 0, 0), 0, "no frame colour is left");
	leave_factory();
}

ZTEST(screens_draw, test_factory_frame_refused_outside_factory)
{
	struct rmd_stats a, b;
	struct rscr s;

	/* STANDBY (the screen is off), CHARGING and TRANSFER: refused, nothing is drawn, nothing is kept */
	reset_to_standby();
	rmd_stats_get(&a);
	zassert_equal(rscr_factory_frame(FAC_RED), -EPERM, "STANDBY: refused");
	rscr_sync();
	rmd_stats_get(&b);
	zassert_equal(b.writes, a.writes, "STANDBY: nothing was written to the display");
	rscr_snapshot(&s);
	zassert_equal(s.fac_frame, FAC_NONE, "STANDBY: no frame kept");
	core_event(RC_EV_VBUS_IN);
	run_for(200);
	zassert_equal(rscr_factory_frame(FAC_GREEN), -EPERM, "CHARGING: refused");
	grab();
	zassert_equal(count_rgb(0, 255, 0), 0, "CHARGING: no green frame");
	core_event(RC_EV_USB_CONFIGURED);
	run_for(200);
	zassert_equal(rc_core_state(&core), RC_ST_TRANSFER, "TRANSFER");
	zassert_equal(rscr_factory_frame(FAC_BLUE), -EPERM, "TRANSFER: refused");
	grab();
	zassert_equal(count_rgb(0, 0, 255), 0, "TRANSFER: no blue frame");
	rscr_snapshot(&s);
	zassert_equal(s.fac_frame, FAC_NONE, "TRANSFER: no frame kept");
	/* RECORDING: refused, the recording picture stays */
	reset_to_standby();
	joy_long();
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING, "recording");
	zassert_equal(rscr_factory_frame(FAC_WHITE), -EPERM, "RECORDING: refused");
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_RECORDING, "RECORDING: still the recording picture");
	zassert_true(count_px(14, 84, 30, 100, red) >= 40, "RECORDING: the red dot is still drawn");
	zassert_equal(count_rgb(255, 255, 255), 0, "RECORDING: no white frame");
	joy_long();
	run_for(6000);
	/* in FACTORY_TEST: a frame is shown; a number outside the list is refused and the frame stays; after the state is left it is gone */
	enter_factory();
	zassert_equal(rscr_factory_frame(FAC_RED), 0, "FACTORY_TEST: accepted");
	zassert_equal(rscr_factory_frame((enum rscr_fac_frame)99), -EPERM, "a frame number outside the list is refused");
	grab();
	zassert_equal(count_rgb(255, 0, 0), RSCR_W * RSCR_H, "the red frame stays");
	leave_factory();
	rscr_snapshot(&s);
	zassert_equal(s.fac_frame, FAC_NONE, "the frame is dropped when FACTORY_TEST is left");
	zassert_equal(rscr_factory_frame(FAC_RED), -EPERM, "after FACTORY_TEST: refused");
	rscr_test_force_down(true);
	zassert_equal(rscr_factory_frame(FAC_RED), -ENODEV, "screens not started: -ENODEV");
	rscr_test_force_down(false);
}

ZTEST(screens_draw, test_ilim_call_reaches_the_display)
{
	struct rmd_stats m0, m1;
	struct rscr_stats rs;
	struct rscr s;

	/* RECORDING: the current limit dims the screen for 10 s, at panel level 85, the red dot stays, the panel is never blanked */
	reset_to_standby();
	joy_long();
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING, "recording");
	run_for(500);
	rmd_stats_get(&m0);
	rscr_ilim_active();
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_REC_DIM, "SCR_REC_DIM at once: %s", rscr_screen_name(s.screen));
	rmd_stats_get(&m1);
	zassert_equal(m1.brightness, 85, "panel level 85: %u", m1.brightness);
	zassert_false(m1.blanked, "not blanked");
	zassert_true(count_px(14, 84, 30, 100, red) >= 40, "the red dot");
	zassert_equal(LIT(0, 0, 239, 80), 0, "nothing above the dot and the timer");
	for (int i = 0; i < 9; i++) {
		run_for(1000);
		grab();
		rscr_snapshot(&s);
		zassert_equal(s.screen, SCR_REC_DIM, "dimmed after %d s", i + 1);
		zassert_true(count_px(14, 84, 30, 100, red) >= 40, "the red dot after %d s", i + 1);
	}
	rmd_stats_get(&m1);
	zassert_equal(m1.blank_on, m0.blank_on, "never blanked in the 10 s (%u)", m1.blank_on - m0.blank_on);
	rscr_stats_get(&rs);
	zassert_equal(rs.sign_missing, 0, "no frame in RECORDING without the sign");
	joy_long();
	run_for(11000);
	/* STANDBY with the screen lit: off at once, the panel blanked */
	reset_to_standby();
	joy_dir(RC_SW_RIGHT);
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_STATUS, "lit");
	rscr_ilim_active();
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_OFF, "off at once");
	rmd_stats_get(&m1);
	zassert_true(m1.blanked, "the panel is blanked");
	run_for(11000);
	rscr_sync();
}

ZTEST(screens_draw, test_sign_start_during_ilim_hold_is_dim_on_the_display)
{
	struct rmd_stats a, b;
	struct rscr s;
	int rc;

	reset_to_standby();
	rscr_ilim_active();
	rscr_sync();
	rmd_stats_get(&a);
	zassert_true(a.blanked, "the hold: the panel is off outside RECORDING");
	rc = rscr_sign_start(t_now());
	zassert_equal(rc, 0, "the sign in the hold is drawn and accepted (%d)", rc);
	rmd_stats_get(&b);
	zassert_true(b.writes > a.writes, "it drew");
	zassert_false(b.blanked, "the panel is on");
	zassert_equal(b.brightness, 85, "panel level 85: %u", b.brightness);
	grab();
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_REC_DIM, "SCR_REC_DIM: %s", rscr_screen_name(s.screen));
	zassert_true(count_px(14, 84, 30, 100, red) >= 40, "the red dot is in the frame");
	zassert_equal(LIT(0, 0, 239, 80), 0, "dimmed picture: nothing above the dot and the timer");
	joy_long();   /* the core starts the recording: the screen stays dimmed in the hold */
	grab();
	rscr_snapshot(&s);
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING, "recording");
	zassert_equal(s.screen, SCR_REC_DIM, "still SCR_REC_DIM in RECORDING: %s", rscr_screen_name(s.screen));
	joy_long();
	run_for(11000);
	rscr_sync();
}

static void stack_cb(const struct k_thread *t, void *u)
{
	size_t unused = 0;
	const char *n = k_thread_name_get((k_tid_t)t);

	ARG_UNUSED(u);
	if (k_thread_stack_space_get(t, &unused) == 0) {
		printk("MEMORY STACK %s: size %u, used at most %u\n", n != NULL && n[0] != 0 ? n : "(no name)",
		       (unsigned)t->stack_info.size, (unsigned)(t->stack_info.size - unused));
	}
}

ZTEST(screens_draw, test_99_cross_check_and_memory)
{
	static uint8_t blank[RSCR_W * RSCR_H * 3];
	static uint8_t whitef[RSCR_W * RSCR_H * 3];
	int own = 0, blank_fail = 0, white_fail = 0, others_fail = 0, others = 0;

	memset(whitef, 0xFF, sizeof(whitef));
	for (unsigned i = 0; i < NSCENES; i++) {
		zassert_true(scene_have[i], "scene %s was captured", scenes[i].name);
	}
	for (unsigned i = 0; i < NSCENES; i++) {
		own += scene_ok((int)i, scene_pic[i]) ? 1 : 0;
		blank_fail += scene_ok((int)i, blank) ? 0 : 1;
		white_fail += scene_ok((int)i, whitef) ? 0 : 1;
		for (unsigned j = 0; j < NSCENES; j++) {
			if (i != j) {
				others++;
				others_fail += scene_ok((int)i, scene_pic[j]) ? 0 : 1;
			}
		}
	}
	TC_PRINT("CROSSCHECK scenes %u: own frame passes %d of %u; blank frame fails %d of %u; white frame fails %d of %u; "
		 "other scenes' frames fail %d of %d\n",
		 (unsigned)NSCENES, own, (unsigned)NSCENES, blank_fail, (unsigned)NSCENES, white_fail, (unsigned)NSCENES,
		 others_fail, others);
	zassert_equal(own, (int)NSCENES, "every scene passes its own frame");
	zassert_equal(blank_fail, (int)NSCENES, "every scene fails a blank frame");
	zassert_equal(white_fail, (int)NSCENES, "every scene fails a full white frame");
	zassert_equal(others_fail, others, "every scene fails the frame of each of the other scenes");
	rscr_sync();
	printk("MEMORY LVGL pool peak %u bytes over the picture test\n", rscr_draw_pool_peak());
	k_thread_foreach(stack_cb, NULL);
}

ZTEST_SUITE(screens_draw, NULL, suite_setup, NULL, NULL, NULL);
