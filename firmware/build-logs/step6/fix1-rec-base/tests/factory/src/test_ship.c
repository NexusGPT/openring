/* Suite factory_ship (software step 6, unit U8): the ship beacon (ruling R20, FW l.1057) of SHIP_ENTER (0x7F) and
 * SHIP_SAMPLE (0x7E), FW l.1034, l.1035. Rows T22. From the acceptance of the command until TASKENTERSHIP: advertising
 * that cannot be connected to, every 100 ms, at 0 dBm, named "Ring" and the last 4 hex digits of the device id; it stops
 * right before the ship task (given to rpw_ship as before_task), within 1 s of VBUS removal, and stays off. The real
 * power unit (ring_power) runs the ship steps on the simulated chip. A scanner over BabbleSim: tests/bsim/factory. */
#include "common.h"

ZTEST_SUITE(factory_ship, NULL, NULL, fx_before, fx_after, NULL);

static void cb_level(uint8_t level)
{
	ARG_UNUSED(level);
}

static void cb_vbus(bool present)
{
	ARG_UNUSED(present);
}

static void cb_cerr(uint8_t reason, uint8_t sensor)
{
	ARG_UNUSED(reason);
	ARG_UNUSED(sensor);
}

static void cb_ilim(bool first, uint16_t mv, uint32_t count)
{
	ARG_UNUSED(first);
	ARG_UNUSED(mv);
	ARG_UNUSED(count);
}

static void cb_log(uint16_t code, const uint8_t *args, size_t n)
{
	ARG_UNUSED(code);
	ARG_UNUSED(args);
	ARG_UNUSED(n);
}

static void window(uint8_t sub)
{
	static const struct rpw_cb cbs = { .level = cb_level, .vbus = cb_vbus, .charge_error = cb_cerr, .ilim = cb_ilim,
					   .log = cb_log };
	struct rhw_pmic_sample s = { .mv = 3900, .ua = 3000, .temp_c_x10 = 250, .die_c_x10 = 300 };
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;

	rhw_sim_pmic_script(&s, 1);
	rhw_sim_pmic_vbus(true);
	zassert_ok(rpw_start(&cbs));
	k_sleep(K_MSEC(20));
	rhw_sim_log_clear();

	/* the command is accepted in FACTORY_TEST: the beacon starts at once */
	zassert_equal(fx_do1(sub, true, out, &n, &eff), 0);
	zassert_equal(out[0], 0);
	zassert_equal(eff, sub == 0x7F ? RFA_EFFECT_SHIP_ENTER : RFA_EFFECT_SHIP_SAMPLE);
	zassert_equal(fx_count(RHW_EV_BEACON_START), 1, "the beacon started");
	zassert_equal(fx_count(RHW_EV_BEACON_STOP), 0, "and runs while VBUS is on");

	/* the jig removes VBUS 700 ms after the ship steps began; the join's step 2 to 5 are rpw_ship */
	int64_t t = rhw_clock()->now_ms();

	rhw_sim_vbus_at(t + 700, false);
	(void)rpw_ship(rfa_beacon_stop);

	int32_t st = fx_find(RHW_EV_BEACON_START, 0);
	int32_t vb = -1;
	struct rhw_sim_ev e;

	for (uint32_t i = 0; i < rhw_sim_log_count(); i++) {
		zassert_true(rhw_sim_log_get(i, &e));
		if (e.kind == RHW_EV_PMIC_VBUS && e.a0 == 0) {
			vb = (int32_t)i;
			break;
		}
	}
	int32_t sp = fx_find(RHW_EV_BEACON_STOP, 0);
	int32_t ship = fx_find(RHW_EV_PMIC_SHIP, 0);
	int32_t cfg = fx_find(RHW_EV_PMIC_SHPHLD_CFG, 0);

	zassert_true(st >= 0 && vb >= 0 && sp >= 0 && ship >= 0 && cfg >= 0, "start %d vbus %d stop %d ship %d", st, vb, sp, ship);
	zassert_true(st < cfg, "advertising starts before the ship steps wait for VBUS");
	zassert_true(st < vb, "the beacon was on while VBUS was still present");
	zassert_true(sp < ship, "the beacon stops before the ship task, not after it (index %d against %d)", sp, ship);
	zassert_true(sp > vb, "and after VBUS was removed");
	zassert_true(fx_ev(sp).t_us - fx_ev(vb).t_us < 1000000, "stopped within 1 s of VBUS removal: %lld us",
		     fx_ev(sp).t_us - fx_ev(vb).t_us);
	zassert_equal(fx_count(RHW_EV_BEACON_STOP), 1, "stopped once");
	zassert_equal(fx_count(RHW_EV_BEACON_START), 1);

	/* and none for 60 s */
	k_sleep(K_SECONDS(60));
	zassert_equal(fx_count(RHW_EV_BEACON_START), 1, "no new start in the next 60 s");
	struct rhw_sim_beacon b;

	rhw_sim_beacon_get(&b);
	zassert_false(b.running, "off");
}

ZTEST(factory_ship, test_beacon_window)
{
	window(0x7F);
}

ZTEST(factory_ship, test_beacon_window_sample)
{
	window(0x7E);
}

/* The beacon is not connectable, every 100 ms, at 0 dBm, named "Ring" and the last 4 hex digits of the device id. */
ZTEST(factory_ship, test_beacon_name)
{
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;
	struct rhw_sim_beacon b;
	char name[RFA_NAME_BYTES];

	/* the simulated chip's default id 0x0123456789ABCDEF ends in CDEF */
	zassert_equal(fx_do1(0x7F, true, out, &n, &eff), 0);
	rhw_sim_beacon_get(&b);
	zassert_true(b.running);
	zassert_equal(strcmp(b.name, "RingCDEF"), 0, "name '%s'", b.name);
	zassert_equal(b.interval_ms, 100, "every 100 ms (FW l.1057)");
	zassert_equal(b.tx_dbm, 0, "at 0 dBm (FW l.1057)");
	zassert_false(b.connectable, "advertising that cannot be connected to (FW l.1057)");
	zassert_equal(b.starts, 1);
	rfa_beacon_stop();
	zassert_equal(fx_count(RHW_EV_BEACON_STOP), 1);
	rfa_beacon_stop();
	zassert_equal(fx_count(RHW_EV_BEACON_STOP), 1, "a second stop does nothing");

	/* other ids: the last four hex digits, upper case, leading zeros kept */
	rhw_sim_clock_device_id(0xDEADBEEF12340A0Full);
	fx_flag(true); /* SHIP_ENTER cleared the flag */
	zassert_equal(fx_do1(0x7E, true, out, &n, &eff), 0);
	rhw_sim_beacon_get(&b);
	zassert_equal(strcmp(b.name, "Ring0A0F"), 0, "name '%s'", b.name);
	zassert_false(b.connectable);
	rfa_beacon_stop();

	/* the pure name */
	zassert_equal(rfa_beacon_name(0x000000000000F000ull, name), RREC_BEACON_NAME_LEN);
	zassert_equal(strcmp(name, "RingF000"), 0);
	zassert_equal(rfa_beacon_name(0x1111111111110000ull, name), 8);
	zassert_equal(strcmp(name, "Ring0000"), 0);
}
