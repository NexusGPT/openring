# fix1 (recorder) checklist. Started 2026-11-13 12:25:37 CET (`date`). Files of this helper: build-logs/step6/fix1-rec-*
(the older fix1-broken*, fix1-plain.console, fix1-compare.txt are another helper's, not mine).

- [x] 1. R6-01: ship path waits until rmo_playing() false, bounded by M2 length + stated margin, then rmo_stop; case asserts full M2 on MOTOR before SHPHLDCONFIG evidence: fix1-rec-u2.log l.7678/7999; rrec.c:330; rrec_spec.h:329
- [x] 2. R6-01 broken copy `ship_cuts_m2` fails its named case on native_sim and on bsim evidence: fix1-rec-u2.log l.607, l.617
- [x] 3. R6-02: ship step 1 closes recording, storage, USB, radio, screen before SHPHLDCONFIG; R20 beacon unchanged; case asserts each closed before the config write evidence: fix1-rec-u2.log l.7677/8000, 7684/8005; fix1-rec-c1.log l.365
- [x] 4. R6-02 broken copy `ship_screen_on` fails its named case on both targets evidence: fix1-rec-u2.log l.642, l.653
- [x] 5. R6-02 additions only where no public call exists (USB stop in ring_xfer, radio stop in ring_devices), each with its reason evidence: fix1-rec-headers-check.txt (0 lines removed); notes FR1.2
- [x] 6. R6-03: after abort / timed-out finish, wait for the command (bound FINISH_WAIT_MS), unmount through a waiting unmount (store addition), failed unmount retried and reported evidence: rrec.c:277 to 302, 485; fix1-rec-u2.log l.7679 to 7681
- [x] 7. R6-03 cases: VBUS removed while a read command runs on a slowed disk; row l.178 with a timed-out finish evidence: fix1-rec-u2.log l.7681/7977, 7680/7978
- [x] 8. R6-03 broken copy `unmount_result_dropped` fails its named case on both targets evidence: fix1-rec-u2.log l.684, l.701
- [x] 9. R6-04: HFXO requested in BOOT and RECOVERY, released per the table for the next state; test_rails.c corrected to the table; plan's corrected P6 wording in the notes evidence: rrec.c:509; fix1-rec-u2.log l.7669/8012; P6 wording in notes FR1.1
- [x] 10. R6-04 broken copy `no_hfxo_in_boot` fails its named case on both targets evidence: fix1-rec-u2.log l.725, l.736
- [x] 11. R6-05: test_close_order checks frames of the closed recording against what was captured, stop moment leaves a partial chunk evidence: fix1-rec-u2.log l.7654/7980 and its close frames print
- [x] 12. R6-05 broken copy `close_drops_partial` fails test_close_order on both targets evidence: fix1-rec-u2.log l.768, l.787
- [x] 13. R6-06: cases on the real rrec_test_recording: type 2, 2 s length, VDD_MIC on/off moments of T-SIGN; T13 and T17 mapped in the notes evidence: fix1-rec-u2.log l.7683/7997, 7682/7998; T13, T17 in notes
- [x] 14. R6-06 broken copy `test_recording_wrong_type` fails its named case on both targets evidence: fix1-rec-u2.log l.810, l.820
- [x] 15. R6-07: notes row C13 says no product code sends the highlight event before FW 7's Bluetooth source evidence: notes, R6-07 paragraph
- [x] 16. R6-08: one latched bit per kind (VBUS_OUT, CHUNK_WRITE_FAILED, MIC_NO_BLOCK), delivered when the queue has room; no new log code evidence: fix1-rec-u2.log l.7645/7989; code list unchanged except the lead's 0x0290
- [x] 17. R6-09: no read of unset `mi`; open flag keeps its value when already mounted evidence: rrec_bridge.c:158 to 166; fix1-rec-u2.log l.7648/7986
- [x] 18. R6-10: menu Power off handed to the join's thread; screens thread free during ship evidence: fix1-rec-u2.log handler print 'on thread rrec'
- [x] 19. R6-13: run printing the stamps on the vbat_read_at_0 copy first; then case independent of earlier cases; 1,000 ms exact if timer driven else tolerance stated evidence: fix1-rec-r613a.log (stamps); fix1-rec-u2.log l.7885/8215
- [x] 20. R6-14: case asserts percent, "Charging"/"Full", time to full as the screen receives them (typed from FW l.374) evidence: fix1-rec-u2.log l.7676/8013 and the SCR_CHARGING frames print
- [x] 21. R6-17: test_recording a real atomic flag evidence: rrec_int.h:80
- [x] 22. F2: guard sim-only helpers in rau.c and rmo.c with CONFIG_RING_RHW_SIM; kit build has none of the three warnings evidence: fix1-rec-u2.log l.8425 'F2 warnings: 0'
- [x] 23. F1: clear_state waits for the capture loop to end; the 100 ms sleeps in rt.c removed if not needed (say which kept, why) evidence: rau.c:324; rt.c (two sleeps after the reboot removed, the one before kept, notes FR1.1 F1 row)
- [x] 24. Bar 2: targeted run ends `UNIT PASS tests/recorder`; `UNIT PASS` for each other changed unit (store, xfer, audio, motor, factory, screens, devices as they apply) evidence: fix1-rec-u2.log l.7535
- [x] 25. Bar 3: 21 screen pictures equal (screens-notes.md method) evidence: fix1-rec-compare-screens2.txt RESULT EQUAL
- [x] 26. Bar 3: kit build compiles, none of the three F2 warnings evidence: fix1-rec-u2.log l.8423, l.8425
- [x] 27. Bar 4: notes map each finding to file and line change, case, broken copy, log line evidence: notes FR1.1, FR1.4
- [x] 28. Notes "Fix round 1": every finding with state, every outside change with reason, what I could not do, questions_for_owner, RESULT last line evidence: notes FR1.5, FR1.2, FR1.7, questions_for_owner, RESULT line
- [x] 29. Order of runs: (1) local edit-match check of each broken copy, (2) short suite run (bounded wait <= 6 min), (3) full unit run in background with exit file, then end turn naming command, pid, exit file evidence: fix1-rec-editcheck1/2/3.log; s1, s2, s4 before u1, u2; u2 started in background with exit file
- [x] 30. At most one server run of mine at a time; server folder only /root/ring-os/src-u-fix6; stop if < 25 GB free evidence: one remote.sh at a time (runs in order r613a, s1, s2, s3, k1, u1, s4, u2, c1, c2); free 29 to 39 GB in the ten consoles
- [x] 31. No git; no browser; no stderr to /dev/null; no kit/Zephyr source lines in any file; no secret or server address in files evidence: no git or browser command in this run; streams to logs
- [x] 32. Public headers: additions only, no existing declaration changed evidence: fix1-rec-headers-check.txt
- [x] 33. Suites of steps 1 to 6 still pass (units touched rerun; full run is the lead's) evidence: fix1-rec-u2.log l.7535 (the units touched) and fix1-rec-c1.log l.936; the full run is the lead's
- [x] 34. Expected values typed from FW with the line; numbers from rrec_spec.h evidence: cases cite FW lines; numbers from rrec_spec.h except the join's two stated margins
- [x] 35. Final reply under 3,500 characters, quotes last line of each cited proof file evidence: fix1-rec-final-reply.md and fix1-rec-audit.txt

Progress at 2026-11-13 13:07 CET (before the full run's result): edits made for items 1, 3, 5, 6, 7, 9, 11, 13, 15 to 23;
local edit check (item 29.1) fix1-rec-editcheck1.log; short runs fix1-rec-s2.log (52 of 52 per board), fix1-rec-s3.log;
pictures and kit build fix1-rec-k1.log, fix1-rec-compare-screens.txt. Full run fix1-rec-u1 started (pid in fix1-rec-u1.pid).
Ticks are set after the full run.
- [x] 36. Lead's ruling on 0x0290 (first failed try, once at the end with the count; case asserts 2 records; copy unmount_result_dropped still failing; short run then unit run on tests/recorder) evidence: fix1-rec-s5.log; fix1-rec-u3.log l.665, l.681, l.802, l.804, l.806 to 808
