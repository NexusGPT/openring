/*
 * rrec.c: the action executor of the join (software step 6, unit J). Every action of the core (enum rc_action) is
 * carried out here, in the order the core gives them, through the units of step 6 (ring_store, ring_audio, ring_power,
 * ring_motor, ring_sys, ring_xfer, ring_factory) and the screens. Runs inside the glue's step with its lock held.
 * "FW l.N" = line N of design/firmware.md. Hardware only through the units' public headers and rhw.h.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/byteorder.h>

#include <ring_audio/rau.h>
#include <ring_core/rc_core.h>
#include <ring_glue/rglue.h>
#include <ring_motor/rmo.h>
#include <ring_power/rpw.h>
#include <ring_recorder/rrec.h>
#include <ring_rhw/rhw.h>
#include <ring_screens/rscr.h>
#include <ring_store/rst.h>
#include <ring_sys/rsy.h>
#include <ring_time/rtime.h>
#include <ring_xfer/rxf.h>
#if defined(CONFIG_RING_FACTORY)
#include <ring_factory/rfa.h>
#endif
#if defined(CONFIG_RING_DEVICES)
#include <ring_devices/rdev.h>
#endif
#if defined(CONFIG_RING_RHW_SIM)
#include <ring_rhw/rhw_sim.h>
#endif

#include "rrec_int.h"

struct rrec_state rrec_st = { .core_state = RC_ST_BOOT };

#define HFXO_WAIT_MS   100   /* the join's limit for rau_prepare (FW l.428 gives no number) */
#define FINISH_WAIT_MS 5000  /* rxf_finish: the command that runs may take this long (FW l.178 gives no number) */
/* Ship mode (review finding R6-01): the wearer feels the whole M2 of FW l.151 before the motor is stopped: the join waits
 * for rmo_playing() to end, at most RREC_PAT_M2_MS (280 ms, FW l.323) plus a margin of 100 ms for the timer and the
 * threads (the margin is the join's choice). */
#define SHIP_M2_MARGIN_MS 100

static uint32_t last_closed_id;
static bool last_closed_valid;

enum rc_state rrec_core_state(void)
{
	return (enum rc_state)rrec_st.core_state;
}

/* ------------------------------------------------------------------ the event log hook (FW l.1062) */
#if defined(CONFIG_RING_RECORDER_TEST_HOOKS)
static struct k_spinlock tap_lk;
static struct rrec_tap_rec tap[RREC_TAP_MAX];
static uint32_t tap_n;

uint32_t rrec_tap_count(void)
{
	return tap_n;
}

bool rrec_tap_get(uint32_t i, struct rrec_tap_rec *out)
{
	bool ok = false;

	K_SPINLOCK(&tap_lk) {
		if (i < tap_n && i < RREC_TAP_MAX) {
			*out = tap[i];
			ok = true;
		}
	}
	return ok;
}

uint32_t rrec_tap_count_code(uint16_t code)
{
	uint32_t n = 0;

	K_SPINLOCK(&tap_lk) {
		for (uint32_t i = 0; i < tap_n && i < RREC_TAP_MAX; i++) {
			n += tap[i].code == code ? 1u : 0u;
		}
	}
	return n;
}

void rrec_tap_clear(void)
{
	K_SPINLOCK(&tap_lk) {
		tap_n = 0;
	}
}
#endif

