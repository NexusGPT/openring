/*
 * recorder_sign1: test SIGN-1 of design/firmware.md l.344 (plan rows C36, C38). Every row of FW 1.2 from its From state on
 * the real screens part (memory display): after the row and at every 100 ms tick of a 10 s idle run, VDD_MIC on means
 * the display is not blanked and the frame holds the red dot. A forced draw failure at the start leaves VDD_MIC off.
 * OLED_PWR_EN is not part of it: the memory display has none (not provable here).
 */
#include "rt.h"

ZTEST(recorder_sign1, test_sign1_every_row)
{
	int bad_rows = 0, skipped = 0, on_ticks = 0;

	for (int row = 1; row <= 72; row++) {
		int bad = 0;

		if (rt_run_row(row) == -ENOTSUP) {
			skipped++;
			TC_PRINT("SIGN-1 ROW %d: NOT RUN (needs the factory part)\n", row);
			continue;
		}
		for (int tick = 0; tick <= 100; tick++) {
			if (rt_mic()) {
				bool blank = rt_blanked();
				bool dot = rt_red_dot();

				on_ticks++;
				if (blank || !dot) {
					if (bad < 3) {
						TC_PRINT("SIGN-1 ROW %d tick %d: VDD_MIC on, blanked %d, red dot %d (%s)\n", row,
							 tick, blank, dot, rc_state_name(rt_state()));
					}
					bad++;
				}
			}
			rt_sleep(100);
		}
		TC_PRINT("SIGN-1 ROW %d: %s\n", row, bad == 0 ? "ok" : "FAILED");
		bad_rows += bad != 0 ? 1 : 0;
		rt_row_cleanup(row);
	}
	TC_PRINT("SIGN-1: 72 rows, %d not run, %d failed, %d ticks with VDD_MIC on checked\n", skipped, bad_rows, on_ticks);
	zassert_equal(bad_rows, 0, "SIGN-1 failed in %d rows", bad_rows);
	zassert_true(on_ticks > 0, "the check met VDD_MIC on (a test that never sees it proves nothing)");
}

ZTEST(recorder_sign1, test_forced_draw_failure)
{
	rt_fresh(NULL);
	rhw_sim_log_clear();
	rmd_inject_fail(-1);   /* every display write refused */
	rt_long();
	rmd_inject_fail(0);
	zassert_true(rt_row_seen(16), "row 16: the sign not drawn (FW l.148)");
	zassert_equal(rt_state(), RC_ST_STANDBY, "no recording");
	zassert_equal(rt_count_rail(RHW_RAIL_MIC, true), 0, "VDD_MIC never on");
	zassert_false(rt_mic(), "VDD_MIC off");
}

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_sign1, NULL, setup, NULL, NULL, NULL);
