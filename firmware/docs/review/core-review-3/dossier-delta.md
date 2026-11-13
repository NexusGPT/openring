# Core round 3 delta check (reviewer of round 2)

OUT = `firmware/docs/review/core-review-3/`. Rulings: `firmware/docs/core-delta-2.md` (R9 to R15, C7 to C9). Commit 16200d5 could not be checked (no git); the code hashes are in `OUT/hashes-end.txt` (no change during my run). Baseline host run on the unchanged module: `OUT/base/host-run.log`, `RESULT PASS tests=202`, exit 0.

## 1. Rows (item 4)
`OUT/rows/dump_rows.c` takes each of the 71 rows through the real module; `OUT/rows/check_rows.py` compares from, event text, guard, to and the ordered actions with the specification (actions typed by me from the action column). `OUT/rows/check_rows.log`: `lines checked 72 rows seen 71 diff lines 0`. Exact event text, spec against code: `OUT/rows/exact.log`: `exact event text diffs [] of 71`. The new or changed rows (8, 24, 41, 42, 59, 60, 65, 67) all match, including row 8 `SD_OFF M3` and row 41 `SAVE_SETTINGS_TIME SHIP_MODE`. Result: 71 of 71 pass.

## 2. N1 to N6 (item 1), probe `OUT/probes/pG_delta.c`, log `pG_delta.log`
| Finding | Status | Evidence (pG_delta.log lines) |
|---|---|---|
| N1 leaving the case at B2 | closed | "N1 CHARGING at B2, VBUS out: OFF + SHIP_MODE", same for TRANSFER; host `test_r10_leaving_case_at_b2_switches_off`; mutations r17, r18 caught |
| N2 open flag | closed | "N2 retry ok flag set: RECOVERY, flag kept"; "N2 recovery scan fails: ERR_STORAGE_FAULT, flag still set"; "after failed scan, retry ok, case, out: long press never opens a recording"; "scan done clears flag"; r10, r11 caught |
| N3 battery in BOOT | closed | "N3 B5 in BOOT kept", "B2 in BOOT kept", "init done at B2, flag set: OFF, no recovery, flag stays"; pC "R12 B5 ... then init done with flag set: RECOVERY first"; r14, r15 caught |
| N4 fault survives the case | closed for the paths I tried | write failure, BOOT init failed, ERR_STORAGE_FAULT then case in/out all return to ERR_STORAGE_FAULT with the retry armed (pC and pG); init done clears the fact; r06, r07, r08, r09 caught. Open point: section 3, finding D1 |
| N5 row 8 | closed | "N5 B5 at init done: ERR_BATTERY_LOW with SD_OFF and M3"; r16 caught |
| N6 one retry per tick | closed | "N6 tick 10 min late: one retry", "next tick 1 ms later: none", "60 s after the late one: one"; pC "R14" check; r12, r13 caught |
Count: 6 of 6 closed.

## 3. R15: a ring awake at B2 without VBUS (item 2)
Walk in pG: every reachable start (no VBUS: OFF, SHIP, BOOT, RECOVERY; with VBUS: BOOT, RECOVERY, CHARGING, TRANSFER, ERR_CHARGER, FACTORY_TEST, ERR_STORAGE_FAULT) with the level at B2, every event as first, every event or none as second, open flag, full and fault facts all combined, then a late tick: 92,928 sequences. Walk 2 (B2 reported then VBUS out, and VBUS out then B2, from all 14 states, 4 fact sets, both orders) passes: no state left awake.

**Walk 1 FAILS: 500 sequences end awake at B2 without VBUS, all one cause (finding D1).**

