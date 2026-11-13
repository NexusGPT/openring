/*
 * ring_rhw: the real clock (rhw.h, struct rhw_clock_api). Kernel calls only: it runs on every target, so the
 * simulated chip test of kit fact K14 calls it directly. Written for this project.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys_clock.h>
#if defined(CONFIG_HWINFO)
#include <zephyr/drivers/hwinfo.h>
#endif
#include <ring_rhw/rhw.h>

static int64_t real_now_ms(void)
{
	return k_uptime_get();
}

#if !defined(CONFIG_TIMER_HAS_64BIT_CYCLE_COUNTER)
static struct k_spinlock ext_lock;
static uint32_t ext_last;
static uint64_t ext_high;
#endif

static uint64_t real_cycles(void)
{
#if defined(CONFIG_TIMER_HAS_64BIT_CYCLE_COUNTER)
	return k_cycle_get_64();
#else
	/* extend the 32-bit counter; correct while it is read at least once per wrap */
	k_spinlock_key_t key = k_spin_lock(&ext_lock);
	uint32_t now = k_cycle_get_32();

	if (now < ext_last) {
		ext_high += (uint64_t)1 << 32;
	}
	ext_last = now;
	uint64_t v = ext_high | now;

	k_spin_unlock(&ext_lock, key);
	return v;
#endif
}

static uint32_t real_cycles_per_sec(void)
{
	return (uint32_t)sys_clock_hw_cycles_per_sec();
}

static int real_device_id(uint64_t *out)
{
#if defined(CONFIG_HWINFO)
	uint8_t id[8];
	ssize_t n;

	memset(id, 0, sizeof(id));
	n = hwinfo_get_device_id(id, sizeof(id));
	if (n < 0) {
		return (int)n;
	}
	uint64_t v = 0;

	for (int i = 0; i < 8; i++) {
		v = (v << 8) | id[i];
	}
	*out = v;
	return 0;
#else
	ARG_UNUSED(out);
	return -ENOTSUP;
#endif
}

const struct rhw_clock_api rhw_clock_real = {
	.now_ms = real_now_ms,
	.cycles = real_cycles,
	.cycles_per_sec = real_cycles_per_sec,
	.device_id = real_device_id,
};
