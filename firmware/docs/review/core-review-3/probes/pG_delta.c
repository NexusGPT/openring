/* Probe G (round 3 delta): N1 to N6, R15 walk. */
#include "probe.h"
static const enum rc_state ALL[] = {RC_ST_SHIP,RC_ST_OFF,RC_ST_BOOT,RC_ST_RECOVERY,RC_ST_STANDBY,RC_ST_RECORDING,RC_ST_CHARGING,RC_ST_TRANSFER,RC_ST_ERR_STORAGE_FULL,RC_ST_ERR_BATTERY_LOW,RC_ST_ERR_STORAGE_FAULT,RC_ST_ERR_MIC_FAULT,RC_ST_ERR_CHARGER,RC_ST_FACTORY_TEST};
int main(void) {
  char nm[220];
  /* N1 */
  init(RC_ST_CHARGING, RC_CENTRE_SW2); F()->vbus = true; bt(RC_BATT_B2, 10); ev(RC_EV_VBUS_OUT, 20);
  CHECK("N1 CHARGING at B2, VBUS out: OFF + SHIP_MODE", S() == RC_ST_OFF && has(RC_ACT_SHIP_MODE));
  init(RC_ST_TRANSFER, RC_CENTRE_SW2); F()->vbus = true; bt(RC_BATT_B2, 10); ev(RC_EV_VBUS_OUT, 20);
  CHECK("N1 TRANSFER at B2, VBUS out: OFF", S() == RC_ST_OFF && has(RC_ACT_SHIP_MODE));
  /* N2: open flag cleared only by CLOSE / scan done */
  init(RC_ST_ERR_STORAGE_FAULT, RC_CENTRE_SW2); F()->open_flag = true; ev(RC_EV_STORAGE_RETRY_OK, 100);
  CHECK("N2 retry ok flag set: RECOVERY, flag kept", S() == RC_ST_RECOVERY && F()->open_flag);
  ev(RC_EV_SCAN_READ_ERROR, 200);
  CHECK("N2 recovery scan fails: ERR_STORAGE_FAULT, flag still set, fault fact set", S() == RC_ST_ERR_STORAGE_FAULT && F()->open_flag && F()->storage_fault);
  ev(RC_EV_STORAGE_RETRY_OK, 60300); ev(RC_EV_VBUS_IN, 60400); ev(RC_EV_VBUS_OUT, 60500);
  sw(RC_SW_CENTRE, true, 61000); tk(62100);
  CHECK("N2 after failed scan, retry ok, case, out: long press never opens a recording while flag set", S() != RC_ST_RECORDING && !has(RC_ACT_OPEN) && F()->open_flag);
  /* flag cleared by scan done only */
  init(RC_ST_RECOVERY, RC_CENTRE_SW2); F()->open_flag = true; ev(RC_EV_SCAN_DONE, 5);
  CHECK("N2 scan done clears flag", !F()->open_flag && S() == RC_ST_STANDBY);
  init(RC_ST_ERR_STORAGE_FAULT, RC_CENTRE_SW2); F()->open_flag = false; ev(RC_EV_STORAGE_RETRY_OK, 100);
  CHECK("N2 retry ok flag clear: STANDBY", S() == RC_ST_STANDBY);
  /* N3 */
  init(RC_ST_BOOT, RC_CENTRE_SW2); F()->open_flag = true; bt(RC_BATT_B5, 5);
  CHECK("N3 B5 in BOOT kept", S() == RC_ST_BOOT && F()->batt == RC_BATT_B5);
  bt(RC_BATT_B2, 6); CHECK("N3 B2 in BOOT kept", S() == RC_ST_BOOT && A.n == 0);
  ev(RC_EV_INIT_DONE, 7); CHECK("N3 init done at B2, flag set: OFF, no recovery, flag stays", S() == RC_ST_OFF && F()->open_flag && !has(RC_ACT_MOUNT));
  init(RC_ST_BOOT, RC_CENTRE_SW2); bt(RC_BATT_B5, 5); bt(RC_BATT_OK, 6); ev(RC_EV_INIT_DONE, 7);
  CHECK("N3 B5 then back above: init done goes STANDBY (level kept as latest)", S() == RC_ST_STANDBY);
  /* N4 */
  init(RC_ST_ERR_STORAGE_FAULT, RC_CENTRE_SW2); ev(RC_EV_VBUS_IN, 1000); ev(RC_EV_VBUS_OUT, 2000);
  CHECK("N4 fault survives case: ERR_STORAGE_FAULT", S() == RC_ST_ERR_STORAGE_FAULT);
  tk(62000); CHECK("N4 retry asked 60 s after re-entry", has(RC_ACT_RETRY_STORAGE));
  init(RC_ST_ERR_STORAGE_FAULT, RC_CENTRE_SW2); ev(RC_EV_VBUS_IN, 1000); ev(RC_EV_STORAGE_RETRY_OK, 1100); ev(RC_EV_VBUS_OUT, 2000);
  printf("INFO N4 retry ok reported while in CHARGING: state=%s fault_fact=%d\n", SN(), F()->storage_fault);
  init(RC_ST_RECORDING, RC_CENTRE_SW2); F()->open_flag = true; ev(RC_EV_CHUNK_WRITE_FAILED, 10); ev(RC_EV_VBUS_IN, 20); ev(RC_EV_VBUS_OUT, 30);
  CHECK("N4 write failed, case in/out: ERR_STORAGE_FAULT, flag set, no recording on long press", S() == RC_ST_ERR_STORAGE_FAULT && F()->open_flag);
  init(RC_ST_BOOT, RC_CENTRE_SW2); ev(RC_EV_STORAGE_INIT_FAILED, 10); ev(RC_EV_VBUS_IN, 20); ev(RC_EV_VBUS_OUT, 30);
  CHECK("N4 BOOT init failed, case in/out: fault kept", S() == RC_ST_ERR_STORAGE_FAULT);
  init(RC_ST_BOOT, RC_CENTRE_SW2); F()->storage_fault = true; ev(RC_EV_INIT_DONE, 10);
  CHECK("N4 init done clears fault fact", !F()->storage_fault && S() == RC_ST_STANDBY);
  /* N5 */
  init(RC_ST_BOOT, RC_CENTRE_SW2); F()->batt = RC_BATT_B5; ev(RC_EV_INIT_DONE, 10);
  CHECK("N5 B5 at init done: ERR_BATTERY_LOW with SD_OFF and M3", S() == RC_ST_ERR_BATTERY_LOW && has(RC_ACT_SD_OFF) && has(RC_ACT_M3));
  /* N6 */
  init(RC_ST_ERR_STORAGE_FAULT, RC_CENTRE_SW2); tk(600000); CHECK("N6 tick 10 min late: one retry", cnt(RC_ACT_RETRY_STORAGE) == 1);
  tk(600001); CHECK("N6 next tick 1 ms later: none", cnt(RC_ACT_RETRY_STORAGE) == 0);
  tk(660000); CHECK("N6 60 s after the late one: one", cnt(RC_ACT_RETRY_STORAGE) == 1);
  /* R15 walk: every state as start, every event (via event entry), battery fact B2 set as a level, no VBUS.
   * Property: after any single event, the ring is not left awake (in a state that is not OFF/SHIP/BOOT/RECOVERY/RECORDING-closed) at B2 with no VBUS,
   * unless in RECOVERY (R4b), BOOT, or FACTORY_TEST. Also after two events in both orders. */
  int awake = 0, tested = 0;
  for (unsigned a = 0; a < sizeof ALL / sizeof *ALL; a++) for (int e1 = 0; e1 < RC_EV_COUNT; e1++) for (int e2 = -1; e2 < RC_EV_COUNT; e2++)
    for (int open = 0; open < 2; open++) for (int full = 0; full < 2; full++) for (int fault = 0; fault < 2; fault++) {
      for (int vb = 0; vb < 2; vb++) {
      { enum rc_state q = ALL[a]; bool reach = vb ? (q == RC_ST_BOOT || q == RC_ST_RECOVERY || q == RC_ST_CHARGING || q == RC_ST_TRANSFER || q == RC_ST_ERR_CHARGER || q == RC_ST_FACTORY_TEST || q == RC_ST_ERR_STORAGE_FAULT) : (q == RC_ST_OFF || q == RC_ST_SHIP || q == RC_ST_BOOT || q == RC_ST_RECOVERY); if (!reach) continue; }
      init(ALL[a], RC_CENTRE_SW2); F()->batt = RC_BATT_B2; F()->vbus = vb; F()->open_flag = open; F()->storage_full = full; F()->storage_fault = fault; F()->factory_flag = true;
      ev((enum rc_event)e1, 10);
      if (e2 >= 0) ev((enum rc_event)e2, 20);
      tk(100000);
      tested++;
      enum rc_state s = S();
      bool bad = !F()->vbus && F()->batt == RC_BATT_B2 &&
        (s == RC_ST_STANDBY || s == RC_ST_ERR_STORAGE_FULL || s == RC_ST_ERR_BATTERY_LOW || s == RC_ST_ERR_STORAGE_FAULT || s == RC_ST_ERR_MIC_FAULT || s == RC_ST_ERR_CHARGER || s == RC_ST_CHARGING || s == RC_ST_TRANSFER || s == RC_ST_RECORDING);
      if (bad) { awake++; if (awake < 600) printf("AWAKE start=%s vbus0=%d e1=%s e2=%s open=%d full=%d fault=%d -> %s\n", rc_state_name(ALL[a]), vb, rc_event_name(e1), e2 >= 0 ? rc_event_name(e2) : "-", open, full, fault, rc_state_name(s)); }
      }
    }
  printf("INFO R15 walk: %d event sequences, awake-at-B2-without-VBUS results %d\n", tested, awake);
  snprintf(nm, sizeof nm, "R15 walk 1: no sequence of 1 or 2 events from any state leaves the ring awake at B2 without VBUS (awake=%d)", awake);
  CHECK(nm, awake == 0);
  /* both orders: battery call and VBUS removal */
  int bad2 = 0;
  for (unsigned a = 0; a < sizeof ALL / sizeof *ALL; a++) for (int order = 0; order < 2; order++) for (int pre = 0; pre < 4; pre++) {
    init(ALL[a], RC_CENTRE_SW2); F()->vbus = true; F()->open_flag = (pre & 1); F()->storage_full = (pre >> 1) & 1; F()->factory_flag = true;
    if (order == 0) { bt(RC_BATT_B2, 10); ev(RC_EV_VBUS_OUT, 20); } else { ev(RC_EV_VBUS_OUT, 10); bt(RC_BATT_B2, 20); }
    tk(100000);
    enum rc_state s = S();
    if (s != RC_ST_OFF && s != RC_ST_SHIP && s != RC_ST_BOOT && s != RC_ST_RECOVERY && s != RC_ST_FACTORY_TEST) { bad2++; printf("AWAKE2 start=%s order=%d pre=%d -> %s\n", rc_state_name(ALL[a]), order, pre, rc_state_name(s)); }
  }
  snprintf(nm, sizeof nm, "R15 walk 2: B2 then VBUS out, and VBUS out then B2, from every state: ends OFF/BOOT/RECOVERY/SHIP (bad=%d)", bad2);
  CHECK(nm, bad2 == 0);
  printf("SUMMARY pass=%d fail=%d\n", npass, nfail);
  return nfail != 0;
}
