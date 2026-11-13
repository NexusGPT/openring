/*
 * rmo.h: the motor part (software step 6, unit U6 builds it; U0 wrote this header, frozen: changes only through the
 * lead). The pattern player of design/firmware.md section 3.1 ("FW l.N" = line N of that file).
 *
 * Pure part (rmo_logic.c: the pattern table, the replace rule, the Vibration filter, the edge schedule, the charge per
 * pulse) is declared in the unit's own src/ header. No soft start (lead's ruling D3: not built in step 6): one MOTOR
 * high per on segment, no PWM (FW l.314). Pattern ids: enum rrec_pattern of rrec_spec.h.
 * Hardware only through rhw.h: rhw_motor(), rhw_clock().
 */
#ifndef RING_MOTOR_RMO_H
#define RING_MOTOR_RMO_H

#include <stdbool.h>
#include <stdint.h>

#include <ring_rhw/rrec_spec.h>

#ifdef __cplusplus
extern "C" {
#endif

struct rmo_cb {
	/* Each MOTOR edge as the pin is set, with rhw_clock()->cycles() of that moment (FW l.496, for ring_audio's
	 * rau_motor_edge). k_timer context: must not block. */
	void (*edge)(bool high, uint64_t cycles);
	/* The charge of one ON pulse in µA·s: t_on x RREC_MOTOR_RUN_MA + RREC_MOTOR_START_MS x RREC_MOTOR_START_MA
	 * (FW l.332), at the pulse's end (for rpw_motor_charge). k_timer context: must not block. */
	void (*charge)(uint32_t uas);
	/* A pattern started (FW l.333: the start time is logged), with its id and uptime ms. Caller's context of rmo_play:
	 * must not block. */
	void (*started)(uint8_t pattern, int64_t t_ms);
};

/* Set the callbacks (any may be NULL) and the pin low. Once, at boot. */
int rmo_init(const struct rmo_cb *cb);  /* FW l.314 */

/* Play a pattern (FW l.318): it replaces the one playing, except that M1, M2, M3 and MF are never cut by MH or MT.
 * Returns 0 when it plays, -EBUSY when refused by that rule, -ECANCELED when the setting "Vibration" is off and the
 * pattern is MH or MT (FW l.301: the setting never mutes M1, M2, M3, MF, MW), -EINVAL for an unknown id.
 * Any thread (not an interrupt); never blocks: the k_timer plays it. */
int rmo_play(enum rrec_pattern p);

/* The setting "Vibration" (FW 2.2). Any thread; never blocks. */
void rmo_set_vibration(bool on);  /* FW l.301 */

/* true while a pattern plays. Never blocks. */
bool rmo_playing(void);  /* FW l.318 */

/* Stop at once, pin low (before ship mode). Any thread; never blocks. */
void rmo_stop(void);  /* FW l.937 */

#ifdef __cplusplus
}
#endif

#endif
