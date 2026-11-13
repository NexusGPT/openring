/*
 * rrec_backend.c: the backend of the USB transfer part (rxf.h) and the factory part's ops (rfa.h), filled by the join
 * (software step 6, unit J). Runs on the transfer thread. No command starts or stops a recording (FW l.209): the only
 * core events a command leads to are FW_END (row FW l.180), FACTORY_ENTER, FACTORY_EXIT, SHIP_ENTER and SHIP_SAMPLE
 * (rows FW l.181, l.201 to l.203), each posted after the response was handed to the transport.
 * "FW l.N" = line N of design/firmware.md.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/byteorder.h>

#include <ring_glue/rglue.h>
#include <ring_power/rpw.h>
#include <ring_recorder/rrec.h>
#include <ring_rhw/rhw.h>
#include <ring_screens/rscr.h>
#include <ring_store/rst.h>
#include <ring_sys/rsy.h>
#include <ring_time/rtime.h>
#include <ring_xfer/rxf.h>
#include <ring_motor/rmo.h>
#if defined(CONFIG_RING_FACTORY)
#include <ring_factory/rfa.h>
#endif

#include "rrec_int.h"

static uint32_t last_first_arg;     /* the first u32 argument of the request, for its log record */
static uint8_t pending_effect;      /* enum rfa_effect of the last FACTORY request, posted after its response */

static enum rrec_status st_of(int r)
{
	switch (r) {
	case 0:
		return RREC_ST_OK;
	case -ENOENT:
		return RREC_ST_NOT_FOUND;
	case -EACCES:
		return RREC_ST_NOT_CONFIRMED;
	case -EBADMSG:
		return RREC_ST_DIGEST_MISMATCH;
	case -EBUSY:
		return RREC_ST_BUSY;
	case -EINVAL:
		return RREC_ST_BAD_ARG;
	default:
		return RREC_ST_STORAGE_ERROR;
	}
}

static bool be_may_answer(void)
{
	enum rc_state s = rrec_core_state();

	return s == RC_ST_CHARGING || s == RC_ST_TRANSFER || s == RC_ST_FACTORY_TEST;   /* FW l.673 */
}

/* recordings not deleted, counted through the list (GET_INFO, FW l.696) */
static uint32_t count_recordings(void)
{
	static struct rst_rec_info info[RREC_LIST_MAX_MAX];
	uint32_t n = 0;
	uint32_t first = 0;

	for (;;) {
		uint16_t got = 0;

		if (rst_list(first, RREC_LIST_MAX_MAX, info, &got) != 0 || got == 0) {
			break;
		}
		n += got;
		if (got < RREC_LIST_MAX_MAX) {
			break;
		}
		first = info[got - 1].recording_id + 1u;
	}
	return n;
}

static enum rrec_status be_get_info(uint8_t out[RREC_GET_INFO_BYTES])
{
	struct rst_space sp;
	uint64_t id = 0;

	memset(out, 0, RREC_GET_INFO_BYTES);
	memset(&sp, 0, sizeof(sp));
	(void)rst_space(&sp);
	(void)rhw_clock()->device_id(&id);
	sys_put_le16(RREC_PROTOCOL_VERSION, &out[RREC_GI_OFF_PROTOCOL]);
	sys_put_le32(rrec_fw_version(), &out[RREC_GI_OFF_FW_VERSION]);
	sys_put_le64(id, &out[RREC_GI_OFF_DEVICE_ID]);
	sys_put_le32(rrec_st.card_sectors, &out[RREC_GI_OFF_CARD_SECTORS]);
	sys_put_le32(sp.total, &out[RREC_GI_OFF_CHUNK_COUNT_TOTAL]);
	sys_put_le32(sp.free_chunks, &out[RREC_GI_OFF_FREE_CHUNKS]);
	sys_put_le32(count_recordings(), &out[RREC_GI_OFF_RECORDINGS]);
	sys_put_le32(rrec_st.boot_count, &out[RREC_GI_OFF_BOOT_COUNT]);
	out[RREC_GI_OFF_FACTORY_FLAG] = rsy_factory_flag() ? 1u : 0u;
	return RREC_ST_OK;
}

static enum rrec_status be_list(uint32_t first, uint16_t max, uint8_t *out, size_t *len)
{
	static struct rst_rec_info info[RREC_LIST_MAX_MAX];
	uint16_t got = 0;
	int r;

