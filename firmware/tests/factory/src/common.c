#include "common.h"

int fx_sign_answer;
uint32_t fx_sign_calls;
uint32_t fx_sign_at_log;
uint32_t fx_rec_calls;
uint8_t fx_rec_type = RREC_REC_TYPE_FACTORY;
uint32_t fx_frames_seen;
uint8_t fx_frame[FX_MAX_FRAMES];
int64_t fx_frame_ms[FX_MAX_FRAMES];
int64_t fx_frame_ticks[FX_MAX_FRAMES];
uint32_t fx_frames;
int fx_screen_rc;
uint64_t fx_xtal_grtc;
uint32_t fx_xtal_sof;
int fx_xtal_rc = -ENOTSUP;

static void (*tap_cb)(const int16_t *frames, uint32_t n);

/* ------------------------------------------------------------------ the recording path of the join, as a stand-in */
static void tap(const struct rst_chunk *c)
{
	const int16_t *p = (const int16_t *)(c->bytes + RREC_CHUNK_HEADER_BYTES);

	for (uint32_t off = 0; off < c->hdr.frames; off += RREC_BLOCK_FRAMES) {
		uint32_t n = c->hdr.frames - off;

		if (n > RREC_BLOCK_FRAMES) {
			n = RREC_BLOCK_FRAMES;
		}
		if (tap_cb != NULL) {
			tap_cb(p + 2u * off, n);
		}
		fx_frames_seen += n;
	}
}

static int fx_put(struct rst_chunk *c, rst_chunk_done_fn done)
{
	tap(c);
	return rst_put_chunk(c, done);
}

static void fx_log(uint16_t code, const uint8_t *args, size_t nargs)
{
	ARG_UNUSED(code);
	ARG_UNUSED(args);
	ARG_UNUSED(nargs);
}

int fx_test_recording(uint32_t ms, void (*on_block)(const int16_t *frames, uint32_t n), int64_t *mic_on_ms,
		      int64_t *mic_off_ms)
{
	struct rst_mount_info mi;
	struct rau_cut_result cut;
	bool mounted_here = false;
	uint32_t id = 0;
	int rc;

	fx_rec_calls++;
	tap_cb = on_block;
	if (!rst_mounted()) {
		rc = rst_mount(false, &mi);
		if (rc < 0) {
			return rc;
		}
		mounted_here = true;
	} else {
		memset(&mi, 0, sizeof(mi));
	}
	rc = rst_open(fx_rec_type, 0, &id);
	if (rc < 0) {
		return rc;
	}
	rc = rau_prepare(100);
	if (rc < 0) {
		return rc;
	}
	/* rec_mics_on() of the join: the sign first, VDD_MIC only on an answer of 0 */
	fx_sign_calls++;
	fx_sign_at_log = rhw_sim_log_count();
	if (fx_sign_answer != 0) {
		struct rst_close_args none;

		memset(&none, 0, sizeof(none));
		(void)rau_release();
		(void)rst_close(NULL, &none);
		if (mounted_here) {
			(void)rst_unmount();
		}
		return -ENODEV;
	}
	rc = rhw_pmic()->rail_set(RHW_RAIL_MIC, true, "rec_mics_on");
	if (rc < 0) {
		return rc;
	}
	*mic_on_ms = rhw_clock()->now_ms();
	k_sleep(K_MSEC(RREC_MIC_RAIL_WAIT_MS));
	struct rau_start_args a = {
		.recording_id = id, .recording_type = fx_rec_type, .boot_count = mi.boot_count, .time_set = false,
	};

	rc = rau_start(&a);
	if (rc < 0) {
		return rc;
	}
	int64_t t0 = rhw_clock()->now_ms();

	k_sleep(K_MSEC(ms));
	rc = rau_cut(t0 + ms, &cut);
	if (rc < 0) {
		return rc;
	}
	if (cut.last != NULL) {
		tap(cut.last);
	}
	rc = rst_close(cut.last, &cut.close);
	(void)rau_halt();
	(void)rhw_pmic()->rail_set(RHW_RAIL_MIC, false, "rec_mics_off");
	*mic_off_ms = rhw_clock()->now_ms();
	(void)rau_release();
	if (mounted_here) {
		(void)rst_unmount();
	}
	return rc < 0 ? rc : 0;
}

/* ------------------------------------------------------------------ the other stand-ins */
int fx_screen_frame(uint8_t which)
{
	if (fx_frames < FX_MAX_FRAMES) {
		fx_frame[fx_frames] = which;
		fx_frame_ms[fx_frames] = rhw_clock()->now_ms();
		fx_frame_ticks[fx_frames] = k_uptime_ticks();
	}
	fx_frames++;
	return fx_screen_rc;
}

static int fx_motor_on(uint32_t ms)
{
	/* the join's motor_on: MOTOR high for ms (ring_motor has patterns only; see factory-notes.md) */
	rhw_motor()->set(true);
	k_sleep(K_MSEC(ms));
	rhw_motor()->set(false);
	return 0;
}

