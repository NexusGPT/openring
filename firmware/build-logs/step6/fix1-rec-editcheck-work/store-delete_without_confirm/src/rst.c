/*
 * rst.c: the storage part's thin layer (software step 6, unit U2): the storage thread, the rail sequence of
 * design/firmware.md 5.1, the 3 card init tries 200 ms apart, the 3 write tries, the one-operation-at-a-time guard.
 * It reaches the card, the storage bus, the VDD_SD rail and the clock only through ring_rhw (rhw.h); the formats,
 * the layout and the scan logic are in the pure files rst_fmt.c, rst_layout.c and rst_log.c. "FW l.N" = line N of
 * design/firmware.md. Written for this project.
 *
 * Locks: op_lock makes calls exclusive (a call made while another thread's call runs returns -EBUSY at once, FW l.219);
 * io_lock serialises every use of the card between the caller's operation and the storage thread; st_lock (spin) guards
 * the queue and the numbers other threads read.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>

#include <ring_rhw/rhw.h>
#ifdef CONFIG_RING_RHW_SIM
#include <ring_rhw/rhw_sim.h>
#endif
#include <ring_store/rst.h>

#include "rst_fmt.h"
#include "rst_layout.h"
#include "rst_log.h"

struct q_item {
	struct rst_chunk *c;
	rst_chunk_done_fn done;
};

struct open_rec {
	bool active;
	uint32_t id;
	uint8_t type;
	int64_t start_utc_ms;
	uint32_t first_seq;
	uint32_t put_seq;             /* next chunk seq to hand out */
	uint32_t written;             /* chunks on the card */
	uint32_t digest;
	bool s30_seen;
	bool sfull_seen;
};

static K_MUTEX_DEFINE(op_lock);
static K_MUTEX_DEFINE(io_lock);
static struct k_spinlock st_lock;
static K_SEM_DEFINE(work_sem, 0, K_SEM_MAX_LIMIT);
static K_SEM_DEFINE(done_sem, 0, K_SEM_MAX_LIMIT);
static K_THREAD_STACK_DEFINE(thr_stack, CONFIG_RING_STORE_STACK_SIZE);
static struct k_thread thr;
static bool thr_started;

static struct {
	bool inited, mounted, space_valid, fault, closing;
	struct rst_cb cb;
	struct rst_sb sb;
	struct rst_space space;
	struct rst_recs recs;
	struct open_rec op;
	struct q_item q[RREC_CHUNK_RING];
	uint32_t qh, qn;
	uint32_t cbs;                 /* items popped whose callbacks have not all run */
	uint32_t log_committed;       /* sb.log_head as of the last superblock write */
	struct rst_evbuf ev;
} S;

static struct rst_rec rec_store[RREC_LIST_CACHE];
static struct rst_rec win_buf[RREC_LIST_MAX_MAX];
static uint8_t sec[RREC_SECTOR_BYTES];            /* caller operations, under op_lock and io_lock */
static uint8_t lsec[RREC_SECTOR_BYTES];           /* event log flush, under io_lock */
static uint8_t scratch[RREC_CHUNK_BYTES];         /* chunk reads and the recovery scan */
static uint8_t scratch2[RREC_CHUNK_BYTES];        /* T-STORE's read back */

/* ------------------------------------------------------------------ small helpers */

static int dread(void *ctx, uint32_t lba, uint8_t *buf, uint32_t count)
{
	ARG_UNUSED(ctx);
	return rhw_disk()->read(lba, buf, count);
}

/* one write call, RREC_WRITE_TRIES tries at once (FW l.643) */
static int dwrite(uint32_t lba, const uint8_t *buf, uint32_t count)
{
	int r = -EIO;

	for (uint32_t i = 0; i < RREC_WRITE_TRIES && r != 0; i++) {
		r = rhw_disk()->write(lba, buf, count);
	}
	return r == 0 ? 0 : -EIO;
}

static void space_update(void)
{
	struct rst_space sp;

	rst_lay_space(S.sb.chunk_count_total, S.sb.head_chunk_seq, S.sb.tail_chunk_seq, &sp);
	k_spinlock_key_t k = k_spin_lock(&st_lock);

	S.space = sp;
	S.space_valid = true;
	k_spin_unlock(&st_lock, k);
}

/* writes the superblock to LBA sb_seq mod 2 with sb_seq + 1 (FW l.587) */
static int sb_write(void)
{
	S.sb.sb_seq++;
	rst_fmt_sb_encode(&S.sb, sec);
	if (dwrite(rst_lay_sb_lba(S.sb.sb_seq), sec, 1) != 0) {
		S.sb.sb_seq--;
		return -EIO;
	}
	S.log_committed = S.sb.log_head;
	return 0;
}

