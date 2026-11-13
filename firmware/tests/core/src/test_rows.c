/*
 * One test per row of the transition table, design/firmware.md section 1.2 (F6 with F7 part 1, R4b, R9 to R14).
 * test_row_NN: NN is the row number (row 1 is line 133 of the document, row NN is line 132 + NN).
 * Step 6: row 16 is new (recording sign not drawn); the old rows 16 to 71 are now 17 to 72.
 * Each test asserts the row taken, the to-state and the exact action list of the row.
 * Press rows use the real switch input (SW2); timer rows use rc_core_tick.
 */
#include <string.h>
#include "th.h"

#define F (rc_core_facts(&core))
#define A(x) RC_ACT_##x

#define ROW(name, num, from, to, prep, act, ...) \
	ZTEST(rc_rows, test_row_##name) \
	{ \
		th_start(RC_ST_##from); \
		prep; \
		act; \
		zassert_equal(out.last_row, num, "row taken"); \
		zassert_equal(rc_core_state(&core), RC_ST_##to, "to-state"); \
		TH_EXPECT(__VA_ARGS__); \
	}

#define EV(e) th_event(RC_EV_##e)
#define BATT(l) th_batt(RC_BATT_##l)
#define KEEP(l) rc_core_battery(&core, RC_BATT_##l, th_now, &rest)
#define NOPREP ((void)0)
/* the sign hook of the core, answering a fixed value (0 = drawn) */
static int sign_answer;
static int sign_calls;
static int sign_fn(void *ctx, rc_ms_t t)
{
	(void)ctx;
	(void)t;
	sign_calls++;
	return sign_answer;
}
#define SIGN(x) do { sign_answer = (strcmp(#x, "REFUSE") == 0) ? -1 : 0; sign_calls = 0; \
	rc_core_set_sign_hook(&core, sign_fn, NULL); } while (0)
#define TIMER(ms) do { rc_actions_clear(&rest); th_tick_to(TH_T0 + (ms) - 1, &rest); \
	zassert_equal(rest.n, 0); rc_actions_clear(&out); th_tick_to(TH_T0 + (ms), &out); } while (0)

ROW(01, 1, SHIP, BOOT, NOPREP, EV(VBUS_IN), A(CHARGE_ON))
ROW(02, 2, OFF, BOOT, NOPREP, EV(VBUS_IN), A(CHARGE_ON))
ROW(03, 3, BOOT, STANDBY, NOPREP, EV(INIT_DONE), A(SD_OFF))
ROW(04, 4, BOOT, RECOVERY, F->open_flag = true, EV(INIT_DONE), A(SD_ON))
ROW(05, 5, BOOT, CHARGING, F->vbus = true, EV(INIT_DONE), A(SD_OFF), A(CHARGE_ON))
ROW(06, 6, BOOT, ERR_STORAGE_FAULT, NOPREP, EV(STORAGE_INIT_FAILED), A(LOG_EVENT), A(MF))
/* rows 7 and 8: a battery level that arrives in BOOT is kept and applied at "init done" (R12) */
ROW(07, 7, BOOT, OFF, KEEP(B2), EV(INIT_DONE), A(SHIP_MODE))
ROW(08, 8, BOOT, ERR_BATTERY_LOW, KEEP(B5), EV(INIT_DONE), A(SD_OFF), A(M3))
ROW(09, 9, RECOVERY, STANDBY, NOPREP, EV(SCAN_DONE), A(WRITE_CLOSE_RECOVERED), A(CLEAR_OPEN_FLAG), A(SD_OFF))
ROW(10, 10, RECOVERY, CHARGING, F->vbus = true, EV(SCAN_DONE),
    A(WRITE_CLOSE_RECOVERED), A(CLEAR_OPEN_FLAG), A(SD_OFF), A(CHARGE_ON))
ROW(11, 11, RECOVERY, ERR_STORAGE_FAULT, NOPREP, EV(SCAN_READ_ERROR), A(LOG_EVENT), A(MF))
ROW(12, 12, STANDBY, RECORDING, NOPREP, th_long(), A(M1), A(OPEN))  /* ruling R21: M1 first, then open */
ROW(13, 13, STANDBY, RECOVERY, F->open_flag = true, th_long(), A(SD_ON), A(MOUNT))
ROW(14, 14, STANDBY, STANDBY, F->batt = RC_BATT_B5, th_long(), A(SCR_MSG_BATTERY_LOW_3S))
ROW(15, 15, STANDBY, STANDBY, F->storage_full = true, th_long(), A(SCR_MSG_STORAGE_FULL_3S))
/* row 16 (step 6): the sign hook refuses; no recording, M3, event log record, no OPEN */
ROW(16, 16, STANDBY, STANDBY, SIGN(REFUSE), th_long(), A(M3), A(LOG_EVENT))
ROW(17, 17, STANDBY, STANDBY, NOPREP, th_short(), A(SCREEN_ON), A(SCR_STATUS_5S))
ROW(18, 18, STANDBY, STANDBY, NOPREP, th_double())
ROW(19, 19, STANDBY, OFF, NOPREP, EV(MENU_POWER_OFF), A(SAVE_SETTINGS_TIME), A(M2), A(SHIP_MODE))
ROW(20, 20, STANDBY, CHARGING, NOPREP, EV(VBUS_IN), A(CHARGE_ON))
ROW(21, 21, STANDBY, STANDBY, NOPREP, BATT(B15), A(M3), A(SCR_STATUS_5S))
ROW(22, 22, STANDBY, ERR_BATTERY_LOW, NOPREP, BATT(B5), A(M3))
ROW(23, 23, STANDBY, OFF, NOPREP, BATT(B2), A(SAVE_SETTINGS_TIME), A(SHIP_MODE))
ROW(24, 24, STANDBY, ERR_STORAGE_FULL, NOPREP, EV(STORAGE_SFULL), A(M3))
/* row 25 is reached only through rule R-STB: ERR_MIC_FAULT 5 s elapsed (row 64, no actions) into STANDBY with the storage fault set */
ROW(25, 25, ERR_MIC_FAULT, ERR_STORAGE_FAULT, F->storage_fault = true, TIMER(SPEC_MIC_FAULT_MS))
ROW(26, 26, RECORDING, STANDBY, NOPREP, th_long(), A(CLOSE), A(M2))
ROW(27, 27, RECORDING, RECORDING, NOPREP, th_short(), A(HIGHLIGHT), A(MH), A(SCR_RECORDING_3S))
ROW(28, 28, RECORDING, RECORDING, NOPREP, th_double())
ROW(29, 29, RECORDING, RECORDING, NOPREP, EV(BLE_HIGHLIGHT), A(HIGHLIGHT), A(MH))
ROW(30, 30, RECORDING, CHARGING, NOPREP, EV(VBUS_IN), A(CLOSE), A(M2), A(CHARGE_ON))
ROW(31, 31, RECORDING, RECORDING, NOPREP, BATT(B15), A(M3))
ROW(32, 32, RECORDING, ERR_BATTERY_LOW, NOPREP, BATT(B5), A(CLOSE), A(M3))
ROW(33, 33, RECORDING, OFF, NOPREP, BATT(B2), A(CLOSE), A(SHIP_MODE))
ROW(34, 34, RECORDING, RECORDING, NOPREP, EV(STORAGE_S30), A(M3), A(SCR_MSG_30MIN_3S))
ROW(35, 35, RECORDING, ERR_STORAGE_FULL, NOPREP, EV(STORAGE_SFULL), A(CLOSE), A(M3))
ROW(36, 36, RECORDING, ERR_STORAGE_FAULT, NOPREP, EV(CHUNK_WRITE_FAILED),
    A(STOP_PDM), A(CLOCKS_LOW), A(MIC_OFF), A(MF))
ROW(37, 37, RECORDING, ERR_MIC_FAULT, NOPREP, EV(MIC_NO_BLOCK), A(CLOSE), A(MF))
ROW(38, 38, RECORDING, BOOT, NOPREP, EV(POWER_LOSS))
ROW(39, 39, CHARGING, TRANSFER, F->vbus = true, EV(USB_CONFIGURED), A(SD_ON), A(MOUNT))
ROW(40, 40, CHARGING, STANDBY, F->vbus = true, EV(VBUS_OUT))
ROW(41, 41, CHARGING, ERR_STORAGE_FULL, (F->vbus = true, F->storage_full = true), EV(VBUS_OUT))
ROW(42, 42, CHARGING, OFF, (F->vbus = true, F->batt = RC_BATT_B2), EV(VBUS_OUT), A(SAVE_SETTINGS_TIME), A(SHIP_MODE))
ROW(43, 43, CHARGING, ERR_BATTERY_LOW, (F->vbus = true, F->batt = RC_BATT_B5), EV(VBUS_OUT))
ROW(44, 44, CHARGING, ERR_CHARGER, F->vbus = true, EV(CHARGE_ERROR), A(LOG_CHARGE_ERROR), A(CHARGE_OFF), A(MF))
ROW(45, 45, CHARGING, CHARGING, F->vbus = true, th_long(), A(M3), A(SCR_MSG_IN_CASE_3S))
ROW(46, 46, TRANSFER, CHARGING, F->vbus = true, EV(USB_UNCONFIGURED), A(FINISH_COMMAND), A(SD_OFF), A(CHARGE_ON))
ROW(47, 47, TRANSFER, STANDBY, F->vbus = true, EV(VBUS_OUT), A(ABORT_COMMAND), A(SD_OFF))
ROW(48, 48, TRANSFER, BOOT, F->vbus = true, EV(FW_END), A(REQUEST_UPGRADE_TEST), A(REBOOT))
ROW(49, 49, TRANSFER, FACTORY_TEST, (F->vbus = true, F->factory_flag = true), EV(FACTORY_ENTER), A(FACTORY_MODE))
ROW(50, 50, TRANSFER, TRANSFER, F->vbus = true, th_long(), A(M3))
ROW(51, 51, ERR_STORAGE_FULL, CHARGING, F->storage_full = true, EV(VBUS_IN), A(CHARGE_ON))
ROW(52, 52, ERR_STORAGE_FULL, ERR_STORAGE_FULL, F->storage_full = true, th_long(), A(M3), A(SCR_MSG_STORAGE_FULL_3S))
ROW(53, 53, ERR_STORAGE_FULL, ERR_BATTERY_LOW, F->storage_full = true, BATT(B5), A(M3))
ROW(54, 54, ERR_STORAGE_FULL, OFF, F->storage_full = true, BATT(B2), A(SHIP_MODE))
ROW(55, 55, ERR_BATTERY_LOW, CHARGING, F->batt = RC_BATT_B5, EV(VBUS_IN), A(CHARGE_ON))
ROW(56, 56, ERR_BATTERY_LOW, ERR_BATTERY_LOW, F->batt = RC_BATT_B5, th_long(), A(M3), A(SCR_MSG_BATTERY_LOW_3S))
ROW(57, 57, ERR_BATTERY_LOW, OFF, F->batt = RC_BATT_B5, BATT(B2), A(SAVE_SETTINGS_TIME), A(SHIP_MODE))
ROW(58, 58, ERR_STORAGE_FAULT, CHARGING, NOPREP, EV(VBUS_IN), A(CHARGE_ON))
ROW(59, 59, ERR_STORAGE_FAULT, ERR_STORAGE_FAULT, NOPREP, TIMER(SPEC_STORAGE_RETRY_MS), A(RETRY_STORAGE))
ROW(60, 60, ERR_STORAGE_FAULT, RECOVERY, F->open_flag = true, EV(STORAGE_RETRY_OK), A(SD_ON))
ROW(61, 61, ERR_STORAGE_FAULT, STANDBY, NOPREP, EV(STORAGE_RETRY_OK))
ROW(62, 62, ERR_STORAGE_FAULT, ERR_STORAGE_FAULT, NOPREP, EV(STORAGE_RETRY_FAILED))
ROW(63, 63, ERR_STORAGE_FAULT, OFF, NOPREP, BATT(B2), A(SHIP_MODE))
ROW(64, 64, ERR_MIC_FAULT, STANDBY, NOPREP, TIMER(SPEC_MIC_FAULT_MS))
ROW(65, 65, ERR_MIC_FAULT, CHARGING, NOPREP, EV(VBUS_IN), A(CHARGE_ON))
ROW(66, 66, ERR_MIC_FAULT, OFF, NOPREP, BATT(B2), A(SAVE_SETTINGS_TIME), A(SHIP_MODE))
ROW(67, 67, ERR_CHARGER, STANDBY, F->vbus = true, EV(VBUS_OUT))
ROW(68, 68, ERR_CHARGER, OFF, NOPREP, BATT(B2), A(SAVE_SETTINGS_TIME), A(SHIP_MODE))
ROW(69, 69, FACTORY_TEST, BOOT, (F->vbus = true, F->factory_flag = true), EV(FACTORY_EXIT), A(REBOOT))
ROW(70, 70, FACTORY_TEST, SHIP, (F->vbus = true, F->factory_flag = true), EV(SHIP_ENTER),
    A(CLEAR_FACTORY_FLAG), A(SHIP_MODE))
ROW(71, 71, FACTORY_TEST, SHIP, (F->vbus = true, F->factory_flag = true), EV(SHIP_SAMPLE), A(SHIP_MODE))
ROW(72, 72, FACTORY_TEST, BOOT, (F->vbus = true, F->factory_flag = true), EV(VBUS_OUT), A(REBOOT))

ZTEST_SUITE(rc_rows, NULL, NULL, NULL, NULL, NULL);

/* Rows whose actions depend on a condition the row states: the other branch. */
ZTEST(rc_row_variants, test_r6_row17_screen_on_centre_action_then_mt)
{
	/* line 149 (ruling R6): "screen on: the centre action of the screen (section 2.2), then MT" */
	th_start(RC_ST_STANDBY);
	F->screen_on = true;
	th_short();
	zassert_equal(out.last_row, 17);
	TH_EXPECT(A(SCREEN_CENTRE), A(MT));
}

ZTEST(rc_row_variants, test_row20_m3_once_per_discharge)
{
	/* line 152: "M3 once per discharge" */
	th_start(RC_ST_STANDBY);
	th_batt(RC_BATT_B15);
	zassert_true(th_has(&out, RC_ACT_M3));
	th_batt(RC_BATT_OK);
	zassert_equal(out.n, 0);
	th_batt(RC_BATT_B15);
	zassert_equal(out.last_row, 21);
	zassert_false(th_has(&out, RC_ACT_M3));
}

ZTEST(rc_row_variants, test_row30_m3_once_per_discharge)
{
	/* lines 152 and 162: B15 already warned in STANDBY, then a recording reaches B15 again */
	th_start(RC_ST_STANDBY);
	th_batt(RC_BATT_B15);
	zassert_true(th_has(&out, RC_ACT_M3));
	th_long();
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING);
	th_batt(RC_BATT_OK);
	th_batt(RC_BATT_B15);
	zassert_equal(out.last_row, 31);
	zassert_false(th_has(&out, RC_ACT_M3));
}

ZTEST(rc_row_variants, test_row33_m3_once)
{
	/* line 165: "M3 once" */
	th_start(RC_ST_RECORDING);
	th_event(RC_EV_STORAGE_S30);
	zassert_true(th_has(&out, RC_ACT_M3));
	th_event(RC_EV_STORAGE_S30);
	zassert_equal(out.last_row, 34);
	zassert_false(th_has(&out, RC_ACT_M3));
}

ZTEST(rc_row_variants, test_row48_needs_factory_flag)
{
	/* line 180: "with the factory flag set" */
	th_start(RC_ST_TRANSFER);
	F->vbus = true;
	th_event(RC_EV_FACTORY_ENTER);
	zassert_equal(out.last_row, -1);
	zassert_equal(rc_core_state(&core), RC_ST_TRANSFER);
}

ZTEST_SUITE(rc_row_variants, NULL, NULL, NULL, NULL, NULL);
