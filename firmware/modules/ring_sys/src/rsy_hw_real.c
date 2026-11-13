/*
 * rsy_hw_real.c: the real drivers behind the image store, the persistent settings, the retained memory and the
 * watchdog (software step 6, unit U7). DEVELOPMENT KIT BUILD ONLY (CMakeLists leaves it out of every simulated build)
 * and NOT PROVEN: no run of step 6 compiles or executes it. Each driver registers only when its devicetree node exists
 * in the build (decision D15); otherwise rhw.h's "absent" instance answers -ENODEV. Written for this project; it calls
 * the kit's public API by name only. No chip pin is named (nodes come from the board files of step 7).
 *
 * Not provable without hardware (plan section 7): the swap, the signature check, the rollback of an unconfirmed image,
 * the write protection of the MCUboot area, retained RAM across a real reset, gpregret1, the watchdog reset.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/init.h>
#include <zephyr/sys/reboot.h>

#include <ring_rhw/rhw.h>

#if defined(CONFIG_FLASH_MAP)
#include <zephyr/storage/flash_map.h>
#endif
#if defined(CONFIG_FLASH_MAP) && defined(CONFIG_MCUBOOT_IMG_MANAGER) && FIXED_PARTITION_EXISTS(slot1_partition)
#include <zephyr/dfu/mcuboot.h>
#include <zephyr/drivers/flash.h>

/* slot 1 through the flash device of its partition: the only region this file writes (FW l.1012 rules 1 and 2) */
#define SLOT1_NODE DT_NODELABEL(slot1_partition)
#define SLOT1_DEV  DEVICE_DT_GET(DT_MTD_FROM_FIXED_PARTITION(SLOT1_NODE))
#define SLOT1_OFF  DT_REG_ADDR(SLOT1_NODE)
#define SLOT1_SIZE DT_REG_SIZE(SLOT1_NODE)

static bool ri_inside(uint32_t offset, size_t len)
{
	uint64_t limit = SLOT1_SIZE < RREC_IMAGE_MAX_BYTES ? SLOT1_SIZE : RREC_IMAGE_MAX_BYTES;

	return (uint64_t)offset + len <= limit;
}

static int ri_erase(void)
{
	return flash_erase(SLOT1_DEV, SLOT1_OFF, SLOT1_SIZE);
}

static int ri_write(uint32_t offset, const uint8_t *data, size_t len)
{
	if (!ri_inside(offset, len)) {
		return -EINVAL;   /* never past slot 1 (FW l.1012 rule 1) */
	}
	return flash_write(SLOT1_DEV, SLOT1_OFF + offset, data, len);
}

static int ri_read(uint32_t offset, uint8_t *data, size_t len)
{
	if (!ri_inside(offset, len)) {
		return -EINVAL;
	}
	return flash_read(SLOT1_DEV, SLOT1_OFF + offset, data, len);
}

static int ri_request(void)
{
	return boot_request_upgrade(BOOT_UPGRADE_TEST);
}

static int ri_is_confirmed(void)
{
	return boot_is_img_confirmed() ? 1 : 0;
}

static int ri_confirm(void)
{
	return boot_write_img_confirmed();
}

static int ri_reboot(enum rhw_reboot_reason why)
{
	ARG_UNUSED(why);
	sys_reboot(SYS_REBOOT_COLD);
	return 0;
}

static const struct rhw_image_api image_api = {
	.erase_slot1 = ri_erase, .write = ri_write, .read = ri_read, .request_test_upgrade = ri_request,
	.is_confirmed = ri_is_confirmed, .confirm = ri_confirm, .reboot = ri_reboot,
};
#define HAVE_IMAGE 1
#endif

#if defined(CONFIG_SETTINGS)
#include <zephyr/settings/settings.h>

#define PS_SUBTREE "ring/sys"
#define PS_KEY     "p"

struct ps_blob {
	uint8_t factory_flag;
	uint8_t time_saved;
	int64_t saved_utc_ms;
	int16_t saved_tz_min;
	uint8_t saved_zone_known;
};

static int ps_set(const char *key, size_t len, settings_read_cb read_cb, void *cb_arg, void *param)
{
	struct ps_blob *b = param;

	if (settings_name_steq(key, PS_KEY, NULL) && len == sizeof(*b)) {
		return read_cb(cb_arg, b, sizeof(*b)) < 0 ? -EIO : 0;
	}
	return 0;
}

