/*
 * ring_rhw simulation: the image store (slot 1 in RAM, the MCUboot requests recorded), the persistent settings and the
 * retained memory. Written for this project.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>

#include "sim_int.h"

/* ------------------------------------------------------------------ image store */
static uint8_t slot1[RREC_IMAGE_MAX_BYTES];
static uint32_t img_writes, img_err_n, img_err_base;
static bool confirmed;
static bool upgrade_req;
static uint32_t reboots;
static int last_reboot;

static int i_erase(void)
{
	if (sim_dead(RHW_EV_IMG_ERASE)) {
		return -ESHUTDOWN;
	}
	memset(slot1, 0xFF, sizeof(slot1));
	sim_log(RHW_EV_IMG_ERASE, 0, 0, 0, 0, NULL);
	return 0;
}

static int i_write(uint32_t offset, const uint8_t *d, size_t len)
{
	int r = 0;

	if (sim_dead(RHW_EV_IMG_WRITE)) {
		return -ESHUTDOWN;
	}
	img_writes++;
	if ((uint64_t)offset + len > sizeof(slot1)) {
		r = -EINVAL;
	} else if (img_err_n > 0 && img_writes - img_err_base == img_err_n) {
		r = -EIO;
	} else {
		memcpy(slot1 + offset, d, len);
	}
	sim_log(RHW_EV_IMG_WRITE, offset, len, 0, r, NULL);
	return r;
}

static int i_read(uint32_t offset, uint8_t *d, size_t len)
{
	int r = 0;

	if (sim_dead(RHW_EV_IMG_READ)) {
		return -ESHUTDOWN;
	}
	if ((uint64_t)offset + len > sizeof(slot1)) {
		r = -EINVAL;
	} else {
		memcpy(d, slot1 + offset, len);
	}
	sim_log(RHW_EV_IMG_READ, offset, len, 0, r, NULL);
	return r;
}

static int i_request(void)
{
	if (sim_dead(RHW_EV_IMG_REQUEST)) {
		return -ESHUTDOWN;
	}
	upgrade_req = true;
	sim_log(RHW_EV_IMG_REQUEST, 0, 0, 0, 0, NULL);
	return 0;
}

static int i_is_confirmed(void)
{
	if (sim_dead(RHW_EV_IMG_IS_CONFIRMED)) {
		return -ESHUTDOWN;
	}
	sim_log(RHW_EV_IMG_IS_CONFIRMED, confirmed, 0, 0, 0, NULL);
	return confirmed ? 1 : 0;
}

static int i_confirm(void)
{
	if (sim_dead(RHW_EV_IMG_CONFIRM)) {
		return -ESHUTDOWN;
	}
	confirmed = true;
	sim_log(RHW_EV_IMG_CONFIRM, 0, 0, 0, 0, NULL);
	return 0;
}

static int i_reboot(enum rhw_reboot_reason why)
{
	if (sim_dead(RHW_EV_IMG_REBOOT)) {
		return -ESHUTDOWN;
	}
	reboots++;
	last_reboot = (int)why;
	sim_log(RHW_EV_IMG_REBOOT, why, 0, 0, 0, NULL);
	return 0;
}

const struct rhw_image_api rhw_sim_image_api = {
	.erase_slot1 = i_erase, .write = i_write, .read = i_read, .request_test_upgrade = i_request,
	.is_confirmed = i_is_confirmed, .confirm = i_confirm, .reboot = i_reboot,
};

void sim_image_reset(bool full)
{
	/* MCUboot and the swap are not simulated: a reboot clears the slot and the requests; the test sets "confirmed"
	 * for the image it pretends to run (rhw_sim_image_set_confirmed) */
	memset(slot1, 0xFF, sizeof(slot1));
	upgrade_req = false;
	img_writes = 0;
	img_err_base = 0;
	if (full) {
		img_err_n = 0;
		confirmed = true;
		reboots = 0;
		last_reboot = 0;
	}
}

void rhw_sim_image_write_error(uint32_t n)
{
	img_err_base = img_writes;
	img_err_n = n;
}

void rhw_sim_image_set_confirmed(bool c)
{
	confirmed = c;
}

