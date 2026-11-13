/*
 * recorder_ship: ship mode as the join carries it out (step 6 fix round 1, review findings R6-01, R6-02, R6-10):
 * design/firmware.md 8.4 (l.936 to l.941), the menu's "Power off" row (l.151) and ruling R20 (l.1057).
 * Orders are read from the one event log of the simulated drivers (rhw_sim.h).
 */
#include <string.h>

#include "rt.h"

/* ------------------------------------------------------------------ ship mode (fix round 1: R6-01, R6-02, R6-10) */
static struct {
	bool called;
	uint32_t log_n;        /* the simulated event log's length when step 1 ended (SHPHLDCONFIG comes after it) */
	bool mic, sd, usb, blanked, beacon_stopped;
	uint32_t radio_stops;
	char thread[16];
} at_ship;

static void ship_hook(void)
{
	const char *nm = k_thread_name_get(k_current_get());

	at_ship.called = true;
	at_ship.log_n = rhw_sim_log_count();
	at_ship.mic = rt_mic();
	at_ship.sd = rt_sd();
	at_ship.usb = rhw_sim_usb_enabled();
	at_ship.blanked = rt_blanked();
	at_ship.beacon_stopped = rt_find(RHW_EV_BEACON_STOP, -1, -1, 0) >= 0;
	at_ship.radio_stops = rrec_test_radio_stops();
	strncpy(at_ship.thread, nm != NULL ? nm : "", sizeof(at_ship.thread) - 1);
}

/* FW l.151, l.323: menu "Power off": the whole M2 (80 on, 120 off, 80 on) on the MOTOR pin before SHPHLDCONFIG (R6-01) */
ZTEST(recorder_ship, test_ship_feels_whole_m2)
{
	static const int32_t m2_ms[3] = { 80, 120, 80 };   /* FW l.323 */
	struct rhw_sim_ev e;
	int64_t t[4];
	int lv[4];
	int n = 0;
	int32_t i_cfg;

	rt_fresh(NULL);
	rhw_sim_log_clear();
	rglue_event(RC_EV_MENU_POWER_OFF);
	rt_settle();
	zassert_true(rt_row_seen(19), "row 19 (FW l.151)");
	i_cfg = rt_find(RHW_EV_PMIC_SHPHLD_CFG, -1, -1, 0);
	zassert_true(i_cfg >= 0, "SHPHLDCONFIG written");
	for (int32_t i = 0; i < i_cfg && rhw_sim_log_get((uint32_t)i, &e); i++) {
		if (e.kind == RHW_EV_MOTOR) {
			if (n < 4) {
				t[n] = e.t_us;
				lv[n] = (int)e.a0;
			}
			n++;
		}
	}
	TC_PRINT("ship: %d MOTOR edges before SHPHLDCONFIG (index %d)\n", n, i_cfg);
	zassert_equal(n, 4, "M2 = 4 edges before SHPHLDCONFIG (%d)", n);
	for (int i = 0; i < 4; i++) {
		zassert_equal(lv[i], (i % 2) == 0 ? 1 : 0, "edge %d level", i);
	}
	for (int i = 0; i < 3; i++) {
		int64_t d = t[i + 1] - t[i];

		TC_PRINT("ship: M2 segment %d lasted %lld us (FW l.323: %d ms)\n", i, d, m2_ms[i]);
		/* the motor unit's tolerance (tests/motor t_check_edges): -1 us to +1 ms */
		zassert_true(d >= (int64_t)m2_ms[i] * 1000 - 1 && d < (int64_t)m2_ms[i] * 1000 + 1000,
			     "segment %d: %lld us, FW l.323 %d ms", i, d, m2_ms[i]);
	}
	/* FW l.323: M2 lasts 280 ms from its first MOTOR high to its last MOTOR low, all before SHPHLDCONFIG */
	TC_PRINT("ship: M2 lasted %lld us on the MOTOR pin (FW l.323: 280 ms)\n", t[3] - t[0]);
	zassert_true(t[3] - t[0] >= 280 * 1000 - 1 && t[3] - t[0] < 280 * 1000 + 3000, "M2 280 ms (%lld us)", t[3] - t[0]);
}

/* FW l.937 step 1, ruling R20: before SHPHLDCONFIG the recording, storage, USB, radio and screen are closed; the ship
 * beacon still runs; ship mode runs on the recorder's thread (R6-02, R6-10). The factory SHIP_ENTER (VBUS present, the
 * ship waits for VBUS removal) and the menu's power off with the screen on. */
