/* Suite motor_player (software step 6, unit U6): the pattern player against the simulated MOTOR pin.
 * Rows C26, C28, C29, C30, C31, C33, P7 of firmware/docs/step6-plan.md. "FW l.N" = line N of design/firmware.md.
 * Pin times are typed from FW l.320 to l.328 (on / off in ms, pin times, FW l.315); the pin's edge times are read from
 * the simulated driver's event log (one entry per call, with its time). */
#include "common.h"

static void before(void *f)
{
	ARG_UNUSED(f);
	t_reset();
}

static void after(void *f)
{
	ARG_UNUSED(f);
	rmo_stop();
}

ZTEST_SUITE(motor_player, NULL, NULL, before, after, NULL);

/* FW l.320 to l.328, typed: the pin's edges in ms from the pattern start (first = high, then alternating). */
struct spec_pat {
	enum rrec_pattern id;
	const char *name;
	uint8_t n;
	uint32_t edge_ms[6];
	uint32_t total_ms;
	uint8_t pulses;
};
static const struct spec_pat spec[7] = {
	{ RREC_PAT_M1, "M1", 2, { 0, 80 }, 80, 1 },                          /* l.320: 80 on */
	{ RREC_PAT_M2, "M2", 4, { 0, 80, 200, 280 }, 280, 2 },               /* l.321: 80 on, 120 off, 80 on */
	{ RREC_PAT_M3, "M3", 6, { 0, 80, 200, 280, 400, 480 }, 480, 3 },     /* l.322 */
	{ RREC_PAT_MH, "MH", 2, { 0, 40 }, 40, 1 },                          /* l.323: 40 on */
	{ RREC_PAT_MT, "MT", 2, { 0, 25 }, 25, 1 },                          /* l.324: 25 on */
	{ RREC_PAT_MW, "MW", 2, { 0, 60 }, 60, 1 },                          /* l.325: 60 on */
	{ RREC_PAT_MF, "MF", 4, { 0, 300, 500, 800 }, 800, 2 },              /* l.326: 300 on, 200 off, 300 on */
};

/* C29, C31, FW l.315, l.320 to l.328: every on and off edge of every pattern at its millisecond. */
ZTEST(motor_player, test_every_pattern_pin_times)
{
	for (int i = 0; i < 7; i++) {
		struct t_edge ev[T_MAX_EV];

		t_reset();
		int64_t call_us = t_now_us();

		zassert_equal(rmo_play(spec[i].id), 0, "%s", spec[i].name);
		zassert_true(rmo_playing(), "%s plays", spec[i].name);
		t_ms(spec[i].total_ms + 100);
		int n = t_pin_events(ev);

		zassert_true(n >= 1, "%s: no edge", spec[i].name);
		/* the pattern starts at the call (pin high without a delay) */
		zassert_true(ev[0].t_us - call_us >= 0 && ev[0].t_us - call_us < 1000, "%s starts at the call", spec[i].name);
		t_check_edges(ev, n, ev[0].t_us, spec[i].edge_ms, spec[i].n);
		zassert_false(rmo_playing(), "%s ended", spec[i].name);
		zassert_false(rhw_sim_motor_pin(), "%s: pin low at the end", spec[i].name);
		printk("pin times %s: %d edges, last at %lld us after the start\n", spec[i].name, n,
		       (long long)(ev[n - 1].t_us - ev[0].t_us));
	}
}

/* C31: the pure table holds the same totals and pulse counts (FW l.320 to l.328, column "Total ms"). */
ZTEST(motor_player, test_pattern_table)
{
	for (int i = 0; i < 7; i++) {
		zassert_equal(rml_total_ms(spec[i].id), spec[i].total_ms, "%s total", spec[i].name);
		zassert_equal(rml_pulses(spec[i].id), spec[i].pulses, "%s pulses", spec[i].name);
	}
	zassert_is_null(rml_get(0));
	zassert_is_null(rml_get(8));
	zassert_equal(rml_total_ms(0), 0);
}