/* appends one index record at index_head (RAM index_head advances; the superblock commits it) */
static int ix_append(struct rst_ix *x)
{
	x->record_number = S.sb.index_head;
	rst_fmt_ix_encode(x, sec);
	if (dwrite(rst_lay_index_lba(x->record_number), sec, 1) != 0) {
		return -EIO;
	}
	S.sb.index_head++;
	return 0;
}

/* writes the buffered event log records to the log ring (FW l.1062); a record that fails stays in the buffer */
static int flush_log(void)
{
	struct rrec_logrec r;

	for (;;) {
		k_spinlock_key_t k = k_spin_lock(&st_lock);
		bool have = rst_evbuf_peek(&S.ev, &r);

		k_spin_unlock(&st_lock, k);
		if (!have) {
			return 0;
		}
		r.seq = S.sb.log_head;
		rst_fmt_log_encode(&r, lsec);
		if (dwrite(rst_lay_log_lba(r.seq), lsec, 1) != 0) {
			return -EIO;
		}
		S.sb.log_head++;
		if (S.sb.log_head - S.log_committed >= RREC_LOG_RING_RECORDS / 2u) {
			/* the superblock's log_head may lag by less than a lap, so the scan at mount finds the head */
			(void)sb_write();
		}
		k = k_spin_lock(&st_lock);
		rst_evbuf_pop(&S.ev);
		k_spin_unlock(&st_lock, k);
	}
}

static void power_down(bool deinit, const char *caller)
{
	if (deinit) {
		(void)rhw_disk()->deinit();
	}
	(void)rhw_sdbus()->suspend();
	(void)rhw_pmic()->rail_set(RHW_RAIL_SD, false, caller);
}

static bool op_take(void)
{
	return k_mutex_lock(&op_lock, K_NO_WAIT) == 0;
}

static void drain_chunks(void)
{
	for (;;) {
		k_spinlock_key_t k = k_spin_lock(&st_lock);
		uint32_t n = S.qn + S.cbs;

		k_spin_unlock(&st_lock, k);
		if (n == 0) {
			return;
		}
		(void)k_sem_take(&done_sem, K_MSEC(50));
	}
}

/* ------------------------------------------------------------------ the storage thread */

/* one queued chunk is on the card: numbers, digest, crossings (storage thread or close) */
static void chunk_landed(uint32_t seq, uint32_t pcrc, bool *s30_now, bool *sfull_now)
{
	k_spinlock_key_t k = k_spin_lock(&st_lock);

	S.sb.head_chunk_seq = seq + 1;
	S.op.digest = rst_fmt_digest_add(S.op.digest, pcrc);
	S.op.written++;
	rst_lay_space(S.sb.chunk_count_total, S.sb.head_chunk_seq, S.sb.tail_chunk_seq, &S.space);
	*s30_now = S.space.s30 && !S.op.s30_seen;
	*sfull_now = S.space.sfull && !S.op.sfull_seen;
	S.op.s30_seen = S.op.s30_seen || S.space.s30;
	S.op.sfull_seen = S.op.sfull_seen || S.space.sfull;
	k_spin_unlock(&st_lock, k);
}

static void thread_write_one(struct q_item it)
{
	bool s30 = false, sfull = false;
	uint32_t pcrc = 0;
	uint32_t seq = it.c->hdr.chunk_seq;
	int r;

	k_mutex_lock(&io_lock, K_FOREVER);
	r = rst_fmt_chunk_encode(it.c, &pcrc);
	if (r == 0) {
		r = dwrite(rst_lay_chunk_lba(S.sb.chunk_count_total, seq), it.c->bytes, RREC_CHUNK_SECTORS);
	}
	if (r == 0) {
		chunk_landed(seq, pcrc, &s30, &sfull);
	}
	k_mutex_unlock(&io_lock);

	struct q_item rest[RREC_CHUNK_RING];
	uint32_t nrest = 0;

	k_spinlock_key_t k = k_spin_lock(&st_lock);

	S.qh = (S.qh + 1) % RREC_CHUNK_RING;
	S.qn--;
	S.cbs++;
	if (r != 0) {
		S.fault = true;
		while (S.qn > 0) {
			rest[nrest++] = S.q[S.qh];
			S.qh = (S.qh + 1) % RREC_CHUNK_RING;
			S.qn--;
		}
	}
	k_spin_unlock(&st_lock, k);

	if (r != 0 && S.cb.write_fault != NULL) {
		S.cb.write_fault(r);                                     /* FW l.168 */
	}
	if (s30 && S.cb.s30 != NULL) {
		S.cb.s30(S.space.free_chunks);                           /* FW l.166 */
	}
	if (sfull && S.cb.sfull != NULL) {
		S.cb.sfull(S.space.free_chunks);                         /* FW l.167 */
	}
	if (it.done != NULL) {
		it.done(it.c, r);
	}
	for (uint32_t i = 0; i < nrest; i++) {
		if (rest[i].done != NULL) {
			rest[i].done(rest[i].c, -EIO);
		}
	}
	k = k_spin_lock(&st_lock);
	S.cbs--;
	k_spin_unlock(&st_lock, k);
	k_sem_give(&done_sem);
}

