/* Suite store_delete (unit U2): CONFIRM, DELETE and the tail (FW l.658 to l.661). */
#include "tst.h"

ZTEST_SUITE(store_delete, NULL, NULL, tst_before, NULL, NULL);

static int recs(uint32_t n, uint32_t chunks_each, uint32_t *ids, uint32_t *digests)
{
	for (uint32_t i = 0; i < n; i++) {
		int r = tst_record(RREC_REC_TYPE_RECORDING, chunks_each, &ids[i], &digests[i]);

		if (r != 0) {
			return r;
		}
	}
	return 0;
}

static uint32_t count_index_records(void)
{
	struct rst_space sp;
	uint8_t s[512];
	struct rst_ix x;
	uint32_t n = 0;

	zassert_equal(rst_space(&sp), 0);
	for (uint32_t i = 1; i < 200; i++) {
		rhw_sim_disk_peek(8192 + i, s);
		if (rst_fmt_ix_decode(s, &x) == 0 && x.record_number == i) {
			n++;
		}
	}
	return n;
}

/* S26: CONFIRM compares the case's digest with the CLOSE digest: match appends CONFIRM; no match changes nothing */
ZTEST(store_delete, test_confirm_match_and_mismatch)
{
	struct rst_mount_info mi;
	uint32_t ids[1], dg[1];
	static struct rst_rec_info li[2];
	uint16_t n;

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(recs(1, 2, ids, dg), 0);
	zassert_equal(count_index_records(), 1u, "the CLOSE record");

	zassert_equal(rst_confirm(ids[0], dg[0] ^ 1u), -EBADMSG, "DIGEST_MISMATCH");
	zassert_equal(count_index_records(), 1u, "nothing appended");
	zassert_equal(rst_list(0, 1, li, &n), 0);
	zassert_equal(li[0].state, RREC_LIST_STATE_NEW, "nothing changed");
	zassert_equal(li[0].digest, dg[0], "the CLOSE digest is the reference digest");

	zassert_equal(rst_confirm(ids[0], dg[0]), 0);
	zassert_equal(count_index_records(), 2u, "a CONFIRM record");
	zassert_equal(rst_list(0, 1, li, &n), 0);
	zassert_equal(li[0].state, RREC_LIST_STATE_TRANSFERRED);
	zassert_equal(rst_confirm(99, dg[0]), -ENOENT);

	tst_reboot();
	tst_mount_boot(&mi);
	zassert_equal(rst_list(0, 1, li, &n), 0);
	zassert_equal(li[0].state, RREC_LIST_STATE_TRANSFERRED, "the CONFIRM survives a restart");
}

/* S27: DELETE is refused without a CONFIRM record (NOT_CONFIRMED, FW l.659) */
ZTEST(store_delete, test_delete_needs_confirm)
{
	struct rst_mount_info mi;
	uint32_t ids[1], dg[1], freed = 0;
	struct rst_space sp;

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(recs(1, 2, ids, dg), 0);
	zassert_equal(rst_delete(ids[0], &freed), -EACCES);
	zassert_equal(count_index_records(), 1u, "no DELETE record");
	zassert_equal(rst_space(&sp), 0);
	zassert_equal(sp.used, 2u, "nothing freed");
	zassert_equal(rst_delete(77, &freed), -ENOENT);
	zassert_equal(rst_confirm(ids[0], dg[0]), 0);
	zassert_equal(rst_delete(ids[0], &freed), 0);
	zassert_equal(freed, 100u, "free chunks after the deletion");
}

/* S28: DELETE appends a record and moves the tail over the leading deleted recordings only; a deleted recording in
 * the middle stays counted as used (FW l.660) */
ZTEST(store_delete, test_tail_moves_over_leading_only)
{
	struct rst_mount_info mi;
	uint32_t ids[3], dg[3], freed = 0;
	struct rst_space sp;
	static struct rst_rec_info li[4];
	uint16_t n;

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(recs(3, 2, ids, dg), 0);
	for (int i = 0; i < 3; i++) {
		zassert_equal(rst_confirm(ids[i], dg[i]), 0);
	}
	zassert_equal(rst_space(&sp), 0);
	zassert_equal(sp.free_chunks, 100u - 6u);

	zassert_equal(rst_delete(ids[1], &freed), 0, "the second of three");
	zassert_equal(freed, 94u, "free unchanged: the deleted recording is in the middle");
	zassert_equal(rst_space(&sp), 0);
	zassert_equal(sp.free_chunks, 94u);
	zassert_equal(rst_list(0, 4, li, &n), 0);
	zassert_equal(n, 2);
	zassert_equal(li[0].recording_id, ids[0]);
	zassert_equal(li[1].recording_id, ids[2]);

	tst_reboot();
	tst_mount_boot(&mi);
	zassert_equal(mi.space.free_chunks, 94u, "also after a restart");
	zassert_equal(mi.recordings, 2u);

	zassert_equal(rst_delete(ids[0], &freed), 0, "now the first");
	zassert_equal(freed, 98u, "the first and the deleted second are freed: 4 chunks");
	zassert_equal(rst_space(&sp), 0);
	zassert_equal(sp.used, 2u, "only the third remains");

	tst_reboot();
	tst_mount_boot(&mi);
	zassert_equal(mi.space.free_chunks, 98u, "the tail is on the card");
	zassert_equal(mi.recordings, 1u);
	zassert_equal(rst_delete(ids[2], &freed), 0);
	zassert_equal(freed, 100u, "all freed");
	zassert_equal(rst_list(0, 4, li, &n), 0);
	zassert_equal(n, 0);
}

