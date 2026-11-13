/*
 * Suite screens_table: the pure screen table (rscr_logic.c) with no display. Every expected value is a literal written
 * here (design/firmware.md 1.1, 2.2, 3.2, 3.3, 3.4), not read from the module. The lock and the gestures are the real
 * core (ring_core) feeding the table, as in the product.
 */

#include <string.h>
#include <zephyr/ztest.h>

#include <ring_core/rc_core.h>
#include <ring_screens/rscr_logic.h>

/* ---- the standard view: STANDBY, devices in slots 0 and 2 (slot 0 active), two notifications ---- */

static void std_view(struct rscr_view *v)
{
	memset(v, 0, sizeof(*v));
	v->core_state = RC_ST_STANDBY;
	v->paired_mask = 0x05;
	v->active_slot = 0;
	v->link_up = true;
	v->inbox_n = 2;
	v->inbox_uid[0] = 100;
	v->inbox_flags[0] = RINBOX_F_POSITIVE | RINBOX_F_NEGATIVE;
	v->inbox_uid[1] = 101;
	v->inbox_flags[1] = RINBOX_F_NEGATIVE;
	v->rec_n = 3;
}

static void put_sel(struct rscr *s, enum rscr_screen sc, uint8_t sel)
{
	switch (sc) {
	case SCR_MENU:
		s->menu_sel = sel;
		break;
	case SCR_SETTINGS:
		s->set_sel = sel;
		break;
	case SCR_MODES:
		s->mode_sel = sel;
		break;
	case SCR_DEVICES:
		s->dev_sel = sel;
		break;
	case SCR_DEVICE:
		s->dev_item = sel;
		s->dev_slot = 2;
		break;
	case SCR_RECORDINGS:
		s->rec_sel = sel;
		break;
	case SCR_NOTIFS:
		s->notif_sel = sel;
		break;
	case SCR_NOTIF:
		s->notif_sel = sel;
		s->notif_uid = sel == 0 ? 100 : 101;
		break;
	case SCR_CONFIRM:
		s->confirm_kind = sel == 0 ? CONFIRM_POWER_OFF : CONFIRM_REMOVE;
		s->confirm_slot = 2;
		break;
	case SCR_PAIR:
		/* a pairing window opened at 1000 ms for slot 1 */
		s->pair_slot = 1;
		s->pair_until = 61000;
		break;
	default:
		break;
	}
}

static uint8_t get_sel(const struct rscr *s, enum rscr_screen sc)
{
	switch (sc) {
	case SCR_MENU:
		return s->menu_sel;
	case SCR_SETTINGS:
		return s->set_sel;
	case SCR_MODES:
		return s->mode_sel;
	case SCR_DEVICES:
		return s->dev_sel;
	case SCR_DEVICE:
		return s->dev_item;
	case SCR_RECORDINGS:
		return s->rec_sel;
	case SCR_NOTIFS:
		return s->notif_sel;
	default:
		return 0;
	}
}

static enum rc_action act_of(enum rscr_dir d)
{
	static const enum rc_action a[] = { RC_ACT_SCREEN_UP, RC_ACT_SCREEN_DOWN, RC_ACT_SCREEN_LEFT,
					    RC_ACT_SCREEN_RIGHT, RC_ACT_SCREEN_CENTRE };
	return a[d];
}

/* feed one core action to the table */
static void feed(struct rscr *s, const struct rscr_view *v, enum rc_action a, enum rc_event ev, rc_ms_t now,
		 struct rscr_fxs *fx)
{
	struct rc_actions al;

	rc_actions_clear(&al);
	if (a != RC_ACT_NONE) {
		rc_actions_push(&al, a);
	}
	memset(fx, 0, sizeof(*fx));
	rscr_on_core(s, v, &al, ev, now, fx);
}

/* ---- the table of 2.2 and 3.4: screen, selection, direction -> screen, selection after, first effect ---- */

struct row {
	enum rscr_screen screen;
	uint8_t sel;
	enum rscr_dir dir;
	enum rscr_screen to;
	uint8_t sel_after;
	enum rscr_fx_kind fx;
	uint8_t fx_a;
	uint32_t fx_u;
};

#define U DIR_UP
#define D DIR_DOWN
#define L DIR_LEFT
#define R DIR_RIGHT
#define C DIR_CENTRE

