/* Ring devices: pure logic (device list, switch decision, plan). */

#include <errno.h>

#include <ring_devices/rdev_logic.h>

void rdev_list_init(struct rdev_list *l)
{
	l->paired = 0;
	l->active = RDEV_NONE;
}

bool rdev_list_is_paired(const struct rdev_list *l, uint8_t slot)
{
	return slot < RDEV_SLOTS && (l->paired & (1U << slot)) != 0;
}

uint8_t rdev_list_count(const struct rdev_list *l)
{
	uint8_t n = 0;

	for (uint8_t i = 0; i < RDEV_SLOTS; i++) {
		n += rdev_list_is_paired(l, i) ? 1 : 0;
	}
	return n;
}

uint8_t rdev_list_free_slot(const struct rdev_list *l)
{
	for (uint8_t i = 0; i < RDEV_SLOTS; i++) {
		if (!rdev_list_is_paired(l, i)) {
			return i;
		}
	}
	return RDEV_NONE;
}

int rdev_list_choose_pair_slot(const struct rdev_list *l, uint8_t requested)
{
	if (requested == RDEV_ANY) {
		uint8_t s = rdev_list_free_slot(l);

		return s == RDEV_NONE ? -ENOSPC : (int)s;
	}
	if (requested >= RDEV_SLOTS) {
		return -EINVAL;
	}
	if (rdev_list_is_paired(l, requested)) {
		return -EEXIST;
	}
	return requested;
}

int rdev_list_add(struct rdev_list *l, uint8_t slot)
{
	if (slot >= RDEV_SLOTS) {
		return -EINVAL;
	}
	if (rdev_list_is_paired(l, slot)) {
		return -EEXIST;
	}
	l->paired |= (uint8_t)(1U << slot);
	/* the new device becomes the active one only when no device is active (design/firmware.md 3.4, 7.4) */
	if (l->active == RDEV_NONE) {
		l->active = slot;
	}
	return 0;
}

uint8_t rdev_list_next(const struct rdev_list *l, uint8_t from)
{
	for (uint8_t k = 1; k <= RDEV_SLOTS; k++) {
		uint8_t s = (uint8_t)((from + k) % RDEV_SLOTS);

		if (s != from && rdev_list_is_paired(l, s)) {
			return s;
		}
	}
	return RDEV_NONE;
}

int rdev_list_remove(struct rdev_list *l, uint8_t slot)
{
	if (slot >= RDEV_SLOTS) {
		return -EINVAL;
	}
	if (!rdev_list_is_paired(l, slot)) {
		return -ENOENT;
	}
	l->paired &= (uint8_t)~(1U << slot);
	if (l->active == slot) {
		l->active = rdev_list_next(l, slot);
	}
	return 0;
}

enum rdev_switch rdev_list_decide_switch(const struct rdev_list *l, uint8_t target)
{
	if (target >= RDEV_SLOTS) {
		return RDEV_SWITCH_REFUSE_RANGE;
	}
	if (!rdev_list_is_paired(l, target)) {
		return RDEV_SWITCH_REFUSE_EMPTY;
	}
	if (l->active == target) {
		return RDEV_SWITCH_NOP;
	}
	return RDEV_SWITCH_GO;
}

enum rdev_switch rdev_list_switch(struct rdev_list *l, uint8_t target)
{
	enum rdev_switch d = rdev_list_decide_switch(l, target);

	if (d == RDEV_SWITCH_GO) {
		l->active = target;
	}
	return d;
}

struct rdev_plan rdev_plan_next(const struct rdev_state *s)
{
	struct rdev_plan p = { RDEV_STEP_IDLE, RDEV_NONE, false };
	uint8_t target = s->window ? s->window_slot : s->active;

	if (target >= RDEV_SLOTS) {
		/* nothing to be connected to: end any link */
		p.step = s->link_slot != RDEV_NONE ? RDEV_STEP_DISCONNECT : RDEV_STEP_IDLE;
		return p;
	}
	if (s->link_slot != RDEV_NONE) {
		p.step = s->link_slot == target ? RDEV_STEP_STAY : RDEV_STEP_DISCONNECT;
		return p;
	}
	p.step = RDEV_STEP_ADVERTISE;
	p.slot = target;
	p.open = s->window;
	return p;
}

const char *rdev_step_name(enum rdev_step s)
{
	switch (s) {
	case RDEV_STEP_IDLE:
		return "idle";
	case RDEV_STEP_STAY:
		return "stay";
	case RDEV_STEP_DISCONNECT:
		return "disconnect";
	case RDEV_STEP_ADVERTISE:
		return "advertise";
	}
	return "?";
}

bool rdev_link_usable(uint8_t link_slot, bool secure, uint8_t active)
{
	return secure && link_slot != RDEV_NONE && link_slot == active;
}
