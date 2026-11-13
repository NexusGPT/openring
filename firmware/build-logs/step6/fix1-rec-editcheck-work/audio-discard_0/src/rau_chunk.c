/*
 * rau_chunk.c: the pure part of the audio unit (software step 6, unit U3). No kernel call. See rau_chunk.h.
 * "FW l.N" = line N of design/firmware.md. Written for this project.
 */
#include <errno.h>
#include <string.h>

#include "rau_chunk.h"

#define RAC_FRAME_BYTES (RREC_CHANNELS * RREC_PCM_WIDTH_BITS / 8u)
#define RAC_NS_PER_SEC 1000000000u
#define RAC_NS_PER_FRAME (RAC_NS_PER_SEC / RREC_PCM_RATE_HZ)
#define RAC_NS_PER_MS 1000000u
#define RAC_MS_PER_SEC 1000u

/* cycles to ns without overflow (whole seconds apart) */
static uint64_t cycles_to_ns(uint64_t cycles, uint32_t hz)
{
	uint64_t sec = cycles / hz;
	uint64_t rem = cycles % hz;

	return sec * RAC_NS_PER_SEC + (rem * RAC_NS_PER_SEC) / hz;
}

/* a cycle difference to frames, rounded down (also for negative differences) */
static int64_t cycles_to_frames(int64_t d, uint32_t hz)
{
	if (d >= 0) {
		uint64_t u = (uint64_t)d;

		return (int64_t)((u / hz) * RREC_PCM_RATE_HZ + ((u % hz) * RREC_PCM_RATE_HZ) / hz);
	}
	uint64_t m = (uint64_t)(-d);
	uint64_t q = (m / hz) * RREC_PCM_RATE_HZ;
	uint64_t r = ((m % hz) * RREC_PCM_RATE_HZ + hz - 1u) / hz;

	return -(int64_t)(q + r);
}

void rac_begin(struct rac *s, const struct rac_start *a)
{
	memset(s, 0, sizeof(*s));
	s->st = *a;
	s->discard_left = 0;
	s->limit = UINT64_MAX;
	s->miss_counted_chunk = UINT32_MAX;
}

int64_t rac_ms_to_frame(const struct rac *s, int64_t ms)
{
	return (ms - s->st.start_ms) * (int64_t)RREC_PCM_RATE_HZ / (int64_t)RAC_MS_PER_SEC -
	       (int64_t)RREC_DISCARD_FRAMES;
}

static uint8_t *payload(struct rst_chunk *c)
{
	return &c->bytes[RREC_CHUNK_HEADER_BYTES];
}

/* A new chunk: the fixed header fields (FW l.545 to l.548, l.556 to l.558, l.567 to l.573). */
static void chunk_begin(struct rac *s, struct rst_chunk *c, const struct rac_facts *f)
{
	struct rst_chunk_hdr *h = &c->hdr;
	uint64_t first_ns = cycles_to_ns(s->st.start_cycles, s->st.cycles_hz) +
			    ((uint64_t)RREC_DISCARD_FRAMES + s->chunk_first) * RAC_NS_PER_FRAME;

	memset(h, 0, sizeof(*h));
	h->recording_id = s->st.recording_id;
	h->chunk_in_recording = s->chunk_no;
	h->recording_type = s->st.recording_type;
	h->first_frame_index = s->chunk_first;
	h->uptime_ns = first_ns;
	h->utc_ms = s->st.time_set ? s->st.utc_offset_ms + (int64_t)(first_ns / RAC_NS_PER_MS) : 0;
	h->boot_count = s->st.boot_count;
	h->cycle_hz = s->st.cycles_hz;
	h->battery_mv = f->battery_mv;
	h->temp_c_x10 = f->temp_c_x10;
	h->fw_version = f->fw_version;
	if (s->chunk_no == 0) {
		h->flags |= RREC_CH_FLAG_FIRST;
	}
	if (!s->st.time_set) {
		h->flags |= RREC_CH_FLAG_TIME_NOT_SET;
	}
	if (f->b15) {
		h->flags |= RREC_CH_FLAG_B15;
	}
	for (uint32_t i = 0; i < RREC_HIGHLIGHTS_PER_CHUNK; i++) {
		h->highlight_frame[i] = RREC_UNUSED_U32;
	}
	for (uint32_t i = 0; i < RREC_MOTOR_PER_CHUNK; i++) {
		h->motor_frames[i][0] = RREC_UNUSED_U32;
		h->motor_frames[i][1] = RREC_UNUSED_U32;
	}
	s->chunk = c;
	s->fill = 0;
}