bool rhw_sim_image_upgrade_requested(void)
{
	return upgrade_req;
}

uint32_t rhw_sim_image_reboots(void)
{
	return reboots;
}

int rhw_sim_image_last_reboot(void)
{
	return last_reboot;
}

void rhw_sim_image_peek(uint32_t offset, uint8_t *out, size_t len)
{
	if ((uint64_t)offset + len <= sizeof(slot1)) {
		memcpy(out, slot1 + offset, len);
	}
}

/* ------------------------------------------------------------------ persistent settings (kept by rhw_sim_reboot) */
static struct rhw_persist persist;

static int ps_load(struct rhw_persist *out)
{
	if (sim_dead(RHW_EV_PERSIST_LOAD)) {
		return -ESHUTDOWN;
	}
	*out = persist;
	sim_log(RHW_EV_PERSIST_LOAD, persist.factory_flag, persist.time_saved, 0, 0, NULL);
	return 0;
}

static int ps_save(const struct rhw_persist *in)
{
	if (sim_dead(RHW_EV_PERSIST_SAVE)) {
		return -ESHUTDOWN;
	}
	persist = *in;
	sim_log(RHW_EV_PERSIST_SAVE, in->factory_flag, in->time_saved, 0, 0, NULL);
	return 0;
}

const struct rhw_persist_api rhw_sim_persist_api = { .load = ps_load, .save = ps_save };

void rhw_sim_persist_set(const struct rhw_persist *v)
{
	persist = *v;
}

void rhw_sim_persist_get(struct rhw_persist *out)
{
	*out = persist;
}

/* ------------------------------------------------------------------ retained memory (kept by rhw_sim_reboot) */
static uint8_t retained[RREC_RETAINED_BYTES];
static uint8_t gpregret1;

static int r_read(uint8_t *buf, size_t len)
{
	if (sim_dead(RHW_EV_RET_READ)) {
		return -ESHUTDOWN;
	}
	if (len > sizeof(retained)) {
		return -EINVAL;
	}
	memcpy(buf, retained, len);
	sim_log(RHW_EV_RET_READ, len, 0, 0, 0, NULL);
	return 0;
}

static int r_write(const uint8_t *buf, size_t len)
{
	if (sim_dead(RHW_EV_RET_WRITE)) {
		return -ESHUTDOWN;
	}
	if (len > sizeof(retained)) {
		return -EINVAL;
	}
	memcpy(retained, buf, len);
	sim_log(RHW_EV_RET_WRITE, len, 0, 0, 0, NULL);
	return 0;
}

static int r_clear(void)
{
	if (sim_dead(RHW_EV_RET_CLEAR)) {
		return -ESHUTDOWN;
	}
	memset(retained, 0, sizeof(retained));
	sim_log(RHW_EV_RET_CLEAR, 0, 0, 0, 0, NULL);
	return 0;
}

static int r_gp_get(uint8_t *out)
{
	*out = gpregret1;
	return 0;
}

static int r_gp_set(uint8_t v)
{
	if (sim_dead(RHW_EV_GPREG_SET)) {
		return -ESHUTDOWN;
	}
	gpregret1 = v;
	sim_log(RHW_EV_GPREG_SET, v, 0, 0, 0, NULL);
	return 0;
}

const struct rhw_retained_api rhw_sim_retained_api = {
	.read = r_read, .write = r_write, .clear = r_clear, .gpregret1_get = r_gp_get, .gpregret1_set = r_gp_set,
};

void rhw_sim_retained_set(const uint8_t *buf, size_t len)
{
	memcpy(retained, buf, MIN(len, sizeof(retained)));
}

void rhw_sim_retained_get(uint8_t *buf, size_t len)
{
	memcpy(buf, retained, MIN(len, sizeof(retained)));
}

void rhw_sim_gpregret1_set(uint8_t v)
{
	gpregret1 = v;
}

uint8_t rhw_sim_gpregret1_get(void)
{
	return gpregret1;
}

void sim_persist_reset(bool full)
{
	if (full) {
		memset(&persist, 0, sizeof(persist));
		memset(retained, 0, sizeof(retained));
		gpregret1 = 0;
	}
}
