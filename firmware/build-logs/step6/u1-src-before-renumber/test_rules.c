/*
 * Rules of design/firmware.md (F6) that span rows: the owner's recording rule,
 * the microphone rail, the collisions C1 to C4, MW, the Vibration setting,
 * and the table's agreement with the generator. Line numbers of the document.
 */
#include "th.h"

#define F (rc_core_facts(&core))
#define A(x) RC_ACT_##x

/* ---- table and generator ---- */

ZTEST(rc_table, test_table_has_71_rows_in_order)
{
	/* line 205: "The table has 71 transitions." */
	zassert_equal(rc_table_rows, 71);
	for (int i = 0; i < rc_table_rows; i++) {
		zassert_equal(rc_table[i].row, i + 1);
		zassert_equal(rc_table[i].doc_line, 133 + i);
	}
}

ZTEST(rc_table, test_table_checksum_matches_generator)
{
	/* the checksum written by tools/gen_table.py equals the one of the compiled table */
	zassert_equal(rc_table_checksum(), rc_table_fnv1a);
}

/* ---- owner's rule: only a long press of the centre starts or stops a recording (line 198) ---- */

static const uint8_t all_states[] = {
	RC_ST_SHIP, RC_ST_OFF, RC_ST_BOOT, RC_ST_RECOVERY, RC_ST_STANDBY, RC_ST_RECORDING,
	RC_ST_CHARGING, RC_ST_TRANSFER, RC_ST_ERR_STORAGE_FULL, RC_ST_ERR_BATTERY_LOW,
	RC_ST_ERR_STORAGE_FAULT, RC_ST_ERR_MIC_FAULT, RC_ST_ERR_CHARGER, RC_ST_FACTORY_TEST,
};

ZTEST(rc_owner_rule, test_only_row_12_enters_recording)
{
	int n = 0;

	for (int i = 0; i < rc_table_rows; i++) {
		if (rc_table[i].to == RC_ST_RECORDING && rc_table[i].from != RC_ST_RECORDING) {
			zassert_equal(rc_table[i].event, RC_EV_LONG_PRESS);
			zassert_equal(rc_table[i].from, RC_ST_STANDBY);
			n++;
		}
	}
	zassert_equal(n, 1);
}

ZTEST(rc_owner_rule, test_no_system_event_starts_a_recording)
{
	/* every state, every event of the event entry, every combination of the guard facts */
	for (unsigned s = 0; s < sizeof(all_states); s++) {
		if (all_states[s] == RC_ST_RECORDING) {
			continue;
		}
		for (int ev = 0; ev < RC_EV_COUNT; ev++) {
			for (int m = 0; m < 64; m++) {
				th_start((enum rc_state)all_states[s]);
				F->vbus = m & 1;
				F->open_flag = (m >> 1) & 1;
				F->storage_full = (m >> 2) & 1;
				F->factory_flag = (m >> 3) & 1;
				F->batt = (uint8_t)((m >> 4) & 3);
				th_event((enum rc_event)ev);
				zassert_not_equal(rc_core_state(&core), RC_ST_RECORDING);
				zassert_false(th_has(&out, RC_ACT_OPEN));
			}
		}
	}
}

ZTEST(rc_owner_rule, test_press_events_cannot_be_injected)
{
	/* the press events come only from the switch input */
	th_start(RC_ST_STANDBY);
	th_event(RC_EV_LONG_PRESS);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
	zassert_equal(out.n, 0);
	th_start(RC_ST_RECORDING);
	th_event(RC_EV_LONG_PRESS);
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING);
	zassert_equal(out.n, 0);
}

static void no_stop_check(void)
{
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING);
	zassert_false(th_has(&out, RC_ACT_CLOSE));
	zassert_false(th_has(&rest, RC_ACT_CLOSE));
}

