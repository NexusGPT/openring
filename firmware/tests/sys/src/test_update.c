/* Suite sys_update (software step 6, unit U7): the firmware update over USB (FW 9.2) and its 30 s self-test, on the
 * simulated image store. Rows T5, T6, T8, T9, T10 of the plan. Expected values are literals written from
 * design/firmware.md (lines cited), never computed by the code under test. Time is the kernel's simulated time. */
#include "common.h"

static uint8_t img[32768];
static uint8_t back[3u * 4096u + 17u];

static void before(void *f)
{
	ARG_UNUSED(f);
	rhw_sim_reset();
}

static void after(void *f)
{
	ARG_UNUSED(f);
	t_cleanup();
}

ZTEST_SUITE(sys_update, NULL, NULL, before, after, NULL);

static bool img_write_ok_and_inside(const struct rhw_sim_ev *e)
{
	return e->res == 0 && e->a0 >= 0 && e->a1 >= 0 && e->a0 + e->a1 <= 999424;
}

/* T5, FW l.1010: the flash layout, typed from the line: MCUboot 64 KB at 0x00000000, slot 0 976 KB at 0x00010000, slot 1
 * 976 KB at 0x00104000, settings 20 KB at 0x001F8000, 2,036 KB in total (64 + 976 + 976 + 20). Not provable: the swap. */
ZTEST(sys_update, test_layout_sums_to_2036_kb)
{
	zassert_equal(RREC_FLASH_MCUBOOT_ADDR, 0x00000000u);
	zassert_equal(RREC_FLASH_MCUBOOT_BYTES, 65536u);
	zassert_equal(RREC_FLASH_SLOT0_ADDR, 0x00010000u);
	zassert_equal(RREC_FLASH_SLOT_BYTES, 999424u);
	zassert_equal(RREC_FLASH_SLOT1_ADDR, 0x00104000u);
	zassert_equal(RREC_FLASH_SETTINGS_ADDR, 0x001F8000u);
	zassert_equal(RREC_FLASH_SETTINGS_BYTES, 20480u);
	zassert_equal(RREC_FLASH_TOTAL_BYTES, 2084864u);   /* 2,036 x 1,024 */
	zassert_equal(RREC_FLASH_MCUBOOT_BYTES + 2u * RREC_FLASH_SLOT_BYTES + RREC_FLASH_SETTINGS_BYTES,
		      2036u * 1024u);
	/* slot 1 ends where the settings begin, slot 0 ends where slot 1 begins (0x00104000 + 976 x 1,024 = 0x001F8000) */
	zassert_equal(RREC_FLASH_SLOT0_ADDR + RREC_FLASH_SLOT_BYTES, RREC_FLASH_SLOT1_ADDR);
	zassert_equal(RREC_FLASH_SLOT1_ADDR + RREC_FLASH_SLOT_BYTES, RREC_FLASH_SETTINGS_ADDR);
	zassert_equal(RREC_IMAGE_MAX_BYTES, 999424u);      /* FW l.1012: 976 KB = 999,424 bytes */
	zassert_equal(RREC_SELFTEST_MS, 30000u);           /* FW l.1014 */
	TC_PRINT("EVIDENCE sys_update layout: sum %u KB, image max %u bytes\n",
		 (unsigned)(RREC_FLASH_TOTAL_BYTES / 1024u), (unsigned)RREC_IMAGE_MAX_BYTES);
}

