/* Ring screens, pure part: see rscr_logic.h. */

#include <errno.h>
#include <string.h>
#include <zephyr/sys/util.h>

#include <ring_core/rc_sm.h>
#include <ring_screens/rscr_logic.h>

static const char *const screen_names[SCR_COUNT] = {
	[SCR_OFF] = "SCR_OFF", [SCR_STATUS] = "SCR_STATUS", [SCR_RECORDING] = "SCR_RECORDING",
	[SCR_REC_DIM] = "SCR_REC_DIM", [SCR_MENU] = "SCR_MENU", [SCR_RECORDINGS] = "SCR_RECORDINGS",
	[SCR_RECORDING_INFO] = "SCR_RECORDING_INFO", [SCR_SETTINGS] = "SCR_SETTINGS", [SCR_CONFIRM] = "SCR_CONFIRM",
	[SCR_PAIR] = "SCR_PAIR", [SCR_MODES] = "SCR_MODES", [SCR_CONTROL] = "SCR_CONTROL", [SCR_DEVICES] = "SCR_DEVICES",
	[SCR_DEVICE] = "SCR_DEVICE", [SCR_MESSAGE] = "SCR_MESSAGE", [SCR_CHARGING] = "SCR_CHARGING",
	[SCR_TRANSFER] = "SCR_TRANSFER", [SCR_ERROR] = "SCR_ERROR", [SCR_RECOVERY] = "SCR_RECOVERY",
	[SCR_FACTORY] = "SCR_FACTORY", [SCR_NOTIFS] = "SCR_NOTIFS", [SCR_NOTIF] = "SCR_NOTIF",
};

const char *rscr_screen_name(enum rscr_screen sc)
{
	return (unsigned)sc < SCR_COUNT ? screen_names[sc] : "?";
}

const char *rscr_menu_name(enum rscr_menu_item i)
{
	static const char *const n[MENU_COUNT] = { "Recordings", "Control", "Devices", "Pair device", "Settings",
						   "Power off" };
	return (unsigned)i < MENU_COUNT ? n[i] : "?";
}

const char *rscr_msg_text(enum rscr_msg m)
{
	static const char *const t[MSG_COUNT] = { "Battery low", "Storage full", "30 min left", "In case",
						  "Remove a device first" };
	return (unsigned)m < MSG_COUNT ? t[m] : "?";
}

uint8_t rscr_menu_count(enum rc_state st)
{
	/* "Power off" (the sixth item) is offered only in STANDBY: the core's row for it is the STANDBY row (design/firmware.md 1.2) */
	return st == RC_ST_STANDBY ? MENU_COUNT : MENU_COUNT - 1;
}

uint8_t rscr_brightness_level(const struct rscr *s)
{
	/* the three levels of the setting "Screen brightness" are 85, 170 and 255; SCR_REC_DIM is driven at the lowest of the three,
	 * never at 0 (design/firmware.md 3.2) */
	return s->screen == SCR_REC_DIM ? RSCR_LEVEL_LOWEST : (uint8_t)(RSCR_LEVEL_LOWEST + RSCR_LEVEL_STEP * s->brightness);
}

void rscr_init(struct rscr *s)
{
	memset(s, 0, sizeof(*s));
	s->screen = SCR_OFF;
	s->seen_state = RC_ST_STANDBY;
	s->last_mode = RCTL_MEDIA;
	s->mode_sel = RCTL_MEDIA;
	s->brightness = 2;
	s->vibration = true;
	s->dev_slot = RDEV_NONE;
	s->pair_slot = RDEV_NONE;
	s->off_at = s->dim_at = s->msg_until = s->pair_until = s->session_at = s->ilim_until = RC_NO_TICK;
}

uint8_t rscr_paired_count(uint8_t m)
{
	uint8_t n = 0;

	for (uint8_t i = 0; i < RDEV_SLOTS; i++) {
		n += (m >> i) & 1U;
	}
	return n;
}

uint8_t rscr_paired_slot(uint8_t m, uint8_t idx)
{
	for (uint8_t i = 0; i < RDEV_SLOTS; i++) {
		if (((m >> i) & 1U) != 0 && idx-- == 0) {
			return i;
		}
	}
	return RDEV_NONE;
}

static bool is_rec_screen(uint8_t sc)
{
	return sc == SCR_RECORDING || sc == SCR_REC_DIM;
}

bool rscr_lock_fact(const struct rscr *s)
{
	bool full = s->screen != SCR_OFF && s->screen != SCR_REC_DIM;

	return full || s->session;
}

