/* Ring time: the kernel wrapper, see rtime.h. */

#include <zephyr/kernel.h>

#include <ring_time/rtime.h>

static struct rtime_rec rec;
static K_MUTEX_DEFINE(lk);

void rtime_set(int64_t utc_ms, int16_t tz_min, bool zone_known)
{
	k_mutex_lock(&lk, K_FOREVER);
	rtime_rec_set(&rec, k_uptime_get(), utc_ms, tz_min, zone_known);
	k_mutex_unlock(&lk);
}

void rtime_set_at(int64_t uptime_ms, int64_t utc_ms, int16_t tz_min, bool zone_known)
{
	k_mutex_lock(&lk, K_FOREVER);
	rtime_rec_set(&rec, uptime_ms, utc_ms, tz_min, zone_known);
	k_mutex_unlock(&lk);
}

void rtime_set_rec(const struct rtime_rec *r)
{
	k_mutex_lock(&lk, K_FOREVER);
	uint32_t n = rec.updates + 1;

	rec = *r;
	rec.updates = n;
	k_mutex_unlock(&lk);
}

bool rtime_zone_known(void)
{
	bool z;

	k_mutex_lock(&lk, K_FOREVER);
	z = rec.set && rec.zone_known;
	k_mutex_unlock(&lk);
	return z;
}

bool rtime_is_set(void)
{
	bool s;

	k_mutex_lock(&lk, K_FOREVER);
	s = rec.set;
	k_mutex_unlock(&lk);
	return s;
}

int64_t rtime_utc_ms(void)
{
	int64_t t;

	k_mutex_lock(&lk, K_FOREVER);
	t = rtime_rec_utc_ms(&rec, k_uptime_get());
	k_mutex_unlock(&lk);
	return t;
}

int16_t rtime_tz_min(void)
{
	int16_t z;

	k_mutex_lock(&lk, K_FOREVER);
	z = rec.tz_min;
	k_mutex_unlock(&lk);
	return z;
}

uint32_t rtime_updates(void)
{
	uint32_t u;

	k_mutex_lock(&lk, K_FOREVER);
	u = rec.updates;
	k_mutex_unlock(&lk);
	return u;
}
