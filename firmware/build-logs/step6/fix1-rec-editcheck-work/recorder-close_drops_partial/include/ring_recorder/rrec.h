/*
 * rrec.h: the recorder join (software step 6, unit J builds it; U0 wrote this header, frozen: changes only through the
 * lead). Carries out the core's actions through the other units, runs the boot sequence, and owns the ONE path to the
 * microphone supply (design/firmware.md l.342: rec_mics_on(); "FW l.N" = line N of that file).
 */
#ifndef RING_RECORDER_RREC_H
#define RING_RECORDER_RREC_H

#include <stdbool.h>
#include <stdint.h>

#include <ring_core/rc_types.h>
#include <ring_rhw/rrec_spec.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Start every unit in order and run the boot sequence (step 6 plan, J: reset causes, crash block, charge on with VBUS
 * before mount, mount, the facts, then "init done" or "storage init fails" into the core). Called once by main()
 * after rglue_init(..., RC_ST_BOOT). Blocks for the boot (card init included). */
int rrec_init(void);  /* FW l.133 to l.140 */

/* rglue_ops.action: every action of the core, in order (FW 1.2). Runs inside the glue's step (its lock held): it may
 * block for the card and the sign (rscr_sign_start is allowed under the glue's lock, rscr.h). */
void rrec_action(enum rc_action a, rc_ms_t t);  /* FW l.124 */

/* The ONE function that switches VDD_MIC on (FW l.342, l.457, ruling R18): rscr_sign_start(t) first; only on an
 * answer of 0, rhw_pmic()->rail_set(RHW_RAIL_MIC, true, "rec_mics_on"). Returns the sign's answer (0 = drawn and
 * VDD_MIC on), or the rail's error. Join's thread or the glue's step; blocks up to the sign's wait. No other source
 * file may call rail_set(RHW_RAIL_MIC, true, ...) (full-run stage recorder-one-mic-path). */
int rec_mics_on(rc_ms_t t);

/* VDD_MIC off (FW l.463), "rec_mics_off". After it the screen may leave the recording pictures (FW l.342). */
int rec_mics_off(void);

/* The core's sign hook (unit U1: rc_core_set_sign_hook(core, rrec_sign_hook, ctx)); its type must equal U1's hook
 * type. Called by the core once per long press in STANDBY when the other guards of row 12 hold (decision D1): draws
 * the sign through rscr_sign_start(t); 0 = drawn (row 12: "M1; open", ruling R21), any other value = not drawn
 * (row of FW l.148). The open that follows switches VDD_MIC on through rec_mics_on() for the same press; whether
 * rec_mics_on() draws the sign again or reuses this press's answer is the join's choice, stated in its notes. */
int rrec_sign_hook(void *ctx, rc_ms_t t);

#ifdef __cplusplus
}
#endif

#endif