bool rscr_has_sign(const struct rscr *s, enum rc_state st)
{
	return is_rec_screen(s->screen) || (st == RC_ST_RECORDING && s->screen == SCR_MESSAGE);
}

bool rscr_sign_ok(const struct rscr *s, enum rc_state st)
{
	if (st != RC_ST_RECORDING) {
		return true;
	}
	return rscr_has_sign(s, st);
}

/* ---- helpers ---- */

static void fx_push(struct rscr_fxs *fx, uint8_t kind, uint8_t a, uint32_t u)
{
	if (fx != NULL && fx->n < RSCR_MAX_FX) {
		fx->e[fx->n].kind = kind;
		fx->e[fx->n].a = a;
		fx->e[fx->n].u = u;
		fx->n++;
	}
}

static void arm_idle(struct rscr *s, const struct rscr_view *v, rc_ms_t now)
{
	if (v->core_state == RC_ST_RECORDING) {
		s->off_at = RC_NO_TICK;
		s->dim_at = now + RSCR_DIM_MS;
	} else {
		s->dim_at = RC_NO_TICK;
		s->off_at = now + RSCR_OFF_MS;
	}
}

static void session_touch(struct rscr *s, rc_ms_t now)
{
	if (s->session) {
		s->session_at = now + RSCR_SESSION_MS;
	}
}

/* The screen the panel shows when it is woken, and after a leave */
static uint8_t home_screen(const struct rscr *s, const struct rscr_view *v)
{
	switch (v->core_state) {
	case RC_ST_RECORDING:
		return SCR_RECORDING;
	case RC_ST_CHARGING:
		return SCR_CHARGING;
	case RC_ST_TRANSFER:
		return SCR_TRANSFER;
	case RC_ST_RECOVERY:
		return SCR_RECOVERY;
	case RC_ST_FACTORY_TEST:
		return SCR_FACTORY;
	case RC_ST_ERR_STORAGE_FAULT:
	case RC_ST_ERR_MIC_FAULT:
	case RC_ST_ERR_CHARGER:
		return SCR_ERROR;
	default:
		return s->session ? SCR_CONTROL : SCR_STATUS;
	}
}

static bool ilim_hold(const struct rscr *s, rc_ms_t now)
{
	return s->ilim_until != RC_NO_TICK && now < s->ilim_until;
}

static void show(struct rscr *s, const struct rscr_view *v, uint8_t sc, rc_ms_t now)
{
	if (ilim_hold(s, now)) {
		/* the current limit holds the screen down: off, and in RECORDING the dimmed sign (R-SIGN) */
		if (v->core_state != RC_ST_RECORDING) {
			s->screen = SCR_OFF;
			s->off_at = s->dim_at = s->msg_until = RC_NO_TICK;
			return;
		}
		sc = SCR_REC_DIM;
	}
	s->screen = sc;
	if (sc == SCR_PAIR || sc == SCR_RECOVERY || sc == SCR_FACTORY) {
		s->off_at = RC_NO_TICK;
		s->dim_at = RC_NO_TICK;
	} else {
		arm_idle(s, v, now);
	}
	s->msg_until = sc == SCR_MESSAGE ? s->msg_until : RC_NO_TICK;
}

static void close_session(struct rscr *s, const struct rscr_view *v, struct rscr_fxs *fx, rc_ms_t now)
{
	if (!s->session) {
		return;
	}
	s->session = false;
	s->session_at = RC_NO_TICK;
	fx_push(fx, FX_CONTROL_ACTIVE, 0, 0);
	if (s->screen == SCR_CONTROL) {
		/* "A double press of the centre closes the session and shows SCR_MODES (in RECORDING: SCR_RECORDING)" */
		if (v->core_state == RC_ST_RECORDING) {
			show(s, v, SCR_RECORDING, now);
		} else {
			s->mode_sel = s->last_mode;
			show(s, v, SCR_MODES, now);
		}
	}
}

static void message_for(struct rscr *s, const struct rscr_view *v, enum rscr_msg m, rc_ms_t now, int ms)
{
	if (s->screen != SCR_MESSAGE) {
		s->msg_back = s->screen == SCR_OFF ? home_screen(s, v) : s->screen;
	}
	s->msg = m;
	s->screen = SCR_MESSAGE;
	s->msg_until = now + ms;
	if (ilim_hold(s, now)) {
		show(s, v, SCR_MESSAGE, now);   /* held down: off, or the dimmed sign in RECORDING */
		return;
	}
	arm_idle(s, v, now);
	/* the panel stays on at least as long as the message */
	if (s->off_at != RC_NO_TICK && s->off_at < s->msg_until) {
		s->off_at = s->msg_until;
	}
}

