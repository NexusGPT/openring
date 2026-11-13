/* Ring screens, kernel part: see rscr.h. */

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

#include <ring_screens/rscr.h>
#include <ring_screens/rmd.h>
#include <ring_time/rtime.h>
#if IS_ENABLED(CONFIG_RING_SCREENS_REAL)
#include <ring_devices/rdev.h>
#endif

static struct rscr s;
static struct rscr_view view;       /* the last core state and facts, updated under lk */
static const struct rscr_ops *ops;
static K_MUTEX_DEFINE(lk);
static K_SEM_DEFINE(kick, 0, 1);
static K_SEM_DEFINE(synced, 0, 1);
static volatile uint32_t gen_asked, gen_done;
static struct rscr_stats stats;
static uint8_t batt_pct = 100;
static bool batt_charging, batt_full;
static uint16_t batt_to_full;
static char dev_names[RDEV_SLOTS][17];
static bool started;
static atomic_t power_off_pending;         /* "Power off" confirmed: carried out by the screens thread, after the core step returned */
static bool forced_down;
static volatile bool sign_from_thread_req;
static volatile int sign_from_thread_rc;                   /* test hook: behave as if rscr_start had failed */
static K_MUTEX_DEFINE(draw_lk);            /* one draw at a time: LVGL and the panel state have one user */
/* a request of rscr_sign_start, answered by the screens thread */
static struct {
	uint32_t seq;        /* the number of the last request made */
	uint32_t waiting;    /* the number of the request a caller waits for now, 0 when none (cancelled or answered) */
	uint32_t claimed;    /* the number of the request the screens thread works on */
	bool pending;        /* a request is queued and not yet taken by the thread */
	rc_ms_t now;
	int result;
} sign_req;
static K_SEM_DEFINE(sign_done, 0, 1);
static K_MUTEX_DEFINE(sign_lk);            /* one rscr_sign_start at a time */
static bool panel_on_state;
static uint8_t panel_level = 0xFF;

K_THREAD_STACK_DEFINE(rscr_stack, CONFIG_RING_SCREENS_STACK_SIZE);
static struct k_thread rscr_thread_data;
static struct rscr_frame frame;   /* the thread's working frame (large: kept out of the stack) */

static rc_ms_t now_ms(void)
{
	return ops != NULL && ops->now_ms != NULL ? ops->now_ms() : k_uptime_get();
}

static void load_view(void)
{
	/* reads of other modules; called with lk held (they do not call back into this module) */
	view.paired_mask = ops->paired_mask();
	view.active_slot = ops->active();
	view.link_up = ops->link_up();
	view.inbox_n = ops->inbox_count();
	if (view.inbox_n > RINBOX_MAX) {
		view.inbox_n = RINBOX_MAX;
	}
	for (uint8_t i = 0; i < view.inbox_n; i++) {
		struct rinbox_item it;

		if (ops->inbox_get(i, &it)) {
			view.inbox_uid[i] = it.uid;
			view.inbox_flags[i] = it.flags;
		} else {
			view.inbox_uid[i] = 0;
			view.inbox_flags[i] = 0;
		}
	}
}

static void wake_thread(void)
{
	k_sem_give(&kick);
}

static void apply_fx(const struct rscr_fxs *fx)
{
	for (uint8_t i = 0; i < fx->n; i++) {
		const struct rscr_fx *e = &fx->e[i];

		switch (e->kind) {
		case FX_CONTROL_ACTIVE:
			ops->control_active(e->a != 0);
			break;
		case FX_SET_MODE:
			ops->set_mode((enum rctl_mode)e->a);
			break;
		case FX_PAIR_OPEN:
			(void)ops->pair_open(e->a);
			break;
		case FX_PAIR_CANCEL:
			ops->pair_cancel();
			break;
		case FX_DEV_USE:
			(void)ops->dev_use(e->a);
			break;
		case FX_DEV_REMOVE:
			(void)ops->dev_remove(e->a);
			break;
		case FX_NOTIF_DISMISS:
			(void)ops->dismiss(e->u);
			break;
		case FX_NOTIF_POSITIVE:
			(void)ops->positive(e->u);
			break;
		case FX_NOTIF_READ:
			(void)ops->mark_read(e->u);
			break;
		case FX_POWER_OFF:
			/* queued: this runs inside a core step (the glue holds its lock); the screens thread calls ops->power_off
			 * after the step returned, as a step of its own */
			atomic_set(&power_off_pending, 1);
			wake_thread();
			break;
		case FX_VIBRATION:
			ops->vibration(e->a != 0);
			break;
		default:
			break;
		}
	}
}

