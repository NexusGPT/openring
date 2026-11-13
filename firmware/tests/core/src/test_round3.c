/*
 * Round 3: tests named after rulings R9 to R14 and C7 of firmware/docs/core-delta-2.md,
 * as written into design/firmware.md sections 1 and 2.
 */
#include "th.h"

#define F (rc_core_facts(&core))
#define A(x) RC_ACT_##x

/* ---- R9: only a close and "scan done" clear the open flag ---- */

ZTEST(rc_round3, test_r9_recovery_request_keeps_open_flag)
{
	th_start(RC_ST_ERR_STORAGE_FAULT);
	F->open_flag = true;
	th_event(RC_EV_STORAGE_RETRY_OK);
	zassert_equal(out.last_row, 60);
	zassert_equal(rc_core_state(&core), RC_ST_RECOVERY);
	TH_EXPECT(A(SD_ON));
	zassert_true(F->open_flag, "asking for recovery clears nothing");
	th_event(RC_EV_SCAN_READ_ERROR);      /* row 11, flag still set */
	zassert_equal(rc_core_state(&core), RC_ST_ERR_STORAGE_FAULT);
	zassert_true(F->open_flag);
	th_event(RC_EV_STORAGE_RETRY_OK);
	zassert_equal(rc_core_state(&core), RC_ST_RECOVERY);
	th_event(RC_EV_SCAN_DONE);            /* row 9: clear open flag */
	zassert_false(F->open_flag);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
}

ZTEST(rc_round3, test_r9_long_press_recovery_keeps_flag_until_scan_done)
{
	th_start(RC_ST_STANDBY);
	F->open_flag = true;
	th_long();                            /* row 13 */
	zassert_equal(rc_core_state(&core), RC_ST_RECOVERY);
	zassert_true(F->open_flag);
	th_event(RC_EV_SCAN_DONE);
	zassert_false(F->open_flag);
}

ZTEST(rc_round3, test_r9_retry_with_flag_clear_goes_to_standby)
{
	th_start(RC_ST_ERR_STORAGE_FAULT);
	th_event(RC_EV_STORAGE_RETRY_OK);
	zassert_equal(out.last_row, 61);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
}

/* ---- R10: leaving the case at B2 switches the ring off ---- */

ZTEST(rc_round3, test_r10_leaving_case_at_b2_switches_off)
{
	th_start(RC_ST_CHARGING);
	F->vbus = true;
	F->batt = RC_BATT_B2;
	th_event(RC_EV_VBUS_OUT);
	zassert_equal(out.last_row, 42);
	zassert_equal(rc_core_state(&core), RC_ST_OFF);
	TH_EXPECT(A(SAVE_SETTINGS_TIME), A(SHIP_MODE));
	/* TRANSFER at B2: into STANDBY, then R-STB B2 first (row 22) */
	th_start(RC_ST_TRANSFER);
	F->vbus = true;
	F->batt = RC_BATT_B2;
	F->storage_full = true;
	th_event(RC_EV_VBUS_OUT);
	zassert_equal(out.last_row, 23);
	zassert_equal(rc_core_state(&core), RC_ST_OFF);
}

/* ---- R11: the storage fault is a fact; leaving the case does not hide it ---- */

ZTEST(rc_round3, test_r11_storage_fault_survives_the_case)
{
	th_start(RC_ST_STANDBY);
	th_long();
	th_event(RC_EV_CHUNK_WRITE_FAILED);
	zassert_true(F->storage_fault);
	th_event(RC_EV_VBUS_IN);
	zassert_equal(rc_core_state(&core), RC_ST_CHARGING);
	th_event(RC_EV_VBUS_OUT);
	zassert_equal(out.last_row, 25);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_STORAGE_FAULT);
	zassert_equal(rc_core_next_tick(&core), th_now + SPEC_STORAGE_RETRY_MS, "back to the 60 s retry");
}

ZTEST(rc_round3, test_r11_fault_cleared_only_by_successful_init)
{
	th_start(RC_ST_ERR_STORAGE_FAULT);
	zassert_true(F->storage_fault);
	th_event(RC_EV_STORAGE_RETRY_FAILED);
	zassert_true(F->storage_fault);
	th_event(RC_EV_STORAGE_RETRY_OK);
	zassert_false(F->storage_fault);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
	th_start(RC_ST_BOOT);
	F->storage_fault = true;
	th_event(RC_EV_INIT_DONE);
	zassert_false(F->storage_fault);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
}

