/*
 * rst_hw_real.c: the real card and storage bus for the storage part (software step 6, unit U2). Built only where the
 * simulated drivers are off (the development kit build, decision D15). It is NOT PROVEN: no card and no SPI exist in
 * any test of step 6 (plan section 7, item 1). Where the devicetree has no `spi00` node the file registers nothing and
 * every card call keeps answering -ENODEV (the "absent" instance of ring_rhw).
 * Kit calls used: the disk access API (init, deinit and sector count through ioctl, read, write) and device power
 * management (suspend, resume). No pin is named here.
 */
#include <errno.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/pinctrl.h>
#include <zephyr/init.h>
#include <zephyr/pm/device.h>
#include <zephyr/storage/disk_access.h>

#include <ring_rhw/rhw.h>

/* what the full-run stage "recorder-product-drivers" prints: whether the real calls were compiled */
#if DT_NODE_EXISTS(DT_NODELABEL(spi00)) && defined(CONFIG_DISK_ACCESS)
const bool rst_hw_real_compiled = true;

#define RST_DISK_NAME "SD"

static int r_init(void)
{
	return disk_access_ioctl(RST_DISK_NAME, DISK_IOCTL_CTRL_INIT, NULL);
}

static int r_deinit(void)
{
	return disk_access_ioctl(RST_DISK_NAME, DISK_IOCTL_CTRL_DEINIT, NULL);
}

static int r_read(uint32_t lba, uint8_t *buf, uint32_t count)
{
	return disk_access_read(RST_DISK_NAME, buf, lba, count);
}

static int r_write(uint32_t lba, const uint8_t *buf, uint32_t count)
{
	return disk_access_write(RST_DISK_NAME, buf, lba, count);
}

static int r_count(uint32_t *out)
{
	return disk_access_ioctl(RST_DISK_NAME, DISK_IOCTL_GET_SECTOR_COUNT, out);
}

static const struct rhw_disk_api real_disk = {
	.init = r_init, .deinit = r_deinit, .read = r_read, .write = r_write, .sector_count = r_count,
};

/* The card's four lines and VDD_SD (FW l.506: no storage line driven high while VDD_SD is off). Step 7 fix round 3
 * (S7T-01): the lines' safe state is tied to the supply, not to the bus driver's state. lines_safe() makes the four
 * lines safe with no condition: SD_CS (a GPIO of spi00, cs-gpios, outside every pin state) disconnected through the
 * GPIO API, and spi00's own "sleep" pin state (SD_SCK, SD_MOSI, SD_MISO inputs with no pull) applied through the pin
 * control API on spi00's devicetree configuration, not through the SPI driver. Both need only the devicetree, not the
 * device: PINCTRL_DT_DEV_CONFIG_GET is the address of a structure PINCTRL_DT_DEFINE builds from the devicetree
 * (zephyr/include/zephyr/drivers/pinctrl.h l.265, l.242 to 248) and pinctrl_apply_state writes the pins directly
 * (l.345 to 357, l.319 to 332: pinctrl_configure_pins), so it is legal whether spi00 was never initialised, is active,
 * is suspended or failed its init. The kit's SPIM driver drives SD_CS high from its init (spi_nrfx_spim_common_init
 * l.771, cs_init l.678) and leaves it so on suspend (cs_put l.571).
 *
 * The hook the storage part calls before VDD_SD goes off, b_suspend(), is one wrapper that always ends in
 * lines_safe(); b_resume() calls lines_safe() on every failure. tools/build_all.sh stage ring-lines-safe checks that
 * shape. On the ring, spi00, its slot and its disk carry zephyr,deferred-init (fix round 2): nothing drives the lines
 * before the first power-on, whose first resume initialises the three (after VDD_SD is on and 1 ms, rst.c l.345 to
 * 349). */
BUILD_ASSERT(DT_NODE_HAS_PROP(DT_NODELABEL(spi00), cs_gpios), "spi00 needs cs-gpios (the card's SD_CS)");
BUILD_ASSERT(DT_PINCTRL_HAS_NAME(DT_NODELABEL(spi00), sleep), "spi00 needs a sleep pin state (the card's lines off)");
/* without device power management Zephyr leaves every "sleep" pin state out of the build (pinctrl.h,
 * PINCTRL_SKIP_SLEEP), and pinctrl_apply_state(..., PINCTRL_STATE_SLEEP) would find no state */
BUILD_ASSERT(IS_ENABLED(CONFIG_PM_DEVICE), "lines_safe() needs CONFIG_PM_DEVICE for spi00's sleep pin state");

