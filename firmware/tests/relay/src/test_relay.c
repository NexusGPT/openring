/* ring_relay logic tests (native_sim and the simulated ring chip, no radio): the frames of the relay service, the record of a PUT,
 * every refusal code, and the store the frames end in (ring_inbox). Design: design/firmware.md section 7.7.
 *
 * Every expected value is a literal written here from section 7.7 (the byte layouts, the codes, the limits 16, 48, 48, 160, 15),
 * not produced by the code under test. The store is the real ring_inbox store; "apply" below does what the Bluetooth part does
 * with an accepted frame (HELLO and CLEAR empty it, PUT replaces or adds, REMOVE removes). */

#include <errno.h>
#include <string.h>

#include <zephyr/ztest.h>

#include <ring_inbox/rinbox.h>
#include <ring_relay/rrl.h>

ZTEST_SUITE(ring_relay, NULL, NULL, NULL, NULL, NULL);

/* ------------------------------------------------------------------ helpers */

struct rb {
	uint8_t b[1100];
	size_t n;
};

static void rb_init(struct rb *r, uint8_t cat, uint8_t flags)
{
	r->b[0] = cat;
	r->b[1] = flags;
	r->n = 2;
}

static void rb_field(struct rb *r, uint8_t type, const void *s, size_t len)
{
	r->b[r->n++] = type;
	r->b[r->n++] = (uint8_t)len;
	memcpy(&r->b[r->n], s, len);
	r->n += len;
}

static void rb_str(struct rb *r, uint8_t type, const char *s)
{
	rb_field(r, type, s, strlen(s));
}

/* the valid record of the truncation tests: category 4, flags positive and negative, four fields (59 bytes) */
static void rec_base(struct rb *r)
{
	rb_init(r, 4, 0x18);
	rb_str(r, 1, "com.example.mail");  /* 18 bytes with its header */
	rb_str(r, 2, "Hello");            /* 7 */
	rb_str(r, 3, "First message");     /* 15 */
	rb_str(r, 4, "20261112T101500");   /* 17 */
}

static size_t put_frame(uint8_t *f, uint32_t id, uint16_t total, uint16_t off, const uint8_t *d, size_t dl)
{
	f[0] = 0x02;
	f[1] = (uint8_t)id;
	f[2] = (uint8_t)(id >> 8);
	f[3] = (uint8_t)(id >> 16);
	f[4] = (uint8_t)(id >> 24);
	f[5] = (uint8_t)total;
	f[6] = (uint8_t)(total >> 8);
	f[7] = (uint8_t)off;
	f[8] = (uint8_t)(off >> 8);
	memcpy(&f[9], d, dl);
	return 9 + dl;
}

static size_t id_frame(uint8_t *f, uint8_t op, uint32_t id)
{
	f[0] = op;
	f[1] = (uint8_t)id;
	f[2] = (uint8_t)(id >> 8);
	f[3] = (uint8_t)(id >> 16);
	f[4] = (uint8_t)(id >> 24);
	return 5;
}

static struct rrl_res one(struct rrl *s, bool apple, const uint8_t *f, size_t n)
{
	struct rrl_res r;

	rrl_frame(s, apple, f, n, &r);
	return r;
}

static struct rrl_res hello(struct rrl *s)
{
	static const uint8_t f[2] = { 0x01, 0x01 };

	return one(s, false, f, 2);
}

/* the whole record in pieces of at most `piece` bytes; every piece but the last must be taken without a result */
static struct rrl_res put_pieces(struct rrl *s, uint32_t id, const uint8_t *rec, size_t total, size_t piece)
{
	struct rrl_res r = { 0 };
	size_t off = 0;

	while (off < total) {
		uint8_t f[9 + 1100];
		size_t dl = total - off < piece ? total - off : piece;
		size_t n = put_frame(f, id, (uint16_t)total, (uint16_t)off, &rec[off], dl);

		r = one(s, false, f, n);
		off += dl;
		if (off < total) {
			zassert_equal(r.act, RRL_ACT_NONE, "piece of %zu bytes at %zu of %zu: taken without a result (act %d err %u)", dl,
				      off - dl, total, r.act, r.err);
		}
	}
	return r;
}

static void apply(struct rinbox *b, const struct rrl_res *r)
{
	switch (r->act) {
	case RRL_ACT_HELLO:
	case RRL_ACT_CLEAR:
		rinbox_clear(b);
		break;
	case RRL_ACT_PUT:
		(void)rinbox_upsert(b, r->id, r->rec.category, r->rec.flags, (const char *)r->rec.text[0], r->rec.len[0],
				    (const char *)r->rec.text[1], r->rec.len[1], (const char *)r->rec.text[2], r->rec.len[2],
				    (const char *)r->rec.text[3], r->rec.len[3], NULL);
		break;
	case RRL_ACT_REMOVE:
		(void)rinbox_remove(b, r->id);
		break;
	default:
		break;
	}
}

/* send one record whole (piece size = the record) and apply it */
static struct rrl_res put_apply(struct rrl *s, struct rinbox *b, uint32_t id, const struct rb *r)
{
	struct rrl_res res = put_pieces(s, id, r->b, r->n, r->n);

	apply(b, &res);
	return res;
}

static void expect_err(struct rrl *s, const uint8_t *f, size_t n, uint8_t code, uint32_t id, const char *what)
{
	struct rrl_res r = one(s, false, f, n);

	zassert_equal(r.act, RRL_ACT_ERROR, "%s: refused (act %d)", what, r.act);
	zassert_equal(r.err, code, "%s: code %u, want %u", what, r.err, code);
	zassert_equal(r.id, id, "%s: id %u, want %u", what, r.id, id);
}

static void expect_item(const struct rinbox *b, uint8_t at, uint32_t uid, uint8_t cat, uint8_t flags, const char *app, const char *title,
			const char *msg, const char *date)
{
	const struct rinbox_item *it = rinbox_get(b, at);

	zassert_not_null(it, "entry %u exists", at);
	zassert_equal(it->uid, uid, "entry %u id %u, want %u", at, it->uid, uid);
	zassert_equal(it->category, cat, "entry %u category", at);
	zassert_equal(it->flags, flags, "entry %u flags 0x%02x, want 0x%02x", at, it->flags, flags);
	zassert_str_equal(it->app, app, "entry %u application identifier", at);
	zassert_str_equal(it->title, title, "entry %u title", at);
	zassert_str_equal(it->msg, msg, "entry %u message", at);
	zassert_str_equal(it->date, date, "entry %u date", at);
}

/* ------------------------------------------------------------------ the bytes on the wire */

ZTEST(ring_relay, test_info_and_out_frames)
{
	uint8_t o[8];
	static const uint8_t info[6] = { 0x01, 0x10, 0x30, 0x30, 0xA0, 0x0F }; /* version 1, store 16, app 48, title 48, message 160, date 15 */
	static const uint8_t ready[3] = { 0x81, 0x01, 0x10 };
	static const uint8_t action[6] = { 0x82, 0x78, 0x56, 0x34, 0x12, 0x01 };
	static const uint8_t error[6] = { 0x83, 0x05, 0x78, 0x56, 0x34, 0x12 };

	memset(o, 0xEE, sizeof(o));
	zassert_equal(rrl_info(o), 6);
	zassert_mem_equal(o, info, 6);
	zassert_equal(o[6], 0xEE, "nothing written past Info");
	zassert_equal(rrl_out_ready(o), 3);
	zassert_mem_equal(o, ready, 3);
	zassert_equal(rrl_out_action(o, 0x12345678, 1), 6);
	zassert_mem_equal(o, action, 6);
	zassert_equal(rrl_out_error(o, 5, 0x12345678), 6);
	zassert_mem_equal(o, error, 6);
	zassert_equal(rrl_out_action(o, 0, 0), 6);
	zassert_equal(o[5], 0, "positive is 0");
}

/* ------------------------------------------------------------------ opcodes */

