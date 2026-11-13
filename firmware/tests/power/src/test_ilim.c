/* Suite power_ilim (software step 6, unit U5): the battery current limit status (FW l.990 to l.995). Row P18.
 * The screen is the join's: this unit tells it ("first" or "again"), logs, and does nothing else (no motor, nothing
 * closed, nothing refused). */
#include "common.h"

ZTEST_SUITE(power_ilim, NULL, NULL, pw_before, NULL, NULL);

static uint32_t le32(const uint8_t *p)
{
	return p[0] | (p[1] << 8) | (p[2] << 16) | ((uint32_t)p[3] << 24);
}

/* FW l.991 to l.995: the first ACTIVE reading: one record (battery mV, state, screen on, count), the callback with
 * first = true; no motor pattern, no rail change, no level or VBUS report: nothing closed, nothing refused. */
ZTEST(power_ilim, test_first_active)
{
	int64_t t0;

	pw_script1(3777, 0);
	rpw_state(RC_ST_RECORDING);
	t0 = k_uptime_get();
	pw_start();
	rhw_sim_log_clear();
	rhw_sim_pmic_ilim_at_sample(1);     /* the next sample (sample 2) reads ACTIVE */
	pw_sleep_until(t0 + 1500);
	zassert_equal(cap.n_ilim, 1, "one callback");
	zassert_true(cap.ilim[0].first, "first reading of a run");
	zassert_equal(cap.ilim[0].mv, 3777);
	zassert_equal(cap.ilim[0].count, 1);
	zassert_equal(pw_log_count(RREC_LOG_ILIM_ACTIVE), 1, "one record");
	zassert_equal(cap.log[0].code, 0x0210);
	zassert_equal(cap.log[0].n, 8);
	zassert_equal(cap.log[0].args[0] | (cap.log[0].args[1] << 8), 3777, "battery mV");
	zassert_equal(cap.log[0].args[2], RC_ST_RECORDING, "the state");
	zassert_equal(cap.log[0].args[3], 1, "the screen was on");
	zassert_equal(le32(&cap.log[0].args[4]), 1, "count 1");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_MOTOR), 0, "no motor pattern (FW l.995)");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_RAIL), 0, "no rail changed");
	zassert_equal(cap.n_level, 0, "nothing closed or refused: no level change");
	zassert_equal(cap.n_vbus, 0);
	/* a later sample that reads not active adds nothing */
	pw_sleep_until(t0 + 2500);
	zassert_equal(cap.n_ilim, 1);
	zassert_equal(pw_log_count(RREC_LOG_ILIM_ACTIVE), 1);
}

/* FW l.995: ACTIVE again with the screen already off: logged once more with a count, nothing else. The screen is off
 * for 10 s (RREC_ILIM_SCREEN_MS); a reading after that starts a new run. Samples come at t0 + j s; ACTIVE at j = 1,
 * 2, 3 and 12. */
ZTEST(power_ilim, test_again_with_screen_off)
{
	int64_t t0;

	pw_script1(3800, 0);
	rpw_state(RC_ST_RECORDING);
	t0 = k_uptime_get();
	pw_start();
	for (uint32_t j = 1; j <= 12; j++) {
		if (j <= 3 || j == 12) {
			rhw_sim_pmic_ilim_at_sample(1);
		}
		pw_sleep_until(t0 + (int64_t)j * 1000 + 500);
	}
	zassert_equal(cap.n_ilim, 4);
	zassert_true(cap.ilim[0].first && cap.ilim[0].count == 1);
	zassert_true(!cap.ilim[1].first && cap.ilim[1].count == 2, "again, count 2");
	zassert_true(!cap.ilim[2].first && cap.ilim[2].count == 3, "again, count 3");
	zassert_true(cap.ilim[3].first && cap.ilim[3].count == 1, "11 s later: the screen is on again, a new run");
	zassert_equal(pw_log_count(RREC_LOG_ILIM_ACTIVE), 4);
	/* the record of an "again" reading: screen off (0), count 2 */
	zassert_equal(cap.log[1].code, 0x0210);
	zassert_equal(cap.log[1].args[3], 0, "the screen was already off");
	zassert_equal(le32(&cap.log[1].args[4]), 2);
	zassert_equal(le32(&cap.log[2].args[4]), 3);
	zassert_equal(cap.log[3].args[3], 1);
	zassert_equal(cap.n_level, 0, "nothing else changes");
}

/* The edge of the 10 s: 9,999 ms is still "again", 10,000 ms starts a new run. */
ZTEST(power_ilim, test_screen_off_edge_10s)
{
	struct rpwl_ilim s;
	uint32_t c = 0;

	rpwl_ilim_reset(&s);
	zassert_equal(rpwl_ilim_step(&s, false, 500, &c), RPWL_ILIM_NONE);
	zassert_equal(rpwl_ilim_step(&s, true, 1000, &c), RPWL_ILIM_FIRST);
	zassert_equal(rpwl_ilim_step(&s, true, 1000 + 9999, &c), RPWL_ILIM_AGAIN);
	zassert_equal(c, 2);
	zassert_equal(rpwl_ilim_step(&s, true, 1000 + 10000, &c), RPWL_ILIM_FIRST);
	zassert_equal(c, 1);
	/* not active for a while, then active: first again */
	zassert_equal(rpwl_ilim_step(&s, false, 30000, &c), RPWL_ILIM_NONE);
	zassert_equal(rpwl_ilim_step(&s, true, 31000, &c), RPWL_ILIM_FIRST);
}