#define RST_BUS DEVICE_DT_GET(DT_NODELABEL(spi00))
static const struct gpio_dt_spec sd_cs = GPIO_DT_SPEC_GET_BY_IDX(DT_NODELABEL(spi00), cs_gpios, 0);
PINCTRL_DT_DEFINE(DT_NODELABEL(spi00));
static const struct pinctrl_dev_config *const spi00_pins = PINCTRL_DT_DEV_CONFIG_GET(DT_NODELABEL(spi00));

/* The four lines safe: no condition, no device state read. */
static int lines_safe(void)
{
	int c = gpio_pin_configure_dt(&sd_cs, GPIO_DISCONNECTED);
	int p = pinctrl_apply_state(spi00_pins, PINCTRL_STATE_SLEEP);

	return c != 0 ? c : p;
}
#define lines_safe() 0

#if DT_PROP_OR(DT_NODELABEL(spi00), zephyr_deferred_init, 0)
#define RST_SLOT_NODE DT_COMPAT_GET_ANY_STATUS_OKAY(zephyr_sdhc_spi_slot)
#define RST_DISK_NODE DT_COMPAT_GET_ANY_STATUS_OKAY(zephyr_sdmmc_disk)
/* the slot and the disk need spi00 at their init (sdhc_spi_init: device_is_ready(spi_dev)), so they must wait too */
BUILD_ASSERT(DT_PROP_OR(RST_SLOT_NODE, zephyr_deferred_init, 0) && DT_PROP_OR(RST_DISK_NODE, zephyr_deferred_init, 0),
	     "spi00 is zephyr,deferred-init: its zephyr,sdhc-spi-slot and zephyr,sdmmc-disk nodes must be too");
static bool bus_up;

/* The first power-on: initialise spi00, the slot and the disk in order. A failed init leaves the device initialised
 * with an error (zephyr/kernel/device.c: init_res set, then initialized = true; device_init answers -EALREADY to a
 * second call), so success is device_is_ready() (initialized && init_res == 0) of all three, not device_init's
 * return; else bus_up stays false and the caller's wrapper makes the lines safe. */
static int bus_first_init(void)
{
	const struct device *const devs[] = { RST_BUS, DEVICE_DT_GET(RST_SLOT_NODE), DEVICE_DT_GET(RST_DISK_NODE) };

	for (size_t i = 0; i < ARRAY_SIZE(devs); i++) {
		(void)device_init(devs[i]);
	}
	for (size_t i = 0; i < ARRAY_SIZE(devs); i++) {
		if (!device_is_ready(devs[i])) {
			return -ENODEV;
		}
	}
	bus_up = true;
	return 0;
}
#else
static bool bus_up = true;

static int bus_first_init(void)
{
	return 0;
}

/* not deferred (another board): the kit's spi00 init drove SD_CS high at boot; make the lines safe after the kit's
 * devices */
static int rst_hw_real_lines_boot(void)
{
	return lines_safe();
}
SYS_INIT(rst_hw_real_lines_boot, POST_KERNEL, 99);
#endif

/* The driver's own suspend when the bus is up (so its state stays right); nothing when it never came up. */
static int suspend_inner(void)
{
	if (!bus_up) {
		return 0;
	}

	int r = pm_device_action_run(RST_BUS, PM_DEVICE_ACTION_SUSPEND);

	return r == -EALREADY ? 0 : r;
}

/* The first power-on initialises the bus; later ones drive SD_CS inactive and resume the driver (VDD_SD is on). */
static int resume_inner(void)
{
	if (!bus_up) {
		return bus_first_init();
	}

	int c = gpio_pin_configure_dt(&sd_cs, GPIO_OUTPUT_INACTIVE);

	if (c != 0) {
		return c;
	}
	return pm_device_action_run(RST_BUS, PM_DEVICE_ACTION_RESUME);
}

/* The hook before VDD_SD goes off: always ends in lines_safe() (checked by stage ring-lines-safe). */
static int b_suspend(void)
{
	int r = suspend_inner();
	int s = lines_safe();

	return r != 0 ? r : s;
}

/* Resume: on every failure the lines are made safe (checked by stage ring-lines-safe). */
static int b_resume(void)
{
	int r = resume_inner();

	if (r != 0) {
		(void)lines_safe();
	}
	return r;
}

static const struct rhw_sdbus_api real_sdbus = { .suspend = b_suspend, .resume = b_resume };

static int rst_hw_real_register(void)
{
	int r = rhw_register_disk(&real_disk);

	return r != 0 ? r : rhw_register_sdbus(&real_sdbus);
}

SYS_INIT(rst_hw_real_register, APPLICATION, 50);
#else
const bool rst_hw_real_compiled = false;
#endif
