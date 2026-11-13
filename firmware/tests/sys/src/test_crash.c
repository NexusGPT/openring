/* Suite sys_crash (software step 6, unit U7): crash capture (FW l.1063) on the simulated retained memory. Row T28 of the
 * plan. The handler on the real chip and retained RAM across a real reset are not provable without hardware. */
#include "common.h"

#include <zephyr/fatal.h>

#include "crash_expect.h"

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

ZTEST_SUITE(sys_crash, NULL, NULL, before, after, NULL);

static uint32_t words64[64];

static void fill_words(void)
{
	for (uint32_t i = 0; i < 64u; i++) {
		words64[i] = 0xA5000000u + i;
	}
}

/* K11 compile test: the kit's declaration of the handler we override has this signature (a different one is a compile
 * error here). */
_Static_assert(__builtin_types_compatible_p(__typeof__(k_sys_fatal_error_handler),
					    void(unsigned int, const struct arch_esf *)),
	       "k_sys_fatal_error_handler signature differs from the one ring_sys overrides");

ZTEST(sys_crash, test_handler_signature_matches_kit)
{
	void (*p)(unsigned int, const struct arch_esf *) = k_sys_fatal_error_handler;

	zassert_not_null(p);
}

/* T28, FW l.1063: the crash block is reason u32, PC u32, LR u32, PSR u32, thread name 16 bytes, 64 stack words (288
 * bytes) in retained RAM; the unit adds its magic in front and a CRC-32 behind (296 bytes). Expected bytes are typed in
 * crash_expect.h from the layout by an independent script. */
ZTEST(sys_crash, test_block_format)
{
	uint8_t raw[RREC_RETAINED_BYTES];

	t_init();
	fill_words();
	zassert_equal(rsy_crash_capture(4u, 0x0001A2B4u, 0x0001A2B5u, 0x61000000u, "audio", words64, 64u), 0);
	rhw_sim_retained_get(raw, sizeof(raw));
	zassert_mem_equal(raw, crash_expect, sizeof(crash_expect), "the stored block equals the typed bytes");
	for (size_t i = sizeof(crash_expect); i < sizeof(raw); i++) {
		zassert_equal(raw[i], 0, "retained byte %u past the block is untouched", (unsigned)i);
	}
	zassert_equal(sizeof(crash_expect), 4u + RREC_CRASH_BLOCK_BYTES + 4u);
	zassert_equal(RREC_CRASH_BLOCK_BYTES, 288u, "4 x 4 + 16 + 64 x 4 (FW l.1063)");

	/* a thread name longer than 15 characters is cut so that it stays NUL-terminated; fewer than 64 words: the rest zero;
	 * more than 64: only 64 are kept */
	rhw_sim_reset();
	zassert_equal(rsy_crash_capture(3u, 1u, 2u, 3u, "abcdefghijklmnopqrstuvwxyz", words64, 10u), 0);
	rhw_sim_retained_get(raw, sizeof(raw));
	zassert_mem_equal(raw + 4 + 16, "abcdefghijklmno", 15, "name cut to 15 characters");
	zassert_equal(raw[4 + 16 + 15], 0, "name ends with NUL");
	for (uint32_t i = 0; i < 64u; i++) {
		uint32_t w = (uint32_t)raw[4 + 32 + 4 * i] | ((uint32_t)raw[4 + 33 + 4 * i] << 8) |
			     ((uint32_t)raw[4 + 34 + 4 * i] << 16) | ((uint32_t)raw[4 + 35 + 4 * i] << 24);

		zassert_equal(w, i < 10u ? 0xA5000000u + i : 0u, "stack word %u", i);
	}
	rhw_sim_reset();
	zassert_equal(rsy_crash_capture(3u, 1u, 2u, 3u, NULL, words64, 200u), 0);
	rhw_sim_retained_get(raw, sizeof(raw));
	zassert_equal(raw[4 + 16], '?', "no thread name: ?");
	TC_PRINT("EVIDENCE sys_crash format: %u stored bytes equal the typed block (crc word %02X%02X%02X%02X)\n",
		 (unsigned)sizeof(crash_expect), crash_expect[295], crash_expect[294], crash_expect[293], crash_expect[292]);
}

/* T28, FW l.1063: BOOT copies a valid crash block into the log and clears it: the copy happens once; gpregret1 is given
 * back with it and cleared too. */
