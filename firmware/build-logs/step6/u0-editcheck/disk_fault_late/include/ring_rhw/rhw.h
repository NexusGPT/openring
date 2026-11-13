/*
 * rhw.h: the driver interfaces of the recorder parts (software step 6, unit U0). One struct of function pointers per
 * kind of driver. The units of step 6 (ring_store, ring_audio, ring_xfer, ring_power, ring_motor, ring_sys,
 * ring_factory, ring_recorder) reach hardware ONLY through these interfaces.
 *
 * Active instance: rhw_<kind>() returns the instance in use. With CONFIG_RING_RHW_SIM=y every kind starts on the
 * simulated driver of this module (src/sim_*.c, controls in rhw_sim.h) and rhw_register_<kind>() is refused with
 * -EPERM, so no real driver can slip into a simulated build. Without it every kind starts on an "absent" instance whose
 * calls return -ENODEV (or false / 0 for queries, as each comment says); a unit's real file (`*_hw_real.c`, development
 * kit build only, decision D15) calls rhw_register_<kind>() once at start (SYS_INIT, level APPLICATION) to make its
 * instance active. Exception: the clock has a real instance in this module (src/rhw_clock_real.c), active without SIM.
 *
 * Common rules for every function pointer below unless its comment says otherwise:
 *  - returns 0 on success or a negative errno; -ENODEV from an absent instance;
 *  - thread context only, never from an interrupt handler; it may block for the time its comment states;
 *  - not re-entrant per kind: one unit owns each kind and calls it from its own thread (the owner is named);
 *  - "FW l.N" = line N of design/firmware.md (commit 783ddc4).
 * Callbacks registered here run in a driver context (interrupt, timer or work queue): they must not block and must
 * only queue work for their unit's thread.
 *
 * No chip pin is named here or in any implementation (FW l.77; pins come from the board files of step 7).
 */
#ifndef RING_RHW_RHW_H
#define RING_RHW_RHW_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <ring_rhw/rrec_spec.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ================================================================== disk (SD card over SPI, FW 5.1). Owner: ring_store */
struct rhw_disk_api {
	/* DISK_IOCTL_CTRL_INIT after VDD_SD is on and the bus resumed (FW l.506, l.507). Blocks up to the card's start-up
	 * (simulated: no wait). -EIO when the card does not answer. */
	int (*init)(void);
	/* DISK_IOCTL_CTRL_DEINIT before VDD_SD goes off (FW l.506). Does not block. */
	int (*deinit)(void);
	/* Read `count` sectors of 512 bytes from `lba` into buf (count x 512 bytes). Blocks for the transfer. -EIO on a
	 * read error (FW l.143), -EINVAL past the card end. */
	int (*read)(uint32_t lba, uint8_t *buf, uint32_t count);
	/* Write `count` sectors from buf in ONE call (one multi-block write per chunk, FW l.515). Blocks for the transfer.
	 * -EIO on a write error (the caller retries, FW l.643), -EINVAL past the card end. */
	int (*write)(uint32_t lba, const uint8_t *buf, uint32_t count);
	/* DISK_IOCTL_GET_SECTOR_COUNT at mount (FW l.507, l.654). Requires init. */
	int (*sector_count)(uint32_t *out);
};

