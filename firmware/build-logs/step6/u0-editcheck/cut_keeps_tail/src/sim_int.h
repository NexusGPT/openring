/* Internal to the simulated drivers of ring_rhw (not public). */
#ifndef RING_RHW_SIM_INT_H
#define RING_RHW_SIM_INT_H

#include <zephyr/kernel.h>
#include <ring_rhw/rhw_sim.h>

/* the one lock of the simulation state; never held across a sleep or a callback */
extern struct k_spinlock sim_lock;

/* append one entry to the event log; caller NULL = the thread's name */
void sim_log(uint16_t kind, int64_t a0, int64_t a1, int64_t a2, int32_t res, const char *caller);

/* the simulated power chip's ship task without VBUS: the ring has no supply from now on */
void sim_set_shipped(void);

/* true after the ship task: the call is refused (logged and counted); kind = the refused event kind */
bool sim_dead(uint16_t kind);

/* driver resets: full = rhw_sim_reset (faults and stores too); otherwise rhw_sim_reboot (ring state only) */
void sim_disk_reset(bool full);
void sim_mic_reset(bool full);
void sim_pmic_reset(bool full);
void sim_hfxo_reset(bool full);
void sim_misc_reset(bool full);
void sim_usb_reset(bool full);
void sim_image_reset(bool full);
void sim_persist_reset(bool full);

/* facts the drivers read from each other */
bool sim_pmic_rail(enum rhw_rail rail);
void sim_disk_rail_changed(bool on);   /* VDD_SD went on or off: the card loses its init when off */
bool sim_motor_high(void);
void sim_usb_vbus_event(bool present);

extern const struct rhw_disk_api rhw_sim_disk_api;
extern const struct rhw_mic_api rhw_sim_mic_api;
extern const struct rhw_pmic_api rhw_sim_pmic_api;
extern const struct rhw_hfxo_api rhw_sim_hfxo_api;
extern const struct rhw_motor_api rhw_sim_motor_api;
extern const struct rhw_sdbus_api rhw_sim_sdbus_api;
extern const struct rhw_usb_api rhw_sim_usb_api;
extern const struct rhw_image_api rhw_sim_image_api;
extern const struct rhw_persist_api rhw_sim_persist_api;
extern const struct rhw_retained_api rhw_sim_retained_api;
extern const struct rhw_wdt_api rhw_sim_wdt_api;
extern const struct rhw_gauge_api rhw_sim_gauge_api;
extern const struct rhw_clock_api rhw_sim_clock_api;
extern const struct rhw_beacon_api rhw_sim_beacon_api;

#endif
