/*
 * Ring side of the screens test (BabbleSim, the simulated ring chip nrf54lm20bsim, real encryption: see run.sh).
 *
 * The real ring_devices, ring_control, ring_glue, ring_inbox, ring_time, ring_iphone and ring_core modules run here, and
 * ring_screens with its memory display (a frame buffer in RAM: the simulated chip has no panel). The stand-in iPhone
 * (host_app, scenario S) pairs with the ring and serves Apple's Notification Center Service. Everything the wearer does
 * is a joystick edge into rglue_input(): the screens open the pairing window, show the notification, and the dismiss chosen
 * on the detail screen goes through ring_iphone to the stand-in. Every expected value is a literal written here.
 *
 * Output lines contain "RING": CHECK <name> PASS|FAIL, one "RING RESULT PASS|FAIL". Times are simulated ms.
 */

#include <errno.h>
#include <stdlib.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/bluetooth/bluetooth.h>

#include <ring_core/rc_core.h>
#include <ring_devices/rdev.h>
#include <ring_control/rctl.h>
#include <ring_glue/rglue.h>
#include <ring_iphone/rip.h>
#include <ring_screens/rmd.h>
#include <ring_screens/rscr.h>
#include "hosttools.h"

static int fails;
static int checks;

#define CHECK(name, cond)                                                                          \
	do {                                                                                       \
		bool ok_ = (cond);                                                                 \
		checks++;                                                                          \
		fails += ok_ ? 0 : 1;                                                              \
		printk("RING CHECK %s %s (t=%lld)\n", name, ok_ ? "PASS" : "FAIL", k_uptime_get()); \
	} while (0)

static void write_passkey(uint32_t passkey)
{
	char buf[16];
	char *path = nsi_host_getenv("RING_PASSFILE");
	int n = snprintk(buf, sizeof(buf), "%06u\n", passkey);

	if (path != NULL) {
		int fd = nsi_host_open(path, HT_O_WRONLY | HT_O_TRUNC);

		if (fd >= 0) {
			(void)nsi_host_write(fd, buf, (unsigned long)n);
			(void)nsi_host_close(fd);
		}
	}
}

/* the devices part's callbacks go to the screens (as in the product); the passkey also goes to the file the stand-in
 * reads (the wearer reads it on the screen and types it on the phone) */
static uint32_t shown_passkey;
static int passkey_calls;
static uint64_t hash_with_key;
static uint64_t hash_no_key;
static enum rscr_screen screen_at_key;

static void on_passkey(uint8_t slot, uint32_t passkey)
{
	shown_passkey = passkey;
	passkey_calls++;
	printk("RING PASSKEY slot %u %06u\n", slot, passkey);
	/* the pairing frame without the digits, then the same screen with them, both taken before the pairing can finish */
	rscr_sync();
	hash_no_key = rmd_hash();
	rscr_on_passkey(slot, passkey);
	{
		struct rscr s;

		rscr_sync();
		rscr_snapshot(&s);
		screen_at_key = (enum rscr_screen)s.screen;
		hash_with_key = rmd_hash();
	}
	write_passkey(passkey);
}

static void on_paired(uint8_t slot)
{
	printk("RING EVENT paired slot %u\n", slot);
	rscr_on_paired(slot);
}

static void on_window_closed(void)
{
	rscr_on_window_closed();
}

static void on_removed(uint8_t slot)
{
	rscr_on_removed(slot);
}

static void on_active(uint8_t slot)
{
	rscr_on_active_changed(slot);
}

static void on_link(uint8_t slot, bool up)
{
	printk("RING EVENT link slot %u %s\n", slot, up ? "up" : "down");
	rscr_poke();
}

static const struct rdev_callbacks cbs = {
	.passkey_show = on_passkey,
	.paired = on_paired,
	.window_closed = on_window_closed,
	.removed = on_removed,
	.active_changed = on_active,
	.link = on_link,
};

static const struct rglue_ops glue_ops = {
	.after = rscr_glue_after,
	.screen_fact = rscr_lock_fact_now,
};

static void press(enum rc_switch sw)
{
	rglue_input(sw, true);
	k_sleep(K_MSEC(80));
	rglue_input(sw, false);
	k_sleep(K_MSEC(700));
}