/* T6, FW l.1012 rule 1: FW_BEGIN refuses an image_size above 999,424 bytes with BAD_ARG (4); 999,424 is accepted. */
ZTEST(sys_update, test_size_limit)
{
	t_init();
	zassert_equal(rsy_fw_begin(999425u, 0u, 1000u, true), 4, "999,425 bytes refused with BAD_ARG");
	zassert_equal(rsy_fw_begin(0u, 0u, 1000u, true), 4, "size 0 refused with BAD_ARG");
	zassert_equal(rsy_fw_begin(4294967295u, 0u, 1000u, true), 4, "4,294,967,295 refused with BAD_ARG");
	zassert_equal(ev_count(RHW_EV_IMG_ERASE), 0u, "a refused FW_BEGIN erases nothing");
	/* a refused FW_BEGIN starts no update: FW_DATA is refused (BAD_ARG) */
	img[0] = 1;
	zassert_equal(rsy_fw_data(0u, img, 1u), 4, "no FW_BEGIN in force after a refusal");
	zassert_equal(rsy_fw_begin(999424u, 0u, 1000u, true), RREC_ST_OK, "999,424 bytes accepted");
	zassert_equal(ev_count(RHW_EV_IMG_ERASE), 1u, "the accepted FW_BEGIN erased slot 1");
	TC_PRINT("EVIDENCE sys_update size: 999424 -> OK, 999425 -> BAD_ARG(4), erases %u\n",
		 (unsigned)ev_count(RHW_EV_IMG_ERASE));
}

/* T6, FW l.1012 rule 1: FW_DATA refuses an offset plus length past the limit with BAD_ARG, and writes nothing then. */
ZTEST(sys_update, test_data_end_limit)
{
	t_init();
	t_fill(img, sizeof(img), 3);
	/* declared size 999,424: the last byte is at 999,423 */
	zassert_equal(rsy_fw_begin(999424u, 0u, 1000u, true), RREC_ST_OK);
	zassert_equal(rsy_fw_data(999324u, img, 100u), RREC_ST_OK, "end exactly at 999,424 accepted");
	uint32_t w = ev_count(RHW_EV_IMG_WRITE);

	zassert_equal(w, 1u);
	zassert_equal(rsy_fw_data(999324u, img, 101u), 4, "end at 999,425 refused (BAD_ARG)");
	zassert_equal(rsy_fw_data(999424u, img, 1u), 4, "offset 999,424 refused");
	zassert_equal(rsy_fw_data(4294967295u, img, 2u), 4, "a sum that wraps 32 bits is refused");
	zassert_equal(ev_count(RHW_EV_IMG_WRITE), w, "refused FW_DATA writes nothing");
	/* a smaller declared image: the end of the image is the limit */
	zassert_equal(rsy_fw_begin(8192u, 0u, 1000u, true), RREC_ST_OK);
	zassert_equal(rsy_fw_data(4096u, img, 4096u), RREC_ST_OK, "end exactly at 8,192 accepted");
	zassert_equal(rsy_fw_data(4096u, img, 4097u), 4, "end at 8,193 refused");
	zassert_equal(rsy_fw_data(8192u, img, 1u), 4, "offset 8,192 refused");
	zassert_equal(ev_count(RHW_EV_IMG_WRITE), w + 1u);
	/* FW_DATA without FW_BEGIN in force is refused */
	t_next_boot();
	zassert_equal(rsy_fw_data(0u, img, 16u), 4, "FW_DATA without FW_BEGIN: BAD_ARG");
	TC_PRINT("EVIDENCE sys_update data end: 999424 ok, 999425 BAD_ARG, 8192 ok, 8193 BAD_ARG\n");
}

/* T6, FW l.1012 rules 1 and 2: every write of the update path lands inside slot 1 at the offset the case sent (the
 * image store has no call for slot 0 or the MCUboot area); a write that goes to the wrong place is seen in the log. */
