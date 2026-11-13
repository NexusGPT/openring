/* Suite factory_cmd (software step 6, unit U8): the gate, the flag rules, the removed sub-command, the result layouts.
 * Rows C20, T11, T12, T23, X17 (the factory half). Expected values are typed from design/firmware.md 9.3 (l.1019 to
 * l.1037) and l.689 (status codes), never taken from the code under test. */
#include "common.h"

ZTEST_SUITE(factory_cmd, NULL, NULL, fx_before, fx_after, NULL);

/* the requests that need nothing but the sub-command byte, typed from l.1019 to l.1035, with the two that carry an
 * argument */
static const uint8_t plain[] = { 0x01, 0x02, 0x20, 0x40, 0x41, 0x50, 0x60, 0x70, 0x71, 0x7E, 0x7F };
static const uint8_t mic1[] = { 0x10, 0x01 };
static const uint8_t joy[] = { 0x30, 0xE8, 0x03 };   /* window 1,000 ms */
static const uint8_t centre[] = { 0x31, 0xE8, 0x03 };

#define NOT_ALLOWED 11  /* FW l.689 */
#define BAD_ARG 4       /* FW l.689 */

static uint32_t side_effects(void)
{
	return fx_count(RHW_EV_BEACON_START) + fx_count(RHW_EV_PERSIST_SAVE) + fx_count(RHW_EV_PMIC_RAIL) +
	       fx_count(RHW_EV_MOTOR) + fx_count(RHW_EV_MIC_START) + fx_rec_calls + fx_frames;
}

/* T11, C20: FACTORY ENTER only with the flag set; the flag is cleared only by SHIP_ENTER; SHIP_SAMPLE keeps it; with the
 * flag clear every FACTORY request answers NOT_ALLOWED (FW l.1019). */
