/*
 * rrec_bridge.c: the units' callbacks into the core (software step 6, unit J). A unit's callback runs on that unit's
 * thread (or a driver context) and must not block or take the glue's lock there (a CLOSE inside the step waits for the
 * storage thread, so the storage thread must never wait for the step). Each callback therefore posts a job; the
 * recorder's thread carries it into the glue (rglue_event, rglue_battery). The thread also runs the two storage jobs
 * the core asks for: the recovery scan (RECOVERY entered) and the 60 s storage retry (ruling R3).
 * "FW l.N" = line N of design/firmware.md.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/byteorder.h>

#include <ring_audio/rau.h>
#include <ring_glue/rglue.h>
#include <ring_motor/rmo.h>
#include <ring_power/rpw.h>
#include <ring_recorder/rrec.h>
#include <ring_rhw/rhw.h>
#include <ring_screens/rscr.h>
#include <ring_store/rst.h>
#include <ring_sys/rsy.h>
#include <ring_xfer/rxf.h>

#include "rrec_int.h"

struct job {
	uint8_t kind;    /* enum rrec_job */
	uint32_t arg;
};

K_MSGQ_DEFINE(job_q, sizeof(struct job), 32, 4);
K_THREAD_STACK_DEFINE(rrec_stack, CONFIG_RING_RECORDER_STACK_SIZE);
static struct k_thread rrec_thread;
static bool thread_up;
static atomic_t posted;
static atomic_t done;

int rrec_post(enum rrec_job kind, uint32_t arg)
{
	struct job j = { .kind = (uint8_t)kind, .arg = arg };
	int r;

	(void)atomic_inc(&posted);
	r = k_msgq_put(&job_q, &j, K_NO_WAIT);
	if (r != 0) {
		(void)atomic_inc(&done);   /* not queued: counted as done so a waiting test does not hang */
	}
	return r;
}

#if defined(CONFIG_RING_RECORDER_TEST_HOOKS)
bool rrec_idle(void)
{
	return atomic_get(&posted) == atomic_get(&done);
}
#endif

/* RECOVERY: scan and close the unfinished recording (FW l.141 to l.143, l.646) */
static void run_recover(void)
{
	struct rst_recover_result rr;
	uint8_t args[12];
	int r;

	if (rrec_core_state() != RC_ST_RECOVERY) {
		return;
	}
	memset(&rr, 0, sizeof(rr));
	if (!rst_mounted()) {
		struct rst_mount_info mi;

		r = rst_mount(false, &mi);
		if (r != 0) {
			sys_put_le32(0, args);
			sys_put_le32((uint32_t)r, &args[4]);
			rrec_log(RREC_LOG_FAULT_SCAN_READ, args, 8);
			rglue_event(RC_EV_SCAN_READ_ERROR);
			return;
		}
	}
	r = rst_recover(NULL, &rr);
	if (r == 0 || r == -EINVAL) {
		/* -EINVAL: the flag was already clear (nothing to scan); the scan is done either way */
		sys_put_le32(rr.recording_id, args);
		sys_put_le32(rr.chunks_kept, &args[4]);
		sys_put_le32(rr.head_chunk_seq, &args[8]);
		rrec_log(RREC_LOG_RECOVERY_DONE, args, 12);
		rglue_event(RC_EV_SCAN_DONE);
	} else {
		sys_put_le32(0, args);   /* rst.h does not give the LBA of the read error */
		sys_put_le32((uint32_t)r, &args[4]);
		rrec_log(RREC_LOG_FAULT_SCAN_READ, args, 8);
		rglue_event(RC_EV_SCAN_READ_ERROR);
	}
}

/* ERR_STORAGE_FAULT, every 60 s: run the storage init and report the result (FW l.191 to l.194, ruling R3) */
static void run_retry(void)
{
	struct rst_mount_info mi;
	uint8_t args[4];
	int r;

	r = rst_mounted() ? 0 : rst_mount(false, &mi);
	if (r == 0 && rst_mounted()) {
		rrec_st.fact_open = mi.open_flag;
		rrec_st.fact_open_pending = true;
	}
	sys_put_le32((uint32_t)r, args);
	rrec_log(RREC_LOG_STORAGE_RETRY, args, sizeof(args));
	rglue_event(r == 0 ? RC_EV_STORAGE_RETRY_OK : RC_EV_STORAGE_RETRY_FAILED);
}

