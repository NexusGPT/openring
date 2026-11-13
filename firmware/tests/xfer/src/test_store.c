/*
 * test_store.c: suite xfer_store (unit U4): the protocol over the simulated USB transport against the store's real
 * code (ring_store) on the simulated card. The backend is glue.c, standing for the join. Rows X8 to X11, X15, X20,
 * C24, S26 to S29 of firmware/docs/step6-plan.md. Expected values are typed from design/firmware.md (l.529, l.531,
 * l.630, l.658 to l.661, l.696 to l.706, l.1062); the test card is small so that chunks wrap.
 */
#include "glue.h"
#include "xt.h"

#define CARD_CHUNKS 24u

static struct rst_mount_info mi;
static uint8_t rq[RXF_REQ_BYTES];
#define BIG_MAX (16u + 5u * RREC_CHUNK_BYTES + 64u)
static uint8_t big[BIG_MAX];
static size_t big_n;

static void big_sink(const uint8_t *d, size_t n)
{
	if (big_n + n <= BIG_MAX) {
		memcpy(big + big_n, d, n);
	}
	big_n += n;
}

static void setup(uint32_t chunks)
{
	rhw_sim_reset();
	glue_reset();
	rhw_sim_disk_set_sectors(81920u + 65u * chunks);
	zassert_equal(rst_init(NULL), 0);
	zassert_equal(rst_mount(true, &mi), 0);
	gl.boot_count = mi.boot_count;
	zassert_equal(rxf_start(glue_be(), NULL), 0);
	rhw_sim_vbus(true);
	k_msleep(2);
	rhw_sim_usb_event(RHW_USB_CONFIGURED);
	k_msleep(2);
}

static void before(void *f)
{
	ARG_UNUSED(f);
	setup(CARD_CHUNKS);
}

static void after(void *f)
{
	ARG_UNUSED(f);
	(void)rxf_finish(5000);
	rhw_sim_usb_host_sink(NULL);
	(void)rst_unmount();
}

ZTEST_SUITE(xfer_store, NULL, NULL, before, after, NULL);

/* one request over the transport; the whole response is in big[], returns its length */
static size_t xfer(uint8_t op, uint32_t tag, const void *pl, uint32_t plen)
{
	size_t n = xt_req(rq, op, tag, pl, plen);

	big_n = 0;
	memset(big, 0, 32);
	rhw_sim_usb_host_sink(big_sink);
	zassert_equal(rhw_sim_usb_host_write(rq, n), 0);
	for (uint32_t t = 0; t < 5000; t++) {
		if (big_n >= 16u && big_n >= 16u + xt_le(big + 8, 4)) {
			break;
		}
		k_msleep(1);
	}
	zassert_equal(rxf_finish(5000), 0);
	rhw_sim_usb_host_sink(NULL);
	zassert_true(big_n >= 16u, "a response came");
	zassert_equal(big_n, 16u + xt_le(big + 8, 4), "exactly 16 + length bytes");
	zassert_equal(xt_le(big + 4, 4), tag, "tag echoed");
	if (big_n <= BIG_MAX) {
		zassert_equal(xt_le(big + 12, 4), big_n == 16u ? 0u : xt_crc(0, big + 16, big_n - 16u),
			      "the header's crc is the reference CRC of the payload, 0 when empty");
	}
	return big_n;
}

static uint8_t st(void)
{
	return big[3];
}

/* ---- recordings written by the store's real code */
static struct rst_chunk wchunk;
static volatile int done_n;
static volatile int done_err;

static void done_cb(struct rst_chunk *c, int err)
{
	ARG_UNUSED(c);
	if (err != 0) {
		done_err = err;
	}
	done_n++;
}

