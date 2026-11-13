/*
 * Suite store_svc (unit U2): the thin part (rst.c) on the simulated card, storage bus and power chip: the rail
 * sequence of design/firmware.md 5.1, init tries, write tries, one operation at a time, the superblock rules.
 */
#include "tst.h"

static int fault_n, fault_err;

static void on_fault(int err)
{
	fault_n++;
	fault_err = err;
}

static struct rst_cb svc_cb = { .write_fault = on_fault };

static void svc_before(void *f)
{
	ARG_UNUSED(f);
	fault_n = 0;
	fault_err = 0;
	tst_reset_cb(&svc_cb);
}

ZTEST_SUITE(store_svc, NULL, NULL, svc_before, NULL, NULL);

static struct rst_chunk big;

static void put_wait(uint32_t id, uint32_t i)
{
	tst_fill(&big, id, i, 8192, i);
	zassert_equal(rst_put_chunk(&big, tst_done_cb), 0, "put %u", i);
	zassert_true(tst_wait_done((int)i + 1, 20000), "done %u", i);
}

static struct rst_close_args no_hl(void)
{
	struct rst_close_args a = { 0 };

	memset(a.highlight_ms, 0xFF, sizeof(a.highlight_ms));
	return a;
}

/* the log entries of the given kinds from index `from`, in order */
static uint32_t collect(uint32_t from, const uint16_t *kinds, uint32_t nk, struct rhw_sim_ev *out, uint32_t max)
{
	uint32_t n = 0, cnt = rhw_sim_log_count();

	for (uint32_t i = from; i < cnt && n < max; i++) {
		struct rhw_sim_ev e;

		rhw_sim_log_get(i, &e);
		for (uint32_t k = 0; k < nk; k++) {
			if (e.kind == kinds[k]) {
				out[n++] = e;
				break;
			}
		}
	}
	return n;
}

/* S3: the sector count is read at mount and gives the chunk count; a blank card gets a new log */
ZTEST(store_svc, test_mount_reads_sector_count)
{
	struct rst_mount_info mi;
	uint8_t s[512];
	struct rst_sb sb;

	rhw_sim_disk_set_sectors(1000000);
	zassert_false(rst_mounted());
	zassert_equal(rst_mount(true, &mi), 0);
	zassert_true(rst_mounted());
	zassert_equal(mi.card_sectors, 1000000u);
	zassert_equal(mi.space.total, 14124u, "(1,000,000 - 81,920) / 65 rounded down");
	zassert_equal(mi.space.free_chunks, 14124u);
	zassert_equal(mi.recordings, 0u);
	zassert_equal(mi.boot_count, 1u);
	zassert_false(mi.open_flag);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_DISK_COUNT), 1u, "the card was asked once");
	/* the new log's superblock: sb_seq 1 in LBA 1 */
	rhw_sim_disk_peek(1, s);
	zassert_equal(rst_fmt_sb_decode(s, &sb), 0);
	zassert_equal(sb.sb_seq, 1u);
	zassert_equal(sb.card_sectors, 1000000u);
	zassert_equal(sb.chunk_count_total, 14124u);
	zassert_equal(sb.head_chunk_seq, 1u);
	zassert_equal(sb.boot_count, 1u);

	/* the 4 GB example */
	zassert_equal(rst_unmount(), 0);
	tst_reset();
	zassert_equal(rst_mount(true, &mi), 0);
	zassert_equal(mi.card_sectors, 7812500u);
	zassert_equal(mi.space.total, 118932u);
	zassert_equal(mi.space.minutes_left, 1014u);
}

/* a card that cannot be read is never formatted; a card smaller than its log is refused */
ZTEST(store_svc, test_mount_never_formats_an_unreadable_card)
{
	struct rst_mount_info mi;

	tst_card(100);
	rhw_sim_disk_read_error_at(1);
	zassert_equal(rst_mount(true, &mi), -EIO);
	zassert_equal(rhw_sim_disk_write_calls(), 0u, "nothing was written");
	zassert_false(rst_mounted());
	zassert_false(rhw_sim_pmic_rail_caller(RHW_RAIL_SD)[0] == 0, "the rail was used");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_DISK_DEINIT), 1u);
	rhw_sim_disk_read_error_at(UINT32_MAX);
	zassert_equal(rst_mount(true, &mi), 0, "then the same card mounts");

	zassert_equal(rst_unmount(), 0);
	tst_reboot();
	rhw_sim_disk_set_sectors(81920 + 65 * 10);
	zassert_equal(rst_mount(true, &mi), -EIO, "10 chunks' worth of card for a log made on 100");
}

