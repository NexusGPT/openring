#include <string.h>
#include "th.h"

struct rc_core core;
struct rc_actions out;
struct rc_actions rest;
rc_ms_t th_now;
struct rc_gesture gg;
struct rc_gev_list gl;

void th_start_src(enum rc_state st, enum rc_centre_source src)
{
	th_now = TH_T0;
	rc_core_init(&core, src, st, th_now);
	rc_actions_clear(&out);
	rc_actions_clear(&rest);
}

void th_start(enum rc_state st)
{
	th_start_src(st, RC_CENTRE_SW2);
}

void th_event(enum rc_event ev)
{
	rc_actions_clear(&out);
	rc_core_event(&core, ev, th_now, &out);
}

void th_batt(enum rc_batt level)
{
	rc_actions_clear(&out);
	rc_core_battery(&core, level, th_now, &out);
}

void th_tick_to(rc_ms_t t, struct rc_actions *o)
{
	for (int i = 0; i < 1000; i++) {
		rc_ms_t n = rc_core_next_tick(&core);

		if (n > t) {
			break;
		}
		rc_core_tick(&core, n, o);
	}
	rc_core_tick(&core, t, o);
	th_now = t;
}

void th_sw(enum rc_switch sw, bool pressed, rc_ms_t t, struct rc_actions *o)
{
	th_tick_to(t, o);
	rc_core_input(&core, sw, pressed, t, o);
	th_now = t;
}

void th_long(void)
{
	rc_ms_t t0 = th_now;

	rc_actions_clear(&rest);
	th_sw(RC_SW_CENTRE, true, t0, &rest);
	th_tick_to(t0 + SPEC_LONG_MS - 1, &rest);
	zassert_equal(rest.last_row, -1, "no row before the 1,000 ms mark");
	rc_actions_clear(&out);
	th_tick_to(t0 + SPEC_LONG_MS, &out);
	rc_actions_clear(&rest);
	th_sw(RC_SW_CENTRE, false, t0 + 1200, &rest);
	th_tick_to(t0 + 3000, &rest);
	zassert_equal(rest.n, 0, "the release after a long press does nothing");
}

void th_short(void)
{
	rc_ms_t t0 = th_now;

	rc_actions_clear(&rest);
	th_sw(RC_SW_CENTRE, true, t0, &rest);
	th_sw(RC_SW_CENTRE, false, t0 + 100, &rest);
	th_tick_to(t0 + 100 + SPEC_DOUBLE_WINDOW_MS, &rest);
	zassert_equal(rest.last_row, -1, "no row while the window is open");
	rc_actions_clear(&out);
	th_tick_to(t0 + 100 + SPEC_DOUBLE_WINDOW_MS + 1, &out);
}

void th_double(void)
{
	rc_ms_t t0 = th_now;

	rc_actions_clear(&rest);
	th_sw(RC_SW_CENTRE, true, t0, &rest);
	th_sw(RC_SW_CENTRE, false, t0 + 100, &rest);
	th_sw(RC_SW_CENTRE, true, t0 + 200, &rest);
	rc_actions_clear(&out);
	th_sw(RC_SW_CENTRE, false, t0 + 300, &out);
	th_tick_to(t0 + 300 + SPEC_RELEASE_HOLDOFF_MS, &out);
	rc_actions_clear(&rest);
	th_tick_to(t0 + 3000, &rest);
}

void th_expect(const struct rc_actions *o, const uint8_t *exp, size_t n)
{
	zassert_equal(o->n, n, "action count");
	for (size_t i = 0; i < n && i < o->n; i++) {
		zassert_equal(o->a[i], exp[i], "action %u", (unsigned)i);
	}
}

bool th_has(const struct rc_actions *o, enum rc_action a)
{
	for (uint8_t i = 0; i < o->n; i++) {
		if (o->a[i] == a) {
			return true;
		}
	}
	return false;
}

void tg_start(enum rc_centre_source src)
{
	rc_gesture_init(&gg, src);
	memset(&gl, 0, sizeof(gl));
}

void tg_in(enum rc_switch sw, bool pressed, rc_ms_t t)
{
	rc_gesture_input(&gg, sw, pressed, t, &gl);
}

void tg_tick(rc_ms_t t)
{
	for (int i = 0; i < 1000; i++) {
		rc_ms_t n = rc_gesture_next_tick(&gg);

		if (n > t) {
			break;
		}
		rc_gesture_tick(&gg, n, &gl);
	}
	rc_gesture_tick(&gg, t, &gl);
}

int tg_count(enum rc_gev_type type)
{
	int c = 0;

	for (uint8_t i = 0; i < gl.n; i++) {
		if (gl.e[i].type == type) {
			c++;
		}
	}
	return c;
}

const struct rc_gev *tg_find(enum rc_gev_type type, int nth)
{
	for (uint8_t i = 0; i < gl.n; i++) {
		if (gl.e[i].type == type && nth-- == 0) {
			return &gl.e[i];
		}
	}
	return NULL;
}

const struct rc_gev *tg_get(enum rc_gev_type type, int nth)
{
	static const struct rc_gev none = { .type = 0xff, .dir = 0xff, .t = -1, .t_down = -1 };
	const struct rc_gev *e = tg_find(type, nth);

	zassert_not_null(e, "gesture event %d number %d is missing", (int)type, nth);
	return e ? e : &none;
}

void tg_centre(rc_ms_t t0, rc_ms_t dur)
{
	if (gg.src == RC_CENTRE_SW2) {
		tg_in(RC_SW_CENTRE, true, t0);
		tg_tick(t0 + dur - 1);
		tg_in(RC_SW_CENTRE, false, t0 + dur);
	} else {
		tg_in(RC_SW_UP, true, t0 - 5);
		tg_in(RC_SW_DOWN, true, t0);   /* CENTRE_DOWN stamped at the second edge */
		tg_tick(t0 + dur - 1);
		tg_in(RC_SW_UP, false, t0 + dur - 1);
		tg_in(RC_SW_DOWN, false, t0 + dur); /* CENTRE_UP at the last opening */
	}
}
