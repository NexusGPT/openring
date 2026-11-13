#include <string.h>

#include "common.h"

struct cap cap;

static void cb_level(uint8_t level)
{
	if (cap.n_level < CAP_MAX) {
		cap.level[cap.n_level] = level;
	}
	cap.n_level++;
}

static void cb_vbus(bool present)
{
	if (cap.n_vbus < CAP_MAX) {
		struct cap_vbus *v = &cap.vbus[cap.n_vbus];

		v->present = present;
		v->log_n = rhw_sim_log_count();
		v->charger_on = rhw_sim_pmic_charger_on();
	}
	cap.n_vbus++;
}

static void cb_cerr(uint8_t reason, uint8_t sensor)
{
	if (cap.n_cerr < CAP_MAX) {
		cap.cerr[cap.n_cerr].reason = reason;
		cap.cerr[cap.n_cerr].sensor = sensor;
	}
	cap.n_cerr++;
}

static void cb_ilim(bool first, uint16_t mv, uint32_t count)
{
	if (cap.n_ilim < CAP_MAX) {
		cap.ilim[cap.n_ilim].first = first;
		cap.ilim[cap.n_ilim].mv = mv;
		cap.ilim[cap.n_ilim].count = count;
	}
	cap.n_ilim++;
}

static void cb_log(uint16_t code, const uint8_t *args, size_t n)
{
	if (cap.n_log < CAP_MAX) {
		struct cap_log *l = &cap.log[cap.n_log];

		l->code = code;
		l->n = n;
		l->t_ms = k_uptime_get();
		memset(l->args, 0, sizeof(l->args));
		memcpy(l->args, args, n < sizeof(l->args) ? n : sizeof(l->args));
	}
	cap.n_log++;
}

const struct rpw_cb pw_cbs = {
	.level = cb_level, .vbus = cb_vbus, .charge_error = cb_cerr, .ilim = cb_ilim, .log = cb_log,
};

void pw_before(void *f)
{
	ARG_UNUSED(f);
	rpw_priv_reset();
	rhw_sim_reset();
	memset(&cap, 0, sizeof(cap));
}

void pw_start(void)
{
	zassert_ok(rpw_start(&pw_cbs), "rpw_start");
}

void pw_script(const uint16_t *mv, const int32_t *ua, uint32_t n)
{
	struct rhw_pmic_sample s[16];

	zassert_true(n <= 16);
	for (uint32_t i = 0; i < n; i++) {
		s[i].mv = mv[i];
		s[i].ua = ua[i];
		s[i].temp_c_x10 = 250;
		s[i].die_c_x10 = 300;
	}
	rhw_sim_pmic_script(s, n);
}

void pw_script1(uint16_t mv, int32_t ua)
{
	pw_script(&mv, &ua, 1);
}

void pw_sleep_until(int64_t t_ms)
{
	int64_t d = t_ms - k_uptime_get();

	if (d > 0) {
		k_sleep(K_MSEC(d));
	}
}

struct rhw_sim_ev pw_ev(uint32_t i)
{
	struct rhw_sim_ev e;

	zassert_true(rhw_sim_log_get(i, &e), "event %u exists", i);
	return e;
}

int32_t pw_find(uint16_t kind, uint32_t from)
{
	return rhw_sim_log_find(kind, from);
}

int32_t pw_nth(uint16_t kind, uint32_t n)
{
	int32_t i = rhw_sim_log_find(kind, 0);

	while (i >= 0 && n > 0) {
		i = rhw_sim_log_find(kind, (uint32_t)i + 1);
		n--;
	}
	return i;
}

uint32_t pw_log_count(uint16_t code)
{
	uint32_t n = 0;

	for (uint32_t i = 0; i < cap.n_log && i < CAP_MAX; i++) {
		if (cap.log[i].code == code) {
			n++;
		}
	}
	return n;
}
