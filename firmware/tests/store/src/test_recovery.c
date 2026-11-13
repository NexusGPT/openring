/* Suite store_recovery (unit U2): the scan after a power loss (FW l.645, l.646, l.170), on a RAM disk for the scan's
 * logic and on the simulated card for the cuts. */
#include "tst.h"

ZTEST_SUITE(store_recovery, NULL, NULL, tst_before, NULL, NULL);

#define TOTAL 8u

static struct rst_chunk rc;

/* one chunk of recording rec_id, number in_rec, with sequence seq, written to the RAM disk where seq belongs */
static void rd_chunk(uint32_t seq, uint32_t rec_id, uint32_t in_rec)
{
	tst_fill(&rc, rec_id, in_rec, 8192, in_rec);
	rc.hdr.chunk_seq = seq;
	zassert_equal(rst_fmt_chunk_encode(&rc, NULL), 0);
	rd_write(rst_lay_chunk_lba(TOTAL, seq), rc.bytes, RREC_CHUNK_SECTORS);
}

static void recrc(uint8_t *hdr)
{
	tst_le(hdr, 508, tst_crc32(hdr, 508), 4);
}

static uint8_t sc_buf[RREC_CHUNK_BYTES];

static int run_scan(uint32_t rec_id, uint32_t first_seq, struct rst_scan *sc)
{
	return rst_log_scan(rd_read, NULL, TOTAL, rec_id, first_seq, sc_buf, NULL, NULL, sc);
}

/* S23: the scan keeps a chunk while magic, header CRC, payload CRC, recording_id and chunk_seq all match and stops at
 * the first mismatch: one case per field, the third of four chunks damaged in that field only */
ZTEST(store_recovery, test_stop_on_each_mismatch)
{
	struct rst_scan sc;

	rd_reset();
	for (uint32_t i = 0; i < 4; i++) {
		rd_chunk(5 + i, 3, i);
	}
	zassert_equal(run_scan(3, 5, &sc), 0);
	zassert_equal(sc.kept, 4u, "all four are good");

	for (int field = 0; field < 5; field++) {
		const uint32_t seq3 = 7;                     /* the third chunk: seq 7 */

		rd_reset();
		for (uint32_t i = 0; i < 4; i++) {
			rd_chunk(5 + i, 3, i);
		}
		uint8_t first[512];

		switch (field) {
		case 0: /* magic wrong, header CRC made right again */
			rd_read(NULL, rst_lay_chunk_lba(TOTAL, seq3), first, 1);
			first[0] ^= 0x01;
			recrc(first);
			rd_write(rst_lay_chunk_lba(TOTAL, seq3), first, 1);
			break;
		case 1: /* header CRC wrong */
			rd_read(NULL, rst_lay_chunk_lba(TOTAL, seq3), first, 1);
			first[508] ^= 0x01;
			rd_write(rst_lay_chunk_lba(TOTAL, seq3), first, 1);
			break;
		case 2: /* payload CRC wrong: one payload byte changed */
			rd_read(NULL, rst_lay_chunk_lba(TOTAL, seq3) + 10, first, 1);
			first[100] ^= 0x01;
			rd_write(rst_lay_chunk_lba(TOTAL, seq3) + 10, first, 1);
			break;
		case 3: /* recording_id of another recording, both CRCs right */
			rd_chunk(seq3, 4, 2);
			break;
		case 4: /* chunk_seq not previous + 1 (a gap: 8 where 7 belongs), both CRCs right */
			tst_fill(&rc, 3, 2, 8192, 2);
			rc.hdr.chunk_seq = 8;
			zassert_equal(rst_fmt_chunk_encode(&rc, NULL), 0);
			rd_write(rst_lay_chunk_lba(TOTAL, seq3), rc.bytes, RREC_CHUNK_SECTORS);
			break;
		}
		zassert_equal(run_scan(3, 5, &sc), 0);
		zassert_equal(sc.kept, 2u, "field %d: stops at the first mismatch (0 magic, 1 header CRC, 2 payload CRC, "
			      "3 recording_id, 4 chunk_seq)", field);
	}

	/* the first chunk must also be the first of the recording's sequence */
	rd_reset();
	rd_chunk(6, 3, 0);
	zassert_equal(run_scan(3, 5, &sc), 0);
	zassert_equal(sc.kept, 0u, "chunk 6 where chunk 5 was expected");
	rd_reset();
	zassert_equal(run_scan(3, 5, &sc), 0);
	zassert_equal(sc.kept, 0u, "nothing written");
}

