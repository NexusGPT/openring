/*
 * rpw_hw_real.c: the real power chip and gauge behind ring_rhw's interfaces (software step 6, unit U5). The
 * development kit build only (CONFIG_RING_POWER_REAL, which needs the nPM1304 node of the real board's devicetree):
 * NOT PROVEN, no hardware (plan section 7). Written for this project from design/firmware.md section 8 and
 * design/datasheets/npm1304_datasheet_v1_0.txt (register names and offsets as that file lists them); it calls the
 * kit's headers only.
 *
 * What it uses (kit fact K5, answered in firmware/docs/power-notes.md): the nPM13xx register access of the multi
 * function device driver (a task or register write), the charger's sensor channels for voltage, current, thermistor
 * and die temperature, the regulator API for the two load switches, and the kit's fuel gauge library (K6).
 *
 * No chip pin appears here: nodes are found by compatible, the load switches by aliases of the real board's
 * devicetree (step 7 names them).
 */
#include <errno.h>
#include <string.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/mfd/npm13xx.h>
#include <zephyr/drivers/regulator.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/init.h>
#include <zephyr/kernel.h>

#include <nrf_fuel_gauge.h>

#include <ring_rhw/rhw.h>

#include "rpw_logic.h"

#define PMIC_NODE    DT_COMPAT_GET_ANY_STATUS_OKAY(nordic_npm1304)
#define CHARGER_NODE DT_COMPAT_GET_ANY_STATUS_OKAY(nordic_npm1304_charger)

#if !DT_NODE_EXISTS(DT_ALIAS(ring_vdd_mic)) || !DT_NODE_EXISTS(DT_ALIAS(ring_vdd_sd))
#error "the real board's devicetree must give the aliases ring-vdd-mic and ring-vdd-sd to the two load switches"
#endif
#if !__has_include("rpw_battery_model.h")
#error "rpw_battery_model.h (the battery model of the cell, made with nPM PowerUP) is missing: FW l.930, open item"
#endif
#include "rpw_battery_model.h"

/* register blocks and offsets, from the datasheet's register maps (base address and offset of each name) */
#define REG_BASE_CHARGER 0x03
#define REG_BASE_SHIP    0x0B
#define REG_BASE_ERRLOG  0x0E
#define REG_BCHGENABLESET     0x04
#define REG_BCHGENABLECLR     0x05
#define REG_BCHGISET          0x08          /* one register, 0.5 mA per step */
#define REG_BCHGILIMSTATUS    0x2D          /* bit 0: BCHGILIMBATACTIVE */
#define REG_BCHGCHARGESTATUS  0x34
#define REG_BCHGERRREASON     0x36
#define REG_BCHGERRSENSOR     0x37
#define REG_TASKSHPHLDCFGSTROBE 0x01
#define REG_TASKENTERSHIPMODE   0x02
#define REG_SHPHLDCONFIG        0x04
#define REG_TASKCLRERRLOG       0x00
#define REG_RSTCAUSE            0x03
#define REG_CHARGERERRREASON    0x04
#define REG_CHARGERERRSENSOR    0x05
/* BCHGCHARGESTATUS bits */
#define CHG_COMPLETED     BIT(1)
#define CHG_TRICKLE       BIT(2)
#define CHG_CC            BIT(3)
#define CHG_CV            BIT(4)
/* SHPHLDTIM value of 96 ms (the register map's list: 16, 32, 64, 96 ... ms = 0, 1, 2, 3) */
#define SHPHLDTIM_96MS    3

static const struct device *const pmic = DEVICE_DT_GET(PMIC_NODE);
static const struct device *const charger = DEVICE_DT_GET(CHARGER_NODE);
static const struct device *const ldsw_mic = DEVICE_DT_GET(DT_ALIAS(ring_vdd_mic));
static const struct device *const ldsw_sd = DEVICE_DT_GET(DT_ALIAS(ring_vdd_sd));

static struct rhw_pmic_cb cbs;
static struct gpio_callback evt_cb;
static bool rail_state[RHW_RAIL_COUNT];

static int rd(uint8_t base, uint8_t off, uint8_t *v)
{
	return mfd_npm13xx_reg_read(pmic, base, off, v);
}

static int wr(uint8_t base, uint8_t off, uint8_t v)
{
	return mfd_npm13xx_reg_write(pmic, base, off, v);
}

/* ------------------------------------------------------------------ load switches (FW l.342: ring_store and
 * rec_mics_on() only; this file only carries the call out) */
