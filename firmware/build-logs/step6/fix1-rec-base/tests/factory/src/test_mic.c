/* Suite factory_mic (software step 6, unit U8): T-MIC1 and T-MIC2 (sub-command 0x10, FW l.1024) and ruling R18 (FW l.1053):
 * a 2 s test recording of type 2 through the normal path, the RMS of each channel in dBFS, the count of identical
 * consecutive samples, the microphones only through rec_mics_on() after the sign. Rows T13.
 * Expected values are typed from FW l.1024 and from the definition of dBFS (20 x log10 of the ratio to 32,768). */
#include "common.h"

ZTEST_SUITE(factory_mic, NULL, NULL, fx_before, fx_after, NULL);

#define MIC1 { 0x10, 0x01 }

/* The measurement itself, on frames the test builds (no simulated input): a run of 1,000 equal samples is stuck, 999 is
 * not (FW l.1024), and a run goes on across blocks; the level of a constant. */
static void pure_checks(void)
{
	static int16_t f[2 * 2048];
	struct rfa_run r;

	/* 999 equal samples, then one different: not stuck */
	memset(&r, 0, sizeof(r));
	for (int i = 0; i < 2048; i++) {
		f[2 * i] = (i < 999) ? 7 : (int16_t)(8 + (i & 1));
		f[2 * i + 1] = (int16_t)i;
	}
	rfa_run_add(&r, f, 2048, 0);
	zassert_equal(r.max, 999, "the longest run is 999");
	zassert_false(rfa_run_is_stuck(r.max), "999 equal samples are not stuck (FW l.1024)");

	/* 1,000 equal samples: stuck */
	for (int i = 0; i < 2048; i++) {
		f[2 * i] = (i < 1000) ? 7 : (int16_t)(8 + (i & 1));
	}
	memset(&r, 0, sizeof(r));
	rfa_run_add(&r, f, 2048, 0);
	zassert_equal(r.max, 1000);
	zassert_true(rfa_run_is_stuck(r.max), "1,000 equal samples are stuck (FW l.1024)");

	/* the same run split over two blocks (600 + 400) */
	for (int i = 0; i < 1000; i++) {
		f[2 * i] = 5;
	}
	f[2 * 1000] = 6;
	memset(&r, 0, sizeof(r));
	rfa_run_add(&r, f, 600, 0);
	rfa_run_add(&r, f + 2 * 600, 1001 - 600, 0);
	zassert_equal(r.max, 1000, "a run continues across blocks");

	/* levels of constants: 16,384 is half of full scale: -6.02 dBFS... as a square wave -6.0206 dB = -60 tenths */
	struct rfa_level lv;

	for (int i = 0; i < 1000; i++) {
		f[2 * i] = 16384;
		f[2 * i + 1] = 0;
	}
	memset(&lv, 0, sizeof(lv));
	rfa_level_add(&lv, f, 1000, 0);
	zassert_equal(rfa_level_dbfs_x10(&lv), -60, "20 x log10(16384 / 32768) = -6.02 dB");
	memset(&lv, 0, sizeof(lv));
	rfa_level_add(&lv, f, 1000, 1);
	zassert_equal(rfa_level_dbfs_x10(&lv), INT16_MIN, "digital silence");
	for (int i = 0; i < 1000; i++) {
		f[2 * i] = 3277;
	}
	memset(&lv, 0, sizeof(lv));
	rfa_level_add(&lv, f, 1000, 0);
	zassert_equal(rfa_level_dbfs_x10(&lv), -200, "20 x log10(3277 / 32768) = -19.9993 dB");
	for (int i = 0; i < 1000; i++) {
		f[2 * i] = 32767;
	}
	memset(&lv, 0, sizeof(lv));
	rfa_level_add(&lv, f, 1000, 0);
	zassert_equal(rfa_level_dbfs_x10(&lv), 0, "full scale");
}