ZTEST(rc_owner_rule, test_user_inputs_other_than_long_never_stop)
{
	/* lines 198, 244: a short press, a double press and a direction never stop a recording;
	 * neither does Bluetooth; grazes and holds under 1,000 ms do nothing (lines 214, 215, 237) */
	static const rc_ms_t holds[] = { 10, 39, 40, 100, 450, 451, 500, 999 };
	static const enum rc_switch dirs[] = { RC_SW_UP, RC_SW_DOWN, RC_SW_LEFT, RC_SW_RIGHT };

	for (int src = 0; src < 2; src++) {
		for (unsigned h = 0; h < sizeof(holds) / sizeof(holds[0]); h++) {
			th_start_src(RC_ST_RECORDING, (enum rc_centre_source)src);
			rc_actions_clear(&out);
			rc_actions_clear(&rest);
			if (src == RC_CENTRE_SW2) {
				th_sw(RC_SW_CENTRE, true, TH_T0, &out);
				th_sw(RC_SW_CENTRE, false, TH_T0 + holds[h], &out);
			} else {
				th_sw(RC_SW_LEFT, true, TH_T0 - 5, &out);
				th_sw(RC_SW_RIGHT, true, TH_T0, &out);
				th_sw(RC_SW_LEFT, false, TH_T0 + holds[h], &out);
				th_sw(RC_SW_RIGHT, false, TH_T0 + holds[h], &out);
			}
			th_tick_to(TH_T0 + 5000, &out);
			no_stop_check();
		}
		for (int d = 0; d < 4; d++) {
			th_start_src(RC_ST_RECORDING, (enum rc_centre_source)src);
			rc_actions_clear(&out);
			th_sw(dirs[d], true, TH_T0, &out);
			th_tick_to(TH_T0 + 3000, &out);  /* held 3 s: event and repeats */
			th_sw(dirs[d], false, TH_T0 + 3000, &out);
			th_tick_to(TH_T0 + 6000, &out);
			no_stop_check();
		}
	}
	th_start(RC_ST_RECORDING);
	th_double();
	no_stop_check();
	th_start(RC_ST_RECORDING);
	th_event(RC_EV_BLE_HIGHLIGHT);
	no_stop_check();
	th_start(RC_ST_RECORDING);
	th_event(RC_EV_MENU_POWER_OFF);
	no_stop_check();
}

ZTEST(rc_owner_rule, test_directions_never_start)
{
	/* lines 198, 207, 257: a direction never starts a recording, held or tapped, either source */
	static const enum rc_switch dirs[] = { RC_SW_UP, RC_SW_DOWN, RC_SW_LEFT, RC_SW_RIGHT };

	for (int src = 0; src < 2; src++) {
		for (int d = 0; d < 4; d++) {
			th_start_src(RC_ST_STANDBY, (enum rc_centre_source)src);
			rc_actions_clear(&out);
			th_sw(dirs[d], true, TH_T0, &out);
			th_tick_to(TH_T0 + 3000, &out);
			th_sw(dirs[d], false, TH_T0 + 3000, &out);
			th_tick_to(TH_T0 + 6000, &out);
			zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
			zassert_false(th_has(&out, RC_ACT_OPEN));
		}
	}
}

ZTEST(rc_owner_rule, test_rows_leaving_recording_are_the_stated_ones)
{
	/* the only ways out of RECORDING are the rows the document lists: 25 (long press),
	 * 29 (case insertion), 31, 32, 34, 35, 36, 37 (21, 25, 27, 28, 30 to 33 in F6) */
	static const uint8_t expect_rows[] = { 25, 29, 31, 32, 34, 35, 36, 37 };
	int k = 0;

	for (int i = 0; i < rc_table_rows; i++) {
		if (rc_table[i].from == RC_ST_RECORDING && rc_table[i].to != RC_ST_RECORDING) {
			zassert_true(k < 8);
			zassert_equal(rc_table[i].row, expect_rows[k]);
			k++;
		}
	}
	zassert_equal(k, 8);
}

ZTEST(rc_owner_rule, test_long_press_starts_and_same_long_press_stops)
{
	/* lines 211, 240: a long press starts; holding on does not stop; a new long press stops */
	th_start(RC_ST_STANDBY);
	rc_actions_clear(&out);
	th_sw(RC_SW_CENTRE, true, TH_T0, &out);
	th_tick_to(TH_T0 + 8000, &out);
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING);
	th_sw(RC_SW_CENTRE, false, TH_T0 + 8000, &out);
	th_tick_to(TH_T0 + 9000, &out);
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING);
	th_long();
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
}

/* ---- microphone rail on only in RECORDING (line 112) ---- */

ZTEST(rc_mic_rail, test_open_only_into_recording_and_every_exit_turns_mic_off)
{
	for (int i = 0; i < rc_table_rows; i++) {
		const struct rc_row *r = &rc_table[i];
		struct rc_sm sm;
		struct rc_facts f = { 0 };

		f.vibration_on = true;
		rc_sm_init(&sm, (enum rc_state)r->from);
		rc_actions_clear(&out);
		rc_row_actions(&sm, r->row, &f, &out);
		f.open_flag = true;
		rc_actions_clear(&rest);
		rc_row_actions(&sm, r->row, &f, &rest);
		if (th_has(&out, RC_ACT_OPEN) || th_has(&rest, RC_ACT_OPEN)) {
			zassert_equal(r->to, RC_ST_RECORDING);
		}
		if (r->from == RC_ST_RECORDING && r->to != RC_ST_RECORDING && r->event != RC_EV_POWER_LOSS) {
			zassert_true(th_has(&out, RC_ACT_CLOSE) || th_has(&out, RC_ACT_MIC_OFF), "row %d", r->row);
		}
	}
}

