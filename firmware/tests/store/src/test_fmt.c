/*
 * Suite store_fmt (unit U2): the byte formats of design/firmware.md 5.3, 5.4 and 9.4. Every expected byte is written
 * out here by hand from the tables (offsets and values typed, "FW l.N" = line N of design/firmware.md), with the
 * test's own bit-wise CRC-32; none of it is produced by the code under test.
 */
#include <zephyr/drivers/disk.h>
#include <zephyr/storage/disk_access.h>
#include <zephyr/sys/crc.h>

#include "tst.h"

static void *none_setup(void)
{
	return NULL;
}

static void before(void *f)
{
	ARG_UNUSED(f);
}

ZTEST_SUITE(store_fmt, NULL, none_setup, before, NULL, NULL);

static int first_diff(const uint8_t *a, const uint8_t *b, size_t n)
{
	for (size_t i = 0; i < n; i++) {
		if (a[i] != b[i]) {
			return (int)i;
		}
	}
	return -1;
}

/* K12 and S8: CRC-32/ISO-HDLC check value of "123456789" is 0xCBF43926 (catalogue value, typed) */
ZTEST(store_fmt, test_crc_check_value)
{
	zassert_equal(rst_fmt_crc32((const uint8_t *)"123456789", 9), 0xCBF43926u);
	zassert_equal(tst_crc32((const uint8_t *)"123456789", 9), 0xCBF43926u, "the test's own reference");
	zassert_equal(rst_fmt_crc32((const uint8_t *)"", 0), 0u);
	printk("store_fmt: crc32 check value 0xCBF43926 holds for crc32_ieee (K12)\n");
}

/* S8: little-endian fields (FW l.70) */
ZTEST(store_fmt, test_little_endian)
{
	uint8_t b[8];

	rst_put16(b, 0x0102);
	zassert_equal(b[0], 0x02);
	zassert_equal(b[1], 0x01);
	rst_put32(b, 0x01020304u);
	zassert_equal(b[0], 0x04);
	zassert_equal(b[3], 0x01);
	rst_put64(b, 0x0102030405060708ull);
	zassert_equal(b[0], 0x08);
	zassert_equal(b[7], 0x01);
	zassert_equal(rst_get64(b), 0x0102030405060708ull);
	zassert_equal(rst_get32(b), 0x05060708u);
	zassert_equal(rst_get16(b), 0x0708);
}

static struct rst_chunk chk;
static uint8_t exp_chunk[RREC_CHUNK_BYTES];

