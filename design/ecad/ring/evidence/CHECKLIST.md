# Checklist: ring schematic (brief from team-lead, 2026-11-10)

Written after the build had started (the rule asks for it first); items were taken from the brief and the builder rules.

- [x] 1. Read architecture.md A2 sections 2, 3, 7, 9, 14 and bom.csv. evidence: this run's reads; bom.csv changed on disk at 15:16 (R51-R56 removed), check_netlist reads the file live.
- [x] 2. Pin names from source documents, never memory: U1 nrf54lm20a-csp61-pins.csv; U2 DK PCA10184 p6 (evidence/dk_npm1300_left.png); U4 evidence/text_sgm38046.txt lines 195-246; mics evidence/text_mic.txt lines 857-875; U9 evidence/text_tpd4e05u06.txt lines 235-272; SW1 evidence/skrh_p2.png; SW2 evidence/evpav_p2.png; D1 evidence/grep_parts2.txt; ANT1 evidence/text_johanson.txt lines 76-91; DISP1 parts/ui-pass2.md section 1.
- [x] 3. netlist.csv with columns net, reference, pin_number, pin_name, pin_type. evidence: netlist.csv
- [x] 4. Provisional numbers for nPM1300, storage, J1 listed in open-pins.csv (plus Q1, Q2, LED1, M1, BT1, X1, X2). evidence: open-pins.csv
- [x] 5. nPM1300 passives: Nordic DK values opened (PCA10184 p6); inductor part numbers OPEN 12.2; NTC value OPEN 12.2. evidence: evidence/dk_npm1300_left.png, dk_npm1300_right.png
- [x] 6. gen_sch.py reads netlist + parts table, writes ring.kicad_sym, ring.kicad_sch + 7 sub-sheets, ring.kicad_pro. evidence: evidence/gen_t7.log
- [x] 7. check (1): section 7 signals, designators vs bom, every pin once, no single-pin nets, one power_out per rail, mic LR, H8 only to its cap. evidence: evidence/check_t7.log
- [x] 8. check (1) can fail: two broken copies exit 1. evidence: evidence/broken/exits.txt
- [x] 9. ERC 0 errors. evidence: erc-report.txt, evidence/erc-report_t6.txt
- [x] 10. ERC can fail: copy without PWR_FLAG gives power_pin_not_driven. evidence: evidence/broken/exits.txt
- [x] 11. PDF exported and every page read (8 pages). evidence: ring-schematic.pdf, evidence/pdf_t6_p1.png, pdf_t6_p2.png, pdf_t5_p3..p8.png, evidence/render_t7.log
- [x] 12. KiCad netlist export compared with netlist.csv inside check_netlist.py. evidence: evidence/check_t7.log last ok line
- [x] 13. sch-notes.md with blocks, values, additions, open pins, warnings, conflicts, risks, questions_for_owner, RESULT line. evidence: sch-notes.md
- [x] 14. No git, no installs, only files under design/ecad/ring. evidence: commands in this run
- [x] 15. Done-when command exits 0. evidence: evidence/done_when.log
- [x] 16. Lead message (2026-11-10): R51-R56 excluded with comment in check_netlist.py; CBL1 replaced by J2, J3 and wires W5-W10; U9 TPD4E05U06 DQA pin table read from codes_tpd4e05u06.pdf; designators frozen in bom_refs_snapshot.csv. evidence: evidence/check_t7.log, evidence/pdf_t7_p7.png, evidence/audit_final.log