/* The highlight markers fired during this chunk and the motor intervals that fall in frames [c0, c1) go into the header (FW l.564 to l.566, l.576, l.577). */
static void chunk_marks(struct rac *s, struct rst_chunk_hdr *h, int64_t c0, int64_t c1)
{
	/* highlights (ruling R24, FW l.564, l.566): each marker that fired while this chunk was being filled is written
	 * here as the frame number of CENTRE_DOWN counted from the first kept frame of the recording; at most 8, a ninth
	 * stays out (ruling D4) */
	for (uint8_t i = 0; i < s->hl_npend; i++) {
		if (h->highlight_count < RREC_HIGHLIGHTS_PER_CHUNK) {
			h->highlight_frame[h->highlight_count++] = (uint32_t)s->hl_pend[i];
		}
	}
	s->hl_npend = 0;

	/* motor intervals: every one that overlaps, cut at the chunk edges, at most 4, a fifth merged into the fourth
	 * (end frame moved) (FW l.576, l.577) */
	uint8_t kept = 0;

	for (uint8_t k = 0; k < s->mi_n; k++) {
		int64_t a = s->mi[k].s;
		int64_t e = s->mi[k].e;

		if (a < c1 && e > c0) {
			uint32_t s_rel = (uint32_t)((a > c0 ? a : c0) - c0);
			uint32_t e_rel = (uint32_t)((e < c1 ? e : c1) - c0);

			if (h->motor_count < RREC_MOTOR_PER_CHUNK) {
				h->motor_frames[h->motor_count][0] = s_rel;
				h->motor_frames[h->motor_count][1] = e_rel;
				h->motor_count++;
			} else if (e_rel > h->motor_frames[RREC_MOTOR_PER_CHUNK - 1u][1]) {
				h->motor_frames[RREC_MOTOR_PER_CHUNK - 1u][1] = e_rel;
			}
		}
		if (s->mi[k].e > c1) {
			s->mi[kept++] = s->mi[k];
		}
	}
	s->mi_n = kept;
	/* an interval still open (MOTOR high, no low yet) runs to the end of this chunk and goes on in the next */
	if (s->mi_open && s->mi_open_start < c1) {
		if (h->motor_count < RREC_MOTOR_PER_CHUNK) {
			int64_t a = s->mi_open_start;

			h->motor_frames[h->motor_count][0] = (uint32_t)((a > c0 ? a : c0) - c0);
			h->motor_frames[h->motor_count][1] = (uint32_t)(c1 - c0);
			h->motor_count++;
		} else {
			h->motor_frames[RREC_MOTOR_PER_CHUNK - 1u][1] = (uint32_t)(c1 - c0);
		}
	}
	if (h->motor_count > 0) {
		h->flags |= RREC_CH_FLAG_MOTOR;
	}
}

static void chunk_finish(struct rac *s, bool last)
{
	struct rst_chunk *c = s->chunk;
	struct rst_chunk_hdr *h = &c->hdr;
	int64_t c0 = (int64_t)s->chunk_first;

	h->frames = s->fill;
	if (last) {
		h->flags |= RREC_CH_FLAG_LAST;
	}
	/* unused payload bytes are zero (FW l.535) */
	memset(&payload(c)[s->fill * RAC_FRAME_BYTES], 0, RREC_CHUNK_PAYLOAD_BYTES - s->fill * RAC_FRAME_BYTES);
	chunk_marks(s, h, c0, c0 + (int64_t)s->fill);
}