/* S14 on the card: the copy with the higher sb_seq wins; with the newest copy damaged the older one is used */
ZTEST(store_svc, test_mount_uses_the_valid_copy)
{
	struct rst_mount_info mi;
	uint32_t id;
	uint8_t junk[512];

	tst_card(100);
	tst_mount_boot(&mi);                           /* new log: sb_seq 1 in LBA 1, boot_count 1 */
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);     /* sb_seq 2 in LBA 0, open flag set */
	tst_reboot();
	tst_mount_boot(&mi);                           /* reads LBA 0 (sb_seq 2); writes sb_seq 3 to LBA 1, boot_count 2 */
	zassert_true(mi.open_flag);
	zassert_equal(mi.boot_count, 2u);
	memset(junk, 0x5A, sizeof(junk));
	tst_reboot();
	zassert_equal(rhw_sim_disk_poke(1, junk), 0);  /* damage the newest copy (sb_seq 3, LBA 1) */
	tst_mount_boot(&mi);
	zassert_true(mi.open_flag, "the older copy still says open");
	zassert_equal(mi.boot_count, 2u, "boot_count 1 of the older copy (sb_seq 2) plus this boot; the newest said 2 + 1");
}

/* S2: after VDD_SD on: wait 1 ms, resume, init; before VDD_SD off: deinit, suspend, rail off; the sleep state at boot */
ZTEST(store_svc, test_rail_sequence)
{
	static const uint16_t kinds[] = { RHW_EV_PMIC_RAIL, RHW_EV_SDBUS_SUSPEND, RHW_EV_SDBUS_RESUME, RHW_EV_DISK_INIT,
					  RHW_EV_DISK_DEINIT, RHW_EV_DISK_REFUSED };
	struct rhw_sim_ev e[16];
	struct rst_mount_info mi;

	tst_card(100);
	zassert_equal(rst_mount(true, &mi), 0);
	zassert_equal(rst_unmount(), 0);
	uint32_t n = collect(0, kinds, ARRAY_SIZE(kinds), e, 16);

	zassert_equal(n, 7u, "the driver calls of one mount and one unmount");
	zassert_equal(e[0].kind, RHW_EV_SDBUS_SUSPEND, "at boot the sleep state comes first, before any SPI use");
	zassert_equal(e[1].kind, RHW_EV_PMIC_RAIL);
	zassert_equal(e[1].a0, RHW_RAIL_SD);
	zassert_equal(e[1].a1, 1, "VDD_SD on");
	zassert_equal(strcmp(e[1].caller, "rst_mount"), 0);
	zassert_equal(e[2].kind, RHW_EV_SDBUS_RESUME);
	zassert_true(e[2].t_us - e[1].t_us >= 1000, "1 ms after the rail: %lld us", (long long)(e[2].t_us - e[1].t_us));
	zassert_equal(e[3].kind, RHW_EV_DISK_INIT);
	zassert_equal(e[4].kind, RHW_EV_DISK_DEINIT, "unmount: deinit first");
	zassert_equal(e[5].kind, RHW_EV_SDBUS_SUSPEND, "then the bus asleep");
	zassert_equal(e[6].kind, RHW_EV_PMIC_RAIL, "then the rail off");
	zassert_equal(e[6].a1, 0);
	zassert_equal(strcmp(e[6].caller, "rst_unmount"), 0);
	zassert_equal(rhw_sim_disk_refused(), 0u);
	zassert_false(rhw_pmic()->rail_get(RHW_RAIL_SD));
	zassert_true(rhw_sim_sdbus_suspended());
}

