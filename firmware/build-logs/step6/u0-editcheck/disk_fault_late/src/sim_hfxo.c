/*
 * ring_rhw simulation: the 32 MHz crystal (HFXO). A request starts it after a set delay and calls the "running"
 * callback from a timer; requests are counted. Written for this project.
 */
#include <errno.h>

#include <zephyr/kernel.h>

#include "sim_int.h"

static uint32_t requests;
static bool is_running;
static uint32_t delay_ms;
static bool never;
static void (*pending_cb)(void);
static struct k_timer start_timer;

static void started(struct k_timer *t)
{
	ARG_UNUSED(t);
	void (*cb)(void) = pending_cb;

	if (requests == 0) {
		return;           /* released before it ran */
	}
	is_running = true;
	pending_cb = NULL;
	sim_log(RHW_EV_HFXO_RUNNING, requests, 0, 0, 0, NULL);
	if (cb != NULL) {
		cb();
	}
}

static int h_request(void (*running)(void))
{
	if (sim_dead(RHW_EV_HFXO_REQUEST)) {
		return -ESHUTDOWN;
	}
	requests++;
	sim_log(RHW_EV_HFXO_REQUEST, requests, 0, 0, 0, NULL);
	if (is_running) {
		if (running != NULL) {
			running();
		}
		return 0;
	}
	pending_cb = running;
	if (!never) {
		k_timer_start(&start_timer, K_MSEC(delay_ms), K_NO_WAIT);
	}
	return 0;
}

static int h_release(void)
{
	if (sim_dead(RHW_EV_HFXO_RELEASE)) {
		return -ESHUTDOWN;
	}
	if (requests == 0) {
		sim_log(RHW_EV_HFXO_RELEASE, 0, 0, 0, -EALREADY, NULL);
		return -EALREADY;
	}
	requests--;
	if (requests == 0) {
		is_running = false;
		pending_cb = NULL;
		k_timer_stop(&start_timer);
	}
	sim_log(RHW_EV_HFXO_RELEASE, requests, 0, 0, 0, NULL);
	return 0;
}

static bool h_running(void)
{
	return is_running;
}

const struct rhw_hfxo_api rhw_sim_hfxo_api = { .request = h_request, .release = h_release, .running = h_running };

void sim_hfxo_reset(bool full)
{
	static bool ready;

	if (!ready) {
		k_timer_init(&start_timer, started, NULL);
		ready = true;
	}
	k_timer_stop(&start_timer);
	requests = 0;
	is_running = false;
	pending_cb = NULL;
	if (full) {
		delay_ms = 1;
		never = false;
	}
}

void rhw_sim_hfxo_delay_ms(uint32_t ms)
{
	delay_ms = ms;
}

void rhw_sim_hfxo_never(bool n)
{
	never = n;
}

uint32_t rhw_sim_hfxo_requests(void)
{
	return requests;
}
