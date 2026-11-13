/*
 * Ring devices: pairing with a passkey the ring displays, up to three paired
 * devices (one local Bluetooth identity per device), one active device,
 * switching, reconnect, removal. One link at a time: holding two devices at
 * once is out of this step.
 *
 * Init order: rctl_init() (registers the HID service), then rdev_init()
 * (enables Bluetooth, loads bonds, starts advertising to the active device).
 */
#ifndef RING_DEVICES_RDEV_H
#define RING_DEVICES_RDEV_H

#include <stdbool.h>
#include <stdint.h>

#include <zephyr/bluetooth/conn.h>

#include "rdev_logic.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Callbacks, all optional. They run in a Bluetooth or system work thread: do
 * not block in them. The screens part shows the passkey. */
struct rdev_callbacks {
	/* The six digits to show on the ring's screen (passkey 0..999999, show as %06u). */
	void (*passkey_show)(uint8_t slot, uint32_t passkey);
	/* The passkey screen is no longer needed (pairing ended or was cancelled). */
	void (*passkey_hide)(uint8_t slot);
	/* A pairing was made in the slot. The slot becomes the active device only when no device was active
	 * (then active_changed follows); otherwise the active device stays. */
	void (*paired)(uint8_t slot);
	/* Pairing failed; reason is the Bluetooth security error (enum bt_security_err). */
	void (*pairing_failed)(uint8_t slot, int reason);
	/* The pairing window closed without a pairing (time ran out or it was cancelled). */
	void (*window_closed)(void);
	/* The pairing of the slot was removed. */
	void (*removed)(uint8_t slot);
	/* The active device changed (RDEV_NONE if there is none). */
	void (*active_changed)(uint8_t slot);
	/* An encrypted and authenticated link with the slot's device is up or down. */
	void (*link)(uint8_t slot, bool up);
};

/* Enable Bluetooth, create identities 1 and 2 when missing, load the bonds,
 * start advertising to the active device (the first paired slot after a boot).
 * Returns 0 or a negative errno. */
int rdev_init(const struct rdev_callbacks *cb);

/* Open the pairing window for 'timeout_ms' (the product uses RDEV_PAIR_WINDOW_MS):
 * slot is 0..2 or RDEV_ANY for the lowest free slot. The link to the active
 * device ends, the ring advertises on the slot's identity, open to any device.
 * When a device pairs in time its slot becomes the active one only if no device is active (else the active device stays and its link comes back); otherwise the
 * ring returns to the previous active device.
 * -ENOSPC all slots are paired, -EEXIST the slot is paired, -EINVAL. */
int rdev_pair_open(uint8_t slot, uint32_t timeout_ms);
void rdev_pair_cancel(void);
bool rdev_pair_window_open(void);

/* Make a paired slot the active device: the link ends, the identity changes,
 * the ring advertises to the chosen device. 0, or -ENOENT for an empty slot,
 * -EINVAL for a slot out of range. Switching to the active slot does nothing. */
int rdev_switch(uint8_t slot);
/* Switch to the next paired slot. -ENOENT when there is no other. */
int rdev_switch_next(void);

/* Remove the pairing of a slot: the link ends when it is the slot's, both key
 * sets of the pairing are deleted, the slot is free. If it was active the next
 * paired slot becomes active. 0, -ENOENT, -EINVAL. */
int rdev_remove(uint8_t slot);

uint8_t rdev_active(void);        /* RDEV_NONE if none */
uint8_t rdev_paired_mask(void);   /* bit n: slot n holds a pairing */
bool rdev_link_up(void);          /* a link to the active device, encrypted with an authenticated key */

/* The connection to the active device when it is encrypted and authenticated
 * (security level 4); the caller releases it with bt_conn_unref().
 * NULL otherwise. */
struct bt_conn *rdev_active_conn(void);

/* The peer address of a slot's pairing; -ENOENT when the slot is empty. */
int rdev_slot_peer(uint8_t slot, bt_addr_le_t *addr);

/* Ship mode step 1 (design/firmware.md l.937, "close ... radio"; added in step 6 fix round 1, review finding R6-02):
 * stop this part's advertising, end the link, and never advertise again until the next boot. Other advertising (the
 * factory ship beacon) is not touched. 0, or the error of bt_conn_disconnect(). Any thread; does not wait for the
 * link to end. */
int rdev_stop(void);

#define RDEV_PAIR_WINDOW_MS 60000   /* FW 7.4: SCR_PAIR open for 60 s */

#ifdef __cplusplus
}
#endif

#endif
