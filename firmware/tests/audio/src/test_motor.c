/* Suite audio_motor (software step 6, unit U3): motor intervals in the chunk headers (design/firmware.md 4.7, 5.3).
 * Pure part only. Time base of every case: the PDM starts at start_cycles on a counter of 1,000,000 cycles per second
 * (1 cycle = 1 us); a frame index counts from the first kept frame (50 ms = 800 frames after the start), so the
 * frame at index f lies (f + 800) / 16 ms after the start. Expected frames are literals worked out by hand from FW l.495. */
#include "common.h"

#define HZ 1000000u

static struct rac s;

static void before(void *f)
{
	ARG_UNUSED(f);
	t_reset();
}

ZTEST_SUITE(audio_motor, NULL, NULL, before, NULL, NULL);

static void begin(uint64_t start_cycles)
{
	struct rac_start a = t_start(true, (int64_t)(start_cycles / 1000u), start_cycles, HZ);

	rac_begin(&s, &a);
}

/* A16, FW l.495: an interval runs from the frame of MOTOR high to 800 frames (50 ms) after MOTOR low.
 * High 200 ms after the start: frame 200 x 16 - 800 = 2,400; low 240 ms after: frame 3,040; end 3,040 + 800 = 3,840. */
ZTEST(audio_motor, test_interval_frames)
{
	struct rst_close_args cl;

	begin(5000000);
	rac_motor_edge(&s, true, 5200000);
	rac_motor_edge(&s, false, 5240000);
	t_feed(&s, 0, 20);                       /* 5,120 raw frames = 4,320 kept */
	struct rst_chunk *c = rac_cut(&s, &cl);

	zassert_not_null(c);
	zassert_equal(c->hdr.frames, 4320);
	zassert_equal(c->hdr.motor_count, 1);
	zassert_equal(c->hdr.motor_frames[0][0], 2400, "start = frame of MOTOR high");
	zassert_equal(c->hdr.motor_frames[0][1], 3840, "end = frame of MOTOR low + 800");
	zassert_true(c->hdr.flags & RREC_CH_FLAG_MOTOR, "flag bit 3");
}

/* A17, FW l.496, l.576: an interval over two chunks is written in both, cut at the chunk edge.
 * High at frame 8,100 (556.25 ms after the start), low at frame 8,300 (568.75 ms): interval [8,100; 9,100).
 * Chunk 0 holds frames 0 to 8,191: {8,100; 8,192}. Chunk 1 starts at 8,192: {0; 908}. */
ZTEST(audio_motor, test_span_two_chunks)
{
	struct rst_close_args cl;

	begin(0);
	rac_motor_edge(&s, true, 556250);
	rac_motor_edge(&s, false, 568750);
	t_feed(&s, 0, 40);                       /* 10,240 raw frames = 9,440 kept: chunk 0 full, 1,248 in chunk 1 */
	zassert_equal(t_fulls(), 1);
	struct rst_chunk *c0 = t_full(0);
	struct rst_chunk *c1 = rac_cut(&s, &cl);

	zassert_equal(c0->hdr.motor_count, 1);
	zassert_equal(c0->hdr.motor_frames[0][0], 8100);
	zassert_equal(c0->hdr.motor_frames[0][1], 8192, "cut at the chunk edge");
	zassert_true(c0->hdr.flags & RREC_CH_FLAG_MOTOR);
	zassert_not_null(c1);
	zassert_equal(c1->hdr.motor_count, 1, "written in the second chunk too");
	zassert_equal(c1->hdr.motor_frames[0][0], 0);
	zassert_equal(c1->hdr.motor_frames[0][1], 908);
	zassert_true(c1->hdr.flags & RREC_CH_FLAG_MOTOR);
}

/* Same, with MOTOR still high when chunk 0 ends: the low edge arrives after the chunk went to the store. */
ZTEST(audio_motor, test_span_open_interval)
{
	struct rst_close_args cl;

	begin(0);
	rac_motor_edge(&s, true, 556250);
	t_feed(&s, 0, 36);                       /* 9,216 raw frames: chunk 0 (8,992 raw) is full, MOTOR still high */
	zassert_equal(t_fulls(), 1);
	rac_motor_edge(&s, false, 568750);
	t_feed(&s, 36, 4);
	struct rst_chunk *c0 = t_full(0);
	struct rst_chunk *c1 = rac_cut(&s, &cl);

	zassert_equal(c0->hdr.motor_count, 1);
	zassert_equal(c0->hdr.motor_frames[0][0], 8100);
	zassert_equal(c0->hdr.motor_frames[0][1], 8192);
	zassert_not_null(c1);
	zassert_equal(c1->hdr.motor_count, 1);
	zassert_equal(c1->hdr.motor_frames[0][0], 0);
	zassert_equal(c1->hdr.motor_frames[0][1], 908);
}

/* A17, FW l.576: at most 4 in a header; a fifth is merged into the fourth (its end frame moved).
 * Five pulses of 100 frames, one every 1,000 frames from frame 100: high at 100, 1,100, 2,100, 3,100, 4,100; low 100
 * frames later; each interval = [high; low + 800) = [100; 1,000), [1,100; 2,000) ... [4,100; 5,000). Header: 4
 * intervals; the fourth {3,100; 5,000} (the fifth's end). */
