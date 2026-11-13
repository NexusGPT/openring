# Core, round 3: the lead's rulings on review 2

Date: 2026-11-11. Source: `firmware/docs/review/core-review-2.md` (S1 0, S2 0, S3 11). Round 2 passes its bar. The rulings below close what the review found; N1 and N2 are treated as must-fix.

## Rulings that change the specification (sections 1 and 2 of design/firmware.md)

| Id | Finding | Ruling |
|---|---|---|
| R9 | N2 | The open flag is cleared only by two things: a successful close of a recording, and "scan done" at the end of RECOVERY. Asking for recovery clears nothing. Old row 57 (storage retry succeeds with the open flag set) goes to RECOVERY, not to STANDBY with an action; with the flag clear it goes to STANDBY through R-STB. A read error during the scan goes to ERR_STORAGE_FAULT with the flag still set, as today. |
| R10 | N1 | A new row: CHARGING, VBUS removed, battery at B2: OFF (same actions as the other B2 rows). The B5 row keeps "battery at B5". R-STB already orders B2 before B5; the same order holds for every row that leaves CHARGING or TRANSFER when VBUS goes. |
| R11 | N4 | The storage fault is a fact the core keeps. It is set on entering ERR_STORAGE_FAULT and cleared only by a successful storage init. R-STB checks it first: an entry into STANDBY with the fault set goes to ERR_STORAGE_FAULT (and so back to the 60 s retry). Leaving the case does not hide a broken storage. |
| R12 | N3 | Battery events that arrive in BOOT before "init done" are not applied at once: the level is kept and the order at "init done" decides (B2: OFF; else an unfinished recording is recovered first). |
| R13 | N5 | Row 8 (BOOT, battery at B5 and no VBUS) turns VDD_SD off. |
| R14 | N6 | At most one storage retry per call of the tick, whatever the delay; the next one is 60 s after it. |
| R15 | builder's question in round 3 | With no VBUS, a battery at B2 always ends in OFF. The level is a fact, not only an event: on entry into any state and at "init done" or a failed storage init in BOOT, the core checks it first and takes that state's "battery reaches B2" row (a state without one gets one). Order of the entry checks: B2, the storage fault, B5, storage full. Exception already ruled in R4b: at B2 the ring goes OFF without recovery, the open flag stays set. |

## Code and tests only

| Id | Finding | Ruling |
|---|---|---|
| C7 | N7 to N10 | Tests that make mutations m21, m31, m35 and m40 fail: the open flag after a recovery request (per R9), a repeated battery event at an unchanged level does nothing, an invalid battery level is refused, the storage-full event sets the fact. |
| C8 | N11 | Rename `test_r6_row15` to the row it tests. |
| C9 | m33, m41 | Say in the notes why they cannot change behaviour, or add the test that catches them. |

## Bar for round 3

- firmware.md sections 1 and 2 carry R9 to R14; the row count the document states equals `count_rows.py`; `design/firmware-check.py` ends "0 failures".
- One test named after each of R9 to R14; m21, m31, m35, m40 fail; the earlier broken copies still fail.
- Host run `RESULT PASS`; Zephyr run on native_sim and on `nrf54lm20bsim/nrf54lm20a/cpuapp` through `firmware/tools/remote.sh`.
- The reviewer of round 2 checks the delta: N1 to N6 closed, no S1, no S2.

## Round 4: rulings on the delta review (firmware/docs/review/core-review-3/dossier-delta.md: S1 0, S2 1, S3 1)

| Id | Finding | Ruling |
|---|---|---|
| R16 | D1 | R15 holds at two moments, not one: on entry into a state, and whenever VBUS is removed, in every state. When VBUS goes and the battery is at B2, the ring takes that state's "battery reaches B2" row to OFF. This covers a ring that entered ERR_STORAGE_FAULT (or any state) in its case and is then taken out. A state that reacts to "VBUS removed" with its own row keeps that row; the B2 check comes first. |
| C10 | D2 | Events the core makes for itself (the storage fault set, timers, press events) are refused when an outside caller sends them through `rc_core_event`; one test per refused event. |

Bar for round 4: R16 in firmware.md; a test that walks every state: enter it with VBUS present and the battery at B2, remove VBUS, assert OFF; the reviewer's sequence walk (92,928 sequences) finds no ring awake at B2 without VBUS; mutation r21 fails; host and Zephyr runs pass; firmware-check 0 failures.
