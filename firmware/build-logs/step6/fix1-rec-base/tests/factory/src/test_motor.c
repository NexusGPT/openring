/* Suite factory_motor (software step 6, unit U8): T-MOTOR (0x40, FW l.1028): VBAT read once before MOTOR goes high,
 * MOTOR on 500 ms, VBAT read again 250 ms into the pulse, both reported and the dip. Rows T16.
 * Expected values are typed from FW l.1028; the times are read from the simulated drivers' one event log. */
#include "common.h"

ZTEST_SUITE(factory_motor, NULL, NULL, fx_before, fx_after, NULL);

ZTEST(factory_motor, test_reads_and_timing)
{
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;
	struct rhw_pmic_sample s = { .mv = 3900, .ua = 3000, .temp_c_x10 = 250, .die_c_x10 = 300 };

	rhw_sim_pmic_script(&s, 1);
	rhw_sim_pmic_motor_dip(30); /* the simulated cell sags by 30 mV while MOTOR is high */
	rhw_sim_log_clear();
	zassert_equal(fx_do1(0x40, true, out, &n, &eff), 0);
	zassert_equal(n, 7, "T-MOTOR answers 7 bytes");
	zassert_equal(out[0], 0, "pass");

	zassert_equal(fx_count(RHW_EV_PMIC_SAMPLE), 2, "two reads of VBAT");
	int32_t s1 = fx_find(RHW_EV_PMIC_SAMPLE, 0);
	int32_t hi = fx_find(RHW_EV_MOTOR, 0);

	zassert_true(s1 >= 0 && hi >= 0);
	zassert_equal(fx_ev(hi).a0, 1, "the first pin event is MOTOR high");
	int32_t s2 = fx_find(RHW_EV_PMIC_SAMPLE, s1 + 1);
	int32_t lo = fx_find(RHW_EV_MOTOR, hi + 1);

	zassert_true(s2 >= 0 && lo >= 0);
	zassert_equal(fx_ev(lo).a0, 0, "then MOTOR low");
	zassert_true(s1 < hi, "VBAT is read before MOTOR goes high");
	zassert_true(hi < s2 && s2 < lo, "the second read is inside the pulse");
	int64_t t_hi = fx_ev(hi).t_us;

	zassert_within(fx_ev(lo).t_us - t_hi, 500000, 2000, "MOTOR on 500 ms (FW l.1028)");
	zassert_within(fx_ev(s2).t_us - t_hi, 250000, 2000, "VBAT read 250 ms into the pulse (FW l.1028): %lld us",
		       fx_ev(s2).t_us - t_hi);
	/* the values: before 3,900 mV, during 3,870 mV, dip 30 mV (what the simulated chip gave) */
	zassert_equal(fx_ev(s1).a0, 3900);
	zassert_equal(fx_ev(s2).a0, 3870);
	zassert_equal(fx_u16(&out[1]), 3900, "VBAT before");
	zassert_equal(fx_u16(&out[3]), 3870, "VBAT during the pulse");
	zassert_equal((int16_t)fx_u16(&out[5]), 30, "the dip");
	zassert_equal(fx_count(RHW_EV_MOTOR), 2, "one high, one low");

	/* no dip: reported as 0 */
	rhw_sim_log_clear();
	rhw_sim_pmic_motor_dip(0);
	zassert_equal(fx_do1(0x40, true, out, &n, &eff), 0);
	zassert_equal((int16_t)fx_u16(&out[5]), 0);
}
