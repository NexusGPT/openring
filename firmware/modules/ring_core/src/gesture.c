/*
 * Ring core: key layer (FW 2.2) and centre gesture recogniser (FW 2.1).
 *
 * Deadline rule: a deadline at time D runs when now >= D. An input at time t
 * first runs every deadline at or before t, then applies the edge, then runs
 * the deadlines again (a re-closed switch can make a past mark due).
 * The double-press window includes its 400th ms, so the short press fires at
 * release + 401 ms, the first ms after the window.
 */
#include <string.h>
#include "ring_core/rc_gesture.h"

#define BIT(sw) ((uint8_t)(1u << (sw)))
#define DIR_MASK (BIT(RC_SW_UP) | BIT(RC_SW_DOWN) | BIT(RC_SW_LEFT) | BIT(RC_SW_RIGHT))

static void emit(struct rc_gev_list *out, uint8_t type, uint8_t dir, bool repeat, rc_ms_t t, rc_ms_t t_down)
{
	if (out->n < RC_MAX_GEV) {
		struct rc_gev *e = &out->e[out->n++];

		e->type = type;
		e->dir = dir;
		e->repeat = repeat;
		e->t = t;
		e->t_down = t_down;
	}
}

static enum rc_switch opposite(enum rc_switch sw)
{
	switch (sw) {
	case RC_SW_UP:
		return RC_SW_DOWN;
	case RC_SW_DOWN:
		return RC_SW_UP;
	case RC_SW_LEFT:
		return RC_SW_RIGHT;
	case RC_SW_RIGHT:
		return RC_SW_LEFT;
	default:
		return RC_SW_CENTRE;
	}
}

void rc_gesture_init(struct rc_gesture *g, enum rc_centre_source src)
{
	memset(g, 0, sizeof(*g));
	g->src = (uint8_t)src;
	g->kstate = RC_K_IDLE;
}

/* ---- gesture layer, FW 2.1 ---- */

static void centre_down(struct rc_gesture *g, rc_ms_t t, struct rc_gev_list *out)
{
	emit(out, RC_GEV_CENTRE_DOWN, 0, false, t, t);
	g->pressing = true;
	g->down_t = t;
	g->warned = false;
	g->long_fired = false;
	g->cancelled = false;
	g->second = false;
	if (g->short_pending) {
		/* line 246: a press inside the window cancels the earlier short press */
		g->second = (t - g->short_up_t) >= RC_DOUBLE_GAP_MIN_MS;
		g->short_pending = false;
	}
}

static void centre_up(struct rc_gesture *g, rc_ms_t t, struct rc_gev_list *out)
{
	rc_ms_t dur = t - g->down_t;

	emit(out, RC_GEV_CENTRE_UP, 0, false, t, g->down_t);
	g->pressing = false;
	if (g->cancelled) {
		g->cancelled = false;
		return;                 /* R7: a cancelled hold gives nothing */
	}
	if (g->long_fired) {
		return;                 /* the release after a long press does nothing */
	}
	if (dur < RC_SHORT_MIN_MS || dur > RC_SHORT_MAX_MS) {
		return;                 /* graze, or held 451 to 999 ms: ignored */
	}
	if (g->second) {
		emit(out, RC_GEV_DOUBLE, 0, false, t, g->down_t);
		return;
	}
	g->short_pending = true;
	g->short_down_t = g->down_t;
	g->short_up_t = t;
}

/* A mark of the hold is reached when the key is down past it, or when a
 * pending release (hold-off) is stamped at or after it. */
static bool mark_live(const struct rc_gesture *g, rc_ms_t mark)
{
	return !g->rel_pending || g->rel_t >= mark;
}

enum dl_kind { DL_NONE, DL_DIR_WINDOW, DL_REPEAT, DL_RELEASE, DL_WARN, DL_LONG, DL_SHORT };

static rc_ms_t next_deadline(const struct rc_gesture *g, enum dl_kind *kind)
{
	rc_ms_t best = RC_NO_TICK;
	enum dl_kind k = DL_NONE;

#define CONSIDER(cond, when, kk) \
	do { if ((cond) && (when) < best) { best = (when); k = (kk); } } while (0)

	CONSIDER(g->kstate == RC_K_DIR_WINDOW, g->dir_t0 + RC_DIR_WINDOW_MS, DL_DIR_WINDOW);
	CONSIDER(g->kstate == RC_K_DIR_SENT, g->next_repeat, DL_REPEAT);
	CONSIDER(g->pressing && !g->cancelled && !g->warned && !g->long_fired && mark_live(g, g->down_t + RC_WARN_MS),
		 g->down_t + RC_WARN_MS, DL_WARN);
	CONSIDER(g->pressing && !g->cancelled && !g->long_fired && mark_live(g, g->down_t + RC_LONG_MS),
		 g->down_t + RC_LONG_MS, DL_LONG);
	CONSIDER(g->kstate == RC_K_CENTRE && g->rel_pending, g->rel_t + RC_RELEASE_HOLDOFF_MS, DL_RELEASE);
	CONSIDER(g->short_pending, g->short_up_t + RC_DOUBLE_WINDOW_MS + 1, DL_SHORT);
#undef CONSIDER
	*kind = k;
	return best;
}

