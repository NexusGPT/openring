/* Suite power_report (software step 6, unit U5): the GET_BATTERY values (FW l.702) and the values for SCR_CHARGING
 * (FW l.374). Rows X13 and C39. */
#include "common.h"

ZTEST_SUITE(power_report, NULL, NULL, pw_before, NULL, NULL);

/* FW l.702: charging state 0 off, 1 trickle, 2 constant current, 3 constant voltage, 4 full, 5 error: the byte after
 * the two u16 values. A latched error reads 5 whatever the state. */
ZTEST(power_report, test_charge_state_codes)
{
	uint8_t b[RREC_GET_BATTERY_BYTES];

	pw_script1(3900, 0);
	pw_start();
	for (int s = 0; s <= 5; s++) {
		rhw_sim_pmic_charge_state(s);
		memset(b, 0xEE, sizeof(b));
		zassert_ok(rpw_battery_report(b));
		zassert_equal(b[4], s, "charger state %d", s);
	}
	/* an error latched while the state still reads constant current: error */
	rhw_sim_pmic_charge_state(2);
	rhw_sim_pmic_charge_error(0x01, 0x02);
	rhw_sim_pmic_charge_state(2);
	zassert_ok(rpw_battery_report(b));
	zassert_equal(b[4], 5);
	/* automatic state: off without VBUS */
	pw_before(NULL);
	pw_script1(3900, 0);
	pw_start();
	zassert_ok(rpw_battery_report(b));
	zassert_equal(b[4], 0);
	/* the pure mapping */
	zassert_equal(rpwl_charge_code(0, 0), 0);
	zassert_equal(rpwl_charge_code(3, 0), 3);
	zassert_equal(rpwl_charge_code(4, 0), 4);
	zassert_equal(rpwl_charge_code(5, 0), 5);
	zassert_equal(rpwl_charge_code(1, 7), 5);
	zassert_equal(rpwl_charge_code(9, 0), 5);
}

/* The nine bytes (FW l.702: battery_mv u16, soc_percent_x10 u16, charging state u8, die temp 0.1 C i16, time to full
 * in minutes u16; little endian, FW l.70). 3,912 mV = 0x0F48, 73.4 % = 734 = 0x02DE, state CC, die 30.0 C = 300 =
 * 0x012C. Not charging: time to full unknown, 0xFFFF. */
ZTEST(power_report, test_battery_bytes_layout)
{
	static const uint8_t want[RREC_GET_BATTERY_BYTES] = { 0x48, 0x0F, 0xDE, 0x02, 0x02, 0x2C, 0x01, 0xFF, 0xFF };
	uint8_t b[RREC_GET_BATTERY_BYTES];

	pw_script1(3912, 0);
	rhw_sim_gauge_start_soc(734);
	pw_start();
	rhw_sim_pmic_charge_state(2);
	zassert_ok(rpw_battery_report(b));
	zassert_mem_equal(b, want, sizeof(want));
	/* a negative die temperature: -5.5 C = -55 = 0xFFC9 */
	rpwl_battery_bytes(3300, 20, 0, -55, 0, b);
	zassert_equal(b[5], 0xC9);
	zassert_equal(b[6], 0xFF);
}

/* Time to full from the gauge while charging: 17.6 mAh cell at 80 %, charging at 15,000 uA: 20 % = 3.52 mAh =
 * 12,672 mA.s, 844 s, rounded up to 15 minutes. And the values for SCR_CHARGING (FW l.374): charging, not full. */
ZTEST(power_report, test_values_and_time_to_full)
{
	struct rpw_values v;
	uint8_t b[RREC_GET_BATTERY_BYTES];

	rhw_sim_pmic_vbus(true);
	pw_script1(4000, -15000);
	rhw_sim_gauge_start_soc(800);
	pw_start();                         /* VBUS present: charge on */
	zassert_ok(rpw_battery_report(b));
	rpw_values(&v);
	zassert_true(v.vbus);
	zassert_true(v.charging, "constant current with VBUS and the charger on");
	zassert_false(v.full);
	zassert_equal(v.battery_mv, 4000);
	zassert_equal(v.soc_x10, 800);
	zassert_equal(v.to_full_min, 15);
	zassert_equal(b[7] | (b[8] << 8), 15);
	zassert_equal(v.die_c_x10, 300);
	rhw_sim_pmic_charge_state(4);       /* full */
	zassert_ok(rpw_battery_report(b));
	rpw_values(&v);
	zassert_equal(b[4], 4);
	/* values change at the next sample; the pure rounding */
	zassert_equal(rpwl_ttf_min(0), 0);
	zassert_equal(rpwl_ttf_min(1), 1);
	zassert_equal(rpwl_ttf_min(60), 1);
	zassert_equal(rpwl_ttf_min(61), 2);
	zassert_equal(rpwl_ttf_min(UINT32_MAX), 0xFFFF);
	zassert_equal(rpwl_ttf_min(60u * 70000u), 65534);
}

/* Before rpw_start there is nothing to report. */
ZTEST(power_report, test_report_before_start)
{
	uint8_t b[RREC_GET_BATTERY_BYTES];
	struct rpw_values v;

	zassert_equal(rpw_battery_report(b), -EAGAIN);
	rpw_values(&v);
	zassert_equal(v.to_full_min, UINT16_MAX);
	zassert_false(v.vbus);
}