ZTEST(ring_relay, test_every_opcode)
{
	struct rrl s;
	struct rrl_res r;
	uint8_t f[16];
	struct rb rec;
	size_t n;

	rrl_init(&s);
	/* 0x01 HELLO, version 1 */
	r = hello(&s);
	zassert_equal(r.act, RRL_ACT_HELLO, "HELLO");
	/* 0x02 PUT, a whole record in one piece */
	rb_init(&rec, 1, 0);
	rb_str(&rec, 2, "t");
	n = put_frame(f, 7, 5, 0, rec.b, rec.n);
	r = one(&s, false, f, n);
	zassert_equal(r.act, RRL_ACT_PUT, "PUT");
	zassert_equal(r.id, 7);
	zassert_equal(r.rec.category, 1);
	zassert_equal(r.rec.len[1], 1);
	zassert_equal(r.rec.text[1][0], 't');
	/* 0x03 REMOVE */
	n = id_frame(f, 0x03, 0xA1B2C3D4);
	r = one(&s, false, f, n);
	zassert_equal(r.act, RRL_ACT_REMOVE, "REMOVE");
	zassert_equal(r.id, 0xA1B2C3D4, "id little endian");
	/* 0x04 CLEAR */
	f[0] = 0x04;
	r = one(&s, false, f, 1);
	zassert_equal(r.act, RRL_ACT_CLEAR, "CLEAR");
	/* every other opcode value is refused with code 1, with a session and without */
	for (int pass = 0; pass < 2; pass++) {
		for (int op = 0; op < 256; op++) {
			if (op >= 1 && op <= 4) {
				continue;
			}
			f[0] = (uint8_t)op;
			f[1] = 1;
			f[2] = 2;
			f[3] = 3;
			f[4] = 4;
			r = one(&s, false, f, 5);
			zassert_equal(r.act, RRL_ACT_ERROR, "opcode 0x%02x refused (pass %d)", op, pass);
			zassert_equal(r.err, 1, "opcode 0x%02x: code 1", op);
			zassert_equal(r.id, 0, "opcode 0x%02x: no id", op);
		}
		rrl_init(&s); /* the second pass has no HELLO: still code 1, not code 2 */
	}
}

/* ------------------------------------------------------------------ every refusal code */

ZTEST(ring_relay, test_code_1_wrong_length)
{
	struct rrl s;
	uint8_t f[40] = { 0 };
	struct rrl_res r;

	rrl_init(&s);
	(void)hello(&s);
	r = one(&s, false, f, 0);
	zassert_equal(r.act, RRL_ACT_ERROR, "an empty write");
	zassert_equal(r.err, 1);
	/* HELLO: exactly 2 bytes */
	f[0] = 0x01;
	f[1] = 1;
	f[2] = 0;
	expect_err(&s, f, 1, 1, 0, "HELLO of 1 byte");
	expect_err(&s, f, 3, 1, 0, "HELLO of 3 bytes");
	/* REMOVE: exactly 5 bytes */
	f[0] = 0x03;
	expect_err(&s, f, 1, 1, 0, "REMOVE of 1 byte");
	expect_err(&s, f, 4, 1, 0, "REMOVE of 4 bytes");
	f[1] = 9;
	expect_err(&s, f, 6, 1, 9, "REMOVE of 6 bytes");
	/* CLEAR: exactly 1 byte */
	f[0] = 0x04;
	expect_err(&s, f, 2, 1, 0, "CLEAR of 2 bytes");
	expect_err(&s, f, 5, 1, 0, "CLEAR of 5 bytes");
	/* PUT: opcode, id, total, offset and at least one data byte (10 bytes) */
	f[0] = 0x02;
	f[1] = 5;
	expect_err(&s, f, 1, 1, 0, "PUT of 1 byte");
	expect_err(&s, f, 8, 1, 5, "PUT of 8 bytes (the id is readable)");
	expect_err(&s, f, 9, 1, 5, "PUT of 9 bytes (no data)");
	/* the same lengths before a HELLO are code 1 too (the length is checked before the session) */
	rrl_init(&s);
	expect_err(&s, f, 9, 1, 5, "PUT of 9 bytes without HELLO");
	f[0] = 0x04;
	expect_err(&s, f, 2, 1, 0, "CLEAR of 2 bytes without HELLO");
}

ZTEST(ring_relay, test_code_2_no_hello)
{
	struct rrl s;
	uint8_t f[40];
	struct rb rec;
	size_t n;

	rrl_init(&s);
	rb_init(&rec, 1, 0);
	n = put_frame(f, 77, 2, 0, rec.b, rec.n);
	expect_err(&s, f, n, 2, 77, "PUT without HELLO");
	n = id_frame(f, 0x03, 78);
	expect_err(&s, f, n, 2, 78, "REMOVE without HELLO");
	f[0] = 0x04;
	expect_err(&s, f, 1, 2, 0, "CLEAR without HELLO");
	/* a refused HELLO (version) does not start a session */
	f[0] = 0x01;
	f[1] = 2;
	expect_err(&s, f, 2, 6, 0, "HELLO version 2");
	f[0] = 0x04;
	expect_err(&s, f, 1, 2, 0, "CLEAR after a refused HELLO");
	/* a HELLO starts it */
	zassert_equal(hello(&s).act, RRL_ACT_HELLO);
	f[0] = 0x04;
	zassert_equal(one(&s, false, f, 1).act, RRL_ACT_CLEAR);
	/* a new link (rrl_init) has no HELLO again */
	rrl_init(&s);
	expect_err(&s, f, 1, 2, 0, "CLEAR on a new link");
}

ZTEST(ring_relay, test_code_3_order)
{
	struct rrl s;
	uint8_t f[80];
	uint8_t d[30];
	size_t n;

	memset(d, 0, sizeof(d));
	d[0] = 1;
	rrl_init(&s);
	(void)hello(&s);
	/* a piece with an offset when no record was started */
	n = put_frame(f, 5, 20, 10, d, 10);
	expect_err(&s, f, n, 3, 5, "offset 10 with no record in progress");
	/* the first piece is taken; the next one skips ahead */
	n = put_frame(f, 5, 20, 0, d, 5);
	zassert_equal(one(&s, false, f, n).act, RRL_ACT_NONE);
	n = put_frame(f, 5, 20, 6, d, 5);
	expect_err(&s, f, n, 3, 5, "a gap (offset 6 after 5 bytes)");
	/* after a refused piece the record is gone: the right next offset is refused too */
	n = put_frame(f, 5, 20, 5, d, 5);
	expect_err(&s, f, n, 3, 5, "offset 5 after the record was dropped");
	/* a repeated piece */
	n = put_frame(f, 5, 20, 0, d, 5);
	zassert_equal(one(&s, false, f, n).act, RRL_ACT_NONE);
	n = put_frame(f, 5, 20, 0 + 5, d, 5);
	zassert_equal(one(&s, false, f, n).act, RRL_ACT_NONE, "offset 5 after 5 bytes is the next piece");
	n = put_frame(f, 5, 20, 5, d, 5);
	expect_err(&s, f, n, 3, 5, "the same piece again (offset 5 after 10 bytes)");
	/* a piece beyond total, at offset 0 and later */
	n = put_frame(f, 5, 20, 0, d, 21);
	expect_err(&s, f, n, 3, 5, "21 bytes for a total of 20, offset 0");
	n = put_frame(f, 5, 20, 0, d, 15);
	zassert_equal(one(&s, false, f, n).act, RRL_ACT_NONE);
	n = put_frame(f, 5, 20, 15, d, 6);
	expect_err(&s, f, n, 3, 5, "6 bytes at offset 15 of 20");
	/* another id or another total in the middle of a record */
	n = put_frame(f, 5, 20, 0, d, 10);
	zassert_equal(one(&s, false, f, n).act, RRL_ACT_NONE);
	n = put_frame(f, 6, 20, 10, d, 10);
	expect_err(&s, f, n, 3, 6, "another id at offset 10");
	n = put_frame(f, 5, 20, 0, d, 10);
	zassert_equal(one(&s, false, f, n).act, RRL_ACT_NONE);
	n = put_frame(f, 5, 21, 10, d, 10);
	expect_err(&s, f, n, 3, 5, "another total at offset 10");
	/* a record that was finished is not continued */
	{
		struct rb rec;

		rb_init(&rec, 1, 0);
		n = put_frame(f, 8, 2, 0, rec.b, 2);
		zassert_equal(one(&s, false, f, n).act, RRL_ACT_PUT);
		n = put_frame(f, 8, 4, 2, d, 2);
		expect_err(&s, f, n, 3, 8, "a piece after the record was stored");
	}
	/* offset 0 with a larger offset field than total */
	n = put_frame(f, 9, 10, 0x4000, d, 4);
	expect_err(&s, f, n, 3, 9, "offset 16384 of 10");
}

