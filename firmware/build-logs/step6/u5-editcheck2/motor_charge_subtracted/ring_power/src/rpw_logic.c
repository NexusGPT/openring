/*
 * rpw_logic.c: the pure part of ring_power (software step 6, unit U5). No kernel call and no driver call: the only
 * includes are stdint, stdbool, string, the specification numbers (rrec_spec.h) and the core's state names
 * (rc_types.h, itself pure). "FW l.N" = line N of design/firmware.md.
 */
#include <string.h>

#include <ring_core/rc_types.h>

#include "rpw_logic.h"

/* ------------------------------------------------------------------ CHARGE_CURRENT (FW l.878, l.894)
 * The one named constant, in microamps, in this one place. FW l.894 rule 2: the build fails when it is unset, above
 * 17,600 (1 C of the smallest cell), under 4,000, over 100,000, or not a multiple of 500. */
#define CHARGE_CURRENT 15000

#ifndef CHARGE_CURRENT
#error "CHARGE_CURRENT is not set (FW l.894)"
#endif
_Static_assert(CHARGE_CURRENT <= 17600, "CHARGE_CURRENT is above 17,600 uA (FW l.894)");
_Static_assert(CHARGE_CURRENT >= 4000, "CHARGE_CURRENT is under 4,000 uA (FW l.894)");
_Static_assert(CHARGE_CURRENT <= 100000, "CHARGE_CURRENT is over 100,000 uA (FW l.894)");
_Static_assert(CHARGE_CURRENT % 500 == 0, "CHARGE_CURRENT is not a multiple of 500 uA (FW l.894)");

uint32_t rpwl_charge_current_ua(void)
{
	return CHARGE_CURRENT;
}

/* ------------------------------------------------------------------ levels */
void rpwl_window_reset(struct rpwl_window *w)
{
	memset(w, 0, sizeof(*w));
}

void rpwl_window_push(struct rpwl_window *w, uint16_t mv)
{
	w->mv[w->next] = mv;
	w->next = (uint8_t)((w->next + 1u) % RPWL_WINDOW);
	if (w->n < RPWL_WINDOW) {
		w->n++;
	}
}

uint32_t rpwl_window_sum(const struct rpwl_window *w)
{
	uint32_t sum = 0;

	for (uint8_t i = 0; i < w->n; i++) {
		sum += w->mv[i];
	}
	return sum;
}

bool rpwl_volt_at_or_under(uint32_t sum_mv, uint32_t n, uint32_t limit_mv)
{
	return sum_mv <= limit_mv * n;
}

uint8_t rpwl_level(uint16_t soc_x10, uint32_t sum_mv, uint32_t n)
{
	if (n == 0) {
		n = 1;
	}
	if (soc_x10 <= RREC_B2_SOC_X10 || rpwl_volt_at_or_under(sum_mv, n, RREC_B2_MV)) {
		return RPWL_LEVEL_B2;
	}
	if (soc_x10 <= RREC_B5_SOC_X10 || rpwl_volt_at_or_under(sum_mv, n, RREC_B5_MV)) {
		return RPWL_LEVEL_B5;
	}
	if (soc_x10 <= RREC_B15_SOC_X10) {
		return RPWL_LEVEL_B15;
	}
	return RPWL_LEVEL_OK;
}

void rpwl_judge_reset(struct rpwl_judge *j)
{
	rpwl_window_reset(&j->w);
	j->reported = RPWL_LEVEL_OK;
}

uint8_t rpwl_judge_sample(struct rpwl_judge *j, uint16_t soc_x10, uint16_t mv, bool recording, uint16_t *mean_mv,
			  bool *changed)
{
	uint32_t sum, n;
	uint8_t lvl;

	rpwl_window_push(&j->w, mv);
	if (recording) {
		sum = rpwl_window_sum(&j->w);
		n = j->w.n;
	} else {
		sum = mv;
		n = 1;
	}
	lvl = rpwl_level(soc_x10, sum, n);
	if (mean_mv != NULL) {
		*mean_mv = (uint16_t)(sum / n);
	}
	*changed = lvl != j->reported;
	j->reported = lvl;
	return lvl;
}

/* ------------------------------------------------------------------ sampling period per state */
bool rpwl_state_valid(uint8_t rc_state)
{
	return rc_state < RC_ST_COUNT;
}

bool rpwl_is_recording(uint8_t rc_state)
{
	return rc_state == RC_ST_RECORDING;
}

uint32_t rpwl_period_ms(uint8_t rc_state)
{
	if (!rpwl_state_valid(rc_state) || rc_state == RC_ST_SHIP || rc_state == RC_ST_OFF) {
		return 0;
	}
	return rpwl_is_recording(rc_state) ? RREC_SAMPLE_REC_MS : RREC_SAMPLE_IDLE_MS;
}

/* ------------------------------------------------------------------ charger */
bool rpwl_charge_on_needed(bool is_on)
{
	return !is_on;
}

enum rpwl_chg_step rpwl_charge_step(uint8_t i)
{
	static const uint8_t order[RPWL_CHG_STEPS] = { RPWL_CHG_DISABLE, RPWL_CHG_CURRENT, RPWL_CHG_ENABLE };