/* S29: audio sectors are not erased; READ_RANGE's store call refuses a deleted recording (FW l.661) */
ZTEST(store_delete, test_no_erase)
{
	struct rst_mount_info mi;
	uint32_t ids[1], dg[1], freed;
	static uint8_t before[RREC_CHUNK_BYTES], after[RREC_CHUNK_BYTES];

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(recs(1, 2, ids, dg), 0);
	zassert_equal(rst_read_chunk(ids[0], 1, before), 0);
	zassert_equal(rst_confirm(ids[0], dg[0]), 0);
	uint32_t w0 = rhw_sim_disk_write_calls();

	zassert_equal(rst_delete(ids[0], &freed), 0);
	/* the delete wrote only an index record and the superblock: no sector of the chunk area */
	uint32_t i = 0;
	struct rhw_sim_ev e;
	uint32_t chunk_area_writes = 0, writes = 0;

	while (rhw_sim_log_get(i++, &e)) {
		if (e.kind == RHW_EV_DISK_WRITE && e.a2 > (int64_t)w0) {
			writes++;
			if (e.a0 >= 81920) {
				chunk_area_writes++;
			}
		}
	}
	zassert_equal(writes, 2u, "an index record and a superblock");
	zassert_equal(chunk_area_writes, 0u);
	for (uint32_t k = 0; k < 65; k++) {
		uint8_t s[512];

		rhw_sim_disk_peek(rst_lay_chunk_lba(mi.space.total, 2) + k, s);
		memcpy(after + k * 512, s, 512);
	}
	zassert_equal(memcmp(before, after, sizeof(before)), 0, "the deleted chunk is still on the card");
}

ZTEST(store_delete, test_read_chunk_deleted_not_found)
{
	struct rst_mount_info mi;
	uint32_t ids[2], dg[2], freed;
	static uint8_t buf[RREC_CHUNK_BYTES];
	struct rst_chunk_hdr h;

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(recs(2, 2, ids, dg), 0);
	zassert_equal(rst_read_chunk(ids[1], 1, buf), 0);
	zassert_equal(rst_fmt_chunk_verify(buf, &h, NULL), 0, "a chunk exactly as stored");
	zassert_equal(h.recording_id, ids[1]);
	zassert_equal(h.chunk_in_recording, 1u);
	zassert_equal(h.chunk_seq, 4u);
	zassert_equal(rst_read_chunk(ids[1], 2, buf), -ENOENT, "past the end of the recording");
	zassert_equal(rst_read_chunk(55, 0, buf), -ENOENT, "unknown recording");
	zassert_equal(rst_confirm(ids[0], dg[0]), 0);
	zassert_equal(rst_delete(ids[0], &freed), 0);
	zassert_equal(rst_read_chunk(ids[0], 0, buf), -ENOENT, "NOT_FOUND for a deleted recording (FW l.661)");
	zassert_equal(rst_read_chunk(ids[1], 0, buf), 0);
}

/* a recording that is open blocks a delete; so does an unrecovered one */
ZTEST(store_delete, test_delete_refused_while_open)
{
	struct rst_mount_info mi;
	uint32_t ids[1], dg[1], freed, id2;

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(recs(1, 1, ids, dg), 0);
	zassert_equal(rst_confirm(ids[0], dg[0]), 0);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id2), 0);
	zassert_equal(rst_delete(ids[0], &freed), -EBUSY);
}

/* T-STORE's last step (FW l.1030): every recording of type 2 is deleted without a CONFIRM, the others stay */
ZTEST(store_delete, test_factory_recordings_deleted)
{
	struct rst_mount_info mi;
	uint32_t id, dg, deleted = 99;
	struct rst_space sp;
	static struct rst_rec_info li[4];
	uint16_t n;

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(tst_record(RREC_REC_TYPE_FACTORY, 1, &id, &dg), 0);
	uint32_t f1 = id;

	zassert_equal(tst_record(RREC_REC_TYPE_RECORDING, 2, &id, &dg), 0);
	uint32_t keep = id;

	zassert_equal(tst_record(RREC_REC_TYPE_FACTORY, 1, &id, &dg), 0);
	zassert_equal(rst_list(0, 4, li, &n), 0);
	zassert_equal(n, 3);
	zassert_equal(li[0].type, RREC_REC_TYPE_FACTORY);
	zassert_equal(rst_delete_factory_recordings(&deleted), 0);
	zassert_equal(deleted, 2u);
	zassert_equal(rst_list(0, 4, li, &n), 0);
	zassert_equal(n, 1);
	zassert_equal(li[0].recording_id, keep);
	zassert_not_equal(li[0].recording_id, f1);
	zassert_equal(rst_space(&sp), 0);
	zassert_equal(sp.used, 3u, "the first factory recording is freed from the tail, the last one stays counted");
	zassert_equal(rst_delete_factory_recordings(&deleted), 0);
	zassert_equal(deleted, 0u);
}