static const struct row rows[] = {
	/* SCR_STATUS: Up opens the notification list (software step 4); Right and Centre open the menu; Down, Left none */
	{ SCR_STATUS, 0, U, SCR_NOTIFS, 0, FX_NONE },
	{ SCR_STATUS, 0, D, SCR_STATUS, 0, FX_NONE },
	{ SCR_STATUS, 0, L, SCR_STATUS, 0, FX_NONE },
	{ SCR_STATUS, 0, R, SCR_MENU, 0, FX_NONE },
	{ SCR_STATUS, 0, C, SCR_MENU, 0, FX_NONE },
	/* SCR_MENU: previous, next, close menu, open item, open item */
	{ SCR_MENU, 3, U, SCR_MENU, 2, FX_NONE },
	{ SCR_MENU, 0, U, SCR_MENU, 0, FX_NONE },
	{ SCR_MENU, 2, D, SCR_MENU, 3, FX_NONE },
	{ SCR_MENU, 5, D, SCR_MENU, 5, FX_NONE },
	{ SCR_MENU, 2, L, SCR_STATUS, 2, FX_NONE },
	{ SCR_MENU, MENU_RECORDINGS, R, SCR_RECORDINGS, 0, FX_NONE },
	{ SCR_MENU, MENU_CONTROL, R, SCR_MODES, 0, FX_NONE },
	{ SCR_MENU, MENU_DEVICES, R, SCR_DEVICES, 0, FX_NONE },
	{ SCR_MENU, MENU_PAIR, R, SCR_PAIR, 3, FX_PAIR_OPEN, 1 },   /* the lowest free slot of 0x05 is slot 1 */
	{ SCR_MENU, MENU_SETTINGS, R, SCR_SETTINGS, 4, FX_NONE },
	{ SCR_MENU, MENU_POWER_OFF, R, SCR_CONFIRM, 5, FX_NONE },
	{ SCR_MENU, MENU_RECORDINGS, C, SCR_RECORDINGS, 0, FX_NONE },
	{ SCR_MENU, MENU_PAIR, C, SCR_PAIR, 3, FX_PAIR_OPEN, 1 },
	{ SCR_MENU, MENU_POWER_OFF, C, SCR_CONFIRM, 5, FX_NONE },
	/* SCR_RECORDINGS (3 recordings): previous, next, back to the menu, open the info */
	{ SCR_RECORDINGS, 1, U, SCR_RECORDINGS, 0, FX_NONE },
	{ SCR_RECORDINGS, 1, D, SCR_RECORDINGS, 2, FX_NONE },
	{ SCR_RECORDINGS, 2, D, SCR_RECORDINGS, 2, FX_NONE },
	{ SCR_RECORDINGS, 1, L, SCR_MENU, 1, FX_NONE },
	{ SCR_RECORDINGS, 1, R, SCR_RECORDING_INFO, 1, FX_NONE },
	{ SCR_RECORDINGS, 1, C, SCR_RECORDING_INFO, 1, FX_NONE },
	/* SCR_RECORDING_INFO: Left back, the rest none */
	{ SCR_RECORDING_INFO, 0, U, SCR_RECORDING_INFO, 0, FX_NONE },
	{ SCR_RECORDING_INFO, 0, D, SCR_RECORDING_INFO, 0, FX_NONE },
	{ SCR_RECORDING_INFO, 0, L, SCR_RECORDINGS, 0, FX_NONE },
	{ SCR_RECORDING_INFO, 0, R, SCR_RECORDING_INFO, 0, FX_NONE },
	{ SCR_RECORDING_INFO, 0, C, SCR_RECORDING_INFO, 0, FX_NONE },
	/* SCR_SETTINGS: previous, next, back, change value, change value */
	{ SCR_SETTINGS, 2, U, SCR_SETTINGS, 1, FX_NONE },
	{ SCR_SETTINGS, 2, D, SCR_SETTINGS, 3, FX_NONE },
	{ SCR_SETTINGS, 2, L, SCR_MENU, 2, FX_NONE },
	{ SCR_SETTINGS, SET_BRIGHTNESS, R, SCR_SETTINGS, 0, FX_BRIGHTNESS, 0 },   /* 3 levels: 2 goes round to 0 */
	{ SCR_SETTINGS, SET_VIBRATION, C, SCR_SETTINGS, 1, FX_VIBRATION, 0 },     /* on goes off */
	{ SCR_SETTINGS, SET_TIME_FORMAT, R, SCR_SETTINGS, 2, FX_NONE },
	{ SCR_SETTINGS, SET_ABOUT, R, SCR_SETTINGS, 3, FX_NONE },
	/* SCR_MODES: previous, next, back, open a session in that mode */
	{ SCR_MODES, 2, U, SCR_MODES, 1, FX_NONE },
	{ SCR_MODES, 1, D, SCR_MODES, 2, FX_NONE },
	{ SCR_MODES, 3, D, SCR_MODES, 3, FX_NONE },
	{ SCR_MODES, 1, L, SCR_MENU, 1, FX_NONE },
	{ SCR_MODES, RCTL_MEDIA, R, SCR_CONTROL, 0, FX_SET_MODE, RCTL_MEDIA },
	{ SCR_MODES, RCTL_PRESENTER, R, SCR_CONTROL, 1, FX_SET_MODE, RCTL_PRESENTER },
	{ SCR_MODES, RCTL_POINTER, C, SCR_CONTROL, 2, FX_SET_MODE, RCTL_POINTER },
	{ SCR_MODES, RCTL_AGENT, C, SCR_CONTROL, 3, FX_SET_MODE, RCTL_AGENT },
	/* SCR_CONTROL: every direction and the centre go to the device; the ring does nothing else */
	{ SCR_CONTROL, 0, U, SCR_CONTROL, 0, FX_NONE },
	{ SCR_CONTROL, 0, D, SCR_CONTROL, 0, FX_NONE },
	{ SCR_CONTROL, 0, L, SCR_CONTROL, 0, FX_NONE },
	{ SCR_CONTROL, 0, R, SCR_CONTROL, 0, FX_NONE },
	{ SCR_CONTROL, 0, C, SCR_CONTROL, 0, FX_NONE },
	/* SCR_DEVICES (slots 0 and 2): previous, next, back, open the device */
	{ SCR_DEVICES, 1, U, SCR_DEVICES, 0, FX_NONE },
	{ SCR_DEVICES, 0, D, SCR_DEVICES, 1, FX_NONE },
	{ SCR_DEVICES, 1, D, SCR_DEVICES, 1, FX_NONE },
	{ SCR_DEVICES, 1, L, SCR_MENU, 1, FX_NONE },
	{ SCR_DEVICES, 1, R, SCR_DEVICE, 0, FX_NONE },
	{ SCR_DEVICES, 1, C, SCR_DEVICE, 0, FX_NONE },
	/* SCR_DEVICE (the device of slot 2): previous item, next item, back, do the item */
	{ SCR_DEVICE, DEV_REMOVE, U, SCR_DEVICE, DEV_USE, FX_NONE },
	{ SCR_DEVICE, DEV_USE, D, SCR_DEVICE, DEV_REMOVE, FX_NONE },
	{ SCR_DEVICE, DEV_USE, L, SCR_DEVICES, DEV_USE, FX_NONE },
	{ SCR_DEVICE, DEV_USE, R, SCR_DEVICES, DEV_USE, FX_DEV_USE, 2 },
	{ SCR_DEVICE, DEV_USE, C, SCR_DEVICES, DEV_USE, FX_DEV_USE, 2 },
	{ SCR_DEVICE, DEV_REMOVE, R, SCR_CONFIRM, DEV_REMOVE, FX_NONE },
	{ SCR_DEVICE, DEV_REMOVE, C, SCR_CONFIRM, DEV_REMOVE, FX_NONE },
	{ SCR_DEVICE, DEV_REMOVE, L, SCR_DEVICES, DEV_REMOVE, FX_NONE },
	/* SCR_CONFIRM: Left No (back), Centre Yes, the rest none (power off: sel 0, remove: sel 1) */
	{ SCR_CONFIRM, 0, U, SCR_CONFIRM, 0, FX_NONE },
	{ SCR_CONFIRM, 0, D, SCR_CONFIRM, 0, FX_NONE },
	{ SCR_CONFIRM, 0, R, SCR_CONFIRM, 0, FX_NONE },
	{ SCR_CONFIRM, 0, L, SCR_MENU, 0, FX_NONE },
	{ SCR_CONFIRM, 0, C, SCR_STATUS, 0, FX_POWER_OFF },
	{ SCR_CONFIRM, 1, L, SCR_DEVICE, 0, FX_NONE },
	{ SCR_CONFIRM, 1, C, SCR_DEVICES, 0, FX_DEV_REMOVE, 2 },
	/* SCR_PAIR: Left cancels the pairing, the rest none */
	{ SCR_PAIR, 0, U, SCR_PAIR, 0, FX_NONE },
	{ SCR_PAIR, 0, D, SCR_PAIR, 0, FX_NONE },
	{ SCR_PAIR, 0, R, SCR_PAIR, 0, FX_NONE },
	{ SCR_PAIR, 0, C, SCR_PAIR, 0, FX_NONE },
	{ SCR_PAIR, 0, L, SCR_MENU, 0, FX_PAIR_CANCEL },
	/* SCR_MESSAGE: every action dismisses (the screen before it was SCR_MENU) */
	{ SCR_MESSAGE, 0, U, SCR_MENU, 0, FX_NONE },
	{ SCR_MESSAGE, 0, D, SCR_MENU, 0, FX_NONE },
	{ SCR_MESSAGE, 0, L, SCR_MENU, 0, FX_NONE },
	{ SCR_MESSAGE, 0, R, SCR_MENU, 0, FX_NONE },
	{ SCR_MESSAGE, 0, C, SCR_MENU, 0, FX_NONE },
	/* SCR_CHARGING, SCR_TRANSFER, SCR_ERROR: the centre turns the screen off, the rest none */
	{ SCR_CHARGING, 0, U, SCR_CHARGING, 0, FX_NONE },
	{ SCR_CHARGING, 0, D, SCR_CHARGING, 0, FX_NONE },
	{ SCR_CHARGING, 0, L, SCR_CHARGING, 0, FX_NONE },
	{ SCR_CHARGING, 0, R, SCR_CHARGING, 0, FX_NONE },
	{ SCR_CHARGING, 0, C, SCR_OFF, 0, FX_NONE },
	{ SCR_TRANSFER, 0, U, SCR_TRANSFER, 0, FX_NONE },
	{ SCR_TRANSFER, 0, D, SCR_TRANSFER, 0, FX_NONE },
	{ SCR_TRANSFER, 0, L, SCR_TRANSFER, 0, FX_NONE },
	{ SCR_TRANSFER, 0, R, SCR_TRANSFER, 0, FX_NONE },
	{ SCR_TRANSFER, 0, C, SCR_OFF, 0, FX_NONE },
	{ SCR_ERROR, 0, U, SCR_ERROR, 0, FX_NONE },
	{ SCR_ERROR, 0, D, SCR_ERROR, 0, FX_NONE },
	{ SCR_ERROR, 0, L, SCR_ERROR, 0, FX_NONE },
	{ SCR_ERROR, 0, R, SCR_ERROR, 0, FX_NONE },
	{ SCR_ERROR, 0, C, SCR_OFF, 0, FX_NONE },
	/* SCR_NOTIFS (software step 4): previous, next, back, open the detail */
	{ SCR_NOTIFS, 1, U, SCR_NOTIFS, 0, FX_NONE },
	{ SCR_NOTIFS, 0, D, SCR_NOTIFS, 1, FX_NONE },
	{ SCR_NOTIFS, 1, D, SCR_NOTIFS, 1, FX_NONE },
	{ SCR_NOTIFS, 1, L, SCR_STATUS, 1, FX_NONE },
	{ SCR_NOTIFS, 1, R, SCR_NOTIF, 1, FX_NOTIF_READ, 0, 101 },
	{ SCR_NOTIFS, 0, C, SCR_NOTIF, 0, FX_NOTIF_READ, 0, 100 },
	/* SCR_NOTIF of 100 (both actions) : Left dismiss, Right the positive action, Centre back, Up and Down the
	 * neighbour */
	{ SCR_NOTIF, 0, L, SCR_NOTIF, 0, FX_NOTIF_DISMISS, 0, 100 },
	{ SCR_NOTIF, 0, R, SCR_NOTIF, 0, FX_NOTIF_POSITIVE, 0, 100 },
	{ SCR_NOTIF, 0, C, SCR_NOTIFS, 0, FX_NONE },
	{ SCR_NOTIF, 0, D, SCR_NOTIF, 1, FX_NOTIF_READ, 0, 101 },
	{ SCR_NOTIF, 0, U, SCR_NOTIF, 0, FX_NONE },
	/* SCR_NOTIF of 101 (dismiss only): the positive action sends nothing */
	{ SCR_NOTIF, 1, L, SCR_NOTIF, 1, FX_NOTIF_DISMISS, 0, 101 },
	{ SCR_NOTIF, 1, R, SCR_NOTIF, 1, FX_NONE },
	{ SCR_NOTIF, 1, U, SCR_NOTIF, 0, FX_NOTIF_READ, 0, 100 },
	{ SCR_NOTIF, 1, D, SCR_NOTIF, 1, FX_NONE },
	{ SCR_NOTIF, 1, C, SCR_NOTIFS, 1, FX_NONE },
};

