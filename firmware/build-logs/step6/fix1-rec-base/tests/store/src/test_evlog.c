/* Suite store_evlog (unit U2): the event log (FW l.1062): the RAM buffer of 8, writing when VDD_SD is on, the ring of 2,046. */
#include "tst.h"

ZTEST_SUITE(store_evlog, NULL, NULL, tst_before, NULL, NULL);

static struct rrec_logrec mkrec(uint16_t code)
{
	struct rrec_logrec r;

	memset(&r, 0, sizeof(r));
	r.code = code;
	r.state = 3;
	r.uptime_ns = (int64_t)code * 1000000;
	r.utc_ms = 1700000000000ll + code;
	r.args[0] = (uint8_t)code;
	return r;
}

static bool log_sector(uint32_t lba, struct rrec_logrec *out)
{
	uint8_t s[512];

	rhw_sim_disk_peek(lba, s);
	return rst_fmt_log_decode(s, out) == 0;
}

/* T26: 8 records wait in RAM; when the buffer is full the oldest unwritten is dropped and counted */
ZTEST(store_evlog, test_buffer_of_8_drops_oldest)
{
	struct rst_evbuf b;
	struct rrec_logrec r, got;

	rst_evbuf_init(&b);
	for (uint16_t c = 1; c <= 10; c++) {
		r = mkrec(c);
		rst_evbuf_push(&b, &r);
	}
	zassert_equal(b.n, 8u, "8 records wait");
	zassert_equal(b.dropped, 2u, "two dropped and counted");
	for (uint16_t c = 3; c <= 10; c++) {
		zassert_true(rst_evbuf_peek(&b, &got));
		zassert_equal(got.code, c, "the oldest kept is record %u", c);
		rst_evbuf_pop(&b);
	}
	zassert_false(rst_evbuf_peek(&b, &got));
	zassert_equal(b.dropped, 2u);

	/* the same through the store's call while the card is off */
	for (uint16_t c = 1; c <= 10; c++) {
		r = mkrec(c);
		rst_log_put(&r);
	}
	zassert_equal(rst_log_dropped(), 2u);
}

/* T26: records wait while VDD_SD is off and are written at the next mount; later ones at once (FW l.1062) */
ZTEST(store_evlog, test_written_when_rail_on)
{
	struct rst_mount_info mi;
	struct rrec_logrec r, got;

	for (uint16_t c = 1; c <= 3; c++) {
		r = mkrec(c);
		rst_log_put(&r);
	}
	k_msleep(50);
	zassert_equal(rhw_sim_disk_write_calls(), 0u, "no write with the rail off");
	zassert_equal(rhw_sim_disk_refused(), 0u, "and no refused call either");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_DISK_WRITE), 0u);
	zassert_false(rhw_sim_pmic_rail_caller(RHW_RAIL_SD)[0] != 0, "the rail was never touched");

	tst_mount_boot(&mi);
	for (uint16_t c = 1; c <= 3; c++) {
		zassert_true(log_sector(2 + c - 1, &got), "record %u at LBA %u", c, 2 + c - 1);
		zassert_equal(got.seq, c);
		zassert_equal(got.code, c);
		zassert_equal(got.state, 3);
		zassert_equal(got.utc_ms, 1700000000000ll + c);
		zassert_equal(got.args[0], c);
	}
	zassert_false(log_sector(5, &got), "nothing more yet");

	r = mkrec(4);
	rst_log_put(&r);
	k_msleep(20);
	zassert_true(log_sector(5, &got), "a record put while mounted is written at once");
	zassert_equal(got.seq, 4u);

	uint8_t out[3 * 512];
	uint16_t n = 0;

	zassert_equal(rst_log_read(0, 3, out, &n), 0);
	zassert_equal(n, 3);
	zassert_equal(rst_fmt_log_decode(out, &got), 0);
	zassert_equal(got.seq, 1u);
	zassert_equal(rst_fmt_log_decode(out + 1024, &got), 0);
	zassert_equal(got.seq, 3u);
	static uint8_t big[32 * 512];

	zassert_equal(rst_log_read(3, 32, big, &n), 0);
	zassert_equal(n, 2, "records 3 and 4");
	zassert_equal(rst_log_read(0, 0, out, &n), -EINVAL);
	zassert_equal(rst_log_read(0, 33, out, &n), -EINVAL);
	zassert_equal(rst_log_read(100, 2, out, &n), 0);
	zassert_equal(n, 0, "past the head");

	/* the drop count and the written records together: 10 records put with the card off */
	tst_reset();
	for (uint16_t c = 1; c <= 10; c++) {
		r = mkrec(c);
		rst_log_put(&r);
	}
	tst_mount_boot(&mi);
	zassert_equal(rst_log_dropped(), 2u);
	zassert_true(log_sector(2, &got));
	zassert_equal(got.code, 3u, "records 1 and 2 were dropped, 3 is the first written");
	zassert_equal(got.seq, 1u, "sequence numbers on the card have no gap");
}