/* S23: what the scan reports for the CLOSE RECOVERED record */
ZTEST(store_recovery, test_scan_summary)
{
	struct rst_scan sc;

	rd_reset();
	for (uint32_t i = 0; i < 3; i++) {
		tst_fill(&rc, 3, i, i == 2 ? 100 : 8192, i);
		rc.hdr.chunk_seq = 5 + i;
		if (i == 1) {
			rc.hdr.highlight_count = 2;
			rc.hdr.highlight_frame[0] = 9792;
			rc.hdr.highlight_frame[1] = 11392;
		}
		zassert_equal(rst_fmt_chunk_encode(&rc, NULL), 0);
		rd_write(rst_lay_chunk_lba(TOTAL, 5 + i), rc.bytes, RREC_CHUNK_SECTORS);
	}
	zassert_equal(run_scan(3, 5, &sc), 0);
	zassert_equal(sc.kept, 3u);
	zassert_equal(sc.duration_frames, 8192u + 8192u + 100u);
	zassert_equal(sc.start_utc_ms, 1700000000000ll);
	zassert_equal(sc.highlight_count, 2);
	zassert_equal(sc.highlight_ms[0], 612u, "frame 9,792 from the first kept frame at 16 kHz = 612 ms (FW l.566)");
	zassert_equal(sc.highlight_ms[1], 712u, "frame 11,392 = 712 ms");
	zassert_equal(sc.highlight_ms[2], 0xFFFFFFFFu);
	uint8_t w[12];

	for (uint32_t i = 0; i < 3; i++) {
		tst_fill(&rc, 3, i, i == 2 ? 100 : 8192, i);
		rc.hdr.frames = i == 2 ? 100 : 8192;
		memset(rc.bytes + 512 + (i == 2 ? 400 : 32768), 0, i == 2 ? 32768 - 400 : 0);
		tst_le(w, i * 4, tst_crc32(rc.bytes + 512, 32768), 4);
	}
	zassert_equal(sc.digest, tst_crc32(w, 12), "digest over the three payload CRCs");
}

/* C9: a read error during the scan is reported, with the sector */
ZTEST(store_recovery, test_scan_read_error_reports)
{
	struct rst_scan sc;

	rd_reset();
	for (uint32_t i = 0; i < 3; i++) {
		rd_chunk(5 + i, 3, i);
	}
	rd_fail_at(rst_lay_chunk_lba(TOTAL, 6) + 3);
	zassert_equal(run_scan(3, 5, &sc), -EIO);
	zassert_equal(sc.err_lba, rst_lay_chunk_lba(TOTAL, 6));
	zassert_equal(sc.kept, 1u, "chunk 5 passed before the failure");
}

static struct rst_chunk big;

static void put_wait(uint32_t id, uint32_t i)
{
	tst_fill(&big, id, i, 8192, i);
	zassert_equal(rst_put_chunk(&big, tst_done_cb), 0, "put %u", i);
	zassert_true(tst_wait_done((int)i + 1, 20000), "done %u", i);
}

/* S22, C16: a power loss inside a chunk write: the chunk fails its CRC and is dropped; a new mount of the same
 * card sees the open flag; recovery keeps the two chunks written before. Cut after sector 1, 33 and 64 of the 65. */