static void message(struct rscr *s, const struct rscr_view *v, enum rscr_msg m, rc_ms_t now)
{
	message_for(s, v, m, now, RSCR_MSG_MS);
}

static void leave_pair(struct rscr *s, struct rscr_fxs *fx)
{
	if (s->pair_until != RC_NO_TICK || s->pair_slot != RDEV_NONE) {
		fx_push(fx, FX_PAIR_CANCEL, 0, 0);
	}
	s->pair_until = RC_NO_TICK;
	s->pair_slot = RDEV_NONE;
	s->pair_has_key = false;
}

/* ---- navigation: the table of design/firmware.md 2.2 and 3.4, one screen per case ---- */

static void clamp_sel(uint8_t *sel, uint8_t n)
{
	if (n == 0) {
		*sel = 0;
	} else if (*sel >= n) {
		*sel = (uint8_t)(n - 1);
	}
}

static void step(uint8_t *sel, uint8_t n, enum rscr_dir d)
{
	if (n == 0) {
		*sel = 0;
	} else if (d == DIR_UP) {
		*sel = *sel > 0 ? (uint8_t)(*sel - 1) : 0;
	} else if (*sel + 1 < n) {
		(*sel)++;
	}
}

static bool is_open_dir(enum rscr_dir d)
{
	return d == DIR_RIGHT || d == DIR_CENTRE;
}

static int notif_index(const struct rscr_view *v, uint32_t uid)
{
	for (uint8_t i = 0; i < v->inbox_n && i < RINBOX_MAX; i++) {
		if (v->inbox_uid[i] == uid) {
			return i;
		}
	}
	return -1;
}

static void open_notif(struct rscr *s, const struct rscr_view *v, uint8_t idx, rc_ms_t now, struct rscr_fxs *fx)
{
	s->notif_sel = idx;
	s->notif_uid = v->inbox_uid[idx];
	fx_push(fx, FX_NOTIF_READ, 0, s->notif_uid);
	show(s, v, SCR_NOTIF, now);
}

