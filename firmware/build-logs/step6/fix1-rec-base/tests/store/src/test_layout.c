/* Suite store_layout (unit U2): the sector map of design/firmware.md 5.2 and the examples of 5.6. */
#include "tst.h"

ZTEST_SUITE(store_layout, NULL, NULL, tst_before, NULL, NULL);

/* S4: sector map (FW l.519 to l.531): superblock A at 0, B at 1, log 2 to 2,047, index 8,192 to 73,727, chunks from 81,920 */
ZTEST(store_layout, test_sector_map)
{
	zassert_equal(rst_lay_sb_lba(0), 0u);
	zassert_equal(rst_lay_sb_lba(1), 1u);
	zassert_equal(rst_lay_sb_lba(6), 0u);
	zassert_equal(rst_lay_sb_lba(7), 1u, "the superblock goes to LBA sb_seq mod 2 (FW l.587)");
	zassert_equal(rst_lay_log_lba(1), 2u, "the first record is in the first sector of the log area");
	zassert_equal(rst_lay_log_lba(2), 3u);
	zassert_equal(rst_lay_log_lba(2046), 2047u, "the last sector of the log area");
	zassert_equal(rst_lay_index_lba(0), 8192u);
	zassert_equal(rst_lay_index_lba(65535), 73727u);
	zassert_equal(rst_lay_chunk_total(81920), 0u, "no room for a chunk");
	zassert_equal(rst_lay_chunk_total(81920 + 64), 0u, "64 sectors do not hold a chunk of 65");
	zassert_equal(rst_lay_chunk_total(81920 + 65), 1u);
	zassert_equal(rst_lay_chunk_total(81920 + 130), 2u);
	zassert_equal(rst_lay_chunk_total(100), 0u, "a card smaller than the metadata areas");
	zassert_equal(rst_lay_chunk_lba(10, 0), 81920u);
	zassert_equal(rst_lay_chunk_lba(10, 1), 81920u + 65u);
	zassert_equal(rst_lay_chunk_lba(10, 9), 81920u + 9u * 65u);
	zassert_equal(rst_lay_chunk_lba(0, 5), UINT32_MAX);
}

/* S4: chunk s starts at 81,920 + (s mod total) x 65 (FW l.531) */
ZTEST(store_layout, test_chunk_lba_wraps)
{
	const uint32_t total = 118932;          /* the 4 GB example of FW l.654 */

	zassert_equal(rst_lay_chunk_lba(total, total - 1), 81920u + 118931u * 65u);
	zassert_equal(rst_lay_chunk_lba(total, total), 81920u, "s = total wraps to the first chunk");
	zassert_equal(rst_lay_chunk_lba(total, total + 1), 81920u + 65u);
	zassert_equal(rst_lay_chunk_lba(total, 2 * total + 5), 81920u + 5u * 65u);
	zassert_equal(rst_lay_chunk_lba(7, 6), 81920u + 6u * 65u);
	zassert_equal(rst_lay_chunk_lba(7, 7), 81920u);
	zassert_equal(rst_lay_chunk_lba(7, 8), 81920u + 65u);
}

/* S4: the examples of FW l.654: 7,812,500 sectors give 118,932 chunks; 7,226,562 give 109,917 */
ZTEST(store_layout, test_examples)
{
	zassert_equal(rst_lay_chunk_total(7812500), 118932u);
	zassert_equal(rst_lay_chunk_total(7226562), 109917u);
}

/* S15: index record n at 8,192 + (n mod 65,536) (FW l.612) */
ZTEST(store_layout, test_index_lba_wraps)
{
	zassert_equal(rst_lay_index_lba(65536), 8192u);
	zassert_equal(rst_lay_index_lba(65537), 8193u);
	zassert_equal(rst_lay_index_lba(3), 8195u);
	zassert_equal(rst_lay_index_lba(131071), 73727u);
}
