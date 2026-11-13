/* Suite sys_time (software step 6, unit U7): the saved time (FW l.1005, ruling D18). Row T4 of the plan.
 * The time is saved on entry into SHIP and OFF (the join calls rsy_time_save); after the next boot it is a guess that the
 * join writes once into the event log and that is used nowhere else: the ring's clock stays "not set" (utc_ms 0, chunk
 * flag bit 5, "--:--") until SET_TIME. */
#include "common.h"

#include <ring_time/rtime.h>

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

ZTEST_SUITE(sys_time, NULL, NULL, before, after, NULL);

/* T4: entry into SHIP saves the time, and so does entry into OFF; the next boot finds the last one saved. */
ZTEST(sys_time, test_saved_on_ship_and_off)
{
	int64_t g = -1;
	struct rhw_persist p;

	t_init();
	zassert_false(rsy_time_guess(&g), "nothing saved yet: no guess");
	zassert_equal(g, -1, "no guess leaves *utc_ms alone");
	/* entry into SHIP: 2026-11-13 08:00:00 UTC (1,794,513,600,000 ms), zone +60 min, zone known */
	zassert_equal(rsy_time_save(1794513600000, 60, true), 0);
	rhw_sim_persist_get(&p);
	zassert_true(p.time_saved);
	zassert_equal(p.saved_utc_ms, 1794513600000);
	zassert_equal(p.saved_tz_min, 60);
	zassert_true(p.saved_zone_known);
	zassert_equal(ev_count(RHW_EV_PERSIST_SAVE), 1u, "one settings write for the save");
	t_next_boot();
	zassert_true(rsy_time_guess(&g), "after the next boot the saved time is there as a guess");
	zassert_equal(g, 1794513600000);
	/* entry into OFF later: the newer time replaces it; zone unknown this time */
	zassert_equal(rsy_time_save(1794600000123, -330, false), 0);
	t_next_boot();
	zassert_true(rsy_time_guess(&g));
	zassert_equal(g, 1794600000123, "the last time saved wins");
	rhw_sim_persist_get(&p);
	zassert_equal(p.saved_tz_min, -330);
	zassert_false(p.saved_zone_known);
	/* a clock that is not set (utc_ms 0) has no time to save: an older saved time is cleared, not kept as a wrong guess */
	zassert_equal(rsy_time_save(0, 0, false), 0);
	t_next_boot();
	zassert_false(rsy_time_guess(&g), "a not-set clock saves no time");
	/* and with nothing saved before, saving a not-set clock writes nothing */
	uint32_t w = ev_count(RHW_EV_PERSIST_SAVE);

	zassert_equal(rsy_time_save(0, 0, false), 0);
	zassert_equal(ev_count(RHW_EV_PERSIST_SAVE), w, "nothing to clear, nothing written");
	/* a settings write that fails (the chip is already in ship mode: every call is refused) is reported */
	zassert_equal(rsy_time_save(1794600000123, 0, true), 0);
	zassert_equal(rhw_pmic()->ship_task(), 0);
	zassert_true(rhw_sim_shipped());
	zassert_not_equal(rsy_time_save(1794600009999, 0, true), 0, "a failed settings write is an error");
	TC_PRINT("EVIDENCE sys_time saved: saved at SHIP and at OFF, the later one found after the reboot (%lld), settings writes %u\n",
		 (long long)1794600000123, (unsigned)ev_count(RHW_EV_PERSIST_SAVE));
}

/* T4, ruling D18: the guess is not the time. After a boot with a saved time the clock is still not set, reads utc_ms 0, and
 * nothing in this unit changed it. (A copy that marks the guess as set calls rtime_set and fails here.) */
ZTEST(sys_time, test_guess_is_not_set)
{
	int64_t g = 0;
	uint32_t upd0 = rtime_updates();

	t_init();
	zassert_equal(rsy_time_save(1794513600000, 60, true), 0);
	t_next_boot();
	zassert_true(rsy_time_guess(&g));
	zassert_equal(g, 1794513600000, "the guess itself is available for the log");
	zassert_false(rtime_is_set(), "the clock is not set by a guess");
	zassert_equal(rtime_utc_ms(), 0, "utc_ms reads 0 (not set)");
	zassert_false(rtime_zone_known(), "no zone is known from a guess");
	zassert_equal(rtime_updates(), upd0, "nothing was written to the clock");
	/* asking again gives the same guess and still does not set anything */
	int64_t g2 = 0;

	zassert_true(rsy_time_guess(&g2));
	zassert_equal(g2, g);
	zassert_false(rtime_is_set());
	zassert_equal(rtime_utc_ms(), 0);
	TC_PRINT("EVIDENCE sys_time guess: guess %lld, rtime_is_set %d, rtime_utc_ms %lld, clock updates %u -> %u\n",
		 (long long)g, (int)rtime_is_set(), (long long)rtime_utc_ms(), (unsigned)upd0, (unsigned)rtime_updates());
}
