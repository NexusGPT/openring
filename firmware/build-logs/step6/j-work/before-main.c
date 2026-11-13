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
 * from passkey_show; the recorder acts on RC_ACT_OPEN and RC_ACT_CLOSE in
 * recording_action().
 */

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <app_version.h>
#include <version.h>

#include <ring_devices/rdev.h>
#include <ring_control/rctl.h>
#include <ring_glue/rglue.h>
#include <ring_screens/rscr.h>

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

/* Every action of the core arrives here after control has seen it. */
static void recording_action(enum rc_action a, rc_ms_t t)
{
	if (a == RC_ACT_OPEN || a == RC_ACT_CLOSE) {
		printk("ring-os: recording %s requested at %lld ms\n", a == RC_ACT_OPEN ? "start" : "stop", t);
	}
}

static const struct rglue_ops glue_ops = {
	.action = recording_action,
	.after = rscr_glue_after,   /* the screens follow every core step */
	.screen_fact = rscr_lock_fact_now,   /* and own the lock fact: read before every core call */
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
	/* The core starts in STANDBY until the recorder part sends the boot events. */
	rglue_init(&glue_ops, RC_ST_STANDBY);
	if (err == 0 && IS_ENABLED(CONFIG_RING_PAIR_WINDOW_AT_BOOT) && rdev_active() == RDEV_NONE) {
		(void)rdev_pair_open(RDEV_ANY, RDEV_PAIR_WINDOW_MS);
	}

	while (1) {
		k_sleep(K_SECONDS(1));
	}

	return 0;
}
