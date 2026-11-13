# Core round 4 delta check (reviewer of rounds 2 and 3)

OUT = `firmware/docs/review/core-review-4/`. Rulings: R16 and C10 (end of `firmware/docs/core-delta-2.md`). Commit 8d54332 could not be checked (no git); code hashes in `OUT/hashes-end.txt`. Baseline host run on the unchanged module: `OUT/base/host-run.log`, `RESULT PASS tests=214`, exit 0.

## 1. Walk pG, 92,928 sequences
`OUT/probes/pG_delta.log`: `INFO R15 walk: 92928 event sequences, awake-at-B2-without-VBUS results 0`; AWAKE lines 0; `SUMMARY pass=22 fail=0` (round 3: 500 AWAKE, 1 fail). Walk 2 (B2 and VBUS out in both orders, 14 states) passes.

## 2. D1 and D2 (`OUT/probes/pH_d1.log`, 11 of 11 pass)
- D1 path 1 (BOOT in the case at B2, storage init fails, VBUS removed): ERR_STORAGE_FAULT, then OFF with SHIP_MODE. Closed.
- D1 path 2 (RECOVERY read error in the case at B2, VBUS removed): OFF with SHIP_MODE, open flag stays set. Closed.
- D2: STORAGE_FAULT_SET sent through `rc_core_event` is refused (no state change, no action). My mutation r21 re-made as `v11_c10_fault_set_injectable_r21` fails 1 test (`test_c10_refuses_storage_fault_set`). Closed.
- Builder's readings of R16: TRANSFER at B2 (VBUS out): ABORT_COMMAND, SD_OFF, then OFF through STANDBY (pH, passes). FACTORY_TEST: BOOT with REBOOT, then init done gives OFF (pH). BOOT: row 7 gives OFF at once (v09 below). RECOVERY stays until the scan ends, then OFF with the CLOSE record (pH). I judge all four readings consistent with the ruling and R4b.

## 3. Rows, probes, fuzz (owner's rule)
- Rows: `OUT/rows/check_rows.log`: `lines checked 72 rows seen 71 diff lines 0` (71 of 71 pass; table unchanged).
- Probe A 120 of 120, B 442 of 442, C 51 of 51 (`probes/pA_standby_entry.log`, `pB_hold.log`, `pC_scen.log`).
- Fuzz D, 20,000 seeds x 400 steps: `entries=1265 exits_by_input=974 exits_by_system=857 violations=0` (`pD_fuzz.log`). The first run gave 7 violations: all `left RECORDING by event VBUS_OUT (batt fact 3)` (`pD_dbg.log`). Cause: the fuzz sets the battery fact to B2 directly while RECORDING, a state the real ring cannot be in (B2 closes the recording through the battery event), and R16 then closes and switches off on VBUS removal. That is the close the spec wants, not a user input; I added "VBUS removal with the battery fact at B2" to the fuzz oracle's list of allowed exits and reran (0 violations). Both runs are kept (`pD_dbg.log` is the first run with the event named).
- Owner's rule verdict: holds. Rows leaving RECORDING are unchanged except R16 acting on VBUS removal at B2.

## 4. Mutations on the VBUS-removal check (`OUT/mut/mutation-table.md`)
13 built (6 asked), all compile; 10 caught by the host tests, 3 not:
- **v02** (R16 also fires at B5): passes 214 tests. Effect: a ring in ERR_STORAGE_FAULT in its case at B5, taken out, would go OFF at 5 % instead of staying awake. My probe pH catches it (`mut/v02_r16_fires_at_b5_too/pH_d1.log`: `FAIL R16 at B5 (not B2)`). Finding T1 (S3, test): no test says that R16 is only for B2.
- **v09** (R16 skips BOOT): passes. Effect: BOOT at B2 with VBUS removed waits for "init done" or a failed init (both end OFF through R15) instead of OFF at once. Behaviour differs only in timing. Finding T2 (S3, test): the BOOT leg of R16 is untested.
- **v07** (R16 also on VBUS_IN): passes. I judge it equivalent for every reachable state (a state with a B2 row at B2 with VBUS present is not reachable); by reading, unverified by a test.

## 5. Stuck states
`probes/pF_overlap.log`: 6 overlap groups, all ordered by the spec (4/5, 13/14/15, 41/42); no new unintended overlap. Exit lines unchanged from round 3. ERR_STORAGE_FAULT at B5 with VBUS removed stays awake by design (retry every 60 s). RECOVERY at B2 waits for its scan to end (R4b). No new stuck state.

## 6. Could not check
Commit id; Zephyr runs and `firmware-check.py` not rerun; test bodies read only by name and by mutation results.

S1 0, S2 0, S3 2 (T1, T2).

RESULT: done, S1 0, S2 0, S3 2 (T1 and T2 are test gaps from surviving mutations v02 and v09); D1 and D2 closed, pG walk 0 AWAKE, 10 of 13 mutations caught.
