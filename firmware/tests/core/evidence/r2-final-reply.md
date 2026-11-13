## Core round 2 report

**Results** (paths under firmware)
- **Host:** `tests/core/host/host-tests.log` shows `suites=10 tests=176 pass=176 fail=0` and `RESULT PASS tests=176`, exit 0.
- **Zephyr:** run through `tools/remote.sh` (`tests/core/evidence/r2-zephyr-run-1.log`, `build-logs/20261111-113611-core-tests-r2.log`).
  - "2 of 2 executed test configurations passed", "352 of 352 executed test cases passed", "with no warnings", exit 0.
  - Platforms: native_sim and the nrf54lm20bsim nrf54lm20a cpuapp board. The log gives no count per platform.
- **Row count:** `evidence/r2-count-rows.log` shows 65 rows in section 1.2 (the document states 65) and 65 row tests. The 65 action cases match their document lines: `COUNT MATCH`.
- **Broken copies** (`tests/core/broken/broken-*.log`), each `RESULT FAIL`:
  - long900: 28 failing tests; row12to: 13 plus the generator check; gap60: 2; row27act: 3.
  - The review's survivors m15, m25, m29 and m33 now fail, with 1 failing test each (the C2 and C3 tests).
  - m09 now gives 12 named FAIL lines and no crash.
  - m21 and m23 still pass as expected: neither can change behaviour (C6, argued in the notes).

**firmware-check.py:** 1 failure, "header does not say Version F6", from lines 531 and 532 of the check script (in the project's design folder).
- The cause is the requested F7 version line. With the old version line it ended "0 failures" (`evidence/r2-fwcheck-1.log`). I did not edit the check.
- I asked you about this earlier; with no answer, I applied the line as asked.

**firmware.md:** I changed line 3 and sections 1 and 2 only (`evidence/r2-firmware-md.diff`).
- The table now has 65 rows instead of 61. R1 added rows 13 and 14; R3 split old row 53 into rows 55 to 57.
- Rules added: R-STB (entry into STANDBY), the order at "init done" (R4, R5), R7 in 2.1, and R8 in R-CHG.

**Code**
- **R1:** the long-press guard, the refusal rows, and the entry check after every row into STANDBY.
- **R2:** a guard on row 38.
- **R3:** action `RETRY_STORAGE`, result events; the 60 s timer repeats.
- **R5:** the battery is read first at init done.
- **R7:** `rc_gesture_cancel_hold` runs on every change of state.
- **R8:** charge on at every VBUS appearance.
- **C1:** `rc_core_battery(level)` is the only way to change the battery fact, in both directions.
- **C4:** `tg_get` fails a missing event by the test's name.
- **C5:** bsim board in `testcase.yaml`.

**Readings for you to confirm** (`docs/core-notes.md`, section "Round 2"):
- **Row 12 guard:** check 17 needs row 12's event text exact, so the R1 guard is at the start of its actions cell, where the generator reads it.
- **R1 entry:** goes through the STANDBY row for that event, with that row's actions. The refusal rows have the message only, no M3.
- **R4 and R5 together:** with no VBUS, the battery is read before the open flag. An unfinished recording at B5 goes to ERR_BATTERY_LOW, and recovery waits for the next boot.
- **R3:** the next try comes 60 s after the previous try.
- **R7:** a short press already released and waiting for its window is not cancelled.

**Rules:** no git command this round.

**Not done:** the check-script failure above. Its owner must accept F7, or you can choose to keep "Version F6, ".

RESULT: done, host `RESULT PASS tests=176` exit 0, Zephyr 352 of 352 on native_sim and nrf54lm20bsim exit 0, broken copies and m15, m25, m29, m33 fail, firmware-check.py 1 failure from the version line.
