/*
 * rmo.c: the thin part of the motor unit (software step 6, unit U6): a k_timer plays one pattern on the MOTOR pin
 * through rhw_motor() and reads the time through rhw_clock(). No other hardware call. Written for this project from
 * design/firmware.md section 3.1.
 *
 * One MOTOR high per on segment, no PWM (FW l.314). Each segment boundary is scheduled from the pattern's start
 * tick, so the rounding of a timer never adds up and the pin times stay the specified ones (FW l.315).
 * A pattern that replaces one playing during an on segment keeps the pin high: the old pulse is closed (its charge
 * so far is reported) and the new pulse counts as a new start. The callbacks run under the player's lock and must not
 * call back into this unit.
 */
#include <errno.h>

#include <zephyr/kernel.h>
#include <zephyr/spinlock.h>

#include <ring_motor/rmo.h>
#include <ring_rhw/rhw.h>
#include <ring_rhw/rhw_sim.h>

#include "rmo_logic.h"

static struct k_spinlock lock;
static struct k_timer tmr;
static bool tmr_ready;
static struct rmo_cb cb;
static bool vib_on = true;
static uint8_t playing;                 /* 0 = nothing, else enum rrec_pattern */
static uint8_t seg;                     /* the segment now running */
static bool pin_high;
static int64_t t0_ticks;                /* tick of the pattern start */
static int64_t pulse_ticks;             /* tick the pin went high (valid while pin_high) */
static const struct rml_pattern *pat;

static void pin_set(bool high)
{
	(void)rhw_motor()->set(high);
	pin_high = high;
	if (cb.edge != NULL) {
		cb.edge(high, rhw_clock()->cycles());
	}
	if (high) {
		pulse_ticks = k_uptime_ticks();
	}
}

/* The pulse that ran from pulse_ticks to now ends: report its charge (FW l.332). */
static void pulse_end(void)
{
	int64_t el_ms = k_ticks_to_ms_floor64(k_uptime_ticks() - pulse_ticks);

	if (cb.charge != NULL) {
		cb.charge(rml_pulse_uas((uint32_t)el_ms));
	}
}

/* Arm the timer for the end of segment k, counted from the pattern's start tick. */
static void schedule_end_of(uint8_t k)
{
	int64_t target = t0_ticks + k_ms_to_ticks_ceil64(rml_seg_start_ms(pat, (uint8_t)(k + 1u)));
	int64_t wait = target - k_uptime_ticks();

	if (wait < 0) {
		wait = 0;
	}
	k_timer_start(&tmr, K_TICKS(wait), K_NO_WAIT);
}

/* The segment `seg` ends now. */
static void on_expiry(struct k_timer *t)
{
	ARG_UNUSED(t);
	k_spinlock_key_t key = k_spin_lock(&lock);

	if (playing == 0u) {
		k_spin_unlock(&lock, key);
		return;
	}
	if ((seg & 1u) == 0u) {              /* an on segment ended: MOTOR low, and the pulse's charge */
		pin_set(false);
		pulse_end();
	} else {                             /* an off segment ended: MOTOR high */
		pin_set(true);
	}
	seg++;
	if (seg >= pat->n) {
		playing = 0;
		pat = NULL;
	} else {
		schedule_end_of(seg);
	}
	k_spin_unlock(&lock, key);
}

static void reboot_hook(void)
{
	k_spinlock_key_t key = k_spin_lock(&lock);

	if (tmr_ready) {
		k_timer_stop(&tmr);
	}
	playing = 0;
	pat = NULL;
	pin_high = false;
	vib_on = true;
	cb = (struct rmo_cb){ 0 };
	k_spin_unlock(&lock, key);
}

int rmo_init(const struct rmo_cb *c)
{
	k_spinlock_key_t key = k_spin_lock(&lock);

	if (!tmr_ready) {
		k_timer_init(&tmr, on_expiry, NULL);
		tmr_ready = true;
	}
	k_timer_stop(&tmr);
	cb = (c != NULL) ? *c : (struct rmo_cb){ 0 };
	playing = 0;
	pat = NULL;
	pin_high = false;
	k_spin_unlock(&lock, key);
#ifdef CONFIG_RING_RHW_SIM
	(void)rhw_sim_add_reboot_hook(reboot_hook);
#endif
	return rhw_motor()->set(false);
}

int rmo_play(enum rrec_pattern p)
{
	const struct rml_pattern *np = rml_get((uint8_t)p);

	if (np == NULL) {
		return -EINVAL;
	}
	k_spinlock_key_t key = k_spin_lock(&lock);

	if (!rml_vibration_allows(vib_on, (uint8_t)p)) {
		k_spin_unlock(&lock, key);
		return -ECANCELED;
	}
	if (!rml_may_replace(playing, (uint8_t)p)) {
		k_spin_unlock(&lock, key);
		return -EBUSY;
	}
	k_timer_stop(&tmr);
	if (pin_high) {                      /* cut during an on segment: close that pulse; the pin stays high */
		pulse_end();
		pulse_ticks = k_uptime_ticks();
	}
	pat = np;
	playing = (uint8_t)p;
	seg = 0;
	t0_ticks = k_uptime_ticks();
	if (!pin_high) {
		pin_set(true);
	}
	if (cb.started != NULL) {
		cb.started((uint8_t)p, rhw_clock()->now_ms());
	}
	schedule_end_of(0u);
	k_spin_unlock(&lock, key);
	return 0;
}

void rmo_set_vibration(bool on)
{
	k_spinlock_key_t key = k_spin_lock(&lock);

	vib_on = on;
	k_spin_unlock(&lock, key);
}

bool rmo_playing(void)
{
	k_spinlock_key_t key = k_spin_lock(&lock);
	bool r = playing != 0u;

	k_spin_unlock(&lock, key);
	return r;
}

void rmo_stop(void)
{
	k_spinlock_key_t key = k_spin_lock(&lock);

	if (tmr_ready) {
		k_timer_stop(&tmr);
	}
	if (pin_high) {
		pin_set(false);
		pulse_end();
	}
	playing = 0;
	pat = NULL;
	k_spin_unlock(&lock, key);
}
