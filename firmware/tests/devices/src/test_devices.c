/* ring_devices logic tests (native_sim, no radio): device list, switch decision, plan. */

#include <errno.h>

#include <zephyr/ztest.h>

#include <ring_devices/rdev_logic.h>

ZTEST(ring_devices, test_three_slots)
{
	struct rdev_list l;

	zassert_equal(RDEV_SLOTS, 3, "up to three paired devices");
	rdev_list_init(&l);
	zassert_equal(l.active, RDEV_NONE);
	zassert_equal(rdev_list_count(&l), 0);
	zassert_equal(rdev_list_free_slot(&l), 0);
	zassert_equal(rdev_list_add(&l, 0), 0);
	zassert_equal(rdev_list_add(&l, 1), 0);
	zassert_equal(rdev_list_add(&l, 2), 0);
	zassert_equal(rdev_list_count(&l), 3);
	zassert_equal(rdev_list_free_slot(&l), RDEV_NONE, "no fourth device");
	zassert_equal(rdev_list_choose_pair_slot(&l, RDEV_ANY), -ENOSPC, "a fourth pairing is refused");
	zassert_equal(rdev_list_add(&l, 1), -EEXIST);
	zassert_equal(rdev_list_add(&l, 3), -EINVAL);
}

ZTEST(ring_devices, test_new_pairing_becomes_active_only_when_none_is_active)
{
	struct rdev_list l;

	rdev_list_init(&l);
	zassert_equal(rdev_list_add(&l, 0), 0);
	zassert_equal(l.active, 0, "the first device paired is active");
	zassert_equal(rdev_list_add(&l, 1), 0);
	zassert_equal(l.active, 0, "a later device does not take over");
	zassert_equal(rdev_list_add(&l, 2), 0);
	zassert_equal(l.active, 0, "nor the third");
	zassert_equal(rdev_list_remove(&l, 0), 0);
	zassert_equal(l.active, 1, "the active one removed: the next paired slot");
	zassert_equal(rdev_list_remove(&l, 1), 0);
	zassert_equal(rdev_list_remove(&l, 2), 0);
	zassert_equal(l.active, RDEV_NONE);
	zassert_equal(rdev_list_add(&l, 2), 0);
	zassert_equal(l.active, 2, "with no active device the new one becomes active");
}

ZTEST(ring_devices, test_choose_pair_slot)
{
	struct rdev_list l;

	rdev_list_init(&l);
	zassert_equal(rdev_list_choose_pair_slot(&l, RDEV_ANY), 0);
	rdev_list_add(&l, 0);
	rdev_list_add(&l, 2);
	zassert_equal(rdev_list_choose_pair_slot(&l, RDEV_ANY), 1, "lowest free slot");
	zassert_equal(rdev_list_choose_pair_slot(&l, 1), 1);
	zassert_equal(rdev_list_choose_pair_slot(&l, 2), -EEXIST, "remove it first");
	zassert_equal(rdev_list_choose_pair_slot(&l, 3), -EINVAL);
	zassert_equal(rdev_list_choose_pair_slot(&l, RDEV_NONE), -EINVAL);
}

ZTEST(ring_devices, test_remove_and_active)
{
	struct rdev_list l;

	rdev_list_init(&l);
	rdev_list_add(&l, 0);
	rdev_list_add(&l, 1);
	rdev_list_add(&l, 2);
	zassert_equal(l.active, 0, "the first device stays active (a later pairing does not take over)");
	zassert_equal(rdev_list_switch(&l, 2), RDEV_SWITCH_GO);
	zassert_equal(l.active, 2);
	zassert_equal(rdev_list_remove(&l, 0), 0);
	zassert_equal(l.active, 2, "removing another slot keeps the active one");
	zassert_false(rdev_list_is_paired(&l, 0));
	zassert_equal(rdev_list_remove(&l, 0), -ENOENT);
	zassert_equal(rdev_list_remove(&l, 3), -EINVAL);
	zassert_equal(rdev_list_remove(&l, 2), 0);
	zassert_equal(l.active, 1, "active removed: the next paired slot");
	zassert_equal(rdev_list_remove(&l, 1), 0);
	zassert_equal(l.active, RDEV_NONE, "none left");
	zassert_equal(rdev_list_count(&l), 0);
	zassert_equal(rdev_list_free_slot(&l), 0);
}

ZTEST(ring_devices, test_next_wraps)
{
	struct rdev_list l;

	rdev_list_init(&l);
	zassert_equal(rdev_list_next(&l, 0), RDEV_NONE);
	rdev_list_add(&l, 0);
	zassert_equal(rdev_list_next(&l, 0), RDEV_NONE, "only itself");
	rdev_list_add(&l, 2);
	zassert_equal(rdev_list_next(&l, 0), 2);
	zassert_equal(rdev_list_next(&l, 2), 0, "wraps");
	zassert_equal(rdev_list_next(&l, 1), 2);
}