static void rrec_thread_fn(void *p1, void *p2, void *p3)
{
	struct job j;

	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);
	for (;;) {
		if (k_msgq_get(&job_q, &j, K_FOREVER) != 0) {
			continue;
		}
		switch (j.kind) {
		case RREC_JOB_EVENT:
			rglue_event((enum rc_event)j.arg);
			break;
		case RREC_JOB_BATTERY:
			rglue_battery((enum rc_batt)j.arg);
			break;
		case RREC_JOB_RECOVER:
			run_recover();
			break;
		case RREC_JOB_RETRY:
			run_retry();
			break;
		default:
			break;
		}
		(void)atomic_inc(&done);
	}
}

/* ------------------------------------------------------------------ battery values to the screens (FW l.374) */
static struct k_work_delayable batt_work;

static void batt_refresh(struct k_work *w)
{
	struct rpw_values v;

	ARG_UNUSED(w);
	rpw_values(&v);
	rscr_set_battery((uint8_t)(v.soc_x10 / 10u), v.charging, v.full, v.to_full_min);
	(void)k_work_reschedule(&batt_work, K_MSEC(RREC_SAMPLE_REC_MS));
}

void rrec_bridge_start(void)
{
	if (thread_up) {
		return;
	}
	thread_up = true;
	k_work_init_delayable(&batt_work, batt_refresh);
	(void)k_thread_create(&rrec_thread, rrec_stack, K_THREAD_STACK_SIZEOF(rrec_stack), rrec_thread_fn, NULL, NULL, NULL,
			      CONFIG_RING_RECORDER_PRIO, 0, K_NO_WAIT);
	k_thread_name_set(&rrec_thread, "rrec");
	(void)k_work_reschedule(&batt_work, K_NO_WAIT);
}

/* ------------------------------------------------------------------ power (ring_power) */
static void pw_level(uint8_t level)
{
	rau_set_b15(level >= RC_BATT_B15);                    /* flag bit 6 of the next chunks (FW l.547) */
	(void)rrec_post(RREC_JOB_BATTERY, level);             /* rc_core_battery through rglue_battery (P11) */
}

static void pw_vbus(bool present)
{
	(void)rrec_post(RREC_JOB_EVENT, present ? RC_EV_VBUS_IN : RC_EV_VBUS_OUT);
}

static void pw_charge_error(uint8_t reason, uint8_t sensor)
{
	rrec_st.chg_err_reason = reason;
	rrec_st.chg_err_sensor = sensor;
	(void)rrec_post(RREC_JOB_EVENT, RC_EV_CHARGE_ERROR);
}

static void pw_ilim(bool first, uint16_t mv, uint32_t count)
{
	ARG_UNUSED(mv);
	ARG_UNUSED(count);
	if (first) {
		rscr_ilim_active();   /* FW l.992: off 10 s, SCR_REC_DIM in RECORDING; the power part logged the reading */
	}
}

static const struct rpw_cb power_cb = {
	.level = pw_level,
	.vbus = pw_vbus,
	.charge_error = pw_charge_error,
	.ilim = pw_ilim,
	.log = rrec_log,
};

const struct rpw_cb *rrec_power_cb(void)
{
	return &power_cb;
}

/* ------------------------------------------------------------------ storage (ring_store) */
static void st_s30(uint32_t free_chunks)
{
	uint8_t args[4];

	sys_put_le32(free_chunks, args);
	rrec_log(RREC_LOG_STORAGE_S30, args, sizeof(args));
	(void)rrec_post(RREC_JOB_EVENT, RC_EV_STORAGE_S30);
}

static void st_sfull(uint32_t free_chunks)
{
	uint8_t args[4];

	sys_put_le32(free_chunks, args);
	rrec_log(RREC_LOG_STORAGE_SFULL, args, sizeof(args));
	(void)rrec_post(RREC_JOB_EVENT, RC_EV_STORAGE_SFULL);
}

static void st_write_fault(int err)
{
	uint8_t args[8];

	sys_put_le32(0, args);   /* rst_cb gives no chunk_seq */
	sys_put_le32((uint32_t)err, &args[4]);
	rrec_log(RREC_LOG_FAULT_CHUNK_WRITE, args, sizeof(args));
	(void)rrec_post(RREC_JOB_EVENT, RC_EV_CHUNK_WRITE_FAILED);
}

static const struct rst_cb store_cb = {
	.s30 = st_s30,
	.sfull = st_sfull,
	.write_fault = st_write_fault,
};

