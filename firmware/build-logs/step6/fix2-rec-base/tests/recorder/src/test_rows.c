/*
 * recorder_rows: every row of design/firmware.md 1.2 run from its From state through the real core, glue, screens,
 * recorder and units on the simulated drivers (plan rows C1, C14, C15, C17, C18, C20, C22, P11, T8).
 */
#include <string.h>

#include <zephyr/sys/byteorder.h>

#include "rt.h"

/* FW l.112 (rule C1): VDD_MIC is on only in RECORDING, and in FACTORY_TEST only inside a test recording */
static bool mic_rule_holds(void)
{
	enum rc_state s = rt_state();
	bool on = rt_mic();

	if (s == RC_ST_RECORDING) {
		return true;   /* on is required while the recording runs; a failed open leaves the state through its row */
	}
	if (s == RC_ST_FACTORY_TEST && atomic_get(&rrec_st.test_recording) != 0) {
		return true;
	}
	return !on;
}

ZTEST(recorder_rows, test_mic_rail_only_in_recording)
{
	int bad_rows = 0, unseen = 0, skipped = 0, checks = 0;

	for (int row = 1; row <= 72; row++) {
		int r = rt_run_row(row);
		int bad = 0;
		bool t_mic_seen_on = false;

		if (r == -ENOTSUP) {
			TC_PRINT("ROW %d: NOT RUN (needs the factory part)\n", row);
			skipped++;
			continue;
		}
		if (row == 49 && rt_state() == RC_ST_FACTORY_TEST) {
			/* FACTORY_TEST: a test recording (T-MIC1, FW l.1024) runs while the rule is checked */
			static uint8_t req[RREC_MSG_HEADER_BYTES + 2];
			uint8_t pl[2] = { RREC_FAC_MIC, 1 };

			sys_put_le16(RREC_MSG_MAGIC, &req[0]);
			req[2] = RREC_OP_FACTORY;
			req[3] = 0;
			sys_put_le32(0x4949, &req[4]);
			sys_put_le32(2, &req[8]);
			sys_put_le32(crc32_ieee(pl, 2), &req[12]);
			memcpy(&req[16], pl, 2);
			(void)rhw_sim_usb_host_write(req, sizeof(req));
		}
		for (int tick = 0; tick <= 100; tick++) {
			checks++;
			if (atomic_get(&rrec_st.test_recording) != 0 && rt_mic()) {
				t_mic_seen_on = true;
			}
			if (!mic_rule_holds()) {
				if (bad < 3) {
					TC_PRINT("ROW %d: VDD_MIC on in %s at tick %d\n", row, rc_state_name(rt_state()), tick);
				}
				bad++;
			}
			if (rt_state() == RC_ST_RECORDING && !rt_mic() && tick == 0) {
				TC_PRINT("ROW %d: RECORDING without VDD_MIC\n", row);
				bad++;
			}
			rt_sleep(100);
		}
		if (row == 49) {
			TC_PRINT("ROW 49: test recording in FACTORY_TEST, VDD_MIC seen on inside it: %s\n",
				 t_mic_seen_on ? "yes" : "no");
		}
		if (rt_mic_at_screens() != 0) {
			TC_PRINT("ROW %d: the screens learned of a state other than RECORDING with VDD_MIC on (%u)\n", row,
				 rt_mic_at_screens());
			bad++;
		}
		rt_row_cleanup(row);   /* first: ship mode holds the step until VBUS goes (rows 68, 70, 71) */
		if (!rt_row_seen(row)) {
			TC_PRINT("ROW %d: the row was not taken (state now %s)\n", row, rc_state_name(rt_state()));
			unseen++;
		}
		TC_PRINT("ROW %d %s -> %s: taken %s, now %s, VDD_MIC checks %s\n", row,
			 rc_state_name((enum rc_state)rt_row(row)->from), rc_state_name((enum rc_state)rt_row(row)->to),
			 rt_row_seen(row) ? "yes" : "no", rc_state_name(rt_state()), bad == 0 ? "ok" : "FAILED");
		bad_rows += bad != 0 ? 1 : 0;
	}
	TC_PRINT("ROWS: 72 rows, %d not run, %d not taken, %d with a VDD_MIC fault, %d checks\n", skipped, unseen, bad_rows,
		 checks);
	zassert_equal(bad_rows, 0, "VDD_MIC on outside RECORDING (and outside a test recording) in %d rows", bad_rows);
	zassert_equal(unseen, 0, "%d rows were not taken", unseen);
}