static void log_put(uint16_t code, const uint8_t *args, size_t nargs, const struct rrec_crash *crash)
{
	struct rrec_logrec r;
	int64_t now = rhw_clock()->now_ms();

	memset(&r, 0, sizeof(r));
	r.uptime_ns = now * 1000000;
	r.utc_ms = rtime_is_set() ? rtime_utc_ms() : 0;   /* 0 when the time is not set (FW l.1062, l.1005) */
	r.code = code;
	r.state = rrec_st.core_state;
	if (args != NULL) {
		memcpy(r.args, args, MIN(nargs, sizeof(r.args)));
	}
	if (crash != NULL) {
		r.has_crash = true;
		r.crash = *crash;
	}
	rst_log_put(&r);
#if defined(CONFIG_RING_RECORDER_TEST_HOOKS)
	K_SPINLOCK(&tap_lk) {
		if (tap_n < RREC_TAP_MAX) {
			tap[tap_n].code = code;
			tap[tap_n].state = r.state;
			memcpy(tap[tap_n].args, r.args, sizeof(r.args));
			tap[tap_n].t_ms = now;
			tap[tap_n].has_crash = r.has_crash;
		}
		tap_n++;
	}
#endif
}

void rrec_log(uint16_t code, const uint8_t *args, size_t nargs)
{
	log_put(code, args, nargs, NULL);
}

void rrec_log_crash(const struct rrec_crash *c)
{
	log_put(RREC_LOG_CRASH, NULL, 0, c);
}

/* ------------------------------------------------------------------ storage helpers */
static int mount_now(void)
{
	struct rst_mount_info mi;
	int r;

	if (rst_mounted()) {
		return 0;
	}
	r = rst_mount(false, &mi);   /* VDD_SD on, mount (FW l.126, l.506) */
	if (r == 0) {
		rrec_st.card_sectors = mi.card_sectors;
	}
	return r;
}

/* ------------------------------------------------------------------ open (FW l.126, l.455 to l.460) */
static void open_recording(rc_ms_t t)
{
	struct rau_start_args sa;
	uint32_t id = 0;
	uint8_t args[12];
	struct rpw_values v;
	int r;

	r = mount_now();
	if (r == 0) {
		r = rst_open(RREC_REC_TYPE_RECORDING, rtime_is_set() ? rtime_utc_ms() : 0, &id);
	}
	if (r != 0) {
		/* storage refused the open: the core leaves RECORDING through the storage fault row (FW l.168) */
		sys_put_le32(0, args);
		sys_put_le32((uint32_t)r, &args[4]);
		rrec_log(RREC_LOG_FAULT_CHUNK_WRITE, args, 8);
		(void)rrec_post(RREC_JOB_EVENT, RC_EV_CHUNK_WRITE_FAILED);
		return;
	}
	rrec_st.recording = true;
	rrec_st.rec_id = id;
	rrec_st.press_ms = t;
	rsy_recording(true);                     /* the watchdog expects progress from now on (FW l.1065) */
	rpw_state(RC_ST_RECORDING);              /* 1 s samples (FW l.928) */
	r = rau_prepare(HFXO_WAIT_MS);           /* 1. HFXO requested and running (FW l.456) */
	if (r == 0) {
		r = rec_mics_on(t);              /* 2. the sign, then VDD_MIC (FW l.457, l.342) */
		if (r != 0) {
			(void)rau_release();
		}
	}
	if (r != 0) {
		/* no microphones: the recording is closed at once (empty) and the core leaves RECORDING through the
		 * microphone fault row (FW l.169: close; MF); reading of the join, written in recorder-notes.md */
		struct rst_close_args ca;

		memset(&ca, 0, sizeof(ca));
		for (uint32_t i = 0; i < RREC_CLOSE_HIGHLIGHTS; i++) {
			ca.highlight_ms[i] = RREC_UNUSED_U32;
		}
		(void)rst_close(NULL, &ca);
		(void)rst_unmount();
		rrec_st.recording = false;
		rsy_recording(false);
		sys_put_le32((uint32_t)r, args);
		rrec_log(RREC_LOG_SIGN_REFUSED, args, 4);
		(void)rrec_post(RREC_JOB_EVENT, RC_EV_MIC_NO_BLOCK);
		return;
	}
	k_sleep(K_MSEC(RREC_MIC_RAIL_WAIT_MS));  /* 3. wait 1 ms (FW l.458) */
	rpw_values(&v);
	memset(&sa, 0, sizeof(sa));
	sa.recording_id = id;
	sa.recording_type = RREC_REC_TYPE_RECORDING;
	sa.boot_count = rrec_st.boot_count;
	sa.time_set = rtime_is_set();
	sa.utc_offset_ms = sa.time_set ? rtime_utc_ms() - rhw_clock()->now_ms() : 0;
	sa.b15 = v.level >= RC_BATT_B15;
	r = rau_start(&sa);                      /* 4. configure, start; 5. the 800 frames dropped (FW l.459, l.460) */
	sys_put_le32(id, args);
	sys_put_le64((uint64_t)t, &args[4]);
	rrec_log(RREC_LOG_REC_START, args, 12);
	if (sa.time_set && !rtime_zone_known()) {
		rrec_log(RREC_LOG_ZONE_UNKNOWN, args, 4);   /* decision D8 */
	}
	if (r != 0) {
		(void)rrec_post(RREC_JOB_EVENT, RC_EV_MIC_NO_BLOCK);
	}
}

