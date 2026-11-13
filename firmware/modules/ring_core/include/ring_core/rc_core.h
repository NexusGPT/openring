/*
 * Ring core: dispatcher. Feeds switch edges (through the gesture recogniser)
 * and system events into the state machine and returns the action list.
 */
#ifndef RING_CORE_RC_CORE_H
#define RING_CORE_RC_CORE_H

#include "rc_types.h"
#include "rc_sm.h"
#include "rc_gesture.h"

#ifdef __cplusplus
extern "C" {
#endif

#define RC_MIC_FAULT_MS      5000   /* ERR_MIC_FAULT: "5 s elapsed" (row 59) */
#define RC_STORAGE_RETRY_MS  60000  /* ERR_STORAGE_FAULT: "60 s elapsed", every 60 s (row 55, ruling R3) */

/* The sign hook (step 6, rule R-SIGN of FW 3.2, row 16 of FW 1.2). Called by the core as fn(ctx, t) once per long
 * press, only in STANDBY and only when the other guards of row 12 hold (open flag clear, battery above B5, free
 * space above SFULL), before the row is chosen. 0 means the recording sign is drawn: row 12. Any other value means
 * it is not drawn: row 16 (no recording, M3, event log record). With no hook set the sign counts as drawn. */
typedef int (*rc_sign_hook_fn)(void *ctx, rc_ms_t t);

struct rc_core {
	struct rc_sm sm;
	struct rc_gesture g;
	struct rc_facts facts;
	rc_ms_t entered_ms;       /* time the current state was entered */
	rc_ms_t timer_next;       /* next 5 s (ERR_MIC_FAULT) or 60 s (ERR_STORAGE_FAULT, repeating) mark */
	bool mic_rail;            /* the microphone rail as requested by the actions so far */
	rc_sign_hook_fn sign_fn;  /* NULL: the sign counts as drawn */
	void *sign_ctx;
};

/* start is BOOT for a normal power-on. vibration_on starts true (FW 2.2). */
void rc_core_init(struct rc_core *c, enum rc_centre_source src, enum rc_state start, rc_ms_t now);
/* Sets or clears (fn NULL) the sign hook; call it after rc_core_init, which clears it. */
void rc_core_set_sign_hook(struct rc_core *c, rc_sign_hook_fn fn, void *ctx);
/* A debounced switch edge. */
void rc_core_input(struct rc_core *c, enum rc_switch sw, bool pressed, rc_ms_t t, struct rc_actions *out);
/* A system event (VBUS, USB, battery, storage, faults, commands). The press
 * events (LONG, SHORT, DOUBLE) and the timers are refused here: they come only
 * from rc_core_input and rc_core_tick. */
void rc_core_event(struct rc_core *c, enum rc_event ev, rc_ms_t t, struct rc_actions *out);
/* Battery level (ruling C1). Called by the power part (fuel gauge sampling, FW 8.3) after
 * every sample whose level differs from the last one reported: OK, B15, B5 or B2, in both
 * directions. A downward crossing runs the row of the threshold reached ("battery reaches ...");
 * an upward crossing, after a charge, only updates the fact the guards read. In BOOT the level is
 * only kept; the order at "init done" decides (ruling R12). This is the only
 * way to change the battery fact; rc_core_event refuses the battery events. */
void rc_core_battery(struct rc_core *c, enum rc_batt level, rc_ms_t t, struct rc_actions *out);
/* Storage: RC_ACT_RETRY_STORAGE asks the caller to run the storage init; it answers with
 * RC_EV_STORAGE_RETRY_OK or RC_EV_STORAGE_RETRY_FAILED through rc_core_event (ruling R3).
 * The fact storage_full is set by RC_EV_STORAGE_SFULL and cleared by the caller (rc_core_facts)
 * when space is freed. The fact storage_fault (ruling R11) is set on entering ERR_STORAGE_FAULT and
 * cleared by INIT_DONE or RC_EV_STORAGE_RETRY_OK; at most one retry per tick call (ruling R14). */
/* Timeouts: call at or after rc_core_next_tick(). Events with the same time as a deadline go first. */
void rc_core_tick(struct rc_core *c, rc_ms_t now, struct rc_actions *out);
rc_ms_t rc_core_next_tick(const struct rc_core *c);

enum rc_state rc_core_state(const struct rc_core *c);
struct rc_facts *rc_core_facts(struct rc_core *c);
/* The microphone rail as requested so far: on after OPEN, off after CLOSE, MIC_OFF or a reset into BOOT. */
bool rc_core_mic_rail(const struct rc_core *c);

#ifdef __cplusplus
}
#endif

#endif
