/*
 * Ring OS application.
 * It prints one start line with the application version from app/VERSION
 * and the Zephyr kernel version, starts the devices and control parts
 * (step 2), then sleeps. Step 3 adds the iPhone part (ring_iphone: notifications with their
 * actions, track title and media commands, the time): rglue_init() starts it next to devices and
 * control, so this file has no extra call. Step 5 adds the relay service (ring_relay, design/firmware.md 7.7): a static
 * Bluetooth service plus a start-up hook that registers it with the iPhone part, so this file has no call for it either.
 *
 * Step 2 wiring: rctl_init() registers the HID service, rdev_init() enables
 * Bluetooth and advertises to the active device, rglue_init() starts the core
 * and carries its actions to control and to the recording hook (the same
 * module the two-device tests run). The joystick driver, the screens and the
 * settings menu come later: the driver calls rglue_input() with each debounced
 * switch edge; a control screen calls rctl_set_active(true) while it is shown
 * (control is off at start, so menu moves never type on the host); the screens
 * call rdev_pair_open(), rdev_switch() and rdev_remove() and show the passkey
 * from passkey_show.
 *
 * Step 6 wiring (the recorder, ring_recorder): the core starts in BOOT; every action of the core goes to
 * rrec_action(), every core step ends in rrec_glue_after() (the recorder's step, then the screens), the facts the
 * recorder owns are written in rrec_glue_screen_fact() before each core call, and the core's sign hook is
 * rrec_sign_hook() (decision D1). rrec_init() runs the boot sequence and gives the core "init done".
 */

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <app_version.h>
#include <version.h>

#include <ring_devices/rdev.h>
#include <ring_control/rctl.h>
#include <ring_glue/rglue.h>
#include <ring_screens/rscr.h>
#include <ring_recorder/rrec.h>
#include <rrec_int.h>

static void passkey_show(uint8_t slot, uint32_t passkey)
{
	/* SCR_PAIR shows these six digits; they also go to the console */
	printk("ring-os: pairing passkey for slot %u: %06u\n", slot, passkey);
	rscr_on_passkey(slot, passkey);
}

static void active_changed(uint8_t slot)
{
	printk("ring-os: active device slot %u\n", slot);
	rscr_on_active_changed(slot);
}

static void paired(uint8_t slot)
{
	rscr_on_paired(slot);
}

static void window_closed(void)
{
	rscr_on_window_closed();
}

static void removed(uint8_t slot)
{
	rscr_on_removed(slot);
}

static void link_changed(uint8_t slot, bool up)
{
	ARG_UNUSED(slot);
	ARG_UNUSED(up);
	rscr_poke();
}

static const struct rglue_ops glue_ops = {
	.action = rrec_action,               /* every action of the core, carried out by the recorder (step 6) */
	.after = rrec_glue_after,            /* the recorder's step, then the screens follow every core step */
	.screen_fact = rrec_glue_screen_fact, /* the recorder's facts, then the screens' lock fact: before every core call */
	.sign_start = rrec_sign_hook,        /* decision D1: the core asks for the recording sign before a start */
	.factory_gesture = rrec_factory_gesture, /* FACTORY_TEST: the gestures go to the factory tests (T-JOY, T-CENTRE) */
};

static const struct rdev_callbacks dev_cb = {
	.passkey_show = passkey_show,
	.paired = paired,
	.window_closed = window_closed,
	.removed = removed,
	.active_changed = active_changed,
	.link = link_changed,
};

int main(void)
{
	int err;

	printk("ring-os start: app %s, zephyr %s, board %s\n",
	       APP_VERSION_STRING, KERNEL_VERSION_STRING, CONFIG_BOARD_TARGET);

	err = rctl_init();
	if (err != 0) {
		printk("ring-os: HID service failed %d\n", err);
	} else {
		err = rdev_init(&dev_cb);
		if (err != 0) {
			printk("ring-os: devices failed %d\n", err);
		}
	}
	err = rscr_start(&rscr_real_ops);
	if (err != 0) {
		printk("ring-os: screens failed %d\n", err);
	}
	/* The core starts in BOOT; the recorder's boot sequence gives it "init done" (or "storage init fails"). */
	rglue_init(&glue_ops, RC_ST_BOOT);
	err = rrec_init();
	if (err != 0) {
		printk("ring-os recorder: boot sequence returned %d\n", err);
	}
	/* RECOVERY ends by itself (the recorder's thread scans): wait for a settled state before the boot line */
	for (int i = 0; i < 100 && (rglue_state() == RC_ST_BOOT || rglue_state() == RC_ST_RECOVERY); i++) {
		k_sleep(K_MSEC(10));
	}
	printk("ring-os recorder: boot done, state %s\n", rc_state_name(rglue_state()));
	if (err == 0 && IS_ENABLED(CONFIG_RING_PAIR_WINDOW_AT_BOOT) && rdev_active() == RDEV_NONE) {
		(void)rdev_pair_open(RDEV_ANY, RDEV_PAIR_WINDOW_MS);
	}

	while (1) {
		k_sleep(K_SECONDS(1));
	}

	return 0;
}