/* T13: RMS of each channel in dBFS and the count of identical consecutive samples. */
ZTEST(factory_mic, test_rms_and_runs)
{
	const uint8_t req[] = MIC1;
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;

	pure_checks();

	/* a 1 kHz sine of peak -20 dBFS on both channels: RMS = peak - 3.01 dB = -23.01 dBFS = -230 tenths */
	rhw_sim_mic_source(RHW_SIM_MIC_SINE, -20);
	zassert_equal(fx_do(req, sizeof(req), true, out, &n, &eff), 0);
	zassert_equal(n, 13, "T-MIC answers 13 bytes");
	zassert_equal(out[0], 0, "pass");
	int16_t l = (int16_t)fx_u16(&out[1]);
	int16_t r = (int16_t)fx_u16(&out[3]);

	zassert_within(l, -230, 2, "left RMS %d tenths of dBFS", l);
	zassert_within(r, -230, 2, "right RMS %d tenths of dBFS", r);
	zassert_true(fx_u32(&out[5]) >= 1 && fx_u32(&out[5]) < RREC_FAC_MIC_STUCK_RUN, "left run %u", fx_u32(&out[5]));
	zassert_true(fx_u32(&out[9]) >= 1 && fx_u32(&out[9]) < RREC_FAC_MIC_STUCK_RUN, "right run %u", fx_u32(&out[9]));

	/* a different level on the same path: peak -10 dBFS gives -13.01 */
	rhw_sim_mic_source(RHW_SIM_MIC_SINE, -10);
	zassert_equal(fx_do(req, sizeof(req), true, out, &n, &eff), 0);
	zassert_within((int16_t)fx_u16(&out[1]), -130, 2);

	/* the right channel stuck at 1,234: its run is every kept frame, the verdict is fail, the left channel is fine.
	 * RMS of the constant 1,234: 20 x log10(1234 / 32768) = -28.48 dB = -285 tenths */
	rhw_sim_mic_source(RHW_SIM_MIC_SINE, -20);
	rhw_sim_mic_stuck(1, 1234);
	fx_frames_seen = 0;
	zassert_equal(fx_do(req, sizeof(req), true, out, &n, &eff), 0);
	zassert_equal(out[0], 1, "a stuck channel fails (no run of 1,000 equal samples)");
	zassert_true(fx_frames_seen > 30000, "about 2 s of kept frames: %u", fx_frames_seen);
	zassert_equal(fx_u32(&out[9]), fx_frames_seen, "the stuck channel's run is every kept frame");
	zassert_true(fx_u32(&out[5]) < RREC_FAC_MIC_STUCK_RUN, "the left channel is not stuck");
	zassert_within((int16_t)fx_u16(&out[3]), -285, 2, "stuck channel level");
	zassert_within((int16_t)fx_u16(&out[1]), -230, 2, "the other channel keeps its level");

	/* T-MIC2 is the same recording (the argument picks the channel the jig judges) */
	const uint8_t req2[] = { 0x10, 0x02 };

	rhw_sim_mic_stuck(-1, 0);
	zassert_equal(fx_do(req2, sizeof(req2), true, out, &n, &eff), 0);
	zassert_equal(out[0], 0);
}

/* T13: the test recording is of type 2 (FW l.548, l.1024) and goes through the normal path: the store holds it as a
 * recording of type 2 with the 2 s of audio, the chunk header says type 2, VDD_MIC only through rec_mics_on(). */
