/* Suite sys_wdt (software step 6, unit U7): the watchdog feed rule (FW l.1065, plan row C23/T29) on the simulated
 * watchdog: 8 s timeout, fed every 1 s, only when the audio and storage threads reported progress in the last 2 s, or when
 * no recording runs (ruling on the root unit's reading 9). The watchdog reset itself is not provable without hardware. */
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

ZTEST_SUITE(sys_wdt, NULL, NULL, before, after, NULL);

/* both threads report every 500 ms for `ms` ms */
static void both_report(uint32_t ms)
{
	for (uint32_t t = 0; t < ms; t += 500u) {
		rsy_progress(RSY_THREAD_AUDIO);
		rsy_progress(RSY_THREAD_STORAGE);
		k_sleep(K_MSEC(500));
	}
}

/* C23/T29: during a recording the feed needs progress of BOTH threads. The storage thread stalls: feeding stops, and the
 * simulated watchdog reports that it would have reset. */
ZTEST(sys_wdt, test_feed_only_with_progress)
{
	t_init();
	zassert_equal(rsy_wdt_start(), 0);
	zassert_true(rhw_sim_wdt_started());
	rsy_recording(true);
	both_report(10000u);
	uint32_t f_ok = rhw_sim_wdt_feeds();

	zassert_true(f_ok >= 8u && f_ok <= 10u, "10 s of progress by both: %u feeds (about 1 per second)", (unsigned)f_ok);
	zassert_false(rhw_sim_wdt_would_reset(), "no reset while both report");

	/* only the audio thread goes on: the storage thread has stopped */
	for (int i = 0; i < 24; i++) {
		rsy_progress(RSY_THREAD_AUDIO);
		k_sleep(K_MSEC(500));
	}
	uint32_t f_stall = rhw_sim_wdt_feeds();

	zassert_true(f_stall <= f_ok + 2u, "at most the two ticks inside the 2 s window still feed: %u after %u",
		     (unsigned)f_stall, (unsigned)f_ok);
	zassert_true(rhw_sim_wdt_would_reset(), "12 s without a feed: the watchdog would have reset");

	/* and the other way round: audio stops, storage goes on */
	t_cleanup();
	t_init();
	zassert_equal(rsy_wdt_start(), 0);
	rsy_recording(true);
	both_report(4000u);
	uint32_t g0 = rhw_sim_wdt_feeds();

	for (int i = 0; i < 24; i++) {
		rsy_progress(RSY_THREAD_STORAGE);
		k_sleep(K_MSEC(500));
	}
	zassert_true(rhw_sim_wdt_feeds() <= g0 + 2u, "audio stalled: feeding stops (%u after %u)",
		     (unsigned)rhw_sim_wdt_feeds(), (unsigned)g0);
	zassert_true(rhw_sim_wdt_would_reset());
	TC_PRINT("EVIDENCE sys_wdt: feeds with progress %u in 10 s; feeds after a 12 s stall of one thread %u; would_reset %d\n",
		 (unsigned)f_ok, (unsigned)f_stall, (int)true);
}

/* Start values: the watchdog is started with 8,000 ms, once; a second start is refused; a start the driver refuses is
 * reported. */
ZTEST(sys_wdt, test_start_8s_once)
{
	struct rhw_sim_ev e;

	t_init();
	zassert_false(rhw_sim_wdt_started());
	zassert_equal(rsy_wdt_start(), 0);
	zassert_true(ev_get(ev_find(RHW_EV_WDT_START, 0), &e));
	zassert_equal(e.a0, 8000, "timeout 8 s (FW l.1065)");
	zassert_equal(rsy_wdt_start(), -EALREADY, "started once");
	zassert_equal(ev_count(RHW_EV_WDT_START), 1u);
	t_cleanup();
	t_init();
	zassert_equal(rhw_pmic()->ship_task(), 0);
	zassert_not_equal(rsy_wdt_start(), 0, "a refused driver start is an error");
	zassert_equal(ev_count(RHW_EV_WDT_FEED), 0u);
}

