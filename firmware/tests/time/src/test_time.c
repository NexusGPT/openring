/* ring_time logic tests (native_sim and the simulated ring chip): the clock record and civil time. */

#include <errno.h>

#include <zephyr/ztest.h>

#include <ring_time/rtime_logic.h>

ZTEST_SUITE(ring_time, NULL, NULL, NULL, NULL, NULL);

ZTEST(ring_time, test_not_set_at_start)
{
	struct rtime_rec r;

	rtime_rec_init(&r);
	zassert_false(r.set);
	zassert_equal(rtime_rec_utc_ms(&r, 123456), 0, "a clock that was never set reads 0");
	zassert_equal(r.updates, 0);
}

ZTEST(ring_time, test_set_then_follows_uptime)
{
	struct rtime_rec r;

	rtime_rec_init(&r);
	rtime_rec_set(&r, 1000, 1794434746000LL, 60, true);
	zassert_true(r.zone_known);
	zassert_true(r.set);
	zassert_equal(r.tz_min, 60);
	zassert_equal(rtime_rec_utc_ms(&r, 1000), 1794434746000LL);
	zassert_equal(rtime_rec_utc_ms(&r, 6000), 1794434751000LL, "5 s of uptime later: 5 s later");
	zassert_equal(r.updates, 1);
}

ZTEST(ring_time, test_a_second_source_value_replaces)
{
	struct rtime_rec r;

	rtime_rec_init(&r);
	rtime_rec_set(&r, 1000, 1794434746000LL, 0, true);
	rtime_rec_set(&r, 9000, 1794434746000LL + 3600000LL, 0, true); /* the iPhone's time moved an hour */
	zassert_equal(rtime_rec_utc_ms(&r, 9000), 1794434746000LL + 3600000LL);
	zassert_equal(rtime_rec_utc_ms(&r, 10000), 1794434746000LL + 3601000LL);
	zassert_equal(r.updates, 2);
}

ZTEST(ring_time, test_zone_not_known_is_kept_as_a_flag)
{
	struct rtime_rec r;

	rtime_rec_init(&r);
	zassert_false(r.zone_known, "not known before any source");
	/* a source with no zone: the time is its local time, the zone offset given is not stored */
	rtime_rec_set(&r, 1000, 1794434746000LL, 120, false);
	zassert_true(r.set);
	zassert_false(r.zone_known);
	zassert_equal(r.tz_min, 0);
	zassert_equal(rtime_rec_utc_ms(&r, 2000), 1794434747000LL);
	/* a later source with a zone: known, offset stored */
	rtime_rec_set(&r, 3000, 1794434746000LL, 120, true);
	zassert_true(r.zone_known);
	zassert_equal(r.tz_min, 120);
	/* and a later one without a zone clears the flag again */
	rtime_rec_set(&r, 4000, 1794434746000LL, 0, false);
	zassert_false(r.zone_known);
}

ZTEST(ring_time, test_civil_known_dates)
{
	int64_t ms;

	zassert_equal(rtime_civil_to_ms(1970, 1, 1, 0, 0, 0, 0, &ms), 0);
	zassert_equal(ms, 0);
	zassert_equal(rtime_civil_to_ms(2000, 2, 29, 0, 0, 0, 0, &ms), 0);
	zassert_equal(ms, 951782400000LL, "leap day of 2000");
	zassert_equal(rtime_civil_to_ms(2024, 2, 29, 0, 0, 0, 0, &ms), 0);
	zassert_equal(ms, 1709164800000LL);
	zassert_equal(rtime_civil_to_ms(2026, 11, 11, 22, 5, 46, 0, &ms), 0);
	zassert_equal(ms, 1794434746000LL);
	zassert_equal(rtime_civil_to_ms(2026, 11, 11, 22, 5, 46, 128, &ms), 0);
	zassert_equal(ms, 1794434746500LL, "128/256 s is half a second");
	zassert_equal(rtime_civil_to_ms(2038, 1, 19, 3, 14, 8, 0, &ms), 0);
	zassert_equal(ms, 2147483648000LL, "past the 32-bit second counter");
	zassert_equal(rtime_civil_to_ms(2100, 3, 1, 0, 0, 0, 0, &ms), 0);
	zassert_equal(ms, 4107542400000LL, "2100 is not a leap year");
	zassert_equal(rtime_civil_to_ms(9999, 12, 31, 23, 59, 59, 0, &ms), 0);
	zassert_equal(ms, 253402300799000LL);
}

ZTEST(ring_time, test_civil_rejects_what_does_not_exist)
{
	int64_t ms = 5;

	zassert_equal(rtime_civil_to_ms(2026, 13, 1, 0, 0, 0, 0, &ms), -EINVAL);
	zassert_equal(rtime_civil_to_ms(2026, 0, 1, 0, 0, 0, 0, &ms), -EINVAL);
	zassert_equal(rtime_civil_to_ms(2026, 4, 31, 0, 0, 0, 0, &ms), -EINVAL);
	zassert_equal(rtime_civil_to_ms(2100, 2, 29, 0, 0, 0, 0, &ms), -EINVAL);
	zassert_equal(rtime_civil_to_ms(2026, 1, 0, 0, 0, 0, 0, &ms), -EINVAL);
	zassert_equal(rtime_civil_to_ms(2026, 1, 1, 24, 0, 0, 0, &ms), -EINVAL);
	zassert_equal(rtime_civil_to_ms(2026, 1, 1, 0, 60, 0, 0, &ms), -EINVAL);
	zassert_equal(rtime_civil_to_ms(2026, 1, 1, 0, 0, 60, 0, &ms), -EINVAL);
	zassert_equal(rtime_civil_to_ms(2026, 1, 1, 0, 0, 0, 256, &ms), -EINVAL);
	zassert_equal(rtime_civil_to_ms(1969, 12, 31, 0, 0, 0, 0, &ms), -EINVAL);
	zassert_equal(rtime_civil_to_ms(10000, 1, 1, 0, 0, 0, 0, &ms), -EINVAL);
	zassert_equal(ms, 5, "nothing is written on an error");
}
