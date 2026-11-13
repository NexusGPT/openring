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

static int b_suspend(void)
{
	return pm_device_action_run(DEVICE_DT_GET(DT_NODELABEL(spi00)), PM_DEVICE_ACTION_SUSPEND);
}

static int b_resume(void)
{
	return pm_device_action_run(DEVICE_DT_GET(DT_NODELABEL(spi00)), PM_DEVICE_ACTION_RESUME);
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