/* FW l.162: VBUS during a recording: close; M2; charge on (C14) */
ZTEST(recorder_rows, test_vbus_in_recording)
{
	int32_t i_off, i_m2;

	rt_fresh(NULL);
	rt_long();
	zassert_equal(rt_state(), RC_ST_RECORDING, "recording");
	rt_sleep(1200);
	rhw_sim_log_clear();
	rt_vbus(true);
	zassert_true(rt_row_seen(30), "row 30 (FW l.162)");
	zassert_equal(rt_state(), RC_ST_CHARGING, "CHARGING (FW l.162)");
	zassert_false(rrec_st.recording, "the recording is closed");
	zassert_false(rt_mic(), "VDD_MIC off");
	zassert_false(rt_sd(), "VDD_SD off");
	zassert_true(rhw_sim_pmic_charger_on(), "charge on");
	i_off = rt_find_rail(RHW_RAIL_MIC, false, 0);
	i_m2 = rt_find(RHW_EV_MOTOR, 1, -1, 0);
	zassert_true(i_off >= 0 && i_m2 > i_off, "M2 after VDD_MIC off (%d, %d)", i_off, i_m2);
}

/* FW l.163 to l.169: the ways a recording ends without a press (C15) */
ZTEST(recorder_rows, test_recording_exits)
{
	struct rt_boot b;

	/* B5: close; M3 (FW l.164) */
	zassert_equal(rt_run_row(32), 0, NULL);
	zassert_true(rt_row_seen(32), "row 32");
	zassert_equal(rt_state(), RC_ST_ERR_BATTERY_LOW, "ERR_BATTERY_LOW");
	zassert_false(rrec_st.recording, "closed");
	zassert_true(rrec_tap_count_code(RREC_LOG_MOTOR_PATTERN) > 0, "a pattern played");
	/* B2: close; ship mode (FW l.165) */
	zassert_equal(rt_run_row(33), 0, NULL);
	zassert_true(rt_row_seen(33), "row 33");
	zassert_equal(rt_state(), RC_ST_OFF, "OFF");
	zassert_true(rhw_sim_shipped(), "the ship task was written");
	/* S30: M3 once; the recording goes on (FW l.166) */
	zassert_equal(rt_run_row(34), 0, NULL);
	zassert_true(rt_row_seen(34), "row 34");
	zassert_equal(rt_state(), RC_ST_RECORDING, "still recording");
	zassert_equal(rrec_tap_count_code(RREC_LOG_STORAGE_S30), 1, "S30 logged once");
	/* SFULL: close; M3 (FW l.167) */
	zassert_equal(rt_run_row(35), 0, NULL);
	zassert_true(rt_row_seen(35), "row 35");
	zassert_equal(rt_state(), RC_ST_ERR_STORAGE_FULL, "ERR_STORAGE_FULL");
	zassert_false(rrec_st.recording, "closed");
	/* 3 failed chunk writes: stop PDM, clocks low, VDD_MIC off, superblock left open, MF (FW l.168) */
	zassert_equal(rt_run_row(36), 0, NULL);
	zassert_true(rt_row_seen(36), "row 36");
	zassert_equal(rt_state(), RC_ST_ERR_STORAGE_FAULT, "ERR_STORAGE_FAULT");
	zassert_false(rt_mic(), "VDD_MIC off");
	zassert_true(rhw_sim_mic_pins_asleep(), "clocks low (sleep state)");
	zassert_true(rt_find(RHW_EV_MIC_STOP, -1, -1, 0) >= 0, "PDM stopped");
	memset(&b, 0, sizeof(b));
	rt_reboot(&b);
	zassert_true(rt_row_seen(4), "the superblock was left open: the next boot recovers (row 4)");
	/* no PDM block for 100 ms: close; MF (FW l.169) */
	zassert_equal(rt_run_row(37), 0, NULL);
	zassert_true(rt_row_seen(37), "row 37");
	zassert_equal(rt_state(), RC_ST_ERR_MIC_FAULT, "ERR_MIC_FAULT");
	zassert_false(rt_mic(), "VDD_MIC off");
	zassert_equal(rrec_tap_count_code(RREC_LOG_FAULT_MIC), 1, "the fault logged");
}

/* FW l.171: USB configured in CHARGING: TRANSFER, VDD_SD on, mount, charge stays on (C17, X4) */
ZTEST(recorder_rows, test_usb_configured)
{
	rt_fresh(NULL);
	rt_vbus(true);
	zassert_equal(rt_state(), RC_ST_CHARGING, "CHARGING");
	zassert_true(rhw_sim_usb_enabled(), "the USB stack runs with VBUS (FW l.978)");
	rt_usb_configured();
	zassert_true(rt_row_seen(39), "row 39");
	zassert_equal(rt_state(), RC_ST_TRANSFER, "TRANSFER");
	zassert_true(rt_sd(), "VDD_SD on");
	zassert_true(rhw_sim_pmic_charger_on(), "charge on stays");
}

