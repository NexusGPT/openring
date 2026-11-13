/*
 * rst.h: the storage part (software step 6, unit U2 builds it; U0 wrote this header, frozen: changes only through the
 * lead). The raw append-only log on the card of design/firmware.md section 5 ("FW l.N" = line N of that file).
 *
 * Layers (step 6 plan, U2): pure files (rst_fmt.c, rst_layout.c, rst_log.c: no kernel call) declared in the unit's own
 * src/ headers, which are not public; this header is the thin part, the only one other units call.
 *
 * Threads: the store has one storage thread (made by rst_init). Every call below except rst_put_chunk, rst_log_put,
 * rst_space, rst_log_dropped and rst_mounted runs the work on the caller's thread under the store's lock and BLOCKS
 * for the card's time. Two calls never run at once: a call made while another one runs (from another thread) returns
 * -EBUSY at once (FW l.219: one storage operation at a time; the transfer part answers BUSY). Never from an interrupt.
 * Hardware only through rhw.h: rhw_disk(), rhw_sdbus(), rhw_pmic()->rail_set(RHW_RAIL_SD, ..., "rst_..."),
 * rhw_clock(). Numbers only from rrec_spec.h.
 */
#ifndef RING_STORE_RST_H
#define RING_STORE_RST_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <ring_rhw/rrec_spec.h>

