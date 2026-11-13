/*
 * rst_fmt.c: the byte formats of the storage part (pure: stdint, stdbool, string, errno constants and the CRC-32 of
 * Zephyr's C library only). Chunk header FW l.537 to l.580, superblock l.587 to l.610, index record l.612 to l.634,
 * event log record l.1062. Written for this project.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/sys/crc.h>

#include "rst_fmt.h"

uint32_t rst_fmt_crc32(const uint8_t *data, size_t len)
{
	return crc32_ieee(data, len);
}

uint32_t rst_fmt_digest_add(uint32_t state, uint32_t payload_crc)
{
	uint8_t w[sizeof(uint32_t)];

	w[0] = (uint8_t)(payload_crc >> 24); w[1] = (uint8_t)(payload_crc >> 16); w[2] = (uint8_t)(payload_crc >> 8); w[3] = (uint8_t)payload_crc;
	return crc32_ieee_update(state, w, sizeof(w));
}

/* ------------------------------------------------------------------ superblock */

void rst_fmt_sb_encode(const struct rst_sb *s, uint8_t *out)
{
	memset(out, 0, RREC_SECTOR_BYTES);
	rst_put32(out + RREC_SB_OFF_MAGIC, RREC_SB_MAGIC);
	rst_put16(out + RREC_SB_OFF_VERSION, RREC_SB_VERSION);
	rst_put16(out + RREC_SB_OFF_SIZE, RREC_SECTOR_BYTES);
	rst_put32(out + RREC_SB_OFF_SB_SEQ, s->sb_seq);
	rst_put32(out + RREC_SB_OFF_CARD_SECTORS, s->card_sectors);
	rst_put32(out + RREC_SB_OFF_CHUNK_FIRST_LBA, s->chunk_first_lba);
	rst_put32(out + RREC_SB_OFF_CHUNK_COUNT_TOTAL, s->chunk_count_total);
	rst_put32(out + RREC_SB_OFF_HEAD_CHUNK_SEQ, s->head_chunk_seq);
	rst_put32(out + RREC_SB_OFF_TAIL_CHUNK_SEQ, s->tail_chunk_seq);
	rst_put32(out + RREC_SB_OFF_NEXT_RECORDING_ID, s->next_recording_id);
	rst_put32(out + RREC_SB_OFF_INDEX_HEAD, s->index_head);
	rst_put32(out + RREC_SB_OFF_INDEX_TAIL, s->index_tail);
	out[RREC_SB_OFF_OPEN_FLAG] = s->open_flag;
	rst_put32(out + RREC_SB_OFF_OPEN_RECORDING_ID, s->open_recording_id);
	rst_put32(out + RREC_SB_OFF_OPEN_FIRST_CHUNK, s->open_first_chunk_seq);
	rst_put32(out + RREC_SB_OFF_BOOT_COUNT, s->boot_count);
	rst_put32(out + RREC_SB_OFF_LOG_HEAD, s->log_head);
	rst_put32(out + RREC_SB_OFF_CRC, crc32_ieee(out, RREC_SB_OFF_CRC));
}

int rst_fmt_sb_decode(const uint8_t *in, struct rst_sb *s)
{
	if (rst_get32(in + RREC_SB_OFF_MAGIC) != RREC_SB_MAGIC ||
	    rst_get16(in + RREC_SB_OFF_VERSION) != RREC_SB_VERSION ||
	    rst_get16(in + RREC_SB_OFF_SIZE) != RREC_SECTOR_BYTES ||
	    rst_get32(in + RREC_SB_OFF_CRC) != crc32_ieee(in, RREC_SB_OFF_CRC)) {
		return -EBADMSG;
	}
	s->sb_seq = rst_get32(in + RREC_SB_OFF_SB_SEQ);
	s->card_sectors = rst_get32(in + RREC_SB_OFF_CARD_SECTORS);
	s->chunk_first_lba = rst_get32(in + RREC_SB_OFF_CHUNK_FIRST_LBA);
	s->chunk_count_total = rst_get32(in + RREC_SB_OFF_CHUNK_COUNT_TOTAL);
	s->head_chunk_seq = rst_get32(in + RREC_SB_OFF_HEAD_CHUNK_SEQ);
	s->tail_chunk_seq = rst_get32(in + RREC_SB_OFF_TAIL_CHUNK_SEQ);
	s->next_recording_id = rst_get32(in + RREC_SB_OFF_NEXT_RECORDING_ID);
	s->index_head = rst_get32(in + RREC_SB_OFF_INDEX_HEAD);
	s->index_tail = rst_get32(in + RREC_SB_OFF_INDEX_TAIL);
	s->open_flag = in[RREC_SB_OFF_OPEN_FLAG];
	s->open_recording_id = rst_get32(in + RREC_SB_OFF_OPEN_RECORDING_ID);
	s->open_first_chunk_seq = rst_get32(in + RREC_SB_OFF_OPEN_FIRST_CHUNK);
	s->boot_count = rst_get32(in + RREC_SB_OFF_BOOT_COUNT);
	s->log_head = rst_get32(in + RREC_SB_OFF_LOG_HEAD);
	return 0;
}