/* S2: no card call is made with VDD_SD off (the simulated card refuses and counts any such call) */
ZTEST(store_svc, test_no_disk_call_with_rail_off)
{
	struct rst_mount_info mi;
	struct rrec_logrec lr = { .code = 1 };
	struct rst_factory_result fr;
	static uint8_t buf[RREC_CHUNK_BYTES];
	static struct rst_rec_info li[2];
	uint16_t n;
	uint32_t id, v;

	tst_card(100);
	zassert_equal(rst_mount(true, &mi), 0);
	zassert_equal(rst_unmount(), 0);
	uint32_t base = rhw_sim_disk_refused();
	uint32_t mark = rhw_sim_log_count();

	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), -ENODEV);
	zassert_equal(rst_put_chunk(&big, tst_done_cb), -EINVAL);
	zassert_equal(rst_close(NULL, &(struct rst_close_args){ 0 }), -EINVAL);
	zassert_equal(rst_recover(NULL, NULL), -ENODEV);
	zassert_equal(rst_list(0, 1, li, &n), -ENODEV);
	zassert_equal(rst_read_chunk(1, 0, buf), -ENODEV);
	zassert_equal(rst_confirm(1, 0), -ENODEV);
	zassert_equal(rst_delete(1, &v), -ENODEV);
	zassert_equal(rst_log_read(0, 1, buf, &n), -ENODEV);
	zassert_equal(rst_factory_area_test(&fr), -ENODEV);
	zassert_equal(rst_delete_factory_recordings(&v), -ENODEV);
	zassert_equal(rst_unmount(), 0, "unmount of an unmounted store does nothing");
	rst_log_put(&lr);
	k_msleep(50);
	zassert_equal(rhw_sim_disk_refused(), base, "no refused call");
	uint32_t cnt = rhw_sim_log_count();

	for (uint32_t i = mark; i < cnt; i++) {
		struct rhw_sim_ev e;

		rhw_sim_log_get(i, &e);
		zassert_true(e.kind != RHW_EV_DISK_INIT && e.kind != RHW_EV_DISK_READ && e.kind != RHW_EV_DISK_WRITE &&
			     e.kind != RHW_EV_DISK_DEINIT && e.kind != RHW_EV_DISK_COUNT && e.kind != RHW_EV_DISK_REFUSED,
			     "no card call after the unmount (kind %u)", e.kind);
	}
	/* a failed mount leaves the rail off too */
	rhw_sim_disk_fail_init(3);
	zassert_equal(rst_mount(true, &mi), -EIO);
	base = rhw_sim_disk_refused();
	zassert_false(rhw_pmic()->rail_get(RHW_RAIL_SD));
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), -ENODEV);
	zassert_equal(rhw_sim_disk_refused(), base);
}

/* C8: storage init: 3 tries 200 ms apart, then the failure with VDD_SD off again (bus asleep first) */
ZTEST(store_svc, test_init_three_tries_200ms)
{
	static const uint16_t kinds[] = { RHW_EV_DISK_INIT, RHW_EV_SDBUS_SUSPEND, RHW_EV_PMIC_RAIL, RHW_EV_DISK_DEINIT };
	struct rhw_sim_ev e[12];
	struct rst_mount_info mi;

	tst_card(100);
	/* two failures, the third try works */
	rhw_sim_disk_fail_init(2);
	uint32_t from = rhw_sim_log_count();

	zassert_equal(rst_mount(true, &mi), 0);
	uint32_t n = collect(from, kinds, ARRAY_SIZE(kinds), e, 12);

	zassert_equal(n, 4u, "rail on, 3 init calls");
	zassert_equal(e[0].kind, RHW_EV_PMIC_RAIL);
	zassert_equal(e[1].kind, RHW_EV_DISK_INIT);
	zassert_equal(e[1].res, -EIO);
	zassert_equal(e[2].res, -EIO);
	zassert_equal(e[3].res, 0);
	zassert_true(e[2].t_us - e[1].t_us >= 200000 && e[2].t_us - e[1].t_us < 205000, "gap 1: %lld us",
		     (long long)(e[2].t_us - e[1].t_us));
	zassert_true(e[3].t_us - e[2].t_us >= 200000 && e[3].t_us - e[2].t_us < 205000, "gap 2: %lld us",
		     (long long)(e[3].t_us - e[2].t_us));
	zassert_true(rst_mounted());
	zassert_equal(rst_unmount(), 0);

	/* three failures: the mount fails after 3 tries, the bus goes to sleep, then the rail goes off */
	rhw_sim_disk_fail_init(3);
	from = rhw_sim_log_count();
	int64_t t0 = k_uptime_get();

	zassert_equal(rst_mount(true, &mi), -EIO);
	zassert_true(k_uptime_get() - t0 >= 400 && k_uptime_get() - t0 < 410, "2 gaps of 200 ms, not 3");
	n = collect(from, kinds, ARRAY_SIZE(kinds), e, 12);
	zassert_equal(n, 6u, "rail on, 3 init calls, suspend, rail off");
	zassert_equal(e[1].kind, RHW_EV_DISK_INIT);
	zassert_equal(e[3].kind, RHW_EV_DISK_INIT);
	zassert_equal(e[4].kind, RHW_EV_SDBUS_SUSPEND);
	zassert_equal(e[5].kind, RHW_EV_PMIC_RAIL);
	zassert_equal(e[5].a1, 0);
	zassert_false(rst_mounted());
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_DISK_DEINIT), 1u, "only the earlier unmount");

	/* and the next mount works */
	zassert_equal(rst_mount(true, &mi), 0);
}