static void nav(struct rscr *s, const struct rscr_view *v, enum rscr_dir d, rc_ms_t now, struct rscr_fxs *fx)
{
	switch (s->screen) {
	case SCR_STATUS:
		if (d == DIR_UP) {
			s->notif_sel = 0;
			show(s, v, SCR_NOTIFS, now);
		} else if (is_open_dir(d)) {
			s->menu_sel = 0;
			show(s, v, SCR_MENU, now);
		} else {
			show(s, v, SCR_STATUS, now);
		}
		break;
	case SCR_MENU:
		if (d == DIR_UP || d == DIR_DOWN) {
			step(&s->menu_sel, rscr_menu_count((enum rc_state)v->core_state), d);
			show(s, v, SCR_MENU, now);
		} else if (d == DIR_LEFT) {
			show(s, v, SCR_STATUS, now);
		} else if (s->menu_sel >= rscr_menu_count((enum rc_state)v->core_state)) {
			/* an index beyond the item count (the state changed under the menu): Centre and Right do nothing */
			show(s, v, SCR_MENU, now);
		} else {
			switch (s->menu_sel) {
			case MENU_RECORDINGS:
				s->rec_sel = 0;
				show(s, v, SCR_RECORDINGS, now);
				break;
			case MENU_CONTROL:
				s->mode_sel = s->last_mode;
				show(s, v, SCR_MODES, now);
				break;
			case MENU_DEVICES:
				s->dev_sel = 0;
				show(s, v, SCR_DEVICES, now);
				break;
			case MENU_PAIR: {
				uint8_t free_slot = RDEV_NONE;

				for (uint8_t i = 0; i < RDEV_SLOTS; i++) {
					if (((v->paired_mask >> i) & 1U) == 0) {
						free_slot = i;
						break;
					}
				}
				if (free_slot == RDEV_NONE) {
					/* with three paired devices SCR_PAIR does not open */
					s->msg_back = SCR_MENU;
					message(s, v, MSG_REMOVE_FIRST, now);
				} else {
					s->pair_slot = free_slot;
					s->pair_has_key = false;
					s->pair_until = now + RSCR_PAIR_MS;
					fx_push(fx, FX_PAIR_OPEN, free_slot, 0);
					show(s, v, SCR_PAIR, now);
				}
				break;
			}
			case MENU_SETTINGS:
				s->set_sel = 0;
				show(s, v, SCR_SETTINGS, now);
				break;
			default:
				s->confirm_kind = CONFIRM_POWER_OFF;
				show(s, v, SCR_CONFIRM, now);
				break;
			}
		}
		break;
	case SCR_RECORDINGS:
		if (d == DIR_UP || d == DIR_DOWN) {
			step(&s->rec_sel, v->rec_n, d);
			show(s, v, SCR_RECORDINGS, now);
		} else if (d == DIR_LEFT) {
			show(s, v, SCR_MENU, now);
		} else if (v->rec_n > 0) {
			show(s, v, SCR_RECORDING_INFO, now);
		} else {
			show(s, v, SCR_RECORDINGS, now);
		}
		break;
	case SCR_RECORDING_INFO:
		show(s, v, d == DIR_LEFT ? SCR_RECORDINGS : SCR_RECORDING_INFO, now);
		break;
	case SCR_SETTINGS:
		if (d == DIR_UP || d == DIR_DOWN) {
			step(&s->set_sel, SET_COUNT, d);
		} else if (d == DIR_LEFT) {
			show(s, v, SCR_MENU, now);
			break;
		} else if (s->set_sel == SET_BRIGHTNESS) {
			s->brightness = (uint8_t)((s->brightness + 1) % 3);
			fx_push(fx, FX_BRIGHTNESS, s->brightness, 0);
		} else if (s->set_sel == SET_VIBRATION) {
			s->vibration = !s->vibration;
			fx_push(fx, FX_VIBRATION, s->vibration ? 1 : 0, 0);
		} else if (s->set_sel == SET_TIME_FORMAT) {
			s->fmt12 = !s->fmt12;
		}
		show(s, v, SCR_SETTINGS, now);
		break;
	case SCR_MODES:
		if (d == DIR_UP || d == DIR_DOWN) {
			step(&s->mode_sel, RCTL_MODE_COUNT, d);
			show(s, v, SCR_MODES, now);
		} else if (d == DIR_LEFT) {
			show(s, v, SCR_MENU, now);
		} else {
			s->mode = s->mode_sel;
			s->last_mode = s->mode_sel;
			s->session = true;
			session_touch(s, now);
			fx_push(fx, FX_SET_MODE, s->mode, 0);
			fx_push(fx, FX_CONTROL_ACTIVE, 1, 0);
			show(s, v, SCR_CONTROL, now);
		}
		break;
	case SCR_CONTROL:
		/* every direction and the centre go to the active device; nothing happens on the ring */
		show(s, v, SCR_CONTROL, now);
		break;
	case SCR_DEVICES: {
		uint8_t n = rscr_paired_count(v->paired_mask);

		if (d == DIR_UP || d == DIR_DOWN) {
			step(&s->dev_sel, n, d);
			show(s, v, SCR_DEVICES, now);
		} else if (d == DIR_LEFT) {
			show(s, v, SCR_MENU, now);
		} else if (n > 0) {
			clamp_sel(&s->dev_sel, n);
			s->dev_slot = rscr_paired_slot(v->paired_mask, s->dev_sel);
			s->dev_item = DEV_USE;
			show(s, v, SCR_DEVICE, now);
		} else {
			show(s, v, SCR_DEVICES, now);
		}
		break;
	}
	case SCR_DEVICE:
		if (d == DIR_UP || d == DIR_DOWN) {
			step(&s->dev_item, DEV_ITEM_COUNT, d);
			show(s, v, SCR_DEVICE, now);
		} else if (d == DIR_LEFT) {
			show(s, v, SCR_DEVICES, now);
		} else if (s->dev_item == DEV_USE) {
			fx_push(fx, FX_DEV_USE, s->dev_slot, 0);
			show(s, v, SCR_DEVICES, now);
		} else {
			s->confirm_kind = CONFIRM_REMOVE;
			s->confirm_slot = s->dev_slot;
			show(s, v, SCR_CONFIRM, now);
		}
		break;
	case SCR_CONFIRM:
		if (d == DIR_LEFT) {
			show(s, v, s->confirm_kind == CONFIRM_REMOVE ? SCR_DEVICE : SCR_MENU, now);
		} else if (d == DIR_CENTRE) {
			if (s->confirm_kind == CONFIRM_POWER_OFF) {
				/* the core has a power-off row only in STANDBY: nothing is sent in any other state */
				if (v->core_state == RC_ST_STANDBY) {
					fx_push(fx, FX_POWER_OFF, 0, 0);
				}
				show(s, v, SCR_STATUS, now);
			} else {
				fx_push(fx, FX_DEV_REMOVE, s->confirm_slot, 0);
				show(s, v, SCR_DEVICES, now);
			}
		} else {
			show(s, v, SCR_CONFIRM, now);
		}
		break;
	case SCR_PAIR:
		if (d == DIR_LEFT) {
			leave_pair(s, fx);
			show(s, v, SCR_MENU, now);
		}
		break;
	case SCR_MESSAGE:
		/* every direction and the centre dismiss the message */
		s->msg_until = RC_NO_TICK;
		show(s, v, s->msg_back == SCR_OFF ? home_screen(s, v) : s->msg_back, now);
		break;
	case SCR_CHARGING:
	case SCR_TRANSFER:
	case SCR_ERROR:
		if (d == DIR_CENTRE) {
			s->screen = SCR_OFF;
			s->off_at = s->dim_at = RC_NO_TICK;
		} else {
			show(s, v, s->screen, now);
		}
		break;
	case SCR_NOTIFS:
		if (d == DIR_UP || d == DIR_DOWN) {
			step(&s->notif_sel, v->inbox_n, d);
			show(s, v, SCR_NOTIFS, now);
		} else if (d == DIR_LEFT) {
			show(s, v, SCR_STATUS, now);
		} else if (v->inbox_n > 0) {
			clamp_sel(&s->notif_sel, v->inbox_n);
			open_notif(s, v, s->notif_sel, now, fx);
		} else {
			show(s, v, SCR_NOTIFS, now);
		}
		break;
	case SCR_NOTIF: {
		int i = notif_index(v, s->notif_uid);

		if (i < 0) {
			show(s, v, SCR_NOTIFS, now);
			break;
		}
		if (d == DIR_LEFT) {
			/* the dismiss: the negative action, only for a notification that has it */
			if ((v->inbox_flags[i] & RINBOX_F_NEGATIVE) != 0) {
				fx_push(fx, FX_NOTIF_DISMISS, 0, s->notif_uid);
			}
			show(s, v, SCR_NOTIF, now);
		} else if (d == DIR_RIGHT) {
			if ((v->inbox_flags[i] & RINBOX_F_POSITIVE) != 0) {
				fx_push(fx, FX_NOTIF_POSITIVE, 0, s->notif_uid);
			}
			show(s, v, SCR_NOTIF, now);
		} else if (d == DIR_CENTRE) {
			s->notif_sel = (uint8_t)i;
			show(s, v, SCR_NOTIFS, now);
		} else {
			int j = d == DIR_UP ? i - 1 : i + 1;

			if (j >= 0 && j < v->inbox_n) {
				open_notif(s, v, (uint8_t)j, now, fx);
			} else {
				show(s, v, SCR_NOTIF, now);
			}
		}
		break;
	}
	case SCR_FACTORY:
		/* reported to the jig: the factory test is not built */
		break;
	default:
		break;
	}
}

