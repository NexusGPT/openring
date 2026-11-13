/* glue.c: see glue.h. Written for the tests of unit U4. */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>

#include <ring_rhw/rhw.h>

#include "glue.h"
#include "xt.h"

struct glue_seen gl;

void glue_reset(void)
{
	memset(&gl, 0, sizeof(gl));
}

static bool g_may(void)
{
	return true;
}

static enum rrec_status map_err(int r)
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
	default:
		return RREC_ST_STORAGE_ERROR;
	}
}

static uint32_t count_recordings(void)
{
	static struct rst_rec_info e[RREC_LIST_MAX_MAX];
	uint32_t first = 0, total = 0;
	uint16_t n = 0;

	do {
		if (rst_list(first, RREC_LIST_MAX_MAX, e, &n) != 0) {
			return 0;
		}
		total += n;
		if (n != 0) {
			first = e[n - 1].recording_id + 1u;
		}
	} while (n == RREC_LIST_MAX_MAX);
	return total;
}

static enum rrec_status g_info(uint8_t out[RREC_GET_INFO_BYTES])
{
	struct rst_space sp;
	uint64_t id = 0;
	uint32_t sectors = 0;

	memset(out, 0, RREC_GET_INFO_BYTES);
	if (rst_space(&sp) != 0) {
		return RREC_ST_STORAGE_ERROR;
	}
	(void)rhw_clock()->device_id(&id);
	/* sector count from the card as the store mounted it */
	(void)rhw_disk()->sector_count(&sectors);
	xt_put(out + RREC_GI_OFF_PROTOCOL, RREC_PROTOCOL_VERSION, 2);
	xt_put(out + RREC_GI_OFF_FW_VERSION, GLUE_FW_VERSION, 4);
	xt_put(out + RREC_GI_OFF_DEVICE_ID, id, 8);
	xt_put(out + RREC_GI_OFF_CARD_SECTORS, sectors, 4);
	xt_put(out + RREC_GI_OFF_CHUNK_COUNT_TOTAL, sp.total, 4);
	xt_put(out + RREC_GI_OFF_FREE_CHUNKS, sp.free_chunks, 4);
	xt_put(out + RREC_GI_OFF_RECORDINGS, count_recordings(), 4);
	xt_put(out + RREC_GI_OFF_BOOT_COUNT, gl.boot_count, 4);
	out[RREC_GI_OFF_FACTORY_FLAG] = gl.factory_flag ? 1 : 0;
	return RREC_ST_OK;
}

static enum rrec_status g_list(uint32_t first, uint16_t max, uint8_t *out, size_t *len)
{
	static struct rst_rec_info e[RREC_LIST_MAX_MAX];
	uint16_t n = 0;
	int r = rst_list(first, max, e, &n);

	if (r != 0) {
		return map_err(r == -EINVAL ? -EIO : r);
	}
	xt_put(out, n, 2);
	for (uint16_t i = 0; i < n; i++) {
		uint8_t *p = out + 2 + i * RREC_LIST_ENTRY_BYTES;

		memset(p, 0, RREC_LIST_ENTRY_BYTES);
		xt_put(p + RREC_LE_OFF_RECORDING_ID, e[i].recording_id, 4);
		p[RREC_LE_OFF_TYPE] = e[i].type;
		p[RREC_LE_OFF_CHANNELS] = e[i].channels;
		p[RREC_LE_OFF_STATE] = e[i].state;
		xt_put(p + RREC_LE_OFF_FIRST_CHUNK_SEQ, e[i].first_chunk_seq, 4);
		xt_put(p + RREC_LE_OFF_CHUNK_COUNT, e[i].chunk_count, 4);
		xt_put(p + RREC_LE_OFF_SAMPLE_RATE, e[i].sample_rate_hz, 4);
		xt_put(p + RREC_LE_OFF_START_UTC_MS, (uint64_t)e[i].start_utc_ms, 8);
		xt_put(p + RREC_LE_OFF_DURATION_FRAMES, e[i].duration_frames, 8);
		xt_put(p + RREC_LE_OFF_DIGEST, e[i].digest, 4);
		xt_put(p + RREC_LE_OFF_HIGHLIGHT_COUNT, e[i].highlight_count, 2);
	}
	*len = 2u + (size_t)n * RREC_LIST_ENTRY_BYTES;
	return RREC_ST_OK;
}

