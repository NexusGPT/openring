/*
 * recorder_rails: what is on in each state (design/firmware.md 8.2, l.912 to l.920; plan rows P6, S18 the join's part).
 */
#include "rt.h"

/* FW l.912 to l.920: VDD_SD on in BOOT, RECOVERY, RECORDING, TRANSFER; VDD_MIC only in RECORDING; HFXO on in RECORDING and
 * TRANSFER, and with USB in CHARGING. FACTORY_TEST is "per test" and BOOT/RECOVERY are passed through (not checked). */
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

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_rails, NULL, setup, NULL, NULL, NULL);
