/* Suite store_log (unit U2): which superblock copy wins at mount (FW l.587). */
#include "tst.h"

ZTEST_SUITE(store_log, NULL, NULL, tst_before, NULL, NULL);

static struct rst_sb mk(uint32_t seq, uint32_t head)
{
	struct rst_sb s = { .sb_seq = seq, .card_sectors = 1000000, .chunk_first_lba = 81920,
			    .chunk_count_total = 14124, .head_chunk_seq = head, .tail_chunk_seq = 1,
			    .next_recording_id = 1, .index_head = 1, .index_tail = 1, .log_head = 1 };

	return s;
}

/* S14: both valid: the higher sb_seq wins; one bad CRC; one bad magic; both bad */
ZTEST(store_log, test_mount_picks_newer_valid_copy)
{
	uint8_t a[512], b[512];
	struct rst_sb s, out;
	int which;

	/* both valid, B newer */
	s = mk(4, 40);
	rst_fmt_sb_encode(&s, a);
	s = mk(5, 50);
	rst_fmt_sb_encode(&s, b);
	zassert_equal(rst_log_pick_sb(a, b, &out, &which), 0);
	zassert_equal(which, 1);
	zassert_equal(out.head_chunk_seq, 50u, "B (sb_seq 5) beats A (sb_seq 4)");

	/* both valid, A newer */
	s = mk(6, 60);
	rst_fmt_sb_encode(&s, a);
	zassert_equal(rst_log_pick_sb(a, b, &out, &which), 0);
	zassert_equal(which, 0);
	zassert_equal(out.head_chunk_seq, 60u, "A (sb_seq 6) beats B (sb_seq 5)");

	/* the newer one has a bad CRC: the older valid one wins */
	a[300] ^= 0x01;                               /* A is the newer (6) and now invalid */
	zassert_equal(rst_log_pick_sb(a, b, &out, &which), 0);
	zassert_equal(which, 1);
	zassert_equal(out.head_chunk_seq, 50u, "a copy with a bad CRC is not used");

	/* the newer one has a bad magic */
	s = mk(6, 60);
	rst_fmt_sb_encode(&s, a);
	a[0] ^= 0x01;
	zassert_equal(rst_log_pick_sb(a, b, &out, &which), 0);
	zassert_equal(which, 1);
	zassert_equal(out.sb_seq, 5u, "a copy with a bad magic is not used");

	/* only A valid */
	s = mk(2, 20);
	rst_fmt_sb_encode(&s, a);
	memset(b, 0, sizeof(b));
	zassert_equal(rst_log_pick_sb(a, b, &out, &which), 0);
	zassert_equal(which, 0);
	zassert_equal(out.head_chunk_seq, 20u);

	/* both bad */
	b[0] = 0x52;
	a[10] ^= 0xFF;
	zassert_equal(rst_log_pick_sb(a, b, &out, &which), -ENOENT);
	memset(a, 0, sizeof(a));
	memset(b, 0, sizeof(b));
	zassert_equal(rst_log_pick_sb(a, b, &out, &which), -ENOENT, "a blank card has no superblock");
}
