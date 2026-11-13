/* Suite power_gauge (software step 6, unit U5): each sample feeds the gauge; the motor's charge since the last
 * sample is added as a discharge, I_fed = I_measured + Q_motor / t_sample (FW l.926, l.927). Row P8. */
#include "common.h"

ZTEST_SUITE(power_gauge, NULL, NULL, pw_before, NULL, NULL);

/* FW l.927: "one MF, 51.50 mA.s, in a 1 s sample adds 51.5 mA to that sample". The sample measures 3,000 uA, so the
 * gauge is fed 54,500 uA; the charge is used once (the next sample is fed the measured current alone). */
ZTEST(power_gauge, test_motor_charge_added)
{
	int64_t t0;
	int32_t g;

	pw_script1(3900, 3000);
	rpw_state(RC_ST_RECORDING);
	t0 = k_uptime_get();
	pw_start();
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_GAUGE_START), 1);
	rpw_motor_charge(51500);            /* 51.50 mA.s in uA.s, added during the first second */
	pw_sleep_until(t0 + 1500);          /* sample 2 came at t0 + 1 s */
	g = pw_nth(RHW_EV_GAUGE_PROCESS, 1);    /* the 0th is the first step of rpw_start (no time passed) */
	zassert_true(g >= 0, "a gauge step after the sample");
	/* the sample covers 1,000 ms (the clock counts whole ms: 1,000 or 1,001); 51,500 uA.s over that time */
	zassert_within(pw_ev(g).a1, 1000, 2, "the sample covers 1,000 ms");
	zassert_within(pw_ev(g).a0, 54500, 100, "3,000 uA measured + about 51,500 uA of the motor (FW l.927)");
	zassert_within(pw_ev(g).a0, 3000 + 51500000 / pw_ev(g).a1, 1, "I_fed = I_measured + Q / t over the ms fed");
	pw_sleep_until(t0 + 2500);          /* sample 3 */
	g = pw_nth(RHW_EV_GAUGE_PROCESS, 2);
	zassert_true(g >= 0);
	zassert_equal(pw_ev(g).a0, 3000, "the charge was used once");
	/* each sample feeds the gauge once: start step + 2 samples */
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_GAUGE_PROCESS), 3);

	/* the pure rule on its own: positive uA = discharge (the sign of struct rhw_pmic_sample) */
	zassert_equal(rpwl_fed_ua(3000, 51500, 1000), 54500);
	zassert_equal(rpwl_fed_ua(3000, 51500, 2000), 3000 + 25750, "spread over the longer sample");
	zassert_equal(rpwl_fed_ua(-15000, 0, 1000), -15000, "charging current is kept as it is");
	zassert_equal(rpwl_fed_ua(-15000, 51500, 1000), 36500);
	zassert_equal(rpwl_fed_ua(3000, 51500, 0), 3000, "no time, no division");

	/* the charge counted before a gauge failure is not lost: it goes into the next step */
	pw_before(NULL);
	pw_script1(3900, 3000);
	rpw_state(RC_ST_RECORDING);
	t0 = k_uptime_get();
	pw_start();
	rhw_sim_gauge_error(-5);
	rpw_motor_charge(10000);
	pw_sleep_until(t0 + 1500);                   /* the step failed */
	rhw_sim_gauge_error(0);
	pw_sleep_until(t0 + 2500);                   /* the next step carries it: 10,000 uA.s over 1 s */
	g = pw_nth(RHW_EV_GAUGE_PROCESS, 2);       /* 0: start, 1: the failed step, 2: the next one */
	zassert_true(g >= 0);
	zassert_equal(pw_ev(g).a0, 3000 + 10000, "the charge of the failed step came with the next one");
}