static int r_rail_set(enum rhw_rail r, bool on, const char *caller)
{
	const struct device *d;
	int rc;

	ARG_UNUSED(caller);
	if (r >= RHW_RAIL_COUNT) {
		return -EINVAL;
	}
	d = r == RHW_RAIL_MIC ? ldsw_mic : ldsw_sd;
	rc = on ? regulator_enable(d) : regulator_disable(d);
	if (rc == 0) {
		rail_state[r] = on;
	}
	return rc;
}

static bool r_rail_get(enum rhw_rail r)
{
	return r < RHW_RAIL_COUNT && rail_state[r];
}

/* ------------------------------------------------------------------ charger (FW l.878, l.888, l.894) */
static int r_chg_enable(bool on)
{
	return wr(REG_BASE_CHARGER, on ? REG_BCHGENABLESET : REG_BCHGENABLECLR, 1);
}

static int r_chg_current(uint32_t ua)
{
	return wr(REG_BASE_CHARGER, REG_BCHGISET, (uint8_t)(ua / 500u));
}

static int r_chg_status(struct rhw_pmic_charge *out)
{
	uint8_t st = 0, er = 0, es = 0;
	int rc = rd(REG_BASE_CHARGER, REG_BCHGCHARGESTATUS, &st);

	if (rc == 0) {
		rc = rd(REG_BASE_CHARGER, REG_BCHGERRREASON, &er);
	}
	if (rc == 0) {
		rc = rd(REG_BASE_CHARGER, REG_BCHGERRSENSOR, &es);
	}
	if (rc != 0) {
		return rc;
	}
	out->err_reason = er;
	out->err_sensor = es;
	if (er != 0) {
		out->state = RREC_CHG_ERROR;
	} else if (st & CHG_COMPLETED) {
		out->state = RREC_CHG_FULL;
	} else if (st & CHG_CV) {
		out->state = RREC_CHG_CV;
	} else if (st & CHG_CC) {
		out->state = RREC_CHG_CC;
	} else if (st & CHG_TRICKLE) {
		out->state = RREC_CHG_TRICKLE;
	} else {
		out->state = RREC_CHG_OFF;
	}
	return 0;
}

/* ------------------------------------------------------------------ system monitor sample (FW l.926) */
static int32_t sv_to_micro(const struct sensor_value *v)
{
	return v->val1 * 1000000 + v->val2;
}

/* The current in the interface's sign (positive = discharge). The sign of the kit's current channel against the
 * library's expectation is kit fact K6, open: this one place converts. */
static int32_t chan_to_ua(const struct sensor_value *v)
{
	return -sv_to_micro(v);
}

static int r_sample(struct rhw_pmic_sample *out)
{
	struct sensor_value v, i, t, d;
	int rc = sensor_sample_fetch(charger);

	if (rc != 0) {
		return rc;
	}
	rc = sensor_channel_get(charger, SENSOR_CHAN_GAUGE_VOLTAGE, &v);
	if (rc == 0) {
		rc = sensor_channel_get(charger, SENSOR_CHAN_GAUGE_AVG_CURRENT, &i);
	}
	if (rc == 0) {
		rc = sensor_channel_get(charger, SENSOR_CHAN_GAUGE_TEMP, &t);
	}
	if (rc == 0) {
		rc = sensor_channel_get(charger, SENSOR_CHAN_DIE_TEMP, &d);
	}
	if (rc != 0) {
		return rc;
	}
	out->mv = (uint16_t)(sv_to_micro(&v) / 1000);
	out->ua = chan_to_ua(&i);
	out->temp_c_x10 = (int16_t)(sv_to_micro(&t) / 100000);
	out->die_c_x10 = (int16_t)(sv_to_micro(&d) / 100000);
	return 0;
}

static int r_ilim(void)
{
	uint8_t v = 0;
	int rc = rd(REG_BASE_CHARGER, REG_BCHGILIMSTATUS, &v);

	return rc != 0 ? rc : (v & BIT(0)) ? 1 : 0;
}

/* ------------------------------------------------------------------ reset causes (FW l.996) */
static int r_rst(uint8_t *rc_, uint8_t *er, uint8_t *es)
{
	int rc = rd(REG_BASE_ERRLOG, REG_RSTCAUSE, rc_);

	if (rc == 0) {
		rc = rd(REG_BASE_ERRLOG, REG_CHARGERERRREASON, er);
	}
	if (rc == 0) {
		rc = rd(REG_BASE_ERRLOG, REG_CHARGERERRSENSOR, es);
	}
	return rc;
}

static int r_rst_clear(void)
{
	return wr(REG_BASE_ERRLOG, REG_TASKCLRERRLOG, 1);
}