ZTEST(ring_relay, test_code_4_total)
{
	struct rrl s;
	uint8_t f[40];
	uint8_t d[8] = { 1, 0, 0, 0, 0, 0, 0, 0 };
	size_t n;
	static const uint16_t bad[] = { 0, 1, 513, 514, 1000, 0x7FFF, 0xFFFF };

	rrl_init(&s);
	(void)hello(&s);
	for (size_t i = 0; i < ARRAY_SIZE(bad); i++) {
		n = put_frame(f, 21, bad[i], 0, d, 2);
		expect_err(&s, f, n, 4, 21, "total out of range");
		/* in the middle of a record too */
		n = put_frame(f, 21, 20, 0, d, 2);
		zassert_equal(one(&s, false, f, n).act, RRL_ACT_NONE);
		n = put_frame(f, 21, bad[i], 2, d, 2);
		expect_err(&s, f, n, 4, 21, "total out of range at offset 2");
	}
	/* 2 and 512 are accepted as totals */
	n = put_frame(f, 21, 2, 0, d, 1);
	zassert_equal(one(&s, false, f, n).act, RRL_ACT_NONE, "total 2, first piece");
	n = put_frame(f, 21, 512, 0, d, 1);
	zassert_equal(one(&s, false, f, n).act, RRL_ACT_NONE, "total 512, first piece");
}

ZTEST(ring_relay, test_code_5_malformed_record)
{
	struct rrl s;
	struct rb r;
	uint8_t f[40];
	size_t n;
	static const uint8_t v5[] = { 0x01, 0x00, 0x05, 0x01, 'a' };        /* type 5 */
	static const uint8_t v0[] = { 0x01, 0x00, 0x00, 0x01, 'a' };        /* type 0 */
	static const uint8_t vff[] = { 0x01, 0x00, 0xFF, 0x00 };            /* type 255 */
	static const uint8_t past[] = { 0x01, 0x00, 0x02, 0x05, 'a', 'b' }; /* length 5, 2 bytes left */
	static const uint8_t rep[] = { 0x01, 0x00, 0x02, 0x01, 'a', 0x02, 0x01, 'b' };
	static const uint8_t rep2[] = { 0x01, 0x00, 0x01, 0x00, 0x03, 0x00, 0x01, 0x00 };
	static const uint8_t nolen[] = { 0x01, 0x00, 0x02 };               /* a type with no length byte */

	rrl_init(&s);
	(void)hello(&s);
	n = put_frame(f, 31, sizeof(v5), 0, v5, sizeof(v5));
	expect_err(&s, f, n, 5, 31, "type 5");
	n = put_frame(f, 31, sizeof(v0), 0, v0, sizeof(v0));
	expect_err(&s, f, n, 5, 31, "type 0");
	n = put_frame(f, 31, sizeof(vff), 0, vff, sizeof(vff));
	expect_err(&s, f, n, 5, 31, "type 255");
	n = put_frame(f, 31, sizeof(past), 0, past, sizeof(past));
	expect_err(&s, f, n, 5, 31, "a field that runs past the end");
	n = put_frame(f, 31, sizeof(rep), 0, rep, sizeof(rep));
	expect_err(&s, f, n, 5, 31, "a repeated type");
	n = put_frame(f, 31, sizeof(rep2), 0, rep2, sizeof(rep2));
	expect_err(&s, f, n, 5, 31, "a repeated type with empty fields");
	n = put_frame(f, 31, sizeof(nolen), 0, nolen, sizeof(nolen));
	expect_err(&s, f, n, 5, 31, "a type with no length byte");
	/* every flag bit above 4 */
	for (int bit = 5; bit < 8; bit++) {
		rb_init(&r, 1, (uint8_t)(1U << bit));
		n = put_frame(f, 31, (uint16_t)r.n, 0, r.b, r.n);
		expect_err(&s, f, n, 5, 31, "a flag bit above 4");
		rb_init(&r, 1, (uint8_t)(0x1F | (1U << bit)));
		n = put_frame(f, 31, (uint16_t)r.n, 0, r.b, r.n);
		expect_err(&s, f, n, 5, 31, "a flag bit above 4 with the others set");
	}
	/* the same refusals when the record comes in pieces of 1 byte: the refusal comes with the last piece */
	{
		struct rrl_res res = put_pieces(&s, 31, past, sizeof(past), 1);

		zassert_equal(res.act, RRL_ACT_ERROR);
		zassert_equal(res.err, 5);
		zassert_equal(res.id, 31);
	}
}

ZTEST(ring_relay, test_code_6_version)
{
	struct rrl s;
	uint8_t f[2];

	rrl_init(&s);
	for (int v = 0; v < 256; v++) {
		struct rrl_res r;

		f[0] = 0x01;
		f[1] = (uint8_t)v;
		r = one(&s, false, f, 2);
		if (v == 1) {
			zassert_equal(r.act, RRL_ACT_HELLO, "version 1 is supported");
			rrl_init(&s);
		} else {
			zassert_equal(r.act, RRL_ACT_ERROR, "version %d refused", v);
			zassert_equal(r.err, 6, "version %d: code 6", v);
			zassert_equal(r.id, 0);
		}
	}
	/* a refused HELLO in a running session leaves the session as it was */
	(void)hello(&s);
	f[1] = 2;
	expect_err(&s, f, 2, 6, 0, "version 2 in a running session");
	f[0] = 0x04;
	zassert_equal(one(&s, false, f, 1).act, RRL_ACT_CLEAR, "the session still runs");
}

static void expect_apple(struct rrl *s, const uint8_t *f, size_t n, uint32_t id, const char *what)
{
	struct rrl_res r = one(s, true, f, n);

	zassert_equal(r.act, RRL_ACT_ERROR, "%s: refused on an Apple link (act %d)", what, r.act);
	zassert_equal(r.err, 7, "%s: code %u, want 7", what, r.err);
	zassert_equal(r.id, id, "%s: id %u, want %u", what, r.id, id);
}

ZTEST(ring_relay, test_code_7_one_source_per_link)
{
	struct rrl s;
	struct rrl before;
	uint8_t f[40];
	struct rb rec;
	size_t n;

	/* every frame on a link whose notifications come from Apple's service: code 7, with or without a session, valid or not */
	for (int pass = 0; pass < 2; pass++) {
		rrl_init(&s);
		if (pass == 1) {
			(void)hello(&s);
		}
		before = s;
		f[0] = 0x01;
		f[1] = 1;
		expect_apple(&s, f, 2, 0, "HELLO");
		f[1] = 2;
		expect_apple(&s, f, 2, 0, "HELLO version 2");
		rb_init(&rec, 1, 0);
		n = put_frame(f, 41, 2, 0, rec.b, rec.n);
		expect_apple(&s, f, n, 41, "PUT");
		n = put_frame(f, 42, 100, 0, rec.b, rec.n);
		expect_apple(&s, f, n, 42, "first piece of a PUT");
		n = id_frame(f, 0x03, 43);
		expect_apple(&s, f, n, 43, "REMOVE");
		f[0] = 0x04;
		expect_apple(&s, f, 1, 0, "CLEAR");
		f[0] = 0x55;
		expect_apple(&s, f, 1, 0, "unknown opcode");
		expect_apple(&s, f, 0, 0, "empty write");
		f[0] = 0x02;
		expect_apple(&s, f, 3, 0, "short PUT");
		/* the refusal changes nothing of the session */
		zassert_mem_equal(&before, &s, sizeof(s), "the session is as it was (pass %d)", pass);
	}
	/* a link that is not Apple's is not refused with 7 */
	rrl_init(&s);
	zassert_equal(hello(&s).act, RRL_ACT_HELLO);
}