static void store_thread(void *a, void *b, void *c)
{
	ARG_UNUSED(a);
	ARG_UNUSED(b);
	ARG_UNUSED(c);
	for (;;) {
		(void)k_sem_take(&work_sem, K_FOREVER);
		for (;;) {
			k_spinlock_key_t k = k_spin_lock(&st_lock);
			bool have = S.qn > 0;
			struct q_item it = S.q[S.qh];

			k_spin_unlock(&st_lock, k);
			if (!have) {
				break;
			}
			thread_write_one(it);
		}
		k_mutex_lock(&io_lock, K_FOREVER);
		if (S.mounted) {
			(void)flush_log();
		}
		k_mutex_unlock(&io_lock);
	}
}

/* ------------------------------------------------------------------ start */

static void reset_state(void)
{
	memset(&S, 0, sizeof(S));
	rst_recs_init(&S.recs, rec_store, RREC_LIST_CACHE);
	rst_evbuf_init(&S.ev);
	k_sem_reset(&work_sem);
	k_sem_reset(&done_sem);
}

#ifdef CONFIG_RING_RHW_SIM
static void sim_reboot_hook(void)
{
	reset_state();
}
#endif

int rst_init(const struct rst_cb *cb)
{
	reset_state();
	if (cb != NULL) {
		S.cb = *cb;
	}
	(void)rhw_sdbus()->suspend();                 /* FW l.506: the sleep state at boot, before any SPI use */
	if (!thr_started) {
		thr_started = true;
		k_thread_create(&thr, thr_stack, K_THREAD_STACK_SIZEOF(thr_stack), store_thread, NULL, NULL, NULL,
				CONFIG_RING_STORE_THREAD_PRIORITY, 0, K_NO_WAIT);
		k_thread_name_set(&thr, "rst");
#ifdef CONFIG_RING_RHW_SIM
		(void)rhw_sim_add_reboot_hook(sim_reboot_hook);
#endif
	}
	S.inited = true;
	return 0;
}

/* ------------------------------------------------------------------ mount, unmount */

static void fill_info(struct rst_mount_info *out)
{
	memset(out, 0, sizeof(*out));
	out->open_flag = S.sb.open_flag != 0;
	out->open_recording_id = S.sb.open_flag ? S.sb.open_recording_id : 0;
	out->boot_count = S.sb.boot_count;
	out->card_sectors = S.sb.card_sectors;
	out->recordings = S.recs.live_total;
	out->space = S.space;
}

static int card_up(void)
{
	int r = -EIO;

	if (rhw_pmic()->rail_set(RHW_RAIL_SD, true, "rst_mount") != 0) {                  /* FW l.506: rail on */
		return -EIO;
	}
	k_msleep(RREC_SD_RAIL_WAIT_MS);                                                  /* wait 1 ms */
	(void)rhw_sdbus()->resume();                                                     /* resume spi00 */
	for (uint32_t i = 0; i < RREC_INIT_TRIES; i++) {                                 /* FW l.138 */
		r = rhw_disk()->init();
		if (r == 0) {
			break;
		}
		if (i + 1 < RREC_INIT_TRIES) {
			k_msleep(RREC_INIT_GAP_MS);
		}
	}
	if (r != 0) {
		power_down(false, "rst_mount");
		return -EIO;
	}
	return 0;
}

static int mount_body(bool boot, struct rst_mount_info *out)
{
	uint8_t *ca = scratch, *cb = scratch + RREC_SECTOR_BYTES;
	uint32_t sectors = 0;
	bool read_error = false, formatted = false;
	struct rst_sb picked;
	int which;

	if (rhw_disk()->sector_count(&sectors) != 0) {                                   /* FW l.507 */
		return -EIO;
	}
	if (dread(NULL, RREC_LBA_SB_A, ca, 1) != 0) {
		memset(ca, 0, RREC_SECTOR_BYTES);
		read_error = true;
	}
	if (dread(NULL, RREC_LBA_SB_B, cb, 1) != 0) {
		memset(cb, 0, RREC_SECTOR_BYTES);
		read_error = true;
	}
	if (rst_log_pick_sb(ca, cb, &picked, &which) == 0) {
		S.sb = picked;
		if (sectors < S.sb.card_sectors) {
			return -EIO;          /* a card smaller than the one this log was made on */
		}
	} else if (read_error) {
		return -EIO;                  /* never format a card that could not be read */
	} else {
		memset(&S.sb, 0, sizeof(S.sb));   /* a card with no valid superblock: a new log (reading, see notes) */
		S.sb.card_sectors = sectors;
		S.sb.chunk_first_lba = RREC_LBA_CHUNK_FIRST;
		S.sb.chunk_count_total = rst_lay_chunk_total(sectors);
		S.sb.head_chunk_seq = 1;
		S.sb.tail_chunk_seq = 1;
		S.sb.next_recording_id = 1;
		S.sb.index_head = 1;
		S.sb.index_tail = 1;
		S.sb.log_head = 1;
		formatted = true;
	}
	if (S.sb.chunk_count_total == 0) {
		return -EIO;
	}
	S.log_committed = S.sb.log_head;
	if (rst_log_load_index(dread, NULL, S.sb.index_tail, S.sb.index_head, &S.recs, sec) != 0) {
		return -EIO;
	}
	uint32_t lh;

	if (rst_log_evlog_head(dread, NULL, S.sb.log_head, &lh, sec) != 0) {
		return -EIO;
	}
	S.sb.log_head = lh;
	if (boot) {
		S.sb.boot_count++;                                                       /* decision D14 */
	}
	if (boot || formatted) {
		if (sb_write() != 0) {
			return -EIO;
		}
	}
	space_update();
	if (flush_log() != 0) {
		return -EIO;
	}
	S.mounted = true;
	fill_info(out);
	return 0;
}

