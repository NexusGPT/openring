Step 6 review: FAIL on bar B1. I found 0 blockers, 6 majors, 8 minors and 3 notes. Every safety rule of B2 holds in the code. The full report is in firmware/docs/step6-review.md.

The pin holds: HEAD moved to 7f9fd031, but 0 files under firmware/ or design/firmware.md changed since af085a68 (W/pin-diff-code.txt).

Majors (all in the join):
- R6-01: menu "Power off" never plays M2 (FW l.151). The next action, ship_mode(), calls rmo_stop() first (rrec.c:268). No case checks it.
- R6-02: ship step 1 (FW l.937, l.939) does not close the screen, the radio or the USB stack. Only storage and the USB crystal are closed (rrec.c:266 to 281).
- R6-03: VBUS can be removed in TRANSFER while a command is running. rxf_abort() does not wait, rst_unmount() returns -EBUSY, and the join ignores that (rrec.c:330, :412). VDD_SD can then stay on in STANDBY. The case only removes VBUS when no command is running.
- R6-04: FW l.915 says HFXO is on in BOOT and RECOVERY. The join never holds it there (rrec.c:406). The plan's row P6 leaves this out, so the lead needs to rule on it.
- R6-05: test_close_order cannot fail for "write the partial chunk". The write it finds is a full chunk, written during the 1,100 ms stop press.
- R6-06: the join's half of T-MIC and T-SIGN is only tested through a stand-in (tests/factory/src/common.c:50 to 92).

R6-03 and R6-05 come from reading the code, not from a run.

Bar results:
- B2: 6 of 6 rules pass. R6-11 is a note against the specification: it says "main loop", and the product has none.
- B1: J 44 of 44 rows read, 38 pass. The other units pass on what I read: core 2 of 2, store 9 of 37, audio 10 of 27, xfer 10 of 28, power 8 of 18, motor 8 of 11, sys 8 of 11, factory 9 of 15, screens 2 of 2, rhw 4 of 4 fault cases.
- B3: 37 broken copies across all 11 units are real, and each named case asserts numbers taken from FW.
- B4: 64 of 64 citations match. An earlier look got 61 of 64; the 3 misses were errors in my own probe texts. Separately, one cited K3 log is not in the commit (R6-12).
- B5: 5 seams listed (R6-03, R6-04, R6-08, R6-10, R6-17).

The three findings the units reported:
- F1: confirmed simulation only. It does make the recorder suites depend on a 100 ms sleep.
- F2: warnings only.
- factory_screen with vbat_read_at_0: a fragile exact 1,000 ms assertion (test_screen.c:202), not a product fault. The likely cause is that the aborted motor case ends after 0.521 s instead of 1.021 s; I did not prove this with a run.

questions_for_owner: none. Evidence is in firmware/build-logs/step6/review-work/ (W/ above), and the audit's last line is `AUDIT: 168 claims checked, 0 without a match`.
