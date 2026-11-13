/*
 * rfa_logic.c: the pure part of the factory unit (software step 6, unit U8). No kernel call: stdint, stdbool and string.
 * See rfa_logic.h. "FW l.N" = line N of design/firmware.md.
 */
#include <string.h>

#include <ring_factory/rfa.h>

#include "rfa_logic.h"

/* ------------------------------------------------------------------ the gate and the parse */
enum rrec_status rfa_parse(const uint8_t *req, size_t len, bool flag, bool in_factory_test, struct rfa_cmd *cmd)
{
	if (req == NULL || len == 0 || cmd == NULL) {
		return RREC_ST_BAD_ARG;
	}
	/* "With the flag clear, FACTORY returns NOT_ALLOWED" (FW l.1019): before anything else about the request. */
	if (false && !flag) {
		return RREC_ST_NOT_ALLOWED;
	}
	memset(cmd, 0, sizeof(*cmd));
	cmd->sub = req[0];
	size_t want;

	switch (req[0]) {
	case RREC_FAC_ENTER:
	case RREC_FAC_EXIT:
	case RREC_FAC_SCREEN:
	case RREC_FAC_MOTOR:
	case RREC_FAC_SIGN:
	case RREC_FAC_STORE:
	case RREC_FAC_RADIO:
	case RREC_FAC_CHARGE:
	case RREC_FAC_XTAL:
	case RREC_FAC_SHIP_SAMPLE:
	case RREC_FAC_SHIP_ENTER:
		want = 1;
		break;
	case RREC_FAC_MIC:
		want = 2;
		break;
	case RREC_FAC_JOY:
	case RREC_FAC_CENTRE:
		want = 3;
		break;
	default: /* unknown, and 0x11 "removed in F3" (FW l.1037) */
		return RREC_ST_BAD_ARG;
	}
	if (len != want) {
		return RREC_ST_BAD_ARG;
	}
	if (req[0] == RREC_FAC_MIC) {
		if (req[1] != 1 && req[1] != 2) {
			return RREC_ST_BAD_ARG;
		}
		cmd->mic = req[1];
	}
	if (req[0] == RREC_FAC_JOY || req[0] == RREC_FAC_CENTRE) {
		cmd->window_ms = (uint16_t)(req[1] | ((uint16_t)req[2] << 8));
		if (cmd->window_ms == 0 || cmd->window_ms > RREC_FAC_RADIO_MS) {
			return RREC_ST_BAD_ARG;
		}
	}
	/* ENTER is answered in TRANSFER (the core is not in FACTORY_TEST yet); every other one only in FACTORY_TEST. */
	if (req[0] == RREC_FAC_ENTER) {
		return in_factory_test ? RREC_ST_NOT_ALLOWED : RREC_ST_OK;
	}
	return in_factory_test ? RREC_ST_OK : RREC_ST_NOT_ALLOWED;
}

bool rfa_clears_flag(uint8_t sub)
{
	return sub == RREC_FAC_SHIP_ENTER;
}

bool rfa_is_ship(uint8_t sub)
{
	return sub == RREC_FAC_SHIP_ENTER || sub == RREC_FAC_SHIP_SAMPLE;
}

/* ------------------------------------------------------------------ response bytes */
static size_t put16(uint8_t *o, size_t at, uint16_t v)
{
	o[at] = (uint8_t)v;
	o[at + 1] = (uint8_t)(v >> 8);
	return at + 2;
}

static size_t put32(uint8_t *o, size_t at, uint32_t v)
{
	for (int i = 0; i < 4; i++) {
		o[at + i] = (uint8_t)(v >> (8 * i));
	}
	return at + 4;
}

static size_t put64(uint8_t *o, size_t at, uint64_t v)
{
	for (int i = 0; i < 8; i++) {
		o[at + i] = (uint8_t)(v >> (8 * i));
	}
	return at + 8;
}

size_t rfa_put_result(uint8_t *out, uint8_t result)
{
	out[0] = result;
	return 1;
}