/* C28, FW l.314: MOTOR high = motor on, no PWM: exactly one high and one low per on segment, nothing in between. */
ZTEST(motor_player, test_one_high_per_on_segment)
{
	for (int i = 0; i < 7; i++) {
		struct t_edge ev[T_MAX_EV];

		t_reset();
		zassert_equal(rmo_play(spec[i].id), 0);
		t_ms(spec[i].total_ms + 100);
		int n = t_pin_events(ev);
		int highs = 0;
		int lows = 0;

		for (int k = 0; k < n; k++) {
			if (ev[k].high) {
				highs++;
				zassert_true(k == 0 || !ev[k - 1].high, "%s: two highs in a row", spec[i].name);
			} else {
				lows++;
				zassert_true(k > 0 && ev[k - 1].high, "%s: low without a high", spec[i].name);
			}
		}
		zassert_equal(highs, spec[i].pulses, "%s: one high per on segment", spec[i].name);
		zassert_equal(lows, spec[i].pulses, "%s: one low per on segment", spec[i].name);
		zassert_equal(n, 2 * spec[i].pulses, "%s: no other pin event", spec[i].name);
		/* in the middle of the first on segment the pin is high and stays quiet: no event until its end */
	}
	t_reset();
	zassert_equal(rmo_play(RREC_PAT_MF), 0);
	t_ms(150);
	struct t_edge ev[T_MAX_EV];

	zassert_equal(t_pin_events(ev), 1, "MF at 150 ms: one event (the high), no pulse train");
	zassert_true(rhw_sim_motor_pin());
}

/* The 7 x 7 table of FW l.318, typed: row = the pattern playing, column = the pattern asked for, in the order M1, M2,
 * M3, MH, MT, MW, MF. 0 = it plays; -EBUSY = refused (MH and MT never cut M1, M2, M3, MF). */
#define E (-EBUSY)
static const int expect_ret[7][7] = {
	/*        M1 M2 M3 MH MT MW MF */
	/* M1 */ { 0, 0, 0, E, E, 0, 0 },
	/* M2 */ { 0, 0, 0, E, E, 0, 0 },
	/* M3 */ { 0, 0, 0, E, E, 0, 0 },
	/* MH */ { 0, 0, 0, 0, 0, 0, 0 },
	/* MT */ { 0, 0, 0, 0, 0, 0, 0 },
	/* MW */ { 0, 0, 0, 0, 0, 0, 0 },
	/* MF */ { 0, 0, 0, E, E, 0, 0 },
};

/* C30, FW l.318: all 49 pairs. A plays; 10 ms into its first on segment B is asked for. Refused: A's schedule goes
 * on. Accepted: B's schedule starts at that moment (the pin, already high, stays high: no new edge). */
ZTEST(motor_player, test_replace_rules)
{
	int refused = 0;
	int played = 0;

	for (int a = 0; a < 7; a++) {
		for (int b = 0; b < 7; b++) {
			struct t_edge ev[T_MAX_EV];
			uint32_t want[8];
			int nw;

			t_reset();
			zassert_equal(rmo_play(spec[a].id), 0);
			t_ms(10);
			int64_t b_us = t_now_us();
			int r = rmo_play(spec[b].id);

			zassert_equal(r, expect_ret[a][b], "%s playing, %s asked for: returned %d, expected %d",
				      spec[a].name, spec[b].name, r, expect_ret[a][b]);
			t_ms(1000);
			int n = t_pin_events(ev);
			int64_t a_us = ev[0].t_us;

			if (r == 0) {
				/* the pin went high for A and stays high; B's edges after its first run from B's start */
				played++;
				nw = 0;
				want[nw++] = 0;
				for (int k = 1; k < spec[b].n; k++) {
					want[nw++] = (uint32_t)((b_us - a_us) / 1000) + spec[b].edge_ms[k];
				}
				zassert_equal(t_n_started(), 2, "both patterns reported started");
				zassert_equal(t_started(1)->pattern, spec[b].id);
			} else {
				refused++;
				nw = spec[a].n;
				for (int k = 0; k < nw; k++) {
					want[k] = spec[a].edge_ms[k];
				}
				zassert_equal(t_n_started(), 1, "a refused pattern is not reported");
			}
			if (r == 0) {
				/* the replacement's times are counted from the moment it was asked for: check to the
				 * microsecond of that moment, not of the rounded ms */
				zassert_equal(n, nw, "%s then %s: %d pin events, expected %d", spec[a].name, spec[b].name, n, nw);
				for (int k = 1; k < nw; k++) {
					int64_t d = ev[k].t_us - b_us;
					int64_t e = (int64_t)spec[b].edge_ms[k] * 1000;

					zassert_equal(ev[k].high, (k % 2) == 0);
					zassert_true(d >= e - 1 && d < e + 1000, "%s then %s: edge %d at %lld us after the call, expected %lld",
						     spec[a].name, spec[b].name, k, (long long)d, (long long)e);
				}
			} else {
				t_check_edges(ev, n, a_us, want, nw);
			}
			zassert_false(rmo_playing());
			zassert_false(rhw_sim_motor_pin());
		}
	}
	printk("replace rules: 49 pairs, %d played, %d refused\n", played, refused);
	zassert_equal(refused, 8, "FW l.318: MH and MT against M1, M2, M3, MF are the 8 refusals");
	zassert_equal(played, 41);
}

