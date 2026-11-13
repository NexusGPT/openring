/*
 * recorder_boot: the boot sequence of the join (plan rows C7, C8, C9, C16, P4, T24).
 */
#include <string.h>

#include <zephyr/sys/byteorder.h>

#include <ring_store/rst.h>
#include <ring_sys/rsy.h>

#include "rt.h"

/* FW l.893 (rule 1), l.133, l.134: with VBUS, BOOT turns the charger on before it mounts storage (C7, P4) */
ZTEST(recorder_boot, test_vbus_boot_charges_before_mount)
{
	struct rt_boot b = { .vbus = true };
	int32_t i_chg, i_init;

	rt_fresh(&b);
	i_chg = rt_find(RHW_EV_PMIC_CHG_ENABLE, 1, -1, 0);
	i_init = rt_find(RHW_EV_DISK_INIT, -1, -1, 0);
	TC_PRINT("boot with VBUS: charger enabled at %d, first card init at %d\n", i_chg, i_init);
	zassert_true(i_chg >= 0, "the charger was enabled");
	zassert_true(i_init > i_chg, "charge on before the mount");
	zassert_equal(rt_find(RHW_EV_PMIC_CHG_CURRENT, 15000, -1, 0) >= 0, true, "CHARGE_CURRENT 15,000 uA (FW l.878)");
	zassert_equal(rt_state(), RC_ST_CHARGING, "init done with VBUS: CHARGING (FW l.137)");
	/* the rows SHIP and OFF, VBUS appears: charge on (FW l.133, l.134) */
	zassert_equal(rt_run_row(1), 0, NULL);
	zassert_true(rt_row_seen(1), "row 1");
	zassert_true(rhw_sim_pmic_charger_on(), "charge on");
	zassert_equal(rt_run_row(2), 0, NULL);
	zassert_true(rt_row_seen(2), "row 2");
	zassert_true(rhw_sim_pmic_charger_on(), "charge on");
}

/* FW l.135 to l.140, l.216: each row of BOOT reached from the simulated facts (C8) */
ZTEST(recorder_boot, test_init_done_each_row)
{
	/* row: the state right after the row (FW 1.2 To column) */
	static const struct {
		int row;
		enum rc_state to;
	} r[] = {
		{ 3, RC_ST_STANDBY }, { 4, RC_ST_RECOVERY }, { 5, RC_ST_CHARGING },
		{ 6, RC_ST_ERR_STORAGE_FAULT }, { 7, RC_ST_OFF }, { 8, RC_ST_ERR_BATTERY_LOW },
	};

	for (size_t i = 0; i < ARRAY_SIZE(r); i++) {
		bool to_seen = false;

		zassert_equal(rt_run_row(r[i].row), 0, NULL);
		zassert_true(rt_row_seen(r[i].row), "row %d", r[i].row);
		for (uint32_t k = 0; k < rt_steps(); k++) {
			to_seen |= rt_step_get(k).row == r[i].row && rt_step_get(k).state == r[i].to;
		}
		zassert_true(to_seen, "row %d ends in %s", r[i].row, rc_state_name(r[i].to));
	}
	/* row 6: 3 tries 200 ms apart (FW l.138): three init calls */
	zassert_equal(rt_run_row(6), 0, NULL);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_DISK_INIT), RREC_INIT_TRIES, "3 init tries");
	zassert_equal(rrec_tap_count_code(RREC_LOG_FAULT_STORAGE_INIT), 1, "logged");
}

/* FW l.141 to l.143: RECOVERY ends with scan done (VBUS or not) or a read error (C9) */
ZTEST(recorder_boot, test_recovery_rows)
{
	zassert_equal(rt_run_row(9), 0, NULL);
	zassert_true(rt_row_seen(4) && rt_row_seen(9), "rows 4 and 9");
	zassert_equal(rt_state(), RC_ST_STANDBY, "STANDBY");
	zassert_false(rt_sd(), "VDD_SD off");
	zassert_equal(rt_run_row(10), 0, NULL);
	zassert_true(rt_row_seen(10), "row 10");
	zassert_equal(rt_state(), RC_ST_CHARGING, "CHARGING");
	zassert_true(rhw_sim_pmic_charger_on(), "charge on");
	zassert_equal(rt_run_row(11), 0, NULL);
	zassert_true(rt_row_seen(11), "row 11");
	zassert_equal(rt_state(), RC_ST_ERR_STORAGE_FAULT, "ERR_STORAGE_FAULT");
	zassert_equal(rrec_tap_count_code(RREC_LOG_FAULT_SCAN_READ), 1, "logged");
}

