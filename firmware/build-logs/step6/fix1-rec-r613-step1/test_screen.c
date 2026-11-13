/* Suite factory_screen (software step 6, unit U8): T-SCREEN (0x20, FW l.1025): full red, green, blue, white, black, 1 s
 * each, then a grid. Rows T14. test_frame_sequence: the order and the 1 s spacing, on the ops stand-in. 
 * test_frames_reach_display (scenario ring_factory.screen only, FACTORY_SCREEN=ON): the real screens part
 * (rscr_factory_frame of decision D7, unit U9) on the memory display: the frame the display received is read back after
 * each frame and its pixels are counted. The camera is the jig's (not provable here). */
#include "common.h"

#if defined(CONFIG_RING_SCREENS)
#include <ring_core/rc_core.h>
#include <ring_screens/rmd.h>
#include <ring_screens/rscr.h>
#include <ring_screens/rscr_logic.h>

/* ---- the other modules behind struct rscr_ops, as empty stubs (the screens part asks for nothing in FACTORY_TEST) */
static struct rc_core core;
static int64_t skew;

static int64_t t_now(void)
{
	return k_uptime_get() + skew;
}

static uint8_t o_inbox_count(void)
{
	return 0;
}

static bool o_inbox_get(uint8_t i, struct rinbox_item *o)
{
	ARG_UNUSED(i);
	ARG_UNUSED(o);
	return false;
}

static void o_media_get(struct ripl_media *o)
{
	memset(o, 0, sizeof(*o));
}

static bool o_false(void)
{
	return false;
}

static uint8_t o_zero8(void)
{
	return 0;
}

static int o_uid(uint32_t uid)
{
	ARG_UNUSED(uid);
	return 0;
}

static int o_slot(uint8_t slot)
{
	ARG_UNUSED(slot);
	return 0;
}

static void o_void(void)
{
}

static void o_bool(bool on)
{
	ARG_UNUSED(on);
}

static void o_mode(enum rctl_mode m)
{
	ARG_UNUSED(m);
}

static int o_int(void)
{
	return 0;
}

static const struct rscr_ops sops = {
	.inbox_count = o_inbox_count, .inbox_get = o_inbox_get, .media_get = o_media_get, .ams_ready = o_false,
	.paired_mask = o_zero8, .active = o_zero8, .link_up = o_false, .dismiss = o_uid, .positive = o_uid,
	.mark_read = o_uid, .pair_open = o_slot, .pair_cancel = o_void, .dev_use = o_slot, .dev_remove = o_slot,
	.control_active = o_bool, .set_mode = o_mode, .power_off = o_int, .vibration = o_bool, .now_ms = t_now,
};

/* the glue's part: the screens' entry after every core step, and the lock fact before it */
static void after(struct rc_actions *a)
{
	enum rc_event last = a->last_row > 0 ? rscr_row_event(a->last_row) : RC_EV_COUNT;

	(void)rscr_glue_after(a, last, rc_core_state(&core), t_now());
}

static void core_event(enum rc_event ev)
{
	struct rc_actions a;

	rc_actions_clear(&a);
	core.facts.screen_on = rscr_lock_fact_now();
	rc_core_event(&core, ev, t_now(), &a);
	after(&a);
}

static void run_for(int ms)
{
	int64_t end = t_now() + ms;

	for (int64_t t = t_now() + 50; t <= end; t += 50) {
		struct rc_actions a;

		skew += 50;
		rc_actions_clear(&a);
		core.facts.screen_on = rscr_lock_fact_now();
		rc_core_tick(&core, t, &a);
		after(&a);
	}
}

static void *screen_setup(void)
{
	static bool started;

	if (!started) {
		rc_core_init(&core, RC_CENTRE_SW2, RC_ST_STANDBY, 0);
		zassert_equal(rscr_start(&sops), 0, "screens start (LVGL on the memory display)");
		started = true;
	}
	return NULL;
}

/* the frame the display received, and what the stand-in saw of each frame */
static uint8_t pic[RSCR_W * RSCR_H * 3];
static int white[6], black[6], red[6], green[6], blue[6];
static int frames_taken;
static bool first_row_white[6], first_col_white[6];

static int count_rgb(uint8_t r, uint8_t g, uint8_t b)
{
	int n = 0;

	for (int i = 0; i < RSCR_W * RSCR_H; i++) {
		n += pic[i * 3] == r && pic[i * 3 + 1] == g && pic[i * 3 + 2] == b;
	}
	return n;
}

/* the join's T-SCREEN call: rfa.h's number 0 to 5 is enum rscr_fac_frame minus one (FAC_RED to FAC_GRID); after the
 * call the screens thread has drawn and the display holds the frame */
static int real_frame(uint8_t which)
{
	int rc = rscr_factory_frame((enum rscr_fac_frame)(which + 1));

	if (rc != 0) {
		return rc;
	}
	rscr_sync();
	rscr_capture_rgb(pic);
	red[which] = count_rgb(255, 0, 0);
	green[which] = count_rgb(0, 255, 0);
	blue[which] = count_rgb(0, 0, 255);
	white[which] = count_rgb(255, 255, 255);
	black[which] = count_rgb(0, 0, 0);
	bool row = true, col = true;

	for (int x = 0; x < RSCR_W; x++) {
		row &= pic[x * 3] == 255 && pic[x * 3 + 1] == 255 && pic[x * 3 + 2] == 255;
	}
	for (int y = 0; y < RSCR_H; y++) {
		col &= pic[(y * RSCR_W) * 3] == 255 && pic[(y * RSCR_W) * 3 + 1] == 255;
	}
	first_row_white[which] = row;
	first_col_white[which] = col;
	fx_screen_frame(which); /* the time of each frame */
	frames_taken++;
	return 0;
}
#else
static void *screen_setup(void)
{
	return NULL;
}
#endif