/* S5, S6: a recording writes each chunk sector once, one 65-sector write per chunk, at sequential addresses; the
 * superblock and the index stay outside the chunk area (the only sectors written twice are the 2 superblock copies) */
ZTEST(store_svc, test_one_write_per_chunk)
{
	static const uint16_t kinds[] = { RHW_EV_DISK_WRITE };
	struct rhw_sim_ev e[40];
	struct rst_mount_info mi;
	struct rst_close_args a = no_hl();
	uint32_t id;

	tst_card(100);
	tst_mount_boot(&mi);
	uint32_t from = rhw_sim_log_count();

	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	for (uint32_t i = 0; i < 5; i++) {
		put_wait(id, i);
	}
	zassert_equal(rst_close(NULL, &a), 0);
	uint32_t n = collect(from, kinds, 1, e, 40);
	uint32_t chunks = 0, sbs = 0, ixs = 0;
	int64_t last_lba = -1;

	for (uint32_t i = 0; i < n; i++) {
		if (e[i].a0 >= 81920) {
			chunks++;
			zassert_equal(e[i].a1, 65, "one write of 65 sectors");
			if (last_lba >= 0) {
				zassert_equal(e[i].a0, last_lba + 65, "sequential addresses");
			}
			last_lba = e[i].a0;
			zassert_equal((e[i].a0 - 81920) % 65, 0);
			for (uint32_t j = 0; j < i; j++) {
				zassert_true(e[j].a0 != e[i].a0, "chunk sector %lld written twice", (long long)e[i].a0);
			}
		} else if (e[i].a0 <= 1) {
			sbs++;
			zassert_equal(e[i].a1, 1);
		} else {
			zassert_true(e[i].a0 >= 8192 && e[i].a0 <= 73727, "index area");
			ixs++;
		}
	}
	zassert_equal(chunks, 5u, "5 chunks, 5 writes");
	zassert_equal(sbs, 2u, "the superblock at open and at close");
	zassert_equal(ixs, 1u, "one CLOSE record");
}

/* S5: the chunk sectors of the whole card are not rewritten while the same recording runs on (no overwrite of data) */
ZTEST(store_svc, test_no_rewrite_during_recording)
{
	struct rst_mount_info mi;
	uint32_t id;
	uint8_t s[512];

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	put_wait(id, 0);
	rhw_sim_disk_peek(81920 + 65, s);              /* chunk seq 1's header sector, kept to compare later */
	uint8_t first[512];

	memcpy(first, s, sizeof(first));
	for (uint32_t i = 1; i < 6; i++) {
		put_wait(id, i);
	}
	rhw_sim_disk_peek(81920 + 65, s);
	zassert_equal(memcmp(first, s, sizeof(s)), 0, "an earlier chunk is not touched by the later ones");
	uint32_t uniq = rhw_sim_disk_stored();

	zassert_true(uniq >= 6 * 65, "6 chunks on the card");
	/* the number of write calls equals the number of chunks plus the superblock at open (no extra writes) */
	zassert_equal(rhw_sim_disk_write_calls(), 1u /* boot superblock */ + 1u /* open */ + 6u);
}

/* S18, S19: the superblock twice per recording (open, close); VDD_SD stays on for the whole recording */
ZTEST(store_svc, test_superblock_twice_per_recording)
{
	static const uint16_t kinds[] = { RHW_EV_DISK_WRITE, RHW_EV_PMIC_RAIL, RHW_EV_DISK_INIT, RHW_EV_DISK_DEINIT };
	struct rhw_sim_ev e[40];
	struct rst_mount_info mi;
	struct rst_close_args a = no_hl();
	uint32_t id;

	tst_card(100);
	tst_mount_boot(&mi);
	uint32_t from = rhw_sim_log_count();

	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	put_wait(id, 0);
	put_wait(id, 1);
	zassert_equal(rst_close(NULL, &a), 0);
	uint32_t n = collect(from, kinds, ARRAY_SIZE(kinds), e, 40), sb = 0;
	int64_t sb_lba[2] = { -1, -1 };

	for (uint32_t i = 0; i < n; i++) {
		zassert_equal(e[i].kind, RHW_EV_DISK_WRITE, "no rail or init event between open and close");
		if (e[i].a0 <= 1) {
			sb_lba[sb < 2 ? sb : 0] = e[i].a0;
			sb++;
		}
	}
	zassert_equal(sb, 2u);
	zassert_true(sb_lba[0] != sb_lba[1], "the two superblock writes go to the two copies in turn");
	zassert_true(rhw_pmic()->rail_get(RHW_RAIL_SD), "VDD_SD still on after the close (the join switches it off)");
	zassert_equal(rst_unmount(), 0);
	zassert_false(rhw_pmic()->rail_get(RHW_RAIL_SD));
}