/* ------------------------------------------------------------------ close (FW l.125; root unit's ruling 2) */
int rrec_close(rc_ms_t mark)
{
	struct rau_cut_result cr;
	int r;

	if (!rrec_st.recording) {
		return 0;
	}
	memset(&cr, 0, sizeof(cr));
	r = rau_cut(mark, &cr);                  /* the frames up to the mark kept; the partial chunk (FW l.448) */
	(void)rst_close(cr.last, &cr.close);     /* partial chunk, CLOSE record, superblock with the flag clear */
	(void)rau_halt();                        /* stop PDM, blocks released, clocks low (FW l.463) */
	(void)rec_mics_off();                    /* VDD_MIC off */
	(void)rau_release();                     /* HFXO after VDD_MIC (FW l.463) */
	(void)rst_unmount();                     /* VDD_SD off */
	rrec_st.recording = false;
	last_closed_id = rrec_st.rec_id;
	last_closed_valid = true;
	rsy_recording(false);
	return r;
}

/* row FW l.168: stop PDM; clocks low; VDD_MIC off; superblock left open (no close) */
static void stop_after_write_fault(enum rc_action a)
{
	switch (a) {
	case RC_ACT_STOP_PDM:
		(void)rau_halt();                /* trigger STOP, blocks released, pins to the sleep state */
		break;
	case RC_ACT_CLOCKS_LOW:
		/* rau_halt applied the clock pins' sleep state (clock low, FW l.465): nothing more to do */
		break;
	case RC_ACT_MIC_OFF:
		(void)rec_mics_off();
		(void)rau_release();
		rrec_st.recording = false;
		rsy_recording(false);
		break;
	default:
		break;
	}
}

/* ------------------------------------------------------------------ VDD_SD off (FW l.178, l.179, l.912 to l.920) */
/* Through the unmount that waits for a store call running on another thread (a transfer command, review finding R6-03),
 * bounded by FINISH_WAIT_MS. The result is never dropped: a failed unmount (the call did not end in time) is written to
 * the event log (RREC_LOG_UNMOUNT_FAILED: errno, state, try, lead's ruling) and tried again on the recorder's thread
 * (RREC_JOB_UNMOUNT) until it succeeds. */
static uint8_t unmount_tries;   /* failed tries since the last successful unmount */

static int unmount_now(void)
{
	uint8_t args[6];
	int r;

	if (!rst_mounted()) {
		unmount_tries = 0;
		return 0;
	}
	r = rst_unmount_wait(FINISH_WAIT_MS);
	if (r == -EBUSY) {
		if (unmount_tries < UINT8_MAX) {
			unmount_tries++;
		}
		sys_put_le32((uint32_t)r, args);
		args[4] = rrec_st.core_state;
		args[5] = unmount_tries;
		rrec_log(RREC_LOG_UNMOUNT_FAILED, args, sizeof(args));
		(void)rrec_post(RREC_JOB_UNMOUNT, 0);
	} else {
		unmount_tries = 0;
	}
	return r;
}