/* FW l.170, 5.5: a power loss during a write; the open flag leads to RECOVERY at the next start (C16) */
ZTEST(recorder_boot, test_restart_after_cut_recovers)
{
	struct rrec_tap_rec t;
	bool found = false;

	zassert_equal(rt_run_row(9), 0, NULL);   /* a recording, the power cut during a chunk write, a new boot */
	zassert_true(rt_cut_seen, "the cut happened (a chunk write was cut)");
	zassert_true(rt_row_seen(4), "init done with the open flag: RECOVERY");
	zassert_true(rt_row_seen(9), "scan done: STANDBY");
	for (uint32_t k = 0; rrec_tap_get(k, &t); k++) {
		found |= t.code == RREC_LOG_RECOVERY_DONE;
	}
	zassert_true(found, "RECOVERY_DONE logged");
	{
		/* the scan really ran: the recording is listed RECOVERED (FW l.697, l.646) */
		struct rst_mount_info mi;
		struct rst_rec_info info[4];
		uint16_t cnt = 0;

		zassert_equal(rst_mount(false, &mi), 0, "mount");
		zassert_false(mi.open_flag, "the open flag is clear on the card");
		zassert_equal(rst_list(0, 4, info, &cnt), 0, "list");
		(void)rst_unmount();
		zassert_equal(cnt, 1, "one recording");
		zassert_equal(info[0].state, RREC_LIST_STATE_RECOVERED, "state RECOVERED (%u)", info[0].state);
		TC_PRINT("recovered recording %u: %u chunks kept\n", info[0].recording_id, info[0].chunk_count);
	}
	/* a new recording can start after the recovery (the flag is clear) */
	rt_long();
	zassert_equal(rt_state(), RC_ST_RECORDING, "recording again");
	rt_long();
}

/* FW l.1043 to l.1056 (T24): boot_count does not change when VBUS goes and comes back in CHARGING and STANDBY */
ZTEST(recorder_boot, test_boot_count_only_at_boot)
{
	static uint8_t resp[64];
	uint8_t st;
	uint32_t b0, b1, b2;

	rt_fresh(NULL);
	b0 = rrec_st.boot_count;
	rt_vbus(true);
	rt_vbus(false);
	rt_vbus(true);
	rt_usb_configured();
	zassert_equal(rt_usb(RREC_OP_GET_INFO, NULL, 0, resp, sizeof(resp), &st) >= 16 + 35, true, "GET_INFO");
	zassert_equal(st, RREC_ST_OK, "OK");
	b1 = sys_get_le32(&resp[16 + RREC_GI_OFF_BOOT_COUNT]);
	TC_PRINT("boot_count at boot %u, after VBUS out and in twice %u\n", b0, b1);
	zassert_equal(b1, b0, "boot_count unchanged by VBUS");
	rt_vbus(false);
	rt_reboot(NULL);
	b2 = rrec_st.boot_count;
	zassert_equal(b2, b0 + 1, "one more at the next boot (%u, %u)", b0, b2);
}

/* FW l.1014 (T9, the join's part): a new image not yet confirmed runs the self-test; the join reports "storage mounted" at
 * the boot mount and "USB enumerated" at the configured event; Bluetooth is not enabled in these suites, so the test
 * gives that item itself; the microphones are never powered */
ZTEST(recorder_boot, test_selftest_items)
{
	struct rt_boot b = { .vbus = true, .unconfirmed = true };

	/* the image is not confirmed: storage and USB come from the join, Bluetooth from the test: confirmed */
	rt_fresh(&b);
	zassert_true(rsy_selftest_running(), "the self-test window runs");
	rt_usb_configured();
	rsy_selftest_pass(RSY_ITEM_BLUETOOTH);
	rt_settle();
	zassert_true(rt_find(RHW_EV_IMG_CONFIRM, -1, -1, 0) >= 0, "confirmed once storage, USB (join) and Bluetooth passed");
	zassert_equal(rt_count_rail(RHW_RAIL_MIC, true), 0, "no microphone in the self-test");
	/* without USB and Bluetooth: 30 s, then a reboot without confirming */
	rt_fresh(&b);
	rt_sleep(31000);
	rt_settle();
	zassert_equal(rt_find(RHW_EV_IMG_CONFIRM, -1, -1, 0), -1, "not confirmed");
	zassert_equal(rhw_sim_image_last_reboot(), RHW_REBOOT_SELFTEST_FAIL, "rebooted after 30 s (FW l.1014)");
	zassert_equal(rt_count_rail(RHW_RAIL_MIC, true), 0, "no microphone in the self-test");
}

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_boot, NULL, setup, NULL, NULL, NULL);
