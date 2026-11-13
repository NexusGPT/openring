/*
 * rpw.c: the thin part of ring_power (software step 6, unit U5). The sampling timer per state, the gauge, the power
 * chip calls and the VBUS and charge-error callbacks. Hardware only through ring_rhw's rhw.h (rhw_pmic(),
 * rhw_gauge(), rhw_clock()); every decision is in rpw_logic.c. "FW l.N" = line N of design/firmware.md.
 *
 * One power thread takes the events (sample tick, VBUS, charge error) from a queue, so the driver callbacks and the
 * timer never block and the callbacks of struct rpw_cb run in that thread.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/spinlock.h>
#include <zephyr/sys/atomic.h>

#include <ring_core/rc_types.h>
#include <ring_power/rpw.h>
#include <ring_rhw/rhw.h>

#include "rpw_logic.h"
#include "rpw_priv.h"

enum ev_type {
	EV_SAMPLE,
	EV_VBUS,
	EV_CHGERR,
	EV_START,                    /* the callbacks of rpw_start(): VBUS now, the first level */
	EV_READ,                     /* addition of the join: a read now for rpw_sample_now / rpw_charger_now */
};

struct ev {
	uint8_t type;
	bool flag;
	uint32_t gen;                /* the start generation that posted it: an event of an older one is dropped */
};

K_MSGQ_DEFINE(ev_q, sizeof(struct ev), 16, 4);
K_MUTEX_DEFINE(proc_lock);           /* held by the power thread while it handles one event */
K_MUTEX_DEFINE(chg_lock);            /* the charger writes of "charge on" and "charge off" */
static K_THREAD_STACK_DEFINE(thr_stack, CONFIG_RING_POWER_STACK_SIZE);
static struct k_thread thr;
static bool thr_up;
static struct k_timer tick;
static bool tick_ready;
static struct k_sem vbus_gone;
static struct k_spinlock slock;      /* cur_state, cur_period, vals, charge_last */

/* guarded by proc_lock (the power thread and rpw_start) */
static struct rpw_cb cb;
static bool started;
static struct rpwl_judge judge;
static struct rpwl_ilim ilim;
static int64_t last_step_ms;
static bool start_vbus;              /* VBUS was present at rpw_start: cb.vbus(true) goes out from the power thread */
static bool start_level_report;
static uint8_t start_level;
static uint16_t start_soc, start_mean, start_mv;
static int start_ilim = -1;
static uint8_t start_state;
static int64_t start_now;        /* the current limit status read with the first sample */

/* guarded by slock */
static uint8_t cur_state = RC_ST_BOOT;
static uint32_t cur_period;
static struct rpw_values vals;
static struct rhw_pmic_charge charge_last;
static uint32_t ttf_s_last = UINT32_MAX;

/* guarded by chg_lock */
static bool chg_on;

static atomic_t motor_q;             /* µA·s since the last sample */
static atomic_t gen;                 /* counts rpw_start() and the test reset */
static atomic_t shipping;

/* ------------------------------------------------------------------ helpers */
static void put_le16(uint8_t *p, uint16_t v)
{
	p[0] = (uint8_t)(v & 0xFFu);
	p[1] = (uint8_t)(v >> 8);
}

static void put_le32(uint8_t *p, uint32_t v)
{
	put_le16(p, (uint16_t)(v & 0xFFFFu));
	put_le16(p + 2, (uint16_t)(v >> 16));
}

static void log_rec(uint16_t code, const uint8_t *args, size_t n)
{
	if (cb.log != NULL) {
		cb.log(code, args, n);
	}
}

/* Apply the sampling period of the state now held (timer). Caller holds slock. */
static void period_apply_locked(bool force)
{
	uint32_t p = started ? rpwl_period_ms(cur_state) : 0;

	if (!tick_ready) {
		return;
	}
	if (atomic_get(&shipping) != 0) {
		p = 0;
	}
	if (p == cur_period && !force) {
		return;
	}
	cur_period = p;
	if (p == 0) {
		k_timer_stop(&tick);
	} else {
		k_timer_start(&tick, K_MSEC(p), K_MSEC(p));
	}
}

static void tick_fn(struct k_timer *t)
{
	struct ev e = { .type = EV_SAMPLE, .flag = false, .gen = (uint32_t)atomic_get(&gen) };

	ARG_UNUSED(t);
	(void)k_msgq_put(&ev_q, &e, K_NO_WAIT);
}

static void pmic_vbus_cb(bool present)
{
	struct ev e = { .type = EV_VBUS, .flag = present, .gen = (uint32_t)atomic_get(&gen) };

	(void)k_msgq_put(&ev_q, &e, K_NO_WAIT);
}