#ifdef __cplusplus
extern "C" {
#endif

/* The chunk header fields ring_audio fills (FW 5.3, l.537 to l.580). The store fills the rest when it writes:
 * magic, header_version, header_size, chunk_seq (the global sequence it owns), channels, sample_rate_hz,
 * sample_format, mic_mask, payload_bytes (= frames x 4), pdm_clock_hz, pdm_ratio, gain_code, the reserved zeros and
 * both CRCs (FW l.579, l.580). */
struct rst_chunk_hdr {
	uint32_t chunk_seq;           /* OUT: set by the store at rst_put_chunk / rst_close */
	uint32_t recording_id;        /* FW l.545 (from rst_open) */
	uint32_t chunk_in_recording;  /* FW l.546 */
	uint16_t flags;               /* FW l.547, RREC_CH_FLAG_* */
	uint8_t recording_type;       /* FW l.548, RREC_REC_TYPE_* */
	uint32_t frames;              /* FW l.554: valid frames, 1 to RREC_CHUNK_FRAMES */
	uint64_t first_frame_index;   /* FW l.556 */
	int64_t utc_ms;               /* FW l.557: 0 when the time is not set */
	uint64_t uptime_ns;           /* FW l.558 */
	uint16_t highlight_count;     /* FW l.564: 0 to 8 */
	uint32_t highlight_frame[RREC_HIGHLIGHTS_PER_CHUNK];    /* FW l.566; RREC_UNUSED_U32 when unused */
	uint16_t battery_mv;          /* FW l.567 */
	int16_t temp_c_x10;           /* FW l.568 */
	uint32_t boot_count;          /* FW l.569 */
	uint32_t dropout_blocks;      /* FW l.570 */
	uint32_t fw_version;          /* FW l.571 */
	uint32_t cycle_hz;            /* FW l.573 */
	uint16_t motor_count;         /* FW l.576: 0 to 4 */
	uint32_t motor_frames[RREC_MOTOR_PER_CHUNK][2];          /* FW l.577; RREC_UNUSED_U32 pairs when unused */
};

/* One chunk as audio fills it and the store writes it: sector 0 of `bytes` is the header (encoded by the store from
 * hdr), sectors 1 to 64 the payload (filled by audio; unused bytes of a last chunk zero, FW l.535). One write of
 * RREC_CHUNK_SECTORS sectors (FW l.515). */
struct rst_chunk {
	struct rst_chunk_hdr hdr;
	uint8_t bytes[RREC_CHUNK_BYTES];
};

/* Called on the storage thread when a queued chunk is written (err 0) or failed its 3 tries (err < 0, FW l.643).
 * Must not block. The chunk buffer is the caller's again from this call on. */
typedef void (*rst_chunk_done_fn)(struct rst_chunk *c, int err);

struct rst_space {
	uint32_t total;               /* chunk_count_total (FW l.529) */
	uint32_t used;                /* head - tail (FW l.650) */
	uint32_t free_chunks;         /* total - used (FW l.650) */
	bool s30;                     /* free at or under RREC_S30_CHUNKS (FW l.652) */
	bool sfull;                   /* free at or under RREC_SFULL_CHUNKS (FW l.651) */
	uint32_t minutes_left;        /* free x 0.512 s, in whole minutes rounded down (FW l.653) */
};

struct rst_mount_info {
	bool open_flag;               /* superblock open flag (FW l.603) */
	uint32_t open_recording_id;   /* when open_flag */
	uint32_t boot_count;          /* after this mount's increment when boot was true (decision D14) */
	uint32_t card_sectors;        /* FW l.507, l.654 */
	uint32_t recordings;          /* not deleted (GET_INFO, FW l.696) */
	struct rst_space space;
};

/* One recording as LIST_RECORDINGS shows it (FW l.697). */
struct rst_rec_info {
	uint32_t recording_id;
	uint8_t type;                 /* RREC_REC_TYPE_* */
	uint8_t channels;             /* 2 */
	uint8_t state;                /* RREC_LIST_STATE_NEW, _TRANSFERRED or _RECOVERED (a recovered recording that was
	                               * confirmed shows TRANSFERRED) */
	uint32_t first_chunk_seq;
	uint32_t chunk_count;
	uint32_t sample_rate_hz;
	int64_t start_utc_ms;
	uint64_t duration_frames;
	uint32_t digest;              /* FW l.630 */
	uint16_t highlight_count;
};

/* What the CLOSE record carries besides what the store counted (FW l.612 to l.634). */
struct rst_close_args {
	uint64_t duration_frames;     /* FW l.629: frames kept in the whole recording */
	uint16_t highlight_count;     /* FW l.626: all highlights of the recording (may exceed 32) */
	uint32_t highlight_ms[RREC_CLOSE_HIGHLIGHTS]; /* FW l.632: the first 32, ms from the start; RREC_UNUSED_U32 after */
};

struct rst_recover_result {
	uint32_t recording_id;
	uint32_t chunks_kept;         /* chunks that passed the scan (FW l.646) */
	uint32_t head_chunk_seq;      /* the new head, past the last good chunk */
};

struct rst_factory_result {      /* T-STORE (FW l.1030) */
	bool equal;                   /* the 65 sectors read back with the same CRC-32 */
	uint32_t write_us;            /* time of the one write of 65 sectors */
	uint32_t read_us;             /* time of the one read */
};

struct rst_cb {
	/* free space reached S30 or SFULL while a recording runs (FW l.166, l.167): once per crossing; storage thread */
	void (*s30)(uint32_t free_chunks);  /* FW l.166 */
	void (*sfull)(uint32_t free_chunks);  /* FW l.167 */
	/* the 3rd failed try of a chunk write (FW l.168): storage thread; the superblock is left open */
	void (*write_fault)(int err);
};

/* Start: the storage thread, the RAM log buffer, and the bus sleep state at boot before any SPI use (FW l.506:
 * rhw_sdbus()->suspend()). VDD_SD stays off. Once, at boot, before every other call. cb may be NULL. */
int rst_init(const struct rst_cb *cb);

/* Mount (FW l.135 to l.138, l.506, l.507): VDD_SD on ("rst_mount"), wait RREC_SD_RAIL_WAIT_MS, resume the bus, card
 * init with RREC_INIT_TRIES tries RREC_INIT_GAP_MS apart (C8), sector count, superblock (the valid copy with the
 * higher sb_seq, FW l.587), list of recordings rebuilt from the index, then the buffered log records written.
 * boot = true at the mount of BOOT only: boot_count + 1 and the superblock written once (decision D14).
 * 0 with *out filled; -EIO after the 3rd failed init, with VDD_SD switched off again (bus suspended first).
 * Blocks: up to 2 x 200 ms plus the card's time. */
int rst_mount(bool boot, struct rst_mount_info *out);

/* Unmount (FW l.506): disk deinit, bus suspend, VDD_SD off ("rst_unmount"), in this order. Waits for queued chunks
 * and log records first. 0 or -EIO (the rail goes off anyway). */
int rst_unmount(void);

/* true between a successful rst_mount and rst_unmount. Does not block. */
bool rst_mounted(void);  /* FW l.640 */

/* Open a recording (FW l.126, l.641): new recording_id, superblock with the open flag and open_first_chunk_seq.
 * 0 with *id; -EBUSY when one is open (FW l.219), -ENOSPC at SFULL, -EPERM when the open flag is already set (a
 * recovery is due, ruling R4b), -EIO on a write error. Requires rst_mount. */
int rst_open(uint8_t recording_type, int64_t start_utc_ms, uint32_t *id);

/* Queue one full chunk of the open recording (FW l.641: written as soon as it is full). Sets c->hdr.chunk_seq.
 * Does NOT block: 0 when queued, -ENOBUFS when RREC_CHUNK_RING chunks already wait, -EIO after a write fault, -EINVAL
 * with no open recording. The storage thread writes it once (3 tries at once, FW l.643) and calls done(c, err).
 * Called by ring_audio's thread. */
int rst_put_chunk(struct rst_chunk *c, rst_chunk_done_fn done);

/* Close (FW l.125 first three steps): wait for the queued chunks, write `last` (the partial chunk, or NULL when
 * none), the CLOSE record (state COMPLETE, digest over every chunk's payload CRC, FW l.630) and the superblock with
 * the open flag clear. VDD_SD stays on (the join switches it off with rst_unmount after VDD_MIC, FW l.125). 0, -EIO.
 * Blocks. */
int rst_close(struct rst_chunk *last, const struct rst_close_args *a);

/* Recovery scan (FW l.646): from open_first_chunk_seq, keep chunks while magic, header CRC, payload CRC,
 * recording_id and chunk_seq + 1 match; CLOSE record RECOVERED; head past the last good chunk; open flag cleared;
 * progress(chunks so far) after each chunk (may be NULL; storage or caller thread, must not block). 0; -EIO on a read
 * error, with the open flag still set (FW l.143, ruling R9). Blocks for the whole scan. */
int rst_recover(void (*progress)(uint32_t chunks), struct rst_recover_result *out);

/* Space now (FW 5.6), from RAM. Does not block. -ENODEV before the first mount. */
int rst_space(struct rst_space *out);  /* FW l.650 */

/* Recordings not deleted, oldest first, starting at recording id `first` (0 = the oldest not deleted; decision D5),
 * at most max (1 to RREC_LIST_MAX_MAX) entries into out; *count set. 0 or -EINVAL. Reads the index on demand beyond the
 * RREC_LIST_CACHE newest (decision D16). */
int rst_list(uint32_t first, uint16_t max, struct rst_rec_info *out, uint16_t *count);  /* FW l.697 */

/* Read chunk `chunk` (0-based in the recording) of a recording exactly as stored: RREC_CHUNK_BYTES bytes (FW l.698).
 * 0; -ENOENT for an unknown or deleted recording or a chunk past its end (FW l.661); -EIO. */
int rst_read_chunk(uint32_t recording_id, uint32_t chunk, uint8_t *out);

/* CONFIRM (FW l.658): compare with the CLOSE digest; match appends a CONFIRM record. 0; -EBADMSG on a mismatch
 * (DIGEST_MISMATCH, nothing changes); -ENOENT. */
int rst_confirm(uint32_t recording_id, uint32_t digest);

/* DELETE (FW l.659, l.660): refused without CONFIRM (-EACCES = NOT_CONFIRMED); appends DELETE, moves the tail over
 * every leading deleted recording, writes the superblock; *free_after = free chunks after it. 0, -ENOENT, -EIO. */
int rst_delete(uint32_t recording_id, uint32_t *free_after);

/* Queue one event log record (FW l.1062): copied into the RAM buffer of RREC_LOG_BUFFER_RECORDS; when full the
 * oldest unwritten record is dropped and counted. Sets r->seq in the copy. Written to the log area at the next time
 * VDD_SD is on (mount, or at once when mounted). Any thread (not an interrupt); never blocks. */
void rst_log_put(const struct rrec_logrec *r);

/* Records dropped from the full buffer since boot (FW l.1062). Does not block. */
uint32_t rst_log_dropped(void);

/* GET_LOG (FW l.706): up to max (1 to RREC_GET_LOG_MAX_MAX) encoded 512-byte records from record seq `first`, into
 * out (max x 512 bytes); *count set. Needs the card mounted. 0, -EINVAL, -EIO. */
int rst_log_read(uint32_t first, uint16_t max, uint8_t *out, uint16_t *count);

/* T-STORE (FW l.1030): needs rst_mount; writes RREC_FACTORY_SECTORS sectors at RREC_LBA_FACTORY_FIRST, reads back,
 * compares the CRC, times both. 0 with *out; -EIO. */
int rst_factory_area_test(struct rst_factory_result *out);

/* T-STORE's last step (FW l.1030): delete every recording of type RREC_REC_TYPE_FACTORY without a CONFIRM record.
 * 0 with *deleted; -EIO. */
int rst_delete_factory_recordings(uint32_t *deleted);

#ifdef __cplusplus
}
#endif

/*
 * ------------------------------------------------------------------ return codes added after the unit landed
 * (comments only, written by the lead from firmware/docs/store-notes.md section 5; no signature changed)
 * - rst_put_chunk: -ENOSPC when the chunk would overwrite a chunk that is not freed; -EINVAL when the header's
 *   frames are 0 or over 8,192, highlight_count over 8 or motor_count over 4. The store overwrites recording_id
 *   and recording_type of the header with those of the open recording.
 * - rst_delete and rst_delete_factory_recordings: -EBUSY when a recording is open or the superblock open flag
 *   is set.
 * - rst_close: -EINVAL before anything is written when `last` has an invalid header.
 * - rst_log_read, rst_list, rst_read_chunk, rst_confirm, rst_delete, rst_open, rst_recover: -ENODEV when not
 *   mounted; rst_mount before rst_init: -ENODEV.
 * - rst_log_put: seq is set when the record is written to the card (gap-free from 1), not when it is queued.
 * - rst_recover: -EINVAL when the open flag is clear.
 * - A card with no valid superblock copy gets a new log at the first mount; a card that cannot be READ is never
 *   formatted (-EIO).
 */

#endif
