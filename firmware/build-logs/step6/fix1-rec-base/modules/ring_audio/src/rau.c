/*
 * rau.c: the thin part of the audio unit (software step 6, unit U3): the audio thread, the ring of chunks, the
 * no-block watch, HFXO request and release, the clock pins' sleep state and the hand-off of full chunks to the store.
 * Hardware only through rhw.h (rhw_mic, rhw_hfxo, rhw_clock). It never switches a rail (FW l.457, l.463: only
 * rec_mics_on() and the join do). "FW l.N" = line N of design/firmware.md. Written for this project.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>
#include <zephyr/sys/util.h>

#include <ring_audio/rau.h>
#include <ring_rhw/rhw.h>
#ifdef CONFIG_RING_RHW_SIM
#include <ring_rhw/rhw_sim.h>
#endif

#include "rau_chunk.h"

/* The chunk ring (FW l.440, l.490): never below the specification's count. */
#define RAU_RING_CHUNKS RREC_CHUNK_RING
BUILD_ASSERT(RAU_RING_CHUNKS >= RREC_CHUNK_RING, "audio: the chunk ring must never be below the specified count (FW l.490)");

/* No block for this long while capturing = report once (FW l.108, l.169). */
#define RAU_WATCH_MS RREC_MIC_NO_BLOCK_MS
/* How often a waiting audio thread looks again at its flags; a tuning value of this unit, not a specification number. */
#define RAU_POLL_MS 4
#define RAU_EDGE_Q 16
#define RAU_HL_Q 16

enum slot_state { SL_FREE = 0, SL_FILLING, SL_QUEUED, SL_HELD };

static struct {
	struct rst_chunk c;
	atomic_t st;
} ring[RAU_RING_CHUNKS];

static struct rau_cb cbs;
static struct rac rac;
static atomic_t capturing, halting, cut_req, cut_now, cut_done, b15_now, lost_chunks;
static bool cut_limit_set;
static int64_t cut_target;
static struct rau_cut_result cut_result;
static bool hfxo_held;
static bool thread_started;
static bool hook_added;

static K_SEM_DEFINE(run_sem, 0, 1);
static K_SEM_DEFINE(halt_sem, 0, 1);
static K_SEM_DEFINE(cut_sem, 0, 1);
static K_SEM_DEFINE(free_sem, 0, RAU_RING_CHUNKS);
static K_SEM_DEFINE(hfxo_sem, 0, 1);

/* edges and highlights wait here for the audio thread (any context may add) */
static struct k_spinlock q_lock;
static struct {
	bool high;
	uint64_t cycles;
} eq[RAU_EDGE_Q];
static uint8_t eq_head, eq_n;
static int64_t hq[RAU_HL_Q];
static uint8_t hq_head, hq_n;

static K_THREAD_STACK_DEFINE(audio_stack, CONFIG_RING_AUDIO_STACK_SIZE);
static struct k_thread audio_thr;

int rst_put_chunk(struct rst_chunk *c, rst_chunk_done_fn done);

/* ------------------------------------------------------------------ chunk slots */
static int slot_of(const struct rst_chunk *c)
{
	for (int i = 0; i < RAU_RING_CHUNKS; i++) {
		if (c == &ring[i].c) {
			return i;
		}
	}
	return -1;
}

static void chunk_done(struct rst_chunk *c, int err)
{
	int i = slot_of(c);

	if (err < 0) {
		atomic_inc(&lost_chunks);
	}
	if (i >= 0) {
		atomic_set(&ring[i].st, SL_FREE);
		k_sem_give(&free_sem);
	}
}

static struct rst_chunk *op_get(void *ctx, struct rac_facts *f)
{
	ARG_UNUSED(ctx);
	for (;;) {
		for (int i = 0; i < RAU_RING_CHUNKS; i++) {
			if (atomic_cas(&ring[i].st, SL_FREE, SL_FILLING)) {
				memset(f, 0, sizeof(*f));
				if (cbs.chunk_facts != NULL) {
					cbs.chunk_facts(&f->battery_mv, &f->temp_c_x10, &f->fw_version);
				}
				f->b15 = atomic_get(&b15_now) != 0;
				return &ring[i].c;
			}
		}
		/* all chunks are with the store: wait, nothing is overwritten (FW l.440) */
		if (atomic_get(&halting) || atomic_get(&cut_now)) {
			return NULL;
		}
		k_sem_take(&free_sem, K_MSEC(RAU_POLL_MS));
	}
}

