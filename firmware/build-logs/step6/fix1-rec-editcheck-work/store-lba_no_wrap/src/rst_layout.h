/*
 * rst_layout.h: where things lie on the card and how much is free (pure: no kernel call). FW l.519 to l.531
 * (sector map), l.650 to l.654 (free space). Not a public header.
 */
#ifndef RST_LAYOUT_H
#define RST_LAYOUT_H

#include <stdbool.h>
#include <stdint.h>

#include <ring_store/rst.h>

/* chunk_count_total = floor((sectors - first chunk LBA) / chunk sectors) (FW l.529); 0 when the card is too small. */
uint32_t rst_lay_chunk_total(uint32_t sectors);
/* First sector of chunk number seq: first chunk LBA + (seq mod total) x chunk sectors (FW l.531). UINT32_MAX when
 * total is 0. */
uint32_t rst_lay_chunk_lba(uint32_t total, uint32_t seq);
/* Index record n at first index LBA + (n mod RREC_INDEX_RING_RECORDS) (FW l.612). */
uint32_t rst_lay_index_lba(uint32_t n);
/* Event log record seq (first seq 1) in the ring of RREC_LOG_RING_RECORDS from RREC_LBA_LOG_FIRST (FW l.525): record 1
 * is in LBA 2, record 2,046 in LBA 2,047, record 2,047 in LBA 2 again. */
uint32_t rst_lay_log_lba(uint32_t seq);
/* A superblock is written to LBA sb_seq mod 2 (FW l.587). */
uint32_t rst_lay_sb_lba(uint32_t sb_seq);
/* Used = head - tail; free = total - used; S30 and SFULL at or under their limits; minutes left = free x 0.512 s
 * rounded down (FW l.650 to l.653). */
void rst_lay_space(uint32_t total, uint32_t head, uint32_t tail, struct rst_space *out);

#endif