/* ---- the core's state decides the screen on entry (design/firmware.md 1.1, screen column) ---- */

static void enter_state(struct rscr *s, const struct rscr_view *v, rc_ms_t now, struct rscr_fxs *fx)
{
	enum rc_state st = (enum rc_state)v->core_state;
	enum rc_state from = (enum rc_state)s->seen_state;

	s->seen_state = (uint8_t)st;
	if (st != RC_ST_FACTORY_TEST) {
		s->fac_frame = FAC_NONE;   /* a test frame lives only in FACTORY_TEST */
	}
	/* "Power off" exists only in STANDBY: the menu selection is clamped to the new item count, and a power-off confirmation that
	 * is open closes (back to the menu) */
	clamp_sel(&s->menu_sel, rscr_menu_count(st));
	if (st != RC_ST_STANDBY && s->screen == SCR_CONFIRM && s->confirm_kind == CONFIRM_POWER_OFF) {
		show(s, v, SCR_MENU, now);
	}
	/* the session closes when the ring enters any state other than STANDBY and RECORDING */
	if (st != RC_ST_STANDBY && st != RC_ST_RECORDING) {
		s->session = false;
		s->session_at = RC_NO_TICK;
		fx_push(fx, FX_CONTROL_ACTIVE, 0, 0);
	}
	if (st != RC_ST_STANDBY && s->screen == SCR_PAIR) {
		leave_pair(s, fx);
	}
	switch (st) {
	case RC_ST_RECORDING:
		/* collision C2: a long press discards every open screen; the session stays (3.4) */
		leave_pair(s, fx);
		close_session(s, v, fx, now);
		s->highlights = 0;
		s->msg_until = RC_NO_TICK;
		show(s, v, SCR_RECORDING, now);
		break;
	case RC_ST_STANDBY:
		if (from == RC_ST_RECORDING) {
			show(s, v, home_screen(s, v), now);
		} else if (from == RC_ST_CHARGING || from == RC_ST_TRANSFER || from == RC_ST_RECOVERY ||
			   from == RC_ST_FACTORY_TEST || from == RC_ST_ERR_STORAGE_FAULT ||
			   from == RC_ST_ERR_MIC_FAULT || from == RC_ST_ERR_CHARGER) {
			show(s, v, SCR_STATUS, now);  /* "SCR_STATUS ... error states after their message" */
		} else if (from == RC_ST_BOOT) {
			s->screen = SCR_OFF;
		}
		break;
	case RC_ST_CHARGING:
		show(s, v, SCR_CHARGING, now);
		s->off_at = now + RSCR_CHARGING_MS;
		break;
	case RC_ST_TRANSFER:
		show(s, v, SCR_TRANSFER, now);
		break;
	case RC_ST_RECOVERY:
		show(s, v, SCR_RECOVERY, now);
		break;
	case RC_ST_ERR_STORAGE_FAULT:
	case RC_ST_ERR_CHARGER:
		show(s, v, SCR_ERROR, now);
		s->off_at = now + RSCR_ERR_STORAGE_MS;
		break;
	case RC_ST_ERR_MIC_FAULT:
		show(s, v, SCR_ERROR, now);
		s->off_at = now + RSCR_ERR_MIC_MS;
		break;
	case RC_ST_FACTORY_TEST:
		show(s, v, SCR_FACTORY, now);
		break;
	case RC_ST_ERR_STORAGE_FULL:
	case RC_ST_ERR_BATTERY_LOW:
		/* "as STANDBY": the screen is off unless a message is showing */
		if (from == RC_ST_RECORDING) {
			show(s, v, SCR_STATUS, now);
		}
		break;
	default:
		s->screen = SCR_OFF;
		s->off_at = s->dim_at = s->msg_until = RC_NO_TICK;
		break;
	}
}