ZTEST(sys_update, test_writes_only_slot1)
{
	const uint32_t total = 3u * 4096u + 17u;

	t_init();
	t_fill(img, total, 9);
	zassert_equal(rsy_fw_begin(total, 0u, 1000u, true), RREC_ST_OK);
	for (uint32_t off = 0; off < total; off += 4096u) {
		uint32_t n = total - off < 4096u ? total - off : 4096u;

		zassert_equal(rsy_fw_data(off, img + off, n), RREC_ST_OK, "block at %u", off);
	}
	int32_t erase = ev_find(RHW_EV_IMG_ERASE, 0);
	uint32_t seen = 0;
	struct rhw_sim_ev e;

	zassert_true(erase >= 0, "slot 1 erased first");
	for (uint32_t i = 0; i < rhw_sim_log_count(); i++) {
		zassert_true(ev_get((int32_t)i, &e));
		if (e.kind != RHW_EV_IMG_WRITE) {
			continue;
		}
		zassert_true((int32_t)i > erase, "a write before the erase");
		zassert_true(img_write_ok_and_inside(&e), "write %u: offset %lld len %lld res %d outside slot 1 (999,424)",
			     seen, e.a0, e.a1, e.res);
		zassert_equal(e.a0, (int64_t)seen * 4096, "write %u at offset %lld", seen, e.a0);
		zassert_equal(e.a1, seen < 3u ? 4096 : 17, "write %u length %lld", seen, e.a1);
		seen++;
	}
	zassert_equal(seen, 4u, "four writes (3 x 4,096 + 17)");
	rhw_sim_image_peek(0u, back, total);
	zassert_mem_equal(back, img, total, "slot 1 holds the image at the offsets sent");
	TC_PRINT("EVIDENCE sys_update slot1: %u writes, all inside 0..999424 and at the offsets sent\n", (unsigned)seen);
}

/* T8, FW l.1013: FW_BEGIN erases slot 1; FW_DATA blocks; FW_END checks the CRC-32 and requests the test upgrade; the
 * reboot comes after the OK response and is the join's (not done by FW_END). Image "123456789": CRC-32 0xCBF43926. */
ZTEST(sys_update, test_sequence)
{
	static const uint8_t nine[9] = { '1', '2', '3', '4', '5', '6', '7', '8', '9' };
	uint32_t crc;

	t_init();
	zassert_equal(rsy_fw_begin(9u, 0xCBF43926u, 1000u, false), RREC_ST_OK);
	zassert_equal(rsy_fw_data(0u, nine, 9u), RREC_ST_OK);
	zassert_false(rhw_sim_image_upgrade_requested(), "no upgrade requested before FW_END");
	zassert_equal(rsy_fw_end(), RREC_ST_OK);
	zassert_true(rhw_sim_image_upgrade_requested(), "test upgrade requested after the CRC matched");
	int32_t er = ev_find(RHW_EV_IMG_ERASE, 0);
	int32_t wr = ev_find(RHW_EV_IMG_WRITE, 0);
	int32_t rd = ev_find(RHW_EV_IMG_READ, 0);
	int32_t rq = ev_find(RHW_EV_IMG_REQUEST, 0);

	zassert_true(er >= 0 && wr > er && rd > wr && rq > rd, "order erase %d, write %d, read-back %d, request %d", er, wr,
		     rd, rq);
	zassert_equal(rhw_sim_image_reboots(), 0u, "FW_END itself does not reboot");
	/* a second FW_DATA or FW_END without a new FW_BEGIN is refused */
	zassert_equal(rsy_fw_data(0u, nine, 9u), 4);
	zassert_equal(rsy_fw_end(), 10, "FW_END without FW_BEGIN: FW_ERROR");
	/* an image of several 4,096-byte blocks, its CRC from the library (the typed case above settles the library) */
	const uint32_t total = 5u * 4096u + 100u;

	t_fill(img, total, 21);
	crc = crc32_ieee(img, total);
	zassert_equal(rsy_fw_begin(total, crc, 1000u, true), RREC_ST_OK);
	for (uint32_t off = 0; off < total; off += 4096u) {
		zassert_equal(rsy_fw_data(off, img + off, total - off < 4096u ? total - off : 4096u), RREC_ST_OK);
	}
	zassert_equal(rsy_fw_end(), RREC_ST_OK, "a multi-block image checks out");
	zassert_equal(ev_count(RHW_EV_IMG_REQUEST), 2u);
	TC_PRINT("EVIDENCE sys_update sequence: erase %d < write %d < read %d < request %d, reboots by FW_END %u\n", er, wr,
		 rd, rq, (unsigned)rhw_sim_image_reboots());
}

