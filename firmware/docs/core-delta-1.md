# Core, round 2: the lead's rulings on review 1 and on the unclear places

Date: 2026-11-11. Sources: `firmware/docs/review/core-review-1.md` (findings F1 to F9, 0 S1, 0 S2, 9 S3; 38 of 44 mutations caught) and `firmware/docs/core-notes.md` section 3 (U1 to U23).

Order of work: the lead first writes these rulings into `design/firmware.md` (version F7, part 1). The core's builder then regenerates the table from the changed rows and changes code and tests. Until the specification carries a ruling, the code does not change for it.

## Rulings that change the specification (lead writes them into firmware.md, then the builder follows)

| Id | Ruling | Why |
|---|---|---|
| R1 (review F2) | Row 12 gains a guard: a long press in STANDBY starts a recording only with the battery above B5 and free space above SFULL. Otherwise no recording starts and the screen shows the message ("Battery low" or "Storage full"). In addition, every entry into STANDBY checks the facts first: battery at B2 goes to OFF, at B5 to ERR_BATTERY_LOW, free space at SFULL to ERR_STORAGE_FULL (battery first). This covers rows 41, 53, 55 and 57. | Section 1.1 says new recordings are refused at B5; the rows did not enforce it. A recording started on full storage or a nearly empty cell can be lost. |
| R2 (U8) | Row 36 gains the guard "battery above B5". Leaving the case with storage full and the battery at B5 gives ERR_BATTERY_LOW. | Row 47 already lets battery low replace storage full; the other order leaves a ring with a low battery in the storage state. |
| R3 (U9, review F3) | In ERR_STORAGE_FAULT the storage is tried again every 60 s, not once. The caller runs the init when the core asks for it (a new action "retry storage") and reports the result as an event. | One failed retry must not leave the ring in the fault state for good. |
| R4 (U6) | Start-up with an unfinished recording and the case attached: row 4 first (RECOVERY), then row 10 (CHARGING). | The recording is saved before anything else. |
| R5 (U7) | At "init done" the battery is read first: at B2 row 7, at B5 row 8, else row 3 or 5. | The rows had no order for this case. |
| R6 (review F5) | Row 13 lists MT after the screen's centre action when the screen is on. | Line 301 already says so; the row text was incomplete. |
| R7 (review F6) | A centre hold is cancelled by any change of state. The wearer must release and press again. A hold that began in CHARGING, TRANSFER or an error state never starts a recording, even if the ring leaves that state before the 1,000 ms mark. | Taking the ring out of its case with the thumb on the joystick must not start a recording. Owner's rule: recording only on a deliberate long press. |
| R8 (review F9) | CHARGE_ON is sent on every appearance of VBUS, in every state, also where no row changes the state (BOOT, RECOVERY). | Rule R-CHG (line 199) says the first VBUS event turns the charger on. |

## Rulings on code and tests only (builder)

| Id | Ruling |
|---|---|
| C1 (review F8) | The battery fact can go down as well as up: the power part reports each threshold crossing in both directions through one call; `rc_core.h` and the notes say who calls it and when. |
| C2 (review F1) | Row 3's guard gets a test on its negative side (mutation m29 must fail). |
| C3 (review F4) | Tests for the B15 re-arm on VBUS, the S30 re-arm on a new recording, and the refusal of timers given through `rc_core_event` (mutations m15, m25, m33 must fail). |
| C4 (review F7) | `tg_find` returning nothing fails the one test with its name; no test run ends on a crash. |
| C5 | The simulated chip target is named `nrf54lm20bsim/nrf54lm20a/cpuapp` in this kit version. Add it to `testcase.yaml` and run the core tests on it through `firmware/tools/remote.sh`. |
| C6 | Mutations m21 and m23 (judged equivalent by reading only): show by a test or by reasoning in the notes that they cannot change behaviour. |

## Bar for round 2

- The table is regenerated from firmware.md F7 and the row count printed by `count_rows.py` matches the document.
- Every ruling R1 to R8 has at least one test named after it; each of the review's surviving mutations m15, m25, m29, m33 now fails.
- Host run `RESULT PASS`, Zephyr run on `native_sim` and on the simulated chip target, the four broken copies still fail.
- The reviewer reads the round again and finds no S1 and no S2.
