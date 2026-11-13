/*
 * rsy_logic.c: the pure part of ring_sys (software step 6, unit U7). No kernel call. Written for this project.
 * "FW l.N" = line N of design/firmware.md. Every limit comes from rrec_spec.h.
 */
#include <string.h>

#include <zephyr/sys/crc.h>

#include "rsy_logic.h"

/* ------------------------------------------------------------------ update */
bool rsl_update_allowed(uint16_t soc_x10, bool vbus)
{
	return vbus || soc_x10 > RREC_UPDATE_MIN_SOC_X10;
}

enum rrec_status rsl_begin_check(uint32_t image_size, uint16_t soc_x10, bool vbus)
{
	if (!rsl_update_allowed(soc_x10, vbus)) {
		return RREC_ST_NOT_ALLOWED;
	}
	if (image_size == 0u || image_size > RREC_IMAGE_MAX_BYTES + 1u) {
		return RREC_ST_BAD_ARG;
	}
	return RREC_ST_OK;
}

enum rrec_status rsl_data_check(bool begun, uint32_t image_size, uint32_t offset, size_t len, bool has_data)
{
	uint64_t end = (uint64_t)offset + (uint64_t)len;
	uint64_t limit = image_size < RREC_IMAGE_MAX_BYTES ? image_size : RREC_IMAGE_MAX_BYTES;

	if (!begun || (len > 0u && !has_data)) {
		return RREC_ST_BAD_ARG;
	}
	if (end > limit) {
		return RREC_ST_BAD_ARG;
	}
	return RREC_ST_OK;
}

uint32_t rsl_crc32_update(uint32_t crc, const uint8_t *data, size_t len)
{
	return crc32_ieee_update(crc, data, len);
}

/* ------------------------------------------------------------------ self-test */
uint32_t rsl_selftest_window_ms(void)
{
	return RREC_SELFTEST_MS;
}

void rsl_st_start(struct rsl_selftest *s, bool vbus)
{
	s->running = true;
	s->passed = 0;
	s->needed = (uint8_t)((1u << RSY_ITEM_STORAGE) | (1u << RSY_ITEM_BLUETOOTH));
	if (vbus) {
		s->needed |= (uint8_t)(1u << RSY_ITEM_USB);
	}
}

bool rsl_st_pass(struct rsl_selftest *s, enum rsy_item item)
{
	if (!s->running || (unsigned int)item > (unsigned int)RSY_ITEM_USB) {
		return false;
	}
	s->passed |= (uint8_t)(1u << (unsigned int)item);
	if ((s->passed & s->needed) == s->needed) {
		s->running = false;
		return true;
	}
	return false;
}

uint8_t rsl_st_expire(struct rsl_selftest *s)
{
	s->running = false;
	return s->passed;
}

/* ------------------------------------------------------------------ crash block */
static void put32(uint8_t *p, uint32_t v)
{
	p[0] = (uint8_t)v;
	p[1] = (uint8_t)(v >> 8);
	p[2] = (uint8_t)(v >> 16);
	p[3] = (uint8_t)(v >> 24);
}

static uint32_t get32(const uint8_t *p)
{
	return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

_Static_assert(RREC_CRASH_BLOCK_BYTES == 4u * 4u + RREC_CRASH_NAME_BYTES + 4u * RREC_CRASH_STACK_WORDS,
	       "crash block layout of FW l.1063");
_Static_assert(RSL_CRASH_STORED_BYTES <= RREC_RETAINED_BYTES, "the crash block fits the retained area (FW l.1063)");

size_t rsl_crash_encode(const struct rrec_crash *c, uint8_t out[RSL_CRASH_STORED_BYTES])
{
	uint8_t *b = out + RSL_CRASH_OFF_BLOCK;

	put32(out + RSL_CRASH_OFF_MAGIC, RSL_CRASH_MAGIC);
	put32(b + 0, c->reason);
	put32(b + 4, c->pc);
	put32(b + 8, c->lr);
	put32(b + 12, c->psr);
	memcpy(b + 16, c->thread, RREC_CRASH_NAME_BYTES);
	for (uint32_t i = 0; i < RREC_CRASH_STACK_WORDS; i++) {
		put32(b + 16 + RREC_CRASH_NAME_BYTES + 4u * i, c->stack[i]);
	}
	put32(out + RSL_CRASH_OFF_CRC, crc32_ieee(out, RSL_CRASH_OFF_CRC));
	return RSL_CRASH_STORED_BYTES;
}

bool rsl_crash_decode(const uint8_t in[RSL_CRASH_STORED_BYTES], struct rrec_crash *c)
{
	const uint8_t *b = in + RSL_CRASH_OFF_BLOCK;

	if (get32(in + RSL_CRASH_OFF_MAGIC) != RSL_CRASH_MAGIC) {
		return false;
	}
	if (get32(in + RSL_CRASH_OFF_CRC) != crc32_ieee(in, RSL_CRASH_OFF_CRC)) {
		return false;
	}
	c->reason = get32(b + 0);
	c->pc = get32(b + 4);
	c->lr = get32(b + 8);
	c->psr = get32(b + 12);
	memcpy(c->thread, b + 16, RREC_CRASH_NAME_BYTES);
	for (uint32_t i = 0; i < RREC_CRASH_STACK_WORDS; i++) {
		c->stack[i] = get32(b + 16 + RREC_CRASH_NAME_BYTES + 4u * i);
	}
	return true;
}

/* ------------------------------------------------------------------ watchdog */
static bool fresh(int64_t now_ms, int64_t last_ms)
{
	return last_ms != RSL_NEVER && now_ms - last_ms <= (int64_t)RREC_WDT_PROGRESS_MS;
}

bool rsl_wdt_should_feed(bool recording, int64_t now_ms, int64_t last_audio_ms, int64_t last_store_ms)
{
	if (!recording) {
		return true;
	}
	return fresh(now_ms, last_audio_ms) && fresh(now_ms, last_store_ms);
}

/* ------------------------------------------------------------------ saved time */
bool rsl_time_saveable(int64_t utc_ms)
{
	return utc_ms > 0;
}

bool rsl_time_guess(bool time_saved, int64_t saved_utc_ms, int64_t *utc_ms)
{
	if (!time_saved || utc_ms == NULL) {
		return false;
	}
	*utc_ms = saved_utc_ms;
	return true;
}