/* ================================================================== microphone input (pdm20, FW 4.1, 4.2). Owner: ring_audio */
struct rhw_mic_cfg {                     /* the values of FW l.410 to l.420 */
	uint32_t pcm_rate;               /* RREC_PCM_RATE_HZ */
	uint8_t pcm_width;               /* RREC_PCM_WIDTH_BITS */
	uint8_t channels;                /* RREC_CHANNELS */
	uint32_t chan_map_lo;            /* FW l.414: channel 0 left (mic 1), channel 1 right (mic 2); the real file builds
	                                  * it with dmic_build_channel_map(); the simulated input only records it */
	uint32_t min_pdm_clk_hz;         /* RREC_PDM_CLK_MIN_HZ */
	uint32_t max_pdm_clk_hz;         /* RREC_PDM_CLK_MAX_HZ */
	int8_t gain_db;                  /* RREC_PDM_GAIN_DB */
	uint32_t block_size;             /* RREC_BLOCK_BYTES */
	uint8_t block_count;             /* RREC_BLOCK_COUNT */
};
struct rhw_mic_api {
	/* dmic_configure() (FW l.429: first step of the start). Does not block. -ENOTSUP for values the input cannot take. */
	int (*configure)(const struct rhw_mic_cfg *cfg);
	/* DMIC_TRIGGER_START (FW l.429: after HFXO runs). Blocks for the trigger only. */
	int (*start)(void);
	/* DMIC_TRIGGER_STOP (FW l.463). Blocks for the trigger only; blocks already filled stay readable until read
	 * returns an error. */
	int (*stop)(void);
	/* dmic_read(): wait up to timeout_ms for the next block of RREC_BLOCK_BYTES (256 stereo frames, interleaved,
	 * channel 0 first, FW l.443). On 0, *block points to the block and *size holds its length; the caller gives it
	 * back with free_block. -EAGAIN when no block came in timeout_ms; -EIO after stop when no block is left, or on a
	 * driver error. Blocks up to timeout_ms. */
	int (*read)(void **block, size_t *size, int32_t timeout_ms);
	/* Gives a block back to the slab (k_mem_slab_free). Does not block. */
	void (*free_block)(void *block);
	/* Clock pins to the sleep state (clock output low, DATA input no pull): at boot before VDD_MIC is ever on, and
	 * after every stop before VDD_MIC goes off (FW l.463, l.465; decision D11c). Does not block. */
	int (*pins_sleep)(void);
	/* Clock pins to the default state, before start (FW l.465: VDD_MIC on before the clock starts). */
	int (*pins_default)(void);
};

/* ================================================================== power chip (nPM1304, FW 8). Owner: ring_power;
 * rail_set also by ring_store (VDD_SD) and ring_recorder (VDD_MIC, only from rec_mics_on(), FW l.342) */
enum rhw_rail {
	RHW_RAIL_MIC = 0,                /* LDSW1, VDD_MIC (FW l.872, l.457) */
	RHW_RAIL_SD = 1,                 /* LDSW2, VDD_SD (FW l.874, l.506) */
	RHW_RAIL_COUNT
};
struct rhw_pmic_sample {                 /* one system monitor sample (FW l.926) */
	uint16_t mv;                     /* battery voltage, mV */
	int32_t ua;                      /* battery current inside the chip's path, µA, positive = discharge (this
	                                  * interface's sign; the real file converts, kit fact K6) */
	int16_t temp_c_x10;              /* thermistor temperature, 0.1 °C */
	int16_t die_c_x10;               /* die temperature, 0.1 °C (chunk field temp_c_x10, FW l.568) */
};
struct rhw_pmic_charge {                 /* charger status (FW l.1032, l.176) */
	uint8_t state;                   /* enum rrec_charge_state (decoded from BCHGCHARGESTATUS by the real file) */
	uint8_t err_reason;              /* BCHGERRREASON, raw (0 = none latched) */
	uint8_t err_sensor;              /* BCHGERRSENSOR, raw */
};
struct rhw_pmic_cb {
	void (*vbus)(bool present);      /* VBUS in (true) or removed (false), from PMIC_INT (FW l.979) */
	void (*charge_error)(void);      /* a charge error event (FW l.176) */
};
struct rhw_pmic_api {
	/* Switch a load switch on or off. caller = a constant string naming the calling function (kept in the simulated
	 * log for the one-path rule of FW l.342: only "rec_mics_on" switches RHW_RAIL_MIC on). Blocks for one I2C
	 * transfer. */
	int (*rail_set)(enum rhw_rail rail, bool on, const char *caller);
	/* The rail as last set (false at reset). Does not block. */
	bool (*rail_get)(enum rhw_rail rail);
	/* BCHGENABLESET / BCHGENABLECLR (FW l.888). One I2C transfer. */
	int (*charger_enable)(bool on);
	/* BCHGISET in µA (FW l.878). The caller disables the charger first (FW l.894). One I2C transfer. */
	int (*charger_current)(uint32_t ua);
	/* Charge state and latched errors (FW l.1032). One I2C transfer. */
	int (*charge_status)(struct rhw_pmic_charge *out);
	/* One sample (FW l.926, l.928). Blocks for the ADC conversion. */
	int (*sample)(struct rhw_pmic_sample *out);
	/* BCHGILIMSTATUS.BCHGILIMBATACTIVE (FW l.990): 1 active, 0 not, or a negative errno. One I2C transfer. */
	int (*ilim_active)(void);
	/* RSTCAUSE (bits RREC_RST_*), CHARGERERRREASON, CHARGERERRSENSOR (FW l.996). One I2C transfer. */
	int (*reset_causes)(uint8_t *rstcause, uint8_t *err_reason, uint8_t *err_sensor);
	/* TASKCLRERRLOG (FW l.996). */
	int (*reset_causes_clear)(void);
	/* SHPHLDCONFIG with the press time in ms (RREC_SHPHLD_MS, FW l.938). */
	int (*shphld_config)(uint32_t press_ms);
	/* TASKSHPHLDCFGSTROBE (FW l.938). */
	int (*shphld_strobe)(void);
	/* TASKENTERSHIPMODE (FW l.940). On the real chip the supply goes and nothing after it runs; the caller must expect
	 * to return anyway (FW l.941). */
	int (*ship_task)(void);
	/* VBUS present now, as the chip reports it (FW l.979). Does not block on the simulated chip; one I2C transfer on
	 * the real one. */
	bool (*vbus_present)(void);
	/* Register the callbacks (NULL clears). There is deliberately no call that drives VBUS (FW l.977) and none that
	 * writes POFCONFIG or VSYSPOF (FW l.997). */
	void (*set_callbacks)(const struct rhw_pmic_cb *cb);
};