/* C30, FW l.318: a replacement in an off gap of the playing pattern: MW starts at once (pin high), the rest of M2
 * (its second pulse) never comes. MH in the same gap is refused. */
ZTEST(motor_player, test_replace_in_gap)
{
	struct t_edge ev[T_MAX_EV];

	zassert_equal(rmo_play(RREC_PAT_M2), 0);
	t_ms(100);                                       /* M2: on 0..80, off 80..200 */
	zassert_false(rhw_sim_motor_pin());
	zassert_equal(rmo_play(RREC_PAT_MH), -EBUSY);
	zassert_false(rhw_sim_motor_pin(), "a refused MH does not touch the pin");
	int64_t w_us = t_now_us();

	zassert_equal(rmo_play(RREC_PAT_MW), 0);
	zassert_true(rhw_sim_motor_pin(), "MW starts at once");
	t_ms(500);
	int n = t_pin_events(ev);

	zassert_equal(n, 4, "H (M2), L (M2), H (MW), L (MW) and nothing from M2's second pulse");
	zassert_true(ev[2].t_us - w_us >= 0 && ev[2].t_us - w_us < 1000);
	zassert_true(ev[3].t_us - w_us >= 60000 - 1 && ev[3].t_us - w_us < 61000, "MW is 60 ms on");
}

/* C26, FW l.301, FW 2.2: the setting "Vibration" off disables MH and MT only; M1, M2, M3, MF and MW still play. */
ZTEST(motor_player, test_vibration_off_keeps_the_others)
{
	struct t_edge ev[T_MAX_EV];

	rmo_set_vibration(false);
	zassert_equal(rmo_play(RREC_PAT_MH), -ECANCELED);
	zassert_equal(rmo_play(RREC_PAT_MT), -ECANCELED);
	t_ms(200);
	zassert_equal(t_pin_events(ev), 0, "MH and MT: no pin event");
	zassert_false(rmo_playing());
	zassert_equal(t_n_started(), 0);
	for (int i = 0; i < 7; i++) {
		if (spec[i].id == RREC_PAT_MH || spec[i].id == RREC_PAT_MT) {
			continue;
		}
		t_reset();
		rmo_set_vibration(false);
		zassert_equal(rmo_play(spec[i].id), 0, "%s plays with Vibration off", spec[i].name);
		t_ms(spec[i].total_ms + 100);
		int n = t_pin_events(ev);

		zassert_true(n >= 1, "%s: no edge with Vibration off", spec[i].name);
		t_check_edges(ev, n, ev[0].t_us, spec[i].edge_ms, spec[i].n);
		zassert_equal(t_n_started(), 1);
	}
	/* a refused-by-setting pattern does not cut the one playing, and the setting back on lets MH play */
	t_reset();
	rmo_set_vibration(false);
	zassert_equal(rmo_play(RREC_PAT_M1), 0);
	zassert_equal(rmo_play(RREC_PAT_MT), -ECANCELED);
	zassert_true(rmo_playing());
	t_ms(200);
	rmo_set_vibration(true);
	zassert_equal(rmo_play(RREC_PAT_MH), 0);
	t_ms(100);
	zassert_equal(t_pin_events(ev), 4, "M1 (2 edges) and MH (2 edges)");
}

/* An unknown id is refused with -EINVAL and nothing happens (also not a started callback). */
ZTEST(motor_player, test_unknown_id)
{
	struct t_edge ev[T_MAX_EV];

	zassert_equal(rmo_play(0), -EINVAL);
	zassert_equal(rmo_play(8), -EINVAL);
	zassert_equal(rmo_play(255), -EINVAL);
	t_ms(100);
	zassert_equal(t_pin_events(ev), 0);
	zassert_equal(t_n_started(), 0);
	zassert_false(rmo_playing());
}

/* C33, FW l.333; FW l.496: every pin edge is reported with the clock's cycles of that moment (the simulated counter
 * runs 1,000,000 per second, so a cycle is a microsecond); the pattern's start is reported with its id and uptime ms. */
