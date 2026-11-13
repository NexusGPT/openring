/*
 * rfa.c: the thin part of the factory unit (software step 6, unit U8). Hardware only through rhw.h (the beacon, the
 * clock) and the other units' public headers (ring_store for T-STORE when the join does not supply its own); every
 * other test goes through struct rfa_ops. Never starts or stops a recording by a command (FW l.209, l.1027): the
 * test recordings of T-MIC and T-SIGN go through ops->test_recording (the join's rec_mics_on path, ruling R18).
 * "FW l.N" = line N of design/firmware.md.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/spinlock.h>

#include <ring_factory/rfa.h>
#include <ring_rhw/rhw.h>
#if defined(CONFIG_RING_STORE)
#include <ring_store/rst.h>
#endif

#include "rfa_logic.h"

static struct rfa_ops ops;
static bool ready;

#define MOTOR_STACK 2048
K_THREAD_STACK_DEFINE(motor_stack, MOTOR_STACK);
static struct k_work_q motor_q;
static struct k_work motor_work;
static K_SEM_DEFINE(motor_started, 0, 1);
static K_SEM_DEFINE(motor_done, 0, 1);
static int motor_rc;
static bool motor_q_ready;

static K_MUTEX_DEFINE(beacon_lock);
static bool beacon_on;

static struct k_spinlock in_lock;
static struct {
	bool armed;
	uint8_t sub;
	int64_t t0;
	uint8_t n;
	uint8_t dropped;
	struct rfa_evrec e[RFA_MAX_EVENTS];
} inp;

/* ------------------------------------------------------------------ the built-in T-STORE (ring_store) */
#if defined(CONFIG_RING_STORE)
static int builtin_store(bool *equal, uint32_t *write_us, uint32_t *read_us, uint32_t *deleted)
{
	struct rst_mount_info mi;
	struct rst_factory_result fr;
	bool mounted_here = false;
	int rc;

	if (!rst_mounted()) {
		rc = rst_mount(false, &mi);
		if (rc < 0) {
			return rc;
		}
		mounted_here = true;
	}
	rc = rst_factory_area_test(&fr);
	if (rc == 0) {
		*equal = fr.equal;
		*write_us = fr.write_us;
		*read_us = fr.read_us;
	}
	/* the last step of T-STORE (FW l.1030): every test recording (type 2) goes */
	int rc2 = rst_delete_factory_recordings(deleted);

	if (mounted_here) {
		(void)rst_unmount();
	}
	return rc != 0 ? rc : rc2;
}
#endif

/* ------------------------------------------------------------------ the beacon */
static int beacon_start(bool connectable)
{
	uint64_t id = 0;
	char name[RFA_NAME_BYTES];
	const struct rhw_beacon_api *b = rhw_beacon();
	int rc = rhw_clock()->device_id(&id);

	if (rc < 0) {
		return rc;
	}
	(void)rfa_beacon_name(id, name);
	k_mutex_lock(&beacon_lock, K_FOREVER);
	rc = b->start(name, RREC_ADV_INTERVAL_MS, RREC_ADV_TX_DBM, connectable);
	if (rc == 0) {
		beacon_on = true;
	}
	k_mutex_unlock(&beacon_lock);
	return rc;
}

static void beacon_stop_now(void)
{
	k_mutex_lock(&beacon_lock, K_FOREVER);
	if (beacon_on) {
		(void)rhw_beacon()->stop();
		beacon_on = false;
	}
	k_mutex_unlock(&beacon_lock);
}

int rfa_ship_begin(void)
{
	return beacon_start(false); /* ship */
}

void rfa_beacon_stop(void)
{
	beacon_stop_now();
}

/* ------------------------------------------------------------------ init */
int rfa_init(const struct rfa_ops *o)
{
	if (o == NULL) {
		return -EINVAL;
	}
	ops = *o;
#if defined(CONFIG_RING_STORE)
	if (ops.store_test == NULL) {
		ops.store_test = builtin_store;
	}
#endif
	if (!motor_q_ready) {
		k_work_queue_init(&motor_q);
		k_work_queue_start(&motor_q, motor_stack, K_THREAD_STACK_SIZEOF(motor_stack), 5, NULL);
		k_thread_name_set(&motor_q.thread, "rfa_motor");
		motor_q_ready = true;
	}
	ready = true;
	return 0;
}

