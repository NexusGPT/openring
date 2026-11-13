/*
 * Ring devices: the device list and the switch decision. Pure logic: no
 * kernel, driver or Bluetooth call; runs on native_sim with no radio.
 *
 * Three slots. Slot n is local Bluetooth identity n of the ring (one identity
 * per paired device, as nRF Desktop does: ble_bond.rst lines 48, 54, 57-58).
 * A slot is paired when a bond exists for its identity; the Bluetooth part
 * tells this module which slots are paired.
 */
#ifndef RING_DEVICES_RDEV_LOGIC_H
#define RING_DEVICES_RDEV_LOGIC_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RDEV_SLOTS 3
#define RDEV_NONE  0xFF   /* no slot */
#define RDEV_ANY   0xFE   /* a request for any free slot */

struct rdev_list {
	uint8_t paired;  /* bit n set: slot n holds a pairing */
	uint8_t active;  /* the active slot, or RDEV_NONE */
};

void rdev_list_init(struct rdev_list *l);
bool rdev_list_is_paired(const struct rdev_list *l, uint8_t slot);
uint8_t rdev_list_count(const struct rdev_list *l);
/* The lowest empty slot, or RDEV_NONE when all three hold a pairing. */
uint8_t rdev_list_free_slot(const struct rdev_list *l);

/* Slot to use for a new pairing: requested is a slot number or RDEV_ANY.
 * Returns the slot, or a negative errno: -EINVAL out of range, -EEXIST the
 * requested slot is paired (remove it first), -ENOSPC no free slot. */
int rdev_list_choose_pair_slot(const struct rdev_list *l, uint8_t requested);

/* A new pairing was made in the slot: it is paired; it becomes active only when no slot is active.
 * -EINVAL out of range, -EEXIST already paired. */
int rdev_list_add(struct rdev_list *l, uint8_t slot);

/* The pairing of the slot was removed. When it was the active one, the next
 * paired slot after it (in slot order, wrapping) becomes active, or none.
 * -EINVAL out of range, -ENOENT not paired. */
int rdev_list_remove(struct rdev_list *l, uint8_t slot);

/* The paired slot after from, wrapping, other than from; RDEV_NONE if none. */
uint8_t rdev_list_next(const struct rdev_list *l, uint8_t from);

enum rdev_switch {
	RDEV_SWITCH_NOP,           /* the target is already active */
	RDEV_SWITCH_GO,            /* make the target active */
	RDEV_SWITCH_REFUSE_RANGE,  /* no such slot */
	RDEV_SWITCH_REFUSE_EMPTY,  /* the slot holds no pairing */
};
enum rdev_switch rdev_list_decide_switch(const struct rdev_list *l, uint8_t target);
/* Make target active. Returns the decision taken. */
enum rdev_switch rdev_list_switch(struct rdev_list *l, uint8_t target);

/* What the Bluetooth part has to do now. */
struct rdev_state {
	uint8_t active;       /* active slot or RDEV_NONE */
	bool window;          /* the pairing window is open */
	uint8_t window_slot;  /* the slot being paired, valid while window */
	uint8_t link_slot;    /* the identity of the current link, or RDEV_NONE when no link */
};

enum rdev_step {
	RDEV_STEP_IDLE,        /* no link, nothing to advertise */
	RDEV_STEP_STAY,        /* the link is the right one: keep it, no advertising */
	RDEV_STEP_DISCONNECT,  /* the link is the wrong one: end it (then ask again) */
	RDEV_STEP_ADVERTISE,   /* no link: advertise with identity slot */
};

struct rdev_plan {
	uint8_t step;   /* enum rdev_step */
	uint8_t slot;   /* RDEV_STEP_ADVERTISE: the identity to advertise with */
	bool open;      /* RDEV_STEP_ADVERTISE: open to any device (pairing window) */
};

/* The target is the window slot while the window is open, else the active slot. */
struct rdev_plan rdev_plan_next(const struct rdev_state *s);

/* May a key go over this link? Only when the link is encrypted with an authenticated key and
 * belongs to the active device: between a switch and the new link the old device's link is
 * still up and must get nothing. */
bool rdev_link_usable(uint8_t link_slot, bool secure, uint8_t active);

const char *rdev_step_name(enum rdev_step s);

#ifdef __cplusplus
}
#endif

#endif