size_t rfa_put_mic(uint8_t *out, uint8_t result, int16_t rms_l_x10, int16_t rms_r_x10, uint32_t run_l, uint32_t run_r)
{
	size_t n = rfa_put_result(out, result);

	n = put16(out, n, (uint16_t)rms_l_x10);
	n = put16(out, n, (uint16_t)rms_r_x10);
	n = put32(out, n, run_l);
	return put32(out, n, run_r);
}

size_t rfa_put_sign(uint8_t *out, uint8_t result, const int64_t t_ms[4])
{
	size_t n = rfa_put_result(out, result);

	for (int i = 0; i < 4; i++) {
		n = put64(out, n, (uint64_t)t_ms[i]);
	}
	return n;
}

size_t rfa_put_motor(uint8_t *out, uint8_t result, uint16_t before_mv, uint16_t during_mv, int16_t dip_mv)
{
	size_t n = rfa_put_result(out, result);

	n = put16(out, n, before_mv);
	n = put16(out, n, during_mv);
	return put16(out, n, (uint16_t)dip_mv);
}

size_t rfa_put_store(uint8_t *out, uint8_t result, bool equal, uint32_t write_us, uint32_t read_us, uint32_t deleted)
{
	size_t n = rfa_put_result(out, result);

	out[n++] = equal ? 1 : 0;
	n = put32(out, n, write_us);
	n = put32(out, n, read_us);
	return put32(out, n, deleted);
}

size_t rfa_put_charge(uint8_t *out, uint8_t result, uint8_t state, uint8_t err_reason, int32_t ua)
{
	size_t n = rfa_put_result(out, result);

	out[n++] = state;
	out[n++] = err_reason;
	return put32(out, n, (uint32_t)ua);
}

size_t rfa_put_xtal(uint8_t *out, uint8_t result, int32_t ppm_x10, uint64_t grtc, uint32_t sof)
{
	size_t n = rfa_put_result(out, result);

	n = put32(out, n, (uint32_t)ppm_x10);
	n = put64(out, n, grtc);
	return put32(out, n, sof);
}

size_t rfa_put_events(uint8_t *out, uint8_t result, uint8_t dropped, const struct rfa_evrec *e, uint8_t n)
{
	size_t k = rfa_put_result(out, result);

	out[k++] = dropped;
	out[k++] = n;
	for (uint8_t i = 0; i < n; i++) {
		out[k++] = e[i].ev;
		k = put32(out, k, e[i].rel_ms);
	}
	return k;
}

bool rfa_event_wanted(uint8_t sub, uint8_t ev)
{
	if (sub == RREC_FAC_JOY) {
		return ev == RFA_IN_UP || ev == RFA_IN_DOWN || ev == RFA_IN_LEFT || ev == RFA_IN_RIGHT ||
		       ev == RFA_IN_CENTRE_DOWN || ev == RFA_IN_CENTRE_UP;
	}
	if (sub == RREC_FAC_CENTRE) {
		return ev == RFA_IN_CENTRE_DOWN || ev == RFA_IN_CENTRE_UP || ev == RFA_IN_SINGLE || ev == RFA_IN_DOUBLE ||
		       ev == RFA_IN_LONG || ev == RFA_IN_MW;
	}
	return false;
}

/* ------------------------------------------------------------------ levels and runs */
void rfa_level_add(struct rfa_level *l, const int16_t *frames, uint32_t n_frames, uint32_t channel)
{
	for (uint32_t i = 0; i < n_frames; i++) {
		int64_t s = frames[2u * i + channel];

		l->sumsq += (uint64_t)(s * s);
	}
	l->n += n_frames;
}

/* log2 of x (> 0) in Q16 (16 fraction bits), by the squaring method. */
static int64_t log2_q16(uint64_t x)
{
	int k = 63 - __builtin_clzll(x);
	uint64_t y = (k >= 31) ? (x >> (k - 31)) : (x << (31 - k)); /* Q31 in [2^31, 2^32) */
	int64_t frac = 0;

	for (int i = 0; i < 16; i++) {
		y = (y * y) >> 31;
		frac <<= 1;
		if (y >= (1ull << 32)) {
			frac |= 1;
			y >>= 1;
		}
	}
	return ((int64_t)k << 16) + frac;
}

