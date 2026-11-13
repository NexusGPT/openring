/*
 * rrec_int.h: the join's own header (not frozen, not part of rrec.h). Two entries for the glue's ops that rrec.h has no
 * name for, the shared state of the join's files, and the test read-outs (CONFIG_RING_RECORDER_TEST_HOOKS).
 * "FW l.N" = line N of design/firmware.md.
 */
#ifndef RING_RECORDER_RREC_INT_H
#define RING_RECORDER_RREC_INT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <ring_core/rc_types.h>
#include <ring_rhw/rrec_spec.h>

#ifdef __cplusplus
extern "C" {
#endif

/* rglue_ops.after for the product: the join's step bookkeeping (state change record, sampling class, rails that follow
 * the state, reboot) and then the screens (rscr_glue_after), in this order: the screens learn of a new state only
 * after the actions ran, so VDD_MIC is off before the screen may leave the recording pictures (FW l.342). */
bool rrec_glue_after(const struct rc_actions *a, enum rc_event last_event, enum rc_state state, rc_ms_t t);

/* rglue_ops.screen_fact for the product: the facts the caller of the core owns (open flag at start-up, factory flag,
 * storage full cleared when space was freed) are written here, under the glue's lock, right before every core call;
 * then the screens' lock fact (rscr_lock_fact_now) is returned. */
bool rrec_glue_screen_fact(void);

/* ------------------------------------------------------------------ shared between the join's files */
/* The event log hook every unit gets (rrec_log_fn): fills time, utc and state, queues the record (rst_log_put). */
void rrec_log(uint16_t code, const uint8_t *args, size_t nargs);

/* Jobs of the recorder's thread (rrec_bridge.c): a unit's callback must not block or take the glue's lock from its own
 * thread, so it posts a job; the thread carries it into the glue. */
enum rrec_job {
	RREC_JOB_EVENT = 1,      /* arg: enum rc_event, through rglue_event() */
	RREC_JOB_BATTERY,        /* arg: enum rc_batt, through rglue_battery() */
	RREC_JOB_RECOVER,        /* RECOVERY entered: the scan (rst_recover), then SCAN_DONE or SCAN_READ_ERROR */
	RREC_JOB_RETRY,          /* RC_ACT_RETRY_STORAGE: the storage init, then RETRY_OK or RETRY_FAILED (ruling R3) */
};
int rrec_post(enum rrec_job job, uint32_t arg);
struct rpw_cb;
struct rst_cb;
struct rau_cb;
struct rxf_cb;
struct rxf_backend;
struct rmo_cb;
struct rfa_ops;
/* Start the thread (once). */
void rrec_bridge_start(void);
/* The units' callback tables (rrec_bridge.c), given to them by the boot sequence. */
const struct rpw_cb *rrec_power_cb(void);
const struct rst_cb *rrec_store_cb(void);
const struct rau_cb *rrec_audio_cb(void);
const struct rxf_cb *rrec_xfer_cb(void);
const struct rxf_backend *rrec_backend(void);
const struct rmo_cb *rrec_motor_cb(void);
#if defined(CONFIG_RING_FACTORY)
const struct rfa_ops *rrec_factory_ops(void);
#endif

/* The join's state (rrec.c). Written under the glue's lock (actions and after) unless the comment says otherwise. */
struct rrec_state {
	uint8_t core_state;      /* enum rc_state after the last core step */
	bool recording;          /* a recording of type 1 is open (OPEN done, CLOSE not yet) */
	bool test_recording;     /* a factory test recording runs (transfer thread; atomic flag) */
	uint32_t rec_id;         /* the open recording */
	rc_ms_t press_ms;        /* the long press of the open recording */
	bool reboot_pending;     /* RC_ACT_REBOOT seen in this step: reboot in after, reason from the step's event */
	bool usb_hfxo;           /* the join holds HFXO for USB (CHARGING with VBUS, TRANSFER; FW l.912 to l.920) */
	uint8_t chg_err_reason;  /* the last charge error (RC_ACT_LOG_CHARGE_ERROR) */
	uint8_t chg_err_sensor;
	/* facts the caller of the core owns, written by rrec_glue_screen_fact() under the lock */
	bool fact_open_pending;
	bool fact_open;
	bool fact_factory_pending;
	bool fact_factory;
	uint32_t boot_count;     /* from the boot mount (GET_INFO) */
	uint32_t card_sectors;
};
extern struct rrec_state rrec_st;

/* rrec_boot.c: the boot sequence (FW l.133 to l.140); also used again by a test after rhw_sim_reboot(). */
int rrec_boot(void);
/* rrec.c: close an open recording in the order of FW l.125 (ruling 2 of the root unit's notes): rau_cut(mark),
 * rst_close, rau_halt, rec_mics_off, rau_release, rst_unmount. */
int rrec_close(rc_ms_t mark);
/* rrec.c: a test recording of type 2 for the factory (T-MIC, T-SIGN; FW l.1024, l.1029, ruling R18). Transfer thread. */
int rrec_test_recording(uint32_t ms, void (*on_block)(const int16_t *frames, uint32_t n), int64_t *mic_on_ms,
			int64_t *mic_off_ms);
/* rrec_bridge.c: the firmware version for the chunk headers and GET_INFO (APPVERSION of app/VERSION; 0 in a test). */
uint32_t rrec_fw_version(void);
/* rrec.c: the state now (any thread). */
enum rc_state rrec_core_state(void);
/* rrec.c: a crash block into the event log (RREC_LOG_CRASH, FW l.1063). */
struct rrec_crash;
void rrec_log_crash(const struct rrec_crash *c);
/* rrec.c: a chunk of a factory test recording to the factory's block callback (256 frames at a time). */
struct rst_chunk;
void rrec_feed_test_blocks(const struct rst_chunk *c);
#if defined(CONFIG_RING_RHW_SIM)
/* rrec.c: the join's RAM state back to reset values on rhw_sim_reboot(). */
void rrec_sim_reboot_hook(void);
#endif

/* ------------------------------------------------------------------ test read-outs */
#if defined(CONFIG_RING_RECORDER_TEST_HOOKS)
struct rrec_tap_rec {
	uint16_t code;
	uint8_t state;
	uint8_t args[RREC_LOG_ARG_BYTES];
	int64_t t_ms;
	bool has_crash;
};
/* Every record the join queued (rst_log_put) since the last clear, in order; at most RREC_TAP_MAX kept. */
#define RREC_TAP_MAX 256
uint32_t rrec_tap_count(void);
bool rrec_tap_get(uint32_t i, struct rrec_tap_rec *out);
uint32_t rrec_tap_count_code(uint16_t code);
void rrec_tap_clear(void);
/* true when the recorder's thread has no job queued and none running. */
bool rrec_idle(void);
#endif

#ifdef __cplusplus
}
#endif

#endif