/* ------------------------------------------------------------------ index record */

void rst_fmt_ix_encode(const struct rst_ix *r, uint8_t *out)
{
	memset(out, 0, RREC_SECTOR_BYTES);
	rst_put32(out + RREC_IX_OFF_MAGIC, RREC_IX_MAGIC);
	rst_put16(out + RREC_IX_OFF_VERSION, RREC_IX_VERSION);
	out[RREC_IX_OFF_TYPE] = r->type;
	out[RREC_IX_OFF_CLOSE_STATE] = r->close_state;
	rst_put32(out + RREC_IX_OFF_RECORD_NUMBER, r->record_number);
	rst_put32(out + RREC_IX_OFF_RECORDING_ID, r->recording_id);
	rst_put32(out + RREC_IX_OFF_FIRST_CHUNK_SEQ, r->first_chunk_seq);
	rst_put32(out + RREC_IX_OFF_CHUNK_COUNT, r->chunk_count);
	out[RREC_IX_OFF_RECORDING_TYPE] = r->recording_type;
	out[RREC_IX_OFF_CHANNELS] = r->channels;
	rst_put16(out + RREC_IX_OFF_HIGHLIGHT_COUNT, r->highlight_count);
	rst_put32(out + RREC_IX_OFF_SAMPLE_RATE, r->sample_rate_hz);
	rst_put64(out + RREC_IX_OFF_START_UTC_MS, (uint64_t)r->start_utc_ms);
	rst_put64(out + RREC_IX_OFF_DURATION_FRAMES, r->duration_frames);
	rst_put32(out + RREC_IX_OFF_DIGEST, r->digest);
	for (uint32_t i = 0; i < RREC_CLOSE_HIGHLIGHTS; i++) {
		rst_put32(out + RREC_IX_OFF_HIGHLIGHT_MS + i * sizeof(uint32_t), r->highlight_ms[i]);
	}
	rst_put32(out + RREC_IX_OFF_CRC, crc32_ieee(out, RREC_IX_OFF_CRC));
}

int rst_fmt_ix_decode(const uint8_t *in, struct rst_ix *r)
{
	if (rst_get32(in + RREC_IX_OFF_MAGIC) != RREC_IX_MAGIC ||
	    rst_get16(in + RREC_IX_OFF_VERSION) != RREC_IX_VERSION ||
	    rst_get32(in + RREC_IX_OFF_CRC) != crc32_ieee(in, RREC_IX_OFF_CRC)) {
		return -EBADMSG;
	}
	r->type = in[RREC_IX_OFF_TYPE];
	r->close_state = in[RREC_IX_OFF_CLOSE_STATE];
	r->record_number = rst_get32(in + RREC_IX_OFF_RECORD_NUMBER);
	r->recording_id = rst_get32(in + RREC_IX_OFF_RECORDING_ID);
	r->first_chunk_seq = rst_get32(in + RREC_IX_OFF_FIRST_CHUNK_SEQ);
	r->chunk_count = rst_get32(in + RREC_IX_OFF_CHUNK_COUNT);
	r->recording_type = in[RREC_IX_OFF_RECORDING_TYPE];
	r->channels = in[RREC_IX_OFF_CHANNELS];
	r->highlight_count = rst_get16(in + RREC_IX_OFF_HIGHLIGHT_COUNT);
	r->sample_rate_hz = rst_get32(in + RREC_IX_OFF_SAMPLE_RATE);
	r->start_utc_ms = (int64_t)rst_get64(in + RREC_IX_OFF_START_UTC_MS);
	r->duration_frames = rst_get64(in + RREC_IX_OFF_DURATION_FRAMES);
	r->digest = rst_get32(in + RREC_IX_OFF_DIGEST);
	for (uint32_t i = 0; i < RREC_CLOSE_HIGHLIGHTS; i++) {
		r->highlight_ms[i] = rst_get32(in + RREC_IX_OFF_HIGHLIGHT_MS + i * sizeof(uint32_t));
	}
	return 0;
}

