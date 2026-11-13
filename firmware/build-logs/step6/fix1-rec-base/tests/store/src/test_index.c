/* Suite store_index (unit U2): recordings rebuilt from the index records (FW l.612 to l.636), the CLOSE record's
 * highlights, and the list beyond the 256-entry cache (decision D16). */
#include "tst.h"

ZTEST_SUITE(store_index, NULL, NULL, tst_before, NULL, NULL);

static struct rst_ix mkix(uint8_t type, uint32_t number, uint32_t id, uint32_t first_seq, uint32_t count,
			  uint8_t close_state)
{
	struct rst_ix x = { .type = type, .close_state = close_state, .record_number = number, .recording_id = id,
			    .first_chunk_seq = first_seq, .chunk_count = count, .recording_type = 1, .channels = 2,
			    .sample_rate_hz = 16000, .digest = 0xD0000000u + id };

	memset(x.highlight_ms, 0xFF, sizeof(x.highlight_ms));
	return x;
}

static void put_ix(const struct rst_ix *x)
{
	uint8_t s[512];

	rst_fmt_ix_encode(x, s);
	rd_write(rst_lay_index_lba(x->record_number), s, 1);
}

/* S17: a recording's state is its last record: CLOSE = new, CONFIRM = transferred, DELETE = deleted; a recovered
 * recording shows RECOVERED until a CONFIRM (rst.h) */
ZTEST(store_index, test_state_is_last_record)
{
	struct rst_rec store[8];
	struct rst_recs t;
	struct rst_ix x;

	rd_reset();
	x = mkix(RREC_IX_TYPE_CLOSE, 1, 1, 1, 4, RREC_IX_CLOSE_COMPLETE);
	put_ix(&x);
	x = mkix(RREC_IX_TYPE_CLOSE, 2, 2, 5, 3, RREC_IX_CLOSE_RECOVERED);
	put_ix(&x);
	x = mkix(RREC_IX_TYPE_CLOSE, 3, 3, 8, 2, RREC_IX_CLOSE_COMPLETE);
	put_ix(&x);

	uint8_t sector[512];

	rst_recs_init(&t, store, 8);
	zassert_equal(rst_log_load_index(rd_read, NULL, 1, 4, &t, sector), 0);
	zassert_equal(t.live_total, 3u);
	zassert_equal(rst_recs_find(&t, 1)->info.state, RREC_LIST_STATE_NEW);
	zassert_equal(rst_recs_find(&t, 2)->info.state, RREC_LIST_STATE_RECOVERED);
	zassert_equal(rst_recs_find(&t, 3)->info.state, RREC_LIST_STATE_NEW);
	zassert_equal(rst_recs_find(&t, 2)->info.chunk_count, 3u);
	zassert_equal(rst_recs_find(&t, 2)->info.first_chunk_seq, 5u);
	zassert_equal(rst_recs_find(&t, 1)->info.digest, 0xD0000001u);

	/* CONFIRM of 1 and 2, DELETE of 1 */
	x = mkix(RREC_IX_TYPE_CONFIRM, 4, 1, 1, 4, 0);
	put_ix(&x);
	x = mkix(RREC_IX_TYPE_CONFIRM, 5, 2, 5, 3, 0);
	put_ix(&x);
	zassert_equal(rst_log_load_index(rd_read, NULL, 1, 6, &t, sector), 0);
	zassert_equal(rst_recs_find(&t, 1)->info.state, RREC_LIST_STATE_TRANSFERRED);
	zassert_equal(rst_recs_find(&t, 2)->info.state, RREC_LIST_STATE_TRANSFERRED, "a recovered recording once confirmed");
	zassert_equal(rst_recs_find(&t, 3)->info.state, RREC_LIST_STATE_NEW);
	x = mkix(RREC_IX_TYPE_DELETE, 6, 1, 1, 4, 0);
	put_ix(&x);
	zassert_equal(rst_log_load_index(rd_read, NULL, 1, 7, &t, sector), 0);
	zassert_true(rst_recs_find(&t, 1) == NULL, "a deleted recording is not listed");
	zassert_equal(t.live_total, 2u);
	zassert_equal(t.n, 2u);

	/* starting at the tail record 3 (record 1 and its records dropped): the orphan DELETE of id 1 is ignored */
	rd_reset();
	x = mkix(RREC_IX_TYPE_CLOSE, 3, 3, 8, 2, RREC_IX_CLOSE_COMPLETE);
	put_ix(&x);
	x = mkix(RREC_IX_TYPE_DELETE, 4, 1, 1, 4, 0);
	put_ix(&x);
	zassert_equal(rst_log_load_index(rd_read, NULL, 3, 5, &t, sector), 0);
	zassert_equal(t.live_total, 1u, "a DELETE for a recording before the tail changes nothing");
}