/* ------------------------------------------------------------------ the joystick events */
void rfa_input(enum rfa_input ev, int64_t t_ms)
{
	k_spinlock_key_t k = k_spin_lock(&in_lock);

	if (inp.armed && rfa_event_wanted(inp.sub, (uint8_t)ev)) {
		if (inp.n < RFA_MAX_EVENTS) {
			int64_t rel = t_ms - inp.t0;

			inp.e[inp.n].ev = (uint8_t)ev;
			inp.e[inp.n].rel_ms = rel < 0 ? 0u : (uint32_t)rel;
			inp.n++;
		} else if (inp.dropped < UINT8_MAX) {
			inp.dropped++;
		}
	}
	k_spin_unlock(&in_lock, k);
	/* the events end here: they reach the jig only, never a recording */
}

static size_t run_events(const struct rfa_cmd *c, uint8_t *out)
{
	k_spinlock_key_t k = k_spin_lock(&in_lock);

	inp.sub = c->sub;
	inp.t0 = rhw_clock()->now_ms();
	inp.n = 0;
	inp.dropped = 0;
	inp.armed = true;
	k_spin_unlock(&in_lock, k);

	k_sleep(K_MSEC(c->window_ms));

	k = k_spin_lock(&in_lock);
	inp.armed = false;
	uint8_t n = inp.n;
	uint8_t dropped = inp.dropped;
	struct rfa_evrec e[RFA_MAX_EVENTS];

	memcpy(e, inp.e, sizeof(e));
	k_spin_unlock(&in_lock, k);
	return rfa_put_events(out, n == 0 ? RREC_FAC_RESULT_TIMEOUT : RREC_FAC_RESULT_PASS, dropped, e, n);
}

/* ------------------------------------------------------------------ T-MIC */
static struct rfa_level mic_level[2];
static struct rfa_run mic_run[2];
static uint32_t mic_frames;

static void mic_block(const int16_t *frames, uint32_t n)
{
	for (uint32_t ch = 0; ch < 2; ch++) {
		rfa_level_add(&mic_level[ch], frames, n, ch);
		rfa_run_add(&mic_run[ch], frames, n, ch);
	}
	mic_frames += n;
}

static uint8_t result_of_rc(int rc)
{
	return rc == -ETIMEDOUT ? RREC_FAC_RESULT_TIMEOUT : RREC_FAC_RESULT_FAIL;
}

static size_t run_mic(uint8_t *out)
{
	int64_t on = 0;
	int64_t off = 0;
	int rc;

	memset(mic_level, 0, sizeof(mic_level));
	memset(mic_run, 0, sizeof(mic_run));
	mic_frames = 0;
	if (ops.test_recording == NULL) {
		return rfa_put_mic(out, RREC_FAC_RESULT_FAIL, RFA_DBFS_SILENT, RFA_DBFS_SILENT, 0, 0);
	}
	/* mic path: the test recording only (rec_mics_on after the sign, R18) */
	rc = ops.test_recording(RREC_FAC_MIC_REC_MS, mic_block, &on, &off);
	if (rc != 0 || mic_frames == 0) {
		/* no sign, no test (-ENODEV), or the recording failed: nothing was measured */
		return rfa_put_mic(out, result_of_rc(rc), RFA_DBFS_SILENT, RFA_DBFS_SILENT, 0, 0);
	}
	uint8_t res = (rfa_run_is_stuck(mic_run[0].max) || rfa_run_is_stuck(mic_run[1].max)) ? RREC_FAC_RESULT_FAIL :
											      RREC_FAC_RESULT_PASS;

	return rfa_put_mic(out, res, rfa_level_dbfs_x10(&mic_level[0]), rfa_level_dbfs_x10(&mic_level[1]),
			   mic_run[0].max, mic_run[1].max);
}

/* ------------------------------------------------------------------ T-SIGN */
static void sign_block(const int16_t *frames, uint32_t n)
{
	ARG_UNUSED(frames);
	ARG_UNUSED(n);
}