/* ------------------------------------------------------------------ the store: refused frames change nothing */

static void three_entries(struct rrl *s, struct rinbox *b)
{
	struct rb r;

	rinbox_init(b);
	rrl_init(s);
	apply(b, &(struct rrl_res){ .act = RRL_ACT_NONE });
	zassert_equal(hello(s).act, RRL_ACT_HELLO);
	rb_init(&r, 1, 0x08);
	rb_str(&r, 1, "app.one");
	rb_str(&r, 2, "One");
	zassert_equal(put_apply(s, b, 101, &r).act, RRL_ACT_PUT);
	rb_init(&r, 2, 0x10);
	rb_str(&r, 2, "Two");
	rb_str(&r, 3, "second");
	zassert_equal(put_apply(s, b, 102, &r).act, RRL_ACT_PUT);
	rb_init(&r, 3, 0x18);
	rb_str(&r, 4, "20261112T101500");
	zassert_equal(put_apply(s, b, 103, &r).act, RRL_ACT_PUT);
	zassert_equal(rinbox_count(b), 3);
}

ZTEST(ring_relay, test_refused_frames_change_nothing)
{
	struct rrl s;
	struct rinbox b;
	uint8_t f[80];
	uint8_t d[40] = { 1, 0 };
	struct rb r;
	size_t n;
	struct rrl_res res;
	int refused = 0;

	three_entries(&s, &b);
	/* a battery of refused frames of every code; each is applied the way an accepted frame is (it must ask for nothing) */
#define TRY(frame_n, code)                                                                                              \
	do {                                                                                                            \
		res = one(&s, false, f, (frame_n));                                                                     \
		zassert_equal(res.act, RRL_ACT_ERROR, "refused: line %d", __LINE__);                                    \
		zassert_equal(res.err, (code), "line %d: code %u", __LINE__, res.err);                                  \
		apply(&b, &res);                                                                                        \
		refused++;                                                                                              \
	} while (0)
	f[0] = 0x7F;
	TRY(3, 1);
	f[0] = 0x01;
	f[1] = 9;
	TRY(2, 6);
	f[0] = 0x04;
	TRY(4, 1);
	f[0] = 0x03;
	TRY(4, 1);
	n = put_frame(f, 101, 10, 4, d, 6); /* an out of order piece for a held id */
	TRY(n, 3);
	n = put_frame(f, 102, 513, 0, d, 2);
	TRY(n, 4);
	n = put_frame(f, 103, 1, 0, d, 1);
	TRY(n, 4);
	/* malformed records for held ids and new ids */
	rb_init(&r, 9, 0x20);
	n = put_frame(f, 101, (uint16_t)r.n, 0, r.b, r.n);
	TRY(n, 5);
	rb_init(&r, 9, 0);
	rb_str(&r, 1, "x");
	rb_str(&r, 1, "y");
	n = put_frame(f, 104, (uint16_t)r.n, 0, r.b, r.n);
	TRY(n, 5);
	rb_init(&r, 9, 0);
	r.b[r.n++] = 3;
	r.b[r.n++] = 200;
	n = put_frame(f, 102, (uint16_t)r.n, 0, r.b, r.n);
	TRY(n, 5);
	rb_init(&r, 9, 0);
	r.b[r.n++] = 6;
	r.b[r.n++] = 0;
	n = put_frame(f, 105, (uint16_t)r.n, 0, r.b, r.n);
	TRY(n, 5);
#undef TRY
	zassert_equal(refused, 11);
	/* what this case proves: every one of these frames is a refusal (act ERROR with its code), so none asks for a change. That the ring then
	 * leaves its store alone is proven by the two-device test, not here: apply() below is the test's own, not the ring's code (the check
	 * "H: the malformed frames changed nothing" with the store digest, and the broken copy refused_frame_changes_store). */
	/* a refusal before HELLO and on an Apple link change nothing either */
	rrl_init(&s);
	n = put_frame(f, 106, 2, 0, d, 2);
	res = one(&s, false, f, n);
	zassert_equal(res.err, 2);
	apply(&b, &res);
	res = one(&s, true, f, n);
	zassert_equal(res.err, 7);
	apply(&b, &res);
}

/* ------------------------------------------------------------------ pieces of every size */

ZTEST(ring_relay, test_pieces_of_every_size)
{
	struct rrl s;
	struct rinbox b;
	struct rb r;

	rb_init(&r, 5, 0x0A);
	rb_str(&r, 1, "com.example.chat");
	rb_str(&r, 3, "A message that is long enough to need many pieces of a small size, and then some more text after it.");
	rb_str(&r, 2, "Title");
	rb_str(&r, 4, "20261112T093000");
	zassert_true(r.n > 130 && r.n < 160, "the record is %zu bytes", r.n);
	/* pieces of 1 byte up to larger than the record (and the largest a piece can be at MTU 247: 235 bytes) */
	for (size_t piece = 1; piece <= r.n + 3; piece++) {
		struct rrl_res res;

		rinbox_init(&b);
		rrl_init(&s);
		(void)hello(&s);
		res = put_pieces(&s, 900, r.b, r.n, piece);
		zassert_equal(res.act, RRL_ACT_PUT, "piece size %zu: stored after the last piece (act %d err %u)", piece, res.act, res.err);
		zassert_equal(res.id, 900);
		apply(&b, &res);
		expect_item(&b, 0, 900, 5, 0x0A, "com.example.chat",
			    "Title", "A message that is long enough to need many pieces of a small size, and then some more text after it.",
			    "20261112T093000");
		zassert_equal(rinbox_count(&b), 1);
	}
	/* a second record right after the first on the same session, pieces of 7 */
	{
		struct rrl_res res = put_pieces(&s, 901, r.b, r.n, 7);

		zassert_equal(res.act, RRL_ACT_PUT);
	}
}

/* a record of exactly 512 bytes: texts longer than their limits, and the largest field sizes */
static void rec_512(struct rb *r)
{
	char a[200], t[100], m[200];

	memset(a, 'A', sizeof(a));
	memset(t, 'T', sizeof(t));
	memset(m, 'M', sizeof(m));
	rb_init(r, 11, 0x1F);
	rb_field(r, 1, a, sizeof(a));       /* 202 */
	rb_field(r, 2, t, sizeof(t));       /* 102 */
	rb_field(r, 3, m, sizeof(m));       /* 202 */
	rb_field(r, 4, "20", 2);            /* 4 */
}

