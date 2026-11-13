/*
 * ring_rhw simulation: the card (ring,sim-disk). Sectors of 512 bytes in a sparse store (unwritten sectors read as
 * zero); init and deinit; one write call for many sectors; the faults of rhw_sim.h. Written for this project.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/devicetree.h>

#include "sim_int.h"

#define POOL CONFIG_RING_RHW_SIM_DISK_POOL
#define HASH (2 * POOL)

#if DT_HAS_COMPAT_STATUS_OKAY(ring_sim_disk)
#define DEFAULT_SECTORS DT_PROP(DT_INST(0, ring_sim_disk), sector_count)
#else
#define DEFAULT_SECTORS 7812500u
#endif

static uint8_t data[POOL][RREC_SECTOR_BYTES];
static uint32_t key_of[HASH];     /* lba + 1; 0 = empty */
static uint32_t slot_of[HASH];
static uint32_t used;

static uint32_t sectors;
static bool inited;
static uint32_t fail_init_n;
static uint32_t wr_calls;          /* since the last reset */
static uint32_t fail_from, fail_k, fail_base;
static uint32_t rd_err_lba;
static uint32_t cut_n, cut_k, cut_base;
static bool cut_done;
static uint32_t stall_ms;
static uint32_t refused;

static uint32_t hidx(uint32_t lba)
{
	return (lba * 2654435761u) % HASH;
}

static int find(uint32_t lba)
{
	uint32_t h = hidx(lba);

	for (uint32_t i = 0; i < HASH; i++) {
		uint32_t j = (h + i) % HASH;

		if (key_of[j] == 0) {
			return -1;
		}
		if (key_of[j] == lba + 1) {
			return (int)slot_of[j];
		}
	}
	return -1;
}

static int store(uint32_t lba, const uint8_t *src)
{
	int s = find(lba);

	if (s < 0) {
		if (used >= POOL) {
			return -ENOSPC;
		}
		uint32_t h = hidx(lba);

		for (uint32_t i = 0; i < HASH; i++) {
			uint32_t j = (h + i) % HASH;

			if (key_of[j] == 0) {
				key_of[j] = lba + 1;
				slot_of[j] = used;
				s = (int)used++;
				break;
			}
		}
	}
	memcpy(data[s], src, RREC_SECTOR_BYTES);
	return 0;
}

static void load(uint32_t lba, uint8_t *dst)
{
	int s = find(lba);

	if (s < 0) {
		memset(dst, 0, RREC_SECTOR_BYTES);
	} else {
		memcpy(dst, data[s], RREC_SECTOR_BYTES);
	}
}

void sim_disk_rail_changed(bool on)
{
	if (!on) {
		inited = false;
	}
}

/* the rail rule: no call while VDD_SD is off (FW l.506); no transfer before init */
static bool refuse(uint16_t kind, bool need_init)
{
	if (!sim_pmic_rail(RHW_RAIL_SD) || (need_init && !inited)) {
		refused++;
		sim_log(RHW_EV_DISK_REFUSED, kind, 0, 0, -EIO, NULL);
		return true;
	}
	return false;
}

static int d_init(void)
{
	int r = 0;

	if (sim_dead(RHW_EV_DISK_INIT)) {
		return -ESHUTDOWN;
	}
	if (refuse(RHW_EV_DISK_INIT, false)) {
		return -EIO;
	}
	if (fail_init_n > 0) {
		fail_init_n--;
		r = -EIO;
	} else {
		inited = true;
	}
	sim_log(RHW_EV_DISK_INIT, 0, 0, 0, r, NULL);
	return r;
}

static int d_deinit(void)
{
	if (sim_dead(RHW_EV_DISK_DEINIT)) {
		return -ESHUTDOWN;
	}
	if (refuse(RHW_EV_DISK_DEINIT, false)) {
		return -EIO;
	}
	inited = false;
	sim_log(RHW_EV_DISK_DEINIT, 0, 0, 0, 0, NULL);
	return 0;
}

static int d_read(uint32_t lba, uint8_t *buf, uint32_t count)
{
	int r = 0;

	if (sim_dead(RHW_EV_DISK_READ)) {
		return -ESHUTDOWN;
	}
	if (refuse(RHW_EV_DISK_READ, true)) {
		return -EIO;
	}
	if (count == 0 || (uint64_t)lba + count > sectors) {
		r = -EINVAL;
	} else if (rd_err_lba != UINT32_MAX && rd_err_lba >= lba && rd_err_lba < lba + count) {
		r = -EIO;
	} else {
		k_spinlock_key_t key = k_spin_lock(&sim_lock);

		for (uint32_t i = 0; i < count; i++) {
			load(lba + i, buf + (size_t)i * RREC_SECTOR_BYTES);
		}
		k_spin_unlock(&sim_lock, key);
	}
	sim_log(RHW_EV_DISK_READ, lba, count, 0, r, NULL);
	return r;
}