/* ------------------------------------------------------------------ chunk */

/* the header CRC-32 over header bytes 0 to 507 (FW l.580), for the encoder and the decoder alike */
static uint32_t chunk_hdr_crc(const uint8_t *h)
{
	return crc32_ieee(h, RREC_CH_OFF_HEADER_CRC);
}

bool rst_fmt_chunk_hdr_valid(const struct rst_chunk_hdr *h)
{
	return h->frames != 0 && h->frames <= RREC_CHUNK_FRAMES && h->highlight_count <= RREC_HIGHLIGHTS_PER_CHUNK &&
	       h->motor_count <= RREC_MOTOR_PER_CHUNK;
}

int rst_fmt_chunk_encode(struct rst_chunk *c, uint32_t *payload_crc)
{
	const struct rst_chunk_hdr *h = &c->hdr;
	uint8_t *o = c->bytes;
	uint8_t *payload = c->bytes + RREC_CHUNK_HEADER_BYTES;
	uint32_t pcrc;

	if (!rst_fmt_chunk_hdr_valid(h)) {
		return -EINVAL;
	}
	/* unused payload bytes of a last chunk are zero (FW l.535) */
	memset(payload + (size_t)h->frames * RREC_CHANNELS * sizeof(int16_t), 0,
	       RREC_CHUNK_PAYLOAD_BYTES - (size_t)h->frames * RREC_CHANNELS * sizeof(int16_t));
	pcrc = crc32_ieee(payload, RREC_CHUNK_PAYLOAD_BYTES);

	memset(o, 0, RREC_CHUNK_HEADER_BYTES);
	rst_put32(o + RREC_CH_OFF_MAGIC, RREC_CHUNK_MAGIC);
	rst_put16(o + RREC_CH_OFF_VERSION, RREC_CHUNK_HEADER_VERSION);
	rst_put16(o + RREC_CH_OFF_SIZE, RREC_CHUNK_HEADER_BYTES);
	rst_put32(o + RREC_CH_OFF_CHUNK_SEQ, h->chunk_seq);
	rst_put32(o + RREC_CH_OFF_RECORDING_ID, h->recording_id);
	rst_put32(o + RREC_CH_OFF_CHUNK_IN_REC, h->chunk_in_recording);
	rst_put16(o + RREC_CH_OFF_FLAGS, h->flags);
	o[RREC_CH_OFF_RECORDING_TYPE] = h->recording_type;
	o[RREC_CH_OFF_CHANNELS] = RREC_CHANNELS;
	rst_put32(o + RREC_CH_OFF_SAMPLE_RATE, RREC_PCM_RATE_HZ);
	o[RREC_CH_OFF_SAMPLE_FORMAT] = RREC_SAMPLE_FORMAT_S16LE;
	o[RREC_CH_OFF_MIC_MASK] = RREC_MIC_MASK;
	rst_put32(o + RREC_CH_OFF_FRAMES, h->frames);
	rst_put32(o + RREC_CH_OFF_PAYLOAD_BYTES, h->frames * RREC_CHANNELS * (uint32_t)sizeof(int16_t));
	rst_put64(o + RREC_CH_OFF_FIRST_FRAME_INDEX, h->first_frame_index);
	rst_put64(o + RREC_CH_OFF_UTC_MS, (uint64_t)h->utc_ms);
	rst_put64(o + RREC_CH_OFF_UPTIME_NS, h->uptime_ns);
	rst_put32(o + RREC_CH_OFF_PDM_CLOCK_HZ, RREC_PDM_CLOCK_HZ);
	rst_put16(o + RREC_CH_OFF_PDM_RATIO, RREC_PDM_RATIO);
	o[RREC_CH_OFF_GAIN_CODE] = RREC_PDM_GAIN_CODE;
	rst_put16(o + RREC_CH_OFF_HIGHLIGHT_COUNT, h->highlight_count);
	for (uint32_t i = 0; i < RREC_HIGHLIGHTS_PER_CHUNK; i++) {
		rst_put32(o + RREC_CH_OFF_HIGHLIGHT_FRAME + i * sizeof(uint32_t),
			  i < h->highlight_count ? h->highlight_frame[i] : RREC_UNUSED_U32);
	}
	rst_put16(o + RREC_CH_OFF_BATTERY_MV, h->battery_mv);
	rst_put16(o + RREC_CH_OFF_TEMP_C_X10, (uint16_t)h->temp_c_x10);
	rst_put32(o + RREC_CH_OFF_BOOT_COUNT, h->boot_count);
	rst_put32(o + RREC_CH_OFF_DROPOUT_BLOCKS, h->dropout_blocks);
	rst_put32(o + RREC_CH_OFF_FW_VERSION, h->fw_version);
	rst_put32(o + RREC_CH_OFF_CYCLE_HZ, h->cycle_hz);
	rst_put16(o + RREC_CH_OFF_MOTOR_COUNT, h->motor_count);
	for (uint32_t i = 0; i < RREC_MOTOR_PER_CHUNK; i++) {
		uint8_t *p = o + RREC_CH_OFF_MOTOR_FRAMES + i * 2 * sizeof(uint32_t);

		rst_put32(p, i < h->motor_count ? h->motor_frames[i][0] : RREC_UNUSED_U32);
		rst_put32(p + sizeof(uint32_t), i < h->motor_count ? h->motor_frames[i][1] : RREC_UNUSED_U32);
	}
	rst_put32(o + RREC_CH_OFF_PAYLOAD_CRC, pcrc);
	rst_put32(o + RREC_CH_OFF_HEADER_CRC, chunk_hdr_crc(o));
	if (payload_crc != NULL) {
		*payload_crc = pcrc;
	}
	return 0;
}

