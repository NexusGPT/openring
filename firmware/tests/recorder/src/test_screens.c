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

/* SCR_CHARGING after a boot with VBUS (row 5) on a set world: 1,000 µAh cell at 50.0 % (gauge start 500), charging at
 * 1 mA (samples of -1,000 µA), the charger's state as given (0 = its own: constant current with VBUS) */
static uint64_t charging_screen(uint8_t chg_forced)
{
	struct rt_boot b = { .vbus = true, .mv = 3900, .ua = -1000, .gauge_uah = 1000, .soc_x10 = 500,
			     .chg_forced = chg_forced };
	struct rscr s;

	rt_fresh(&b);
	zassert_equal(rt_state(), RC_ST_CHARGING, "CHARGING (row 5)");
	rt_sleep(1500);   /* the battery values reach the screens once a second (rscr_set_battery) */
	rscr_snapshot(&s);
	zassert_equal(s.screen, SCR_CHARGING, "SCR_CHARGING for 5 s after insertion (FW l.103)");
	return frame_hash();
}

/* the same screen drawn from values the test gives the screens itself */
static uint64_t ref_screen(uint8_t pct, bool charging, bool full, uint16_t to_full_min)
{
	rscr_set_battery(pct, charging, full, to_full_min);
	return frame_hash();
}

/* FW l.374 (C39, review finding R6-14): SCR_CHARGING shows "battery % and icon, "Charging" or "Full", time to full in
 * minutes from the fuel gauge". The values the screen received are those typed here: the picture the join's values drew
 * equals the picture of the typed values, and differs when any one of them differs. */
ZTEST(recorder_screens, test_battery_reaches_screens)
{
	/* 50 % (gauge 500 = 50.0 %); "Charging" (constant current with VBUS); time to full 30 min [CALC: 1,000 µAh x
	 * (1,000 - 500) / 1,000 at 1 mA = 0.5 h = 30 min] */
	uint64_t a = charging_screen(0);
	uint64_t ok = ref_screen(50, true, false, 30);
	uint64_t ttf31 = ref_screen(50, true, false, 31);
	uint64_t pct51 = ref_screen(51, true, false, 30);
	uint64_t full = ref_screen(50, false, true, 30);
	uint64_t f, f_ok, f_chg;

	TC_PRINT("SCR_CHARGING frames: from the join %016llx; typed 50 %% Charging 30 min %016llx, 31 min %016llx, 51 %% "
		 "%016llx, Full %016llx\n", a, ok, ttf31, pct51, full);
	zassert_equal(a, ok, "the screen received 50 %%, Charging, 30 min");
	zassert_not_equal(a, ttf31, "the time to full is in the picture");
	zassert_not_equal(a, pct51, "the percent is in the picture");
	zassert_not_equal(a, full, "Charging, not Full");
	/* "Full": the charger reports charging completed (RREC_CHG_FULL) */
	f = charging_screen(RREC_CHG_FULL + 1);
	f_ok = ref_screen(50, false, true, 30);
	f_chg = ref_screen(50, true, false, 30);
	TC_PRINT("SCR_CHARGING frames (full): from the join %016llx; typed 50 %% Full %016llx, Charging %016llx\n", f, f_ok,
		 f_chg);
	zassert_equal(f, f_ok, "the screen received 50 %%, Full");
	zassert_not_equal(f, f_chg, "Full, not Charging");
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