static void op_full(void *ctx, struct rst_chunk *c)
{
	ARG_UNUSED(ctx);
	int i = slot_of(c);
	int (*put)(struct rst_chunk *, rst_chunk_done_fn) = cbs.put != NULL ? cbs.put : rst_put_chunk;

	atomic_set(&ring[i].st, SL_QUEUED);
	for (;;) {
		int rc = put(c, chunk_done);

		if (rc == 0) {
			return;
		}
		if (rc == -ENOBUFS && !atomic_get(&halting) && !atomic_get(&cut_now)) {
			k_sem_take(&free_sem, K_MSEC(RAU_POLL_MS));
			continue;
		}
		/* refused for good (write fault, no open recording) or the capture is ending: the chunk is lost */
		atomic_inc(&lost_chunks);
		atomic_set(&ring[i].st, SL_FREE);
		return;
	}
}

static void op_dropout(void *ctx, uint32_t chunk_in_recording, uint8_t block)
{
	ARG_UNUSED(ctx);
	if (cbs.dropout != NULL) {
		cbs.dropout(rac.st.recording_id, chunk_in_recording, block);
	}
}

static const struct rac_ops ops = { .get = op_get, .full = op_full, .dropout = op_dropout };

/* ------------------------------------------------------------------ audio thread */
static void drain_queues(void)
{
	for (;;) {
		bool high;
		uint64_t cy;
		k_spinlock_key_t k = k_spin_lock(&q_lock);

		if (eq_n == 0) {
			k_spin_unlock(&q_lock, k);
			break;
		}
		high = eq[eq_head].high;
		cy = eq[eq_head].cycles;
		eq_head = (eq_head + 1) % RAU_EDGE_Q;
		eq_n--;
		k_spin_unlock(&q_lock, k);
		rac_motor_edge(&rac, high, cy);
	}
	for (;;) {
		int64_t ms;
		k_spinlock_key_t k = k_spin_lock(&q_lock);

		if (hq_n == 0) {
			k_spin_unlock(&q_lock, k);
			break;
		}
		ms = hq[hq_head];
		hq_head = (hq_head + 1) % RAU_HL_Q;
		hq_n--;
		k_spin_unlock(&q_lock, k);
		rac_highlight(&rac, ms);
	}
}

static void do_cut(void)
{
	struct rst_chunk *cur = rac.chunk;

	cut_result.last = rac_cut(&rac, &cut_result.close);
	if (cut_result.last != NULL) {
		atomic_set(&ring[slot_of(cut_result.last)].st, SL_HELD);
	} else if (cur != NULL) {
		atomic_set(&ring[slot_of(cur)].st, SL_FREE);
	}
	atomic_set(&cut_done, 1);
	k_sem_give(&cut_sem);
}

static void cut_check(void)
{
	if (atomic_get(&cut_done)) {
		return;
	}
	if (atomic_get(&cut_now)) {
		rac_set_limit(&rac, rac.total);
		cut_limit_set = true;
	} else if (atomic_get(&cut_req) && !cut_limit_set) {
		rac_set_limit(&rac, (uint64_t)cut_target);
		cut_limit_set = true;
	}
	if (cut_limit_set && rac_limit_reached(&rac)) {
		do_cut();
	}
}

static void capture(void)
{
	int64_t start_ms = rac.st.start_ms;
	int64_t last_good = start_ms;
	uint32_t e = 0;                 /* index of the next block expected */
	bool sent = false;

	for (;;) {
		bool halt = atomic_get(&halting) != 0;
		int32_t slice = RREC_BLOCK_MS;
		void *blk = NULL;
		size_t sz = 0;

		if (!halt) {
			drain_queues();
			cut_check();
		}
		int64_t t_call = rhw_clock()->now_ms();

		if (!sent) {
			int64_t rem = (int64_t)RAU_WATCH_MS - (t_call - last_good);

			if (rem < (int64_t)slice) {
				slice = rem > 0 ? (int32_t)rem : 1;
			}
		}
		int rc = rhw_mic()->read(&blk, &sz, slice);
		int64_t now = rhw_clock()->now_ms();

		if (atomic_get(&halting)) {
			/* stopping: give every block back; the input's error after the stop ends it (FW l.463) */
			if (rc == 0) {
				rhw_mic()->free_block(blk);
				continue;
			}
			/* no block for a whole block time after the stop: nothing is left (FW l.463) */
			break;
		}
		int64_t ready_e = start_ms + ((int64_t)e + 1) * (int64_t)RREC_BLOCK_MS;

		if (rc == 0 && sz == RREC_BLOCK_BYTES) {
			/* the block arrived a whole block or more after its time although this thread was already waiting:
			 * the blocks before it were not delivered (FW l.430) */
			if (t_call <= ready_e && now - ready_e >= (int64_t)RREC_BLOCK_MS) {
				for (int64_t m = (now - ready_e) / (int64_t)RREC_BLOCK_MS; m > 0; m--) {
					rac_block(&rac, NULL, &ops);
					e++;
				}
			}
			rac_block(&rac, (const int16_t *)blk, &ops);
			rhw_mic()->free_block(blk);
			e++;
			last_good = now;
			if (!atomic_get(&halting)) {
				drain_queues();
				cut_check();
			}
		} else if (rc == -EAGAIN) {
			/* nothing yet */
		} else {
			/* a lost block or a driver error: zeros at the time the block was due, so the recording keeps
			 * its length and does not run ahead of the clock (FW l.430) */
			if (rc == 0) {
				rhw_mic()->free_block(blk);
			}
			if (ready_e > now) {
				k_sleep(K_MSEC(ready_e - now));
			}
			rac_block(&rac, NULL, &ops);
			e++;
		}
		if (!sent && now - last_good >= (int64_t)RAU_WATCH_MS) {
			sent = true;
			if (cbs.no_block != NULL) {
				cbs.no_block();
			}
		}
	}
}