/* ------------------------------------------------------------------ ship mode (FW 8.4, l.936 to l.941) */
#if defined(CONFIG_RING_RECORDER_TEST_HOOKS)
static void (*ship_hook)(void);
static uint32_t radio_stops;
static int radio_stop_rc;

void rrec_test_set_ship_hook(void (*fn)(void))
{
	ship_hook = fn;
}

uint32_t rrec_test_radio_stops(void)
{
	return radio_stops;
}

int rrec_test_radio_stop_rc(void)
{
	return radio_stop_rc;
}
#endif

/* The recorder's thread, after the step that asked for ship mode ended (RREC_JOB_SHIP): the screens were told the new
 * state (SHIP or OFF) in that step, the menu's power off no longer holds the screens thread (R6-10). */
void rrec_ship_now(void)
{
	int64_t end = rhw_clock()->now_ms() + RREC_PAT_M2_MS + SHIP_M2_MARGIN_MS;
	int r;

	/* the M2 of FW l.151 is felt whole (R6-01), then no motor while the chip is cut */
	while (rmo_playing() && rhw_clock()->now_ms() < end) {
		k_sleep(K_MSEC(5));
	}
	rmo_stop();
	/* step 1 (FW l.937, R6-02): close everything: recording, storage, USB, radio, screen */
	if (rrec_st.recording) {
		(void)rrec_close(rhw_clock()->now_ms());   /* the rows close it before; kept as the last guard */
	}
	(void)unmount_now();                     /* storage closed (the queued log records are written first) */
	(void)rxf_stop(FINISH_WAIT_MS);          /* USB: the command aborted, the stack disabled */
	if (rrec_st.usb_hfxo) {
		(void)rhw_hfxo()->release();
		rrec_st.usb_hfxo = false;
	}
#if defined(CONFIG_RING_DEVICES)
	r = rdev_stop();                         /* radio: this part's advertising and link; the ship beacon (R20) stays */
#else
	r = 0;
#endif
#if defined(CONFIG_RING_RECORDER_TEST_HOOKS)
	radio_stops++;
	radio_stop_rc = r;
#else
	ARG_UNUSED(r);
#endif
	rscr_sync();                             /* screen: the screens thread drew SCR_OFF (panel off) for SHIP or OFF */
#if defined(CONFIG_RING_RECORDER_TEST_HOOKS)
	if (ship_hook != NULL) {
		ship_hook();
	}
#endif
#if defined(CONFIG_RING_FACTORY)
	(void)rpw_ship(rfa_beacon_stop);         /* steps 2 to 5; the beacon stops right before the ship task (R20) */
#else
	(void)rpw_ship(NULL);
#endif
}

/* the recorder's thread: a failed unmount tried again (RREC_JOB_UNMOUNT) while the state still wants VDD_SD off */
void rrec_unmount_retry(void)
{
	enum rc_state s = rrec_core_state();

	if (s == RC_ST_RECOVERY || s == RC_ST_RECORDING || s == RC_ST_TRANSFER || s == RC_ST_BOOT ||
	    s == RC_ST_FACTORY_TEST) {
		return;   /* the state wants the card (or runs its own sequence): nothing to retry */
	}
	(void)unmount_now();
}

static void play(enum rrec_pattern p)
{
	(void)rmo_play(p);
}

