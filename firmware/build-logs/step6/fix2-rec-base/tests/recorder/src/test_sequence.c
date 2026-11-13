/*
 * recorder_sequence: the microphone start and stop sequences of design/firmware.md 4.5 (plan rows A6, A12, A13).
 */
#include "rt.h"

/* FW l.455 to l.460: HFXO requested and running; rec_mics_on (sign, then VDD_MIC); wait 1 ms; configure and start PDM */
ZTEST(recorder_sequence, test_start_order_and_times)
{
	int32_t i_req, i_run, i_mic, i_cfg, i_def, i_start;

	rt_fresh(NULL);
	rhw_sim_log_clear();
	rt_long();
	i_req = rt_find(RHW_EV_HFXO_REQUEST, -1, -1, 0);
	i_run = rt_find(RHW_EV_HFXO_RUNNING, -1, -1, 0);
	i_mic = rt_find_rail(RHW_RAIL_MIC, true, 0);
	i_cfg = rt_find(RHW_EV_MIC_CONFIGURE, -1, -1, 0);
	i_def = rt_find(RHW_EV_MIC_PINS_DEFAULT, -1, -1, 0);
	i_start = rt_find(RHW_EV_MIC_START, -1, -1, 0);
	TC_PRINT("start: HFXO request %d (%lld us), running %d (%lld us), VDD_MIC on %d (%lld us), configure %d (%lld us), "
		 "pins default %d, PDM start %d (%lld us)\n", i_req, rt_ev_us(i_req), i_run, rt_ev_us(i_run), i_mic,
		 rt_ev_us(i_mic), i_cfg, rt_ev_us(i_cfg), i_def, i_start, rt_ev_us(i_start));
	zassert_true(i_req >= 0 && i_run > i_req, "1. HFXO requested and running (FW l.456)");
	zassert_true(i_mic > i_run, "2. VDD_MIC on after HFXO runs (FW l.457)");
	zassert_true(rt_ev_us(i_cfg) - rt_ev_us(i_mic) >= 1000, "3. at least 1 ms between VDD_MIC on and the PDM (FW l.458)");
	zassert_true(i_cfg > i_mic && i_start > i_cfg, "4. configure, then start (FW l.459, l.429)");
	zassert_true(i_def > i_mic && i_def < i_start, "the clock starts only after VDD_MIC is on (FW l.465)");
	rt_long();
}

/* FW l.463: STOP, blocks released, clock pins asleep, VDD_MIC off, HFXO released; only then the screen may leave */
ZTEST(recorder_sequence, test_stop_order)
{
	int32_t i_stop, i_sleep, i_mic, i_rel;

	rt_fresh(NULL);
	rt_long();
	rt_sleep(700);
	rhw_sim_log_clear();
	rt_steps_clear();
	rt_long();
	i_stop = rt_find(RHW_EV_MIC_STOP, -1, -1, 0);
	i_sleep = rt_find(RHW_EV_MIC_PINS_SLEEP, -1, -1, i_stop < 0 ? 0 : (uint32_t)i_stop);
	i_mic = rt_find_rail(RHW_RAIL_MIC, false, 0);
	i_rel = rt_find(RHW_EV_HFXO_RELEASE, -1, -1, 0);
	TC_PRINT("stop: PDM stop %d, pins sleep %d, VDD_MIC off %d, HFXO release %d, blocks held after %u\n", i_stop, i_sleep,
		 i_mic, i_rel, rhw_sim_mic_held());
	zassert_true(i_stop >= 0 && i_sleep > i_stop, "STOP, then the clock pins asleep");
	zassert_equal(rhw_sim_mic_held(), 0, "every block given back (FW l.463: the driver releases its blocks)");
	zassert_true(i_mic > i_sleep, "VDD_MIC off after the clock is low (FW l.465)");
	zassert_true(i_rel > i_mic, "HFXO released after VDD_MIC off (FW l.463, A6)");
	zassert_false(rhw_hfxo()->running(), "HFXO off in STANDBY");
	zassert_equal(rt_mic_at_screens(), 0, "the screens learned of STANDBY only after VDD_MIC off");
}

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_sequence, NULL, setup, NULL, NULL, NULL);
