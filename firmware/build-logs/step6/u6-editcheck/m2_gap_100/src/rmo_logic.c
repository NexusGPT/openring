/*
 * rmo_logic.c: the pure part of the motor unit (software step 6, unit U6). No kernel call: stdint and stdbool only.
 * Written for this project from design/firmware.md section 3.1.
 */
#include "rmo_logic.h"

/* FW l.320 to l.328: on / off times in ms, MOTOR-pin times (FW l.315). rrec_spec.h holds the ids, not the times. */
static const struct rml_pattern pat_m1 = { 1, { 80 } };
static const struct rml_pattern pat_m2 = { 3, { 80, 100, 80 } };
static const struct rml_pattern pat_m3 = { 5, { 80, 120, 80, 120, 80 } };
static const struct rml_pattern pat_mh = { 1, { 40 } };
static const struct rml_pattern pat_mt = { 1, { 25 } };
static const struct rml_pattern pat_mw = { 1, { 60 } };
static const struct rml_pattern pat_mf = { 3, { 300, 200, 300 } };

const struct rml_pattern *rml_get(uint8_t id)
{
	switch (id) {
	case RREC_PAT_M1:
		return &pat_m1;
	case RREC_PAT_M2:
		return &pat_m2;
	case RREC_PAT_M3:
		return &pat_m3;
	case RREC_PAT_MH:
		return &pat_mh;
	case RREC_PAT_MT:
		return &pat_mt;
	case RREC_PAT_MW:
		return &pat_mw;
	case RREC_PAT_MF:
		return &pat_mf;
	default:
		return NULL;
	}
}

uint32_t rml_seg_start_ms(const struct rml_pattern *p, uint8_t k)
{
	uint32_t t = 0;

	for (uint8_t i = 0; i < k && i < p->n; i++) {
		t += p->ms[i];
	}
	return t;
}

uint32_t rml_total_ms(uint8_t id)
{
	const struct rml_pattern *p = rml_get(id);

	return p == NULL ? 0u : rml_seg_start_ms(p, p->n);
}

uint8_t rml_pulses(uint8_t id)
{
	const struct rml_pattern *p = rml_get(id);

	return p == NULL ? 0u : (uint8_t)((p->n + 1u) / 2u);
}

static bool is_never_cut(uint8_t id)
{
	return id == RREC_PAT_M1 || id == RREC_PAT_M2 || id == RREC_PAT_M3 || id == RREC_PAT_MF;
}

bool rml_may_replace(uint8_t playing, uint8_t incoming)
{
	if (playing == 0u) {
		return true;
	}
	if ((incoming == RREC_PAT_MH || incoming == RREC_PAT_MT) && is_never_cut(playing)) {
		return false;
	}
	return true;
}

bool rml_vibration_allows(bool vibration_on, uint8_t id)
{
	if (vibration_on) {
		return true;
	}
	return !(id == RREC_PAT_MH || id == RREC_PAT_MT);
}

uint32_t rml_pulse_uas(uint32_t t_on_ms)
{
	return t_on_ms * RREC_MOTOR_RUN_MA + RREC_MOTOR_START_MS * RREC_MOTOR_START_MA;
}

uint32_t rml_pattern_uas(uint8_t id)
{
	const struct rml_pattern *p = rml_get(id);
	uint32_t q = 0;

	if (p == NULL) {
		return 0;
	}
	for (uint8_t i = 0; i < p->n; i += 2u) {
		q += rml_pulse_uas(p->ms[i]);
	}
	return q;
}