/* S20, C15: a failed chunk write is retried twice at once (3 tries); then the fault, the superblock left open */
ZTEST(store_svc, test_three_tries_then_fault_open_flag_kept)
{
	struct rst_mount_info mi;
	struct rst_close_args a = no_hl();
	uint32_t id;
	uint8_t s[512];
	struct rst_sb sb;

	/* two failures: the third try works, no fault */
	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	uint32_t w0 = rhw_sim_disk_write_calls();

	rhw_sim_disk_fail_write(1, 2);
	put_wait(id, 0);
	zassert_equal(tst_done_last_err(), 0, "written on the third try");
	zassert_equal(rhw_sim_disk_write_calls() - w0, 3u, "1 + 2 tries");
	zassert_equal(fault_n, 0);
	put_wait(id, 1);
	zassert_equal(rst_close(NULL, &a), 0);

	/* three failures: the fault */
	svc_before(NULL);
	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	w0 = rhw_sim_disk_write_calls();
	rhw_sim_disk_fail_write(1, 3);
	tst_fill(&big, id, 0, 8192, 0);
	static struct rst_chunk second;

	tst_fill(&second, id, 1, 8192, 1);
	zassert_equal(rst_put_chunk(&big, tst_done_cb), 0);
	zassert_equal(rst_put_chunk(&second, tst_done_cb), 0, "a second chunk waits behind the first");
	zassert_true(tst_wait_done(2, 20000));
	zassert_equal(tst_done_last_err(), -EIO);
	zassert_equal(fault_n, 1, "the write fault is reported once");
	zassert_equal(fault_err, -EIO);
	zassert_equal(rhw_sim_disk_write_calls() - w0, 3u, "3 tries, and nothing more for the chunk behind it");
	zassert_equal(rst_put_chunk(&big, tst_done_cb), -EIO, "after the fault no chunk is taken");
	zassert_equal(rst_close(NULL, &a), -EIO, "no close after a fault: the superblock stays open");

	/* the card: superblock still says open, no CLOSE record */
	uint8_t a_[512], b_[512];
	int which;

	rhw_sim_disk_peek(0, a_);
	rhw_sim_disk_peek(1, b_);
	zassert_equal(rst_log_pick_sb(a_, b_, &sb, &which), 0);
	zassert_equal(sb.open_flag, 1, "open flag kept");
	zassert_equal(sb.open_recording_id, id);
	rhw_sim_disk_peek(8192 + 1, s);
	struct rst_ix x;

	zassert_true(rst_fmt_ix_decode(s, &x) != 0, "no CLOSE record");
	tst_reboot();
	tst_mount_boot(&mi);
	zassert_true(mi.open_flag, "the next start goes to RECOVERY");
}

/* C24: one recording open at a time; none starts while the open flag is set (ruling R4b) */
ZTEST(store_svc, test_one_open_recording)
{
	struct rst_mount_info mi;
	struct rst_close_args a = no_hl();
	uint32_t id, id2;

	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), -ENODEV, "not mounted");
	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	zassert_equal(id, 1u);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id2), -EBUSY, "a second recording while one is open");
	zassert_equal(rst_close(NULL, &a), 0);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id2), 0);
	zassert_equal(id2, 2u, "ids are never reused");
	tst_reboot();
	tst_mount_boot(&mi);
	zassert_true(mi.open_flag);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), -EPERM, "the open flag is set: recovery first");
	zassert_equal(rst_recover(NULL, NULL), 0);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	zassert_equal(id, 3u);
	zassert_equal(rst_close(NULL, &a), 0);
}

static K_THREAD_STACK_DEFINE(helper_stack, 4096);
static struct k_thread helper;
static volatile int helper_rc;

static void helper_close(void *a, void *b, void *c)
{
	struct rst_close_args args = no_hl();

	ARG_UNUSED(a);
	ARG_UNUSED(b);
	ARG_UNUSED(c);
	helper_rc = rst_close(NULL, &args);
}

