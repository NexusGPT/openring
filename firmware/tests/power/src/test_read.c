/* Suite power_read (software step 6, the join's addition to the power unit, lead's ruling 3 on the factory unit's gaps):
 * rpw_sample_now() and rpw_charger_now() read the power chip NOW on the power thread (the one owner of the chip, rhw.h)
 * and hand the values to the caller, for T-MOTOR (FW l.1028) and T-CHARGE (FW l.1032). */
#include <string.h>

#include "common.h"

ZTEST_SUITE(power_read, NULL, NULL, pw_before, NULL, NULL);

/* the sample events of the simulated chip since the log was cleared, and the thread that made the last one */
static uint32_t samples(char *who, size_t n)
{
	uint32_t k = 0;

	for (int32_t i = pw_find(RHW_EV_PMIC_SAMPLE, 0); i >= 0; i = pw_find(RHW_EV_PMIC_SAMPLE, i + 1)) {
		struct rhw_sim_ev e = pw_ev(i);

		strncpy(who, e.caller, n - 1);
		who[n - 1] = '\0';
		k++;
	}
	return k;
}

/* one sample now, taken by the power thread, values as the chip gives them; the gauge is not stepped */
ZTEST(power_read, test_sample_now_from_power_thread)
{
	char who[16] = "";
	uint16_t mv = 0;
	int32_t ua = 0;

	pw_start();
	k_sleep(K_MSEC(50));   /* the start's callbacks are out */
	pw_script1(3712, 4321);
	rhw_sim_log_clear();
	zassert_ok(rpw_sample_now(&mv, &ua));
	zassert_equal(mv, 3712, "mV as sampled (%u)", mv);
	zassert_equal(ua, 4321, "uA as sampled (%d)", ua);
	zassert_equal(samples(who, sizeof(who)), 1, "one sample");
	zassert_equal(strcmp(who, "rpw"), 0, "taken by the power thread, not by the caller (%s)", who);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_GAUGE_PROCESS), 0, "the gauge is not stepped by the read");
}

/* T-CHARGE: the charger state with the latched error and the battery current, read now (FW l.702 code 5 = error) */
ZTEST(power_read, test_charger_now_latched_error)
{
	uint8_t st = 0xFF, err = 0xFF;
	int32_t ua = 0;

	pw_start();
	k_sleep(K_MSEC(50));
	pw_script1(3900, -15000);
	zassert_ok(rpw_charger_now(&st, &err, &ua));
	zassert_equal(st, 0, "no VBUS: charger off, code 0 (FW l.702)");
	zassert_equal(err, 0, "no error latched");
	zassert_equal(ua, -15000, "the battery current of the sample");
	rhw_sim_pmic_charge_error(3, 4);
	k_sleep(K_MSEC(50));
	zassert_ok(rpw_charger_now(&st, &err, &ua));
	zassert_equal(st, 5, "error, code 5 (FW l.702)");
	zassert_equal(err, 3, "the latched reason");
}

/* not started: no power thread answers; the caller gets -ETIMEDOUT, not a stale value */
ZTEST(power_read, test_read_before_start_times_out)
{
	uint16_t mv = 0;
	int32_t ua = 0;

	zassert_equal(rpw_sample_now(&mv, &ua), -ETIMEDOUT, "no answer without rpw_start");
}
