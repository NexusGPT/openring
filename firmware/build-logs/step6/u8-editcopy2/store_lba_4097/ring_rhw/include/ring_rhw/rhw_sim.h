/*
 * rhw_sim.h: controls of the simulated drivers (software step 6, unit U0). TEST BUILDS ONLY: every declaration here
 * exists only with CONFIG_RING_RHW_SIM=y (the full run checks that the development kit build has it off).
 *
 * The simulated drivers are written for this project (no code of the kit). They run on native_sim and on
 * nrf54lm20bsim/nrf54lm20a/cpuapp, on the kernel's simulated time (k_sleep costs no wall time). Each call of a driver
 * is written into ONE ordered event log (kind, three arguments, result, time in µs, caller), so a test reads order
 * and time from one place. Plan: firmware/docs/step6-plan.md section 5.
 *
 * Controls are called from the test thread (any thread; never from an interrupt handler unless the comment says so).
 * A fault stays set until the test clears it, rhw_sim_reset() runs, or the comment says it fires once.
 *
 * Two resets:
 *  - rhw_sim_reset(): everything back to the start values, the three kept stores emptied, every fault cleared, the
 *    event log emptied. Call it at the start of each test case.
 *  - rhw_sim_reboot(): stands for a reset of the ring (power cycle, ship-mode wake, watchdog, FW_END). It calls every
 *    registered reboot hook (each unit's "clear my RAM state") and puts every driver's own state back to reset values,
 *    and KEEPS exactly three stores: the simulated card's sectors, the persistent settings and the retained memory
 *    (crash block and gpregret1). It also keeps the test's world: faults and set values (card size, cell, VBUS
 *    present, mic source) and the event log itself (the test's observer, not ring state), where it writes
 *    RHW_EV_SIM_REBOOT.
 */
#ifndef RING_RHW_RHW_SIM_H
#define RING_RHW_RHW_SIM_H

#include <ring_rhw/rhw.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ================================================================== the event log */
enum rhw_ev_kind {
	RHW_EV_NONE = 0,
	/* card: a0 lba, a1 count, a2 extra (see each) */
	RHW_EV_DISK_INIT,           /* res 0 or -EIO */
	RHW_EV_DISK_DEINIT,
	RHW_EV_DISK_READ,           /* a0 lba, a1 count */
	RHW_EV_DISK_WRITE,          /* a0 lba, a1 count, a2 write call number (from 1 since the last reset) */
	RHW_EV_DISK_COUNT,          /* a0 sectors */
	RHW_EV_DISK_REFUSED,        /* a call while VDD_SD is off or the card is not initialised: a0 the refused kind */
	RHW_EV_DISK_CUT,            /* the cut happened: a0 lba of the write, a1 sectors kept */
	/* microphone input */
	RHW_EV_MIC_CONFIGURE,       /* a0 pcm_rate, a1 block_size, a2 channels */
	RHW_EV_MIC_START,
	RHW_EV_MIC_STOP,
	RHW_EV_MIC_READ,            /* a0 block index (-1 when none), a1 timeout ms; res 0, -EAGAIN, -EIO, -ENOMEM */
	RHW_EV_MIC_FREE,
	RHW_EV_MIC_DROP,            /* a block the input dropped: a0 block index */
	RHW_EV_MIC_PINS_SLEEP,
	RHW_EV_MIC_PINS_DEFAULT,
	/* power chip */
	RHW_EV_PMIC_RAIL,           /* a0 rail, a1 on; caller = the caller string given */
	RHW_EV_PMIC_CHG_ENABLE,     /* a0 on */
	RHW_EV_PMIC_CHG_CURRENT,    /* a0 µA */
	RHW_EV_PMIC_CHG_STATUS,     /* a0 state */
	RHW_EV_PMIC_SAMPLE,         /* a0 mV, a1 µA, a2 sample number (from 1) */
	RHW_EV_PMIC_ILIM,           /* a0 active */
	RHW_EV_PMIC_RST_READ,       /* a0 RSTCAUSE */
	RHW_EV_PMIC_RST_CLEAR,
	RHW_EV_PMIC_SHPHLD_CFG,     /* a0 ms */
	RHW_EV_PMIC_SHPHLD_STROBE,
	RHW_EV_PMIC_SHIP,
	RHW_EV_PMIC_VBUS,           /* the test changed VBUS: a0 present */
	RHW_EV_PMIC_CHARGE_ERROR,   /* the test raised a charge error: a0 reason, a1 sensor */
	RHW_EV_SHIP_REFUSED,        /* a driver call after the ship task: a0 the refused kind */
	/* HFXO */
	RHW_EV_HFXO_REQUEST,        /* a0 requests now */
	RHW_EV_HFXO_RUNNING,
	RHW_EV_HFXO_RELEASE,        /* a0 requests now */
	/* motor pin, storage bus */
	RHW_EV_MOTOR,               /* a0 high */
	RHW_EV_SDBUS_SUSPEND,
	RHW_EV_SDBUS_RESUME,
	/* USB transport */
	RHW_EV_USB_ENABLE,
	RHW_EV_USB_DISABLE,
	RHW_EV_USB_PACKET,          /* one IN packet: a0 length (0 = a zero-length packet), a1 packet size of the speed */
	RHW_EV_USB_RX,              /* the host wrote: a0 length */
	RHW_EV_USB_EVENT,           /* a0 enum rhw_usb_event */
	/* image store */
	RHW_EV_IMG_ERASE,
	RHW_EV_IMG_WRITE,           /* a0 offset, a1 length */
	RHW_EV_IMG_READ,            /* a0 offset, a1 length */
	RHW_EV_IMG_REQUEST,
	RHW_EV_IMG_IS_CONFIRMED,
	RHW_EV_IMG_CONFIRM,
	RHW_EV_IMG_REBOOT,          /* a0 reason */
	/* settings, retained memory, watchdog */
	RHW_EV_PERSIST_LOAD,
	RHW_EV_PERSIST_SAVE,        /* a0 factory flag, a1 time_saved */
	RHW_EV_RET_READ,
	RHW_EV_RET_WRITE,           /* a0 length */
	RHW_EV_RET_CLEAR,
	RHW_EV_GPREG_SET,           /* a0 value */
	RHW_EV_WDT_START,           /* a0 timeout ms */
	RHW_EV_WDT_FEED,
	/* gauge */
	RHW_EV_GAUGE_START,
	RHW_EV_GAUGE_PROCESS,       /* a0 µA fed, a1 dt ms, a2 soc_x10 out */
	/* beacon */
	RHW_EV_BEACON_START,        /* a0 interval ms, a1 tx dBm, a2 connectable; caller = the name */
	RHW_EV_BEACON_STOP,
	/* the simulation */
	RHW_EV_SIM_REBOOT,
	RHW_EV_KIND_COUNT
};