/* D16: a table of 4 holds the newest 4; the older live ones are read from the index; the count stays exact */
ZTEST(store_index, test_table_pushes_out_oldest_and_finds_on_demand)
{
	struct rst_rec store[4], win[8];
	struct rst_recs t;
	struct rst_ix x;
	uint8_t sector[512];
	uint32_t n = 0;

	rd_reset();
	for (uint32_t i = 1; i <= 10; i++) {
		x = mkix(RREC_IX_TYPE_CLOSE, i, i, i * 10, 2, RREC_IX_CLOSE_COMPLETE);
		put_ix(&x);
	}
	x = mkix(RREC_IX_TYPE_CONFIRM, 11, 2, 20, 2, 0);
	put_ix(&x);
	x = mkix(RREC_IX_TYPE_DELETE, 12, 3, 30, 2, 0);
	put_ix(&x);
	rst_recs_init(&t, store, 4);
	zassert_equal(rst_log_load_index(rd_read, NULL, 1, 13, &t, sector), 0);
	zassert_equal(t.n, 4u);
	zassert_equal(t.live_total, 9u, "10 closed, 1 deleted");
	zassert_equal(t.first_id, 1u);
	zassert_equal(t.evict_max_id, 6u, "ids 1 to 6 were pushed out");
	zassert_equal(t.ent[0].info.recording_id, 7u);
	zassert_equal(t.ent[3].info.recording_id, 10u);

	zassert_equal(rst_log_index_find(rd_read, NULL, 1, 13, 1, 8, win, &n, sector), 0);
	zassert_equal(n, 7u, "ids 1 to 8 minus the deleted 3: 7 of them");
	zassert_equal(win[0].info.recording_id, 1u);
	zassert_equal(win[1].info.recording_id, 2u);
	zassert_equal(win[1].info.state, RREC_LIST_STATE_TRANSFERRED, "id 2 was confirmed");
	zassert_equal(win[2].info.recording_id, 4u, "id 3 was deleted");
	zassert_equal(win[6].info.recording_id, 8u);

	/* a DELETE of a pushed-out recording lowers the exact count */
	x = mkix(RREC_IX_TYPE_DELETE, 13, 5, 50, 2, 0);
	rst_recs_apply(&t, &x);
	zassert_equal(t.live_total, 8u);
}

/* S11, decision D4: the CLOSE record keeps the first 32 highlights (ms from the start) and the full count */
ZTEST(store_index, test_close_highlights_32)
{
	struct rst_mount_info mi;
	struct rst_close_args a = { .duration_frames = 8192u * 2 };
	uint32_t id;
	uint8_t s[512];
	struct rst_ix x;
	static struct rst_chunk c;

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 1700000000000ll, &id), 0);
	tst_fill(&c, id, 0, 8192, 0);
	zassert_equal(rst_put_chunk(&c, tst_done_cb), 0);
	zassert_true(tst_wait_done(1, 1000));
	a.highlight_count = 40;
	for (uint32_t i = 0; i < 32; i++) {
		a.highlight_ms[i] = 100 * i + 7;
	}
	zassert_equal(rst_close(NULL, &a), 0);
	rhw_sim_disk_peek(8192 + 1, s);               /* the first index record: number 1 */
	zassert_equal(rst_fmt_ix_decode(s, &x), 0);
	zassert_equal(x.type, 1);
	zassert_equal(x.highlight_count, 40, "the full count");
	for (uint32_t i = 0; i < 32; i++) {
		zassert_equal(x.highlight_ms[i], 100 * i + 7, "highlight %u", i);
	}
	/* a ninth highlight in one chunk's header is refused by the store (the header holds 8, decision D4) */
	tst_fill(&c, id, 1, 8192, 1);
	c.hdr.highlight_count = 9;
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	zassert_equal(rst_put_chunk(&c, tst_done_cb), -EINVAL);
	zassert_equal(rst_close(NULL, &a), 0);
}

/* D16, S17: 300 recordings (the table holds 256): list, confirm and delete work on the ones pushed out of it */
ZTEST(store_index, test_list_beyond_cache_reads_index)
{
	struct rst_mount_info mi;
	uint32_t id, freed;
	static struct rst_rec_info li[64];
	uint16_t n = 0;

	tst_card(100);
	tst_mount_boot(&mi);
	for (uint32_t i = 1; i <= 300; i++) {
		zassert_equal(tst_record(RREC_REC_TYPE_RECORDING, 0, &id, NULL), 0, "recording %u", i);
		zassert_equal(id, i);
	}
	tst_reboot();
	tst_mount_boot(&mi);
	zassert_equal(mi.recordings, 300u);

	zassert_equal(rst_list(0, 64, li, &n), 0);
	zassert_equal(n, 64);
	zassert_equal(li[0].recording_id, 1u, "from the index: older than the table");
	zassert_equal(li[63].recording_id, 64u, "ids 1 to 44 from the index, 45 to 64 from the table");
	zassert_equal(li[43].recording_id, 44u);
	zassert_equal(li[44].recording_id, 45u);
	zassert_equal(rst_list(290, 64, li, &n), 0);
	zassert_equal(n, 11);
	zassert_equal(li[10].recording_id, 300u);

	/* the digest of a recording without chunks is the CRC-32 of nothing: 0 */
	zassert_equal(rst_confirm(2, 5), -EBADMSG);
	zassert_equal(rst_confirm(2, 0), 0);
	zassert_equal(rst_list(2, 1, li, &n), 0);
	zassert_equal(li[0].state, RREC_LIST_STATE_TRANSFERRED);
	zassert_equal(rst_delete(2, &freed), 0);
	zassert_equal(rst_list(0, 3, li, &n), 0);
	zassert_equal(n, 3);
	zassert_equal(li[0].recording_id, 1u);
	zassert_equal(li[1].recording_id, 3u, "2 is deleted");
	zassert_equal(rst_delete(1, &freed), -EACCES);

	tst_reboot();
	tst_mount_boot(&mi);
	zassert_equal(mi.recordings, 299u, "the count after a remount");
}
