# Checklist (ring-route-h, board A2)

- [x] 1. A1 board, project and rules copied into H as steps/h00-base.kicad_pcb. evidence: logs/base-copy-sha.log
- [x] 2. Bar 1: rules check on pcb/ring-thin-a2.kicad_pcb, project and rules beside it, Found 0 violations / Found 0 unconnected items. evidence: logs/final-drc.log
- [x] 3. Bar 2: screen face holds only test pads. evidence: logs/final-compare.log check 2b
- [x] 4. Bar 2: the eight parts on the under face. evidence: logs/final-compare.log check 2a
- [x] 5. Bar 2: courtyards clear, outside the keep-free zones (both fold zones, antenna zone). evidence: logs/final-compare.log check 2c, logs/final-drc.log
- [x] 6. Bar 3: every other footprint identical (place, side, rotation, pad nets), J1 and 12 test pads included. evidence: logs/final-compare.log check 1
- [x] 7. Bar 3: the eight parts' pad nets identical. evidence: logs/final-compare.log check 2a
- [x] 8. Bar 3: antenna nets and USB pair copper item for item identical. evidence: logs/final-compare.log checks 3a, 3b
- [x] 9. Bar 3: rule areas, outline, layers, rules unchanged. evidence: logs/final-compare.log checks 5a to 5e
- [x] 10. Bar 4: broken copy with C7 on the screen face, script names C7. evidence: logs/final-broken-C7.log
- [x] 11. C7 within 3.0 mm of U1 A8 (DECA pad, plan view): 2.328. evidence: logs/final-compare.log check 2d
- [x] 12. Each decoupling capacitor's distance to its ball stated. evidence: logs/final-compare.log check 2d, notes.md
- [x] 13. One script from ROOT shows bars 1 to 4: scripts/check_final.sh. evidence: logs/final-drc.log, logs/final-compare.log, logs/final-broken-C7.log
- [x] 14. Partial-result count stated: 8 of 8. evidence: logs/final-compare.log check 2a
- [x] 15. At most 12 step boards, H under 150 MB. evidence: logs/audit.log (listing and du)
- [x] 16. No git run in this job; only H written. evidence: notes.md; logs/audit.log re-hashes the A1 board
- [x] 17. notes.md start time, steps, last line RESULT. evidence: notes.md
- [x] 18. Final audit. evidence: logs/audit.log