struct rhw_sim_ev {
	uint32_t seq;               /* 0, 1, 2 ... in the order of the calls */
	int64_t t_us;               /* kernel uptime in µs at the call */
	uint16_t kind;              /* enum rhw_ev_kind */
	int64_t a0, a1, a2;
	int32_t res;                /* what the call returned */
	char caller[16];            /* the rail's caller string, the beacon's name, else the calling thread's name ("isr"
	                             * in an interrupt, "?" without CONFIG_THREAD_NAME) */
};

/* Entries kept (CONFIG_RING_RHW_SIM_LOG_SIZE); later ones are counted in rhw_sim_log_overflow() and not kept. */
uint32_t rhw_sim_log_count(void);
bool rhw_sim_log_get(uint32_t i, struct rhw_sim_ev *out);
uint32_t rhw_sim_log_overflow(void);
void rhw_sim_log_clear(void);
/* First index >= from with this kind, or -1. */
int32_t rhw_sim_log_find(uint16_t kind, uint32_t from);
/* Entries of this kind since the last clear. */
uint32_t rhw_sim_log_count_kind(uint16_t kind);
/* Print the log (printk), for a failing test. */
void rhw_sim_log_dump(void);

/* ================================================================== resets */
void rhw_sim_reset(void);
void rhw_sim_reboot(void);
/* A unit's "clear my RAM state" hook for rhw_sim_reboot(); the same function registered twice counts once.
 * -ENOMEM past CONFIG_RING_RHW_SIM_REBOOT_HOOKS. Hooks stay registered across reboots and resets. */
int rhw_sim_add_reboot_hook(void (*fn)(void));
/* rhw_sim_reboot() calls so far (cleared by rhw_sim_reset). */
uint32_t rhw_sim_reboots(void);

/* ================================================================== card (ring,sim-disk) */
/* Sector count (default: the devicetree node's sector-count, else 7,812,500 = 4,000,000,000 bytes, FW l.654). Only
 * written sectors use memory (CONFIG_RING_RHW_SIM_DISK_POOL sectors); unwritten ones read as zero. A write past the
 * pool fails with -ENOSPC and is logged (a test card too small for the test). */
void rhw_sim_disk_set_sectors(uint32_t sectors);
/* The next n init calls fail with -EIO. */
void rhw_sim_disk_fail_init(uint32_t n);
/* Write calls n to n + k - 1 (counted from 1 since this call) fail with -EIO and store nothing. k = 0 clears. */
void rhw_sim_disk_fail_write(uint32_t n, uint32_t k);
/* Every read that covers this LBA fails with -EIO; UINT32_MAX clears. */
void rhw_sim_disk_read_error_at(uint32_t lba);
/* The power is cut during write call n (counted from 1 since this call), after its first k sectors: those k are
 * stored, the rest of that write and every later write are lost (the calls return 0, standing for the moments before
 * the ring dies). Ends at rhw_sim_reboot() or rhw_sim_reset(). n = 0 clears. */