const struct rst_cb *rrec_store_cb(void)
{
	return &store_cb;
}

/* ------------------------------------------------------------------ audio (ring_audio) */
static rst_chunk_done_fn audio_done;

static void chunk_written(struct rst_chunk *c, int err)
{
	rst_chunk_done_fn fn = audio_done;

	if (err == 0) {
		rsy_progress(RSY_THREAD_STORAGE);   /* the storage thread wrote a chunk (FW l.1065) */
	}
	if (fn != NULL) {
		fn(c, err);
	}
}

static int au_put(struct rst_chunk *c, rst_chunk_done_fn done)
{
	rsy_progress(RSY_THREAD_AUDIO);             /* the audio thread filled a chunk (FW l.1065) */
	rrec_feed_test_blocks(c);                  /* only while a factory test recording runs */
	audio_done = done;
	return rst_put_chunk(c, chunk_written);
}

static void au_no_block(void)
{
	uint8_t args[4];

	sys_put_le32(0, args);
	rrec_log(RREC_LOG_FAULT_MIC, args, sizeof(args));
	if (!rrec_st.test_recording) {
		(void)rrec_post(RREC_JOB_EVENT, RC_EV_MIC_NO_BLOCK);   /* FW l.169 */
	}
}

static void au_dropout(uint32_t recording_id, uint32_t chunk_in_recording, uint8_t block)
{
	uint8_t args[9];

	sys_put_le32(recording_id, args);
	sys_put_le32(chunk_in_recording, &args[4]);
	args[8] = block;
	rrec_log(RREC_LOG_DROPOUT, args, sizeof(args));   /* FW l.430: "is logged" */
}

#if defined(__has_include)
#if __has_include(<app_version.h>)
#include <app_version.h>
#define RREC_FW_VERSION ((uint32_t)APPVERSION)
#endif
#endif
#ifndef RREC_FW_VERSION
#define RREC_FW_VERSION 0u   /* a test build has no app version */
#endif

static void au_chunk_facts(uint16_t *battery_mv, int16_t *temp_c_x10, uint32_t *fw_version)
{
	struct rpw_values v;

	rpw_values(&v);
	*battery_mv = v.battery_mv;     /* FW l.567 */
	*temp_c_x10 = v.die_c_x10;      /* FW l.568: die temperature */
	*fw_version = RREC_FW_VERSION;  /* FW l.571 */
}

static const struct rau_cb audio_cb = {
	.put = au_put,
	.no_block = au_no_block,
	.dropout = au_dropout,
	.chunk_facts = au_chunk_facts,
};

const struct rau_cb *rrec_audio_cb(void)
{
	return &audio_cb;
}

uint32_t rrec_fw_version(void)
{
	return RREC_FW_VERSION;
}

/* ------------------------------------------------------------------ USB (ring_xfer) */
static void xf_configured(void)
{
	if (rsy_selftest_running()) {
		rsy_selftest_pass(RSY_ITEM_USB);    /* USB enumerated again (FW l.1014) */
	}
	(void)rrec_post(RREC_JOB_EVENT, RC_EV_USB_CONFIGURED);
}

static void xf_unconfigured(void)
{
	(void)rrec_post(RREC_JOB_EVENT, RC_EV_USB_UNCONFIGURED);
}

static const struct rxf_cb xfer_cb = {
	.configured = xf_configured,
	.unconfigured = xf_unconfigured,
};

const struct rxf_cb *rrec_xfer_cb(void)
{
	return &xfer_cb;
}

/* ------------------------------------------------------------------ motor (ring_motor) */
static void mo_edge(bool high, uint64_t cycles)
{
	rau_motor_edge(high, cycles);               /* FW l.496: the audio part marks the interval */
}

static void mo_charge(uint32_t uas)
{
	rpw_motor_charge(uas);                      /* FW l.927: added to the gauge's current */
}

static void mo_started(uint8_t pattern, int64_t t_ms)
{
	uint8_t args[9];

	args[0] = pattern;
	sys_put_le64((uint64_t)t_ms, &args[1]);
	rrec_log(RREC_LOG_MOTOR_PATTERN, args, sizeof(args));   /* FW l.333: the pattern start time is logged */
}

static const struct rmo_cb motor_cb = {
	.edge = mo_edge,
	.charge = mo_charge,
	.started = mo_started,
};

const struct rmo_cb *rrec_motor_cb(void)
{
	return &motor_cb;
}