/* S7, A3, S9: the chunk header, every field at its offset (FW l.541 to l.580, the table of 5.3) */
ZTEST(store_fmt, test_chunk_header_bytes)
{
	uint32_t pcrc;

	memset(&chk, 0, sizeof(chk));
	for (uint32_t i = 0; i < 32768; i++) {
		chk.bytes[512 + i] = (uint8_t)i;
	}
	chk.hdr.chunk_seq = 7;
	chk.hdr.recording_id = 3;
	chk.hdr.chunk_in_recording = 2;
	chk.hdr.flags = 0x00A9;                       /* bits 0, 3, 5, 7 */
	chk.hdr.recording_type = 1;
	chk.hdr.frames = 8192;
	chk.hdr.first_frame_index = 16384;
	chk.hdr.utc_ms = 1700000000123ll;
	chk.hdr.uptime_ns = 123456789012ull;
	chk.hdr.highlight_count = 2;
	chk.hdr.highlight_frame[0] = 1000;
	chk.hdr.highlight_frame[1] = 5000;
	chk.hdr.battery_mv = 3911;
	chk.hdr.temp_c_x10 = -25;
	chk.hdr.boot_count = 4;
	chk.hdr.dropout_blocks = 1;
	chk.hdr.fw_version = 0x01020304u;
	chk.hdr.cycle_hz = 1000000;
	chk.hdr.motor_count = 1;
	chk.hdr.motor_frames[0][0] = 100;
	chk.hdr.motor_frames[0][1] = 900;
	zassert_equal(rst_fmt_chunk_encode(&chk, &pcrc), 0);

	memset(exp_chunk, 0, sizeof(exp_chunk));
	uint8_t *e = exp_chunk;

	tst_le(e, 0, 0x4B435252u, 4);                 /* magic "RRCK" (FW l.541) */
	tst_le(e, 4, 1, 2);                           /* header_version */
	tst_le(e, 6, 512, 2);                         /* header_size */
	tst_le(e, 8, 7, 4);                           /* chunk_seq */
	tst_le(e, 12, 3, 4);                          /* recording_id */
	tst_le(e, 16, 2, 4);                          /* chunk_in_recording */
	tst_le(e, 20, 0x00A9, 2);                     /* flags */
	tst_le(e, 22, 1, 1);                          /* recording_type */
	tst_le(e, 23, 2, 1);                          /* channels */
	tst_le(e, 24, 16000, 4);                      /* sample_rate_hz */
	tst_le(e, 28, 1, 1);                          /* sample_format */
	tst_le(e, 29, 0x03, 1);                       /* mic_mask */
	tst_le(e, 32, 8192, 4);                       /* frames */
	tst_le(e, 36, 32768, 4);                      /* payload_bytes = frames x 2 x 2 */
	tst_le(e, 40, 16384, 8);                      /* first_frame_index */
	tst_le(e, 48, 1700000000123ull, 8);           /* utc_ms */
	tst_le(e, 56, 123456789012ull, 8);            /* uptime_ns */
	tst_le(e, 68, 1280000, 4);                    /* pdm_clock_hz */
	tst_le(e, 72, 80, 2);                         /* pdm_ratio */
	tst_le(e, 74, 0x28, 1);                       /* gain_code */
	tst_le(e, 76, 2, 2);                          /* highlight_count */
	tst_le(e, 80, 1000, 4);                       /* highlight_frame 0 */
	tst_le(e, 84, 5000, 4);
	for (unsigned i = 2; i < 8; i++) {
		tst_le(e, 80 + 4 * i, 0xFFFFFFFFu, 4);        /* unused */
	}
	tst_le(e, 112, 3911, 2);                      /* battery_mv */
	tst_le(e, 114, 0xFFE7, 2);                    /* temp_c_x10 = -25 */
	tst_le(e, 116, 4, 4);                         /* boot_count */
	tst_le(e, 120, 1, 4);                         /* dropout_blocks */
	tst_le(e, 124, 0x01020304u, 4);               /* fw_version */
	tst_le(e, 132, 1000000, 4);                   /* cycle_hz */
	tst_le(e, 144, 1, 4);                         /* motor_count */
	tst_le(e, 148, 100, 4);                       /* motor 0 start */
	tst_le(e, 152, 900, 4);                       /* motor 0 end */
	for (unsigned i = 1; i < 4; i++) {
		tst_le(e, 148 + 8 * i, 0xFFFFFFFFu, 4);
		tst_le(e, 152 + 8 * i, 0xFFFFFFFFu, 4);
	}
	for (uint32_t i = 0; i < 32768; i++) {
		e[512 + i] = (uint8_t)i;
	}
	uint32_t pc = tst_crc32(e + 512, 32768);

	tst_le(e, 504, pc, 4);                        /* payload_crc32 */
	tst_le(e, 508, tst_crc32(e, 508), 4);         /* header_crc32 over bytes 0 to 507 */

	int d = first_diff(chk.bytes, exp_chunk, RREC_CHUNK_BYTES);

	zassert_equal(d, -1, "first differing byte at offset %d (header 0 to 511, payload from 512)", d);
	zassert_equal(pcrc, pc);
}

/* S9: unused payload bytes of a last chunk are zero (FW l.535), payload_bytes = frames x 2 x 2 */
ZTEST(store_fmt, test_last_chunk_zero_tail)
{
	uint32_t pcrc;

	memset(&chk, 0, sizeof(chk));
	memset(chk.bytes + 512, 0xAA, 32768);
	chk.hdr.frames = 100;
	chk.hdr.recording_type = 1;
	zassert_equal(rst_fmt_chunk_encode(&chk, &pcrc), 0);
	for (uint32_t i = 0; i < 32768; i++) {
		uint8_t want = i < 400 ? 0xAA : 0;

		zassert_equal(chk.bytes[512 + i], want, "payload byte %u", i);
	}
	zassert_equal(rst_get32(chk.bytes + 36), 400u, "payload_bytes");
	uint8_t ref[32768];

	memset(ref, 0, sizeof(ref));
	memset(ref, 0xAA, 400);
	zassert_equal(pcrc, tst_crc32(ref, sizeof(ref)), "the payload CRC covers all 32,768 bytes");
}