static void fill(struct rst_chunk *c, uint32_t id, uint32_t i, uint32_t seed)
{
	uint16_t *p = (uint16_t *)(c->bytes + 512);

	memset(c, 0, sizeof(*c));
	for (uint32_t k = 0; k < 16384; k++) {
		p[k] = (uint16_t)(seed * 977u + k * 13u + i * 5u + 1u);
	}
	c->hdr.recording_id = id;
	c->hdr.chunk_in_recording = i;
	c->hdr.flags = i == 0 ? 1u : 0u;
	c->hdr.recording_type = RREC_REC_TYPE_RECORDING;
	c->hdr.frames = RREC_CHUNK_FRAMES;
	c->hdr.first_frame_index = (uint64_t)i * RREC_CHUNK_FRAMES;
	c->hdr.utc_ms = 1700000000000ll + i * 512;
	c->hdr.uptime_ns = 5000000000ull + i * 512000000ull;
	c->hdr.battery_mv = 3900;
	c->hdr.temp_c_x10 = 301;
	c->hdr.boot_count = 1;
	c->hdr.fw_version = GLUE_FW_VERSION;
	c->hdr.cycle_hz = 1000000;
	memset(c->hdr.highlight_frame, 0xFF, sizeof(c->hdr.highlight_frame));
	memset(c->hdr.motor_frames, 0xFF, sizeof(c->hdr.motor_frames));
}

/* the digest a case computes (FW l.630) over chunks filled with `seed`: CRC-32 over the payload CRCs as 4-byte
 * little-endian words, with the test's own reference CRC */
static uint32_t ref_digest(uint32_t id, uint32_t n, uint32_t seed)
{
	static struct rst_chunk c;
	uint8_t words[64 * 4];

	for (uint32_t i = 0; i < n; i++) {
		fill(&c, id, i, seed);
		xt_put(words + 4 * i, xt_crc(0, c.bytes + 512, 32768), 4);
	}
	return xt_crc(0, words, 4u * n);
}

static void record(uint32_t n, uint32_t seed, uint32_t *id)
{
	struct rst_close_args a = { .duration_frames = (uint64_t)n * RREC_CHUNK_FRAMES };

	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 1700000000000ll, id), 0);
	done_n = 0;
	done_err = 0;
	for (uint32_t i = 0; i < n; i++) {
		fill(&wchunk, *id, i, seed);
		zassert_equal(rst_put_chunk(&wchunk, done_cb), 0);
		for (uint32_t t = 0; t < 20000 && done_n < (int)i + 1; t++) {
			k_msleep(1);
		}
		zassert_equal(done_n, (int)i + 1, "chunk %u written", i);
		zassert_equal(done_err, 0);
	}
	memset(a.highlight_ms, 0xFF, sizeof(a.highlight_ms));
	zassert_equal(rst_close(NULL, &a), 0);
}

static uint32_t chunk_lba(uint32_t total, uint32_t seq)
{
	return 81920u + (seq % total) * 65u;     /* FW l.531 */
}

/* the first_chunk_seq the ring lists for a recording (where its chunks start in the card's sequence) */
static uint32_t first_seq(uint32_t id)
{
	uint8_t pl[6];

	xt_put(pl, id, 4);
	xt_put(pl + 4, 1, 2);
	zassert_equal(xfer(RREC_OP_LIST_RECORDINGS, 0x1F, pl, 6), 16u + 2u + 64u);
	zassert_equal(xt_le(big + 18, 4), id, "listed");
	return xt_le(big + 18 + 8, 4);
}

/* X8 (with real values): GET_INFO from the store; layout typed from FW l.696 */
ZTEST(xfer_store, test_get_info_from_store)
{
	uint32_t a, b;
	uint64_t id = 0;

	record(2, 1, &a);
	record(3, 2, &b);
	zassert_equal(xfer(RREC_OP_GET_INFO, 0x10, NULL, 0), 16u + 35u);
	zassert_equal(st(), RREC_ST_OK);
	zassert_equal(xt_le(big + 16, 2), 1u, "protocol version 1");
	zassert_equal(xt_le(big + 16 + 2, 4), GLUE_FW_VERSION);
	(void)rhw_clock()->device_id(&id);
	zassert_equal(xt_le64(big + 16 + 6), id, "device id u64 at offset 6");
	zassert_equal(xt_le(big + 16 + 14, 4), 81920u + 65u * CARD_CHUNKS, "card_sectors at 14");
	zassert_equal(xt_le(big + 16 + 18, 4), CARD_CHUNKS, "chunk_count_total at 18: floor((sectors - 81,920) / 65)");
	zassert_equal(xt_le(big + 16 + 22, 4), CARD_CHUNKS - 5u, "free_chunks at 22");
	zassert_equal(xt_le(big + 16 + 26, 4), 2u, "recordings (not deleted) at 26");
	zassert_equal(xt_le(big + 16 + 30, 4), mi.boot_count, "boot_count at 30");
	zassert_equal(big[16 + 34], 0u, "factory flag at 34");
}

