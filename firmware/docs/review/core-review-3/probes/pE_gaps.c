/* Probe E: scenarios behind findings G2 to G5 (all on the unchanged module). */
#include "probe.h"
int main(void) {
  /* G2: retry reported OK, the core clears the open-flag fact at once; if the caller's recovery then fails, nothing tells the core */
  init(RC_ST_ERR_STORAGE_FAULT, RC_CENTRE_SW2); F()->open_flag = true;
  ev(RC_EV_STORAGE_RETRY_OK, 100);
  printf("INFO G2 after retry ok: state=%s open_flag_fact=%d run_recovery=%d\n", SN(), F()->open_flag, has(RC_ACT_RUN_RECOVERY));
  ev(RC_EV_SCAN_READ_ERROR, 200);
  printf("INFO G2 a read error event in STANDBY: state=%s (no row)\n", SN());
  sw(RC_SW_CENTRE, true, 1000); tk(2100);
  printf("INFO G2 long press after that: state=%s open=%d\n", SN(), has(RC_ACT_OPEN));
  /* G3: B5 reported in BOOT before init done, flag set */
  init(RC_ST_BOOT, RC_CENTRE_SW2); F()->open_flag = true; bt(RC_BATT_B5, 5);
  printf("INFO G3 B5 in BOOT, flag set: state=%s recovery_ran=%d\n", SN(), has(RC_ACT_SD_ON));
  /* G4: fault -> case -> out: STANDBY, no storage retry, long press tries to record */
  init(RC_ST_ERR_STORAGE_FAULT, RC_CENTRE_SW2); ev(RC_EV_VBUS_IN, 1000); ev(RC_EV_VBUS_OUT, 2000);
  sw(RC_SW_CENTRE, true, 3000); tk(4100);
  printf("INFO G4 state=%s open=%d\n", SN(), has(RC_ACT_OPEN));
  /* G5: BOOT row 8 leaves VDD_SD on */
  init(RC_ST_BOOT, RC_CENTRE_SW2); F()->batt = RC_BATT_B5; ev(RC_EV_INIT_DONE, 10);
  printf("INFO G5 B5 at init done: state=%s SD_OFF=%d (BOOT has VDD_SD on)\n", SN(), has(RC_ACT_SD_OFF));
  /* G6: stop at 1000 ms, hold on to 5000 ms: no restart (G5 rule of spec) and release/press records again */
  init(RC_ST_RECORDING, RC_CENTRE_SW2); F()->open_flag = true; sw(RC_SW_CENTRE, true, 0); tk(1100);
  enum rc_state s1 = S(); tk(5000); enum rc_state s2 = S();
  CHECK("E stop by long press, thumb kept down 4 s: STANDBY and stays", s1 == RC_ST_STANDBY && s2 == RC_ST_STANDBY);
  sw(RC_SW_CENTRE, false, 5100); tk(5200); sw(RC_SW_CENTRE, true, 6000); tk(7100);
  CHECK("E new press then records", S() == RC_ST_RECORDING);
  printf("SUMMARY pass=%d fail=%d\n", npass, nfail);
  return nfail != 0;
}
