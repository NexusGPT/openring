/* Suite audio_chunk (software step 6, unit U3): blocks into chunks (design/firmware.md 4.1 to 4.5, 5.3). Pure part
 * only. Source of every case: the frame counter (left = frame number since the PDM start, 16 bits; right = its
 * bitwise inverse), so the kept frame i of a recording holds the value i + 800 on the left (FW l.460: 800 frames
 * are dropped). Expected values are literals written from the specification, with the line cited. */
#include "common.h"

static struct rac s;

static void before(void *f)
{
	ARG_UNUSED(f);
	t_reset();
}

ZTEST_SUITE(audio_chunk, NULL, NULL, before, NULL, NULL);

static void begin_with(bool time_set, int64_t start_ms, uint64_t start_cycles, uint32_t hz)
{
	struct rac_start a = t_start(time_set, start_ms, start_cycles, hz);

	rac_begin(&s, &a);
}

static void begin(void)
{
	begin_with(true, 1000, 1000000, 1000000);
}

/* A4, FW l.418, l.422, l.443: the block's order is kept, channel 0 first. First kept frame = raw frame 800. */
ZTEST(audio_chunk, test_interleave_order)
{
	struct rst_close_args cl;

	begin();
	t_feed(&s, 0, 4);
	struct rst_chunk *c = rac_cut(&s, &cl);

	zassert_not_null(c);
	zassert_equal(t_left(c, 0), 800, "channel 0 first");
	zassert_equal(t_right(c, 0), -801, "channel 1 second: bitwise inverse of 800");
	zassert_equal(t_left(c, 1), 801);
	zassert_equal(t_right(c, 1), -802);
}

/* A5, FW l.423: samples stored as they come, no level rule. */
ZTEST(audio_chunk, test_payload_equals_blocks)
{
	begin();
	t_feed(&s, 0, 36);
	zassert_equal(t_fulls(), 1);
	const struct rst_chunk *c = t_full(0);

	for (uint32_t i = 0; i < 8192; i++) {
		int16_t l = (int16_t)(uint16_t)((i + 800u) & 0xFFFFu);

		zassert_equal(t_left(c, i), l, "frame %u left", i);
		zassert_equal(t_right(c, i), (int16_t)~(uint16_t)l, "frame %u right", i);
	}
}

/* A9, FW l.447, l.460: the first 50 ms (800 frames) are dropped. 3 blocks = 768 frames: nothing kept; 4 blocks: 224. */
ZTEST(audio_chunk, test_discard_800_frames)
{
	struct rst_close_args cl;

	begin();
	t_feed(&s, 0, 3);
	zassert_is_null(rac_cut(&s, &cl), "768 frames are all inside the discard");
	zassert_equal(cl.duration_frames, 0);

	t_reset();
	begin();
	t_feed(&s, 0, 4);
	struct rst_chunk *c = rac_cut(&s, &cl);

	zassert_not_null(c);
	zassert_equal(c->hdr.frames, 224, "1,024 - 800");
	zassert_equal(cl.duration_frames, 224);
	zassert_equal(t_left(c, 0), 800, "the first kept frame is raw frame 800, not 0");
}

/* A9, FW l.460, l.558: the recording time is that of the first kept frame (PDM start + 50 ms). PDM start at 12 s. */
ZTEST(audio_chunk, test_start_time_is_first_kept_frame)
{
	struct rst_close_args cl;

	begin_with(true, 12000, 12000000, 1000000);
	t_feed(&s, 0, 4);
	struct rst_chunk *c = rac_cut(&s, &cl);

	zassert_not_null(c);
	zassert_equal(c->hdr.uptime_ns, 12050000000ULL, "12 s + 50 ms");
	zassert_equal(c->hdr.utc_ms, 1700000012050LL, "offset 1,700,000,000,000 ms + 12,050 ms");
	zassert_equal(c->hdr.first_frame_index, 0);
}

/* A8, FW l.443: 32 blocks fill a chunk (8,192 frames). The first chunk is full in the 36th block (8,992 raw frames
 * = 800 + 8,192), the next 32 blocks later, in the 68th. */