ZTEST(store_fmt, test_chunk_header_roundtrip_and_rejects)
{
	struct rst_chunk_hdr h;
	uint32_t pcrc, p2;

	tst_fill(&chk, 9, 4, 8192, 3);
	chk.hdr.chunk_seq = 21;
	chk.hdr.highlight_count = 8;
	for (unsigned i = 0; i < 8; i++) {
		chk.hdr.highlight_frame[i] = 100 * (i + 1);
	}
	chk.hdr.motor_count = 4;
	for (unsigned i = 0; i < 4; i++) {
		chk.hdr.motor_frames[i][0] = 10 * i;
		chk.hdr.motor_frames[i][1] = 10 * i + 5;
	}
	zassert_equal(rst_fmt_chunk_encode(&chk, &pcrc), 0);
	zassert_equal(rst_fmt_chunk_verify(chk.bytes, &h, &p2), 0);
	zassert_equal(p2, pcrc);
	zassert_equal(h.chunk_seq, 21u);
	zassert_equal(h.recording_id, 9u);
	zassert_equal(h.chunk_in_recording, 4u);
	zassert_equal(h.frames, 8192u);
	zassert_equal(h.highlight_count, 8u);
	zassert_equal(h.highlight_frame[7], 800u);
	zassert_equal(h.motor_count, 4u);
	zassert_equal(h.motor_frames[3][1], 35u);
	zassert_equal(h.temp_c_x10, 301);
	zassert_equal(h.utc_ms, 1700000000000ll + 4 * 512);

	static uint8_t bad[RREC_CHUNK_BYTES];

	memcpy(bad, chk.bytes, sizeof(bad));
	bad[0] ^= 1;                                  /* magic */
	zassert_equal(rst_fmt_chunk_verify(bad, &h, NULL), -EBADMSG);
	memcpy(bad, chk.bytes, sizeof(bad));
	bad[4] = 2;                                   /* version (header CRC then also differs) */
	zassert_equal(rst_fmt_chunk_verify(bad, &h, NULL), -EBADMSG);
	memcpy(bad, chk.bytes, sizeof(bad));
	bad[508] ^= 1;                                /* header CRC */
	zassert_equal(rst_fmt_chunk_verify(bad, &h, NULL), -EBADMSG);
	memcpy(bad, chk.bytes, sizeof(bad));
	bad[512 + 17000] ^= 1;                        /* payload */
	zassert_equal(rst_fmt_chunk_verify(bad, &h, NULL), -EILSEQ);
}

ZTEST(store_fmt, test_chunk_encode_rejects_bad_counts)
{
	tst_fill(&chk, 1, 0, 0, 0);
	zassert_equal(rst_fmt_chunk_encode(&chk, NULL), -EINVAL, "0 frames");
	tst_fill(&chk, 1, 0, 8193, 0);
	zassert_equal(rst_fmt_chunk_encode(&chk, NULL), -EINVAL, "8193 frames");
	tst_fill(&chk, 1, 0, 8192, 0);
	chk.hdr.highlight_count = 9;
	zassert_equal(rst_fmt_chunk_encode(&chk, NULL), -EINVAL, "9 highlights (decision D4: a ninth stays out)");
	chk.hdr.highlight_count = 0;
	chk.hdr.motor_count = 5;
	zassert_equal(rst_fmt_chunk_encode(&chk, NULL), -EINVAL, "5 motor intervals");
}

ZTEST(store_fmt, test_unused_slots_are_ff)
{
	tst_fill(&chk, 1, 0, 8192, 0);
	memset(chk.hdr.highlight_frame, 0x11, sizeof(chk.hdr.highlight_frame));
	memset(chk.hdr.motor_frames, 0x22, sizeof(chk.hdr.motor_frames));
	chk.hdr.highlight_count = 1;
	chk.hdr.motor_count = 1;
	zassert_equal(rst_fmt_chunk_encode(&chk, NULL), 0);
	zassert_equal(rst_get32(chk.bytes + 80), 0x11111111u, "the one used slot is kept");
	for (unsigned i = 1; i < 8; i++) {
		zassert_equal(rst_get32(chk.bytes + 80 + 4 * i), 0xFFFFFFFFu, "highlight slot %u", i);
	}
	for (unsigned i = 1; i < 4; i++) {
		zassert_equal(rst_get32(chk.bytes + 148 + 8 * i), 0xFFFFFFFFu, "motor start %u", i);
		zassert_equal(rst_get32(chk.bytes + 152 + 8 * i), 0xFFFFFFFFu, "motor end %u", i);
	}
}