ZTEST(screens_table, test_table_every_screen_every_action)
{
	int n = ARRAY_SIZE(rows);

	for (int i = 0; i < n; i++) {
		const struct row *r = &rows[i];
		struct rscr s;
		struct rscr_view v;
		struct rscr_fxs fx;

		rscr_init(&s);
		std_view(&v);
		s.screen = r->screen;
		put_sel(&s, r->screen, r->sel);
		if (r->screen == SCR_MESSAGE) {
			s.msg_back = SCR_MENU;
			s.msg_until = 3000;
		}
		feed(&s, &v, act_of(r->dir), RC_EV_COUNT, 1000, &fx);
		zassert_equal(s.screen, r->to, "row %d: %s sel %u dir %d: screen %s, expected %s", i,
			      rscr_screen_name(r->screen), r->sel, r->dir, rscr_screen_name(s.screen),
			      rscr_screen_name(r->to));
		if (r->to == r->screen && (r->screen == SCR_MENU || r->screen == SCR_SETTINGS || r->screen == SCR_MODES ||
					  r->screen == SCR_DEVICES || r->screen == SCR_DEVICE || r->screen == SCR_RECORDINGS ||
					  r->screen == SCR_NOTIFS)) {
			zassert_equal(get_sel(&s, r->screen), r->sel_after, "row %d: %s selection %u, expected %u", i,
				      rscr_screen_name(r->screen), get_sel(&s, r->screen), r->sel_after);
		}
		zassert_equal(fx.e[0].kind, r->fx, "row %d: %s dir %d: first effect %d, expected %d", i,
			      rscr_screen_name(r->screen), r->dir, fx.e[0].kind, r->fx);
		if (r->fx != FX_NONE) {
			zassert_equal(fx.e[0].a, r->fx_a, "row %d: effect argument %u, expected %u", i, fx.e[0].a,
				      r->fx_a);
			zassert_equal(fx.e[0].u, r->fx_u, "row %d: effect uid %u, expected %u", i, fx.e[0].u,
				      r->fx_u);
		}
	}
	TC_PRINT("SCREENS_TABLE rows checked: %d\n", n);
}

ZTEST(screens_table, test_menu_has_six_items_in_order)
{
	static const char *const want[] = { "Recordings", "Control", "Devices", "Pair device", "Settings", "Power off" };

	zassert_equal(MENU_COUNT, 6, "six items");
	for (int i = 0; i < 6; i++) {
		zassert_str_equal(rscr_menu_name((enum rscr_menu_item)i), want[i], "item %d", i);
	}
}

ZTEST(screens_table, test_pair_with_three_devices_says_remove_first)
{
	struct rscr s;
	struct rscr_view v;
	struct rscr_fxs fx;

	rscr_init(&s);
	std_view(&v);
	v.paired_mask = 0x07;
	s.screen = SCR_MENU;
	s.menu_sel = MENU_PAIR;
	feed(&s, &v, RC_ACT_SCREEN_RIGHT, RC_EV_COUNT, 1000, &fx);
	zassert_equal(s.screen, SCR_MESSAGE, "with three devices SCR_PAIR does not open");
	zassert_equal(s.msg, MSG_REMOVE_FIRST, "message");
	zassert_str_equal(rscr_msg_text(MSG_REMOVE_FIRST), "Remove a device first", "text");
	zassert_equal(fx.n, 0, "no pairing window is opened");
}

ZTEST(screens_table, test_geometry_turn)
{
	int px, py, x, y;

	rscr_to_panel(0, 0, &px, &py);
	zassert_equal(px, 119, "top left of the picture is the top right of the panel");
	zassert_equal(py, 0, "");
	rscr_to_panel(239, 119, &px, &py);
	zassert_equal(px, 0, "bottom right of the picture");
	zassert_equal(py, 239, "");
	for (int i = 0; i < 240 * 120; i += 7) {
		rscr_to_panel(i % 240, i / 240, &px, &py);
		zassert_true(px >= 0 && px < 120 && py >= 0 && py < 240, "inside the panel");
		rscr_from_panel(px, py, &x, &y);
		zassert_equal(x, i % 240, "round trip x");
		zassert_equal(y, i / 240, "round trip y");
	}
}

/* ---- the real core feeds the table: gestures, the lock, the session ---- */

struct rig {
	struct rc_core c;
	struct rscr s;
	struct rscr_view v;
	struct rscr_fxs fx;       /* all effects since the last clear */
	rc_ms_t t;
	int opens, closes, sent, mts;  /* RC_ACT_OPEN, RC_ACT_CLOSE, key-bearing screen actions seen */
	bool session_sent_ok;
};

static void rig_after(struct rig *g, const struct rc_actions *a)
{
	struct rscr_fxs f = { 0 };
	enum rc_event last = a->last_row > 0 ? rscr_row_event(a->last_row) : RC_EV_COUNT;

	g->v.core_state = rc_core_state(&g->c);
	for (uint8_t i = 0; i < a->n; i++) {
		g->mts += a->a[i] == RC_ACT_MT;
		g->opens += a->a[i] == RC_ACT_OPEN;
		g->closes += a->a[i] == RC_ACT_CLOSE;
		if (a->a[i] >= RC_ACT_SCREEN_CENTRE && a->a[i] <= RC_ACT_SCREEN_RIGHT) {
			g->sent++;
		}
	}
	rscr_on_core(&g->s, &g->v, a, last, g->t, &f);
	for (uint8_t i = 0; i < f.n && g->fx.n < RSCR_MAX_FX; i++) {
		g->fx.e[g->fx.n++] = f.e[i];
	}
	g->c.facts.screen_on = rscr_lock_fact(&g->s);
}

static void rig_tick(struct rig *g, rc_ms_t t)
{
	struct rc_actions a;
	struct rscr_fxs f = { 0 };

	g->t = t;
	rc_actions_clear(&a);
	rc_core_tick(&g->c, t, &a);
	rig_after(g, &a);
	g->v.core_state = rc_core_state(&g->c);
	rscr_tick(&g->s, &g->v, t, &f);
	for (uint8_t i = 0; i < f.n && g->fx.n < RSCR_MAX_FX; i++) {
		g->fx.e[g->fx.n++] = f.e[i];
	}
	g->c.facts.screen_on = rscr_lock_fact(&g->s);
}

static void rig_edge(struct rig *g, enum rc_switch sw, bool down, rc_ms_t t)
{
	struct rc_actions a;

	g->t = t;
	rc_actions_clear(&a);
	rc_core_input(&g->c, sw, down, t, &a);
	rig_after(g, &a);
}

static void rig_init(struct rig *g)
{
	memset(g, 0, sizeof(*g));
	rc_core_init(&g->c, RC_CENTRE_SW2, RC_ST_STANDBY, 0);
	rscr_init(&g->s);
	std_view(&g->v);
	g->t = 10000;
}

/* time passes in steps of 50 ms up to t (the timers run as in the product) */
static void rig_run_to(struct rig *g, rc_ms_t t)
{
	for (rc_ms_t x = g->t + 50; x <= t; x += 50) {
		rig_tick(g, x);
	}
	if (g->t < t) {
		rig_tick(g, t);
	}
}

static void rig_dir(struct rig *g, enum rc_switch sw)
{
	rc_ms_t t0 = g->t + 300;

	rig_run_to(g, t0);
	rig_edge(g, sw, true, t0);
	rig_run_to(g, t0 + 60);
	rig_edge(g, sw, false, t0 + 80);
	rig_run_to(g, t0 + 100);
}

static void rig_short(struct rig *g)
{
	rc_ms_t t0 = g->t + 300;

	rig_run_to(g, t0);
	rig_edge(g, RC_SW_CENTRE, true, t0);
	rig_run_to(g, t0 + 100);
	rig_edge(g, RC_SW_CENTRE, false, t0 + 100);
	rig_run_to(g, t0 + 100 + 450);
}

static void rig_double(struct rig *g)
{
	rc_ms_t t0 = g->t + 300;

	rig_run_to(g, t0);
	rig_edge(g, RC_SW_CENTRE, true, t0);
	rig_run_to(g, t0 + 100);
	rig_edge(g, RC_SW_CENTRE, false, t0 + 100);
	rig_run_to(g, t0 + 250);
	rig_edge(g, RC_SW_CENTRE, true, t0 + 250);
	rig_run_to(g, t0 + 350);
	rig_edge(g, RC_SW_CENTRE, false, t0 + 350);
	rig_run_to(g, t0 + 800);
}

static void rig_long(struct rig *g)
{
	rc_ms_t t0 = g->t + 300;

	rig_run_to(g, t0);
	rig_edge(g, RC_SW_CENTRE, true, t0);
	rig_run_to(g, t0 + 1050);
	rig_edge(g, RC_SW_CENTRE, false, t0 + 1100);
	rig_run_to(g, t0 + 1200);
}

