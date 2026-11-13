/*
 * rsy_logic.h: the pure part of ring_sys (software step 6, unit U7; not a public header). No kernel call: stdint,
 * stdbool, string and the CRC library only (decision D11a). "FW l.N" = line N of design/firmware.md.
 */
#ifndef RING_SYS_RSY_LOGIC_H
#define RING_SYS_RSY_LOGIC_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <ring_rhw/rrec_spec.h>
#include <ring_sys/rsy.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ------------------------------------------------------------------ update (FW l.1012, l.1015) */
/* FW l.1015: allowed only with the battery ABOVE 30 % (soc_x10 > RREC_UPDATE_MIN_SOC_X10) or VBUS present. */
bool rsl_update_allowed(uint16_t soc_x10, bool vbus);
/* FW_BEGIN: NOT_ALLOWED (ruling D12) first, then BAD_ARG for a size of 0 or above RREC_IMAGE_MAX_BYTES (FW l.1012
 * rule 1), else OK. */
enum rrec_status rsl_begin_check(uint32_t image_size, uint16_t soc_x10, bool vbus);
/* FW_DATA: BAD_ARG without FW_BEGIN, with data NULL and len > 0, or when offset + len (computed in 64 bits) goes
 * past the declared image_size or past RREC_IMAGE_MAX_BYTES (FW l.1012 rule 1); else OK. */
enum rrec_status rsl_data_check(bool begun, uint32_t image_size, uint32_t offset, size_t len, bool has_data);
/* Running CRC-32/ISO-HDLC: start with 0, feed pieces in order; the result after the last piece is the CRC of the
 * whole (crc32_ieee_update of the library). */
uint32_t rsl_crc32_update(uint32_t crc, const uint8_t *data, size_t len);

/* ------------------------------------------------------------------ self-test (FW l.1014) */
/* The window length in ms (RREC_SELFTEST_MS). */
uint32_t rsl_selftest_window_ms(void);
struct rsl_selftest {
	bool running;
	uint8_t needed;   /* bit per enum rsy_item */
	uint8_t passed;
};
/* Start: storage and Bluetooth are always needed, USB only with VBUS (FW l.1014). */
void rsl_st_start(struct rsl_selftest *s, bool vbus);
/* One item passed; true when this call completed the needed set (the step machine then stops running). Ignored
 * (false) when not running or for an item outside the enum. */
bool rsl_st_pass(struct rsl_selftest *s, enum rsy_item item);
/* The window ended: stop running; returns the mask of items passed. */
uint8_t rsl_st_expire(struct rsl_selftest *s);

/* ------------------------------------------------------------------ crash block (FW l.1063) */
/* Stored form in retained memory: magic u32, the block of FW l.1063 (reason u32, PC u32, LR u32, PSR u32, thread name
 * 16 bytes, 64 stack words, all little-endian: RREC_CRASH_BLOCK_BYTES), CRC-32 over the 292 bytes before it. The magic
 * and the CRC are this unit's way to tell a valid block from power-up garbage (FW says "a valid crash block"). */
#define RSL_CRASH_MAGIC          0x48535243u   /* bytes "CRSH" */
#define RSL_CRASH_OFF_MAGIC      0u
#define RSL_CRASH_OFF_BLOCK      4u
#define RSL_CRASH_OFF_CRC        (RSL_CRASH_OFF_BLOCK + RREC_CRASH_BLOCK_BYTES)
#define RSL_CRASH_STORED_BYTES   (RSL_CRASH_OFF_CRC + 4u)
size_t rsl_crash_encode(const struct rrec_crash *c, uint8_t out[RSL_CRASH_STORED_BYTES]);
/* true (and *c filled) when magic and CRC are right. */
bool rsl_crash_decode(const uint8_t in[RSL_CRASH_STORED_BYTES], struct rrec_crash *c);

/* ------------------------------------------------------------------ watchdog (FW l.1065) */
#define RSL_NEVER INT64_MIN   /* "never reported" */
/* Feed when no recording runs (ruling on reading 9), or when both threads reported at most RREC_WDT_PROGRESS_MS ago. */
bool rsl_wdt_should_feed(bool recording, int64_t now_ms, int64_t last_audio_ms, int64_t last_store_ms);

/* ------------------------------------------------------------------ saved time (FW l.1005, ruling D18) */
/* A time worth saving: a set clock reads above 0 (utc_ms 0 means "not set"). */
bool rsl_time_saveable(int64_t utc_ms);
/* The guess from the loaded settings: true with *utc_ms when one was saved (nothing is written otherwise). */
bool rsl_time_guess(bool time_saved, int64_t saved_utc_ms, int64_t *utc_ms);

#ifdef __cplusplus
}
#endif

#endif