static void wake(struct rscr *s, const struct rscr_view *v, rc_ms_t now)
{
	/* the lock: the first joystick event only turns the full screen on */
	show(s, v, home_screen(s, v), now);
}

void rscr_on_core(struct rscr *s, const struct rscr_view *v, const struct rc_actions *a, enum rc_event last_event,
		  rc_ms_t now, struct rscr_fxs *fx)
{
	bool recording;

	if (v->core_state != s->seen_state) {
		enter_state(s, v, now, fx);
	}
	recording = v->core_state == RC_ST_RECORDING;
	for (uint8_t i = 0; i < a->n; i++) {
		switch ((enum rc_action)a->a[i]) {
		case RC_ACT_OPEN:
			s->rec_start = now;
			break;
		case RC_ACT_HIGHLIGHT:
			if (s->highlights < UINT16_MAX) {
				s->highlights++;
			}
			break;
		case RC_ACT_SCREEN_ON:
			wake(s, v, now);
			break;
		case RC_ACT_SCR_STATUS_5S:
			if (last_event == RC_EV_BATT_B15) {
				/* B15 in STANDBY: the status screen no longer shows the battery, so "Battery low" shows for 5 s,
				 * amber; while SCR_PAIR is shown or a control session is open it shows nothing (the vibration M3 is
				 * the warning) and neither the pairing window nor the session is touched */
				if (!recording && s->screen != SCR_PAIR && !s->session) {
					message_for(s, v, MSG_BATTERY_LOW, now, RSCR_B15_MSG_MS);
				}
			} else if (!recording) {
				show(s, v, SCR_STATUS, now);
			}
			break;
		case RC_ACT_SCR_RECORDING_3S:
			s->msg_until = RC_NO_TICK;
			show(s, v, SCR_RECORDING, now);
			break;
		case RC_ACT_SCR_MSG_30MIN_3S:
			message(s, v, MSG_30_MIN, now);
			break;
		case RC_ACT_SCR_MSG_IN_CASE_3S:
			message(s, v, MSG_IN_CASE, now);
			break;
		case RC_ACT_SCR_MSG_STORAGE_FULL_3S:
			message(s, v, MSG_STORAGE_FULL, now);
			break;
		case RC_ACT_SCR_MSG_BATTERY_LOW_3S:
			message(s, v, MSG_BATTERY_LOW, now);
			break;
		case RC_ACT_SCREEN_UP:
		case RC_ACT_SCREEN_DOWN:
		case RC_ACT_SCREEN_LEFT:
		case RC_ACT_SCREEN_RIGHT:
		case RC_ACT_SCREEN_CENTRE: {
			enum rscr_dir d = a->a[i] == RC_ACT_SCREEN_UP     ? DIR_UP
					  : a->a[i] == RC_ACT_SCREEN_DOWN ? DIR_DOWN
					  : a->a[i] == RC_ACT_SCREEN_LEFT ? DIR_LEFT
					  : a->a[i] == RC_ACT_SCREEN_RIGHT ? DIR_RIGHT
									   : DIR_CENTRE;

			session_touch(s, now);
			if (recording) {
				/* nothing to navigate in RECORDING: any input shows the full recording picture for 3 s
				 * (the direction itself went to the active device through control, in a session) */
				if (s->screen == SCR_MESSAGE) {
					s->msg_until = RC_NO_TICK;
				}
				show(s, v, SCR_RECORDING, now);
			} else if (s->screen == SCR_OFF) {
				wake(s, v, now);
			} else {
				nav(s, v, d, now, fx);
			}
			break;
		}
		default:
			break;
		}
	}
	if (last_event == RC_EV_DOUBLE_PRESS && s->session) {
		close_session(s, v, fx, now);
		if (recording) {
			/* in RECORDING the input shows SCR_RECORDING for 3 s */
			show(s, v, SCR_RECORDING, now);
		} else {
			/* in STANDBY the double press always shows SCR_MODES, also when the panel was off */
			s->mode_sel = s->last_mode;
			show(s, v, SCR_MODES, now);
		}
	}
}