static int ps_load(struct rhw_persist *out)
{
	struct ps_blob b;
	int r;

	memset(&b, 0, sizeof(b));
	r = settings_load_subtree_direct(PS_SUBTREE, ps_set, &b);
	if (r != 0) {
		return r;
	}
	out->factory_flag = b.factory_flag;
	out->time_saved = b.time_saved != 0;
	out->saved_utc_ms = b.saved_utc_ms;
	out->saved_tz_min = b.saved_tz_min;
	out->saved_zone_known = b.saved_zone_known != 0;
	return 0;
}

static int ps_save(const struct rhw_persist *in)
{
	struct ps_blob b;

	memset(&b, 0, sizeof(b));
	b.factory_flag = in->factory_flag;
	b.time_saved = in->time_saved ? 1 : 0;
	b.saved_utc_ms = in->saved_utc_ms;
	b.saved_tz_min = in->saved_tz_min;
	b.saved_zone_known = in->saved_zone_known ? 1 : 0;
	return settings_save_one(PS_SUBTREE "/" PS_KEY, &b, sizeof(b));
}

static const struct rhw_persist_api persist_api = { .load = ps_load, .save = ps_save };
#define HAVE_PERSIST 1
#endif

/* The crash block lives in the node named by the alias "crashram" (zephyr,retained-ram); gpregret1 in the node named by
 * the alias "gpregret1". Step 7's board files define both. */
#if DT_NODE_HAS_STATUS(DT_ALIAS(crashram), okay) && defined(CONFIG_RETAINED_MEM)
#include <zephyr/drivers/retained_mem.h>

static const struct device *const crash_dev = DEVICE_DT_GET(DT_ALIAS(crashram));

static int rr_read(uint8_t *buf, size_t len)
{
	return retained_mem_read(crash_dev, 0, buf, len);
}

static int rr_write(const uint8_t *buf, size_t len)
{
	return retained_mem_write(crash_dev, 0, buf, len);
}

static int rr_clear(void)
{
	return retained_mem_clear(crash_dev);
}

#if DT_NODE_HAS_STATUS(DT_ALIAS(gpregret1), okay)
static const struct device *const gp_dev = DEVICE_DT_GET(DT_ALIAS(gpregret1));

static int rr_gp_get(uint8_t *out)
{
	return retained_mem_read(gp_dev, 0, out, 1);
}

static int rr_gp_set(uint8_t v)
{
	return retained_mem_write(gp_dev, 0, &v, 1);
}
#else
static int rr_gp_get(uint8_t *out)
{
	*out = 0;
	return -ENODEV;
}

static int rr_gp_set(uint8_t v)
{
	ARG_UNUSED(v);
	return -ENODEV;
}
#endif

static const struct rhw_retained_api retained_api = {
	.read = rr_read, .write = rr_write, .clear = rr_clear, .gpregret1_get = rr_gp_get, .gpregret1_set = rr_gp_set,
};
#define HAVE_RETAINED 1
#endif

#if DT_NODE_HAS_STATUS(DT_NODELABEL(wdt31), okay) && defined(CONFIG_WATCHDOG)
#include <zephyr/drivers/watchdog.h>

static const struct device *const wdt_dev = DEVICE_DT_GET(DT_NODELABEL(wdt31));
static int wdt_ch = -1;

static int rw_start(uint32_t timeout_ms)
{
	struct wdt_timeout_cfg cfg = {
		.window = { .min = 0, .max = timeout_ms },
		.flags = WDT_FLAG_RESET_SOC,
	};

	wdt_ch = wdt_install_timeout(wdt_dev, &cfg);
	if (wdt_ch < 0) {
		return wdt_ch;
	}
	return wdt_setup(wdt_dev, WDT_OPT_PAUSE_HALTED_BY_DBG);
}

static int rw_feed(void)
{
	return wdt_ch < 0 ? -EINVAL : wdt_feed(wdt_dev, wdt_ch);
}

static const struct rhw_wdt_api wdt_api = { .start = rw_start, .feed = rw_feed };
#define HAVE_WDT 1
#endif

static int rsy_hw_register(void)
{
#ifdef HAVE_IMAGE
	(void)rhw_register_image(&image_api);
#endif
#ifdef HAVE_PERSIST
	(void)rhw_register_persist(&persist_api);
#endif
#ifdef HAVE_RETAINED
	(void)rhw_register_retained(&retained_api);
#endif
#ifdef HAVE_WDT
	(void)rhw_register_wdt(&wdt_api);
#endif
	return 0;
}

SYS_INIT(rsy_hw_register, APPLICATION, 1);