static void audio_thread(void *a, void *b, void *c)
{
	ARG_UNUSED(a);
	ARG_UNUSED(b);
	ARG_UNUSED(c);
	for (;;) {
		/* k_sem_reset() elsewhere would wake this wait with an error: only a real start runs a capture */
		if (k_sem_take(&run_sem, K_FOREVER) != 0) {
			continue;
		}
		capture();
		k_sem_give(&halt_sem);
	}
}

/* ------------------------------------------------------------------ public */
static void clear_state(void)
{
	/* a simulated reboot: whatever runs stops, the RAM state is empty */
	if (atomic_get(&capturing)) {
		atomic_set(&halting, 1);
	}
	atomic_set(&capturing, 0);
	hfxo_held = false;
}

int rau_init(const struct rau_cb *cb)
{
	if (atomic_get(&capturing)) {
		return -EBUSY;
	}
	memset(&cbs, 0, sizeof(cbs));
	if (cb != NULL) {
		cbs = *cb;
	}
	for (int i = 0; i < RAU_RING_CHUNKS; i++) {
		atomic_set(&ring[i].st, SL_FREE);
	}
	k_sem_reset(&free_sem);
	atomic_set(&halting, 0);
	hfxo_held = false;
	if (!thread_started) {
		k_thread_create(&audio_thr, audio_stack, K_THREAD_STACK_SIZEOF(audio_stack), audio_thread, NULL, NULL,
				NULL, K_PRIO_PREEMPT(CONFIG_RING_AUDIO_THREAD_PRIO), 0, K_NO_WAIT);
#ifdef CONFIG_THREAD_NAME
		k_thread_name_set(&audio_thr, "rau");
#endif
		thread_started = true;
	}
#ifdef CONFIG_RING_RHW_SIM
	if (!hook_added) {
		hook_added = rhw_sim_add_reboot_hook(clear_state) == 0;
	}
#endif
	/* clock pins low before VDD_MIC is ever on (FW l.465) */
	return rhw_mic()->pins_sleep() == 0 ? 0 : -EIO;
}

static void hfxo_running(void)
{
	k_sem_give(&hfxo_sem);
}

int rau_prepare(int32_t timeout_ms)
{
	k_sem_reset(&hfxo_sem);
	int rc = rhw_hfxo()->request(hfxo_running);

	if (rc != 0) {
		return rc;
	}
	if (k_sem_take(&hfxo_sem, K_MSEC(timeout_ms)) != 0) {
		rhw_hfxo()->release();
		return -ETIMEDOUT;
	}
	hfxo_held = true;
	return 0;
}

