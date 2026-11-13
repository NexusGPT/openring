/* Suite factory_radio (software step 6, unit U8): T-RADIO (0x60, FW l.1031): advertise 10 s at 0 dBm, 100 ms interval.
 * Rows T19. The received power is the jig's (not provable here); a scanner over BabbleSim is tests/bsim/factory. */
#include "common.h"

ZTEST_SUITE(factory_radio, NULL, NULL, fx_before, fx_after, NULL);

ZTEST(factory_radio, test_adv_parameters)
{
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;
	struct rhw_sim_ev e;
	struct rhw_sim_beacon b;

	rhw_sim_log_clear();
	zassert_equal(fx_do1(0x60, true, out, &n, &eff), 0);
	zassert_equal(n, 1);
	zassert_equal(out[0], 0, "pass");
	zassert_equal(eff, RFA_EFFECT_NONE);
	zassert_equal(fx_count(RHW_EV_BEACON_START), 1, "one advertising start");
	zassert_equal(fx_count(RHW_EV_BEACON_STOP), 1, "one stop");
	int32_t st = fx_find(RHW_EV_BEACON_START, 0);
	int32_t sp = fx_find(RHW_EV_BEACON_STOP, 0);

	zassert_true(st >= 0 && sp > st);
	e = fx_ev(st);
	zassert_equal(e.a0, 100, "interval 100 ms (FW l.1031)");
	zassert_equal(e.a1, 0, "0 dBm (FW l.1031)");
	zassert_equal(e.a2, 0, "not connectable");
	zassert_equal(strcmp(e.caller, "RingCDEF"), 0, "the ring's name, '%s'", e.caller);
	zassert_within(fx_ev(sp).t_us - e.t_us, 10000000, 20000, "advertises 10 s (FW l.1031): %lld us", fx_ev(sp).t_us - e.t_us);
	rhw_sim_beacon_get(&b);
	zassert_false(b.running, "off again");
}