/* X9, D5: LIST_RECORDINGS: 64-byte entries after a u16 count; "first" is a recording id (0 = the oldest not deleted) */
ZTEST(xfer_store, test_list_entries)
{
	uint32_t a, b, c;
	uint8_t pl[6];

	record(2, 1, &a);
	record(3, 2, &b);
	record(1, 3, &c);
	xt_put(pl, 0, 4);
	xt_put(pl + 4, 64, 2);
	zassert_equal(xfer(RREC_OP_LIST_RECORDINGS, 0x20, pl, 6), 16u + 2u + 3u * 64u);
	zassert_equal(st(), RREC_ST_OK);
	zassert_equal(xt_le(big + 16, 2), 3u, "count");
	static const uint32_t chunks[3] = { 2, 3, 1 };
	uint32_t ids[3] = { a, b, c };
	/* first_chunk_seq: the sequence is global and each recording starts where the one before it ended */
	uint32_t base = xt_le(big + 18 + 8, 4);
	const uint32_t firsts[3] = { base, base + 2, base + 5 };

	printk("first_chunk_seq of the first recording: %u\n", base);

	for (unsigned i = 0; i < 3; i++) {
		const uint8_t *e = big + 18 + 64 * i;

		zassert_equal(xt_le(e + 0, 4), ids[i], "recording_id of entry %u", i);
		zassert_equal(e[4], 1u, "type 1: recording");
		zassert_equal(e[5], 2u, "2 channels");
		zassert_equal(e[6], 1u, "state 1: new");
		zassert_equal(e[7], 0u, "reserved");
		zassert_equal(xt_le(e + 8, 4), firsts[i], "first_chunk_seq");
		zassert_equal(xt_le(e + 12, 4), chunks[i], "chunk_count");
		zassert_equal(xt_le(e + 16, 4), 16000u, "sample_rate_hz");
		zassert_equal(xt_le64(e + 20), 1700000000000ull, "start_utc_ms");
		zassert_equal(xt_le64(e + 28), (uint64_t)chunks[i] * 8192u, "duration_frames");
		zassert_equal(xt_le(e + 36, 4), ref_digest(ids[i], chunks[i], i + 1u), "digest of the CLOSE record");
		for (unsigned k = 42; k < 64; k++) {
			zassert_equal(e[k], 0u, "reserved bytes %u", k);
		}
	}
	/* "first" is a recording id: the list starts at that id */
	xt_put(pl, b, 4);
	zassert_equal(xfer(RREC_OP_LIST_RECORDINGS, 0x21, pl, 6), 16u + 2u + 2u * 64u);
	zassert_equal(xt_le(big + 18, 4), b);
	xt_put(pl, b + 1, 4);
	zassert_equal(xfer(RREC_OP_LIST_RECORDINGS, 0x22, pl, 6), 16u + 2u + 64u);
	zassert_equal(xt_le(big + 18, 4), c, "an id between two recordings starts at the next one");
	xt_put(pl, c + 100, 4);
	zassert_equal(xfer(RREC_OP_LIST_RECORDINGS, 0x23, pl, 6), 16u + 2u);
	zassert_equal(xt_le(big + 16, 2), 0u, "past the newest: count 0");
	/* max limits the count */
	xt_put(pl, 0, 4);
	xt_put(pl + 4, 2, 2);
	zassert_equal(xfer(RREC_OP_LIST_RECORDINGS, 0x24, pl, 6), 16u + 2u + 2u * 64u);
	xt_put(pl + 4, 65, 2);
	zassert_equal(xfer(RREC_OP_LIST_RECORDINGS, 0x25, pl, 6), 16u);
	zassert_equal(st(), RREC_ST_BAD_ARG);
}

/* confirm and delete one recording over the transport (the case's last two steps) */
static uint32_t confirm_delete(uint32_t id, uint32_t n, uint32_t seed, uint32_t tag)
{
	uint8_t cf[8];

	xt_put(cf, id, 4);
	xt_put(cf + 4, ref_digest(id, n, seed), 4);
	zassert_equal(xfer(RREC_OP_CONFIRM, tag, cf, 8), 16u);
	zassert_equal(st(), RREC_ST_OK);
	zassert_equal(xfer(RREC_OP_DELETE, tag + 1, cf, 4), 16u + 4u);
	zassert_equal(st(), RREC_ST_OK);
	return xt_le(big + 16, 4);
}

