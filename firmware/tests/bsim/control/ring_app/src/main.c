/*
 * Ring side of the two-device tests (BabbleSim, the simulated ring chip nrf54lm20bsim by default, with real encryption: see run.sh).
 *
 * The real ring_devices, ring_control and ring_glue modules run here; ring_glue is the module
 * the product application runs. The joystick is injected as switch edges into the glue (the
 * test hook) in simulated time; the glue feeds the real core, which returns the screen actions;
 * control turns them into HID reports for the active device, and the core's recording actions
 * reach the recording hook counted below. The scenario (RING_SCENARIO = A, B, C, D or F) is the
 * script of this ring; the stand-in host (host_app) checks what it receives against its own
 * expected values.
 *
 * Output lines contain "RING": CHECK <name> PASS|FAIL, and one "RING RESULT PASS|FAIL" at the
 * end. Times are simulated milliseconds.
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
#include "hosttools.h"

static int fails;
static int checks;
static int paired_events;
static int passkey_shown;
static bool passkey_valid = true;
static int rec_starts;
static int rec_stops;

#define CHECK(name, cond)                                                                          \
	do {                                                                                       \
		bool ok_ = (cond);                                                                 \
		checks++;                                                                          \
		fails += ok_ ? 0 : 1;                                                              \
		printk("RING CHECK %s %s (t=%lld)\n", name, ok_ ? "PASS" : "FAIL", k_uptime_get()); \
	} while (0)

static uint32_t wire_sends(void)
{
	struct rctl_stats st;

	rctl_stats_get(&st);
	return st.wire_sends;
}

static uint32_t reports(void)
{
	struct rctl_stats st;

	rctl_stats_get(&st);
	return st.reports;
}

/* ---- the screen part is not built yet: the passkey goes to a file the host reads ---- */

static void on_passkey_show(uint8_t slot, uint32_t passkey)
{
	char buf[16];
	char *path = nsi_host_getenv("RING_PASSFILE");
	int n = snprintk(buf, sizeof(buf), "%06u\n", passkey);

	passkey_shown++;
	passkey_valid = passkey_valid && passkey <= 999999;
	printk("RING PASSKEY slot %u %06u\n", slot, passkey);
	if (path != NULL) {
		int fd = nsi_host_open(path, HT_O_WRONLY | HT_O_TRUNC);

		if (fd >= 0) {
			(void)nsi_host_write(fd, buf, (unsigned long)n);
			(void)nsi_host_close(fd);
		} else {
			printk("RING cannot open passfile %s (%d)\n", path, fd);
		}
	}
}

static void on_paired(uint8_t slot)
{
	paired_events++;
	printk("RING EVENT paired slot %u\n", slot);
}

static void on_active(uint8_t slot)
{
	printk("RING EVENT active slot %u\n", slot);
}

static int link_down_events;

static void on_link(uint8_t slot, bool up)
{
	link_down_events += up ? 0 : 1;
	printk("RING EVENT link slot %u %s\n", slot, up ? "up" : "down");
}

static void on_removed(uint8_t slot)
{
	printk("RING EVENT removed slot %u\n", slot);
}

static const struct rdev_callbacks cbs = {
	.passkey_show = on_passkey_show,
	.paired = on_paired,
	.active_changed = on_active,
	.link = on_link,
	.removed = on_removed,
};

/* ---- the recording hook: what the recorder part will act on ---- */

static void recording_hook(enum rc_action a, rc_ms_t t)
{
	if (a == RC_ACT_OPEN) {
		rec_starts++;
		printk("RING EVENT recording start (t=%lld)\n", t);
	} else if (a == RC_ACT_CLOSE) {
		rec_stops++;
		printk("RING EVENT recording stop (t=%lld)\n", t);
	}
}

static const struct rglue_ops glue_ops = {
	.action = recording_hook,
};

/* ---- the test hook: joystick edges into the glue, in simulated time ---- */

static void inject(enum rc_switch sw, int hold_ms)
{
	rglue_input(sw, true);
	k_sleep(K_MSEC(hold_ms));
	rglue_input(sw, false);
	k_sleep(K_MSEC(600)); /* past the double-press window of the centre (400 ms) */
}

