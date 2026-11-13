/* Test helpers shared by the core suites (Zephyr ztest and the host shim). */
#ifndef RING_CORE_TEST_TH_H
#define RING_CORE_TEST_TH_H

#include <stddef.h>
#include <zephyr/ztest.h>
#include "ring_core/rc_core.h"

#define TH_T0 10000  /* start time of every test, ms */

/* Values of the specification, written here and not taken from the module, so a
 * wrong constant in the module fails the tests. design/firmware.md (F6) lines. */
#define SPEC_LONG_MS            1000   /* line 220 */
#define SPEC_DOUBLE_WINDOW_MS   400    /* line 222 */
#define SPEC_RELEASE_HOLDOFF_MS 30     /* line 224 */
#define SPEC_MIC_FAULT_MS       5000   /* line 187 "5 s elapsed" */
#define SPEC_STORAGE_RETRY_MS   60000  /* F6 line 185, now line 188 "60 s elapsed", every 60 s (R3) */

extern struct rc_core core;
extern struct rc_actions out;    /* actions of the step under test */
extern struct rc_actions rest;   /* actions of the steps after it */
extern rc_ms_t th_now;

void th_start(enum rc_state st);
void th_start_src(enum rc_state st, enum rc_centre_source src);
void th_event(enum rc_event ev);                 /* system event at th_now, into out */
void th_batt(enum rc_batt level);                /* battery level at th_now, into out (C1) */
void th_tick_to(rc_ms_t t, struct rc_actions *o); /* tick every next deadline up to t */
void th_sw(enum rc_switch sw, bool pressed, rc_ms_t t, struct rc_actions *o);
/* Real switch input: long press of the centre (SW2). out = actions of the 1,000 ms mark only;
 * rest = actions after it (release included). */
void th_long(void);
/* Short press of 100 ms; out = actions when the window closes. */
void th_short(void);
/* Two 100 ms presses 100 ms apart; out = actions of the second release. */
void th_double(void);
void th_expect(const struct rc_actions *o, const uint8_t *exp, size_t n);
bool th_has(const struct rc_actions *o, enum rc_action a);

#define TH_EXPECT(...) do { static const uint8_t e_[] = {0, __VA_ARGS__}; \
	th_expect(&out, e_ + 1, sizeof(e_) - 1); } while (0)

/* gesture-only helpers */
extern struct rc_gesture gg;
extern struct rc_gev_list gl;
void tg_start(enum rc_centre_source src);
void tg_in(enum rc_switch sw, bool pressed, rc_ms_t t);
void tg_tick(rc_ms_t t);
int tg_count(enum rc_gev_type type);
const struct rc_gev *tg_find(enum rc_gev_type type, int nth);
/* Like tg_find, but a missing event fails the test by its name (ruling C4), never a crash. */
const struct rc_gev *tg_get(enum rc_gev_type type, int nth);
/* A centre press of dur ms starting (CENTRE_DOWN) at t0 for either source; PAIR uses up and down. */
void tg_centre(rc_ms_t t0, rc_ms_t dur);

#endif