/* X10: each chunk exactly as stored: the response bytes equal the card's sectors, also where the chunk area wraps
 * (the card has 20 chunk slots; a recording is opened only above 16 free slots, so recordings are recycled until the
 * sequence number passes 20) */
/* the chunks of a recording read over USB equal the card's sectors at the LBAs of FW l.531 */
static void check_against_disk(uint32_t id, uint32_t n, uint32_t total, uint32_t tag)
{
	uint8_t pl[12], sec[512];
	uint32_t base = first_seq(id);

	xt_put(pl, id, 4);
	xt_put(pl + 4, 0, 4);
	xt_put(pl + 8, n, 4);
	zassert_equal(xfer(RREC_OP_READ_RANGE, tag, pl, 12), 16u + n * 33280u);
	zassert_equal(st(), RREC_ST_OK);
	for (uint32_t k = 0; k < n; k++) {
		for (uint32_t s = 0; s < 65; s++) {
			rhw_sim_disk_peek(chunk_lba(total, base + k) + s, sec);
			zassert_mem_equal(big + 16 + k * 33280 + s * 512, sec, 512, "chunk %u (seq %u) sector %u", k,
					  base + k, s);
		}
	}
}

/* X10: each chunk exactly as stored: the response bytes equal the card's sectors, also where the chunk area wraps
 * (the card has 20 chunk slots; a recording is opened only above 16 free slots, so recordings are recycled by
 * confirm and delete until one has a chunk whose sequence number reaches 20) */
ZTEST(xfer_store, test_read_range_bytes_equal_disk)
{
	uint32_t a, total = 20, wrapped = 0;

	setup(total);
	record(3, 1, &a);
	check_against_disk(a, 3, total, 0x30);
	zassert_equal(confirm_delete(a, 3, 1, 0x31), total, "all slots free again");
	for (uint32_t r = 0; r < 10 && wrapped == 0; r++) {
		uint32_t x;

		record(3, 10 + r, &x);
		if (first_seq(x) + 3u > total) {
			wrapped = x;                       /* its last chunk(s) sit past the end of the sequence */
			check_against_disk(x, 3, total, 0x50);
			zassert_true(first_seq(x) + 2u >= total, "a chunk with a sequence number of 20 or more");
			zassert_not_equal(chunk_lba(total, first_seq(x) + 2u), 81920u + (first_seq(x) + 2u) * 65u,
					  "the last chunk is in a wrapped slot");
		} else {
			check_against_disk(x, 3, total, 0x40);
			zassert_equal(confirm_delete(x, 3, 10 + r, 0x60 + 2 * r), total);
		}
	}
	zassert_not_equal(wrapped, 0u, "a recording reached the wrap");
}

/* X20: no transfer state on the ring: a read can start at any chunk, in any order, and returns the same bytes */
ZTEST(xfer_store, test_resume_from_any_chunk)
{
	uint32_t a;
	uint8_t pl[12];
	static uint8_t full[5 * RREC_CHUNK_BYTES];

	record(5, 7, &a);
	xt_put(pl, a, 4);
	xt_put(pl + 4, 0, 4);
	xt_put(pl + 8, 5, 4);
	zassert_equal(xfer(RREC_OP_READ_RANGE, 0x40, pl, 12), 16u + 5u * 33280u);
	memcpy(full, big + 16, sizeof(full));
	static const uint32_t order[5] = { 3, 1, 4, 0, 2 };

	for (unsigned i = 0; i < 5; i++) {
		uint32_t k = order[i];

		xt_put(pl + 4, k, 4);
		xt_put(pl + 8, 5 - k, 4);
		zassert_equal(xfer(RREC_OP_READ_RANGE, 0x41 + i, pl, 12), 16u + (5u - k) * 33280u);
		zassert_equal(st(), RREC_ST_OK);
		zassert_mem_equal(big + 16, full + k * 33280, (5u - k) * 33280u, "resume from chunk %u", k);
	}
	/* one chunk alone, the last one */
	xt_put(pl + 4, 4, 4);
	xt_put(pl + 8, 1, 4);
	zassert_equal(xfer(RREC_OP_READ_RANGE, 0x50, pl, 12), 16u + 33280u);
	zassert_mem_equal(big + 16, full + 4 * 33280, 33280);
	/* the ring kept nothing: GET_INFO has no transfer field and the recording is still new */
	xt_put(pl, 0, 4);
	xt_put(pl + 4, 64, 2);
	zassert_equal(xfer(RREC_OP_LIST_RECORDINGS, 0x51, pl, 6), 16u + 2u + 64u);
	zassert_equal(big[18 + 6], 1u, "still state new: a read changes nothing");
}