ZTEST(audio_chunk, test_32_blocks_per_chunk)
{
	int first = 0, second = 0;

	begin();
	for (uint32_t k = 0; k < 70; k++) {
		t_feed(&s, k, 1);
		if (t_fulls() == 1 && first == 0) {
			first = (int)k + 1;
		}
		if (t_fulls() == 2 && second == 0) {
			second = (int)k + 1;
		}
	}
	zassert_equal(first, 36, "first chunk full after 36 blocks");
	zassert_equal(second, 68, "second chunk full after 68 blocks");
	zassert_equal(second - first, 32, "32 blocks per chunk");
	zassert_equal(t_full(0)->hdr.frames, 8192);
	zassert_equal(t_full(1)->hdr.frames, 8192);
	zassert_equal(t_full(1)->hdr.first_frame_index, 8192);
	zassert_equal(t_full(1)->hdr.chunk_in_recording, 1);
}

/* A7, FW l.430: a missing block becomes zeros of the same length, flag bit 7, counted, logged; the recording keeps its
 * length. Block 6 (raw frames 1,536 to 1,791 = kept 736 to 991) is missing. */
ZTEST(audio_chunk, test_dropout_zero_fill)
{
	struct rst_close_args cl;

	begin();
	t_feed(&s, 0, 6);
	zassert_ok(rac_block(&s, NULL, t_ops()));
	t_feed(&s, 7, 3);
	struct rst_chunk *c = rac_cut(&s, &cl);

	zassert_not_null(c);
	zassert_equal(c->hdr.frames, 1760, "10 blocks = 2,560 raw frames - 800: the length does not change");
	zassert_equal(cl.duration_frames, 1760);
	zassert_equal(c->hdr.dropout_blocks, 1);
	zassert_equal(c->hdr.flags, RREC_CH_FLAG_FIRST | RREC_CH_FLAG_LAST | RREC_CH_FLAG_DROPOUT, "0x83");
	zassert_equal(t_left(c, 735), 1535, "the frame before the gap");
	for (uint32_t i = 736; i < 992; i++) {
		zassert_equal(t_left(c, i), 0, "frame %u zero", i);
		zassert_equal(t_right(c, i), 0, "frame %u zero", i);
	}
	zassert_equal(t_left(c, 992), 1792, "the stream goes on in place after the gap");
	zassert_equal(t_dropouts(), 1, "logged once");
	zassert_equal(t_dropout_chunk(0), 0);
	zassert_equal(t_dropout_block(0), 2, "at frame 736 of the chunk = block position 2");

	/* a missing block over a chunk edge: block 35 holds kept frames 8,160 to 8,415 (chunk edge at 8,192) */
	t_reset();
	begin();
	t_feed(&s, 0, 35);
	zassert_ok(rac_block(&s, NULL, t_ops()));
	t_feed(&s, 36, 1);
	zassert_equal(t_fulls(), 1);
	c = rac_cut(&s, &cl);
	zassert_not_null(c);
	const struct rst_chunk *c0 = t_full(0);

	zassert_equal(c0->hdr.flags, RREC_CH_FLAG_FIRST | RREC_CH_FLAG_DROPOUT, "0x81");
	zassert_equal(c0->hdr.dropout_blocks, 1);
	zassert_equal(c->hdr.flags, RREC_CH_FLAG_LAST | RREC_CH_FLAG_DROPOUT, "0x82");
	zassert_equal(c->hdr.dropout_blocks, 1, "counted in each chunk it touches");
	zassert_equal(c->hdr.frames, 480, "9,472 raw - 800 - 8,192");
	zassert_equal(t_left(c0, 8191), 0);
	zassert_equal(t_left(c, 223), 0);
	zassert_equal(t_left(c, 224), 9216, "8,416 + 800");
	zassert_equal(t_dropouts(), 1, "one block, one log");
	zassert_equal(cl.duration_frames, 8672);
}

/* S10, FW l.547: each flag bit; bit 2 and bits 8 to 15 are zero. Frame 100 of block 3 is raw frame 868 (kept). */
static uint16_t flags_of(bool time_set, bool b15, int clip_channel, int16_t clip_val, bool dropout, bool motor)
{
	struct rst_close_args cl;

	t_reset();
	t_facts(3800, 250, 0x01020003, b15);
	begin_with(time_set, 1000, 1000000, 1000000);
	if (motor) {
		rac_motor_edge(&s, true, 1060000);    /* frame 160 */
		rac_motor_edge(&s, false, 1062000);   /* frame 192: interval [160; 992) */
	}
	t_feed(&s, 0, 3);
	if (dropout) {
		(void)rac_block(&s, NULL, t_ops());
	} else if (clip_channel >= 0) {
		t_feed_block_with(&s, 3, 100, clip_channel, clip_val);
	} else {
		t_feed(&s, 3, 1);
	}
	struct rst_chunk *c = rac_cut(&s, &cl);

	zassert_not_null(c);
	zassert_equal(c->hdr.flags & 0xFF04, 0, "bit 2 and bits 8 to 15 are zero");
	return c->hdr.flags;
}

