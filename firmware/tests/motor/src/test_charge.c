/* Suite motor_charge (software step 6, unit U6): the charge each pulse takes from the cell, for the battery gauge
 * (FW l.332, FW 8.3 l.927). Row C32 of firmware/docs/step6-plan.md. Units: the callback gives µA·s, so 8.15 mA.s is
 * 8,150. Expected values are typed from FW l.332 (M1 8.15, M2 16.30, M3 24.45, MH 4.95, MT 3.75, MW 6.55, MF 51.50
 * mA.s); the rule behind them is t_on x 80 mA + 10 ms x 175 mA per ON pulse (80 ms: 6,400 + 1,750 = 8,150). */
#include "common.h"

static void before(void *f)
{
	ARG_UNUSED(f);
	t_reset();
}

static void after(void *f)
{
	ARG_UNUSED(f);
	rmo_stop();
}

ZTEST_SUITE(motor_charge, NULL, NULL, before, after, NULL);

struct spec_q {
	enum rrec_pattern id;
	const char *name;
	uint32_t total_ms;      /* FW l.320 to l.328 */
	uint8_t pulses;
	uint32_t pulse_uas[3];  /* the charge of each pulse, µA·s */
	uint32_t uas;           /* FW l.332, mA.s x 1000 */
};
static const struct spec_q q[7] = {
	{ RREC_PAT_M1, "M1", 80, 1, { 8150 }, 8150 },
	{ RREC_PAT_M2, "M2", 280, 2, { 8150, 8150 }, 16300 },
	{ RREC_PAT_M3, "M3", 480, 3, { 8150, 8150, 8150 }, 24450 },
	{ RREC_PAT_MH, "MH", 40, 1, { 4950 }, 4950 },
	{ RREC_PAT_MT, "MT", 25, 1, { 3750 }, 3750 },
	{ RREC_PAT_MW, "MW", 60, 1, { 6550 }, 6550 },
	{ RREC_PAT_MF, "MF", 800, 2, { 25750, 25750 }, 51500 },
};

/* C32, FW l.332: the charge per pattern, and per pulse; reported once per ON pulse, at the pulse's end (the same
 * instant as the MOTOR-low edge), nothing for an off segment. */
ZTEST(motor_charge, test_charge_per_pattern)
{
	for (int i = 0; i < 7; i++) {
		uint32_t sum = 0;

		t_reset();
		zassert_equal(rmo_play(q[i].id), 0);
		zassert_equal(t_n_charge(), 0, "%s: nothing reported before a pulse ends", q[i].name);
		t_ms(q[i].total_ms + 100);
		zassert_equal(t_n_charge(), q[i].pulses, "%s: one report per ON pulse", q[i].name);
		for (int k = 0; k < q[i].pulses; k++) {
			sum += t_charge(k)->uas;
			zassert_equal(t_charge(k)->uas, q[i].pulse_uas[k], "%s pulse %d: %u uA.s", q[i].name, k,
				      t_charge(k)->uas);
		}
		zassert_equal(sum, q[i].uas, "%s: %u uA.s in all, expected %u", q[i].name, sum, q[i].uas);
		/* the pure part says the same, and its single-pulse rule matches the typed pulses */
		zassert_equal(rml_pattern_uas(q[i].id), q[i].uas, "%s pure part", q[i].name);
		/* the report comes at the pulse's end: the callback's clock equals the MOTOR-low edge's cycles */
		int lows = 0;

		for (int k = 0; k < t_n_edge(); k++) {
			if (!t_edge(k)->high) {
				zassert_equal(t_charge(lows)->cycles, t_edge(k)->cycles, "%s: report %d at the low edge",
					      q[i].name, lows);
				lows++;
			}
		}
		zassert_equal(lows, q[i].pulses);
		printk("charge %s: %u uA.s in %d pulses\n", q[i].name, sum, q[i].pulses);
	}
	zassert_equal(rml_pulse_uas(80), 8150u);
	zassert_equal(rml_pulse_uas(300), 25750u);
	zassert_equal(rml_pulse_uas(25), 3750u);
	zassert_equal(rml_pattern_uas(0), 0u);
}

/* Nothing is reported for a pattern that did not play: refused by the replace rule, refused by the setting, unknown. */
ZTEST(motor_charge, test_no_charge_without_a_pulse)
{
	rmo_set_vibration(false);
	zassert_equal(rmo_play(RREC_PAT_MH), -ECANCELED);
	zassert_equal(rmo_play(9), -EINVAL);
	rmo_set_vibration(true);
	zassert_equal(rmo_play(RREC_PAT_M3), 0);
	zassert_equal(rmo_play(RREC_PAT_MT), -EBUSY);
	t_ms(40);
	rmo_stop();                                      /* cut in the first pulse: that pulse is reported once */
	t_ms(1000);
	zassert_equal(t_n_charge(), 1, "only the cut pulse of M3");
}

/* A pulse cut by a replacement or by rmo_stop is reported with the time it ran: elapsed ms x 80 mA + the start
 * allowance 10 ms x 175 mA. The expected value is typed from the elapsed time the test measured itself. */
ZTEST(motor_charge, test_cut_pulse_charge)
{
	zassert_equal(rmo_play(RREC_PAT_M1), 0);
	int64_t p0 = t_now_us();

	t_ms(50);
	int64_t el_ms = (t_now_us() - p0) / 1000;

	zassert_equal(rmo_play(RREC_PAT_MW), 0);         /* M1 cut at 50 ms by MW */
	zassert_equal(t_n_charge(), 1);
	zassert_true(el_ms >= 50);
	zassert_equal(t_charge(0)->uas, (uint32_t)(el_ms * 80 + 1750), "cut M1 pulse: %lld ms ran", (long long)el_ms);
	t_ms(200);
	zassert_equal(t_n_charge(), 2, "MW's own pulse");
	zassert_equal(t_charge(1)->uas, 6550u);
	/* rmo_stop in the middle of the second MF pulse reports that pulse's part only */
	t_reset();
	zassert_equal(rmo_play(RREC_PAT_MF), 0);
	t_ms(600);                                       /* second pulse started at 500 */
	rmo_stop();
	t_ms(300);
	zassert_equal(t_n_charge(), 2);
	zassert_equal(t_charge(0)->uas, 25750u);
	zassert_true(t_charge(1)->uas >= 99u * 80u + 1750u && t_charge(1)->uas < 102u * 80u + 1750u, "%u", t_charge(1)->uas);
}
