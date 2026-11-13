/* Suite factory_input (software step 6, unit U8): T-JOY (0x30) and T-CENTRE (0x31), FW l.1026, l.1027, and the rule that
 * factory test mode never starts a recording (FW l.209, l.1027). Rows T15.
 * The events of the centre come from the REAL gesture recogniser (ring_core) fed by edges, the stand-in for the join
 * hands them to rfa_input() (rfa.h: "the join calls it instead of nothing"). The real core in FACTORY_TEST is fed the
 * same edges and must answer with no recording action. */
#include <ring_core/rc_core.h>

#include "common.h"

ZTEST_SUITE(factory_input, NULL, NULL, fx_before, fx_after, NULL);

#define FEED_STACK 4096
K_THREAD_STACK_DEFINE(feed_stack, FEED_STACK);
static struct k_thread feed_thr;

struct ev_item {
	int64_t off_ms;
	uint8_t ev;
};
static const struct ev_item *items;
static int n_items;
static int64_t base_ms;

static void sleep_to(int64_t t)
{
	int64_t d = t - rhw_clock()->now_ms();

	if (d > 0) {
		k_sleep(K_MSEC(d));
	}
}

static void feed_fn(void *a, void *b, void *c)
{
	ARG_UNUSED(a);
	ARG_UNUSED(b);
	ARG_UNUSED(c);
	for (int i = 0; i < n_items; i++) {
		sleep_to(base_ms + items[i].off_ms);
		rfa_input((enum rfa_input)items[i].ev, rhw_clock()->now_ms());
	}
}

static void start_feed(const struct ev_item *it, int n)
{
	items = it;
	n_items = n;
	base_ms = rhw_clock()->now_ms();
	k_thread_create(&feed_thr, feed_stack, K_THREAD_STACK_SIZEOF(feed_stack), feed_fn, NULL, NULL, NULL,
			K_PRIO_PREEMPT(5), 0, K_NO_WAIT);
}

static void end_feed(void)
{
	zassert_ok(k_thread_join(&feed_thr, K_SECONDS(30)));
}

/* returns the number of events; fills ev[] and rel[] */
static int run_window(uint8_t sub, uint16_t window_ms, uint8_t *result, uint8_t *dropped, uint8_t *ev, uint32_t *rel)
{
	uint8_t req[3] = { sub, (uint8_t)window_ms, (uint8_t)(window_ms >> 8) };
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;

	zassert_equal(fx_do(req, 3, true, out, &n, &eff), 0);
	zassert_equal(eff, RFA_EFFECT_NONE);
	zassert_true(n >= 3);
	*result = out[0];
	*dropped = out[1];
	int cnt = out[2];

	zassert_equal(n, 3u + 5u * (size_t)cnt, "length %u for %d events", (unsigned)n, cnt);
	for (int i = 0; i < cnt; i++) {
		ev[i] = out[3 + 5 * i];
		rel[i] = fx_u32(&out[4 + 5 * i]);
	}
	return cnt;
}

/* T15: the four directions in turn, each reported once with its time, no other event; the centre's down and up are
 * reported; the gestures of the centre are not part of T-JOY. */
ZTEST(factory_input, test_directions_reported)
{
	static const struct ev_item script[] = {
		{ 100, RFA_IN_UP }, { 300, RFA_IN_DOWN }, { 500, RFA_IN_LEFT }, { 700, RFA_IN_RIGHT },
		{ 900, RFA_IN_CENTRE_DOWN }, { 1000, RFA_IN_CENTRE_UP }, { 1400, RFA_IN_SINGLE },
	};
	uint8_t ev[RFA_MAX_EVENTS + 1];
	uint32_t rel[RFA_MAX_EVENTS + 1];
	uint8_t result, dropped;

	/* before a test runs the events are not kept */
	rfa_input(RFA_IN_UP, 5);
	start_feed(script, ARRAY_SIZE(script));
	int n = run_window(RREC_FAC_JOY, 2000, &result, &dropped, ev, rel);

	end_feed();
	zassert_equal(result, 0, "pass");
	zassert_equal(dropped, 0);
	zassert_equal(n, 6, "six events, the single press is not part of T-JOY: %d", n);
	static const uint8_t want[6] = { RFA_IN_UP, RFA_IN_DOWN, RFA_IN_LEFT, RFA_IN_RIGHT, RFA_IN_CENTRE_DOWN,
					 RFA_IN_CENTRE_UP };
	static const uint32_t at[6] = { 100, 300, 500, 700, 900, 1000 };

	for (int i = 0; i < 6; i++) {
		zassert_equal(ev[i], want[i], "event %d", i);
		zassert_within(rel[i], at[i], 5, "event %d at %u ms", i, rel[i]);
	}
	/* an event after the window is not kept: the next test with no event ends as a timeout */
	rfa_input(RFA_IN_DOWN, 5000);
	n = run_window(RREC_FAC_JOY, 100, &result, &dropped, ev, rel);
	zassert_equal(n, 0);
	zassert_equal(result, 2, "no event in the window: timeout (FW l.1020)");

	/* more events than fit: the first 32 are kept and the rest are counted */
	static struct ev_item many[40];

	for (int i = 0; i < 40; i++) {
		many[i].off_ms = 10 + 10 * i;
		many[i].ev = RFA_IN_UP;
	}
	start_feed(many, 40);
	n = run_window(RREC_FAC_JOY, 1000, &result, &dropped, ev, rel);
	end_feed();
	zassert_equal(n, 32, "RFA_MAX_EVENTS events kept");
	zassert_equal(dropped, 8, "eight counted as dropped");
	zassert_equal(fx_rec_calls, 0);
}

