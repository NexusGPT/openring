/*
 * Ring glue: the one place where the joystick, the core, the control module and recording meet.
 *
 *   joystick edge -> rglue_input() -> core (gestures, state table) -> actions
 *   actions -> ring_control (keys, only while control is active)
 *          -> the recording hook (every action, in order: RC_ACT_OPEN and RC_ACT_CLOSE start and
 *             stop a recording; the recorder part will act on them)
 *
 * The product application and the two-device tests both use this module. The core decides
 * everything about gestures: a centre hold of 1,000 ms is a long press in every control mode
 * and reaches the hook as RC_ACT_OPEN or RC_ACT_CLOSE; control never sees it as a key.
 * Nothing in the Bluetooth parts calls this module: a host cannot start or stop a recording.
 * When CONFIG_RING_IPHONE is set, rglue_init() also starts the iPhone part (ring_iphone, rip_init()) next to
 * devices and control; that part calls nothing in this module or in the core.
 *
 * THREAD CONTEXT ONLY. rglue_input() must be called from a thread, never from an interrupt
 * handler: it takes a mutex, and while it holds that mutex the core's actions are carried out,
 * which sends Bluetooth reports (bt_hids_inp_rep_send) and may block. The joystick driver
 * must queue the debounced edge from its interrupt and call rglue_input() from a thread.
 *
 * Time is milliseconds from k_uptime_get(). A thread runs the core's deadlines (long press,
 * repeat, double-press window); rglue_input() wakes it.
 */
#ifndef RING_GLUE_RGLUE_H
#define RING_GLUE_RGLUE_H

#include <stdbool.h>
#include <stdint.h>

#include <ring_core/rc_core.h>

#ifdef __cplusplus
extern "C" {
#endif

struct rglue_ops {
	/* Every action the core returns, in order, after control has seen it. Runs in the glue's
	 * thread or in the caller of rglue_input(). Step 6: the recorder (rrec_action) carries out every action here and
	 * may block for the card and the sign (rrec.h). Optional. */
	void (*action)(enum rc_action a, rc_ms_t t);
	/* Step 4 (screens): once per core step, after every action, with the whole list, the event of the last row
	 * (RC_EV_COUNT when none) and the core state after it. The return value is not used: the lock fact comes from
	 * screen_fact below. Optional. */
	bool (*after)(const struct rc_actions *a, enum rc_event last_event, enum rc_state state, rc_ms_t t);
	/* The value of the core fact screen_on now. Called under the glue's lock right before every core call (input, tick,
	 * event); nothing is stored between calls. Optional (NULL leaves the fact alone). */
	bool (*screen_fact)(void);
	/* Step 6 (decision D1): the core's sign hook. rglue_init() passes it to rc_core_set_sign_hook(); the core calls it
	 * under the glue's lock once per long press in STANDBY when the other guards of row 12 hold (0 = the recording sign
	 * is drawn). The product sets rrec_sign_hook. Optional: NULL leaves the core without a hook (the sign counts as
	 * drawn, the test applications of steps 2 to 5). */
	int (*sign_start)(void *ctx, rc_ms_t t);
	/* Step 6 (lead's ruling 5 on the factory unit's gaps): while the core is in FACTORY_TEST the joystick edges go to
	 * the core's own gesture recogniser (no second one) and each gesture event (direction, centre down and up, MW,
	 * long, short, double) is handed here, under the glue's lock, for the factory tests T-JOY and T-CENTRE; the core
	 * has no press row in FACTORY_TEST. Optional: NULL leaves FACTORY_TEST input to the core as before. */
	void (*factory_gesture)(const struct rc_gev *e);
};

/* Start the core in the given state and the tick thread. */
void rglue_init(const struct rglue_ops *ops, enum rc_state start);

/* A debounced joystick edge now. */
void rglue_input(enum rc_switch sw, bool pressed);

/* The core, for facts (screen on) and the state; take care: it is shared with the thread. */
struct rc_core *rglue_core(void);
enum rc_state rglue_state(void);
/* The setter of the core fact screen_on for builds WITHOUT rglue_ops.screen_fact (the step 2 and 3 test apps). When screen_fact is set,
 * the fact is replaced by screen_fact() right before every core call, so a value set here lasts only until the next call. */
void rglue_set_screen_on(bool on);
/* A system event of the core (VBUS, battery events through rc_core_event, the menu's power off): takes the lock,
 * runs the core and carries out the actions like an input does. */
void rglue_event(enum rc_event ev);
/* As rglue_event, but returns -EBUSY at once when the glue's lock is taken (0 when the event was given to the core; an event
 * without a row in the current state is dropped by the core, as for rglue_event). */
int rglue_event_try(enum rc_event ev);
/* Step 6: the battery level (enum rc_batt) from the power part: takes the lock, runs rc_core_battery() (the only way
 * the level enters the core; rc_core_event refuses battery events) and carries out the actions like rglue_event(). */
void rglue_battery(enum rc_batt level);
/* The core fact "Vibration" (setting, FW 2.2) */
void rglue_set_vibration(bool on);

#ifdef __cplusplus
}
#endif

#endif
