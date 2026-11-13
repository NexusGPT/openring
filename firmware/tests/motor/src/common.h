/* Helpers shared by the suites of tests/motor (software step 6, unit U6). Every expected value in the suites is a
 * literal typed from design/firmware.md (the line is cited at each case), never produced by the code under test. */
#ifndef MOTOR_TEST_COMMON_H
#define MOTOR_TEST_COMMON_H

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/ztest.h>

#include <ring_motor/rmo.h>
#include <ring_rhw/rhw.h>
#include <ring_rhw/rhw_sim.h>

#include "rmo_logic.h"

#define T_MAX_EV 16

struct t_edge {
	int64_t t_us;       /* the simulated pin's event time */
	bool high;
};

/* what the callbacks received since t_reset() */
struct t_cb_edge {
	bool high;
	uint64_t cycles;
};
struct t_cb_charge {
	uint32_t uas;
	uint64_t cycles;    /* the clock when the charge callback ran */
};
struct t_cb_started {
	uint8_t pattern;
	int64_t t_ms;
};

/* Stop the player, reset the simulated drivers, init the player with the recording callbacks, empty the log. */
void t_reset(void);
/* MOTOR pin events of the simulated driver log, in order; returns how many (at most T_MAX_EV). */
int t_pin_events(struct t_edge *out);
int t_n_edge(void);
const struct t_cb_edge *t_edge(int i);
int t_n_charge(void);
const struct t_cb_charge *t_charge(int i);
int t_n_started(void);
const struct t_cb_started *t_started(int i);
/* kernel uptime in us now (the log's time base) */
int64_t t_now_us(void);
/* sleep in simulated time */
void t_ms(uint32_t ms);
/* Check the pin events against expected edge times in ms from `base_us`: events[0] is high, then alternating;
 * `n` edges; each time within [exp*1000 - 1, exp*1000 + 1000) us of base. */
void t_check_edges(const struct t_edge *ev, int n_ev, int64_t base_us, const uint32_t *exp_ms, int n);

#endif