/* the stand-in of the join's mapping from the gesture recogniser to the factory part */
static void gev_to_rfa(const struct rc_gev_list *l)
{
	for (int i = 0; i < l->n; i++) {
		const struct rc_gev *e = &l->e[i];
		enum rfa_input in = 0;

		switch (e->type) {
		case RC_GEV_DIR:
			in = e->dir == RC_SW_UP ? RFA_IN_UP : e->dir == RC_SW_DOWN ? RFA_IN_DOWN :
			     e->dir == RC_SW_LEFT ? RFA_IN_LEFT : RFA_IN_RIGHT;
			break;
		case RC_GEV_CENTRE_DOWN:
			in = RFA_IN_CENTRE_DOWN;
			break;
		case RC_GEV_CENTRE_UP:
			in = RFA_IN_CENTRE_UP;
			break;
		case RC_GEV_WARN:
			in = RFA_IN_MW;
			break;
		case RC_GEV_LONG:
			in = RFA_IN_LONG;
			break;
		case RC_GEV_SHORT:
			in = RFA_IN_SINGLE;
			break;
		case RC_GEV_DOUBLE:
			in = RFA_IN_DOUBLE;
			break;
		}
		if (in != 0) {
			rfa_input(in, e->t);
		}
	}
}

struct edge {
	int64_t off_ms;
	bool pressed;
};
static const struct edge *edges;
static int n_edges;
static uint32_t bad_actions;
static uint32_t core_actions;

static uint8_t first_bad = 0xFF;

static void count_bad(const struct rc_actions *acts)
{
	core_actions += acts->n;
	for (int k = 0; k < acts->n; k++) {
		uint8_t a = acts->a[k];

		if (a == RC_ACT_OPEN || a == RC_ACT_CLOSE || a == RC_ACT_M1 || a == RC_ACT_M2) {
			bad_actions++;
			if (first_bad == 0xFF) {
				first_bad = a;
			}
		}
	}
}

static void gesture_fn(void *a, void *b, void *c)
{
	struct rc_gesture g;
	struct rc_core core;
	struct rc_gev_list l;
	struct rc_actions acts;

	ARG_UNUSED(a);
	ARG_UNUSED(b);
	ARG_UNUSED(c);
	rc_gesture_init(&g, RC_CENTRE_SW2);
	rc_core_init(&core, RC_CENTRE_SW2, RC_ST_FACTORY_TEST, base_ms);
	rc_core_facts(&core)->factory_flag = true;
	for (int i = 0; i < n_edges; i++) {
		int64_t t = base_ms + edges[i].off_ms;

		/* every deadline before this edge first */
		for (;;) {
			rc_ms_t nt = rc_gesture_next_tick(&g);
			rc_ms_t cn = rc_core_next_tick(&core);
			rc_ms_t m = nt < cn ? nt : cn;

			if (m == RC_NO_TICK || m > t) {
				break;
			}
			sleep_to(m);
			l.n = 0;
			rc_gesture_tick(&g, m, &l);
			gev_to_rfa(&l);
			rc_actions_clear(&acts);
		rc_core_tick(&core, m, &acts);
				count_bad(&acts);
		}
		sleep_to(t);
		l.n = 0;
		rc_gesture_input(&g, RC_SW_CENTRE, edges[i].pressed, t, &l);
		gev_to_rfa(&l);
		rc_actions_clear(&acts);
		rc_core_input(&core, RC_SW_CENTRE, edges[i].pressed, t, &acts);
		count_bad(&acts);
	}
	/* run out the deadlines after the last edge */
	for (int guard = 0; guard < 16; guard++) {
		rc_ms_t nt = rc_gesture_next_tick(&g);
		rc_ms_t cn = rc_core_next_tick(&core);
		rc_ms_t m = nt < cn ? nt : cn;

		if (m == RC_NO_TICK) {
			break;
		}
		sleep_to(m);
		l.n = 0;
		rc_gesture_tick(&g, m, &l);
		gev_to_rfa(&l);
		rc_actions_clear(&acts);
		rc_core_tick(&core, m, &acts);
		count_bad(&acts);
	}
}

