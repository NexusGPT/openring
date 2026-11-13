/*
 * Round 4: ruling R16 (the B2 check also runs whenever VBUS is removed) and C10 (events the
 * core makes for itself are refused from outside), firmware/docs/core-delta-2.md "Round 4".
 */
#include "th.h"

#define F (rc_core_facts(&core))
#define A(x) RC_ACT_##x

ZTEST(rc_round4, test_r16_storage_fault_entered_in_case_then_vbus_out_goes_off)
{
	/* the reviewer's path D1: BOOT in the case at B2, storage init fails, VBUS removed */
	th_start(RC_ST_BOOT);
	F->vbus = true;
	th_batt(RC_BATT_B2);
	th_event(RC_EV_STORAGE_INIT_FAILED);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_STORAGE_FAULT, "VBUS present: awake");
	th_event(RC_EV_VBUS_OUT);
	zassert_equal(out.last_row, 62);
	zassert_equal(rc_core_state(&core), RC_ST_OFF);
	TH_EXPECT(A(SHIP_MODE));
}

ZTEST(rc_round4, test_r16_recovery_read_error_in_case_then_vbus_out_goes_off)
{
	th_start(RC_ST_RECOVERY);
	F->vbus = true;
	F->batt = RC_BATT_B2;
	th_event(RC_EV_SCAN_READ_ERROR);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_STORAGE_FAULT);
	th_event(RC_EV_VBUS_OUT);
	zassert_equal(rc_core_state(&core), RC_ST_OFF);
}

ZTEST(rc_round4, test_r16_b2_row_comes_before_the_vbus_removed_row)
{
	/* ERR_CHARGER has its own "VBUS removed" row (to STANDBY); at B2 its B2 row (67) comes first */
	th_start(RC_ST_ERR_CHARGER);
	F->vbus = true;
	F->batt = RC_BATT_B2;
	th_event(RC_EV_VBUS_OUT);
	zassert_equal(out.last_row, 67);
	TH_EXPECT(A(SAVE_SETTINGS_TIME), A(SHIP_MODE));
}

ZTEST(rc_round4, test_r16_walk_every_state_vbus_present_b2_then_vbus_out_ends_off)
{
	/* Every state, started with VBUS present and the battery fact at B2, then VBUS removed.
	 * RECOVERY ends OFF at the end of its scan, BOOT at "init done" (R4b, R12). SHIP stays SHIP:
	 * the factory ship mode, entered with VBUS, completes on VBUS removal (FW 8.4). */
	for (int s = 0; s < RC_ST_COUNT; s++) {
		th_start((enum rc_state)s);
		F->vbus = true;
		F->batt = RC_BATT_B2;
		F->factory_flag = (s == RC_ST_FACTORY_TEST);
		th_event(RC_EV_VBUS_OUT);
		if (rc_core_state(&core) == RC_ST_RECOVERY) {
			th_event(RC_EV_SCAN_DONE);
		}
		if (rc_core_state(&core) == RC_ST_BOOT) {
			th_event(RC_EV_INIT_DONE);
		}
		if (s == RC_ST_SHIP) {
			zassert_equal(rc_core_state(&core), RC_ST_SHIP);
			continue;
		}
		zassert_equal(rc_core_state(&core), RC_ST_OFF, "state %d", s);
		zassert_false(F->vbus);
	}
}

ZTEST(rc_round4, test_r16_above_b2_vbus_out_keeps_the_state_row)
{
	th_start(RC_ST_ERR_CHARGER);
	F->vbus = true;
	F->batt = RC_BATT_B15;
	th_event(RC_EV_VBUS_OUT);
	zassert_equal(out.last_row, 66);
	zassert_equal(rc_core_state(&core), RC_ST_STANDBY);
}

