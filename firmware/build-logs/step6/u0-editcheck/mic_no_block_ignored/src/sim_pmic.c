/*
 * ring_rhw simulation: the power chip (two rails with the caller's name, charger, samples, current-limit bit, reset
 * causes, SHPHLD, ship task, VBUS) and the gauge. Written for this project; register names follow the nPM1304
 * specification as cited in design/firmware.md section 8, nothing of the kit's drivers.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>

#include "sim_int.h"

/* ------------------------------------------------------------------ power chip state */
static bool rail[RHW_RAIL_COUNT];
static char rail_caller[RHW_RAIL_COUNT][16];
static bool chg_on;
static uint32_t chg_ua;
static uint8_t err_reason, err_sensor;
static bool err_latched;
static int forced_state;
static uint32_t n_samples;
static uint32_t ilim_n, ilim_base;
static bool ilim_now;
static uint8_t rst_cause, rst_er, rst_es;
static uint16_t dip_mv;
static bool vbus;
static struct rhw_pmic_cb cbs;

/* sample sources */
static struct rhw_pmic_sample script[64];
static uint32_t script_n, script_i;
static bool cell_mode;
static uint32_t cell_cap, base_ua, mic_ua, sd_ua;
static int64_t cell_uas;         /* charge left in µA·s */
static int64_t last_sample_ms;

/* scheduled VBUS change */
static struct k_timer vbus_timer;
static bool vbus_timer_val;

bool sim_pmic_rail(enum rhw_rail r)
{
	return r < RHW_RAIL_COUNT && rail[r];
}

static int p_rail_set(enum rhw_rail r, bool on, const char *caller)
{
	if (sim_dead(RHW_EV_PMIC_RAIL)) {
		return -ESHUTDOWN;
	}
	if (r >= RHW_RAIL_COUNT) {
		sim_log(RHW_EV_PMIC_RAIL, r, on, 0, -EINVAL, caller);
		return -EINVAL;
	}
	rail[r] = on;
	strncpy(rail_caller[r], caller != NULL ? caller : "", 15);
	rail_caller[r][15] = '\0';
	if (r == RHW_RAIL_SD) {
		sim_disk_rail_changed(on);
	}
	sim_log(RHW_EV_PMIC_RAIL, r, on, 0, 0, caller != NULL ? caller : "");
	return 0;
}

static bool p_rail_get(enum rhw_rail r)
{
	return sim_pmic_rail(r);
}

static int p_chg_enable(bool on)
{
	if (sim_dead(RHW_EV_PMIC_CHG_ENABLE)) {
		return -ESHUTDOWN;
	}
	chg_on = on;
	sim_log(RHW_EV_PMIC_CHG_ENABLE, on, 0, 0, 0, NULL);
	return 0;
}

static int p_chg_current(uint32_t ua)
{
	if (sim_dead(RHW_EV_PMIC_CHG_CURRENT)) {
		return -ESHUTDOWN;
	}
	chg_ua = ua;
	sim_log(RHW_EV_PMIC_CHG_CURRENT, ua, chg_on, 0, 0, NULL);
	return 0;
}

static uint8_t state_now(void)
{
	if (forced_state >= 0) {
		return (uint8_t)forced_state;
	}
	if (err_latched) {
		return RREC_CHG_ERROR;
	}
	return (vbus && chg_on) ? RREC_CHG_CC : RREC_CHG_OFF;
}

static int p_chg_status(struct rhw_pmic_charge *out)
{
	if (sim_dead(RHW_EV_PMIC_CHG_STATUS)) {
		return -ESHUTDOWN;
	}
	out->state = state_now();
	out->err_reason = err_reason;
	out->err_sensor = err_sensor;
	sim_log(RHW_EV_PMIC_CHG_STATUS, out->state, err_reason, err_sensor, 0, NULL);
	return 0;
}

static int p_sample(struct rhw_pmic_sample *out)
{
	if (sim_dead(RHW_EV_PMIC_SAMPLE)) {
		return -ESHUTDOWN;
	}
	int64_t now = k_uptime_get();

	n_samples++;
	ilim_now = (ilim_n > 0 && n_samples - ilim_base == ilim_n);
	if (script_n > 0) {
		*out = script[script_i];
		if (script_i + 1 < script_n) {
			script_i++;
		}
	} else if (cell_mode) {
		int64_t dt = now - last_sample_ms;
		int32_t ua = (int32_t)(base_ua + (rail[RHW_RAIL_MIC] ? mic_ua : 0) + (rail[RHW_RAIL_SD] ? sd_ua : 0));

		if (vbus && chg_on && !err_latched) {
			ua = -(int32_t)chg_ua;
		}
		cell_uas -= (int64_t)ua * dt / 1000;
		int64_t cap_uas = (int64_t)cell_cap * 3600;

		if (cell_uas < 0) {
			cell_uas = 0;
		}
		if (cell_uas > cap_uas) {
			cell_uas = cap_uas;
		}
		out->mv = (uint16_t)(3300 + (cap_uas > 0 ? (1050 * cell_uas) / cap_uas : 0));
		out->ua = ua;
		out->temp_c_x10 = 250;
		out->die_c_x10 = 300;
	} else {
		out->mv = 3900;
		out->ua = 3000;
		out->temp_c_x10 = 250;
		out->die_c_x10 = 300;
	}
	if (sim_motor_high() && dip_mv > 0) {
		out->mv = (uint16_t)(out->mv - dip_mv);
	}
	last_sample_ms = now;
	sim_log(RHW_EV_PMIC_SAMPLE, out->mv, out->ua, n_samples, 0, NULL);
	return 0;
}