ZTEST(screens_table, test_lock_first_event_only_wakes)
{
	struct rig g;

	rig_init(&g);
	zassert_equal(g.s.screen, SCR_OFF, "starts dark");
	zassert_false(rscr_lock_fact(&g.s), "locked");
	rig_dir(&g, RC_SW_RIGHT);
	zassert_equal(g.s.screen, SCR_STATUS, "the first Right only wakes: %s", rscr_screen_name(g.s.screen));
	zassert_equal(g.sent, 0, "no screen action reached the table while locked");
	rig_dir(&g, RC_SW_RIGHT);
	zassert_equal(g.s.screen, SCR_MENU, "the second Right opens the menu: %s", rscr_screen_name(g.s.screen));
	zassert_equal(g.sent, 1, "one screen action");
	/* 5 s after the last input the screen is off again and the lock is back */
	rig_run_to(&g, g.t + RSCR_OFF_MS + 100);
	zassert_equal(g.s.screen, SCR_OFF, "off after 5 s: %s", rscr_screen_name(g.s.screen));
	zassert_false(rscr_lock_fact(&g.s), "locked again");
	rig_dir(&g, RC_SW_DOWN);
	zassert_equal(g.s.screen, SCR_STATUS, "a Down after the lock only wakes (the menu is closed)");
	zassert_equal(g.s.menu_sel, 0, "the menu did not move");
}

ZTEST(screens_table, test_short_press_with_screen_off_shows_status_5s)
{
	struct rig g;

	rig_init(&g);
	rig_short(&g);
	zassert_equal(g.s.screen, SCR_STATUS, "status: %s", rscr_screen_name(g.s.screen));
	rig_run_to(&g, g.t + 4000);
	zassert_equal(g.s.screen, SCR_STATUS, "still on at 4 s");
	rig_run_to(&g, g.t + 1500);
	zassert_equal(g.s.screen, SCR_OFF, "off at 5 s after the input");
}

ZTEST(screens_table, test_session_open_and_double_press_closes)
{
	struct rig g;

	rig_init(&g);
	g.s.screen = SCR_MODES;
	g.c.facts.screen_on = true;
	g.s.mode_sel = RCTL_AGENT;
	rig_dir(&g, RC_SW_RIGHT);
	zassert_equal(g.s.screen, SCR_CONTROL, "session screen");
	zassert_true(g.s.session, "session open");
	zassert_equal(g.s.mode, RCTL_AGENT, "mode");
	zassert_equal(g.fx.e[0].kind, FX_SET_MODE, "mode set");
	zassert_equal(g.fx.e[1].kind, FX_CONTROL_ACTIVE, "control on");
	zassert_equal(g.fx.e[1].a, 1, "control on");
	g.fx.n = 0;
	/* a direction in the session goes to the device (the core emits it) and the ring stays on SCR_CONTROL */
	rig_dir(&g, RC_SW_LEFT);
	zassert_equal(g.s.screen, SCR_CONTROL, "stays");
	zassert_true(g.s.session, "still open");
	zassert_equal(g.fx.n, 0, "the table asks for no effect for a key");
	/* a double press of the centre closes it and shows SCR_MODES */
	rig_double(&g);
	zassert_false(g.s.session, "closed by the double press");
	zassert_equal(g.s.screen, SCR_MODES, "SCR_MODES: %s", rscr_screen_name(g.s.screen));
	zassert_equal(g.s.mode_sel, RCTL_AGENT, "the last used mode is highlighted");
	zassert_equal(g.fx.e[g.fx.n - 1].kind, FX_CONTROL_ACTIVE, "control off");
	zassert_equal(g.fx.e[g.fx.n - 1].a, 0, "control off");
}

ZTEST(screens_table, test_double_press_without_session_does_nothing_on_a_menu)
{
	struct rig g;

	rig_init(&g);
	g.s.screen = SCR_MENU;
	g.c.facts.screen_on = true;
	g.s.menu_sel = MENU_DEVICES;
	rig_double(&g);
	zassert_equal(g.s.screen, SCR_MENU, "a double press does nothing, on a menu too: %s", rscr_screen_name(g.s.screen));
	zassert_equal(g.s.menu_sel, MENU_DEVICES, "no item was opened");
}

ZTEST(screens_table, test_session_lock_does_not_apply_with_screen_off)
{
	struct rig g;

	rig_init(&g);
	g.s.session = true;
	g.s.mode = RCTL_MEDIA;
	g.s.screen = SCR_OFF;
	g.c.facts.screen_on = rscr_lock_fact(&g.s);
	zassert_true(g.c.facts.screen_on, "the lock fact is open in a session");
	rig_dir(&g, RC_SW_RIGHT);
	zassert_equal(g.sent, 1, "the action reached control at once with the screen off");
	zassert_equal(g.s.screen, SCR_CONTROL, "and the screen came on: %s", rscr_screen_name(g.s.screen));
}

ZTEST(screens_table, test_long_press_records_from_any_screen)
{
	static const enum rscr_screen from[] = { SCR_OFF, SCR_STATUS, SCR_MENU, SCR_SETTINGS, SCR_CONFIRM, SCR_PAIR,
						 SCR_DEVICES, SCR_NOTIFS, SCR_MODES };

	for (unsigned i = 0; i < ARRAY_SIZE(from); i++) {
		struct rig g;

		rig_init(&g);
		g.s.screen = from[i];
		if (from[i] == SCR_PAIR) {
			g.s.pair_until = g.t + RSCR_PAIR_MS;
			g.s.pair_slot = 1;
		}
		g.c.facts.screen_on = rscr_lock_fact(&g.s);
		rig_long(&g);
		zassert_equal(g.opens, 1, "from %s a long press opens a recording", rscr_screen_name(from[i]));
		zassert_equal(rc_core_state(&g.c), RC_ST_RECORDING, "recording");
		zassert_true(g.s.screen == SCR_RECORDING || g.s.screen == SCR_REC_DIM, "recording sign from %s: %s",
			     rscr_screen_name(from[i]), rscr_screen_name(g.s.screen));
		if (from[i] == SCR_PAIR) {
			bool cancelled = false;

			for (uint8_t k = 0; k < g.fx.n; k++) {
				cancelled |= g.fx.e[k].kind == FX_PAIR_CANCEL;
			}
			zassert_true(cancelled, "an open pairing window is closed");
		}
	}
}

ZTEST(screens_table, test_long_press_does_not_close_a_session)
{
	struct rig g;

	rig_init(&g);
	g.s.session = true;
	g.s.mode = RCTL_POINTER;
	g.s.screen = SCR_CONTROL;
	g.c.facts.screen_on = true;
	rig_long(&g);
	zassert_equal(g.opens, 1, "recording starts");
	zassert_true(g.s.session, "the session stays open (the one exception to collision C2)");
	zassert_true(g.s.screen == SCR_RECORDING || g.s.screen == SCR_REC_DIM, "recording sign: %s",
		     rscr_screen_name(g.s.screen));
	for (uint8_t k = 0; k < g.fx.n; k++) {
		zassert_false(g.fx.e[k].kind == FX_CONTROL_ACTIVE && g.fx.e[k].a == 0, "control stays active");
	}
	/* a double press in RECORDING closes it and shows SCR_RECORDING */
	rig_double(&g);
	zassert_false(g.s.session, "closed");
	zassert_equal(g.s.screen, SCR_RECORDING, "SCR_RECORDING: %s", rscr_screen_name(g.s.screen));
}

ZTEST(screens_table, test_session_closes_after_30_minutes_and_on_state_change_and_device_removal)
{
	struct rig g;
	struct rscr_fxs fx = { 0 };

	rig_init(&g);
	g.s.session = true;
	g.s.mode = RCTL_MEDIA;
	g.s.screen = SCR_CONTROL;
	g.s.session_at = g.t + RSCR_SESSION_MS;
	g.c.facts.screen_on = true;
	rscr_tick(&g.s, &g.v, g.t + RSCR_SESSION_MS - 1, &fx);
	zassert_true(g.s.session, "open at 30 min less 1 ms");
	rscr_tick(&g.s, &g.v, g.t + RSCR_SESSION_MS, &fx);
	zassert_false(g.s.session, "closed at 30 min");

	/* the ring enters CHARGING */
	rig_init(&g);
	g.s.session = true;
	g.s.screen = SCR_CONTROL;
	g.c.facts.screen_on = true;
	{
		struct rc_actions a;

		rc_actions_clear(&a);
		rc_core_event(&g.c, RC_EV_VBUS_IN, g.t, &a);
		rig_after(&g, &a);
	}
	zassert_equal(rc_core_state(&g.c), RC_ST_CHARGING, "charging");
	zassert_false(g.s.session, "the session closes when the ring enters a state other than STANDBY and RECORDING");
	zassert_equal(g.s.screen, SCR_CHARGING, "charging screen");

	/* the active device is removed */
	rig_init(&g);
	g.s.session = true;
	g.s.screen = SCR_CONTROL;
	memset(&fx, 0, sizeof(fx));
	g.v.paired_mask = 0x04;
	rscr_dev_removed(&g.s, &g.v, 0, true, g.t, &fx);
	zassert_false(g.s.session, "closed when the active device is removed");
	zassert_equal(fx.e[0].kind, FX_CONTROL_ACTIVE, "control off");
	zassert_equal(fx.e[0].a, 0, "control off");
}

