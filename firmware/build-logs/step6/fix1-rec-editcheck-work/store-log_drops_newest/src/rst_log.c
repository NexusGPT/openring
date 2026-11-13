/*
 * rst_log.c: the logic that works on what is on the card (pure: stdint, stdbool, string and the formats of rst_fmt.c;
 * the card is reached through a read callback). Written for this project.
 */
#include <errno.h>
#include <string.h>

#include "rst_layout.h"
#include "rst_log.h"

/* ------------------------------------------------------------------ superblock choice */

int rst_log_pick_sb(const uint8_t *copy_a, const uint8_t *copy_b, struct rst_sb *out, int *which)
{
	struct rst_sb a, b;
	bool va = rst_fmt_sb_decode(copy_a, &a) == 0;
	bool vb = rst_fmt_sb_decode(copy_b, &b) == 0;

	if (!va && !vb) {
		return -ENOENT;
	}
	if (va && (!vb || a.sb_seq > b.sb_seq)) {
		*out = a;
		*which = 0;
	} else {
		*out = b;
		*which = 1;
	}
	return 0;
}

/* ------------------------------------------------------------------ recordings */

static void rec_from_ix(struct rst_rec *r, const struct rst_ix *x)
{
	memset(r, 0, sizeof(*r));
	r->info.recording_id = x->recording_id;
	r->info.type = x->recording_type;
	r->info.channels = x->channels;
	r->info.first_chunk_seq = x->first_chunk_seq;
	r->info.chunk_count = x->chunk_count;
	r->info.sample_rate_hz = x->sample_rate_hz;
	r->info.start_utc_ms = x->start_utc_ms;
	r->info.duration_frames = x->duration_frames;
	r->info.digest = x->digest;
	r->info.highlight_count = x->highlight_count;
	r->close_state = x->close_state;
	r->confirmed = false;
	r->info.state = x->close_state == RREC_IX_CLOSE_RECOVERED ? RREC_LIST_STATE_RECOVERED : RREC_LIST_STATE_NEW;
}

static void rec_confirm(struct rst_rec *r)
{
	r->confirmed = true;
	r->info.state = RREC_LIST_STATE_TRANSFERRED;
}

void rst_recs_init(struct rst_recs *t, struct rst_rec *store, uint32_t cap)
{
	memset(t, 0, sizeof(*t));
	t->ent = store;
	t->cap = cap;
}

struct rst_rec *rst_recs_find(struct rst_recs *t, uint32_t id)
{
	for (uint32_t i = 0; i < t->n; i++) {
		if (t->ent[i].info.recording_id == id) {
			return &t->ent[i];
		}
	}
	return NULL;
}

void rst_recs_apply(struct rst_recs *t, const struct rst_ix *x)
{
	struct rst_rec *r;

	switch (x->type) {
	case RREC_IX_TYPE_CLOSE:
		if (t->first_id == 0) {
			t->first_id = x->recording_id;
		}
		if (x->recording_id < t->first_id || rst_recs_find(t, x->recording_id) != NULL) {
			return;       /* a record this table already has or has seen the end of */
		}
		if (t->n == t->cap) {
			t->evict_max_id = t->ent[0].info.recording_id;
			memmove(&t->ent[0], &t->ent[1], (t->n - 1) * sizeof(t->ent[0]));
			t->n--;
		}
		rec_from_ix(&t->ent[t->n++], x);
		t->live_total++;
		break;
	case RREC_IX_TYPE_CONFIRM:
		r = rst_recs_find(t, x->recording_id);
		if (r != NULL) {
			rec_confirm(r);
		}
		break;
	case RREC_IX_TYPE_DELETE:
		r = rst_recs_find(t, x->recording_id);
		if (r != NULL) {
			uint32_t i = (uint32_t)(r - t->ent);

			memmove(&t->ent[i], &t->ent[i + 1], (t->n - i - 1) * sizeof(t->ent[0]));
			t->n--;
			t->live_total--;
		} else if (t->first_id != 0 && x->recording_id >= t->first_id && x->recording_id <= t->evict_max_id &&
			   t->live_total > 0) {
			t->live_total--;       /* a live recording that was pushed out of the table */
		}
		break;
	default:
		break;
	}
}

static int read_ix(rst_rd_fn rd, void *ctx, uint32_t n, struct rst_ix *x, uint8_t *sector)
{
	int r = rd(ctx, rst_lay_index_lba(n), sector, 1);

	if (r != 0) {
		return -EIO;
	}
	if (rst_fmt_ix_decode(sector, x) != 0 || x->record_number != n) {
		return -EBADMSG;
	}
	return 0;
}

int rst_log_load_index(rst_rd_fn rd, void *ctx, uint32_t tail, uint32_t head, struct rst_recs *t, uint8_t *sector)
{
	struct rst_ix x;

	rst_recs_init(t, t->ent, t->cap);
	for (uint32_t n = tail; n != head; n++) {
		int r = read_ix(rd, ctx, n, &x, sector);

		if (r != 0) {
			return r;
		}
		rst_recs_apply(t, &x);
	}
	return 0;
}

int rst_log_index_find(rst_rd_fn rd, void *ctx, uint32_t tail, uint32_t head, uint32_t id_lo, uint32_t win,
		       struct rst_rec *out, uint32_t *n, uint8_t *sector)
{
	struct rst_ix x;

