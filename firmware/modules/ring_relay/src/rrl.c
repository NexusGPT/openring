/* Ring relay, pure part: see rrl.h. All numbers on the wire are little endian. */

#include <string.h>

#include <ring_inbox/rinbox.h>
#include <ring_relay/rrl.h>

static uint32_t le32(const uint8_t *p)
{
	return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static uint16_t le16(const uint8_t *p)
{
	return (uint16_t)(p[0] | (p[1] << 8));
}

static void put32(uint8_t *p, uint32_t v)
{
	p[0] = (uint8_t)v;
	p[1] = (uint8_t)(v >> 8);
	p[2] = (uint8_t)(v >> 16);
	p[3] = (uint8_t)(v >> 24);
}

int rrl_parse(const uint8_t *rec, size_t len, struct rrl_rec *out)
{
	bool seen[4] = { false, false, false, false };
	size_t p = 2;

	memset(out, 0, sizeof(*out));
	for (int i = 0; i < 4; i++) {
		out->text[i] = rec; /* a missing field: empty, with a valid pointer */
	}
	if (rec == NULL || len < RRL_REC_MIN) {
		return RRL_E_RECORD;
	}
	if ((rec[1] & ~RRL_FLAGS_MASK) != 0) {
		return RRL_E_RECORD;
	}
	out->category = rec[0];
	out->flags = rec[1];
	while (p < len) {
		uint8_t type;
		uint8_t l;

		if (p + 2 > len) {
			return RRL_E_RECORD; /* the type is there, its length is not */
		}
		type = rec[p];
		l = rec[p + 1];
		if (p + 2 + l > len) {
			return RRL_E_RECORD; /* the field runs past the end */
		}
		if (type < RRL_F_APP || type > RRL_F_DATE || seen[type - 1]) {
			return RRL_E_RECORD; /* unknown or repeated */
		}
		seen[type - 1] = true;
		out->text[type - 1] = &rec[p + 2];
		out->len[type - 1] = l;
		p += 2U + l;
	}
	return 0;
}

void rrl_init(struct rrl *s)
{
	memset(s, 0, sizeof(*s));
}

static void refuse(struct rrl_res *r, uint8_t code, uint32_t id)
{
	r->act = RRL_ACT_ERROR;
	r->err = code;
	r->id = id;
}

static void drop_record(struct rrl *s)
{
	s->busy = false;
	s->got = 0;
	s->total = 0;
}

/* the id the frame carries, 0 when it carries none that can be read */
static uint32_t frame_id(const uint8_t *f, size_t len)
{
	if (len >= 5 && (f[0] == RRL_OP_PUT || f[0] == RRL_OP_REMOVE)) {
		return le32(&f[1]);
	}
	return 0;
}

void rrl_frame(struct rrl *s, bool apple, const uint8_t *f, size_t len, struct rrl_res *r)
{
	memset(r, 0, sizeof(*r));
	r->act = RRL_ACT_NONE;
	if (apple) {
		refuse(r, RRL_E_SOURCE, frame_id(f, len));
		return;
	}
	if (len == 0) {
		refuse(r, RRL_E_FRAME, 0);
		return;
	}
	switch (f[0]) {
	case RRL_OP_HELLO:
		if (len != 2) {
			refuse(r, RRL_E_FRAME, 0);
		} else if (f[1] != RRL_VERSION) {
			refuse(r, RRL_E_VERSION, 0);
		} else {
			s->hello = true;
			drop_record(s);
			r->act = RRL_ACT_HELLO;
		}
		break;
	case RRL_OP_PUT: {
		uint32_t id;
		uint16_t total, off;
		size_t dlen;

		if (len < 10) { /* opcode, id, total, offset and at least one data byte */
			refuse(r, RRL_E_FRAME, frame_id(f, len));
			break;
		}
		id = le32(&f[1]);
		total = le16(&f[5]);
		off = le16(&f[7]);
		dlen = len - 9;
		if (!s->hello) {
			refuse(r, RRL_E_NO_HELLO, id);
			break;
		}
		if (total < RRL_REC_MIN || total > RRL_REC_MAX) {
			drop_record(s);
			refuse(r, RRL_E_TOTAL, id);
			break;
		}
		if (off == 0) {
			drop_record(s); /* a piece with offset 0 drops an unfinished record and begins a new one */
			s->busy = true;
			s->id = id;
			s->total = total;
		} else if (!s->busy || id != s->id || total != s->total || off != s->got) {
			drop_record(s);
			refuse(r, RRL_E_ORDER, id);
			break;
		}
		if ((size_t)off + dlen > total) {
			drop_record(s);
			refuse(r, RRL_E_ORDER, id);
			break;
		}
		memcpy(&s->buf[off], &f[9], dlen);
		s->got = (uint16_t)(off + dlen);
		if (s->got == s->total) {
			int pr;

			s->busy = false;
			pr = rrl_parse(s->buf, s->total, &r->rec);
			if (pr != 0) {
				drop_record(s);
				refuse(r, RRL_E_RECORD, id);
				break;
			}
			r->act = RRL_ACT_PUT;
			r->id = id;
		}
		break;
	}
	case RRL_OP_REMOVE:
		if (len != 5) {
			refuse(r, RRL_E_FRAME, frame_id(f, len));
		} else if (!s->hello) {
			refuse(r, RRL_E_NO_HELLO, le32(&f[1]));
		} else {
			r->act = RRL_ACT_REMOVE;
			r->id = le32(&f[1]);
		}
		break;
	case RRL_OP_CLEAR:
		if (len != 1) {
			refuse(r, RRL_E_FRAME, 0);
		} else if (!s->hello) {
			refuse(r, RRL_E_NO_HELLO, 0);
		} else {
			r->act = RRL_ACT_CLEAR;
		}
		break;
	default:
		refuse(r, RRL_E_FRAME, 0);
		break;
	}
}

size_t rrl_out_ready(uint8_t *o)
{
	o[0] = RRL_OUT_READY;
	o[1] = RRL_VERSION;
	o[2] = RINBOX_MAX;
	return 3;
}

size_t rrl_out_action(uint8_t *o, uint32_t id, uint8_t action)
{
	o[0] = RRL_OUT_ACTION;
	put32(&o[1], id);
	o[5] = action;
	return 6;
}

size_t rrl_out_error(uint8_t *o, uint8_t code, uint32_t id)
{
	o[0] = RRL_OUT_ERROR;
	o[1] = code;
	put32(&o[2], id);
	return 6;
}

size_t rrl_info(uint8_t *o)
{
	o[0] = RRL_VERSION;
	o[1] = RINBOX_MAX;
	o[2] = RINBOX_APP_MAX;
	o[3] = RINBOX_TITLE_MAX;
	o[4] = RINBOX_MSG_MAX;
	o[5] = RINBOX_DATE_MAX;
	return RRL_INFO_LEN;
}