ZTEST(screens_table, test_pairing_shows_the_device_list_and_asks_the_devices_for_nothing)
{
	/* design/firmware.md 3.4, 7.4: the new device becomes active only when none was; that is ring_devices' rule (its tests and the
	 * two-device test B). The screens part only shows the list and does not touch the devices. */
	struct rscr s;
	struct rscr_view v;

	rscr_init(&s);
	std_view(&v);
	v.paired_mask = 0x03;
	s.screen = SCR_PAIR;
	s.pair_slot = 1;
	s.pair_until = 60000;
	rscr_dev_paired(&s, &v, 1, 1000);
	zassert_equal(s.screen, SCR_DEVICES, "the device list is shown");
	zassert_equal(s.pair_until, RC_NO_TICK, "the window is over");
	zassert_equal(s.pair_slot, RDEV_NONE, "no slot is being paired");
}

ZTEST(screens_table, test_pairing_window_60s_and_passkey)
{
	struct rscr s;
	struct rscr_view v;
	struct rscr_fxs fx = { 0 };

	rscr_init(&s);
	std_view(&v);
	v.paired_mask = 0x01;
	s.screen = SCR_MENU;
	s.menu_sel = MENU_PAIR;
	feed(&s, &v, RC_ACT_SCREEN_RIGHT, RC_EV_COUNT, 5000, &fx);
	zassert_equal(s.screen, SCR_PAIR, "");
	zassert_equal(s.pair_until, 65000, "60 s");
	zassert_equal(s.off_at, RC_NO_TICK, "the screen stays on while pairing");
	rscr_dev_passkey(&s, 1, 482913);
	zassert_true(s.pair_has_key, "");
	zassert_equal(s.passkey, 482913, "");
	rscr_dev_passkey(&s, 1, 1234567);
	zassert_equal(s.passkey, 234567, "six digits only");
	memset(&fx, 0, sizeof(fx));
	rscr_tick(&s, &v, 64999, &fx);
	zassert_equal(s.screen, SCR_PAIR, "open at 59.999 s");
	rscr_tick(&s, &v, 65000, &fx);
	zassert_equal(s.screen, SCR_MENU, "closed at 60 s");
	zassert_equal(fx.e[0].kind, FX_PAIR_CANCEL, "window closed");
}

/* ---- R-SIGN at this layer ---- */

static void sign_check(struct rig *g, const char *what)
{
	zassert_true(rscr_sign_ok(&g->s, rc_core_state(&g->c)), "R-SIGN %s: in RECORDING the screen is %s", what,
		     rscr_screen_name(g->s.screen));
	if (rc_core_state(&g->c) == RC_ST_RECORDING) {
		zassert_true(g->s.screen != SCR_OFF, "R-SIGN %s: dark", what);
	}
}

ZTEST(screens_table, test_rsign_recording_never_dark)
{
	struct rig g;
	int checks = 0;

	rig_init(&g);
	rig_long(&g);
	zassert_equal(rc_core_state(&g.c), RC_ST_RECORDING, "recording");
	rc_ms_t idle_end = g.t + 120000;

	for (rc_ms_t x = g.t + 50; x < idle_end; x += 50) {
		rig_tick(&g, x);
		sign_check(&g, "idle");
		checks++;
	}
	zassert_equal(g.s.screen, SCR_REC_DIM, "dimmed after the idle time");
	/* every kind of input, then idle again */
	enum rc_switch sws[] = { RC_SW_UP, RC_SW_DOWN, RC_SW_LEFT, RC_SW_RIGHT };

	for (unsigned i = 0; i < ARRAY_SIZE(sws); i++) {
		/* the lock: from the dimmed screen the first direction only brings the full recording picture */
		rig_dir(&g, sws[i]);
		sign_check(&g, "direction");
		zassert_equal(g.s.screen, SCR_RECORDING, "full picture after input");
		rig_run_to(&g, g.t + RSCR_DIM_MS - 100);
		sign_check(&g, "before dim");
		zassert_equal(g.s.screen, SCR_RECORDING, "3 s after the last input it is still full");
		rig_run_to(&g, g.t + 300);
		zassert_equal(g.s.screen, SCR_REC_DIM, "dim after 3 s");
		checks += 3;
	}
	rig_short(&g);   /* highlight */
	sign_check(&g, "short press");
	zassert_equal(g.s.highlights, 1, "highlight counted");
	rig_double(&g);
	sign_check(&g, "double press");
	/* a message during a recording keeps the sign */
	{
		struct rc_actions a;

		rc_actions_clear(&a);
		rc_actions_push(&a, RC_ACT_SCR_MSG_30MIN_3S);
		rig_after(&g, &a);
		sign_check(&g, "message");
		zassert_equal(g.s.screen, SCR_MESSAGE, "message shown");
		zassert_true(rscr_has_sign(&g.s, RC_ST_RECORDING), "with the sign");
		rig_run_to(&g, g.t + RSCR_MSG_MS + 100);
		sign_check(&g, "after message");
	}
	/* VBUS in a recording: the recording closes and the screen may change (the rule ends with the recording) */
	{
		struct rc_actions a;

		rc_actions_clear(&a);
		rc_core_event(&g.c, RC_EV_VBUS_IN, g.t, &a);
		rig_after(&g, &a);
		zassert_equal(rc_core_state(&g.c), RC_ST_CHARGING, "charging");
		zassert_equal(g.s.screen, SCR_CHARGING, "charging screen");
	}
	TC_PRINT("SCREENS_TABLE rsign checks: %d\n", checks);
}

ZTEST(screens_table, test_rsign_stop_returns_to_status_then_off)
{
	struct rig g;

	rig_init(&g);
	rig_long(&g);
	rig_run_to(&g, g.t + 5000);
	rig_long(&g);
	zassert_equal(rc_core_state(&g.c), RC_ST_STANDBY, "stopped");
	zassert_equal(g.s.screen, SCR_STATUS, "status after the stop: %s", rscr_screen_name(g.s.screen));
	rig_run_to(&g, g.t + 5200);
	zassert_equal(g.s.screen, SCR_OFF, "off after 5 s");
}

ZTEST(screens_table, test_dim_pairs_with_lowest_lock_state)
{
	struct rig g;

	rig_init(&g);
	rig_long(&g);
	rig_run_to(&g, g.t + 4000);
	zassert_equal(g.s.screen, SCR_REC_DIM, "dim");
	zassert_false(rscr_lock_fact(&g.s), "locked while dimmed: a direction only turns the full screen on");
	rig_dir(&g, RC_SW_RIGHT);
	zassert_equal(g.s.screen, SCR_RECORDING, "full");
	zassert_equal(g.sent, 0, "that direction was not acted on");
	zassert_true(rscr_lock_fact(&g.s), "open for the next one");
}

ZTEST(screens_table, test_messages_last_3s)
{
	struct rscr s;
	struct rscr_view v;
	struct rscr_fxs fx = { 0 };
	struct rc_actions a;

	rscr_init(&s);
	std_view(&v);
	s.screen = SCR_STATUS;
	rc_actions_clear(&a);
	rc_actions_push(&a, RC_ACT_SCR_MSG_BATTERY_LOW_3S);
	rscr_on_core(&s, &v, &a, RC_EV_COUNT, 1000, &fx);
	zassert_equal(s.screen, SCR_MESSAGE, "");
	zassert_equal(s.msg, MSG_BATTERY_LOW, "");
	zassert_equal(s.msg_until, 4000, "3 s");
	rscr_tick(&s, &v, 3999, &fx);
	zassert_equal(s.screen, SCR_MESSAGE, "");
	rscr_tick(&s, &v, 4000, &fx);
	zassert_equal(s.screen, SCR_STATUS, "back to the screen before");
	zassert_str_equal(rscr_msg_text(MSG_BATTERY_LOW), "Battery low", "");
	zassert_str_equal(rscr_msg_text(MSG_STORAGE_FULL), "Storage full", "");
	zassert_str_equal(rscr_msg_text(MSG_30_MIN), "30 min left", "");
	zassert_str_equal(rscr_msg_text(MSG_IN_CASE), "In case", "");
}

ZTEST(screens_table, test_notification_removed_by_the_phone_leaves_the_detail)
{
	struct rscr s;
	struct rscr_view v;
	struct rscr_fxs fx = { 0 };

	rscr_init(&s);
	std_view(&v);
	s.screen = SCR_NOTIF;
	s.notif_uid = 100;
	rscr_refresh(&s, &v, 1000, &fx);
	zassert_equal(s.screen, SCR_NOTIF, "still held");
	v.inbox_n = 1;
	v.inbox_uid[0] = 101;
	rscr_refresh(&s, &v, 1000, &fx);
	zassert_equal(s.screen, SCR_NOTIFS, "back to the list when the iPhone removed it");
}