rc_ms_t rc_gesture_next_tick(const struct rc_gesture *g)
{
	enum dl_kind k;

	return next_deadline(g, &k);
}

static void run_deadlines(struct rc_gesture *g, rc_ms_t now, struct rc_gev_list *out)
{
	for (int guard = 0; guard < 64; guard++) {
		enum dl_kind k;
		rc_ms_t d = next_deadline(g, &k);

		if (k == DL_NONE || d > now) {
			return;
		}
		switch (k) {
		case DL_DIR_WINDOW:
			/* window ended with no centre press: send the direction (line 254) */
			emit(out, RC_GEV_DIR, g->dir, false, d, d);
			g->kstate = RC_K_DIR_SENT;
			g->next_repeat = g->dir_t0 + RC_REPEAT_DELAY_MS;
			break;
		case DL_REPEAT:
			emit(out, RC_GEV_DIR, g->dir, true, d, d);
			g->next_repeat += RC_REPEAT_PERIOD_MS;
			break;
		case DL_WARN:
			g->warned = true;
			emit(out, RC_GEV_WARN, 0, false, d, g->down_t);
			break;
		case DL_LONG:
			g->long_fired = true;
			g->warned = true;
			emit(out, RC_GEV_LONG, 0, false, d, g->down_t);
			break;
		case DL_RELEASE:
			g->rel_pending = false;
			g->kstate = RC_K_IDLE;
			centre_up(g, g->rel_t, out);
			break;
		case DL_SHORT:
			g->short_pending = false;
			emit(out, RC_GEV_SHORT, 0, false, d, g->short_down_t);
			break;
		default:
			return;
		}
	}
}

/* ---- key layer, FW 2.2 ---- */

static uint8_t relevant(const struct rc_gesture *g)
{
	/* case PAIR: BTN_REC is unused (FW 2.1 table "Centre source") */
	return (g->src == RC_CENTRE_SW2) ? (DIR_MASK | BIT(RC_SW_CENTRE)) : DIR_MASK;
}

static void apply_edge(struct rc_gesture *g, enum rc_switch sw, bool pressed, rc_ms_t t, struct rc_gev_list *out)
{
	if (!(relevant(g) & BIT(sw))) {
		return;
	}
	if (pressed) {
		g->held |= BIT(sw);
	} else {
		g->held &= (uint8_t)~BIT(sw);
	}

	switch (g->kstate) {
	case RC_K_IDLE:
		if (!pressed) {
			break;
		}
		if (sw == RC_SW_CENTRE) {
			g->kstate = RC_K_CENTRE;
			g->rel_pending = false;
			centre_down(g, t, out);
		} else {
			g->kstate = RC_K_DIR_WINDOW;
			g->dir = (uint8_t)sw;
			g->dir_t0 = t;
		}
		break;
	case RC_K_DIR_WINDOW:
		if (pressed) {
			bool centre = (g->src == RC_CENTRE_SW2) ? (sw == RC_SW_CENTRE)
				: (sw == opposite((enum rc_switch)g->dir));
			if (centre) {
				/* the direction is dropped; the centre wins */
				g->kstate = RC_K_CENTRE;
				g->rel_pending = false;
				centre_down(g, t, out);
			}
			/* any other switch is ignored while the first is held */
		} else if (sw == g->dir) {
			/* released first, no centre press: send the direction now */
			emit(out, RC_GEV_DIR, g->dir, false, t, t);
			g->kstate = g->held ? RC_K_IGNORE : RC_K_IDLE;
		}
		break;
	case RC_K_DIR_SENT:
		if (!pressed && sw == g->dir) {
			g->kstate = g->held ? RC_K_IGNORE : RC_K_IDLE;
		}
		break;
	case RC_K_IGNORE:
		if (g->held == 0) {
			g->kstate = RC_K_IDLE;
		}
		break;
	case RC_K_CENTRE:
		if (pressed) {
			g->rel_pending = false;       /* roll or bounce: the key stays down */
		} else if (g->held == 0) {
			g->rel_pending = true;        /* all open: start the 30 ms hold-off */
			g->rel_t = t;
		}
		break;
	default:
		break;
	}
}

void rc_gesture_input(struct rc_gesture *g, enum rc_switch sw, bool pressed, rc_ms_t t, struct rc_gev_list *out)
{
	run_deadlines(g, t, out);
	apply_edge(g, sw, pressed, t, out);
	run_deadlines(g, t, out);
}

void rc_gesture_cancel_hold(struct rc_gesture *g)
{
	if (g->pressing) {
		g->cancelled = true;
		g->second = false;
	}
}

void rc_gesture_tick(struct rc_gesture *g, rc_ms_t now, struct rc_gev_list *out)
{
	run_deadlines(g, now, out);
}
