/*
 * test_proto.c: suite xfer_proto (unit U4): the pure protocol (rxf_proto.c) against a fake backend.
 * Rows X5 to X17, X19, X18, C24 of firmware/docs/step6-plan.md. "FW l.N" = line N of design/firmware.md.
 * Expected bytes are typed from FW 6.2 and 6.3, not produced by the code under test.
 */
#include "xt.h"

static void before(void *f)
{
	ARG_UNUSED(f);
	fake_reset();
	rxf_proto_init(&xctx, fake_be());
}

static uint8_t rq[RXF_REQ_BYTES];

/* one request through the handler; the response sits in `cap` */
static int go(uint8_t op, uint32_t tag, const void *pl, uint32_t plen, struct rxf_result *res)
{
	size_t n = xt_req(rq, op, tag, pl, plen);

	return xt_run(RREC_USB_MPS_FS, rq, n, res);
}

static void expect_error_only(enum rrec_status st, uint32_t tag)
{
	zassert_equal(cap.total, 16u, "an error response is the 16-byte header only, got %u", (unsigned)cap.total);
	zassert_equal(cap_status(), st);
	zassert_equal(cap_len(), 0u);
	zassert_equal(cap_crc(), 0u);
	zassert_equal(cap_tag(), tag);
}

ZTEST_SUITE(xfer_proto, NULL, NULL, before, NULL, NULL);

/* the reference CRC used by every case: "123456789" gives 0xCBF43926 (FW l.70, CRC-32/ISO-HDLC) */
ZTEST(xfer_proto, test_reference_crc_check_value)
{
	zassert_equal(xt_crc(0, (const uint8_t *)"123456789", 9), 0xCBF43926u);
	/* chaining over two parts equals one pass */
	zassert_equal(xt_crc(xt_crc(0, (const uint8_t *)"1234", 4), (const uint8_t *)"56789", 5), 0xCBF43926u);
	zassert_equal(rxf_proto_payload_crc((const uint8_t *)"123456789", 9), 0xCBF43926u, "the unit's CRC");
}