ZTEST(audio_chunk, test_flags_each_bit)
{
	zassert_equal(flags_of(true, false, -1, 0, false, false), 0x03, "first and last only");
	zassert_equal(flags_of(true, false, -1, 0, false, true), 0x0B, "bit 3: a motor interval");
	zassert_equal(flags_of(true, false, 0, INT16_MIN, false, false), 0x13, "bit 4: -32768");
	zassert_equal(flags_of(true, false, 1, INT16_MAX, false, false), 0x13, "bit 4: 32767");
	zassert_equal(flags_of(false, false, -1, 0, false, false), 0x23, "bit 5: time not set");
	zassert_equal(flags_of(true, true, -1, 0, false, false), 0x43, "bit 6: battery at B15 or under");
	zassert_equal(flags_of(true, false, -1, 0, true, false), 0x83, "bit 7: dropout");
	/* a clipped sample in the discarded 800 frames is not stored: no flag */
	struct rst_close_args cl;

	t_reset();
	begin();
	t_feed_block_with(&s, 0, 10, 0, INT16_MIN);
	t_feed(&s, 1, 3);
	struct rst_chunk *c = rac_cut(&s, &cl);

	zassert_not_null(c);
	zassert_equal(c->hdr.flags, 0x03, "no clip flag for a sample that was dropped");
}

/* S9, FW l.535: unused payload bytes of the last chunk are zero (the buffers were filled with 0xA5), the last chunk is
 * flagged; frames are what was kept. */
ZTEST(audio_chunk, test_partial_last_chunk)
{
	struct rst_close_args cl;

	begin();
	t_feed(&s, 0, 40);
	struct rst_chunk *c1 = rac_cut(&s, &cl);

	zassert_not_null(c1);
	zassert_equal(t_fulls(), 1);
	zassert_equal(t_full(0)->hdr.flags, 0x01, "the full chunk: first only");
	zassert_equal(c1->hdr.flags, 0x02, "the partial chunk: last only");
	zassert_equal(c1->hdr.frames, 1248, "10,240 - 800 - 8,192");
	zassert_equal(c1->hdr.chunk_in_recording, 1);
	zassert_true(t_tail_zero(c1, 1248), "payload bytes after the last frame are zero");
	zassert_equal(cl.duration_frames, 9440);

	/* the stop mark inside a block: exactly 1,000 frames are kept */
	t_reset();
	begin();
	rac_set_limit(&s, 1000);
	t_feed(&s, 0, 10);
	zassert_true(rac_limit_reached(&s));
	c1 = rac_cut(&s, &cl);
	zassert_not_null(c1);
	zassert_equal(c1->hdr.frames, 1000);
	zassert_equal(cl.duration_frames, 1000);
	zassert_equal(t_left(c1, 999), 1799, "999 + 800");
	zassert_equal(t_left(c1, 1000), 0, "nothing after the mark");
	zassert_true(t_tail_zero(c1, 1000));

	/* the mark exactly at a chunk edge: that chunk has already gone to the store; no partial chunk */
	t_reset();
	begin();
	rac_set_limit(&s, 8192);
	t_feed(&s, 0, 40);
	c1 = rac_cut(&s, &cl);
	zassert_is_null(c1);
	zassert_equal(t_fulls(), 1);
	zassert_equal(cl.duration_frames, 8192);
}

/* C13, FW l.244, l.263, l.566 (ruling R24): the marker is the frame number of CENTRE_DOWN counted from the first kept
 * frame of the recording. PDM start at 1,000 ms; CENTRE_DOWN at 1,600 ms = 600 ms after the start: frame
 * 600 x 16 - 800 = 8,800. The call comes later, when 9,440 frames are kept; the chunk being filled is chunk 1. */
ZTEST(audio_chunk, test_highlight_frame_from_down_time)
{
	struct rst_close_args cl;

	begin();
	t_feed(&s, 0, 40);
	rac_highlight(&s, 1600);
	struct rst_chunk *c1 = rac_cut(&s, &cl);

	zassert_not_null(c1);
	zassert_equal(c1->hdr.highlight_count, 1);
	zassert_equal(c1->hdr.highlight_frame[0], 8800, "frame number of CENTRE_DOWN, not an offset in the chunk");
	zassert_equal(cl.highlight_count, 1);
	zassert_equal(cl.highlight_ms[0], 550, "8,800 frames = 550 ms from the first kept frame");
	zassert_equal(cl.highlight_ms[1], 0xFFFFFFFFu);
}

