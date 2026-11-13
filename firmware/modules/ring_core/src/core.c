/*
 * Ring core: dispatcher. Gestures and system events in, actions out.
 */
#include <string.h>
#include "ring_core/rc_core.h"

static rc_ms_t state_timer_start(uint8_t st, rc_ms_t t);

void rc_core_init(struct rc_core *c, enum rc_centre_source src, enum rc_state start, rc_ms_t now)
{
	memset(c, 0, sizeof(*c));
	rc_sm_init(&c->sm, start);
	rc_gesture_init(&c->g, src);
	c->facts.vibration_on = true;
	c->facts.batt = RC_BATT_OK;
	c->entered_ms = now;
	c->timer_next = state_timer_start((uint8_t)start, now);
	c->mic_rail = (start == RC_ST_RECORDING);
	c->facts.storage_fault = (start == RC_ST_ERR_STORAGE_FAULT);  /* ruling R11 */
}

enum rc_state rc_core_state(const struct rc_core *c)
{
	return (enum rc_state)c->sm.state;
}

struct rc_facts *rc_core_facts(struct rc_core *c)
{
	return &c->facts;
}

void rc_core_set_sign_hook(struct rc_core *c, rc_sign_hook_fn fn, void *ctx)
{
	c->sign_fn = fn;
	c->sign_ctx = ctx;
}

bool rc_core_mic_rail(const struct rc_core *c)
{
	return c->mic_rail;
}

static rc_ms_t state_timer_start(uint8_t st, rc_ms_t t)
{
	if (st == RC_ST_ERR_MIC_FAULT) {
		return t + RC_MIC_FAULT_MS;
	}
	if (st == RC_ST_ERR_STORAGE_FAULT) {
		return t + RC_STORAGE_RETRY_MS;
	}
	return RC_NO_TICK;
}

static bool has_from(const struct rc_actions *out, uint8_t first, enum rc_action a)
{
	for (uint8_t i = first; i < out->n; i++) {
		if (out->a[i] == a) {
			return true;
		}
	}
	return false;
}

/* One row of the table, and what a change of state brings. */
static void step(struct rc_core *c, enum rc_event ev, rc_ms_t t, struct rc_actions *out)
{
	uint8_t from = c->sm.state;
	uint8_t first = out->n;

	rc_sm_handle(&c->sm, ev, &c->facts, out);
	for (uint8_t i = first; i < out->n; i++) {
		if (out->a[i] == RC_ACT_OPEN) {
			c->mic_rail = true;
		} else if (out->a[i] == RC_ACT_CLOSE || out->a[i] == RC_ACT_MIC_OFF) {
			c->mic_rail = false;
		}
		/* the superblock open flag follows the core's own actions (R4b); only a successful
		 * close and "scan done" clear it (R9) */
		if (out->a[i] == RC_ACT_OPEN) {
			c->facts.open_flag = true;
		} else if (out->a[i] == RC_ACT_CLOSE || out->a[i] == RC_ACT_CLEAR_OPEN_FLAG) {
			c->facts.open_flag = false;
		}
	}
	if (c->sm.state != from) {
		c->entered_ms = t;
		c->timer_next = state_timer_start(c->sm.state, t);
		if (c->sm.state == RC_ST_BOOT) {
			c->mic_rail = false;  /* a reboot or power loss: the chip restarts with every rail off */
		}
		rc_gesture_cancel_hold(&c->g);  /* ruling R7: any change of state cancels a centre hold */
		if (c->sm.state == RC_ST_ERR_STORAGE_FAULT) {
			c->facts.storage_fault = true;  /* ruling R11 */
		}
	}
}