/* S14: superblock fields (FW l.587 to l.610) */
ZTEST(store_fmt, test_superblock_bytes)
{
	struct rst_sb s = {
		.sb_seq = 5, .card_sectors = 7812500, .chunk_first_lba = 81920, .chunk_count_total = 118932,
		.head_chunk_seq = 41, .tail_chunk_seq = 9, .next_recording_id = 6, .index_head = 12, .index_tail = 3,
		.open_flag = 1, .open_recording_id = 5, .open_first_chunk_seq = 33, .boot_count = 2, .log_head = 17,
	};
	uint8_t got[512], exp[512], *e = exp;

	rst_fmt_sb_encode(&s, got);
	memset(exp, 0, sizeof(exp));
	tst_le(e, 0, 0x42535252u, 4);                 /* magic "RRSB" */
	tst_le(e, 4, 1, 2);                           /* version */
	tst_le(e, 6, 512, 2);                         /* size */
	tst_le(e, 8, 5, 4);                           /* sb_seq */
	tst_le(e, 12, 7812500, 4);                    /* card_sectors */
	tst_le(e, 16, 81920, 4);                      /* chunk_area_first_lba */
	tst_le(e, 20, 118932, 4);                     /* chunk_count_total */
	tst_le(e, 24, 41, 4);                         /* head_chunk_seq */
	tst_le(e, 28, 9, 4);                          /* tail_chunk_seq */
	tst_le(e, 32, 6, 4);                          /* next_recording_id */
	tst_le(e, 36, 12, 4);                         /* index_head */
	tst_le(e, 40, 3, 4);                          /* index_tail */
	tst_le(e, 44, 1, 1);                          /* open_flag */
	tst_le(e, 48, 5, 4);                          /* open_recording_id */
	tst_le(e, 52, 33, 4);                         /* open_first_chunk_seq */
	tst_le(e, 56, 2, 4);                          /* boot_count */
	tst_le(e, 60, 17, 4);                         /* log_head */
	tst_le(e, 508, tst_crc32(e, 508), 4);         /* crc32 over bytes 0 to 507 */
	int d = first_diff(got, exp, 512);

	zassert_equal(d, -1, "first differing byte at offset %d", d);

	struct rst_sb back;

	zassert_equal(rst_fmt_sb_decode(got, &back), 0);
	zassert_equal(back.head_chunk_seq, 41u);
	zassert_equal(back.open_flag, 1);
	zassert_equal(back.log_head, 17u);
	zassert_equal(back.index_tail, 3u);
	got[100] ^= 1;
	zassert_equal(rst_fmt_sb_decode(got, &back), -EBADMSG, "a changed reserved byte fails the CRC");
}

