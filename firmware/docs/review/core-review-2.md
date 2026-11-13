# Core review 2: round 2 of the ring software's core (independent)

Written down by the lead on 2026-11-11 from the reviewer's final report, word for word in substance: the reviewer's own write of this file was refused by the tool and it did not route around the refusal. Evidence folder (the reviewer's own files): `firmware/docs/review/core-review-2/` (OUT below).

Version judged: commit fc3b104 (the reviewer ran no git; the md5 of code and tests and the sha1 of `design/firmware.md` were identical at the start and the end of its run, `OUT/hashes-end.txt`).

## 1. Rows

66 of 66 pass. `OUT/rows/rows-dump.txt` takes every row through the real module; `OUT/rows/check_rows.log` reads "lines checked 68 rows seen 66 diff lines 0". The event text of all 66 rows equals the specification (`OUT/rows/exact_event_text.log`). The only overlapping rows are 4/5 and 13/14/15, as the specification orders them (`OUT/probes/pF_overlap.log`).

## 2. Rulings R1 to R8 and R4b

All nine landed as ruled.
- Probe A (`OUT/probes/pA_standby_entry.log`): 8 paths into STANDBY, 7 fact sets, both centre sources, then a real long press: 120 of 120 pass; no start at B5, B2 or full storage.
- Probe B: holds begun in 7 non-STANDBY states, left at 9 different times, never record (442 of 442); a release and a new press does record.
- Probe C: open-flag paths, the 60 s retry every time, VBUS in all 14 states (one CHARGE_ON each), battery calls: 47 of 47.

## 3. Owner's rule

Pass. Row 12 is the only way into RECORDING and only a real long press reaches it. The only user input that leaves RECORDING is a long press (row 24); row 28, the case's VBUS, is allowed by line 203. Fuzz of 20,000 seeds with 1,493 entries into RECORDING: 0 violations (`OUT/probes/pD_fuzz.log`).

## 4. Review 1 findings F1 to F9

All nine closed, each shown by a test or by a mutation of the reviewer that now fails.

## 5. Mutations

51 copies built, 3 invalid and replaced (m05b, m26b, m27b). Of 48 valid copies, 42 are caught by the host tests and 6 survive (`OUT/mut/mutation-table.md`).
- Real test gaps: m21 (the open flag is not cleared on the recovery request), m31 (the battery event repeats at an unchanged level), m35 (an invalid battery level is accepted), m40 (the storage-full event no longer sets the fact).
- Judged equivalent by reading only: m33 and m41.

## 6. Findings: S1 0, S2 0, S3 11

- N1: CHARGING with VBUS removed at B2 goes to ERR_BATTERY_LOW, not OFF (row 40, `state_table.c:112`). The B2 event is not sent again at an unchanged level, so the ring stays there with no ship mode. The code equals the row: a specification gap; the lead may count it S2.
- N2: the core clears the open-flag fact when it asks for recovery in row 57 (`core.c:73-75`), and nothing reports a failed recovery. After that a long press opens a new recording (`OUT/probes/pE_gaps.log` G2). S3, but S1 if a recovery can fail.
- N3: a B5 battery event in BOOT before "init done", with the flag set, skips recovery.
- N4: a storage fault, then the case, then VBUS out lands in STANDBY and never retries.
- N5: row 8 leaves VDD_SD on.
- N6: a tick 10 minutes late gives 8 retries in one call.
- N7 to N10: the four surviving mutations of section 5.
- N11: the test name `test_r6_row15` names the wrong row.

## 7. Not checked, and the reviewer's own slips

- Not rerun: the Zephyr runs and `firmware-check.py` (only the end of the Zephyr log was read). The caller's glue code does not exist in the core.
- The first probe A had 2 FAIL lines caused by a bug in the probe; fixed and rerun. The first logs of mutation m01 were deleted with `rm -f` by mistake and rerun. The older `probes/pA.log`, `pB.log`, `pC.log`, `pD.log` come from runs before `run.sh`.

RESULT: done, S1 0, S2 0, S3 11 (N1 and N2 flagged for the lead), 42 of 48 valid mutations caught by the host tests.