ZTEST(store_recovery, test_cut_inside_chunk_write)
{
	static const uint32_t cuts[] = { 1, 33, 64 };

	for (unsigned c = 0; c < ARRAY_SIZE(cuts); c++) {
		struct rst_mount_info mi;
		struct rst_recover_result rr;
		struct rst_ix x;
		uint32_t id;
		uint8_t s[512];
		static struct rst_rec_info li[2];
		uint16_t n;

		tst_reset();
		tst_card(100);
		tst_mount_boot(&mi);
		zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 1700000000000ll, &id), 0);
		put_wait(id, 0);
		put_wait(id, 1);
		rhw_sim_disk_cut(1, cuts[c]);                 /* the next write call (chunk 3) loses power after k sectors */
		put_wait(id, 2);
		zassert_true(rhw_sim_disk_was_cut(), "cut %u", cuts[c]);

		/* the sectors of chunk 3 that reached the card: exactly k of them (the header sector first) */
		uint32_t lba3 = rst_lay_chunk_lba(mi.space.total, 3);
		uint32_t present = 0;

		for (uint32_t k = 0; k < 65; k++) {
			rhw_sim_disk_peek(lba3 + k, s);
			for (unsigned b = 0; b < 512; b++) {
				if (s[b] != 0) {
					present++;
					break;
				}
			}
		}
		zassert_equal(present, cuts[c], "sectors of the cut chunk on the card");

		tst_reboot();                                 /* the new start: the card is the same */
		zassert_false(rst_mounted());
		tst_mount_boot(&mi);
		zassert_true(mi.open_flag, "cut %u: the open flag leads to RECOVERY", cuts[c]);
		zassert_equal(mi.open_recording_id, id);
		zassert_equal(rst_recover(NULL, &rr), 0);
		zassert_equal(rr.chunks_kept, 2u, "cut after sector %u: the chunk in flight is dropped", cuts[c]);
		zassert_equal(rr.recording_id, id);
		zassert_equal(rr.head_chunk_seq, 3u, "head past the last good chunk (1 and 2 kept)");

		rhw_sim_disk_peek(8192 + 1, s);
		zassert_equal(rst_fmt_ix_decode(s, &x), 0);
		zassert_equal(x.type, 1);
		zassert_equal(x.close_state, 2, "RECOVERED");
		zassert_equal(x.chunk_count, 2u);
		zassert_equal(x.digest, tst_ref_digest(id, 2));
		zassert_equal(rst_list(0, 2, li, &n), 0);
		zassert_equal(n, 1);
		zassert_equal(li[0].state, RREC_LIST_STATE_RECOVERED);

		tst_reboot();
		tst_mount_boot(&mi);
		zassert_false(mi.open_flag, "the flag is cleared");
		zassert_equal(rst_recover(NULL, &rr), -EINVAL, "nothing to recover");
		zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0, "a new recording may start");
	}
}

static int prog_n, prog_last;

static void prog(uint32_t chunks)
{
	prog_n++;
	prog_last = (int)chunks;
}

/* S23: the CLOSE RECOVERED record, head, open flag; the progress callback */
ZTEST(store_recovery, test_recovered_close_record)
{
	struct rst_mount_info mi;
	struct rst_recover_result rr;
	struct rst_ix x;
	uint32_t id;
	uint8_t s[512];

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 1700000000000ll, &id), 0);
	for (uint32_t i = 0; i < 3; i++) {
		put_wait(id, i);
	}
	tst_reboot();
	tst_mount_boot(&mi);
	zassert_true(mi.open_flag);
	zassert_equal(mi.boot_count, 2u);
	prog_n = 0;
	zassert_equal(rst_recover(prog, &rr), 0);
	zassert_equal(prog_n, 3, "progress after each chunk");
	zassert_equal(prog_last, 3);
	zassert_equal(rr.chunks_kept, 3u);
	rhw_sim_disk_peek(8192 + 1, s);
	zassert_equal(rst_fmt_ix_decode(s, &x), 0);
	zassert_equal(x.type, RREC_IX_TYPE_CLOSE);
	zassert_equal(x.close_state, RREC_IX_CLOSE_RECOVERED);
	zassert_equal(x.recording_id, id);
	zassert_equal(x.first_chunk_seq, 1u);
	zassert_equal(x.chunk_count, 3u);
	zassert_equal(x.duration_frames, 3u * 8192u);
	zassert_equal(x.start_utc_ms, 1700000000000ll);
	zassert_equal(x.digest, tst_ref_digest(id, 3));
	struct rst_space sp;

	zassert_equal(rst_space(&sp), 0);
	zassert_equal(sp.used, 3u);
	tst_reboot();
	tst_mount_boot(&mi);
	zassert_false(mi.open_flag);
	zassert_equal(mi.recordings, 1u);
}

