/* Suite audio_cfg (software step 6, unit U3): the configuration the audio part gives the microphone input, and the
 * specification's constants it rests on. Expected values are literals from design/firmware.md (lines cited). */
#include "common.h"

static void before(void *f)
{
	ARG_UNUSED(f);
	svc_setup();
}

static void after(void *f)
{
	ARG_UNUSED(f);
	svc_cleanup();
}

ZTEST_SUITE(audio_cfg, NULL, NULL, before, after, NULL);

/* A1: FW l.410 to l.420: pdm20, 2 channels, 16,000 Hz, 16 bits, clock window 1,200,000 to 1,650,000 Hz, block 1,024
 * bytes, 8 blocks; the simulated input records what it received. */
ZTEST(audio_cfg, test_dmic_config_values)
{
	struct rhw_mic_cfg got;

	zassert_false(rhw_sim_mic_last_cfg(&got), "nothing configured before the start");
	(void)svc_begin(true, false);
	zassert_true(rhw_sim_mic_last_cfg(&got));
	zassert_equal(got.pcm_rate, 16000, "FW l.411");
	zassert_equal(got.pcm_width, 16, "FW l.412");
	zassert_equal(got.channels, 2, "FW l.413");
	zassert_equal(got.min_pdm_clk_hz, 1200000, "FW l.415");
	zassert_equal(got.max_pdm_clk_hz, 1650000, "FW l.415");
	zassert_equal(got.gain_db, 0, "FW l.417");
	zassert_equal(got.block_size, 1024, "FW l.419");
	zassert_equal(got.block_count, 8, "FW l.420");
	/* order: configure, pins default, trigger (rau.h) */
	int32_t c = ev_find(RHW_EV_MIC_CONFIGURE, 0);
	int32_t d = ev_find(RHW_EV_MIC_PINS_DEFAULT, 0);
	int32_t s = ev_find(RHW_EV_MIC_START, 0);

	zassert_true(c >= 0 && d > c && s > d, "configure %d, pins default %d, start %d", c, d, s);
}

/* The numbers of rrec_spec.h that the unit uses, against the specification's literals (FW l.411 to l.420, l.440,
 * l.443, l.460, l.495, l.535). */
ZTEST(audio_cfg, test_spec_numbers)
{
	zassert_equal(RREC_BLOCK_BYTES, 1024, "FW l.419");
	zassert_equal(RREC_BLOCK_FRAMES, 256, "FW l.419");
	zassert_equal(RREC_BLOCK_MS, 16, "FW l.419");
	zassert_equal(RREC_BLOCK_COUNT, 8, "FW l.420");
	zassert_equal(RREC_BLOCKS_PER_CHUNK, 32, "FW l.443");
	zassert_equal(RREC_CHUNK_RING, 3, "FW l.440");
	zassert_equal(RREC_CHUNK_BYTES, 33280, "FW l.535");
	zassert_equal(RREC_CHUNK_FRAMES, 8192, "FW l.535");
	zassert_equal(RREC_DISCARD_FRAMES, 800, "FW l.460");
	zassert_equal(RREC_MOTOR_TAIL_FRAMES, 800, "FW l.495");
	zassert_equal(RREC_MIC_NO_BLOCK_MS, 100, "FW l.169");
}

/* A2: FW l.416, l.560, l.561: the header carries 1,280,000 and 80 (the store writes them from these numbers); the
 * driver's own pick of the clock is not shown by the simulation. */
ZTEST(audio_cfg, test_header_clock_fields)
{
	zassert_equal(RREC_PDM_CLOCK_HZ, 1280000, "FW l.416, l.560");
	zassert_equal(RREC_PDM_RATIO, 80, "FW l.416, l.561");
	zassert_equal(RREC_PDM_CLOCK_HZ / RREC_PDM_RATIO, 16000, "FW l.416: 1,280,000 / 80 = 16,000 Hz");
}

/* A3: FW l.417: gain 0 dB, register value 0x28; header gain_code 0x28 (l.562). */
ZTEST(audio_cfg, test_gain_zero)
{
	struct rhw_mic_cfg got;

	(void)svc_begin(true, false);
	zassert_true(rhw_sim_mic_last_cfg(&got));
	zassert_equal(got.gain_db, 0, "FW l.417");
	zassert_equal(RREC_PDM_GAIN_DB, 0, "FW l.417");
	zassert_equal(RREC_PDM_GAIN_CODE, 0x28, "FW l.417, l.562");
}
