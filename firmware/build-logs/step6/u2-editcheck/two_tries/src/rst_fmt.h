/*
 * rst_fmt.h: the byte formats of the storage part (pure: no kernel call). "FW l.N" = line N of design/firmware.md.
 * Not a public header (the public one is ring_store/rst.h). Every number comes from rrec_spec.h.
 */
#ifndef RST_FMT_H
#define RST_FMT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <ring_store/rst.h>

/* ---- little-endian access (FW l.70: every multi-byte field is little-endian) */
static inline void rst_put16(uint8_t *p, uint16_t v)
{
	p[0] = (uint8_t)v;
	p[1] = (uint8_t)(v >> 8);
}
static inline void rst_put32(uint8_t *p, uint32_t v)
{
	rst_put16(p, (uint16_t)v);
	rst_put16(p + 2, (uint16_t)(v >> 16));
}
static inline void rst_put64(uint8_t *p, uint64_t v)
{
	rst_put32(p, (uint32_t)v);
	rst_put32(p + 4, (uint32_t)(v >> 32));
}
static inline uint16_t rst_get16(const uint8_t *p)
{
	return (uint16_t)(p[0] | (p[1] << 8));
}
static inline uint32_t rst_get32(const uint8_t *p)
{
	return (uint32_t)rst_get16(p) | ((uint32_t)rst_get16(p + 2) << 16);
}
static inline uint64_t rst_get64(const uint8_t *p)
{
	return (uint64_t)rst_get32(p) | ((uint64_t)rst_get32(p + 4) << 32);
}

/* ---- superblock (FW l.587 to l.610) */
struct rst_sb {
	uint32_t sb_seq;
	uint32_t card_sectors;
	uint32_t chunk_first_lba;
	uint32_t chunk_count_total;
	uint32_t head_chunk_seq;
	uint32_t tail_chunk_seq;
	uint32_t next_recording_id;
	uint32_t index_head;          /* next index record number */
	uint32_t index_tail;          /* oldest index record still needed */
	uint8_t open_flag;
	uint32_t open_recording_id;
	uint32_t open_first_chunk_seq;
	uint32_t boot_count;
	uint32_t log_head;            /* next event log record number (seq) */
};

/* out: RREC_SECTOR_BYTES bytes, reserved bytes zero, CRC-32 over bytes 0 to 507 in the last 4 (FW l.610). */
void rst_fmt_sb_encode(const struct rst_sb *s, uint8_t *out);
/* 0, or -EBADMSG when magic, version, size or CRC do not match. */
int rst_fmt_sb_decode(const uint8_t *in, struct rst_sb *s);

/* ---- index record (FW l.612 to l.634) */
struct rst_ix {
	uint8_t type;                 /* RREC_IX_TYPE_* */
	uint8_t close_state;          /* RREC_IX_CLOSE_*; 0 for CONFIRM and DELETE */
	uint32_t record_number;
	uint32_t recording_id;
	uint32_t first_chunk_seq;
	uint32_t chunk_count;
	uint8_t recording_type;
	uint8_t channels;
	uint16_t highlight_count;
	uint32_t sample_rate_hz;
	int64_t start_utc_ms;
	uint64_t duration_frames;
	uint32_t digest;
	uint32_t highlight_ms[RREC_CLOSE_HIGHLIGHTS];
};
void rst_fmt_ix_encode(const struct rst_ix *r, uint8_t *out);
int rst_fmt_ix_decode(const uint8_t *in, struct rst_ix *r);

/* ---- chunk (FW l.535 to l.580) */
/* Encodes c->hdr into sector 0 of c->bytes: the constant fields, payload_bytes = frames x 4, the unused highlight and
 * motor slots as RREC_UNUSED_U32, the reserved bytes zero. Zeroes the payload bytes after the valid frames (FW l.535),
 * then both CRC-32 (payload over all RREC_CHUNK_PAYLOAD_BYTES, header over bytes 0 to 507). *payload_crc (may be NULL)
 * gets the payload CRC. -EINVAL when frames is 0 or over RREC_CHUNK_FRAMES, highlight_count over 8 or motor_count over 4. */
int rst_fmt_chunk_encode(struct rst_chunk *c, uint32_t *payload_crc);
/* true when frames, highlight_count and motor_count are in their ranges (what rst_fmt_chunk_encode accepts). */
bool rst_fmt_chunk_hdr_valid(const struct rst_chunk_hdr *h);
/* Decodes one header sector. 0, or -EBADMSG when magic, version, size or header CRC do not match. */
int rst_fmt_chunk_hdr_decode(const uint8_t *sector0, struct rst_chunk_hdr *h, uint32_t *payload_crc);
/* Decodes a whole chunk (RREC_CHUNK_BYTES) and also checks the payload CRC. 0, -EBADMSG (header), -EILSEQ (payload). */
int rst_fmt_chunk_verify(const uint8_t *chunk, struct rst_chunk_hdr *h, uint32_t *payload_crc);

/* ---- event log record (FW l.1062) */
void rst_fmt_log_encode(const struct rrec_logrec *r, uint8_t *out);
int rst_fmt_log_decode(const uint8_t *in, struct rrec_logrec *r);

/* ---- digest (FW l.630): CRC-32 over the payload_crc32 values of all chunks in order, each as a 4-byte little-endian
 * word. State 0 at the start; add each chunk's payload CRC in order; the state after the last is the digest. */
uint32_t rst_fmt_digest_add(uint32_t state, uint32_t payload_crc);

/* CRC-32 (ISO-HDLC) of a buffer: Zephyr's crc32_ieee (FW l.70). */
uint32_t rst_fmt_crc32(const uint8_t *data, size_t len);

#endif