ZTEST(ring_relay, test_record_of_2_and_512_and_513)
{
	struct rrl s;
	struct rinbox b;
	struct rb r;
	struct rrl_res res;
	uint8_t f[20];
	uint8_t d[4] = { 1, 0, 0, 0 };
	size_t n;
	char want_a[49], want_t[49], want_m[161];

	rinbox_init(&b);
	rrl_init(&s);
	(void)hello(&s);
	/* exactly 2 bytes: category and flags, every text empty */
	rb_init(&r, 3, 0x03);
	zassert_equal(r.n, 2);
	res = put_apply(&s, &b, 1, &r);
	zassert_equal(res.act, RRL_ACT_PUT, "a record of exactly 2 bytes is stored");
	expect_item(&b, 0, 1, 3, 0x03, "", "", "", "");
	/* and in two pieces of 1 byte */
	res = put_pieces(&s, 2, r.b, r.n, 1);
	zassert_equal(res.act, RRL_ACT_PUT);
	/* 1 byte and 0 bytes: code 4 */
	n = put_frame(f, 3, 1, 0, d, 1);
	expect_err(&s, f, n, 4, 3, "a record of 1 byte");
	n = put_frame(f, 3, 0, 0, d, 1);
	expect_err(&s, f, n, 4, 3, "a record of 0 bytes");
	/* exactly 512 bytes, in pieces of every size from 1 byte to larger than the record (1 to 520) */
	rec_512(&r);
	zassert_equal(r.n, 512, "the large record is %zu bytes", r.n);
	memset(want_a, 'A', 48);
	want_a[48] = 0;
	memset(want_t, 'T', 48);
	want_t[48] = 0;
	memset(want_m, 'M', 160);
	want_m[160] = 0;
	for (size_t piece = 1; piece <= 520; piece++) {
		rinbox_init(&b);
		(void)hello(&s);
		res = put_pieces(&s, 512, r.b, r.n, piece);
		zassert_equal(res.act, RRL_ACT_PUT, "512 bytes in pieces of %zu: stored", piece);
		apply(&b, &res);
		expect_item(&b, 0, 512, 11, 0x1F, want_a, want_t, want_m, "20");
		zassert_equal(strlen(b.items[0].app), 48);
		zassert_equal(strlen(b.items[0].title), 48);
		zassert_equal(strlen(b.items[0].msg), 160);
	}
	/* 513: refused with code 4 with its first piece, whatever the piece size */
	{
		uint8_t big[513];

		memset(big, 0, sizeof(big));
		big[0] = 1;
		(void)hello(&s);
		n = put_frame(f, 513, 513, 0, big, 11);
		expect_err(&s, f, n, 4, 513, "513 bytes, first piece");
		n = put_frame(f, 513, 513, 0, big, 1);
		expect_err(&s, f, n, 4, 513, "513 bytes, a piece of 1 byte");
	}
	/* the store did not take the refused ones */
	zassert_equal(rinbox_count(&b), 1);
	zassert_equal(b.items[0].uid, 512);
}

/* ------------------------------------------------------------------ every truncation of a valid record */

ZTEST(ring_relay, test_every_truncation_of_a_valid_record)
{
	struct rb v;
	struct rrl s;
	/* the record ends exactly at a field boundary only at these lengths (2 = no field, then after each of the four fields) */
	static const size_t ok_at[] = { 2, 20, 27, 42, 59 };
	size_t ok = 0, code4 = 0, code5 = 0;

	rec_base(&v);
	zassert_equal(v.n, 59);
	for (size_t k = 0; k <= v.n; k++) {
		uint8_t f[9 + 80];
		struct rrl_res res;
		size_t n;
		bool boundary = false;

		for (size_t i = 0; i < ARRAY_SIZE(ok_at); i++) {
			boundary = boundary || (ok_at[i] == k);
		}
		rrl_init(&s);
		(void)hello(&s);
		/* the whole truncated record in one piece; with k = 0 the frame has no data byte, so a single byte is sent for the total of 0 */
		n = put_frame(f, 60, (uint16_t)k, 0, v.b, k == 0 ? 1 : k);
		res = one(&s, false, f, n);
		if (k < 2) {
			zassert_equal(res.act, RRL_ACT_ERROR, "truncated to %zu bytes: refused", k);
			zassert_equal(res.err, 4, "truncated to %zu bytes: code 4", k);
			code4++;
		} else if (boundary) {
			struct rinbox b;

			zassert_equal(res.act, RRL_ACT_PUT, "truncated at the field boundary %zu: stored as a shorter record", k);
			rinbox_init(&b);
			apply(&b, &res);
			zassert_equal(b.items[0].category, 4);
			zassert_equal(b.items[0].flags, 0x18);
			zassert_str_equal(b.items[0].app, k >= 20 ? "com.example.mail" : "");
			zassert_str_equal(b.items[0].title, k >= 27 ? "Hello" : "");
			zassert_str_equal(b.items[0].msg, k >= 42 ? "First message" : "");
			zassert_str_equal(b.items[0].date, k >= 59 ? "20261112T101500" : "");
			ok++;
		} else {
			zassert_equal(res.act, RRL_ACT_ERROR, "truncated to %zu bytes (inside a field): refused", k);
			zassert_equal(res.err, 5, "truncated to %zu bytes: code 5", k);
			zassert_equal(res.id, 60);
			code5++;
		}
		/* the same cut record sent in pieces of 1 byte gives the same result */
		if (k >= 2) {
			rrl_init(&s);
			(void)hello(&s);
			res = put_pieces(&s, 61, v.b, k, 1);
			zassert_equal(res.act, boundary ? RRL_ACT_PUT : RRL_ACT_ERROR, "pieces of 1 byte, cut at %zu", k);
			zassert_equal(res.err, boundary ? 0 : 5);
		}
	}
	zassert_equal(ok, 5, "five lengths are valid");
	zassert_equal(code4, 2, "lengths 0 and 1");
	zassert_equal(code5, 59 + 1 - 2 - 5, "every other length");

	/* a record that is cut in transit (the pieces stop) is never stored, and the next HELLO drops it */
	for (size_t piece = 1; piece < 20; piece += 3) {
		struct rrl_res res;
		size_t sent = 0;

		rrl_init(&s);
		(void)hello(&s);
		while (sent + piece < v.n) {
			uint8_t f[9 + 60];
			size_t n = put_frame(f, 62, (uint16_t)v.n, (uint16_t)sent, &v.b[sent], piece);

			res = one(&s, false, f, n);
			zassert_equal(res.act, RRL_ACT_NONE, "an unfinished record asks for nothing (piece %zu, sent %zu)", piece, sent);
			sent += piece;
		}
		/* a HELLO drops it: the next piece is out of order */
		(void)hello(&s);
		{
			uint8_t f[9 + 60];
			size_t n = put_frame(f, 62, (uint16_t)v.n, (uint16_t)sent, &v.b[sent], v.n - sent);

			res = one(&s, false, f, n);
			zassert_equal(res.act, RRL_ACT_ERROR);
			zassert_equal(res.err, 3, "after a new HELLO the old record is gone");
		}
	}
}

/* the same sweep on a record of 512 bytes (field boundaries at 2, 204, 306, 508, 512) */
ZTEST(ring_relay, test_every_truncation_of_the_largest_record)
{
	struct rb v;
	struct rrl s;
	static const size_t ok_at[] = { 2, 204, 306, 508, 512 };

	rec_512(&v);
	zassert_equal(v.n, 512);
	for (size_t k = 2; k <= v.n; k++) {
		uint8_t f[9 + 512];
		struct rrl_res res;
		bool boundary = false;
		size_t n;

		for (size_t i = 0; i < ARRAY_SIZE(ok_at); i++) {
			boundary = boundary || (ok_at[i] == k);
		}
		rrl_init(&s);
		(void)hello(&s);
		n = put_frame(f, 70, (uint16_t)k, 0, v.b, k);
		res = one(&s, false, f, n);
		zassert_equal(res.act, boundary ? RRL_ACT_PUT : RRL_ACT_ERROR, "cut at %zu", k);
		zassert_equal(res.err, boundary ? 0 : 5, "cut at %zu: code", k);
	}
}

/* a record that is not stored before its last piece (the first pieces never store, whatever their size) */
ZTEST(ring_relay, test_put_not_stored_before_its_last_piece)
{
	struct rb v;
	struct rrl s;
	struct rinbox b;

	rec_base(&v);
	for (size_t piece = 1; piece < v.n; piece++) {
		size_t sent = 0;

		rinbox_init(&b);
		rrl_init(&s);
		(void)hello(&s);
		while (sent + piece < v.n) {
			uint8_t f[9 + 80];
			size_t n = put_frame(f, 80, (uint16_t)v.n, (uint16_t)sent, &v.b[sent], piece);
			struct rrl_res res = one(&s, false, f, n);

			zassert_equal(res.act, RRL_ACT_NONE, "piece of %zu bytes at %zu of %zu", piece, sent, v.n);
			/* what this case proves: no piece before the last one asks for a store (act NONE). That the ring then stores nothing before the last
			 * piece is proven by the two-device test (ring check "H: two more pieces were taken, nothing was stored" with the store digest, and
			 * the copy put_early), not here: apply() is the test's own code. */
			(void)b;
			sent += piece;
		}
	}
}