/* S11, FW l.564, l.566, l.582, l.632, ruling D4: up to 8 in a chunk header; the first 32 in the CLOSE record with the
 * full count. Nine in one chunk: frames 160 x k (k = 1 to 9) = CENTRE_DOWN at 1,000 + 50 + 10 k ms. */
ZTEST(audio_chunk, test_highlights_in_header)
{
	struct rst_close_args cl;

	begin();
	t_feed(&s, 0, 12);                      /* 3,072 raw frames = 2,272 kept */
	for (int k = 1; k <= 9; k++) {
		rac_highlight(&s, 1050 + 10 * k);
	}
	struct rst_chunk *c = rac_cut(&s, &cl);

	zassert_not_null(c);
	zassert_equal(c->hdr.highlight_count, 8, "a ninth stays out of the header (D4)");
	for (int k = 1; k <= 8; k++) {
		zassert_equal(c->hdr.highlight_frame[k - 1], 160 * k, "highlight %d", k);
	}
	zassert_equal(cl.highlight_count, 9, "the CLOSE record keeps the full count");
	for (int k = 1; k <= 9; k++) {
		zassert_equal(cl.highlight_ms[k - 1], 10 * k, "close ms %d", k);
	}
	zassert_equal(cl.highlight_ms[9], 0xFFFFFFFFu);

	/* 40 highlights, one every 80 ms (1,280 frames) from the first kept frame, over 6 full chunks and a partial one */
	t_reset();
	begin();
	int next = 0;

	for (uint32_t k = 0; k < 208; k++) {
		int64_t kept_after = (int64_t)(k + 1) * 256 - 800;

		while (next < 40 && 1280 * (int64_t)next < kept_after) {
			rac_highlight(&s, 1050 + 80 * next);
			next++;
		}
		t_feed(&s, k, 1);
	}
	c = rac_cut(&s, &cl);
	zassert_not_null(c);
	zassert_equal(next, 40);
	zassert_equal(cl.highlight_count, 40);
	for (int i = 0; i < 32; i++) {
		zassert_equal(cl.highlight_ms[i], 80 * i, "close ms %d", i);
	}
	int seen = 0;

	for (int n = 0; n <= t_fulls(); n++) {
		const struct rst_chunk *ch = n < t_fulls() ? t_full(n) : c;

		zassert_true(ch->hdr.highlight_count <= 8);
		for (int j = 0; j < ch->hdr.highlight_count; j++) {
			zassert_equal(ch->hdr.highlight_frame[j], 1280u * (uint32_t)seen, "highlight %d at its frame", seen);
			seen++;
		}
	}
	zassert_equal(seen, 40, "every highlight is in a header, in order");
}

/* Ruling R24, FW l.566: a highlight fires 440 to 850 ms after CENTRE_DOWN, so its frame often lies in a chunk that has
 * already gone to the store. The marker is written in the chunk being filled when it fires, with the frame number of
 * CENTRE_DOWN. CENTRE_DOWN at 1,300 ms = frame 4,000 (chunk 0, already full); chunk 1 is being filled. */
ZTEST(audio_chunk, test_late_highlight_in_next_chunk)
{
	struct rst_close_args cl;

	begin();
	t_feed(&s, 0, 40);
	zassert_equal(t_fulls(), 1);
	rac_highlight(&s, 1300);
	struct rst_chunk *c1 = rac_cut(&s, &cl);

	zassert_not_null(c1);
	zassert_equal(t_full(0)->hdr.highlight_count, 0);
	zassert_equal(c1->hdr.highlight_count, 1, "found in the next chunk's header");
	zassert_equal(c1->hdr.highlight_frame[0], 4000, "with the frame number of CENTRE_DOWN");
	zassert_equal(cl.highlight_count, 1);
	zassert_equal(cl.highlight_ms[0], 250, "4,000 frames = 250 ms");
}

/* Ruling R24, F2: the stop comes right after a full chunk went out (mark exactly at the chunk edge) and a highlight
 * fires after it: no partial chunk exists, so the marker is in the CLOSE record only. */
ZTEST(audio_chunk, test_highlight_without_partial_chunk_close_only)
{
	struct rst_close_args cl;

	begin();
	rac_set_limit(&s, 8192);
	t_feed(&s, 0, 40);
	rac_highlight(&s, 1300);
	struct rst_chunk *c = rac_cut(&s, &cl);

	zassert_is_null(c);
	zassert_equal(t_fulls(), 1);
	zassert_equal(t_full(0)->hdr.highlight_count, 0);
	zassert_equal(cl.highlight_count, 1, "kept in the CLOSE record");
	zassert_equal(cl.highlight_ms[0], 250);
}