ZTEST(sys_crash, test_boot_copies_valid_block_once)
{
	struct rrec_crash c;
	uint8_t gp = 0xEE;
	uint8_t raw[RREC_RETAINED_BYTES];

	t_init();
	fill_words();
	zassert_equal(rsy_crash_capture(4u, 0x0001A2B4u, 0x0001A2B5u, 0x61000000u, "audio", words64, 64u), 0);
	zassert_equal(rhw_retained()->gpregret1_set(4u), 0);
	t_next_boot();                       /* the reboot after the crash */
	memset(&c, 0, sizeof(c));
	zassert_equal(rsy_crash_take(&c, &gp), 1, "a valid block is found at boot");
	zassert_equal(c.reason, 4u);
	zassert_equal(c.pc, 0x0001A2B4u);
	zassert_equal(c.lr, 0x0001A2B5u);
	zassert_equal(c.psr, 0x61000000u);
	zassert_mem_equal(c.thread, "audio", 6);
	for (uint32_t i = 0; i < 64u; i++) {
		zassert_equal(c.stack[i], 0xA5000000u + i, "stack word %u", i);
	}
	zassert_equal(gp, 4u, "gpregret1 handed back");
	rhw_sim_retained_get(raw, sizeof(raw));
	for (size_t i = 0; i < sizeof(raw); i++) {
		zassert_equal(raw[i], 0, "retained byte %u cleared", (unsigned)i);
	}
	zassert_equal(rhw_sim_gpregret1_get(), 0, "gpregret1 cleared");
	/* once: the next boot finds nothing */
	zassert_equal(rsy_crash_take(&c, &gp), 0, "the block is not copied a second time");
	t_next_boot();
	zassert_equal(rsy_crash_take(&c, &gp), 0, "nor at the boot after");
	TC_PRINT("EVIDENCE sys_crash once: first take 1, second take 0, retained cleared, gpregret1 %u\n",
		 rhw_sim_gpregret1_get());
}

/* T28: power-up garbage and damaged blocks are not valid: nothing is returned and nothing is touched. */
ZTEST(sys_crash, test_invalid_block_ignored)
{
	struct rrec_crash c;
	uint8_t gp = 0xEE;
	uint8_t raw[RREC_RETAINED_BYTES];

	t_init();
	memset(&c, 0x5A, sizeof(c));
	zassert_equal(rsy_crash_take(&c, &gp), 0, "blank retained memory: no block");
	memset(raw, 0xFF, sizeof(raw));
	rhw_sim_retained_set(raw, sizeof(raw));
	zassert_equal(rsy_crash_take(&c, &gp), 0, "all 0xFF: no block");
	for (size_t bad = 0; bad < 4; bad++) {
		static const size_t where[4] = { 0, 4, 100, 292 };   /* magic, reason, a stack word, the CRC */

		rhw_sim_retained_set(crash_expect, sizeof(crash_expect));
		rhw_sim_retained_get(raw, sizeof(raw));
		raw[where[bad]] ^= 0x01;
		rhw_sim_retained_set(raw, sizeof(raw));
		zassert_equal(rsy_crash_take(&c, &gp), 0, "one flipped bit at byte %u: not valid", (unsigned)where[bad]);
	}
	zassert_equal(gp, 0xEE, "gpregret1 output untouched when no block is valid");
	zassert_equal(c.reason, 0x5A5A5A5Au, "the output block untouched when no block is valid");
	zassert_equal(ev_count(RHW_EV_RET_CLEAR), 0u, "an invalid area is left as it is");
	zassert_equal(rsy_crash_take(NULL, &gp), 0, "no output: nothing taken");
	/* the intact block is still valid and is taken (gp output may be NULL) */
	rhw_sim_retained_set(crash_expect, sizeof(crash_expect));
	zassert_equal(rsy_crash_take(&c, NULL), 1);
	TC_PRINT("EVIDENCE sys_crash invalid: blank, 0xFF and 4 damaged blocks all rejected, retained clears %u\n",
		 (unsigned)ev_count(RHW_EV_RET_CLEAR));
}

/* T28, FW l.1063: the fatal path writes the block, puts the reason code into gpregret1, then reboots (in this order). */
ZTEST(sys_crash, test_fatal_path_order)
{
	struct rrec_crash c;
	uint8_t gp = 0;

	t_init();
	rsy_fatal(4u, NULL);
	int32_t w = ev_find(RHW_EV_RET_WRITE, 0);
	int32_t g = ev_find(RHW_EV_GPREG_SET, 0);
	int32_t r = ev_find(RHW_EV_IMG_REBOOT, 0);

	zassert_true(w >= 0 && g > w && r > g, "order: block %d, gpregret1 %d, reboot %d", w, g, r);
	zassert_equal(rhw_sim_gpregret1_get(), 4u, "reason code in gpregret1");
	zassert_equal(rhw_sim_image_last_reboot(), 6, "reboot reason CRASH (6)");
	t_next_boot();
	zassert_equal(rsy_crash_take(&c, &gp), 1, "the block written by the fatal path is valid at the next boot");
	zassert_equal(c.reason, 4u);
	zassert_equal(c.pc, 0u, "no exception frame: registers 0");
	zassert_equal(gp, 4u);
	/* when the retained write fails (the chip is already gone: every call is refused) the path still ends in a reboot request
	 * and does not hang */
	t_cleanup();
	t_init();
	zassert_equal(rhw_pmic()->ship_task(), 0);
	rsy_fatal(4u, NULL);
	zassert_equal(ev_count(RHW_EV_IMG_REBOOT), 0u, "refused calls are not counted as reboots");
	zassert_true(rhw_sim_ship_refused() >= 3u, "the three calls of the path were made and refused (%u)",
		     (unsigned)rhw_sim_ship_refused());
	TC_PRINT("EVIDENCE sys_crash fatal path: block %d < gpregret1 %d < reboot %d, reboot reason %d\n", w, g, r, 6);
}