/* ------------------------------------------------------------------ texts */

ZTEST(ring_relay, test_texts_cut_at_a_character)
{
	struct rrl s;
	struct rinbox b;
	struct rb r;
	char t[200];
	char want[200];
	int k;

	rinbox_init(&b);
	rrl_init(&s);
	(void)hello(&s);
	/* title: 20 euro signs (3 bytes each, 60 bytes): limit 48 = 16 characters exactly */
	/* message: 100 e-acute (2 bytes each, 200 bytes): limit 160 = 80 characters exactly */
	rb_init(&r, 1, 0);
	for (k = 0; k < 20; k++) {
		memcpy(&t[3 * k], "\xE2\x82\xAC", 3);
	}
	rb_field(&r, 2, t, 60);
	for (k = 0; k < 100; k++) {
		memcpy(&t[2 * k], "\xC3\xA9", 2);
	}
	rb_field(&r, 3, t, 200);
	zassert_equal(put_apply(&s, &b, 1, &r).act, RRL_ACT_PUT);
	for (k = 0; k < 16; k++) {
		memcpy(&want[3 * k], "\xE2\x82\xAC", 3);
	}
	want[48] = 0;
	zassert_str_equal(b.items[0].title, want, "16 euro signs, 48 bytes");
	for (k = 0; k < 80; k++) {
		memcpy(&want[2 * k], "\xC3\xA9", 2);
	}
	want[160] = 0;
	zassert_str_equal(b.items[0].msg, want, "80 e-acute, 160 bytes");

	/* the limit falls inside a character: 47 letters then a 3-byte character (50 bytes): cut at 47 */
	rb_init(&r, 1, 0);
	memset(t, 'a', 47);
	memcpy(&t[47], "\xE2\x82\xAC", 3);
	rb_field(&r, 1, t, 50);
	/* inside a 4-byte character: 46 letters then two 4-byte characters (54 bytes): the first ends at 50, past the limit 48: cut at 46 */
	memset(t, 'b', 46);
	memcpy(&t[46], "\xF0\x9F\x98\x80\xF0\x9F\x98\x80", 8);
	rb_field(&r, 2, t, 54);
	zassert_equal(put_apply(&s, &b, 2, &r).act, RRL_ACT_PUT);
	memset(want, 'a', 47);
	want[47] = 0;
	zassert_str_equal(b.items[0].app, want, "cut at 47, before the 3-byte character");
	zassert_equal(strlen(b.items[0].app), 47);
	memset(want, 'b', 46);
	want[46] = 0;
	zassert_str_equal(b.items[0].title, want, "cut at 46, before the 4-byte character");
	/* 4-byte characters over the message limit: 50 of them (200 bytes): limit 160 = 40 characters */
	rb_init(&r, 1, 0);
	for (k = 0; k < 50; k++) {
		memcpy(&t[4 * k], "\xF0\x9F\x98\x80", 4);
	}
	rb_field(&r, 3, t, 200);
	zassert_equal(put_apply(&s, &b, 3, &r).act, RRL_ACT_PUT);
	zassert_equal(strlen(b.items[0].msg), 160, "40 four-byte characters");
	for (k = 0; k < 40; k++) {
		zassert_mem_equal(&b.items[0].msg[4 * k], "\xF0\x9F\x98\x80", 4);
	}
	/* a 3-byte character cut by a limit that falls after its first byte: 48 + ... title of 16 euro signs + 1 more byte of the 17th */
	rb_init(&r, 1, 0);
	for (k = 0; k < 16; k++) {
		memcpy(&t[3 * k], "\xE2\x82\xAC", 3);
	}
	t[48] = (char)0xE2;
	rb_field(&r, 2, t, 49);
	zassert_equal(put_apply(&s, &b, 4, &r).act, RRL_ACT_PUT);
	zassert_equal(strlen(b.items[0].title), 48, "16 whole characters, the stray lead byte is not kept");
	/* the helper cut a character itself: the text ends with the first two bytes of a 3-byte character */
	rb_init(&r, 1, 0);
	rb_field(&r, 2, "ab\xE2\x82", 4);
	zassert_equal(put_apply(&s, &b, 5, &r).act, RRL_ACT_PUT);
	zassert_str_equal(b.items[0].title, "ab", "an incomplete character at the end is dropped");
	/* the date: 15 characters */
	rb_init(&r, 1, 0);
	rb_str(&r, 4, "20261112T1015001234567890");
	zassert_equal(put_apply(&s, &b, 6, &r).act, RRL_ACT_PUT);
	zassert_str_equal(b.items[0].date, "20261112T101500", "the date is cut at 15");
}

/* ------------------------------------------------------------------ flags and fields */

ZTEST(ring_relay, test_flags_and_category)
{
	struct rrl s;
	struct rinbox b;
	struct rb r;

	rinbox_init(&b);
	rrl_init(&s);
	(void)hello(&s);
	for (int fl = 0; fl < 256; fl++) {
		struct rrl_res res;

		rb_init(&r, 2, (uint8_t)fl);
		res = put_pieces(&s, 1, r.b, r.n, r.n);
		if (fl <= 0x1F) {
			zassert_equal(res.act, RRL_ACT_PUT, "flags 0x%02x are valid", fl);
			apply(&b, &res);
			zassert_equal(b.items[0].flags, fl, "flags 0x%02x stored as sent", fl);
		} else {
			zassert_equal(res.act, RRL_ACT_ERROR, "flags 0x%02x: a bit above 4 is set", fl);
			zassert_equal(res.err, 5);
		}
	}
	/* every category value 0 to 255 is stored as received, never refused (section 7.7: the ring does not read the category); the store is
	 * the real ring_inbox code (rinbox_upsert) */
	for (int c = 0; c <= 255; c++) {
		struct rrl_res res;

		rb_init(&r, (uint8_t)c, 0);
		res = put_pieces(&s, 2, r.b, r.n, r.n);
		zassert_equal(res.act, RRL_ACT_PUT, "category %d is not refused", c);
		apply(&b, &res);
		zassert_equal(b.items[0].category, c, "category %d stored as received", c);
	}
}

ZTEST(ring_relay, test_fields_in_any_order_each_once)
{
	static const uint8_t perms[24][4] = {
		{ 1, 2, 3, 4 }, { 1, 2, 4, 3 }, { 1, 3, 2, 4 }, { 1, 3, 4, 2 }, { 1, 4, 2, 3 }, { 1, 4, 3, 2 },
		{ 2, 1, 3, 4 }, { 2, 1, 4, 3 }, { 2, 3, 1, 4 }, { 2, 3, 4, 1 }, { 2, 4, 1, 3 }, { 2, 4, 3, 1 },
		{ 3, 1, 2, 4 }, { 3, 1, 4, 2 }, { 3, 2, 1, 4 }, { 3, 2, 4, 1 }, { 3, 4, 1, 2 }, { 3, 4, 2, 1 },
		{ 4, 1, 2, 3 }, { 4, 1, 3, 2 }, { 4, 2, 1, 3 }, { 4, 2, 3, 1 }, { 4, 3, 1, 2 }, { 4, 3, 2, 1 },
	};
	static const char *const txt[5] = { "", "app.x", "Ti", "Message text", "20260101T000000" };

	for (int p = 0; p < 24; p++) {
		struct rrl s;
		struct rinbox b;
		struct rb r;

		rinbox_init(&b);
		rrl_init(&s);
		(void)hello(&s);
		rb_init(&r, 6, 0x04);
		for (int i = 0; i < 4; i++) {
			rb_str(&r, perms[p][i], txt[perms[p][i]]);
		}
		zassert_equal(put_apply(&s, &b, 1, &r).act, RRL_ACT_PUT, "order %d", p);
		expect_item(&b, 0, 1, 6, 0x04, "app.x", "Ti", "Message text", "20260101T000000");
	}
	/* a missing field is empty: each field left out in turn, and none */
	for (int skip = 0; skip <= 4; skip++) {
		struct rrl s;
		struct rinbox b;
		struct rb r;

		rinbox_init(&b);
		rrl_init(&s);
		(void)hello(&s);
		rb_init(&r, 6, 0);
		for (int t = 1; t <= 4; t++) {
			if (t != skip) {
				rb_str(&r, (uint8_t)t, txt[t]);
			}
		}
		zassert_equal(put_apply(&s, &b, 1, &r).act, RRL_ACT_PUT, "field %d left out", skip);
		expect_item(&b, 0, 1, 6, 0, skip == 1 ? "" : "app.x", skip == 2 ? "" : "Ti", skip == 3 ? "" : "Message text",
			    skip == 4 ? "" : "20260101T000000");
	}
	/* a field of length 0 is allowed; a type twice is not, even when one is empty */
	{
		struct rrl s;
		struct rb r;
		struct rrl_res res;

		rrl_init(&s);
		(void)hello(&s);
		rb_init(&r, 6, 0);
		rb_field(&r, 3, "", 0);
		zassert_equal(put_pieces(&s, 1, r.b, r.n, r.n).act, RRL_ACT_PUT);
		rb_field(&r, 3, "x", 1);
		res = put_pieces(&s, 1, r.b, r.n, r.n);
		zassert_equal(res.act, RRL_ACT_ERROR);
		zassert_equal(res.err, 5);
	}
}