static void pmic_chgerr_cb(void)
{
	struct ev e = { .type = EV_CHGERR, .flag = false, .gen = (uint32_t)atomic_get(&gen) };

	(void)k_msgq_put(&ev_q, &e, K_NO_WAIT);
}

static const struct rhw_pmic_cb pmic_cb = { .vbus = pmic_vbus_cb, .charge_error = pmic_chgerr_cb };

/* ------------------------------------------------------------------ charger (FW l.129, l.894) */
int rpw_charge_on(void)
{
	int r = 0;

	k_mutex_lock(&chg_lock, K_FOREVER);
	if (rpwl_charge_on_needed(chg_on)) {
		for (uint8_t i = 0; i < RPWL_CHG_STEPS && r == 0; i++) {
			switch (rpwl_charge_step(i)) {
			case RPWL_CHG_DISABLE:
				r = rhw_pmic()->charger_enable(false);
				break;
			case RPWL_CHG_CURRENT:
				r = rhw_pmic()->charger_current(rpwl_charge_current_ua());
				break;
			case RPWL_CHG_ENABLE:
				r = rhw_pmic()->charger_enable(true);
				break;
			default:
				break;
			}
		}
		chg_on = (r == 0);
	}
	k_mutex_unlock(&chg_lock);
	return r;
}

int rpw_charge_off(void)
{
	int r;

	k_mutex_lock(&chg_lock, K_FOREVER);
	r = rhw_pmic()->charger_enable(false);
	chg_on = false;
	k_mutex_unlock(&chg_lock);
	return r;
}

uint32_t rpw_charge_current_ua(void)
{
	return rpwl_charge_current_ua();
}

/* ------------------------------------------------------------------ the motor's charge (FW l.927) */
void rpw_motor_charge(uint32_t uas)
{
	(void)atomic_add(&motor_q, (atomic_val_t)uas);
}

/* ------------------------------------------------------------------ one sample (power thread, proc_lock held) */
static void report_level(uint8_t level, uint16_t soc_x10, uint16_t mean_mv)
{
	uint8_t a[5];

	a[0] = level;
	put_le16(&a[1], soc_x10);
	put_le16(&a[3], mean_mv);
	log_rec(RREC_LOG_BATTERY, a, sizeof(a));
	if (cb.level != NULL) {
		cb.level(level);
	}
}

static void refresh_charge(void)
{
	struct rhw_pmic_charge ch;

	if (rhw_pmic()->charge_status(&ch) == 0) {
		K_SPINLOCK(&slock) {
			charge_last = ch;
		}
	}
}

static void values_set(const struct rhw_pmic_sample *s, uint16_t soc_x10, uint32_t ttf_s, uint8_t level)
{
	K_SPINLOCK(&slock) {
		vals.battery_mv = s->mv;
		vals.soc_x10 = soc_x10;
		vals.die_c_x10 = s->die_c_x10;
		vals.level = level;
		ttf_s_last = ttf_s;
		vals.to_full_min = rpwl_ttf_min(ttf_s);
		vals.charging = charge_last.state == RREC_CHG_TRICKLE || charge_last.state == RREC_CHG_CC ||
				charge_last.state == RREC_CHG_CV;
		vals.full = charge_last.state == RREC_CHG_FULL;
	}
}

/* One gauge step with the motor's charge added; returns the gauge's output or keeps the last state of charge. */
static int gauge_step(const struct rhw_pmic_sample *s, uint32_t dt_ms, struct rhw_gauge_out *g)
{
	struct rhw_pmic_sample fed = *s;
	uint32_t q = 0;
	int r;

	if (dt_ms > 0) {
		q = (uint32_t)atomic_set(&motor_q, 0);
	}
	fed.ua = rpwl_fed_ua(s->ua, q, dt_ms);
	r = rhw_gauge()->process(&fed, dt_ms, g);
	if (r != 0 && q > 0) {
		(void)atomic_add(&motor_q, (atomic_val_t)q);    /* the charge is not lost when the gauge failed */
	}
	return r;
}