int rst_mount(bool boot, struct rst_mount_info *out)
{
	int r;

	if (!S.inited) {
		return -ENODEV;
	}
	if (!op_take()) {
		return -EBUSY;
	}
	if (S.mounted) {
		fill_info(out);
		k_mutex_unlock(&op_lock);
		return 0;
	}
	S.fault = false;                       /* a new mount starts clean; the open flag on the card still leads to RECOVERY */
	S.closing = false;
	S.op.active = false;
	r = card_up();
	if (r == 0) {
		k_mutex_lock(&io_lock, K_FOREVER);
		r = mount_body(boot, out);
		if (r != 0) {
			rst_recs_init(&S.recs, rec_store, RREC_LIST_CACHE);
			power_down(true, "rst_mount");
		}
		k_mutex_unlock(&io_lock);
	}
	k_mutex_unlock(&op_lock);
	return r;
}

/* the body of rst_unmount and rst_unmount_wait, with op_lock held by the caller */
static int unmount_locked(void)
{
	int r = 0;

	if (!S.mounted) {
		k_mutex_unlock(&op_lock);
		return 0;
	}
	drain_chunks();
	k_mutex_lock(&io_lock, K_FOREVER);
	if (flush_log() != 0) {
		r = -EIO;
	}
	if (rhw_disk()->deinit() != 0) {                                                 /* FW l.506: deinit, */
		r = -EIO;
	}
	(void)rhw_sdbus()->suspend();                                                    /* then suspend, */
	if (rhw_pmic()->rail_set(RHW_RAIL_SD, false, "rst_unmount") != 0) {              /* then rail off */
		r = -EIO;
	}
	S.mounted = false;
	S.op.active = false;
	S.closing = false;
	k_mutex_unlock(&io_lock);
	k_mutex_unlock(&op_lock);
	return r;
}

int rst_unmount(void)
{
	if (!op_take()) {
		return -EBUSY;
	}
	return unmount_locked();
}

/* Step 6 fix round 1 (review finding R6-03): the unmount that waits up to timeout_ms for the store call that runs on
 * another thread (op_lock taken with a timeout instead of K_NO_WAIT), then the same body as rst_unmount. */
int rst_unmount_wait(int32_t timeout_ms)
{
	if (k_mutex_lock(&op_lock, K_MSEC(MAX(timeout_ms, 0))) != 0) {
		return -EBUSY;
	}
	return unmount_locked();
}

bool rst_mounted(void)
{
	return S.mounted;
}

/* ------------------------------------------------------------------ record, chunks */

int rst_open(uint8_t recording_type, int64_t start_utc_ms, uint32_t *id)
{
	int r = 0;

	if (!op_take()) {
		return -EBUSY;
	}
	if (!S.mounted) {
		r = -ENODEV;
	} else if (S.op.active) {
		r = -EBUSY;                                                              /* FW l.219 */
	} else if (S.sb.open_flag) {
		r = -EPERM;                                                              /* ruling R4b */
	} else if (S.fault) {
		r = -EIO;
	} else if (S.space.sfull) {
		r = -ENOSPC;
	}
	if (r == 0) {
		k_mutex_lock(&io_lock, K_FOREVER);
		struct rst_sb keep = S.sb;

		S.sb.open_flag = 1;
		S.sb.open_recording_id = S.sb.next_recording_id;
		S.sb.open_first_chunk_seq = S.sb.head_chunk_seq;
		S.sb.next_recording_id++;
		if (sb_write() != 0) {
			S.sb = keep;
			r = -EIO;
		} else {
			k_spinlock_key_t k = k_spin_lock(&st_lock);

			memset(&S.op, 0, sizeof(S.op));
			S.op.active = true;
			S.op.id = S.sb.open_recording_id;
			S.op.type = recording_type;
			S.op.start_utc_ms = start_utc_ms;
			S.op.first_seq = S.sb.head_chunk_seq;
			S.op.put_seq = S.sb.head_chunk_seq;
			S.op.s30_seen = S.space.s30;
			S.op.sfull_seen = S.space.sfull;
			S.closing = false;
			k_spin_unlock(&st_lock, k);
			*id = S.op.id;
		}
		k_mutex_unlock(&io_lock);
	}
	k_mutex_unlock(&op_lock);
	return r;
}