/* ------------------------------------------------------------------ the store: replace, order, 17th, remove, clear */

ZTEST(ring_relay, test_replace_keeps_place_and_read_mark)
{
	struct rrl s;
	struct rinbox b;
	struct rb r;

	rinbox_init(&b);
	rrl_init(&s);
	(void)hello(&s);
	for (uint32_t id = 1; id <= 3; id++) {
		char title[8];

		rb_init(&r, 1, 0x10);
		snprintf(title, sizeof(title), "T%u", id);
		rb_str(&r, 2, title);
		zassert_equal(put_apply(&s, &b, id, &r).act, RRL_ACT_PUT);
	}
	/* newest first: 3, 2, 1 */
	expect_item(&b, 0, 3, 1, 0x10, "", "T3", "", "");
	expect_item(&b, 1, 2, 1, 0x10, "", "T2", "", "");
	expect_item(&b, 2, 1, 1, 0x10, "", "T1", "", "");
	zassert_equal(rinbox_mark_read(&b, 2), 0);
	zassert_equal(rinbox_mark_read(&b, 1), 0);
	/* replace the middle one: new category, flags and text; the place and the read mark stay */
	rb_init(&r, 7, 0x08);
	rb_str(&r, 1, "app.new");
	rb_str(&r, 2, "T2 new");
	rb_str(&r, 3, "body");
	zassert_equal(put_apply(&s, &b, 2, &r).act, RRL_ACT_PUT);
	zassert_equal(rinbox_count(&b), 3, "a replace adds no entry");
	expect_item(&b, 0, 3, 1, 0x10, "", "T3", "", "");
	expect_item(&b, 1, 2, 7, 0x08, "app.new", "T2 new", "body", "");
	expect_item(&b, 2, 1, 1, 0x10, "", "T1", "", "");
	zassert_true(b.items[1].read, "the read mark of 2 stays");
	zassert_false(b.items[0].read, "3 was never read");
	zassert_true(b.items[2].read, "the read mark of 1 stays");
	/* replace the oldest: it stays the oldest */
	rb_init(&r, 1, 0);
	rb_str(&r, 2, "T1 again");
	zassert_equal(put_apply(&s, &b, 1, &r).act, RRL_ACT_PUT);
	expect_item(&b, 2, 1, 1, 0, "", "T1 again", "", "");
	zassert_true(b.items[2].read);
	/* replace the newest */
	rb_init(&r, 1, 0);
	rb_str(&r, 2, "T3 again");
	zassert_equal(put_apply(&s, &b, 3, &r).act, RRL_ACT_PUT);
	expect_item(&b, 0, 3, 1, 0, "", "T3 again", "", "");
	/* a fields that is missing in the replace is empty again (the text is replaced as a whole) */
	expect_item(&b, 1, 2, 7, 0x08, "app.new", "T2 new", "body", "");
	/* a new id goes to the front, unread */
	rb_init(&r, 1, 0);
	zassert_equal(put_apply(&s, &b, 4, &r).act, RRL_ACT_PUT);
	zassert_equal(b.items[0].uid, 4);
	zassert_false(b.items[0].read);
	zassert_equal(b.items[1].uid, 3);
	zassert_equal(rinbox_count(&b), 4);
}

ZTEST(ring_relay, test_the_17th_pushes_the_oldest_out)
{
	struct rrl s;
	struct rinbox b;
	struct rb r;

	rinbox_init(&b);
	rrl_init(&s);
	(void)hello(&s);
	for (uint32_t id = 1; id <= 16; id++) {
		rb_init(&r, 1, 0);
		zassert_equal(put_apply(&s, &b, id, &r).act, RRL_ACT_PUT);
	}
	zassert_equal(rinbox_count(&b), 16);
	zassert_equal(b.items[0].uid, 16);
	zassert_equal(b.items[15].uid, 1);
	/* a replace in a full store pushes nothing out */
	rb_init(&r, 2, 0);
	zassert_equal(put_apply(&s, &b, 5, &r).act, RRL_ACT_PUT);
	zassert_equal(rinbox_count(&b), 16);
	zassert_equal(b.items[15].uid, 1, "a replace in a full store drops nobody");
	/* the 17th */
	rb_init(&r, 1, 0);
	zassert_equal(put_apply(&s, &b, 17, &r).act, RRL_ACT_PUT);
	zassert_equal(rinbox_count(&b), 16, "still 16");
	zassert_equal(b.items[0].uid, 17);
	zassert_equal(b.items[15].uid, 2, "id 1 was pushed out");
	zassert_equal(rinbox_find(&b, 1), -1);
	/* and the 18th pushes out id 2 */
	zassert_equal(put_apply(&s, &b, 18, &r).act, RRL_ACT_PUT);
	zassert_equal(b.items[15].uid, 3);
	zassert_equal(rinbox_find(&b, 2), -1);
	zassert_equal(rinbox_count(&b), 16);
}

ZTEST(ring_relay, test_remove_clear_and_hello_empty_the_store)
{
	struct rrl s;
	struct rinbox b, before;
	struct rb r;
	uint8_t f[8];
	size_t n;
	struct rrl_res res;

	three_entries(&s, &b);
	/* REMOVE of the middle entry */
	n = id_frame(f, 0x03, 102);
	res = one(&s, false, f, n);
	zassert_equal(res.act, RRL_ACT_REMOVE);
	apply(&b, &res);
	zassert_equal(rinbox_count(&b), 2);
	zassert_equal(b.items[0].uid, 103);
	zassert_equal(b.items[1].uid, 101);
	/* REMOVE of an id that is not held: accepted, nothing changes */
	before = b;
	n = id_frame(f, 0x03, 999);
	res = one(&s, false, f, n);
	zassert_equal(res.act, RRL_ACT_REMOVE, "an unknown id is not a refusal");
	apply(&b, &res);
	zassert_mem_equal(&before, &b, sizeof(b));
	/* CLEAR */
	f[0] = 0x04;
	res = one(&s, false, f, 1);
	zassert_equal(res.act, RRL_ACT_CLEAR);
	/* CLEAR and HELLO ask the ring to empty the store (act CLEAR, act HELLO). That the ring then empties it is proven by the two-device test
	 * (checks "H: CLEAR emptied the store" and "H: the store holds 2003, 2002, 2001 (HELLO emptied what was there)", broken copy
	 * hello_keeps_store), not here: apply() is the test's own code. */
	zassert_equal(hello(&s).act, RRL_ACT_HELLO);
	(void)r;
}