/* The current limit status of one sample (a < 0: the read failed, nothing is decided). FW l.990 to l.995. */
static void ilim_handle(int a, uint16_t mv, uint8_t state, int64_t now)
{
	uint32_t count = 0;
	enum rpwl_ilim_act act;

	if (a < 0) {
		return;
	}
	act = rpwl_ilim_step(&ilim, a == 1, (uint32_t)now, &count);
	if (act != RPWL_ILIM_NONE) {
		uint8_t args[8];
		bool first = act == RPWL_ILIM_FIRST;

		put_le16(&args[0], mv);
		args[2] = state;
		args[3] = first ? 1u : 0u;      /* the screen was on at the first reading, off at the later ones */
		put_le32(&args[4], count);
		log_rec(RREC_LOG_ILIM_ACTIVE, args, sizeof(args));
		if (cb.ilim != NULL) {
			cb.ilim(first, mv, count);
		}
	}
}

static void do_sample(void)
{
	struct rhw_pmic_sample s;
	struct rhw_gauge_out g;
	uint8_t state = RC_ST_BOOT;
	bool changed = false;
	uint16_t mean = 0, soc = 0;
	uint32_t ttf = UINT32_MAX;
	uint8_t level;
	int64_t now;

	if (rhw_pmic()->sample(&s) != 0) {
		return;
	}
	now = rhw_clock()->now_ms();
	K_SPINLOCK(&slock) {
		state = cur_state;
		soc = vals.soc_x10;
		ttf = ttf_s_last;
	}
	if (gauge_step(&s, (uint32_t)(now - last_step_ms), &g) == 0) {
		soc = g.soc_x10;
		ttf = g.ttf_s;
	}
	last_step_ms = now;
	refresh_charge();
	level = rpwl_judge_sample(&judge, soc, s.mv, rpwl_is_recording(state), &mean, &changed);
	values_set(&s, soc, ttf, level);
	if (changed) {
		report_level(level, soc, mean);
	}

	/* every sample also reads the current limit status (FW l.928, l.990) */
	ilim_handle(rhw_pmic()->ilim_active(), s.mv, state, now);
}

static void do_vbus(bool present)
{
	if (present) {
		(void)rpw_charge_on();                  /* R-CHG, ruling R8: at every appearance, in every state */
		K_SPINLOCK(&slock) {
			vals.vbus = true;
		}
		if (cb.vbus != NULL) {
			cb.vbus(true);
		}
	} else {
		k_mutex_lock(&chg_lock, K_FOREVER);
		chg_on = false;                         /* the next appearance writes "charge on" again */
		k_mutex_unlock(&chg_lock);
		K_SPINLOCK(&slock) {
			vals.vbus = false;
		}
		k_sem_give(&vbus_gone);
		if (cb.vbus != NULL) {
			cb.vbus(false);
		}
	}
}

static void do_chgerr(void)
{
	struct rhw_pmic_charge ch;

	if (rhw_pmic()->charge_status(&ch) != 0) {
		return;
	}
	K_SPINLOCK(&slock) {
		charge_last = ch;
	}
	if (cb.charge_error != NULL) {
		cb.charge_error(ch.err_reason, ch.err_sensor);
	}
}

/* ------------------------------------------------------------------ addition of the join: reads now (factory tests) */
K_MUTEX_DEFINE(rd_lock);             /* one read at a time */
K_SEM_DEFINE(rd_done, 0, 1);
static struct {
	int rc;
	struct rhw_pmic_sample s;
	struct rhw_pmic_charge ch;
} rd;

/* power thread: one sample and the charger status, for the caller waiting in read_now() */
static void do_read(void)
{
	rd.rc = rhw_pmic()->sample(&rd.s);
	if (rd.rc == 0) {
		rd.rc = rhw_pmic()->charge_status(&rd.ch);
	}
	k_sem_give(&rd_done);
}

static int read_now(void)
{
	struct ev e = { .type = EV_READ, .flag = false, .gen = (uint32_t)atomic_get(&gen) };
	int r;

	if (thr_up && k_current_get() == &thr) {
		return -EDEADLK;
	}
	k_mutex_lock(&rd_lock, K_FOREVER);
	k_sem_reset(&rd_done);
	if (k_msgq_put(&ev_q, &e, K_NO_WAIT) != 0) {
		r = -EBUSY;
	} else if (k_sem_take(&rd_done, K_MSEC(RPW_READ_WAIT_MS)) != 0) {
		r = -ETIMEDOUT;
	} else {
		r = rd.rc;
	}
	k_mutex_unlock(&rd_lock);
	return r;
}

int rpw_sample_now(uint16_t *mv, int32_t *ua)
{
	int r = read_now();

	if (r == 0) {
		*mv = rd.s.mv;
		*ua = rd.s.ua;
	}
	return r;
}

int rpw_charger_now(uint8_t *state, uint8_t *err_reason, int32_t *ua)
{
	int r = read_now();

	if (r == 0) {
		*state = rd.ch.state;
		*err_reason = rd.ch.err_reason;
		*ua = rd.s.ua;
	}
	return r;
}