/* ------------------------------------------------------------------ ship mode (FW l.936 to l.941) */
static int r_shphld_config(uint32_t press_ms)
{
	if (press_ms != 96u) {
		return -EINVAL;             /* only the default press time is used (FW l.938) */
	}
	return wr(REG_BASE_SHIP, REG_SHPHLDCONFIG, SHPHLDTIM_96MS);
}

static int r_shphld_strobe(void)
{
	return wr(REG_BASE_SHIP, REG_TASKSHPHLDCFGSTROBE, 1);
}

static int r_ship_task(void)
{
	return wr(REG_BASE_SHIP, REG_TASKENTERSHIPMODE, 1);
}

/* ------------------------------------------------------------------ VBUS and events (FW l.977 to l.979):
 * an input only; there is deliberately no call that drives it. */
static bool vbus_now;

static bool r_vbus_present(void)
{
	return vbus_now;
}

static void evt_handler(const struct device *dev, struct gpio_callback *cb, uint32_t pins)
{
	ARG_UNUSED(dev);
	ARG_UNUSED(cb);
	if (pins & BIT(NPM13XX_EVENT_VBUS_DETECTED)) {
		vbus_now = true;
		if (cbs.vbus != NULL) {
			cbs.vbus(true);
		}
	}
	if (pins & BIT(NPM13XX_EVENT_VBUS_REMOVED)) {
		vbus_now = false;
		if (cbs.vbus != NULL) {
			cbs.vbus(false);
		}
	}
	if (pins & BIT(NPM13XX_EVENT_CHG_ERROR)) {
		if (cbs.charge_error != NULL) {
			cbs.charge_error();
		}
	}
}

static void r_set_callbacks(const struct rhw_pmic_cb *cb)
{
	if (cb == NULL) {
		memset(&cbs, 0, sizeof(cbs));
	} else {
		cbs = *cb;
	}
}

static const struct rhw_pmic_api real_pmic = {
	.rail_set = r_rail_set, .rail_get = r_rail_get, .charger_enable = r_chg_enable,
	.charger_current = r_chg_current, .charge_status = r_chg_status, .sample = r_sample, .ilim_active = r_ilim,
	.reset_causes = r_rst, .reset_causes_clear = r_rst_clear, .shphld_config = r_shphld_config,
	.shphld_strobe = r_shphld_strobe, .ship_task = r_ship_task, .vbus_present = r_vbus_present,
	.set_callbacks = r_set_callbacks,
};

/* ------------------------------------------------------------------ the kit's fuel gauge library (FW l.926, l.927).
 * The library's current argument follows the kit's convention; the interface's positive-discharge current is
 * converted in this one function (kit fact K6: the sign is open). */
static int g_start(const struct rhw_pmic_sample *first)
{
	struct nrf_fuel_gauge_init_parameters p = { .model = &battery_model };

	p.v0 = first->mv / 1000.0f;
	p.i0 = -(first->ua / 1000000.0f);
	p.t0 = first->temp_c_x10 / 10.0f;
	return nrf_fuel_gauge_init(&p, NULL);
}

static int g_process(const struct rhw_pmic_sample *s, uint32_t dt_ms, struct rhw_gauge_out *out)
{
	float soc = nrf_fuel_gauge_process(s->mv / 1000.0f, -(s->ua / 1000000.0f), s->temp_c_x10 / 10.0f,
					   dt_ms / 1000.0f, NULL);
	float tte = nrf_fuel_gauge_tte_get();
	float ttf = nrf_fuel_gauge_ttf_get();

	out->soc_x10 = (uint16_t)(soc * 10.0f + 0.5f);
	out->tte_s = tte > 0.0f ? (uint32_t)tte : UINT32_MAX;
	out->ttf_s = ttf > 0.0f ? (uint32_t)ttf : UINT32_MAX;
	return 0;
}

static const struct rhw_gauge_api real_gauge = { .start = g_start, .process = g_process };

static int rpw_real_init(void)
{
	if (!device_is_ready(pmic) || !device_is_ready(charger) || !device_is_ready(ldsw_mic) ||
	    !device_is_ready(ldsw_sd)) {
		return -ENODEV;
	}
	gpio_init_callback(&evt_cb, evt_handler,
			   BIT(NPM13XX_EVENT_VBUS_DETECTED) | BIT(NPM13XX_EVENT_VBUS_REMOVED) |
				   BIT(NPM13XX_EVENT_CHG_ERROR));
	if (mfd_npm13xx_add_callback(pmic, &evt_cb) != 0) {
		return -EIO;
	}
	if (rhw_register_pmic(&real_pmic) != 0) {
		return -EPERM;
	}
	return rhw_register_gauge(&real_gauge);
}

SYS_INIT(rpw_real_init, APPLICATION, 50);