/* ================================================================== HFXO (FW l.428). Owner: ring_audio; ring_xfer for USB */
struct rhw_hfxo_api {
	/* Request the 32 MHz crystal; `running` is called once (driver context) when it runs. Requests are counted:
	 * each request needs one release. Does not block. */
	int (*request)(void (*running)(void));
	/* Release one request (FW l.463: after the microphones stop). */
	int (*release)(void);
	/* true while the crystal runs. */
	bool (*running)(void);
};

/* ================================================================== motor pin (MOTOR, FW 3.1 l.314). Owner: ring_motor */
struct rhw_motor_api {
	/* MOTOR high (true) = U11 enabled = motor on; low = off. Never PWM (FW l.314). Does not block; may be called
	 * from the k_timer handler of the player (the one exception to "thread only"). */
	int (*set)(bool high);
};

/* ================================================================== storage bus (spi00 power management, FW l.506). Owner: ring_store */
struct rhw_sdbus_api {
	/* Suspend spi00 so its sleep pin state applies (lines inputs, no pull) BEFORE VDD_SD goes off; also at boot
	 * before any SPI use (FW l.506). */
	int (*suspend)(void);
	/* Resume spi00 (default pin state) 1 ms after VDD_SD came on, before init (FW l.506). */
	int (*resume)(void);
};

/* ================================================================== USB transport (FW 6.1). Owner: ring_xfer */
enum rhw_usb_event {
	RHW_USB_VBUS_READY,              /* UDC_EVT_VBUS_READY: the class enables the stack now (FW l.978) */
	RHW_USB_VBUS_REMOVED,            /* UDC_EVT_VBUS_REMOVED: the class disables the stack (FW l.978) */
	RHW_USB_CONFIGURED,              /* USBD_MSG_CONFIGURATION: TRANSFER (FW l.171, l.673) */
	RHW_USB_UNCONFIGURED,            /* configuration 0 or a bus reset (FW l.178) */
	RHW_USB_SUSPENDED,               /* bus suspend (FW l.178) */
};
enum rhw_usb_speed {
	RHW_USB_FS = 0,                  /* full speed: 64-byte bulk packets (FW l.669) */
	RHW_USB_HS = 1,                  /* high speed: 512-byte bulk packets */
};
struct rhw_usb_cb {
	/* Bytes received on bulk OUT 0x01 (driver context; copy and queue). */
	void (*rx)(const uint8_t *data, size_t len);
	/* A bus event (driver context). */
	void (*event)(enum rhw_usb_event ev);
};
struct rhw_usb_api {
	/* usbd_init() once, then usbd_enable() (only after RHW_USB_VBUS_READY, FW l.978). */
	int (*enable)(void);
	/* usbd_disable() (on RHW_USB_VBUS_REMOVED, FW l.978). */
	int (*disable)(void);
	/* Send len bytes on bulk IN 0x81 as one response; the transport cuts them into packets of the bus speed's size and
	 * never adds a zero-length packet (FW l.688). Blocks until the host took every byte or timeout_ms passed:
	 * -EAGAIN on the timeout (host stopped reading), -ENODEV when the stack is not enabled. */
	int (*send)(const uint8_t *data, size_t len, int32_t timeout_ms);
	/* The speed found at the last bus reset (usbd_bus_speed(), FW l.669). */
	enum rhw_usb_speed (*speed)(void);
	/* Register the callbacks (NULL clears). */
	void (*set_callbacks)(const struct rhw_usb_cb *cb);
};

