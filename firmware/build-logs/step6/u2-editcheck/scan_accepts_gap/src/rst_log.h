/*
 * rst_log.h: the logic of the storage part that works on what is on the card (pure: no kernel call; the card is
 * reached through a read callback). FW l.587 (superblock choice), l.636 (state of a recording), l.646 (recovery scan),
 * l.660 (tail move), l.1062 (event log buffer). Not a public header.
 */
#ifndef RST_LOG_H
#define RST_LOG_H

#include <stdbool.h>
#include <stdint.h>

#include "rst_fmt.h"

/* Reads count sectors from lba into buf. 0 or a negative errno. */
typedef int (*rst_rd_fn)(void *ctx, uint32_t lba, uint8_t *buf, uint32_t count);

/* ---- superblock choice at mount (FW l.587): the copy with a valid CRC and the higher sb_seq wins.
 * 0 with *out filled and *which = 0 (copy A) or 1 (copy B); -ENOENT when neither copy is valid. */
int rst_log_pick_sb(const uint8_t *copy_a, const uint8_t *copy_b, struct rst_sb *out, int *which);

/* ---- recordings rebuilt from the index (FW l.636: a recording's state is its last record) */
struct rst_rec {
	struct rst_rec_info info;     /* info.recording_id 0 = no such recording (ids start at 1) */
	uint8_t close_state;          /* RREC_IX_CLOSE_* of its CLOSE record */
	bool confirmed;               /* a CONFIRM record follows */
};

/* The newest recordings (cap of them, oldest first) that are not deleted. A live recording pushed out when the table
 * is full is not lost: evict_max_id is the highest id pushed out, and every id at or under it is read from the index
 * on demand (decision D16). Ids above evict_max_id are complete in ent[]. */
struct rst_recs {
	struct rst_rec *ent;
	uint32_t cap;
	uint32_t n;
	uint32_t live_total;          /* recordings not deleted, exact */
	uint32_t first_id;            /* id of the first CLOSE record of the walk (0 when none) */
	uint32_t evict_max_id;        /* 0 when nothing was pushed out */
};

void rst_recs_init(struct rst_recs *t, struct rst_rec *store, uint32_t cap);
/* Applies one index record (CLOSE adds, CONFIRM marks, DELETE removes). Unknown ids are ignored. */
void rst_recs_apply(struct rst_recs *t, const struct rst_ix *r);
struct rst_rec *rst_recs_find(struct rst_recs *t, uint32_t id);
/* Builds the table from index records tail to head - 1. 0, -EIO on a read error, -EBADMSG on a bad record. */
int rst_log_load_index(rst_rd_fn rd, void *ctx, uint32_t tail, uint32_t head, struct rst_recs *t, uint8_t *sector);
/* Reads the index for ids id_lo to id_lo + win - 1 only: out[] (win entries) gets the live ones in id order,
 * *n their count. 0, -EIO, -EBADMSG. */
int rst_log_index_find(rst_rd_fn rd, void *ctx, uint32_t tail, uint32_t head, uint32_t id_lo, uint32_t win,
		       struct rst_rec *out, uint32_t *n, uint8_t *sector);

/* ---- delete (FW l.660): after a DELETE record was appended, the new tail: the first chunk seq of the first recording,
 * in chunk order, that is not deleted (head_chunk_seq when none is left), and the index record number of its CLOSE
 * record (index_head when none). 0, -EIO, -EBADMSG. */
int rst_log_tail_walk(rst_rd_fn rd, void *ctx, uint32_t index_tail, uint32_t index_head, uint32_t head_chunk_seq,
		      uint32_t *new_chunk_tail, uint32_t *new_index_tail, uint8_t *sector);

/* ---- recovery scan (FW l.646) */
struct rst_scan {
	uint32_t kept;                /* chunks that passed */
	uint32_t digest;              /* over their payload CRCs */
	uint64_t duration_frames;
	int64_t start_utc_ms;         /* of the first chunk */
	uint8_t recording_type;
	uint16_t highlight_count;     /* sum over the kept chunk headers */
	uint32_t highlight_ms[RREC_CLOSE_HIGHLIGHTS];
	uint32_t err_lba;             /* the sector that failed to read, on -EIO */
};
/* From first_seq: keep a chunk while magic, header CRC, payload CRC, recording_id and chunk_seq (the previous + 1;
 * first_seq for the first) all match; stop at the first mismatch. buf: RREC_CHUNK_BYTES. progress(ctx, kept so far) after
 * each kept chunk, may be NULL. 0, or -EIO on a read error. */
int rst_log_scan(rst_rd_fn rd, void *rctx, uint32_t total, uint32_t recording_id, uint32_t first_seq, uint8_t *buf,
		 void (*progress)(void *ctx, uint32_t kept), void *pctx, struct rst_scan *out);

/* ---- event log in the card (FW l.525): the first free seq at or after hint (the superblock's log_head may lag). 0, -EIO. */
int rst_log_evlog_head(rst_rd_fn rd, void *ctx, uint32_t hint, uint32_t *head, uint8_t *sector);

/* ---- the RAM buffer of event log records (FW l.1062): RREC_LOG_BUFFER_RECORDS, the oldest unwritten dropped when full */
struct rst_evbuf {
	struct rrec_logrec r[RREC_LOG_BUFFER_RECORDS];
	uint32_t first;
	uint32_t n;
	uint32_t dropped;
};
void rst_evbuf_init(struct rst_evbuf *b);
void rst_evbuf_push(struct rst_evbuf *b, const struct rrec_logrec *r);
/* The oldest record, without removing it; false when empty. */
bool rst_evbuf_peek(const struct rst_evbuf *b, struct rrec_logrec *out);
void rst_evbuf_pop(struct rst_evbuf *b);

#endif
