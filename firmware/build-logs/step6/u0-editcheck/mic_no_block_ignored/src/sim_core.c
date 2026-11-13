/*
 * ring_rhw simulation: the event log, the two resets, the reboot hooks and the "shipped" state. Written for this
 * project (no code of the kit).
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

#include "sim_int.h"

struct k_spinlock sim_lock;

static struct rhw_sim_ev evlog[CONFIG_RING_RHW_SIM_LOG_SIZE];
static uint32_t ev_n;
static uint32_t ev_seq;
static uint32_t ev_over;

static void (*hooks[CONFIG_RING_RHW_SIM_REBOOT_HOOKS])(void);
static uint32_t n_hooks;
static uint32_t n_reboots;

static bool shipped;
static uint32_t ship_refused;

static void name_of_caller(char out[16], const char *caller)
{
	const char *src = caller;

	if (src == NULL) {
		if (k_is_in_isr()) {
			src = "isr";
		} else {
#if defined(CONFIG_THREAD_NAME)
			src = k_thread_name_get(k_current_get());
			if (src == NULL || src[0] == '\0') {
				src = "?";
			}
#else
			src = "?";
#endif
		}
	}
	strncpy(out, src, 15);
	out[15] = '\0';
}

void sim_log(uint16_t kind, int64_t a0, int64_t a1, int64_t a2, int32_t res, const char *caller)
{
	struct rhw_sim_ev e;

	memset(&e, 0, sizeof(e));
	e.kind = kind;
	e.a0 = a0;
	e.a1 = a1;
	e.a2 = a2;
	e.res = res;
	name_of_caller(e.caller, caller);

	k_spinlock_key_t key = k_spin_lock(&sim_lock);

	e.t_us = (int64_t)k_ticks_to_us_floor64(k_uptime_ticks());
	e.seq = ev_seq++;
	if (ev_n < ARRAY_SIZE(evlog)) {
		evlog[ev_n++] = e;
	} else {
		ev_over++;
	}
	k_spin_unlock(&sim_lock, key);
}

uint32_t rhw_sim_log_count(void)
{
	return ev_n;
}

bool rhw_sim_log_get(uint32_t i, struct rhw_sim_ev *out)
{
	bool ok = false;
	k_spinlock_key_t key = k_spin_lock(&sim_lock);

	if (i < ev_n) {
		*out = evlog[i];
		ok = true;
	}
	k_spin_unlock(&sim_lock, key);
	return ok;
}

uint32_t rhw_sim_log_overflow(void)
{
	return ev_over;
}

void rhw_sim_log_clear(void)
{
	k_spinlock_key_t key = k_spin_lock(&sim_lock);

	ev_n = 0;
	ev_over = 0;
	ev_seq = 0;
	k_spin_unlock(&sim_lock, key);
}

int32_t rhw_sim_log_find(uint16_t kind, uint32_t from)
{
	for (uint32_t i = from; i < ev_n; i++) {
		if (evlog[i].kind == kind) {
			return (int32_t)i;
		}
	}
	return -1;
}

uint32_t rhw_sim_log_count_kind(uint16_t kind)
{
	uint32_t c = 0;

	for (uint32_t i = 0; i < ev_n; i++) {
		if (evlog[i].kind == kind) {
			c++;
		}
	}
	return c;
}

void rhw_sim_log_dump(void)
{
	for (uint32_t i = 0; i < ev_n; i++) {
		const struct rhw_sim_ev *e = &evlog[i];

		printk("rhw_sim ev %u t_us %lld kind %u a0 %lld a1 %lld a2 %lld res %d caller %s\n", e->seq,
		       (long long)e->t_us, e->kind, (long long)e->a0, (long long)e->a1, (long long)e->a2, e->res,
		       e->caller);
	}
}

bool sim_dead(uint16_t kind)
{
	if (!shipped) {
		return false;
	}
	ship_refused++;
	sim_log(RHW_EV_SHIP_REFUSED, kind, 0, 0, -ESHUTDOWN, NULL);
	return true;
}

/* called by the simulated power chip's ship task */
void sim_set_shipped(void)
{
	shipped = true;
}

bool rhw_sim_shipped(void)
{
	return shipped;
}

uint32_t rhw_sim_ship_refused(void)
{
	return ship_refused;
}

int rhw_sim_add_reboot_hook(void (*fn)(void))
{
	if (fn == NULL) {
		return -EINVAL;
	}
	for (uint32_t i = 0; i < n_hooks; i++) {
		if (hooks[i] == fn) {
			return 0;
		}
	}
	if (n_hooks >= ARRAY_SIZE(hooks)) {
		return -ENOMEM;
	}
	hooks[n_hooks++] = fn;
	return 0;
}

uint32_t rhw_sim_reboots(void)
{
	return n_reboots;
}

static void drivers_reset(bool full)
{
	sim_disk_reset(full);
	sim_mic_reset(full);
	sim_pmic_reset(full);
	sim_hfxo_reset(full);
	sim_misc_reset(full);
	sim_usb_reset(full);
	sim_image_reset(full);
	sim_persist_reset(full);
}

void rhw_sim_reboot(void)
{
	n_reboots++;
	shipped = false;
	ship_refused = 0;
	drivers_reset(false);
	for (uint32_t i = 0; i < n_hooks; i++) {
		hooks[i]();
	}
	sim_log(RHW_EV_SIM_REBOOT, n_reboots, 0, 0, 0, NULL);
}

void rhw_sim_reset(void)
{
	n_reboots = 0;
	shipped = false;
	ship_refused = 0;
	drivers_reset(true);
	rhw_sim_log_clear();
}

static int sim_init(void)
{
	rhw_sim_reset();
	return 0;
}

SYS_INIT(sim_init, APPLICATION, 0);