void rrec_action(enum rc_action a, rc_ms_t t)
{
	switch (a) {
	case RC_ACT_OPEN:
		open_recording(t);
		break;
	case RC_ACT_CLOSE:
		(void)rrec_close(t);
		break;
	case RC_ACT_CHARGE_ON:
		(void)rpw_charge_on();
		break;
	case RC_ACT_CHARGE_OFF:
		(void)rpw_charge_off();
		break;
	case RC_ACT_M1:
		play(RREC_PAT_M1);
		break;
	case RC_ACT_M2:
		play(RREC_PAT_M2);
		break;
	case RC_ACT_M3:
		play(RREC_PAT_M3);
		break;
	case RC_ACT_MH:
		play(RREC_PAT_MH);
		break;
	case RC_ACT_MT:
		play(RREC_PAT_MT);
		break;
	case RC_ACT_MF:
		play(RREC_PAT_MF);
		break;
	case RC_ACT_MW:
		play(RREC_PAT_MW);
		break;
	case RC_ACT_SD_ON:
	case RC_ACT_MOUNT:
		(void)mount_now();
		break;
	case RC_ACT_SD_OFF:
		(void)unmount_now();             /* FW l.178, l.179: the result is kept (R6-03) */
		break;
	case RC_ACT_STOP_PDM:
	case RC_ACT_CLOCKS_LOW:
	case RC_ACT_MIC_OFF:
		stop_after_write_fault(a);
		break;
	case RC_ACT_SHIP_MODE:
		rrec_st.ship_pending = true;     /* on the recorder's thread after this step (rrec_glue_after) */
		break;
	case RC_ACT_SAVE_SETTINGS_TIME:
		/* FW l.1005: the time is saved on entry into SHIP and OFF (0 when not set: nothing saved, ring_sys) */
		(void)rsy_time_save(rtime_is_set() ? rtime_utc_ms() : 0, rtime_tz_min(), rtime_zone_known());
		break;
	case RC_ACT_CLEAR_FACTORY_FLAG:
		(void)rsy_factory_flag_set(false);
		rrec_st.fact_factory = false;
		rrec_st.fact_factory_pending = true;
		break;
	case RC_ACT_REQUEST_UPGRADE_TEST:
		/* rsy_fw_end() requested the test upgrade before it answered OK (rsy.h); the row follows that OK */
		break;
	case RC_ACT_REBOOT:
		rrec_st.reboot_pending = true;   /* after the step, with the reason of the step's event */
		break;
	case RC_ACT_FACTORY_MODE:
		/* FW 9.3: the factory part answers the jig from now on (rfa_request with in_factory_test) */
		break;
	case RC_ACT_RETRY_STORAGE:
		(void)rrec_post(RREC_JOB_RETRY, 0);   /* ruling R3: the result comes back as an event */
		break;
	case RC_ACT_LOG_EVENT:
		/* the part that reported the event wrote its record (rows 6, 11, 16: FAULT_STORAGE_INIT, FAULT_SCAN_READ,
		 * SIGN_REFUSED) */
		break;
	case RC_ACT_LOG_CHARGE_ERROR: {
		uint8_t args[2] = { rrec_st.chg_err_reason, rrec_st.chg_err_sensor };

		rrec_log(RREC_LOG_FAULT_CHARGER, args, sizeof(args));
		break;
	}
	case RC_ACT_WRITE_CLOSE_RECOVERED:
	case RC_ACT_CLEAR_OPEN_FLAG:
		/* rst_recover() wrote the CLOSE record RECOVERED and cleared the flag at the end of the scan (rst.h) */
		break;
	case RC_ACT_HIGHLIGHT:
		/* the time of CENTRE_DOWN is in the action list: rrec_glue_after() passes it to the audio part */
		break;
	case RC_ACT_FINISH_COMMAND:
		(void)rxf_finish(FINISH_WAIT_MS);
		break;
	case RC_ACT_ABORT_COMMAND:
		/* FW l.179: abort the command, then wait for it to end (bounded as rxf_finish) so that VDD_SD goes off in this
		 * step (R6-03) */
		rxf_abort();
		(void)rxf_finish(FINISH_WAIT_MS);
		break;
	default:
		/* the screen actions: the screens part reads them in rrec_glue_after() */
		break;
	}
}