static const enum rc_switch sw_of[RCTL_ACTION_COUNT] = {
	[RCTL_CENTRE] = RC_SW_CENTRE, [RCTL_UP] = RC_SW_UP, [RCTL_DOWN] = RC_SW_DOWN,
	[RCTL_LEFT] = RC_SW_LEFT,     [RCTL_RIGHT] = RC_SW_RIGHT,
};

/* One joystick action in a mode; checks the number of reports the ring sent. */
static void act(enum rctl_mode m, enum rctl_action a, int want_reports, const char *tag)
{
	uint32_t before = reports();
	char name[96];

	rctl_set_mode(m);
	inject(sw_of[a], 100);
	snprintk(name, sizeof(name), "%s%s.%s sends %d report(s)", tag, rctl_mode_name(m), rctl_action_name(a),
		 want_reports);
	CHECK(name, reports() - before == (uint32_t)want_reports);
}

/* Wait until the paired callback has fired n times in all. */
static bool wait_for_paired(int n, int64_t timeout_ms)
{
	int64_t end = k_uptime_get() + timeout_ms;

	while (k_uptime_get() < end) {
		if (paired_events >= n) {
			k_sleep(K_MSEC(500));
			return true;
		}
		k_sleep(K_MSEC(50));
	}
	return paired_events >= n;
}

/* Wait until the device of 'slot' is the active one and has a ready link (the old link of
 * another slot may still be up for a moment after a switch or a pairing window). After a
 * reconnect the notification switches of the bonded device are restored from the bond, so the
 * ring cannot see when the host's HID client is ready again: wait 3 s (the host needs about 2 s). */
static bool wait_ready(uint8_t slot, int64_t timeout_ms)
{
	int64_t end = k_uptime_get() + timeout_ms;

	while (k_uptime_get() < end) {
		if (rdev_active() == slot && rctl_ready()) {
			k_sleep(K_MSEC(3000));
			return rdev_active() == slot && rctl_ready();
		}
		k_sleep(K_MSEC(100));
	}
	return false;
}

static void sleep_until(int64_t t_ms)
{
	if (k_uptime_get() < t_ms) {
		k_sleep(K_MSEC(t_ms - k_uptime_get()));
	}
}

/* A fault hook for the broken copy "host_write": a broken ring_control calls this from the
 * handler of a host write, so a host write reaches the joystick path (a centre hold). */
static struct k_work_delayable fault_release;
static void fault_release_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	rglue_input(RC_SW_CENTRE, false);
}
void bsim_fault_hook(void)
{
	rglue_input(RC_SW_CENTRE, true);
	k_work_reschedule(&fault_release, K_MSEC(1200));
}

/* ---- scenarios ---- */