/* X20: the digest the case computes from the payload CRCs it received equals the ring's; CONFIRM accepts it */
ZTEST(xfer_store, test_case_digest_matches_close)
{
	uint32_t a;
	uint8_t pl[12], words[5 * 4], cf[8];

	record(4, 9, &a);
	xt_put(pl, a, 4);
	xt_put(pl + 4, 0, 4);
	xt_put(pl + 8, 4, 4);
	zassert_equal(xfer(RREC_OP_READ_RANGE, 0x60, pl, 12), 16u + 4u * 33280u);
	for (uint32_t k = 0; k < 4; k++) {
		const uint8_t *c = big + 16 + k * 33280;
		uint32_t got = xt_le(c + RREC_CH_OFF_PAYLOAD_CRC, 4);

		/* the case's check (FW l.715): payload_crc32 of the header against the payload it received */
		zassert_equal(got, xt_crc(0, c + 512, 32768), "payload_crc32 of chunk %u", k);
		zassert_equal(xt_le(c + RREC_CH_OFF_RECORDING_ID, 4), a, "recording_id of chunk %u", k);
		zassert_equal(xt_le(c + RREC_CH_OFF_CHUNK_IN_REC, 4), k, "chunk_in_recording");
		xt_put(words + 4 * k, got, 4);
	}
	uint32_t digest = xt_crc(0, words, 16);

	zassert_equal(digest, ref_digest(a, 4, 9), "the case's digest from received CRCs");
	xt_put(cf, a, 4);
	xt_put(cf + 4, digest, 4);
	zassert_equal(xfer(RREC_OP_CONFIRM, 0x61, cf, 8), 16u);
	zassert_equal(st(), RREC_ST_OK, "the case's digest equals the ring's");
	xt_put(pl, 0, 4);
	xt_put(pl + 4, 64, 2);
	zassert_equal(xfer(RREC_OP_LIST_RECORDINGS, 0x62, pl, 6), 16u + 2u + 64u);
	zassert_equal(xt_le(big + 18 + 36, 4), digest, "the listed digest is the same");
	zassert_equal(big[18 + 6], 2u, "state 2: transferred after CONFIRM");
}

/* X11, S26, S27, S28: CONFIRM then DELETE; a wrong digest changes nothing; DELETE needs CONFIRM; the middle one stays
 * counted as used until the ones before it are gone */