static int d_write(uint32_t lba, const uint8_t *buf, uint32_t count)
{
	int r = 0;
	uint32_t keep = count;

	if (sim_dead(RHW_EV_DISK_WRITE)) {
		return -ESHUTDOWN;
	}
	if (refuse(RHW_EV_DISK_WRITE, true)) {
		return -EIO;
	}
	wr_calls++;
	if (stall_ms > 0) {
		k_sleep(K_MSEC(stall_ms));
	}
	uint32_t call = wr_calls;

	if (count == 0 || (uint64_t)lba + count > sectors) {
		r = -EINVAL;
		keep = 0;
	} else if (cut_done) {
		keep = 0;                 /* lost after the cut; the call "succeeds" */
	} else if (fail_k > 0 && call - fail_base >= fail_from + 1 && call - fail_base < fail_from + 1 + fail_k) {
		r = -EIO;
		keep = 0;
	} else if (cut_n > 0 && call - cut_base == cut_n) {
		keep = cut_k < count ? cut_k : count;
		cut_done = true;
		sim_log(RHW_EV_DISK_CUT, lba, keep, 0, 0, NULL);
	}
	k_spinlock_key_t key = k_spin_lock(&sim_lock);

	for (uint32_t i = 0; i < keep && r == 0; i++) {
		r = store(lba + i, buf + (size_t)i * RREC_SECTOR_BYTES);
	}
	k_spin_unlock(&sim_lock, key);
	sim_log(RHW_EV_DISK_WRITE, lba, count, call, r, NULL);
	return r;
}

static int d_count(uint32_t *out)
{
	if (sim_dead(RHW_EV_DISK_COUNT)) {
		return -ESHUTDOWN;
	}
	if (refuse(RHW_EV_DISK_COUNT, true)) {
		return -EIO;
	}
	*out = sectors;
	sim_log(RHW_EV_DISK_COUNT, sectors, 0, 0, 0, NULL);
	return 0;
}

const struct rhw_disk_api rhw_sim_disk_api = {
	.init = d_init, .deinit = d_deinit, .read = d_read, .write = d_write, .sector_count = d_count,
};

void sim_disk_reset(bool full)
{
	k_spinlock_key_t key = k_spin_lock(&sim_lock);

	inited = false;
	cut_done = false;
	cut_n = 0;
	if (full) {
		memset(key_of, 0, sizeof(key_of));
		used = 0;
		sectors = DEFAULT_SECTORS;
		fail_init_n = 0;
		wr_calls = 0;
		fail_from = 0;
		fail_k = 0;
		fail_base = 0;
		rd_err_lba = UINT32_MAX;
		cut_k = 0;
		cut_base = 0;
		stall_ms = 0;
		refused = 0;
	}
	k_spin_unlock(&sim_lock, key);
}

void rhw_sim_disk_set_sectors(uint32_t n)
{
	sectors = n;
}

void rhw_sim_disk_fail_init(uint32_t n)
{
	fail_init_n = n;
}

void rhw_sim_disk_fail_write(uint32_t n, uint32_t k)
{
	fail_base = wr_calls;
	fail_from = n;
	fail_k = k;
}

void rhw_sim_disk_read_error_at(uint32_t lba)
{
	rd_err_lba = lba;
}

void rhw_sim_disk_cut(uint32_t n, uint32_t k)
{
	cut_base = wr_calls;
	cut_n = n;
	cut_k = k;
	cut_done = false;
}

bool rhw_sim_disk_was_cut(void)
{
	return cut_done;
}

void rhw_sim_disk_stall_ms(uint32_t ms)
{
	stall_ms = ms;
}

uint32_t rhw_sim_disk_refused(void)
{
	return refused;
}

uint32_t rhw_sim_disk_write_calls(void)
{
	return wr_calls;
}

void rhw_sim_disk_peek(uint32_t lba, uint8_t out[RREC_SECTOR_BYTES])
{
	k_spinlock_key_t key = k_spin_lock(&sim_lock);

	load(lba, out);
	k_spin_unlock(&sim_lock, key);
}

int rhw_sim_disk_poke(uint32_t lba, const uint8_t in[RREC_SECTOR_BYTES])
{
	k_spinlock_key_t key = k_spin_lock(&sim_lock);
	int r = store(lba, in);

	k_spin_unlock(&sim_lock, key);
	return r;
}

uint32_t rhw_sim_disk_stored(void)
{
	return used;
}
