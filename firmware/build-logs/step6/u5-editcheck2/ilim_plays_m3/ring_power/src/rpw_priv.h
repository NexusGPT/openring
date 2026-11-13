/*
 * rpw_priv.h: test control of the thin part (not public, not frozen). The unit's tests use it to put the part back
 * to its state before rpw_start(); the product never calls it.
 */
#ifndef RING_POWER_RPW_PRIV_H
#define RING_POWER_RPW_PRIV_H

#ifdef __cplusplus
extern "C" {
#endif

/* Stop the sampling timer, drop queued events, forget the callbacks and every value; the power thread stays and
 * idles. Waits for the thread to finish the event it is on. */
void rpw_priv_reset(void);

/* The sampling period in ms now set (0 = no sampling). */
unsigned int rpw_priv_period_ms(void);

#ifdef __cplusplus
}
#endif

#endif
