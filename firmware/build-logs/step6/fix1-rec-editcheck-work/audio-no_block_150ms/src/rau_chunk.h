/*
 * rau_chunk.h: the pure part of the audio unit (software step 6, unit U3). Blocks of the microphone input into chunks
 * of the store (design/firmware.md sections 4 and 5.3; "FW l.N" = line N of that file). No kernel call: stdint,
 * stdbool, string and errno constants only. Not a public header (the public one is ring_audio/rau.h).
 *
 * Frame numbers: a "frame index" counts from the first KEPT frame of the recording (FW l.460); the 800 discarded
 * frames come before it, so a time before the first kept frame has a negative index. Every number of the
 * specification comes from ring_rhw/rrec_spec.h.
 */
#ifndef RAU_CHUNK_H
#define RAU_CHUNK_H

#include <stdbool.h>
#include <stdint.h>

#include <ring_rhw/rrec_spec.h>
#include <ring_store/rst.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RAC_HL_PEND 16u      /* highlights waiting for their chunk's header */
#define RAC_MOTOR_PEND 16u   /* closed motor intervals waiting for their chunk's header */

/* Facts the caller gives at the start of each chunk (FW l.567 to l.571, l.547 bit 6). */
struct rac_facts {
	uint16_t battery_mv;
	int16_t temp_c_x10;
	uint32_t fw_version;
	bool b15;
};

/* What the pure part needs from the thin part. Called from rac_block() on the caller's thread. */
struct rac_ops {
	/* The next empty chunk buffer, with the facts for its header; NULL when none can be had (the frames of the
	 * block that need it are dropped). May wait. */
	struct rst_chunk *(*get)(void *ctx, struct rac_facts *facts);
	/* A full chunk (FW l.443): hand it to the store. */
	void (*full)(void *ctx, struct rst_chunk *c);
	/* A block replaced by zeros (FW l.430): once per block; `block` = frame position in the chunk divided by the
	 * block length. */
	void (*dropout)(void *ctx, uint32_t chunk_in_recording, uint8_t block);
	void *ctx;
};

struct rac_start {
	uint32_t recording_id;
	uint8_t recording_type;
	uint32_t boot_count;
	bool time_set;
	int64_t utc_offset_ms;       /* utc = uptime ms + offset, when time_set */
	int64_t start_ms;            /* uptime ms of the PDM start */
	uint64_t start_cycles;       /* cycle counter at the PDM start */
	uint32_t cycles_hz;          /* cycles per second */
};

struct rac {
	struct rac_start st;
	uint32_t discard_left;       /* frames still to drop at the start (FW l.460) */
	uint64_t total;              /* kept frames taken so far */
	uint64_t limit;              /* frames at most (the stop mark, FW l.448); UINT64_MAX = none */
	bool cut;                    /* rac_cut() ran: later frames are dropped */
	struct rst_chunk *chunk;     /* the chunk being filled, or NULL */
	uint32_t fill;               /* frames in it */
	uint64_t chunk_first;        /* frame index of its first frame */
	uint32_t chunk_no;           /* chunk_in_recording of the chunk being filled (or the next one) */
	uint32_t miss_counted_chunk; /* the chunk in which the block being fed was counted as a dropout */
	/* highlights */
	uint16_t hl_total;
	uint32_t hl_ms[RREC_CLOSE_HIGHLIGHTS];
	int64_t hl_pend[RAC_HL_PEND];
	uint8_t hl_npend;
	/* motor */
	struct {
		int64_t s;
		int64_t e;           /* exclusive */
	} mi[RAC_MOTOR_PEND];
	uint8_t mi_n;
	bool mi_open;
	int64_t mi_open_start;
};

/* Start a recording's chunking (FW l.459, l.460). */
void rac_begin(struct rac *s, const struct rac_start *a);

/* Frame index of an uptime in ms (FW l.460: the first kept frame is index 0; earlier times are negative). */
int64_t rac_ms_to_frame(const struct rac *s, int64_t ms);

/* One block of RREC_BLOCK_FRAMES stereo frames (blk = RREC_BLOCK_BYTES bytes) or NULL for a missing block (zeros of
 * the same length, flag bit 7, FW l.430). Frames over the limit are dropped. 0, or -ENOBUFS when ops->get gave no
 * chunk (the frames that needed it are dropped). */
int rac_block(struct rac *s, const int16_t *blk, const struct rac_ops *ops);

/* A highlight at the time of CENTRE_DOWN (FW l.244, l.263; not of the press's release or of the moment it fires). */
void rac_highlight(struct rac *s, int64_t centre_down_ms);

/* A MOTOR edge at this cycle count (FW l.495, l.496). */
void rac_motor_edge(struct rac *s, bool high, uint64_t cycles);

/* Keep at most `frames` frames in all (FW l.448). */
void rac_set_limit(struct rac *s, uint64_t frames);
bool rac_limit_reached(const struct rac *s);

/* End the recording's audio: the chunk being filled is finished as the last one (flag bit 1, unused payload bytes
 * zero) and returned, or NULL when it holds no frame (the caller takes the buffer back from s->chunk before the
 * call). Fills the CLOSE record's audio part. Later frames are dropped. */
struct rst_chunk *rac_cut(struct rac *s, struct rst_close_args *close);

#ifdef __cplusplus
}
#endif

#endif
