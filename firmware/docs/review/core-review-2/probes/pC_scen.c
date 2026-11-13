/* Probe C: open flag paths, storage retry, VBUS in each state, the battery call, init-done order. */
#include "probe.h"
static void hold(rc_ms_t t0, rc_ms_t t1) { sw(RC_SW_CENTRE, true, t0); tk(t1); }
static void rel(rc_ms_t t) { sw(RC_SW_CENTRE, false, t); tk(t + 100); }
int main(void) {
  char nm[200];
  /* ---- open flag ---- */
  init(RC_ST_STANDBY, RC_CENTRE_SW2); F()->open_flag = true; hold(0, 1100);
  CHECK("C open flag set in STANDBY: long press goes to RECOVERY, no OPEN action", S() == RC_ST_RECOVERY && !has(RC_ACT_OPEN) && has(RC_ACT_SD_ON) && has(RC_ACT_MOUNT));
  rel(1200); ev(RC_EV_SCAN_DONE, 1500);
  CHECK("C after scan: STANDBY, flag clear", S() == RC_ST_STANDBY && !F()->open_flag && has(RC_ACT_CLEAR_OPEN_FLAG));
  hold(2000, 3100);
  CHECK("C second press records", S() == RC_ST_RECORDING && has(RC_ACT_OPEN) && F()->open_flag);
  rel(3200);
  /* write failure leaves it open; case in and out; STANDBY with flag set */
  ev(RC_EV_CHUNK_WRITE_FAILED, 4000);
  CHECK("C write failure: ERR_STORAGE_FAULT, no CLOSE, flag stays", S() == RC_ST_ERR_STORAGE_FAULT && !has(RC_ACT_CLOSE) && F()->open_flag);
  ev(RC_EV_VBUS_IN, 5000); ev(RC_EV_VBUS_OUT, 6000);
  CHECK("C fault, case in/out: STANDBY with flag set", S() == RC_ST_STANDBY && F()->open_flag);
  hold(7000, 8100);
  CHECK("C that STANDBY long press does not record", S() == RC_ST_RECOVERY && !has(RC_ACT_OPEN));
  rel(8200);
  /* retry-ok with flag: RUN_RECOVERY */
  init(RC_ST_ERR_STORAGE_FAULT, RC_CENTRE_SW2); F()->open_flag = true; ev(RC_EV_STORAGE_RETRY_OK, 100);
  CHECK("C retry ok with flag: STANDBY, RUN_RECOVERY, flag cleared in facts", S() == RC_ST_STANDBY && has(RC_ACT_RUN_RECOVERY) && !F()->open_flag);
  /* BOOT with flag in every battery level, VBUS absent */
  for (int b = 0; b <= 3; b++) {
    init(RC_ST_BOOT, RC_CENTRE_SW2); F()->open_flag = true; F()->batt = b; ev(RC_EV_INIT_DONE, 10);
    enum rc_state e1 = S();
    int bad_ship = has(RC_ACT_SHIP_MODE);
    enum rc_state want = (b == 3) ? RC_ST_OFF : RC_ST_RECOVERY;
    snprintf(nm, sizeof nm, "C R4b init done flag set batt=%d: %s (got %s)", b, rc_state_name(want), rc_state_name(e1));
    CHECK(nm, e1 == want && (b == 3) == bad_ship);
    if (b == 2) { ev(RC_EV_SCAN_DONE, 20); CHECK("C R4b flag set B5: end of scan -> ERR_BATTERY_LOW with M3", S() == RC_ST_ERR_BATTERY_LOW && has(RC_ACT_M3) && has(RC_ACT_WRITE_CLOSE_RECOVERED)); }
  }
  /* with VBUS */
  init(RC_ST_BOOT, RC_CENTRE_SW2); F()->open_flag = true; ev(RC_EV_VBUS_IN, 5); F()->batt = 2; ev(RC_EV_INIT_DONE, 10);
  CHECK("C R4 flag set + VBUS: RECOVERY first", S() == RC_ST_RECOVERY); ev(RC_EV_SCAN_DONE, 20);
  CHECK("C R4 then CHARGING, charge on", S() == RC_ST_CHARGING && has(RC_ACT_CHARGE_ON));
  /* B5 event in BOOT before init done with flag set (R4b bypass?) */
  init(RC_ST_BOOT, RC_CENTRE_SW2); F()->open_flag = true; bt(RC_BATT_B5, 5);
  printf("INFO battery B5 reported in BOOT before init done, flag set: state=%s flag=%d\n", SN(), F()->open_flag);
  /* ---- retry ---- */
  init(RC_ST_BOOT, RC_CENTRE_SW2); ev(RC_EV_STORAGE_INIT_FAILED, 600);
  CHECK("C retry: BOOT init failed -> ERR_STORAGE_FAULT", S() == RC_ST_ERR_STORAGE_FAULT);
  tk(60599); CHECK("C retry: nothing at 59,999 ms after entry", !has(RC_ACT_RETRY_STORAGE));
  tk(60600); CHECK("C retry: RETRY_STORAGE at 60,000 ms after entry", cnt(RC_ACT_RETRY_STORAGE) == 1);
  ev(RC_EV_STORAGE_RETRY_FAILED, 60700); CHECK("C retry failed: stays, no action", S() == RC_ST_ERR_STORAGE_FAULT && A.n == 0);
  tk(120599); CHECK("C retry: nothing before 120,600", !has(RC_ACT_RETRY_STORAGE));
  tk(120600); CHECK("C retry: second RETRY_STORAGE", cnt(RC_ACT_RETRY_STORAGE) == 1);
  ev(RC_EV_STORAGE_RETRY_FAILED, 120700);
  tk(180600); CHECK("C retry: third RETRY_STORAGE", cnt(RC_ACT_RETRY_STORAGE) == 1);
  ev(RC_EV_STORAGE_RETRY_OK, 180700); CHECK("C retry ok: STANDBY", S() == RC_ST_STANDBY);
  tk(900000); CHECK("C no retry after leaving the fault state", !has(RC_ACT_RETRY_STORAGE) && rc_core_next_tick(&C) == RC_NO_TICK);
  ev(RC_EV_STORAGE_RETRY_OK, 900001); CHECK("C RETRY_OK outside fault state ignored", S() == RC_ST_STANDBY && A.n == 0);
  /* re-entry restarts the 60 s */
  init(RC_ST_ERR_STORAGE_FAULT, RC_CENTRE_SW2); ev(RC_EV_VBUS_IN, 1000); ev(RC_EV_VBUS_OUT, 2000);
  CHECK("C fault -> case -> out lands in STANDBY (storage still faulty, no retry ever asked)", S() == RC_ST_STANDBY && rc_core_next_tick(&C) == RC_NO_TICK);
  /* far-ahead tick */
  init(RC_ST_ERR_STORAGE_FAULT, RC_CENTRE_SW2); tk(10 * 60000 + 5);
  printf("INFO tick 10 min ahead in fault state: RETRY_STORAGE count=%d next_tick=%lld\n", cnt(RC_ACT_RETRY_STORAGE), (long long)rc_core_next_tick(&C));
  /* ---- VBUS appearing in each state ---- */
  for (int s = 0; s < RC_ST_COUNT; s++) {
    init((enum rc_state)s, RC_CENTRE_SW2); F()->open_flag = (s == RC_ST_RECORDING);
    enum rc_state want;
    switch (s) {
    case RC_ST_SHIP: case RC_ST_OFF: want = RC_ST_BOOT; break;
    case RC_ST_STANDBY: case RC_ST_RECORDING: case RC_ST_ERR_STORAGE_FULL: case RC_ST_ERR_BATTERY_LOW: case RC_ST_ERR_STORAGE_FAULT: case RC_ST_ERR_MIC_FAULT: want = RC_ST_CHARGING; break;
    default: want = (enum rc_state)s;
    }
    ev(RC_EV_VBUS_IN, 50);
    snprintf(nm, sizeof nm, "C VBUS appears in %s: -> %s, exactly one CHARGE_ON, vbus fact", rc_state_name((enum rc_state)s), rc_state_name(want));
    CHECK(nm, S() == want && cnt(RC_ACT_CHARGE_ON) == 1 && F()->vbus);
    if (s == RC_ST_RECORDING) CHECK("C VBUS in RECORDING: CLOSE before M2 before CHARGE_ON", A.n == 3 && A.a[0] == RC_ACT_CLOSE && A.a[1] == RC_ACT_M2 && A.a[2] == RC_ACT_CHARGE_ON && !rc_core_mic_rail(&C));
  }
  /* ---- battery call ---- */
  init(RC_ST_RECORDING, RC_CENTRE_SW2); bt(RC_BATT_B15, 10); CHECK("C batt B15 in RECORDING: M3, stays", S() == RC_ST_RECORDING && has(RC_ACT_M3));
  bt(RC_BATT_B15, 11); CHECK("C same level twice: no event", A.n == 0);
  bt(RC_BATT_B5, 12); CHECK("C batt B5 in RECORDING: CLOSE, M3, ERR_BATTERY_LOW", S() == RC_ST_ERR_BATTERY_LOW && has(RC_ACT_CLOSE));
  bt(RC_BATT_OK, 13); CHECK("C battery up: fact only", S() == RC_ST_ERR_BATTERY_LOW && A.n == 0 && F()->batt == RC_BATT_OK);
  bt((enum rc_batt)7, 14); CHECK("C invalid level ignored", F()->batt == RC_BATT_OK && A.n == 0);
  init(RC_ST_RECORDING, RC_CENTRE_SW2); bt(RC_BATT_B2, 10); CHECK("C batt B2 in RECORDING: CLOSE, SHIP_MODE, OFF", S() == RC_ST_OFF && has(RC_ACT_CLOSE) && has(RC_ACT_SHIP_MODE));
  init(RC_ST_CHARGING, RC_CENTRE_SW2); F()->vbus = true; bt(RC_BATT_B2, 10); ev(RC_EV_VBUS_OUT, 20);
  printf("INFO CHARGING, battery to B2, VBUS out: state=%s ship_mode=%d\n", SN(), has(RC_ACT_SHIP_MODE));
  bt(RC_BATT_B2, 30); printf("INFO same level reported again: state=%s (no event: level unchanged)\n", SN());
  bt(RC_BATT_B5, 40); printf("INFO B2 -> B5 reported: state=%s\n", SN());
  bt(RC_BATT_B2, 50); printf("INFO B5 -> B2 reported again: state=%s ship=%d\n", SN(), has(RC_ACT_SHIP_MODE));
  /* storage full fact */
  init(RC_ST_RECORDING, RC_CENTRE_SW2); ev(RC_EV_STORAGE_SFULL, 10);
  CHECK("C SFULL in RECORDING: CLOSE, M3, ERR_STORAGE_FULL", S() == RC_ST_ERR_STORAGE_FULL && has(RC_ACT_CLOSE) && F()->storage_full);
  printf("SUMMARY pass=%d fail=%d\n", npass, nfail);
  return nfail != 0;
}