/* S15: index record fields (FW l.616 to l.634) */
ZTEST(store_fmt, test_index_record_bytes)
{
	struct rst_ix x = {
		.type = RREC_IX_TYPE_CLOSE, .close_state = RREC_IX_CLOSE_RECOVERED, .record_number = 11,
		.recording_id = 4, .first_chunk_seq = 100, .chunk_count = 200, .recording_type = 2, .channels = 2,
		.highlight_count = 3, .sample_rate_hz = 16000, .start_utc_ms = 1700000000123ll,
		.duration_frames = 1638400, .digest = 0xCAFEBABEu,
	};
	uint8_t got[512], exp[512], *e = exp;

	memset(x.highlight_ms, 0xFF, sizeof(x.highlight_ms));
	x.highlight_ms[0] = 1000;
	x.highlight_ms[1] = 2000;
	x.highlight_ms[2] = 3000;
	rst_fmt_ix_encode(&x, got);
	memset(exp, 0, sizeof(exp));
	tst_le(e, 0, 0x58495252u, 4);                 /* magic "RRIX" */
	tst_le(e, 4, 1, 2);                           /* version */
	tst_le(e, 6, 1, 1);                           /* type CLOSE */
	tst_le(e, 7, 2, 1);                           /* close state RECOVERED */
	tst_le(e, 8, 11, 4);                          /* record number */
	tst_le(e, 12, 4, 4);                          /* recording_id */
	tst_le(e, 16, 100, 4);                        /* first_chunk_seq */
	tst_le(e, 20, 200, 4);                        /* chunk_count */
	tst_le(e, 24, 2, 1);                          /* recording_type */
	tst_le(e, 25, 2, 1);                          /* channels */
	tst_le(e, 26, 3, 2);                          /* highlight_count */
	tst_le(e, 28, 16000, 4);                      /* sample_rate_hz */
	tst_le(e, 32, 1700000000123ull, 8);           /* start_utc_ms */
	tst_le(e, 40, 1638400, 8);                    /* duration_frames */
	tst_le(e, 48, 0xCAFEBABEu, 4);                /* digest */
	tst_le(e, 56, 1000, 4);                       /* highlight times in ms */
	tst_le(e, 60, 2000, 4);
	tst_le(e, 64, 3000, 4);
	for (unsigned i = 3; i < 32; i++) {
		tst_le(e, 56 + 4 * i, 0xFFFFFFFFu, 4);
	}
	tst_le(e, 508, tst_crc32(e, 508), 4);
	int d = first_diff(got, exp, 512);

	zassert_equal(d, -1, "first differing byte at offset %d", d);

	struct rst_ix back;

	zassert_equal(rst_fmt_ix_decode(got, &back), 0);
	zassert_equal(back.type, RREC_IX_TYPE_CLOSE);
	zassert_equal(back.close_state, RREC_IX_CLOSE_RECOVERED);
	zassert_equal(back.start_utc_ms, 1700000000123ll);
	zassert_equal(back.digest, 0xCAFEBABEu);
	zassert_equal(back.highlight_ms[2], 3000u);
	zassert_equal(back.highlight_ms[3], 0xFFFFFFFFu);
	got[7] ^= 1;
	zassert_equal(rst_fmt_ix_decode(got, &back), -EBADMSG);
}

/* S16: digest = CRC-32 over the payload_crc32 values of the chunks in order, 4-byte little-endian words (FW l.630).
 * The values were computed once with Python's zlib on the Mac (build-logs/step6/u2-typed-values.log) and typed here. */
ZTEST(store_fmt, test_digest)
{
	uint32_t s = 0;

	s = rst_fmt_digest_add(s, 0x11111111u);
	s = rst_fmt_digest_add(s, 0x22222222u);
	s = rst_fmt_digest_add(s, 0x33333333u);
	zassert_equal(s, 0x6ddb5d74u, "3 chunks: got 0x%08x", s);
	zassert_equal(rst_fmt_digest_add(0, 0xDEADBEEFu), 0x1a5a601fu, "1 chunk");
	zassert_equal(rst_fmt_digest_add(0, 0x11111111u) != rst_fmt_digest_add(0, 0x11111112u), true);
}

ZTEST(store_fmt, test_digest_stream_equals_oneshot)
{
	uint8_t words[16];
	uint32_t s = 0, v[4] = { 0x01020304u, 0xA0B0C0D0u, 0, 0xFFFFFFFFu };

	for (unsigned i = 0; i < 4; i++) {
		s = rst_fmt_digest_add(s, v[i]);
		tst_le(words, i * 4, v[i], 4);
	}
	zassert_equal(s, tst_crc32(words, sizeof(words)), "the chained CRC equals one CRC over all the words");
}