ZTEST(ring_relay, test_a_new_record_at_offset_0_drops_the_unfinished_one)
{
	struct rrl s;
	struct rinbox b;
	struct rb a, c;
	struct rrl_res res;
	uint8_t f[9 + 100];
	size_t n;

	rinbox_init(&b);
	rrl_init(&s);
	(void)hello(&s);
	rb_init(&a, 1, 0);
	rb_str(&a, 2, "first record, never finished");
	rb_init(&c, 2, 0);
	rb_str(&c, 2, "second");
	/* the first piece of the first record, then offset 0 of another id */
	n = put_frame(f, 10, (uint16_t)a.n, 0, a.b, 10);
	zassert_equal(one(&s, false, f, n).act, RRL_ACT_NONE);
	res = put_pieces(&s, 11, c.b, c.n, 4);
	zassert_equal(res.act, RRL_ACT_PUT);
	zassert_equal(res.id, 11);
	apply(&b, &res);
	/* the rest of the first record is out of order now */
	n = put_frame(f, 10, (uint16_t)a.n, 10, &a.b[10], a.n - 10);
	expect_err(&s, f, n, 3, 10, "the rest of a dropped record");
	zassert_equal(rinbox_count(&b), 1);
	zassert_equal(b.items[0].uid, 11);
	/* the same id again at offset 0 also starts over */
	n = put_frame(f, 12, (uint16_t)a.n, 0, a.b, 10);
	zassert_equal(one(&s, false, f, n).act, RRL_ACT_NONE);
	n = put_frame(f, 12, (uint16_t)a.n, 0, a.b, 10);
	zassert_equal(one(&s, false, f, n).act, RRL_ACT_NONE);
	n = put_frame(f, 12, (uint16_t)a.n, 10, &a.b[10], a.n - 10);
	zassert_equal(one(&s, false, f, n).act, RRL_ACT_PUT, "a restart at offset 0 begins a new record");
}

/* The worked example of the helper specification (design/software/os/android-helper-example.py): the same bytes, written out here as literals.
 * One record of 62 bytes for the id 0x000100a5 (category 4, flags 0x12, 'com.example.chat', 'Anna', 'Lunch at 12? ' and a bowl of noodles,
 * 17 bytes, '20261112T191500'), as six PUT frames at a write value of 20 bytes and as one frame at 244. */
ZTEST(ring_relay, test_helper_example_bytes)
{
	static const uint8_t info[6] = { 0x01, 0x10, 0x30, 0x30, 0xa0, 0x0f };
	static const uint8_t hello_f[2] = { 0x01, 0x01 };
	static const uint8_t ready[3] = { 0x81, 0x01, 0x10 };
	static const uint8_t f20[6][20] = {
		{ 0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x00, 0x00, 0x04, 0x12, 0x01, 0x10, 0x63, 0x6f, 0x6d, 0x2e, 0x65, 0x78, 0x61 },
		{ 0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x0b, 0x00, 0x6d, 0x70, 0x6c, 0x65, 0x2e, 0x63, 0x68, 0x61, 0x74, 0x02, 0x04 },
		{ 0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x16, 0x00, 0x41, 0x6e, 0x6e, 0x61, 0x03, 0x11, 0x4c, 0x75, 0x6e, 0x63, 0x68 },
		{ 0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x21, 0x00, 0x20, 0x61, 0x74, 0x20, 0x31, 0x32, 0x3f, 0x20, 0xf0, 0x9f, 0x8d },
		{ 0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x2c, 0x00, 0x9c, 0x04, 0x0f, 0x32, 0x30, 0x32, 0x36, 0x31, 0x31, 0x31, 0x32 },
		{ 0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x37, 0x00, 0x54, 0x31, 0x39, 0x31, 0x35, 0x30, 0x30 },
	};
	static const uint8_t f244[71] = {
		0x02, 0xa5, 0x00, 0x01, 0x00, 0x3e, 0x00, 0x00, 0x00, 0x04, 0x12, 0x01, 0x10, 0x63, 0x6f, 0x6d, 0x2e, 0x65, 0x78, 0x61, 0x6d, 0x70,
		0x6c, 0x65, 0x2e, 0x63, 0x68, 0x61, 0x74, 0x02, 0x04, 0x41, 0x6e, 0x6e, 0x61, 0x03, 0x11, 0x4c, 0x75, 0x6e, 0x63, 0x68, 0x20, 0x61,
		0x74, 0x20, 0x31, 0x32, 0x3f, 0x20, 0xf0, 0x9f, 0x8d, 0x9c, 0x04, 0x0f, 0x32, 0x30, 0x32, 0x36, 0x31, 0x31, 0x31, 0x32, 0x54, 0x31,
		0x39, 0x31, 0x35, 0x30, 0x30,
	};
	static const uint8_t remove[5] = { 0x03, 0xa5, 0x00, 0x01, 0x00 };
	static const uint8_t action_neg[6] = { 0x82, 0xa5, 0x00, 0x01, 0x00, 0x01 };
	static const uint8_t action_pos[6] = { 0x82, 0xa5, 0x00, 0x01, 0x00, 0x00 };
	static const uint8_t err2[6] = { 0x83, 0x02, 0x00, 0x00, 0x00, 0x00 };
	static const uint8_t clear[1] = { 0x04 };
	static const size_t f20_len[6] = { 20, 20, 20, 20, 20, 16 };
	uint8_t o[8];
	struct rrl s;
	struct rinbox b;
	struct rrl_res res;

	rrl_init(&s);
	rinbox_init(&b);
	zassert_equal(rrl_info(o), 6);
	zassert_mem_equal(o, info, 6);
	zassert_equal(hello(&s).act, RRL_ACT_HELLO);
	zassert_equal(one(&s, false, hello_f, 2).act, RRL_ACT_HELLO);
	zassert_equal(rrl_out_ready(o), 3);
	zassert_mem_equal(o, ready, 3);
	/* six frames of the example: five taken, the sixth stores */
	for (int i = 0; i < 6; i++) {
		res = one(&s, false, f20[i], f20_len[i]);
		zassert_equal(res.act, i < 5 ? RRL_ACT_NONE : RRL_ACT_PUT, "frame %d", i + 1);
	}
	zassert_equal(res.id, 0x000100a5);
	apply(&b, &res);
	expect_item(&b, 0, 0x000100a5, 4, 0x12, "com.example.chat", "Anna", "Lunch at 12? \xF0\x9F\x8D\x9C", "20261112T191500");
	/* REMOVE, and the same record again as one frame of 71 bytes */
	res = one(&s, false, remove, 5);
	zassert_equal(res.act, RRL_ACT_REMOVE);
	zassert_equal(res.id, 0x000100a5);
	apply(&b, &res);
	zassert_equal(rinbox_count(&b), 0);
	res = one(&s, false, f244, sizeof(f244));
	zassert_equal(res.act, RRL_ACT_PUT);
	apply(&b, &res);
	expect_item(&b, 0, 0x000100a5, 4, 0x12, "com.example.chat", "Anna", "Lunch at 12? \xF0\x9F\x8D\x9C", "20261112T191500");
	/* CLEAR at any time in the session */
	res = one(&s, false, clear, 1);
	zassert_equal(res.act, RRL_ACT_CLEAR);
	/* the frames of the ring */
	zassert_equal(rrl_out_action(o, 0x000100a5, RRL_ACTION_NEGATIVE), 6);
	zassert_mem_equal(o, action_neg, 6);
	zassert_equal(rrl_out_action(o, 0x000100a5, RRL_ACTION_POSITIVE), 6);
	zassert_mem_equal(o, action_pos, 6);
	zassert_equal(rrl_out_error(o, RRL_E_NO_HELLO, 0), 6);
	zassert_mem_equal(o, err2, 6);
	/* the date is stored as received: a date that is not a date is kept, and a long one is cut at 15 characters */
	rrl_init(&s);
	rinbox_init(&b);
	(void)hello(&s);
	{
		struct rb r;

		rb_init(&r, 1, 0);
		rb_str(&r, 4, "not a date at all");
		res = put_pieces(&s, 7, r.b, r.n, 20);
		zassert_equal(res.act, RRL_ACT_PUT);
		apply(&b, &res);
		zassert_str_equal(b.items[0].date, "not a date at a");
	}
}
