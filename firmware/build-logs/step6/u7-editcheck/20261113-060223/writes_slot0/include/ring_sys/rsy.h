/*
 * rsy.h: the system part (software step 6, unit U7 builds it; U0 wrote this header, frozen: changes only through the
 * lead). Firmware update with the 30 s self-test, the persistent factory flag and saved time, crash capture, the
 * watchdog feed rule: design/firmware.md sections 9.1, 9.2, 9.3 (flag), 9.4 ("FW l.N" = line N of that file).
 *
 * Pure part (rsy_logic.c: image size and range checks, running CRC-32, the self-test step machine, the "update
 * allowed" rule, the crash block format, the feed decision, the saved-time guess) is declared in the unit's own src/
 * header. The flash layout numbers of FW 9.2 are in rrec_spec.h (RREC_FLASH_*, RREC_IMAGE_MAX_BYTES).
 * The fatal error handler (k_sys_fatal_error_handler, FW l.1063) lives in ring_sys's source; it is not called by
 * other units and has no declaration here.
 * Hardware only through rhw.h: rhw_image(), rhw_persist(), rhw_retained(), rhw_wdt(), rhw_clock().
 */
#ifndef RING_SYS_RSY_H
#define RING_SYS_RSY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <ring_rhw/rrec_spec.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Load the persistent settings (factory flag, saved time) and keep the log hook (RREC_LOG_SELFTEST, RREC_LOG_CRASH
 * are written by the caller from rsy_crash_take; the self-test writes its own record). Once, at boot, first of the
 * units. Blocks for the settings read. */
int rsy_init(rrec_log_fn log);  /* FW l.1010 */

/* ------------------------------------------------------------------ update (FW 9.2) */
/* FW_BEGIN (FW l.703, l.1012, l.1013, l.1015): NOT_ALLOWED when soc_x10 <= RREC_UPDATE_MIN_SOC_X10 and no VBUS
 * (ruling D12); BAD_ARG when image_size is 0 or above RREC_IMAGE_MAX_BYTES; else erase slot 1 and OK (FW_ERROR when
 * the erase fails). Transfer thread; blocks for the erase. */
enum rrec_status rsy_fw_begin(uint32_t image_size, uint32_t image_crc32, uint16_t soc_x10, bool vbus);
/* FW_DATA (FW l.704): BAD_ARG for an offset + len past image_size or past RREC_IMAGE_MAX_BYTES, or without FW_BEGIN;
 * FW_ERROR on a write error; OK. Writes only slot 1 (FW l.1012 rule 1). Blocks for the write. */
enum rrec_status rsy_fw_data(uint32_t offset, const uint8_t *data, size_t len);
/* FW_END (FW l.705, l.1013): CRC-32 of the image_size bytes of slot 1 against image_crc32 (FW_ERROR on a mismatch or
 * without FW_BEGIN), then boot_request_upgrade(BOOT_UPGRADE_TEST); OK. The REBOOT itself is the join's, after the OK
 * response was sent (rxf_backend.after_response). Blocks for the read-back. */
enum rrec_status rsy_fw_end(void);

/* ------------------------------------------------------------------ self-test (FW l.1014) */
enum rsy_item {
	RSY_ITEM_STORAGE = 0,       /* storage mounted */
	RSY_ITEM_BLUETOOTH = 1,     /* Bluetooth enabled */
	RSY_ITEM_USB = 2,           /* USB enumerated again (needed only when VBUS is present) */
};
/* At boot: when the running image is not confirmed (rhw_image()->is_confirmed() == 0), start the RREC_SELFTEST_MS
 * window and return 1; 0 when confirmed (nothing to do). The self-test never powers the microphones (FW l.1014).
 * Join's thread; never blocks. */
int rsy_selftest_start(bool vbus);
/* One item passed. When every needed item passed: boot_write_img_confirmed() and a RREC_LOG_SELFTEST record. Any
 * thread (not an interrupt); blocks for the confirm write. */
void rsy_selftest_pass(enum rsy_item item);  /* FW l.1014 */
/* true while a self-test window runs. Never blocks. (At the end of the window without every item, ring_sys logs and
 * reboots with RHW_REBOOT_SELFTEST_FAIL without confirming, from its own timer work.) */
bool rsy_selftest_running(void);  /* FW l.1014 */

/* ------------------------------------------------------------------ factory flag and saved time (FW l.1005, l.1019) */
bool rsy_factory_flag(void);
/* Write the flag through the settings (SHIP_ENTER clears it, FW l.1019; set only by the factory programming).
 * Blocks for the write. */
int rsy_factory_flag_set(bool on);
/* Save the time on entry into SHIP or OFF (FW l.1005). Blocks for the write. */
int rsy_time_save(int64_t utc_ms, int16_t tz_min, bool zone_known);
/* The saved time as a guess (FW l.1005, ruling D18): true with *utc_ms when one was saved. The clock stays "not set";
 * the join writes the guess once into the log (RREC_LOG_TIME_GUESS). Never blocks. */
bool rsy_time_guess(int64_t *utc_ms);

/* ------------------------------------------------------------------ crash (FW l.1063) */
/* At boot: when retained memory holds a valid crash block, copy it to *out, clear it (and gpregret1) and return 1;
 * 0 when none or not valid. Once, at boot. */
int rsy_crash_take(struct rrec_crash *out, uint8_t *gpregret1);  /* FW l.1063 */

/* ------------------------------------------------------------------ watchdog (FW l.1065) */
enum rsy_thread {
	RSY_THREAD_AUDIO = 0,
	RSY_THREAD_STORAGE = 1,
};
/* A thread made progress now. Called by ring_audio's and ring_store's threads (through a hook the join sets, so those
 * units need no ring_sys header). Any thread; never blocks. */
void rsy_progress(enum rsy_thread t);  /* FW l.1065 */
/* Start wdt31 with RREC_WDT_TIMEOUT_MS and the feed work: every RREC_WDT_FEED_MS, feed only when both threads reported
 * progress in the last RREC_WDT_PROGRESS_MS, or when no recording runs (recording = rsy_recording(true)). Once. */
int rsy_wdt_start(void);  /* FW l.1065 */
/* The audio and storage threads are expected to report only while a recording runs. Any thread; never blocks. */
void rsy_recording(bool on);  /* FW l.1065 */

#ifdef __cplusplus
}
#endif

#endif
