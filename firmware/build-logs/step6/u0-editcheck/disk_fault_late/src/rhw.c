/*
 * ring_rhw: the active driver instance of each kind (rhw.h). With CONFIG_RING_RHW_SIM every kind is the simulated
 * driver and registration is refused; without it every kind starts "absent" (calls give -ENODEV) until a real file
 * registers its instance. Written for this project.
 */
#include <errno.h>

#include <zephyr/kernel.h>
#include <ring_rhw/rhw.h>

#if defined(CONFIG_RING_RHW_SIM)
#include "sim_int.h"
#endif

/* ------------------------------------------------------------------ absent instances (no real file registered) */
static int none_v(void) { return -ENODEV; }
static int none_u32(uint32_t a) { ARG_UNUSED(a); return -ENODEV; }
static int none_b(bool a) { ARG_UNUSED(a); return -ENODEV; }
static bool none_false(void) { return false; }

static int none_disk_rd(uint32_t l, uint8_t *b, uint32_t c) { ARG_UNUSED(l); ARG_UNUSED(b); ARG_UNUSED(c); return -ENODEV; }
static int none_disk_wr(uint32_t l, const uint8_t *b, uint32_t c) { ARG_UNUSED(l); ARG_UNUSED(b); ARG_UNUSED(c); return -ENODEV; }
static int none_disk_cnt(uint32_t *o) { ARG_UNUSED(o); return -ENODEV; }
static const struct rhw_disk_api none_disk = {
	.init = none_v, .deinit = none_v, .read = none_disk_rd, .write = none_disk_wr, .sector_count = none_disk_cnt,
};

static int none_mic_cfg(const struct rhw_mic_cfg *c) { ARG_UNUSED(c); return -ENODEV; }
static int none_mic_read(void **b, size_t *s, int32_t t) { ARG_UNUSED(b); ARG_UNUSED(s); ARG_UNUSED(t); return -ENODEV; }
static void none_mic_free(void *b) { ARG_UNUSED(b); }
static const struct rhw_mic_api none_mic = {
	.configure = none_mic_cfg, .start = none_v, .stop = none_v, .read = none_mic_read, .free_block = none_mic_free,
	.pins_sleep = none_v, .pins_default = none_v,
};

static int none_rail_set(enum rhw_rail r, bool on, const char *c) { ARG_UNUSED(r); ARG_UNUSED(on); ARG_UNUSED(c); return -ENODEV; }
static bool none_rail_get(enum rhw_rail r) { ARG_UNUSED(r); return false; }
static int none_chg_st(struct rhw_pmic_charge *o) { ARG_UNUSED(o); return -ENODEV; }
static int none_sample(struct rhw_pmic_sample *o) { ARG_UNUSED(o); return -ENODEV; }
static int none_rst(uint8_t *a, uint8_t *b, uint8_t *c) { ARG_UNUSED(a); ARG_UNUSED(b); ARG_UNUSED(c); return -ENODEV; }
static void none_pmic_cb(const struct rhw_pmic_cb *cb) { ARG_UNUSED(cb); }
static const struct rhw_pmic_api none_pmic = {
	.rail_set = none_rail_set, .rail_get = none_rail_get, .charger_enable = none_b, .charger_current = none_u32,
	.charge_status = none_chg_st, .sample = none_sample, .ilim_active = none_v, .reset_causes = none_rst,
	.reset_causes_clear = none_v, .shphld_config = none_u32, .shphld_strobe = none_v, .ship_task = none_v,
	.vbus_present = none_false, .set_callbacks = none_pmic_cb,
};

static int none_hfxo_req(void (*cb)(void)) { ARG_UNUSED(cb); return -ENODEV; }
static const struct rhw_hfxo_api none_hfxo = { .request = none_hfxo_req, .release = none_v, .running = none_false };
static const struct rhw_motor_api none_motor = { .set = none_b };
static const struct rhw_sdbus_api none_sdbus = { .suspend = none_v, .resume = none_v };

static int none_usb_send(const uint8_t *d, size_t n, int32_t t) { ARG_UNUSED(d); ARG_UNUSED(n); ARG_UNUSED(t); return -ENODEV; }
static enum rhw_usb_speed none_usb_speed(void) { return RHW_USB_FS; }
static void none_usb_cb(const struct rhw_usb_cb *cb) { ARG_UNUSED(cb); }
static const struct rhw_usb_api none_usb = {
	.enable = none_v, .disable = none_v, .send = none_usb_send, .speed = none_usb_speed, .set_callbacks = none_usb_cb,
};

static int none_img_wr(uint32_t o, const uint8_t *d, size_t n) { ARG_UNUSED(o); ARG_UNUSED(d); ARG_UNUSED(n); return -ENODEV; }
static int none_img_rd(uint32_t o, uint8_t *d, size_t n) { ARG_UNUSED(o); ARG_UNUSED(d); ARG_UNUSED(n); return -ENODEV; }
static int none_img_reboot(enum rhw_reboot_reason w) { ARG_UNUSED(w); return -ENODEV; }
static const struct rhw_image_api none_image = {
	.erase_slot1 = none_v, .write = none_img_wr, .read = none_img_rd, .request_test_upgrade = none_v,
	.is_confirmed = none_v, .confirm = none_v, .reboot = none_img_reboot,
};

