/* Probe D: random fuzz against the owner's rule. Oracle (written here, not copied from the module):
 *  - RECORDING is entered only by rc_core_input/rc_core_tick, never by rc_core_event/rc_core_battery;
 *  - at entry: some switch has been closed without an all-open gap of 30 ms or more for >= 1000 ms (minus the 40 ms of the pair window),
 *    no change of state happened since that contact began (+40 ms), the facts were: open flag clear, battery below B5, storage not full, previous state STANDBY;
 *  - RECORDING is left only by: a LONG hold under the same rule (through input/tick), or a system event of {VBUS_IN, STORAGE_SFULL, CHUNK_WRITE_FAILED, MIC_NO_BLOCK, POWER_LOSS}
 *    or a battery downward crossing to B5/B2 through rc_core_battery.
 * Usage: pD <seed0> <nseeds> <steps> */
#include "probe.h"
static uint64_t rs;
static unsigned rnd(unsigned n) { rs = rs * 6364136223846793005ULL + 1442695040888963407ULL; return (unsigned)((rs >> 33) % n); }
static int viol;
static void v(const char *m, long seed, int step) { viol++; if (viol < 40) printf("VIOLATION seed=%ld step=%d: %s\n", seed, step, m); }
int main(int argc, char **argv) {
  long s0 = atol(argv[1]), ns = atol(argv[2]); int steps = atoi(argv[3]);
  long entries = 0, exits_long = 0, exits_sys = 0;
  static const unsigned gaps[] = {1, 5, 20, 29, 31, 45, 100, 300, 499, 500, 501, 999, 1000, 1001, 1500, 4999, 5001, 60000};
  for (long seed = s0; seed < s0 + ns; seed++) {
    rs = (uint64_t)seed * 2654435761u + 12345;
    int pair = rnd(2), dirs = rnd(2);
    enum rc_state st0 = (enum rc_state)rnd(RC_ST_COUNT);
    init(st0, pair ? RC_CENTRE_PAIR : RC_CENTRE_SW2);
    F()->vbus = (st0 == RC_ST_CHARGING || st0 == RC_ST_TRANSFER || st0 == RC_ST_ERR_CHARGER || st0 == RC_ST_FACTORY_TEST);
    F()->open_flag = rnd(3) == 0 && st0 != RC_ST_RECORDING; F()->factory_flag = rnd(2);
    if (st0 == RC_ST_RECORDING) F()->open_flag = true;
    rc_ms_t now = 0; bool held[RC_SW_COUNT] = {0};
    rc_ms_t contact_start = -1, all_open_since = 0, last_change = 0; bool anydown = false;
    enum rc_state prev = S();
    for (int step = 0; step < steps; step++) {
      rc_ms_t t = now + gaps[rnd(sizeof gaps / sizeof gaps[0])];
      /* run the module's own timers up to t as the scheduler would */
      int guard = 0;
      while (guard++ < 200 && rc_core_next_tick(&C) <= t) {
        rc_ms_t nt = rc_core_next_tick(&C); bool fa = F()->open_flag, fb = F()->batt, fs = F()->storage_full; (void)fa;(void)fb;(void)fs;
        struct rc_facts snap = *F(); enum rc_state before = S();
        tk(nt);
        if (S() != before) { last_change = nt; }
        if (before != RC_ST_RECORDING && S() == RC_ST_RECORDING) {
          entries++;
          if (before != RC_ST_STANDBY) v("entered RECORDING from non STANDBY (tick)", seed, step);
          if (snap.open_flag || snap.batt >= RC_BATT_B5 || snap.storage_full) v("entered with open flag/B5/SFULL", seed, step);
          if (!anydown || nt - contact_start < 1000 - 40) v("entered without a 1000 ms contact (tick)", seed, step);
          if (contact_start + 40 < last_change && last_change != nt) v("contact began before a state change (tick)", seed, step);
        }
        if (before == RC_ST_RECORDING && S() != RC_ST_RECORDING) {
          exits_long++;
          if (!anydown || nt - contact_start < 1000 - 40) v("left RECORDING by tick without a 1000 ms contact", seed, step);
        }
        if (S() == before) { /* ok */ }
        prev = S();
      }
      now = t;
      unsigned a = rnd(100);
      struct rc_facts snap = *F(); enum rc_state before = S();
      bool via_input = false;
      if (a < 45) {
        enum rc_switch sw_ = (enum rc_switch)rnd(RC_SW_COUNT);
        if (!dirs && sw_ != RC_SW_CENTRE && !pair) sw_ = RC_SW_CENTRE;
        if (!dirs && pair && sw_ == RC_SW_CENTRE) sw_ = RC_SW_UP;
        bool p = !held[sw_]; held[sw_] = p;
        /* all-open bookkeeping of my own model (SW2 BTN_REC counts only in case SW2) */
        bool rel_sw = pair ? (sw_ != RC_SW_CENTRE) : true;
        bool before_any = anydown; (void)before_any;
        int n = 0; for (int i = 0; i < RC_SW_COUNT; i++) if (held[i] && (pair ? i != RC_SW_CENTRE : true)) n++;
        if (rel_sw) {
          if (p && !anydown) { if (t - all_open_since >= 30 || contact_start < 0) contact_start = t; anydown = true; }
          if (n == 0 && anydown) { anydown = false; all_open_since = t; }
        }
        via_input = true; sw(sw_, p, t);
        /* the 30 ms hold-off: a re-press inside 30 ms of an all-open is the same contact */
        if (rel_sw && p && n == 1 && t - all_open_since < 30) { /* contact continues: keep start */ }
      } else if (a < 60) { tk(t); via_input = true; }
      else if (a < 85) {
        enum rc_event e = (enum rc_event)rnd(RC_EV_COUNT + 2);
        if (e == RC_EV_VBUS_IN) F()->vbus = true;
        if (e == RC_EV_VBUS_OUT) F()->vbus = false;
        ev(e, t);
        if (before != RC_ST_RECORDING && S() == RC_ST_RECORDING) v("entered RECORDING from rc_core_event", seed, step);
        if (before == RC_ST_RECORDING && S() != RC_ST_RECORDING) {
          exits_sys++;
          if (!(e == RC_EV_VBUS_IN || e == RC_EV_STORAGE_SFULL || e == RC_EV_CHUNK_WRITE_FAILED || e == RC_EV_MIC_NO_BLOCK || e == RC_EV_POWER_LOSS || (e == RC_EV_VBUS_OUT && F()->batt == RC_BATT_B2))) v("left RECORDING by an event outside the list", seed, step);
        }
      } else if (a < 93) {
        bt((enum rc_batt)rnd(4), t);
        if (before != RC_ST_RECORDING && S() == RC_ST_RECORDING) v("entered RECORDING from battery call", seed, step);
        if (before == RC_ST_RECORDING && S() != RC_ST_RECORDING && F()->batt < RC_BATT_B5) v("left RECORDING by battery above B5", seed, step);
      } else if (a < 96) { unsigned k = rnd(3); if (k == 0) F()->storage_full = rnd(2); else if (k == 1 && S() != RC_ST_RECORDING) F()->open_flag = rnd(2); else F()->batt = (uint8_t)rnd(4); }
      else { F()->screen_on = rnd(2); F()->vibration_on = rnd(2); }
      if (S() != before) last_change = t;
      if (via_input) {
        if (before != RC_ST_RECORDING && S() == RC_ST_RECORDING) {
          entries++;
          if (before != RC_ST_STANDBY) v("entered RECORDING from non STANDBY (input)", seed, step);
          if (snap.open_flag || snap.batt >= RC_BATT_B5 || snap.storage_full || snap.storage_fault) v("entered with open flag/B5/SFULL/fault (input)", seed, step);
          if (!anydown || t - contact_start < 1000 - 40) v("entered without 1000 ms contact (input)", seed, step);
          if (contact_start + 40 < last_change && last_change != t) v("contact began before a state change", seed, step);
          if (!has(RC_ACT_OPEN) || !has(RC_ACT_M1)) v("entry without OPEN, M1", seed, step);
        }
        if (before == RC_ST_RECORDING && S() != RC_ST_RECORDING) {
          exits_long++;
          if (!anydown || t - contact_start < 1000 - 40) v("left RECORDING by input without 1000 ms contact", seed, step);
        }
      }
     
      (void)prev;
    }
  }
  printf("SUMMARY seeds=%ld steps=%d entries=%ld exits_by_input=%ld exits_by_system=%ld violations=%d\n", ns, steps, entries, exits_long, exits_sys, viol);
  return viol != 0;
}
