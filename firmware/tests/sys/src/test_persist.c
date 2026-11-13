/* Suite sys_persist (software step 6, unit U7): the persistent settings, the factory flag (FW l.1019) and the way saved
 * values keep each other. Row T11 (the ring's part) of the plan. */
#include "common.h"

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

ZTEST_SUITE(sys_persist, NULL, NULL, before, after, NULL);

/* T11, FW l.1019: the flag is written when the factory programs the ring (assembly step 5: the settings hold 1), and
 * cleared only by SHIP_ENTER; it survives reboots; a cleared flag stays cleared. */
ZTEST(sys_persist, test_factory_flag_survives_reboot)
{
	struct rhw_persist seed = { .factory_flag = 1 };
	struct rhw_persist p;

	/* before the first init the flag is clear (nothing loaded) */
	rhw_sim_reset();
	zassert_false(rsy_factory_flag(), "no flag before rsy_init");
	rhw_sim_persist_set(&seed);        /* the factory's programming */
	zassert_equal(rsy_init(t_log_fn), 0);
	zassert_true(rsy_factory_flag(), "flag 1 read from the settings");
	t_next_boot();
	zassert_true(rsy_factory_flag(), "flag still 1 after a reboot");
	t_next_boot();
	zassert_true(rsy_factory_flag(), "flag still 1 after a second reboot");
	/* SHIP_SAMPLE keeps it: the join then only saves the time */
	zassert_equal(rsy_time_save(1794513600000, 60, true), 0);
	t_next_boot();
	zassert_true(rsy_factory_flag(), "saving the time keeps the flag");
	/* SHIP_ENTER clears it */
	zassert_equal(rsy_factory_flag_set(false), 0);
	zassert_false(rsy_factory_flag(), "cleared at once");
	rhw_sim_persist_get(&p);
	zassert_equal(p.factory_flag, 0, "cleared in the settings");
	zassert_true(p.time_saved, "clearing the flag keeps the saved time");
	zassert_equal(p.saved_utc_ms, 1794513600000);
	t_next_boot();
	zassert_false(rsy_factory_flag(), "a cleared flag stays cleared after a reboot");
	int64_t g = 0;

	zassert_true(rsy_time_guess(&g), "the saved time survived the flag write");
	zassert_equal(g, 1794513600000);
	/* the flag can be set again through the settings (factory programming of a sample ring) and is kept */
	zassert_equal(rsy_factory_flag_set(true), 0);
	t_next_boot();
	zassert_true(rsy_factory_flag());
	/* a failing settings write (ship mode already entered: every call refused) is an error and the flag stays as it was */
	zassert_equal(rhw_pmic()->ship_task(), 0);
	zassert_not_equal(rsy_factory_flag_set(false), 0, "a failed write is reported");
	zassert_true(rsy_factory_flag(), "the flag is unchanged after a failed write");
	TC_PRINT("EVIDENCE sys_persist flag: 1 over 3 reboots, cleared by the write, clear over 1 reboot, write errors reported\n");
}

/* A blank settings area reads all zero: no flag, no saved time. */
ZTEST(sys_persist, test_blank_settings_read_as_clear)
{
	int64_t g = 7;

	t_init();
	zassert_false(rsy_factory_flag());
	zassert_false(rsy_time_guess(&g));
	zassert_equal(g, 7);
	zassert_equal(ev_count(RHW_EV_PERSIST_LOAD), 1u, "one settings read at init");
	zassert_equal(ev_count(RHW_EV_PERSIST_SAVE), 0u, "init writes nothing");
}