/* ------------------------------------------------------------------ after every core step */
/* VDD_SD per state (FW l.912 to l.920): on in RECOVERY, RECORDING, TRANSFER; BOOT runs its own sequence and
 * FACTORY_TEST is "per test" (the factory tests mount and unmount themselves). */
static bool sd_wanted(enum rc_state s)
{
	return s == RC_ST_RECOVERY || s == RC_ST_RECORDING || s == RC_ST_TRANSFER;
}

static void usb_hfxo_running(void)
{
	/* the USB part does not wait for the crystal: nothing to do when it runs */
}

/* HFXO held by the join per FW 8.2 (review finding R6-04): on in BOOT and RECOVERY (l.915), CHARGING "when USB runs"
 * (l.918: VBUS is present in CHARGING), TRANSFER (l.919), FACTORY_TEST (driven over USB); RECORDING's is the audio
 * part's (rau_prepare); STANDBY and the error states "when the radio runs" (the radio's own request) */
static bool hfxo_wanted(enum rc_state s)
{
	return s == RC_ST_BOOT || s == RC_ST_RECOVERY || s == RC_ST_CHARGING || s == RC_ST_TRANSFER || s == RC_ST_FACTORY_TEST;
}

void rrec_hfxo_follow_state(enum rc_state s)
{
	bool want = hfxo_wanted(s);

	if (want && !rrec_st.usb_hfxo) {
		rrec_st.usb_hfxo = rhw_hfxo()->request(usb_hfxo_running) == 0;
	} else if (!want && rrec_st.usb_hfxo) {
		(void)rhw_hfxo()->release();
		rrec_st.usb_hfxo = false;
	}
}

static void rails_follow_state(enum rc_state s)
{
	if (s != RC_ST_BOOT && s != RC_ST_FACTORY_TEST) {
		if (sd_wanted(s)) {
			(void)mount_now();
		} else if (rst_mounted()) {
			(void)unmount_now();
		}
	}
	/* VDD_MIC only in RECORDING (FW l.112): never needed when the actions ran as written; kept as the last guard */
	if (s != RC_ST_RECORDING && atomic_get(&rrec_st.test_recording) == 0 && rhw_pmic()->rail_get(RHW_RAIL_MIC)) {
		if (rau_capturing()) {
			(void)rau_halt();
		}
		(void)rec_mics_off();
		(void)rau_release();
		rrec_st.recording = false;
		rsy_recording(false);
	}
	rrec_hfxo_follow_state(s);   /* FW 8.2, for the state that follows */
}

static enum rhw_reboot_reason reboot_reason(enum rc_event ev)
{
	switch (ev) {
	case RC_EV_FW_END:
		return RHW_REBOOT_UPDATE;
	case RC_EV_FACTORY_EXIT:
		return RHW_REBOOT_FACTORY_EXIT;
	case RC_EV_VBUS_OUT:
		return RHW_REBOOT_FACTORY_VBUS;
	default:
		return RHW_REBOOT_COMMAND;
	}
}

/* T-JOY and T-CENTRE (FW l.1026, l.1027; lead's ruling 5): in FACTORY_TEST the glue hands the gesture events of the core's
 * recogniser here (rglue_ops.factory_gesture) and they go to the factory part, never to a recording */
void rrec_factory_gesture(const struct rc_gev *e)
{
#if defined(CONFIG_RING_FACTORY)
	enum rfa_input in;

	switch (e->type) {
	case RC_GEV_DIR:
		in = e->dir == RC_SW_UP ? RFA_IN_UP : e->dir == RC_SW_DOWN ? RFA_IN_DOWN :
		     e->dir == RC_SW_LEFT ? RFA_IN_LEFT : RFA_IN_RIGHT;
		break;
	case RC_GEV_CENTRE_DOWN:
		in = RFA_IN_CENTRE_DOWN;
		break;
	case RC_GEV_CENTRE_UP:
		in = RFA_IN_CENTRE_UP;
		break;
	case RC_GEV_WARN:
		in = RFA_IN_MW;
		break;
	case RC_GEV_LONG:
		in = RFA_IN_LONG;
		break;
	case RC_GEV_SHORT:
		in = RFA_IN_SINGLE;
		break;
	case RC_GEV_DOUBLE:
		in = RFA_IN_DOUBLE;
		break;
	default:
		return;
	}
	rfa_input(in, e->t);
#else
	ARG_UNUSED(e);
#endif
}

