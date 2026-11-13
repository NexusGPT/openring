/* xt.c: helpers shared by the suites of tests/xfer (unit U4). */
#include "xt.h"

static uint32_t crc_table[256];
static bool crc_ready;

uint32_t xt_crc(uint32_t prev, const uint8_t *d, size_t n)
{
	uint32_t c = ~prev;

	if (!crc_ready) {
		for (uint32_t i = 0; i < 256; i++) {
			uint32_t v = i;

			for (int b = 0; b < 8; b++) {
				v = (v & 1u) ? (v >> 1) ^ 0xEDB88320u : (v >> 1);
			}
			crc_table[i] = v;
		}
		crc_ready = true;
	}
	for (size_t i = 0; i < n; i++) {
		c = crc_table[(c ^ d[i]) & 0xFFu] ^ (c >> 8);
	}
	return ~c;
}

uint32_t xt_le(const uint8_t *p, unsigned bytes)
{
	uint32_t v = 0;

	for (unsigned i = 0; i < bytes; i++) {
		v |= (uint32_t)p[i] << (8 * i);
	}
	return v;
}

uint64_t xt_le64(const uint8_t *p)
{
	return (uint64_t)xt_le(p, 4) | ((uint64_t)xt_le(p + 4, 4) << 32);
}

void xt_put(uint8_t *p, uint64_t v, unsigned bytes)
{
	for (unsigned i = 0; i < bytes; i++) {
		p[i] = (uint8_t)(v >> (8 * i));
	}
}

size_t xt_req(uint8_t *out, uint8_t op, uint32_t tag, const void *payload, uint32_t plen)
{
	xt_put(out, 0x5252, 2);
	out[2] = op;
	out[3] = 0;
	xt_put(out + 4, tag, 4);
	xt_put(out + 8, plen, 4);
	xt_put(out + 12, plen == 0 ? 0u : xt_crc(0, payload, plen), 4);
	if (plen != 0) {
		memcpy(out + 16, payload, plen);
	}
	return 16u + plen;
}

/* ---- fake backend */
struct fake fk;

uint8_t fake_chunk_byte(uint32_t rec, uint32_t chunk, uint32_t i)
{
	return (uint8_t)(rec * 31u + chunk * 7u + i * 13u + (i >> 8));
}

static bool f_may(void)
{
	return fk.allowed;
}

static enum rrec_status f_info(uint8_t out[RREC_GET_INFO_BYTES])
{
	fk.calls[RREC_OP_GET_INFO]++;
	for (unsigned i = 0; i < RREC_GET_INFO_BYTES; i++) {
		out[i] = (uint8_t)(0xA0u + i);
	}
	return fk.st[RREC_OP_GET_INFO];
}

static enum rrec_status f_list(uint32_t first, uint16_t max, uint8_t *out, size_t *len)
{
	fk.calls[RREC_OP_LIST_RECORDINGS]++;
	fk.last_first = first;
	fk.last_max = max;
	/* count = max, entries filled with a pattern, up to the size the test asked for */
	xt_put(out, max, 2);
	for (size_t i = 2; i < fk.list_len; i++) {
		out[i] = (uint8_t)i;
	}
	*len = fk.list_len;
	return fk.st[RREC_OP_LIST_RECORDINGS];
}

static enum rrec_status f_range(uint32_t rec, uint32_t first, uint32_t count)
{
	fk.calls[RREC_OP_READ_RANGE]++;
	fk.last_rec = rec;
	fk.last_first = first;
	fk.last_count = count;
	return fk.st[RREC_OP_READ_RANGE];
}

static enum rrec_status f_read(uint32_t rec, uint32_t chunk, uint8_t *out)
{
	fk.read_calls++;
	if (fk.fail_read_at != 0 && fk.read_calls == fk.fail_read_at) {
		return RREC_ST_STORAGE_ERROR;
	}
	for (uint32_t i = 0; i < RREC_CHUNK_BYTES; i++) {
		out[i] = fake_chunk_byte(rec, chunk, i);
	}
	if (fk.change_read_at != 0 && fk.read_calls == fk.change_read_at) {
		out[100] ^= 0x01;
	}
	return RREC_ST_OK;
}

static enum rrec_status f_confirm(uint32_t rec, uint32_t digest)
{
	fk.calls[RREC_OP_CONFIRM]++;
	fk.last_rec = rec;
	fk.last_digest = digest;
	return fk.st[RREC_OP_CONFIRM];
}

static enum rrec_status f_del(uint32_t rec, uint32_t *free_after)
{
	fk.calls[RREC_OP_DELETE]++;
	fk.last_rec = rec;
	*free_after = fk.free_after;
	return fk.st[RREC_OP_DELETE];
}

static enum rrec_status f_time(int64_t utc_ms, int16_t tz)
{
	fk.calls[RREC_OP_SET_TIME]++;
	fk.last_utc_ms = utc_ms;
	fk.last_tz = tz;
	return fk.st[RREC_OP_SET_TIME];
}

static enum rrec_status f_batt(uint8_t out[RREC_GET_BATTERY_BYTES])
{
	fk.calls[RREC_OP_GET_BATTERY]++;
	for (unsigned i = 0; i < RREC_GET_BATTERY_BYTES; i++) {
		out[i] = (uint8_t)(0x50u + i);
	}
	if (fk.hook != NULL) {
		fk.hook();
	}
	return fk.st[RREC_OP_GET_BATTERY];
}

