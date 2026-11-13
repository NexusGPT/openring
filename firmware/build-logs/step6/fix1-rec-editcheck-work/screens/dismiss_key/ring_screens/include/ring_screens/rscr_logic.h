/*
 * Ring screens, pure part: which screen is shown for which state and input. No kernel, driver,
 * graphics or Bluetooth call: runs on native_sim and on the simulated chip with no display.
 *
 * Source of the rules: design/firmware.md 1.1 (screen column), 2.2 (the joystick per screen, the
 * lock), 3.2 (R-SIGN), 3.3 (screens), 3.4 (control session, devices, pairing). The inputs are what
 * the core returns for one joystick edge or tick (its action list and the event of its last row):
 * the core already applies the lock and the gestures; this part decides the screen.
 *
 * The lock and the control session: the core reads one fact, facts.screen_on. rscr_lock_fact() is
 * the value to store there: true when the screen is fully lit (not off, not the dimmed SCR_REC_DIM)
 * or a control session is open (design/firmware.md 3.4: the lock does not apply in a session).
 */
#ifndef RING_SCREENS_RSCR_LOGIC_H
#define RING_SCREENS_RSCR_LOGIC_H

#include <stdbool.h>
#include <stdint.h>
#include <ring_core/rc_types.h>
#include <ring_control/rctl_modes.h>
#include <ring_inbox/rinbox.h>
#include <ring_devices/rdev_logic.h>
#include <ring_rhw/rrec_spec.h>   /* the 10 s of the current limit (RREC_ILIM_SCREEN_MS): defined once, there */