	memset(out, 0, win * sizeof(out[0]));
	for (uint32_t k = tail; k != head; k++) {
		int r = read_ix(rd, ctx, k, &x, sector);

		if (r != 0) {
			return r;
		}
		if (x.recording_id < id_lo || x.recording_id - id_lo >= win) {
			continue;
		}
		struct rst_rec *slot = &out[x.recording_id - id_lo];

		if (x.type == RREC_IX_TYPE_CLOSE) {
			rec_from_ix(slot, &x);
		} else if (x.type == RREC_IX_TYPE_CONFIRM && slot->info.recording_id != 0) {
			rec_confirm(slot);
		} else if (x.type == RREC_IX_TYPE_DELETE) {
			memset(slot, 0, sizeof(*slot));
		}
	}
	uint32_t m = 0;

	for (uint32_t i = 0; i < win; i++) {
		if (out[i].info.recording_id != 0) {
			if (m != i) {
				out[m] = out[i];
			}
			m++;
		}
	}
	*n = m;
	return 0;
}

int rst_log_tail_walk(rst_rd_fn rd, void *ctx, uint32_t index_tail, uint32_t index_head, uint32_t head_chunk_seq,
		      uint32_t *new_chunk_tail, uint32_t *new_index_tail, uint8_t *sector)
{
	struct rst_ix c, x;

	for (uint32_t n = index_tail; n != index_head; n++) {
		int r = read_ix(rd, ctx, n, &c, sector);

		if (r != 0) {
			return r;
		}
		if (c.type != RREC_IX_TYPE_CLOSE) {
			continue;
		}
		bool deleted = false;

		for (uint32_t m = n + 1; m != index_head && !deleted; m++) {
			r = read_ix(rd, ctx, m, &x, sector);
			if (r != 0) {
				return r;
			}
			deleted = x.type == RREC_IX_TYPE_DELETE && x.recording_id == c.recording_id;
		}
		if (!deleted) {
			*new_chunk_tail = c.first_chunk_seq;
			*new_index_tail = n;
			return 0;
		}
	}
	*new_chunk_tail = head_chunk_seq;
	*new_index_tail = index_head;
	return 0;
}

/* ------------------------------------------------------------------ recovery scan */

int rst_log_scan(rst_rd_fn rd, void *rctx, uint32_t total, uint32_t recording_id, uint32_t first_seq, uint8_t *buf,
		 void (*progress)(void *ctx, uint32_t kept), void *pctx, struct rst_scan *out)
{
	struct rst_chunk_hdr h;
	uint32_t pcrc;

	memset(out, 0, sizeof(*out));
	while (out->kept < total) {
		uint32_t seq = first_seq + out->kept;
		uint32_t lba = rst_lay_chunk_lba(total, seq);

		if (rd(rctx, lba, buf, RREC_CHUNK_SECTORS) != 0) {
			out->err_lba = lba;
			return -EIO;
		}
		if (rst_fmt_chunk_verify(buf, &h, &pcrc) != 0 || h.recording_id != recording_id || h.chunk_seq != seq) {
			break;
		}
		if (out->kept == 0) {
			out->start_utc_ms = h.utc_ms;
			out->recording_type = h.recording_type;
		}
		out->digest = rst_fmt_digest_add(out->digest, pcrc);
		out->duration_frames += h.frames;
		for (uint32_t i = 0; i < h.highlight_count && i < RREC_HIGHLIGHTS_PER_CHUNK; i++) {
			if (out->highlight_count < RREC_CLOSE_HIGHLIGHTS) {
				out->highlight_ms[out->highlight_count] =
					(uint32_t)(((uint64_t)h.highlight_frame[i] * 1000u) / RREC_PCM_RATE_HZ);   /* frames from the first kept frame (FW l.566) */
			}
			out->highlight_count++;
		}
		out->kept++;
		if (progress != NULL) {
			progress(pctx, out->kept);
		}
	}
	for (uint32_t i = out->highlight_count; i < RREC_CLOSE_HIGHLIGHTS; i++) {
		out->highlight_ms[i] = RREC_UNUSED_U32;
	}
	return 0;
}

/* ------------------------------------------------------------------ event log on the card */

int rst_log_evlog_head(rst_rd_fn rd, void *ctx, uint32_t hint, uint32_t *head, uint8_t *sector)
{
	struct rrec_logrec rec;
	uint32_t s = hint == 0 ? 1 : hint;

	for (uint32_t i = 0; i < RREC_LOG_RING_RECORDS; i++) {
		if (rd(ctx, rst_lay_log_lba(s), sector, 1) != 0) {
			return -EIO;
		}
		if (rst_fmt_log_decode(sector, &rec) != 0 || rec.seq != s) {
			break;
		}
		s++;
	}
	*head = s;
	return 0;
}

/* ------------------------------------------------------------------ event log RAM buffer */

void rst_evbuf_init(struct rst_evbuf *b)
{
	memset(b, 0, sizeof(*b));
}

void rst_evbuf_push(struct rst_evbuf *b, const struct rrec_logrec *r)
{
	if (b->n == RREC_LOG_BUFFER_RECORDS) {
		b->dropped++;
		return;
	}
	b->r[(b->first + b->n) % RREC_LOG_BUFFER_RECORDS] = *r;
	b->n++;
}

bool rst_evbuf_peek(const struct rst_evbuf *b, struct rrec_logrec *out)
{
	if (b->n == 0) {
		return false;
	}
	*out = b->r[b->first];
	return true;
}

void rst_evbuf_pop(struct rst_evbuf *b)
{
	if (b->n > 0) {
		b->first = (b->first + 1) % RREC_LOG_BUFFER_RECORDS;
		b->n--;
	}
}