/* T15, FW l.1027: the jig presses the centre once, twice (200 ms gap) and long (1,500 ms); the ring reports single,
 * double, long and the pulse MW at 500 ms of the long press; factory test mode reports the events and never starts a
 * recording. */
ZTEST(factory_input, test_centre_reported_never_records)
{
	static const struct edge script[] = {
		{ 100, true }, { 200, false },                                   /* once */
		{ 1000, true }, { 1100, false }, { 1300, true }, { 1400, false }, /* twice, 200 ms gap */
		{ 3000, true }, { 4500, false },                                 /* long, 1,500 ms */
	};
	uint8_t ev[RFA_MAX_EVENTS + 1];
	uint32_t rel[RFA_MAX_EVENTS + 1];
	uint8_t result, dropped;
	int singles = 0, doubles = 0, longs = 0, mws = 0, others = 0;
	uint32_t t_long = 0, t_mw = 0;

	edges = script;
	n_edges = ARRAY_SIZE(script);
	bad_actions = 0;
	core_actions = 0;
	first_bad = 0xFF;
	base_ms = rhw_clock()->now_ms();
	k_thread_create(&feed_thr, feed_stack, K_THREAD_STACK_SIZEOF(feed_stack), gesture_fn, NULL, NULL, NULL,
			K_PRIO_PREEMPT(5), 0, K_NO_WAIT);
	int n = run_window(RREC_FAC_CENTRE, 6000, &result, &dropped, ev, rel);

	end_feed();
	zassert_equal(result, 0);
	zassert_equal(dropped, 0);
	for (int i = 0; i < n; i++) {
		switch (ev[i]) {
		case RFA_IN_SINGLE:
			singles++;
			break;
		case RFA_IN_DOUBLE:
			doubles++;
			break;
		case RFA_IN_LONG:
			longs++;
			t_long = rel[i];
			break;
		case RFA_IN_MW:
			mws++;
			t_mw = rel[i];
			break;
		case RFA_IN_CENTRE_DOWN:
		case RFA_IN_CENTRE_UP:
			break;
		default:
			others++;
		}
	}
	zassert_equal(singles, 1, "one single press");
	zassert_equal(doubles, 1, "one double press");
	zassert_equal(longs, 1, "one long press");
	zassert_equal(mws, 1, "one warning pulse MW");
	zassert_equal(others, 0, "no direction in a centre test");
	zassert_within(t_mw, 3000 + 500, 5, "MW at 500 ms of the long press (FW l.1027), at %u", t_mw);
	zassert_within(t_long, 3000 + RREC_LONG_PRESS_MS, 5, "long at 1,000 ms of the hold, at %u", t_long);

	/* the real core, in FACTORY_TEST, fed the same edges, asked for no recording action; the factory part started no
	 * recording, switched no rail, wrote nothing to the card */
	zassert_equal(bad_actions, 0, "first bad action %s; the core's actions in FACTORY_TEST never open or close a recording or play M1/M2", rc_action_name(first_bad));
	zassert_equal(fx_rec_calls, 0, "no test recording by a centre event");
	zassert_equal(fx_count(RHW_EV_PMIC_RAIL), 0, "no rail switched");
	zassert_equal(fx_count(RHW_EV_MIC_START), 0, "no microphone started");
	zassert_equal(fx_count(RHW_EV_DISK_WRITE), 0, "nothing written to the card");
	zassert_equal(fx_sign_calls, 0, "no sign asked for");
}