static void sm_event(struct rc_core *c, enum rc_event ev, rc_ms_t t, struct rc_actions *out)
{
	uint8_t from = c->sm.state;
	uint8_t first = out->n;

	/* facts carried by the event itself (the battery level is set by rc_core_battery) */
	switch (ev) {
	case RC_EV_VBUS_IN:
		c->facts.vbus = true;
		c->sm.b15_warned = false;   /* a new discharge starts after a charge (reading U4, ruled by C3) */
		break;
	case RC_EV_VBUS_OUT:
		c->facts.vbus = false;
		break;
	case RC_EV_STORAGE_SFULL:
		c->facts.storage_full = true;
		break;
	case RC_EV_INIT_DONE:
	case RC_EV_STORAGE_RETRY_OK:
		c->facts.storage_fault = false;  /* ruling R11: a successful storage init */
		break;
	default:
		break;
	}
	/* ruling R16: when VBUS goes at B2, the state's "battery reaches B2" row comes before its own
	 * "VBUS removed" row (a state with no B2 row keeps its own row; R15 then checks the entry) */
	if (ev == RC_EV_VBUS_OUT && c->facts.batt == RC_BATT_B2 &&
	    rc_sm_find(&c->sm, RC_EV_BATT_B2, &c->facts) != NULL) {
		ev = RC_EV_BATT_B2;
	}
	/* rulings R4, R5 and correction R4b: at "init done", B2 first (no recovery), then an
	 * unfinished recording (RECOVERY, row 4), then B5 */
	if (ev == RC_EV_INIT_DONE && from == RC_ST_BOOT && !c->facts.vbus) {
		if (c->facts.batt == RC_BATT_B2) {
			ev = RC_EV_BATT_B2;
		} else if (!c->facts.open_flag && c->facts.batt >= RC_BATT_B5) {
			ev = RC_EV_BATT_B5;
		}
	}
	/* rule R-SIGN (FW 3.2, row 16): a long press in STANDBY whose other row 12 guards hold asks the sign hook once,
	 * before the row is chosen; a refusal makes row 12 not match and row 16 match. The fact lives for this press only. */
	if (ev == RC_EV_LONG_PRESS && from == RC_ST_STANDBY && c->sign_fn != NULL && !c->facts.open_flag &&
	    c->facts.batt < RC_BATT_B5 && !c->facts.storage_full) {
		c->facts.sign_not_drawn = (c->sign_fn(c->sign_ctx, t) != 0);
	}
	step(c, ev, t, out);
	c->facts.sign_not_drawn = false;
	/* ruling R15: with no VBUS, B2 always ends in OFF. On entry into STANDBY or an error state
	 * (also from BOOT after "init done" or a failed storage init) the core checks it first and
	 * takes that state's "battery reaches B2" row. RECOVERY is the R4b exception. */
	if (c->sm.state != from && c->facts.batt == RC_BATT_B2 && !c->facts.vbus &&
	    (c->sm.state == RC_ST_STANDBY || c->sm.state == RC_ST_ERR_STORAGE_FAULT ||
	     c->sm.state == RC_ST_ERR_STORAGE_FULL || c->sm.state == RC_ST_ERR_BATTERY_LOW ||
	     c->sm.state == RC_ST_ERR_MIC_FAULT || c->sm.state == RC_ST_ERR_CHARGER)) {
		step(c, RC_EV_BATT_B2, t, out);
	}
	/* rule R-STB (rulings R1, R11, R15): every entry into STANDBY from another state checks the facts:
	 * B2 (above), then the storage fault, then B5, then SFULL */
	if (c->sm.state == RC_ST_STANDBY && from != RC_ST_STANDBY) {
		if (c->facts.storage_fault) {
			step(c, RC_EV_STORAGE_FAULT_SET, t, out);
		} else if (c->facts.batt >= RC_BATT_B5) {
			step(c, RC_EV_BATT_B5, t, out);
		} else if (c->facts.storage_full) {
			step(c, RC_EV_STORAGE_SFULL, t, out);
		}
	}
	/* ruling R8: charge on at every appearance of VBUS, in every state */
	if (ev == RC_EV_VBUS_IN && !has_from(out, first, RC_ACT_CHARGE_ON)) {
		rc_actions_push(out, RC_ACT_CHARGE_ON);
	}
}

void rc_core_event(struct rc_core *c, enum rc_event ev, rc_ms_t t, struct rc_actions *out)
{
	/* Owner's rule (FW 1.2): only a long press of the centre starts or stops a
	 * recording. The press events come only from the switch input path
	 * (rc_core_input), the timers only from rc_core_tick, the battery
	 * thresholds only from rc_core_battery; a caller cannot inject them here. */
	if (ev == RC_EV_LONG_PRESS || ev == RC_EV_SHORT_PRESS || ev == RC_EV_DOUBLE_PRESS ||
	    ev == RC_EV_TIMER_5S || ev == RC_EV_TIMER_60S || ev == RC_EV_BATT_B15 ||
	    ev == RC_EV_BATT_B5 || ev == RC_EV_BATT_B2 || ev == RC_EV_STORAGE_FAULT_SET ||
	    (unsigned)ev >= RC_EV_COUNT) {
		return;
	}
	sm_event(c, ev, t, out);
}