ZTEST(rc_mic_rail, test_rail_follows_state_on_every_event_from_every_state)
{
	for (unsigned s = 0; s < sizeof(all_states); s++) {
		for (int ev = 0; ev < RC_EV_COUNT; ev++) {
			for (int m = 0; m < 4; m++) {
				th_start((enum rc_state)all_states[s]);
				F->vbus = m & 1;
				F->storage_full = (m >> 1) & 1;
				th_event((enum rc_event)ev);
				zassert_equal(rc_core_mic_rail(&core), rc_core_state(&core) == RC_ST_RECORDING);
			}
		}
		/* and through the switch input and the timers */
		th_start((enum rc_state)all_states[s]);
		th_long();
		zassert_equal(rc_core_mic_rail(&core), rc_core_state(&core) == RC_ST_RECORDING);
		th_tick_to(TH_T0 + 70000, &rest);
		zassert_equal(rc_core_mic_rail(&core), rc_core_state(&core) == RC_ST_RECORDING);
	}
}

/* ---- collisions C1 to C4, lines 279 to 282 ---- */

ZTEST(rc_collisions, test_c1_short_in_recording_marks_highlight_not_status)
{
	th_start(RC_ST_RECORDING);
	F->screen_on = true;
	th_short();
	TH_EXPECT(A(HIGHLIGHT), A(MH), A(SCR_RECORDING_3S));
	zassert_false(th_has(&out, RC_ACT_SCR_STATUS_5S));
	zassert_false(th_has(&out, RC_ACT_SCREEN_CENTRE));
}

ZTEST(rc_collisions, test_c2_long_press_with_screen_on_starts)
{
	/* the long press starts a recording from any screen (screen on) */
	th_start(RC_ST_STANDBY);
	F->screen_on = true;
	th_long();
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING);
	TH_EXPECT(A(OPEN), A(M1));
}

ZTEST(rc_collisions, test_c3_centre_action_comes_after_window_and_double_is_dead)
{
	th_start(RC_ST_STANDBY);
	F->screen_on = true;
	rc_actions_clear(&out);
	th_sw(RC_SW_CENTRE, true, TH_T0, &out);
	th_sw(RC_SW_CENTRE, false, TH_T0 + 100, &out);
	th_tick_to(TH_T0 + 100 + 399, &out);
	zassert_false(th_has(&out, RC_ACT_SCREEN_CENTRE), "not before the window closes");
	th_tick_to(TH_T0 + 100 + 401, &out);
	zassert_true(th_has(&out, RC_ACT_SCREEN_CENTRE));
	th_start(RC_ST_STANDBY);
	F->screen_on = true;
	th_double();
	zassert_equal(out.n, 0);
	zassert_equal(rest.n, 0);
}

ZTEST(rc_collisions, test_c4_lock_direction_and_short_only_wake)
{
	static const enum rc_switch dirs[] = { RC_SW_UP, RC_SW_DOWN, RC_SW_LEFT, RC_SW_RIGHT };

	/* line 258: screen off, the first direction only turns the screen on */
	for (int d = 0; d < 4; d++) {
		th_start(RC_ST_STANDBY);
		rc_actions_clear(&out);
		th_sw(dirs[d], true, TH_T0, &out);
		th_sw(dirs[d], false, TH_T0 + 20, &out);
		TH_EXPECT(A(SCREEN_ON));
	}
	/* screen off, short press in another state: screen on only (line 212) */
	th_start(RC_ST_CHARGING);
	F->vbus = true;
	th_short();
	TH_EXPECT(A(SCREEN_ON));
}

ZTEST(rc_collisions, test_c4_long_press_with_screen_off_starts)
{
	th_start(RC_ST_STANDBY);
	F->screen_on = false;
	th_long();
	zassert_equal(rc_core_state(&core), RC_ST_RECORDING);
	TH_EXPECT(A(OPEN), A(M1));
}

ZTEST(rc_collisions, test_c4_short_in_recording_screen_off_marks_and_shows_3s)
{
	th_start(RC_ST_RECORDING);
	F->screen_on = false;
	th_short();
	TH_EXPECT(A(HIGHLIGHT), A(MH), A(SCR_RECORDING_3S));
}

