/*
 * recorder_rails: what is on in each state (design/firmware.md 8.2, l.912 to l.920; plan rows P6, S18 the join's part).
 */
#include "rt.h"

/* FW l.912 to l.920 (the table of 8.2): VDD_SD on in BOOT, RECOVERY, RECORDING, TRANSFER; VDD_MIC only in RECORDING;
 * HFXO on in BOOT and RECOVERY (l.915), RECORDING (l.917), TRANSFER (l.919), with USB in CHARGING (l.918: VBUS is present
 * in CHARGING, so USB runs), and in STANDBY and the error states only when the radio runs (l.916, l.920; these suites
 * do not run the radio, so off). After a row the ring rests in its new state; BOOT and RECOVERY are passed through, so
 * their HFXO is checked by test_hfxo_in_boot_and_recovery from the event log; FACTORY_TEST is "per test". */
static int check_rails(int row)
{
	enum rc_state s = rt_state();
	bool sd_want = s == RC_ST_RECORDING || s == RC_ST_TRANSFER;
	bool mic_want = s == RC_ST_RECORDING;
	bool hfxo_want = s == RC_ST_RECORDING || s == RC_ST_TRANSFER || s == RC_ST_CHARGING;
	int bad = 0;

	if (s == RC_ST_BOOT || s == RC_ST_RECOVERY || s == RC_ST_FACTORY_TEST || s == RC_ST_OFF || s == RC_ST_SHIP) {
		return 0;
	}
	if (rt_sd() != sd_want) {
		TC_PRINT("RAILS row %d: %s VDD_SD %d, wanted %d\n", row, rc_state_name(s), rt_sd(), sd_want);
		bad++;
	}
	if (rt_mic() != mic_want) {
		TC_PRINT("RAILS row %d: %s VDD_MIC %d, wanted %d\n", row, rc_state_name(s), rt_mic(), mic_want);
		bad++;
	}
	if (hfxo_want && !rhw_hfxo()->running()) {
		TC_PRINT("RAILS row %d: %s HFXO not running\n", row, rc_state_name(s));
		bad++;
	}
	if (!hfxo_want && rhw_sim_hfxo_requests() != 0) {
		TC_PRINT("RAILS row %d: %s HFXO still requested (%u)\n", row, rc_state_name(s), rhw_sim_hfxo_requests());
		bad++;
	}
	return bad;
}

ZTEST(recorder_rails, test_rails_per_state)
{
	/* rows that end in each checked state: STANDBY (3, 9, 26, 40, 47, 61), CHARGING (5, 20, 30, 46), TRANSFER (39),
	 * RECORDING (12, 27), the error states (6, 8, 24, 37, 44) */
	static const int rows[] = { 3, 5, 6, 8, 9, 12, 20, 24, 26, 27, 30, 37, 39, 40, 44, 46, 47, 61 };
	int bad = 0;

	for (size_t i = 0; i < ARRAY_SIZE(rows); i++) {
		int b;

		zassert_equal(rt_run_row(rows[i]), 0, NULL);
		zassert_true(rt_row_seen(rows[i]), "row %d", rows[i]);
		b = check_rails(rows[i]);
		TC_PRINT("RAILS row %d -> %s: %s\n", rows[i], rc_state_name(rt_state()), b == 0 ? "ok" : "FAILED");
		bad += b;
	}
	zassert_equal(bad, 0, "%d rail faults", bad);
}

/* FW l.640: VDD_SD on for the whole recording, off between recordings */
ZTEST(recorder_rails, test_sd_rail_per_state)
{
	rt_fresh(NULL);
	zassert_false(rt_sd(), "off in STANDBY");
	rt_long();
	for (int i = 0; i < 30; i++) {
		zassert_true(rt_sd(), "on in the recording at %d00 ms", i);
		rt_sleep(100);
	}
	rt_long();
	zassert_false(rt_sd(), "off after the recording");
	zassert_equal(rt_count_rail(RHW_RAIL_SD, false), 2, "off once after the boot mount and once at the close");
}

