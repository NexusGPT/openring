/* Suite store_space (unit U2): free-space accounting (FW l.650 to l.654): counts, S30, SFULL, "storage left". */
#include "tst.h"

static struct {
	int s30, sfull;
	uint32_t s30_free, sfull_free;
} cbn;

static void on_s30(uint32_t f)
{
	cbn.s30++;
	cbn.s30_free = f;
}

static void on_sfull(uint32_t f)
{
	cbn.sfull++;
	cbn.sfull_free = f;
}

ZTEST_SUITE(store_space, NULL, NULL, tst_before, NULL, NULL);

/* S24: used = head - tail; free = total - used */
ZTEST(store_space, test_counts)
{
	struct rst_space sp;

	rst_lay_space(1000, 11, 1, &sp);
	zassert_equal(sp.total, 1000u);
	zassert_equal(sp.used, 10u);
	zassert_equal(sp.free_chunks, 990u);
	rst_lay_space(1000, 1, 1, &sp);
	zassert_equal(sp.used, 0u);
	zassert_equal(sp.free_chunks, 1000u);
	rst_lay_space(1000, 1001, 1, &sp);
	zassert_equal(sp.free_chunks, 0u);
	rst_lay_space(1000, 2500, 1, &sp);
	zassert_equal(sp.used, 1000u, "never more used than the card holds");
	zassert_equal(sp.free_chunks, 0u);
}

/* C3, S24: SFULL at or under 16 free chunks (FW l.651), S30 at or under 3,516 (FW l.652) */
ZTEST(store_space, test_s30_sfull_edges)
{
	struct rst_space sp;
	const uint32_t total = 10000;

	rst_lay_space(total, 1 + (total - 3517), 1, &sp);
	zassert_equal(sp.free_chunks, 3517u);
	zassert_false(sp.s30, "3,517 free: no S30");
	zassert_false(sp.sfull);
	rst_lay_space(total, 1 + (total - 3516), 1, &sp);
	zassert_equal(sp.free_chunks, 3516u);
	zassert_true(sp.s30, "3,516 free: S30");
	zassert_false(sp.sfull);
	rst_lay_space(total, 1 + (total - 17), 1, &sp);
	zassert_equal(sp.free_chunks, 17u);
	zassert_true(sp.s30);
	zassert_false(sp.sfull, "17 free: no SFULL");
	rst_lay_space(total, 1 + (total - 16), 1, &sp);
	zassert_equal(sp.free_chunks, 16u);
	zassert_true(sp.sfull, "16 free: SFULL");
	rst_lay_space(total, 1 + total, 1, &sp);
	zassert_equal(sp.free_chunks, 0u);
	zassert_true(sp.sfull);
}

/* S24: "storage left" = free x 0.512 s in whole minutes (FW l.653): 118,932 chunks = 60,893 s = 1,014 minutes */
ZTEST(store_space, test_storage_left_minutes)
{
	struct rst_space sp;

	rst_lay_space(118932, 1, 1, &sp);
	zassert_equal(sp.minutes_left, 1014u);
	rst_lay_space(109917, 1, 1, &sp);
	zassert_equal(sp.minutes_left, 937u, "109,917 x 0.512 s = 56,278 s = 937.97 minutes");
	rst_lay_space(1172, 1, 1, &sp);
	zassert_equal(sp.minutes_left, 10u, "1,172 x 0.512 = 600.06 s");
	rst_lay_space(1171, 1, 1, &sp);
	zassert_equal(sp.minutes_left, 9u, "1,171 x 0.512 = 599.55 s");
	rst_lay_space(100, 1, 1, &sp);
	zassert_equal(sp.minutes_left, 0u);
}

static struct rst_chunk big;

static void put_n(uint32_t id, uint32_t from, uint32_t n)
{
	for (uint32_t i = from; i < from + n; i++) {
		tst_fill(&big, id, i, 8192, i);
		zassert_equal(rst_put_chunk(&big, tst_done_cb), 0, "put %u", i);
		zassert_true(tst_wait_done((int)i + 1, 20000));
		zassert_equal(tst_done_last_err(), 0);
	}
}

/* S24, C15: S30 and SFULL are reported once per crossing while a recording runs (FW l.166, l.167) */
ZTEST(store_space, test_callbacks_once_per_crossing)
{
	struct rst_cb cb = { .s30 = on_s30, .sfull = on_sfull };
	struct rst_mount_info mi;
	struct rst_close_args a = { .duration_frames = 0 };
	struct rst_space sp;
	uint32_t id;

	memset(a.highlight_ms, 0xFF, sizeof(a.highlight_ms));
	memset(&cbn, 0, sizeof(cbn));

	/* S30: a card of 3,530 chunks; the 14th chunk takes the free count from 3,530 to 3,516 */
	tst_reset_cb(&cb);
	tst_card(3530);
	tst_mount_boot(&mi);
	zassert_equal(mi.space.total, 3530u);
	zassert_false(mi.space.s30);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	put_n(id, 0, 13);
	zassert_equal(cbn.s30, 0, "3,517 free");
	put_n(id, 13, 1);
	zassert_equal(cbn.s30, 1);
	zassert_equal(cbn.s30_free, 3516u);
	put_n(id, 14, 2);
	zassert_equal(cbn.s30, 1, "S30 once");
	zassert_equal(cbn.sfull, 0);
	zassert_equal(rst_close(NULL, &a), 0);
	zassert_equal(rst_space(&sp), 0);
	zassert_equal(sp.free_chunks, 3530u - 16u);
	zassert_true(sp.s30);

	/* SFULL: a card of 30 chunks (S30 is true from the start); the 14th chunk takes free from 30 to 16 */
	memset(&cbn, 0, sizeof(cbn));
	tst_reset_cb(&cb);
	tst_card(30);
	tst_mount_boot(&mi);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	put_n(id, 0, 13);
	zassert_equal(cbn.sfull, 0, "17 free");
	put_n(id, 13, 1);
	zassert_equal(cbn.sfull, 1);
	zassert_equal(cbn.sfull_free, 16u);
	zassert_equal(cbn.s30, 0, "a recording that opens under S30 is not told again");
	zassert_equal(rst_close(NULL, &a), 0);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), -ENOSPC, "no recording opens at SFULL");
	zassert_equal(rst_space(&sp), 0);
	zassert_true(sp.sfull);
}