/* FW l.178 to l.181 (C18) and l.180 (T8) */
ZTEST(recorder_rows, test_transfer_rows)
{
	zassert_equal(rt_run_row(46), 0, NULL);
	zassert_true(rt_row_seen(46), "row 46");
	zassert_equal(rt_state(), RC_ST_CHARGING, "unconfigured: CHARGING");
	zassert_false(rt_sd(), "VDD_SD off");
	zassert_true(rhw_sim_pmic_charger_on(), "charge on");
	zassert_equal(rt_run_row(47), 0, NULL);
	zassert_true(rt_row_seen(47), "row 47");
	zassert_false(rt_sd(), "VDD_SD off");
	zassert_false(rhw_sim_usb_enabled(), "the stack is off without VBUS");
#if defined(CONFIG_RING_FACTORY)
	zassert_equal(rt_run_row(49), 0, NULL);
	zassert_true(rt_row_seen(49), "row 49");
	zassert_equal(rt_state(), RC_ST_FACTORY_TEST, "FACTORY_TEST");
#endif
}

ZTEST(recorder_rows, test_fw_end_row)
{
	zassert_equal(rt_run_row(48), 0, NULL);
	zassert_true(rt_row_seen(48), "row 48 (FW l.180)");
	zassert_true(rhw_sim_image_upgrade_requested(), "boot_request_upgrade(BOOT_UPGRADE_TEST)");
	zassert_equal(rhw_sim_image_reboots(), 1, "one reboot");
	zassert_equal(rhw_sim_image_last_reboot(), RHW_REBOOT_UPDATE, "reboot after FW_END");
}

/* R-CHG and ruling R8 (FW l.210): charge on at every VBUS appearance, in every state (C22) */
ZTEST(recorder_rows, test_charge_on_every_vbus_row)
{
	static const int rows[] = { 1, 2, 5, 10, 20, 30, 51, 55, 58, 65 };
	struct rt_boot b = { .vbus = true };

	for (size_t i = 0; i < ARRAY_SIZE(rows); i++) {
		zassert_equal(rt_run_row(rows[i]), 0, NULL);
		zassert_true(rt_row_seen(rows[i]), "row %d", rows[i]);
		zassert_true(rhw_sim_pmic_charger_on(), "charger on after row %d", rows[i]);
		zassert_equal(rhw_sim_pmic_charger_ua(), 15000, "CHARGE_CURRENT 15,000 uA (FW l.878)");
	}
	/* BOOT with VBUS (no row: R8) */
	rt_fresh(&b);
	zassert_true(rhw_sim_pmic_charger_on(), "charger on in BOOT");
}

/* FW l.201 to l.204 (C20) */
ZTEST(recorder_rows, test_factory_rows)
{
#if defined(CONFIG_RING_FACTORY)
	struct rhw_persist p;

	zassert_equal(rt_run_row(69), 0, NULL);
	zassert_true(rt_row_seen(69), "row 69");
	zassert_equal(rhw_sim_image_last_reboot(), RHW_REBOOT_FACTORY_EXIT, "reboot (FW l.201)");
	zassert_equal(rt_run_row(70), 0, NULL);
	rt_row_cleanup(70);   /* ship mode holds the step until VBUS goes: the row is logged after it */
	zassert_true(rt_row_seen(70), "row 70");
	rhw_sim_persist_get(&p);
	zassert_equal(p.factory_flag, 0, "SHIP_ENTER clears the flag (FW l.202)");
	zassert_true(rhw_sim_shipped(), "ship task after VBUS removal");
	zassert_equal(rt_run_row(71), 0, NULL);
	rt_row_cleanup(71);
	zassert_true(rt_row_seen(71), "row 71");
	rhw_sim_persist_get(&p);
	zassert_equal(p.factory_flag, 1, "SHIP_SAMPLE keeps the flag (FW l.203)");
	zassert_equal(rt_run_row(72), 0, NULL);
	zassert_true(rt_row_seen(72), "row 72");
	zassert_equal(rhw_sim_image_last_reboot(), RHW_REBOOT_FACTORY_VBUS, "reboot (FW l.204)");
#else
	ztest_test_skip();
#endif
}

/* P11: the level reaches the core on every change, both ways; B2 before B5 when VBUS goes (FW l.211, l.213) */
ZTEST(recorder_rows, test_vbus_out_at_b2_goes_off)
{
	struct rt_boot b = { .mv = 3400, .mv_next = 3900 };

	zassert_equal(rt_run_row(42), 0, NULL);
	zassert_true(rt_row_seen(42), "row 42");
	zassert_equal(rt_state(), RC_ST_OFF, "OFF");
	/* up: B5 at boot, then a sample above: the fact goes back to OK (the level is reported upward too) */
	rt_fresh(&b);
	zassert_equal(rt_state(), RC_ST_ERR_BATTERY_LOW, "B5 at boot");
	zassert_equal(rglue_core()->facts.batt, RC_BATT_B5, "fact B5");
	rt_sleep(61000);
	rt_settle();
	zassert_equal(rglue_core()->facts.batt, RC_BATT_OK, "fact back to OK after the rise");
}

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_rows, NULL, setup, NULL, NULL, NULL);
