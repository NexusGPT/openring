/*
 * rsy.c: the thin part of ring_sys (software step 6, unit U7). Hardware only through rhw.h (image store, persistent
 * settings, retained memory, watchdog, clock). Written for this project. "FW l.N" = line N of design/firmware.md.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/spinlock.h>

#include <ring_rhw/rhw.h>
#include <ring_sys/rsy.h>

#include "rsy_int.h"
#include "rsy_logic.h"

#ifdef CONFIG_RING_RHW_SIM
#include <ring_rhw/rhw_sim.h>
#endif

#define READBACK_BYTES 512u   /* the piece FW_END reads back at a time */

static struct k_spinlock lk;
static K_MUTEX_DEFINE(save_mtx);   /* one settings write at a time */

static rrec_log_fn log_fn;
static struct rhw_persist ps;        /* the settings as loaded and as last saved */
static bool guess_ok;                /* a time was saved before this boot (FW l.1005) */
static int64_t guess_utc;

/* update */
static bool fw_begun;
static uint32_t fw_size;
static uint32_t fw_crc;

/* self-test */
static struct rsl_selftest st;
static struct k_work_delayable st_work;
static bool st_work_ready;

/* watchdog */
static bool wdt_running;
static bool rec_running;
static int64_t last_audio = RSL_NEVER;
static int64_t last_store = RSL_NEVER;
static struct k_work_delayable wdt_work;
#ifdef CONFIG_RING_RHW_SIM
static bool hook_added;
#endif

static void log_selftest(uint8_t result, uint8_t mask)
{
	uint8_t a[2] = { result, mask };

	if (log_fn != NULL) {
		log_fn(RREC_LOG_SELFTEST, a, sizeof(a));
	}
}

/* ------------------------------------------------------------------ RAM state (the reboot hook of the simulation) */
#ifdef CONFIG_RING_RHW_SIM
static void clear_state(void)
{
	if (st_work_ready) {
		(void)k_work_cancel_delayable(&st_work);
		(void)k_work_cancel_delayable(&wdt_work);
	}
	K_SPINLOCK(&lk) {
		log_fn = NULL;
		memset(&ps, 0, sizeof(ps));
		guess_ok = false;
		guess_utc = 0;
		fw_begun = false;
		fw_size = 0;
		fw_crc = 0;
		memset(&st, 0, sizeof(st));
		wdt_running = false;
		rec_running = false;
		last_audio = RSL_NEVER;
		last_store = RSL_NEVER;
	}
}
#endif

static void st_expired(struct k_work *w);
static void wdt_tick(struct k_work *w);

int rsy_init(rrec_log_fn log)
{
	struct rhw_persist loaded;
	int r;

	if (!st_work_ready) {
		k_work_init_delayable(&st_work, st_expired);
		k_work_init_delayable(&wdt_work, wdt_tick);
		st_work_ready = true;
	}
#ifdef CONFIG_RING_RHW_SIM
	if (!hook_added) {
		hook_added = rhw_sim_add_reboot_hook(clear_state) == 0;
	}
#endif
	memset(&loaded, 0, sizeof(loaded));
	r = rhw_persist()->load(&loaded);
	if (r != 0) {
		/* a settings read that fails leaves every value at its safe default: factory flag clear (FACTORY then
		 * answers NOT_ALLOWED), no saved time */
		memset(&loaded, 0, sizeof(loaded));
	}
	K_SPINLOCK(&lk) {
		log_fn = log;
		ps = loaded;
		guess_ok = rsl_time_guess(loaded.time_saved, loaded.saved_utc_ms, &guess_utc);
		fw_begun = false;
		fw_size = 0;
		fw_crc = 0;
	}
	return r;
}

/* ------------------------------------------------------------------ update */
enum rrec_status rsy_fw_begin(uint32_t image_size, uint32_t image_crc32, uint16_t soc_x10, bool vbus)
{
	enum rrec_status s = rsl_begin_check(image_size, soc_x10, vbus);

	if (s != RREC_ST_OK) {
		return s;
	}
	K_SPINLOCK(&lk) {
		fw_begun = false;
	}
	if (rhw_image()->erase_slot1() != 0) {
		return RREC_ST_FW_ERROR;
	}
	K_SPINLOCK(&lk) {
		fw_begun = true;
		fw_size = image_size;
		fw_crc = image_crc32;
	}
	return RREC_ST_OK;
}

enum rrec_status rsy_fw_data(uint32_t offset, const uint8_t *data, size_t len)
{
	bool begun = false;
	uint32_t size = 0;
	enum rrec_status s;

	K_SPINLOCK(&lk) {
		begun = fw_begun;
		size = fw_size;
	}
	s = rsl_data_check(begun, size, offset, len, data != NULL);
	if (s != RREC_ST_OK) {
		return s;
	}
	if (len == 0u) {
		return RREC_ST_OK;
	}
	if (rhw_image()->write(offset, data, len) != 0) {
		return RREC_ST_FW_ERROR;
	}
	return RREC_ST_OK;
}