static int none_p_load(struct rhw_persist *o) { ARG_UNUSED(o); return -ENODEV; }
static int none_p_save(const struct rhw_persist *i) { ARG_UNUSED(i); return -ENODEV; }
static const struct rhw_persist_api none_persist = { .load = none_p_load, .save = none_p_save };

static int none_ret_rd(uint8_t *b, size_t n) { ARG_UNUSED(b); ARG_UNUSED(n); return -ENODEV; }
static int none_ret_wr(const uint8_t *b, size_t n) { ARG_UNUSED(b); ARG_UNUSED(n); return -ENODEV; }
static int none_gp_get(uint8_t *o) { ARG_UNUSED(o); return -ENODEV; }
static int none_gp_set(uint8_t v) { ARG_UNUSED(v); return -ENODEV; }
static const struct rhw_retained_api none_retained = {
	.read = none_ret_rd, .write = none_ret_wr, .clear = none_v, .gpregret1_get = none_gp_get, .gpregret1_set = none_gp_set,
};
static const struct rhw_wdt_api none_wdt = { .start = none_u32, .feed = none_v };

static int none_g_start(const struct rhw_pmic_sample *s) { ARG_UNUSED(s); return -ENODEV; }
static int none_g_proc(const struct rhw_pmic_sample *s, uint32_t dt, struct rhw_gauge_out *o) { ARG_UNUSED(s); ARG_UNUSED(dt); ARG_UNUSED(o); return -ENODEV; }
static const struct rhw_gauge_api none_gauge = { .start = none_g_start, .process = none_g_proc };

static int none_bc_start(const char *n, uint16_t i, int8_t p, bool c) { ARG_UNUSED(n); ARG_UNUSED(i); ARG_UNUSED(p); ARG_UNUSED(c); return -ENODEV; }
static const struct rhw_beacon_api none_beacon = { .start = none_bc_start, .stop = none_v };

/* ------------------------------------------------------------------ the active table */
#if defined(CONFIG_RING_RHW_SIM)
#define START(kind) (&rhw_sim_##kind##_api)
#else
#define START(kind) (&none_##kind)
#endif

static const struct rhw_disk_api *act_disk = START(disk);
static const struct rhw_mic_api *act_mic = START(mic);
static const struct rhw_pmic_api *act_pmic = START(pmic);
static const struct rhw_hfxo_api *act_hfxo = START(hfxo);
static const struct rhw_motor_api *act_motor = START(motor);
static const struct rhw_sdbus_api *act_sdbus = START(sdbus);
static const struct rhw_usb_api *act_usb = START(usb);
static const struct rhw_image_api *act_image = START(image);
static const struct rhw_persist_api *act_persist = START(persist);
static const struct rhw_retained_api *act_retained = START(retained);
static const struct rhw_wdt_api *act_wdt = START(wdt);
static const struct rhw_gauge_api *act_gauge = START(gauge);
static const struct rhw_beacon_api *act_beacon = START(beacon);
#if defined(CONFIG_RING_RHW_SIM)
static const struct rhw_clock_api *act_clock = &rhw_sim_clock_api;
#else
static const struct rhw_clock_api *act_clock = &rhw_clock_real;
#endif

#define GETTER(kind) const struct rhw_##kind##_api *rhw_##kind(void) { return act_##kind; }
GETTER(disk)
GETTER(mic)
GETTER(pmic)
GETTER(hfxo)
GETTER(motor)
GETTER(sdbus)
GETTER(usb)
GETTER(image)
GETTER(persist)
GETTER(retained)
GETTER(wdt)
GETTER(gauge)
GETTER(clock)
GETTER(beacon)

#if defined(CONFIG_RING_RHW_SIM)
#define REGISTER(kind)                                                                     \
	int rhw_register_##kind(const struct rhw_##kind##_api *api)                        \
	{                                                                                  \
		return api == NULL ? -EINVAL : -EPERM;                                     \
	}
#else
#define REGISTER(kind)                                                                     \
	int rhw_register_##kind(const struct rhw_##kind##_api *api)                        \
	{                                                                                  \
		if (api == NULL) {                                                         \
			return -EINVAL;                                                    \
		}                                                                          \
		if (act_##kind != &none_##kind) {                                          \
			return -EPERM;                                                     \
		}                                                                          \
		act_##kind = api;                                                          \
		return 0;                                                                  \
	}
#endif
REGISTER(disk)
REGISTER(mic)
REGISTER(pmic)
REGISTER(hfxo)
REGISTER(motor)
REGISTER(sdbus)
REGISTER(usb)
REGISTER(image)
REGISTER(persist)
REGISTER(retained)
REGISTER(wdt)
REGISTER(gauge)
REGISTER(beacon)

#if defined(CONFIG_RING_RHW_SIM)
/* the absent instances exist for the real build only; keep the compiler quiet in the simulated one */
const void *const rhw_none_table[] = {
	&none_disk, &none_mic, &none_pmic, &none_hfxo, &none_motor, &none_sdbus, &none_usb, &none_image,
	&none_persist, &none_retained, &none_wdt, &none_gauge, &none_beacon,
};
#endif