/* S12, FW l.557, l.558, l.573: utc_ms, uptime_ns of the chunk's first frame, cycle_hz. Chunk 1 starts 8,192 frames =
 * 512 ms after chunk 0. */
ZTEST(audio_chunk, test_timestamps)
{
	struct rst_close_args cl;
	struct rst_chunk *c1;

	begin_with(true, 12000, 12000000, 1000000);
	t_feed(&s, 0, 40);
	c1 = rac_cut(&s, &cl);
	zassert_not_null(c1);
	zassert_equal(t_full(0)->hdr.uptime_ns, 12050000000ULL);
	zassert_equal(t_full(0)->hdr.utc_ms, 1700000012050LL);
	zassert_equal(t_full(0)->hdr.cycle_hz, 1000000);
	zassert_equal(c1->hdr.uptime_ns, 12562000000ULL, "+ 512 ms");
	zassert_equal(c1->hdr.utc_ms, 1700000012562LL);

	/* a counter of 16 MHz: the same instant is 192,000,000 cycles */
	t_reset();
	begin_with(true, 12000, 192000000, 16000000);
	t_feed(&s, 0, 40);
	c1 = rac_cut(&s, &cl);
	zassert_not_null(c1);
	zassert_equal(t_full(0)->hdr.uptime_ns, 12050000000ULL);
	zassert_equal(t_full(0)->hdr.cycle_hz, 16000000);
	zassert_equal(c1->hdr.uptime_ns, 12562000000ULL);

	/* 20 days of uptime on a 16 MHz counter: 27,648,000,000,000 cycles: no overflow */
	t_reset();
	begin_with(true, 1728000000, 27648000000000ULL, 16000000);
	t_feed(&s, 0, 40);
	c1 = rac_cut(&s, &cl);
	zassert_not_null(c1);
	zassert_equal(t_full(0)->hdr.uptime_ns, 1728000050000000ULL);
	zassert_equal(t_full(0)->hdr.utc_ms, 1701728000050LL);
}

/* S12, FW l.557, l.1005: time not set: utc_ms 0 in every chunk, flag bit 5; uptime_ns still written. */
ZTEST(audio_chunk, test_time_not_set)
{
	struct rst_close_args cl;

	begin_with(false, 12000, 12000000, 1000000);
	t_feed(&s, 0, 40);
	struct rst_chunk *c1 = rac_cut(&s, &cl);

	zassert_not_null(c1);
	zassert_equal(t_full(0)->hdr.utc_ms, 0);
	zassert_equal(c1->hdr.utc_ms, 0);
	zassert_true(t_full(0)->hdr.flags & RREC_CH_FLAG_TIME_NOT_SET);
	zassert_true(c1->hdr.flags & RREC_CH_FLAG_TIME_NOT_SET);
	zassert_equal(t_full(0)->hdr.uptime_ns, 12050000000ULL);
	zassert_equal(c1->hdr.uptime_ns, 12562000000ULL);
}

/* S13, FW l.567 to l.571: battery_mv and temp_c_x10 at the chunk start, boot_count, fw_version. The test's source of
 * facts gives 3,871 mV for the first chunk and 3,872 mV for the second. */
ZTEST(audio_chunk, test_fill_fields)
{
	struct rst_close_args cl;
	struct rac_start a = t_start(true, 1000, 1000000, 1000000);

	a.boot_count = 9;
	a.recording_id = 5;
	a.recording_type = RREC_REC_TYPE_FACTORY;
	t_facts(3871, -45, 0x01020003, false);
	rac_begin(&s, &a);
	t_feed(&s, 0, 40);
	struct rst_chunk *c1 = rac_cut(&s, &cl);

	zassert_not_null(c1);
	zassert_equal(t_full(0)->hdr.battery_mv, 3871);
	zassert_equal(t_full(0)->hdr.temp_c_x10, -45);
	zassert_equal(t_full(0)->hdr.boot_count, 9);
	zassert_equal(t_full(0)->hdr.fw_version, 0x01020003);
	zassert_equal(t_full(0)->hdr.recording_id, 5);
	zassert_equal(t_full(0)->hdr.recording_type, 2);
	zassert_equal(c1->hdr.battery_mv, 3872, "taken at the start of each chunk");
	zassert_equal(c1->hdr.boot_count, 9);
	zassert_equal(c1->hdr.recording_id, 5);
}
