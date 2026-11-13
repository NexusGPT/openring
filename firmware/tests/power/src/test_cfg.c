/* Suite power_cfg (software step 6, unit U5): CHARGE_CURRENT, VBUS is an input only, the power-fail warning is not
 * used. Rows P2 (runtime part), P17, P19. The build assertions of P2 are proven by the broken copies cc_*. */
#include "common.h"

ZTEST_SUITE(power_cfg, NULL, NULL, pw_before, NULL, NULL);

/* The calls that exist on the power chip interface (rhw.h) and the event kinds a full session may log: the session
 * starts, charges, samples, hits the current limit, reports, ships and boots. */
static bool kind_allowed(uint16_t k)
{
	switch (k) {
	case RHW_EV_PMIC_CHG_ENABLE:
	case RHW_EV_PMIC_CHG_CURRENT:
	case RHW_EV_PMIC_CHG_STATUS:
	case RHW_EV_PMIC_SAMPLE:
	case RHW_EV_PMIC_ILIM:
	case RHW_EV_PMIC_RST_READ:
	case RHW_EV_PMIC_RST_CLEAR:
	case RHW_EV_PMIC_SHPHLD_CFG:
	case RHW_EV_PMIC_SHPHLD_STROBE:
	case RHW_EV_PMIC_SHIP:
	case RHW_EV_SHIP_REFUSED:
	case RHW_EV_GAUGE_START:
	case RHW_EV_GAUGE_PROCESS:
	case RHW_EV_PMIC_VBUS:             /* only the test's own calls write this kind */
		return true;
	default:
		return false;
	}
}

/* FW l.878, l.894 (rule 2): 15,000 uA; a multiple of 500 inside 4,000 to 100,000 and at most 17,600; the value that
 * reaches the chip is the constant. */
ZTEST(power_cfg, test_charge_current_constant)
{
	uint32_t cc = rpw_charge_current_ua();

	zassert_equal(cc, 15000, "FW l.878: 15 mA");
	zassert_equal(cc, rpwl_charge_current_ua());
	zassert_true(cc <= 17600 && cc >= 4000 && cc <= 100000 && cc % 500 == 0);
	pw_start();
	zassert_ok(rpw_charge_on());
	zassert_equal(rhw_sim_pmic_charger_ua(), 15000);
}

/* FW l.977 (8.6 rule 1): VBUS is an input only. The power chip interface has 14 calls and none drives VBUS (the
 * frozen header rhw.h; a new member would change the size), and a full session makes no call of any other kind than
 * those of that interface; the VBUS entries in the log are the test's own (counted below). */
ZTEST(power_cfg, test_no_vbus_output_call)
{
	uint32_t own = 0;

	zassert_equal(sizeof(struct rhw_pmic_api), 14 * sizeof(void *),
		      "14 calls: rail_set rail_get charger_enable charger_current charge_status sample ilim_active "
		      "reset_causes reset_causes_clear shphld_config shphld_strobe ship_task vbus_present set_callbacks");
	zassert_equal(sizeof(struct rhw_pmic_cb), 2 * sizeof(void *), "two callbacks in: VBUS and charge error");
	pw_script1(3900, 0);
	rpw_state(RC_ST_RECORDING);
	pw_start();
	rhw_sim_pmic_vbus(true);            /* the test's own VBUS: 1 */
	k_sleep(K_MSEC(50));
	rhw_sim_pmic_vbus(false);           /* 2 */
	own = 2;
	k_sleep(K_MSEC(3500));
	zassert_ok(rpw_charge_on());
	zassert_ok(rpw_charge_off());
	(void)rpw_ship(NULL);
	for (uint32_t i = 0; i < rhw_sim_log_count(); i++) {
		struct rhw_sim_ev e = pw_ev(i);

		zassert_true(kind_allowed(e.kind), "entry %u has kind %u", i, e.kind);
	}
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_VBUS), own, "VBUS changed only where the test changed it");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_RAIL), 0, "and no rail call at all (ruling: no rail in this unit)");
}

/* FW l.997: the power-fail warning is not used: POFCONFIG and VSYSPOF stay at their reset values. The interface has
 * no call that could write them (the size check above) and the same session leaves only the kinds listed above in
 * the log: no entry of any other kind, so no register write besides the charger, SHPHLD and ship ones. */
ZTEST(power_cfg, test_pof_untouched)
{
	pw_script1(3900, 0);
	rpw_state(RC_ST_RECORDING);
	pw_start();
	zassert_ok(rpw_charge_on());
	k_sleep(K_MSEC(2500));
	zassert_ok(rpw_boot_causes(NULL));
	(void)rpw_ship(NULL);
	zassert_equal(sizeof(struct rhw_pmic_api), 14 * sizeof(void *));
	for (uint32_t i = 0; i < rhw_sim_log_count(); i++) {
		zassert_true(kind_allowed(pw_ev(i).kind), "entry %u has kind %u", i, pw_ev(i).kind);
	}
}