int rst_put_chunk(struct rst_chunk *c, rst_chunk_done_fn done)
{
	int r = 0;
	k_spinlock_key_t k = k_spin_lock(&st_lock);

	if (!S.op.active || S.closing || !rst_fmt_chunk_hdr_valid(&c->hdr)) {
		r = -EINVAL;
	} else if (S.fault) {
		r = -EIO;
	} else if (S.qn >= RREC_CHUNK_RING) {
		r = -ENOBUFS;
	} else if (S.op.put_seq - S.sb.tail_chunk_seq >= S.sb.chunk_count_total) {
		r = -ENOSPC;          /* a chunk would overwrite one that is not freed */
	} else {
		c->hdr.chunk_seq = S.op.put_seq++;
		c->hdr.recording_id = S.op.id;
		c->hdr.recording_type = S.op.type;
		S.q[(S.qh + S.qn) % RREC_CHUNK_RING] = (struct q_item){ .c = c, .done = done };
		S.qn++;
	}
	k_spin_unlock(&st_lock, k);
	if (r == 0) {
		k_sem_give(&work_sem);
	}
	return r;
}

int rst_close(struct rst_chunk *last, const struct rst_close_args *a)
{
	int r = 0;

	if (last != NULL && !rst_fmt_chunk_hdr_valid(&last->hdr)) {
		return -EINVAL;
	}
	if (!op_take()) {
		return -EBUSY;
	}
	k_spinlock_key_t k = k_spin_lock(&st_lock);
	bool active = S.op.active;

	if (active) {
		S.closing = true;
	}
	k_spin_unlock(&st_lock, k);
	if (!active) {
		k_mutex_unlock(&op_lock);
		return -EINVAL;
	}
	drain_chunks();
	if (S.fault) {
		k_mutex_unlock(&op_lock);
		return -EIO;                  /* the superblock stays open (FW l.168) */
	}
	k_mutex_lock(&io_lock, K_FOREVER);
	if (last != NULL) {
		bool s30, sfull;
		uint32_t pcrc, seq = S.op.put_seq++;

		last->hdr.chunk_seq = seq;
		last->hdr.recording_id = S.op.id;
		last->hdr.recording_type = S.op.type;
		r = rst_fmt_chunk_encode(last, &pcrc);
		if (r == 0) {
			r = dwrite(rst_lay_chunk_lba(S.sb.chunk_count_total, seq), last->bytes, RREC_CHUNK_SECTORS);
		}
		if (r == 0) {
			chunk_landed(seq, pcrc, &s30, &sfull);
		}
	}
	if (r == 0) {
		struct rst_ix x = {
			.type = RREC_IX_TYPE_CLOSE,
			.close_state = RREC_IX_CLOSE_COMPLETE,
			.recording_id = S.op.id,
			.first_chunk_seq = S.op.first_seq,
			.chunk_count = S.op.written,
			.recording_type = S.op.type,
			.channels = RREC_CHANNELS,
			.highlight_count = a->highlight_count,
			.sample_rate_hz = RREC_PCM_RATE_HZ,
			.start_utc_ms = S.op.start_utc_ms,
			.duration_frames = a->duration_frames,
			.digest = S.op.digest,
		};

		memcpy(x.highlight_ms, a->highlight_ms, sizeof(x.highlight_ms));
		r = ix_append(&x);
		if (r == 0) {
			S.sb.open_flag = 0;
			S.sb.head_chunk_seq = S.op.first_seq + S.op.written;
			r = sb_write();
			if (r == 0) {
				rst_recs_apply(&S.recs, &x);
			}
		}
	}
	if (r == 0) {
		k = k_spin_lock(&st_lock);
		S.op.active = false;
		S.closing = false;
		k_spin_unlock(&st_lock, k);
		space_update();
	} else {
		S.fault = true;
		r = -EIO;
	}
	k_mutex_unlock(&io_lock);
	k_mutex_unlock(&op_lock);
	return r;
}

/* ------------------------------------------------------------------ recovery */

struct prog_ctx {
	void (*fn)(uint32_t);
};

static void prog_thunk(void *ctx, uint32_t kept)
{
	struct prog_ctx *p = ctx;

	if (p->fn != NULL) {
		p->fn(kept);
	}
}

