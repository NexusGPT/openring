/*
 * Ring relay, pure part (design/firmware.md section 7.7): the frames a helper app writes to the relay service, the
 * record of a PUT, and the decision on each frame. No kernel, driver or Bluetooth call, no locking (the Bluetooth part
 * holds one mutex around every call).
 *
 * rrl_frame() takes one frame written to In and says what to do: nothing (a piece of a record was taken), HELLO, store a
 * record, REMOVE, CLEAR, or refuse with a code. A refused frame never asks for a change of the store.
 */
#ifndef RING_RELAY_RRL_H
#define RING_RELAY_RRL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RRL_VERSION    1
#define RRL_REC_MIN    2
#define RRL_REC_MAX    512
#define RRL_INFO_LEN   6

/* frames written to In */
#define RRL_OP_HELLO   0x01
#define RRL_OP_PUT     0x02
#define RRL_OP_REMOVE  0x03
#define RRL_OP_CLEAR   0x04
/* frames notified on Out */
#define RRL_OUT_READY  0x81
#define RRL_OUT_ACTION 0x82
#define RRL_OUT_ERROR  0x83

/* the action byte of ACTION */
#define RRL_ACTION_POSITIVE 0
#define RRL_ACTION_NEGATIVE 1

/* refusal codes of ERROR (and of the ATT error 0x80 on the write) */
enum rrl_err {
	RRL_OK = 0,
	RRL_E_FRAME = 1,    /* unknown opcode or wrong frame length */
	RRL_E_NO_HELLO = 2, /* no HELLO in this session */
	RRL_E_ORDER = 3,    /* PUT piece out of order or beyond total */
	RRL_E_TOTAL = 4,    /* total under 2 or over 512 */
	RRL_E_RECORD = 5,   /* record malformed */
	RRL_E_VERSION = 6,  /* version not supported */
	RRL_E_SOURCE = 7,   /* the link's notifications come from Apple's service */
};

/* field types of a record */
#define RRL_F_APP   1
#define RRL_F_TITLE 2
#define RRL_F_MSG   3
#define RRL_F_DATE  4

/* flag bits above this one must be 0 */
#define RRL_FLAGS_MASK 0x1FU

/* A parsed record. text[0..3] are the application identifier, title, message and date (field types 1 to 4); they point into
 * the bytes that were parsed; len[i] is the length as sent (not yet cut); a missing field has len 0 and a non-NULL pointer. */
struct rrl_rec {
	uint8_t category;
	uint8_t flags;
	const uint8_t *text[4];
	uint8_t len[4];
};

/* Parse a whole record. 0, or RRL_E_RECORD: shorter than 2 bytes, a flag bit above 4, a field that runs past the end, a type
 * that is not 1 to 4 or is repeated. (The range of the total is a separate refusal, RRL_E_TOTAL.) */
int rrl_parse(const uint8_t *rec, size_t len, struct rrl_rec *out);

/* The state of one session (one link). */
struct rrl {
	bool hello;      /* a HELLO was accepted on this link */
	bool busy;       /* a record is being received */
	uint32_t id;     /* its notification id */
	uint16_t total;  /* its length */
	uint16_t got;    /* bytes received so far */
	uint8_t buf[RRL_REC_MAX];
};

/* A new link: no HELLO, no record in progress. */
void rrl_init(struct rrl *s);

enum rrl_act {
	RRL_ACT_NONE = 0, /* the frame was accepted and asks for nothing yet (a piece of a record) */
	RRL_ACT_HELLO,    /* answer READY and empty what the relay stored */
	RRL_ACT_PUT,      /* store res.rec under res.id */
	RRL_ACT_REMOVE,   /* remove res.id */
	RRL_ACT_CLEAR,    /* empty what the relay stored */
	RRL_ACT_ERROR,    /* refused: res.err, res.id */
};

struct rrl_res {
	enum rrl_act act;
	uint8_t err;        /* RRL_E_* when act is RRL_ACT_ERROR */
	uint32_t id;        /* the notification id of PUT, REMOVE; the id in ERROR (0 when the frame had none) */
	struct rrl_rec rec; /* for RRL_ACT_PUT; its text points into s->buf, valid until the next call */
};

/* One frame written to In. apple: Apple's notification service was found on this link (every frame is refused with code 7). */
void rrl_frame(struct rrl *s, bool apple, const uint8_t *frame, size_t len, struct rrl_res *res);

/* Frames for Out and the bytes of Info; each returns the length written (o is at least 6 bytes). */
size_t rrl_out_ready(uint8_t *o);
size_t rrl_out_action(uint8_t *o, uint32_t id, uint8_t action);
size_t rrl_out_error(uint8_t *o, uint8_t code, uint32_t id);
size_t rrl_info(uint8_t *o);

#ifdef __cplusplus
}
#endif

#endif