bool rrec_glue_after(const struct rc_actions *a, enum rc_event last_event, enum rc_state state, rc_ms_t t)
{
	enum rc_state prev = (enum rc_state)rrec_st.core_state;
	bool on;

	if (state != prev) {
		uint8_t sc[5];

		/* FW l.1062: each state change becomes a record (from, to, row, event) */
		sc[0] = (uint8_t)prev;
		sc[1] = (uint8_t)state;
		sys_put_le16((uint16_t)(a->last_row > 0 ? a->last_row : 0), &sc[2]);
		sc[4] = (uint8_t)last_event;
		rrec_st.core_state = (uint8_t)state;
		rrec_log(RREC_LOG_STATE_CHANGE, sc, sizeof(sc));
	}
	if (prev == RC_ST_RECORDING && state != RC_ST_RECORDING && last_event == RC_EV_LONG_PRESS && last_closed_valid) {
		uint8_t args[12];

		/* FW l.448: the press start time of a stop is written to the event log (the long press fires 1,000 ms
		 * after CENTRE_DOWN) */
		sys_put_le32(last_closed_id, args);
		sys_put_le64((uint64_t)(t - RREC_LONG_PRESS_MS), &args[4]);
		rrec_log(RREC_LOG_REC_STOP_PRESS, args, sizeof(args));
	}
	for (uint8_t i = 0; i < a->n; i++) {
		if (a->a[i] == RC_ACT_HIGHLIGHT) {
			rau_highlight(a->highlight_ms >= 0 ? a->highlight_ms : t);   /* the time of CENTRE_DOWN (FW l.159) */
		}
	}
	rpw_state(atomic_get(&rrec_st.test_recording) != 0 ? RC_ST_RECORDING : state);   /* ruling 8 of the root unit's notes */
	rails_follow_state(state);
	if (state == RC_ST_RECOVERY && prev != RC_ST_RECOVERY) {
		(void)rrec_post(RREC_JOB_RECOVER, 0);
	}
	if (rrec_st.reboot_pending) {
		rrec_st.reboot_pending = false;
		(void)rhw_image()->reboot(reboot_reason(last_event));
	}
	on = rscr_glue_after(a, last_event, state, t);
	if (rrec_st.ship_pending) {
		/* ship mode after the screens learned SHIP or OFF (the screen closes, R6-02), on the recorder's thread (R6-10) */
		rrec_st.ship_pending = false;
		(void)rrec_post(RREC_JOB_SHIP, 0);
	}
	return on;
}

bool rrec_glue_screen_fact(void)
{
	struct rc_core *c = rglue_core();   /* under the glue's lock: this runs right before the core call */
	struct rst_space sp;

	if (rrec_st.fact_open_pending) {
		c->facts.open_flag = rrec_st.fact_open;
		rrec_st.fact_open_pending = false;
	}
	if (rrec_st.fact_factory_pending) {
		c->facts.factory_flag = rrec_st.fact_factory;
		rrec_st.fact_factory_pending = false;
	}
	/* storage full is set by the SFULL event and cleared by the caller when space was freed (rc_core.h) */
	if (c->facts.storage_full && rst_space(&sp) == 0 && !sp.sfull) {
		c->facts.storage_full = false;
	}
	return rscr_lock_fact_now();
}

/* ------------------------------------------------------------------ the factory's test recording (T-MIC, T-SIGN) */
static void (*tr_block)(const int16_t *frames, uint32_t n);