ZTEST_SUITE(factory_screen, NULL, screen_setup, fx_before, fx_after, NULL);

ZTEST(factory_screen, test_frame_sequence)
{
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;

	zassert_equal(fx_do1(0x20, true, out, &n, &eff), 0);
	zassert_equal(n, 1);
	zassert_equal(out[0], 0);
	/* red 0, green 1, blue 2, white 3, black 4, grid 5 (rfa.h), 1 s apart */
	for (uint32_t i = 0; i < fx_frames && i < FX_MAX_FRAMES; i++) {
		TC_PRINT("T-SCREEN stamps: frame %u at %lld ms, %lld ticks (%u ticks/s), spacing %lld ms\n", i, fx_frame_ms[i],
			 fx_frame_ticks[i], (unsigned)CONFIG_SYS_CLOCK_TICKS_PER_SEC, i > 0 ? fx_frame_ms[i] - fx_frame_ms[i - 1] : 0);
	}
	zassert_equal(fx_frames, 6);
	for (uint32_t i = 0; i < 6; i++) {
		zassert_equal(fx_frame[i], i, "frame %u", i);
		if (i > 0) {
			zassert_equal(fx_frame_ms[i] - fx_frame_ms[i - 1], 1000, "1 s each (FW l.1025)");
		}
	}
	/* a refused frame ends the test with a fail */
	fx_frames = 0;
	fx_screen_rc = -EIO;
	zassert_equal(fx_do1(0x20, true, out, &n, &eff), 0);
	zassert_equal(out[0], 1);
	zassert_equal(fx_frames, 1, "the first refusal ends the test");
}

#if defined(CONFIG_RING_SCREENS)
/* T14: T-SCREEN on the real screens part: every one of the 240 x 120 = 28,800 pixels is the colour (FW l.1025: full red,
 * green, blue, white, black), then a grid with lit lines on black whose first row and first column are lit (no dead edge). */
ZTEST(factory_screen, test_frames_reach_display)
{
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;
	struct rmd_stats m;

	/* the real core, from STANDBY into FACTORY_TEST: VBUS in, USB configured, the flag, the factory ENTER */
	core_event(RC_EV_VBUS_IN);
	run_for(200);
	core_event(RC_EV_USB_CONFIGURED);
	run_for(200);
	zassert_equal(rc_core_state(&core), RC_ST_TRANSFER);
	core.facts.factory_flag = true;
	core_event(RC_EV_FACTORY_ENTER);
	run_for(200);
	zassert_equal(rc_core_state(&core), RC_ST_FACTORY_TEST, "FACTORY_TEST");
	rscr_sync();

	fx_ops.screen_frame = real_frame;
	zassert_ok(rfa_init(&fx_ops));
	frames_taken = 0;
	fx_frames = 0;
	zassert_equal(fx_do1(0x20, true, out, &n, &eff), 0);
	fx_ops.screen_frame = fx_screen_frame;
	zassert_ok(rfa_init(&fx_ops));
	zassert_equal(out[0], 0, "pass");
	zassert_equal(frames_taken, 6, "six frames reached the display");
	zassert_equal(red[0], RSCR_W * RSCR_H, "red: every pixel (255, 0, 0), found %d", red[0]);
	zassert_equal(green[1], RSCR_W * RSCR_H, "green: every pixel (0, 255, 0), found %d", green[1]);
	zassert_equal(blue[2], RSCR_W * RSCR_H, "blue: every pixel (0, 0, 255), found %d", blue[2]);
	zassert_equal(white[3], RSCR_W * RSCR_H, "white: every pixel (255, 255, 255), found %d", white[3]);
	zassert_equal(black[4], RSCR_W * RSCR_H, "black: every pixel (0, 0, 0), found %d", black[4]);
	/* the grid: lit and dark pixels, edges lit */
	zassert_true(white[5] > 1000 && black[5] > 1000, "grid: %d white, %d black pixels", white[5], black[5]);
	zassert_true(first_row_white[5] && first_col_white[5], "the grid's first row and first column are lit");
	zassert_equal(red[5] + green[5] + blue[5], 0, "no colour in the grid");
	for (int i = 1; i < 6; i++) {
		/* 1 s each (FW l.1025), plus the time the screens thread takes to draw and the read-back */
		zassert_true(fx_frame_ms[i] - fx_frame_ms[i - 1] >= 1000 && fx_frame_ms[i] - fx_frame_ms[i - 1] <= 1200,
			     "frame %d came %lld ms after the one before", i, fx_frame_ms[i] - fx_frame_ms[i - 1]);
	}
	rmd_stats_get(&m);
	zassert_false(m.blanked, "the panel is on");
	core_event(RC_EV_FACTORY_EXIT);
	run_for(100);
}
#endif
