/* Helpers of tests/factory (software step 6, unit U8): the stand-ins for the join and the ops table of the factory part.
 * "FW l.N" = line N of design/firmware.md. */
#ifndef FX_COMMON_H
#define FX_COMMON_H

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/ztest.h>

#include <ring_audio/rau.h>
#include <ring_factory/rfa.h>
#include <ring_power/rpw.h>
#include <ring_rhw/rhw.h>
#include <ring_rhw/rhw_sim.h>
#include <ring_rhw/rrec_spec.h>
#include <ring_store/rst.h>
#include <ring_sys/rsy.h>

#include "rfa_logic.h"
#include "rpw_priv.h"

extern struct rfa_ops fx_ops;

/* Reset everything the cases share: the simulated drivers, the finished units, the factory part with fx_ops, the factory
 * flag set (persistent settings, loaded by ring_sys). */
void fx_before(void *f);
void fx_after(void *f);
/* A reset of the ring (the three kept stores stay) and the settings loaded again. */
void fx_next_boot(void);
/* Set the persistent factory flag and load it again through ring_sys. */
void fx_flag(bool on);

/* One request. */
enum rrec_status fx_do(const uint8_t *req, size_t n, bool in_factory_test, uint8_t *out, size_t *out_len,
		       enum rfa_effect *eff);
enum rrec_status fx_do1(uint8_t sub, bool in_factory_test, uint8_t *out, size_t *out_len, enum rfa_effect *eff);

/* ---- the join's stand-ins (the join is not built yet) */
/* rec_mics_on() of the join: the sign, then VDD_MIC on, caller "rec_mics_on" (rrec.h). The answer of the sign is
 * fx_sign_answer (0 = drawn). */
extern int fx_sign_answer;
extern uint32_t fx_sign_calls;
extern uint32_t fx_sign_at_log;     /* rhw_sim_log_count() when the sign was last asked */
extern uint32_t fx_rec_calls;       /* test recordings asked for */
extern uint8_t fx_rec_type;         /* recording_type the stand-in opens with (default 2, a test recording) */
extern uint32_t fx_frames_seen;     /* frames the tap passed to on_block */
int fx_test_recording(uint32_t ms, void (*on_block)(const int16_t *frames, uint32_t n), int64_t *mic_on_ms,
		      int64_t *mic_off_ms);

/* T-SCREEN stand-in: the frames asked for, in order, with the uptime of each */
#define FX_MAX_FRAMES 16
extern uint8_t fx_frame[FX_MAX_FRAMES];
extern int64_t fx_frame_ms[FX_MAX_FRAMES];
extern int64_t fx_frame_ticks[FX_MAX_FRAMES];   /* k_uptime_ticks() of each frame (fix round 1, R6-13) */
extern uint32_t fx_frames;
extern int fx_screen_rc;
extern bool fx_real_screen;          /* test_screen.c: the real screens part draws */
int fx_screen_frame(uint8_t which);

/* T-XTAL stand-in */
extern uint64_t fx_xtal_grtc;
extern uint32_t fx_xtal_sof;
extern int fx_xtal_rc;

/* simulated-log helpers */
int32_t fx_find(uint16_t kind, uint32_t from);
struct rhw_sim_ev fx_ev(uint32_t i);
uint32_t fx_count(uint16_t kind);
/* entries of RHW_EV_PMIC_RAIL for the microphone rail that switch it on */
uint32_t fx_mic_on_events(void);

uint16_t fx_u16(const uint8_t *p);
uint32_t fx_u32(const uint8_t *p);
uint64_t fx_u64(const uint8_t *p);

#endif