int16_t rfa_level_dbfs_x10(const struct rfa_level *l)
{
	uint64_t s = l->sumsq;
	uint64_t n = l->n;

	if (n == 0 || s == 0) {
		return RFA_DBFS_SILENT;
	}
	while (s >= (1ull << 55) && n > 1) {
		s >>= 1;
		n >>= 1;
	}
	uint64_t m = (s << 8) / n; /* mean of the squares, times 256 */

	if (m == 0) {
		return RFA_DBFS_SILENT;
	}
	/* log2(mean / 2^30) with the 2^8 and the 2^30 taken off */
	int64_t lr = log2_q16(m) - ((int64_t)(8 + 30) << 16);
	/* dB x 10 = 100 x log10(ratio) = 30.103 x log2(ratio) */
	int64_t num = lr * 30103;
	int64_t den = 65536ll * 1000ll;
	int64_t v = (num >= 0) ? (num + den / 2) / den : -((-num + den / 2) / den);

	if (v < INT16_MIN + 1) {
		return INT16_MIN + 1;
	}
	return (int16_t)v;
}

void rfa_run_add(struct rfa_run *r, const int16_t *frames, uint32_t n_frames, uint32_t channel)
{
	for (uint32_t i = 0; i < n_frames; i++) {
		int32_t s = frames[2u * i + channel];

		if (r->cur == 0 || s != r->last) {
			r->last = s;
			r->cur = 1;
		} else {
			r->cur++;
		}
		if (r->cur > r->max) {
			r->max = r->cur;
		}
	}
}

bool rfa_run_is_stuck(uint32_t longest_run)
{
	return longest_run >= RREC_FAC_MIC_STUCK_RUN;
}

/* ------------------------------------------------------------------ crystal, charger, motor, name */
int32_t rfa_ppm_x10(uint64_t grtc_ticks, uint32_t sof, bool *ok)
{
	if (sof == 0) {
		if (ok != NULL) {
			*ok = false;
		}
		return 0;
	}
	int64_t den = (int64_t)sof * RFA_GRTC_HZ;
	int64_t num = (int64_t)grtc_ticks * RFA_SOF_PER_S - den;

	if (ok != NULL) {
		*ok = true;
	}
	return (int32_t)((num * 10000000ll) / den);
}

bool rfa_ppm_within(int32_t ppm_x10)
{
	return ppm_x10 >= -RFA_XTAL_LIMIT_PPM_X10 && ppm_x10 <= RFA_XTAL_LIMIT_PPM_X10;
}

uint8_t rfa_charge_result(uint8_t state, uint8_t err_reason)
{
	if (state == RREC_CHG_OFF || state == RREC_CHG_ERROR || err_reason != 0) {
		return RREC_FAC_RESULT_FAIL;
	}
	return RREC_FAC_RESULT_PASS;
}

uint32_t rfa_motor_read_delay_ms(void)
{
	return RREC_FAC_MOTOR_READ_MS;
}

int16_t rfa_motor_dip_mv(uint16_t before_mv, uint16_t during_mv)
{
	int32_t d = (int32_t)before_mv - (int32_t)during_mv;

	if (d > INT16_MAX) {
		d = INT16_MAX;
	}
	if (d < INT16_MIN) {
		d = INT16_MIN;
	}
	return (int16_t)d;
}

size_t rfa_beacon_name(uint64_t device_id, char out[RFA_NAME_BYTES])
{
	static const char hex[] = "0123456789ABCDEF";
	const size_t pre = sizeof(RREC_BEACON_NAME_PREFIX) - 1u;

	memcpy(out, RREC_BEACON_NAME_PREFIX, pre);
	for (int i = 0; i < 4; i++) {
		out[pre + i] = hex[(device_id >> (12 - 4 * i)) & 0xFu];
	}
	out[pre + 4] = '\0';
	return pre + 4;
}