int rst_fmt_chunk_hdr_decode(const uint8_t *in, struct rst_chunk_hdr *h, uint32_t *payload_crc)
{
	if (rst_get32(in + RREC_CH_OFF_MAGIC) != RREC_CHUNK_MAGIC ||
	    rst_get16(in + RREC_CH_OFF_VERSION) != RREC_CHUNK_HEADER_VERSION ||
	    rst_get16(in + RREC_CH_OFF_SIZE) != RREC_CHUNK_HEADER_BYTES ||
	    rst_get32(in + RREC_CH_OFF_HEADER_CRC) != chunk_hdr_crc(in)) {
		return -EBADMSG;
	}
	h->chunk_seq = rst_get32(in + RREC_CH_OFF_CHUNK_SEQ);
	h->recording_id = rst_get32(in + RREC_CH_OFF_RECORDING_ID);
	h->chunk_in_recording = rst_get32(in + RREC_CH_OFF_CHUNK_IN_REC);
	h->flags = rst_get16(in + RREC_CH_OFF_FLAGS);
	h->recording_type = in[RREC_CH_OFF_RECORDING_TYPE];
	h->frames = rst_get32(in + RREC_CH_OFF_FRAMES);
	h->first_frame_index = rst_get64(in + RREC_CH_OFF_FIRST_FRAME_INDEX);
	h->utc_ms = (int64_t)rst_get64(in + RREC_CH_OFF_UTC_MS);
	h->uptime_ns = rst_get64(in + RREC_CH_OFF_UPTIME_NS);
	h->highlight_count = rst_get16(in + RREC_CH_OFF_HIGHLIGHT_COUNT);
	for (uint32_t i = 0; i < RREC_HIGHLIGHTS_PER_CHUNK; i++) {
		h->highlight_frame[i] = rst_get32(in + RREC_CH_OFF_HIGHLIGHT_FRAME + i * sizeof(uint32_t));
	}
	h->battery_mv = rst_get16(in + RREC_CH_OFF_BATTERY_MV);
	h->temp_c_x10 = (int16_t)rst_get16(in + RREC_CH_OFF_TEMP_C_X10);
	h->boot_count = rst_get32(in + RREC_CH_OFF_BOOT_COUNT);
	h->dropout_blocks = rst_get32(in + RREC_CH_OFF_DROPOUT_BLOCKS);
	h->fw_version = rst_get32(in + RREC_CH_OFF_FW_VERSION);
	h->cycle_hz = rst_get32(in + RREC_CH_OFF_CYCLE_HZ);
	h->motor_count = rst_get16(in + RREC_CH_OFF_MOTOR_COUNT);
	for (uint32_t i = 0; i < RREC_MOTOR_PER_CHUNK; i++) {
		const uint8_t *p = in + RREC_CH_OFF_MOTOR_FRAMES + i * 2 * sizeof(uint32_t);

		h->motor_frames[i][0] = rst_get32(p);
		h->motor_frames[i][1] = rst_get32(p + sizeof(uint32_t));
	}
	if (payload_crc != NULL) {
		*payload_crc = rst_get32(in + RREC_CH_OFF_PAYLOAD_CRC);
	}
	return 0;
}

