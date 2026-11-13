/* Helpers shared by the suites of tests/sys (software step 6, unit U7). Every expected value in the suites is a literal
 * written from design/firmware.md (the line is cited at each case), never produced by the code under test. */
#ifndef SYS_TEST_COMMON_H
#define SYS_TEST_COMMON_H

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/crc.h>
#include <zephyr/ztest.h>

#include <ring_rhw/rhw.h>
#include <ring_rhw/rhw_sim.h>
#include <ring_sys/rsy.h>

#include "rsy_int.h"
#include "rsy_logic.h"

/* the log records the unit wrote through its hook */
#define T_LOG_MAX 16
struct t_logged {
	uint16_t code;
	uint8_t args[RREC_LOG_ARG_BYTES];
	size_t n;
};
void t_log_reset(void);
int t_nlog(void);
const struct t_logged *t_log_at(int i);
void t_log_fn(uint16_t code, const uint8_t *args, size_t nargs);

/* rhw_sim_reset(), the captured log emptied, then rsy_init(t_log_fn) */
void t_init(void);
/* rhw_sim_reboot() (the unit's reboot hook clears its RAM state and cancels its work), then rhw_sim_reset() */
void t_cleanup(void);
/* a simulated reboot of the ring followed by rsy_init(t_log_fn): the next boot */
void t_next_boot(void);

/* event log helpers */
int32_t ev_find(uint16_t kind, uint32_t from);
uint32_t ev_count(uint16_t kind);
bool ev_get(int32_t i, struct rhw_sim_ev *e);

/* a deterministic byte pattern */
void t_fill(uint8_t *p, size_t n, uint8_t seed);

#endif