void rscr_refresh(struct rscr *s, const struct rscr_view *v, rc_ms_t now, struct rscr_fxs *fx)
{
	(void)fx;
	if (s->screen == SCR_NOTIF && notif_index(v, s->notif_uid) < 0) {
		/* the iPhone removed it (a dismiss arrived): back to the list */
		clamp_sel(&s->notif_sel, v->inbox_n);
		show(s, v, SCR_NOTIFS, now);
	}
	clamp_sel(&s->notif_sel, v->inbox_n);
	clamp_sel(&s->dev_sel, rscr_paired_count(v->paired_mask));
	clamp_sel(&s->rec_sel, v->rec_n);
	if ((s->screen == SCR_DEVICE || (s->screen == SCR_CONFIRM && s->confirm_kind == CONFIRM_REMOVE)) &&
	    ((v->paired_mask >> (s->screen == SCR_DEVICE ? s->dev_slot : s->confirm_slot)) & 1U) == 0) {
		show(s, v, SCR_DEVICES, now);
	}
}

rc_ms_t rscr_next_tick(const struct rscr *s)
{
	rc_ms_t t = RC_NO_TICK;
	const rc_ms_t d[] = { s->off_at, s->dim_at, s->msg_until, s->pair_until, s->session_at, s->ilim_until };

	for (unsigned i = 0; i < ARRAY_SIZE(d); i++) {
		t = d[i] < t ? d[i] : t;
	}
	return t;
}

void rscr_tick(struct rscr *s, const struct rscr_view *v, rc_ms_t now, struct rscr_fxs *fx)
{
	bool recording = v->core_state == RC_ST_RECORDING;

	if (s->ilim_until != RC_NO_TICK && now >= s->ilim_until) {
		s->ilim_until = RC_NO_TICK;   /* the 10 s are over; the screen stays as it is until the next input */
	}
	if (s->msg_until != RC_NO_TICK && now >= s->msg_until) {
		uint8_t back = s->msg_back == SCR_OFF || s->msg_back == SCR_MESSAGE ? home_screen(s, v) : s->msg_back;

		s->msg_until = RC_NO_TICK;
		if (s->screen == SCR_MESSAGE) {
			if (recording) {
				back = SCR_RECORDING;
			}
			show(s, v, back, now);
			/* the message was the last thing shown: the panel is not held on by it */
			if (!recording && s->off_at != RC_NO_TICK) {
				s->off_at = now + 1;
			}
		}
	}
	if (s->pair_until != RC_NO_TICK && now >= s->pair_until) {
		leave_pair(s, fx);
		if (s->screen == SCR_PAIR) {
			show(s, v, SCR_MENU, now);
		}
	}
	if (s->session && s->session_at != RC_NO_TICK && now >= s->session_at) {
		close_session(s, v, fx, now);
	}
	if (s->dim_at != RC_NO_TICK && now >= s->dim_at) {
		s->dim_at = RC_NO_TICK;
		if (recording) {
			s->screen = SCR_REC_DIM;
		}
	}
	if (s->off_at != RC_NO_TICK && now >= s->off_at) {
		s->off_at = RC_NO_TICK;
		/* R-SIGN: nothing in RECORDING turns the panel off (the dim timer is the only one armed there) */
		if (!recording) {
			s->screen = SCR_OFF;
		}
	}
}