ZTEST(factory_cmd, test_flag_rules)
{
	uint8_t out[RFA_OUT_MAX];
	size_t n;
	enum rfa_effect eff;
	struct rhw_persist p;

	/* flag clear: NOT_ALLOWED for every sub-command, in TRANSFER and in FACTORY_TEST, and nothing happens */
	fx_flag(false);
	for (int ft = 0; ft < 2; ft++) {
		for (size_t i = 0; i < sizeof(plain); i++) {
			n = 99;
			eff = RFA_EFFECT_ENTER;
			zassert_equal(fx_do(&plain[i], 1, ft != 0, out, &n, &eff), NOT_ALLOWED, "flag clear: sub 0x%02x ft %d",
				      plain[i], ft);
			zassert_equal(n, 0, "no response bytes");
			zassert_equal(eff, RFA_EFFECT_NONE, "no effect");
		}
		zassert_equal(fx_do(mic1, sizeof(mic1), ft != 0, out, &n, &eff), NOT_ALLOWED);
		zassert_equal(fx_do(joy, sizeof(joy), ft != 0, out, &n, &eff), NOT_ALLOWED);
		zassert_equal(fx_do(centre, sizeof(centre), ft != 0, out, &n, &eff), NOT_ALLOWED);
	}
	zassert_equal(side_effects(), 0, "a refused request does nothing: %u", side_effects());

	/* flag set: ENTER in TRANSFER is accepted and keeps the flag */
	fx_flag(true);
	zassert_equal(fx_do1(0x01, false, out, &n, &eff), 0);
	zassert_equal(eff, RFA_EFFECT_ENTER);
	zassert_equal(n, 1);
	zassert_equal(out[0], 0, "result pass");
	zassert_true(rsy_factory_flag(), "ENTER keeps the flag");

	/* EXIT: reboot effect, flag kept */
	zassert_equal(fx_do1(0x02, true, out, &n, &eff), 0);
	zassert_equal(eff, RFA_EFFECT_EXIT);
	zassert_true(rsy_factory_flag(), "EXIT keeps the flag");

	/* SHIP_SAMPLE (0x7E): ship mode, the flag stays 1, also after a reset: the ring can be tested again */
	zassert_equal(fx_do1(0x7E, true, out, &n, &eff), 0);
	zassert_equal(eff, RFA_EFFECT_SHIP_SAMPLE);
	zassert_equal(out[0], 0);
	rhw_sim_persist_get(&p);
	zassert_equal(p.factory_flag, 1, "SHIP_SAMPLE keeps the flag in the settings");
	zassert_equal(fx_count(RHW_EV_PERSIST_SAVE), 0, "SHIP_SAMPLE writes no setting");
	rfa_beacon_stop();
	fx_next_boot();
	zassert_true(rsy_factory_flag());
	zassert_equal(fx_do1(0x01, false, out, &n, &eff), 0, "after the wake FACTORY ENTER works again");
	zassert_equal(eff, RFA_EFFECT_ENTER);

	/* SHIP_ENTER (0x7F): the flag is cleared, and after a reset ENTER is refused */
	zassert_equal(fx_do1(0x7F, true, out, &n, &eff), 0);
	zassert_equal(eff, RFA_EFFECT_SHIP_ENTER);
	rhw_sim_persist_get(&p);
	zassert_equal(p.factory_flag, 0, "SHIP_ENTER clears the flag in the settings");
	zassert_false(rsy_factory_flag());
	rfa_beacon_stop();
	fx_next_boot();
	zassert_equal(fx_do1(0x01, false, out, &n, &eff), NOT_ALLOWED, "flag clear after SHIP_ENTER");
	zassert_equal(eff, RFA_EFFECT_NONE);

	/* the other sub-commands never clear it */
	fx_flag(true);
	zassert_equal(fx_do1(0x02, true, out, &n, &eff), 0);
	zassert_equal(fx_do1(0x70, true, out, &n, &eff), 0);
	zassert_true(rsy_factory_flag(), "no other sub-command clears the flag");

	/* outside FACTORY_TEST nothing but ENTER; in FACTORY_TEST ENTER is not answered again; the ship commands only in
	 * FACTORY_TEST (ruling R20: the beacon exists only there) */
	rhw_sim_log_clear();
	zassert_equal(fx_do1(0x20, false, out, &n, &eff), NOT_ALLOWED);
	zassert_equal(fx_do1(0x7F, false, out, &n, &eff), NOT_ALLOWED);
	zassert_equal(fx_do1(0x7E, false, out, &n, &eff), NOT_ALLOWED);
	zassert_equal(fx_do1(0x01, true, out, &n, &eff), NOT_ALLOWED);
	zassert_equal(fx_count(RHW_EV_BEACON_START), 0, "no beacon outside FACTORY_TEST");
	zassert_true(rsy_factory_flag(), "a refused SHIP_ENTER keeps the flag");
}

/* T23: sub-command 0x11 answers BAD_ARG (FW l.1037); so do unknown sub-commands and wrong argument lengths. */
ZTEST(factory_cmd, test_0x11_bad_arg)
{
	uint8_t out[RFA_OUT_MAX];
	size_t n = 99;
	enum rfa_effect eff = RFA_EFFECT_ENTER;
	const uint8_t x11[] = { 0x11 };
	const uint8_t x11a[] = { 0x11, 0x00 };
	const uint8_t x11b[] = { 0x11, 0x01, 0x02, 0x03 };

	zassert_equal(fx_do(x11, sizeof(x11), true, out, &n, &eff), BAD_ARG, "0x11 in FACTORY_TEST");
	zassert_equal(n, 0);
	zassert_equal(eff, RFA_EFFECT_NONE);
	zassert_equal(fx_do(x11a, sizeof(x11a), true, out, &n, &eff), BAD_ARG);
	zassert_equal(fx_do(x11b, sizeof(x11b), true, out, &n, &eff), BAD_ARG);
	zassert_equal(fx_do(x11, sizeof(x11), false, out, &n, &eff), BAD_ARG, "0x11 outside FACTORY_TEST");
	zassert_equal(side_effects(), 0, "the removed test runs nothing");
	/* unknown sub-commands and an empty request */
	for (unsigned s = 0; s < 256; s++) {
		bool known = false;

		for (size_t i = 0; i < sizeof(plain); i++) {
			known |= (plain[i] == s);
		}
		known |= (s == 0x10 || s == 0x30 || s == 0x31);
		if (known) {
			continue;
		}
		uint8_t r = (uint8_t)s;

		zassert_equal(fx_do(&r, 1, true, out, &n, &eff), BAD_ARG, "sub 0x%02x", s);
	}
	zassert_equal(fx_do(x11, 0, true, out, &n, &eff), BAD_ARG, "empty request");
	zassert_equal(side_effects(), 0);
}

