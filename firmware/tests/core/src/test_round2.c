/*
 * Round 2: one or more tests per ruling R1 to R8 and C1 to C6 of
 * firmware/docs/core-delta-1.md, as written into design/firmware.md (F7 part 1).
 * Line numbers are those of F7 part 1.
 */
#include "th.h"

#define F (rc_core_facts(&core))
#define A(x) RC_ACT_##x

/* ---- R1: row 12 guard, refusal rows 14 and 15, rule R-STB (lines 144 to 147, 205) ---- */

ZTEST(rc_round2, test_r1_long_press_at_b5_refused_with_message)
{
	th_start(RC_ST_STANDBY);
	F->batt = RC_BATT_B5;
	th_long();
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
	zassert_false(th_has(&out, RC_ACT_OPEN));
	zassert_false(rc_core_mic_rail(&core));
	TH_EXPECT(A(SCR_MSG_BATTERY_LOW_3S));
}

ZTEST(rc_round2, test_r1_long_press_at_sfull_refused_with_message)
{
	th_start(RC_ST_STANDBY);
	F->storage_full = true;
	th_long();
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
	TH_EXPECT(A(SCR_MSG_STORAGE_FULL_3S));
}

ZTEST(rc_round2, test_r1_long_press_at_b5_and_sfull_battery_message)
{
	/* row 14 comes before row 15 (battery first) */
	th_start(RC_ST_STANDBY);
	F->batt = RC_BATT_B2;
	F->storage_full = true;
	th_long();
	zassert_equal(out.last_row, 14);
	TH_EXPECT(A(SCR_MSG_BATTERY_LOW_3S));
}

static void entry_case(enum rc_state from, bool vbus, enum rc_event ev, rc_ms_t tick_ms,
		       uint8_t batt, bool full, enum rc_state want, int want_row)
{
	th_start(from);
	F->vbus = vbus;
	F->batt = batt;
	F->storage_full = full;
	if (tick_ms > 0) {
		rc_actions_clear(&out);
		th_tick_to(TH_T0 + tick_ms, &out);
	} else {
		th_event(ev);
	}
	zassert_equal(rc_core_state(&core), want, "from %d", from);
	zassert_equal(out.last_row, want_row, "from %d", from);
}

ZTEST(rc_round2, test_r1_entry_into_standby_checks_battery_then_storage)
{
	/* rule R-STB: B2 to OFF (row 22), B5 to ERR_BATTERY_LOW (row 21), SFULL to ERR_STORAGE_FULL (row 23), battery first */
	entry_case(RC_ST_TRANSFER, true, RC_EV_VBUS_OUT, 0, RC_BATT_B2, false, RC_ST_OFF, 23);
	entry_case(RC_ST_TRANSFER, true, RC_EV_VBUS_OUT, 0, RC_BATT_B5, true, RC_ST_ERR_BATTERY_LOW, 22);
	entry_case(RC_ST_TRANSFER, true, RC_EV_VBUS_OUT, 0, RC_BATT_OK, true, RC_ST_ERR_STORAGE_FULL, 24);
	entry_case(RC_ST_ERR_STORAGE_FAULT, false, RC_EV_STORAGE_RETRY_OK, 0, RC_BATT_B5, false, RC_ST_ERR_BATTERY_LOW, 22);
	entry_case(RC_ST_ERR_MIC_FAULT, false, RC_EV_TIMER_5S, SPEC_MIC_FAULT_MS, RC_BATT_OK, true, RC_ST_ERR_STORAGE_FULL, 24);
	/* since R16 the B2 row of ERR_CHARGER (67) comes before its VBUS removed row; before R16: row 22 through STANDBY */
	entry_case(RC_ST_ERR_CHARGER, true, RC_EV_VBUS_OUT, 0, RC_BATT_B2, false, RC_ST_OFF, 68);
	/* with good facts the ring stays in STANDBY */
	entry_case(RC_ST_TRANSFER, true, RC_EV_VBUS_OUT, 0, RC_BATT_B15, false, RC_ST_STANDBY, 47);
}

ZTEST(rc_round2, test_r1_entry_actions_are_those_of_the_standby_row)
{
	/* TRANSFER, VBUS removed (row 46), battery at B5: then row 21 (M3) */
	th_start(RC_ST_TRANSFER);
	F->vbus = true;
	F->batt = RC_BATT_B5;
	th_event(RC_EV_VBUS_OUT);
	TH_EXPECT(A(ABORT_COMMAND), A(SD_OFF), A(M3));
}

/* ---- R2: row 40 guard (line 171) ---- */

