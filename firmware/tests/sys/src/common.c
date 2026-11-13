#include "common.h"

static struct t_logged logged[T_LOG_MAX];
static int nlogged;

void t_log_fn(uint16_t code, const uint8_t *args, size_t nargs)
{
	if (nlogged < T_LOG_MAX) {
		logged[nlogged].code = code;
		logged[nlogged].n = nargs;
		memset(logged[nlogged].args, 0, sizeof(logged[nlogged].args));
		memcpy(logged[nlogged].args, args, nargs < RREC_LOG_ARG_BYTES ? nargs : RREC_LOG_ARG_BYTES);
	}
	nlogged++;
}

void t_log_reset(void)
{
	nlogged = 0;
}

int t_nlog(void)
{
	return nlogged;
}

const struct t_logged *t_log_at(int i)
{
	return &logged[i];
}

void t_init(void)
{
	rhw_sim_reset();
	t_log_reset();
	zassert_equal(rsy_init(t_log_fn), 0, "rsy_init");
}

void t_cleanup(void)
{
	rhw_sim_reboot();
	rhw_sim_reset();
	t_log_reset();
}

void t_next_boot(void)
{
	rhw_sim_reboot();
	t_log_reset();
	zassert_equal(rsy_init(t_log_fn), 0, "rsy_init after reboot");
}

int32_t ev_find(uint16_t kind, uint32_t from)
{
	return rhw_sim_log_find(kind, from);
}

uint32_t ev_count(uint16_t kind)
{
	return rhw_sim_log_count_kind(kind);
}

bool ev_get(int32_t i, struct rhw_sim_ev *e)
{
	return i >= 0 && rhw_sim_log_get((uint32_t)i, e);
}

void t_fill(uint8_t *p, size_t n, uint8_t seed)
{
	for (size_t i = 0; i < n; i++) {
		p[i] = (uint8_t)(seed + 7u * i + (i >> 8));
	}
}
