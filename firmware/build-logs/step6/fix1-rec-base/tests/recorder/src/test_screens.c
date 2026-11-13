/*
 * recorder_screens: what the join gives the screens part (plan rows C39, P18 the join's part, and the ruling "a recording
 * started during the 10 s current-limit hold draws the dim sign").
 */
#include <string.h>

#include "rt.h"

static uint8_t frame[RSCR_W * RSCR_H * 3];

static uint64_t frame_hash(void)
{
	uint64_t h = 0xcbf29ce484222325ull;

	rscr_sync();
	rscr_capture_rgb(frame);
	for (size_t i = 0; i < sizeof(frame); i++) {
		h = (h ^ frame[i]) * 0x100000001b3ull;
	}
	return h;
}

static uint64_t charging_screen(uint16_t soc_x10)
{
	struct rt_boot b = { .soc_x10 = soc_x10 };
	struct rscr s;

	rt_fresh(&b);
	rt_vbus(true);
	rt_sleep(1500);   /* the battery values reach the screens once a second (rscr_set_battery) */
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_CHARGING, "SCR_CHARGING for 5 s after insertion (FW l.103)");
	return frame_hash();
}

/* FW l.374: SCR_CHARGING shows the battery from the gauge (C39): the same gauge value draws the same frame, another value
 * another frame */
ZTEST(recorder_screens, test_battery_reaches_screens)
{
	uint64_t a1 = charging_screen(623);
	uint64_t a2 = charging_screen(623);
	uint64_t b1 = charging_screen(412);

	TC_PRINT("SCR_CHARGING frame hash: 62.3 %% %016llx, again %016llx, 41.2 %% %016llx\n", a1, a2, b1);
	zassert_equal(a1, a2, "the same gauge value, the same picture");
	zassert_not_equal(a1, b1, "another gauge value, another picture: the value reaches the screen");
}

/* FW l.990 to l.995: the current limit reads ACTIVE in RECORDING: SCR_REC_DIM 10 s, never dark, the recording goes on,
 * no motor pattern (P18, the join's part: the power part's callback reaches rscr_ilim_active) */
ZTEST(recorder_screens, test_ilim_dims_in_recording)
{
	struct rmd_stats m;
	struct rscr s;
	uint32_t pats;

	rt_fresh(NULL);
	rt_long();
	rt_sleep(4000);   /* SCR_REC_DIM by the idle rule already; give one input to show the full picture */
	rglue_input(RC_SW_RIGHT, true);
	rt_sleep(60);
	rglue_input(RC_SW_RIGHT, false);
	rt_sleep(200);
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_RECORDING, "the full picture after an input");
	pats = rrec_tap_count_code(RREC_LOG_MOTOR_PATTERN);
	rhw_sim_pmic_ilim_at_sample(1);   /* the next 1 s sample reads ACTIVE */
	rt_sleep(1200);
	rscr_snapshot(&s);
	rmd_stats_get(&m);
	zassert_equal(s.screen, SCR_REC_DIM, "SCR_REC_DIM (FW l.992): %s", rscr_screen_name(s.screen));
	zassert_false(m.blanked, "never dark");
	zassert_equal(m.brightness, 85, "panel level 85 (FW l.341)");
	zassert_true(rt_red_dot(), "the red dot");
	zassert_equal(rt_state(), RC_ST_RECORDING, "nothing closed (FW l.993)");
	zassert_true(rt_mic(), "VDD_MIC on");
	zassert_equal(rrec_tap_count_code(RREC_LOG_MOTOR_PATTERN), pats, "no motor pattern for it (FW l.994)");
	zassert_true(rrec_tap_count_code(RREC_LOG_ILIM_ACTIVE) >= 1, "logged (FW l.991)");
	rt_long();
}

/* ruling (screens unit, reading 2): a recording started during the 10 s hold draws SCR_REC_DIM as its sign */
ZTEST(recorder_screens, test_start_during_ilim_hold_is_dim)
{
	struct rmd_stats m;
	struct rscr s;

	rt_fresh(NULL);
	rt_short();   /* the screen on */
	rscr_ilim_active();   /* the power part's call (the hold of 10 s) */
	rt_sleep(500);
	rt_long();
	zassert_equal(rt_state(), RC_ST_RECORDING, "recording");
	zassert_true(rt_mic(), "VDD_MIC on");
	rscr_snapshot(&s);
	rmd_stats_get(&m);
	zassert_equal(s.screen, SCR_REC_DIM, "the dim sign: %s", rscr_screen_name(s.screen));
	zassert_false(m.blanked, "not blanked");
	zassert_true(rt_red_dot(), "the red dot");
	rt_long();
}

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_screens, NULL, setup, NULL, NULL, NULL);