/* wrong lengths and arguments (this unit's reading of the request layouts, rfa_logic.h) */
ZTEST(factory_cmd, test_bad_arguments)
{
	uint8_t out[RFA_OUT_MAX];
	size_t n;
	enum rfa_effect eff;
	const uint8_t m0[] = { 0x10, 0x00 };
	const uint8_t m3[] = { 0x10, 0x03 };
	const uint8_t m[] = { 0x10 };
	const uint8_t mx[] = { 0x10, 0x01, 0x01 };
	const uint8_t j0[] = { 0x30, 0x00, 0x00 };
	const uint8_t j10001[] = { 0x30, 0x11, 0x27 };
	const uint8_t j10000[] = { 0x30, 0x10, 0x27 };
	const uint8_t jshort[] = { 0x30, 0x10 };
	const uint8_t eextra[] = { 0x01, 0x00 };

	zassert_equal(fx_do(m0, sizeof(m0), true, out, &n, &eff), BAD_ARG);
	zassert_equal(fx_do(m3, sizeof(m3), true, out, &n, &eff), BAD_ARG);
	zassert_equal(fx_do(m, sizeof(m), true, out, &n, &eff), BAD_ARG);
	zassert_equal(fx_do(mx, sizeof(mx), true, out, &n, &eff), BAD_ARG);
	zassert_equal(fx_do(j0, sizeof(j0), true, out, &n, &eff), BAD_ARG, "window 0");
	zassert_equal(fx_do(j10001, sizeof(j10001), true, out, &n, &eff), BAD_ARG, "window above 10,000 ms");
	zassert_equal(fx_do(jshort, sizeof(jshort), true, out, &n, &eff), BAD_ARG);
	zassert_equal(fx_do(eextra, sizeof(eextra), false, out, &n, &eff), BAD_ARG);
	zassert_equal(side_effects(), 0);
	/* 10,000 ms is the largest window and is accepted (the test then runs its window) */
	zassert_equal(fx_do(j10000, sizeof(j10000), true, out, &n, &eff), 0);
	zassert_equal(out[0], 2, "no event in the window: timeout");
}