static int p_ilim(void)
{
	if (sim_dead(RHW_EV_PMIC_ILIM)) {
		return -ESHUTDOWN;
	}
	sim_log(RHW_EV_PMIC_ILIM, ilim_now, 0, 0, 0, NULL);
	return ilim_now ? 1 : 0;
}

static int p_rst(uint8_t *rc, uint8_t *er, uint8_t *es)
{
	if (sim_dead(RHW_EV_PMIC_RST_READ)) {
		return -ESHUTDOWN;
	}
	*rc = rst_cause;
	*er = rst_er;
	*es = rst_es;
	sim_log(RHW_EV_PMIC_RST_READ, rst_cause, rst_er, rst_es, 0, NULL);
	return 0;
}

static int p_rst_clear(void)
{
	if (sim_dead(RHW_EV_PMIC_RST_CLEAR)) {
		return -ESHUTDOWN;
	}
	rst_cause = 0;
	rst_er = 0;
	rst_es = 0;
	sim_log(RHW_EV_PMIC_RST_CLEAR, 0, 0, 0, 0, NULL);
	return 0;
}

static int p_shphld_cfg(uint32_t ms)
{
	if (sim_dead(RHW_EV_PMIC_SHPHLD_CFG)) {
		return -ESHUTDOWN;
	}
	sim_log(RHW_EV_PMIC_SHPHLD_CFG, ms, 0, 0, 0, NULL);
	return 0;
}

static int p_shphld_strobe(void)
{
	if (sim_dead(RHW_EV_PMIC_SHPHLD_STROBE)) {
		return -ESHUTDOWN;
	}
	sim_log(RHW_EV_PMIC_SHPHLD_STROBE, 0, 0, 0, 0, NULL);
	return 0;
}

static int p_ship(void)
{
	if (sim_dead(RHW_EV_PMIC_SHIP)) {
		return -ESHUTDOWN;
	}
	sim_log(RHW_EV_PMIC_SHIP, vbus, 0, 0, 0, NULL);
	/* with VBUS present the chip waits (FW l.934); the simulation stands for "the supply is gone" at once only
	 * without VBUS */
	if (!vbus) {
		sim_set_shipped();
	}
	return 0;
}

static bool p_vbus(void)
{
	return vbus;
}

static void p_set_cb(const struct rhw_pmic_cb *cb)
{
	if (cb == NULL) {
		memset(&cbs, 0, sizeof(cbs));
	} else {
		cbs = *cb;
	}
}

const struct rhw_pmic_api rhw_sim_pmic_api = {
	.rail_set = p_rail_set, .rail_get = p_rail_get, .charger_enable = p_chg_enable,
	.charger_current = p_chg_current, .charge_status = p_chg_status, .sample = p_sample, .ilim_active = p_ilim,
	.reset_causes = p_rst, .reset_causes_clear = p_rst_clear, .shphld_config = p_shphld_cfg,
	.shphld_strobe = p_shphld_strobe, .ship_task = p_ship, .vbus_present = p_vbus, .set_callbacks = p_set_cb,
};

/* ------------------------------------------------------------------ controls */
void rhw_sim_pmic_vbus(bool present)
{
	vbus = present;
	sim_log(RHW_EV_PMIC_VBUS, present, 0, 0, 0, NULL);
	if (cbs.vbus != NULL) {
		cbs.vbus(present);
	}
}

void rhw_sim_vbus(bool present)
{
	rhw_sim_pmic_vbus(present);
	sim_usb_vbus_event(present);
}

static void vbus_timer_fn(struct k_timer *t)
{
	ARG_UNUSED(t);
	rhw_sim_vbus(vbus_timer_val);
}

void rhw_sim_vbus_at(int64_t t_ms, bool present)
{
	int64_t d = t_ms - k_uptime_get();

	vbus_timer_val = present;
	k_timer_start(&vbus_timer, K_MSEC(d > 0 ? d : 0), K_NO_WAIT);
}

void rhw_sim_pmic_charge_error(uint8_t reason, uint8_t sensor)
{
	err_reason = reason;
	err_sensor = sensor;
	err_latched = true;
	sim_log(RHW_EV_PMIC_CHARGE_ERROR, reason, sensor, 0, 0, NULL);
	if (cbs.charge_error != NULL) {
		cbs.charge_error();
	}
}

void rhw_sim_pmic_ilim_at_sample(uint32_t n)
{
	ilim_base = n_samples;
	ilim_n = n;
}

