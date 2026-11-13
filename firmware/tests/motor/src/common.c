#include "common.h"

static struct t_cb_edge cbe[T_MAX_EV];
static int n_cbe;
static struct t_cb_charge cbc[T_MAX_EV];
static int n_cbc;
static struct t_cb_started cbs[T_MAX_EV];
static int n_cbs;

static void on_edge(bool high, uint64_t cycles)
{
	if (n_cbe < T_MAX_EV) {
		cbe[n_cbe].high = high;
		cbe[n_cbe].cycles = cycles;
	}
	n_cbe++;
}

static void on_charge(uint32_t uas)
{
	if (n_cbc < T_MAX_EV) {
		cbc[n_cbc].uas = uas;
		cbc[n_cbc].cycles = rhw_clock()->cycles();
	}
	n_cbc++;
}

static void on_started(uint8_t pattern, int64_t t_ms)
{
	if (n_cbs < T_MAX_EV) {
		cbs[n_cbs].pattern = pattern;
		cbs[n_cbs].t_ms = t_ms;
	}
	n_cbs++;
}

void t_reset(void)
{
	static const struct rmo_cb cb = { .edge = on_edge, .charge = on_charge, .started = on_started };

	rmo_stop();
	rhw_sim_reset();
	n_cbe = 0;
	n_cbc = 0;
	n_cbs = 0;
	zassert_equal(rmo_init(&cb), 0);
	rmo_set_vibration(true);
	rhw_sim_log_clear();
}

int t_pin_events(struct t_edge *out)
{
	int n = 0;
	struct rhw_sim_ev e;

	for (uint32_t i = 0; i < rhw_sim_log_count(); i++) {
		if (rhw_sim_log_get(i, &e) && e.kind == RHW_EV_MOTOR) {
			zassert_true(n < T_MAX_EV, "too many pin events");
			out[n].t_us = e.t_us;
			out[n].high = e.a0 != 0;
			n++;
		}
	}
	return n;
}

int t_n_edge(void)
{
	return n_cbe;
}

const struct t_cb_edge *t_edge(int i)
{
	return &cbe[i];
}

int t_n_charge(void)
{
	return n_cbc;
}

const struct t_cb_charge *t_charge(int i)
{
	return &cbc[i];
}

int t_n_started(void)
{
	return n_cbs;
}

const struct t_cb_started *t_started(int i)
{
	return &cbs[i];
}

int64_t t_now_us(void)
{
	return (int64_t)k_ticks_to_us_floor64(k_uptime_ticks());
}

void t_ms(uint32_t ms)
{
	k_sleep(K_MSEC(ms));
}

void t_check_edges(const struct t_edge *ev, int n_ev, int64_t base_us, const uint32_t *exp_ms, int n)
{
	zassert_equal(n_ev, n, "pin events %d, expected %d", n_ev, n);
	for (int i = 0; i < n; i++) {
		int64_t d = ev[i].t_us - base_us;

		zassert_equal(ev[i].high, (i % 2) == 0, "edge %d has the wrong level", i);
		zassert_true(d >= (int64_t)exp_ms[i] * 1000 - 1 && d < (int64_t)exp_ms[i] * 1000 + 1000,
			     "edge %d at %lld us from the start, expected %u ms", i, (long long)d, exp_ms[i]);
	}
}
