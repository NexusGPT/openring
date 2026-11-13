# Checklist, firmware F5 (brief of the lead, 2026-11-11)

Started 01:55 (first command), limit 120 minutes. Base check on F4: `base_check_F4.log` (exit 0).

- [x] 1. firmware.md first lines say Version F5, with a numbered list "Changes from F4 to F5", one item per brief point 1 to 8, each naming its source. evidence: check_final.log (check 16 header and 8-item list), firmware.md lines 3 to 15
- [x] 2. P1a: CHARGE_CURRENT = 15,000 microamps; 4.35 V value 9 (p36); 10 percent (p37); charge time per size. evidence: check_final.log (checks 7, 16, 18e), calc.log, firmware.md 8.1
- [x] 3. P1b: discharge limit setting removed; IBATLIM 100 mA minimum (p28 to p30); action on BCHGILIMBATACTIVE. evidence: check_final.log (18d), firmware.md 8.1 last row and 8.7
- [x] 4. P1c: 8.4 rewritten, ship task after VBUS removal (p116), no timed hibernate. evidence: check_final.log (18c), run_broken_final.log (b3, b9)
- [x] 5. P1c: SHIP_SAMPLE keeps the factory flag, sample rings only. evidence: check_final.log (18c), firmware.md 1.2 and 9.3
- [x] 6. P1d: devicetree properties: only binding-confirmed ones plain, the rest TO CONFIRM with who; none invented (one added: the charger compatible, confirmed by research-npm1304.md line 10). evidence: firmware.md 8.1, 10.5 item 3
- [x] 7. P1: no "nPM1300" outside dated change notes. evidence: check_final.log (check 13: 0 uses), run_broken_final.log (b7)
- [x] 8. P2: motor on U11 via R61, R62, MOT_EN; 0.55 ms; no PWM. evidence: check_final.log (check 16 motor, 18a), run_broken_final.log (b2)
- [x] 9. P2: motor charge added to the gauge, allowance tagged ESTIMATE. evidence: check_final.log (16 motor rule, 18d), firmware.md 3.1 and 8.3
- [x] 10. P2: T-MOTOR reads the VBAT dip. evidence: check_final.log (16 T-MOTOR rule)
- [x] 11. P3: Knowles part; gain -11 dB; gain, level and clipping figures recomputed with arithmetic. evidence: check_final.log (18b), calc.log, firmware.md 4.1, run_broken_final.log (b6)
- [x] 12. P3: clock range and current from the datasheet copy. evidence: check_final.log (check 8 modes read from the Knowles copy; check 16 current 630 uA)
- [x] 13. P3: recording current 4.1 mA, dependents recomputed. evidence: calc.log, check_final.log (check 16 battery)
- [x] 14. P4: minutes on 18.2 mAh, hours as ranges across sizes, C-rates recomputed. evidence: calc.log, check_final.log (check 16 battery: 7 recording rows, 7 charge rows)
- [x] 15. P4: no "15 to 20 mAh" outside change notes. evidence: check_final.log (check 13), run_broken_final.log (b4)
- [x] 16. P5: R41 820 ohm, 1.50 mA; budget value kept, arithmetic corrected. evidence: calc.log (Light), firmware.md 3.2
- [x] 17. P6: VMOT, MOT_EN, U11; Q1 and D1 gone; microphone pins. evidence: check_final.log (18a: 20 named nets, no Q1 or D1 in the netlist)
- [x] 18. P6: pin table against netlist.csv by script. evidence: check_final.log (18a: 40 pairs, 29 pins), run_broken_final.log (b5)
- [x] 19. P7: factory flow by assembly steps 5, 16, 18, 20, 21, 24, 25, 26, 27. evidence: check_final.log (18f), firmware.md 9.3
- [x] 20. P7: K-A1 applied (USB path cannot write the boot loader; hardware lock TO CONFIRM). evidence: check_final.log (18f), firmware.md 9.2
- [x] 21. P7: first charge to 50 percent marked PROPOSED. evidence: check_final.log (18f)
- [x] 22. P8: one sentence at the top of section 7, sections 7.1 to 7.4 unchanged. evidence: check_final.log (18f), diff_sections_final.log (only lines 660 to 661 changed in section 7), run_broken_final.log (b8)
- [x] 23. Kept from F4: states, gestures, one control, recording rule, hard-wired light. evidence: check_final.log (checks 2, 14, 15, 17), diff_sections_final.log (no hunk in 2.1, 2.2)
- [x] 24. to 30. Check fails on each new fact. evidence: run_broken_final.log (b1 to b9, 0 cases differ), newcheck_on_F4.log (157 failures on F4)
- [x] 31. Replaced checks named in the notes. evidence: firmware-f5-notes.md section 6, oldcheck_on_F5draft.log
- [x] 32. Broken copy proof saved. evidence: run_broken_final.log, broken_final/
- [x] 33. Check exits 0 on the delivered file. evidence: check_final.log
- [x] 34. to 37. Notes: line ranges, arithmetic, TO CONFIRM with who, conflicts. evidence: firmware-f5-notes.md sections 1 to 4, diff_sections_final.log, calc.log
- [x] 38. Notes end with a RESULT line. evidence: tail of firmware-f5-notes.md (audit.log)
- [x] 39. Standing rules: no always-listening (check 14), one control, US 7 to 13, no browser, no web request, nice -n 19 on every python run, no em dash (audit.log dash count).
- [x] 40. Wrote only design/firmware.md, design/firmware-check.py, design/firmware-f5-notes.md and this folder; no git; no install; no folder deleted. evidence: audit.log (file list)
- [x] 41. Final audit and report: evidence audit.log (claims checked and unmatched count), final_reply.md, check_final2.log.
