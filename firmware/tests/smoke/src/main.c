/*
 * Smoke test of the build workspace. Each assertion can fail.
 */

#include <zephyr/ztest.h>
#include <zephyr/kernel.h>

ZTEST(ring_smoke, test_arithmetic)
{
	volatile int a = 2;

	zassert_equal(a + 2, 4, "2 + 2 must be 4");
}

ZTEST(ring_smoke, test_kernel_time_moves)
{
	int64_t t0 = k_uptime_get();

	k_sleep(K_MSEC(20));
	zassert_true(k_uptime_get() - t0 >= 20, "uptime must move by 20 ms");
}

ZTEST_SUITE(ring_smoke, NULL, NULL, NULL, NULL, NULL);
