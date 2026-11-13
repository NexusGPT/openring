/*
 * rfa_logic.h: the pure part of the factory unit (software step 6, unit U8). No kernel call: stdint, stdbool, string
 * and rrec_spec.h only. "FW l.N" = line N of design/firmware.md. Every number of the specification that more than one
 * unit uses comes from rrec_spec.h; the few numbers only this unit uses are defined below with their line.
 *
 * Request layouts (this unit's reading; FW 9.3 names the sub-commands and what each reports, not the bytes):
 *   0x01 ENTER, 0x02 EXIT, 0x20, 0x40, 0x41, 0x50, 0x60, 0x70, 0x71, 0x7E, 0x7F: the sub-command byte only.
 *   0x10 T-MIC: sub, microphone (1 or 2).
 *   0x30 T-JOY, 0x31 T-CENTRE: sub, window_ms u16 little endian (1 to RREC_FAC_RADIO_MS): how long the ring collects the
 *   joystick events for the jig.
 * Response (FW l.1020): result u8 (RREC_FAC_RESULT_*), then the values (little endian), see each rfa_put_* below.
 */
#ifndef RFA_LOGIC_H
#define RFA_LOGIC_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <ring_rhw/rrec_spec.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Numbers only this unit uses (not in rrec_spec.h; the lead may move them there). */
#define RFA_SCREEN_FRAME_MS   1000u    /* FW l.1025: "1 s each" (red, green, blue, white, black; the grid is held as long) */
#define RFA_XTAL_LIMIT_PPM_X10 500     /* FW l.1033: "within 50 ppm", in tenths of a ppm */
#define RFA_GRTC_HZ           32768u   /* FW l.1003: the 32.768 kHz crystal */
#define RFA_SOF_PER_S         1000u    /* USB start-of-frame at full speed: one per ms (FW l.669 names full speed) */
#define RFA_NAME_BYTES        9u       /* "Ring" + 4 hex digits + NUL (RREC_BEACON_NAME_LEN is 8, FW l.1057) */
#define RFA_DBFS_SILENT       INT16_MIN /* RMS of digital silence */
#define RFA_MAX_EVENTS        32u      /* joystick events kept for one T-JOY or T-CENTRE run */
#define RFA_OUT_MAX           256u     /* rfa.h: the response is at most 256 bytes */

/* The parsed request. */
struct rfa_cmd {
	uint8_t sub;          /* enum rrec_factory_sub */
	uint8_t mic;          /* T-MIC: 1 or 2 */
	uint16_t window_ms;   /* T-JOY, T-CENTRE */
};

/* The gate and the parse (FW l.1019, l.1037): an empty request BAD_ARG; flag clear NOT_ALLOWED (every sub-command);
 * then a sub-command that is unknown or removed (0x11) or with a wrong length BAD_ARG; then the state: ENTER only when
 * the core is not yet in FACTORY_TEST (it is answered in TRANSFER), every other sub-command only in FACTORY_TEST,
 * else NOT_ALLOWED. RREC_ST_OK with *cmd filled otherwise. */
enum rrec_status rfa_parse(const uint8_t *req, size_t len, bool flag, bool in_factory_test, struct rfa_cmd *cmd);

/* true when the sub-command clears the flag (SHIP_ENTER only, FW l.1019, l.1035). */
bool rfa_clears_flag(uint8_t sub);
/* true when the sub-command enters ship mode with the ship beacon (SHIP_ENTER and SHIP_SAMPLE, FW l.1034, l.1035). */
bool rfa_is_ship(uint8_t sub);