static void thread_fn(void *a, void *b, void *c)
{
	struct ev e;

	ARG_UNUSED(a);
	ARG_UNUSED(b);
	ARG_UNUSED(c);
	for (;;) {
		(void)k_msgq_get(&ev_q, &e, K_FOREVER);
		k_mutex_lock(&proc_lock, K_FOREVER);
		if (started && e.gen == (uint32_t)atomic_get(&gen)) {
			switch (e.type) {
			case EV_SAMPLE:
				if (atomic_get(&shipping) == 0) {
					do_sample();
				}
				break;
			case EV_VBUS:
				do_vbus(e.flag);
				break;
			case EV_CHGERR:
				do_chgerr();
				break;
			case EV_READ:
				do_read();
				break;
			case EV_START:
				if (start_vbus && cb.vbus != NULL) {
					cb.vbus(true);
				}
				if (start_level_report) {
					report_level(start_level, start_soc, start_mean);
				}
				ilim_handle(start_ilim, start_mv, start_state, start_now);
				break;
			default:
				break;
			}
		}
		k_mutex_unlock(&proc_lock);
	}
}

static void thread_ensure(void)
{
	if (thr_up) {
		return;
	}
	k_timer_init(&tick, tick_fn, NULL);
	k_sem_init(&vbus_gone, 0, K_SEM_MAX_LIMIT);
	tick_ready = true;
	k_thread_create(&thr, thr_stack, K_THREAD_STACK_SIZEOF(thr_stack), thread_fn, NULL, NULL, NULL,
			CONFIG_RING_POWER_PRIORITY, 0, K_NO_WAIT);
	k_thread_name_set(&thr, "rpw");
	thr_up = true;
}

/* ------------------------------------------------------------------ start (FW l.893, l.926) */
static void forget_locked(bool reset_state)
{
	(void)atomic_inc(&gen);
	started = false;
	K_SPINLOCK(&slock) {
		if (reset_state) {
			cur_state = RC_ST_BOOT;
		}
		cur_period = 0;
		memset(&vals, 0, sizeof(vals));
		vals.to_full_min = UINT16_MAX;
		memset(&charge_last, 0, sizeof(charge_last));
		ttf_s_last = UINT32_MAX;
	}
	if (tick_ready) {
		k_timer_stop(&tick);
		k_sem_reset(&vbus_gone);
	}
	k_msgq_purge(&ev_q);
	memset(&cb, 0, sizeof(cb));
	rpwl_judge_reset(&judge);
	rpwl_ilim_reset(&ilim);
	(void)atomic_set(&motor_q, 0);
	(void)atomic_set(&shipping, 0);
	k_mutex_lock(&chg_lock, K_FOREVER);
	chg_on = false;
	k_mutex_unlock(&chg_lock);
	start_vbus = false;
	start_level_report = false;
	start_ilim = -1;
}

int rpw_start(const struct rpw_cb *c)
{
	struct rhw_pmic_sample s;
	struct rhw_gauge_out g;
	bool changed = false;
	uint16_t mean = 0;
	uint8_t level;
	int r;

	if (c == NULL) {
		return -EINVAL;
	}
	thread_ensure();
	k_mutex_lock(&proc_lock, K_FOREVER);
	forget_locked(false);
	cb = *c;
	rhw_pmic()->set_callbacks(&pmic_cb);

	r = rhw_pmic()->sample(&s);
	if (r == 0) {
		r = rhw_gauge()->start(&s);
	}
	if (r == 0) {
		r = rhw_gauge()->process(&s, 0, &g);       /* the first step: no time has passed */
	}
	if (r != 0) {
		rhw_pmic()->set_callbacks(NULL);
		memset(&cb, 0, sizeof(cb));
		k_mutex_unlock(&proc_lock);
		return r;
	}
	last_step_ms = rhw_clock()->now_ms();
	level = rpwl_judge_sample(&judge, g.soc_x10, s.mv, false, &mean, &changed);
	start_level_report = changed;
	start_level = level;
	start_soc = g.soc_x10;
	start_mean = mean;

	start_vbus = rhw_pmic()->vbus_present();
	if (start_vbus) {
		(void)rpw_charge_on();                      /* FW l.893: before storage is mounted */
		K_SPINLOCK(&slock) {
			vals.vbus = true;
		}
	}
	refresh_charge();
	values_set(&s, g.soc_x10, g.ttf_s, level);
	start_ilim = rhw_pmic()->ilim_active();      /* every sample also reads the current limit status (FW l.928) */
	start_mv = s.mv;
	start_now = last_step_ms;
	K_SPINLOCK(&slock) {
		start_state = cur_state;
	}
	started = true;
	K_SPINLOCK(&slock) {
		period_apply_locked(true);
	}
	{
		struct ev e = { .type = EV_START, .flag = false, .gen = (uint32_t)atomic_get(&gen) };

		(void)k_msgq_put(&ev_q, &e, K_NO_WAIT);
	}
	k_mutex_unlock(&proc_lock);
	return 0;
}