ZTEST(audio_motor, test_fifth_merged_into_fourth)
{
	struct rst_close_args cl;
	/* frame f is at (f + 800) / 16 ms = (f + 800) x 62.5 us */
	static const uint64_t hi_us[5] = { 56250, 118750, 181250, 243750, 306250 };   /* frames 100, 1100, 2100, 3100, 4100 */
	static const uint64_t lo_us[5] = { 62500, 125000, 187500, 250000, 312500 };   /* frames 200, 1200, 2200, 3200, 4200 */

	begin(0);
	for (int i = 0; i < 5; i++) {
		rac_motor_edge(&s, true, hi_us[i]);
		rac_motor_edge(&s, false, lo_us[i]);
	}
	t_feed(&s, 0, 25);                       /* 6,400 raw frames = 5,600 kept */
	struct rst_chunk *c = rac_cut(&s, &cl);

	zassert_not_null(c);
	zassert_equal(c->hdr.motor_count, 4, "at most 4");
	zassert_equal(c->hdr.motor_frames[0][0], 100);
	zassert_equal(c->hdr.motor_frames[0][1], 1000);
	zassert_equal(c->hdr.motor_frames[1][0], 1100);
	zassert_equal(c->hdr.motor_frames[2][0], 2100);
	zassert_equal(c->hdr.motor_frames[3][0], 3100);
	zassert_equal(c->hdr.motor_frames[3][1], 5000, "the fifth's end moved into the fourth");
}

/* A17, FW l.577, l.566: unused motor pairs and highlight slots read 0xFFFFFFFF; no interval: count 0, flag bit 3 clear. */
ZTEST(audio_motor, test_unused_pairs_ff)
{
	struct rst_close_args cl;

	begin(0);
	rac_motor_edge(&s, true, 100000);        /* frame 800 */
	rac_motor_edge(&s, false, 110000);       /* frame 960; interval [800; 1,760) */
	t_feed(&s, 0, 10);
	struct rst_chunk *c = rac_cut(&s, &cl);

	zassert_not_null(c);
	zassert_equal(c->hdr.motor_count, 1);
	for (int i = 1; i < 4; i++) {
		zassert_equal(c->hdr.motor_frames[i][0], 0xFFFFFFFFu, "pair %d start", i);
		zassert_equal(c->hdr.motor_frames[i][1], 0xFFFFFFFFu, "pair %d end", i);
	}
	for (int i = 0; i < 8; i++) {
		zassert_equal(c->hdr.highlight_frame[i], 0xFFFFFFFFu, "highlight slot %d", i);
	}
	/* no interval at all */
	t_reset();
	begin(0);
	t_feed(&s, 0, 10);
	c = rac_cut(&s, &cl);
	zassert_not_null(c);
	zassert_equal(c->hdr.motor_count, 0);
	zassert_false(c->hdr.flags & RREC_CH_FLAG_MOTOR);
	for (int i = 0; i < 4; i++) {
		zassert_equal(c->hdr.motor_frames[i][0], 0xFFFFFFFFu);
		zassert_equal(c->hdr.motor_frames[i][1], 0xFFFFFFFFu);
	}
}

/* A18, FW l.497: M1 (80 ms) runs while the first 50 ms are discarded; the rest of the pulse plus 50 ms is marked in
 * the first chunk. PDM start at 1,000,000 us. */
ZTEST(audio_motor, test_m1_rest_marked_in_first_chunk)
{
	struct rst_close_args cl;
	struct rst_chunk *c;

	/* MOTOR high at 970 ms, low at 1,050 ms (80 ms): the low edge is exactly at the first kept frame (index 0), so
	 * the marked part is only the 800-frame tail: {0; 800}. The start (index -1,280) is cut at the chunk start. */
	begin(1000000);
	rac_motor_edge(&s, true, 970000);
	rac_motor_edge(&s, false, 1050000);
	t_feed(&s, 0, 8);
	c = rac_cut(&s, &cl);
	zassert_not_null(c);
	zassert_equal(c->hdr.motor_count, 1);
	zassert_equal(c->hdr.motor_frames[0][0], 0);
	zassert_equal(c->hdr.motor_frames[0][1], 800);
	zassert_true(c->hdr.flags & RREC_CH_FLAG_MOTOR);

	/* the pulse ends 100 ms after the start (frame 800): 800 + 800 = {0; 1,600} */
	t_reset();
	begin(1000000);
	rac_motor_edge(&s, true, 1020000);
	rac_motor_edge(&s, false, 1100000);
	t_feed(&s, 0, 12);
	c = rac_cut(&s, &cl);
	zassert_not_null(c);
	zassert_equal(c->hdr.motor_count, 1);
	zassert_equal(c->hdr.motor_frames[0][0], 0);
	zassert_equal(c->hdr.motor_frames[0][1], 1600);

	/* the pulse ends 20 ms after the start (inside the discard, frame -480): only the tail's 320 frames are kept */
	t_reset();
	begin(1000000);
	rac_motor_edge(&s, true, 940000);
	rac_motor_edge(&s, false, 1020000);
	t_feed(&s, 0, 8);
	c = rac_cut(&s, &cl);
	zassert_not_null(c);
	zassert_equal(c->hdr.motor_count, 1);
	zassert_equal(c->hdr.motor_frames[0][1], 320);

	/* a pulse that ended before the PDM started leaves no mark (its tail ends inside the discard) */
	t_reset();
	begin(1000000);
	rac_motor_edge(&s, true, 800000);
	rac_motor_edge(&s, false, 880000);
	t_feed(&s, 0, 8);
	c = rac_cut(&s, &cl);
	zassert_not_null(c);
	zassert_equal(c->hdr.motor_count, 0);
	zassert_false(c->hdr.flags & RREC_CH_FLAG_MOTOR);
}