ZTEST(ring_devices, test_switch_decision)
{
	struct rdev_list l;

	rdev_list_init(&l);
	rdev_list_add(&l, 0);
	rdev_list_add(&l, 1);
	zassert_equal(l.active, 0);
	zassert_equal(rdev_list_switch(&l, 1), RDEV_SWITCH_GO);
	zassert_equal(l.active, 1);
	zassert_equal(rdev_list_decide_switch(&l, 1), RDEV_SWITCH_NOP);
	zassert_equal(rdev_list_decide_switch(&l, 0), RDEV_SWITCH_GO);
	zassert_equal(rdev_list_decide_switch(&l, 2), RDEV_SWITCH_REFUSE_EMPTY);
	zassert_equal(rdev_list_decide_switch(&l, 3), RDEV_SWITCH_REFUSE_RANGE);
	zassert_equal(rdev_list_decide_switch(&l, RDEV_NONE), RDEV_SWITCH_REFUSE_RANGE);
	zassert_equal(l.active, 1, "deciding changes nothing");
	zassert_equal(rdev_list_switch(&l, 2), RDEV_SWITCH_REFUSE_EMPTY);
	zassert_equal(l.active, 1, "a refused switch changes nothing");
	zassert_equal(rdev_list_switch(&l, 0), RDEV_SWITCH_GO);
	zassert_equal(l.active, 0);
	zassert_equal(rdev_list_switch(&l, 0), RDEV_SWITCH_NOP);
}

static struct rdev_plan plan(uint8_t active, bool window, uint8_t wslot, uint8_t link)
{
	struct rdev_state s = { .active = active, .window = window, .window_slot = wslot, .link_slot = link };

	return rdev_plan_next(&s);
}

ZTEST(ring_devices, test_plan)
{
	struct rdev_plan p;

	/* no device, no window, no link: nothing */
	p = plan(RDEV_NONE, false, RDEV_NONE, RDEV_NONE);
	zassert_equal(p.step, RDEV_STEP_IDLE);
	/* an active device and no link: advertise to it, not open */
	p = plan(1, false, RDEV_NONE, RDEV_NONE);
	zassert_equal(p.step, RDEV_STEP_ADVERTISE);
	zassert_equal(p.slot, 1);
	zassert_false(p.open);
	/* the link is the active device's: keep it */
	p = plan(1, false, RDEV_NONE, 1);
	zassert_equal(p.step, RDEV_STEP_STAY);
	/* switch: the link is on another identity: end it first */
	p = plan(0, false, RDEV_NONE, 1);
	zassert_equal(p.step, RDEV_STEP_DISCONNECT);
	/* then advertise on the new identity */
	p = plan(0, false, RDEV_NONE, RDEV_NONE);
	zassert_equal(p.step, RDEV_STEP_ADVERTISE);
	zassert_equal(p.slot, 0);
	/* the pairing window wins over the active device */
	p = plan(0, true, 2, 0);
	zassert_equal(p.step, RDEV_STEP_DISCONNECT, "the active device's link ends for the window");
	p = plan(0, true, 2, RDEV_NONE);
	zassert_equal(p.step, RDEV_STEP_ADVERTISE);
	zassert_equal(p.slot, 2);
	zassert_true(p.open, "open to any device");
	p = plan(0, true, 2, 2);
	zassert_equal(p.step, RDEV_STEP_STAY, "the new device is connected: pairing runs");
	/* window ends without a pairing: back to the active device */
	p = plan(0, false, RDEV_NONE, 2);
	zassert_equal(p.step, RDEV_STEP_DISCONNECT);
	/* the last pairing removed while linked: end the link */
	p = plan(RDEV_NONE, false, RDEV_NONE, 1);
	zassert_equal(p.step, RDEV_STEP_DISCONNECT);
	/* window with no device at all */
	p = plan(RDEV_NONE, true, 0, RDEV_NONE);
	zassert_equal(p.step, RDEV_STEP_ADVERTISE);
	zassert_true(p.open);
}

/* A key may go only over an authenticated link of the active device: during a switch the old
 * device's link is still up and gets nothing. */
ZTEST(ring_devices, test_link_usable_only_for_the_active_device)
{
	zassert_true(rdev_link_usable(0, true, 0));
	zassert_false(rdev_link_usable(0, true, 1), "the old device's link in the switch window");
	zassert_false(rdev_link_usable(1, true, 0));
	zassert_false(rdev_link_usable(0, false, 0), "not authenticated");
	zassert_false(rdev_link_usable(RDEV_NONE, true, RDEV_NONE), "no link, no device");
	zassert_false(rdev_link_usable(0, true, RDEV_NONE), "no active device");
}

ZTEST_SUITE(ring_devices, NULL, NULL, NULL, NULL, NULL);