ZTEST(rc_round2, test_r2_vbus_out_with_sfull_and_b5_gives_battery_low)
{
	th_start(RC_ST_CHARGING);
	F->vbus = true;
	F->storage_full = true;
	F->batt = RC_BATT_B5;
	th_event(RC_EV_VBUS_OUT);
	zassert_equal(out.last_row, 43);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_BATTERY_LOW);
}

/* ---- R3: storage tried again every 60 s (rows 56 to 58) ---- */

ZTEST(rc_round2, test_r3_storage_retried_every_60s_until_success)
{
	th_start(RC_ST_ERR_STORAGE_FAULT);
	for (int k = 1; k <= 3; k++) {
		rc_actions_clear(&out);
		th_tick_to(TH_T0 + k * SPEC_STORAGE_RETRY_MS - 1, &out);
		zassert_equal(out.n, 0, "try %d early", k);
		th_tick_to(TH_T0 + k * SPEC_STORAGE_RETRY_MS, &out);
		TH_EXPECT(A(RETRY_STORAGE));
		zassert_equal(rc_core_next_tick(&core), TH_T0 + (k + 1) * SPEC_STORAGE_RETRY_MS);
		th_event(RC_EV_STORAGE_RETRY_FAILED);
		zassert_equal(out.last_row, 62);
		zassert_equal(rc_core_state(&core), RC_ST_ERR_STORAGE_FAULT);
	}
	th_event(RC_EV_STORAGE_RETRY_OK);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
	zassert_equal(rc_core_next_tick(&core), RC_NO_TICK);
}

/* ---- R4, R5: order at init done (lines 206, 207) ---- */

ZTEST(rc_round2, test_r4_unfinished_recording_with_case_recovery_then_charging)
{
	th_start(RC_ST_BOOT);
	F->open_flag = true;
	F->vbus = true;
	th_event(RC_EV_INIT_DONE);
	zassert_equal(out.last_row, 4);
	zassert_equal(rc_core_state(&core), RC_ST_RECOVERY);
	th_event(RC_EV_SCAN_DONE);
	zassert_equal(out.last_row, 10);
	zassert_equal(rc_core_state(&core), RC_ST_CHARGING);
}

ZTEST(rc_round2, test_r5_init_done_reads_battery_first)
{
	th_start(RC_ST_BOOT);
	F->batt = RC_BATT_B2;
	th_event(RC_EV_INIT_DONE);
	zassert_equal(out.last_row, 7);
	zassert_equal(rc_core_state(&core), RC_ST_OFF);
	TH_EXPECT(A(SHIP_MODE));

	th_start(RC_ST_BOOT);
	F->batt = RC_BATT_B5;
	th_event(RC_EV_INIT_DONE);
	zassert_equal(out.last_row, 8);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_BATTERY_LOW);

	th_start(RC_ST_BOOT);
	F->batt = RC_BATT_B5;
	F->vbus = true;
	th_event(RC_EV_INIT_DONE);
	zassert_equal(out.last_row, 5, "with VBUS present the battery rows do not apply (they need no VBUS)");

	th_start(RC_ST_BOOT);
	F->batt = RC_BATT_B15;
	th_event(RC_EV_INIT_DONE);
	zassert_equal(out.last_row, 3);
}

/* ---- R4b (lead's correction): recovery before battery low; no recording while the open flag is set (lines 145, 206, 207) ---- */

ZTEST(rc_round2, test_r4b_b5_with_open_flag_at_init_done_recovers_first)
{
	th_start(RC_ST_BOOT);
	F->open_flag = true;
	F->batt = RC_BATT_B5;
	th_event(RC_EV_INIT_DONE);
	zassert_equal(out.last_row, 4);
	zassert_equal(rc_core_state(&core), RC_ST_RECOVERY);
	th_event(RC_EV_SCAN_DONE);           /* row 9 into STANDBY, then R-STB: row 21 */
	zassert_equal(out.last_row, 22);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_BATTERY_LOW);
	TH_EXPECT(A(WRITE_CLOSE_RECOVERED), A(CLEAR_OPEN_FLAG), A(SD_OFF), A(M3));
	zassert_false(F->open_flag);
}

ZTEST(rc_round2, test_r4b_b2_with_open_flag_goes_off_without_recovery)
{
	th_start(RC_ST_BOOT);
	F->open_flag = true;
	F->batt = RC_BATT_B2;
	th_event(RC_EV_INIT_DONE);
	zassert_equal(out.last_row, 7);
	zassert_equal(rc_core_state(&core), RC_ST_OFF);
	TH_EXPECT(A(SHIP_MODE));
	zassert_true(F->open_flag, "the flag stays set; the next start-up recovers");
}

