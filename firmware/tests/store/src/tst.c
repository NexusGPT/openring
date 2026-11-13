/* tst.c: helpers shared by the suites of tests/store (unit U2). */
#include "tst.h"

uint32_t tst_crc32(const uint8_t *d, size_t n)
{
	uint32_t c = 0xFFFFFFFFu;

	for (size_t i = 0; i < n; i++) {
		c ^= d[i];
		for (int b = 0; b < 8; b++) {
			c = (c & 1u) ? (c >> 1) ^ 0xEDB88320u : (c >> 1);
		}
	}
	return ~c;
}

void tst_le(uint8_t *buf, unsigned off, uint64_t v, unsigned bytes)
{
	for (unsigned i = 0; i < bytes; i++) {
		buf[off + i] = (uint8_t)(v >> (8 * i));
	}
}

void tst_reset_cb(const struct rst_cb *cb)
{
	rhw_sim_reset();
	tst_done_reset();
	zassert_equal(rst_init(cb), 0);
}

void tst_reset(void)
{
	tst_reset_cb(NULL);
}

void tst_before(void *f)
{
	ARG_UNUSED(f);
	tst_reset();
}

void tst_reboot(void)
{
	rhw_sim_reboot();
	zassert_equal(rst_init(NULL), 0);
}

void tst_card(uint32_t chunks)
{
	rhw_sim_disk_set_sectors(81920u + 65u * chunks);
}

void tst_mount_boot(struct rst_mount_info *mi)
{
	struct rst_mount_info local;

	zassert_equal(rst_mount(true, mi != NULL ? mi : &local), 0);
}

void tst_fill(struct rst_chunk *c, uint32_t rec_id, uint32_t in_rec, uint32_t frames, uint32_t seed)
{
	uint16_t *p = (uint16_t *)(c->bytes + 512);

	memset(c, 0, sizeof(*c));
	for (uint32_t i = 0; i < 16384; i++) {
		p[i] = (uint16_t)(seed * 7u + i * 13u + in_rec + 1u);
	}
	c->hdr.recording_id = rec_id;
	c->hdr.chunk_in_recording = in_rec;
	c->hdr.flags = in_rec == 0 ? 1u : 0u;
	c->hdr.recording_type = 1;
	c->hdr.frames = frames;
	c->hdr.first_frame_index = (uint64_t)in_rec * 8192u;
	c->hdr.utc_ms = 1700000000000ll + in_rec * 512;
	c->hdr.uptime_ns = 5000000000ull + in_rec * 512000000ull;
	c->hdr.battery_mv = 3900;
	c->hdr.temp_c_x10 = 301;
	c->hdr.boot_count = 1;
	c->hdr.fw_version = 0x00010203u;
	c->hdr.cycle_hz = 1000000;
	memset(c->hdr.highlight_frame, 0xFF, sizeof(c->hdr.highlight_frame));
	memset(c->hdr.motor_frames, 0xFF, sizeof(c->hdr.motor_frames));
}

static volatile int done_n;
static volatile int done_err;

void tst_done_cb(struct rst_chunk *c, int err)
{
	ARG_UNUSED(c);
	done_err = err;
	done_n++;
}

int tst_done_count(void)
{
	return done_n;
}

int tst_done_last_err(void)
{
	return done_err;
}

void tst_done_reset(void)
{
	done_n = 0;
	done_err = 0;
}

bool tst_wait_done(int n, uint32_t timeout_ms)
{
	for (uint32_t t = 0; t < timeout_ms; t++) {
		if (done_n >= n) {
			return true;
		}
		k_msleep(1);
	}
	return done_n >= n;
}

static struct rst_chunk rec_chunk;

uint32_t tst_ref_digest(uint32_t id, uint32_t nchunks)
{
	uint8_t words[64 * 4];
	static struct rst_chunk c;

	zassert_true(nchunks <= 64);
	for (uint32_t i = 0; i < nchunks; i++) {
		tst_fill(&c, id, i, 8192, i);
		tst_le(words, i * 4, tst_crc32(c.bytes + 512, 32768), 4);
	}
	return tst_crc32(words, nchunks * 4);
}

int tst_record(uint8_t type, uint32_t nchunks, uint32_t *id, uint32_t *digest)
{
	struct rst_close_args a = { .duration_frames = (uint64_t)nchunks * 8192u };
	int r = rst_open(type, 1700000000000ll, id);

	if (r != 0) {
		return r;
	}
	tst_done_reset();
	for (uint32_t i = 0; i < nchunks; i++) {
		tst_fill(&rec_chunk, *id, i, 8192, i);
		rec_chunk.hdr.recording_type = type;
		r = rst_put_chunk(&rec_chunk, tst_done_cb);
		if (r != 0) {
			return r;
		}
		if (!tst_wait_done((int)i + 1, 20000)) {
			return -ETIMEDOUT;
		}
	}
	memset(a.highlight_ms, 0xFF, sizeof(a.highlight_ms));
	r = rst_close(NULL, &a);
	if (digest != NULL) {
		*digest = tst_ref_digest(*id, nchunks);
	}
	return r;
}

/* ---- RAM disk */
#define RD_CAP 1100
static struct {
	uint32_t lba;
	uint8_t d[512];
} rd[RD_CAP];
static uint32_t rd_n;
static uint32_t rd_fail;

void rd_reset(void)
{
	rd_n = 0;
	rd_fail = UINT32_MAX;
}

void rd_fail_at(uint32_t lba)
{
	rd_fail = lba;
}

static int rd_find(uint32_t lba)
{
	for (uint32_t i = 0; i < rd_n; i++) {
		if (rd[i].lba == lba) {
			return (int)i;
		}
	}
	return -1;
}

int rd_read(void *ctx, uint32_t lba, uint8_t *buf, uint32_t count)
{
	ARG_UNUSED(ctx);
	for (uint32_t i = 0; i < count; i++) {
		if (rd_fail != UINT32_MAX && rd_fail == lba + i) {
			return -EIO;
		}
		int k = rd_find(lba + i);

		if (k < 0) {
			memset(buf + i * 512, 0, 512);
		} else {
			memcpy(buf + i * 512, rd[k].d, 512);
		}
	}
	return 0;
}

void rd_write(uint32_t lba, const uint8_t *buf, uint32_t count)
{
	for (uint32_t i = 0; i < count; i++) {
		int k = rd_find(lba + i);

		if (k < 0) {
			zassert_true(rd_n < RD_CAP, "ram disk full");
			k = (int)rd_n++;
			rd[k].lba = lba + i;
		}
		memcpy(rd[k].d, buf + i * 512, 512);
	}
}
