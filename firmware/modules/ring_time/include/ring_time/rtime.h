/*
 * Ring time: the ring's clock. UTC in milliseconds, a "time is set" flag and a "zone known" flag.
 * Sources call rtime_set(); the iPhone part sets it from the Current Time Service.
 * Thread safe.
 */
#ifndef RING_TIME_RTIME_H
#define RING_TIME_RTIME_H

#include <stdbool.h>
#include <stdint.h>

#include "rtime_logic.h"

#ifdef __cplusplus
extern "C" {
#endif

/* The source gives the time now. zone_known: utc_ms is UTC and tz_min is the wearer's offset in minutes east of UTC.
 * Not zone_known: the source gave no zone; utc_ms is then the source's local time and rtime_zone_known() says so. */
void rtime_set(int64_t utc_ms, int16_t tz_min, bool zone_known);
/* false until a source gave a zone (also false before the clock is set) */
bool rtime_zone_known(void);
/* As rtime_set, for a time that was true at the given uptime (k_uptime_get() units) rather than now. */
void rtime_set_at(int64_t uptime_ms, int64_t utc_ms, int16_t tz_min, bool zone_known);
/* Replaces the whole record (used by the iPhone part, which keeps its own pure clock state). */
void rtime_set_rec(const struct rtime_rec *rec);
bool rtime_is_set(void);
/* UTC ms now; 0 when not set */
int64_t rtime_utc_ms(void);
int16_t rtime_tz_min(void);
uint32_t rtime_updates(void);

#ifdef __cplusplus
}
#endif

#endif