ZTEST(screens_table, test_state_screens)
{
	static const struct {
		enum rc_state st;
		enum rscr_screen sc;
	} t[] = {
		{ RC_ST_CHARGING, SCR_CHARGING }, { RC_ST_TRANSFER, SCR_TRANSFER }, { RC_ST_RECOVERY, SCR_RECOVERY },
		{ RC_ST_ERR_STORAGE_FAULT, SCR_ERROR }, { RC_ST_ERR_MIC_FAULT, SCR_ERROR },
		{ RC_ST_ERR_CHARGER, SCR_ERROR }, { RC_ST_FACTORY_TEST, SCR_FACTORY }, { RC_ST_RECORDING, SCR_RECORDING },
		{ RC_ST_OFF, SCR_OFF }, { RC_ST_BOOT, SCR_OFF },
	};

	for (unsigned i = 0; i < ARRAY_SIZE(t); i++) {
		struct rscr s;
		struct rscr_view v;
		struct rscr_fxs fx = { 0 };
		struct rc_actions a;

		rscr_init(&s);
		std_view(&v);
		v.core_state = t[i].st;
		rc_actions_clear(&a);
		rscr_on_core(&s, &v, &a, RC_EV_COUNT, 1000, &fx);
		zassert_equal(s.screen, t[i].sc, "state %s shows %s, not %s", rc_state_name(t[i].st),
			      rscr_screen_name(t[i].sc), rscr_screen_name(s.screen));
	}
}

ZTEST(screens_table, test_recording_screens_every_action)
{
	/* SCR_RECORDING and SCR_REC_DIM: no direction and no centre does anything on the ring; each input shows the full
	 * recording picture and re-arms the 3 s dim timer, never the 5 s off timer (design/firmware.md 2.2, 3.2) */
	static const enum rscr_screen from[] = { SCR_RECORDING, SCR_REC_DIM };

	for (unsigned i = 0; i < ARRAY_SIZE(from); i++) {
		for (int d = DIR_UP; d <= DIR_CENTRE; d++) {
			struct rscr s;
			struct rscr_view v;
			struct rscr_fxs fx;

			rscr_init(&s);
			std_view(&v);
			v.core_state = RC_ST_RECORDING;
			s.seen_state = RC_ST_RECORDING;
			s.screen = from[i];
			feed(&s, &v, act_of((enum rscr_dir)d), RC_EV_COUNT, 1000, &fx);
			zassert_equal(s.screen, SCR_RECORDING, "%s dir %d: %s", rscr_screen_name(from[i]), d,
				      rscr_screen_name(s.screen));
			zassert_equal(fx.n, 0, "%s dir %d: no effect", rscr_screen_name(from[i]), d);
			zassert_equal(s.dim_at, 4000, "dim timer 3 s after the input");
			zassert_equal(s.off_at, RC_NO_TICK, "no off timer in RECORDING");
		}
	}
}

ZTEST(screens_table, test_recovery_and_factory_screens_ignore_the_joystick)
{
	/* SCR_RECOVERY: no action in the table of 2.2 (the ring is busy). SCR_FACTORY: the joystick is reported to the jig;
	 * the factory test is not built (software step 4 notes), so the screens do nothing with it. */
	static const struct {
		enum rscr_screen sc;
		enum rc_state st;
	} t[] = { { SCR_RECOVERY, RC_ST_RECOVERY }, { SCR_FACTORY, RC_ST_FACTORY_TEST } };

	for (unsigned i = 0; i < ARRAY_SIZE(t); i++) {
		for (int d = DIR_UP; d <= DIR_CENTRE; d++) {
			struct rscr s;
			struct rscr_view v;
			struct rscr_fxs fx;

			rscr_init(&s);
			std_view(&v);
			v.core_state = t[i].st;
			s.seen_state = t[i].st;
			s.screen = t[i].sc;
			feed(&s, &v, act_of((enum rscr_dir)d), RC_EV_COUNT, 1000, &fx);
			zassert_equal(s.screen, t[i].sc, "%s dir %d stays", rscr_screen_name(t[i].sc), d);
			zassert_equal(fx.n, 0, "%s dir %d: no effect", rscr_screen_name(t[i].sc), d);
			zassert_equal(s.off_at, RC_NO_TICK, "the screen stays on");
		}
	}
}

ZTEST(screens_table, test_wake_shows_the_screen_of_the_state)
{
	/* the lock: a joystick event with the screen off only turns it on, and what comes on is the screen of the core state */
	static const struct {
		enum rc_state st;
		enum rscr_screen sc;
	} t[] = {
		{ RC_ST_STANDBY, SCR_STATUS }, { RC_ST_CHARGING, SCR_CHARGING }, { RC_ST_TRANSFER, SCR_TRANSFER },
		{ RC_ST_ERR_STORAGE_FAULT, SCR_ERROR }, { RC_ST_ERR_BATTERY_LOW, SCR_STATUS },
	};

	for (unsigned i = 0; i < ARRAY_SIZE(t); i++) {
		struct rscr s;
		struct rscr_view v;
		struct rscr_fxs fx;

		rscr_init(&s);
		std_view(&v);
		v.core_state = t[i].st;
		s.seen_state = t[i].st;
		s.screen = SCR_OFF;
		feed(&s, &v, RC_ACT_SCREEN_ON, RC_EV_COUNT, 1000, &fx);
		zassert_equal(s.screen, t[i].sc, "state %s wakes to %s, not %s", rc_state_name(t[i].st),
			      rscr_screen_name(t[i].sc), rscr_screen_name(s.screen));
		zassert_equal(s.off_at, 6000, "off 5 s after the input");
	}
}

ZTEST(screens_table, test_brightness_levels_and_the_dimmed_recording_screen)
{
	/* design/firmware.md 3.2: SCR_REC_DIM is driven at the lowest of the three levels of the setting, never at 0 */
	for (uint8_t b = 0; b < 3; b++) {
		struct rscr s;

		rscr_init(&s);
		s.brightness = b;
		s.screen = SCR_STATUS;
		zassert_equal(rscr_brightness_level(&s), 85 + 85 * b, "setting %u: level %u", b, rscr_brightness_level(&s));
		s.screen = SCR_REC_DIM;
		zassert_equal(rscr_brightness_level(&s), 85, "SCR_REC_DIM at the lowest level (85) for every setting, not %u",
			      rscr_brightness_level(&s));
		zassert_true(rscr_brightness_level(&s) != 0, "never 0");
	}
}

ZTEST(screens_table, test_menu_has_five_items_outside_standby)
{
	/* "Power off" only in STANDBY: its core row is the STANDBY row */
	for (int st = 0; st < RC_ST_COUNT; st++) {
		struct rscr s;
		struct rscr_view v;
		struct rscr_fxs fx;
		uint8_t want = st == RC_ST_STANDBY ? 6 : 5;

		zassert_equal(rscr_menu_count((enum rc_state)st), want, "state %s: %u items", rc_state_name((enum rc_state)st),
			      rscr_menu_count((enum rc_state)st));
		if (st == RC_ST_RECORDING) {
			continue;   /* no menu in RECORDING (collision C2) */
		}
		rscr_init(&s);
		std_view(&v);
		v.core_state = (uint8_t)st;
		s.seen_state = (uint8_t)st;
		s.screen = SCR_MENU;
		for (int i = 0; i < 8; i++) {
			feed(&s, &v, RC_ACT_SCREEN_DOWN, RC_EV_COUNT, 1000 + i, &fx);
		}
		zassert_equal(s.menu_sel, want - 1, "state %s: Down stops at item %u", rc_state_name((enum rc_state)st), want);
	}
	/* in a state with five items the last item opens Settings, and Power off cannot be confirmed */
	{
		struct rscr s;
		struct rscr_view v;
		struct rscr_fxs fx;

		rscr_init(&s);
		std_view(&v);
		v.core_state = RC_ST_ERR_BATTERY_LOW;
		s.seen_state = RC_ST_ERR_BATTERY_LOW;
		s.screen = SCR_MENU;
		s.menu_sel = 4;
		feed(&s, &v, RC_ACT_SCREEN_RIGHT, RC_EV_COUNT, 1000, &fx);
		zassert_equal(s.screen, SCR_SETTINGS, "item 5 of 5 is Settings");
	}
}