bool rscr_glue_after(const struct rc_actions *a, enum rc_event last_event, enum rc_state state, rc_ms_t t)
{
	struct rscr_fxs fx = { 0 };
	bool fact;

	if (!started || forced_down) {
		return true;
	}
	k_mutex_lock(&lk, K_FOREVER);
	view.core_state = (uint8_t)state;
	load_view();
	rscr_on_core(&s, &view, a, last_event, t, &fx);
	fact = rscr_lock_fact(&s);
	k_mutex_unlock(&lk);
	apply_fx(&fx);
	wake_thread();
	return fact;
}

/* a change that comes from outside a core step: callbacks and the thread */
static void after_async(struct rscr_fxs *fx, bool do_refresh)
{
	k_mutex_lock(&lk, K_FOREVER);
	load_view();
	if (do_refresh) {
		rscr_refresh(&s, &view, now_ms(), fx);
	}
	k_mutex_unlock(&lk);
	apply_fx(fx);
	wake_thread();
}

/* The core fact screen_on is read from here by the glue before every core call, under the glue's lock: there is no stored
 * copy that an older value could overwrite (design: finding 6 of the step 4 review). */
bool rscr_lock_fact_now(void)
{
	bool f;

	if (!started || forced_down) {
		return true;
	}
	k_mutex_lock(&lk, K_FOREVER);
	f = rscr_lock_fact(&s);
	k_mutex_unlock(&lk);
	return f;
}

void rscr_on_passkey(uint8_t slot, uint32_t passkey)
{
	k_mutex_lock(&lk, K_FOREVER);
	rscr_dev_passkey(&s, slot, passkey);
	k_mutex_unlock(&lk);
	wake_thread();
}

void rscr_on_paired(uint8_t slot)
{
	k_mutex_lock(&lk, K_FOREVER);
	load_view();
	/* ring_devices makes the new device active only when none was; the screens change nothing in the devices */
	rscr_dev_paired(&s, &view, slot, now_ms());
	k_mutex_unlock(&lk);
	wake_thread();
}

void rscr_on_window_closed(void)
{
	k_mutex_lock(&lk, K_FOREVER);
	rscr_dev_window_closed(&s, now_ms());
	k_mutex_unlock(&lk);
	wake_thread();
}

void rscr_on_removed(uint8_t slot)
{
	struct rscr_fxs fx = { 0 };
	bool was_active;

	k_mutex_lock(&lk, K_FOREVER);
	was_active = view.active_slot == slot;
	load_view();
	rscr_dev_removed(&s, &view, slot, was_active, now_ms(), &fx);
	k_mutex_unlock(&lk);
	apply_fx(&fx);
	wake_thread();
}

void rscr_on_active_changed(uint8_t slot)
{
	ARG_UNUSED(slot);
	rscr_poke();
}

void rscr_poke(void)
{
	struct rscr_fxs fx = { 0 };

	if (started) {
		after_async(&fx, true);
	}
}

void rscr_set_battery(uint8_t pct, bool charging, bool full, uint16_t to_full_min)
{
	k_mutex_lock(&lk, K_FOREVER);
	batt_pct = pct;
	batt_charging = charging;
	batt_full = full;
	batt_to_full = to_full_min;
	k_mutex_unlock(&lk);
	wake_thread();
}

void rscr_set_device_name(uint8_t slot, const char *name)
{
	k_mutex_lock(&lk, K_FOREVER);
	if (slot < RDEV_SLOTS) {
		memset(dev_names[slot], 0, sizeof(dev_names[slot]));
		if (name != NULL) {
			strncpy(dev_names[slot], name, 16);
		}
	}
	k_mutex_unlock(&lk);
	wake_thread();
}

void rscr_ilim_active(void)
{
	if (!started || forced_down) {
		return;
	}
	k_mutex_lock(&lk, K_FOREVER);
	load_view();
	rscr_ilim(&s, &view, now_ms());
	k_mutex_unlock(&lk);
	wake_thread();
}

int rscr_factory_frame(enum rscr_fac_frame f)
{
	bool ok;

	if (!started || forced_down) {
		return -ENODEV;
	}
	k_mutex_lock(&lk, K_FOREVER);
	load_view();
	ok = rscr_fac_frame(&s, &view, f, now_ms());
	k_mutex_unlock(&lk);
	wake_thread();
	return ok ? 0 : -EPERM;
}

void rscr_snapshot(struct rscr *out)
{
	k_mutex_lock(&lk, K_FOREVER);
	*out = s;
	k_mutex_unlock(&lk);
}

void rscr_stats_get(struct rscr_stats *st)
{
	*st = stats;
}

/* ---- drawing ---- */

