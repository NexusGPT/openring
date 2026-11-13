/*
 * rpw.h: the power part (software step 6, unit U5 builds it; U0 wrote this header, frozen: changes only through the
 * lead). Battery levels, the charger, the gauge with the motor's charge, ship mode, reset causes, the current limit:
 * design/firmware.md sections 1.1, 1.2 (R-CHG) and 8 ("FW l.N" = line N of that file).
 *
 * Pure part (rpw_logic.c: levels from SoC and the mean voltage, mean of 10, report on change both ways, charge on when
 * off only, CHARGE_CURRENT and its build assertions, motor charge added, the current-limit decision, the ship steps as
 * a step machine, reset-cause decoding, GET_BATTERY codes) is declared in the unit's own src/ header.
 *
 * CHARGE_CURRENT (FW l.878, l.894) is defined ONCE, in ring_power's own source, with the five build assertions of FW
 * l.894 (unset, above 17,600, under 4,000, over 100,000, not a multiple of 500); it is not in rrec_spec.h so that the
 * unit's broken copies change one place. Other units read it with rpw_charge_current_ua().
 *
 * The rails: ring_power does NOT switch VDD_MIC or VDD_SD. They are switched only through
 * rhw_pmic()->rail_set(): VDD_SD by ring_store, VDD_MIC only by rec_mics_on() (FW l.342). (The plan's U5 offer "set a
 * rail" is dropped so that one path exists per rail.)
 * Levels are enum rc_batt values of ring_core/rc_types.h (OK 0, B15 1, B5 2, B2 3) and states enum rc_state values,
 * passed as uint8_t so that this header needs no core header.
 * Hardware only through rhw.h: rhw_pmic(), rhw_gauge(), rhw_clock().
 */
#ifndef RING_POWER_RPW_H
#define RING_POWER_RPW_H

#include <stdbool.h>
#include <stdint.h>

#include <ring_rhw/rrec_spec.h>

#ifdef __cplusplus
extern "C" {
#endif

struct rpw_cb {
	/* The level changed (either way) after a sample (FW l.211 to l.213; rc_core_battery's contract): enum rc_batt.
	 * Power thread; may take the glue's lock (the join calls rglue_battery). */
	void (*level)(uint8_t level);
	/* VBUS in or out (FW l.979), after "charge on" was done for VBUS in (R-CHG, FW l.210, ruling R8). Power thread. */
	void (*vbus)(bool present);
	/* A charge error with the chip's latched values (FW l.176). Power thread. */
	void (*charge_error)(uint8_t err_reason, uint8_t err_sensor);
	/* The current limit read ACTIVE (FW l.990 to l.995): first = true for the first reading of a run of ACTIVE readings
	 * (screen to act on), false for "again with the screen off" (log only, with the count). Power thread. */
	void (*ilim)(bool first, uint16_t battery_mv, uint32_t count);
	/* Event log hook (rrec_spec.h); RREC_LOG_BATTERY, RREC_LOG_ILIM_ACTIVE, RREC_LOG_PMIC_RESET, RREC_LOG_SHIP_RETRY. */
	rrec_log_fn log;
};

/* Start: callbacks, the power chip's callbacks, the gauge from a first sample, the sampling timer (60 s until
 * rpw_state says otherwise). If VBUS is present now, charge on at once (FW l.893: in BOOT before storage is mounted)
 * and cb->vbus(true). Once, at boot, after rpw_boot_causes. Blocks for one sample. */
int rpw_start(const struct rpw_cb *cb);

/* BOOT (FW l.996): read RSTCAUSE and the charger error log, log them (RREC_LOG_PMIC_RESET), clear them
 * (TASKCLRERRLOG). Once, at boot, before rpw_start; cb->log of rpw_start is not set yet, so the log hook is passed. */
int rpw_boot_causes(rrec_log_fn log);

/* The core state now (enum rc_state): RECORDING samples every RREC_SAMPLE_REC_MS and judges on the mean of the last
 * RREC_MEAN_SAMPLES; every other awake state every RREC_SAMPLE_IDLE_MS on the single sample (FW l.928). Any thread;
 * never blocks. */
void rpw_state(uint8_t rc_state);

/* "charge on" (FW l.129): when off, disable, write CHARGE_CURRENT, enable (FW l.894); when already on, nothing.
 * "charge off": disable. Any thread; blocks for the I2C writes. */
int rpw_charge_on(void);
int rpw_charge_off(void);  /* FW l.129 */

/* The motor's charge of one pulse in µA·s (mA.s x 1000), added to the next sample's current as a discharge
 * (FW l.927). ANY context (the motor's timer); never blocks. */
void rpw_motor_charge(uint32_t uas);

/* Ship mode steps 2 to 5 of FW 8.4 (step 1 is the join's): SHPHLDCONFIG RREC_SHPHLD_MS and the strobe; with VBUS
 * wait for VBUS removed doing nothing else (FW l.939); before_task() right before TASKENTERSHIPMODE (the ship beacon
 * stops there, ruling R20; may be NULL); the task; still running RREC_SHIP_RETRY_MS later: log and back to the wait
 * once (FW l.941). Returns only when the chip did not cut the supply: -ETIMEDOUT after the retry. Join's thread;
 * blocks until VBUS is removed. */
int rpw_ship(void (*before_task)(void));

/* GET_BATTERY (FW l.702): RREC_GET_BATTERY_BYTES bytes from the last sample and gauge step. Any thread; blocks for
 * the charger status read. */
int rpw_battery_report(uint8_t out[RREC_GET_BATTERY_BYTES]);

struct rpw_values {               /* for SCR_CHARGING (FW l.374) and the rules of other units */
	uint16_t battery_mv;      /* the last sample */
	uint16_t soc_x10;         /* the gauge */
	bool vbus;
	bool charging;            /* state trickle, CC or CV */
	bool full;                /* state full */
	uint16_t to_full_min;     /* UINT16_MAX when unknown */
	int16_t die_c_x10;
	uint8_t level;            /* enum rc_batt */
};
/* The values of the last sample. Any thread; never blocks. */
void rpw_values(struct rpw_values *out);  /* FW l.374 */

/* CHARGE_CURRENT in µA (FW l.878). */
uint32_t rpw_charge_current_ua(void);

#ifdef __cplusplus
}
#endif

#endif
