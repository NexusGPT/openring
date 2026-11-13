/*
 * rpw_logic.h: the pure part of ring_power (software step 6, unit U5). No kernel call, no driver call: stdint,
 * stdbool, string and the specification numbers of rrec_spec.h. "FW l.N" = line N of design/firmware.md.
 * The thin part (rpw.c) calls these; the unit's tests call them directly.
 */
#ifndef RING_POWER_RPW_LOGIC_H
#define RING_POWER_RPW_LOGIC_H

#include <stdbool.h>
#include <stdint.h>

#include <ring_rhw/rrec_spec.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ------------------------------------------------------------------ levels (FW l.114 to l.118) */
enum rpwl_level {                 /* the values of enum rc_batt in ring_core/rc_types.h */
	RPWL_LEVEL_OK = 0,
	RPWL_LEVEL_B15 = 1,
	RPWL_LEVEL_B5 = 2,
	RPWL_LEVEL_B2 = 3,
};

/* The window of the last samples (FW l.928: "the mean of the last 10"). */
#define RPWL_WINDOW 5u
struct rpwl_window {
	uint16_t mv[RPWL_WINDOW];
	uint8_t n;                /* samples held, at most RPWL_WINDOW */
	uint8_t next;             /* slot the next sample goes to */
};
void rpwl_window_reset(struct rpwl_window *w);
void rpwl_window_push(struct rpwl_window *w, uint16_t mv);
uint32_t rpwl_window_sum(const struct rpwl_window *w);

/* mean voltage sum_mv / n (n >= 1) at or under limit_mv, compared without rounding (FW l.116, l.117). */
bool rpwl_volt_at_or_under(uint32_t sum_mv, uint32_t n, uint32_t limit_mv);

/* The level of a state of charge (0.1 %) and a mean voltage given as sum and count (FW l.115 to l.117). */
uint8_t rpwl_level(uint16_t soc_x10, uint32_t sum_mv, uint32_t n);

/* One judge per run: the window and the last level reported to the core. */
struct rpwl_judge {
	struct rpwl_window w;
	uint8_t reported;         /* enum rpwl_level last reported; OK at start (the core starts at OK) */
};
void rpwl_judge_reset(struct rpwl_judge *j);
/* Feed one sample. recording = the mean of the last RPWL_WINDOW samples; else the single sample (FW l.928).
 * Returns the level; *changed = the level differs from the last reported (both directions, FW l.211 to l.213);
 * *mean_mv = the mean used. A reported level is remembered. */
uint8_t rpwl_judge_sample(struct rpwl_judge *j, uint16_t soc_x10, uint16_t mv, bool recording, uint16_t *mean_mv,
			  bool *changed);

/* ------------------------------------------------------------------ sampling period per core state (FW l.928) */
/* ms between samples for an enum rc_state value: RREC_SAMPLE_REC_MS in RECORDING, RREC_SAMPLE_IDLE_MS in every other
 * awake state, 0 in SHIP and OFF (no sampling) and for a value that is no state (rpwl_state_valid false). */
uint32_t rpwl_period_ms(uint8_t rc_state);
bool rpwl_state_valid(uint8_t rc_state);
bool rpwl_is_recording(uint8_t rc_state);

/* ------------------------------------------------------------------ charger (FW l.129, l.878, l.894) */
/* CHARGE_CURRENT in microamps, the one constant (defined in rpw_logic.c with its five build assertions). */
uint32_t rpwl_charge_current_ua(void);
/* "charge on" writes only when the charger is off (FW l.129: already on, nothing changes). */
bool rpwl_charge_on_needed(bool is_on);
enum rpwl_chg_step {
	RPWL_CHG_NONE = 0,
	RPWL_CHG_DISABLE,         /* BCHGENABLECLR */
	RPWL_CHG_CURRENT,         /* BCHGISET */
	RPWL_CHG_ENABLE,          /* BCHGENABLESET */
};
#define RPWL_CHG_STEPS 3u
/* The order of the writes of "charge on": disable, current, enable (FW l.894). */
enum rpwl_chg_step rpwl_charge_step(uint8_t i);

/* ------------------------------------------------------------------ the motor's charge (FW l.927) */
/* I_fed = I_measured + Q_motor / t_sample, the motor's charge counted as a discharge (positive µA = discharge, the
 * sign of struct rhw_pmic_sample). motor_uas in µA·s, dt_ms the time since the last step; dt_ms = 0 adds nothing. */