	last_first_arg = first;
	r = rst_list(first, max, info, &got);
	if (r != 0) {
		return st_of(r);
	}
	sys_put_le16(got, out);
	for (uint16_t i = 0; i < got; i++) {
		uint8_t *e = &out[2 + (size_t)i * RREC_LIST_ENTRY_BYTES];

		memset(e, 0, RREC_LIST_ENTRY_BYTES);
		sys_put_le32(info[i].recording_id, &e[RREC_LE_OFF_RECORDING_ID]);
		e[RREC_LE_OFF_TYPE] = info[i].type;
		e[RREC_LE_OFF_CHANNELS] = info[i].channels;
		e[RREC_LE_OFF_STATE] = info[i].state;
		sys_put_le32(info[i].first_chunk_seq, &e[RREC_LE_OFF_FIRST_CHUNK_SEQ]);
		sys_put_le32(info[i].chunk_count, &e[RREC_LE_OFF_CHUNK_COUNT]);
		sys_put_le32(info[i].sample_rate_hz, &e[RREC_LE_OFF_SAMPLE_RATE]);
		sys_put_le64((uint64_t)info[i].start_utc_ms, &e[RREC_LE_OFF_START_UTC_MS]);
		sys_put_le64(info[i].duration_frames, &e[RREC_LE_OFF_DURATION_FRAMES]);
		sys_put_le32(info[i].digest, &e[RREC_LE_OFF_DIGEST]);
		sys_put_le16(info[i].highlight_count, &e[RREC_LE_OFF_HIGHLIGHT_COUNT]);
	}
	*len = 2u + (size_t)got * RREC_LIST_ENTRY_BYTES;
	return RREC_ST_OK;
}

static enum rrec_status be_range_check(uint32_t recording_id, uint32_t first, uint32_t count)
{
	struct rst_rec_info info;
	uint16_t got = 0;
	int r;

	last_first_arg = recording_id;
	r = rst_list(recording_id, 1, &info, &got);
	if (r != 0) {
		return st_of(r);
	}
	if (got == 0 || info.recording_id != recording_id || first >= info.chunk_count ||
	    count > info.chunk_count - first) {
		return RREC_ST_NOT_FOUND;   /* also a deleted recording (FW l.661) */
	}
	return RREC_ST_OK;
}

static enum rrec_status be_read_chunk(uint32_t recording_id, uint32_t chunk, uint8_t *out)
{
	return st_of(rst_read_chunk(recording_id, chunk, out));
}

static enum rrec_status be_confirm(uint32_t recording_id, uint32_t digest)
{
	last_first_arg = recording_id;
	return st_of(rst_confirm(recording_id, digest));
}

static enum rrec_status be_del(uint32_t recording_id, uint32_t *free_after)
{
	last_first_arg = recording_id;
	return st_of(rst_delete(recording_id, free_after));
}

static enum rrec_status be_set_time(int64_t utc_ms, int16_t tz_min)
{
	last_first_arg = (uint32_t)utc_ms;
	rtime_set(utc_ms, tz_min, true);   /* FW l.701: the case gives the zone */
	return RREC_ST_OK;
}

static enum rrec_status be_get_battery(uint8_t out[RREC_GET_BATTERY_BYTES])
{
	return rpw_battery_report(out) == 0 ? RREC_ST_OK : RREC_ST_STORAGE_ERROR;
}

static enum rrec_status be_fw_begin(uint32_t image_size, uint32_t image_crc32)
{
	struct rpw_values v;

	last_first_arg = image_size;
	rpw_values(&v);
	return rsy_fw_begin(image_size, image_crc32, v.soc_x10, v.vbus);   /* FW l.1015, ruling D12 */
}

static enum rrec_status be_fw_data(uint32_t offset, const uint8_t *data, size_t len)
{
	last_first_arg = offset;
	return rsy_fw_data(offset, data, len);
}

static enum rrec_status be_fw_end(void)
{
	last_first_arg = 0;
	return rsy_fw_end();
}

static enum rrec_status be_get_log(uint32_t first, uint16_t max, uint8_t *out, size_t *len)
{
	uint16_t got = 0;
	int r;

	last_first_arg = first;
	r = rst_log_read(first, max, &out[2], &got);
	if (r != 0) {
		return st_of(r);
	}
	sys_put_le16(got, out);
	*len = 2u + (size_t)got * RREC_LOG_RECORD_BYTES;
	return RREC_ST_OK;
}

static enum rrec_status be_factory(const uint8_t *req, size_t len, uint8_t *out, size_t *out_len)
{
#if defined(CONFIG_RING_FACTORY)
	enum rfa_effect eff = RFA_EFFECT_NONE;
	enum rrec_status st;

	last_first_arg = len > 0 ? req[0] : 0;
	st = rfa_request(req, len, rrec_core_state() == RC_ST_FACTORY_TEST, out, out_len, &eff);
	pending_effect = (uint8_t)eff;
	return st;
#else
	ARG_UNUSED(req);
	ARG_UNUSED(len);
	ARG_UNUSED(out);
	*out_len = 0;
	return RREC_ST_NOT_ALLOWED;
#endif
}