enum rrec_status rsy_fw_end(void)
{
	uint8_t buf[READBACK_BYTES];
	bool begun = false;
	uint32_t size = 0, want = 0, crc = 0;

	K_SPINLOCK(&lk) {
		begun = fw_begun;
		size = fw_size;
		want = fw_crc;
	}
	if (!begun) {
		return RREC_ST_FW_ERROR;
	}
	for (uint32_t off = 0; off < size;) {
		uint32_t n = size - off < sizeof(buf) ? size - off : (uint32_t)sizeof(buf);

		if (rhw_image()->read(off, buf, n) != 0) {
			return RREC_ST_FW_ERROR;
		}
		crc = rsl_crc32_update(crc, buf, n);
		off += n;
	}
	K_SPINLOCK(&lk) {
		fw_begun = false;   /* one FW_END per FW_BEGIN, whatever it answers */
	}
	if (crc != want) {
		return RREC_ST_FW_ERROR;
	}
	if (rhw_image()->request_test_upgrade() != 0) {
		return RREC_ST_FW_ERROR;
	}
	return RREC_ST_OK;
}

/* ------------------------------------------------------------------ self-test */
static void st_expired(struct k_work *w)
{
	uint8_t mask = 0;
	bool was_running = false;

	ARG_UNUSED(w);
	K_SPINLOCK(&lk) {
		was_running = st.running;
		if (was_running) {
			mask = rsl_st_expire(&st);
		}
	}
	if (!was_running) {
		return;
	}
	log_selftest(2u, mask);   /* result 2: the window ended before every item passed */
	(void)rhw_image()->reboot(RHW_REBOOT_SELFTEST_FAIL);
}

int rsy_selftest_start(bool vbus)
{
	if (rhw_image()->is_confirmed() != 0) {
		return 0;   /* confirmed (1), or unknown (negative): nothing to do */
	}
	K_SPINLOCK(&lk) {
		rsl_st_start(&st, vbus);
	}
	(void)k_work_reschedule(&st_work, K_MSEC(rsl_selftest_window_ms()));
	return 1;
}

void rsy_selftest_pass(enum rsy_item item)
{
	bool done = false;
	uint8_t mask = 0;

	K_SPINLOCK(&lk) {
		done = rsl_st_pass(&st, item);
		mask = st.passed;
	}
	if (!done) {
		return;
	}
	(void)k_work_cancel_delayable(&st_work);
	if (rhw_image()->confirm() == 0) {
		log_selftest(0u, mask);
	} else {
		log_selftest(1u, mask);   /* result 1: the confirm write failed */
		(void)rhw_image()->reboot(RHW_REBOOT_SELFTEST_FAIL);
	}
}

bool rsy_selftest_running(void)
{
	bool r = false;

	K_SPINLOCK(&lk) {
		r = st.running;
	}
	return r;
}

/* ------------------------------------------------------------------ factory flag and saved time */
bool rsy_factory_flag(void)
{
	bool r = false;

	K_SPINLOCK(&lk) {
		r = ps.factory_flag != 0u;
	}
	return r;
}

/* Save a changed copy of the settings; the RAM copy follows only when the write worked. */
static int save_with(bool set_flag, bool flag, bool set_time, bool time_saved, int64_t utc_ms, int16_t tz_min,
		     bool zone_known)
{
	struct rhw_persist n;
	int r;

	k_mutex_lock(&save_mtx, K_FOREVER);
	K_SPINLOCK(&lk) {
		n = ps;
	}
	if (set_flag) {
		n.factory_flag = flag ? 1u : 0u;
	}
	if (set_time) {
		n.time_saved = time_saved;
		n.saved_utc_ms = utc_ms;
		n.saved_tz_min = tz_min;
		n.saved_zone_known = zone_known;
	}
	r = rhw_persist()->save(&n);
	if (r == 0) {
		K_SPINLOCK(&lk) {
			ps = n;
		}
	}
	k_mutex_unlock(&save_mtx);
	return r;
}

int rsy_factory_flag_set(bool on)
{
	return save_with(true, on, false, false, 0, 0, false);
}

int rsy_time_save(int64_t utc_ms, int16_t tz_min, bool zone_known)
{
	if (!rsl_time_saveable(utc_ms)) {
		/* the clock is not set: there is no time to keep; an older saved time must not stay as a wrong guess */
		bool had = false;

		K_SPINLOCK(&lk) {
			had = ps.time_saved;
		}
		if (!had) {
			return 0;
		}
		return save_with(false, false, true, false, 0, 0, false);
	}
	return save_with(false, false, true, true, utc_ms, tz_min, zone_known);
}

bool rsy_time_guess(int64_t *utc_ms)
{
	bool ok = false;
	int64_t v = 0;

	K_SPINLOCK(&lk) {
		ok = guess_ok;
		v = guess_utc;
	}
	if (!ok || utc_ms == NULL) {
		return false;
	}
	*utc_ms = v;
	return true;
}