ZTEST(rc_round2, test_r4b_long_press_with_open_flag_runs_recovery_first)
{
	th_start(RC_ST_STANDBY);
	F->open_flag = true;
	th_long();
	zassert_equal(out.last_row, 13);
	zassert_equal(rc_core_state(&core), RC_ST_RECOVERY);
	zassert_false(rc_core_mic_rail(&core));
	TH_EXPECT(A(SD_ON), A(MOUNT));
	th_event(RC_EV_SCAN_DONE);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
	th_long();                           /* the wearer presses again */
	zassert_equal(out.last_row, 12);
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING);
}

ZTEST(rc_round2, test_r4b_failed_write_then_case_then_long_press_never_records_over_it)
{
	/* the lead's path: a write fails (open flag left set), charge, leave the case, long press */
	th_start(RC_ST_STANDBY);
	th_long();
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING);
	zassert_true(F->open_flag);
	th_event(RC_EV_CHUNK_WRITE_FAILED);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_STORAGE_FAULT);
	th_event(RC_EV_VBUS_IN);
	th_event(RC_EV_VBUS_OUT);
	/* since R11 the storage fault survives the case: back to ERR_STORAGE_FAULT through row 24 */
	zassert_equal(out.last_row, 25);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_STORAGE_FAULT);
	zassert_true(F->open_flag);
	th_long();                           /* ignored in ERR_STORAGE_FAULT */
	zassert_false(th_has(&out, RC_ACT_OPEN));
	th_event(RC_EV_STORAGE_RETRY_OK);    /* R9: with the flag set, to RECOVERY (row 59) */
	zassert_equal(out.last_row, 60);
	zassert_equal(rc_core_state(&core), RC_ST_RECOVERY);
	zassert_true(F->open_flag);
	th_event(RC_EV_SCAN_DONE);
	zassert_false(F->open_flag);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
}

/* ---- R6 is test_r6_row17_screen_on_centre_action_then_mt in test_rows.c ---- */

/* ---- R7: a centre hold is cancelled by any change of state (line 257) ---- */

ZTEST(rc_round2, test_r7_hold_begun_in_charging_never_starts)
{
	th_start(RC_ST_CHARGING);
	F->vbus = true;
	rc_actions_clear(&out);
	th_sw(RC_SW_CENTRE, true, TH_T0, &out);
	th_tick_to(TH_T0 + 600, &out);
	th_event(RC_EV_VBUS_OUT);              /* out of the case, thumb still on the nub */
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
	rc_actions_clear(&out);
	th_tick_to(TH_T0 + 5000, &out);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
	zassert_equal(out.n, 0, "no MW, no start");
	th_sw(RC_SW_CENTRE, false, TH_T0 + 5000, &out);
	th_tick_to(TH_T0 + 8000, &out);
	zassert_equal(out.n, 0, "the release of a cancelled hold gives nothing");
	th_long();                             /* release and press again: starts */
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING);
}

ZTEST(rc_round2, test_r7_hold_cancelled_by_change_of_state_in_standby)
{
	/* hold begun in STANDBY, case inserted and removed before the mark */
	th_start(RC_ST_STANDBY);
	rc_actions_clear(&out);
	th_sw(RC_SW_CENTRE, true, TH_T0, &out);
	th_tick_to(TH_T0 + 300, &out);
	th_event(RC_EV_VBUS_IN);
	th_event(RC_EV_VBUS_OUT);
	rc_actions_clear(&out);
	th_tick_to(TH_T0 + 3000, &out);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
	zassert_false(th_has(&out, RC_ACT_OPEN));
	zassert_false(th_has(&out, RC_ACT_MW));
}

ZTEST(rc_round2, test_r7_no_change_of_state_keeps_the_hold)
{
	/* a self row (B15 in STANDBY) is not a change of state: the long press still starts */
	th_start(RC_ST_STANDBY);
	rc_actions_clear(&out);
	th_sw(RC_SW_CENTRE, true, TH_T0, &out);
	th_tick_to(TH_T0 + 300, &out);
	th_batt(RC_BATT_B15);
	rc_actions_clear(&out);
	th_tick_to(TH_T0 + 1000, &out);
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING);
}

/* ---- R8: charge on at every appearance of VBUS, every state (line 204) ---- */

ZTEST(rc_round2, test_r8_charge_on_at_every_vbus_appearance)
{
	for (int s = 0; s < RC_ST_COUNT; s++) {
		int n = 0;

		th_start((enum rc_state)s);
		th_event(RC_EV_VBUS_IN);
		for (uint8_t i = 0; i < out.n; i++) {
			n += out.a[i] == RC_ACT_CHARGE_ON;
		}
		zassert_equal(n, 1, "state %d", s);
	}
	th_start(RC_ST_BOOT);
	th_event(RC_EV_VBUS_IN);
	zassert_equal(rc_core_state(&core), RC_ST_BOOT);
	TH_EXPECT(A(CHARGE_ON));
	th_start(RC_ST_RECOVERY);
	th_event(RC_EV_VBUS_IN);
	zassert_equal(rc_core_state(&core), RC_ST_RECOVERY);
	TH_EXPECT(A(CHARGE_ON));
}