/* Response bytes: each puts the bytes at out[0..] and returns the length. */
size_t rfa_put_result(uint8_t *out, uint8_t result);
/* T-MIC (FW l.1024): result, rms_left i16, rms_right i16 (tenths of dBFS), run_left u32, run_right u32. 13 bytes. */
size_t rfa_put_mic(uint8_t *out, uint8_t result, int16_t rms_l_x10, int16_t rms_r_x10, uint32_t run_l, uint32_t run_r);
/* T-SIGN (FW l.1029): result, then on and off times of the two recordings in ms of uptime, 4 x i64. 33 bytes. */
size_t rfa_put_sign(uint8_t *out, uint8_t result, const int64_t t_ms[4]);
/* T-MOTOR (FW l.1028): result, vbat_before u16, vbat_during u16 (mV), dip i16 (mV). 7 bytes. */
size_t rfa_put_motor(uint8_t *out, uint8_t result, uint16_t before_mv, uint16_t during_mv, int16_t dip_mv);
/* T-STORE (FW l.1030): result, equal u8, write_us u32, read_us u32, deleted u32. 14 bytes. */
size_t rfa_put_store(uint8_t *out, uint8_t result, bool equal, uint32_t write_us, uint32_t read_us, uint32_t deleted);
/* T-CHARGE (FW l.1032): result, state u8, err_reason u8, current uA i32. 7 bytes. */
size_t rfa_put_charge(uint8_t *out, uint8_t result, uint8_t state, uint8_t err_reason, int32_t ua);
/* T-XTAL (FW l.1033): result, ppm_x10 i32, grtc_ticks u64, sof u32. 17 bytes. */
size_t rfa_put_xtal(uint8_t *out, uint8_t result, int32_t ppm_x10, uint64_t grtc, uint32_t sof);

/* A joystick event kept for the jig: the event (enum rfa_input) and ms since the request began. */
struct rfa_evrec {
	uint8_t ev;
	uint32_t rel_ms;
};
/* T-JOY, T-CENTRE (FW l.1026, l.1027): result, dropped u8 (events that did not fit), count u8, then count x (ev u8,
 * rel_ms u32). */
size_t rfa_put_events(uint8_t *out, uint8_t result, uint8_t dropped, const struct rfa_evrec *e, uint8_t n);
/* true when the event belongs to the sub-command (T-JOY: directions and the centre's down and up; T-CENTRE: the centre's
 * down, up, single, double, long and MW). */
bool rfa_event_wanted(uint8_t sub, uint8_t ev);

/* RMS of one channel in tenths of dBFS (0 = a full-scale square wave, so a full-scale sine is -30): a streaming sum of
 * squares. */
struct rfa_level {
	uint64_t sumsq;
	uint64_t n;
};
void rfa_level_add(struct rfa_level *l, const int16_t *frames, uint32_t n_frames, uint32_t channel);
int16_t rfa_level_dbfs_x10(const struct rfa_level *l);

/* The longest run of identical consecutive samples of one channel, across blocks. */
struct rfa_run {
	int32_t last;
	uint32_t cur;
	uint32_t max;
};
void rfa_run_add(struct rfa_run *r, const int16_t *frames, uint32_t n_frames, uint32_t channel);
/* A channel with a run of RREC_FAC_MIC_STUCK_RUN equal samples is stuck (FW l.1024). */
bool rfa_run_is_stuck(uint32_t longest_run);

/* T-XTAL arithmetic (FW l.1033): ppm x 10 of the GRTC against the start-of-frame count; *ok false when sof is 0. */
int32_t rfa_ppm_x10(uint64_t grtc_ticks, uint32_t sof, bool *ok);
bool rfa_ppm_within(int32_t ppm_x10);

/* T-CHARGE (FW l.1032, R-CHG): fail when the state is off or an error is latched; else pass. */
uint8_t rfa_charge_result(uint8_t state, uint8_t err_reason);

/* T-MOTOR (FW l.1028): how long after MOTOR goes high VBAT is read; the dip is before minus during, clamped to i16. */
uint32_t rfa_motor_read_delay_ms(void);
int16_t rfa_motor_dip_mv(uint16_t before_mv, uint16_t during_mv);

/* The ship beacon's name (FW l.1057): "Ring" and the last four hex digits (upper case) of the device id. out holds
 * RFA_NAME_BYTES bytes. Returns the length (RREC_BEACON_NAME_LEN). */
size_t rfa_beacon_name(uint64_t device_id, char out[RFA_NAME_BYTES]);

#ifdef __cplusplus
}
#endif

#endif