/* C24: no storage operation runs while another one does: the second call returns -EBUSY at once (FW l.219) */
ZTEST(store_svc, test_busy_while_operation_runs)
{
	struct rst_mount_info mi;
	static struct rst_rec_info li[1];
	uint16_t n;
	uint32_t id, v;
	static uint8_t buf[RREC_CHUNK_BYTES];

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	rhw_sim_disk_stall_ms(300);                    /* the close writes 2 sectors, 300 ms each */
	helper_rc = 99;
	k_thread_create(&helper, helper_stack, K_THREAD_STACK_SIZEOF(helper_stack), helper_close, NULL, NULL, NULL, 1,
			0, K_NO_WAIT);
	k_msleep(100);
	int64_t t0 = k_uptime_get();

	zassert_equal(rst_list(0, 1, li, &n), -EBUSY);
	zassert_equal(rst_confirm(1, 0), -EBUSY);
	zassert_equal(rst_delete(1, &v), -EBUSY);
	zassert_equal(rst_read_chunk(1, 0, buf), -EBUSY);
	zassert_equal(rst_log_read(0, 1, buf, &n), -EBUSY);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &v), -EBUSY);
	zassert_equal(rst_mount(false, &mi), -EBUSY);
	zassert_equal(rst_unmount(), -EBUSY);
	zassert_true(k_uptime_get() - t0 < 5, "answered at once, did not wait for the card");
	zassert_equal(k_thread_join(&helper, K_SECONDS(5)), 0);
	zassert_equal(helper_rc, 0);
	zassert_equal(rst_list(0, 1, li, &n), 0, "free again");
	zassert_equal(n, 1);
}

/* step 6 fix round 1 (R6-03): rst_unmount_wait waits for the call that runs on another thread, then unmounts (rail off);
 * with a bound shorter than that call it answers -EBUSY and changes nothing */
ZTEST(store_svc, test_unmount_wait_waits_for_running_call)
{
	struct rst_mount_info mi;
	uint32_t id;

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	rhw_sim_disk_stall_ms(300);                    /* the close writes 2 sectors, 300 ms each */
	helper_rc = 99;
	k_thread_create(&helper, helper_stack, K_THREAD_STACK_SIZEOF(helper_stack), helper_close, NULL, NULL, NULL, 1,
			0, K_NO_WAIT);
	k_msleep(100);
	zassert_equal(rst_unmount_wait(50), -EBUSY, "the close runs longer than 50 ms");
	zassert_true(rst_mounted(), "nothing changed");
	zassert_true(rhw_pmic()->rail_get(RHW_RAIL_SD), "VDD_SD still on");
	int64_t t0 = k_uptime_get();

	zassert_equal(rst_unmount_wait(5000), 0, "waited for the close, then unmounted");
	TC_PRINT("rst_unmount_wait waited %lld ms for the running close\n", k_uptime_get() - t0);
	zassert_true(k_uptime_get() - t0 >= 100, "it waited for the running call");
	zassert_false(rst_mounted(), "unmounted");
	zassert_false(rhw_pmic()->rail_get(RHW_RAIL_SD), "VDD_SD off");
	zassert_equal(k_thread_join(&helper, K_SECONDS(5)), 0);
	zassert_equal(helper_rc, 0, "the close itself succeeded");
}

/* the ring of 3: a fourth chunk waits for nobody and is refused, nothing is overwritten */
ZTEST(store_svc, test_put_chunk_ring_of_three)
{
	static struct rst_chunk c[4];
	struct rst_mount_info mi;
	uint32_t id;

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(rst_put_chunk(&c[0], tst_done_cb), -EINVAL, "no open recording");
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	rhw_sim_disk_stall_ms(1000);
	for (uint32_t i = 0; i < 4; i++) {
		tst_fill(&c[i], id, i, 8192, i);
	}
	int64_t t0 = k_uptime_get();

	for (int i = 0; i < 3; i++) {
		zassert_equal(rst_put_chunk(&c[i], tst_done_cb), 0, "chunk %d", i);
	}
	zassert_equal(rst_put_chunk(&c[3], tst_done_cb), -ENOBUFS, "the fourth");
	zassert_true(k_uptime_get() - t0 < 5, "never blocks");
	zassert_true(tst_wait_done(1, 3000));
	zassert_equal(rst_put_chunk(&c[3], tst_done_cb), 0, "a place is free again");
	zassert_true(tst_wait_done(4, 10000));
	zassert_equal(c[0].hdr.chunk_seq, 1u);
	zassert_equal(c[3].hdr.chunk_seq, 4u);
	zassert_equal(c[2].hdr.recording_id, id);
	tst_fill(&c[0], id, 0, 0, 0);
	zassert_equal(rst_put_chunk(&c[0], tst_done_cb), -EINVAL, "a chunk with 0 frames");
}