void rc_core_battery(struct rc_core *c, enum rc_batt level, rc_ms_t t, struct rc_actions *out)
{
	static const uint8_t ev_of[] = { 0, RC_EV_BATT_B15, RC_EV_BATT_B5, RC_EV_BATT_B2 };
	uint8_t old = c->facts.batt;

	if ((unsigned)level > RC_BATT_B2) {
		return;
	}
	c->facts.batt = (uint8_t)level;
	if (c->sm.state == RC_ST_BOOT) {
		return;  /* ruling R12: kept; the order at "init done" decides */
	}
	if (level > old) {
		/* a downward crossing: the row of the threshold reached */
		sm_event(c, (enum rc_event)ev_of[level], t, out);
	}
	/* an upward crossing (after a charge) only updates the fact */
}

static void screen_input(struct rc_core *c, enum rc_action screen_act, struct rc_actions *out)
{
	/* FW 2.2 lock: with the screen off the first event only turns the screen on */
	if (!c->facts.screen_on) {
		rc_actions_push(out, RC_ACT_SCREEN_ON);
		return;
	}
	rc_actions_push(out, screen_act);
	if (c->facts.vibration_on) {
		rc_actions_push(out, RC_ACT_MT);  /* FW 3.1: joystick move or select, screen on */
	}
}

static void dispatch_gestures(struct rc_core *c, const struct rc_gev_list *gl, struct rc_actions *out)
{
	for (uint8_t i = 0; i < gl->n; i++) {
		const struct rc_gev *e = &gl->e[i];
		uint8_t st = c->sm.state;

		switch (e->type) {
		case RC_GEV_DIR: {
			static const uint8_t map[RC_SW_COUNT] = {
				RC_ACT_SCREEN_UP, RC_ACT_NONE, RC_ACT_SCREEN_DOWN, RC_ACT_SCREEN_LEFT, RC_ACT_SCREEN_RIGHT,
			};
			screen_input(c, (enum rc_action)map[e->dir], out);
			break;
		}
		case RC_GEV_WARN:
			/* FW 2.1 line 223: MW in STANDBY and RECORDING; the Vibration setting never turns it off */
			if (st == RC_ST_STANDBY || st == RC_ST_RECORDING) {
				rc_actions_push(out, RC_ACT_MW);
			}
			break;
		case RC_GEV_LONG:
			sm_event(c, RC_EV_LONG_PRESS, e->t, out);
			break;
		case RC_GEV_SHORT:
			if (rc_sm_find(&c->sm, RC_EV_SHORT_PRESS, &c->facts) != NULL) {
				sm_event(c, RC_EV_SHORT_PRESS, e->t, out);
				if (st == RC_ST_RECORDING) {
					out->highlight_ms = e->t_down;  /* line 226: the time of CENTRE_DOWN */
				}
			} else {
				/* FW 2.1 table, "every other state" */
				screen_input(c, RC_ACT_SCREEN_CENTRE, out);
			}
			break;
		case RC_GEV_DOUBLE:
			sm_event(c, RC_EV_DOUBLE_PRESS, e->t, out);
			break;
		default:
			break;
		}
	}
}

void rc_core_input(struct rc_core *c, enum rc_switch sw, bool pressed, rc_ms_t t, struct rc_actions *out)
{
	struct rc_gev_list gl;

	gl.n = 0;
	rc_core_tick(c, t, out);
	rc_gesture_input(&c->g, sw, pressed, t, &gl);
	dispatch_gestures(c, &gl, out);
}

void rc_core_tick(struct rc_core *c, rc_ms_t now, struct rc_actions *out)
{
	struct rc_gev_list gl;

	gl.n = 0;
	rc_gesture_tick(&c->g, now, &gl);
	dispatch_gestures(c, &gl, out);
	if (c->timer_next != RC_NO_TICK && now >= c->timer_next) {
		rc_ms_t when = c->timer_next;

		if (c->sm.state == RC_ST_ERR_STORAGE_FAULT) {
			/* rulings R3, R14: at most one try per call, whatever the delay; the next 60 s after it */
			c->timer_next = now + RC_STORAGE_RETRY_MS;
			sm_event(c, RC_EV_TIMER_60S, now, out);
		} else if (c->sm.state == RC_ST_ERR_MIC_FAULT) {
			c->timer_next = RC_NO_TICK;
			sm_event(c, RC_EV_TIMER_5S, when, out);
		} else {
			c->timer_next = RC_NO_TICK;
		}
	}
}

rc_ms_t rc_core_next_tick(const struct rc_core *c)
{
	rc_ms_t a = rc_gesture_next_tick(&c->g);

	return a < c->timer_next ? a : c->timer_next;
}