void rrec_feed_test_blocks(const struct rst_chunk *c)
{
	void (*fn)(const int16_t *, uint32_t) = tr_block;
	const int16_t *p;
	uint32_t frames;

	if (fn == NULL || c == NULL) {
		return;
	}
	p = (const int16_t *)&c->bytes[RREC_CHUNK_HEADER_BYTES];
	frames = c->hdr.frames;
	for (uint32_t f = 0; f < frames; f += RREC_BLOCK_FRAMES) {
		uint32_t n = MIN(RREC_BLOCK_FRAMES, frames - f);

		fn(&p[f * RREC_CHANNELS], n);
	}
}

int rrec_test_recording(uint32_t ms, void (*on_block)(const int16_t *frames, uint32_t n), int64_t *mic_on_ms,
			int64_t *mic_off_ms)
{
	struct rau_start_args sa;
	struct rau_cut_result cr;
	uint32_t id = 0;
	int r;

	if (rrec_core_state() != RC_ST_FACTORY_TEST) {
		return -EPERM;   /* only the factory part, in FACTORY_TEST */
	}
	r = mount_now();
	if (r == 0) {
		r = rst_open(RREC_REC_TYPE_FACTORY, 0, &id);   /* type 2 (FW l.548, l.1024) */
	}
	if (r != 0) {
		return r;
	}
	tr_block = on_block;
	atomic_set(&rrec_st.test_recording, 1);
	rsy_recording(true);
	rpw_state(RC_ST_RECORDING);              /* ruling 8: sampling of the recording states in a test recording */
	r = rau_prepare(HFXO_WAIT_MS);
	if (r == 0) {
		r = rec_mics_on(rhw_clock()->now_ms());
		if (r != 0) {
			(void)rau_release();
			r = -ENODEV;             /* no screen, no test (ruling R18) */
		}
	}
	if (r != 0) {
		struct rst_close_args ca;

		memset(&ca, 0, sizeof(ca));
		for (uint32_t i = 0; i < RREC_CLOSE_HIGHLIGHTS; i++) {
			ca.highlight_ms[i] = RREC_UNUSED_U32;
		}
		(void)rst_close(NULL, &ca);
		(void)rst_unmount();
		goto out;
	}
	if (mic_on_ms != NULL) {
		*mic_on_ms = rhw_clock()->now_ms();
	}
	k_sleep(K_MSEC(RREC_MIC_RAIL_WAIT_MS));
	memset(&sa, 0, sizeof(sa));
	sa.recording_id = id;
	sa.recording_type = RREC_REC_TYPE_FACTORY;
	sa.boot_count = rrec_st.boot_count;
	r = rau_start(&sa);
	k_sleep(K_MSEC(ms + RREC_DISCARD_MS));
	memset(&cr, 0, sizeof(cr));
	(void)rau_cut(rhw_clock()->now_ms(), &cr);
	rrec_feed_test_blocks(cr.last);
	(void)rst_close(cr.last, &cr.close);
	(void)rau_halt();
	(void)rec_mics_off();
	if (mic_off_ms != NULL) {
		*mic_off_ms = rhw_clock()->now_ms();
	}
	(void)rau_release();
	(void)rst_unmount();
out:
	tr_block = NULL;
	atomic_set(&rrec_st.test_recording, 0);
	rsy_recording(false);
	rpw_state(RC_ST_FACTORY_TEST);
	return r;
}

#if defined(CONFIG_RING_RHW_SIM)
/* rhw_sim_reboot(): the join's RAM state goes back to its reset values (the tap is the test's observer and stays) */
void rrec_sim_reboot_hook(void)
{
	memset(&rrec_st, 0, sizeof(rrec_st));
	rrec_st.core_state = RC_ST_BOOT;
	last_closed_valid = false;
	tr_block = NULL;
	unmount_tries = 0;
}
#endif
