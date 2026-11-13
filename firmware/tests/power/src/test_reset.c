/* Suite power_reset (software step 6, unit U5): after a wake BOOT reads RSTCAUSE and the charger error log, writes
 * them into the event log and clears them (FW l.943, l.996). Row P14. */
#include "common.h"

ZTEST_SUITE(power_reset, NULL, NULL, pw_before, NULL, NULL);

/* rpw_boot_causes() takes the log hook itself (rpw_start has not run yet at boot). */
static void boot_log(uint16_t code, const uint8_t *args, size_t n)
{
	if (cap.n_log < CAP_MAX) {
		cap.log[cap.n_log].code = code;
		cap.log[cap.n_log].n = n;
		for (size_t i = 0; i < n && i < sizeof(cap.log[0].args); i++) {
			cap.log[cap.n_log].args[i] = args[i];
		}
	}
	cap.n_log++;
}

/* FW l.996: each of the seven bits (SHIPMODEEXIT bit 0, BOOTMONITORTIMEOUT 1, WATCHDOGTIMEOUT 2, LONGPRESSTIMEOUT 3,
 * THERMALSHUTDOWN 4, VSYSLOW 5, SWRESET 6) with the two charger error values beside it: one record
 * (code 0x0220: RSTCAUSE, CHARGERERRREASON, CHARGERERRSENSOR); the read comes before the clear; after it the chip
 * holds nothing. */
ZTEST(power_reset, test_causes_logged_then_cleared)
{
	for (uint8_t bit = 0; bit < 7; bit++) {
		uint8_t rc = 0xFF, er = 0xFF, es = 0xFF;
		int32_t rd, cl;

		pw_before(NULL);
		rhw_sim_pmic_set_reset_causes((uint8_t)(1u << bit), (uint8_t)(0x01 + bit), (uint8_t)(0x10 + bit));
		zassert_ok(rpw_boot_causes(boot_log), "bit %u", bit);
		zassert_equal(cap.n_log, 1, "bit %u: one record", bit);
		zassert_equal(cap.log[0].code, 0x0220);
		zassert_equal(cap.log[0].n, 3);
		zassert_equal(cap.log[0].args[0], 1u << bit, "bit %u in the record", bit);
		zassert_equal(cap.log[0].args[1], 0x01 + bit);
		zassert_equal(cap.log[0].args[2], 0x10 + bit);
		rd = pw_find(RHW_EV_PMIC_RST_READ, 0);
		cl = pw_find(RHW_EV_PMIC_RST_CLEAR, 0);
		zassert_true(rd >= 0 && cl > rd, "bit %u: read, then clear", bit);
		zassert_ok(rhw_pmic()->reset_causes(&rc, &er, &es));
		zassert_equal(rc, 0, "bit %u: RSTCAUSE cleared", bit);
		zassert_equal(er, 0, "bit %u: error reason cleared", bit);
		zassert_equal(es, 0, "bit %u: error sensor cleared", bit);
	}
}

/* All seven bits together, and nothing set: still one record (a boot with no cause is a fact too). */
ZTEST(power_reset, test_all_bits_and_none)
{
	rhw_sim_pmic_set_reset_causes(0x7F, 0xAB, 0xCD);
	zassert_ok(rpw_boot_causes(boot_log));
	zassert_equal(cap.n_log, 1);
	zassert_equal(cap.log[0].args[0], 0x7F);
	zassert_equal(cap.log[0].args[1], 0xAB);
	zassert_equal(cap.log[0].args[2], 0xCD);
	zassert_equal(rpwl_cause_count(0x7F), 7);
	zassert_equal(rpwl_cause_count(0x00), 0);
	zassert_equal(rpwl_cause_count(0x80), 0, "bit 7 is no cause");

	pw_before(NULL);
	zassert_ok(rpw_boot_causes(boot_log));
	zassert_equal(cap.n_log, 1);
	zassert_equal(cap.log[0].args[0], 0);
}
