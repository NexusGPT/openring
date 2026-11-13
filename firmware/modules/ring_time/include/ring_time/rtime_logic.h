/*
 * Ring time, pure part: the clock record and the conversion of a civil date and time.
 *
 * design/firmware.md section 9.1: wall time = uptime + a UTC offset, "set" once a source has given
 * the time. Here the record holds that offset; the caller passes the uptime in milliseconds.
 */
#ifndef RING_TIME_RTIME_LOGIC_H
#define RING_TIME_RTIME_LOGIC_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

struct rtime_rec {
	bool set;            /* "time is set": a source has given the time */
	int64_t offset_ms;   /* utc_ms = uptime_ms + offset_ms */
	int16_t tz_min;      /* minutes east of UTC (zone plus daylight saving), as the source gave it; 0 when not known */
	bool zone_known;     /* false: the source gave no zone, so the clock holds the source's local time (utc_ms is then
	                      * that local time, not UTC) */
	uint32_t updates;    /* how many times a source set the clock */
};

void rtime_rec_init(struct rtime_rec *r);

/* A source says: at uptime_ms the time was utc_ms. With zone_known the time is UTC and tz_min is the wearer's offset
 * east of UTC in minutes; without it the time is the source's local time and tz_min is stored as 0. */
void rtime_rec_set(struct rtime_rec *r, int64_t uptime_ms, int64_t utc_ms, int16_t tz_min, bool zone_known);

/* The UTC time in ms at uptime_ms; 0 when the time is not set. */
int64_t rtime_rec_utc_ms(const struct rtime_rec *r, int64_t uptime_ms);

/* Days since 1970-01-01 of a civil date (proleptic Gregorian) into *days. Returns 0, or -EINVAL for a date
 * that does not exist: month 1..12, day 1..days in the month, year 1970..9999. */
int rtime_days_from_civil(int year, int month, int day, int64_t *days);

/* Milliseconds since 1970-01-01 00:00:00 of a civil date and time read as UTC. fractions256 is
 * 0..255 (1/256 s). Returns 0 or -EINVAL. */
int rtime_civil_to_ms(int year, int month, int day, int hour, int minute, int second, int fractions256,
		      int64_t *ms);

#ifdef __cplusplus
}
#endif

#endif