static int fx_vbat(uint16_t *mv)
{
	struct rhw_pmic_sample s;
	int rc = rhw_pmic()->sample(&s);

	if (rc == 0) {
		*mv = s.mv;
	}
	return rc;
}

static int fx_charge(uint8_t *state, uint8_t *err, int32_t *ua)
{
	struct rhw_pmic_charge c;
	struct rhw_pmic_sample s;
	int rc = rhw_pmic()->charge_status(&c);

	if (rc == 0) {
		rc = rhw_pmic()->sample(&s);
	}
	if (rc == 0) {
		*state = c.state;
		*err = c.err_reason;
		*ua = s.ua;
	}
	return rc;
}

static int fx_xtal(uint64_t *grtc, uint32_t *sof)
{
	if (fx_xtal_rc != 0) {
		return fx_xtal_rc;
	}
	*grtc = fx_xtal_grtc;
	*sof = fx_xtal_sof;
	return 0;
}

struct rfa_ops fx_ops = {
	.test_recording = fx_test_recording,
	.screen_frame = fx_screen_frame,
	.motor_on = fx_motor_on,
	.vbat_mv = fx_vbat,
	.store_test = NULL, /* the built-in T-STORE of the factory part (ring_store) */
	.charge = fx_charge,
	.xtal_counts = fx_xtal,
	.flag = rsy_factory_flag,
	.flag_set = rsy_factory_flag_set,
};

/* ------------------------------------------------------------------ setup */
void fx_flag(bool on)
{
	struct rhw_persist p;

	memset(&p, 0, sizeof(p));
	p.factory_flag = on ? 1 : 0;
	rhw_sim_persist_set(&p);
	zassert_ok(rsy_init(fx_log), "rsy_init");
}

void fx_before(void *f)
{
	ARG_UNUSED(f);
	rpw_priv_reset();
	rhw_sim_reset();
	fx_sign_answer = 0;
	fx_sign_calls = 0;
	fx_sign_at_log = 0;
	fx_rec_calls = 0;
	fx_rec_type = RREC_REC_TYPE_FACTORY;
	fx_frames_seen = 0;
	fx_frames = 0;
	fx_screen_rc = 0;
	fx_xtal_rc = -ENOTSUP;
	tap_cb = NULL;
	zassert_ok(rst_init(NULL), "rst_init");
	struct rau_cb cb = { .put = fx_put };

	zassert_ok(rau_init(&cb), "rau_init");
	fx_flag(true);
	zassert_ok(rfa_init(&fx_ops), "rfa_init");
	rhw_sim_log_clear();
}

void fx_next_boot(void)
{
	rhw_sim_reboot();
	zassert_ok(rsy_init(fx_log), "rsy_init after reboot");
}

void fx_after(void *f)
{
	ARG_UNUSED(f);
	rfa_beacon_stop();
	k_sleep(K_MSEC(20));
}

enum rrec_status fx_do(const uint8_t *req, size_t n, bool in_factory_test, uint8_t *out, size_t *out_len,
		       enum rfa_effect *eff)
{
	return rfa_request(req, n, in_factory_test, out, out_len, eff);
}

enum rrec_status fx_do1(uint8_t sub, bool in_factory_test, uint8_t *out, size_t *out_len, enum rfa_effect *eff)
{
	return fx_do(&sub, 1, in_factory_test, out, out_len, eff);
}

/* ------------------------------------------------------------------ small helpers */
int32_t fx_find(uint16_t kind, uint32_t from)
{
	return rhw_sim_log_find(kind, from);
}

struct rhw_sim_ev fx_ev(uint32_t i)
{
	struct rhw_sim_ev e;

	zassert_true(rhw_sim_log_get(i, &e), "event %u exists", i);
	return e;
}

uint32_t fx_count(uint16_t kind)
{
	return rhw_sim_log_count_kind(kind);
}

uint32_t fx_mic_on_events(void)
{
	uint32_t n = 0;
	struct rhw_sim_ev e;

	for (uint32_t i = 0; i < rhw_sim_log_count(); i++) {
		if (rhw_sim_log_get(i, &e) && e.kind == RHW_EV_PMIC_RAIL && e.a0 == RHW_RAIL_MIC && e.a1 != 0) {
			n++;
		}
	}
	return n;
}

uint16_t fx_u16(const uint8_t *p)
{
	return (uint16_t)(p[0] | ((uint16_t)p[1] << 8));
}

uint32_t fx_u32(const uint8_t *p)
{
	return (uint32_t)fx_u16(p) | ((uint32_t)fx_u16(p + 2) << 16);
}

uint64_t fx_u64(const uint8_t *p)
{
	return (uint64_t)fx_u32(p) | ((uint64_t)fx_u32(p + 4) << 32);
}
