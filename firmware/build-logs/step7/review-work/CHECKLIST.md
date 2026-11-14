# Step 7 review checklist (reviewer's own)

- [x] 1. Files at commit 47204f09 (16 artifact files + README) evidence: version-check.txt, diff-stat.txt
- [x] 2. B1 pins, each U1 signal read from the files; reverse direction evidence: netlist-u1.txt, b1-pins.txt, b1-dropped-spares.txt
- [x] 3. B1 pin-changes applied (3 spares dropped, LCD_TE, OLED_PWR_EN moved) evidence: netlist-u1.txt lines 181, 205, 390, 394, 395; b1-dropped-spares.txt
- [x] 4. B2 copy byte-equal; does a difference fail anything evidence: b2-cmp.txt, b2-drift-checkers.txt
- [x] 5. B3 read check_ring_pins.py; blind spots; broken-copy stage evidence: log-ring-ram-pins.txt
- [-] 6. B3 run fakes (wrong port, missing node, extra pin, drift) through the real check not done: no dtlib or nrf-pinctrl.h on the Mac (local-dtlib.txt), build server forbidden by the brief
- [x] 7. B4 each power value against FW 8.1 and 8.7 evidence: firmware.md l.864-890, dts l.311-384, s7-explore3.console bindings
- [x] 8. B5 partitions, fit, 9.2, build sizes, retained 1,024, wdt31, gpregret1 evidence: b5-layout.txt, log-ring-drivers.txt, b5-swap-move.txt
- [x] 9. B6 real files vs stubs, reasons, RHW_SIM off evidence: log-ring-drivers.txt, rpw-build1-errors.txt, rhw-power.txt
- [x] 10. B7 long press, one mic rail, no raw pins, test switches off evidence: log-safety-stages.txt, b7-input-paths.txt, b7-raw-pins-code-only.txt, b7-test-switches.txt, b7-test-switch-defaults.txt, b8-claim-checks.txt
- [x] 11. B8 README and board-notes claims evidence: board-notes-as-read.md, b8-claim-checks.txt, readme-step7-lines.txt
- [x] 12. Findings table, counts, verdict, RESULT line evidence: step7-review.md
- [x] 13. Final audit of the reply evidence: audit-output.txt
