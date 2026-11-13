/* Suite factory_xtal (software step 6, unit U8): T-XTAL (0x71, FW l.1033): the GRTC against the USB start-of-frame
 * count over 10 s, within 50 ppm. Rows T21. The measurement itself is not provable here (the simulation has no
 * start-of-frame count): the counts come from the test, the ppm arithmetic is checked. Expected values are typed from
 * the definition: a 32.768 kHz crystal gives 32.768 ticks per start-of-frame (1 ms). */
#include "common.h"

ZTEST_SUITE(factory_xtal, NULL, NULL, fx_before, fx_after, NULL);

ZTEST(factory_xtal, test_ppm_arithmetic)
{
	bool ok;

	/* 10,000 frames = 10 s = 327,680 ticks exactly */
	zassert_equal(rfa_ppm_x10(327680, 10000, &ok), 0);
	zassert_true(ok);
	/* 16 ticks over: 16 / 327,680 = 48.83 ppm -> 488 tenths; 16 under: -488 */
	zassert_equal(rfa_ppm_x10(327696, 10000, &ok), 488);
	zassert_equal(rfa_ppm_x10(327664, 10000, &ok), -488);
	/* 17 ticks over: 51.88 ppm */
	zassert_equal(rfa_ppm_x10(327697, 10000, &ok), 518);
	/* no frame counted: no result */
	(void)rfa_ppm_x10(327680, 0, &ok);
	zassert_false(ok);
	/* 50 ppm is the limit (FW l.1033): 500 tenths pass, 501 fail, both signs */
	zassert_true(rfa_ppm_within(500));
	zassert_false(rfa_ppm_within(501));
	zassert_true(rfa_ppm_within(-500));
	zassert_false(rfa_ppm_within(-501));

	/* through the request: no start-of-frame count in the simulation: the stand-in answers -ENOTSUP, the test fails */
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;

	zassert_equal(fx_do1(0x71, true, out, &n, &eff), 0);
	zassert_equal(n, 17);
	zassert_equal(out[0], 1, "no count: fail");
	/* 48.8 ppm passes, 51.9 fails */
	fx_xtal_rc = 0;
	fx_xtal_sof = 10000;
	fx_xtal_grtc = 327696;
	zassert_equal(fx_do1(0x71, true, out, &n, &eff), 0);
	zassert_equal(out[0], 0);
	zassert_equal((int32_t)fx_u32(&out[1]), 488);
	fx_xtal_grtc = 327697;
	zassert_equal(fx_do1(0x71, true, out, &n, &eff), 0);
	zassert_equal(out[0], 1);
	zassert_equal((int32_t)fx_u32(&out[1]), 518);
	fx_xtal_grtc = 327664;
	zassert_equal(fx_do1(0x71, true, out, &n, &eff), 0);
	zassert_equal(out[0], 0, "slow crystal by 48.8 ppm passes");
	/* zero frames: fail */
	fx_xtal_sof = 0;
	zassert_equal(fx_do1(0x71, true, out, &n, &eff), 0);
	zassert_equal(out[0], 1);
}