ZTEST(rc_round3, test_r15a_b2_checked_before_the_storage_fault)
{
	/* ruling R15, path (a): R-STB checks B2 (no VBUS) before the storage fault */
	th_start(RC_ST_ERR_MIC_FAULT);
	F->storage_fault = true;
	F->batt = RC_BATT_B2;
	rc_actions_clear(&out);
	th_tick_to(TH_T0 + SPEC_MIC_FAULT_MS, &out);
	zassert_equal(out.last_row, 23);
	zassert_equal(rc_core_state(&core), RC_ST_OFF);
}

/* ---- R12: battery events in BOOT are kept until "init done" ---- */

ZTEST(rc_round3, test_r12_b5_in_boot_kept_then_recovery_first)
{
	th_start(RC_ST_BOOT);
	F->open_flag = true;
	th_batt(RC_BATT_B5);
	zassert_equal(out.n, 0);
	zassert_equal(rc_core_state(&core), RC_ST_BOOT);
	zassert_equal(F->batt, RC_BATT_B5);
	th_event(RC_EV_INIT_DONE);
	zassert_equal(out.last_row, 4);
	zassert_equal(rc_core_state(&core), RC_ST_RECOVERY);
}

ZTEST(rc_round3, test_r12_b2_in_boot_kept_then_off)
{
	th_start(RC_ST_BOOT);
	th_batt(RC_BATT_B2);
	zassert_equal(out.n, 0);
	th_event(RC_EV_INIT_DONE);
	zassert_equal(out.last_row, 7);
	zassert_equal(rc_core_state(&core), RC_ST_OFF);
	/* ruling R15, path (b): the storage init fails instead: OFF through row 62 */
	th_start(RC_ST_BOOT);
	th_batt(RC_BATT_B2);
	th_event(RC_EV_STORAGE_INIT_FAILED);
	zassert_equal(out.last_row, 63);
	zassert_equal(rc_core_state(&core), RC_ST_OFF);
}

/* ---- R13: row 8 turns VDD_SD off ---- */

ZTEST(rc_round3, test_r13_row8_turns_sd_off)
{
	th_start(RC_ST_BOOT);
	F->batt = RC_BATT_B5;
	th_event(RC_EV_INIT_DONE);
	zassert_equal(out.last_row, 8);
	TH_EXPECT(A(SD_OFF), A(M3));
}

/* ---- R14: at most one storage retry per call of the tick ---- */

ZTEST(rc_round3, test_r14_one_retry_per_tick_whatever_the_delay)
{
	int n = 0;

	th_start(RC_ST_ERR_STORAGE_FAULT);
	rc_actions_clear(&out);
	rc_core_tick(&core, TH_T0 + 600000, &out);   /* 10 minutes late, one call */
	for (uint8_t i = 0; i < out.n; i++) {
		n += out.a[i] == RC_ACT_RETRY_STORAGE;
	}
	zassert_equal(n, 1);
	zassert_equal(rc_core_next_tick(&core), TH_T0 + 600000 + SPEC_STORAGE_RETRY_MS);
}

/* ---- C7: the review's surviving mutations m31, m35, m40 (m21 is the R9 tests) ---- */

ZTEST(rc_round3, test_code_c7_repeated_battery_level_does_nothing)
{
	th_start(RC_ST_STANDBY);
	th_batt(RC_BATT_B15);
	zassert_equal(out.last_row, 21);
	th_batt(RC_BATT_B15);
	zassert_equal(out.n, 0);
	zassert_equal(out.last_row, -1);
}

ZTEST(rc_round3, test_code_c7_invalid_battery_level_refused)
{
	th_start(RC_ST_STANDBY);
	th_batt((enum rc_batt)7);
	zassert_equal(out.n, 0);
	zassert_equal(F->batt, RC_BATT_OK);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
}

ZTEST(rc_round3, test_code_c7_sfull_event_sets_the_fact)
{
	th_start(RC_ST_STANDBY);
	th_event(RC_EV_STORAGE_SFULL);
	zassert_true(F->storage_full);
	th_event(RC_EV_VBUS_IN);
	th_event(RC_EV_VBUS_OUT);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_STORAGE_FULL, "the case does not hide full storage");
}

ZTEST(rc_round3, test_r15b_failed_storage_init_with_b2_kept_goes_off)
{
	/* ruling R15, path (b), as its own test */
	th_start(RC_ST_BOOT);
	th_batt(RC_BATT_B2);
	zassert_equal(rc_core_state(&core), RC_ST_BOOT);
	th_event(RC_EV_STORAGE_INIT_FAILED);
	zassert_equal(out.last_row, 63);
	zassert_equal(rc_core_state(&core), RC_ST_OFF);
	TH_EXPECT(A(LOG_EVENT), A(MF), A(SHIP_MODE));
}