void rpw_state(uint8_t rc_state)
{
	if (!rpwl_state_valid(rc_state)) {
		return;
	}
	K_SPINLOCK(&slock) {
		cur_state = rc_state;
		period_apply_locked(false);
	}
}

/* ------------------------------------------------------------------ boot causes (FW l.996) */
int rpw_boot_causes(rrec_log_fn log)
{
	uint8_t rc = 0, er = 0, es = 0;
	uint8_t args[RPWL_CAUSE_ARGS];
	int r = rhw_pmic()->reset_causes(&rc, &er, &es);

	if (r != 0) {
		return r;
	}
	rpwl_cause_args(rc, er, es, args);
	if (log != NULL) {
		log(RREC_LOG_PMIC_RESET, args, sizeof(args));
	}
	r = rhw_pmic()->reset_causes_clear();
	return r;
}

/* ------------------------------------------------------------------ ship mode (FW l.936 to l.941) */
int rpw_ship(void (*before_task)(void))
{
	struct rpwl_ship ss;
	int result = 0;

	rpwl_ship_reset(&ss);
	(void)atomic_set(&shipping, 1);             /* "doing nothing else": no sampling while this runs */
	K_SPINLOCK(&slock) {
		period_apply_locked(true);
	}
	k_sem_reset(&vbus_gone);
	for (;;) {
		switch (rpwl_ship_next(&ss, rhw_pmic()->vbus_present())) {
		case RPWL_SHIP_CONFIG:
			(void)rhw_pmic()->shphld_config(RREC_SHPHLD_MS);
			break;
		case RPWL_SHIP_STROBE:
			(void)rhw_pmic()->shphld_strobe();
			break;
		case RPWL_SHIP_WAIT_VBUS:
			(void)k_sem_take(&vbus_gone, K_MSEC(50));
			break;
		case RPWL_SHIP_BEFORE_TASK:
			if (before_task != NULL) {
				before_task();
			}
			break;
		case RPWL_SHIP_TASK:
			(void)rhw_pmic()->ship_task();
			break;
		case RPWL_SHIP_WAIT_1S:
			k_sleep(K_MSEC(RREC_SHIP_RETRY_MS));
			break;
		case RPWL_SHIP_LOG_RETRY: {
			uint8_t n_try = 1;

			if (cb.log != NULL) {
				cb.log(RREC_LOG_SHIP_RETRY, &n_try, 1);
			}
			break;
		}
		case RPWL_SHIP_GIVE_UP:
		default:
			result = -ETIMEDOUT;
			goto out;
		}
	}
out:
	(void)atomic_set(&shipping, 0);
	K_SPINLOCK(&slock) {
		period_apply_locked(true);
	}
	return result;
}

/* ------------------------------------------------------------------ reports (FW l.374, l.702) */
void rpw_values(struct rpw_values *out)
{
	K_SPINLOCK(&slock) {
		*out = vals;
	}
}

int rpw_battery_report(uint8_t out[RREC_GET_BATTERY_BYTES])
{
	struct rhw_pmic_charge ch;
	struct rpw_values v;
	int r;

	if (!started) {
		return -EAGAIN;
	}
	r = rhw_pmic()->charge_status(&ch);
	if (r != 0) {
		return r;
	}
	K_SPINLOCK(&slock) {
		charge_last = ch;
		v = vals;
	}
	rpwl_battery_bytes(v.battery_mv, v.soc_x10, rpwl_charge_code(ch.state, ch.err_reason), v.die_c_x10,
			   v.to_full_min, out);
	return 0;
}

/* ------------------------------------------------------------------ test control (rpw_priv.h) */
void rpw_priv_reset(void)
{
	k_mutex_lock(&proc_lock, K_FOREVER);
	forget_locked(true);
	if (tick_ready) {
		rhw_pmic()->set_callbacks(NULL);
	}
	k_mutex_unlock(&proc_lock);
}

unsigned int rpw_priv_period_ms(void)
{
	unsigned int p = 0;

	K_SPINLOCK(&slock) {
		p = cur_period;
	}
	return p;
}
