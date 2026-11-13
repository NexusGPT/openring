/* rst_layout.c: the sector map and the free-space rules of the storage part (pure). Written for this project. */
#include "rst_layout.h"

uint32_t rst_lay_chunk_total(uint32_t sectors)
{
	if (sectors <= RREC_LBA_CHUNK_FIRST) {
		return 0;
	}
	return (sectors - RREC_LBA_CHUNK_FIRST) / RREC_CHUNK_SECTORS;
}

uint32_t rst_lay_chunk_lba(uint32_t total, uint32_t seq)
{
	if (total == 0) {
		return UINT32_MAX;
	}
	return RREC_LBA_CHUNK_FIRST + (seq % total) * RREC_CHUNK_SECTORS;
}

uint32_t rst_lay_index_lba(uint32_t n)
{
	return RREC_LBA_INDEX_FIRST + (n % RREC_INDEX_RING_RECORDS);
}

uint32_t rst_lay_log_lba(uint32_t seq)
{
	return RREC_LBA_LOG_FIRST + ((seq > 0 ? seq - 1u : 0u) % RREC_LOG_RING_RECORDS);
}

uint32_t rst_lay_sb_lba(uint32_t sb_seq)
{
	return sb_seq % 2u ? RREC_LBA_SB_B : RREC_LBA_SB_A;
}

void rst_lay_space(uint32_t total, uint32_t head, uint32_t tail, struct rst_space *out)
{
	uint32_t used = head >= tail ? head - tail : 0;

	out->total = total;
	out->used = used > total ? total : used;
	out->free_chunks = total - out->used;
	out->sfull = out->free_chunks <= RREC_SFULL_CHUNKS;
	out->s30 = out->free_chunks <= RREC_S30_CHUNKS;
	out->minutes_left = (uint32_t)(((uint64_t)out->free_chunks * RREC_CHUNK_MS) / (60u * 1000u));
}