	return i < RPWL_CHG_STEPS ? (enum rpwl_chg_step)order[i] : RPWL_CHG_NONE;
}

/* ------------------------------------------------------------------ the motor's charge */
int32_t rpwl_fed_ua(int32_t measured_ua, uint32_t motor_uas, uint32_t dt_ms)
{
	int64_t fed = measured_ua;

	if (dt_ms > 0) {
		fed = fed - (int64_t)motor_uas * 1000 / dt_ms;
	}
	if (fed > INT32_MAX) {
		fed = INT32_MAX;
	}
	if (fed < INT32_MIN) {
		fed = INT32_MIN;
	}
	return (int32_t)fed;
}

/* ------------------------------------------------------------------ the current limit */
void rpwl_ilim_reset(struct rpwl_ilim *s)
{
	memset(s, 0, sizeof(*s));
}

enum rpwl_ilim_act rpwl_ilim_step(struct rpwl_ilim *s, bool active, uint32_t now_ms, uint32_t *count)
{
	uint32_t elapsed = now_ms - s->since_ms;

	if (!active) {
		if (s->off && elapsed >= RREC_ILIM_SCREEN_MS) {
			s->off = false;
		}
		return RPWL_ILIM_NONE;
	}
	if (!s->off || elapsed >= RREC_ILIM_SCREEN_MS) {
		s->off = true;
		s->since_ms = now_ms;
		s->count = 1;
		*count = 1;
		return RPWL_ILIM_FIRST;
	}
	s->count++;
	*count = s->count;
	return RPWL_ILIM_AGAIN;
}

/* ------------------------------------------------------------------ ship mode */
void rpwl_ship_reset(struct rpwl_ship *s)
{
	s->st = RPWL_SS_CONFIG;
	s->tries = 0;
}

enum rpwl_ship_act rpwl_ship_next(struct rpwl_ship *s, bool vbus)
{
	switch (s->st) {
	case RPWL_SS_CONFIG:
		s->st = RPWL_SS_STROBE;
		return RPWL_SHIP_CONFIG;
	case RPWL_SS_STROBE:
		s->st = RPWL_SS_VBUS;
		return RPWL_SHIP_STROBE;
	case RPWL_SS_VBUS:
		if (vbus) {
			return RPWL_SHIP_WAIT_VBUS;
		}
		s->st = RPWL_SS_TASK;
		if (s->tries == 0) {
			return RPWL_SHIP_BEFORE_TASK;
		}
		return rpwl_ship_next(s, vbus);
	case RPWL_SS_TASK:
		s->st = RPWL_SS_AFTER;
		return RPWL_SHIP_TASK;
	case RPWL_SS_AFTER:
		s->st = RPWL_SS_RETRY;
		return RPWL_SHIP_WAIT_1S;
	case RPWL_SS_RETRY:
		if (s->tries == 0) {
			s->tries = 1;
			s->st = RPWL_SS_VBUS;
			return RPWL_SHIP_LOG_RETRY;
		}
		s->st = RPWL_SS_DONE;
		return RPWL_SHIP_GIVE_UP;
	default:
		return RPWL_SHIP_GIVE_UP;
	}
}

/* ------------------------------------------------------------------ reset causes */
void rpwl_cause_args(uint8_t rstcause, uint8_t err_reason, uint8_t err_sensor, uint8_t out[RPWL_CAUSE_ARGS])
{
	out[0] = rstcause;
	out[1] = err_reason;
	out[2] = err_sensor;
}

uint8_t rpwl_cause_count(uint8_t rstcause)
{
	uint8_t n = 0;

	for (uint8_t b = 0; b < 7; b++) {
		if ((rstcause & RPWL_CAUSE_MASK) & (1u << b)) {
			n++;
		}
	}
	return n;
}

/* ------------------------------------------------------------------ GET_BATTERY */
uint8_t rpwl_charge_code(uint8_t state, uint8_t err_reason)
{
	if (err_reason != 0 || state > RREC_CHG_ERROR) {
		return RREC_CHG_ERROR;
	}
	return state;
}

uint16_t rpwl_ttf_min(uint32_t ttf_s)
{
	uint32_t m;

	if (ttf_s == UINT32_MAX) {
		return UINT16_MAX;
	}
	m = ttf_s / 60u + ((ttf_s % 60u) != 0u ? 1u : 0u);
	return m > 65534u ? 65534u : (uint16_t)m;
}

void rpwl_battery_bytes(uint16_t mv, uint16_t soc_x10, uint8_t code, int16_t die_c_x10, uint16_t ttf_min,
			uint8_t out[RREC_GET_BATTERY_BYTES])
{
	uint16_t die = (uint16_t)die_c_x10;

	out[0] = (uint8_t)(mv & 0xFFu);
	out[1] = (uint8_t)(mv >> 8);
	out[2] = (uint8_t)(soc_x10 & 0xFFu);
	out[3] = (uint8_t)(soc_x10 >> 8);
	out[4] = code;
	out[5] = (uint8_t)(die & 0xFFu);
	out[6] = (uint8_t)(die >> 8);
	out[7] = (uint8_t)(ttf_min & 0xFFu);
	out[8] = (uint8_t)(ttf_min >> 8);
}
