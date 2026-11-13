/* Helpers of tests/audio: the pure part's pool of chunk buffers, the frame-counter source, and the stand-in for the
 * store's hand-off (the store's own code is never linked here: another builder writes it). */
#include "common.h"

/* ------------------------------------------------------------------ pool for the pure tests */
static struct rst_chunk pool[T_POOL];
static int pool_next;
static struct rst_chunk *fulls[T_POOL];
static int n_fulls;
static struct {
	uint32_t chunk;
	uint8_t block;
} drops[64];
static int n_drops;
static struct rac_facts facts;

static struct rst_chunk *op_get(void *ctx, struct rac_facts *f)
{
	ARG_UNUSED(ctx);
	if (pool_next >= T_POOL) {
		return NULL;
	}
	*f = facts;
	facts.battery_mv++;
	return &pool[pool_next++];
}

static void op_full(void *ctx, struct rst_chunk *c)
{
	ARG_UNUSED(ctx);
	fulls[n_fulls++] = c;
}

static void op_dropout(void *ctx, uint32_t chunk, uint8_t block)
{
	ARG_UNUSED(ctx);
	if (n_drops < 64) {
		drops[n_drops].chunk = chunk;
		drops[n_drops].block = block;
	}
	n_drops++;
}

static const struct rac_ops ops = { .get = op_get, .full = op_full, .dropout = op_dropout };

void t_reset(void)
{
	memset(pool, 0xA5, sizeof(pool));
	pool_next = 0;
	n_fulls = 0;
	n_drops = 0;
	memset(&facts, 0, sizeof(facts));
}

const struct rac_ops *t_ops(void)
{
	return &ops;
}

int t_fulls(void)
{
	return n_fulls;
}

struct rst_chunk *t_full(int i)
{
	return fulls[i];
}

int t_dropouts(void)
{
	return n_drops;
}

uint32_t t_dropout_chunk(int i)
{
	return drops[i].chunk;
}

uint8_t t_dropout_block(int i)
{
	return drops[i].block;
}

void t_facts(uint16_t mv, int16_t temp, uint32_t fw, bool b15)
{
	facts.battery_mv = mv;
	facts.temp_c_x10 = temp;
	facts.fw_version = fw;
	facts.b15 = b15;
}

struct rac_start t_start(bool time_set, int64_t start_ms, uint64_t start_cycles, uint32_t hz)
{
	struct rac_start a = {
		.recording_id = 1, .recording_type = 1, .boot_count = 1, .time_set = time_set,
		.utc_offset_ms = 1700000000000LL, .start_ms = start_ms, .start_cycles = start_cycles, .cycles_hz = hz,
	};

	return a;
}

int16_t t_counter_left(uint32_t f)
{
	return (int16_t)(uint16_t)(f & 0xFFFFu);
}

static void counter_block(int16_t *b, uint32_t k)
{
	for (uint32_t j = 0; j < 256; j++) {
		uint32_t f = k * 256 + j;

		b[2 * j] = t_counter_left(f);
		b[2 * j + 1] = (int16_t)~(uint16_t)t_counter_left(f);
	}
}

void t_feed(struct rac *s, uint32_t first, uint32_t n)
{
	static int16_t b[512];

	for (uint32_t k = first; k < first + n; k++) {
		counter_block(b, k);
		(void)rac_block(s, b, &ops);
	}
}

void t_feed_block_with(struct rac *s, uint32_t k, uint32_t frame_in_block, int channel, int16_t v)
{
	static int16_t b[512];

	counter_block(b, k);
	b[2 * frame_in_block + channel] = v;
	(void)rac_block(s, b, &ops);
}

int16_t t_left(const struct rst_chunk *c, uint32_t i)
{
	int16_t v;

	memcpy(&v, &c->bytes[RREC_CHUNK_HEADER_BYTES + 4 * i], 2);
	return v;
}

int16_t t_right(const struct rst_chunk *c, uint32_t i)
{
	int16_t v;

	memcpy(&v, &c->bytes[RREC_CHUNK_HEADER_BYTES + 4 * i + 2], 2);
	return v;
}

bool t_tail_zero(const struct rst_chunk *c, uint32_t frames)
{
	for (uint32_t i = RREC_CHUNK_HEADER_BYTES + 4 * frames; i < RREC_CHUNK_BYTES; i++) {
		if (c->bytes[i] != 0) {
			return false;
		}
	}
	return true;
}

/* ------------------------------------------------------------------ the store's hand-off, as a stand-in */
static struct {
	struct rst_chunk *live;
	struct rst_chunk copy;
	rst_chunk_done_fn done;
	bool completed;
} si[SI_MAX];
static int si_n;
static bool hold;
static int enobufs_after = -1;
static struct k_spinlock si_lock;
static struct k_work si_work;
static bool work_ready;