ZTEST(xfer_store, test_confirm_then_delete)
{
	uint32_t a, b, c;
	uint8_t cf[8], pl[6];

	record(2, 1, &a);
	record(3, 2, &b);
	record(1, 3, &c);                          /* 6 of 24 slots used */
	/* S27: DELETE before CONFIRM */
	xt_put(cf, b, 4);
	zassert_equal(xfer(RREC_OP_DELETE, 0x70, cf, 4), 16u);
	zassert_equal(st(), RREC_ST_NOT_CONFIRMED, "6");
	/* S26: a wrong digest is DIGEST_MISMATCH and nothing changes: DELETE still refused */
	xt_put(cf + 4, ref_digest(b, 3, 2) ^ 1u, 4);
	zassert_equal(xfer(RREC_OP_CONFIRM, 0x71, cf, 8), 16u);
	zassert_equal(st(), RREC_ST_DIGEST_MISMATCH, "9");
	zassert_equal(xfer(RREC_OP_DELETE, 0x72, cf, 4), 16u);
	zassert_equal(st(), RREC_ST_NOT_CONFIRMED);
	xt_put(pl, 0, 4);
	xt_put(pl + 4, 64, 2);
	zassert_equal(xfer(RREC_OP_LIST_RECORDINGS, 0x73, pl, 6), 16u + 2u + 3u * 64u);
	zassert_equal(big[18 + 64 + 6], 1u, "b is still new");
	/* the right digest, then DELETE of the middle recording: free chunks unchanged (S28) */
	xt_put(cf + 4, ref_digest(b, 3, 2), 4);
	zassert_equal(xfer(RREC_OP_CONFIRM, 0x74, cf, 8), 16u);
	zassert_equal(st(), RREC_ST_OK);
	zassert_equal(xfer(RREC_OP_DELETE, 0x75, cf, 4), 16u + 4u);
	zassert_equal(st(), RREC_ST_OK);
	zassert_equal(xt_le(big + 16, 4), CARD_CHUNKS - 6u, "the middle one stays counted as used: 18 free");
	/* then the first: both are freed, only c's chunk is left (23 free) */
	xt_put(cf, a, 4);
	xt_put(cf + 4, ref_digest(a, 2, 1), 4);
	zassert_equal(xfer(RREC_OP_CONFIRM, 0x76, cf, 8), 16u);
	zassert_equal(st(), RREC_ST_OK);
	zassert_equal(xfer(RREC_OP_DELETE, 0x77, cf, 4), 16u + 4u);
	zassert_equal(xt_le(big + 16, 4), CARD_CHUNKS - 1u, "a and b freed: 23 free");
	/* GET_INFO agrees */
	zassert_equal(xfer(RREC_OP_GET_INFO, 0x78, NULL, 0), 16u + 35u);
	zassert_equal(xt_le(big + 16 + 22, 4), CARD_CHUNKS - 1u);
	zassert_equal(xt_le(big + 16 + 26, 4), 1u, "one recording left");
	/* an unknown recording */
	xt_put(cf, 999, 4);
	zassert_equal(xfer(RREC_OP_DELETE, 0x79, cf, 4), 16u);
	zassert_equal(st(), RREC_ST_NOT_FOUND, "5");
	zassert_equal(xfer(RREC_OP_CONFIRM, 0x7A, cf, 8), 16u);
	zassert_equal(st(), RREC_ST_NOT_FOUND);
	(void)c;
}

/* S29: a deleted recording cannot be read (NOT_FOUND, no data); its sectors are not erased; so are an unknown
 * recording and a range past the end */
ZTEST(xfer_store, test_read_range_deleted_not_found)
{
	uint32_t a, b;
	uint8_t pl[12], cf[8], sec[512];

	record(2, 1, &a);
	record(2, 2, &b);
	uint32_t a_first = first_seq(a);

	xt_put(pl, a, 4);
	xt_put(pl + 4, 0, 4);
	xt_put(pl + 8, 2, 4);
	zassert_equal(xfer(RREC_OP_READ_RANGE, 0x80, pl, 12), 16u + 2u * 33280u);
	zassert_equal(st(), RREC_ST_OK, "readable before the delete");
	xt_put(cf, a, 4);
	xt_put(cf + 4, ref_digest(a, 2, 1), 4);
	zassert_equal(xfer(RREC_OP_CONFIRM, 0x81, cf, 8), 16u);
	zassert_equal(xfer(RREC_OP_DELETE, 0x82, cf, 4), 16u + 4u);
	zassert_equal(st(), RREC_ST_OK);
	zassert_equal(xfer(RREC_OP_READ_RANGE, 0x83, pl, 12), 16u, "no data after a delete");
	zassert_equal(st(), RREC_ST_NOT_FOUND, "5");
	xt_put(pl + 8, 1, 4);
	zassert_equal(xfer(RREC_OP_READ_RANGE, 0x84, pl, 12), 16u);
	zassert_equal(st(), RREC_ST_NOT_FOUND);
	/* the audio sectors are still on the card (FW l.661: not erased) */
	rhw_sim_disk_peek(chunk_lba(CARD_CHUNKS, a_first) + 1, sec);
	bool any = false;

	for (unsigned i = 0; i < 512; i++) {
		any |= sec[i] != 0;
	}
	zassert_true(any, "the deleted chunk's payload sector was not erased");
	/* an unknown recording and a range past the end of a real one */
	xt_put(pl, 12345, 4);
	zassert_equal(xfer(RREC_OP_READ_RANGE, 0x85, pl, 12), 16u);
	zassert_equal(st(), RREC_ST_NOT_FOUND);
	xt_put(pl, b, 4);
	xt_put(pl + 4, 1, 4);
	xt_put(pl + 8, 2, 4);                       /* chunks 1 and 2 of a 2-chunk recording */
	zassert_equal(xfer(RREC_OP_READ_RANGE, 0x86, pl, 12), 16u);
	zassert_equal(st(), RREC_ST_NOT_FOUND, "no byte of a range that is only partly there");
	xt_put(pl + 4, 2, 4);
	xt_put(pl + 8, 1, 4);
	zassert_equal(xfer(RREC_OP_READ_RANGE, 0x87, pl, 12), 16u);
	zassert_equal(st(), RREC_ST_NOT_FOUND);
	xt_put(pl + 4, 1, 4);
	xt_put(pl + 8, 1, 4);
	zassert_equal(xfer(RREC_OP_READ_RANGE, 0x88, pl, 12), 16u + 33280u);
	zassert_equal(st(), RREC_ST_OK, "the last chunk of b");
}