void rhw_sim_disk_cut(uint32_t n, uint32_t k);
/* true once the cut happened (until the next reboot) */
bool rhw_sim_disk_was_cut(void);
/* Each write blocks this long (k_sleep) before it stores (a stalling card). */
void rhw_sim_disk_stall_ms(uint32_t ms);
/* Calls refused because VDD_SD was off or the card not initialised (FW l.506). */
uint32_t rhw_sim_disk_refused(void);
uint32_t rhw_sim_disk_write_calls(void);
/* Read or write a sector directly, without the log, the rail rule or the faults (test set-up and checks). */
void rhw_sim_disk_peek(uint32_t lba, uint8_t out[RREC_SECTOR_BYTES]);
int rhw_sim_disk_poke(uint32_t lba, const uint8_t in[RREC_SECTOR_BYTES]);
/* Sectors held in the sparse store. */
uint32_t rhw_sim_disk_stored(void);

/* ================================================================== microphone input (ring,sim-mic) */
enum rhw_sim_mic_source {
	RHW_SIM_MIC_COUNTER = 0,    /* left = frame number since start (16 bits, wraps), right = its bitwise inverse */
	RHW_SIM_MIC_SINE = 1,       /* a 1 kHz sine on both channels, peak level set in whole dBFS (0 = 32767) */
};
void rhw_sim_mic_source(enum rhw_sim_mic_source src, int level_dbfs);
/* One channel (0 left, 1 right) stuck at a value; channel -1 clears. */
void rhw_sim_mic_stuck(int channel, int16_t value);
/* Block n (from 0 since start) holds -32768 at frame 0 left and 32767 at frame 1 right; -1 clears. */
void rhw_sim_mic_clip_block(int32_t n);
/* After n blocks were delivered, no block comes any more: every read waits its timeout and returns -EAGAIN (the
 * 100 ms watch of FW l.169). -1 clears. */
void rhw_sim_mic_stop_after(int32_t n);
/* Block n is never delivered (the next read gets block n + 1 at its own time); logged RHW_EV_MIC_DROP. -1 clears. */
void rhw_sim_mic_drop_block(int32_t n);
/* The read that would deliver block n returns -EIO once and block n is lost. -1 clears. */
void rhw_sim_mic_read_error(int32_t n);
/* The configuration last received; false when none since the reset. */
bool rhw_sim_mic_last_cfg(struct rhw_mic_cfg *out);
uint32_t rhw_sim_mic_delivered(void);
uint32_t rhw_sim_mic_held(void);         /* blocks read and not freed */
bool rhw_sim_mic_pins_asleep(void);      /* the last pin state applied was the sleep state */

/* ================================================================== power chip */
/* VBUS now: the power chip's callback (vbus) and the USB transport's event (VBUS_READY or VBUS_REMOVED) both fire, in
 * that order, in the caller's context. */
void rhw_sim_vbus(bool present);
/* Only the power chip side (no USB event). */
void rhw_sim_pmic_vbus(bool present);
/* VBUS changes at uptime t_ms (from a timer, so the callbacks run in interrupt context there). One pending change. */
void rhw_sim_vbus_at(int64_t t_ms, bool present);
/* A charge error: latches reason and sensor, the state reads RREC_CHG_ERROR, the charge_error callback fires. */
void rhw_sim_pmic_charge_error(uint8_t reason, uint8_t sensor);
/* The current-limit bit reads active for sample number n (counted from 1 since this call; it reads active from
 * that sample until the next sample). 0 clears. */
void rhw_sim_pmic_ilim_at_sample(uint32_t n);
/* RSTCAUSE and the charger error log the next reset_causes read gives (cleared by reset_causes_clear). */
void rhw_sim_pmic_set_reset_causes(uint8_t rstcause, uint8_t err_reason, uint8_t err_sensor);
/* While the motor pin is high, sample mV is lower by this much (T-MOTOR, FW l.1028). */
void rhw_sim_pmic_motor_dip(uint16_t mv);
/* Samples from a script: each sample call returns the next entry; the last one repeats. n = 0 goes back to the
 * fixed sample (3,900 mV, 3,000 µA, 25.0 °C, die 30.0 °C). At most 64 entries. */
void rhw_sim_pmic_script(const struct rhw_pmic_sample *s, uint32_t n);
/* Samples from a simple cell: capacity in µAh, a start charge in µAh, a base current and the current each rail adds
 * (µA). Each sample takes off the charge of the time since the last sample at the current of THIS sample (the rails
 * as they are now). Voltage = 3,300 mV + 1,050 mV x charge / capacity (empty 3.30 V, full 4.35 V); with VBUS and the
 * charger on, the current is minus the charger current and the charge rises. */
