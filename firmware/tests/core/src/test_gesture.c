/*
 * Gesture recogniser tests, design/firmware.md (F6) sections 2.1 and 2.2.
 * Every centre case runs for both centre sources (SW2 and PAIR).
 * Line numbers are those of design/firmware.md.
 */
#include "th.h"

#define T0 10000

/* ---- centre press durations, gesture table lines 211 to 215 ---- */

static void dur_case(enum rc_centre_source src, rc_ms_t dur, int shorts, int warns, int longs)
{
	tg_start(src);
	tg_centre(T0, dur);
	tg_tick(T0 + 5000);
	zassert_equal(tg_count(RC_GEV_SHORT), shorts, "short");
	zassert_equal(tg_count(RC_GEV_WARN), warns, "warn");
	zassert_equal(tg_count(RC_GEV_LONG), longs, "long");
	zassert_equal(tg_count(RC_GEV_DOUBLE), 0, "double");
}

#define DUR(name, dur, s, w, l) \
	ZTEST(rc_gesture, test_sw2_hold_##name) { dur_case(RC_CENTRE_SW2, dur, s, w, l); } \
	ZTEST(rc_gesture, test_pair_hold_##name) { dur_case(RC_CENTRE_PAIR, dur, s, w, l); }

DUR(39ms_graze_ignored, 39, 0, 0, 0)      /* line 214: under 40 ms ignored */
DUR(40ms_short, 40, 1, 0, 0)              /* line 212: 40 ms to 450 ms */
DUR(450ms_short, 450, 1, 0, 0)            /* lines 212, 221: 450 included (reading, notes U1) */
DUR(451ms_ignored, 451, 0, 0, 0)          /* line 215: ignored */
DUR(499ms_ignored_no_warn, 499, 0, 0, 0)  /* line 223: MW at 500 ms */
DUR(500ms_ignored_warn, 500, 0, 1, 0)     /* lines 215, 223 */
DUR(999ms_ignored_warn, 999, 0, 1, 0)     /* line 215 */
DUR(1000ms_long, 1000, 0, 1, 1)           /* line 211 */

static void long_fires_while_held(enum rc_centre_source src)
{
	/* line 211: fires at the 1,000 ms mark while still held, once per press; the release does nothing */
	tg_start(src);
	if (src == RC_CENTRE_SW2) {
		tg_in(RC_SW_CENTRE, true, T0);
	} else {
		tg_in(RC_SW_LEFT, true, T0 - 10);
		tg_in(RC_SW_RIGHT, true, T0);
	}
	tg_tick(T0 + 999);
	zassert_equal(tg_count(RC_GEV_LONG), 0);
	tg_tick(T0 + 1000);
	zassert_equal(tg_count(RC_GEV_LONG), 1);
	zassert_equal(tg_get(RC_GEV_LONG, 0)->t, T0 + 1000);
	zassert_equal(tg_get(RC_GEV_LONG, 0)->t_down, T0);
	tg_tick(T0 + 6000);                 /* G5 line 240: holding on does nothing more */
	zassert_equal(tg_count(RC_GEV_LONG), 1);
	int before = gl.n;
	if (src == RC_CENTRE_SW2) {
		tg_in(RC_SW_CENTRE, false, T0 + 6000);
	} else {
		tg_in(RC_SW_LEFT, false, T0 + 6000);
		tg_in(RC_SW_RIGHT, false, T0 + 6000);
	}
	tg_tick(T0 + 9000);
	for (int i = before; i < gl.n; i++) {
		zassert_true(gl.e[i].type == RC_GEV_CENTRE_UP, "only the key release");
	}
	zassert_equal(tg_count(RC_GEV_SHORT) + tg_count(RC_GEV_DOUBLE), 0);
}

ZTEST(rc_gesture, test_sw2_long_fires_once_while_held) { long_fires_while_held(RC_CENTRE_SW2); }
ZTEST(rc_gesture, test_pair_long_fires_once_while_held) { long_fires_while_held(RC_CENTRE_PAIR); }

static void warn_time(enum rc_centre_source src)
{
	/* G2 line 237: one MW at 500 ms of the hold */
	tg_start(src);
	tg_centre(T0, 700);
	zassert_equal(tg_count(RC_GEV_WARN), 1);
	zassert_equal(tg_get(RC_GEV_WARN, 0)->t, T0 + 500);
}

ZTEST(rc_gesture, test_sw2_warn_at_500ms) { warn_time(RC_CENTRE_SW2); }
ZTEST(rc_gesture, test_pair_warn_at_500ms) { warn_time(RC_CENTRE_PAIR); }

static void short_window(enum rc_centre_source src)
{
	/* line 212: fires when the 400 ms window closes; line 226: carries the CENTRE_DOWN time */
	tg_start(src);
	tg_centre(T0, 100);
	tg_tick(T0 + 100 + 400);
	zassert_equal(tg_count(RC_GEV_SHORT), 0, "window still open at 400 ms");
	tg_tick(T0 + 100 + 401);
	zassert_equal(tg_count(RC_GEV_SHORT), 1);
	zassert_equal(tg_get(RC_GEV_SHORT, 0)->t_down, T0);
}

ZTEST(rc_gesture, test_sw2_short_fires_when_window_closes) { short_window(RC_CENTRE_SW2); }
ZTEST(rc_gesture, test_pair_short_fires_when_window_closes) { short_window(RC_CENTRE_PAIR); }

/* ---- second press gap, lines 213, 222, 246 ---- */

static void gap_case(enum rc_centre_source src, rc_ms_t gap, int doubles, int shorts)
{
	tg_start(src);
	tg_centre(T0, 100);
	tg_centre(T0 + 100 + gap, 100);
	tg_tick(T0 + 5000);
	zassert_equal(tg_count(RC_GEV_DOUBLE), doubles, "double");
	zassert_equal(tg_count(RC_GEV_SHORT), shorts, "short");
	zassert_equal(tg_count(RC_GEV_LONG), 0);
}

#define GAP(name, gap, d, s) \
	ZTEST(rc_gesture, test_sw2_gap_##name) { gap_case(RC_CENTRE_SW2, gap, d, s); } \
	ZTEST(rc_gesture, test_pair_gap_##name) { gap_case(RC_CENTRE_PAIR, gap, d, s); }

GAP(59ms_not_double, 59, 0, 1)   /* under 60 ms: not a double; line 246: the first short is cancelled, the second judged on its own (reading, notes U2) */
GAP(60ms_double, 60, 1, 0)
GAP(400ms_double, 400, 1, 0)
GAP(401ms_two_shorts, 401, 0, 2) /* window closed: the first short fired, the second is its own short */

static void second_press_long(enum rc_centre_source src)
{
	/* line 246: held 1,000 ms, a long press from its own CENTRE_DOWN; the earlier short is cancelled */
	tg_start(src);
	tg_centre(T0, 100);
	tg_centre(T0 + 300, 1200);
	tg_tick(T0 + 5000);
	zassert_equal(tg_count(RC_GEV_LONG), 1);
	zassert_equal(tg_get(RC_GEV_LONG, 0)->t, T0 + 300 + 1000);
	zassert_equal(tg_count(RC_GEV_SHORT), 0);
	zassert_equal(tg_count(RC_GEV_DOUBLE), 0);
}

ZTEST(rc_gesture, test_sw2_second_press_long_counts_from_own_down) { second_press_long(RC_CENTRE_SW2); }
ZTEST(rc_gesture, test_pair_second_press_long_counts_from_own_down) { second_press_long(RC_CENTRE_PAIR); }

/* ---- directions, line 252 to 256 ---- */

static const enum rc_switch dirs[4] = { RC_SW_UP, RC_SW_DOWN, RC_SW_LEFT, RC_SW_RIGHT };

static void dir_tap(enum rc_centre_source src, enum rc_switch d)
{
	/* line 254: released first with no centre press: the direction is sent at that moment */
	tg_start(src);
	tg_in(d, true, T0);
	tg_in(d, false, T0 + 25);
	tg_tick(T0 + 3000);
	zassert_equal(tg_count(RC_GEV_DIR), 1);
	zassert_equal(tg_get(RC_GEV_DIR, 0)->dir, d);
	zassert_equal(tg_get(RC_GEV_DIR, 0)->t, T0 + 25);
	zassert_equal(tg_count(RC_GEV_CENTRE_DOWN), 0);
}

static void dir_hold_repeat(enum rc_centre_source src, enum rc_switch d)
{
	/* line 254: the window ends at 40 ms, the event is sent then (at most 40 ms after the edge);
	 * line 252: held 500 ms repeats every 150 ms */
	tg_start(src);
	tg_in(d, true, T0);
	tg_tick(T0 + 39);
	zassert_equal(tg_count(RC_GEV_DIR), 0);
	tg_tick(T0 + 40);
	zassert_equal(tg_count(RC_GEV_DIR), 1);
	zassert_equal(tg_get(RC_GEV_DIR, 0)->t, T0 + 40);
	zassert_false(tg_get(RC_GEV_DIR, 0)->repeat);
	tg_tick(T0 + 499);
	zassert_equal(tg_count(RC_GEV_DIR), 1);
	tg_tick(T0 + 500);
	zassert_equal(tg_count(RC_GEV_DIR), 2);
	zassert_true(tg_get(RC_GEV_DIR, 1)->repeat);
	tg_tick(T0 + 649);
	zassert_equal(tg_count(RC_GEV_DIR), 2);
	tg_tick(T0 + 650);
	zassert_equal(tg_count(RC_GEV_DIR), 3);
	tg_tick(T0 + 800);
	zassert_equal(tg_count(RC_GEV_DIR), 4);
	zassert_equal(tg_get(RC_GEV_DIR, 3)->dir, d);
	tg_in(d, false, T0 + 801);
	tg_tick(T0 + 3000);
	zassert_equal(tg_count(RC_GEV_DIR), 4, "repeat stops at release");
	zassert_equal(tg_count(RC_GEV_CENTRE_DOWN) + tg_count(RC_GEV_LONG) + tg_count(RC_GEV_WARN), 0);
}

#define DIRT(name, idx) \
	ZTEST(rc_gesture, test_sw2_dir_##name##_tap) { dir_tap(RC_CENTRE_SW2, dirs[idx]); } \
	ZTEST(rc_gesture, test_pair_dir_##name##_tap) { dir_tap(RC_CENTRE_PAIR, dirs[idx]); } \
	ZTEST(rc_gesture, test_sw2_dir_##name##_hold_repeat) { dir_hold_repeat(RC_CENTRE_SW2, dirs[idx]); } \
	ZTEST(rc_gesture, test_pair_dir_##name##_hold_repeat) { dir_hold_repeat(RC_CENTRE_PAIR, dirs[idx]); }

DIRT(up, 0)
DIRT(down, 1)
DIRT(left, 2)
DIRT(right, 3)

ZTEST(rc_gesture, test_sw2_dir_then_centre_at_39ms_centre_wins)
{
	/* line 232: a direction that closed 0 to 40 ms before SW2 is dropped and the centre wins */
	for (int i = 0; i < 4; i++) {
		tg_start(RC_CENTRE_SW2);
		tg_in(dirs[i], true, T0);
		tg_in(RC_SW_CENTRE, true, T0 + 39);
		tg_tick(T0 + 39 + 1000);
		zassert_equal(tg_count(RC_GEV_DIR), 0);
		zassert_equal(tg_get(RC_GEV_CENTRE_DOWN, 0)->t, T0 + 39);
		zassert_equal(tg_count(RC_GEV_LONG), 1);
	}
}

ZTEST(rc_gesture, test_sw2_dir_then_centre_at_40ms_direction_kept)
{
	/* line 232: one that closed 40 ms or more before SW2 keeps its direction and SW2 is ignored until all switches are open */
	for (int i = 0; i < 4; i++) {
		tg_start(RC_CENTRE_SW2);
		tg_in(dirs[i], true, T0);
		tg_in(RC_SW_CENTRE, true, T0 + 40);
		tg_tick(T0 + 3000);
		zassert_equal(tg_get(RC_GEV_DIR, 0)->dir, dirs[i]);
		zassert_equal(tg_count(RC_GEV_CENTRE_DOWN), 0);
		zassert_equal(tg_count(RC_GEV_LONG) + tg_count(RC_GEV_WARN), 0);
	}
}

ZTEST(rc_gesture, test_pair_opposite_at_39ms_is_centre_stamped_second_edge)
{
	/* line 256 rules (1), (2); line 233: stamped at the second edge */
	for (int i = 0; i < 4; i++) {
		enum rc_switch opp = dirs[i ^ 1];

		tg_start(RC_CENTRE_PAIR);
		tg_in(dirs[i], true, T0);
		tg_in(opp, true, T0 + 39);
		tg_tick(T0 + 39 + 1000);
		zassert_equal(tg_count(RC_GEV_DIR), 0);
		zassert_equal(tg_get(RC_GEV_CENTRE_DOWN, 0)->t, T0 + 39);
		zassert_equal(tg_get(RC_GEV_LONG, 0)->t, T0 + 39 + 1000);
	}
}

ZTEST(rc_gesture, test_pair_opposite_at_40ms_is_direction)
{
	/* line 256 rule (3) and "a close of the opposite switch after the window is ignored" */
	for (int i = 0; i < 4; i++) {
		enum rc_switch opp = dirs[i ^ 1];

		tg_start(RC_CENTRE_PAIR);
		tg_in(dirs[i], true, T0);
		tg_in(opp, true, T0 + 40);
		tg_tick(T0 + 3000);
		zassert_equal(tg_get(RC_GEV_DIR, 0)->dir, dirs[i]);
		zassert_equal(tg_get(RC_GEV_DIR, 0)->t, T0 + 40);
		zassert_equal(tg_count(RC_GEV_CENTRE_DOWN) + tg_count(RC_GEV_LONG), 0);
	}
}

ZTEST(rc_gesture, test_pair_non_opposite_switch_ignored)
{
	/* line 256 rule (4) */
	tg_start(RC_CENTRE_PAIR);
	tg_in(RC_SW_UP, true, T0);
	tg_in(RC_SW_LEFT, true, T0 + 10);
	tg_tick(T0 + 40);
	zassert_equal(tg_count(RC_GEV_DIR), 1);
	zassert_equal(tg_get(RC_GEV_DIR, 0)->dir, RC_SW_UP);
	zassert_equal(tg_count(RC_GEV_CENTRE_DOWN), 0);
}

ZTEST(rc_gesture, test_pair_centre_has_no_repeat)
{
	/* line 256 rule (5) */
	tg_start(RC_CENTRE_PAIR);
	tg_in(RC_SW_UP, true, T0);
	tg_in(RC_SW_DOWN, true, T0 + 5);
	tg_tick(T0 + 4000);
	zassert_equal(tg_count(RC_GEV_DIR), 0);
	zassert_equal(tg_count(RC_GEV_LONG), 1);
}

ZTEST(rc_gesture, test_pair_ignores_btn_rec)
{
	/* line 233: BTN_REC P0.04 is unused in case PAIR */
	tg_start(RC_CENTRE_PAIR);
	tg_in(RC_SW_CENTRE, true, T0);
	tg_tick(T0 + 3000);
	zassert_equal(gl.n, 0);
	zassert_equal(rc_gesture_next_tick(&gg), RC_NO_TICK);
}

ZTEST(rc_gesture, test_dir_sent_then_others_ignored_until_all_open)
{
	/* line 254: after a direction event is sent, every other switch is ignored until all switches are open */
	tg_start(RC_CENTRE_SW2);
	tg_in(RC_SW_UP, true, T0);
	tg_tick(T0 + 40);
	tg_in(RC_SW_LEFT, true, T0 + 100);
	tg_in(RC_SW_UP, false, T0 + 150);
	tg_in(RC_SW_CENTRE, true, T0 + 200);
	tg_tick(T0 + 2000);
	zassert_equal(tg_count(RC_GEV_DIR), 1);
	zassert_equal(tg_count(RC_GEV_CENTRE_DOWN), 0);
}

/* ---- centre key: roll and release hold-off, line 255 ---- */

ZTEST(rc_gesture, test_sw2_roll_does_not_end_long_press)
{
	tg_start(RC_CENTRE_SW2);
	tg_in(RC_SW_CENTRE, true, T0);
	tg_in(RC_SW_RIGHT, true, T0 + 300);   /* thumb rolls toward a direction */
	tg_in(RC_SW_CENTRE, false, T0 + 400); /* SW2 opens, the direction is still closed */
	tg_tick(T0 + 1000);
	zassert_equal(tg_count(RC_GEV_LONG), 1);
	zassert_equal(tg_count(RC_GEV_DIR), 0, "no direction while the key is down");
}

ZTEST(rc_gesture, test_pair_one_side_lets_go_does_not_end_long_press)
{
	tg_start(RC_CENTRE_PAIR);
	tg_in(RC_SW_LEFT, true, T0 - 10);
	tg_in(RC_SW_RIGHT, true, T0);
	tg_in(RC_SW_RIGHT, false, T0 + 300);
	tg_tick(T0 + 1000);
	zassert_equal(tg_count(RC_GEV_LONG), 1);
	zassert_equal(tg_count(RC_GEV_DIR), 0);
}

ZTEST(rc_gesture, test_release_holdoff_29ms_bounce_same_press)
{
	/* line 224: 30 ms release hold-off; a re-close inside it keeps the key down */
	tg_start(RC_CENTRE_SW2);
	tg_in(RC_SW_CENTRE, true, T0);
	tg_in(RC_SW_CENTRE, false, T0 + 200);
	tg_in(RC_SW_CENTRE, true, T0 + 229);
	tg_tick(T0 + 1000);
	zassert_equal(tg_count(RC_GEV_CENTRE_UP), 0);
	zassert_equal(tg_count(RC_GEV_LONG), 1);
}

ZTEST(rc_gesture, test_release_holdoff_30ms_ends_press_stamped_at_release)
{
	/* line 255: CENTRE_UP is stamped at the instant the last switch opened */
	tg_start(RC_CENTRE_SW2);
	tg_in(RC_SW_CENTRE, true, T0);
	tg_in(RC_SW_CENTRE, false, T0 + 200);
	tg_in(RC_SW_CENTRE, true, T0 + 230);
	zassert_equal(tg_count(RC_GEV_CENTRE_UP), 1);
	zassert_equal(tg_get(RC_GEV_CENTRE_UP, 0)->t, T0 + 200);
	zassert_equal(tg_count(RC_GEV_CENTRE_DOWN), 2);
}

ZTEST(rc_gesture, test_release_before_mark_in_holdoff_no_long)
{
	/* held 990 ms: the 1,000 ms mark falls inside the hold-off, the press was shorter: no long */
	tg_start(RC_CENTRE_SW2);
	tg_in(RC_SW_CENTRE, true, T0);
	tg_in(RC_SW_CENTRE, false, T0 + 990);
	tg_tick(T0 + 3000);
	zassert_equal(tg_count(RC_GEV_LONG), 0);
}

/* ---- next tick ---- */

ZTEST(rc_gesture, test_next_tick_follows_deadlines)
{
	tg_start(RC_CENTRE_SW2);
	zassert_equal(rc_gesture_next_tick(&gg), RC_NO_TICK);
	tg_in(RC_SW_CENTRE, true, T0);
	zassert_equal(rc_gesture_next_tick(&gg), T0 + 500);
	tg_tick(T0 + 500);
	zassert_equal(rc_gesture_next_tick(&gg), T0 + 1000);
	tg_start(RC_CENTRE_SW2);
	tg_in(RC_SW_CENTRE, true, T0);
	tg_in(RC_SW_CENTRE, false, T0 + 100);
	zassert_equal(rc_gesture_next_tick(&gg), T0 + 130);
	tg_tick(T0 + 130);
	zassert_equal(rc_gesture_next_tick(&gg), T0 + 100 + 401);
	tg_tick(T0 + 501);
	zassert_equal(rc_gesture_next_tick(&gg), RC_NO_TICK);
	tg_in(RC_SW_UP, true, T0 + 1000);
	zassert_equal(rc_gesture_next_tick(&gg), T0 + 1040);
}

ZTEST(rc_core_timing, test_core_next_tick_includes_state_timers)
{
	th_start(RC_ST_ERR_MIC_FAULT);
	zassert_equal(rc_core_next_tick(&core), TH_T0 + SPEC_MIC_FAULT_MS);
	th_start(RC_ST_ERR_STORAGE_FAULT);
	zassert_equal(rc_core_next_tick(&core), TH_T0 + SPEC_STORAGE_RETRY_MS);
	th_start(RC_ST_STANDBY);
	zassert_equal(rc_core_next_tick(&core), RC_NO_TICK);
}

ZTEST_SUITE(rc_gesture, NULL, NULL, NULL, NULL, NULL);
ZTEST_SUITE(rc_core_timing, NULL, NULL, NULL, NULL, NULL);