int rst_recover(void (*progress)(uint32_t chunks), struct rst_recover_result *out)
{
	int r = 0;
	struct rst_scan sc;
	struct prog_ctx pc = { .fn = progress };

	if (!op_take()) {
		return -EBUSY;
	}
	if (!S.mounted) {
		r = -ENODEV;
	} else if (!S.sb.open_flag || S.op.active) {
		r = -EINVAL;
	}
	if (r != 0) {
		k_mutex_unlock(&op_lock);
		return r;
	}
	k_mutex_lock(&io_lock, K_FOREVER);
	r = rst_log_scan(dread, NULL, S.sb.chunk_count_total, S.sb.open_recording_id, S.sb.open_first_chunk_seq, scratch,
			 prog_thunk, &pc, &sc);
	if (r != 0) {
		r = -EIO;                     /* the open flag stays set (FW l.143, ruling R9) */
	} else {
		struct rst_ix x = {
			.type = RREC_IX_TYPE_CLOSE,
			.close_state = RREC_IX_CLOSE_RECOVERED,
			.recording_id = S.sb.open_recording_id,
			.first_chunk_seq = S.sb.open_first_chunk_seq,
			.chunk_count = sc.kept,
			.recording_type = sc.recording_type != 0 ? sc.recording_type : RREC_REC_TYPE_RECORDING,
			.channels = RREC_CHANNELS,
			.highlight_count = sc.highlight_count,
			.sample_rate_hz = RREC_PCM_RATE_HZ,
			.start_utc_ms = sc.start_utc_ms,
			.duration_frames = sc.duration_frames,
			.digest = sc.digest,
		};
		uint32_t id = S.sb.open_recording_id;

		memcpy(x.highlight_ms, sc.highlight_ms, sizeof(x.highlight_ms));
		r = ix_append(&x);
		if (r == 0) {
			S.sb.head_chunk_seq = S.sb.open_first_chunk_seq + sc.kept;               /* FW l.646 */
			S.sb.open_flag = 0;
			r = sb_write();
		}
		if (r == 0) {
			rst_recs_apply(&S.recs, &x);
			space_update();
			if (out != NULL) {
				out->recording_id = id;
				out->chunks_kept = sc.kept;
				out->head_chunk_seq = S.sb.head_chunk_seq;
			}
		} else {
			r = -EIO;
		}
	}
	k_mutex_unlock(&io_lock);
	k_mutex_unlock(&op_lock);
	return r;
}

/* ------------------------------------------------------------------ space, lists */

int rst_space(struct rst_space *out)
{
	k_spinlock_key_t k = k_spin_lock(&st_lock);
	bool valid = S.space_valid;

	if (valid) {
		*out = S.space;
	}
	k_spin_unlock(&st_lock, k);
	return valid ? 0 : -ENODEV;
}

/* up to max live recordings with id >= id_from, oldest first; ids at or under evict_max_id come from the index (D16) */
static int rec_batch(uint32_t id_from, uint32_t max, struct rst_rec *out, uint32_t *n)
{
	uint32_t m = 0, lo = id_from;

	*n = 0;
	if (S.recs.first_id == 0 || max == 0) {
		return 0;
	}
	if (lo < S.recs.first_id) {
		lo = S.recs.first_id;
	}
	while (m < max && S.recs.evict_max_id != 0 && lo <= S.recs.evict_max_id) {
		uint32_t win = RREC_LIST_MAX_MAX, k = 0;

		if (lo + win - 1 > S.recs.evict_max_id) {
			win = S.recs.evict_max_id - lo + 1;
		}
		if (rst_log_index_find(dread, NULL, S.sb.index_tail, S.sb.index_head, lo, win, win_buf, &k, sec) != 0) {
			return -EIO;
		}
		for (uint32_t i = 0; i < k && m < max; i++) {
			out[m++] = win_buf[i];
		}
		lo += win;
	}
	for (uint32_t i = 0; i < S.recs.n && m < max; i++) {
		if (S.recs.ent[i].info.recording_id >= lo) {
			out[m++] = S.recs.ent[i];
		}
	}
	*n = m;
	return 0;
}

static int rec_lookup(uint32_t id, struct rst_rec *out)
{
	uint32_t n = 0;

	if (S.recs.first_id == 0 || id < S.recs.first_id) {
		return -ENOENT;
	}
	if (S.recs.evict_max_id == 0 || id > S.recs.evict_max_id) {
		struct rst_rec *r = rst_recs_find(&S.recs, id);

		if (r == NULL) {
			return -ENOENT;
		}
		*out = *r;
		return 0;
	}
	if (rst_log_index_find(dread, NULL, S.sb.index_tail, S.sb.index_head, id, 1, win_buf, &n, sec) != 0) {
		return -EIO;
	}
	if (n == 0) {
		return -ENOENT;
	}
	*out = win_buf[0];
	return 0;
}