void rhw_sim_pmic_cell(uint32_t capacity_uah, uint32_t start_uah, uint32_t base_ua, uint32_t mic_ua, uint32_t sd_ua);
/* Override the charge state (enum rrec_charge_state); -1 = automatic: CC with VBUS and the charger on, else OFF. */
void rhw_sim_pmic_charge_state(int state);
bool rhw_sim_pmic_charger_on(void);
uint32_t rhw_sim_pmic_charger_ua(void);
/* The caller string of the last write to a rail ("" when none). */
const char *rhw_sim_pmic_rail_caller(enum rhw_rail rail);
/* true after the ship task until a reboot; then every driver call is refused (-ESHUTDOWN) and counted. */
bool rhw_sim_shipped(void);
uint32_t rhw_sim_ship_refused(void);

/* ================================================================== gauge */
void rhw_sim_gauge_start_soc(uint16_t soc_x10);     /* default 800 */
void rhw_sim_gauge_capacity(uint32_t uah);          /* default 17,600 µAh (FW l.114: the smallest cell) */
void rhw_sim_gauge_error(int err);                  /* process returns err while set; 0 clears */

/* ================================================================== HFXO */
void rhw_sim_hfxo_delay_ms(uint32_t ms);            /* default 1 ms */
void rhw_sim_hfxo_never(bool never);                /* the crystal never runs */
uint32_t rhw_sim_hfxo_requests(void);               /* requests not released */

/* ================================================================== motor pin, storage bus */
bool rhw_sim_motor_pin(void);
bool rhw_sim_sdbus_suspended(void);

/* ================================================================== USB transport (the test is the case's host) */
void rhw_sim_usb_speed(enum rhw_usb_speed s);       /* default full speed */
/* The host stops reading (send blocks for its timeout and returns -EAGAIN) or reads again. */
void rhw_sim_usb_host_stop(bool stop);
/* The host writes a request: the rx callback runs in the caller's context. -ENODEV when the stack is off. */
int rhw_sim_usb_host_write(const uint8_t *data, size_t len);
/* The host reads up to max bytes of what the ring sent; returns the count. */
size_t rhw_sim_usb_host_read(uint8_t *out, size_t max);
/* A sink that takes every packet as it is sent (for long responses); NULL goes back to the buffer
 * (CONFIG_RING_RHW_SIM_USB_HOST_BYTES). */
void rhw_sim_usb_host_sink(void (*sink)(const uint8_t *data, size_t len));
/* A bus event: the event callback runs in the caller's context. */
void rhw_sim_usb_event(enum rhw_usb_event ev);
bool rhw_sim_usb_enabled(void);

/* ================================================================== image store */
/* Write call n (from 1 since this call) fails with -EIO; 0 clears. */
void rhw_sim_image_write_error(uint32_t n);
void rhw_sim_image_set_confirmed(bool confirmed);   /* default true */
bool rhw_sim_image_upgrade_requested(void);
uint32_t rhw_sim_image_reboots(void);
int rhw_sim_image_last_reboot(void);                /* enum rhw_reboot_reason, 0 when none */
void rhw_sim_image_peek(uint32_t offset, uint8_t *out, size_t len);

/* ================================================================== persistent settings, retained memory */
void rhw_sim_persist_set(const struct rhw_persist *v);
void rhw_sim_persist_get(struct rhw_persist *out);
void rhw_sim_retained_set(const uint8_t *buf, size_t len);   /* a valid or a corrupt crash block, as the test writes it */
void rhw_sim_retained_get(uint8_t *buf, size_t len);
void rhw_sim_gpregret1_set(uint8_t v);
uint8_t rhw_sim_gpregret1_get(void);

/* ================================================================== watchdog */
/* true when, since start, a gap between start and a feed, between two feeds, or from the last feed to now was longer
 * than the timeout (the real chip would have reset). */
bool rhw_sim_wdt_would_reset(void);
bool rhw_sim_wdt_started(void);
uint32_t rhw_sim_wdt_feeds(void);

/* ================================================================== clock */
void rhw_sim_clock_rate(uint32_t hz);               /* cycles per second of the simulated counter; default 1 MHz */
void rhw_sim_clock_device_id(uint64_t id);          /* default 0x0123456789ABCDEF */

/* ================================================================== beacon */
struct rhw_sim_beacon {
	bool running;
	char name[30];
	uint16_t interval_ms;
	int8_t tx_dbm;
	bool connectable;
	uint32_t starts;
	uint32_t stops;
};
void rhw_sim_beacon_get(struct rhw_sim_beacon *out);

#ifdef __cplusplus
}
#endif

#endif