static void fill_frame(rc_ms_t now)
{
	int64_t utc;
	int tz;

	k_mutex_lock(&lk, K_FOREVER);
	frame.s = s;
	frame.v = view;
	frame.batt_pct = batt_pct;
	frame.charging = batt_charging;
	frame.full = batt_full;
	frame.to_full_min = batt_to_full;
	memcpy(frame.dev_name, dev_names, sizeof(dev_names));
	k_mutex_unlock(&lk);
	frame.now = now;
	frame.time_set = rtime_is_set();
	frame.hh = frame.mm = 0;
	if (frame.time_set) {
		utc = rtime_utc_ms();
		tz = rtime_zone_known() ? rtime_tz_min() : 0;
		int64_t local_min = utc / 60000 + tz;
		int64_t dm = ((local_min % 1440) + 1440) % 1440;

		frame.hh = (uint8_t)(dm / 60);
		frame.mm = (uint8_t)(dm % 60);
	}
	frame.elapsed_s = frame.v.core_state == RC_ST_RECORDING ? (uint32_t)((now - frame.s.rec_start) / 1000) : 0;
	ops->media_get(&frame.media);
	frame.ams_ready = ops->ams_ready();
	for (uint8_t i = 0; i < frame.v.inbox_n; i++) {
		if (!ops->inbox_get(i, &frame.inbox[i])) {
			memset(&frame.inbox[i], 0, sizeof(frame.inbox[i]));
		}
	}
	frame.err_code = frame.v.core_state;
}

static int render_locked(rc_ms_t now)
{
	int rc = 0;
	uint8_t level;
	bool want_on;

	fill_frame(now);
	want_on = frame.s.screen != SCR_OFF;
	level = rscr_brightness_level(&frame.s);
	if (want_on) {
		rc = rscr_draw(&frame);
		stats.draws++;
		if (rc != 0) {
			stats.draw_errors++;
		}
		if (frame.v.core_state == RC_ST_RECORDING && !rscr_has_sign(&frame.s, RC_ST_RECORDING)) {
			stats.sign_missing++;
		}
	}
	if (want_on != panel_on_state || level != panel_level) {
		int e = rscr_panel(want_on, level);

		if (e != 0 && rc == 0) {
			rc = e;
		}
		panel_on_state = want_on;
		panel_level = level;
	}
	return rc;
}

static int render(rc_ms_t now)
{
	int rc;

	k_mutex_lock(&draw_lk, K_FOREVER);
	rc = render_locked(now);
	k_mutex_unlock(&draw_lk);
	return rc;
}

void rscr_draw_lock(void)
{
	k_mutex_lock(&draw_lk, K_FOREVER);
}

void rscr_draw_unlock(void)
{
	k_mutex_unlock(&draw_lk);
}

int rscr_test_sign_start_from_thread(void)
{
	sign_from_thread_rc = 1;
	sign_from_thread_req = true;
	rscr_sync();
	return sign_from_thread_rc;
}

void rscr_test_force_down(bool down)
{
	forced_down = down;
}

/* Runs on the screens thread: the one place that draws. A request is worked on only while its caller still waits for it:
 * the check is made with the draw lock and the screens lock held, and the state change and the draw follow under the same
 * locks, so a caller that gave up (timeout) cannot have its request drawn later, and an answer goes only to its own request. */
static void do_sign_start(void)
{
	struct rmd_stats a, b;
	uint32_t id;
	rc_ms_t now;
	int rc;

	k_mutex_lock(&lk, K_FOREVER);
	id = sign_req.seq;
	sign_req.claimed = id;
	sign_req.pending = false;
	k_mutex_unlock(&lk);
	k_mutex_lock(&draw_lk, K_FOREVER);   /* lock order: draw lock, then screens lock (as in render) */
	k_mutex_lock(&lk, K_FOREVER);
	if (sign_req.waiting != id) {
		/* the caller gave up while this thread waited for the draw lock: nothing is changed, nothing is drawn */
		k_mutex_unlock(&lk);
		k_mutex_unlock(&draw_lk);
		return;
	}
	now = sign_req.now;
	s.screen = SCR_RECORDING;
	s.rec_start = now;
	s.highlights = 0;
	s.dim_at = now + RSCR_DIM_MS;
	s.off_at = RC_NO_TICK;
	rmd_stats_get(&a);
	/* never trust the cached panel state here: switch the panel on again */
	panel_on_state = false;
	panel_level = 0xFF;
	rc = render_locked(now);
	rmd_stats_get(&b);
	if (rc == 0 && (b.refused != a.refused || b.blanked || b.writes == a.writes)) {
		rc = -EIO;
	}
	sign_req.result = rc;
	sign_req.waiting = 0;   /* answered */
	k_sem_give(&sign_done);
	k_mutex_unlock(&lk);
	k_mutex_unlock(&draw_lk);
}

