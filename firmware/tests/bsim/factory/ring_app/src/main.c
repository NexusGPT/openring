/*
 * The ring side of the ship beacon test (BabbleSim, the simulated ring chip, see run.sh): the real factory part with its
 * real beacon (rfa_hw_real.c) and a stand-in scanner on the other device. Software step 6, unit U8, decision D6 (b).
 *
 * The script, in simulated ms (the stand-in knows the same times, typed from design/firmware.md l.1034, l.1035, l.1057):
 *   2,000   FACTORY SHIP_ENTER (0x7F) in FACTORY_TEST: the beacon starts at once ("Ring" + 4 hex digits, not connectable, every 100 ms)
 *   8,000   VBUS is removed: the join's ship steps call rfa_beacon_stop() right before the ship task
 *   70,000  FACTORY T-RADIO (0x60): the ring advertises for 10 s
 * Output lines: "RING CHECK <name> PASS|FAIL", "RING BEACON NAME <name>", "RING SCRIPT DONE t=<ms>", one "RING RESULT PASS|FAIL".
 */
#include <string.h>

#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

#include <ring_factory/rfa.h>
#include <ring_rhw/rhw.h>

#include "rfa_logic.h"

#define SHIP_AT_MS 2000
#define VBUS_OFF_AT_MS 8000
#define RADIO_AT_MS 70000

static int fails;
static int checks;
static bool flag = true;

#define CHECK(label, cond)                                                                            \
	do {                                                                                          \
		bool ok_ = (cond);                                                                    \
		checks++;                                                                             \
		fails += ok_ ? 0 : 1;                                                                 \
		printk("RING CHECK %s %s (t=%lld)\n", label, ok_ ? "PASS" : "FAIL", k_uptime_get()); \
	} while (0)

/* the join's two calls into the factory part: the factory flag (settings) */
static bool op_flag(void)
{
	return flag;
}

static int op_flag_set(bool on)
{
	flag = on;
	return 0;
}

static void sleep_until(int64_t t)
{
	int64_t d = t - k_uptime_get();

	if (d > 0) {
		k_sleep(K_MSEC(d));
	}
}

int main(void)
{
	struct rfa_ops ops = { .flag = op_flag, .flag_set = op_flag_set };
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff = RFA_EFFECT_NONE;
	uint64_t id = 0;
	char name[RFA_NAME_BYTES];
	uint8_t req;
	enum rrec_status st;

	CHECK("bt_enable", bt_enable(NULL) == 0);
	CHECK("rfa_init", rfa_init(&ops) == 0);
	CHECK("device id", rhw_clock()->device_id(&id) == 0);
	(void)rfa_beacon_name(id, name);
	printk("RING BEACON NAME %s\n", name);

	sleep_until(SHIP_AT_MS);
	req = 0x7F;
	st = rfa_request(&req, 1, true, out, &n, &eff);
	CHECK("SHIP_ENTER accepted", st == 0 && eff == RFA_EFFECT_SHIP_ENTER && n == 1 && out[0] == 0);
	CHECK("SHIP_ENTER cleared the flag", !flag);
	printk("RING SHIP_ENTER ANSWERED t=%lld\n", k_uptime_get());

	sleep_until(VBUS_OFF_AT_MS);
	printk("RING VBUS REMOVED t=%lld\n", k_uptime_get());
	rfa_beacon_stop(); /* what rpw_ship() calls right before TASKENTERSHIPMODE */
	printk("RING BEACON STOPPED t=%lld\n", k_uptime_get());

	flag = true; /* the ring is woken and programmed again for the radio test */
	sleep_until(RADIO_AT_MS);
	int64_t t0 = k_uptime_get();

	req = 0x60;
	st = rfa_request(&req, 1, true, out, &n, &eff);
	int64_t took = k_uptime_get() - t0;

	CHECK("T-RADIO answered pass", st == 0 && n == 1 && out[0] == 0);
	CHECK("T-RADIO took 10 s", took >= 10000 && took < 10200);
	printk("RING SCRIPT DONE t=%lld\n", k_uptime_get());
	printk("RING RESULT %s (%d checks)\n", fails == 0 ? "PASS" : "FAIL", checks);
	for (;;) {
		k_sleep(K_SECONDS(10));
	}
	return 0;
}