/* ---- C1: the battery fact goes down as well as up ---- */

ZTEST(rc_round2, test_code_c1_battery_fact_both_directions)
{
	th_start(RC_ST_ERR_BATTERY_LOW);
	F->batt = RC_BATT_B5;
	F->vbus = false;
	th_event(RC_EV_VBUS_IN);
	zassert_equal(rc_core_state(&core), RC_ST_CHARGING);
	th_batt(RC_BATT_B15);                  /* charging: level rises, no row */
	zassert_equal(out.n, 0);
	th_batt(RC_BATT_OK);
	zassert_equal(out.n, 0);
	zassert_equal(F->batt, RC_BATT_OK);
	th_event(RC_EV_VBUS_OUT);
	zassert_equal(out.last_row, 40, "above B5 after the charge: STANDBY");
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
	th_batt(RC_BATT_B5);                   /* falling again: the row runs */
	zassert_equal(out.last_row, 22);
}

ZTEST(rc_round2, test_code_c1_battery_events_refused_from_event_entry)
{
	th_start(RC_ST_STANDBY);
	th_event(RC_EV_BATT_B5);
	zassert_equal(out.n, 0);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
	zassert_equal(F->batt, RC_BATT_OK);
}

/* ---- C2: row 3's guard, negative side ---- */

ZTEST(rc_round2, test_code_c2_row3_guard_refuses_b5)
{
	struct rc_sm sm;
	struct rc_facts f = { 0 };

	rc_sm_init(&sm, RC_ST_BOOT);
	f.batt = RC_BATT_B5;
	zassert_is_null(rc_sm_find(&sm, RC_EV_INIT_DONE, &f));
	f.batt = RC_BATT_B2;
	zassert_is_null(rc_sm_find(&sm, RC_EV_INIT_DONE, &f));
	f.batt = RC_BATT_B15;
	zassert_equal(rc_sm_find(&sm, RC_EV_INIT_DONE, &f)->row, 3);
}

/* ---- C3: re-arm of the once flags, timers refused ---- */

ZTEST(rc_round2, test_code_c3_b15_rearmed_by_vbus)
{
	th_start(RC_ST_STANDBY);
	th_batt(RC_BATT_B15);
	zassert_true(th_has(&out, RC_ACT_M3));
	th_event(RC_EV_VBUS_IN);
	th_batt(RC_BATT_OK);
	th_event(RC_EV_VBUS_OUT);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
	th_batt(RC_BATT_B15);
	zassert_equal(out.last_row, 21);
	zassert_true(th_has(&out, RC_ACT_M3), "a new discharge warns again");
}

ZTEST(rc_round2, test_code_c3_s30_rearmed_by_new_recording)
{
	th_start(RC_ST_STANDBY);
	th_long();
	th_event(RC_EV_STORAGE_S30);
	zassert_true(th_has(&out, RC_ACT_M3));
	th_now += 3000;
	th_long();
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
	th_now += 3000;
	th_long();
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING);
	th_event(RC_EV_STORAGE_S30);
	zassert_true(th_has(&out, RC_ACT_M3), "a new recording warns again");
}

ZTEST(rc_round2, test_code_c3_timers_refused_from_event_entry)
{
	th_start(RC_ST_ERR_MIC_FAULT);
	th_event(RC_EV_TIMER_5S);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_MIC_FAULT);
	zassert_equal(out.n, 0);
	th_start(RC_ST_ERR_STORAGE_FAULT);
	th_event(RC_EV_TIMER_60S);
	zassert_equal(out.n, 0);
}

/* ---- C6: m23 cannot change behaviour (no row lists MW, so the row filter never sees it) ---- */

ZTEST(rc_round2, test_code_c6_no_row_action_is_mw)
{
	for (int i = 0; i < rc_table_rows; i++) {
		for (int m = 0; m < 4; m++) {
			struct rc_sm sm;
			struct rc_facts f = { 0 };

			f.vibration_on = true;
			f.screen_on = m & 1;
			f.open_flag = (m >> 1) & 1;
			rc_sm_init(&sm, (enum rc_state)rc_table[i].from);
			rc_actions_clear(&out);
			rc_row_actions(&sm, rc_table[i].row, &f, &out);
			zassert_false(th_has(&out, RC_ACT_MW), "row %d", rc_table[i].row);
		}
	}
}

ZTEST_SUITE(rc_round2, NULL, NULL, NULL, NULL, NULL);
