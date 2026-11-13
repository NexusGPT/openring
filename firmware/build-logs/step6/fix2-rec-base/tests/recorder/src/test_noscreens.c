/*
 * recorder_a_noscreens: ship mode when the screens part never started (step 6 fix round 1, lead's ruling 4 on the open
 * point of rscr_sync() without a time limit). The suite's name sorts first, so ztest runs it before every suite that
 * starts the screens (rt_setup); the case checks that the screens were indeed never started.
 */
#include "rt.h"

/* FW l.151, l.936 to l.941: the menu's power off goes through all of ship mode although no screens thread exists */
ZTEST(recorder_a_noscreens, test_ship_without_screens_ends)
{
	int64_t t0;

	zassert_false(rt_screens_started, "this case runs before any suite started the screens part");
	rt_fresh(NULL);
	rhw_sim_log_clear();
	t0 = k_uptime_get();
	rglue_event(RC_EV_MENU_POWER_OFF);
	rt_settle();
	TC_PRINT("ship without screens: idle %d, SHPHLDCONFIG at %d, ship task at %d, %lld ms\n", rrec_idle(),
		 rt_find(RHW_EV_PMIC_SHPHLD_CFG, -1, -1, 0), rt_find(RHW_EV_PMIC_SHIP, -1, -1, 0), k_uptime_get() - t0);
	zassert_true(rrec_idle(), "ship mode ended (the recorder's thread is free)");
	zassert_true(rt_find(RHW_EV_PMIC_SHPHLD_CFG, -1, -1, 0) >= 0, "SHPHLDCONFIG written (FW l.938)");
	zassert_true(rhw_sim_shipped(), "the ship task written (FW l.940)");
}

static void *setup(void)
{
	rt_setup_no_screens();
	return NULL;
}

ZTEST_SUITE(recorder_a_noscreens, NULL, setup, NULL, NULL, NULL);