/* ================================================================== image store (slot 1 and MCUboot, FW 9.2). Owner: ring_sys */
enum rhw_reboot_reason {
	RHW_REBOOT_UPDATE = 1,           /* after FW_END (FW l.1013) */
	RHW_REBOOT_COMMAND = 2,          /* REBOOT command (FW l.707) */
	RHW_REBOOT_FACTORY_EXIT = 3,     /* FACTORY_EXIT (FW l.201) */
	RHW_REBOOT_FACTORY_VBUS = 4,     /* VBUS removed in FACTORY_TEST (FW l.204) */
	RHW_REBOOT_SELFTEST_FAIL = 5,    /* self-test failed or 30 s passed (FW l.1014) */
	RHW_REBOOT_CRASH = 6,            /* after the crash block was written (FW l.1063) */
};
struct rhw_image_api {
	/* Erase slot 1 (FW l.1013, FW_BEGIN). Blocks for the erase (seconds on the real chip). */
	int (*erase_slot1)(void);
	/* Write len bytes at `offset` inside slot 1 (offset + len <= RREC_IMAGE_MAX_BYTES, else -EINVAL; FW l.1012).
	 * There is no call that writes slot 0 or the MCUboot area (FW l.1012 rule 2). Blocks for the write. */
	int (*write)(uint32_t offset, const uint8_t *data, size_t len);
	/* Read back len bytes of slot 1 (for the image CRC, FW l.1013). */
	int (*read)(uint32_t offset, uint8_t *data, size_t len);
	/* boot_request_upgrade(BOOT_UPGRADE_TEST) (FW l.180, l.1013). */
	int (*request_test_upgrade)(void);
	/* boot_is_img_confirmed(): 1 confirmed, 0 not, or a negative errno (FW l.1014). */
	int (*is_confirmed)(void);
	/* boot_write_img_confirmed() (FW l.1014). */
	int (*confirm)(void);
	/* sys_reboot(); the simulated store records it and returns 0 (the test then calls rhw_sim_reboot()). */
	int (*reboot)(enum rhw_reboot_reason why);
};

/* ================================================================== persistent settings (RRAM settings area, FW l.1010). Owner: ring_sys */
struct rhw_persist {
	uint8_t factory_flag;            /* 1 = factory flag set (FW l.1019) */
	bool time_saved;                 /* a time was saved on entry into SHIP or OFF (FW l.1005) */
	int64_t saved_utc_ms;            /* the saved time */
	int16_t saved_tz_min;
	bool saved_zone_known;
};
struct rhw_persist_api {
	/* Read the stored values (all zero when nothing was ever saved). Blocks for the settings read. */
	int (*load)(struct rhw_persist *out);
	/* Store the values through the settings subsystem (FW l.1012 rule 3). Blocks for the write. */
	int (*save)(const struct rhw_persist *in);
};

/* ================================================================== retained memory (crash block, gpregret1, FW l.1063). Owner: ring_sys */
struct rhw_retained_api {
	/* Copy len bytes (len <= RREC_RETAINED_BYTES) of the retained area from its start. Allowed in the fatal error
	 * handler (no lock, no wait). */
	int (*read)(uint8_t *buf, size_t len);
	int (*write)(const uint8_t *buf, size_t len);
	/* Zero the whole area. */
	int (*clear)(void);
	/* gpregret1 (one byte). Allowed in the fatal error handler. */
	int (*gpregret1_get)(uint8_t *out);
	int (*gpregret1_set)(uint8_t v);
};

/* ================================================================== watchdog (wdt31, FW l.1065). Owner: ring_sys */
struct rhw_wdt_api {
	/* Install one channel with timeout_ms (RREC_WDT_TIMEOUT_MS) and start it. Once per boot. */
	int (*start)(uint32_t timeout_ms);
	/* Feed (FW l.1065: every 1 s only with progress). Does not block. */
	int (*feed)(void);
};

