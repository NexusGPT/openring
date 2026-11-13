/*
 * Ring control: the ring as a Bluetooth keyboard, media remote and pointer
 * (HID over GATT) to the active device. Four modes, each a table in
 * rctl_modes.h.
 *
 * Rules kept (design.md section 2, Apple's rules):
 * - a report is sent only for a joystick action given to rctl_action() or
 *   rctl_core_actions(); nothing else ever sends a key;
 * - every press report is followed by its release report;
 * - reports go only to the active device, over a link that is encrypted with
 *   an authenticated key, and only when that device has switched the report
 *   on (notification subscribed);
 * - nothing here starts or stops a recording; the long press of the centre
 *   is never a control action.
 */
#ifndef RING_CONTROL_RCTL_H
#define RING_CONTROL_RCTL_H

#include <stdbool.h>
#include <stdint.h>

#include <zephyr/kernel.h>
#include <zephyr/bluetooth/conn.h>
#include <ring_core/rc_types.h>
#include "rctl_modes.h"
#include "rctl_report.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Register the HID service. Call before rdev_init() (which enables Bluetooth). */
int rctl_init(void);

void rctl_set_mode(enum rctl_mode mode);
enum rctl_mode rctl_get_mode(void);
void rctl_set_options(const struct rctl_options *opt);

/* Control active: the ring shows a control screen. Only then do joystick actions become
 * keys. Off at start: a menu move never types on the host. The screens part calls this when a
 * control screen opens and closes. (Until it exists, the product application leaves it off and
 * the test application switches it on.) */
void rctl_set_active(bool active);
bool rctl_is_active(void);

/* One joystick action in the current mode. Returns the number of reports
 * sent (0 when the mode sends nothing for it), or a negative errno:
 * -EPERM control is not active, -ENOTCONN no authenticated link (security level 4) to the
 * active device, -EACCES the device has not switched the report on, -EBUSY a release report
 * of the last action is still waiting to be sent, or the error of the send.
 *
 * A press report is always followed by its release. When the release cannot be sent (the
 * send fails), it is retried every RCTL_RETRY_MS up to RCTL_RETRY_MAX times; when the link is
 * gone the host has dropped the key with the link. */
/* RCTL_RETRY_MS and RCTL_RETRY_MAX are in rctl_report.h */
int rctl_action(enum rctl_action action);

/* The actions the core returned for one input or tick: each joystick action of the
 * screen shown goes to rctl_action(); every other action is ignored. Returns the
 * number of reports sent. */
int rctl_core_actions(const struct rc_actions *a);

/* True when the active device has an encrypted link and has switched on all three reports. */
bool rctl_ready(void);

struct rctl_stats {
	uint32_t wire_sends;   /* every call that hands a report to the Bluetooth stack */
	uint32_t host_writes;  /* writes by a host to the HID control point: counted, never acted on */
	uint32_t release_retries; /* release reports sent late, after a failed send */
	uint32_t release_lost; /* releases given up after RCTL_RETRY_MAX tries, or dropped with the link */
	uint32_t actions;      /* actions given */
	uint32_t reports;      /* reports sent */
	uint32_t dropped;      /* actions dropped: no link or report not switched on */
	uint32_t errors;       /* send errors */
};
void rctl_stats_get(struct rctl_stats *s);
/* True while a release report is waiting to be sent. */
bool rctl_release_pending(void);

#if IS_ENABLED(CONFIG_RING_CONTROL_TEST_HOOKS)
/* Test hooks (CONFIG_RING_CONTROL_TEST_HOOKS, off in the product): make the next n sends of a
 * release report fail with -EIO; send a mode and action to a given connection. */
void rctl_test_fail_releases(int n);
int rctl_test_send_to(struct bt_conn *conn, enum rctl_action action);
#endif

#ifdef __cplusplus
}
#endif

#endif