static enum rscr_screen screen(void)
{
	struct rscr s;

	rscr_sync();
	rscr_snapshot(&s);
	return (enum rscr_screen)s.screen;
}

static uint64_t frame_hash(void)
{
	rscr_sync();
	return rmd_hash();
}

static bool wait_for(bool (*cond)(void), int64_t timeout_ms)
{
	int64_t end = k_uptime_get() + timeout_ms;

	while (k_uptime_get() < end) {
		if (cond()) {
			return true;
		}
		k_sleep(K_MSEC(50));
	}
	return cond();
}

static bool passkey_seen(void)
{
	return passkey_calls > 0 && hash_with_key != 0;
}

static bool paired_active(void)
{
	return rdev_active() == 0 && rdev_link_up();
}

static bool ancs_ready(void)
{
	return rip_ancs_ready();
}

static bool one_with_text(void)
{
	struct rinbox_item it;

	return rip_inbox_count() == 1 && rip_inbox_get(0, &it) && it.text_ready;
}

static bool core_off(void)
{
	return rglue_state() == RC_ST_OFF;
}

static bool inbox_empty(void)
{
	return rip_inbox_count() == 0;
}

/* the peak use of each thread's stack (Zephyr's thread analyzer is not available on this board: this is its job, done by hand) */
static void stack_cb(const struct k_thread *t, void *u)
{
	size_t unused = 0;
	const char *n = k_thread_name_get((k_tid_t)t);

	ARG_UNUSED(u);
	if (k_thread_stack_space_get(t, &unused) == 0) {
		printk("RING STACK %s: size %u, used at most %u\n", n != NULL && n[0] != 0 ? n : "(no name)", (unsigned)t->stack_info.size,
		       (unsigned)(t->stack_info.size - unused));
	}
}