/* ------------------------------------------------------------------ crash */
int rsy_crash_capture(uint32_t reason, uint32_t pc, uint32_t lr, uint32_t psr, const char *thread,
		      const uint32_t *stack, size_t stack_words)
{
	struct rrec_crash c;
	uint8_t raw[RSL_CRASH_STORED_BYTES];

	memset(&c, 0, sizeof(c));
	c.reason = reason;
	c.pc = pc;
	c.lr = lr;
	c.psr = psr;
	strncpy(c.thread, thread != NULL ? thread : "?", RREC_CRASH_NAME_BYTES - 1u);
	for (size_t i = 0; stack != NULL && i < stack_words && i < RREC_CRASH_STACK_WORDS; i++) {
		c.stack[i] = stack[i];
	}
	(void)rsl_crash_encode(&c, raw);
	return rhw_retained()->write(raw, sizeof(raw));
}

void rsy_fatal(unsigned int reason, const struct arch_esf *esf)
{
	uint32_t pc = 0, lr = 0, psr = 0;
	const uint32_t *sp = NULL;
	size_t words = 0;
	const char *name = "?";

#ifdef CONFIG_ARM
	if (esf != NULL) {
		pc = esf->basic.pc;
		lr = esf->basic.lr;
		psr = esf->basic.xpsr;
		sp = (const uint32_t *)esf;
	}
#ifdef CONFIG_THREAD_STACK_INFO
	/* the words of the faulting thread's stack from the exception frame, never past the stack's end */
	if (sp != NULL) {
		uintptr_t lo = k_current_get()->stack_info.start;
		uintptr_t hi = lo + k_current_get()->stack_info.size;

		if ((uintptr_t)sp >= lo && (uintptr_t)sp < hi) {
			words = (hi - (uintptr_t)sp) / sizeof(uint32_t);
		} else {
			sp = NULL;
		}
	}
#else
	sp = NULL;
#endif
#else
	ARG_UNUSED(esf);
#endif
	if (k_is_in_isr()) {
		name = "isr";
	}
#ifdef CONFIG_THREAD_NAME
	else {
		const char *n = k_thread_name_get(k_current_get());

		if (n != NULL && n[0] != '\0') {
			name = n;
		}
	}
#endif
	(void)rsy_crash_capture((uint32_t)reason, pc, lr, psr, name, sp, words);
	(void)rhw_retained()->gpregret1_set((uint8_t)reason);
	(void)rhw_image()->reboot(RHW_REBOOT_CRASH);
}

int rsy_crash_take(struct rrec_crash *out, uint8_t *gpregret1)
{
	uint8_t raw[RSL_CRASH_STORED_BYTES];
	uint8_t gp = 0;

	if (out == NULL) {
		return 0;
	}
	if (rhw_retained()->read(raw, sizeof(raw)) != 0) {
		return 0;
	}
	if (!rsl_crash_decode(raw, out)) {
		return 0;
	}
	(void)rhw_retained()->gpregret1_get(&gp);
	if (gpregret1 != NULL) {
		*gpregret1 = gp;
	}
	(void)rhw_retained()->clear();
	(void)rhw_retained()->gpregret1_set(0);
	return 1;
}

/* ------------------------------------------------------------------ watchdog */
void rsy_progress(enum rsy_thread t)
{
	int64_t now = rhw_clock()->now_ms();

	K_SPINLOCK(&lk) {
		if (t == RSY_THREAD_AUDIO) {
			last_audio = now;
		} else if (t == RSY_THREAD_STORAGE) {
			last_store = now;
		}
	}
}

void rsy_recording(bool on)
{
	K_SPINLOCK(&lk) {
		if (on && !rec_running) {
			/* progress counts only when it was reported during this recording */
			last_audio = RSL_NEVER;
			last_store = RSL_NEVER;
		}
		rec_running = on;
	}
}

static void wdt_tick(struct k_work *w)
{
	int64_t now = rhw_clock()->now_ms();
	bool feed = false;

	ARG_UNUSED(w);
	K_SPINLOCK(&lk) {
		feed = rsl_wdt_should_feed(rec_running, now, last_audio, last_store);
	}
	if (feed) {
		(void)rhw_wdt()->feed();
	}
	(void)k_work_reschedule(&wdt_work, K_MSEC(RREC_WDT_FEED_MS));
}

int rsy_wdt_start(void)
{
	bool already = false;
	int r;

	K_SPINLOCK(&lk) {
		already = wdt_running;
	}
	if (already) {
		return -EALREADY;
	}
	r = rhw_wdt()->start(RREC_WDT_TIMEOUT_MS);
	if (r != 0) {
		return r;
	}
	K_SPINLOCK(&lk) {
		wdt_running = true;
	}
	(void)k_work_reschedule(&wdt_work, K_MSEC(RREC_WDT_FEED_MS));
	return 0;
}