ZTEST(rc_round4, test_r16_sequences_never_awake_at_b2_without_vbus)
{
	/* Every state, started in the case (VBUS present) at B2, with every combination of the open
	 * flag, storage full and storage fault, then every sequence of three steps out of the outside
	 * events and a 70 s tick. After each step with no VBUS the ring must be OFF or SHIP, or in
	 * BOOT or RECOVERY, which end at B2 in OFF at "init done" or "scan done" (R4b, R15). */
	static const uint8_t evs[] = {
		RC_EV_VBUS_IN, RC_EV_VBUS_OUT, RC_EV_INIT_DONE, RC_EV_STORAGE_INIT_FAILED,
		RC_EV_SCAN_DONE, RC_EV_SCAN_READ_ERROR, RC_EV_MENU_POWER_OFF, RC_EV_STORAGE_SFULL,
		RC_EV_STORAGE_S30, RC_EV_BLE_HIGHLIGHT, RC_EV_CHUNK_WRITE_FAILED, RC_EV_MIC_NO_BLOCK,
		RC_EV_POWER_LOSS, RC_EV_USB_CONFIGURED, RC_EV_USB_UNCONFIGURED, RC_EV_CHARGE_ERROR,
		RC_EV_FW_END, RC_EV_FACTORY_ENTER, RC_EV_FACTORY_EXIT, RC_EV_SHIP_ENTER,
		RC_EV_SHIP_SAMPLE, RC_EV_STORAGE_RETRY_OK, RC_EV_STORAGE_RETRY_FAILED, 0xff,
	};
	const int ne = sizeof(evs);
	long runs = 0;

	for (int s = 0; s < RC_ST_COUNT; s++) {
		for (int m = 0; m < 8; m++) {
			for (int a = 0; a < ne; a++) {
				for (int b = 0; b < ne; b++) {
					for (int c = 0; c < ne; c++) {
						const uint8_t seq[3] = { evs[a], evs[b], evs[c] };

						th_start((enum rc_state)s);
						F->vbus = true;
						F->batt = RC_BATT_B2;
						F->open_flag = m & 1;
						F->storage_full = (m >> 1) & 1;
						F->storage_fault = (m >> 2) & 1;
						F->factory_flag = true;
						for (int k = 0; k < 3; k++) {
							rc_actions_clear(&out);
							if (seq[k] == 0xff) {
								th_now += 70000;
								rc_core_tick(&core, th_now, &out);
							} else {
								th_event((enum rc_event)seq[k]);
							}
							if (!F->vbus) {
								enum rc_state st = rc_core_state(&core);

								zassert_true(st == RC_ST_OFF || st == RC_ST_SHIP ||
									     st == RC_ST_BOOT || st == RC_ST_RECOVERY,
									     "awake at B2 without VBUS: start %d facts %d seq %d %d %d step %d state %d",
									     s, m, seq[0], seq[1], seq[2], k, st);
							}
						}
						runs++;
					}
				}
			}
		}
	}
	zassert_equal(runs, (long)RC_ST_COUNT * 8 * ne * ne * ne);
}

ZTEST(rc_round4, test_t1_r16_does_not_fire_at_b5)
{
	/* R16 is for B2 only: a ring in ERR_STORAGE_FAULT in its case at B5, taken out, stays there */
	th_start(RC_ST_ERR_STORAGE_FAULT);
	F->vbus = true;
	F->batt = RC_BATT_B5;
	th_event(RC_EV_VBUS_OUT);
	zassert_equal(rc_core_state(&core), RC_ST_ERR_STORAGE_FAULT);
	zassert_equal(out.last_row, -1);
	zassert_false(th_has(&out, RC_ACT_SHIP_MODE));
}

ZTEST(rc_round4, test_t2_r16_boot_vbus_out_at_b2_takes_row_7_before_init_done)
{
	/* BOOT leg of R16 (confirmed reading): VBUS removed in BOOT at B2 takes row 7 at once */
	th_start(RC_ST_BOOT);
	F->vbus = true;
	th_batt(RC_BATT_B2);                 /* kept in BOOT (R12) */
	zassert_equal(rc_core_state(&core), RC_ST_BOOT);
	th_event(RC_EV_VBUS_OUT);
	zassert_equal(out.last_row, 7);
	zassert_equal(rc_core_state(&core), RC_ST_OFF);
	TH_EXPECT(A(SHIP_MODE));
}

/* ---- C10: one test per event the core makes for itself ---- */

static void refused(enum rc_state st, enum rc_event ev)
{
	th_start(st);
	F->open_flag = false;
	th_event(ev);
	zassert_equal(out.n, 0, "event %d", ev);
	zassert_equal(out.last_row, -1, "event %d", ev);
	zassert_equal(rc_core_state(&core), st, "event %d", ev);
}

ZTEST(rc_round4, test_c10_refuses_storage_fault_set) { refused(RC_ST_STANDBY, RC_EV_STORAGE_FAULT_SET); }
ZTEST(rc_round4, test_c10_refuses_timer_5s) { refused(RC_ST_ERR_MIC_FAULT, RC_EV_TIMER_5S); }
ZTEST(rc_round4, test_c10_refuses_timer_60s) { refused(RC_ST_ERR_STORAGE_FAULT, RC_EV_TIMER_60S); }
ZTEST(rc_round4, test_c10_refuses_long_press) { refused(RC_ST_STANDBY, RC_EV_LONG_PRESS); }
ZTEST(rc_round4, test_c10_refuses_short_press) { refused(RC_ST_STANDBY, RC_EV_SHORT_PRESS); }
ZTEST(rc_round4, test_c10_refuses_double_press) { refused(RC_ST_STANDBY, RC_EV_DOUBLE_PRESS); }

ZTEST_SUITE(rc_round4, NULL, NULL, NULL, NULL, NULL);
