/* xt.h: helpers shared by the suites of tests/xfer (unit U4): a reference CRC-32, little-endian access, request
 * builders, a response capture, and a fake backend. Expected values in the cases are typed from design/firmware.md. */
#ifndef XT_H
#define XT_H

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/ztest.h>

#include <ring_rhw/rhw.h>
#include <ring_rhw/rhw_sim.h>
#include <ring_xfer/rxf.h>

#include "rxf_desc.h"
#include "rxf_proto.h"

/* CRC-32/ISO-HDLC written for the tests (table built from the reflected polynomial): the expected values never come
 * from the code under test (which calls the C library's crc32_ieee). */
uint32_t xt_crc(uint32_t prev, const uint8_t *d, size_t n);      /* prev = 0 starts; chain with the result */
uint32_t xt_le(const uint8_t *p, unsigned bytes);                /* little-endian read, 1 to 4 bytes */
uint64_t xt_le64(const uint8_t *p);
void xt_put(uint8_t *p, uint64_t v, unsigned bytes);             /* little-endian write */

/* A request: header (status 0, CRC of the payload, 0 when empty) and payload. Returns the total length. */
size_t xt_req(uint8_t *out, uint8_t op, uint32_t tag, const void *payload, uint32_t plen);

/* What the fake backend does and what it saw. */
struct fake {
	bool allowed;                           /* may_answer() */
	enum rrec_status st[RREC_OP_LAST + 1];  /* status each command returns (index = opcode; READ_RANGE: range_check) */
	uint32_t calls[RREC_OP_LAST + 1];       /* calls per opcode (READ_RANGE counts range_check; reads: read_calls) */
	uint32_t read_calls;                    /* read_chunk calls */
	uint32_t fail_read_at;                  /* read_chunk call number (from 1) that fails with STORAGE_ERROR; 0 = never */
	uint32_t change_read_at;                /* read_chunk call number whose data differs (a chunk that changed); 0 = never */
	uint32_t last_rec, last_first, last_count;
	uint32_t last_digest;
	int64_t last_utc_ms;
	int16_t last_tz;
	uint32_t last_image_size, last_image_crc, last_fw_offset;
	size_t last_fw_len;
	uint8_t last_fw_first, last_fw_lastbyte;
	uint8_t last_factory[16];
	size_t last_factory_len;
	uint16_t last_max;
	uint32_t free_after;
	size_t factory_out_len;                 /* bytes the factory call reports (it writes them even when it refuses) */
	size_t list_len, log_len;               /* payload sizes the list and log calls report */
	void (*hook)(void);                     /* called inside get_battery (a command that runs) */
	/* after_response */
	uint32_t after_calls;
	uint8_t after_op;
	enum rrec_status after_st;
	uint32_t after_tag, after_len;
	uint32_t seq;                           /* counts emitted pieces and after_response calls in order */
	uint32_t after_seq;                     /* the value of seq when after_response ran */
	uint32_t after_packets;                 /* USB packets in the simulated log when after_response ran */
};
extern struct fake fk;
void fake_reset(void);
const struct rxf_backend *fake_be(void);
/* The byte i of chunk `chunk` of recording `rec` as the fake serves it (the same function on both sides). */
uint8_t fake_chunk_byte(uint32_t rec, uint32_t chunk, uint32_t i);

/* Response capture: an emit function for rxf_proto_handle(). */
#define CAP_MAX 140000u
struct cap {
	uint8_t buf[CAP_MAX];
	size_t total;           /* bytes handed over (also when more than CAP_MAX) */
	uint32_t pieces;        /* emit calls */
	uint32_t bad_pieces;    /* non-last pieces that are not a multiple of mps */
	uint32_t last_flags;    /* emit calls with last = true */
	uint32_t mps;
	uint32_t pcrc;          /* running reference CRC of everything after the 16-byte header */
	int fail_after;         /* emit returns -EIO from this piece number on (0 = never) */
	bool last_seen_then_more;
};
extern struct cap cap;
void cap_reset(uint32_t mps);
int cap_emit(void *user, const uint8_t *d, size_t n, bool last);

/* Runs one request through the pure handler on a context bound to the fake backend, with the capture. */
extern struct rxf_ctx xctx;
int xt_run(uint32_t mps, const uint8_t *req, size_t n, struct rxf_result *res);
/* The response header fields of what the capture holds. */
uint8_t cap_status(void);
uint32_t cap_len(void);
uint32_t cap_tag(void);
uint32_t cap_crc(void);

#endif