/* ================================================================== fuel gauge (FW l.926, l.927). Owner: ring_power */
struct rhw_gauge_out {
	uint16_t soc_x10;                /* state of charge, 0.1 % (0 to 1000) */
	uint32_t tte_s;                  /* time to empty in s, UINT32_MAX when unknown (charging) */
	uint32_t ttf_s;                  /* time to full in s, UINT32_MAX when unknown (not charging) */
};
struct rhw_gauge_api {
	/* Start the gauge from a first sample (nrf_fuel_gauge_init()). Blocks for the library's init. */
	int (*start)(const struct rhw_pmic_sample *first);
	/* One step: the sample, with the CURRENT ALREADY CORRECTED by the motor charge (I_fed, FW l.927, positive =
	 * discharge as in struct rhw_pmic_sample), and the seconds since the last step in ms. Pure computation. */
	int (*process)(const struct rhw_pmic_sample *s, uint32_t dt_ms, struct rhw_gauge_out *out);
};

/* ================================================================== clock (GRTC, FW 9.1). Any unit; any thread or interrupt */
struct rhw_clock_api {
	/* ms since boot (k_uptime_get on the real chip). Never fails. */
	int64_t (*now_ms)(void);
	/* the cycle counter (64-bit, from k_cycle_get_64 or k_cycle_get_32 extended on the real chip); the chunk header's
	 * uptime_ns uses it with cycles_per_sec (FW l.558, l.573) */
	uint64_t (*cycles)(void);
	/* sys_clock_hw_cycles_per_sec() (FW l.573; kit fact K14) */
	uint32_t (*cycles_per_sec)(void);
	/* device id (FICR, 64 bits; FW l.696, l.1057). */
	int (*device_id)(uint64_t *out);
};

/* ================================================================== beacon (not-connectable advertising, FW l.1031, l.1057). Owner: ring_factory */
struct rhw_beacon_api {
	/* Start advertising with this name (NUL-terminated, at most 29 bytes), interval and TX power. The ship beacon and
	 * T-RADIO pass connectable = false (FW l.1057: "advertising that cannot be connected to"); the flag exists so the
	 * simulated beacon can record what the caller asked. A running beacon is replaced. Blocks for the controller
	 * command. */
	int (*start)(const char *name, uint16_t interval_ms, int8_t tx_dbm, bool connectable);
	/* Stop it (no error when none runs). */
	int (*stop)(void);
};

/* ================================================================== active instances */
const struct rhw_disk_api *rhw_disk(void);
const struct rhw_mic_api *rhw_mic(void);
const struct rhw_pmic_api *rhw_pmic(void);
const struct rhw_hfxo_api *rhw_hfxo(void);
const struct rhw_motor_api *rhw_motor(void);
const struct rhw_sdbus_api *rhw_sdbus(void);
const struct rhw_usb_api *rhw_usb(void);
const struct rhw_image_api *rhw_image(void);
const struct rhw_persist_api *rhw_persist(void);
const struct rhw_retained_api *rhw_retained(void);
const struct rhw_wdt_api *rhw_wdt(void);
const struct rhw_gauge_api *rhw_gauge(void);
const struct rhw_clock_api *rhw_clock(void);
const struct rhw_beacon_api *rhw_beacon(void);

/* Registration by a real file (development kit build). 0, -EINVAL for NULL, -EPERM with CONFIG_RING_RHW_SIM or when
 * that kind was already registered. Call once, before the units start (SYS_INIT, level APPLICATION). */
int rhw_register_disk(const struct rhw_disk_api *api);
int rhw_register_mic(const struct rhw_mic_api *api);
int rhw_register_pmic(const struct rhw_pmic_api *api);
int rhw_register_hfxo(const struct rhw_hfxo_api *api);
int rhw_register_motor(const struct rhw_motor_api *api);
int rhw_register_sdbus(const struct rhw_sdbus_api *api);
int rhw_register_usb(const struct rhw_usb_api *api);
int rhw_register_image(const struct rhw_image_api *api);
int rhw_register_persist(const struct rhw_persist_api *api);
int rhw_register_retained(const struct rhw_retained_api *api);
int rhw_register_wdt(const struct rhw_wdt_api *api);
int rhw_register_gauge(const struct rhw_gauge_api *api);
int rhw_register_beacon(const struct rhw_beacon_api *api);

/* The real clock of this module (k_uptime_get, k_cycle_get_64, sys_clock_hw_cycles_per_sec, hwinfo device id when
 * CONFIG_HWINFO). Always built with CONFIG_RING_RHW; active without SIM; tests call it directly (kit fact K14). */
extern const struct rhw_clock_api rhw_clock_real;

#ifdef __cplusplus
}
#endif

#endif