ZTEST(factory_mic, test_type_2_recording)
{
	const uint8_t req[] = MIC1;
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;
	struct rst_rec_info list[4];
	uint16_t count = 0;
	uint8_t sector[RREC_SECTOR_BYTES];

	rhw_sim_mic_source(RHW_SIM_MIC_SINE, -20);
	fx_frames_seen = 0;
	zassert_equal(fx_do(req, sizeof(req), true, out, &n, &eff), 0);
	zassert_equal(out[0], 0);
	zassert_equal(fx_rec_calls, 1, "one test recording");
	/* 2 s at 16 kHz minus the discarded 50 ms (FW l.460, l.1024): 31,200 frames, within one block */
	zassert_within(fx_frames_seen, 31200, 256, "kept frames %u", fx_frames_seen);

	struct rst_mount_info mi;

	zassert_ok(rst_mount(false, &mi));
	zassert_ok(rst_list(0, 4, list, &count));
	zassert_equal(count, 1, "one recording on the card");
	zassert_equal(list[0].type, 2, "recording_type 2 (FW l.548)");
	zassert_true(list[0].chunk_count >= 1);
	zassert_within(list[0].duration_frames, 31200, 256);
	/* the chunk header on the card: recording_type at byte 22 (FW l.548) */
	/* chunk s starts at sector 81,920 + (s mod chunk count) x 65 (FW l.531) */
	rhw_sim_disk_peek(81920u + (list[0].first_chunk_seq % mi.space.total) * 65u, sector);
	zassert_equal(fx_u32(sector), 0x4B435252u, "a chunk header at the first chunk sector (magic RRCK)");
	zassert_equal(sector[22], 2, "the chunk header says type 2 (byte 22, FW l.548), it says %u", sector[22]);
	zassert_ok(rst_unmount());

	/* the normal path: the microphone started once, the rail came on once, by rec_mics_on only */
	zassert_equal(fx_count(RHW_EV_MIC_START), 1);
	zassert_equal(fx_mic_on_events(), 1);
	zassert_equal(strcmp(rhw_sim_pmic_rail_caller(RHW_RAIL_MIC), "rec_mics_off"), 0);
	int32_t on = -1;
	struct rhw_sim_ev e;

	for (uint32_t i = 0; i < rhw_sim_log_count(); i++) {
		zassert_true(rhw_sim_log_get(i, &e));
		if (e.kind == RHW_EV_PMIC_RAIL && e.a0 == RHW_RAIL_MIC && e.a1 != 0) {
			on = (int32_t)i;
			zassert_equal(strcmp(e.caller, "rec_mics_on"), 0, "VDD_MIC on only by rec_mics_on, not by '%s'", e.caller);
		}
	}
	zassert_true(on >= 0);
	zassert_true((uint32_t)on >= fx_sign_at_log, "the sign was asked before VDD_MIC came on");
	zassert_equal(fx_sign_calls, 1);
}

/* R18, T13: no screen, no test. The sign is refused: the answer is a fail, VDD_MIC never comes on, the input never
 * starts. T-SIGN refuses the same way. */
ZTEST(factory_mic, test_no_screen_no_mic)
{
	const uint8_t req[] = MIC1;
	uint8_t out[RFA_OUT_MAX];
	size_t n = 0;
	enum rfa_effect eff;

	rhw_sim_mic_source(RHW_SIM_MIC_SINE, -20);
	fx_sign_answer = -ENODEV;
	rhw_sim_log_clear();
	zassert_equal(fx_do(req, sizeof(req), true, out, &n, &eff), 0, "the request itself is answered");
	zassert_equal(n, 13);
	zassert_equal(out[0], 1, "no screen: the test fails");
	zassert_equal((int16_t)fx_u16(&out[1]), INT16_MIN, "nothing measured");
	zassert_equal(fx_u32(&out[5]), 0);
	zassert_equal(fx_sign_calls, 1, "the sign was asked");
	zassert_equal(fx_mic_on_events(), 0, "VDD_MIC never on without the sign");
	zassert_equal(fx_count(RHW_EV_MIC_START), 0, "the input never started");
	zassert_equal(fx_count(RHW_EV_MIC_READ), 0, "no block read");

	const uint8_t sreq[] = { 0x41 };

	zassert_equal(fx_do(sreq, sizeof(sreq), true, out, &n, &eff), 0);
	zassert_equal(out[0], 1, "T-SIGN with no sign fails too");
	zassert_equal(fx_mic_on_events(), 0, "VDD_MIC never on");
	zassert_equal(fx_count(RHW_EV_MIC_START), 0);

	/* with the sign drawn the same request runs */
	fx_sign_answer = 0;
	zassert_equal(fx_do(req, sizeof(req), true, out, &n, &eff), 0);
	zassert_equal(out[0], 0);
	zassert_equal(fx_mic_on_events(), 1);
}