/* C9: a read error during the scan reports -EIO and leaves the open flag set (FW l.143, ruling R9) */
ZTEST(store_recovery, test_read_error_reports)
{
	struct rst_mount_info mi;
	struct rst_recover_result rr;
	uint32_t id;

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	for (uint32_t i = 0; i < 3; i++) {
		put_wait(id, i);
	}
	tst_reboot();
	tst_mount_boot(&mi);
	rhw_sim_disk_read_error_at(rst_lay_chunk_lba(mi.space.total, 2) + 5);
	prog_n = 0;
	zassert_equal(rst_recover(prog, &rr), -EIO);
	zassert_equal(prog_n, 1, "chunk 1 passed before the failure");
	tst_reboot();
	tst_mount_boot(&mi);
	zassert_true(mi.open_flag, "the flag stays set: the next start goes to RECOVERY again");
	rhw_sim_disk_read_error_at(UINT32_MAX);
	zassert_equal(rst_recover(NULL, &rr), 0);
	zassert_equal(rr.chunks_kept, 3u);
}

/* S21: audio lost on a power loss is at most the chunks in RAM: with a stalled card the ring of 3 bounds it. A card
 * that takes 2 s per write; a chunk is offered every 512 ms; at the instant of the cut at most 3 chunks that
 * were accepted are not on the card. */
ZTEST(store_recovery, test_loss_bound_with_stalled_card)
{
	static struct rst_chunk bufs[4];
	static bool used[4];
	struct rst_mount_info mi;
	struct rst_recover_result rr;
	uint32_t id;
	int accepted = 0, refused = 0;

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	rhw_sim_disk_stall_ms(2000);
	rhw_sim_disk_cut(4, 10);                      /* the 4th chunk write is cut after 10 sectors */
	for (int step = 0; step < 40 * 32; step++) {
		if (rhw_sim_disk_was_cut()) {
			break;
		}
		if (step % 32 == 0) {
			int b = -1;

			for (int i = 0; i < 4 && b < 0; i++) {
				if (!used[i]) {
					b = i;
				}
			}
			zassert_true(b >= 0, "a free buffer");
			tst_fill(&bufs[b], id, (uint32_t)(accepted + refused), 8192, (uint32_t)(accepted + refused));
			int r = rst_put_chunk(&bufs[b], tst_done_cb);

			if (r == 0) {
				used[b] = true;
				accepted++;
			} else {
				zassert_equal(r, -ENOBUFS, "the ring of 3 is full");
				refused++;
			}
		}
		k_msleep(16);
		/* free a buffer for each completion */
		int done = tst_done_count();
		int busy = 0;

		for (int i = 0; i < 4; i++) {
			busy += used[i] ? 1 : 0;
		}
		for (int i = 0; i < 4 && busy > accepted - done; i++) {
			if (used[i]) {
				used[i] = false;
				busy--;
			}
		}
	}
	zassert_true(rhw_sim_disk_was_cut(), "the cut came");
	zassert_true(refused > 0, "the ring of 3 filled up");
	k_msleep(5000);
	tst_reboot();
	tst_mount_boot(&mi);
	zassert_true(mi.open_flag);
	zassert_equal(rst_recover(NULL, &rr), 0);
	zassert_equal(rr.chunks_kept, 3u, "3 chunk writes landed before the 4th was cut");
	zassert_true(accepted - (int)rr.chunks_kept <= (int)RREC_CHUNK_RING,
		     "accepted %d, on the card %u: at most %u in RAM at the cut", accepted, rr.chunks_kept,
		     (unsigned)RREC_CHUNK_RING);
	zassert_true(accepted - (int)rr.chunks_kept >= 1, "something was lost");
}