k_tid_t rscr_thread_id(void)
{
	return &rscr_thread_data;
}

/* R-SIGN, the one path that starts the recording sign: the screens thread draws, the caller waits for the answer (calling
 * rules: rscr.h). Every request has a number; a timeout cancels the request, so the thread never draws it later and the next
 * call is never given an old answer. */
int rscr_sign_start(rc_ms_t now)
{
	uint32_t id;
	int rc;

	if (!started || forced_down) {
		return -ENODEV;
	}
	if (k_current_get() == rscr_thread_id()) {
		return -EDEADLK;   /* on the screens thread: it would wait for itself */
	}
	k_mutex_lock(&sign_lk, K_FOREVER);
	k_mutex_lock(&lk, K_FOREVER);
	id = ++sign_req.seq;
	sign_req.waiting = id;
	sign_req.now = now;
	sign_req.result = -EIO;
	sign_req.pending = true;
	k_sem_reset(&sign_done);
	k_mutex_unlock(&lk);
	wake_thread();
	if (k_sem_take(&sign_done, K_MSEC(CONFIG_RING_SCREENS_SIGN_WAIT_MS)) == 0) {
		rc = sign_req.result;
	} else {
		/* timeout: cancel the request. When the thread answered in the meantime (it holds the screens lock while it draws),
		 * its answer counts. */
		k_mutex_lock(&lk, K_FOREVER);
		if (sign_req.waiting == id) {
			sign_req.waiting = 0;
			sign_req.pending = false;
			rc = -ETIMEDOUT;
		} else {
			rc = sign_req.result;
		}
		k_mutex_unlock(&lk);
	}
	k_mutex_unlock(&sign_lk);
	return rc;
}

static void screens_thread(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);
	for (;;) {
		struct rscr_fxs fx = { 0 };
		k_timeout_t to = K_MSEC(1000);
		rc_ms_t nt, now;
		uint32_t want;
		bool sign;

		k_mutex_lock(&lk, K_FOREVER);
		nt = rscr_next_tick(&s);
		k_mutex_unlock(&lk);
		now = now_ms();
		if (nt != RC_NO_TICK && nt - now < 1000) {
			to = nt > now ? K_MSEC(nt - now) : K_NO_WAIT;
		}
		if (atomic_get(&power_off_pending) != 0) {
			to = K_MSEC(10);   /* a power off waits for the glue to be free */
		}
		(void)k_sem_take(&kick, to);
		want = gen_asked;
		now = now_ms();
		k_mutex_lock(&lk, K_FOREVER);
		sign = sign_req.pending;
		k_mutex_unlock(&lk);
		if (sign) {
			do_sign_start();
		}
		if (sign_from_thread_req) {
			sign_from_thread_rc = rscr_sign_start(now_ms());   /* on this thread: -EDEADLK at once */
			sign_from_thread_req = false;
		}
		k_mutex_lock(&lk, K_FOREVER);
		load_view();
		rscr_tick(&s, &view, now, &fx);
		/* what other modules hold may have changed (the iPhone removed a notification, a device went): the inbox
		 * and the device list send no event to this module, so each pass looks again */
		rscr_refresh(&s, &view, now, &fx);
		k_mutex_unlock(&lk);
		apply_fx(&fx);
		(void)render(now);
		if (atomic_get(&power_off_pending) != 0 && ops->power_off() == 0) {
			atomic_set(&power_off_pending, 0);   /* -EBUSY (the glue is busy): tried again on the next pass, 10 ms later */
		}
		gen_done = want;
		k_sem_give(&synced);
	}
}

void rscr_sync(void)
{
	uint32_t want = ++gen_asked;

	wake_thread();
	while ((int32_t)(gen_done - want) < 0) {
		(void)k_sem_take(&synced, K_MSEC(200));
	}
}

int rscr_start(const struct rscr_ops *o)
{
	int rc;

	if (started) {
		return -EALREADY;
	}
	ops = o;
	rscr_init(&s);
	memset(&view, 0, sizeof(view));
	view.core_state = RC_ST_STANDBY;
	view.active_slot = RDEV_NONE;
	rc = rscr_draw_init();
	if (rc != 0) {
		return rc;
	}
	started = true;
	(void)k_thread_create(&rscr_thread_data, rscr_stack, K_THREAD_STACK_SIZEOF(rscr_stack), screens_thread, NULL,
			      NULL, NULL, K_PRIO_PREEMPT(9), 0, K_NO_WAIT);
	k_thread_name_set(&rscr_thread_data, "screens");
	return 0;
}