static size_t run_sign(uint8_t *out)
{
	int64_t t[4] = { 0, 0, 0, 0 };
	uint8_t res = RREC_FAC_RESULT_PASS;

	if (ops.test_recording == NULL) {
		return rfa_put_sign(out, RREC_FAC_RESULT_FAIL, t);
	}
	for (int i = 0; i < 2; i++) {
		int rc = ops.test_recording(RREC_FAC_SIGN_REC_MS, sign_block, &t[2 * i], &t[2 * i + 1]);

		if (rc != 0) {
			res = result_of_rc(rc);
			break;
		}
		if (i == 0) {
			k_sleep(K_MSEC(RREC_FAC_SIGN_GAP_MS));
		}
	}
	return rfa_put_sign(out, res, t);
}

/* ------------------------------------------------------------------ T-SCREEN */
static size_t run_screen(uint8_t *out)
{
	if (ops.screen_frame == NULL) {
		return rfa_put_result(out, RREC_FAC_RESULT_FAIL);
	}
	/* red, green, blue, white, black (0 to 4), then the grid (5): 1 s each (FW l.1025) */
	for (uint8_t f = 0; f <= 5; f++) {
		int rc = ops.screen_frame(f);

		if (rc != 0) {
			return rfa_put_result(out, RREC_FAC_RESULT_FAIL);
		}
		k_sleep(K_MSEC(RFA_SCREEN_FRAME_MS));
	}
	return rfa_put_result(out, RREC_FAC_RESULT_PASS);
}

/* ------------------------------------------------------------------ T-MOTOR */
static void motor_work_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	k_sem_give(&motor_started);
	motor_rc = ops.motor_on(RREC_FAC_MOTOR_ON_MS);
	k_sem_give(&motor_done);
}

static size_t run_motor(uint8_t *out)
{
	uint16_t before = 0;
	uint16_t during = 0;

	if (ops.motor_on == NULL || ops.vbat_mv == NULL) {
		return rfa_put_motor(out, RREC_FAC_RESULT_FAIL, 0, 0, 0);
	}
	if (ops.vbat_mv(&before) != 0) { /* VBAT once before MOTOR goes high (FW l.1028) */
		return rfa_put_motor(out, RREC_FAC_RESULT_FAIL, 0, 0, 0);
	}
	k_sem_reset(&motor_started);
	k_sem_reset(&motor_done);
	motor_rc = 0;
	k_work_init(&motor_work, motor_work_fn);
	k_work_submit_to_queue(&motor_q, &motor_work);
	if (k_sem_take(&motor_started, K_SECONDS(1)) != 0) {
		return rfa_put_motor(out, RREC_FAC_RESULT_TIMEOUT, before, 0, 0);
	}
	k_sleep(K_MSEC(rfa_motor_read_delay_ms())); /* 250 ms into the pulse */
	int rc = ops.vbat_mv(&during);

	if (k_sem_take(&motor_done, K_MSEC(RREC_FAC_MOTOR_ON_MS + 1000u)) != 0) {
		return rfa_put_motor(out, RREC_FAC_RESULT_TIMEOUT, before, during, rfa_motor_dip_mv(before, during));
	}
	if (rc != 0 || motor_rc != 0) {
		return rfa_put_motor(out, RREC_FAC_RESULT_FAIL, before, during, 0);
	}
	return rfa_put_motor(out, RREC_FAC_RESULT_PASS, before, during, rfa_motor_dip_mv(before, during));
}

/* ------------------------------------------------------------------ T-STORE, T-RADIO, T-CHARGE, T-XTAL */
static size_t run_store(uint8_t *out)
{
	bool equal = false;
	uint32_t w = 0;
	uint32_t r = 0;
	uint32_t del = 0;
	int rc = ops.store_test != NULL ? ops.store_test(&equal, &w, &r, &del) : -ENOTSUP;

	if (rc != 0) {
		return rfa_put_store(out, result_of_rc(rc), false, 0, 0, del);
	}
	return rfa_put_store(out, equal ? RREC_FAC_RESULT_PASS : RREC_FAC_RESULT_FAIL, equal, w, r, del);
}

static size_t run_radio(uint8_t *out)
{
	int rc = beacon_start(false); /* radio */

	if (rc != 0) {
		return rfa_put_result(out, RREC_FAC_RESULT_FAIL);
	}
	k_sleep(K_MSEC(RREC_FAC_RADIO_MS));
	beacon_stop_now();
	return rfa_put_result(out, RREC_FAC_RESULT_PASS);
}

