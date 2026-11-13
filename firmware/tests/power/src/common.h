/* Shared helpers of the power suites (software step 6, unit U5): a capture of the callbacks, the event log helpers and
 * the set-up that puts the unit and the simulated drivers back to their start before every case. */
#ifndef POWER_TEST_COMMON_H
#define POWER_TEST_COMMON_H

#include <errno.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>

#include <zephyr/kernel.h>
#include <zephyr/ztest.h>

#include <ring_core/rc_types.h>
#include <ring_power/rpw.h>
#include <ring_rhw/rhw.h>
#include <ring_rhw/rhw_sim.h>

#include "rpw_logic.h"
#include "rpw_priv.h"

#define CAP_MAX 40

struct cap_vbus { bool present; uint32_t log_n; bool charger_on; };
struct cap_ilim { bool first; uint16_t mv; uint32_t count; };
struct cap_cerr { uint8_t reason, sensor; };
struct cap_log { uint16_t code; uint8_t args[16]; size_t n; int64_t t_ms; };

struct cap {
	volatile uint32_t n_level;
	uint8_t level[CAP_MAX];
	volatile uint32_t n_vbus;
	struct cap_vbus vbus[CAP_MAX];
	volatile uint32_t n_cerr;
	struct cap_cerr cerr[CAP_MAX];
	volatile uint32_t n_ilim;
	struct cap_ilim ilim[CAP_MAX];
	volatile uint32_t n_log;
	struct cap_log log[CAP_MAX];
};
extern struct cap cap;
extern const struct rpw_cb pw_cbs;

/* before every case: unit and simulated drivers back to the start, the capture cleared */
void pw_before(void *f);
/* rpw_start() with pw_cbs; asserts 0 */
void pw_start(void);
/* One script entry for the simulated power chip's sample (thermistor 25.0 C, die 30.0 C), repeated for the last one. */
void pw_script(const uint16_t *mv, const int32_t *ua, uint32_t n);
void pw_script1(uint16_t mv, int32_t ua);
/* sleep until the uptime t_ms (no-op when past) */
void pw_sleep_until(int64_t t_ms);
/* entry i of the event log (asserts it exists) */
struct rhw_sim_ev pw_ev(uint32_t i);
/* the next entry index of this kind at or after from, or -1 */
int32_t pw_find(uint16_t kind, uint32_t from);
/* index of the n-th (from 0) entry of this kind, or -1 */
int32_t pw_nth(uint16_t kind, uint32_t n);
/* number of captured log records with this code */
uint32_t pw_log_count(uint16_t code);
/* all 14 states in table order (FW l.1.1) */
#define PW_STATES RC_ST_COUNT

#endif
