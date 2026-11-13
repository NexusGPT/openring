/*
 * rxf.h: the USB transfer part (software step 6, unit U4 builds it; U0 wrote this header, frozen: changes only through
 * the lead). The vendor class and the protocol of design/firmware.md section 6 ("FW l.N" = line N of that file).
 *
 * Pure part (rxf_proto.c: header, CRC, status codes, opcode table, argument limits, response layouts, BUSY;
 * rxf_desc.c: the full-speed and high-speed descriptor tables) is declared in the unit's own src/ header. This header is
 * the thin part (rxf_class.c) and the backend the join fills. Numbers only from rrec_spec.h (RREC_OP_*, RREC_ST_*,
 * RREC_MSG_*, RREC_USB_*). Hardware only through rhw_usb() (and rhw_hfxo() if the class needs the crystal).
 *
 * The class enables the stack on RHW_USB_VBUS_READY and disables it on RHW_USB_VBUS_REMOVED (FW l.978); it answers
 * only while backend->may_answer() is true (FW l.673: CHARGING, TRANSFER, FACTORY_TEST). Requests are handled one at a
 * time on the transfer thread; a request that arrives while one runs gets BUSY (FW l.711).
 *
 * FACT FOR U4 (FW l.686 with l.698): the header's crc32 covers the whole payload and comes before it, so a READ_RANGE
 * response (up to 256 x 33,280 bytes) needs the CRC of every chunk before the first byte is sent: read the chunks
 * twice (once for the CRC, once to send) or keep them; the backend's read_chunk may be called twice per chunk.
 */
#ifndef RING_XFER_RXF_H
#define RING_XFER_RXF_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <ring_rhw/rrec_spec.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Filled by the join (ring_recorder). Each function runs on the transfer thread, may block, and returns the status of
 * the response (enum rrec_status); the protocol checks the argument limits of FW 6.3 BEFORE it calls (BAD_ARG), so a
 * backend sees only valid ranges. `out` buffers have the size named; *len is set to the payload length. */
struct rxf_backend {
	/* CHARGING, TRANSFER or FACTORY_TEST now (FW l.673). Any thread; never blocks. */
	bool (*may_answer)(void);
	/* GET_INFO (FW l.696): RREC_GET_INFO_BYTES bytes in the stated order. */
	enum rrec_status (*get_info)(uint8_t out[RREC_GET_INFO_BYTES]);
	/* LIST_RECORDINGS (FW l.697): count u16 then count x RREC_LIST_ENTRY_BYTES; out holds 2 + 64 x 64 bytes. */
	enum rrec_status (*list)(uint32_t first, uint16_t max, uint8_t *out, size_t *len);
	/* READ_RANGE (FW l.698): check that chunks first .. first + count - 1 of the recording exist (NOT_FOUND
	 * otherwise, also for a deleted recording, FW l.661) before any byte is sent. */
	enum rrec_status (*range_check)(uint32_t recording_id, uint32_t first, uint32_t count);
	/* One chunk exactly as stored (RREC_CHUNK_BYTES bytes). */
	enum rrec_status (*read_chunk)(uint32_t recording_id, uint32_t chunk, uint8_t *out);  /* FW l.698 */
	/* CONFIRM (FW l.699): OK or DIGEST_MISMATCH, NOT_FOUND. */
	enum rrec_status (*confirm)(uint32_t recording_id, uint32_t digest);
	/* DELETE (FW l.700): OK with *free_after, NOT_CONFIRMED, NOT_FOUND. */
	enum rrec_status (*del)(uint32_t recording_id, uint32_t *free_after);
	/* SET_TIME (FW l.701): the clock set with the zone known (rtime_set(utc_ms, tz_min, true)). */
	enum rrec_status (*set_time)(int64_t utc_ms, int16_t tz_min);
	/* GET_BATTERY (FW l.702): RREC_GET_BATTERY_BYTES bytes. */
	enum rrec_status (*get_battery)(uint8_t out[RREC_GET_BATTERY_BYTES]);
	/* FW_BEGIN, FW_DATA, FW_END (FW l.703 to l.705, 9.2): the protocol checks 1 to 4,096 data bytes; the size and range
	 * limits of FW l.1012 are ring_sys's (BAD_ARG), the "allowed" rule of FW l.1015 too (NOT_ALLOWED, ruling D12). */
	enum rrec_status (*fw_begin)(uint32_t image_size, uint32_t image_crc32);
	enum rrec_status (*fw_data)(uint32_t offset, const uint8_t *data, size_t len);  /* FW l.704 */
	enum rrec_status (*fw_end)(void);  /* FW l.705 */
	/* GET_LOG (FW l.706): count u16 then count x 512 bytes; out holds 2 + 32 x 512 bytes. */
	enum rrec_status (*get_log)(uint32_t first, uint16_t max, uint8_t *out, size_t *len);
	/* FACTORY (FW l.708, 9.3): sub-command and arguments; out holds the result (at most 256 bytes). NOT_ALLOWED when
	 * the factory flag is clear (checked by the backend). */
	enum rrec_status (*factory)(const uint8_t *req, size_t len, uint8_t *out, size_t *out_len);
	/* Called AFTER the response of every request was handed to the transport (FW l.705 "reboots after sending OK",
	 * l.707 REBOOT): the join reboots here for FW_END OK and REBOOT OK, and logs the command (FW l.1062). */
	void (*after_response)(uint8_t opcode, enum rrec_status st, uint32_t tag, uint32_t req_len);
};

struct rxf_cb {
	/* USBD_MSG_CONFIGURATION (FW l.171, l.673): CHARGING -> TRANSFER. Transfer thread; must not block. */
	void (*configured)(void);
	/* unconfigured or suspended (FW l.178). Transfer thread; must not block. */
	void (*unconfigured)(void);
};

/* Start the class with its backend: register the transport callbacks, the transfer thread. The stack itself starts
 * only on VBUS (FW l.978). Once, at boot. */
int rxf_start(const struct rxf_backend *be, const struct rxf_cb *cb);

/* VBUS removed in TRANSFER (FW l.179): abort the command that runs; no response is sent for it. Any thread; does not
 * wait. */
void rxf_abort(void);

/* Unconfigured in TRANSFER (FW l.178): wait until the command that runs has finished and its response was handed to
 * the transport. 0; -ETIMEDOUT after timeout_ms. Join's thread; blocks up to timeout_ms. */
int rxf_finish(int32_t timeout_ms);

/* true while a command runs (the store must not be used by another part then, FW l.219). Never blocks. */
bool rxf_busy(void);

#ifdef __cplusplus
}
#endif

#endif
