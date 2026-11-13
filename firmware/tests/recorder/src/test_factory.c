/*
 * recorder_factory: the join's half of T-MIC and T-SIGN on the REAL rrec_test_recording (step 6 fix round 1, review
 * finding R6-06): design/firmware.md l.1024 (T-MIC: "a 2 s test recording (recording_type 2) through the normal path")
 * and l.1029 (T-SIGN: "two 1 s test recordings 1 s apart; the ring reports the times VDD_MIC went on and off"). The
 * requests go over the simulated USB to the real factory part, which calls the join through its ops.
 */
#include <string.h>

#include <zephyr/sys/byteorder.h>

#include <ring_store/rst.h>

#include "rt.h"

#if defined(CONFIG_RING_FACTORY)
static uint8_t resp[RREC_MSG_HEADER_BYTES + 256];

static void to_factory(void)
{
	struct rt_boot b = { .factory_flag = true };
	uint8_t st;
	uint8_t sub = RREC_FAC_ENTER;

	rt_fresh(&b);
	rt_vbus(true);
	rt_usb_configured();
	(void)rt_usb(RREC_OP_FACTORY, &sub, 1, resp, sizeof(resp), &st);
	zassert_equal(rt_state(), RC_ST_FACTORY_TEST, "FACTORY_TEST");
}

/* the newest recording on the card (mounted for the read) */
static bool newest(struct rst_rec_info *out)
{
	struct rst_mount_info mi;
	struct rst_rec_info info[8];
	uint16_t n = 0;
	bool was = rst_mounted();

	if (!was && rst_mount(false, &mi) != 0) {
		return false;
	}
	(void)rst_list(0, 8, info, &n);
	if (!was) {
		(void)rst_unmount();
	}
	if (n == 0) {
		return false;
	}
	*out = info[n - 1];
	return true;
}
#endif

/* T-MIC1 (FW l.1024): one recording of type 2, 2 s long (32,000 frames at 16 kHz, FW l.443), through rec_mics_on */
ZTEST(recorder_factory, test_tmic_records_type_2_for_2s)
{
#if defined(CONFIG_RING_FACTORY)
	uint8_t pl[2] = { RREC_FAC_MIC, 1 };
	struct rst_rec_info r;
	uint8_t st = 0xFF;
	int n;

	memset(&r, 0, sizeof(r));

	to_factory();
	rhw_sim_log_clear();
	n = rt_usb(RREC_OP_FACTORY, pl, sizeof(pl), resp, sizeof(resp), &st);
	TC_PRINT("T-MIC1: response %d bytes, status %u, result %u\n", n, st, n > RREC_MSG_HEADER_BYTES ?
		 resp[RREC_MSG_HEADER_BYTES] : 0xFF);
	zassert_equal(st, RREC_ST_OK, "the request answered OK");
	zassert_equal(resp[RREC_MSG_HEADER_BYTES], RREC_FAC_RESULT_PASS, "T-MIC1 passed on the counter input");
	zassert_equal(rt_count_rail(RHW_RAIL_MIC, true), 1u, "VDD_MIC on once");
	zassert_true(newest(&r), "the test recording is on the card");
	TC_PRINT("T-MIC1: recording %u type %u, %llu frames, %u chunks\n", r.recording_id, r.type, r.duration_frames,
		 r.chunk_count);
	zassert_equal(r.type, 2, "recording_type 2 (FW l.1024)");
	/* 2 s = 32,000 frames (FW l.1024, l.443); within one block of 256 frames (FW l.443): the cut is at a ms time */
	zassert_true(r.duration_frames + 256 >= 32000 && r.duration_frames <= 32000 + 256, "2 s long (%llu frames)",
		     r.duration_frames);
	zassert_false(rt_mic(), "VDD_MIC off after the test");
#else
	ztest_test_skip();
#endif
}

/* T-SIGN (FW l.1029): two 1 s test recordings 1 s apart; the reported VDD_MIC on and off times are the rail's own */
ZTEST(recorder_factory, test_tsign_reports_mic_times)
{
#if defined(CONFIG_RING_FACTORY)
	uint8_t sub = RREC_FAC_SIGN;
	uint8_t st = 0xFF;
	int64_t rep[4];
	int64_t rail[4];
	int32_t i = 0;
	int n;

	to_factory();
	rhw_sim_log_clear();
	n = rt_usb(RREC_OP_FACTORY, &sub, 1, resp, sizeof(resp), &st);
	zassert_equal(st, RREC_ST_OK, "the request answered OK");
	zassert_true(n >= RREC_MSG_HEADER_BYTES + 1 + 32, "result and four times (%d bytes)", n);
	zassert_equal(resp[RREC_MSG_HEADER_BYTES], RREC_FAC_RESULT_PASS, "T-SIGN result pass");
	for (int k = 0; k < 4; k++) {
		rep[k] = (int64_t)sys_get_le64(&resp[RREC_MSG_HEADER_BYTES + 1 + 8 * k]);
	}
	/* the rail's own on, off, on, off times from the event log of the simulated power chip */
	for (int k = 0; k < 4; k++) {
		i = rt_find_rail(RHW_RAIL_MIC, (k % 2) == 0, k == 0 ? 0 : (uint32_t)i + 1);
		rail[k] = i >= 0 ? rt_ev_us(i) / 1000 : -1;
	}
	TC_PRINT("T-SIGN: reported on %lld off %lld on %lld off %lld ms; rail on %lld off %lld on %lld off %lld ms\n", rep[0],
		 rep[1], rep[2], rep[3], rail[0], rail[1], rail[2], rail[3]);
	zassert_equal(rt_count_rail(RHW_RAIL_MIC, true), 2u, "two test recordings: VDD_MIC on twice");
	for (int k = 0; k < 4; k++) {
		zassert_true(rail[k] >= 0, "rail edge %d", k);
		/* the time is read right after the rail call: the same ms or the next (1 ms, the rail wait of FW l.458) */
		zassert_true(rep[k] >= rail[k] && rep[k] <= rail[k] + 1, "time %d reported %lld, rail %lld", k, rep[k],
			     rail[k]);
	}
	/* each 1 s long (FW l.1029), the second 1 s after the first ended (FW l.1029). From above too (review 2, R2-07):
	 * VDD_MIC stays on for the 1 s kept, the 50 ms dropped at the start (FW l.460) and the close (the join's allowance of
	 * 100 ms: the specification gives no number for it), so under 1,150 ms */
	zassert_true(rep[1] - rep[0] >= 1000 && rep[1] - rep[0] < 1000 + RREC_DISCARD_MS + 100, "first recording 1 s (%lld ms)",
		     rep[1] - rep[0]);
	zassert_true(rep[3] - rep[2] >= 1000 && rep[3] - rep[2] < 1000 + RREC_DISCARD_MS + 100, "second recording 1 s (%lld ms)",
		     rep[3] - rep[2]);
	zassert_true(rep[2] - rep[1] >= 1000, "1 s apart (%lld ms)", rep[2] - rep[1]);
	zassert_false(rt_mic(), "VDD_MIC off after the test");
#else
	ztest_test_skip();
#endif
}

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_factory, NULL, setup, NULL, NULL, NULL);
