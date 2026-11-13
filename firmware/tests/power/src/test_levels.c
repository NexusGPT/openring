/* Suite power_levels (software step 6, unit U5): the battery levels from the gauge and the voltage, the mean of 10 in
 * RECORDING, the report to the core on every change in both directions. Rows C2 and P11 of firmware/docs/step6-plan.md.
 * Every expected value is typed here from design/firmware.md ("FW l.N"), never produced by the code under test. */
#include "common.h"

ZTEST_SUITE(power_levels, NULL, NULL, pw_before, NULL, NULL);

/* FW l.115 to l.117: B15 at or under 15 %, B5 at or under 5 %, B2 at or under 2 % (state of charge).
 * rpw_start judges its first sample alone (single sample), so the level is read right after it. */
ZTEST(power_levels, test_soc_edges)
{
	static const struct { uint16_t pct_x10; uint8_t level; } t[] = {
		{ 160, 0 },   /* 16 %: above B15 */
		{ 150, 1 },   /* 15 %: B15 */
		{ 60, 1 },    /* 6 %: B15 */
		{ 50, 2 },    /* 5 %: B5 */
		{ 30, 2 },    /* 3 %: B5 */
		{ 20, 3 },    /* 2 %: B2 */
		{ 19, 3 },    /* 1.9 % */
		{ 21, 2 },    /* 2.1 % */
	};

	for (size_t i = 0; i < ARRAY_SIZE(t); i++) {
		struct rpw_values v;

		pw_before(NULL);
		rhw_sim_gauge_start_soc(t[i].pct_x10);
		pw_script1(3900, 0);        /* a full cell's voltage: only the state of charge judges */
		pw_start();
		rpw_values(&v);
		zassert_equal(v.soc_x10, t[i].pct_x10, "case %u: gauge value passed on", (unsigned)i);
		zassert_equal(v.level, t[i].level, "case %u: soc %u (x10) level %u", (unsigned)i, t[i].pct_x10,
			      v.level);
		/* the pure rule agrees on the same pair */
		zassert_equal(rpwl_level(t[i].pct_x10, 3900, 1), t[i].level, "pure rule, case %u", (unsigned)i);
	}
}

/* FW l.116 and l.117: B5 at or under 3.45 V, B2 at or under 3.30 V (single sample outside RECORDING). */
ZTEST(power_levels, test_voltage_edges)
{
	static const struct { uint16_t mv; uint8_t level; } t[] = {
		{ 3451, 0 }, { 3450, 2 }, { 3301, 2 }, { 3300, 3 }, { 4350, 0 }, { 3299, 3 },
	};

	for (size_t i = 0; i < ARRAY_SIZE(t); i++) {
		struct rpw_values v;

		pw_before(NULL);
		rhw_sim_gauge_start_soc(800);   /* 80 %: only the voltage judges */
		pw_script1(t[i].mv, 0);
		pw_start();
		rpw_values(&v);
		zassert_equal(v.battery_mv, t[i].mv, "case %u: sample passed on", (unsigned)i);
		zassert_equal(v.level, t[i].level, "case %u: %u mV level %u", (unsigned)i, t[i].mv, v.level);
		zassert_equal(rpwl_level(800, t[i].mv, 1), t[i].level, "pure rule, case %u", (unsigned)i);
	}
	/* the compare is exact, not rounded: a mean of 3450.9 mV (34509 over 10) is above 3.45 V */
	zassert_equal(rpwl_level(800, 34509, 10), 0);
	zassert_equal(rpwl_level(800, 34500, 10), 2);
	zassert_equal(rpwl_level(800, 33001, 10), 2);
	zassert_equal(rpwl_level(800, 33000, 10), 3);
}

/* FW l.114, l.928: voltage averaged over 10 s, one sample a second in RECORDING. Eleven samples: 3,340 mV five times,
 * 3,260 mV five times, then 3,400 mV. The mean of the last ten is 3,300 mV (B2) exactly at the tenth sample, and not
 * B2 before it (a mean of the last five would reach B2 at the eighth) and not after the eleventh (3,306 mV). */
ZTEST(power_levels, test_mean_of_ten_in_recording)
{
	static const uint16_t mv[11] = { 3340, 3340, 3340, 3340, 3340, 3260, 3260, 3260, 3260, 3260, 3400 };
	static const int32_t ua[11] = { 0 };
	int64_t t0;

	pw_script(mv, ua, 11);
	rhw_sim_gauge_start_soc(800);
	rpw_state(RC_ST_RECORDING);
	t0 = k_uptime_get();
	pw_start();                         /* sample 1 */
	for (uint32_t j = 2; j <= 11; j++) {
		struct rpw_values v;

		pw_sleep_until(t0 + (int64_t)(j - 1) * 1000 + 500);   /* sample j came at t0 + (j - 1) s */
		rpw_values(&v);
		zassert_equal(v.battery_mv, mv[j - 1], "sample %u was taken", j);
		if (j == 10) {
			zassert_equal(v.level, 3, "mean of ten is 3,300 mV: B2 at sample 10");
		} else if (j == 11) {
			zassert_not_equal(v.level, 3, "mean 3,306 mV: no longer B2 after sample 11");
		} else {
			zassert_not_equal(v.level, 3, "sample %u: mean above 3,300 mV, not B2", j);
		}
	}
}

/* FW l.211 to l.213 (R-CHG, R-STB): the level is reported to the core on every change, both directions, and not
 * twice for the same level. The gauge value is set before each sample (ua 0: the gauge keeps it). */
ZTEST(power_levels, test_report_on_change_both_ways)
{
	static const uint16_t soc[] = { 40, 12, 12, 100, 800 };   /* 4 %, 1.2 %, same, 10 %, 80 % */
	static const uint8_t expect[] = { 2, 3, 1, 0 };            /* B5, B2, B15, OK: two down, two up */
	int64_t t0;

	pw_script1(3900, 0);
	rhw_sim_gauge_start_soc(800);
	rpw_state(RC_ST_RECORDING);
	t0 = k_uptime_get();
	pw_start();
	for (uint32_t j = 1; j <= ARRAY_SIZE(soc); j++) {
		rhw_sim_gauge_start_soc(soc[j - 1]);               /* for sample j */
		pw_sleep_until(t0 + (int64_t)j * 1000 + 500);
	}
	zassert_equal(cap.n_level, ARRAY_SIZE(expect), "levels reported: %u", cap.n_level);
	for (uint32_t i = 0; i < ARRAY_SIZE(expect); i++) {
		zassert_equal(cap.level[i], expect[i], "report %u", i);
	}
	/* the event log holds one record per change: level u8, soc x10 u16, mean mV u16 (rrec_spec.h) */
	zassert_equal(pw_log_count(RREC_LOG_BATTERY), 4);
	zassert_equal(cap.log[0].code, 0x0020);
	zassert_equal(cap.log[0].n, 5);
	zassert_equal(cap.log[0].args[0], 2);
	zassert_equal(cap.log[0].args[1] | (cap.log[0].args[2] << 8), 40);
	zassert_equal(cap.log[0].args[3] | (cap.log[0].args[4] << 8), 3900);
	zassert_equal(cap.log[3].args[0], 0, "the last record is the way back up to OK");
}

/* A level other than OK at the first sample is reported once, from the power thread, after rpw_start. */
ZTEST(power_levels, test_first_level_reported_at_start)
{
	pw_script1(3900, 0);
	rhw_sim_gauge_start_soc(100);       /* 10 %: B15 */
	pw_start();
	k_sleep(K_MSEC(20));
	zassert_equal(cap.n_level, 1);
	zassert_equal(cap.level[0], 1);
}