void rscr_ilim(struct rscr *s, const struct rscr_view *v, rc_ms_t now)
{
	if (ilim_hold(s, now)) {
		return;   /* again while the 10 s run: nothing else changes */
	}
	s->ilim_until = now + RSCR_ILIM_MS;
	s->off_at = s->dim_at = s->msg_until = RC_NO_TICK;
	if (v->core_state == RC_ST_RECORDING) {
		s->screen = SCR_REC_DIM;   /* R-SIGN: dimmed, never dark */
	} else {
		s->screen = SCR_OFF;
	}
}

void rscr_sign_begin(struct rscr *s, rc_ms_t now)
{
	bool hold = ilim_hold(s, now);

	s->screen = hold ? SCR_REC_DIM : SCR_RECORDING;   /* the sign at the start: dimmed in the hold */
	s->rec_start = now;
	s->highlights = 0;
	s->dim_at = hold ? RC_NO_TICK : now + RSCR_DIM_MS;
	s->off_at = RC_NO_TICK;
}

bool rscr_fac_frame(struct rscr *s, const struct rscr_view *v, enum rscr_fac_frame f, rc_ms_t now)
{
	if (v->core_state != RC_ST_FACTORY_TEST || (unsigned)f >= FAC_COUNT) {
		return false;
	}
	s->fac_frame = (uint8_t)f;
	show(s, v, SCR_FACTORY, now);
	return true;
}

void rscr_dev_passkey(struct rscr *s, uint8_t slot, uint32_t passkey)
{
	s->pair_slot = slot;
	s->passkey = passkey % 1000000U;
	s->pair_has_key = true;
}

void rscr_dev_paired(struct rscr *s, const struct rscr_view *v, uint8_t slot, rc_ms_t now)
{
	/* ring_devices makes the new device the active one only when none was (design/firmware.md 3.4, 7.4); this part
	 * changes nothing in the devices */
	s->pair_until = RC_NO_TICK;
	s->pair_slot = RDEV_NONE;
	s->pair_has_key = false;
	if (s->screen == SCR_PAIR) {
		s->dev_sel = 0;
		for (uint8_t i = 0; i < RDEV_SLOTS && i < slot; i++) {
			s->dev_sel += (v->paired_mask >> i) & 1U;
		}
		show(s, v, SCR_DEVICES, now);
	}
}

void rscr_dev_window_closed(struct rscr *s, rc_ms_t now)
{
	struct rscr_view none;

	memset(&none, 0, sizeof(none));
	none.core_state = RC_ST_STANDBY;
	s->pair_until = RC_NO_TICK;
	s->pair_slot = RDEV_NONE;
	s->pair_has_key = false;
	if (s->screen == SCR_PAIR) {
		show(s, &none, SCR_MENU, now);
	}
}

void rscr_dev_removed(struct rscr *s, const struct rscr_view *v, uint8_t slot, bool was_active, rc_ms_t now,
		      struct rscr_fxs *fx)
{
	ARG_UNUSED(slot);
	/* the session closes when the active device is removed */
	if (was_active) {
		close_session(s, v, fx, now);
	}
	rscr_refresh(s, v, now, fx);
}

enum rc_event rscr_row_event(int16_t row)
{
	for (uint16_t i = 0; i < rc_table_rows; i++) {
		if (rc_table[i].row == row) {
			return (enum rc_event)rc_table[i].event;
		}
	}
	return RC_EV_COUNT;
}

/* ---- the panel's turn (design: the picture is 240 x 120, the panel 120 x 240) ---- */

void rscr_to_panel(int x, int y, int *px, int *py)
{
	*px = 119 - y;
	*py = x;
}

void rscr_from_panel(int px, int py, int *x, int *y)
{
	*x = py;
	*y = 119 - px;
}
