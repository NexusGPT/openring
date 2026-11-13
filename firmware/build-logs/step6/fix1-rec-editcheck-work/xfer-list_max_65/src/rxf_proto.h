/*
 * rxf_proto.h: the pure part of the USB transfer (software step 6, unit U4). Not public: the logic suites and
 * rxf_class.c include it. No kernel call (stdint, stdbool, string, and crc32_ieee() of the C library, decision D11a).
 * "FW l.N" = line N of design/firmware.md. Numbers only from rrec_spec.h.
 *
 * What it does: validates one complete request (FW 6.2), checks the argument limits (FW 6.3) BEFORE it calls the
 * backend, builds the response and hands it to an emit function in pieces whose sizes are multiples of the bus
 * speed's packet size except the last one (so no short packet ends a transfer early and no zero-length packet is
 * needed, FW l.688), then calls backend->after_response().
 */
#ifndef RXF_PROTO_H
#define RXF_PROTO_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <ring_xfer/rxf.h>

/* The largest request payload: FW_DATA = offset u32 + 4,096 image bytes (FW l.704). */
#define RXF_MAX_REQ_PAYLOAD (4u + RREC_FW_DATA_MAX)
#define RXF_REQ_BYTES (RREC_MSG_HEADER_BYTES + RXF_MAX_REQ_PAYLOAD)

#define RXF_LIST_PAYLOAD_MAX (2u + RREC_LIST_MAX_MAX * RREC_LIST_ENTRY_BYTES)         /* FW l.697 */
#define RXF_LOG_PAYLOAD_MAX (2u + RREC_GET_LOG_MAX_MAX * RREC_LOG_RECORD_BYTES)       /* FW l.706 */
#define RXF_FACTORY_RESULT_MAX 256u                                                   /* rxf.h */

/* One staging buffer holds the 16-byte header and a whole small response, or the carry-over (less than one packet)
 * and one chunk of a READ_RANGE stream. */
#define RXF_STAGE_BYTES (RREC_CHUNK_BYTES + RREC_USB_MPS_HS)

/* Hands out bytes to the transport. 0, or a negative errno (the response is then abandoned). Every call but the last
 * of one response (last = false) has a size that is a multiple of the packet size passed to rxf_proto_handle(); the
 * transport may hold its output line from the first call until the call with last = true. */
typedef int (*rxf_emit_fn)(void *user, const uint8_t *data, size_t len, bool last);

struct rxf_ctx {
	const struct rxf_backend *be;
	volatile int running;   /* a command runs (set and cleared inside rxf_proto_handle only) */
	volatile int aborted;   /* rxf_proto_abort() while a command ran */
	uint8_t stage[RXF_STAGE_BYTES];
	uint32_t crcs[RREC_READ_COUNT_MAX];
};

enum rxf_outcome {
	RXF_SENT = 0,           /* the response was handed over completely */
	RXF_NO_ANSWER = 1,      /* may_answer() was false: nothing was sent (FW l.673) */
	RXF_ABORTED = 2,        /* rxf_proto_abort() (VBUS removed): the rest of the response was not sent (FW l.179) */
	RXF_SEND_FAILED = 3,    /* emit failed (host stopped reading) or a chunk read changed or failed mid-stream */
};

struct rxf_result {
	enum rxf_outcome outcome;
	uint8_t opcode;         /* of the request (as received) */
	enum rrec_status status;
	uint32_t tag;
	uint32_t length;        /* payload length of the response */
	bool dispatched;        /* the request reached the command table (valid header, known opcode, not BUSY) */
};

/* Parsed header of a request (little-endian fields, FW l.677 to l.686). */
struct rxf_req {
	uint8_t opcode;
	uint32_t tag;
	uint32_t length;
	uint32_t crc;
};

void rxf_proto_init(struct rxf_ctx *c, const struct rxf_backend *be);

/* VBUS removed: if a command runs, it stops at its next step and sends nothing more (FW l.179). Any thread. */
void rxf_proto_abort(struct rxf_ctx *c);

/* The checks that need no backend: header present, magic, length bound and match, CRC, opcode known. Returns OK or the
 * status of FW l.689 to l.690 (BAD_MAGIC, BAD_CRC, UNKNOWN_OPCODE, BAD_ARG for a length that is too large or does
 * not match the bytes given). *h is filled from the header bytes whenever 16 bytes were given. */
enum rrec_status rxf_proto_check(const uint8_t *req, size_t req_len, struct rxf_req *h);

/* The 16-byte header of a response (FW l.677 to l.686): magic, opcode, status, tag, length, crc (0 when length is 0). */
void rxf_proto_put_header(uint8_t out[RREC_MSG_HEADER_BYTES], uint8_t opcode, enum rrec_status st, uint32_t tag,
			 uint32_t length, uint32_t crc);

/* The CRC-32 of a payload; 0 when the length is 0 (FW l.686). */
uint32_t rxf_proto_payload_crc(const uint8_t *payload, size_t length);

/* The header of the answer to a request that cannot run now: its own error status when the request is bad, BUSY
 * when it is valid (FW l.711). For the part that receives a request while a command runs. */
void rxf_proto_busy_header(const uint8_t *req, size_t req_len, uint8_t out[RREC_MSG_HEADER_BYTES]);

/* true when the command table knows the opcode (RREC_OP_FIRST to RREC_OP_LAST). */
bool rxf_proto_opcode_known(uint8_t opcode);

/* Handle one request of req_len bytes (header + payload, complete) and hand the response to emit. mps = the packet
 * size of the bus speed now (64 or 512). Runs on the transfer thread. Returns 0 (RXF_SENT) or a nonzero outcome of
 * `res`. backend->after_response() is called only after a complete hand-over (outcome RXF_SENT) and only for a
 * dispatched request (valid header, known opcode, not BUSY): its status may be an error such as BAD_ARG. */
int rxf_proto_handle(struct rxf_ctx *c, uint32_t mps, const uint8_t *req, size_t req_len, rxf_emit_fn emit,
		     void *user, struct rxf_result *res);

#endif
