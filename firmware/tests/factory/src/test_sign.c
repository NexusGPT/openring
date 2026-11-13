/* Suite factory_sign (software step 6, unit U8): T-SIGN (0x41, FW l.1029): two 1 s test recordings 1 s apart; the ring
 * reports the times VDD_MIC went on and off. Rows T17. The camera is the jig's (not provable here). */
#include "common.h"

ZTEST_SUITE(factory_sign, NULL, NULL, fx_before, fx_after, NULL);

ZTEST(factory_sign, test_two_recordings_times)
{
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;
	int64_t on_log[2], off_log[2];
	int no = 0, nf = 0;
	struct rhw_sim_ev e;

	rhw_sim_mic_source(RHW_SIM_MIC_SINE, -20);
	zassert_equal(fx_do1(0x41, true, out, &n, &eff), 0);
	zassert_equal(n, 33, "T-SIGN answers 33 bytes");
	zassert_equal(out[0], 0, "pass");
	zassert_equal(fx_rec_calls, 2, "two test recordings");
	zassert_equal(fx_sign_calls, 2, "the sign was asked for each");
	int64_t t[4];

	for (int i = 0; i < 4; i++) {
		t[i] = (int64_t)fx_u64(&out[1 + 8 * i]);
	}
	/* the times of VDD_MIC on and off in the one event log of the simulated drivers */
	for (uint32_t i = 0; i < rhw_sim_log_count(); i++) {
		zassert_true(rhw_sim_log_get(i, &e));
		if (e.kind == RHW_EV_PMIC_RAIL && e.a0 == RHW_RAIL_MIC) {
			if (e.a1 != 0 && no < 2) {
				on_log[no++] = e.t_us / 1000;
			} else if (e.a1 == 0 && nf < 2) {
				off_log[nf++] = e.t_us / 1000;
			}
		}
	}
	zassert_equal(no, 2, "VDD_MIC on twice");
	zassert_equal(nf, 2, "VDD_MIC off twice");
	zassert_within(t[0], on_log[0], 1, "first on");
	zassert_within(t[1], off_log[0], 1, "first off");
	zassert_within(t[2], on_log[1], 1, "second on");
	zassert_within(t[3], off_log[1], 1, "second off");
	zassert_true(t[0] < t[1] && t[1] < t[2] && t[2] < t[3], "on, off, on, off in order");
	/* each recording lasts 1 s (the stop waits for the block holding the mark and for the input to drain), the second
	 * starts 1 s after the first ended (FW l.1029) */
	zassert_true(t[1] - t[0] >= 1000 && t[1] - t[0] <= 1250, "first recording %lld ms", t[1] - t[0]);
	zassert_true(t[3] - t[2] >= 1000 && t[3] - t[2] <= 1250, "second recording %lld ms", t[3] - t[2]);
	zassert_true(t[2] - t[1] >= 1000 && t[2] - t[1] <= 1100, "the gap between them %lld ms", t[2] - t[1]);

	/* both are test recordings (type 2) on the card */
	struct rst_rec_info list[4];
	uint16_t count = 0;

	zassert_ok(rst_mount(false, &(struct rst_mount_info){ 0 }));
	zassert_ok(rst_list(0, 4, list, &count));
	zassert_equal(count, 2);
	zassert_equal(list[0].type, 2);
	zassert_equal(list[1].type, 2);
	zassert_ok(rst_unmount());
}
