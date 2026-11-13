/* Probe A: every path into STANDBY, with the battery at B5 / B2 / storage full / both, then a real centre long press.
 * Expect: no path ends in RECORDING unless the facts are clean (control). */
#include "probe.h"
enum path { P_BOOT, P_RECOV, P_CHG, P_XFER, P_FAULT, P_MIC, P_CHGERR, P_REC_STOP, P_COUNT };
static const char *pn[] = {"BOOT.init_done","RECOVERY.scan_done","CHARGING.vbus_out","TRANSFER.vbus_out","ERR_STORAGE_FAULT.retry_ok","ERR_MIC_FAULT.5s","ERR_CHARGER.vbus_out","RECORDING.long_stop"};
static const enum rc_state pst[] = {RC_ST_BOOT,RC_ST_RECOVERY,RC_ST_CHARGING,RC_ST_TRANSFER,RC_ST_ERR_STORAGE_FAULT,RC_ST_ERR_MIC_FAULT,RC_ST_ERR_CHARGER,RC_ST_RECORDING};
static int SRC;
static void trigger(int p) {
  switch (p) {
  case P_BOOT: ev(RC_EV_INIT_DONE, 100); break;
  case P_RECOV: ev(RC_EV_SCAN_DONE, 100); break;
  case P_CHG: case P_XFER: case P_CHGERR: ev(RC_EV_VBUS_OUT, 100); break;
  case P_FAULT: ev(RC_EV_STORAGE_RETRY_OK, 100); break;
  case P_MIC: tk(5000); break;
  case P_REC_STOP: if (SRC) { sw(RC_SW_UP, true, 100); sw(RC_SW_DOWN, true, 110); tk(1200); sw(RC_SW_UP, false, 1210); sw(RC_SW_DOWN, false, 1220); } else { sw(RC_SW_CENTRE, true, 100); tk(1100); sw(RC_SW_CENTRE, false, 1200); } tk(1300); break;
  }
}
int main(void) {
  struct { const char *n; enum rc_batt b; bool full; } cond[] = {
    {"clean", RC_BATT_OK, false}, {"B15", RC_BATT_B15, false}, {"B5", RC_BATT_B5, false}, {"B2", RC_BATT_B2, false},
    {"SFULL", RC_BATT_OK, true}, {"B5+SFULL", RC_BATT_B5, true}, {"B2+SFULL", RC_BATT_B2, true}};
  for (int p = 0; p < P_COUNT; p++) for (unsigned k = 0; k < sizeof cond / sizeof cond[0]; k++) for (int src = 0; src < 2; src++) {
    char nm[160];
    SRC = src; init(pst[p], src ? RC_CENTRE_PAIR : RC_CENTRE_SW2);
    F()->batt = cond[k].b; F()->storage_full = cond[k].full;
    F()->vbus = (p == P_CHG || p == P_XFER || p == P_CHGERR);   /* trigger removes it */
    if (p == P_REC_STOP) F()->open_flag = true;
    trigger(p);
    enum rc_state after = S();
    /* now a real long press at 2000..3200 with every state change since cancelled */
    enum rc_switch s1 = RC_SW_CENTRE, s2 = RC_SW_CENTRE;
    if (src) { s1 = RC_SW_UP; s2 = RC_SW_DOWN; }
    sw(s1, true, 2000); if (src) sw(s2, true, 2010); tk(3200);
    enum rc_state fin = S();
    bool clean = (k == 0 || k == 1);
    printf("INFO path=%s cond=%s src=%s after_entry=%s after_long=%s\n", pn[p], cond[k].n, src ? "PAIR" : "SW2", rc_state_name(after), rc_state_name(fin));
    snprintf(nm, sizeof nm, "A %s %s %s: recording %s", pn[p], cond[k].n, src ? "PAIR" : "SW2", clean ? "starts (control)" : "never starts");
    if (clean) { CHECK(nm, fin == RC_ST_RECORDING); }
    else CHECK(nm, fin != RC_ST_RECORDING);
  }
  /* direct facts in STANDBY (no event): a long press must still be refused by the row 12 guard */
  for (int k = 0; k < 4; k++) for (int src = 0; src < 2; src++) {
    char nm[120]; SRC = src; init(RC_ST_STANDBY, src ? RC_CENTRE_PAIR : RC_CENTRE_SW2);
    if (k == 0) F()->batt = RC_BATT_B5; if (k == 1) F()->batt = RC_BATT_B2; if (k == 2) F()->storage_full = true; if (k == 3) F()->open_flag = true;
    if (src) { sw(RC_SW_UP, true, 0); sw(RC_SW_DOWN, true, 10); } else sw(RC_SW_CENTRE, true, 0);
    tk(1100);
    snprintf(nm, sizeof nm, "A direct fact in STANDBY k=%d src=%d: long press does not start a recording (guard of row 12)", k, src);
    CHECK(nm, S() != RC_ST_RECORDING && !has(RC_ACT_OPEN));
  }
  printf("SUMMARY pass=%d fail=%d\n", npass, nfail);
  return nfail != 0;
}
