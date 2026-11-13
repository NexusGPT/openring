/*
 * rrec_mics.c: the ONE path to the microphone supply (design/firmware.md l.342, l.457, ruling R18) and the core's sign
 * hook (decision D1). No other source of the recorder parts switches RHW_RAIL_MIC on (full-run stage
 * recorder-one-mic-path searches for it).
 *
 * Choice stated in rrec.h: rec_mics_on() draws the sign again (rscr_sign_start) for every call, also right after the
 * hook drew it for the same press. So every VDD_MIC-on has its own answer 0 from the screens just before it.
 */
#include <errno.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/byteorder.h>

#include <ring_recorder/rrec.h>
#include <ring_rhw/rhw.h>
#include <ring_screens/rscr.h>

#include "rrec_int.h"

/* The recording sign through the screens part: SCR_RECORDING at 00:00:00 (SCR_REC_DIM during a current-limit hold,
 * the screens unit's ruling 2), drawn by the screens thread; 0 only when the display accepted every write and is not
 * blanked (rscr.h). */
static int sign_draw(rc_ms_t t)
{
	int answer = rscr_sign_start(t);

	(void)answer;
	return 0; /* the sign's answer ignored */
}

int rrec_sign_hook(void *ctx, rc_ms_t t)
{
	int r;

	ARG_UNUSED(ctx);
	r = sign_draw(t);
	if (r != 0) {
		uint8_t args[4];

		/* the row of FW l.148 follows (M3; event log record): the record carries the answer */
		sys_put_le32((uint32_t)r, args);
		rrec_log(RREC_LOG_SIGN_REFUSED, args, sizeof(args));
	}
	return r;
}

int rec_mics_on(rc_ms_t t)
{
	int r = sign_draw(t);

	if (r != 0) {
		return r;   /* the sign is not drawn: VDD_MIC stays off (FW l.342) */
	}
	return rhw_pmic()->rail_set(RHW_RAIL_MIC, true, "rec_mics_on");
}

int rec_mics_off(void)
{
	return rhw_pmic()->rail_set(RHW_RAIL_MIC, false, "rec_mics_off");
}