/* T8: FW_END with a CRC that does not match answers FW_ERROR (10) and requests nothing. Outside answers: a write error
 * and a read-back that cannot be done are FW_ERROR too. */
ZTEST(sys_update, test_end_bad_crc_fw_error)
{
	static const uint8_t nine[9] = { '1', '2', '3', '4', '5', '6', '7', '8', '9' };
	static const uint8_t nine_bad[9] = { '1', '2', '3', '4', '5', '6', '7', '8', '0' };

	t_init();
	zassert_equal(rsy_fw_end(), 10, "FW_END without FW_BEGIN: FW_ERROR");
	/* wrong CRC announced */
	zassert_equal(rsy_fw_begin(9u, 0xCBF43927u, 1000u, true), RREC_ST_OK);
	zassert_equal(rsy_fw_data(0u, nine, 9u), RREC_ST_OK);
	zassert_equal(rsy_fw_end(), 10, "announced CRC differs by one bit: FW_ERROR");
	zassert_false(rhw_sim_image_upgrade_requested(), "nothing requested");
	zassert_equal(ev_count(RHW_EV_IMG_REQUEST), 0u);
	/* a byte of the image differs from the one the CRC was made for */
	zassert_equal(rsy_fw_begin(9u, 0xCBF43926u, 1000u, true), RREC_ST_OK);
	zassert_equal(rsy_fw_data(0u, nine_bad, 9u), RREC_ST_OK);
	zassert_equal(rsy_fw_end(), 10, "one byte differs: FW_ERROR");
	/* only part of the image was sent: the rest reads as erased bytes */
	zassert_equal(rsy_fw_begin(9u, 0xCBF43926u, 1000u, true), RREC_ST_OK);
	zassert_equal(rsy_fw_data(0u, nine, 5u), RREC_ST_OK);
	zassert_equal(rsy_fw_end(), 10, "an incomplete image: FW_ERROR");
	/* a write error of the store: FW_ERROR (the second write fails) */
	rhw_sim_image_write_error(2u);
	zassert_equal(rsy_fw_begin(9u, 0xCBF43926u, 1000u, true), RREC_ST_OK);
	zassert_equal(rsy_fw_data(0u, nine, 4u), RREC_ST_OK, "first write works");
	zassert_equal(rsy_fw_data(4u, nine + 4, 5u), 10, "second write fails: FW_ERROR");
	rhw_sim_image_write_error(0u);
	zassert_equal(ev_count(RHW_EV_IMG_REQUEST), 0u, "no test upgrade requested in any failing case");
	TC_PRINT("EVIDENCE sys_update bad crc: FW_END -> FW_ERROR(10) in 4 cases, upgrade requests %u\n",
		 (unsigned)ev_count(RHW_EV_IMG_REQUEST));
}

/* T10, FW l.1015 and ruling D12: allowed only with the battery ABOVE 30 % or VBUS present; otherwise NOT_ALLOWED (11).
 * soc_x10 is in tenths of a percent: 300 = 30.0 %. */
ZTEST(sys_update, test_allowed_rule)
{
	t_init();
	zassert_equal(rsy_fw_begin(100u, 0u, 300u, false), 11, "30.0 % without VBUS: NOT_ALLOWED");
	zassert_equal(rsy_fw_begin(100u, 0u, 299u, false), 11, "29.9 %: NOT_ALLOWED");
	zassert_equal(rsy_fw_begin(100u, 0u, 0u, false), 11, "0 %: NOT_ALLOWED");
	zassert_equal(ev_count(RHW_EV_IMG_ERASE), 0u, "a refused update erases nothing");
	zassert_equal(rsy_fw_begin(100u, 0u, 301u, false), RREC_ST_OK, "30.1 % without VBUS: accepted");
	zassert_equal(rsy_fw_begin(100u, 0u, 1000u, false), RREC_ST_OK, "100 %: accepted");
	zassert_equal(rsy_fw_begin(100u, 0u, 0u, true), RREC_ST_OK, "0 % with VBUS: accepted");
	zassert_equal(rsy_fw_begin(100u, 0u, 300u, true), RREC_ST_OK, "30.0 % with VBUS: accepted");
	zassert_equal(ev_count(RHW_EV_IMG_ERASE), 4u);
	TC_PRINT("EVIDENCE sys_update allowed: 300 no-VBUS -> 11, 301 -> OK, VBUS any -> OK\n");
}