int rac_block(struct rac *s, const int16_t *blk, const struct rac_ops *ops)
{
	bool missing = (blk == NULL);
	uint32_t i = 0;
	int ret = 0;

	if (missing) {
		s->miss_counted_chunk = UINT32_MAX;     /* a dropout block is counted once in each chunk it touches */
		ops->dropout(ops->ctx, s->chunk_no, (uint8_t)(s->fill / RREC_BLOCK_FRAMES));
	}
	while (i < RREC_BLOCK_FRAMES) {
		if (s->discard_left > 0) {
			uint32_t n = RREC_BLOCK_FRAMES - i;

			if (n > s->discard_left) {
				n = s->discard_left;
			}
			s->discard_left -= n;
			i += n;
			continue;
		}
		if (s->cut || s->total >= s->limit) {
			break;
		}
		if (s->chunk == NULL) {
			struct rac_facts f;
			struct rst_chunk *c = ops->get(ops->ctx, &f);

			if (c == NULL) {
				ret = -ENOBUFS;
				break;
			}
			chunk_begin(s, c, &f);
		}
		uint32_t n = RREC_BLOCK_FRAMES - i;

		if (n > RREC_CHUNK_FRAMES - s->fill) {
			n = RREC_CHUNK_FRAMES - s->fill;
		}
		if ((uint64_t)n > s->limit - s->total) {
			n = (uint32_t)(s->limit - s->total);
		}
		uint8_t *dst = &payload(s->chunk)[s->fill * RAC_FRAME_BYTES];

		if (missing) {
			memset(dst, 0, n * RAC_FRAME_BYTES);
			s->chunk->hdr.flags |= RREC_CH_FLAG_DROPOUT;
			if (s->miss_counted_chunk != s->chunk_no) {
				s->miss_counted_chunk = s->chunk_no;
				s->chunk->hdr.dropout_blocks++;
			}
		} else {
			const int16_t *src = &blk[i * RREC_CHANNELS];

			memcpy(dst, src, n * RAC_FRAME_BYTES);
			for (uint32_t k = 0; k < n * RREC_CHANNELS; k++) {
				int16_t v = src[k];

				if (v == INT16_MIN || v == INT16_MAX) {
					s->chunk->hdr.flags |= RREC_CH_FLAG_CLIPPED;
					break;
				}
			}
		}
		s->fill += n;
		s->total += n;
		i += n;
		if (s->fill == RREC_CHUNK_FRAMES) {
			struct rst_chunk *c = s->chunk;

			chunk_finish(s, false);
			s->chunk = NULL;
			s->fill = 0;
			s->chunk_no++;
			s->chunk_first = s->total;
			ops->full(ops->ctx, c);
		}
	}
	return ret;
}

void rac_highlight(struct rac *s, int64_t centre_down_ms)
{
	int64_t fr = rac_ms_to_frame(s, centre_down_ms);

	if (s->cut) {
		return;
	}
	if (fr < 0) {
		fr = 0;
	}
	uint16_t idx = s->hl_total;

	if (s->hl_total < UINT16_MAX) {
		s->hl_total++;
	}
	if (idx < RREC_CLOSE_HIGHLIGHTS) {
		s->hl_ms[idx] = (uint32_t)(fr * (int64_t)RAC_MS_PER_SEC / (int64_t)RREC_PCM_RATE_HZ);
	}
	/* it goes in the header of the chunk being filled now (ruling R24) */
	if (s->hl_npend < RAC_HL_PEND) {
		s->hl_pend[s->hl_npend++] = fr;
	}
}

static void mi_push(struct rac *s, int64_t a, int64_t e)
{
	if (e <= 0) {
		return;           /* ended inside the discarded start: nothing of it is kept */
	}
	if (s->mi_n < RAC_MOTOR_PEND) {
		s->mi[s->mi_n].s = a;
		s->mi[s->mi_n].e = e;
		s->mi_n++;
	} else if (e > s->mi[s->mi_n - 1u].e) {
		s->mi[s->mi_n - 1u].e = e;
	}
}

void rac_motor_edge(struct rac *s, bool high, uint64_t cycles)
{
	int64_t f = cycles_to_frames((int64_t)(cycles - s->st.start_cycles), s->st.cycles_hz) -
		    (int64_t)RREC_DISCARD_FRAMES;

	if (s->cut) {
		return;
	}
	if (high) {
		if (!s->mi_open) {
			s->mi_open = true;
			s->mi_open_start = f;
		}
		return;
	}
	int64_t e = f + (int64_t)RREC_MOTOR_TAIL_FRAMES;

	if (s->mi_open) {
		mi_push(s, s->mi_open_start, e);
		s->mi_open = false;
	} else {
		mi_push(s, f, e);
	}
}

void rac_set_limit(struct rac *s, uint64_t frames)
{
	s->limit = frames;
}

bool rac_limit_reached(const struct rac *s)
{
	return s->total >= s->limit;
}

struct rst_chunk *rac_cut(struct rac *s, struct rst_close_args *close)
{
	struct rst_chunk *last = NULL;
	uint64_t target = s->limit;

	if (target < s->chunk_first) {
		target = s->chunk_first;      /* chunks already with the store stay as they are */
	}
	if (s->chunk != NULL && s->total > target) {
		s->fill = (uint32_t)(target - s->chunk_first);
		s->total = target;
	}
	if (s->chunk != NULL && s->fill > 0) {
		chunk_finish(s, true);
		last = s->chunk;
	}
	s->chunk = NULL;
	s->cut = true;
	s->limit = s->total;
	if (close != NULL) {
		close->duration_frames = s->total;
		close->highlight_count = s->hl_total;
		for (uint32_t i = 0; i < RREC_CLOSE_HIGHLIGHTS; i++) {
			close->highlight_ms[i] = i < s->hl_total ? s->hl_ms[i] : RREC_UNUSED_U32;
		}
	}
	return last;
}