ZTEST(rc_round3, test_r15_walk_every_entry_with_b2_kept_ends_off)
{
	/* Every row of the table from another state into STANDBY or an error state, given through
	 * the real entry points with the battery fact at B2 and no VBUS after the event, ends in OFF.
	 * Rows whose guard cannot hold at B2 (above B5, or a B5 row that a B2 row precedes) and rows
	 * whose event is a battery event (it sets the level itself) or internal are skipped and counted. */
	static const uint8_t targets[] = {
		RC_ST_STANDBY, RC_ST_ERR_STORAGE_FAULT, RC_ST_ERR_STORAGE_FULL,
		RC_ST_ERR_BATTERY_LOW, RC_ST_ERR_MIC_FAULT, RC_ST_ERR_CHARGER,
	};
	int walked[RC_ST_COUNT] = { 0 };
	int total = 0;

	for (int i = 0; i < rc_table_rows; i++) {
		const struct rc_row *r = &rc_table[i];
		bool target = false;
		int ev = r->event;

		for (unsigned k = 0; k < sizeof(targets); k++) {
			target |= r->to == targets[k];
		}
		if (!target || r->to == r->from || ev == RC_EV_BATT_B15 || ev == RC_EV_BATT_B5 ||
		    ev == RC_EV_BATT_B2 || ev == RC_EV_STORAGE_FAULT_SET) {
			continue;
		}
		/* find facts under which this row is the one taken at B2 */
		bool found = false;
		int m;

		for (m = 0; m < 16 && !found; m++) {
			struct rc_sm sm;
			struct rc_facts f = { 0 };

			rc_sm_init(&sm, (enum rc_state)r->from);
			f.batt = RC_BATT_B2;
			f.vbus = (ev == RC_EV_VBUS_OUT) || (m & 8);
			f.open_flag = m & 1;
			f.storage_full = (m >> 1) & 1;
			f.factory_flag = (m >> 2) & 1;
			const struct rc_row *hit = rc_sm_find(&sm, (enum rc_event)ev, &f);

			found = hit != NULL && hit->row == r->row && !(f.vbus && ev != RC_EV_VBUS_OUT && ev != RC_EV_VBUS_IN);
		}
		if (!found) {
			continue;
		}
		m--;
		th_start((enum rc_state)r->from);
		F->batt = RC_BATT_B2;
		F->vbus = (ev == RC_EV_VBUS_OUT);
		F->open_flag = m & 1;
		F->storage_full = (m >> 1) & 1;
		F->factory_flag = (m >> 2) & 1;
		rc_actions_clear(&out);
		if (ev == RC_EV_LONG_PRESS) {
			th_long();
		} else if (ev == RC_EV_TIMER_5S) {
			th_tick_to(TH_T0 + SPEC_MIC_FAULT_MS, &out);
		} else if (ev == RC_EV_TIMER_60S) {
			th_tick_to(TH_T0 + SPEC_STORAGE_RETRY_MS, &out);
		} else {
			th_event((enum rc_event)ev);
		}
		zassert_equal(rc_core_state(&core), RC_ST_OFF, "row %d", r->row);
		zassert_true(th_has(&out, RC_ACT_SHIP_MODE), "row %d", r->row);
		walked[r->to]++;
		total++;
	}
	/* every target state is entered at least once at B2, except ERR_BATTERY_LOW: every row into it
	 * is a B5 row (battery event, or "VBUS removed, battery at B5", which the B2 row 41 precedes) */
	zassert_true(walked[RC_ST_STANDBY] > 0);
	zassert_true(walked[RC_ST_ERR_STORAGE_FAULT] > 0);
	zassert_true(walked[RC_ST_ERR_STORAGE_FULL] > 0);
	zassert_true(walked[RC_ST_ERR_MIC_FAULT] > 0);
	zassert_true(walked[RC_ST_ERR_CHARGER] > 0);
	zassert_equal(walked[RC_ST_ERR_BATTERY_LOW], 0);
	zassert_true(total >= 10, "walked %d rows", total);
}

ZTEST(rc_round3, test_r15_with_vbus_b2_does_not_switch_off)
{
	/* "with no VBUS": a fault entry while VBUS is present stays awake */
	th_start(RC_ST_CHARGING);
	F->vbus = true;
	F->batt = RC_BATT_B2;
	th_event(RC_EV_CHARGE_ERROR);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_CHARGER);
	th_event(RC_EV_VBUS_OUT);            /* then leaving the case: STANDBY, R-STB B2: OFF */
	zassert_equal(rc_core_state(&core), RC_ST_OFF);
}

ZTEST_SUITE(rc_round3, NULL, NULL, NULL, NULL, NULL);