/* unmount waits for the queued chunks, then deinit, suspend, rail off */
ZTEST(store_svc, test_unmount_waits_for_chunks)
{
	static const uint16_t kinds[] = { RHW_EV_DISK_WRITE, RHW_EV_DISK_DEINIT, RHW_EV_SDBUS_SUSPEND, RHW_EV_PMIC_RAIL };
	struct rhw_sim_ev e[10];
	struct rst_mount_info mi;
	uint32_t id;

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 0, &id), 0);
	uint32_t from = rhw_sim_log_count();

	rhw_sim_disk_stall_ms(200);
	tst_fill(&big, id, 0, 8192, 0);
	zassert_equal(rst_put_chunk(&big, tst_done_cb), 0);
	zassert_equal(rst_unmount(), 0);
	uint32_t n = collect(from, kinds, ARRAY_SIZE(kinds), e, 10);

	zassert_equal(n, 4u);
	zassert_equal(e[0].kind, RHW_EV_DISK_WRITE);
	zassert_equal(e[0].a1, 65);
	zassert_equal(e[1].kind, RHW_EV_DISK_DEINIT);
	zassert_equal(e[2].kind, RHW_EV_SDBUS_SUSPEND);
	zassert_equal(e[3].kind, RHW_EV_PMIC_RAIL);
	zassert_equal(tst_done_count(), 1);
}

/* D14: boot_count grows at each mount in BOOT (once per boot), not at other mounts */
ZTEST(store_svc, test_boot_count)
{
	struct rst_mount_info mi;

	tst_card(100);
	zassert_equal(rst_mount(true, &mi), 0);
	zassert_equal(mi.boot_count, 1u);
	zassert_equal(rhw_sim_disk_write_calls(), 1u, "the superblock once for the boot");
	zassert_equal(rst_mount(true, &mi), 0, "already mounted: nothing changes");
	zassert_equal(mi.boot_count, 1u);
	zassert_equal(rst_unmount(), 0);
	zassert_equal(rst_mount(false, &mi), 0, "a mount that is not BOOT's");
	zassert_equal(mi.boot_count, 1u);
	zassert_equal(rst_unmount(), 0);
	tst_reboot();
	zassert_equal(rst_mount(true, &mi), 0);
	zassert_equal(mi.boot_count, 2u);
	tst_reboot();
	zassert_equal(rst_mount(true, &mi), 0);
	zassert_equal(mi.boot_count, 3u);
}

/* a whole recording: 3 full chunks and a partial last chunk, then list, read back, digest */
ZTEST(store_svc, test_full_cycle_with_partial_last_chunk)
{
	struct rst_mount_info mi;
	static struct rst_chunk last;
	static struct rst_rec_info li[2];
	static uint8_t rb[RREC_CHUNK_BYTES];
	struct rst_chunk_hdr h;
	struct rst_close_args a = { .duration_frames = 3u * 8192u + 3000u, .highlight_count = 1 };
	uint32_t id;
	uint16_t n;

	memset(a.highlight_ms, 0xFF, sizeof(a.highlight_ms));
	a.highlight_ms[0] = 4321;
	tst_card(100);
	tst_mount_boot(&mi);
	zassert_equal(rst_open(RREC_REC_TYPE_RECORDING, 1700000000000ll, &id), 0);
	for (uint32_t i = 0; i < 3; i++) {
		put_wait(id, i);
	}
	tst_fill(&last, id, 3, 3000, 3);
	last.hdr.flags |= RREC_CH_FLAG_LAST;
	zassert_equal(rst_close(&last, &a), 0);
	zassert_equal(rst_list(0, 2, li, &n), 0);
	zassert_equal(n, 1);
	zassert_equal(li[0].recording_id, id);
	zassert_equal(li[0].type, RREC_REC_TYPE_RECORDING);
	zassert_equal(li[0].channels, 2);
	zassert_equal(li[0].state, RREC_LIST_STATE_NEW);
	zassert_equal(li[0].first_chunk_seq, 1u);
	zassert_equal(li[0].chunk_count, 4u);
	zassert_equal(li[0].sample_rate_hz, 16000u);
	zassert_equal(li[0].start_utc_ms, 1700000000000ll);
	zassert_equal(li[0].duration_frames, 3u * 8192u + 3000u);
	zassert_equal(li[0].highlight_count, 1);
	/* the digest: the payload CRCs of the 4 chunks as the card holds them (the last with its zeroed tail) */
	uint8_t w[16];

	for (uint32_t i = 0; i < 4; i++) {
		zassert_equal(rst_read_chunk(id, i, rb), 0);
		zassert_equal(rst_fmt_chunk_verify(rb, &h, NULL), 0);
		tst_le(w, i * 4, tst_crc32(rb + 512, 32768), 4);
		zassert_equal(h.chunk_seq, i + 1);
		zassert_equal(h.chunk_in_recording, i);
	}
	zassert_equal(li[0].digest, tst_crc32(w, sizeof(w)), "digest over the 4 payload CRCs");
	zassert_equal(h.frames, 3000u);
	zassert_true((h.flags & RREC_CH_FLAG_LAST) != 0);
	zassert_equal(rst_get32(rb + 36), 12000u, "payload_bytes of the partial chunk");
	for (uint32_t i = 512 + 12000; i < RREC_CHUNK_BYTES; i++) {
		zassert_equal(rb[i], 0, "zero tail at %u", i);
	}
	struct rst_space sp;

	zassert_equal(rst_space(&sp), 0);
	zassert_equal(sp.used, 4u);
}