ZTEST(rc_collisions, test_screen_on_direction_goes_to_screen_with_mt)
{
	/* line 262 table: directions act on the screen when it is on; line 301 MT on a joystick move */
	static const enum rc_switch dirs[] = { RC_SW_UP, RC_SW_DOWN, RC_SW_LEFT, RC_SW_RIGHT };
	static const uint8_t acts[] = { A(SCREEN_UP), A(SCREEN_DOWN), A(SCREEN_LEFT), A(SCREEN_RIGHT) };

	for (int d = 0; d < 4; d++) {
		th_start(RC_ST_STANDBY);
		F->screen_on = true;
		rc_actions_clear(&out);
		th_sw(dirs[d], true, TH_T0, &out);
		th_sw(dirs[d], false, TH_T0 + 20, &out);
		zassert_equal(out.n, 2);
		zassert_equal(out.a[0], acts[d]);
		zassert_equal(out.a[1], RC_ACT_MT);
	}
}

/* ---- MW, Vibration, refusals, highlight time ---- */

ZTEST(rc_feedback, test_mw_in_standby_and_recording_only)
{
	/* line 223: MW at 500 ms in STANDBY and RECORDING; line 215: other states ignore the hold */
	for (unsigned s = 0; s < sizeof(all_states); s++) {
		th_start((enum rc_state)all_states[s]);
		F->vbus = (all_states[s] == RC_ST_CHARGING || all_states[s] == RC_ST_TRANSFER);
		rc_actions_clear(&out);
		th_sw(RC_SW_CENTRE, true, TH_T0, &out);
		th_tick_to(TH_T0 + 499, &out);
		zassert_false(th_has(&out, RC_ACT_MW));
		th_tick_to(TH_T0 + 500, &out);
		bool want = all_states[s] == RC_ST_STANDBY || all_states[s] == RC_ST_RECORDING;
		zassert_equal(th_has(&out, RC_ACT_MW), want, "state %d", all_states[s]);
	}
}

ZTEST(rc_feedback, test_vibration_off_drops_mh_mt_only)
{
	/* line 276: "off disables MH and joystick ticks only, never M1, M2, M3, MF, MW" */
	th_start(RC_ST_RECORDING);
	F->vibration_on = false;
	th_short();
	TH_EXPECT(A(HIGHLIGHT), A(SCR_RECORDING_3S));
	th_start(RC_ST_STANDBY);
	F->vibration_on = false;
	F->screen_on = true;
	rc_actions_clear(&out);
	th_sw(RC_SW_UP, true, TH_T0, &out);
	th_sw(RC_SW_UP, false, TH_T0 + 20, &out);
	TH_EXPECT(A(SCREEN_UP));
	th_start(RC_ST_STANDBY);
	F->vibration_on = false;
	rc_actions_clear(&out);
	th_sw(RC_SW_CENTRE, true, TH_T0, &out);
	th_tick_to(TH_T0 + 1000, &out);
	TH_EXPECT(A(MW), A(OPEN), A(M1));
	th_batt(RC_BATT_B5);
	TH_EXPECT(A(CLOSE), A(M3));
}

ZTEST(rc_feedback, test_long_press_ignored_in_other_states)
{
	/* line 211: refused with M3 in CHARGING, TRANSFER, ERR_STORAGE_FULL, ERR_BATTERY_LOW; ignored elsewhere */
	static const uint8_t ignored[] = {
		RC_ST_SHIP, RC_ST_OFF, RC_ST_BOOT, RC_ST_RECOVERY, RC_ST_ERR_STORAGE_FAULT,
		RC_ST_ERR_MIC_FAULT, RC_ST_ERR_CHARGER, RC_ST_FACTORY_TEST,
	};

	for (unsigned i = 0; i < sizeof(ignored); i++) {
		th_start((enum rc_state)ignored[i]);
		th_long();
		zassert_equal(rc_core_state(&core), ignored[i]);
		zassert_equal(out.n, 0);
		zassert_equal(out.last_row, -1);
	}
}

ZTEST(rc_feedback, test_highlight_carries_centre_down_time)
{
	/* lines 226, 245 */
	th_start(RC_ST_RECORDING);
	th_short();
	zassert_equal(out.highlight_ms, TH_T0);
}

ZTEST_SUITE(rc_table, NULL, NULL, NULL, NULL, NULL);
ZTEST_SUITE(rc_owner_rule, NULL, NULL, NULL, NULL, NULL);
ZTEST_SUITE(rc_mic_rail, NULL, NULL, NULL, NULL, NULL);
ZTEST_SUITE(rc_collisions, NULL, NULL, NULL, NULL, NULL);
ZTEST_SUITE(rc_feedback, NULL, NULL, NULL, NULL, NULL);
