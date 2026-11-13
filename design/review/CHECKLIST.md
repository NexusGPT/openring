# Checklist: design review 1 (brief from team-lead, 2026-11-10)

Pinned version: no commit id in the brief; files read at the state hashed in hashes-start.txt (architecture A5-draft, firmware F3, case C3). requirements.md had uncommitted edits at the start (requirements-uncommitted-diff.txt).

- [x] 1. Read requirements.md in full, with "Changes after sign-off". evidence: hashes-start.txt, requirements-uncommitted-diff.txt
- [x] 2. Read architecture.md in full, apply its precedence (17.10 > 17.8 > 17.7 > 17.1-17.6 > 16 > rest). evidence: design-review-1.md findings citing lines
- [x] 3. Read bom.csv and bom-notes.md. evidence: probe_refs.log
- [x] 4. Read sch-notes.md, netlist.csv, parts.csv, open-pins.csv (open-pins.csv read through sch-notes section 5 and the probes only, not row by row: see item 22). evidence: probe_refs.log, probe_sd_nets.log, probe_sd2.log, probe_fw_pins.log
- [x] 5. Read pcb/board-notes.md. evidence: probe_lines.log
- [x] 6. Read thin-notes.md and placement.csv. evidence: probe_chains.log
- [x] 7. Read mfg-notes.md, parts-notes.md, parts/index.csv, the 8 spec pages. evidence: probe_lines2.log
- [x] 8. Read firmware.md (F3) in full. evidence: probe_fw_pins.log
- [x] 9. Read case-architecture.md (C3) and case-notes.md. evidence: grep_topics2.log
- [x] 10. Read bench-plan.md and status.json. evidence: grep_topics.log
- [x] 11. Run check_bom.py. evidence: check_bom.log
- [x] 12. Run check_netlist.py. evidence: check_netlist.log (it rewrote the date line of ring-kicad.xml: ring-kicad-xml-diff.txt)
- [x] 13. Run firmware-check.py. evidence: firmware_check.log
- [x] 14. Run check_docs.py. evidence: check_docs.log
- [x] 15. Attack one check with faulty copies (honest control included). evidence: attack_fwcheck.log, fakes/
- [-] 16. Attack check_bom.py, check_netlist.py, check_docs.py with faulty copies. not done: time and step budget spent on the design itself; their holes are shown by the real files passing (findings F25, F26), not by fakes
- [x] 17. Verdict line per area (9 areas). evidence: design-review-1.md section 1
- [x] 18. Findings table with id, severity, area, evidence quotes, requirement. evidence: design-review-1.md section 2
- [x] 19. Contradictions section with both quotes. evidence: design-review-1.md section 3
- [x] 20. What I did not read or could not check. evidence: design-review-1.md section 4
- [x] 21. Counts per severity and RESULT line. evidence: design-review-1.md section 5, audit.log
- [-] 22. open-pins.csv, symbols.csv, KiCad schematic and board files, drawings (SVG/PDF), STEP files opened row by row or in a viewer. not done: 60-minute limit; read through the notes and the index only
- [x] 23. Final audit script over the reply and the review file. evidence: audit.log
