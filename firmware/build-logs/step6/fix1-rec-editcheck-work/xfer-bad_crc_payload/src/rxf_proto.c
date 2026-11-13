/*
 * rxf_proto.c: the pure part of the USB transfer (software step 6, unit U4): header, CRC, status codes, opcode table,
 * argument limits, response layouts, BUSY. No kernel call (decision D11a: crc32_ieee() of the C library is a library
 * function). "FW l.N" = line N of design/firmware.md. Written for this project.
 */
#include <string.h>

#include <zephyr/sys/crc.h>

#include "rxf_proto.h"

/* ------------------------------------------------------------------ little-endian helpers (FW l.70) */
static uint16_t get16(const uint8_t *p)
{
	return (uint16_t)(p[0] | (p[1] << 8));
}

static uint32_t get32(const uint8_t *p)
{
	return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static uint64_t get64(const uint8_t *p)
{
	return (uint64_t)get32(p) | ((uint64_t)get32(p + 4) << 32);
}

static void put16(uint8_t *p, uint16_t v)
{
	p[0] = (uint8_t)v;
	p[1] = (uint8_t)(v >> 8);
}

static void put32(uint8_t *p, uint32_t v)
{
	p[0] = (uint8_t)v;
	p[1] = (uint8_t)(v >> 8);
	p[2] = (uint8_t)(v >> 16);
	p[3] = (uint8_t)(v >> 24);
}

/* ------------------------------------------------------------------ header */
uint32_t rxf_proto_payload_crc(const uint8_t *payload, size_t length)
{
	return length == 0u ? 0u : crc32_ieee(payload, length);   /* FW l.686: 0 when the length is 0 */
}

void rxf_proto_put_header(uint8_t out[RREC_MSG_HEADER_BYTES], uint8_t opcode, enum rrec_status st, uint32_t tag,
			  uint32_t length, uint32_t crc)
{
	put16(out + RREC_MSG_OFF_MAGIC, RREC_MSG_MAGIC);
	out[RREC_MSG_OFF_OPCODE] = opcode;
	out[RREC_MSG_OFF_STATUS] = (uint8_t)st;
	put32(out + RREC_MSG_OFF_TAG, tag);
	put32(out + RREC_MSG_OFF_LENGTH, length);
	put32(out + RREC_MSG_OFF_CRC, crc);
}

bool rxf_proto_opcode_known(uint8_t opcode)
{
	return opcode >= RREC_OP_FIRST && opcode <= RREC_OP_LAST;
}

enum rrec_status rxf_proto_check(const uint8_t *req, size_t req_len, struct rxf_req *h)
{
	uint32_t expect;

	memset(h, 0, sizeof(*h));
	if (req_len < RREC_MSG_HEADER_BYTES) {
		return RREC_ST_BAD_MAGIC;
	}
	h->opcode = req[RREC_MSG_OFF_OPCODE];
	h->tag = get32(req + RREC_MSG_OFF_TAG);
	h->length = get32(req + RREC_MSG_OFF_LENGTH);
	h->crc = get32(req + RREC_MSG_OFF_CRC);
	if (get16(req + RREC_MSG_OFF_MAGIC) != RREC_MSG_MAGIC) {
		return RREC_ST_BAD_MAGIC;                     /* FW l.690 */
	}
	if (h->length > RXF_MAX_REQ_PAYLOAD || h->length != req_len - RREC_MSG_HEADER_BYTES) {
		return RREC_ST_BAD_ARG;
	}
	expect = rxf_proto_payload_crc(req + RREC_MSG_HEADER_BYTES, h->length);
	if (h->crc != expect) {
		return RREC_ST_BAD_CRC;                       /* FW l.690 */
	}
	if (!rxf_proto_opcode_known(h->opcode)) {
		return RREC_ST_UNKNOWN_OPCODE;                /* FW l.689 */
	}
	return RREC_ST_OK;
}

/* A response with no payload: status in the header, length 0, CRC 0 (FW l.690). Its own small buffer, so it can be
 * sent while a command uses the staging buffer. */
static int emit_error(rxf_emit_fn emit, void *user, uint8_t opcode, enum rrec_status st, uint32_t tag)
{
	uint8_t out[RREC_MSG_HEADER_BYTES + 4] = { 0 };
	uint32_t len;

	len = st == RREC_ST_BAD_CRC ? 4u : 0u;
	rxf_proto_put_header(out, opcode, st, tag, len, rxf_proto_payload_crc(out + RREC_MSG_HEADER_BYTES, len));
	return emit(user, out, RREC_MSG_HEADER_BYTES + len, true);
}

void rxf_proto_busy_header(const uint8_t *req, size_t req_len, uint8_t out[RREC_MSG_HEADER_BYTES])
{
	struct rxf_req h;
	enum rrec_status st = rxf_proto_check(req, req_len, &h);

	if (st == RREC_ST_OK) {
		st = RREC_ST_BUSY;                            /* FW l.711 */
	}
	rxf_proto_put_header(out, h.opcode, st, h.tag, 0u, 0u);
}

void rxf_proto_init(struct rxf_ctx *c, const struct rxf_backend *be)
{
	memset(c, 0, sizeof(*c));
	c->be = be;
}

void rxf_proto_abort(struct rxf_ctx *c)
{
	if (__atomic_load_n(&c->running, __ATOMIC_ACQUIRE) != 0) {
		__atomic_store_n(&c->aborted, 1, __ATOMIC_RELEASE);
	}
}

static bool stopped(const struct rxf_ctx *c)
{
	return __atomic_load_n(&c->aborted, __ATOMIC_ACQUIRE) != 0;
}

/* ------------------------------------------------------------------ the commands */
static int outcome_of(int emit_rc, struct rxf_ctx *c)
{
	if (emit_rc == 0) {
		return RXF_SENT;
	}
	return stopped(c) ? RXF_ABORTED : RXF_SEND_FAILED;
}

/* Answer with the payload already at stage + 16 (or an error status). */
static int finish_small(struct rxf_ctx *c, rxf_emit_fn emit, void *user, const struct rxf_req *h, enum rrec_status st,
			uint32_t len, struct rxf_result *res)
{
	int rc;

	if (stopped(c)) {
		return RXF_ABORTED;                           /* FW l.179: no response for an aborted command */
	}
	res->status = st;
	if (st != RREC_ST_OK) {
		rc = emit_error(emit, user, h->opcode, st, h->tag);
		return outcome_of(rc, c);
	}
	res->length = len;
	rxf_proto_put_header(c->stage, h->opcode, st, h->tag, len, rxf_proto_payload_crc(c->stage + RREC_MSG_HEADER_BYTES, len));
	rc = emit(user, c->stage, RREC_MSG_HEADER_BYTES + len, true);
	return outcome_of(rc, c);
}

static int read_range(struct rxf_ctx *c, uint32_t mps, const struct rxf_req *h, const uint8_t *p, rxf_emit_fn emit,
		      void *user, struct rxf_result *res)
{
	uint32_t rec, first, count, crc = 0u, rem, total, n;
	enum rrec_status st;
	uint8_t *s = c->stage;

	if (h->length != RREC_READ_REQ_BYTES) {
		return finish_small(c, emit, user, h, RREC_ST_BAD_ARG, 0u, res);
	}
	rec = get32(p);
	first = get32(p + 4);
	count = get32(p + 8);
	if (count < RREC_READ_COUNT_MIN || count > RREC_READ_COUNT_MAX) {              /* FW l.698 */
		return finish_small(c, emit, user, h, RREC_ST_BAD_ARG, 0u, res);
	}
	if (first + count < first) {
		return finish_small(c, emit, user, h, RREC_ST_NOT_FOUND, 0u, res);
	}
	/* every chunk must exist before any byte is sent (rxf.h range_check, FW l.661) */
	st = c->be->range_check(rec, first, count);
	if (st != RREC_ST_OK) {
		return finish_small(c, emit, user, h, st, 0u, res);
	}
	/* pass 1: the header's CRC covers the whole payload and comes before it (FW l.686, rxf.h) */
	for (uint32_t i = 0; i < count; i++) {
		if (stopped(c)) {
			return RXF_ABORTED;
		}
		st = c->be->read_chunk(rec, first + i, s);
		if (st != RREC_ST_OK) {
			return finish_small(c, emit, user, h, st, 0u, res);
		}
		c->crcs[i] = crc32_ieee(s, RREC_CHUNK_BYTES);
		crc = crc32_ieee_update(crc, s, RREC_CHUNK_BYTES);
	}
	res->status = RREC_ST_OK;
	res->length = count * RREC_CHUNK_BYTES;
	rxf_proto_put_header(s, h->opcode, RREC_ST_OK, h->tag, res->length, crc);
	if (mps == 0u) {
		mps = RREC_USB_MPS_FS;
	}
	/* pass 2: header, then each chunk exactly as stored; the carry (less than one packet) stays in front of the
	 * next chunk so that every piece but the last is a whole number of packets */
	rem = RREC_MSG_HEADER_BYTES;
	for (uint32_t i = 0; i < count; i++) {
		if (stopped(c)) {
			return RXF_ABORTED;
		}
		st = c->be->read_chunk(rec, first + i, s + rem);
		if (st != RREC_ST_OK || crc32_ieee(s + rem, RREC_CHUNK_BYTES) != c->crcs[i]) {
			res->status = RREC_ST_STORAGE_ERROR;  /* the chunk changed or failed after the header was fixed */
			return RXF_SEND_FAILED;
		}
		total = rem + RREC_CHUNK_BYTES;
		n = (i + 1u == count) ? total : (total / mps) * mps;
		if (n != 0u) {
			int rc = emit(user, s, n, i + 1u == count);

			if (rc != 0) {
				return outcome_of(rc, c);
			}
		}
		rem = total - n;
		memmove(s, s + n, rem);
	}
	return RXF_SENT;
}

static int dispatch(struct rxf_ctx *c, uint32_t mps, const struct rxf_req *h, const uint8_t *p, rxf_emit_fn emit,
		    void *user, struct rxf_result *res)
{
	const struct rxf_backend *be = c->be;
	uint8_t *out = c->stage + RREC_MSG_HEADER_BYTES;
	enum rrec_status st = RREC_ST_OK;
	uint32_t len = 0u, plen = h->length;
	size_t olen = 0u;

	switch (h->opcode) {
	case RREC_OP_GET_INFO:                                                  /* FW l.696 */
		if (plen != 0u) {
			st = RREC_ST_BAD_ARG;
			break;
		}
		st = be->get_info(out);
		len = RREC_GET_INFO_BYTES;
		break;
	case RREC_OP_LIST_RECORDINGS: {                                         /* FW l.697 */
		uint16_t max;

		if (plen != RREC_LIST_REQ_BYTES) {
			st = RREC_ST_BAD_ARG;
			break;
		}
		max = get16(p + 4);
		if (max < RREC_LIST_MAX_MIN || max > RREC_LIST_MAX_MAX) {
			st = RREC_ST_BAD_ARG;
			break;
		}
		st = be->list(get32(p), max, out, &olen);
		if (st == RREC_ST_OK && (olen < 2u || olen > RXF_LIST_PAYLOAD_MAX)) {
			st = RREC_ST_STORAGE_ERROR;
		}
		len = (uint32_t)olen;
		break;
	}
	case RREC_OP_READ_RANGE:                                                /* FW l.698 */
		return read_range(c, mps, h, p, emit, user, res);
	case RREC_OP_CONFIRM:                                                   /* FW l.699 */
		if (plen != RREC_CONFIRM_REQ_BYTES) {
			st = RREC_ST_BAD_ARG;
			break;
		}
		st = be->confirm(get32(p), get32(p + 4));
		break;
	case RREC_OP_DELETE: {                                                  /* FW l.700 */
		uint32_t free_after = 0u;

		if (plen != RREC_DELETE_REQ_BYTES) {
			st = RREC_ST_BAD_ARG;
			break;
		}
		st = be->del(get32(p), &free_after);
		put32(out, free_after);
		len = RREC_DELETE_RESP_BYTES;
		break;
	}
	case RREC_OP_SET_TIME:                                                  /* FW l.701 */
		if (plen != RREC_SET_TIME_REQ_BYTES) {
			st = RREC_ST_BAD_ARG;
			break;
		}
		st = be->set_time((int64_t)get64(p), (int16_t)get16(p + 8));
		break;
	case RREC_OP_GET_BATTERY:                                               /* FW l.702 */
		if (plen != 0u) {
			st = RREC_ST_BAD_ARG;
			break;
		}
		st = be->get_battery(out);
		len = RREC_GET_BATTERY_BYTES;
		break;
	case RREC_OP_FW_BEGIN:                                                  /* FW l.703 */
		if (plen != RREC_FW_BEGIN_REQ_BYTES) {
			st = RREC_ST_BAD_ARG;
			break;
		}
		st = be->fw_begin(get32(p), get32(p + 4));
		break;
	case RREC_OP_FW_DATA:                                                   /* FW l.704 */
		if (plen < 4u + RREC_FW_DATA_MIN || plen > 4u + RREC_FW_DATA_MAX) {
			st = RREC_ST_BAD_ARG;
			break;
		}
		st = be->fw_data(get32(p), p + 4, plen - 4u);
		break;
	case RREC_OP_FW_END:                                                    /* FW l.705 */
		if (plen != 0u) {
			st = RREC_ST_BAD_ARG;
			break;
		}
		st = be->fw_end();
		break;
	case RREC_OP_GET_LOG: {                                                 /* FW l.706 */
		uint16_t max;

		if (plen != RREC_GET_LOG_REQ_BYTES) {
			st = RREC_ST_BAD_ARG;
			break;
		}
		max = get16(p + 4);
		if (max < RREC_GET_LOG_MAX_MIN || max > RREC_GET_LOG_MAX_MAX) {
			st = RREC_ST_BAD_ARG;
			break;
		}
		st = be->get_log(get32(p), max, out, &olen);
		if (st == RREC_ST_OK && (olen < 2u || olen > RXF_LOG_PAYLOAD_MAX)) {
			st = RREC_ST_STORAGE_ERROR;
		}
		len = (uint32_t)olen;
		break;
	}
	case RREC_OP_REBOOT:                                                    /* FW l.707 */
		if (plen != 0u) {
			st = RREC_ST_BAD_ARG;
		}
		break;                                                          /* the join reboots in after_response */
	case RREC_OP_FACTORY:                                                   /* FW l.708 */
		if (plen < 1u) {
			st = RREC_ST_BAD_ARG;
			break;
		}
		st = be->factory(p, plen, out, &olen);
		if (st == RREC_ST_OK && olen > RXF_FACTORY_RESULT_MAX) {
			st = RREC_ST_STORAGE_ERROR;
		}
		len = (uint32_t)olen;
		break;
	default:
		st = RREC_ST_UNKNOWN_OPCODE;
		break;
	}
	return finish_small(c, emit, user, h, st, len, res);
}

int rxf_proto_handle(struct rxf_ctx *c, uint32_t mps, const uint8_t *req, size_t req_len, rxf_emit_fn emit,
		     void *user, struct rxf_result *res)
{
	struct rxf_req h;
	enum rrec_status st;
	int rc;

	memset(res, 0, sizeof(*res));
	if (!c->be->may_answer()) {                       /* FW l.673: CHARGING, TRANSFER, FACTORY_TEST only */
		res->outcome = RXF_NO_ANSWER;
		return RXF_NO_ANSWER;
	}
	st = rxf_proto_check(req, req_len, &h);
	res->opcode = h.opcode;
	res->tag = h.tag;
	if (st != RREC_ST_OK) {
		res->status = st;
		rc = emit_error(emit, user, h.opcode, st, h.tag);
		res->outcome = rc == 0 ? RXF_SENT : RXF_SEND_FAILED;
		return res->outcome;
	}
	if (__atomic_exchange_n(&c->running, 1, __ATOMIC_ACQ_REL) != 0) {
		res->status = RREC_ST_BUSY;               /* FW l.711 */
		rc = emit_error(emit, user, h.opcode, RREC_ST_BUSY, h.tag);
		res->outcome = rc == 0 ? RXF_SENT : RXF_SEND_FAILED;
		return res->outcome;
	}
	__atomic_store_n(&c->aborted, 0, __ATOMIC_RELEASE);
	res->dispatched = true;
	res->outcome = (enum rxf_outcome)dispatch(c, mps, &h, req + RREC_MSG_HEADER_BYTES, emit, user, res);
	__atomic_store_n(&c->running, 0, __ATOMIC_RELEASE);
	if (res->outcome == RXF_SENT && c->be->after_response != NULL) {
		c->be->after_response(h.opcode, res->status, h.tag, h.length);   /* FW l.705, l.707 */
	}
	return res->outcome;
}
