/*
 * Ring control: HID report map, report builder, mode state and the link from
 * the core's actions. Pure logic: runs on native_sim with no radio.
 */
#ifndef RING_CONTROL_RCTL_REPORT_H
#define RING_CONTROL_RCTL_REPORT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "rctl_modes.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Report IDs in the report map, and the index of each input report in the HID service. */
#define RCTL_RID_KEYBOARD 1
#define RCTL_RID_CONSUMER 2
#define RCTL_RID_POINTER  3
#define RCTL_IDX_KEYBOARD 0
#define RCTL_IDX_CONSUMER 1
#define RCTL_IDX_POINTER  2
#define RCTL_REPORT_COUNT 3

/* Report sizes in bytes, without the report ID.
 * keyboard: modifiers, reserved, six key codes.
 * consumer: one 16-bit usage, 0 = released.
 * pointer: button bits (bit 0 = button 1), dx, dy (signed 8 bit). */
#define RCTL_LEN_KEYBOARD 8
#define RCTL_LEN_CONSUMER 2
#define RCTL_LEN_POINTER  3

extern const uint8_t rctl_report_map[];
extern const size_t rctl_report_map_len;

struct rctl_report {
	uint8_t index;   /* RCTL_IDX_* */
	uint8_t id;      /* RCTL_RID_* */
	uint8_t len;
	uint8_t data[RCTL_LEN_KEYBOARD];
};

/* An action sends at most two reports: down and release. */
#define RCTL_MAX_REPORTS 2

/* Mode options */
struct rctl_options {
	bool presenter_pages; /* presenter uses Page Up and Page Down instead of the arrows */
};

/* The table entry of a mode and action; NULL for a value out of range. */
const struct rctl_entry *rctl_lookup(enum rctl_mode mode, enum rctl_action action,
				     const struct rctl_options *opt);

/*
 * Build the reports of one joystick action. Returns the number of reports
 * (0, 1 or 2) written to out. Every report that presses is followed by its
 * release report. Returns 0 for an entry that sends nothing and for a value
 * out of range.
 */
size_t rctl_build(enum rctl_mode mode, enum rctl_action action,
		  const struct rctl_options *opt, struct rctl_report out[RCTL_MAX_REPORTS]);

/* The core's actions. rc_action is a value of enum rc_action (ring_core/rc_types.h).
 * Returns true and sets *out only for the five joystick actions of the screen
 * shown (RC_ACT_SCREEN_CENTRE, _UP, _DOWN, _LEFT, _RIGHT). Every other action
 * returns false: nothing else ever produces a key (Apple's rule). */
bool rctl_from_core(uint8_t rc_action, enum rctl_action *out);

/* The gate between the core and the keys: a core action becomes a joystick action only when
 * control is active (the ring shows a control screen) and the action is one of the five of
 * rctl_from_core(). With control not active nothing is ever typed on the host: menu moves stay
 * on the ring. */
bool rctl_core_filter(bool control_active, uint8_t rc_action, enum rctl_action *out);

/*
 * The release wait. When the release report of a key cannot be sent, the ring keeps it and retries
 * (RCTL_RETRY_MS, RCTL_RETRY_MAX tries). While it waits, the wearer's next action is refused
 * (-EBUSY), so a new press never goes out before the old key is up: at most 20 x 50 ms = 1 s.
 * This is a design choice: it keeps the host's key state right. Pure logic.
 */
#define RCTL_RETRY_MS  50
#define RCTL_RETRY_MAX 20
struct rctl_wait {
	int npend;  /* releases waiting */
	int tries;  /* retries done */
};
enum rctl_retry { RCTL_RETRY_AGAIN, RCTL_RETRY_GIVE_UP, RCTL_RETRY_DONE };
void rctl_wait_start(struct rctl_wait *w, int n);
bool rctl_wait_admit(const struct rctl_wait *w);          /* may a new action go out? */
void rctl_wait_released(struct rctl_wait *w, int n);      /* n waiting releases were sent */
enum rctl_retry rctl_wait_retry(struct rctl_wait *w);     /* after a retry round: again, give up, done */

/* The next mode in the order media, presenter, pointer, agent, media. */
enum rctl_mode rctl_mode_next(enum rctl_mode mode);

const char *rctl_mode_name(enum rctl_mode mode);
const char *rctl_action_name(enum rctl_action action);

#ifdef __cplusplus
}
#endif

#endif