static void be_after_response(uint8_t opcode, enum rrec_status st, uint32_t tag, uint32_t req_len)
{
	uint8_t args[13];

	rglue_input(RC_SW_CENTRE, true);
	k_sleep(K_MSEC(RREC_LONG_PRESS_MS + 100));
	rglue_input(RC_SW_CENTRE, false);
	/* FW l.1062: each transfer command becomes a record (code 0x0100 | opcode) */
	args[0] = (uint8_t)st;
	sys_put_le32(tag, &args[1]);
	sys_put_le32(req_len, &args[5]);
	sys_put_le32(last_first_arg, &args[9]);
	rrec_log((uint16_t)(RREC_LOG_XFER_BASE | opcode), args, sizeof(args));
	last_first_arg = 0;
	if (st != RREC_ST_OK) {
		pending_effect = 0;
		return;
	}
	switch (opcode) {
	case RREC_OP_FW_END:
		(void)rrec_post(RREC_JOB_EVENT, RC_EV_FW_END);   /* row FW l.180: request done, reboot after the OK */
		break;
	case RREC_OP_REBOOT:
		(void)rhw_image()->reboot(RHW_REBOOT_COMMAND);   /* FW l.707 */
		break;
#if defined(CONFIG_RING_FACTORY)
	case RREC_OP_FACTORY:
		switch (pending_effect) {
		case RFA_EFFECT_ENTER:
			rrec_st.fact_factory = rsy_factory_flag();
			rrec_st.fact_factory_pending = true;
			(void)rrec_post(RREC_JOB_EVENT, RC_EV_FACTORY_ENTER);
			break;
		case RFA_EFFECT_EXIT:
			(void)rrec_post(RREC_JOB_EVENT, RC_EV_FACTORY_EXIT);
			break;
		case RFA_EFFECT_SHIP_ENTER:
			(void)rrec_post(RREC_JOB_EVENT, RC_EV_SHIP_ENTER);
			break;
		case RFA_EFFECT_SHIP_SAMPLE:
			(void)rrec_post(RREC_JOB_EVENT, RC_EV_SHIP_SAMPLE);
			break;
		default:
			break;
		}
		pending_effect = 0;
		break;
#endif
	default:
		break;
	}
}

static const struct rxf_backend backend = {
	.may_answer = be_may_answer,
	.get_info = be_get_info,
	.list = be_list,
	.range_check = be_range_check,
	.read_chunk = be_read_chunk,
	.confirm = be_confirm,
	.del = be_del,
	.set_time = be_set_time,
	.get_battery = be_get_battery,
	.fw_begin = be_fw_begin,
	.fw_data = be_fw_data,
	.fw_end = be_fw_end,
	.get_log = be_get_log,
	.factory = be_factory,
	.after_response = be_after_response,
};

const struct rxf_backend *rrec_backend(void)
{
	return &backend;
}

/* ------------------------------------------------------------------ the factory part's ops (rfa.h) */
#if defined(CONFIG_RING_FACTORY)
static int fo_screen_frame(uint8_t which)
{
	/* 0 red, 1 green, 2 blue, 3 white, 4 black, 5 grid (rfa.h) = the frames after FAC_NONE (rscr_logic.h) */
	return rscr_factory_frame((enum rscr_fac_frame)(FAC_NONE + 1 + which));
}

static int fo_motor_on(uint32_t ms)
{
	/* T-MOTOR (FW l.1028; lead's ruling 2): rmo.h plays the seven patterns only, so in FACTORY_TEST the join stops the
	 * player and drives MOTOR through rhw_motor() for ms; the pulse's charge goes to the gauge (FW l.332's formula) */
	int r;

	if (rrec_core_state() != RC_ST_FACTORY_TEST) {
		return -EPERM;
	}
	rmo_stop();
	r = rhw_motor()->set(true);
	k_sleep(K_MSEC(ms));
	(void)rhw_motor()->set(false);
	rpw_motor_charge(ms * RREC_MOTOR_RUN_MA + RREC_MOTOR_START_MS * RREC_MOTOR_START_MA);
	return r;
}

static int fo_vbat_mv(uint16_t *mv)
{
	int32_t ua;

	return rpw_sample_now(mv, &ua);   /* a sample now, taken by the power thread (lead's ruling 3) */
}

static int fo_charge(uint8_t *state, uint8_t *err_reason, int32_t *ua)
{
	return rpw_charger_now(state, err_reason, ua);   /* read by the power thread (lead's ruling 3) */
}

static int fo_xtal_counts(uint64_t *grtc, uint32_t *sof)
{
	ARG_UNUSED(grtc);
	ARG_UNUSED(sof);
	return -ENOTSUP;   /* no start-of-frame count in rhw.h (simulation and kit build alike) */
}

static bool fo_flag(void)
{
	return rsy_factory_flag();
}

static int fo_flag_set(bool on)
{
	int r = rsy_factory_flag_set(on);

	rrec_st.fact_factory = on;
	rrec_st.fact_factory_pending = true;
	return r;
}

static const struct rfa_ops factory_ops = {
	.test_recording = rrec_test_recording,
	.screen_frame = fo_screen_frame,
	.motor_on = fo_motor_on,
	.vbat_mv = fo_vbat_mv,
	.store_test = NULL,   /* the factory part's own T-STORE through rst.h */
	.charge = fo_charge,
	.xtal_counts = fo_xtal_counts,
	.flag = fo_flag,
	.flag_set = fo_flag_set,
};

const struct rfa_ops *rrec_factory_ops(void)
{
	return &factory_ops;
}
#endif
