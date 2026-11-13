/*
 * Ring core: joystick key layer (FW 2.2) and centre gesture recogniser (FW 2.1).
 * Input: debounced switch edges with their time in ms (the 20 ms debounce is
 * done by gpio-keys before this module). Output: gesture events.
 */
#ifndef RING_CORE_RC_GESTURE_H
#define RING_CORE_RC_GESTURE_H

#include "rc_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* FW 2.1 parameter table and FW 2.2 */
#define RC_LONG_MS            1000  /* long press */
#define RC_WARN_MS            500   /* warning pulse MW */
#define RC_SHORT_MIN_MS       40    /* under this: graze */
#define RC_SHORT_MAX_MS       450   /* short press ceiling, included */
#define RC_DOUBLE_WINDOW_MS   400   /* window after a release, included */
#define RC_DOUBLE_GAP_MIN_MS  60    /* minimum gap of a double press */
#define RC_DIR_WINDOW_MS      40    /* direction decision window */
#define RC_RELEASE_HOLDOFF_MS 30    /* centre release hold-off */
#define RC_REPEAT_DELAY_MS    500   /* a direction held 500 ms repeats */
#define RC_REPEAT_PERIOD_MS   150   /* every 150 ms */

/* Switches, FW 2.2 */
enum rc_switch {
	RC_SW_UP,     /* SW1 JOY_UP */
	RC_SW_CENTRE, /* SW2 BTN_REC, used only with RC_CENTRE_SW2 */
	RC_SW_DOWN,   /* SW3 JOY_DOWN */
	RC_SW_LEFT,   /* SW4 JOY_LEFT, toward the hand */
	RC_SW_RIGHT,  /* SW5 JOY_RIGHT, toward the fingertip */
	RC_SW_COUNT
};

/* Build constant CENTRE_SOURCE, FW 2.1 */
enum rc_centre_source {
	RC_CENTRE_SW2,
	RC_CENTRE_PAIR
};

enum rc_gev_type {
	RC_GEV_DIR,         /* a direction event (dir), first or repeat */
	RC_GEV_CENTRE_DOWN, /* key layer output, for information */
	RC_GEV_CENTRE_UP,   /* key layer output, stamped at the release instant */
	RC_GEV_WARN,        /* 500 ms of a continuous centre hold: MW */
	RC_GEV_LONG,        /* 1,000 ms: fires once while held */
	RC_GEV_SHORT,       /* fires when the double-press window closes */
	RC_GEV_DOUBLE       /* second short press 60 to 400 ms after the first release */
};

struct rc_gev {
	uint8_t type;       /* enum rc_gev_type */
	uint8_t dir;        /* enum rc_switch for RC_GEV_DIR */
	bool repeat;        /* RC_GEV_DIR: true for a repeat */
	rc_ms_t t;          /* time the event happened */
	rc_ms_t t_down;     /* RC_GEV_SHORT, RC_GEV_LONG: time of CENTRE_DOWN */
};

#define RC_MAX_GEV 16
struct rc_gev_list {
	uint8_t n;
	struct rc_gev e[RC_MAX_GEV];
};

enum rc_key_state { RC_K_IDLE, RC_K_DIR_WINDOW, RC_K_DIR_SENT, RC_K_CENTRE, RC_K_IGNORE };

struct rc_gesture {
	uint8_t src;          /* enum rc_centre_source */
	uint8_t held;         /* bit per enum rc_switch, closed switches */
	uint8_t kstate;       /* enum rc_key_state */
	uint8_t dir;          /* first direction switch of the window */
	rc_ms_t dir_t0;
	rc_ms_t next_repeat;
	bool rel_pending;     /* centre release hold-off running */
	rc_ms_t rel_t;
	/* gesture layer */
	bool pressing;
	rc_ms_t down_t;
	bool warned;
	bool long_fired;
	bool cancelled;       /* ruling R7: this hold was cancelled by a change of state */
	bool second;          /* this press began 60 to 400 ms after a short press */
	bool short_pending;
	rc_ms_t short_down_t;
	rc_ms_t short_up_t;
};

void rc_gesture_init(struct rc_gesture *g, enum rc_centre_source src);
/* A debounced edge of one switch at time t. */
void rc_gesture_input(struct rc_gesture *g, enum rc_switch sw, bool pressed, rc_ms_t t, struct rc_gev_list *out);
/* Run every deadline at or before now. */
void rc_gesture_tick(struct rc_gesture *g, rc_ms_t now, struct rc_gev_list *out);
/* Ruling R7: cancel the centre hold in progress (no MW, no long, no short, no double
 * from it); the wearer must release and press again. No effect when no hold is in progress. */
void rc_gesture_cancel_hold(struct rc_gesture *g);
/* Time of the next deadline, RC_NO_TICK if none. */
rc_ms_t rc_gesture_next_tick(const struct rc_gesture *g);

#ifdef __cplusplus
}
#endif

#endif