/* FW l.525: a ring of 2,046 records, 1 record per sector from LBA 2 */
ZTEST(store_evlog, test_ring_of_2046)
{
	struct rst_mount_info mi;
	struct rrec_logrec r, got;
	static uint8_t out[32 * 512];
	uint16_t n;

	zassert_equal(rst_lay_log_lba(1), 2u);
	zassert_equal(rst_lay_log_lba(2046), 2047u, "the 2,046th record is in the last sector of the log area");
	zassert_equal(rst_lay_log_lba(2047), 2u, "the 2,047th record wraps to the first sector");
	zassert_equal(rst_lay_log_lba(2048), 3u);
	zassert_equal(rst_lay_log_lba(4093), 2u, "2 x 2,046 + 1");

	tst_mount_boot(&mi);
	for (uint16_t c = 1; c <= 2100; c++) {
		r = mkrec(c);
		rst_log_put(&r);
		k_msleep(1);
	}
	k_msleep(10);
	zassert_equal(rst_log_dropped(), 0u);
	zassert_true(log_sector(2 + 53, &got));
	zassert_equal(got.seq, 2100u, "record 2,100 = 2,046 + 54 is in the 54th sector of the area, LBA 55");
	zassert_true(log_sector(2, &got));
	zassert_equal(got.seq, 2047u, "sector 2 was overwritten by the second lap: record 2,047, no longer record 1");
	zassert_true(log_sector(2047, &got));
	zassert_equal(got.seq, 2046u);
	zassert_equal(rst_log_read(0, 32, out, &n), 0);
	zassert_equal(n, 32);
	zassert_equal(rst_fmt_log_decode(out, &got), 0);
	zassert_equal(got.seq, 2100u - 2046u + 1u, "only the newest 2,046 are kept: the oldest is record 55");

	/* after a restart the head is found although the superblock lags */
	tst_reboot();
	tst_mount_boot(&mi);
	r = mkrec(9000);
	rst_log_put(&r);
	k_msleep(20);
	zassert_true(log_sector(rst_lay_log_lba(2101), &got), "the next record goes to sequence 2,101");
	zassert_equal(got.seq, 2101u);
	zassert_equal(got.code, 9000u);
}

/* a crash block travels through the buffer and the card */
ZTEST(store_evlog, test_crash_block_roundtrip)
{
	struct rst_mount_info mi;
	struct rrec_logrec r = mkrec(0x0230), got;

	r.has_crash = true;
	r.crash.reason = 4;
	r.crash.pc = 0x1234;
	strcpy(r.crash.thread, "rst");
	r.crash.stack[63] = 77;
	tst_mount_boot(&mi);
	rst_log_put(&r);
	k_msleep(20);
	zassert_true(log_sector(2, &got));
	zassert_true(got.has_crash);
	zassert_equal(got.crash.pc, 0x1234u);
	zassert_equal(got.crash.stack[63], 77u);
}