ZTEST(recorder_ship, test_ship_closes_each_part_first)
{
#if defined(CONFIG_RING_FACTORY)
	static uint8_t resp[64];
	uint8_t st;
	uint8_t sub = RREC_FAC_SHIP_ENTER;
	struct rt_boot b = { .factory_flag = true };
	int32_t i_cfg, i_usb_off, i_sd_off;
	uint32_t radio0;

	rt_fresh(&b);
	rt_vbus(true);
	rt_usb_configured();
	(void)rt_usb(RREC_OP_FACTORY, (const uint8_t[]){ RREC_FAC_ENTER }, 1, resp, sizeof(resp), &st);
	zassert_equal(rt_state(), RC_ST_FACTORY_TEST, "FACTORY_TEST");
	zassert_true(rhw_sim_usb_enabled(), "USB runs");
	zassert_false(rt_blanked(), "the screen is on (SCR_FACTORY)");
	memset(&at_ship, 0, sizeof(at_ship));
	radio0 = rrec_test_radio_stops();
	rrec_test_set_ship_hook(ship_hook);
	rhw_sim_log_clear();
	(void)rt_usb_send(RREC_OP_FACTORY, &sub, 1);
	for (int i = 0; i < 300 && !at_ship.called; i++) {
		rt_sleep(10);
	}
	rt_sleep(200);   /* the ship waits for VBUS removal now (FW l.939) */
	rrec_test_set_ship_hook(NULL);
	i_cfg = rt_find(RHW_EV_PMIC_SHPHLD_CFG, -1, -1, 0);
	i_usb_off = rt_find(RHW_EV_USB_DISABLE, -1, -1, 0);
	i_sd_off = rt_find_rail(RHW_RAIL_SD, false, 0);
	TC_PRINT("ship (factory): step 1 ended at log %u on thread %s; SHPHLDCONFIG %d, USB disable %d, VDD_SD off %d; "
		 "at step 1's end: VDD_MIC %d, VDD_SD %d, USB %d, screen blanked %d, radio stops %u, beacon stopped %d\n",
		 at_ship.log_n, at_ship.thread, i_cfg, i_usb_off, i_sd_off, at_ship.mic, at_ship.sd, at_ship.usb,
		 at_ship.blanked, at_ship.radio_stops - radio0, at_ship.beacon_stopped);
	zassert_true(at_ship.called, "ship mode step 1 ran");
	zassert_true(i_cfg >= 0 && (uint32_t)i_cfg >= at_ship.log_n, "SHPHLDCONFIG after step 1");
	zassert_false(at_ship.mic, "recording closed (VDD_MIC off)");
	zassert_false(at_ship.sd, "storage closed (VDD_SD off)");
	zassert_true(i_sd_off >= 0 && i_sd_off < i_cfg, "VDD_SD off before SHPHLDCONFIG");
	zassert_false(at_ship.usb, "USB closed");
	zassert_true(i_usb_off >= 0 && i_usb_off < i_cfg, "USB disabled before SHPHLDCONFIG");
	zassert_equal(at_ship.radio_stops - radio0, 1u, "the radio stopped once (rdev_stop)");
	zassert_true(at_ship.blanked, "the screen closed (panel off) before SHPHLDCONFIG");
	zassert_false(at_ship.beacon_stopped, "the ship beacon still runs (ruling R20)");
	zassert_equal(strcmp(at_ship.thread, "rrec"), 0, "on the recorder's thread (%s)", at_ship.thread);
	rt_row_cleanup(70);
	zassert_true(rhw_sim_shipped(), "the ship task after VBUS removal");

	/* the menu's power off with the screen on (the status screen of a short press) */
	rt_fresh(NULL);
	rt_short();
	zassert_false(rt_blanked(), "the screen is on");
	memset(&at_ship, 0, sizeof(at_ship));
	rrec_test_set_ship_hook(ship_hook);
	rhw_sim_log_clear();
	rglue_event(RC_EV_MENU_POWER_OFF);
	rt_settle();
	rrec_test_set_ship_hook(NULL);
	i_cfg = rt_find(RHW_EV_PMIC_SHPHLD_CFG, -1, -1, 0);
	TC_PRINT("ship (menu): step 1 ended at log %u on thread %s, SHPHLDCONFIG %d, screen blanked %d\n", at_ship.log_n,
		 at_ship.thread, i_cfg, at_ship.blanked);
	zassert_true(at_ship.called && i_cfg >= 0 && (uint32_t)i_cfg >= at_ship.log_n, "step 1, then SHPHLDCONFIG");
	zassert_true(at_ship.blanked, "the screen closed before SHPHLDCONFIG");
	zassert_equal(strcmp(at_ship.thread, "rrec"), 0, "on the recorder's thread (%s)", at_ship.thread);
#else
	ztest_test_skip();
#endif
}


static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_ship, NULL, setup, NULL, NULL, NULL);