static void run_s(void)
{
	struct rmd_stats ms;
	uint64_t h_empty, h_list, h_detail, h_pair1;
	struct rip_stats st;

	/* 1. wake the screen with a joystick event (the lock: the first event only turns the screen on) */
	k_sleep(K_MSEC(1000));
	press(RC_SW_DOWN);
	CHECK("S: the first joystick event turns the screen on: SCR_STATUS", screen() == SCR_STATUS);
	rmd_stats_get(&ms);
	CHECK("S: the panel is on", !ms.blanked);
	/* 2. the menu, item "Pair device" (the fourth), open it with Right: the pairing window opens */
	press(RC_SW_RIGHT);
	CHECK("S: Right opens the menu", screen() == SCR_MENU);
	press(RC_SW_DOWN);
	press(RC_SW_DOWN);
	press(RC_SW_DOWN);
	press(RC_SW_RIGHT);
	CHECK("S: Pair device opens SCR_PAIR and the pairing window of ring_devices", screen() == SCR_PAIR && rdev_pair_window_open());
	/* the stand-in connects and the ring shows the passkey it generated */
	CHECK("S: the passkey arrives from the pairing", wait_for(passkey_seen, 40000));
	CHECK("S: six digits were generated and SCR_PAIR was on the screen when they arrived", passkey_calls == 1 &&
	      shown_passkey <= 999999 && screen_at_key == SCR_PAIR);
	CHECK("S: the frame with the digits differs from the pairing frame without them", hash_with_key != hash_no_key);
	/* 3. paired: the first paired device is the active one, the screen shows the device list */
	CHECK("S: the iPhone paired and is the active device (slot 0, the first paired device)", wait_for(paired_active, 40000));
	k_sleep(K_MSEC(500));
	CHECK("S: after the pairing the screen shows SCR_DEVICES", screen() == SCR_DEVICES);
	h_pair1 = frame_hash();
	CHECK("S: the pairing screen and the device list are different frames", hash_with_key != h_pair1);
	/* 4. leave the menu: Left twice goes devices to menu to status */
	press(RC_SW_LEFT);
	press(RC_SW_LEFT);
	CHECK("S: back on the status screen", screen() == SCR_STATUS);
	CHECK("S: the notification service is found and subscribed", wait_for(ancs_ready, 40000));
	/* 5. the empty list: Up from the status screen */
	press(RC_SW_UP);
	CHECK("S: Up opens the notification list (empty: the inbox holds nothing)", screen() == SCR_NOTIFS && rip_inbox_count() == 0);
	h_empty = frame_hash();
	/* 6. the notification arrives from the iPhone (the stand-in sends it at 2 s after the subscription) */
	CHECK("S: the notification arrives with its text", wait_for(one_with_text, 30000));
	k_sleep(K_MSEC(500));
	CHECK("S: the list screen follows the inbox (still SCR_NOTIFS, redrawn)", screen() == SCR_NOTIFS);
	h_list = frame_hash();
	CHECK("S: the frame of the list with the notification differs from the frame of the empty list", h_list != h_empty);
	/* 7. open it, choose dismiss with the joystick */
	press(RC_SW_RIGHT);
	CHECK("S: Right opens the notification detail", screen() == SCR_NOTIF);
	h_detail = frame_hash();
	CHECK("S: the detail frame differs from the list frame", h_detail != h_list);
	press(RC_SW_LEFT);
	rip_stats_get(&st);
	CHECK("S: the dismiss went out through ring_iphone once", st.actions_sent == 1 && st.actions_refused == 0 && st.action_errors == 0);
	/* 8. the iPhone removes it; the inbox empties and the screens leave the detail */
	CHECK("S: the iPhone reported the removal: the inbox is empty", wait_for(inbox_empty, 20000));
	k_sleep(K_MSEC(500));
	CHECK("S: the screen went back to the list", screen() == SCR_NOTIFS);
	CHECK("S: the list is empty again and its frame equals the first empty-list frame", frame_hash() == h_empty);
	rmd_stats_get(&ms);
	CHECK("S: no draw was refused", ms.refused == 0);
	/* round 3: menu, Power off, Yes through the real glue: the screens queue the power off, their thread calls rglue_event_try, and
	 * the core goes to OFF (its STANDBY row for the menu's power off) */
	press(RC_SW_LEFT);
	CHECK("S: Left from the empty list shows the status screen", screen() == SCR_STATUS);
	press(RC_SW_RIGHT);
	for (int i = 0; i < 5; i++) {
		press(RC_SW_DOWN);
	}
	press(RC_SW_RIGHT);
	CHECK("S: the menu's sixth item, Power off, opens the confirmation", screen() == SCR_CONFIRM);
	CHECK("S: the core is still in STANDBY before Yes", rglue_state() == RC_ST_STANDBY);
	press(RC_SW_CENTRE);   /* Yes */
	CHECK("S: after Yes the core is in OFF (the screens' power off went through rglue_event)", wait_for(core_off, 5000));
	CHECK("S: the screen is off with the ring", screen() == SCR_OFF);
	/* stack use of every thread so far (Zephyr thread analyzer): the glue, the Bluetooth RX context and the screens thread are
	 * among them */
	printk("RING MEMORY stack use of every thread after the two-device test (k_thread_stack_space_get):\n");
	k_thread_foreach(stack_cb, NULL);
}

int main(void)
{
	char *scen = nsi_host_getenv("RING_SCENARIO");
	int err;

	printk("RING START scenario %s\n", scen != NULL ? scen : "(none)");
	err = rctl_init();
	CHECK("HID service registered", err == 0);
	err = rdev_init(&cbs);
	CHECK("Bluetooth up, devices ready", err == 0);
	err = rscr_start(&rscr_real_ops);
	CHECK("screens started (LVGL on the memory display)", err == 0);
	rglue_init(&glue_ops, RC_ST_STANDBY);
	if (err != 0 || scen == NULL) {
		printk("RING RESULT FAIL\n");
		return 0;
	}
	if (strcmp(scen, "S") == 0) {
		run_s();
	} else {
		CHECK("known scenario", false);
	}
	printk("RING SCRIPT DONE t=%lld checks=%d fails=%d\n", k_uptime_get(), checks, fails);
	printk("RING RESULT %s\n", fails == 0 ? "PASS" : "FAIL");
	while (1) {
		k_sleep(K_SECONDS(1));
	}
	return 0;
}
