/* D1 paths and shortest sequences, round 4 */
#include "probe.h"
int main(void) {
  /* path 1: BOOT in the case at B2, storage init fails, VBUS removed */
  init(RC_ST_BOOT, RC_CENTRE_SW2); F()->vbus = true; bt(RC_BATT_B2, 1); ev(RC_EV_STORAGE_INIT_FAILED, 10);
  CHECK("D1 path 1 entered ERR_STORAGE_FAULT under VBUS at B2", S() == RC_ST_ERR_STORAGE_FAULT);
  ev(RC_EV_VBUS_OUT, 20);
  CHECK("D1 path 1 VBUS removed: OFF with SHIP_MODE", S() == RC_ST_OFF && has(RC_ACT_SHIP_MODE));
  /* path 2: RECOVERY read error under VBUS at B2, VBUS removed */
  init(RC_ST_RECOVERY, RC_CENTRE_SW2); F()->vbus = true; F()->open_flag = true; bt(RC_BATT_B2, 1); ev(RC_EV_SCAN_READ_ERROR, 10);
  CHECK("D1 path 2 entered ERR_STORAGE_FAULT under VBUS at B2", S() == RC_ST_ERR_STORAGE_FAULT);
  ev(RC_EV_VBUS_OUT, 20);
  CHECK("D1 path 2 VBUS removed: OFF with SHIP_MODE, flag stays set", S() == RC_ST_OFF && has(RC_ACT_SHIP_MODE) && F()->open_flag);
  /* D2 */
  init(RC_ST_STANDBY, RC_CENTRE_SW2); ev(RC_EV_STORAGE_FAULT_SET, 5);
  CHECK("D2 STORAGE_FAULT_SET from outside refused", S() == RC_ST_STANDBY && A.n == 0 && !F()->storage_fault);
  /* B5 with VBUS out keeps state row; TRANSFER at B2 aborts command then OFF */
  init(RC_ST_TRANSFER, RC_CENTRE_SW2); F()->vbus = true; bt(RC_BATT_B2, 1); ev(RC_EV_VBUS_OUT, 10);
  CHECK("R16 TRANSFER at B2: ABORT_COMMAND, SD_OFF, then OFF", S() == RC_ST_OFF && has(RC_ACT_ABORT_COMMAND) && has(RC_ACT_SHIP_MODE));
  init(RC_ST_ERR_STORAGE_FAULT, RC_CENTRE_SW2); F()->vbus = true; bt(RC_BATT_B5, 1); ev(RC_EV_VBUS_OUT, 10);
  CHECK("R16 at B5 (not B2): VBUS out leaves ERR_STORAGE_FAULT awake as before", S() == RC_ST_ERR_STORAGE_FAULT);
  init(RC_ST_RECORDING, RC_CENTRE_SW2); F()->open_flag = true; F()->vbus = false; bt(RC_BATT_B2, 1);
  CHECK("B2 in RECORDING: close, OFF", S() == RC_ST_OFF && has(RC_ACT_CLOSE));
  init(RC_ST_FACTORY_TEST, RC_CENTRE_SW2); F()->vbus = true; bt(RC_BATT_B2, 1); ev(RC_EV_VBUS_OUT, 10);
  CHECK("R16 FACTORY_TEST at B2: BOOT (reboot) then init done gives OFF", S() == RC_ST_BOOT && has(RC_ACT_REBOOT));
  ev(RC_EV_INIT_DONE, 20); CHECK("... init done at B2 no VBUS: OFF", S() == RC_ST_OFF);
  init(RC_ST_RECOVERY, RC_CENTRE_SW2); F()->vbus = true; F()->open_flag = true; bt(RC_BATT_B2, 1); ev(RC_EV_VBUS_OUT, 10);
  printf("INFO RECOVERY at B2, VBUS out: state=%s (stays until the scan ends)\n", SN());
  ev(RC_EV_SCAN_DONE, 20); CHECK("RECOVERY scan done after VBUS out at B2: OFF", S() == RC_ST_OFF && has(RC_ACT_WRITE_CLOSE_RECOVERED));
  printf("SUMMARY pass=%d fail=%d\n", npass, nfail);
  return nfail != 0;
}