int32_t rpwl_fed_ua(int32_t measured_ua, uint32_t motor_uas, uint32_t dt_ms);

/* ------------------------------------------------------------------ the current limit (FW l.990 to l.995) */
enum rpwl_ilim_act {
	RPWL_ILIM_NONE = 0,       /* not active: nothing */
	RPWL_ILIM_FIRST,          /* first reading of a run: log, the screen goes off for RREC_ILIM_SCREEN_MS */
	RPWL_ILIM_AGAIN,          /* ACTIVE again with the screen already off: log with the count, nothing else */
};
struct rpwl_ilim {
	bool off;                 /* the screen is off for the 10 s */
	uint32_t since_ms;        /* when it went off */
	uint32_t count;           /* ACTIVE readings of this run */
};
void rpwl_ilim_reset(struct rpwl_ilim *s);
enum rpwl_ilim_act rpwl_ilim_step(struct rpwl_ilim *s, bool active, uint32_t now_ms, uint32_t *count);

/* ------------------------------------------------------------------ ship mode steps 2 to 5 (FW l.936 to l.941) */
enum rpwl_ship_act {
	RPWL_SHIP_CONFIG,         /* step 2: SHPHLDCONFIG RREC_SHPHLD_MS */
	RPWL_SHIP_STROBE,         /* step 2: TASKSHPHLDCFGSTROBE */
	RPWL_SHIP_WAIT_VBUS,      /* step 3: wait for VBUS removed, doing nothing else; then ask again */
	RPWL_SHIP_BEFORE_TASK,    /* the caller's hook (the ship beacon stops), first try only */
	RPWL_SHIP_TASK,           /* step 4: TASKENTERSHIPMODE */
	RPWL_SHIP_WAIT_1S,        /* step 5: wait RREC_SHIP_RETRY_MS; reaching the end of it means still running */
	RPWL_SHIP_LOG_RETRY,      /* step 5: log the event, back to step 3 (once) */
	RPWL_SHIP_GIVE_UP,        /* the retry also left the ring running: return -ETIMEDOUT */
};
enum rpwl_ship_state {
	RPWL_SS_CONFIG, RPWL_SS_STROBE, RPWL_SS_VBUS, RPWL_SS_TASK, RPWL_SS_AFTER, RPWL_SS_RETRY, RPWL_SS_DONE,
};
struct rpwl_ship {
	uint8_t st;               /* enum rpwl_ship_state */
	uint8_t tries;            /* retries taken */
};
void rpwl_ship_reset(struct rpwl_ship *s);
/* The next action. vbus = VBUS is present now (read by the caller each time it asks). */
enum rpwl_ship_act rpwl_ship_next(struct rpwl_ship *s, bool vbus);

/* ------------------------------------------------------------------ reset causes (FW l.996) */
#define RPWL_CAUSE_MASK 0x7Fu     /* the seven RSTCAUSE bits RREC_RST_* */
/* The log arguments of RREC_LOG_PMIC_RESET: RSTCAUSE, CHARGERERRREASON, CHARGERERRSENSOR (rrec_spec.h). */
#define RPWL_CAUSE_ARGS 3u
void rpwl_cause_args(uint8_t rstcause, uint8_t err_reason, uint8_t err_sensor, uint8_t out[RPWL_CAUSE_ARGS]);
/* Number of known cause bits set. */
uint8_t rpwl_cause_count(uint8_t rstcause);

/* ------------------------------------------------------------------ GET_BATTERY (FW l.702) */
/* enum rrec_charge_state code from the charger's state and its latched error: a latched error or a state that is
 * none of the six reads 5 (error). */
uint8_t rpwl_charge_code(uint8_t state, uint8_t err_reason);
/* Time to full in minutes, rounded up; UINT16_MAX when unknown (UINT32_MAX seconds), at most 65,534 otherwise. */
uint16_t rpwl_ttf_min(uint32_t ttf_s);
/* RREC_GET_BATTERY_BYTES bytes, little endian: mV u16, SoC x10 u16, charging state u8, die temperature 0.1 C i16,
 * time to full u16. */
void rpwl_battery_bytes(uint16_t mv, uint16_t soc_x10, uint8_t code, int16_t die_c_x10, uint16_t ttf_min,
			uint8_t out[RREC_GET_BATTERY_BYTES]);

#ifdef __cplusplus
}
#endif

#endif