static struct rrec_logrec mkrec(uint16_t code)
{
	struct rrec_logrec r = { 0 };

	r.uptime_ns = 1000000ll * code;
	r.utc_ms = 1700000000000ll + code;
	r.code = code;
	r.state = 3;
	r.args[0] = (uint8_t)code;
	return r;
}

/* X15: GET_LOG: count u16 then count x 512-byte records, from record number `first` */
ZTEST(xfer_store, test_get_log_records)
{
	uint8_t pl[6];

	for (uint16_t c = 1; c <= 5; c++) {
		struct rrec_logrec r = mkrec(c);

		rst_log_put(&r);
	}
	k_msleep(50);
	xt_put(pl, 3, 4);
	xt_put(pl + 4, 32, 2);
	zassert_equal(xfer(RREC_OP_GET_LOG, 0x90, pl, 6), 16u + 2u + 3u * 512u);
	zassert_equal(st(), RREC_ST_OK);
	zassert_equal(xt_le(big + 16, 2), 3u, "records 3, 4 and 5");
	for (uint32_t i = 0; i < 3; i++) {
		const uint8_t *r = big + 18 + 512 * i;

		zassert_equal(xt_le(r + RREC_LG_OFF_MAGIC, 4), 0x474C5252u, "RRLG");
		zassert_equal(xt_le(r + RREC_LG_OFF_SEQ, 4), 3u + i);
		zassert_equal(xt_le(r + RREC_LG_OFF_CODE, 2), 3u + i);
		zassert_equal(r[RREC_LG_OFF_STATE], 3u);
		zassert_equal(r[RREC_LG_OFF_ARGS], 3u + i);
		zassert_equal(xt_le(r + RREC_LG_OFF_CRC, 4), xt_crc(0, r, 508), "crc over bytes 0 to 507");
	}
	xt_put(pl, 0, 4);
	xt_put(pl + 4, 2, 2);
	zassert_equal(xfer(RREC_OP_GET_LOG, 0x91, pl, 6), 16u + 2u + 2u * 512u);
	zassert_equal(xt_le(big + 16, 2), 2u);
	xt_put(pl + 4, 33, 2);
	zassert_equal(xfer(RREC_OP_GET_LOG, 0x92, pl, 6), 16u);
	zassert_equal(st(), RREC_ST_BAD_ARG);
}

/* X12 over the transport: SET_TIME reaches the clock layer; X17: FACTORY is refused with the flag clear */
ZTEST(xfer_store, test_set_time_and_factory_over_usb)
{
	uint8_t pl[10], fac[2] = { 0x01, 0 };

	xt_put(pl, 1700000123456ull, 8);
	xt_put(pl + 8, (uint16_t)(int16_t)60, 2);
	zassert_equal(xfer(RREC_OP_SET_TIME, 0xA0, pl, 10), 16u);
	zassert_equal(st(), RREC_ST_OK);
	zassert_equal(gl.utc_ms, 1700000123456ll);
	zassert_equal(gl.tz, 60);
	zassert_equal(xfer(RREC_OP_FACTORY, 0xA1, fac, 2), 16u);
	zassert_equal(st(), RREC_ST_NOT_ALLOWED, "11");
	gl.factory_flag = true;
	zassert_equal(xfer(RREC_OP_FACTORY, 0xA2, fac, 2), 16u);
	zassert_equal(st(), RREC_ST_OK);
	zassert_equal(gl.after_calls, 3u);
}