int rst_list(uint32_t first, uint16_t max, struct rst_rec_info *out, uint16_t *count)
{
	static struct rst_rec lbuf[RREC_LIST_MAX_MAX];
	uint32_t n = 0;
	int r;

	if (max < RREC_LIST_MAX_MIN || max > RREC_LIST_MAX_MAX) {
		return -EINVAL;
	}
	if (!op_take()) {
		return -EBUSY;
	}
	k_mutex_lock(&io_lock, K_FOREVER);
	r = S.mounted ? rec_batch(first, max, lbuf, &n) : -ENODEV;
	k_mutex_unlock(&io_lock);
	if (r == 0) {
		for (uint32_t i = 0; i < n; i++) {
			out[i] = lbuf[i].info;
		}
		*count = (uint16_t)n;
	}
	k_mutex_unlock(&op_lock);
	return r;
}

int rst_read_chunk(uint32_t recording_id, uint32_t chunk, uint8_t *out)
{
	struct rst_rec rec;
	int r;

	if (!op_take()) {
		return -EBUSY;
	}
	k_mutex_lock(&io_lock, K_FOREVER);
	r = S.mounted ? rec_lookup(recording_id, &rec) : -ENODEV;
	if (r == 0 && chunk >= rec.info.chunk_count) {
		r = -ENOENT;
	}
	if (r == 0) {
		r = dread(NULL, rst_lay_chunk_lba(S.sb.chunk_count_total, rec.info.first_chunk_seq + chunk), out,
			  RREC_CHUNK_SECTORS) == 0 ? 0 : -EIO;
	}
	k_mutex_unlock(&io_lock);
	k_mutex_unlock(&op_lock);
	return r;
}

/* ------------------------------------------------------------------ confirm, delete */

static struct rst_ix ix_for(const struct rst_rec *rec, uint8_t type)
{
	struct rst_ix x = {
		.type = type,
		.recording_id = rec->info.recording_id,
		.first_chunk_seq = rec->info.first_chunk_seq,
		.chunk_count = rec->info.chunk_count,
		.recording_type = rec->info.type,
		.channels = rec->info.channels,
		.sample_rate_hz = rec->info.sample_rate_hz,
	};

	return x;
}

int rst_confirm(uint32_t recording_id, uint32_t digest)
{
	struct rst_rec rec;
	int r;

	if (!op_take()) {
		return -EBUSY;
	}
	k_mutex_lock(&io_lock, K_FOREVER);
	r = S.mounted ? rec_lookup(recording_id, &rec) : -ENODEV;
	if (r == 0 && rec.info.digest != digest) {
		r = -EBADMSG;                                                            /* FW l.658: nothing changes */
	}
	if (r == 0 && !rec.confirmed) {
		struct rst_ix x = ix_for(&rec, RREC_IX_TYPE_CONFIRM);

		r = ix_append(&x);
		if (r == 0) {
			r = sb_write();                                                  /* commits the record */
		}
		if (r == 0) {
			rst_recs_apply(&S.recs, &x);
		} else {
			r = -EIO;
		}
	}
	k_mutex_unlock(&io_lock);
	k_mutex_unlock(&op_lock);
	return r;
}

/* the tail after a DELETE record was appended (FW l.660); writes the superblock */
static int tail_move_and_commit(void)
{
	uint32_t ct, it;

	if (rst_log_tail_walk(dread, NULL, S.sb.index_tail, S.sb.index_head, S.sb.head_chunk_seq, &ct, &it, sec) != 0) {
		return -EIO;
	}
	S.sb.tail_chunk_seq = ct;
	S.sb.index_tail = it;
	if (sb_write() != 0) {
		return -EIO;
	}
	space_update();
	return 0;
}

int rst_delete(uint32_t recording_id, uint32_t *free_after)
{
	struct rst_rec rec;
	int r;

	if (!op_take()) {
		return -EBUSY;
	}
	k_mutex_lock(&io_lock, K_FOREVER);
	r = S.mounted ? rec_lookup(recording_id, &rec) : -ENODEV;
	if (r == 0 && S.sb.open_flag) {
		r = -EBUSY;                   /* a recording is open or waits for its recovery */
	}
	if (r == 0 && !rec.confirmed && false) {
		r = -EACCES;                                                             /* FW l.659 */
	}
	if (r == 0) {
		struct rst_ix x = ix_for(&rec, RREC_IX_TYPE_DELETE);

		r = ix_append(&x);
		if (r == 0) {
			rst_recs_apply(&S.recs, &x);
			r = tail_move_and_commit();
		}
		if (r == 0 && free_after != NULL) {
			*free_after = S.space.free_chunks;
		}
	}
	k_mutex_unlock(&io_lock);
	k_mutex_unlock(&op_lock);
	return r;
}

