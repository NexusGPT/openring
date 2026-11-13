/*
 * ring_rhw simulation: the microphone input (ring,sim-mic). The shape of the kit's microphone interface (configure,
 * start, stop, read with a time limit, free); a block of 1,024 bytes (256 stereo frames) every 16 ms of simulated
 * time; a slab of 8 blocks; records the configuration it received. Written for this project.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/devicetree.h>

#include "sim_int.h"

#if DT_HAS_COMPAT_STATUS_OKAY(ring_sim_mic)
#define SLAB_BLOCKS DT_PROP(DT_INST(0, ring_sim_mic), queue_size)
#else
#define SLAB_BLOCKS RREC_BLOCK_COUNT
#endif

static int16_t slab[SLAB_BLOCKS][RREC_BLOCK_BYTES / 2];
static bool held[SLAB_BLOCKS];
static uint32_t n_held;

static struct rhw_mic_cfg last_cfg;
static bool have_cfg;
static bool running;
static bool stopped;
static int64_t t0_ms;
static int64_t t_stop_ms;
static uint32_t next_idx;          /* next block index to deliver */
static uint32_t delivered;
static bool asleep;

static enum rhw_sim_mic_source source;
static int32_t amp;
static int stuck_ch;
static int16_t stuck_val;
static int32_t clip_blk, stop_after, drop_blk, err_blk;

/* sin(2 pi k / 16) x 32767, k = 0..15: one period of 1 kHz at 16 kHz */
static const int16_t sine16[16] = {
	0, 12539, 23170, 30273, 32767, 30273, 23170, 12539,
	0, -12539, -23170, -30273, -32767, -30273, -23170, -12539,
};

static void fill(int16_t *b, uint32_t idx)
{
	for (uint32_t j = 0; j < RREC_BLOCK_FRAMES; j++) {
		uint32_t f = idx * RREC_BLOCK_FRAMES + j;
		int16_t l, r;

		if (source == RHW_SIM_MIC_SINE) {
			l = (int16_t)(((int32_t)sine16[f % 16] * amp) / 32767);
			r = l;
		} else {
			l = (int16_t)(uint16_t)(f & 0xFFFFu);
			r = (int16_t)~(uint16_t)l;
		}
		if (stuck_ch == 0) {
			l = stuck_val;
		} else if (stuck_ch == 1) {
			r = stuck_val;
		}
		if (clip_blk >= 0 && idx == (uint32_t)clip_blk) {
			if (j == 0) {
				l = -32768;
			}
			if (j == 1) {
				r = 32767;
			}
		}
		b[2 * j] = l;
		b[2 * j + 1] = r;
	}
}

static int m_configure(const struct rhw_mic_cfg *cfg)
{
	int r = 0;

	if (sim_dead(RHW_EV_MIC_CONFIGURE)) {
		return -ESHUTDOWN;
	}
	last_cfg = *cfg;
	have_cfg = true;
	if (cfg->pcm_rate != RREC_PCM_RATE_HZ || cfg->pcm_width != RREC_PCM_WIDTH_BITS ||
	    cfg->channels != RREC_CHANNELS || cfg->block_size != RREC_BLOCK_BYTES) {
		r = -ENOTSUP;
	}
	sim_log(RHW_EV_MIC_CONFIGURE, cfg->pcm_rate, cfg->block_size, cfg->channels, r, NULL);
	return r;
}

static int m_start(void)
{
	if (sim_dead(RHW_EV_MIC_START)) {
		return -ESHUTDOWN;
	}
	if (!have_cfg) {
		sim_log(RHW_EV_MIC_START, 0, 0, 0, -EINVAL, NULL);
		return -EINVAL;
	}
	running = true;
	stopped = false;
	t0_ms = k_uptime_get();
	next_idx = 0;
	delivered = 0;
	sim_log(RHW_EV_MIC_START, 0, 0, 0, 0, NULL);
	return 0;
}

static int m_stop(void)
{
	if (sim_dead(RHW_EV_MIC_STOP)) {
		return -ESHUTDOWN;
	}
	if (running) {
		stopped = true;
		t_stop_ms = k_uptime_get();
	}
	running = false;
	sim_log(RHW_EV_MIC_STOP, 0, 0, 0, 0, NULL);
	return 0;
}