#ifdef __cplusplus
extern "C" {
#endif

/* Screens of design/firmware.md 3.3, plus SCR_NOTIFS and SCR_NOTIF (software step 4: the list and the
 * detail of the inbox) and SCR_OFF (the panel is off). */
enum rscr_screen {
	SCR_OFF,
	SCR_STATUS,
	SCR_RECORDING,
	SCR_REC_DIM,
	SCR_MENU,
	SCR_RECORDINGS,
	SCR_RECORDING_INFO,
	SCR_SETTINGS,
	SCR_CONFIRM,
	SCR_PAIR,
	SCR_MODES,
	SCR_CONTROL,
	SCR_DEVICES,
	SCR_DEVICE,
	SCR_MESSAGE,
	SCR_CHARGING,
	SCR_TRANSFER,
	SCR_ERROR,
	SCR_RECOVERY,
	SCR_FACTORY,
	SCR_NOTIFS,
	SCR_NOTIF,
	SCR_COUNT
};

/* The frames of the factory test T-SCREEN (design/firmware.md 9.3, sub-command 0x20): drawn only in FACTORY_TEST (software step 6) */
enum rscr_fac_frame {
	FAC_NONE,    /* the plain SCR_FACTORY screen */
	FAC_RED, FAC_GREEN, FAC_BLUE, FAC_WHITE, FAC_BLACK,   /* the whole 240 x 120 frame in one colour */
	FAC_GRID,    /* one pixel lines every 20 pixels, the first and the last row and column included, on black */
	FAC_COUNT
};

/* The six menu items, in the order of design/firmware.md 2.2 */
enum rscr_menu_item {
	MENU_RECORDINGS, MENU_CONTROL, MENU_DEVICES, MENU_PAIR, MENU_SETTINGS, MENU_POWER_OFF, MENU_COUNT
};
enum rscr_setting { SET_BRIGHTNESS, SET_VIBRATION, SET_TIME_FORMAT, SET_ABOUT, SET_COUNT };
enum rscr_msg { MSG_BATTERY_LOW, MSG_STORAGE_FULL, MSG_30_MIN, MSG_IN_CASE, MSG_REMOVE_FIRST, MSG_COUNT };
enum rscr_confirm { CONFIRM_POWER_OFF, CONFIRM_REMOVE };
enum rscr_dev_item { DEV_USE, DEV_REMOVE, DEV_ITEM_COUNT };

/* Times, design/firmware.md 1.1, 2.2, 3.2, 3.4, 7.4 */
#define RSCR_OFF_MS        5000     /* the screen turns off 5 s after the last input */
#define RSCR_DIM_MS        3000     /* RECORDING: SCR_REC_DIM 3 s after the last input */
#define RSCR_MSG_MS        3000     /* SCR_MESSAGE */
#define RSCR_PAIR_MS       60000    /* SCR_PAIR */
#define RSCR_SESSION_MS    1800000  /* control session closes after 30 minutes with no joystick action */
#define RSCR_ERR_STORAGE_MS 10000   /* error screens: storage fault, charger 10 s, microphone 5 s */
#define RSCR_ERR_MIC_MS     5000
#define RSCR_CHARGING_MS   5000
#define RSCR_ILIM_MS       RREC_ILIM_SCREEN_MS   /* design/firmware.md 8.7: current limit active, 10 s (software step 6) */

/* Joystick directions as the core's screen actions */
enum rscr_dir { DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_CENTRE };

/* What the caller must do after a step (it carries them out in order). */
enum rscr_fx_kind {
	FX_NONE,
	FX_CONTROL_ACTIVE,   /* a = 0/1: rctl_set_active */
	FX_SET_MODE,         /* a = enum rctl_mode: rctl_set_mode */
	FX_PAIR_OPEN,        /* a = slot: rdev_pair_open(slot, RDEV_PAIR_WINDOW_MS) */
	FX_PAIR_CANCEL,      /* rdev_pair_cancel */
	FX_DEV_USE,          /* a = slot: rdev_switch */
	FX_DEV_REMOVE,       /* a = slot: rdev_remove */
	FX_NOTIF_DISMISS,    /* u = uid: rip_dismiss (the negative action) */
	FX_NOTIF_POSITIVE,   /* u = uid: rip_action(uid, positive) */
	FX_NOTIF_READ,       /* u = uid: rip_inbox_mark_read */
	FX_POWER_OFF,        /* the core event RC_EV_MENU_POWER_OFF */
	FX_VIBRATION,        /* a = 0/1: the core fact vibration_on */
	FX_BRIGHTNESS        /* a = 0..2 */
};
struct rscr_fx {
	uint8_t kind;
	uint8_t a;
	uint32_t u;
};
#define RSCR_MAX_FX 8
struct rscr_fxs {
	uint8_t n;
	struct rscr_fx e[RSCR_MAX_FX];
};

/* The facts of other modules, copied by the caller before each step. */
struct rscr_view {
	uint8_t core_state;                 /* enum rc_state */
	uint8_t paired_mask;                /* ring_devices: bit n = slot n paired */
	uint8_t active_slot;                /* RDEV_NONE if none */
	bool link_up;                       /* level 4 link to the active device */
	uint8_t inbox_n;                    /* ring_inbox: count */
	uint32_t inbox_uid[RINBOX_MAX];
	uint8_t inbox_flags[RINBOX_MAX];
	uint8_t rec_n;                      /* recordings stored (0 until the recorder exists) */
};

struct rscr {
	uint8_t screen;       /* enum rscr_screen; SCR_OFF = panel off */
	uint8_t seen_state;   /* the core state of the last step */
	uint8_t menu_sel, rec_sel, set_sel, mode_sel, dev_sel, dev_item, notif_sel;
	uint32_t notif_uid;
	uint8_t confirm_kind, confirm_slot, msg, msg_back;
	uint8_t dev_slot;     /* the slot SCR_DEVICE is about */
	uint8_t pair_slot;
	bool pair_has_key;
	uint32_t passkey;
	bool session;         /* a control session is open (design/firmware.md 3.4) */
	uint8_t mode;         /* enum rctl_mode of the open session */
	uint8_t last_mode;    /* the last used mode (Media the first time) */
	uint8_t brightness;   /* 0..2, "Screen brightness" */
	bool vibration;
	bool fmt12;
	uint16_t highlights;
	uint8_t fac_frame;    /* enum rscr_fac_frame; drawn on SCR_FACTORY; FAC_NONE outside FACTORY_TEST */
	rc_ms_t ilim_until;   /* current limit active: the screen is held off (SCR_REC_DIM in RECORDING) until then; RC_NO_TICK when not */
	rc_ms_t rec_start;
	rc_ms_t off_at, dim_at, msg_until, pair_until, session_at;  /* RC_NO_TICK when not armed */
};

void rscr_init(struct rscr *s);
const char *rscr_screen_name(enum rscr_screen sc);
const char *rscr_menu_name(enum rscr_menu_item i);
const char *rscr_msg_text(enum rscr_msg m);

#define RSCR_LEVEL_LOWEST 85
#define RSCR_LEVEL_STEP   85
#define RSCR_B15_MSG_MS   5000   /* "Battery low" at B15 in STANDBY */

/* "Power off" only in STANDBY: 6 items there, 5 in every other state */
uint8_t rscr_menu_count(enum rc_state st);
/* The panel brightness (0..255) for the screen shown: the setting's level, SCR_REC_DIM the lowest level */
uint8_t rscr_brightness_level(const struct rscr *s);

/* The core fact screen_on (see the header comment). */
bool rscr_lock_fact(const struct rscr *s);
/* R-SIGN: in RECORDING the panel is lit and shows the red dot and the timer (SCR_RECORDING, SCR_REC_DIM, or a message
 * with the sign drawn in its corner). True in every other core state (the rule does not apply). */
bool rscr_sign_ok(const struct rscr *s, enum rc_state core_state);
/* The screen shown is drawn with the red dot and the timer (RECORDING screens and a message during RECORDING). */
bool rscr_has_sign(const struct rscr *s, enum rc_state core_state);

/* One core step: the action list, the event of its last row (RC_EV_COUNT when none) and the core state after it. */
void rscr_on_core(struct rscr *s, const struct rscr_view *v, const struct rc_actions *a, enum rc_event last_event,
		  rc_ms_t now, struct rscr_fxs *fx);
/* Deadlines (off, dim, message, pairing window, session idle). */
void rscr_tick(struct rscr *s, const struct rscr_view *v, rc_ms_t now, struct rscr_fxs *fx);
rc_ms_t rscr_next_tick(const struct rscr *s);
/* The inbox or the device list changed: leave a screen about something that is gone. */
void rscr_refresh(struct rscr *s, const struct rscr_view *v, rc_ms_t now, struct rscr_fxs *fx);

/* The nPM1304's current limit reads ACTIVE (design/firmware.md 8.7): the screen goes off at once and stays off for RSCR_ILIM_MS
 * (an input does not light it in that time); in RECORDING it shows SCR_REC_DIM for those 10 s instead, at the lowest level, never
 * dark (R-SIGN), and an input does not raise it to SCR_RECORDING. Called again while the 10 s run: nothing changes (the time is
 * not extended). When the 10 s end the screen stays as it is (off, or SCR_REC_DIM) until the next input or state change. */
void rscr_ilim(struct rscr *s, const struct rscr_view *v, rc_ms_t now);
/* The recording sign starts (rscr_sign_start): SCR_RECORDING at 00:00:00, dimming after RSCR_DIM_MS; while the current limit holds the screen
 * down (rscr_ilim) the sign is SCR_REC_DIM instead (panel level 85), with no timer to dim, and the screen follows the normal rules when
 * the hold ends. Never dark (R-SIGN). */
void rscr_sign_begin(struct rscr *s, rc_ms_t now);
/* The factory test T-SCREEN shows frame f (FAC_NONE returns to the plain SCR_FACTORY). True when accepted; false (nothing
 * changed) when the core state is not FACTORY_TEST or f is not one of the enum values. The frame is dropped when the state
 * is left. */
bool rscr_fac_frame(struct rscr *s, const struct rscr_view *v, enum rscr_fac_frame f, rc_ms_t now);

/* ring_devices callbacks */
void rscr_dev_passkey(struct rscr *s, uint8_t slot, uint32_t passkey);
void rscr_dev_paired(struct rscr *s, const struct rscr_view *v, uint8_t slot, rc_ms_t now);
void rscr_dev_window_closed(struct rscr *s, rc_ms_t now);
void rscr_dev_removed(struct rscr *s, const struct rscr_view *v, uint8_t slot, bool was_active, rc_ms_t now,
		      struct rscr_fxs *fx);

/* The slot of the idx-th paired device in slot order, RDEV_NONE if out of range */
uint8_t rscr_paired_slot(uint8_t paired_mask, uint8_t idx);
uint8_t rscr_paired_count(uint8_t paired_mask);

/* The event of a row of the core's table (rc_actions.last_row, 1 = first row): RC_EV_COUNT when row < 1 or unknown. */
enum rc_event rscr_row_event(int16_t row);

/* The panel's turn: logical (x, y) of the 240 x 120 frame to the panel's (px, py) of 120 x 240, and back. One
 * quarter turn clockwise: the top left of the frame goes to the top right of the panel. */
void rscr_to_panel(int x, int y, int *px, int *py);
void rscr_from_panel(int px, int py, int *x, int *y);

#ifdef __cplusplus
}
#endif

#endif
