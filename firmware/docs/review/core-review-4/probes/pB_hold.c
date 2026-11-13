/* Probe B: a centre hold that begins in a state, the state changes at tc, the hold goes on to 3000 ms. Expect never RECORDING
 * for a hold begun outside STANDBY; then release and press again starts a recording (control). Both centre sources,
 * and the state change delivered with and without a tick before it. */
#include "probe.h"
static int SRC;
static void down(rc_ms_t t) { if (SRC) { sw(RC_SW_UP, true, t); sw(RC_SW_DOWN, true, t + 10); } else sw(RC_SW_CENTRE, true, t); }
static void up(rc_ms_t t) { if (SRC) { sw(RC_SW_UP, false, t); sw(RC_SW_DOWN, false, t + 1); } else sw(RC_SW_CENTRE, false, t); }
struct c { const char *n; enum rc_state st; int leave; /* 0 vbus_out 1 retry_ok 2 timer 3 scan_done 4 init_done */ bool vbus; };
static void leave(int how, rc_ms_t t, bool via_tick) {
  if (via_tick) tk(t);
  switch (how) {
  case 0: ev(RC_EV_VBUS_OUT, t); break;
  case 1: ev(RC_EV_STORAGE_RETRY_OK, t); break;
  case 2: tk(t); break;
  case 3: ev(RC_EV_SCAN_DONE, t); break;
  case 4: ev(RC_EV_INIT_DONE, t); break;
  }
}
int main(void) {
  struct c cs[] = {
    {"CHARGING", RC_ST_CHARGING, 0, true}, {"TRANSFER", RC_ST_TRANSFER, 0, true}, {"ERR_CHARGER", RC_ST_ERR_CHARGER, 0, true},
    {"ERR_STORAGE_FAULT", RC_ST_ERR_STORAGE_FAULT, 1, false}, {"ERR_MIC_FAULT", RC_ST_ERR_MIC_FAULT, 2, false},
    {"RECOVERY", RC_ST_RECOVERY, 3, false}, {"BOOT", RC_ST_BOOT, 4, false}};
  rc_ms_t leave_at[] = {100, 499, 500, 900, 999, 1000, 1001, 1500, 2900};
  for (unsigned i = 0; i < sizeof cs / sizeof cs[0]; i++) for (int src = 0; src < 2; src++) for (int via = 0; via < 2; via++)
    for (unsigned j = 0; j < sizeof leave_at / sizeof leave_at[0]; j++) {
      char nm[200]; SRC = src; init(cs[i].st, src ? RC_CENTRE_PAIR : RC_CENTRE_SW2);
      F()->vbus = cs[i].vbus;
      rc_ms_t t0 = 0;
      if (cs[i].st == RC_ST_ERR_MIC_FAULT) { rc_core_init(&C, src, cs[i].st, 0); }   /* 5 s timer from 0 */
      rc_ms_t base = (cs[i].leave == 2) ? 4000 : 0;      /* ERR_MIC_FAULT: hold begins at 4000, state leaves at 5000 */
      t0 = base;
      down(t0);
      rc_ms_t tl = (cs[i].leave == 2) ? 5000 : t0 + leave_at[j];
      if (cs[i].leave == 2 && j > 0) continue;
      leave(cs[i].leave, tl, via);
      enum rc_state mid = S();
      tk(t0 + 3000 + 2000);               /* hold goes on long after 1000 ms from its beginning, and after the state change */
      enum rc_state fin = S();
      snprintf(nm, sizeof nm, "B hold begun in %s src=%s leave_at=%lld via_tick=%d: mid=%s fin=%s never RECORDING", cs[i].n, src ? "PAIR" : "SW2", (long long)(tl - t0), via, rc_state_name(mid), rc_state_name(fin));
      CHECK(nm, fin != RC_ST_RECORDING && mid != RC_ST_RECORDING);
      /* release, press again: a deliberate new hold in STANDBY starts */
      up(t0 + 5100);
      if (fin == RC_ST_STANDBY) {
        down(t0 + 6000); tk(t0 + 7100);
        snprintf(nm, sizeof nm, "B control after release, %s src=%s leave_at=%lld via=%d: new hold starts recording", cs[i].n, src ? "PAIR" : "SW2", (long long)(tl - t0), via);
        CHECK(nm, S() == RC_ST_RECORDING);
      }
    }
  /* the hold that begins in STANDBY and a state-neutral event (B15, STORAGE_S30 no row, VBUS none) still starts */
  init(RC_ST_STANDBY, RC_CENTRE_SW2); sw(RC_SW_CENTRE, true, 0); bt(RC_BATT_B15, 300); tk(1100);
  CHECK("B hold in STANDBY survives a B15 crossing (no change of state)", S() == RC_ST_RECORDING);
  /* hold begun in STANDBY, state changes to ERR_BATTERY_LOW at 600 and the ring never recording */
  init(RC_ST_STANDBY, RC_CENTRE_SW2); sw(RC_SW_CENTRE, true, 0); bt(RC_BATT_B5, 600); tk(1100);
  CHECK("B hold begun in STANDBY, B5 at 600 ms: ERR_BATTERY_LOW, no recording", S() == RC_ST_ERR_BATTERY_LOW);
  /* PAIR: first switch closes in CHARGING, VBUS out at 10, opposite closes at 30: the pair forms in STANDBY */
  init(RC_ST_CHARGING, RC_CENTRE_PAIR); F()->vbus = true; sw(RC_SW_UP, true, 0); ev(RC_EV_VBUS_OUT, 10); sw(RC_SW_DOWN, true, 30); tk(1100);
  printf("INFO PAIR press half closed in CHARGING, completes in STANDBY at 30 ms: state=%s\n", SN());
  printf("SUMMARY pass=%d fail=%d\n", npass, nfail);
  return nfail != 0;
}
