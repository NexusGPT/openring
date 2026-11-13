# Step 4 checklist (screens). Evidence: firmware/build-logs/20261112-115540-os-screens.log (the log), screens-notes.md, files in this folder.

- [x] 1. Orientation 240 x 120, one turn function rscr_to_panel; deviation listed. evidence: screens-notes.md section 4 point 5; test_geometry_turn in the log (SUITE PASS screens_table)
- [x] 2. LVGL on a simulated display, frame within 45 min. evidence: spike2.out (first frame about 20 min after the start), final log stage tests-native_sim
- [x] 3. Pictures from the frame buffer the driver received, no window. evidence: rscr_capture.c, pictures stage lines in the log
- [x] 4. Module ring_screens, pure part plus drawing; ring_core table untouched; no accessor added to other modules. evidence: screens-notes.md section 2 and section 4 point 13
- [x] 5. Screens drawn (21 pictures). evidence: log SCREENPIC lines, pictures-compare.txt
- [x] 6. R-SIGN at this layer; broken copies rsign_dark and rsign_blank_panel fail. evidence: log lines of broken-screens
- [x] a. pictures saved, manifest, copied. evidence: design/software/os/screens/manifest.md, pictures-compare.txt
- [x] b. pixel checks per picture. evidence: SUITE PASS screens_draw in the log
- [x] c. table on native_sim and nrf54lm20bsim. evidence: SUITE PASS screens_table twice in the log
- [x] d. two-device test. evidence: TEST S RESULT PASS (33 checks passed) in the log
- [x] e. 12 broken copies caught on their named checks. evidence: stages broken-screens and bsim-screens-broken in the log
- [x] f. RESULT PASS, all 20 stages exit 0, flash and RAM in the log. evidence: the log
- [x] g. screens-notes.md written, last line RESULT. evidence: firmware/docs/screens-notes.md
- [x] h. no git, no browser; own server copy removed (listing saved). evidence: server-listing-after-cleanup.txt
- [-] i. Time: the 3 hour limit was passed while the notes were written; the final self-audit is the claim script output audit-output.txt only (not a full extraction of every sentence).
- [x] j. must-not-touch files untouched except ring_glue (deviation 13).