static void run_a(void)
{
	/* expected reports per mode and action: centre, up, down, left, right */
	static const int want[RCTL_MODE_COUNT][RCTL_ACTION_COUNT] = {
		[RCTL_MEDIA] = { 2, 2, 2, 2, 2 },
		[RCTL_PRESENTER] = { 0, 2, 2, 2, 2 },
		[RCTL_POINTER] = { 2, 1, 1, 1, 1 },
		[RCTL_AGENT] = { 2, 2, 2, 2, 2 },
	};
	struct rctl_options opt = { .presenter_pages = false };
	uint32_t before;
	struct rctl_stats st;

	CHECK("pairing window opens", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	CHECK("host pairs and its link is ready", wait_ready(0, 40000));
	CHECK("passkey was shown once, six digits", passkey_shown == 1 && passkey_valid);
	CHECK("paired callback once", paired_events == 1);
	CHECK("slot 0 is active", rdev_active() == 0 && (rdev_paired_mask() & 1) != 0);

	/* control is off until a control screen is shown: a direction types nothing */
	CHECK("control starts not active", !rctl_is_active());
	rctl_set_mode(RCTL_MEDIA);
	before = reports();
	inject(RC_SW_UP, 100);
	CHECK("control inactive: direction sends no report", reports() == before);
	rctl_set_active(true);

	rctl_set_options(&opt);
	for (int a = 0; a < RCTL_ACTION_COUNT; a++) {
		act(RCTL_MEDIA, a, want[RCTL_MEDIA][a], "");
	}
	for (int a = 0; a < RCTL_ACTION_COUNT; a++) {
		act(RCTL_PRESENTER, a, want[RCTL_PRESENTER][a], "");
	}
	opt.presenter_pages = true;
	rctl_set_options(&opt);
	for (int a = 0; a < RCTL_ACTION_COUNT; a++) {
		act(RCTL_PRESENTER, a, want[RCTL_PRESENTER][a], "pages ");
	}
	opt.presenter_pages = false;
	rctl_set_options(&opt);
	for (int a = 0; a < RCTL_ACTION_COUNT; a++) {
		act(RCTL_POINTER, a, want[RCTL_POINTER][a], "");
	}
	for (int a = 0; a < RCTL_ACTION_COUNT; a++) {
		act(RCTL_AGENT, a, want[RCTL_AGENT][a], "");
	}

	/* a held direction repeats through the core: pointer, right, held 1100 ms */
	rctl_set_mode(RCTL_POINTER);
	before = reports();
	inject(RC_SW_RIGHT, 1100);
	printk("RING INFO held right 1100 ms sent %u reports\n", reports() - before);
	CHECK("pointer held right repeats (at least 4 reports)", reports() - before >= 4);
	CHECK("pointer held right repeats (at most 8 reports)", reports() - before <= 8);

	/* screen off: the first event only wakes the screen, no key (Apple's rule) */
	rctl_set_mode(RCTL_AGENT);
	rglue_set_screen_on(false);
	before = reports();
	inject(RC_SW_RIGHT, 100);
	CHECK("screen off: a direction sends no report", reports() == before);
	rglue_set_screen_on(true);

	/* a double press of the centre is not a joystick action of the screen: no key */
	before = reports();
	rglue_input(RC_SW_CENTRE, true);
	k_sleep(K_MSEC(80));
	rglue_input(RC_SW_CENTRE, false);
	k_sleep(K_MSEC(150));
	rglue_input(RC_SW_CENTRE, true);
	k_sleep(K_MSEC(80));
	rglue_input(RC_SW_CENTRE, false);
	k_sleep(K_MSEC(800));
	CHECK("centre double press sends no report", reports() == before);

	rctl_stats_get(&st);
	CHECK("no action was dropped", st.dropped == 0 && st.errors == 0);

	/* a drop: the host ends the link at 40 s; the ring advertises to the bonded device again and
	 * the host reconnects by itself; the keys flow again */
	{
		int downs = link_down_events;

		sleep_until(41000);
		CHECK("the drop was seen (link down)", link_down_events > downs);
		CHECK("reconnect after the drop, link ready", wait_ready(0, 40000));
		act(RCTL_AGENT, RCTL_CENTRE, 2, "after the drop ");
	}
}

static void run_b(void)
{
	bt_addr_le_t addrs[RDEV_SLOTS];
	size_t count = RDEV_SLOTS;
	bool distinct;
	int r;
	uint32_t w0;

	rctl_set_active(true);
	/* host 1 pairs on slot 0 and receives the keys of phase 1 */
	CHECK("pairing window opens for slot 0", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	CHECK("host 1 pairs, link ready", wait_ready(0, 40000));
	CHECK("slot 0 active", rdev_active() == 0);
	act(RCTL_MEDIA, RCTL_CENTRE, 2, "P1 ");
	act(RCTL_MEDIA, RCTL_RIGHT, 2, "P1 ");

	/* host 2 is told to start scanning at 25 s; the window for slot 1 opens at 30 s */
	sleep_until(30000);
	CHECK("pairing window opens for slot 1", rdev_pair_open(1, RDEV_PAIR_WINDOW_MS) == 0);
	CHECK("B: host 2 pairs (the paired callback fires)", wait_for_paired(2, 40000));
	/* design/firmware.md 3.4 and 7.4: the first device stays the active one; the new device's link ends and
	 * the ring advertises to host 1 again */
	CHECK("B: after the second pairing the first device is still the active one (slot 0) and both bonds exist",
	      rdev_active() == 0 && rdev_paired_mask() == 0x03);
	CHECK("B: host 1 reconnects and its link is ready again", wait_ready(0, 40000));
	CHECK("B: the first device is still the active one with its link up", rdev_active() == 0 && rdev_link_up());
	act(RCTL_MEDIA, RCTL_CENTRE, 2, "P2a ");
	act(RCTL_MEDIA, RCTL_LEFT, 2, "P2a ");
	/* the wearer chooses "Use" for the second device */
	CHECK("B: switch to slot 1", rdev_switch(1) == 0);
	CHECK("B: host 2 reconnects, link ready", wait_ready(1, 40000));
	CHECK("slot 1 active after the switch", rdev_active() == 1);
	act(RCTL_MEDIA, RCTL_CENTRE, 2, "P2 ");
	act(RCTL_MEDIA, RCTL_LEFT, 2, "P2 ");

	/* switch back to host 1: host 1 receives, host 2 none */
	CHECK("switch to slot 0", rdev_switch(0) == 0);
	CHECK("host 1 reconnects, link ready", wait_ready(0, 40000));
	CHECK("slot 0 active", rdev_active() == 0);
	act(RCTL_MEDIA, RCTL_UP, 2, "P3 ");
	act(RCTL_MEDIA, RCTL_DOWN, 2, "P3 ");

	/* switch to host 2 again; a key given in the same instant, while host 1's link is still up,
	 * must not go to host 1 (the old device) */
	CHECK("switch to slot 1", rdev_switch(1) == 0);
	w0 = wire_sends();
	r = rctl_action(RCTL_CENTRE);
	/* not sent: the call says so AND nothing was handed to the Bluetooth stack (the counter of
	 * every send, not the return code alone) */
	CHECK("key in the switch window is not sent", r == -ENOTCONN && wire_sends() == w0);
	CHECK("host 2 reconnects, link ready", wait_ready(1, 40000));
	act(RCTL_MEDIA, RCTL_RIGHT, 2, "P4 ");

	CHECK("switch to an empty slot is refused", rdev_switch(2) == -ENOENT);
	CHECK("switch to the active slot changes nothing", rdev_switch(1) == 0 && rdev_active() == 1);

	bt_id_get(addrs, &count);
	distinct = count == RDEV_SLOTS && !bt_addr_le_eq(&addrs[0], &addrs[1]) &&
		   !bt_addr_le_eq(&addrs[0], &addrs[2]) && !bt_addr_le_eq(&addrs[1], &addrs[2]);
	CHECK("three distinct local identities", distinct);
	CHECK("two paired callbacks", paired_events == 2);
}

static void run_c(void)
{
	bt_addr_le_t peer;
	int r;

	rctl_set_active(true);
	CHECK("pairing window opens", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	CHECK("host pairs, link ready", wait_ready(0, 40000));
	act(RCTL_MEDIA, RCTL_CENTRE, 2, "before removal ");
	CHECK("bond exists before removal", rdev_slot_peer(0, &peer) == 0);

	r = rdev_remove(0);
	CHECK("pairing removed", r == 0);
	CHECK("bond deleted", rdev_slot_peer(0, &peer) == -ENOENT && rdev_paired_mask() == 0);
	CHECK("no active device and no link", rdev_active() == RDEV_NONE && !rdev_link_up());
	CHECK("removing again reports no pairing", rdev_remove(0) == -ENOENT);

	/* the removed host still holds its keys; it tries to reconnect while the ring is open to pairing */
	k_sleep(K_MSEC(3000));
	CHECK("pairing window opens again", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	k_sleep(K_MSEC(8000));
	rctl_set_mode(RCTL_MEDIA);
	{
		uint32_t w1 = wire_sends(), r1 = reports();

		/* the removed host's keys do not work and the ring has no device: nothing goes to the stack */
		CHECK("no key goes out while the host is not paired", rctl_action(RCTL_CENTRE) == -ENOTCONN &&
		      wire_sends() == w1 && reports() == r1 && !rdev_link_up() && rdev_paired_mask() == 0);
	}

	/* the host drops its old keys and pairs again with a new passkey */
	CHECK("host pairs again, link ready", wait_ready(0, 25000));
	CHECK("two pairings in total", paired_events == 2 && rdev_active() == 0);
	act(RCTL_MEDIA, RCTL_CENTRE, 2, "after new pairing ");

	/* step 6 fix round 1 (review finding R6-02, FW l.937 "close ... radio"): ship mode's step 1 closes the radio with
	 * rdev_stop() at 55 s; host 1 sees the link end and no advertising after it (its check "C: no advertising after
	 * ship close") */
	sleep_until(55000);
	printk("RING INFO ship close: rdev_stop at t=%lld\n", k_uptime_get());
	CHECK("C: ship close stops the radio (rdev_stop answers 0)", rdev_stop() == 0);
}

/* D: a centre hold is a recording gesture in every mode; a failed release is sent later; a host
 * that writes to the ring cannot start or stop a recording. */
static void run_d(void)
{
	struct rctl_stats st0, st1;
	uint32_t before;
	int starts, stops;
	char name[96];

	k_work_init_delayable(&fault_release, fault_release_fn);
	rctl_set_active(true);
	CHECK("pairing window opens", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	CHECK("host pairs and its link is ready", wait_ready(0, 40000));

	for (int m = 0; m < RCTL_MODE_COUNT; m++) {
		rctl_set_mode(m);
		before = reports();
		starts = rec_starts;
		stops = rec_stops;
		inject(RC_SW_CENTRE, 1200);
		snprintk(name, sizeof(name), "%s: centre hold starts a recording", rctl_mode_name(m));
		CHECK(name, rec_starts == starts + 1 && rec_stops == stops && rglue_state() == RC_ST_RECORDING);
		snprintk(name, sizeof(name), "%s: centre hold sends no report", rctl_mode_name(m));
		CHECK(name, reports() == before);

		before = reports();
		inject(RC_SW_CENTRE, 1200);
		snprintk(name, sizeof(name), "%s: second centre hold stops the recording", rctl_mode_name(m));
		CHECK(name, rec_stops == stops + 1 && rglue_state() == RC_ST_STANDBY);
		snprintk(name, sizeof(name), "%s: second centre hold sends no report", rctl_mode_name(m));
		CHECK(name, reports() == before);
	}

	/* a release report that fails is sent later: no key stays down on the host */
	rctl_set_mode(RCTL_AGENT);
	rctl_stats_get(&st0);
	rctl_test_fail_releases(1);
	inject(RC_SW_CENTRE, 100);
	rctl_stats_get(&st1);
	CHECK("failed release is sent later", st1.release_retries == st0.release_retries + 1 && !rctl_release_pending() &&
	      st1.release_lost == st0.release_lost);

	/* the host writes to the HID control point at 45 s; nothing it writes starts or stops a recording */
	starts = rec_starts;
	stops = rec_stops;
	before = reports();
	sleep_until(50000);
	rctl_stats_get(&st1);
	CHECK("host control point writes arrived", st1.host_writes >= 2);
	CHECK("host writes start no recording", rec_starts == starts && rec_stops == stops &&
	      rglue_state() == RC_ST_STANDBY);
	CHECK("host writes send no report", reports() == before);
}

/* F: pairing outside the window is refused. Host 1 pairs and drops; host 2, never paired, tries
 * to pair while the ring advertises to host 1 with the window closed. */
static void run_f(void)
{
	rctl_set_active(true);
	CHECK("pairing window opens", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	CHECK("host 1 pairs, link ready", wait_ready(0, 40000));
	act(RCTL_MEDIA, RCTL_CENTRE, 2, "before the drop ");
	CHECK("pairing window is closed", !rdev_pair_window_open());

	/* host 1 drops at 12 s and stays away until 32 s; host 2 tries from 14 s */
	sleep_until(30000);
	CHECK("no new pairing outside the window (one bond)", rdev_paired_mask() == 0x01 && paired_events == 1);
	CHECK("host 1 returns, link ready", wait_ready(0, 40000));
	act(RCTL_MEDIA, RCTL_CENTRE, 2, "after host 2 tried ");
	CHECK("still one bond", rdev_paired_mask() == 0x01 && paired_events == 1);
}

/* G: three devices over Bluetooth. Three hosts pair in turn on slots 0, 1, 2; the ring switches to
 * each; each gets its own key and the other two none (host totals); a fourth pairing is refused. */
static void run_g(void)
{
	CHECK("G: the pairing window opens for slot 0", rdev_pair_open(0, RDEV_PAIR_WINDOW_MS) == 0);
	rctl_set_active(true);
	CHECK("G: host 1 pairs, link ready", wait_ready(0, 40000));
	act(RCTL_MEDIA, RCTL_CENTRE, 2, "G host 1 ");
	sleep_until(30000);
	CHECK("G: the pairing window opens for slot 1", rdev_pair_open(1, RDEV_PAIR_WINDOW_MS) == 0);
	CHECK("G: host 2 pairs", wait_for_paired(2, 40000));
	CHECK("G: the first device is still the active one", rdev_active() == 0);
	CHECK("G: host 1 reconnects, link ready", wait_ready(0, 40000));
	CHECK("G: switch to slot 1 after its pairing", rdev_switch(1) == 0);
	CHECK("G: host 2 reconnects, link ready", wait_ready(1, 40000));
	act(RCTL_MEDIA, RCTL_LEFT, 2, "G host 2 ");
	sleep_until(55000);
	CHECK("G: the pairing window opens for slot 2", rdev_pair_open(2, RDEV_PAIR_WINDOW_MS) == 0);
	CHECK("G: host 3 pairs", wait_for_paired(3, 40000));
	/* the device that was active (slot 1, after the switch) stays active: the new device does not take over */
	CHECK("G: after the third pairing the device that was active (slot 1) is still the active one", rdev_active() == 1);
	CHECK("G: switch to slot 2 after its pairing", rdev_switch(2) == 0);
	CHECK("G: host 3 reconnects, link ready", wait_ready(2, 40000));
	act(RCTL_MEDIA, RCTL_RIGHT, 2, "G host 3 ");
	CHECK("G: three bonds", rdev_paired_mask() == 0x07 && paired_events == 3);

	/* switch to each: the key goes to that device only */
	CHECK("G: switch to slot 0", rdev_switch(0) == 0);
	CHECK("G: host 1 reconnects, link ready", wait_ready(0, 40000));
	act(RCTL_MEDIA, RCTL_UP, 2, "G switch to host 1 ");
	CHECK("G: switch to slot 1", rdev_switch(1) == 0);
	CHECK("G: host 2 reconnects, link ready", wait_ready(1, 40000));
	act(RCTL_MEDIA, RCTL_DOWN, 2, "G switch to host 2 ");
	CHECK("G: switch to slot 2", rdev_switch(2) == 0);
	CHECK("G: host 3 reconnects, link ready", wait_ready(2, 40000));
	act(RCTL_MEDIA, RCTL_CENTRE, 2, "G switch to host 3 ");

	/* a fourth pairing: all three slots hold a pairing, so the window cannot open. Host 3 drops
	 * at 102 s and stays away until 122 s, so the ring advertises with the window closed; host 4
	 * tries to pair from 103 s. */
	sleep_until(100000);
	CHECK("G: fourth pairing refused (-ENOSPC)", rdev_pair_open(RDEV_ANY, RDEV_PAIR_WINDOW_MS) == -ENOSPC);
	sleep_until(125000);
	CHECK("G: no fourth bond", rdev_paired_mask() == 0x07 && paired_events == 3);
	if (rdev_pair_window_open()) {
		rdev_pair_cancel();
	}
	CHECK("G: host 3 returns, link ready", wait_ready(2, 20000));
	act(RCTL_MEDIA, RCTL_UP, 2, "G host 3 after the fourth ");
}

int main(void)
{
	char *scen = nsi_host_getenv("RING_SCENARIO");
	int err;

	printk("RING START scenario %s\n", scen != NULL ? scen : "(none)");
	rglue_init(&glue_ops, RC_ST_STANDBY);
	rglue_set_screen_on(true);

	err = rctl_init();
	CHECK("HID service registered", err == 0);
	err = rdev_init(&cbs);
	CHECK("Bluetooth up, devices ready", err == 0);
	if (err != 0 || scen == NULL) {
		printk("RING RESULT FAIL\n");
		return 0;
	}

	if (strcmp(scen, "A") == 0) {
		run_a();
	} else if (strcmp(scen, "B") == 0) {
		run_b();
	} else if (strcmp(scen, "C") == 0) {
		run_c();
	} else if (strcmp(scen, "D") == 0) {
		run_d();
	} else if (strcmp(scen, "F") == 0) {
		run_f();
	} else if (strcmp(scen, "G") == 0) {
		run_g();
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