/* the recording exists (not deleted) and holds chunks first .. first + count - 1 */
static enum rrec_status g_range(uint32_t rec, uint32_t first, uint32_t count)
{
	static struct rst_rec_info e[1];
	uint16_t n = 0;
	int r = rst_list(rec, 1, e, &n);

	if (r != 0) {
		return RREC_ST_STORAGE_ERROR;
	}
	if (n == 0 || e[0].recording_id != rec) {
		return RREC_ST_NOT_FOUND;
	}
	if (first >= e[0].chunk_count || count > e[0].chunk_count - first) {
		return RREC_ST_NOT_FOUND;
	}
	return RREC_ST_OK;
}

static enum rrec_status g_read(uint32_t rec, uint32_t chunk, uint8_t *out)
{
	return map_err(rst_read_chunk(rec, chunk, out));
}

static enum rrec_status g_confirm(uint32_t rec, uint32_t digest)
{
	return map_err(rst_confirm(rec, digest));
}

static enum rrec_status g_del(uint32_t rec, uint32_t *free_after)
{
	return map_err(rst_delete(rec, free_after));
}

static enum rrec_status g_time(int64_t utc_ms, int16_t tz)
{
	gl.utc_ms = utc_ms;
	gl.tz = tz;
	gl.time_calls++;
	return RREC_ST_OK;
}

static enum rrec_status g_batt(uint8_t out[RREC_GET_BATTERY_BYTES])
{
	memset(out, 0, RREC_GET_BATTERY_BYTES);
	return RREC_ST_OK;
}

static enum rrec_status g_fwb(uint32_t s, uint32_t c)
{
	ARG_UNUSED(s);
	ARG_UNUSED(c);
	return RREC_ST_OK;
}

static enum rrec_status g_fwd(uint32_t o, const uint8_t *d, size_t l)
{
	ARG_UNUSED(o);
	ARG_UNUSED(d);
	ARG_UNUSED(l);
	return RREC_ST_OK;
}

static enum rrec_status g_fwe(void)
{
	return RREC_ST_OK;
}

static enum rrec_status g_log(uint32_t first, uint16_t max, uint8_t *out, size_t *len)
{
	uint16_t n = 0;
	int r = rst_log_read(first, max, out + 2, &n);

	if (r != 0) {
		return RREC_ST_STORAGE_ERROR;
	}
	xt_put(out, n, 2);
	*len = 2u + (size_t)n * RREC_LOG_RECORD_BYTES;
	return RREC_ST_OK;
}

static enum rrec_status g_factory(const uint8_t *req, size_t len, uint8_t *out, size_t *out_len)
{
	ARG_UNUSED(req);
	ARG_UNUSED(len);
	ARG_UNUSED(out);
	*out_len = 0;
	return gl.factory_flag ? RREC_ST_OK : RREC_ST_NOT_ALLOWED;
}

static void g_after(uint8_t op, enum rrec_status st, uint32_t tag, uint32_t len)
{
	ARG_UNUSED(st);
	ARG_UNUSED(tag);
	ARG_UNUSED(len);
	gl.after_calls++;
	gl.after_op = op;
}

static const struct rxf_backend glue_backend = {
	.may_answer = g_may, .get_info = g_info, .list = g_list, .range_check = g_range, .read_chunk = g_read,
	.confirm = g_confirm, .del = g_del, .set_time = g_time, .get_battery = g_batt, .fw_begin = g_fwb,
	.fw_data = g_fwd, .fw_end = g_fwe, .get_log = g_log, .factory = g_factory, .after_response = g_after,
};

const struct rxf_backend *glue_be(void)
{
	return &glue_backend;
}