ZTEST(screens_table, test_b15_message_in_standby_and_nothing_during_pairing_or_a_session)
{
	struct rscr_fxs fx;
	struct rc_actions a;

	/* panel off: the message shows for 5 s in amber (the message text is checked by the picture test) */
	{
		struct rscr s;
		struct rscr_view v;

		rscr_init(&s);
		std_view(&v);
		rc_actions_clear(&a);
		rc_actions_push(&a, RC_ACT_M3);
		rc_actions_push(&a, RC_ACT_SCR_STATUS_5S);
		memset(&fx, 0, sizeof(fx));
		rscr_on_core(&s, &v, &a, RC_EV_BATT_B15, 1000, &fx);
		zassert_equal(s.screen, SCR_MESSAGE, "B15: %s", rscr_screen_name(s.screen));
		zassert_equal(s.msg, MSG_BATTERY_LOW, "Battery low");
		zassert_equal(s.msg_until, 6000, "5 s");
		zassert_equal(fx.n, 0, "no effect");
	}
	/* SCR_PAIR shown: nothing, the window is not touched */
	{
		struct rscr s;
		struct rscr_view v;

		rscr_init(&s);
		std_view(&v);
		s.screen = SCR_PAIR;
		s.pair_slot = 1;
		s.pair_until = 61000;
		memset(&fx, 0, sizeof(fx));
		rscr_on_core(&s, &v, &a, RC_EV_BATT_B15, 1000, &fx);
		zassert_equal(s.screen, SCR_PAIR, "SCR_PAIR stays");
		zassert_equal(s.pair_until, 61000, "the window runs on");
		zassert_equal(fx.n, 0, "no pairing cancel");
	}
	/* a control session open: nothing, the session stays */
	{
		struct rscr s;
		struct rscr_view v;

		rscr_init(&s);
		std_view(&v);
		s.session = true;
		s.mode = RCTL_MEDIA;
		s.screen = SCR_CONTROL;
		memset(&fx, 0, sizeof(fx));
		rscr_on_core(&s, &v, &a, RC_EV_BATT_B15, 1000, &fx);
		zassert_equal(s.screen, SCR_CONTROL, "SCR_CONTROL stays");
		zassert_true(s.session, "the session stays open");
		zassert_equal(fx.n, 0, "no effect");
		/* and the session open with the panel off: still nothing */
		s.screen = SCR_OFF;
		rscr_on_core(&s, &v, &a, RC_EV_BATT_B15, 2000, &fx);
		zassert_equal(s.screen, SCR_OFF, "the panel stays off");
	}
	/* a short press with the panel off is not B15: it shows the status screen */
	{
		struct rscr s;
		struct rscr_view v;

		rscr_init(&s);
		std_view(&v);
		rc_actions_clear(&a);
		rc_actions_push(&a, RC_ACT_SCREEN_ON);
		rc_actions_push(&a, RC_ACT_SCR_STATUS_5S);
		memset(&fx, 0, sizeof(fx));
		rscr_on_core(&s, &v, &a, RC_EV_SHORT_PRESS, 1000, &fx);
		zassert_equal(s.screen, SCR_STATUS, "status");
	}
}

ZTEST(screens_table, test_double_press_in_a_session_with_the_panel_off_shows_the_modes)
{
	struct rig g;

	rig_init(&g);
	g.s.session = true;
	g.s.mode = RCTL_POINTER;
	g.s.last_mode = RCTL_POINTER;
	g.s.screen = SCR_OFF;
	g.c.facts.screen_on = rscr_lock_fact(&g.s);
	rig_double(&g);
	zassert_false(g.s.session, "closed");
	zassert_equal(g.s.screen, SCR_MODES, "SCR_MODES shown although the panel was off: %s", rscr_screen_name(g.s.screen));
	zassert_equal(g.s.mode_sel, RCTL_POINTER, "the last used mode is highlighted");
	/* the same when another screen was up (a message) */
	rig_init(&g);
	g.s.session = true;
	g.s.mode = RCTL_MEDIA;
	g.s.screen = SCR_MESSAGE;
	g.s.msg_back = SCR_CONTROL;
	g.s.msg_until = g.t + 3000;
	g.c.facts.screen_on = rscr_lock_fact(&g.s);
	rig_double(&g);
	zassert_equal(g.s.screen, SCR_MODES, "SCR_MODES: %s", rscr_screen_name(g.s.screen));
}

ZTEST(screens_table, test_mt_tick_follows_the_lock_fact_as_built)
{
	struct rig g;

	/* the first direction from the lit, dimmed recording screen: no tick (the fact is false) */
	rig_init(&g);
	rig_long(&g);
	rig_run_to(&g, g.t + 4000);
	zassert_equal(g.s.screen, SCR_REC_DIM, "dimmed");
	g.mts = 0;
	rig_dir(&g, RC_SW_RIGHT);
	zassert_equal(g.mts, 0, "no MT for the first direction from SCR_REC_DIM");
	zassert_equal(g.s.screen, SCR_RECORDING, "the full picture");
	rig_dir(&g, RC_SW_RIGHT);
	zassert_equal(g.mts, 1, "the next direction gives its tick");
	/* a direction in a session with the panel off: acted on at once, with a tick */
	rig_init(&g);
	g.s.session = true;
	g.s.mode = RCTL_MEDIA;
	g.s.screen = SCR_OFF;
	g.c.facts.screen_on = rscr_lock_fact(&g.s);
	g.mts = 0;
	rig_dir(&g, RC_SW_RIGHT);
	zassert_equal(g.sent, 1, "acted on");
	zassert_equal(g.mts, 1, "with a tick although the panel was off");
}

ZTEST(screens_table, test_power_off_only_in_standby)
{
	struct rscr s;
	struct rscr_view v;
	struct rscr_fxs fx;
	struct rc_actions a;

	/* (a) the menu is on "Power off" in STANDBY; the state changes: the selection is clamped to the five items, Centre then opens
	 * Settings (item 5 of 5), never the power-off confirmation */
	rscr_init(&s);
	std_view(&v);
	s.screen = SCR_MENU;
	s.menu_sel = MENU_POWER_OFF;
	v.core_state = RC_ST_ERR_BATTERY_LOW;
	rc_actions_clear(&a);
	memset(&fx, 0, sizeof(fx));
	rscr_on_core(&s, &v, &a, RC_EV_COUNT, 1000, &fx);
	zassert_equal(s.menu_sel, MENU_SETTINGS, "clamped to the last of five items: %u", s.menu_sel);
	feed(&s, &v, RC_ACT_SCREEN_CENTRE, RC_EV_COUNT, 1100, &fx);
	zassert_equal(s.screen, SCR_SETTINGS, "Centre opens Settings, not Power off: %s", rscr_screen_name(s.screen));

	/* (b) Centre and Right on an index beyond the count do nothing */
	for (int d = 0; d < 2; d++) {
		rscr_init(&s);
		std_view(&v);
		v.core_state = RC_ST_ERR_STORAGE_FULL;
		s.seen_state = RC_ST_ERR_STORAGE_FULL;
		s.screen = SCR_MENU;
		s.menu_sel = MENU_POWER_OFF;
		feed(&s, &v, d == 0 ? RC_ACT_SCREEN_CENTRE : RC_ACT_SCREEN_RIGHT, RC_EV_COUNT, 1000, &fx);
		zassert_equal(s.screen, SCR_MENU, "index 5 of 5 items: nothing opens (%s)", rscr_screen_name(s.screen));
		zassert_equal(fx.n, 0, "no effect");
	}

	/* (c) a power-off confirmation that is open when the state leaves STANDBY closes (back to the menu) */
	rscr_init(&s);
	std_view(&v);
	s.screen = SCR_CONFIRM;
	s.confirm_kind = CONFIRM_POWER_OFF;
	s.menu_sel = MENU_POWER_OFF;
	v.core_state = RC_ST_ERR_STORAGE_FULL;
	rc_actions_clear(&a);
	memset(&fx, 0, sizeof(fx));
	rscr_on_core(&s, &v, &a, RC_EV_COUNT, 1000, &fx);
	zassert_equal(s.screen, SCR_MENU, "the confirmation closed: %s", rscr_screen_name(s.screen));

	/* (d) FX_POWER_OFF is sent only in STANDBY, also when the confirmation is shown in another state */
	rscr_init(&s);
	std_view(&v);
	v.core_state = RC_ST_ERR_BATTERY_LOW;
	s.seen_state = RC_ST_ERR_BATTERY_LOW;
	s.screen = SCR_CONFIRM;
	s.confirm_kind = CONFIRM_POWER_OFF;
	feed(&s, &v, RC_ACT_SCREEN_CENTRE, RC_EV_COUNT, 1000, &fx);
	zassert_equal(fx.n, 0, "no power off outside STANDBY");
	rscr_init(&s);
	std_view(&v);
	s.screen = SCR_CONFIRM;
	s.confirm_kind = CONFIRM_POWER_OFF;
	feed(&s, &v, RC_ACT_SCREEN_CENTRE, RC_EV_COUNT, 1000, &fx);
	zassert_equal(fx.e[0].kind, FX_POWER_OFF, "in STANDBY Yes sends it");
}

/* ---- software step 6 (unit U9): the current limit and the factory frames (design/firmware.md 8.7, 9.3) ---- */

