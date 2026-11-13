/*
 * rmo_logic.h: the pure part of the motor unit (software step 6, unit U6): no kernel call. Not a public header.
 * Design: design/firmware.md section 3.1 ("FW l.N" = line N of that file).
 */
#ifndef RING_MOTOR_RMO_LOGIC_H
#define RING_MOTOR_RMO_LOGIC_H

#include <stdbool.h>
#include <stdint.h>

#include <ring_rhw/rrec_spec.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RML_MAX_SEGS 5u   /* the longest pattern, M3: on, off, on, off, on (FW l.322) */

/* A pattern is a list of segments that alternate on, off, on ... and starts with an on segment (FW l.320 to l.328). */
struct rml_pattern {
	uint8_t n;                    /* segments */
	uint16_t ms[RML_MAX_SEGS];    /* segment 0, 2, 4 on; 1, 3 off */
};

/* The pattern of this id, or NULL for an unknown id. */
const struct rml_pattern *rml_get(uint8_t id);   /* FW l.320 to l.328 */

/* Total ms of the pattern (FW l.320 to l.328, column "Total ms"); 0 for an unknown id. */
uint32_t rml_total_ms(uint8_t id);

/* Number of on segments (pulses); 0 for an unknown id. */
uint8_t rml_pulses(uint8_t id);

/* Time in ms from the pattern start to the start of segment k (k = n gives the total); segment k is on for even k. */
uint32_t rml_seg_start_ms(const struct rml_pattern *p, uint8_t k);

/* A new pattern replaces the one playing, except that M1, M2, M3 and MF are never cut by MH or MT (FW l.318).
 * `playing` 0 = nothing plays. */
bool rml_may_replace(uint8_t playing, uint8_t incoming);   /* FW l.318 */

/* The setting "Vibration" off disables MH and MT only (FW l.301, FW 2.2). */
bool rml_vibration_allows(bool vibration_on, uint8_t id);

/* The charge of one ON pulse of t_on ms in µA·s: t_on x RREC_MOTOR_RUN_MA + RREC_MOTOR_START_MS x
 * RREC_MOTOR_START_MA (FW l.332). */
uint32_t rml_pulse_uas(uint32_t t_on_ms);

/* The charge of a whole pattern in µA·s (sum over its pulses); 0 for an unknown id. */
uint32_t rml_pattern_uas(uint8_t id);

#ifdef __cplusplus
}
#endif

#endif