/* the pure layouts, typed byte for byte (little endian, FW l.70) */
ZTEST(factory_cmd, test_result_layout)
{
	uint8_t o[RFA_OUT_MAX];
	size_t n;

	/* result codes, FW l.1020 */
	zassert_equal(RREC_FAC_RESULT_PASS, 0);
	zassert_equal(RREC_FAC_RESULT_FAIL, 1);
	zassert_equal(RREC_FAC_RESULT_TIMEOUT, 2);

	/* T-MIC: result, rms L -230, rms R -233 (tenths of dBFS), runs 5 and 1,000 */
	n = rfa_put_mic(o, 0, -230, -233, 5, 1000);
	const uint8_t mic[] = { 0x00, 0x1A, 0xFF, 0x17, 0xFF, 0x05, 0, 0, 0, 0xE8, 0x03, 0, 0 };

	zassert_equal(n, sizeof(mic));
	zassert_mem_equal(o, mic, sizeof(mic));

	/* T-SIGN: result, four times 100, 1,100, 2,100, 3,100 ms */
	const int64_t t[4] = { 100, 1100, 2100, 3100 };
	const uint8_t sign[] = { 0x00, 0x64, 0, 0, 0, 0, 0, 0, 0, 0x4C, 0x04, 0, 0, 0, 0, 0, 0, 0x34, 0x08, 0, 0, 0, 0, 0, 0,
				 0x1C, 0x0C, 0, 0, 0, 0, 0, 0 };

	n = rfa_put_sign(o, 0, t);
	zassert_equal(n, sizeof(sign));
	zassert_mem_equal(o, sign, sizeof(sign));

	/* T-STORE: result, equal 1, write 1,000 us, read 2,000 us, deleted 3 */
	const uint8_t st[] = { 0x00, 0x01, 0xE8, 0x03, 0, 0, 0xD0, 0x07, 0, 0, 0x03, 0, 0, 0 };

	n = rfa_put_store(o, 0, true, 1000, 2000, 3);
	zassert_equal(n, sizeof(st));
	zassert_mem_equal(o, st, sizeof(st));

	/* T-JOY, T-CENTRE: result, dropped 0, count 2, (up at 100 ms), (long at 1,000 ms) */
	const struct rfa_evrec e[2] = { { RFA_IN_UP, 100 }, { RFA_IN_LONG, 1000 } };
	const uint8_t ev[] = { 0x00, 0x00, 0x02, 0x01, 0x64, 0, 0, 0, 0x09, 0xE8, 0x03, 0, 0 };

	n = rfa_put_events(o, 0, 0, e, 2);
	zassert_equal(n, sizeof(ev));
	zassert_mem_equal(o, ev, sizeof(ev));

	/* T-CHARGE through the request: state constant current (2), no error, 15,000 uA */
	struct rhw_pmic_sample s = { .mv = 3900, .ua = 15000, .temp_c_x10 = 250, .die_c_x10 = 300 };

	rhw_sim_pmic_script(&s, 1);
	rhw_sim_pmic_charge_state(2);
	enum rfa_effect eff;
	const uint8_t chg[] = { 0x00, 0x02, 0x00, 0x98, 0x3A, 0x00, 0x00 };

	zassert_equal(fx_do1(0x70, true, o, &n, &eff), 0);
	zassert_equal(n, sizeof(chg));
	zassert_mem_equal(o, chg, sizeof(chg));

	/* T-MOTOR through the request: VBAT 3,900 mV, 3,870 mV during the pulse, dip 30 mV */
	rhw_sim_pmic_motor_dip(30);
	const uint8_t mot[] = { 0x00, 0x3C, 0x0F, 0x1E, 0x0F, 0x1E, 0x00 };

	zassert_equal(fx_do1(0x40, true, o, &n, &eff), 0);
	zassert_equal(n, sizeof(mot));
	zassert_mem_equal(o, mot, sizeof(mot));

	/* T-XTAL through the request: 327,696 GRTC ticks against 10,000 frames: +488 (48.8 ppm) */
	fx_xtal_rc = 0;
	fx_xtal_grtc = 327696;
	fx_xtal_sof = 10000;
	const uint8_t xt[] = { 0x00, 0xE8, 0x01, 0, 0, 0x10, 0x00, 0x05, 0, 0, 0, 0, 0, 0x10, 0x27, 0, 0 };

	zassert_equal(fx_do1(0x71, true, o, &n, &eff), 0);
	zassert_equal(n, sizeof(xt));
	zassert_mem_equal(o, xt, sizeof(xt));

	/* the response is at most 256 bytes: the largest layout is T-JOY with RFA_MAX_EVENTS events */
	zassert_true(3u + 5u * RFA_MAX_EVENTS <= 256u);
}
