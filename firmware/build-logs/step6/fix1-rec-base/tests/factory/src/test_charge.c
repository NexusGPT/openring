/* Suite factory_charge (software step 6, unit U8): T-CHARGE (0x70, FW l.1032): the charge state, the latched errors and
 * the battery current; the result is fail when the state is off or an error is latched (R-CHG). Rows T20. */
#include "common.h"

ZTEST_SUITE(factory_charge, NULL, NULL, fx_before, fx_after, NULL);

static void ask(uint8_t *out, uint8_t *result, uint8_t *state, uint8_t *err, int32_t *ua)
{
	size_t n = 0;
	enum rfa_effect eff;

	zassert_equal(fx_do1(0x70, true, out, &n, &eff), 0);
	zassert_equal(n, 7, "T-CHARGE answers 7 bytes");
	*result = out[0];
	*state = out[1];
	*err = out[2];
	*ua = (int32_t)fx_u32(&out[3]);
}

ZTEST(factory_charge, test_fail_when_off_or_error)
{
	uint8_t out[RFA_OUT_MAX], result, state, err;
	int32_t ua;
	struct rhw_pmic_sample s = { .mv = 3900, .ua = 15000, .temp_c_x10 = 250, .die_c_x10 = 300 };

	rhw_sim_pmic_script(&s, 1);

	/* trickle, constant current, constant voltage, completed: pass (FW l.1032: states 1 to 4 of GET_BATTERY, l.702) */
	for (int st = 1; st <= 4; st++) {
		rhw_sim_pmic_charge_state(st);
		ask(out, &result, &state, &err, &ua);
		zassert_equal(result, 0, "state %d passes", st);
		zassert_equal(state, st);
		zassert_equal(err, 0);
		zassert_equal(ua, 15000, "the battery current is reported");
	}
	/* off: fail */
	rhw_sim_pmic_charge_state(0);
	ask(out, &result, &state, &err, &ua);
	zassert_equal(result, 1, "state off fails");
	zassert_equal(state, 0);

	/* an error latched: fail, with the reason reported */
	rhw_sim_pmic_charge_state(-1);
	rhw_sim_pmic_charge_error(0x04, 0x01);
	ask(out, &result, &state, &err, &ua);
	zassert_equal(result, 1, "an error is latched: fail");
	zassert_equal(state, 5, "state error (FW l.702)");
	zassert_equal(err, 0x04, "the latched reason");

	/* a latched error with a state that looks fine still fails */
	rhw_sim_pmic_charge_state(2);
	ask(out, &result, &state, &err, &ua);
	zassert_equal(result, 1, "a latched error fails whatever the state says");
	zassert_equal(state, 2);
	zassert_equal(err, 0x04);

	/* the pure judgement at its edges */
	zassert_equal(rfa_charge_result(0, 0), 1);
	zassert_equal(rfa_charge_result(1, 0), 0);
	zassert_equal(rfa_charge_result(4, 0), 0);
	zassert_equal(rfa_charge_result(5, 0), 1);
	zassert_equal(rfa_charge_result(3, 1), 1);
}