ZTEST(motor_player, test_edge_times_reported)
{
	for (int i = 0; i < 7; i++) {
		struct t_edge ev[T_MAX_EV];

		t_reset();
		zassert_equal(rhw_clock()->cycles_per_sec(), 1000000u, "the simulated counter");
		zassert_equal(rmo_play(spec[i].id), 0);
		t_ms(spec[i].total_ms + 100);
		int n = t_pin_events(ev);

		zassert_equal(n, spec[i].n, "%s", spec[i].name);
		zassert_equal(t_n_edge(), n, "%s: one edge callback per pin edge", spec[i].name);
		for (int k = 0; k < n; k++) {
			zassert_equal(t_edge(k)->high, ev[k].high, "%s edge %d level", spec[i].name, k);
			zassert_equal((int64_t)t_edge(k)->cycles, ev[k].t_us, "%s edge %d: cycles %llu, pin time %lld us",
				      spec[i].name, k, (unsigned long long)t_edge(k)->cycles, (long long)ev[k].t_us);
		}
		zassert_equal(t_n_started(), 1);
		zassert_equal(t_started(0)->pattern, spec[i].id);
		zassert_equal(t_started(0)->t_ms, ev[0].t_us / 1000, "%s: start time in ms", spec[i].name);
	}
}

/* P7, FW l.922: the pin (which enables U11) is low between patterns, in the gaps of a pattern and at the end; it is
 * high only inside an on segment. M3 (FW l.322) is sampled in the middle of each of its five segments. */
ZTEST(motor_player, test_pin_low_between_patterns)
{
	struct t_edge ev[T_MAX_EV];

	zassert_false(rhw_sim_motor_pin(), "low after init");
	t_ms(1000);
	zassert_equal(t_pin_events(ev), 0, "no pin event while nothing plays");
	zassert_equal(rmo_play(RREC_PAT_M3), 0);
	static const uint32_t mid_ms[5] = { 40, 140, 240, 340, 440 };   /* middles of on 0..80, off 80..200, on, off, on 400..480 */
	static const bool want_high[5] = { true, false, true, false, true };
	uint32_t at = 0;

	for (int k = 0; k < 5; k++) {
		t_ms(mid_ms[k] - at);
		at = mid_ms[k];
		zassert_equal(rhw_sim_motor_pin(), want_high[k], "M3 at %u ms", mid_ms[k]);
	}
	t_ms(100);
	zassert_false(rhw_sim_motor_pin(), "low after M3");
	zassert_false(rmo_playing());
	/* two patterns one after the other: the pin is low between them */
	zassert_equal(rmo_play(RREC_PAT_M1), 0);
	t_ms(200);
	zassert_false(rhw_sim_motor_pin());
	zassert_equal(rmo_play(RREC_PAT_MH), 0);
	t_ms(100);
	zassert_false(rhw_sim_motor_pin());
	zassert_equal(t_pin_events(ev), 6 + 2 + 2);
}

/* FW l.937: rmo_stop sets the pin low at once, in an on segment and in a gap, and nothing comes after it. */
ZTEST(motor_player, test_stop_pin_low_at_once)
{
	struct t_edge ev[T_MAX_EV];

	zassert_equal(rmo_play(RREC_PAT_MF), 0);
	t_ms(100);
	zassert_true(rhw_sim_motor_pin());
	rmo_stop();
	zassert_false(rhw_sim_motor_pin());
	zassert_false(rmo_playing());
	t_ms(1500);
	zassert_equal(t_pin_events(ev), 2, "H then L; the second pulse of MF never comes");
	zassert_equal(t_n_edge(), 2);
	rmo_stop();                                          /* stopping again changes nothing */
	zassert_equal(t_pin_events(ev), 2);
}

/* FW l.318: the same pattern asked for again while it plays restarts it; the pin stays high through the restart. */
ZTEST(motor_player, test_same_pattern_restarts)
{
	struct t_edge ev[T_MAX_EV];

	zassert_equal(rmo_play(RREC_PAT_MF), 0);
	t_ms(100);
	int64_t again_us = t_now_us();

	zassert_equal(rmo_play(RREC_PAT_MF), 0);
	t_ms(1000);
	int n = t_pin_events(ev);

	zassert_equal(n, 4, "H, then the restarted MF's L, H, L");
	zassert_true(ev[1].t_us - again_us >= 300000 - 1 && ev[1].t_us - again_us < 301000, "300 ms from the restart");
	zassert_true(ev[3].t_us - again_us >= 800000 - 1 && ev[3].t_us - again_us < 801000, "800 ms from the restart");
}