int rau_start(const struct rau_start_args *a)
{
	if (atomic_get(&capturing)) {
		return -EBUSY;
	}
	struct rhw_mic_cfg cfg = {
		.pcm_rate = RREC_PCM_RATE_HZ,
		.pcm_width = RREC_PCM_WIDTH_BITS,
		.channels = RREC_CHANNELS,
		.chan_map_lo = 0,       /* the real file builds the map: channel 0 left, channel 1 right (FW l.414) */
		.min_pdm_clk_hz = RREC_PDM_CLK_MIN_HZ,
		.max_pdm_clk_hz = RREC_PDM_CLK_MAX_HZ,
		.gain_db = RREC_PDM_GAIN_DB,
		.block_size = RREC_BLOCK_BYTES,
		.block_count = RREC_BLOCK_COUNT,
	};

	if (rhw_mic()->configure(&cfg) != 0) {
		return -EIO;
	}
	if (rhw_mic()->pins_default() != 0) {
		rhw_mic()->pins_sleep();
		return -EIO;
	}
	for (int i = 0; i < RAU_RING_CHUNKS; i++) {
		if (atomic_get(&ring[i].st) == SL_HELD || atomic_get(&ring[i].st) == SL_FILLING) {
			atomic_set(&ring[i].st, SL_FREE);
		}
	}
	struct rac_start st = {
		.recording_id = a->recording_id,
		.recording_type = a->recording_type,
		.boot_count = a->boot_count,
		.time_set = a->time_set,
		.utc_offset_ms = a->utc_offset_ms,
		.cycles_hz = rhw_clock()->cycles_per_sec(),
	};

	k_sem_reset(&halt_sem);
	k_sem_reset(&cut_sem);
	atomic_set(&halting, 0);
	atomic_set(&cut_req, 0);
	atomic_set(&cut_now, 0);
	atomic_set(&cut_done, 0);
	cut_limit_set = false;
	atomic_set(&b15_now, a->b15 ? 1 : 0);
	hq_n = 0;
	hq_head = 0;
	if (rhw_mic()->start() != 0) {
		rhw_mic()->pins_sleep();
		return -EIO;
	}
	st.start_ms = rhw_clock()->now_ms();
	st.start_cycles = rhw_clock()->cycles();
	rac_begin(&rac, &st);
	/* the last motor edges before the start are kept: the M1 that starts before the PDM is marked (FW l.497) */
	drain_queues();
	atomic_set(&capturing, 1);
	k_sem_give(&run_sem);
	return 0;
}

int rau_cut(int64_t mark_ms, struct rau_cut_result *out)
{
	bool forced = false;

	out->last = NULL;
	for (uint32_t i = 0; i < RREC_CLOSE_HIGHLIGHTS; i++) {
		out->close.highlight_ms[i] = RREC_UNUSED_U32;
	}
	out->close.duration_frames = 0;
	out->close.highlight_count = 0;
	if (!atomic_get(&capturing) || atomic_get(&halting)) {
		return -EIO;
	}
	if (!atomic_get(&cut_done)) {
		int64_t t = rac_ms_to_frame(&rac, mark_ms);

		cut_target = t < 0 ? 0 : t;
		atomic_set(&cut_req, 1);
		if (k_sem_take(&cut_sem, K_MSEC(RAU_WATCH_MS - RREC_BLOCK_MS)) != 0) {
			/* the block with the mark did not come: end with the frames there are */
			forced = true;
			atomic_set(&cut_now, 1);
			if (k_sem_take(&cut_sem, K_MSEC(2 * RREC_BLOCK_MS)) != 0) {
				return -EIO;
			}
		}
	}
	*out = cut_result;
	return forced ? -EIO : 0;
}

int rau_halt(void)
{
	int ret = 0;

	if (atomic_get(&capturing)) {
		atomic_set(&halting, 1);
		if (rhw_mic()->stop() != 0) {
			ret = -EIO;
		}
		if (k_sem_take(&halt_sem, K_MSEC(RREC_BLOCK_COUNT * RREC_BLOCK_MS)) != 0) {
			ret = -EIO;
		}
		for (int i = 0; i < RAU_RING_CHUNKS; i++) {
			atomic_cas(&ring[i].st, SL_FILLING, SL_FREE);
		}
		atomic_set(&capturing, 0);
	}
	/* clock pins low, so that VDD_MIC may go off (FW l.463, l.465) */
	if (rhw_mic()->pins_sleep() != 0) {
		ret = -EIO;
	}
	return ret;
}

int rau_release(void)
{
	if (atomic_get(&capturing)) {
		return -EBUSY;       /* the crystal stays while the microphones run (FW l.428) */
	}
	if (!hfxo_held) {
		return 0;
	}
	hfxo_held = false;
	return rhw_hfxo()->release();
}

void rau_highlight(int64_t centre_down_ms)
{
	if (!atomic_get(&capturing)) {
		return;
	}
	k_spinlock_key_t k = k_spin_lock(&q_lock);

	if (hq_n < RAU_HL_Q) {
		hq[(hq_head + hq_n) % RAU_HL_Q] = centre_down_ms;
		hq_n++;
	}
	k_spin_unlock(&q_lock, k);
}

void rau_motor_edge(bool high, uint64_t cycles)
{
	k_spinlock_key_t k = k_spin_lock(&q_lock);

	if (eq_n == RAU_EDGE_Q) {          /* full: the oldest edge goes */
		eq_head = (eq_head + 1) % RAU_EDGE_Q;
		eq_n--;
	}
	eq[(eq_head + eq_n) % RAU_EDGE_Q].high = high;
	eq[(eq_head + eq_n) % RAU_EDGE_Q].cycles = cycles;
	eq_n++;
	k_spin_unlock(&q_lock, k);
}

void rau_set_b15(bool b15)
{
	atomic_set(&b15_now, b15 ? 1 : 0);
}

bool rau_capturing(void)
{
	return atomic_get(&capturing) != 0;
}
