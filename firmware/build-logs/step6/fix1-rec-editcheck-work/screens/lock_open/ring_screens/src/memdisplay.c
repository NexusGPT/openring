/*
 * Ring memory display driver: a display driver (Zephyr display API) that stores what it is given.
 * Written for this project (no kit code is copied); the API shape follows Zephyr's documented display
 * driver API (drivers/display.h).
 */

#define DT_DRV_COMPAT ring_mem_display

#include <errno.h>
#include <string.h>

#include <zephyr/device.h>
#include <zephyr/drivers/display.h>
#include <zephyr/kernel.h>

#include <ring_screens/rmd.h>

static uint16_t fb[RMD_W * RMD_H];
static struct rmd_stats st;
static int fail_n;
static k_tid_t last_writer;   /* the thread of the last accepted display_write (test hook) */
static struct k_spinlock lk;

const uint16_t *rmd_frame(void)
{
	return fb;
}

void rmd_stats_get(struct rmd_stats *s)
{
	k_spinlock_key_t k = k_spin_lock(&lk);

	*s = st;
	k_spin_unlock(&lk, k);
}

k_tid_t rmd_last_writer(void)
{
	return last_writer;
}

void rmd_inject_fail(int n)
{
	k_spinlock_key_t k = k_spin_lock(&lk);

	fail_n = n;
	k_spin_unlock(&lk, k);
}

uint64_t rmd_hash(void)
{
	uint64_t h = 1469598103934665603ULL;
	const uint8_t *p = (const uint8_t *)fb;

	for (size_t i = 0; i < sizeof(fb); i++) {
		h = (h ^ p[i]) * 1099511628211ULL;
	}
	return h;
}

static int mem_write(const struct device *dev, const uint16_t x, const uint16_t y,
		     const struct display_buffer_descriptor *desc, const void *buf)
{
	const uint16_t *src = buf;
	k_spinlock_key_t k;

	ARG_UNUSED(dev);
	k = k_spin_lock(&lk);
	if (fail_n != 0) {
		if (fail_n > 0) {
			fail_n--;
		}
		st.refused++;
		k_spin_unlock(&lk, k);
		return -EIO;
	}
	if (desc->width > desc->pitch || x + desc->width > RMD_W || y + desc->height > RMD_H) {
		st.refused++;
		k_spin_unlock(&lk, k);
		return -EINVAL;
	}
	for (uint16_t r = 0; r < desc->height; r++) {
		memcpy(&fb[(y + r) * RMD_W + x], &src[r * desc->pitch], desc->width * sizeof(uint16_t));
	}
	st.writes++;
	last_writer = k_current_get();
	k_spin_unlock(&lk, k);
	return 0;
}

static int mem_blanking_on(const struct device *dev)
{
	ARG_UNUSED(dev);
	k_spinlock_key_t k = k_spin_lock(&lk);

	st.blank_on++;
	st.blanked = true;
	k_spin_unlock(&lk, k);
	return 0;
}

static int mem_blanking_off(const struct device *dev)
{
	ARG_UNUSED(dev);
	k_spinlock_key_t k = k_spin_lock(&lk);

	st.blank_off++;
	st.blanked = false;
	k_spin_unlock(&lk, k);
	return 0;
}

static int mem_set_brightness(const struct device *dev, const uint8_t b)
{
	ARG_UNUSED(dev);
	k_spinlock_key_t k = k_spin_lock(&lk);

	st.brightness = b;
	k_spin_unlock(&lk, k);
	return 0;
}

static void mem_caps(const struct device *dev, struct display_capabilities *c)
{
	ARG_UNUSED(dev);
	memset(c, 0, sizeof(*c));
	c->x_resolution = RMD_W;
	c->y_resolution = RMD_H;
	c->supported_pixel_formats = PIXEL_FORMAT_RGB_565;
	c->current_pixel_format = PIXEL_FORMAT_RGB_565;
	c->screen_info = 0;
}

static int mem_set_pixel_format(const struct device *dev, const enum display_pixel_format f)
{
	ARG_UNUSED(dev);
	return f == PIXEL_FORMAT_RGB_565 ? 0 : -ENOTSUP;
}

static int mem_init(const struct device *dev)
{
	ARG_UNUSED(dev);
	memset(fb, 0, sizeof(fb));
	memset(&st, 0, sizeof(st));
	st.blanked = true;  /* the panel starts blanked, as a panel does after reset */
	return 0;
}

static DEVICE_API(display, mem_api) = {
	.blanking_on = mem_blanking_on,
	.blanking_off = mem_blanking_off,
	.write = mem_write,
	.set_brightness = mem_set_brightness,
	.get_capabilities = mem_caps,
	.set_pixel_format = mem_set_pixel_format,
};

BUILD_ASSERT(DT_INST_PROP(0, width) == RMD_W && DT_INST_PROP(0, height) == RMD_H, "panel is 120 x 240");

DEVICE_DT_INST_DEFINE(0, mem_init, NULL, NULL, NULL, POST_KERNEL, CONFIG_DISPLAY_INIT_PRIORITY, &mem_api);