static int m_read(void **block, size_t *size, int32_t timeout_ms)
{
	if (sim_dead(RHW_EV_MIC_READ)) {
		return -ESHUTDOWN;
	}
	if (!running && !stopped) {
		sim_log(RHW_EV_MIC_READ, -1, timeout_ms, 0, -EIO, NULL);
		return -EIO;
	}
	/* skip a dropped block: the next read gets the one after it, at its own time */
	if (drop_blk >= 0 && next_idx == (uint32_t)drop_blk) {
		sim_log(RHW_EV_MIC_DROP, next_idx, 0, 0, 0, NULL);
		next_idx++;
	}
	int64_t ready = t0_ms + (int64_t)(next_idx + 1) * RREC_BLOCK_MS;
	int64_t now = k_uptime_get();

	if (stopped && ready > t_stop_ms) {
		stopped = false;      /* every filled block was read: the driver released them */
		sim_log(RHW_EV_MIC_READ, -1, timeout_ms, 0, -EIO, NULL);
		return -EIO;
	}
	if (stop_after >= 0 && delivered >= (uint32_t)stop_after) {
		k_sleep(K_MSEC(timeout_ms));
		sim_log(RHW_EV_MIC_READ, -1, timeout_ms, 0, -EAGAIN, NULL);
		return -EAGAIN;
	}
	if (ready > now) {
		if (ready - now > timeout_ms) {
			k_sleep(K_MSEC(timeout_ms));
			sim_log(RHW_EV_MIC_READ, -1, timeout_ms, 0, -EAGAIN, NULL);
			return -EAGAIN;
		}
		k_sleep(K_MSEC(ready - now));
	}
	if (err_blk >= 0 && next_idx == (uint32_t)err_blk) {
		err_blk = -1;
		next_idx++;
		sim_log(RHW_EV_MIC_READ, next_idx - 1, timeout_ms, 0, -EIO, NULL);
		return -EIO;
	}
	int s = -1;

	for (int i = 0; i < SLAB_BLOCKS; i++) {
		if (!held[i]) {
			s = i;
			break;
		}
	}
	if (s < 0) {
		sim_log(RHW_EV_MIC_READ, next_idx, timeout_ms, 0, -ENOMEM, NULL);
		return -ENOMEM;
	}
	held[s] = true;
	n_held++;
	fill(slab[s], next_idx);
	*block = slab[s];
	*size = RREC_BLOCK_BYTES;
	sim_log(RHW_EV_MIC_READ, next_idx, timeout_ms, 0, 0, NULL);
	next_idx++;
	delivered++;
	return 0;
}

static void m_free(void *block)
{
	for (int i = 0; i < SLAB_BLOCKS; i++) {
		if (block == (void *)slab[i] && held[i]) {
			held[i] = false;
			n_held--;
			sim_log(RHW_EV_MIC_FREE, i, 0, 0, 0, NULL);
			return;
		}
	}
	sim_log(RHW_EV_MIC_FREE, -1, 0, 0, -EINVAL, NULL);
}

static int m_pins_sleep(void)
{
	if (sim_dead(RHW_EV_MIC_PINS_SLEEP)) {
		return -ESHUTDOWN;
	}
	asleep = true;
	sim_log(RHW_EV_MIC_PINS_SLEEP, 0, 0, 0, 0, NULL);
	return 0;
}

static int m_pins_default(void)
{
	if (sim_dead(RHW_EV_MIC_PINS_DEFAULT)) {
		return -ESHUTDOWN;
	}
	asleep = false;
	sim_log(RHW_EV_MIC_PINS_DEFAULT, 0, 0, 0, 0, NULL);
	return 0;
}

const struct rhw_mic_api rhw_sim_mic_api = {
	.configure = m_configure, .start = m_start, .stop = m_stop, .read = m_read, .free_block = m_free,
	.pins_sleep = m_pins_sleep, .pins_default = m_pins_default,
};

void sim_mic_reset(bool full)
{
	memset(held, 0, sizeof(held));
	n_held = 0;
	running = false;
	stopped = false;
	next_idx = 0;
	delivered = 0;
	have_cfg = false;
	asleep = false;
	if (full) {
		memset(&last_cfg, 0, sizeof(last_cfg));
		source = RHW_SIM_MIC_COUNTER;
		amp = 32767;
		stuck_ch = -1;
		stuck_val = 0;
		clip_blk = -1;
		stop_after = -1;
		drop_blk = -1;
		err_blk = -1;
	}
}

void rhw_sim_mic_source(enum rhw_sim_mic_source src, int level_dbfs)
{
	int32_t a = 32767;

	source = src;
	/* 10^(-1/20) = 0.891251 = 58409 / 65536, one step per whole dB */
	for (int d = 0; d < -level_dbfs && d < 200; d++) {
		a = (int32_t)(((int64_t)a * 58409) >> 16);
	}
	amp = a;
}

void rhw_sim_mic_stuck(int channel, int16_t value)
{
	stuck_ch = channel;
	stuck_val = value;
}

void rhw_sim_mic_clip_block(int32_t n)
{
	clip_blk = n;
}

void rhw_sim_mic_stop_after(int32_t n)
{
	stop_after = n;
}

void rhw_sim_mic_drop_block(int32_t n)
{
	drop_blk = n;
}

void rhw_sim_mic_read_error(int32_t n)
{
	err_blk = n;
}

bool rhw_sim_mic_last_cfg(struct rhw_mic_cfg *out)
{
	if (have_cfg) {
		*out = last_cfg;
	}
	return have_cfg;
}

uint32_t rhw_sim_mic_delivered(void)
{
	return delivered;
}

uint32_t rhw_sim_mic_held(void)
{
	return n_held;
}

bool rhw_sim_mic_pins_asleep(void)
{
	return asleep;
}