ZTEST(screens_table, test_ilim_dim_never_dark_in_recording)
{
	/* the current limit reads ACTIVE at 5,000 ms in RECORDING: the screen shows SCR_REC_DIM (panel level 85) for 10,000 ms and is
	 * never dark, whatever was shown before; an input in that time does not raise it; again while it runs changes nothing */
	static const enum rscr_screen before[] = { SCR_RECORDING, SCR_REC_DIM, SCR_MESSAGE };

	for (unsigned i = 0; i < ARRAY_SIZE(before); i++) {
		struct rscr s;
		struct rscr_view v;
		struct rscr_fxs fx;

		rscr_init(&s);
		std_view(&v);
		v.core_state = RC_ST_RECORDING;
		s.seen_state = RC_ST_RECORDING;
		s.screen = before[i];
		s.rec_start = 0;
		rscr_ilim(&s, &v, 5000);
		zassert_equal(s.screen, SCR_REC_DIM, "from %s: SCR_REC_DIM at once, got %s", rscr_screen_name(before[i]),
			      rscr_screen_name(s.screen));
		zassert_equal(rscr_brightness_level(&s), 85, "panel level 85, never 0");
		zassert_true(rscr_sign_ok(&s, RC_ST_RECORDING), "R-SIGN holds");
		zassert_equal(s.ilim_until, 15000, "held until 15,000 ms");
		for (rc_ms_t t = 5100; t <= 30000; t += 100) {
			memset(&fx, 0, sizeof(fx));
			rscr_tick(&s, &v, t, &fx);
			if (t == 7000 || t == 14900) {
				/* an input in the 10 s: the screen stays dimmed */
				feed(&s, &v, RC_ACT_SCREEN_RIGHT, RC_EV_COUNT, t, &fx);
			}
			if (t == 9000) {
				rscr_ilim(&s, &v, t);   /* again while it runs: the time is not extended */
				zassert_equal(s.ilim_until, 15000, "not extended");
			}
			if (t == 11000) {
				feed(&s, &v, RC_ACT_SCR_MSG_BATTERY_LOW_3S, RC_EV_COUNT, t, &fx);
			}
			zassert_not_equal(s.screen, SCR_OFF, "from %s: dark at %lld ms", rscr_screen_name(before[i]), (long long)t);
			zassert_true(rscr_sign_ok(&s, RC_ST_RECORDING), "R-SIGN at %lld ms", (long long)t);
			if (t < 15000) {
				zassert_equal(s.screen, SCR_REC_DIM, "dimmed at %lld ms, got %s", (long long)t,
					      rscr_screen_name(s.screen));
				zassert_equal(rscr_brightness_level(&s), 85, "level 85 at %lld ms", (long long)t);
			}
		}
		/* the 10 s are over: an input shows the full recording picture again */
		feed(&s, &v, RC_ACT_SCREEN_RIGHT, RC_EV_COUNT, 30000, &fx);
		zassert_equal(s.screen, SCR_RECORDING, "after the 10 s an input shows SCR_RECORDING");
		zassert_equal(s.ilim_until, RC_NO_TICK, "the hold ended");
	}
}

ZTEST(screens_table, test_start_during_ilim_hold_draws_dim_sign)
{
	/* a recording starts at 8,000 ms inside the hold (5,000 to 15,000 ms): the sign is SCR_REC_DIM at panel level 85, never dark, and
	 * the core's step into RECORDING keeps it so; after the hold the normal rules apply (an input shows SCR_RECORDING) */
	struct rscr s;
	struct rscr_view v;
	struct rscr_fxs fx = { 0 };
	struct rc_actions al;

	rscr_init(&s);
	std_view(&v);
	rscr_ilim(&s, &v, 5000);
	rscr_sign_begin(&s, 8000);
	zassert_equal(s.screen, SCR_REC_DIM, "the sign in the hold is SCR_REC_DIM, got %s", rscr_screen_name(s.screen));
	zassert_equal(rscr_brightness_level(&s), 85, "panel level 85");
	zassert_true(rscr_has_sign(&s, RC_ST_RECORDING), "the red dot and the timer are drawn");
	zassert_equal(s.rec_start, 8000, "the timer starts at 8,000 ms");
	v.core_state = RC_ST_RECORDING;
	rc_actions_clear(&al);
	rscr_on_core(&s, &v, &al, RC_EV_COUNT, 8010, &fx);
	zassert_equal(s.screen, SCR_REC_DIM, "RECORDING entered: still dimmed, got %s", rscr_screen_name(s.screen));
	for (rc_ms_t t = 8100; t < 15000; t += 100) {
		rscr_tick(&s, &v, t, &fx);
		zassert_equal(s.screen, SCR_REC_DIM, "dimmed at %lld ms", (long long)t);
		zassert_true(rscr_sign_ok(&s, RC_ST_RECORDING), "R-SIGN at %lld ms", (long long)t);
	}
	rscr_tick(&s, &v, 15000, &fx);
	feed(&s, &v, RC_ACT_SCREEN_RIGHT, RC_EV_COUNT, 15000, &fx);
	zassert_equal(s.screen, SCR_RECORDING, "after the hold an input shows SCR_RECORDING");
	/* with no hold the sign is the full picture, dimming after 3,000 ms (the rule of step 4) */
	rscr_init(&s);
	rscr_sign_begin(&s, 1000);
	zassert_equal(s.screen, SCR_RECORDING, "no hold: SCR_RECORDING");
	zassert_equal(s.dim_at, 4000, "dims at 4,000 ms");
}

ZTEST(screens_table, test_ilim_off_10s_outside_recording)
{
	/* outside RECORDING the screen goes off at once and stays off for 10,000 ms, input or not; then it can be woken */
	static const enum rscr_screen before[] = { SCR_STATUS, SCR_MENU, SCR_MODES, SCR_NOTIFS };

	for (unsigned i = 0; i < ARRAY_SIZE(before); i++) {
		struct rscr s;
		struct rscr_view v;
		struct rscr_fxs fx;

		rscr_init(&s);
		std_view(&v);
		s.screen = before[i];
		s.off_at = 9000;
		rscr_ilim(&s, &v, 5000);
		zassert_equal(s.screen, SCR_OFF, "from %s: off at once", rscr_screen_name(before[i]));
		zassert_false(rscr_lock_fact(&s), "the lock fact: the screen is not lit");
		zassert_equal(s.ilim_until, 15000, "held until 15,000 ms");
		for (rc_ms_t t = 5100; t < 15000; t += 100) {
			memset(&fx, 0, sizeof(fx));
			rscr_tick(&s, &v, t, &fx);
			if (t == 6000) {
				feed(&s, &v, RC_ACT_SCREEN_ON, RC_EV_COUNT, t, &fx);   /* the first input */
			}
			if (t == 9000) {
				rscr_ilim(&s, &v, t);   /* again with the screen off: nothing changes */
				zassert_equal(s.ilim_until, 15000, "not extended");
			}
			if (t == 12000) {
				feed(&s, &v, RC_ACT_SCREEN_UP, RC_EV_COUNT, t, &fx);
			}
			zassert_equal(s.screen, SCR_OFF, "from %s: off at %lld ms, got %s", rscr_screen_name(before[i]),
				      (long long)t, rscr_screen_name(s.screen));
		}
		rscr_tick(&s, &v, 15000, &fx);
		zassert_equal(s.ilim_until, RC_NO_TICK, "the hold ended at 15,000 ms");
		zassert_equal(s.screen, SCR_OFF, "still off until an input");
		feed(&s, &v, RC_ACT_SCREEN_ON, RC_EV_COUNT, 15000, &fx);
		zassert_equal(s.screen, SCR_STATUS, "an input at 15,000 ms wakes the screen");
		/* a new reading after the 10 s starts a new 10 s */
		rscr_ilim(&s, &v, 16000);
		zassert_equal(s.screen, SCR_OFF, "off again");
		zassert_equal(s.ilim_until, 26000, "a new 10 s");
	}
}

ZTEST(screens_table, test_factory_frame_state_rules)
{
	/* a frame is accepted only in FACTORY_TEST, nothing changes when it is refused, and it is dropped when the state is left */
	for (int st = RC_ST_SHIP; st <= RC_ST_FACTORY_TEST; st++) {
		struct rscr s, before;
		struct rscr_view v;

		rscr_init(&s);
		std_view(&v);
		v.core_state = (uint8_t)st;
		s.seen_state = (uint8_t)st;
		before = s;
		for (int f = FAC_NONE; f < FAC_COUNT; f++) {
			bool ok = rscr_fac_frame(&s, &v, (enum rscr_fac_frame)f, 1000);

			if (st == RC_ST_FACTORY_TEST) {
				zassert_true(ok, "frame %d accepted in FACTORY_TEST", f);
				zassert_equal(s.screen, SCR_FACTORY, "on SCR_FACTORY");
				zassert_equal(s.fac_frame, f, "frame %d kept", f);
			} else {
				zassert_false(ok, "frame %d refused in state %d", f, st);
				zassert_equal(memcmp(&s, &before, sizeof(s)), 0, "state %d: nothing changed", st);
			}
		}
		if (st == RC_ST_FACTORY_TEST) {
			struct rscr_fxs fx = { 0 };
			struct rc_actions al;

			zassert_false(rscr_fac_frame(&s, &v, FAC_COUNT, 1000), "a number outside the enum is refused");
			zassert_equal(s.fac_frame, FAC_GRID, "and the last frame stays");
			v.core_state = RC_ST_STANDBY;
			rc_actions_clear(&al);
			rscr_on_core(&s, &v, &al, RC_EV_COUNT, 2000, &fx);
			zassert_equal(s.fac_frame, FAC_NONE, "the frame is dropped when FACTORY_TEST is left");
		}
	}
}

ZTEST_SUITE(screens_table, NULL, NULL, NULL, NULL, NULL);