/* T9, FW l.1014: all items pass: confirm. Without VBUS the USB item is not needed; with VBUS it is. */
ZTEST(sys_update, test_self_test_pass_confirms)
{
	t_init();
	rhw_sim_image_set_confirmed(false);
	zassert_equal(rsy_selftest_start(true), 1, "an unconfirmed image starts the self-test");
	zassert_true(rsy_selftest_running());
	rsy_selftest_pass(RSY_ITEM_STORAGE);
	rsy_selftest_pass(RSY_ITEM_BLUETOOTH);
	zassert_equal(ev_count(RHW_EV_IMG_CONFIRM), 0u, "with VBUS the USB item is still missing");
	zassert_true(rsy_selftest_running());
	rsy_selftest_pass(RSY_ITEM_USB);
	zassert_equal(ev_count(RHW_EV_IMG_CONFIRM), 1u, "all three passed: confirmed");
	zassert_false(rsy_selftest_running());
	zassert_equal(t_nlog(), 1);
	zassert_equal(t_log_at(0)->code, RREC_LOG_SELFTEST);
	zassert_equal(t_log_at(0)->args[0], 0, "log result 0 = pass");
	zassert_equal(t_log_at(0)->args[1], 7, "log mask: storage, Bluetooth and USB");
	rsy_selftest_pass(RSY_ITEM_USB);
	k_sleep(K_MSEC(31000));
	zassert_equal(rhw_sim_image_reboots(), 0u, "a passed self-test never reboots at 30 s");
	zassert_equal(ev_count(RHW_EV_IMG_CONFIRM), 1u, "one confirm only");
	TC_PRINT("EVIDENCE sys_update self-test pass: confirm events %u, reboots %u, log result %u mask %u\n",
		 (unsigned)ev_count(RHW_EV_IMG_CONFIRM), (unsigned)rhw_sim_image_reboots(), t_log_at(0)->args[0],
		 t_log_at(0)->args[1]);

	/* no VBUS: storage and Bluetooth are enough; passing the same item twice counts once */
	t_cleanup();
	t_init();
	rhw_sim_image_set_confirmed(false);
	zassert_equal(rsy_selftest_start(false), 1);
	rsy_selftest_pass(RSY_ITEM_STORAGE);
	rsy_selftest_pass(RSY_ITEM_STORAGE);
	zassert_equal(ev_count(RHW_EV_IMG_CONFIRM), 0u, "the same item twice is not two items");
	rsy_selftest_pass(RSY_ITEM_BLUETOOTH);
	zassert_equal(ev_count(RHW_EV_IMG_CONFIRM), 1u, "no VBUS: two items confirm");
	zassert_equal(t_log_at(0)->args[1], 3);

	/* a confirmed image: nothing to do, no window, no reboot, a late pass is ignored */
	t_cleanup();
	t_init();
	rhw_sim_image_set_confirmed(true);
	zassert_equal(rsy_selftest_start(true), 0, "a confirmed image: nothing to do");
	zassert_false(rsy_selftest_running());
	rsy_selftest_pass(RSY_ITEM_STORAGE);
	rsy_selftest_pass(RSY_ITEM_BLUETOOTH);
	rsy_selftest_pass(RSY_ITEM_USB);
	k_sleep(K_MSEC(31000));
	zassert_equal(ev_count(RHW_EV_IMG_CONFIRM), 0u);
	zassert_equal(rhw_sim_image_reboots(), 0u);
}