/* No recording runs: the threads do not report, and the watchdog is fed every second all the same. Feeds come 1 s apart. */
ZTEST(sys_wdt, test_feed_when_no_recording)
{
	t_init();
	zassert_equal(rsy_wdt_start(), 0);
	k_sleep(K_MSEC(30500));
	uint32_t f = rhw_sim_wdt_feeds();

	zassert_equal(f, 30u, "30 feeds in 30.5 s");
	zassert_false(rhw_sim_wdt_would_reset());
	struct rhw_sim_ev a, b;
	int32_t i0 = ev_find(RHW_EV_WDT_FEED, 0);

	zassert_true(ev_get(i0, &a));
	for (int k = 1; k < 30; k++) {
		int32_t i1 = ev_find(RHW_EV_WDT_FEED, (uint32_t)i0 + 1u);

		zassert_true(ev_get(i1, &b));
		zassert_true(b.t_us - a.t_us >= 999000 && b.t_us - a.t_us <= 1001000, "feed %d came %lld us after the one before", k,
			     b.t_us - a.t_us);
		a = b;
		i0 = i1;
	}
	/* a recording that ends resumes feeding at once: stall during a recording, then stop it */
	rsy_recording(true);
	k_sleep(K_MSEC(6000));
	uint32_t f_stalled = rhw_sim_wdt_feeds();

	rsy_recording(false);
	k_sleep(K_MSEC(2000));
	zassert_true(rhw_sim_wdt_feeds() >= f_stalled + 1u, "feeding resumes when the recording ends");
	TC_PRINT("EVIDENCE sys_wdt no recording: %u feeds in 30.5 s with no progress reports, spacing 1 s\n", (unsigned)f);
}

/* FW l.1065 "in the last 2 s" at the edge, on the pure rule: 2,000 ms ago counts, 2,001 ms does not; never reported does
 * not; no recording needs no progress. */
ZTEST(sys_wdt, test_progress_window_edges)
{
	const int64_t now = 100000;

	zassert_true(rsl_wdt_should_feed(true, now, now - 2000, now - 2000), "2,000 ms: counts");
	zassert_false(rsl_wdt_should_feed(true, now, now - 2001, now - 2000), "audio 2,001 ms ago");
	zassert_false(rsl_wdt_should_feed(true, now, now - 2000, now - 2001), "storage 2,001 ms ago");
	zassert_true(rsl_wdt_should_feed(true, now, now, now));
	zassert_false(rsl_wdt_should_feed(true, now, RSL_NEVER, now), "audio never reported");
	zassert_false(rsl_wdt_should_feed(true, now, now, RSL_NEVER), "storage never reported");
	zassert_true(rsl_wdt_should_feed(false, now, RSL_NEVER, RSL_NEVER), "no recording: fed without progress");
	zassert_equal(RREC_WDT_TIMEOUT_MS, 8000u);
	zassert_equal(RREC_WDT_FEED_MS, 1000u);
	zassert_equal(RREC_WDT_PROGRESS_MS, 2000u);
}

/* A new recording does not inherit the progress of the one before: reports count only when made during this recording. */
ZTEST(sys_wdt, test_new_recording_clears_old_progress)
{
	t_init();
	zassert_equal(rsy_wdt_start(), 0);
	rsy_recording(true);
	both_report(2000u);
	rsy_recording(false);
	rsy_recording(true);                 /* the next recording starts at once; both reports above are stale for it */
	uint32_t f0 = rhw_sim_wdt_feeds();

	k_sleep(K_MSEC(1500));               /* one tick inside the 2 s of the old reports */
	zassert_equal(rhw_sim_wdt_feeds(), f0, "old progress does not feed a new recording");
	rsy_progress(RSY_THREAD_AUDIO);
	rsy_progress(RSY_THREAD_STORAGE);
	k_sleep(K_MSEC(1000));
	zassert_true(rhw_sim_wdt_feeds() > f0, "reports of this recording feed");
}
