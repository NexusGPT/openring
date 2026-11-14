# Brief: step 7 fix round 2 (lead, 2026-11-14 night)

Goal: Close the findings of the second independent review of step 7 (firmware/docs/step7-review-2.md, verdict FAIL: 1 major, 4 minor, 4 notes). Read it in full first.

FW: firmware
Version: project commit 77dff412 (code of 08820c32). The lead's own full run of 08820c32 (lead-full6) is on the server in /root/ring-os/src-lead7 until about 04:20: leave it alone.

The lead's rulings:
- S7R-07 first, because it sets the words: design/firmware.md l.506 stands. The card's lines are driven at resume, 1 ms after VDD_SD is on. The lead's earlier wording "driven again before VDD_SD comes on" was wrong; your code order is right.
- S7R-01 (major, the boot window): from spi00's init until your POST_KERNEL 99 hook the card's chip-select line is driven high while VDD_SD is off. Close it as far as code can. Read the SDK's source in the container and choose, with the lines cited: (a) a way in which spi00 and its card nodes do not initialise at boot at all and are initialised by the storage part when it first powers the card (for example the devicetree property for deferred initialisation with device_init), if that leaves NO driven window and the storage part's real file can do it cleanly; or (b) the release hook moved to run directly after spi00's init (the init priority right after the SPI controller's, with a BUILD_ASSERT that keeps that order), which leaves a window of the init calls in between. Use (a) if it builds and you can show from the source that the line is never configured as an output before the first power-on; else (b). Either way write in the notes exactly what happens to the line from reset to the first power-on, step by step, with the source line of each step, and what only hardware can measure. The simulated tests must stay unchanged and pass.
- S7R-02: ring-production-check must fail when the debug port is on, when DBG_TX has no pull-down, and when one of its input files is missing: add a planted copy for each and show it failing in the run.
- S7R-03: remote.sh refuses when shasum cannot run or prints no 64-character value for either file.
- S7R-04 and S7R-05: mark every superseded statement of the older sections of docs/board-notes.md as replaced (or correct it in place with the old text kept as "REPLACED 2026-11-14 (was ...)"), and correct README.md lines 70, 71 and 100 to what the logs show.
- S7R-06 (sign of the current given to the fuel gauge library): read the SDK's own source for it (the library header's text for the current argument, Nordic's fuel gauge sample for the nPM13xx in the SDK, and the sensor channel's sign in the nPM13xx charger driver) and make rpw_hw_real.c pass the sign the library expects, citing each line. If the SDK's files do not settle it, change nothing, write "not confirmed" with what you read, and add it to the list of what hardware must prove.
- S7R-08: run check_ring_pins.py on the production build's devicetree too (a new line of the production stage); list the remaining blind spots in the notes as they are; no further planted copies.
- S7R-09: no action.

Bar (it can fail):
1. One row per finding S7R-01 to S7R-09 in a new section "Fix round 2" of docs/board-notes.md: what changed (file:line), the log line that proves it, or "ruled, no change".
2. S7R-01: the step-by-step account of the chip-select line from reset to first power-on, with source lines; the ring build compiles; if (b), the BUILD_ASSERT is shown to fail on a wrong order (a scratch build, logged).
3. The production check's three planted copies each fail (log lines cited).
4. remote.sh's refusal without shasum is shown on a scratch copy that cannot reach the server (stop before the first network command; do not sync anything this time: check your planted change is really there before you run).
5. The whole tools/build_all.sh in /root/ring-os/src-s7: last result line RESULT PASS, every stage exit 0, the stage count stated (background run with an exit file firmware/build-logs/step7/fix2/f2-full1.exit and console f2-full1.console; end your turn naming the job; the lead wakes you).

Owns: as in fix round 1 (the board folder, the application's ringrec files, tools/build_all.sh, tools/check_ring_pins.py, tools/remote.sh for S7R-03 only, README.md, docs/board-notes.md, modules/ring_power/src/rpw_hw_real.c, modules/ring_store/src/rst_hw_real.c), plus the new folder firmware/build-logs/step7/fix2. Any other module file: stop and ask the lead first.
Must not touch: every other module and every test; design/ (read only; the lead edits design/firmware.md himself after your result); both review files and the reviewers' folders; the server copies /root/ring-os/src and /root/ring-os/src-lead7 and the lead's run; other people's processes on the server; any process on the Mac you did not start; any browser. The server's address and the ssh key are never printed or written; a scratch copy of remote.sh is deleted after use.
Writes to: firmware/docs/board-notes.md (section "Fix round 2", as you go).
Done when: the lead can read bars 1 to 5 from your full run's log and the notes.

Standing rules: the same as your step 7 brief, word for word (no git at all; never stderr to /dev/null, use 2>&1; absolute paths and chained cd; file names never start with REPORT, SUMMARY, FINDINGS or ANALYSIS; clock times from `date`; no foreground sleep; long runs in the background with an exit file; nothing large on the Mac, which has under 9 GB free; every number from a log line you name; no check result written before it is read).
Limits: 3 hours of your own work from your first `date` of this round.
End line: the last line of the "Fix round 2" section is `RESULT: <done|blocked>, <one sentence>`.
Your report ends with `questions_for_owner:` (`none` if there are none).
When you finish, your final reply is your report: it reaches the lead automatically. Keep it under 3,500 characters and put anything longer in a file it names. Do not also send it with SendMessage; use SendMessage only for a question or news while you keep working.