/* S4: the chunk area is a ring: chunk seq 25 on a card of 24 chunks lands where seq 1 was */
ZTEST(store_svc, test_chunks_wrap_on_small_card)
{
	struct rst_mount_info mi;
	uint32_t id, dg, freed;
	static uint8_t rb[RREC_CHUNK_BYTES];
	struct rst_chunk_hdr h;

	tst_card(24);
	tst_mount_boot(&mi);
	zassert_equal(mi.space.total, 24u);
	for (int r = 0; r < 5; r++) {
		zassert_equal(tst_record(RREC_REC_TYPE_RECORDING, 6, &id, &dg), 0, "recording %d", r);
		zassert_equal(rst_confirm(id, dg), 0);
		if (r < 4) {
			zassert_equal(rst_delete(id, &freed), 0);
			zassert_equal(freed, 24u);
		}
	}
	/* recording 5 holds chunk seq 25 to 30: seq 25 is at the LBA of seq 1 (25 mod 24 = 1) */
	zassert_equal(rst_read_chunk(id, 0, rb), 0);
	zassert_equal(rst_fmt_chunk_verify(rb, &h, NULL), 0);
	zassert_equal(h.chunk_seq, 25u);
	rhw_sim_disk_peek(81920 + 65, rb);
	zassert_equal(rst_get32(rb + 8), 25u, "the sector where chunk 1 was");
	rhw_sim_disk_peek(81920, rb);
	zassert_equal(rst_get32(rb + 8), 24u, "chunk 24 is in the first slot of the ring (24 mod 24 = 0)");
	struct rst_space sp;

	zassert_equal(rst_space(&sp), 0);
	zassert_equal(sp.used, 6u);
}

/* T-STORE (FW l.1030): 65 sectors at LBA 4,096 written, read back, compared, both timed */
ZTEST(store_svc, test_factory_area_test)
{
	struct rst_mount_info mi;
	struct rst_factory_result fr;
	uint8_t s[512];

	tst_card(100);
	tst_mount_boot(&mi);
	uint32_t w0 = rhw_sim_disk_write_calls();

	rhw_sim_disk_stall_ms(4);
	zassert_equal(rst_factory_area_test(&fr), 0);
	zassert_true(fr.equal);
	zassert_equal(rhw_sim_disk_write_calls() - w0, 1u, "one write of 65 sectors");
	zassert_true(fr.write_us >= 4000u, "write took %u us", fr.write_us);
	zassert_true(fr.write_us < 20000u);
	rhw_sim_disk_peek(4096, s);
	zassert_true(s[1] != 0 || s[2] != 0);
	rhw_sim_disk_peek(4160, s);
	zassert_true(s[1] != 0 || s[2] != 0, "up to LBA 4,160");
	rhw_sim_disk_peek(4161, s);
	zassert_equal(s[1], 0u);
}

/* the reboot hook of the simulation: a power cycle clears the store's RAM state */
ZTEST(store_svc, test_sim_reboot_clears_ram_state)
{
	struct rst_mount_info mi;
	struct rst_space sp;

	tst_card(100);
	tst_mount_boot(&mi);
	zassert_true(rst_mounted());
	zassert_equal(rst_space(&sp), 0);
	rhw_sim_reboot();
	zassert_false(rst_mounted());
	zassert_equal(rst_space(&sp), -ENODEV, "no space before the first mount");
}