void rhw_sim_pmic_set_reset_causes(uint8_t rc, uint8_t er, uint8_t es)
{
	rst_cause = rc;
	rst_er = er;
	rst_es = es;
}

void rhw_sim_pmic_motor_dip(uint16_t mv)
{
	dip_mv = mv;
}

void rhw_sim_pmic_script(const struct rhw_pmic_sample *s, uint32_t n)
{
	if (n > ARRAY_SIZE(script)) {
		n = ARRAY_SIZE(script);
	}
	if (n > 0) {
		memcpy(script, s, n * sizeof(*s));
	}
	script_n = n;
	script_i = 0;
	if (n > 0) {
		cell_mode = false;
	}
}

void rhw_sim_pmic_cell(uint32_t capacity_uah, uint32_t start_uah, uint32_t b, uint32_t m, uint32_t sd)
{
	cell_mode = true;
	script_n = 0;
	cell_cap = capacity_uah;
	cell_uas = (int64_t)start_uah * 3600;
	base_ua = b;
	mic_ua = m;
	sd_ua = sd;
	last_sample_ms = k_uptime_get();
}

void rhw_sim_pmic_charge_state(int state)
{
	forced_state = state;
}

bool rhw_sim_pmic_charger_on(void)
{
	return chg_on;
}

uint32_t rhw_sim_pmic_charger_ua(void)
{
	return chg_ua;
}

const char *rhw_sim_pmic_rail_caller(enum rhw_rail r)
{
	return r < RHW_RAIL_COUNT ? rail_caller[r] : "";
}

/* ------------------------------------------------------------------ gauge */
static uint16_t g_start_soc;
static uint32_t g_cap_uah;
static int g_err;
static int64_t g_used_uas;
static bool g_started;

static int g_start(const struct rhw_pmic_sample *first)
{
	if (sim_dead(RHW_EV_GAUGE_START)) {
		return -ESHUTDOWN;
	}
	ARG_UNUSED(first);
	g_used_uas = 0;
	g_started = true;
	sim_log(RHW_EV_GAUGE_START, g_start_soc, 0, 0, 0, NULL);
	return 0;
}

static int g_process(const struct rhw_pmic_sample *s, uint32_t dt_ms, struct rhw_gauge_out *out)
{
	if (sim_dead(RHW_EV_GAUGE_PROCESS)) {
		return -ESHUTDOWN;
	}
	if (g_err != 0 || !g_started) {
		int r = g_err != 0 ? g_err : -EINVAL;

		sim_log(RHW_EV_GAUGE_PROCESS, s->ua, dt_ms, 0, r, NULL);
		return r;
	}
	g_used_uas += (int64_t)s->ua * dt_ms / 1000;
	int64_t cap_uas = (int64_t)g_cap_uah * 3600;
	int64_t left = cap_uas * g_start_soc / 1000 - g_used_uas;

	if (left < 0) {
		left = 0;
	}
	if (left > cap_uas) {
		left = cap_uas;
	}
	out->soc_x10 = (uint16_t)(cap_uas > 0 ? (left * 1000) / cap_uas : 0);
	out->tte_s = s->ua > 0 ? (uint32_t)(left / s->ua) : UINT32_MAX;
	out->ttf_s = s->ua < 0 ? (uint32_t)((cap_uas - left) / -(int64_t)s->ua) : UINT32_MAX;
	sim_log(RHW_EV_GAUGE_PROCESS, s->ua, dt_ms, out->soc_x10, 0, NULL);
	return 0;
}

const struct rhw_gauge_api rhw_sim_gauge_api = { .start = g_start, .process = g_process };

void rhw_sim_gauge_start_soc(uint16_t soc_x10)
{
	g_start_soc = soc_x10;
}

void rhw_sim_gauge_capacity(uint32_t uah)
{
	g_cap_uah = uah;
}

void rhw_sim_gauge_error(int err)
{
	g_err = err;
}

/* ------------------------------------------------------------------ reset */
void sim_pmic_reset(bool full)
{
	static bool timer_ready;

	if (!timer_ready) {
		k_timer_init(&vbus_timer, vbus_timer_fn, NULL);
		timer_ready = true;
	}
	memset(rail, 0, sizeof(rail));
	memset(rail_caller, 0, sizeof(rail_caller));
	chg_on = false;
	chg_ua = 0;
	ilim_now = false;
	memset(&cbs, 0, sizeof(cbs));
	g_started = false;
	g_used_uas = 0;
	n_samples = 0;
	ilim_base = 0;
	if (full) {
		k_timer_stop(&vbus_timer);
		err_reason = 0;
		err_sensor = 0;
		err_latched = false;
		forced_state = -1;
		ilim_n = 0;
		rst_cause = 0;
		rst_er = 0;
		rst_es = 0;
		dip_mv = 0;
		vbus = false;
		script_n = 0;
		script_i = 0;
		cell_mode = false;
		g_start_soc = 800;
		g_cap_uah = 17600;
		g_err = 0;
	}
}
