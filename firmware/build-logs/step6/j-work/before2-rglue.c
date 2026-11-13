/* Ring glue: see rglue.h. */

#include <errno.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

#include <ring_core/rc_core.h>
#include <ring_control/rctl.h>
#include <ring_glue/rglue.h>
#if IS_ENABLED(CONFIG_RING_IPHONE)
#include <ring_iphone/rip.h>
#endif

static struct rc_core core;
static struct rglue_ops ops;
static K_MUTEX_DEFINE(lk);
static K_SEM_DEFINE(wake, 0, 1);

/* The screens part owns the fact screen_on. It is read here, under the glue's lock, right before every core call, so there is
 * no stored copy that an older value could overwrite. */
static void refresh_fact(void)
{
	if (ops.screen_fact != NULL) {
		core.facts.screen_on = ops.screen_fact();
	}
}

static void dispatch(const struct rc_actions *a, rc_ms_t t)
{
	enum rc_event last = RC_EV_COUNT;

	/* control first: it is gated by "control active" and takes only the five screen actions */
	(void)rctl_core_actions(a);
	if (ops.action != NULL) {
		for (uint8_t i = 0; i < a->n; i++) {
			ops.action((enum rc_action)a->a[i], t);
		}
	}
	if (ops.after != NULL) {
		if (a->last_row > 0) {
			for (uint16_t i = 0; i < rc_table_rows; i++) {
				if (rc_table[i].row == a->last_row) {
					last = (enum rc_event)rc_table[i].event;
				}
			}
		}
		(void)ops.after(a, last, rc_core_state(&core), t);
	}
}

/* Step 6: FACTORY_TEST hands the gesture events of the core's recogniser to the join (rglue_ops.factory_gesture) */
static bool factory_gestures(void)
{
	return ops.factory_gesture != NULL && rc_core_state(&core) == RC_ST_FACTORY_TEST;
}

static void hand_gestures(const struct rc_gev_list *gl)
{
	for (uint8_t i = 0; i < gl->n; i++) {
		ops.factory_gesture(&gl->e[i]);
	}
}

static void tick_thread(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);
	for (;;) {
		k_timeout_t to = K_FOREVER;
		rc_ms_t nt;
		struct rc_actions a;
		rc_ms_t now;

		k_mutex_lock(&lk, K_FOREVER);
		nt = rc_core_next_tick(&core);
		k_mutex_unlock(&lk);
		now = k_uptime_get();
		if (nt != RC_NO_TICK) {
			to = nt > now ? K_MSEC(nt - now) : K_NO_WAIT;
		}
		(void)k_sem_take(&wake, to);
		now = k_uptime_get();
		k_mutex_lock(&lk, K_FOREVER);
		rc_actions_clear(&a);
		refresh_fact();
		if (factory_gestures()) {
			struct rc_gev_list gl;

			gl.n = 0;
			rc_gesture_tick(&core.g, now, &gl);   /* the deadlines of the hold (MW, long, short, double) */
			hand_gestures(&gl);
		}
		rc_core_tick(&core, now, &a);
		dispatch(&a, now);
		k_mutex_unlock(&lk);
	}
}

K_THREAD_STACK_DEFINE(tick_stack, CONFIG_RING_GLUE_STACK_SIZE);
static struct k_thread tick_thread_data;

void rglue_init(const struct rglue_ops *o, enum rc_state start)
{
	ops = o != NULL ? *o : (struct rglue_ops){ 0 };
#if IS_ENABLED(CONFIG_RING_IPHONE)
	/* the iPhone part (notifications, media, time) starts next to devices and control; it calls
	 * nothing in the core or in this module, so nothing from the iPhone can start a recording */
	(void)rip_init();
#endif
	rc_core_init(&core, RC_CENTRE_SW2, start, k_uptime_get());
	/* step 6, decision D1: the sign hook (NULL leaves none: the sign counts as drawn) */
	rc_core_set_sign_hook(&core, ops.sign_start, NULL);
	(void)k_thread_create(&tick_thread_data, tick_stack, K_THREAD_STACK_SIZEOF(tick_stack), tick_thread, NULL,
			      NULL, NULL, K_PRIO_PREEMPT(8), 0, K_NO_WAIT);
	k_thread_name_set(&tick_thread_data, "rglue");
}

void rglue_input(enum rc_switch sw, bool pressed)
{
	struct rc_actions a;
	rc_ms_t now = k_uptime_get();

	k_mutex_lock(&lk, K_FOREVER);
	rc_actions_clear(&a);
	refresh_fact();
	if (factory_gestures()) {
		struct rc_gev_list gl;

		gl.n = 0;
		rc_gesture_input(&core.g, sw, pressed, now, &gl);   /* the same recogniser the core uses */
		hand_gestures(&gl);
	} else {
		rc_core_input(&core, sw, pressed, now, &a);
	}
	dispatch(&a, now);
	k_mutex_unlock(&lk);
	k_sem_give(&wake);
}

struct rc_core *rglue_core(void)
{
	return &core;
}

enum rc_state rglue_state(void)
{
	enum rc_state s;

	k_mutex_lock(&lk, K_FOREVER);
	s = rc_core_state(&core);
	k_mutex_unlock(&lk);
	return s;
}

void rglue_set_screen_on(bool on)
{
	k_mutex_lock(&lk, K_FOREVER);
	rc_core_facts(&core)->screen_on = on;
	k_mutex_unlock(&lk);
}

void rglue_event(enum rc_event ev)
{
	struct rc_actions a;
	rc_ms_t now = k_uptime_get();

	k_mutex_lock(&lk, K_FOREVER);
	rc_actions_clear(&a);
	refresh_fact();
	rc_core_event(&core, ev, now, &a);
	dispatch(&a, now);
	k_mutex_unlock(&lk);
	k_sem_give(&wake);
}

int rglue_event_try(enum rc_event ev)
{
	struct rc_actions a;
	rc_ms_t now = k_uptime_get();

	if (k_mutex_lock(&lk, K_NO_WAIT) != 0) {
		return -EBUSY;
	}
	rc_actions_clear(&a);
	refresh_fact();
	rc_core_event(&core, ev, now, &a);
	dispatch(&a, now);
	k_mutex_unlock(&lk);
	k_sem_give(&wake);
	return 0;
}

void rglue_battery(enum rc_batt level)
{
	struct rc_actions a;
	rc_ms_t now = k_uptime_get();

	k_mutex_lock(&lk, K_FOREVER);
	rc_actions_clear(&a);
	refresh_fact();
	rc_core_battery(&core, level, now, &a);
	dispatch(&a, now);
	k_mutex_unlock(&lk);
	k_sem_give(&wake);
}

void rglue_set_vibration(bool on)
{
	k_mutex_lock(&lk, K_FOREVER);
	rc_core_facts(&core)->vibration_on = on;
	k_mutex_unlock(&lk);
}