int rst_fmt_chunk_verify(const uint8_t *chunk, struct rst_chunk_hdr *h, uint32_t *payload_crc)
{
	uint32_t pcrc;
	int r = rst_fmt_chunk_hdr_decode(chunk, h, &pcrc);

	if (r != 0) {
		return r;
	}
	if (crc32_ieee(chunk + RREC_CHUNK_HEADER_BYTES, RREC_CHUNK_PAYLOAD_BYTES) != pcrc) {
		return -EILSEQ;
	}
	if (payload_crc != NULL) {
		*payload_crc = pcrc;
	}
	return 0;
}

/* ------------------------------------------------------------------ event log record */

void rst_fmt_log_encode(const struct rrec_logrec *r, uint8_t *out)
{
	memset(out, 0, RREC_LOG_RECORD_BYTES);
	rst_put32(out + RREC_LG_OFF_MAGIC, RREC_LOG_MAGIC);
	rst_put32(out + RREC_LG_OFF_SEQ, r->seq);
	rst_put64(out + RREC_LG_OFF_UPTIME_NS, (uint64_t)r->uptime_ns);
	rst_put64(out + RREC_LG_OFF_UTC_MS, (uint64_t)r->utc_ms);
	rst_put16(out + RREC_LG_OFF_CODE, r->code);
	out[RREC_LG_OFF_STATE] = r->state;
	memcpy(out + RREC_LG_OFF_ARGS, r->args, RREC_LOG_ARG_BYTES);
	if (r->has_crash) {
		uint8_t *p = out + RREC_LG_OFF_CRASH;

		rst_put32(p, r->crash.reason);
		rst_put32(p + 4, r->crash.pc);
		rst_put32(p + 8, r->crash.lr);
		rst_put32(p + 12, r->crash.psr);
		p += 16;
		memcpy(p, r->crash.thread, RREC_CRASH_NAME_BYTES);
		p += RREC_CRASH_NAME_BYTES;
		for (uint32_t i = 0; i < RREC_CRASH_STACK_WORDS; i++) {
			rst_put32(p + i * sizeof(uint32_t), r->crash.stack[i]);
		}
	}
	rst_put32(out + RREC_LG_OFF_CRC, crc32_ieee(out, RREC_LG_OFF_CRC));
}

int rst_fmt_log_decode(const uint8_t *in, struct rrec_logrec *r)
{
	if (rst_get32(in + RREC_LG_OFF_MAGIC) != RREC_LOG_MAGIC ||
	    rst_get32(in + RREC_LG_OFF_CRC) != crc32_ieee(in, RREC_LG_OFF_CRC)) {
		return -EBADMSG;
	}
	memset(r, 0, sizeof(*r));
	r->seq = rst_get32(in + RREC_LG_OFF_SEQ);
	r->uptime_ns = (int64_t)rst_get64(in + RREC_LG_OFF_UPTIME_NS);
	r->utc_ms = (int64_t)rst_get64(in + RREC_LG_OFF_UTC_MS);
	r->code = rst_get16(in + RREC_LG_OFF_CODE);
	r->state = in[RREC_LG_OFF_STATE];
	memcpy(r->args, in + RREC_LG_OFF_ARGS, RREC_LOG_ARG_BYTES);
	const uint8_t *p = in + RREC_LG_OFF_CRASH;

	for (uint32_t i = 0; i < RREC_CRASH_BLOCK_BYTES; i++) {
		if (p[i] != 0) {
			r->has_crash = true;
			break;
		}
	}
	if (r->has_crash) {
		r->crash.reason = rst_get32(p);
		r->crash.pc = rst_get32(p + 4);
		r->crash.lr = rst_get32(p + 8);
		r->crash.psr = rst_get32(p + 12);
		p += 16;
		memcpy(r->crash.thread, p, RREC_CRASH_NAME_BYTES);
		p += RREC_CRASH_NAME_BYTES;
		for (uint32_t i = 0; i < RREC_CRASH_STACK_WORDS; i++) {
			r->crash.stack[i] = rst_get32(p + i * sizeof(uint32_t));
		}
	}
	return 0;
}