/* the HFXO requests outstanding just after simulated event i (the a0 of the last HFXO request or release up to i) */
static int64_t hfxo_at(uint32_t upto)
{
	struct rhw_sim_ev e;
	int64_t n = 0;

	for (uint32_t i = 0; i <= upto && rhw_sim_log_get(i, &e); i++) {
		if (e.kind == RHW_EV_HFXO_REQUEST || e.kind == RHW_EV_HFXO_RELEASE) {
			n = e.a0;
		}
	}
	return n;
}

/* the first step whose state after it is s, at or after step `from`; -1 when none */
static int32_t step_into(enum rc_state s, uint32_t from)
{
	for (uint32_t i = from; i < rt_steps(); i++) {
		if (rt_step_get(i).state == s) {
			return (int32_t)i;
		}
	}
	return -1;
}

/* the HFXO count stays above 0 from simulated event `a` through every event before time t_end_us */
static bool held_through(int32_t a, int64_t t_end_us)
{
	struct rhw_sim_ev e;
	int64_t n = hfxo_at((uint32_t)a);

	if (n < 1) {
		return false;
	}
	for (uint32_t i = (uint32_t)a + 1; rhw_sim_log_get(i, &e) && e.t_us < t_end_us; i++) {
		if ((e.kind == RHW_EV_HFXO_REQUEST || e.kind == RHW_EV_HFXO_RELEASE) && e.a0 < 1) {
			return false;
		}
	}
	return true;
}

/* FW l.915 (review finding R6-04): HFXO on in BOOT and RECOVERY, released when the state that follows does not want it
 * (STANDBY, l.916: "when the radio runs"; these suites do not run the radio) */
ZTEST(recorder_rails, test_hfxo_in_boot_and_recovery)
{
	int32_t i_init, i_rec, i_stb;
	int64_t t_stb_us;

	/* BOOT: the boot mount (the first card init) runs with HFXO held, until the step into STANDBY */
	rt_fresh(NULL);
	i_init = rt_find(RHW_EV_DISK_INIT, -1, -1, 0);
	i_stb = step_into(RC_ST_STANDBY, 0);
	zassert_true(i_init >= 0 && i_stb >= 0, "booted to STANDBY (%d, %d)", i_init, i_stb);
	t_stb_us = rt_step_get((uint32_t)i_stb).t_ms * 1000;
	TC_PRINT("HFXO BOOT: requests %lld at the boot card init (event %d), STANDBY step at %lld us, now %u\n",
		 hfxo_at((uint32_t)i_init), i_init, t_stb_us, rhw_sim_hfxo_requests());
	zassert_true(held_through(i_init, t_stb_us), "HFXO on in BOOT (FW l.915)");
	zassert_equal(rhw_sim_hfxo_requests(), 0u, "released in STANDBY (FW l.916)");

	/* RECOVERY (row 9: the open flag at boot, the scan, STANDBY): held from BOOT through RECOVERY */
	zassert_equal(rt_run_row(9), 0, NULL);
	zassert_true(rt_row_seen(9), "row 9");
	i_rec = step_into(RC_ST_RECOVERY, 0);
	i_stb = step_into(RC_ST_STANDBY, i_rec < 0 ? 0 : (uint32_t)i_rec);
	zassert_true(i_rec >= 0 && i_stb > i_rec, "BOOT, RECOVERY, STANDBY (%d, %d)", i_rec, i_stb);
	i_init = rt_find(RHW_EV_DISK_INIT, -1, -1, 0);
	t_stb_us = rt_step_get((uint32_t)i_stb).t_ms * 1000;
	TC_PRINT("HFXO RECOVERY: requests %lld at the boot card init (event %d), RECOVERY step at %lld ms, STANDBY at %lld us, "
		 "now %u\n", hfxo_at((uint32_t)i_init), i_init, rt_step_get((uint32_t)i_rec).t_ms, t_stb_us,
		 rhw_sim_hfxo_requests());
	zassert_true(held_through(i_init, t_stb_us), "HFXO on in BOOT and RECOVERY (FW l.915)");
	zassert_equal(rhw_sim_hfxo_requests(), 0u, "released in STANDBY (FW l.916)");
}

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_rails, NULL, setup, NULL, NULL, NULL);