static size_t run_charge(uint8_t *out)
{
	uint8_t state = 0;
	uint8_t err = 0;
	int32_t ua = 0;

	if (ops.charge == NULL || ops.charge(&state, &err, &ua) != 0) {
		return rfa_put_charge(out, RREC_FAC_RESULT_FAIL, 0, 0, 0);
	}
	return rfa_put_charge(out, rfa_charge_result(state, err), state, err, ua);
}

static size_t run_xtal(uint8_t *out)
{
	uint64_t grtc = 0;
	uint32_t sof = 0;
	bool ok = false;

	if (ops.xtal_counts == NULL || ops.xtal_counts(&grtc, &sof) != 0) {
		return rfa_put_xtal(out, RREC_FAC_RESULT_FAIL, 0, 0, 0);
	}
	int32_t ppm = rfa_ppm_x10(grtc, sof, &ok);

	if (!ok) {
		return rfa_put_xtal(out, RREC_FAC_RESULT_FAIL, 0, grtc, sof);
	}
	return rfa_put_xtal(out, rfa_ppm_within(ppm) ? RREC_FAC_RESULT_PASS : RREC_FAC_RESULT_FAIL, ppm, grtc, sof);
}

/* ------------------------------------------------------------------ the request */
enum rrec_status rfa_request(const uint8_t *req, size_t len, bool in_factory_test, uint8_t *out, size_t *out_len,
			     enum rfa_effect *effect)
{
	struct rfa_cmd c;
	enum rfa_effect eff = RFA_EFFECT_NONE;
	size_t n = 0;
	bool flag = ready && ops.flag != NULL && ops.flag();
	enum rrec_status st = rfa_parse(req, len, flag, in_factory_test, &c);

	if (effect != NULL) {
		*effect = RFA_EFFECT_NONE;
	}
	if (out_len != NULL) {
		*out_len = 0;
	}
	if (st != RREC_ST_OK) {
		return st;
	}
	switch (c.sub) {
	case RREC_FAC_ENTER:
		eff = RFA_EFFECT_ENTER;
		n = rfa_put_result(out, RREC_FAC_RESULT_PASS);
		break;
	case RREC_FAC_EXIT:
		eff = RFA_EFFECT_EXIT;
		n = rfa_put_result(out, RREC_FAC_RESULT_PASS);
		break;
	case RREC_FAC_MIC:
		n = run_mic(out);
		break;
	case RREC_FAC_SCREEN:
		n = run_screen(out);
		break;
	case RREC_FAC_JOY:
	case RREC_FAC_CENTRE:
		n = run_events(&c, out);
		break;
	case RREC_FAC_MOTOR:
		n = run_motor(out);
		break;
	case RREC_FAC_SIGN:
		n = run_sign(out);
		break;
	case RREC_FAC_STORE:
		n = run_store(out);
		break;
	case RREC_FAC_RADIO:
		n = run_radio(out);
		break;
	case RREC_FAC_CHARGE:
		n = run_charge(out);
		break;
	case RREC_FAC_XTAL:
		n = run_xtal(out);
		break;
	case RREC_FAC_SHIP_ENTER:
	case RREC_FAC_SHIP_SAMPLE: {
		/* The beacon first, then the flag (SHIP_ENTER only): when either fails nothing changes and the ring stays in
		 * FACTORY_TEST with the flag as it was, so the jig can ask again (FW l.1019, l.1035). */
		int rc = rfa_ship_begin();

		if (rc == 0 && rfa_clears_flag(c.sub)) {
			rc = ops.flag_set != NULL ? ops.flag_set(false) : -ENOTSUP;
			if (rc != 0) {
				beacon_stop_now();
			}
		}
		if (rc != 0) {
			n = rfa_put_result(out, RREC_FAC_RESULT_FAIL);
			break;
		}
		eff = c.sub == RREC_FAC_SHIP_ENTER ? RFA_EFFECT_SHIP_ENTER : RFA_EFFECT_SHIP_SAMPLE;
		n = rfa_put_result(out, RREC_FAC_RESULT_PASS);
		break;
	}
	default: /* unreachable: rfa_parse admits only the sub-commands above */
		n = rfa_put_result(out, RREC_FAC_RESULT_FAIL);
		break;
	}
	if (out_len != NULL) {
		*out_len = n;
	}
	if (effect != NULL) {
		*effect = eff;
	}
	return RREC_ST_OK;
}
