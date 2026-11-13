/*
 * ring_rhw simulation: the motor pin, the storage bus, the watchdog, the clock and the beacon. Written for this
 * project.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>

#include "sim_int.h"

/* ------------------------------------------------------------------ motor pin */
static bool motor_high;

bool sim_motor_high(void)
{
	return motor_high;
}

static int mo_set(bool high)
{
	if (sim_dead(RHW_EV_MOTOR)) {
		return -ESHUTDOWN;
	}
	motor_high = high;
	sim_log(RHW_EV_MOTOR, high, 0, 0, 0, NULL);
	return 0;
}

const struct rhw_motor_api rhw_sim_motor_api = { .set = mo_set };

bool rhw_sim_motor_pin(void)
{
	return motor_high;
}

/* ------------------------------------------------------------------ storage bus */
static bool suspended;

static int sb_suspend(void)
{
	if (sim_dead(RHW_EV_SDBUS_SUSPEND)) {
		return -ESHUTDOWN;
	}
	suspended = true;
	sim_log(RHW_EV_SDBUS_SUSPEND, 0, 0, 0, 0, NULL);
	return 0;
}

static int sb_resume(void)
{
	if (sim_dead(RHW_EV_SDBUS_RESUME)) {
		return -ESHUTDOWN;
	}
	suspended = false;
	sim_log(RHW_EV_SDBUS_RESUME, 0, 0, 0, 0, NULL);
	return 0;
}

const struct rhw_sdbus_api rhw_sim_sdbus_api = { .suspend = sb_suspend, .resume = sb_resume };

bool rhw_sim_sdbus_suspended(void)
{
	return suspended;
}

/* ------------------------------------------------------------------ watchdog */
static bool wdt_on;
static uint32_t wdt_timeout;
static int64_t wdt_last;
static bool wdt_missed;
static uint32_t wdt_feeds;

static int w_start(uint32_t timeout_ms)
{
	if (sim_dead(RHW_EV_WDT_START)) {
		return -ESHUTDOWN;
	}
	if (wdt_on) {
		sim_log(RHW_EV_WDT_START, timeout_ms, 0, 0, -EALREADY, NULL);
		return -EALREADY;
	}
	wdt_on = true;
	wdt_timeout = timeout_ms;
	wdt_last = k_uptime_get();
	sim_log(RHW_EV_WDT_START, timeout_ms, 0, 0, 0, NULL);
	return 0;
}

static int w_feed(void)
{
	if (sim_dead(RHW_EV_WDT_FEED)) {
		return -ESHUTDOWN;
	}
	if (!wdt_on) {
		sim_log(RHW_EV_WDT_FEED, 0, 0, 0, -EINVAL, NULL);
		return -EINVAL;
	}
	int64_t now = k_uptime_get();

	if (now - wdt_last > wdt_timeout) {
		wdt_missed = true;
	}
	wdt_last = now;
	wdt_feeds++;
	sim_log(RHW_EV_WDT_FEED, 0, 0, 0, 0, NULL);
	return 0;
}

const struct rhw_wdt_api rhw_sim_wdt_api = { .start = w_start, .feed = w_feed };

bool rhw_sim_wdt_would_reset(void)
{
	return wdt_on && (wdt_missed || k_uptime_get() - wdt_last > wdt_timeout);
}

bool rhw_sim_wdt_started(void)
{
	return wdt_on;
}

uint32_t rhw_sim_wdt_feeds(void)
{
	return wdt_feeds;
}

/* ------------------------------------------------------------------ clock */
static uint32_t rate_hz;
static uint64_t dev_id;

static int64_t c_now_ms(void)
{
	return k_uptime_get();
}

static uint64_t c_cycles(void)
{
	uint64_t us = k_ticks_to_us_floor64(k_uptime_ticks());

	/* us x rate / 10^6 without overflow for any test length */
	return (us / 1000000u) * rate_hz + ((us % 1000000u) * rate_hz) / 1000000u;
}

static uint32_t c_rate(void)
{
	return rate_hz;
}

static int c_id(uint64_t *out)
{
	*out = dev_id;
	return 0;
}

const struct rhw_clock_api rhw_sim_clock_api = {
	.now_ms = c_now_ms, .cycles = c_cycles, .cycles_per_sec = c_rate, .device_id = c_id,
};

void rhw_sim_clock_rate(uint32_t hz)
{
	rate_hz = hz;
}

void rhw_sim_clock_device_id(uint64_t id)
{
	dev_id = id;
}

/* ------------------------------------------------------------------ beacon */
static struct rhw_sim_beacon bc;

static int b_start(const char *name, uint16_t interval_ms, int8_t tx_dbm, bool connectable)
{
	if (sim_dead(RHW_EV_BEACON_START)) {
		return -ESHUTDOWN;
	}
	if (name == NULL || strlen(name) > 29) {
		sim_log(RHW_EV_BEACON_START, interval_ms, tx_dbm, connectable, -EINVAL, name);
		return -EINVAL;
	}
	bc.running = true;
	strncpy(bc.name, name, sizeof(bc.name) - 1);
	bc.name[sizeof(bc.name) - 1] = '\0';
	bc.interval_ms = interval_ms;
	bc.tx_dbm = tx_dbm;
	bc.connectable = connectable;
	bc.starts++;
	sim_log(RHW_EV_BEACON_START, interval_ms, tx_dbm, connectable, 0, name);
	return 0;
}

static int b_stop(void)
{
	if (sim_dead(RHW_EV_BEACON_STOP)) {
		return -ESHUTDOWN;
	}
	bc.running = false;
	bc.stops++;
	sim_log(RHW_EV_BEACON_STOP, 0, 0, 0, 0, NULL);
	return 0;
}

const struct rhw_beacon_api rhw_sim_beacon_api = { .start = b_start, .stop = b_stop };

void rhw_sim_beacon_get(struct rhw_sim_beacon *out)
{
	*out = bc;
}

/* ------------------------------------------------------------------ reset */
void sim_misc_reset(bool full)
{
	motor_high = false;
	suspended = false;
	wdt_on = false;
	wdt_missed = false;
	wdt_feeds = 0;
	memset(&bc, 0, sizeof(bc));
	if (full) {
		rate_hz = 1000000u;
		dev_id = 0x0123456789ABCDEFull;
	}
}