static void si_work_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	for (int i = 0; i < SI_MAX; i++) {
		struct rst_chunk *c = NULL;
		rst_chunk_done_fn d = NULL;
		k_spinlock_key_t k = k_spin_lock(&si_lock);

		if (i < si_n && !si[i].completed && !hold) {
			si[i].completed = true;
			c = si[i].live;
			d = si[i].done;
		}
		k_spin_unlock(&si_lock, k);
		if (d != NULL) {
			d(c, 0);
		}
	}
}

void si_reset(void)
{
	if (!work_ready) {
		k_work_init(&si_work, si_work_fn);
		work_ready = true;
	}
	k_work_cancel(&si_work);
	si_n = 0;
	hold = false;
	enobufs_after = -1;
	memset(si, 0, sizeof(si));
}

void si_hold(bool h)
{
	hold = h;
	if (!h) {
		k_work_submit(&si_work);
	}
}

void si_enobufs_after(int n)
{
	enobufs_after = n;
}

int si_puts(void)
{
	return si_n;
}

const struct rst_chunk *si_copy(int i)
{
	return &si[i].copy;
}

const struct rst_chunk *si_live(int i)
{
	return si[i].live;
}

int si_put(struct rst_chunk *c, rst_chunk_done_fn done)
{
	if (enobufs_after >= 0 && si_n >= enobufs_after) {
		return -ENOBUFS;
	}
	k_spinlock_key_t k = k_spin_lock(&si_lock);
	int i = si_n++;

	if (i < SI_MAX) {
		si[i].live = c;
		si[i].done = done;
		memcpy(&si[i].copy, c, sizeof(*c));
	}
	k_spin_unlock(&si_lock, k);
	if (!hold) {
		k_work_submit(&si_work);
	}
	return 0;
}

void si_complete(int i)
{
	struct rst_chunk *c = NULL;
	rst_chunk_done_fn d = NULL;
	k_spinlock_key_t k = k_spin_lock(&si_lock);

	if (i < si_n && !si[i].completed) {
		si[i].completed = true;
		c = si[i].live;
		d = si[i].done;
	}
	k_spin_unlock(&si_lock, k);
	if (d != NULL) {
		d(c, 0);
	}
}

void si_complete_all(void)
{
	for (int i = 0; i < SI_MAX && i < si_n; i++) {
		si_complete(i);
	}
}

/* the default path of rau.c (cb.put NULL) lands here, as it would in the store */
int rst_put_chunk(struct rst_chunk *c, rst_chunk_done_fn done)
{
	return si_put(c, done);
}

/* ------------------------------------------------------------------ thin part */
struct svc_events svc_ev;
uint32_t svc_fw_version = 0x01020003u;

static void cb_no_block(void)
{
	svc_ev.no_block++;
	svc_ev.no_block_ms = rhw_clock()->now_ms();
}

static void cb_dropout(uint32_t rec, uint32_t chunk, uint8_t block)
{
	svc_ev.dropouts++;
	svc_ev.dr_rec = rec;
	svc_ev.dr_chunk = chunk;
	svc_ev.dr_block = block;
}

static void cb_facts(uint16_t *mv, int16_t *temp, uint32_t *fw)
{
	struct rhw_pmic_sample s;

	/* stands for the join: the battery and the die temperature of the simulated power chip */
	if (rhw_pmic()->sample(&s) == 0) {
		*mv = s.mv;
		*temp = s.die_c_x10;
	}
	*fw = svc_fw_version;
}

void svc_setup(void)
{
	rhw_sim_reset();
	si_reset();
	memset(&svc_ev, 0, sizeof(svc_ev));
	struct rau_cb cb = { .put = si_put, .no_block = cb_no_block, .dropout = cb_dropout, .chunk_facts = cb_facts };

	zassert_ok(rau_init(&cb));
}

void svc_cleanup(void)
{
	si_hold(false);
	si_complete_all();
	if (rau_capturing()) {
		(void)rau_halt();
	}
	(void)rau_release();
	k_sleep(K_MSEC(20));
}

int64_t svc_begin(bool time_set, bool b15)
{
	struct rau_start_args a = {
		.recording_id = 7, .recording_type = RREC_REC_TYPE_RECORDING, .boot_count = 4, .time_set = time_set,
		.utc_offset_ms = 1700000000000LL, .b15 = b15,
	};

	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_MIC, true, "test_join"));
	zassert_ok(rau_prepare(100));
	k_sleep(K_MSEC(RREC_MIC_RAIL_WAIT_MS));
	zassert_ok(rau_start(&a));
	return rhw_clock()->now_ms();
}

int32_t ev_find(uint16_t kind, uint32_t from)
{
	return rhw_sim_log_find(kind, from);
}

int64_t ev_t_us(int32_t idx)
{
	struct rhw_sim_ev e;

	zassert_true(rhw_sim_log_get((uint32_t)idx, &e));
	return e.t_us;
}

int64_t ev_a0(int32_t idx)
{
	struct rhw_sim_ev e;

	zassert_true(rhw_sim_log_get((uint32_t)idx, &e));
	return e.a0;
}