## 4. Findings
**D1 (S2): R15 does not hold when the ring enters ERR_STORAGE_FAULT with VBUS present.** Path: ring in the case at start-up, battery at B2 (kept level), storage init fails (row 6, no VBUS guard) or a recovery scan read error (row 11); the state is ERR_STORAGE_FAULT with VBUS present, so the entry check (`core.c:129-134`, needs no VBUS) does not fire. VBUS then removed: `ERR_STORAGE_FAULT` has no "VBUS removed" row and the level does not change, so no B2 event comes: the ring stays awake at B2 without VBUS until a retry succeeds (then R-STB gives OFF) or the cell dies. Evidence: `pG_delta.log` lines `AWAKE start=BOOT vbus0=1 e1=STORAGE_INIT_FAILED e2=VBUS_OUT ... -> ERR_STORAGE_FAULT`, `AWAKE start=RECOVERY vbus0=1 e1=SCAN_READ_ERROR e2=VBUS_OUT ...`, `AWAKE start=ERR_STORAGE_FAULT vbus0=1 e1=VBUS_OUT ...` (500 lines, 8 fact sets each). The builder's walk only covers rows into the six states, not VBUS removal inside a state. Who: lead (spec: a row or an R-STB-like check on VBUS removal for ERR_STORAGE_FAULT, and the same check for any state entered or kept with VBUS: BOOT and RECOVERY already leave through rows that check) and builder (test).

**D2 (S3, test):** mutation r21 (the internal event STORAGE_FAULT_SET accepted by `rc_core_event`) passes all 202 tests (`mut/r21_internal_fault_event_injectable/host-run.log`). Effect: an outside caller could put a STANDBY ring into ERR_STORAGE_FAULT; it cannot start or stop a recording (owner's rule unaffected). Who: builder.

Notes: r22 (row 60 guard always true) passes because row 59 precedes it in table order: equivalent. r20 did not compile (my pattern); not counted.

S1 0, S2 1, S3 1.

## 5. Owner's rule on the new table (item 3)
- Probe A (8 paths into STANDBY x 7 fact sets x both sources, plus direct facts): 120 of 120 pass (`pA_standby_entry.log`).
- Probe B (holds begun in 7 states, 9 leave times, both sources, with and without tick): 442 of 442 pass (`pB_hold.log`).
- Probe C (updated for R9 to R14): 51 of 51 pass (`pC_scen.log`).
- Fuzz D, oracle as in round 2 plus "no entry with the storage fault set": `SUMMARY seeds=20000 steps=400 entries=1287 exits_by_input=987 exits_by_system=860 violations=0` (`pD_fuzz.log`).
- Probe F (rows that both match, `pF_overlap.log`): 6 groups, all ordered by the spec (4/5, 13/14/15, new: CHARGING VBUS removed rows 41 before 42, B2 before B5, as R10 says). No unintended overlap.
Verdict: the owner's rule holds.

## 6. Mutations on round 3 code (item 5)
22 built, 1 invalid (r20), 21 valid, 19 caught by the host tests, 2 not caught (r21 real gap D2; r22 equivalent). Areas: B2 entry check (r01 to r05, r20), storage fault fact (r06 to r09, r21), open flag (r10, r11, r22), retry timer (r12, r13), kept battery level in BOOT (r14, r15), rows (r16 to r19). Table: `OUT/mut/mutation-table.md`; each copy and its probe logs in `OUT/mut/<name>/`.

## 7. Stuck states (item 6)
Exits per state (`pF_overlap.log` EXITS lines): the only new gap is ERR_STORAGE_FAULT with VBUS, which has no VBUS-removed row (D1). Other states unchanged from round 2.

## 8. Could not check
Commit id; Zephyr runs and `firmware-check.py` not rerun; test bodies not read line by line; the caller-side glue does not exist.

## 9. Own steps
Probe pG's first version counted impossible start states (STANDBY at B2 with no VBUS) as failures; I restricted the starts to reachable ones and reran (the 36,320 count of the first run is not used). The `.bak` files in `OUT/probes` are sed backups.

RESULT: done, 71 of 71 rows pass, N1 to N6 all closed, owner's rule holds (fuzz 20,000 seeds 0 violations), S1 0, S2 1 (D1: R15 fails with ERR_STORAGE_FAULT entered under VBUS), S3 1, 19 of 21 valid mutations caught.
