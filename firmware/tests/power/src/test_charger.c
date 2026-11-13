/* Suite power_charger (software step 6, unit U5): "charge on" and "charge off" (FW l.129), the order of the writes
 * (FW l.894), charge on at every VBUS appearance in every state (R-CHG, ruling R8, FW l.210). Rows C6, C22, P3. */
#include "common.h"

ZTEST_SUITE(power_charger, NULL, NULL, pw_before, NULL, NULL);

/* ENABLE entries of the log with this value (1 = enable, 0 = disable) */
static uint32_t n_enable(int64_t on)
{
	uint32_t n = 0;

	for (int32_t i = pw_find(RHW_EV_PMIC_CHG_ENABLE, 0); i >= 0; i = pw_find(RHW_EV_PMIC_CHG_ENABLE, i + 1)) {
		if (pw_ev(i).a0 == on) {
			n++;
		}
	}
	return n;
}

/* FW l.129: charge on = enabled and set to CHARGE_CURRENT; already on, nothing changes. FW l.878: 15,000 uA.
 * FW l.894: disable, write the current, enable. */
ZTEST(power_charger, test_charge_on_twice_writes_once)
{
	uint32_t n1;

	pw_start();
	rhw_sim_log_clear();
	zassert_ok(rpw_charge_on());
	zassert_equal(n_enable(1), 1, "enabled once");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_CHG_CURRENT), 1, "current written once");
	zassert_true(rhw_sim_pmic_charger_on());
	zassert_equal(rhw_sim_pmic_charger_ua(), 15000);
	n1 = rhw_sim_log_count();
	zassert_ok(rpw_charge_on());
	zassert_equal(n_enable(1), 1, "the second call enabled nothing");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_CHG_CURRENT), 1, "the second call wrote nothing");
	zassert_equal(rhw_sim_log_count(), n1, "the second call made no call at all");
}

/* FW l.129: charge off = the charger is disabled. A later "charge on" writes again. */
ZTEST(power_charger, test_charge_off)
{
	pw_start();
	zassert_ok(rpw_charge_on());
	zassert_true(rhw_sim_pmic_charger_on());
	rhw_sim_log_clear();
	zassert_ok(rpw_charge_off());
	zassert_false(rhw_sim_pmic_charger_on());
	zassert_equal(rhw_sim_log_count(), 1);
	zassert_equal(pw_ev(0).kind, RHW_EV_PMIC_CHG_ENABLE);
	zassert_equal(pw_ev(0).a0, 0);
	zassert_ok(rpw_charge_on());
	zassert_true(rhw_sim_pmic_charger_on());
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_CHG_CURRENT), 1, "on after off writes the sequence again");
}

/* FW l.894: the charger is disabled before the current register is written and enabled after. The chip is found
 * enabled (it came up so); the write of the current must find it disabled. */
ZTEST(power_charger, test_disable_write_enable_order)
{
	int32_t a, b, c;

	pw_start();
	zassert_ok(rhw_pmic()->charger_enable(true));
	rhw_sim_log_clear();
	zassert_ok(rpw_charge_on());
	zassert_equal(rhw_sim_log_count(), 3);
	a = 0;
	b = 1;
	c = 2;
	zassert_equal(pw_ev(a).kind, RHW_EV_PMIC_CHG_ENABLE);
	zassert_equal(pw_ev(a).a0, 0, "first: disable");
	zassert_equal(pw_ev(b).kind, RHW_EV_PMIC_CHG_CURRENT);
	zassert_equal(pw_ev(b).a0, 15000);
	zassert_equal(pw_ev(b).a1, 0, "the current is written while the charger is disabled");
	zassert_equal(pw_ev(c).kind, RHW_EV_PMIC_CHG_ENABLE);
	zassert_equal(pw_ev(c).a0, 1, "last: enable");
}

/* FW l.210 and ruling R8: charge on at every VBUS appearance, in every state, BOOT and RECOVERY included, before
 * the VBUS callback goes out. Each state: VBUS out, VBUS in. */
ZTEST(power_charger, test_on_at_every_vbus)
{
	pw_start();
	zassert_false(rhw_sim_pmic_charger_on());
	for (uint8_t st = 0; st < PW_STATES; st++) {
		uint32_t cur_before, nv;

		rpw_state(st);
		rhw_sim_pmic_vbus(false);
		k_sleep(K_MSEC(20));
		cur_before = rhw_sim_log_count_kind(RHW_EV_PMIC_CHG_CURRENT);
		nv = cap.n_vbus;
		rhw_sim_pmic_vbus(true);
		k_sleep(K_MSEC(20));
		zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_CHG_CURRENT), cur_before + 1,
			      "state %u: charge on written at VBUS in", st);
		zassert_true(rhw_sim_pmic_charger_on(), "state %u: charger on", st);
		zassert_equal(cap.n_vbus, nv + 1, "state %u: VBUS callback", st);
		zassert_true(cap.vbus[nv].present);
		zassert_true(cap.vbus[nv].charger_on, "state %u: charge on done before the callback", st);
	}
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_CHG_CURRENT), PW_STATES, "once per state, 14 states");
	zassert_equal(RC_ST_BOOT, 2);
	zassert_equal(RC_ST_RECOVERY, 3);
}

/* FW l.893: VBUS present at start: charge on at once, then the callback. */
ZTEST(power_charger, test_on_at_start_with_vbus)
{
	rhw_sim_pmic_vbus(true);
	pw_start();
	zassert_true(rhw_sim_pmic_charger_on(), "on when rpw_start returns");
	k_sleep(K_MSEC(20));
	zassert_equal(cap.n_vbus, 1);
	zassert_true(cap.vbus[0].present);
	zassert_true(cap.vbus[0].charger_on);
}

/* A charge error: the chip's latched values reach the callback (FW l.176). */
ZTEST(power_charger, test_charge_error_reaches_callback)
{
	pw_start();
	rhw_sim_pmic_charge_error(0x12, 0x34);
	k_sleep(K_MSEC(20));
	zassert_equal(cap.n_cerr, 1);
	zassert_equal(cap.cerr[0].reason, 0x12);
	zassert_equal(cap.cerr[0].sensor, 0x34);
}
