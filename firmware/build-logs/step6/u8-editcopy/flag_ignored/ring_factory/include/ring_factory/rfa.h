/*
 * rfa.h: the factory part (software step 6, unit U8 builds it; U0 wrote this header, frozen: changes only through the
 * lead). The FACTORY sub-commands of design/firmware.md section 9.3 and the ship beacon of ruling R20 ("FW l.N" =
 * line N of that file).
 *
 * Pure part (rfa_logic.c: sub-command parsing, the flag rules, the result layout, RMS in dBFS and the longest run of
 * equal samples, ppm, the T-CHARGE judgement, the T-MOTOR timing, the beacon name) is declared in the unit's own src/
 * header. Sub-command numbers: enum rrec_factory_sub of rrec_spec.h; results RREC_FAC_RESULT_*.
 * No factory command starts or stops a recording (FW l.209); test recordings (type 2) go through the join's
 * rec_mics_on() only (ruling R18), through struct rfa_ops below.
 * Hardware only through rhw.h: rhw_beacon(), rhw_clock(); the rest through the other units.
 */
#ifndef RING_FACTORY_RFA_H
#define RING_FACTORY_RFA_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <ring_rhw/rrec_spec.h>

#ifdef __cplusplus
extern "C" {
#endif

/* What the join must do after a sub-command answered (the core's events of FW l.181, l.201 to l.203). */
enum rfa_effect {
	RFA_EFFECT_NONE = 0,
	RFA_EFFECT_ENTER,          /* RC_EV_FACTORY_ENTER (FW l.181) */
	RFA_EFFECT_EXIT,           /* RC_EV_FACTORY_EXIT: reboot (FW l.201) */
	RFA_EFFECT_SHIP_ENTER,     /* RC_EV_SHIP_ENTER: flag cleared, beacon running (FW l.202, l.1035) */
	RFA_EFFECT_SHIP_SAMPLE,    /* RC_EV_SHIP_SAMPLE: flag kept, beacon running (FW l.203, l.1034) */
};

/* Joystick events reported to the jig in FACTORY_TEST (T-JOY, T-CENTRE, FW l.1026, l.1027). */
enum rfa_input {
	RFA_IN_UP = 1,
	RFA_IN_DOWN,
	RFA_IN_LEFT,
	RFA_IN_RIGHT,
	RFA_IN_CENTRE_DOWN,
	RFA_IN_CENTRE_UP,
	RFA_IN_SINGLE,
	RFA_IN_DOUBLE,
	RFA_IN_LONG,
	RFA_IN_MW,                 /* the warning pulse at 500 ms of a hold */
};

/* What the factory tests need from the other units; the join fills it (a test fills stand-ins). Each may block;
 * called on the transfer thread. */
struct rfa_ops {
	/* A test recording of type 2 for ms milliseconds through the normal path (rec_mics_on after the sign, FW l.1053);
	 * each kept block of interleaved samples is passed to on_block (frames = 256 per block); *mic_on_ms and
	 * *mic_off_ms receive the VDD_MIC on and off times (T-SIGN, FW l.1029). 0; -ENODEV when the screen refused the
	 * sign (no screen, no test, R18); another errno. */
	int (*test_recording)(uint32_t ms, void (*on_block)(const int16_t *frames, uint32_t n),
			      int64_t *mic_on_ms, int64_t *mic_off_ms);
	/* T-SCREEN frames (decision D7, unit U9): colour 0 red, 1 green, 2 blue, 3 white, 4 black, 5 grid. 0 or errno. */
	int (*screen_frame)(uint8_t which);  /* FW l.1025 */
	/* T-MOTOR: MOTOR on for ms (the motor part, rmo). 0 or errno. */
	int (*motor_on)(uint32_t ms);  /* FW l.1028 */
	/* VBAT now in mV (the power chip's ADC through ring_power). 0 or errno. */
	int (*vbat_mv)(uint16_t *mv);  /* FW l.1028 */
	/* T-STORE: mount, area test, delete type-2 recordings (ring_store). */
	int (*store_test)(bool *equal, uint32_t *write_us, uint32_t *read_us, uint32_t *deleted);  /* FW l.1030 */
	/* T-CHARGE: state (enum rrec_charge_state), latched error reason, battery current µA. */
	int (*charge)(uint8_t *state, uint8_t *err_reason, int32_t *ua);  /* FW l.1032 */
	/* T-XTAL: GRTC ticks and USB start-of-frame count over RREC_FAC_XTAL_MS. -ENOTSUP where no start-of-frame count
	 * exists (the simulation). */
	int (*xtal_counts)(uint64_t *grtc, uint32_t *sof);  /* FW l.1033 */
	/* The factory flag (ring_sys). */
	bool (*flag)(void);  /* FW l.1019 */
	int (*flag_set)(bool on);  /* FW l.1019 */
};

/* Keep the ops (copied). Once, at boot. */
int rfa_init(const struct rfa_ops *ops);  /* FW l.1019 */

/* One FACTORY request (FW l.708): req[0] = sub-command, then its arguments. Writes the response payload (result u8
 * then the values, FW l.1020) to out (at most 256 bytes), *out_len, and *effect. Returns the status: NOT_ALLOWED when
 * the flag is clear (FW l.1019), BAD_ARG for 0x11 (FW l.1037) and unknown sub-commands, OK otherwise.
 * in_factory_test: the core is in FACTORY_TEST (every sub-command other than ENTER needs it; ENTER needs TRANSFER).
 * Transfer thread; blocks for the test's time (at most RREC_FAC_RADIO_MS). */
enum rrec_status rfa_request(const uint8_t *req, size_t len, bool in_factory_test, uint8_t *out, size_t *out_len,
			     enum rfa_effect *effect);

/* A joystick event while the core is in FACTORY_TEST (T-JOY, T-CENTRE): kept for the sub-command that runs. The join
 * calls it instead of nothing; it never reaches a recording. Any thread (not an interrupt); never blocks. */
void rfa_input(enum rfa_input ev, int64_t t_ms);  /* FW l.1026, l.1027 */

/* SHIP_ENTER / SHIP_SAMPLE accepted (ruling R20, FW l.1057): start the beacon ("Ring" + the last 4 hex digits of the
 * device id, not connectable, RREC_ADV_INTERVAL_MS, RREC_ADV_TX_DBM). Called by rfa_request itself; public for the
 * join's tests. */
int rfa_ship_begin(void);
/* Stop the beacon: given to rpw_ship() as before_task, right before TASKENTERSHIPMODE (FW l.1057). */
void rfa_beacon_stop(void);

#ifdef __cplusplus
}
#endif

#endif