/* T9, FW l.1014: 30 s pass without every item: reboot without confirming. */
ZTEST(sys_update, test_self_test_timeout_reboots)
{
	t_init();
	rhw_sim_image_set_confirmed(false);
	zassert_equal(rsy_selftest_start(false), 1);
	int32_t start_ev = ev_find(RHW_EV_IMG_IS_CONFIRMED, 0);

	zassert_true(start_ev >= 0);
	rsy_selftest_pass(RSY_ITEM_STORAGE);   /* only one of the two needed items */
	k_sleep(K_MSEC(29900));
	zassert_true(rsy_selftest_running(), "still running at 29.9 s");
	zassert_equal(rhw_sim_image_reboots(), 0u, "no reboot before 30 s");
	k_sleep(K_MSEC(200));                  /* now 30.1 s after the start */
	zassert_false(rsy_selftest_running(), "the window ended");
	zassert_equal(rhw_sim_image_reboots(), 1u, "rebooted once");
	zassert_equal(rhw_sim_image_last_reboot(), 5, "reason SELFTEST_FAIL (5)");
	zassert_equal(ev_count(RHW_EV_IMG_CONFIRM), 0u, "never confirmed");
	struct rhw_sim_ev s, r;

	zassert_true(ev_get(start_ev, &s));
	zassert_true(ev_get(ev_find(RHW_EV_IMG_REBOOT, 0), &r));
	int64_t dt_us = r.t_us - s.t_us;

	zassert_true(dt_us >= 30000000 && dt_us <= 30005000, "reboot %lld us after the start (30 s = 30,000,000 us)", dt_us);
	zassert_equal(t_nlog(), 1);
	zassert_equal(t_log_at(0)->code, RREC_LOG_SELFTEST);
	zassert_equal(t_log_at(0)->args[0], 2, "log result 2 = window ended");
	zassert_equal(t_log_at(0)->args[1], 1, "log mask: storage only");
	TC_PRINT("EVIDENCE sys_update self-test timeout: reboot %lld us after the start, reason %d, confirms %u\n", dt_us,
		 rhw_sim_image_last_reboot(), (unsigned)ev_count(RHW_EV_IMG_CONFIRM));
}

/* T9, FW l.1014: the microphones are not powered in the self-test: neither rail nor input is touched by the unit, in the
 * passing run and in the run that times out. */
ZTEST(sys_update, test_self_test_no_mic)
{
	t_init();
	rhw_sim_image_set_confirmed(false);
	zassert_equal(rsy_selftest_start(true), 1);
	rsy_selftest_pass(RSY_ITEM_STORAGE);
	rsy_selftest_pass(RSY_ITEM_BLUETOOTH);
	rsy_selftest_pass(RSY_ITEM_USB);
	zassert_equal(ev_count(RHW_EV_PMIC_RAIL), 0u, "a passing self-test switches no rail");
	zassert_equal(ev_count(RHW_EV_MIC_CONFIGURE) + ev_count(RHW_EV_MIC_START) + ev_count(RHW_EV_MIC_READ), 0u);
	zassert_equal(strlen(rhw_sim_pmic_rail_caller(RHW_RAIL_MIC)), 0u, "the microphone rail was never written");
	t_cleanup();
	t_init();
	rhw_sim_image_set_confirmed(false);
	zassert_equal(rsy_selftest_start(true), 1);
	k_sleep(K_MSEC(31000));
	zassert_equal(rhw_sim_image_reboots(), 1u);
	zassert_equal(ev_count(RHW_EV_PMIC_RAIL), 0u, "a failing self-test switches no rail");
	zassert_equal(ev_count(RHW_EV_MIC_START), 0u);
	TC_PRINT("EVIDENCE sys_update self-test no mic: rail events %u, microphone input events %u\n",
		 (unsigned)ev_count(RHW_EV_PMIC_RAIL), (unsigned)ev_count(RHW_EV_MIC_START));
}
