/*
 * rt.h: the harness of the recorder's suites (tests/recorder). The real core, glue (rglue), screens (memory display),
 * recorder and every unit of step 6 run on the simulated drivers of ring_rhw. The harness only observes: it wraps the
 * glue's ops of the product (rrec_action, rrec_glue_after, rrec_glue_screen_fact, rrec_sign_hook) to keep a log of
 * actions and steps, gives the screens a set of stand-in reads (no inbox, no devices), and drives the simulated
 * world (joystick edges through rglue_input, VBUS, USB requests, battery samples, card faults).
 * Expected values in the cases are typed from design/firmware.md ("FW l.N") or from the core's table (rc_table).
 */
#ifndef RT_H
#define RT_H

#include <stdbool.h>
#include <stdint.h>

#include <zephyr/kernel.h>
#include <zephyr/ztest.h>
#include <zephyr/sys/crc.h>

#include <ring_core/rc_core.h>
#include <ring_glue/rglue.h>
#include <ring_recorder/rrec.h>
#include <ring_rhw/rhw.h>
#include <ring_rhw/rhw_sim.h>
#include <ring_rhw/rrec_spec.h>
#include <ring_screens/rmd.h>
#include <ring_screens/rscr.h>
#include <ring_time/rtime.h>
#include <rrec_int.h>

/* ---- conditions of a boot ---- */
struct rt_boot {
	bool vbus;                /* VBUS present at power-up */
	uint16_t mv;              /* first battery sample in mV (0 = the simulated chip's 3,900 mV) */
	uint16_t mv_next;         /* the samples after the first (0 = same as mv) */
	uint16_t soc_x10;         /* gauge start (0 = the simulated gauge's 800) */
	uint32_t gauge_uah;       /* gauge capacity (0 = default) */
	uint32_t init_fail;       /* card init fails this many times */
	uint32_t chunks;          /* card with this many chunks (0 = the 4 GB card of FW l.654) */
	bool factory_flag;        /* persistent factory flag */
	bool unconfirmed;         /* the running image is not confirmed (the update self-test runs, FW l.1014) */
	int32_t ua;               /* with mv: the battery current of the samples in µA (0 = 3,000 µA discharge; < 0 charging) */
	uint8_t chg_forced;       /* 0 = the simulated charger's own state; else the charge state + 1 (RREC_CHG_* + 1) */
};

void rt_setup(void);                          /* once: screens and glue started */
void rt_setup_no_screens(void);               /* the glue only (the screens part never started), for recorder_a_noscreens */
extern bool rt_screens_started;               /* rt_setup started the screens part */
void rt_fresh(const struct rt_boot *b);       /* empty world, then a boot through rrec_boot() (NULL = defaults) */
void rt_reboot(const struct rt_boot *b);      /* rhw_sim_reboot(): the card, settings and retained memory kept */
void rt_core_at(enum rc_state s);             /* the core (and the join's copy) put in state s directly */
void rt_settle(void);                         /* the recorder's thread idle and the units quiet */
void rt_sleep(int32_t ms);

/* joystick, through rglue_input (the joystick driver's entry) */
void rt_long(void);                           /* centre held 1,100 ms */
void rt_short(void);
void rt_double(void);
/* VBUS (power chip and USB transport events), USB bus events */
void rt_vbus(bool on);
void rt_usb_ready(void);
void rt_usb_configured(void);
/* a USB request as the case writes it (FW 6.2): returns the response length (header included), status in *st */
int rt_usb(uint8_t op, const uint8_t *pl, uint32_t len, uint8_t *resp, size_t max, uint8_t *st);
/* the two halves of rt_usb: send without waiting; wait up to timeout_ms for the whole response */
int rt_usb_send(uint8_t op, const uint8_t *pl, uint32_t len);
int rt_usb_recv(uint8_t *resp, size_t max, uint8_t *st, int32_t timeout_ms);
/* charger, battery: the next sample(s) of the simulated power chip */
void rt_samples(uint16_t mv);

enum rc_state rt_state(void);
bool rt_mic(void);
bool rt_sd(void);

/* ---- the log of steps (test wrapper of rrec_glue_after) and actions (wrapper of rrec_action) ---- */
struct rt_step {
	int16_t row;
	uint8_t ev;
	uint8_t state;
	int64_t t_ms;
};
uint32_t rt_steps(void);
struct rt_step rt_step_get(uint32_t i);
bool rt_row_seen(int row);
void rt_steps_clear(void);
struct rt_act {
	uint8_t a;
	int64_t t_ms;
};
uint32_t rt_acts(void);
struct rt_act rt_act_get(uint32_t i);
/* the screens learned of a state other than RECORDING while VDD_MIC was on (a stand-in read of the screens, called
 * inside rscr_glue_after, counts it) */
uint32_t rt_mic_at_screens(void);
uint32_t rt_screens_told(void);

/* ---- the simulated event log ---- */
int32_t rt_find(uint16_t kind, int64_t a0, int64_t a1, uint32_t from);   /* a0/a1 = -1: any */
int32_t rt_find_rail(enum rhw_rail rail, bool on, uint32_t from);
int64_t rt_ev_us(int32_t i);
uint32_t rt_count_rail(enum rhw_rail rail, bool on);

/* ---- the display ---- */
bool rt_red_dot(void);                         /* the frame holds the red dot (40 px or more, as in tests/screens) */
bool rt_blanked(void);

/* ---- rows of FW 1.2: reach the From state and fire the event (shared by recorder_rows and recorder_sign1) ---- */
/* 0 = done; -ENOTSUP = the row needs a part not built (then the case says so) */
int rt_run_row(int row);
/* undo what a row left that blocks (ship mode waiting for VBUS removal) */
void rt_row_cleanup(int row);
const struct rc_row *rt_row(int row);
/* the power cut of the last open-flag card happened (read before its reboot) */
extern bool rt_cut_seen;

#endif
