/* Suite power_sample (software step 6, unit U5): a sample every 1 s in RECORDING, every 60 s in the other awake
 * states, none in SHIP and OFF; every sample also reads the current limit status (FW l.928). Row P9. */
#include "common.h"

ZTEST_SUITE(power_sample, NULL, NULL, pw_before, NULL, NULL);

/* The sampling period of every state (FW l.928; the states of FW 1.1 in table order): RECORDING 1,000 ms; SHIP and OFF
 * do not run; every other awake state 60,000 ms. A value that is no state changes nothing. */
ZTEST(power_sample, test_period_per_state)
{
	static const uint32_t want[RC_ST_COUNT] = {
		0,      /* SHIP */
		0,      /* OFF */
		60000,  /* BOOT */
		60000,  /* RECOVERY */
		60000,  /* STANDBY */
		1000,   /* RECORDING */
		60000,  /* CHARGING */
		60000,  /* TRANSFER */
		60000,  /* ERR_STORAGE_FULL */
		60000,  /* ERR_BATTERY_LOW */
		60000,  /* ERR_STORAGE_FAULT */
		60000,  /* ERR_MIC_FAULT */
		60000,  /* ERR_CHARGER */
		60000,  /* FACTORY_TEST */
	};

	pw_start();
	zassert_equal(rpw_priv_period_ms(), 60000, "60 s until rpw_state says otherwise");
	for (uint8_t st = 0; st < RC_ST_COUNT; st++) {
		rpw_state(st);
		zassert_equal(rpw_priv_period_ms(), want[st], "state %u", st);
		zassert_equal(rpwl_period_ms(st), want[st], "pure rule, state %u", st);
	}
	rpw_state(RC_ST_STANDBY);
	rpw_state(RC_ST_COUNT);             /* no such state */
	rpw_state(200);
	zassert_equal(rpw_priv_period_ms(), 60000, "an unknown state changes nothing");
}

/* The period is real: in RECORDING 5 samples in 5.5 s, 1,000 ms apart; in STANDBY 2 samples in 125 s, 60 s apart. */
ZTEST(power_sample, test_period_in_time)
{
	int64_t t0;
	int32_t i, prev;
	uint32_t seen = 0;

	pw_script1(3900, 0);
	rpw_state(RC_ST_RECORDING);
	t0 = k_uptime_get();
	pw_start();
	pw_sleep_until(t0 + 5500);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_SAMPLE), 6, "the start sample and 5 more");
	prev = -1;
	for (i = pw_find(RHW_EV_PMIC_SAMPLE, 0); i >= 0; i = pw_find(RHW_EV_PMIC_SAMPLE, i + 1)) {
		if (prev >= 0) {
			int64_t d = pw_ev(i).t_us - pw_ev(prev).t_us;

			zassert_within(d, 1000000, 2000, "samples 1,000 ms apart, got %lld us", d);
			seen++;
		}
		prev = i;
	}
	zassert_equal(seen, 5);

	pw_before(NULL);
	pw_script1(3900, 0);
	rpw_state(RC_ST_STANDBY);
	t0 = k_uptime_get();
	pw_start();
	pw_sleep_until(t0 + 125000);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_SAMPLE), 3, "the start sample, 60 s, 120 s");
	i = pw_find(RHW_EV_PMIC_SAMPLE, 1);
	zassert_within(pw_ev(i).t_us - pw_ev(0).t_us, 60000000, 2000);
}

/* SHIP and OFF: no sampling at all. */
ZTEST(power_sample, test_no_sampling_in_ship_and_off)
{
	int64_t t0;

	pw_script1(3900, 0);
	rpw_state(RC_ST_OFF);
	t0 = k_uptime_get();
	pw_start();
	pw_sleep_until(t0 + 130000);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_SAMPLE), 1, "only the start sample");
}

/* FW l.928: every sample also reads the current limit status, right after it. */
ZTEST(power_sample, test_ilim_read_with_every_sample)
{
	int64_t t0;
	uint32_t ns, k = 0;

	pw_script1(3900, 0);
	rpw_state(RC_ST_RECORDING);
	t0 = k_uptime_get();
	pw_start();
	pw_sleep_until(t0 + 4500);
	ns = rhw_sim_log_count_kind(RHW_EV_PMIC_SAMPLE);
	zassert_equal(ns, 5);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_ILIM), ns, "one status read per sample");
	for (int32_t i = pw_find(RHW_EV_PMIC_SAMPLE, 0); i >= 0; i = pw_find(RHW_EV_PMIC_SAMPLE, i + 1)) {
		int32_t j = pw_find(RHW_EV_PMIC_ILIM, i);

		zassert_true(j > i, "a status read follows sample %u", k);
		/* nothing but the gauge step and the charger status between the sample and its status read */
		for (int32_t m = i + 1; m < j; m++) {
			uint16_t kd = pw_ev(m).kind;

			zassert_true(kd == RHW_EV_GAUGE_START || kd == RHW_EV_GAUGE_PROCESS ||
				     kd == RHW_EV_PMIC_CHG_STATUS,
				     "entry %d between a sample and its status read: kind %u", m, kd);
		}
		k++;
	}
}
