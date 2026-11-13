/*
 * rrec_boot.c: the boot sequence of the join (software step 6, unit J; design/firmware.md 1.2 rows of BOOT, l.133 to
 * l.140, and l.893, l.996, l.1005, l.1063, l.1014). The core is in BOOT (main() started it there); this sequence starts
 * every unit, then gives the core its facts and "init done" or "storage init fails".
 * Order: settings, crash block, reset causes, the units, then CHARGE ON (with VBUS) BEFORE the storage is mounted
 * (FW l.893), the mount (3 tries 200 ms apart, inside rst_mount), the facts, the event.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/byteorder.h>
#if defined(CONFIG_BT)
#include <zephyr/bluetooth/bluetooth.h>
#endif

#include <ring_audio/rau.h>
#include <ring_glue/rglue.h>
#include <ring_motor/rmo.h>
#include <ring_power/rpw.h>
#include <ring_recorder/rrec.h>
#include <ring_rhw/rhw.h>
#include <ring_store/rst.h>
#include <ring_sys/rsy.h>
#include <ring_xfer/rxf.h>
#if defined(CONFIG_RING_FACTORY)
#include <ring_factory/rfa.h>
#endif
#if defined(CONFIG_RING_RHW_SIM)
#include <ring_rhw/rhw_sim.h>
#endif

#include "rrec_int.h"

int rrec_boot(void)
{
	struct rst_mount_info mi;
	struct rrec_crash crash;
	struct rpw_values v;
	uint8_t gpreg = 0;
	uint8_t args[8];
	int64_t guess;
	bool selftest;
	bool vbus;
	int pr;
	int mr;

#if defined(CONFIG_RING_RHW_SIM)
	(void)rhw_sim_add_reboot_hook(rrec_sim_reboot_hook);
#endif
	rrec_st.core_state = RC_ST_BOOT;
	rrec_bridge_start();
	(void)rsy_init(rrec_log);                         /* settings: factory flag, saved time (FW l.1010) */
	if (rsy_crash_take(&crash, &gpreg) == 1) {
		rrec_log_crash(&crash);                   /* FW l.1063: a valid crash block into the log, then cleared */
	} else {
		(void)rhw_retained()->gpregret1_get(&gpreg);
	}
	sys_put_le32(0, args);                            /* the main chip's reason: not read through rhw.h (notes) */
	args[4] = gpreg;
	rrec_log(RREC_LOG_MAIN_RESET, args, 5);           /* FW l.996: beside the power chip's causes */
	if (rsy_time_guess(&guess)) {
		sys_put_le64((uint64_t)guess, args);
		rrec_log(RREC_LOG_TIME_GUESS, args, 8);   /* ruling D18: a guess, the clock stays not set */
	}
	(void)rpw_boot_causes(rrec_log);                  /* RSTCAUSE and the charger error log, then cleared */
	(void)rmo_init(rrec_motor_cb());
	(void)rst_init(rrec_store_cb());                  /* the bus asleep before any SPI use (FW l.506) */
	(void)rau_init(rrec_audio_cb());                  /* the clock pins asleep before VDD_MIC is ever on (FW l.465) */
	(void)rxf_start(rrec_backend(), rrec_xfer_cb());  /* the stack itself starts on VBUS (FW l.978) */
#if defined(CONFIG_RING_FACTORY)
	(void)rfa_init(rrec_factory_ops());
#endif
	(void)rsy_wdt_start();                            /* fed while no recording runs (FW l.1065) */
	rrec_st.fact_factory = rsy_factory_flag();
	rrec_st.fact_factory_pending = true;

	/* FW l.893: with VBUS the charger is on BEFORE the storage is mounted (rpw_start does charge on) */
	pr = rpw_start(rrec_power_cb());
	mr = rst_mount(true, &mi);

	vbus = rhw_pmic()->vbus_present();
	selftest = rsy_selftest_start(vbus) == 1;
	if (pr == 0) {
		rpw_values(&v);
		rglue_battery((enum rc_batt)v.level);     /* in BOOT the level is kept; "init done" decides (R12) */
	}
	if (vbus) {
		rglue_event(RC_EV_VBUS_IN);               /* the fact (and charge on, R8) */
	}
	if (mr != 0) {
		sys_put_le32((uint32_t)mr, args);
		rrec_log(RREC_LOG_FAULT_STORAGE_INIT, args, 4);
		rglue_event(RC_EV_STORAGE_INIT_FAILED);  /* row FW l.138 */
		return mr;
	}
	rrec_st.boot_count = mi.boot_count;
	rrec_st.card_sectors = mi.card_sectors;
	rrec_st.fact_open = mi.open_flag;
	rrec_st.fact_open_pending = true;
	if (selftest) {
		rsy_selftest_pass(RSY_ITEM_STORAGE);      /* FW l.1014: storage mounts */
#if defined(CONFIG_BT)
		if (bt_is_ready()) {
			rsy_selftest_pass(RSY_ITEM_BLUETOOTH);
		}
#endif
	}
	if (mi.space.sfull) {
		rglue_event(RC_EV_STORAGE_SFULL);         /* the fact: R-STB sends STANDBY to ERR_STORAGE_FULL */
	}
	rglue_event(RC_EV_INIT_DONE);                     /* rows FW l.135 to l.140 */
	return 0;
}

int rrec_init(void)
{
	return rrec_boot();
}