int rst_delete_factory_recordings(uint32_t *deleted)
{
	static struct rst_rec fbuf[RREC_LIST_MAX_MAX];
	uint32_t count = 0, from = 0;
	int r = 0;

	if (!op_take()) {
		return -EBUSY;
	}
	k_mutex_lock(&io_lock, K_FOREVER);
	if (!S.mounted) {
		r = -ENODEV;
	} else if (S.sb.open_flag) {
		r = -EBUSY;
	}
	while (r == 0) {
		uint32_t n = 0;
		bool again = false;

		r = rec_batch(from, RREC_LIST_MAX_MAX, fbuf, &n);
		for (uint32_t i = 0; r == 0 && i < n; i++) {
			from = fbuf[i].info.recording_id + 1;
			if (fbuf[i].info.type == RREC_REC_TYPE_FACTORY) {
				struct rst_ix x = ix_for(&fbuf[i], RREC_IX_TYPE_DELETE);

				r = ix_append(&x);
				if (r == 0) {
					rst_recs_apply(&S.recs, &x);
					count++;
				}
			}
		}
		again = n == RREC_LIST_MAX_MAX;
		if (!again) {
			break;
		}
	}
	if (r == 0 && count > 0) {
		r = tail_move_and_commit();
	}
	if (r != 0 && r != -ENODEV && r != -EBUSY) {
		r = -EIO;
	}
	if (r == 0 && deleted != NULL) {
		*deleted = count;
	}
	k_mutex_unlock(&io_lock);
	k_mutex_unlock(&op_lock);
	return r;
}

/* ------------------------------------------------------------------ event log */

void rst_log_put(const struct rrec_logrec *r)
{
	k_spinlock_key_t k = k_spin_lock(&st_lock);

	rst_evbuf_push(&S.ev, r);
	k_spin_unlock(&st_lock, k);
	k_sem_give(&work_sem);
}

uint32_t rst_log_dropped(void)
{
	k_spinlock_key_t k = k_spin_lock(&st_lock);
	uint32_t d = S.ev.dropped;

	k_spin_unlock(&st_lock, k);
	return d;
}

int rst_log_read(uint32_t first, uint16_t max, uint8_t *out, uint16_t *count)
{
	int r = 0;
	uint16_t n = 0;

	if (max < RREC_GET_LOG_MAX_MIN || max > RREC_GET_LOG_MAX_MAX) {
		return -EINVAL;
	}
	if (!op_take()) {
		return -EBUSY;
	}
	k_mutex_lock(&io_lock, K_FOREVER);
	if (!S.mounted) {
		r = -ENODEV;
	} else if (flush_log() != 0) {
		r = -EIO;
	} else {
		uint32_t head = S.sb.log_head;
		uint32_t oldest = head > RREC_LOG_RING_RECORDS ? head - RREC_LOG_RING_RECORDS : 1;
		uint32_t s = first < oldest ? oldest : first;
		struct rrec_logrec rec;

		for (; s < head && n < max && r == 0; s++) {
			uint8_t *dst = out + (size_t)n * RREC_LOG_RECORD_BYTES;

			if (dread(NULL, rst_lay_log_lba(s), dst, 1) != 0 || rst_fmt_log_decode(dst, &rec) != 0 ||
			    rec.seq != s) {
				r = -EIO;
			} else {
				n++;
			}
		}
	}
	k_mutex_unlock(&io_lock);
	k_mutex_unlock(&op_lock);
	if (r == 0) {
		*count = n;
	}
	return r;
}

/* ------------------------------------------------------------------ factory area test (T-STORE, FW l.1030) */

int rst_factory_area_test(struct rst_factory_result *out)
{
	const struct rhw_clock_api *ck = rhw_clock();
	uint32_t cps = ck->cycles_per_sec();
	int r = 0;

	if (!op_take()) {
		return -EBUSY;
	}
	k_mutex_lock(&io_lock, K_FOREVER);
	if (!S.mounted) {
		r = -ENODEV;
	} else {
		for (uint32_t i = 0; i < RREC_FACTORY_SECTORS * RREC_SECTOR_BYTES; i++) {
			scratch[i] = (uint8_t)(i * 31u + (i >> 8));
		}
		uint64_t t0 = ck->cycles();

		r = rhw_disk()->write(RREC_LBA_FACTORY_FIRST, scratch, RREC_FACTORY_SECTORS);
		uint64_t t1 = ck->cycles();

		if (r == 0) {
			r = rhw_disk()->read(RREC_LBA_FACTORY_FIRST, scratch2, RREC_FACTORY_SECTORS);
		}
		uint64_t t2 = ck->cycles();

		if (r == 0) {
			out->equal = rst_fmt_crc32(scratch, RREC_FACTORY_SECTORS * RREC_SECTOR_BYTES) ==
				     rst_fmt_crc32(scratch2, RREC_FACTORY_SECTORS * RREC_SECTOR_BYTES);
			out->write_us = cps != 0 ? (uint32_t)(((t1 - t0) * 1000000u) / cps) : 0;
			out->read_us = cps != 0 ? (uint32_t)(((t2 - t1) * 1000000u) / cps) : 0;
		} else {
			r = -EIO;
		}
	}
	k_mutex_unlock(&io_lock);
	k_mutex_unlock(&op_lock);
	return r;
}