static enum rrec_status f_fwb(uint32_t size, uint32_t crc)
{
	fk.calls[RREC_OP_FW_BEGIN]++;
	fk.last_image_size = size;
	fk.last_image_crc = crc;
	return fk.st[RREC_OP_FW_BEGIN];
}

static enum rrec_status f_fwd(uint32_t offset, const uint8_t *data, size_t len)
{
	fk.calls[RREC_OP_FW_DATA]++;
	fk.last_fw_offset = offset;
	fk.last_fw_len = len;
	fk.last_fw_first = data[0];
	fk.last_fw_lastbyte = data[len - 1];
	return fk.st[RREC_OP_FW_DATA];
}

static enum rrec_status f_fwe(void)
{
	fk.calls[RREC_OP_FW_END]++;
	return fk.st[RREC_OP_FW_END];
}

static enum rrec_status f_log(uint32_t first, uint16_t max, uint8_t *out, size_t *len)
{
	fk.calls[RREC_OP_GET_LOG]++;
	fk.last_first = first;
	fk.last_max = max;
	xt_put(out, max, 2);
	for (size_t i = 2; i < fk.log_len; i++) {
		out[i] = (uint8_t)(i * 3u);
	}
	*len = fk.log_len;
	return fk.st[RREC_OP_GET_LOG];
}

static enum rrec_status f_factory(const uint8_t *req, size_t len, uint8_t *out, size_t *out_len)
{
	fk.calls[RREC_OP_FACTORY]++;
	fk.last_factory_len = len;
	memcpy(fk.last_factory, req, MIN(len, sizeof(fk.last_factory)));
	for (size_t i = 0; i < fk.factory_out_len; i++) {
		out[i] = (uint8_t)(0xC0u + i);
	}
	*out_len = fk.factory_out_len;
	return fk.st[RREC_OP_FACTORY];
}

static void f_after(uint8_t op, enum rrec_status st, uint32_t tag, uint32_t len)
{
	fk.after_calls++;
	fk.after_op = op;
	fk.after_st = st;
	fk.after_tag = tag;
	fk.after_len = len;
	fk.after_seq = ++fk.seq;
	fk.after_packets = rhw_sim_log_count_kind(RHW_EV_USB_PACKET);
}

static const struct rxf_backend fake_backend = {
	.may_answer = f_may, .get_info = f_info, .list = f_list, .range_check = f_range, .read_chunk = f_read,
	.confirm = f_confirm, .del = f_del, .set_time = f_time, .get_battery = f_batt, .fw_begin = f_fwb,
	.fw_data = f_fwd, .fw_end = f_fwe, .get_log = f_log, .factory = f_factory, .after_response = f_after,
};

const struct rxf_backend *fake_be(void)
{
	return &fake_backend;
}

void fake_reset(void)
{
	memset(&fk, 0, sizeof(fk));
	fk.allowed = true;
	fk.list_len = 2 + 3 * RREC_LIST_ENTRY_BYTES;
	fk.log_len = 2 + 2 * RREC_LOG_RECORD_BYTES;
	fk.free_after = 777;
	fk.factory_out_len = 3;
}

/* ---- capture */
struct cap cap;
struct rxf_ctx xctx;

void cap_reset(uint32_t mps)
{
	cap.total = 0;
	cap.pieces = 0;
	cap.bad_pieces = 0;
	cap.last_flags = 0;
	cap.mps = mps;
	cap.pcrc = 0;
	cap.fail_after = 0;
	cap.last_seen_then_more = false;
}

int cap_emit(void *user, const uint8_t *d, size_t n, bool last)
{
	ARG_UNUSED(user);
	if (cap.last_flags != 0) {
		cap.last_seen_then_more = true;
	}
	cap.pieces++;
	fk.seq++;
	if (cap.fail_after != 0 && cap.pieces >= (uint32_t)cap.fail_after) {
		return -EIO;
	}
	if (!last && (n % cap.mps) != 0) {
		cap.bad_pieces++;
	}
	if (last) {
		cap.last_flags++;
	}
	/* the reference CRC covers what follows the header */
	if (cap.total >= RREC_MSG_HEADER_BYTES) {
		cap.pcrc = xt_crc(cap.pcrc, d, n);
	} else {
		size_t skip = RREC_MSG_HEADER_BYTES - cap.total;

		if (n > skip) {
			cap.pcrc = xt_crc(cap.pcrc, d + skip, n - skip);
		}
	}
	if (cap.total < CAP_MAX) {
		memcpy(cap.buf + cap.total, d, MIN(n, CAP_MAX - cap.total));
	}
	cap.total += n;
	return 0;
}

int xt_run(uint32_t mps, const uint8_t *req, size_t n, struct rxf_result *res)
{
	cap_reset(mps);
	return rxf_proto_handle(&xctx, mps, req, n, cap_emit, NULL, res);
}

uint8_t cap_status(void)
{
	return cap.buf[3];
}

uint32_t cap_len(void)
{
	return xt_le(cap.buf + 8, 4);
}

uint32_t cap_tag(void)
{
	return xt_le(cap.buf + 4, 4);
}

uint32_t cap_crc(void)
{
	return xt_le(cap.buf + 12, 4);
}
