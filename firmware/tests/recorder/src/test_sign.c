/*
 * recorder_sign: rule R-SIGN and the one microphone path (design/firmware.md l.342, l.457; plan rows C10, C11, C27,
 * C37). The screens part is the real one on the memory display.
 */
#include <string.h>

#include "rt.h"

static int64_t unlocked_us;
static K_SEM_DEFINE(hold_go, 0, 1);

static void holder(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);
	for (;;) {
		k_sem_take(&hold_go, K_FOREVER);
		rscr_draw_lock();
		k_sleep(K_MSEC(300));
		unlocked_us = k_ticks_to_us_floor64(k_uptime_ticks());
		rscr_draw_unlock();
	}
}

K_THREAD_DEFINE(sign_holder, 2048, holder, NULL, NULL, NULL, 2, 0, 0);

/* FW l.342, l.457: rec_mics_on() has the sign drawn first and enables VDD_MIC only on an answer of 0 (C10, C27) */
ZTEST(recorder_sign, test_start_draws_sign_before_mic)
{
	int32_t i_on;
	int r;

	rt_fresh(NULL);
	/* (a) the screens cannot draw for 300 ms: VDD_MIC must not come on before the sign is drawn */
	rhw_sim_log_clear();
	unlocked_us = -1;
	k_sem_give(&hold_go);
	k_sleep(K_MSEC(10));
	r = rec_mics_on(k_uptime_get());
	i_on = rt_find_rail(RHW_RAIL_MIC, true, 0);
	TC_PRINT("sign held by the draw lock until %lld us; rec_mics_on answered %d; VDD_MIC on at %lld us\n", unlocked_us, r,
		 rt_ev_us(i_on));
	zassert_equal(r, 0, "the sign was drawn once the screens could draw");
	zassert_true(i_on >= 0, "VDD_MIC on");
	zassert_true(unlocked_us >= 0 && rt_ev_us(i_on) >= unlocked_us, "VDD_MIC on only after the sign could be drawn");
	(void)rec_mics_off();
	/* (b) a start by the long press: the red dot is on the display and VDD_MIC on */
	rt_fresh(NULL);
	rt_long();
	zassert_equal(rt_state(), RC_ST_RECORDING, "recording");
	zassert_true(rt_mic(), "VDD_MIC on");
	zassert_false(rt_blanked(), "the display is not blanked");
	zassert_true(rt_red_dot(), "the red dot");
	rt_long();
}

/* FW l.148: the sign not drawn: no recording, VDD_MIC stays off, M3, event log record (C11) */
ZTEST(recorder_sign, test_sign_refused_no_mic_m3_log)
{
	struct rrec_tap_rec t;
	bool m3 = false;

	zassert_equal(rt_run_row(16), 0, NULL);   /* the screens part refuses (rscr_test_force_down) */
	rscr_test_force_down(false);
	zassert_true(rt_row_seen(16), "row 16");
	zassert_equal(rt_state(), RC_ST_STANDBY, "STANDBY");
	zassert_equal(rt_count_rail(RHW_RAIL_MIC, true), 0, "VDD_MIC never switched on");
	zassert_false(rrec_st.recording, "no recording");
	for (uint32_t k = 0; rrec_tap_get(k, &t); k++) {
		m3 |= t.code == RREC_LOG_MOTOR_PATTERN && t.args[0] == RREC_PAT_M3;
	}
	zassert_true(m3, "M3");
	zassert_equal(rrec_tap_count_code(RREC_LOG_SIGN_REFUSED), 1, "one event log record");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_DISK_INIT), 1, "storage not opened for it (only the boot mount)");
}

/* FW l.342: rec_mics_on() is the only code that enables VDD_MIC (C37): every VDD_MIC-on write names it */
ZTEST(recorder_sign, test_only_rec_mics_on_enables_mic)
{
	struct rhw_sim_ev e;
	int ons = 0, others = 0;

	rt_fresh(NULL);
	rt_long();
	rt_short();
	rt_sleep(500);
	rt_long();
	rt_long();
	rt_vbus(true);
	for (uint32_t i = 0; rhw_sim_log_get(i, &e); i++) {
		if (e.kind == RHW_EV_PMIC_RAIL && e.a0 == RHW_RAIL_MIC && e.a1 == 1) {
			ons++;
			if (strcmp(e.caller, "rec_mics_on") != 0) {
				others++;
				TC_PRINT("VDD_MIC on by %s\n", e.caller);
			}
		}
	}
	zassert_equal(ons, 2, "two starts, two VDD_MIC on (%d)", ons);
	zassert_equal(others, 0, "only rec_mics_on");
	zassert_equal(strcmp(rhw_sim_pmic_rail_caller(RHW_RAIL_MIC), "rec_mics_off"), 0, "the last write is the off twin");
}

/* FW l.342, l.463: the close turns VDD_MIC off before the screen may leave the recording pictures (C37) */
ZTEST(recorder_sign, test_close_mic_off_before_screen_leaves)
{
	uint32_t told;

	rt_fresh(NULL);
	rt_long();
	rt_sleep(800);
	rt_steps_clear();
	rt_long();
	told = rt_screens_told();
	TC_PRINT("stop: the screens were told %u times, %u of them with VDD_MIC on outside RECORDING\n", told,
		 rt_mic_at_screens());
	zassert_true(told > 0, "the screens learned of the stop");
	zassert_equal(rt_mic_at_screens(), 0, "VDD_MIC was off whenever the screens learned of a state other than RECORDING");
	/* the same for the other closes: VBUS during a recording, a microphone fault */
	rt_fresh(NULL);
	rt_long();
	rt_steps_clear();
	rt_vbus(true);
	zassert_equal(rt_mic_at_screens(), 0, "VBUS close");
	zassert_equal(rt_run_row(37), 0, NULL);
	zassert_equal(rt_mic_at_screens(), 0, "microphone fault close");
}

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_sign, NULL, setup, NULL, NULL, NULL);