/* X5: the 16-byte header, every field at its offset (FW l.677 to l.686) */
ZTEST(xfer_proto, test_header_bytes)
{
	struct rxf_result res;
	/* CONFIRM OK: no payload. magic 5252, opcode 04, status 00, tag 0x12345678, length 0, crc 0 */
	const uint8_t want_confirm[16] = { 0x52, 0x52, 0x04, 0x00, 0x78, 0x56, 0x34, 0x12,
					   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
	uint8_t pl[8] = { 1, 0, 0, 0, 2, 0, 0, 0 };

	zassert_equal(go(RREC_OP_CONFIRM, 0x12345678u, pl, 8, &res), 0);
	zassert_equal(cap.total, 16u);
	zassert_mem_equal(cap.buf, want_confirm, 16);

	/* GET_BATTERY: payload of 9 bytes (0x50 .. 0x58 from the fake); length 9, crc of those bytes */
	const uint8_t batt[9] = { 0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58 };

	zassert_equal(go(RREC_OP_GET_BATTERY, 0xCAFEF00Du, NULL, 0, &res), 0);
	zassert_equal(cap.total, 25u);
	zassert_equal(cap.buf[0], 0x52);
	zassert_equal(cap.buf[1], 0x52);
	zassert_equal(cap.buf[2], 0x07, "opcode at offset 2");
	zassert_equal(cap.buf[3], 0x00, "status at offset 3");
	zassert_mem_equal(cap.buf + 4, ((const uint8_t[]){ 0x0D, 0xF0, 0xFE, 0xCA }), 4, "tag at offset 4");
	zassert_mem_equal(cap.buf + 8, ((const uint8_t[]){ 9, 0, 0, 0 }), 4, "length at offset 8");
	zassert_equal(cap_crc(), xt_crc(0, batt, 9), "crc of the payload at offset 12");
	zassert_mem_equal(cap.buf + 16, batt, 9);
}

/* X5: the tag of the request comes back in the response, for every opcode and for errors */
ZTEST(xfer_proto, test_tag_echoed)
{
	static const uint32_t tags[] = { 0x00000001u, 0xDEADBEEFu, 0xFFFFFFFFu, 0x80000000u };
	struct rxf_result res;
	uint8_t pl[16] = { 0 };

	xt_put(pl + 4, 1, 2);    /* LIST max 1; also valid for GET_LOG max 1; READ_RANGE needs 12 bytes: set below */
	for (unsigned t = 0; t < ARRAY_SIZE(tags); t++) {
		for (uint8_t op = RREC_OP_FIRST; op <= RREC_OP_LAST; op++) {
			uint32_t plen = 0;
			uint8_t body[4200] = { 0 };

			switch (op) {
			case RREC_OP_LIST_RECORDINGS:
			case RREC_OP_GET_LOG:
				plen = 6; memcpy(body, pl, 6); break;
			case RREC_OP_READ_RANGE:
				plen = 12; xt_put(body + 8, 1, 4); break;
			case RREC_OP_CONFIRM:
			case RREC_OP_FW_BEGIN:
				plen = 8; break;
			case RREC_OP_DELETE:
				plen = 4; break;
			case RREC_OP_SET_TIME:
				plen = 10; break;
			case RREC_OP_FW_DATA:
				plen = 5; break;
			case RREC_OP_FACTORY:
				plen = 1; body[0] = 0x01; break;
			default:
				break;
			}
			zassert_equal(go(op, tags[t], body, plen, &res), 0, "op %u", op);
			zassert_equal(cap_tag(), tags[t], "op %u tag %08x", op, tags[t]);
			zassert_equal(cap.buf[2], op);
			zassert_equal(cap_status(), RREC_ST_OK, "op %u", op);
		}
		/* errors echo it too */
		zassert_equal(go(0x55, tags[t], NULL, 0, &res), 0);
		zassert_equal(cap_tag(), tags[t]);
		zassert_equal(cap_status(), RREC_ST_UNKNOWN_OPCODE);
	}
}

/* X5: crc32 field is 0 when the length is 0, in a good response and in every error response */
ZTEST(xfer_proto, test_crc_zero_for_empty)
{
	struct rxf_result res;
	uint8_t pl[8] = { 1, 0, 0, 0, 2, 0, 0, 0 };

	zassert_equal(go(RREC_OP_CONFIRM, 7, pl, 8, &res), 0);
	zassert_equal(cap_status(), RREC_ST_OK);
	zassert_equal(cap_len(), 0u);
	zassert_equal(cap_crc(), 0u, "CONFIRM OK has no payload: crc 0");
	zassert_equal(go(RREC_OP_REBOOT, 8, NULL, 0, &res), 0);
	zassert_equal(cap_len(), 0u);
	zassert_equal(cap_crc(), 0u, "REBOOT OK has no payload: crc 0");
	zassert_equal(go(RREC_OP_FW_END, 9, NULL, 0, &res), 0);
	zassert_equal(cap_crc(), 0u);
	fk.st[RREC_OP_CONFIRM] = RREC_ST_DIGEST_MISMATCH;
	zassert_equal(go(RREC_OP_CONFIRM, 10, pl, 8, &res), 0);
	zassert_equal(cap_status(), RREC_ST_DIGEST_MISMATCH);
	zassert_equal(cap_crc(), 0u, "an error response has crc 0");
	/* and a response with a payload has a nonzero CRC of it */
	zassert_equal(go(RREC_OP_GET_INFO, 11, NULL, 0, &res), 0);
	zassert_not_equal(cap_crc(), 0u);
}

/* X6: the response is exactly 16 + length bytes, for each command, at both packet sizes; the pieces are whole
 * packets except the last one */
ZTEST(xfer_proto, test_response_length_exact)
{
	struct rxf_result res;
	uint8_t pl[16] = { 0 };

	/* typed sizes: GET_INFO 35, GET_BATTERY 9, DELETE 4, LIST 2 + 3 x 64, GET_LOG 2 + 2 x 512, FACTORY 3 */
	zassert_equal(go(RREC_OP_GET_INFO, 1, NULL, 0, &res), 0);
	zassert_equal(cap.total, 16u + 35u);
	zassert_equal(cap_len(), 35u);
	zassert_equal(go(RREC_OP_GET_BATTERY, 1, NULL, 0, &res), 0);
	zassert_equal(cap.total, 16u + 9u);
	xt_put(pl, 5, 4);
	zassert_equal(go(RREC_OP_DELETE, 1, pl, 4, &res), 0);
	zassert_equal(cap.total, 16u + 4u);
	zassert_equal(xt_le(cap.buf + 16, 4), 777u, "free chunks after, u32");
	xt_put(pl, 0, 4);
	xt_put(pl + 4, 3, 2);
	zassert_equal(go(RREC_OP_LIST_RECORDINGS, 1, pl, 6, &res), 0);
	zassert_equal(cap.total, 16u + 2u + 3u * 64u);
	zassert_equal(cap_len(), 2u + 3u * 64u);
	xt_put(pl + 4, 2, 2);
	zassert_equal(go(RREC_OP_GET_LOG, 1, pl, 6, &res), 0);
	zassert_equal(cap.total, 16u + 2u + 2u * 512u);
	/* a payload that makes the whole response exactly one packet or two: 16 + 48 = 64 and 16 + 112 = 128 at full
	 * speed; 16 + 496 = 512 at high speed: handed over in one piece each, no zero-length piece */
	uint8_t fac = 0x01;
	size_t want_pay[] = { 48, 112 };

	for (unsigned i = 0; i < 2; i++) {
		fk.factory_out_len = want_pay[i];
		zassert_equal(go(RREC_OP_FACTORY, 2, &fac, 1, &res), 0);
		zassert_equal(cap.total, 16u + want_pay[i]);
		zassert_equal(cap.pieces, 1u);
		zassert_equal(cap.last_flags, 1u);
	}
	fk.factory_out_len = 240;     /* under the 256-byte limit (rxf.h) */
	zassert_equal(go(RREC_OP_FACTORY, 2, &fac, 1, &res), 0);
	zassert_equal(cap.total, 16u + 240u);
	/* high speed */
	fk.factory_out_len = 200;
	size_t n = xt_req(rq, RREC_OP_FACTORY, 3, &fac, 1);

	zassert_equal(xt_run(RREC_USB_MPS_HS, rq, n, &res), 0);
	zassert_equal(cap.total, 16u + 200u);
	zassert_equal(cap.bad_pieces, 0u);
	/* more than 256 result bytes is refused by the unit (STORAGE_ERROR), not sent */
	fk.factory_out_len = 257;
	zassert_equal(go(RREC_OP_FACTORY, 2, &fac, 1, &res), 0);
	zassert_equal(cap_status(), RREC_ST_STORAGE_ERROR);
	zassert_equal(cap.total, 16u);
}

/* X7: a wrong magic gets BAD_MAGIC and no payload, and the backend is not called */
ZTEST(xfer_proto, test_bad_magic)
{
	struct rxf_result res;
	uint8_t pl[8] = { 1, 0, 0, 0, 2, 0, 0, 0 };
	static const uint16_t bad[] = { 0x5253, 0x0000, 0x2525, 0xFFFF, 0x5152 };

	for (unsigned i = 0; i < ARRAY_SIZE(bad); i++) {
		size_t n = xt_req(rq, RREC_OP_CONFIRM, 0xAB000000u + i, pl, 8);

		xt_put(rq, bad[i], 2);
		zassert_equal(xt_run(RREC_USB_MPS_FS, rq, n, &res), 0);
		expect_error_only(RREC_ST_BAD_MAGIC, 0xAB000000u + i);
		zassert_equal(res.status, RREC_ST_BAD_MAGIC);
	}
	zassert_equal(fk.calls[RREC_OP_CONFIRM], 0u, "the command did not run");
	zassert_equal(fk.after_calls, 0u, "no after_response for a request that was not a command");
	/* a header alone, then 15 bytes: not a header at all */
	zassert_equal(xt_run(RREC_USB_MPS_FS, rq, 15, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_MAGIC);
}

/* X7: a wrong CRC gets BAD_CRC and no payload (FW l.690) */
ZTEST(xfer_proto, test_bad_crc)
{
	struct rxf_result res;
	uint8_t pl[8] = { 1, 0, 0, 0, 2, 0, 0, 0 };
	size_t n = xt_req(rq, RREC_OP_CONFIRM, 0x01020304u, pl, 8);

	rq[12] ^= 0x01;                     /* the header's crc */
	zassert_equal(xt_run(RREC_USB_MPS_FS, rq, n, &res), 0);
	expect_error_only(RREC_ST_BAD_CRC, 0x01020304u);

	n = xt_req(rq, RREC_OP_CONFIRM, 0x01020305u, pl, 8);
	rq[20] ^= 0x80;                     /* a payload byte */
	zassert_equal(xt_run(RREC_USB_MPS_FS, rq, n, &res), 0);
	expect_error_only(RREC_ST_BAD_CRC, 0x01020305u);

	n = xt_req(rq, RREC_OP_GET_INFO, 0x01020306u, NULL, 0);
	rq[12] = 0x01;                      /* length 0 with a crc other than 0 */
	zassert_equal(xt_run(RREC_USB_MPS_FS, rq, n, &res), 0);
	expect_error_only(RREC_ST_BAD_CRC, 0x01020306u);
	zassert_equal(fk.calls[RREC_OP_CONFIRM] + fk.calls[RREC_OP_GET_INFO], 0u, "no command ran");
}

/* X7: every opcode outside 0x01 to 0x0D gives UNKNOWN_OPCODE: 243 values */
ZTEST(xfer_proto, test_unknown_opcodes)
{
	struct rxf_result res;
	unsigned unknown = 0;

	for (unsigned op = 0; op < 256; op++) {
		if (op >= 0x01 && op <= 0x0D) {
			continue;
		}
		size_t n = xt_req(rq, (uint8_t)op, 0x77000000u + op, NULL, 0);

		zassert_equal(xt_run(RREC_USB_MPS_FS, rq, n, &res), 0);
		zassert_equal(cap_status(), RREC_ST_UNKNOWN_OPCODE, "opcode %02x", op);
		zassert_equal(cap.total, 16u);
		zassert_equal(cap_tag(), 0x77000000u + op);
		unknown++;
	}
	zassert_equal(unknown, 243u);
	for (unsigned op = 1; op <= 13; op++) {
		zassert_true(rxf_proto_opcode_known((uint8_t)op));
	}
}

/* X8: GET_INFO passes the backend's 35 bytes; a request payload is refused */
ZTEST(xfer_proto, test_get_info_layout)
{
	struct rxf_result res;
	uint8_t one = 1;

	zassert_equal(go(RREC_OP_GET_INFO, 1, NULL, 0, &res), 0);
	zassert_equal(cap_len(), 35u);
	for (unsigned i = 0; i < 35; i++) {
		zassert_equal(cap.buf[16 + i], 0xA0 + i, "byte %u in the backend's order", i);
	}
	zassert_equal(go(RREC_OP_GET_INFO, 1, &one, 1, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
	fk.st[RREC_OP_GET_INFO] = RREC_ST_STORAGE_ERROR;
	zassert_equal(go(RREC_OP_GET_INFO, 1, NULL, 0, &res), 0);
	expect_error_only(RREC_ST_STORAGE_ERROR, 1);
}

/* X9: LIST_RECORDINGS: max 1 to 64, else BAD_ARG before the backend is called */
ZTEST(xfer_proto, test_list_args)
{
	struct rxf_result res;
	uint8_t pl[6];
	static const uint16_t bad[] = { 0, 65, 66, 255, 0xFFFF };
	static const uint16_t good[] = { 1, 2, 63, 64 };

	for (unsigned i = 0; i < ARRAY_SIZE(bad); i++) {
		xt_put(pl, 5, 4);
		xt_put(pl + 4, bad[i], 2);
		zassert_equal(go(RREC_OP_LIST_RECORDINGS, 9, pl, 6, &res), 0);
		expect_error_only(RREC_ST_BAD_ARG, 9);
	}
	zassert_equal(fk.calls[RREC_OP_LIST_RECORDINGS], 0u, "the backend saw no invalid range");
	for (unsigned i = 0; i < ARRAY_SIZE(good); i++) {
		xt_put(pl, 0x01020304u, 4);
		xt_put(pl + 4, good[i], 2);
		zassert_equal(go(RREC_OP_LIST_RECORDINGS, 9, pl, 6, &res), 0);
		zassert_equal(cap_status(), RREC_ST_OK, "max %u", good[i]);
		zassert_equal(fk.last_max, good[i]);
		zassert_equal(fk.last_first, 0x01020304u, "first passes through as a u32");
	}
	/* the request payload must be 6 bytes */
	zassert_equal(go(RREC_OP_LIST_RECORDINGS, 9, pl, 5, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
	zassert_equal(go(RREC_OP_LIST_RECORDINGS, 9, pl, 7, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
	/* a list answer larger than 2 + 64 x 64 is refused */
	fk.list_len = RXF_LIST_PAYLOAD_MAX + 1;
	xt_put(pl + 4, 64, 2);
	zassert_equal(go(RREC_OP_LIST_RECORDINGS, 9, pl, 6, &res), 0);
	zassert_equal(cap_status(), RREC_ST_STORAGE_ERROR);
	fk.list_len = RXF_LIST_PAYLOAD_MAX;   /* the full list: 2 + 4,096 bytes */
	zassert_equal(go(RREC_OP_LIST_RECORDINGS, 9, pl, 6, &res), 0);
	zassert_equal(cap_status(), RREC_ST_OK);
	zassert_equal(cap_len(), 4098u);
}

/* X10: READ_RANGE: chunk_count 1 to 256, else BAD_ARG; a missing chunk answers NOT_FOUND before any data */
ZTEST(xfer_proto, test_read_range_args)
{
	struct rxf_result res;
	uint8_t pl[12];
	static const uint32_t bad[] = { 0, 257, 258, 1000, 0xFFFFFFFFu };

	fk.st[RREC_OP_READ_RANGE] = RREC_ST_NOT_FOUND;   /* a backend that refuses whatever reaches it */
	for (unsigned i = 0; i < ARRAY_SIZE(bad); i++) {
		xt_put(pl, 3, 4);
		xt_put(pl + 4, 0, 4);
		xt_put(pl + 8, bad[i], 4);
		zassert_equal(go(RREC_OP_READ_RANGE, 5, pl, 12, &res), 0);
		expect_error_only(RREC_ST_BAD_ARG, 5);
	}
	zassert_equal(fk.calls[RREC_OP_READ_RANGE], 0u, "the backend saw no invalid count");
	/* a valid count reaches the backend, which says NOT_FOUND: no data was read, no byte beyond the header */
	xt_put(pl + 8, 256, 4);
	zassert_equal(go(RREC_OP_READ_RANGE, 5, pl, 12, &res), 0);
	expect_error_only(RREC_ST_NOT_FOUND, 5);
	zassert_equal(fk.calls[RREC_OP_READ_RANGE], 1u);
	zassert_equal(fk.read_calls, 0u, "no chunk was read after a refused range check");
	xt_put(pl + 8, 1, 4);
	zassert_equal(go(RREC_OP_READ_RANGE, 5, pl, 12, &res), 0);
	expect_error_only(RREC_ST_NOT_FOUND, 5);
	/* the length of the request payload must be 12 */
	zassert_equal(go(RREC_OP_READ_RANGE, 5, pl, 8, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
	/* first + count beyond u32: no such chunk */
	fk.st[RREC_OP_READ_RANGE] = RREC_ST_OK;
	xt_put(pl + 4, 0xFFFFFFFFu, 4);
	xt_put(pl + 8, 2, 4);
	zassert_equal(go(RREC_OP_READ_RANGE, 5, pl, 12, &res), 0);
	expect_error_only(RREC_ST_NOT_FOUND, 5);
	/* the smallest range */
	xt_put(pl, 9, 4);
	xt_put(pl + 4, 4, 4);
	xt_put(pl + 8, 1, 4);
	zassert_equal(go(RREC_OP_READ_RANGE, 5, pl, 12, &res), 0);
	zassert_equal(cap_status(), RREC_ST_OK);
	zassert_equal(cap_len(), 33280u);
	zassert_equal(fk.last_rec, 9u);
	zassert_equal(fk.last_first, 4u);
	zassert_equal(fk.last_count, 1u);
}

/* X10, FACT of rxf.h: every chunk exactly as the backend serves it, in order, with the header's CRC over all of
 * them, from a second read of each chunk; the pieces are whole packets except the last (no short packet inside) */
ZTEST(xfer_proto, test_read_range_stream)
{
	struct rxf_result res;
	uint8_t pl[12];
	static const uint32_t mps_list[] = { 64, 512 };

	for (unsigned m = 0; m < 2; m++) {
		fake_reset();
		xt_put(pl, 12, 4);
		xt_put(pl + 4, 5, 4);
		xt_put(pl + 8, 3, 4);
		size_t n = xt_req(rq, RREC_OP_READ_RANGE, 0x0BADF00Du, pl, 12);

		zassert_equal(xt_run(mps_list[m], rq, n, &res), 0);
		zassert_equal(res.outcome, RXF_SENT);
		zassert_equal(cap.total, 16u + 3u * 33280u);
		zassert_equal(cap_len(), 3u * 33280u);
		zassert_equal(cap_status(), RREC_ST_OK);
		zassert_equal(cap_tag(), 0x0BADF00Du);
		for (uint32_t c = 0; c < 3; c++) {
			for (uint32_t i = 0; i < 33280; i += 97) {
				zassert_equal(cap.buf[16 + c * 33280 + i], fake_chunk_byte(12, 5 + c, i),
					      "chunk %u byte %u at mps %u", c, i, mps_list[m]);
			}
			zassert_equal(cap.buf[16 + c * 33280 + 33279], fake_chunk_byte(12, 5 + c, 33279));
		}
		zassert_equal(cap_crc(), cap.pcrc, "the header's crc covers the whole payload (reference CRC)");
		zassert_equal(fk.read_calls, 6u, "each chunk is read twice: once for the CRC, once to send");
		zassert_equal(cap.bad_pieces, 0u, "every piece but the last is whole packets at mps %u", mps_list[m]);
		zassert_equal(cap.last_flags, 1u);
		zassert_false(cap.last_seen_then_more);
		zassert_equal(cap.pieces, 3u, "header carried in front of the chunks: one piece per chunk");
	}
}

/* X10: the largest range, 256 chunks = 8,519,680 payload bytes, checked as it streams (no copy kept) */
ZTEST(xfer_proto, test_read_range_256)
{
	struct rxf_result res;
	uint8_t pl[12];

	xt_put(pl, 2, 4);
	xt_put(pl + 4, 0, 4);
	xt_put(pl + 8, 256, 4);
	size_t n = xt_req(rq, RREC_OP_READ_RANGE, 1, pl, 12);

	cap_reset(RREC_USB_MPS_FS);
	zassert_equal(rxf_proto_handle(&xctx, RREC_USB_MPS_FS, rq, n, cap_emit, NULL, &res), 0);
	zassert_equal(cap.total, 16u + 256u * 33280u);
	zassert_equal(res.length, 8519680u);
	zassert_equal(fk.read_calls, 512u);
	zassert_equal(cap.bad_pieces, 0u);
	zassert_equal(cap.pieces, 256u);
	zassert_equal(cap_crc(), cap.pcrc, "the header's crc covers all 8,519,680 bytes (reference CRC)");
	zassert_equal(cap_len(), 8519680u);
}

/* X10: a read that fails before the header went out gives that status with no data; one that changes between the two
 * reads cannot be repaired after the header: the stream stops, nothing is claimed as sent */
ZTEST(xfer_proto, test_read_range_failures)
{
	struct rxf_result res;
	uint8_t pl[12];

	xt_put(pl, 1, 4);
	xt_put(pl + 4, 0, 4);
	xt_put(pl + 8, 4, 4);
	fk.fail_read_at = 3;               /* the 3rd read, in the first pass */
	zassert_equal(go(RREC_OP_READ_RANGE, 1, pl, 12, &res), 0);
	expect_error_only(RREC_ST_STORAGE_ERROR, 1);
	zassert_equal(fk.after_calls, 1u, "a dispatched command, answered with its error");
	fake_reset();
	fk.change_read_at = 6;             /* the 2nd read of the 2nd chunk, in the second pass (4 + 2) */
	size_t n = xt_req(rq, RREC_OP_READ_RANGE, 1, pl, 12);

	zassert_equal(xt_run(RREC_USB_MPS_FS, rq, n, &res), RXF_SEND_FAILED);
	zassert_equal(res.outcome, RXF_SEND_FAILED);
	zassert_equal(res.status, RREC_ST_STORAGE_ERROR);
	zassert_true(cap.total < 16u + 4u * 33280u, "the stream stopped");
	zassert_equal(fk.after_calls, 0u, "the response was not completely handed over");
}

/* X11: CONFIRM and DELETE carry their arguments; DELETE returns the free chunks after */
ZTEST(xfer_proto, test_confirm_delete_args)
{
	struct rxf_result res;
	/* recording 0x00000102, digest 0xA1B2C3D4 in little-endian order */
	const uint8_t conf[8] = { 0x02, 0x01, 0x00, 0x00, 0xD4, 0xC3, 0xB2, 0xA1 };

	zassert_equal(go(RREC_OP_CONFIRM, 1, conf, 8, &res), 0);
	zassert_equal(fk.last_rec, 0x102u);
	zassert_equal(fk.last_digest, 0xA1B2C3D4u);
	zassert_equal(go(RREC_OP_CONFIRM, 1, conf, 7, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
	fk.st[RREC_OP_CONFIRM] = RREC_ST_DIGEST_MISMATCH;
	zassert_equal(go(RREC_OP_CONFIRM, 1, conf, 8, &res), 0);
	expect_error_only(RREC_ST_DIGEST_MISMATCH, 1);
	fk.st[RREC_OP_CONFIRM] = RREC_ST_NOT_FOUND;
	zassert_equal(go(RREC_OP_CONFIRM, 1, conf, 8, &res), 0);
	expect_error_only(RREC_ST_NOT_FOUND, 1);

	fk.free_after = 0x00112233u;
	zassert_equal(go(RREC_OP_DELETE, 2, conf, 4, &res), 0);
	zassert_equal(fk.last_rec, 0x102u);
	zassert_equal(cap_status(), RREC_ST_OK);
	zassert_mem_equal(cap.buf + 16, ((const uint8_t[]){ 0x33, 0x22, 0x11, 0x00 }), 4);
	zassert_equal(go(RREC_OP_DELETE, 2, conf, 8, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
	fk.st[RREC_OP_DELETE] = RREC_ST_NOT_CONFIRMED;
	zassert_equal(go(RREC_OP_DELETE, 2, conf, 4, &res), 0);
	expect_error_only(RREC_ST_NOT_CONFIRMED, 2);
}

/* X12: SET_TIME hands the clock layer utc_ms (i64) and tz_offset_min (i16) */
ZTEST(xfer_proto, test_set_time_calls_clock)
{
	struct rxf_result res;
	/* utc_ms 1,700,000,123,456 and tz -90 minutes */
	const int64_t utc = 1700000123456ll;
	uint8_t pl[10];

	xt_put(pl, (uint64_t)utc, 8);
	xt_put(pl + 8, (uint16_t)(int16_t)-90, 2);       /* UTC-1:30 */
	zassert_mem_equal(pl + 8, ((const uint8_t[]){ 0xA6, 0xFF }), 2, "typed: -90 = 0xFFA6");
	zassert_equal(go(RREC_OP_SET_TIME, 3, pl, 10, &res), 0);
	zassert_equal(cap_status(), RREC_ST_OK);
	zassert_equal(fk.calls[RREC_OP_SET_TIME], 1u);
	zassert_equal(fk.last_utc_ms, utc);
	zassert_equal(fk.last_tz, -90);
	/* a negative time and a positive zone */
	xt_put(pl, (uint64_t)(int64_t)-1, 8);
	xt_put(pl + 8, 330, 2);
	zassert_equal(go(RREC_OP_SET_TIME, 3, pl, 10, &res), 0);
	zassert_equal(fk.last_utc_ms, -1);
	zassert_equal(fk.last_tz, 330);
	zassert_equal(go(RREC_OP_SET_TIME, 3, pl, 9, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
	zassert_equal(fk.calls[RREC_OP_SET_TIME], 2u);
}

/* X13: GET_BATTERY passes 9 bytes */
ZTEST(xfer_proto, test_get_battery_layout)
{
	struct rxf_result res;

	zassert_equal(go(RREC_OP_GET_BATTERY, 4, NULL, 0, &res), 0);
	zassert_equal(cap_len(), 9u);
	for (unsigned i = 0; i < 9; i++) {
		zassert_equal(cap.buf[16 + i], 0x50 + i);
	}
	zassert_equal(go(RREC_OP_GET_BATTERY, 4, rq, 1, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
}

/* X14: FW_BEGIN 8 bytes, FW_DATA offset + 1 to 4,096 bytes, FW_END none */
ZTEST(xfer_proto, test_fw_args)
{
	struct rxf_result res;
	static uint8_t body[4400];

	/* FW_BEGIN: image_size 0x000F0000, crc 0x11223344 */
	const uint8_t beg[8] = { 0x00, 0x00, 0x0F, 0x00, 0x44, 0x33, 0x22, 0x11 };

	zassert_equal(go(RREC_OP_FW_BEGIN, 1, beg, 8, &res), 0);
	zassert_equal(fk.last_image_size, 0x000F0000u);
	zassert_equal(fk.last_image_crc, 0x11223344u);
	zassert_equal(go(RREC_OP_FW_BEGIN, 1, beg, 7, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
	/* FW_DATA: sizes 1 and 4,096 are accepted, 0 and 4,097 are not */
	static const uint32_t good[] = { 1, 2, 4095, 4096 };

	for (unsigned i = 0; i < ARRAY_SIZE(good); i++) {
		memset(body, 0xEE, sizeof(body));
		xt_put(body, 0x00001000u + i, 4);
		body[4 + good[i] - 1] = 0xA5;
		body[4] = 0x5A;
		zassert_equal(go(RREC_OP_FW_DATA, 1, body, 4 + good[i], &res), 0);
		zassert_equal(cap_status(), RREC_ST_OK, "len %u", good[i]);
		zassert_equal(fk.last_fw_len, good[i]);
		zassert_equal(fk.last_fw_offset, 0x1000u + i);
		zassert_equal(fk.last_fw_first, 0x5A);
		zassert_equal(fk.last_fw_lastbyte, good[i] == 1 ? 0x5A : 0xA5, "the last data byte");
	}
	uint32_t calls = fk.calls[RREC_OP_FW_DATA];

	zassert_equal(go(RREC_OP_FW_DATA, 1, body, 4, &res), 0);       /* no data bytes */
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
	zassert_equal(go(RREC_OP_FW_DATA, 1, body, 3, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
	zassert_equal(go(RREC_OP_FW_DATA, 1, body, 4 + 4097, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
	zassert_equal(fk.calls[RREC_OP_FW_DATA], calls, "no invalid length reached the backend");
	zassert_equal(go(RREC_OP_FW_END, 1, NULL, 0, &res), 0);
	zassert_equal(fk.calls[RREC_OP_FW_END], 1u);
	zassert_equal(go(RREC_OP_FW_END, 1, body, 1, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
	/* the update refused (D12) and an image fault come back as the backend's status */
	fk.st[RREC_OP_FW_BEGIN] = RREC_ST_NOT_ALLOWED;
	zassert_equal(go(RREC_OP_FW_BEGIN, 1, beg, 8, &res), 0);
	expect_error_only(RREC_ST_NOT_ALLOWED, 1);
	fk.st[RREC_OP_FW_END] = RREC_ST_FW_ERROR;
	zassert_equal(go(RREC_OP_FW_END, 1, NULL, 0, &res), 0);
	expect_error_only(RREC_ST_FW_ERROR, 1);
}

/* X15: GET_LOG: max 1 to 32, else BAD_ARG */
ZTEST(xfer_proto, test_get_log_args)
{
	struct rxf_result res;
	uint8_t pl[6];
	static const uint16_t bad[] = { 0, 33, 34, 0xFFFF };
	static const uint16_t good[] = { 1, 31, 32 };

	for (unsigned i = 0; i < ARRAY_SIZE(bad); i++) {
		xt_put(pl, 0, 4);
		xt_put(pl + 4, bad[i], 2);
		zassert_equal(go(RREC_OP_GET_LOG, 6, pl, 6, &res), 0);
		expect_error_only(RREC_ST_BAD_ARG, 6);
	}
	zassert_equal(fk.calls[RREC_OP_GET_LOG], 0u);
	for (unsigned i = 0; i < ARRAY_SIZE(good); i++) {
		xt_put(pl, 0x0A0B0C0Du, 4);
		xt_put(pl + 4, good[i], 2);
		zassert_equal(go(RREC_OP_GET_LOG, 6, pl, 6, &res), 0);
		zassert_equal(cap_status(), RREC_ST_OK);
		zassert_equal(fk.last_max, good[i]);
		zassert_equal(fk.last_first, 0x0A0B0C0Du);
	}
	fk.log_len = RXF_LOG_PAYLOAD_MAX;            /* 2 + 32 x 512 = 16,386 bytes */
	xt_put(pl + 4, 32, 2);
	zassert_equal(go(RREC_OP_GET_LOG, 6, pl, 6, &res), 0);
	zassert_equal(cap_len(), 16386u);
	zassert_equal(cap.total, 16u + 16386u);
	fk.log_len = RXF_LOG_PAYLOAD_MAX + 1;
	zassert_equal(go(RREC_OP_GET_LOG, 6, pl, 6, &res), 0);
	zassert_equal(cap_status(), RREC_ST_STORAGE_ERROR);
}

/* X16: the reboot request comes after the OK response was handed to the transport; also FW_END; never for a
 * response that was not handed over, and never for BUSY or a bad request */
ZTEST(xfer_proto, test_reboot_after_ok)
{
	struct rxf_result res;

	zassert_equal(go(RREC_OP_REBOOT, 0x4242u, NULL, 0, &res), 0);
	zassert_equal(cap_status(), RREC_ST_OK);
	zassert_equal(fk.after_calls, 1u);
	zassert_equal(fk.after_op, RREC_OP_REBOOT);
	zassert_equal(fk.after_st, RREC_ST_OK);
	zassert_equal(fk.after_tag, 0x4242u);
	zassert_equal(fk.after_len, 0u);
	zassert_true(fk.after_seq > cap.pieces, "after_response ran after the last piece was handed over");
	zassert_equal(cap.pieces, 1u);

	/* FW_END */
	fake_reset();
	zassert_equal(go(RREC_OP_FW_END, 5, NULL, 0, &res), 0);
	zassert_equal(fk.after_op, RREC_OP_FW_END);
	zassert_equal(fk.after_st, RREC_ST_OK);
	zassert_equal(fk.after_seq, 2u, "response piece, then after_response");

	/* the transport takes nothing: no reboot request */
	fake_reset();
	size_t n = xt_req(rq, RREC_OP_REBOOT, 1, NULL, 0);

	cap_reset(RREC_USB_MPS_FS);
	cap.fail_after = 1;
	zassert_equal(rxf_proto_handle(&xctx, RREC_USB_MPS_FS, rq, n, cap_emit, NULL, &res), RXF_SEND_FAILED);
	zassert_equal(fk.after_calls, 0u, "the OK response never left: no reboot request");

	/* a bad request is not a command */
	fake_reset();
	n = xt_req(rq, RREC_OP_REBOOT, 1, NULL, 0);
	rq[12] = 1;
	zassert_equal(xt_run(RREC_USB_MPS_FS, rq, n, &res), 0);
	zassert_equal(fk.after_calls, 0u);
	/* REBOOT with a payload: a dispatched command answered BAD_ARG, no reboot (status is not OK) */
	zassert_equal(go(RREC_OP_REBOOT, 1, rq, 1, &res), 0);
	zassert_equal(cap_status(), RREC_ST_BAD_ARG);
	zassert_equal(fk.after_calls, 1u);
	zassert_equal(fk.after_st, RREC_ST_BAD_ARG);
}

/* X17: FACTORY answers NOT_ALLOWED, with no payload, when the backend says the factory flag is clear */
ZTEST(xfer_proto, test_factory_not_allowed)
{
	struct rxf_result res;
	/* FACTORY_ENTER is 0x01, FACTORY_EXIT 0x02 (ruling), a test 0x10 with an argument */
	static const uint8_t subs[][2] = { { 0x01, 0 }, { 0x02, 0 }, { 0x10, 2 }, { 0x7F, 0 } };

	fk.st[RREC_OP_FACTORY] = RREC_ST_NOT_ALLOWED;       /* flag clear */
	fk.factory_out_len = 3;                              /* the backend even filled a result */
	for (unsigned i = 0; i < ARRAY_SIZE(subs); i++) {
		zassert_equal(go(RREC_OP_FACTORY, 0x31, subs[i], 2, &res), 0);
		expect_error_only(RREC_ST_NOT_ALLOWED, 0x31);
		zassert_equal(res.status, RREC_ST_NOT_ALLOWED);
		zassert_equal(fk.last_factory[0], subs[i][0], "the backend got the sub-command byte");
	}
	fk.st[RREC_OP_FACTORY] = RREC_ST_OK;                 /* flag set */
	zassert_equal(go(RREC_OP_FACTORY, 0x32, subs[1], 2, &res), 0);
	zassert_equal(cap_status(), RREC_ST_OK);
	zassert_equal(cap_len(), 3u);
	zassert_equal(cap.buf[16], 0xC0);
	zassert_equal(fk.last_factory[0], 0x02, "FACTORY_EXIT is sub-command 0x02");
	zassert_equal(fk.last_factory_len, 2u);
	/* no sub-command at all */
	zassert_equal(go(RREC_OP_FACTORY, 0x33, NULL, 0, &res), 0);
	expect_error_only(RREC_ST_BAD_ARG, 0x33);
}

/* X18: the case's order is the case's own; the ring takes any order */
ZTEST(xfer_proto, test_any_order)
{
	struct rxf_result res;
	uint8_t pl[16] = { 0 };

	xt_put(pl + 4, 1, 2);
	static const uint8_t orders[2][3] = {
		{ RREC_OP_SET_TIME, RREC_OP_GET_BATTERY, RREC_OP_LIST_RECORDINGS },
		{ RREC_OP_LIST_RECORDINGS, RREC_OP_GET_BATTERY, RREC_OP_SET_TIME },
	};

	for (unsigned o = 0; o < 2; o++) {
		for (unsigned i = 0; i < 3; i++) {
			uint8_t op = orders[o][i];
			uint32_t plen = op == RREC_OP_SET_TIME ? 10 : op == RREC_OP_LIST_RECORDINGS ? 6 : 0;

			zassert_equal(go(op, 100 + i, pl, plen, &res), 0);
			zassert_equal(cap_status(), RREC_ST_OK, "order %u step %u", o, i);
		}
	}
	/* a DELETE straight away is not a protocol error either: the backend decides (NOT_CONFIRMED) */
	fk.st[RREC_OP_DELETE] = RREC_ST_NOT_CONFIRMED;
	zassert_equal(go(RREC_OP_DELETE, 1, pl, 4, &res), 0);
	zassert_equal(cap_status(), RREC_ST_NOT_CONFIRMED);
}

/* the second request that arrives while a command runs (in the backend's own call here) */
static uint8_t nested_resp[64];
static size_t nested_n;
static int nested_outcome;
static struct rxf_result nested_res;

static int nested_emit(void *u, const uint8_t *d, size_t n, bool last)
{
	ARG_UNUSED(u);
	ARG_UNUSED(last);
	memcpy(nested_resp, d, MIN(n, sizeof(nested_resp)));
	nested_n = n;
	return 0;
}

static void nested_hook(void)
{
	static uint8_t r2[16];
	size_t n = xt_req(r2, RREC_OP_GET_INFO, 0x5151u, NULL, 0);

	nested_outcome = rxf_proto_handle(&xctx, RREC_USB_MPS_FS, r2, n, nested_emit, NULL, &nested_res);
}

/* X19, C24: a command that arrives while the previous one still runs gets BUSY; after it ended the next one runs */
ZTEST(xfer_proto, test_busy_while_running)
{
	struct rxf_result res;

	fk.hook = nested_hook;
	nested_n = 0;
	zassert_equal(go(RREC_OP_GET_BATTERY, 0x10, NULL, 0, &res), 0);
	zassert_equal(cap_status(), RREC_ST_OK, "the first command finishes normally");
	zassert_equal(nested_outcome, 0);
	zassert_equal(nested_n, 16u, "BUSY is the 16-byte header");
	zassert_equal(nested_resp[3], RREC_ST_BUSY, "status 7");
	zassert_equal(nested_resp[2], RREC_OP_GET_INFO, "the opcode is echoed");
	zassert_equal(xt_le(nested_resp + 4, 4), 0x5151u, "the tag is echoed");
	zassert_equal(xt_le(nested_resp + 8, 4), 0u);
	zassert_equal(fk.calls[RREC_OP_GET_INFO], 0u, "the second command did not run");
	zassert_equal(fk.after_calls, 1u, "only the command that ran is reported");
	zassert_equal(nested_res.status, RREC_ST_BUSY);
	zassert_false(nested_res.dispatched);
	/* afterwards the unit is free again */
	fk.hook = NULL;
	zassert_equal(go(RREC_OP_GET_INFO, 0x11, NULL, 0, &res), 0);
	zassert_equal(cap_status(), RREC_ST_OK);
	zassert_equal(fk.calls[RREC_OP_GET_INFO], 1u);

	/* the header the receiving part sends while a command runs: BUSY for a good request, its own status for a bad one */
	uint8_t h[16];
	size_t n = xt_req(rq, RREC_OP_DELETE, 0x99, ((const uint8_t[]){ 1, 0, 0, 0 }), 4);

	rxf_proto_busy_header(rq, n, h);
	zassert_equal(h[3], RREC_ST_BUSY);
	zassert_equal(xt_le(h + 4, 4), 0x99u);
	rq[0] = 0;
	rxf_proto_busy_header(rq, n, h);
	zassert_equal(h[3], RREC_ST_BAD_MAGIC);
}

/* X4: the unit answers only while the backend allows it: otherwise nothing is sent and nothing runs */
ZTEST(xfer_proto, test_silent_when_not_allowed)
{
	struct rxf_result res;

	fk.allowed = false;
	zassert_equal(go(RREC_OP_GET_INFO, 1, NULL, 0, &res), RXF_NO_ANSWER);
	zassert_equal(res.outcome, RXF_NO_ANSWER);
	zassert_equal(cap.total, 0u, "no byte sent");
	zassert_equal(cap.pieces, 0u);
	zassert_equal(fk.calls[RREC_OP_GET_INFO], 0u);
	size_t n = xt_req(rq, RREC_OP_GET_INFO, 1, NULL, 0);

	rq[0] = 0;                                  /* even a bad request gets no answer */
	zassert_equal(xt_run(RREC_USB_MPS_FS, rq, n, &res), RXF_NO_ANSWER);
	zassert_equal(cap.total, 0u);
	fk.allowed = true;
	zassert_equal(go(RREC_OP_GET_INFO, 1, NULL, 0, &res), 0);
	zassert_equal(cap.total, 51u);
}

/* C18: an abort (VBUS removed) stops the command that runs and nothing more is sent; an abort with nothing running
 * does not spoil the next command */
static void abort_in_read(void)
{
	rxf_proto_abort(&xctx);
}

ZTEST(xfer_proto, test_abort_stops_stream)
{
	struct rxf_result res;

	rxf_proto_abort(&xctx);                       /* idle: no effect */
	zassert_equal(go(RREC_OP_GET_INFO, 1, NULL, 0, &res), 0);
	zassert_equal(cap_status(), RREC_ST_OK, "an abort while idle does not drop the next command");

	fk.hook = abort_in_read;
	/* abort from inside the backend's battery call: the response of that command is not sent */
	zassert_equal(go(RREC_OP_GET_BATTERY, 2, NULL, 0, &res), RXF_ABORTED);
	zassert_equal(res.outcome, RXF_ABORTED);
	zassert_equal(cap.total, 0u, "no response for an aborted command");
	zassert_equal(fk.after_calls, 1u, "only the GET_INFO before it was reported");
	fk.hook = NULL;
	zassert_equal(go(RREC_OP_GET_INFO, 3, NULL, 0, &res), 0);
	zassert_equal(cap.total, 51u, "the next command runs");
	zassert_equal(xctx.running, 0);
}
