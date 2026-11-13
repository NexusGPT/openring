/* Ring time, pure part: see rtime_logic.h. */

#include <errno.h>

#include <ring_time/rtime_logic.h>

void rtime_rec_init(struct rtime_rec *r)
{
	r->set = false;
	r->offset_ms = 0;
	r->tz_min = 0;
	r->zone_known = false;
	r->updates = 0;
}

void rtime_rec_set(struct rtime_rec *r, int64_t uptime_ms, int64_t utc_ms, int16_t tz_min, bool zone_known)
{
	r->offset_ms = utc_ms - uptime_ms;
	r->zone_known = zone_known;
	r->tz_min = zone_known ? tz_min : 0;
	r->set = true;
	r->updates++;
}

int64_t rtime_rec_utc_ms(const struct rtime_rec *r, int64_t uptime_ms)
{
	return r->set ? uptime_ms + r->offset_ms : 0;
}

static bool is_leap(int y)
{
	return (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;
}

static int month_days(int y, int m)
{
	static const int d[12] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };

	return (m == 2 && is_leap(y)) ? 29 : d[m - 1];
}

int rtime_days_from_civil(int year, int month, int day, int64_t *days)
{
	int64_t y, era, yoe, doy, doe;

	if (year < 1970 || year > 9999 || month < 1 || month > 12 || day < 1 || day > month_days(year, month)) {
		return -EINVAL;
	}
	/* Howard Hinnant's days_from_civil */
	y = year - (month <= 2 ? 1 : 0);
	era = (y >= 0 ? y : y - 399) / 400;
	yoe = y - era * 400;
	doy = (153 * (month + (month > 2 ? -3 : 9)) + 2) / 5 + day - 1;
	doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
	*days = era * 146097 + doe - 719468;
	return 0;
}

int rtime_civil_to_ms(int year, int month, int day, int hour, int minute, int second, int fractions256,
		      int64_t *ms)
{
	int64_t days;

	if (hour < 0 || hour > 23 || minute < 0 || minute > 59 || second < 0 || second > 59 || fractions256 < 0 ||
	    fractions256 > 255 || rtime_days_from_civil(year, month, day, &days) != 0) {
		return -EINVAL;
	}
	*ms = ((days * 24 + hour) * 60 + minute) * 60 * 1000LL + second * 1000LL + (fractions256 * 1000) / 256;
	return 0;
}