/* T26: the event log record (FW l.1062, l.1063) */
ZTEST(store_fmt, test_log_record_bytes)
{
	struct rrec_logrec r;
	uint8_t got[512], exp[512], *e = exp;

	memset(&r, 0, sizeof(r));
	r.seq = 77;
	r.uptime_ns = 5000000000ll;
	r.utc_ms = 1700000000123ll;
	r.code = 0x0011;
	r.state = 4;
	for (unsigned i = 0; i < 16; i++) {
		r.args[i] = (uint8_t)(0x30 + i);
	}
	rst_fmt_log_encode(&r, got);
	memset(exp, 0, sizeof(exp));
	tst_le(e, 0, 0x474C5252u, 4);                 /* magic "RRLG" */
	tst_le(e, 4, 77, 4);                          /* record seq */
	tst_le(e, 8, 5000000000ull, 8);               /* uptime_ns */
	tst_le(e, 16, 1700000000123ull, 8);           /* utc_ms */
	tst_le(e, 24, 0x0011, 2);                     /* code */
	tst_le(e, 26, 4, 1);                          /* state; byte 27 reserved */
	for (unsigned i = 0; i < 16; i++) {
		e[28 + i] = (uint8_t)(0x30 + i);          /* 16 argument bytes */
	}
	tst_le(e, 508, tst_crc32(e, 508), 4);         /* CRC-32 in the last 4 bytes */
	int d = first_diff(got, exp, 512);

	zassert_equal(d, -1, "no crash: first differing byte at offset %d", d);

	/* with a crash block (FW l.1063): reason, PC, LR, PSR (4 bytes each), thread name 16 bytes, 64 stack words */
	r.has_crash = true;
	r.crash.reason = 0x11111111u;
	r.crash.pc = 0x22222222u;
	r.crash.lr = 0x33333333u;
	r.crash.psr = 0x44444444u;
	strcpy(r.crash.thread, "audio");
	for (unsigned i = 0; i < 64; i++) {
		r.crash.stack[i] = 0x1000u + i;
	}
	rst_fmt_log_encode(&r, got);
	tst_le(e, 44, 0x11111111u, 4);
	tst_le(e, 48, 0x22222222u, 4);
	tst_le(e, 52, 0x33333333u, 4);
	tst_le(e, 56, 0x44444444u, 4);
	memcpy(e + 60, "audio", 6);                  /* thread name, 16 bytes, zero padded */
	for (unsigned i = 0; i < 64; i++) {
		tst_le(e, 76 + 4 * i, 0x1000u + i, 4);
	}
	tst_le(e, 508, tst_crc32(e, 508), 4);
	d = first_diff(got, exp, 512);
	zassert_equal(d, -1, "crash: first differing byte at offset %d", d);

	struct rrec_logrec back;

	zassert_equal(rst_fmt_log_decode(got, &back), 0);
	zassert_equal(back.seq, 77u);
	zassert_equal(back.code, 0x0011);
	zassert_true(back.has_crash);
	zassert_equal(back.crash.pc, 0x22222222u);
	zassert_equal(back.crash.stack[63], 0x1000u + 63);
	zassert_equal(strcmp(back.crash.thread, "audio"), 0);
	zassert_equal(back.args[15], 0x3F);
	got[30] ^= 1;
	zassert_equal(rst_fmt_log_decode(got, &back), -EBADMSG);
	rst_fmt_log_encode(&r, got);
	got[0] ^= 1;
	zassert_equal(rst_fmt_log_decode(got, &back), -EBADMSG);
}

/* K2 (step 6 plan section 8): the kit names the real file rst_hw_real.c relies on exist. A compile test: nothing is
 * called, nothing of the kit is printed; the arguments of the calls are NOT checked (the real file is not proven). */
ZTEST(store_fmt, test_kit_disk_and_crc_names_exist)
{
	/* typeof names the function without referring to it, so nothing is linked */
	__typeof__(disk_access_read) *p1 = NULL;
	__typeof__(disk_access_write) *p2 = NULL;
	__typeof__(disk_access_ioctl) *p3 = NULL;
	__typeof__(crc32_ieee) *p4 = NULL;
	__typeof__(crc32_ieee_update) *p5 = NULL;

	zassert_true(p1 == NULL && p2 == NULL && p3 == NULL && p4 == NULL && p5 == NULL);
	zassert_true(DISK_IOCTL_CTRL_INIT != DISK_IOCTL_CTRL_DEINIT);
	zassert_true(DISK_IOCTL_GET_SECTOR_COUNT != DISK_IOCTL_CTRL_INIT);
	zassert_true(DISK_IOCTL_GET_SECTOR_COUNT != DISK_IOCTL_CTRL_DEINIT);
	printk("K2: disk_access_read, disk_access_write, disk_access_ioctl, DISK_IOCTL_CTRL_INIT, DISK_IOCTL_CTRL_DEINIT, "
	       "DISK_IOCTL_GET_SECTOR_COUNT, crc32_ieee, crc32_ieee_update exist (compile test)\n");
}
