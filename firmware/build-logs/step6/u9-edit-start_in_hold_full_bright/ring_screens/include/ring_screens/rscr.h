/*
 * Ring screens: the kernel part. Owns the screens thread, which keeps the pure state (rscr_logic.h) and draws it
 * (rscr_draw.h). Everything it reads from, and every action it takes in, the other modules goes through struct
 * rscr_ops: the product uses rscr_real_ops (ring_devices, ring_control, ring_iphone, ring_glue), the picture test uses
 * the pure data structures of the same modules.
 *
 * Wiring in the product (app/src/main.c):  rscr_start(&rscr_real_ops); the glue calls rscr_glue_after() after every
 * core step (rglue_ops.after), and the devices part calls the rdev callbacks of rscr_dev_callbacks().
 */
#ifndef RING_SCREENS_RSCR_H
#define RING_SCREENS_RSCR_H

#include <ring_screens/rscr_draw.h>

#ifdef __cplusplus
extern "C" {
#endif

struct rscr_ops {
	/* reads */
	uint8_t (*inbox_count)(void);
	bool (*inbox_get)(uint8_t index, struct rinbox_item *out);
	void (*media_get)(struct ripl_media *out);
	bool (*ams_ready)(void);
	uint8_t (*paired_mask)(void);
	uint8_t (*active)(void);
	bool (*link_up)(void);
	/* actions in the other modules */
	int (*dismiss)(uint32_t uid);
	int (*positive)(uint32_t uid);
	int (*mark_read)(uint32_t uid);
	int (*pair_open)(uint8_t slot);
	void (*pair_cancel)(void);
	int (*dev_use)(uint8_t slot);
	int (*dev_remove)(uint8_t slot);
	void (*control_active)(bool active);
	void (*set_mode)(enum rctl_mode mode);
	/* "Power off" confirmed: called by the screens thread after the core step returned. 0 = carried out; -EBUSY = the glue is busy
	 * (it must not block the screens thread on the glue's lock): the call is repeated 10 ms later. */
	int (*power_off)(void);
	void (*vibration)(bool on);
	/* the clock of the screens (ms); NULL = k_uptime_get(). The tests move it forward without waiting. */
	int64_t (*now_ms)(void);
};

/* Start the screens thread and LVGL. 0 or a negative errno. */
int rscr_start(const struct rscr_ops *ops);

/* One core step (called by the glue after the actions were carried out, under the glue's lock). Returns the value
 * the core's fact screen_on must have from now on. */
bool rscr_glue_after(const struct rc_actions *a, enum rc_event last_event, enum rc_state state, rc_ms_t t);

/* The core fact screen_on as it is now: the glue calls this before every core call, under its own lock
 * (rglue_ops.screen_fact). No copy is stored, so an older value cannot overwrite a newer one. */
bool rscr_lock_fact_now(void);

/* One draw at a time (the test hook that draws a reference text takes it too) */
void rscr_draw_lock(void);
void rscr_draw_unlock(void);
/* Test hook: behave as if rscr_start had failed (rscr_sign_start then returns -ENODEV) */
void rscr_test_force_down(bool down);
/* Test hook: the screens thread calls rscr_sign_start itself; returns what it returned (-EDEADLK) */
int rscr_test_sign_start_from_thread(void);

/* The devices part's callbacks (passkey, paired, window closed, removed) */
void rscr_on_passkey(uint8_t slot, uint32_t passkey);
void rscr_on_paired(uint8_t slot);
void rscr_on_window_closed(void);
void rscr_on_removed(uint8_t slot);
void rscr_on_active_changed(uint8_t slot);
/* Something other modules hold changed (an inbox event, a link): redraw and leave a screen about something gone. */
void rscr_poke(void);

/* Facts of modules that do not exist yet; set by the product when they do, by the scripted scenes now. */
void rscr_set_battery(uint8_t pct, bool charging, bool full, uint16_t to_full_min);
void rscr_set_device_name(uint8_t slot, const char *name);   /* the first 16 characters; NULL clears */

/* R-SIGN, the one path that starts the recording sign: the screens thread draws SCR_RECORDING at 00:00:00 and the caller waits
 * for its answer (one drawing thread). 0 only when the display accepted every write and is not blanked; -ENODEV when
 * rscr_start failed or the display is not ready. The recorder calls it before it switches the microphone supply on (step 6;
 * the core's row "long press, sign not drawn" stays for step 6). */
/* Calling rules:
 *  - allowed under the glue's lock (the recorder runs inside a core step): the screens thread never waits for the glue's lock
 *    while a sign request is pending (power off uses -EBUSY and tries again);
 *  - NOT allowed on the screens thread (returns -EDEADLK at once, no wait);
 *  - NOT allowed with the draw lock held (rscr_draw_lock: a test hook): the thread cannot draw, the call times out;
 *  - the wait is CONFIG_RING_SCREENS_SIGN_WAIT_MS; on a timeout the request is cancelled: it is never drawn later, never
 *    forces SCR_RECORDING, and the next call gets its own answer. */
int rscr_sign_start(rc_ms_t now);
/* Test hook: the screens thread's id */
k_tid_t rscr_thread_id(void);

/* The battery current limit reads ACTIVE (software step 6, design/firmware.md 8.7; the power part calls this once per reading,
 * after it logged the event): the screen goes off for RSCR_ILIM_MS, in RECORDING it shows SCR_REC_DIM for those 10 s at panel
 * level RSCR_LEVEL_LOWEST (85), never dark (rscr_ilim in rscr_logic.h has the exact rules). Allowed under the glue's lock and on
 * any thread but the caller never waits for the draw: the screens thread draws. Does nothing before rscr_start. */
void rscr_ilim_active(void);
/* The factory test T-SCREEN's frame (design/firmware.md 9.3): 0 when accepted; -EPERM when the core state is not FACTORY_TEST or the
 * frame is not one of enum rscr_fac_frame (nothing changes); -ENODEV before rscr_start. The frame is drawn by the screens thread on
 * SCR_FACTORY's display path and dropped when the state is left. */
int rscr_factory_frame(enum rscr_fac_frame frame);

/* Read-outs for tests */
void rscr_snapshot(struct rscr *out);
void rscr_sync(void);   /* returns when the thread has ticked and drawn everything asked so far */
struct rscr_stats {
	uint32_t draws;
	uint32_t draw_errors;
	uint32_t sign_missing;   /* draws in RECORDING that were not a recording picture */
};
void rscr_stats_get(struct rscr_stats *st);

#if IS_ENABLED(CONFIG_RING_SCREENS_REAL)
extern const struct rscr_ops rscr_real_ops;
const struct rdev_callbacks *rscr_dev_callbacks(void);
#endif

#if IS_ENABLED(CONFIG_RING_SCREENS_CAPTURE)
/* Test hook: one text drawn alone (same helpers and fonts as the screens) on a flat background; align 0 left, 1 centre, 2 right,
 * w = 0 for a plain label. Colours 0xRRGGBB. */
void rscr_ref_text(const char *txt, int font_px, uint32_t fg, uint32_t bg, int x, int y, int w, int align, bool wrap);
/* Test hook: the peak use of LVGL's memory pool so far, in bytes */
uint32_t rscr_draw_pool_peak(void);
/* Test hook: read the display back as the 240 x 120 picture (RGB888, RSCR_W * RSCR_H * 3 bytes) */
void rscr_capture_rgb(uint8_t *out);
/* Write the picture as a PNG file (scale 1 = 240 x 120, 4 = 960 x 480). 0 or a negative errno. */
int rscr_capture_png(const char *path, int scale);
#endif

#ifdef __cplusplus
}
#endif

#endif
