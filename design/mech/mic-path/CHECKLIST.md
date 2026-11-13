# Checklist: microphone sound path study (review finding F02)

Brief from the lead, 2026-11-11. Started 00:11:48 (printed by the first command). Limit 90 minutes.

- [x] 1. One recommended sound path, complete. evidence: mic-path.md sections 1, 4, 5.
- [x] 2. Rejected options table with (a), (b), (c), (d), each with a measured reason (plus e to h). evidence: mic-path.md section 7; check.log C02, C03, C29, C30.
- [x] 3. Part, maker, number, port position, package size and height from a datasheet copy in the project. evidence: datasheets/knowles-spk0641ht4h-1_chipsmall.txt lines 30, 345 to 348; evidence/pages/knowles-spk0641ht4h-1_chipsmall-p7.png. The reel suffix and distributor code are not confirmed (open item O1).
- [x] 4. Position of each microphone in model coordinates. evidence: check.log C10.mic_1, C10.mic_2.
- [x] 5. Path piece by piece, K8 answered. evidence: mic-path.md section 5; check.log C16 to C27.
- [x] 6. check_mic_path.py reads placement.csv and layers.json (and the STEP), rules quoted, one line per check, RESULT line. evidence: check_mic_path.py, check.log.
- [x] 7. check.log saved; tail -1 is RESULT PASS. evidence: check.log, evidence/check-final-exit.log.
- [x] 8. Larger parts at today's place: what collides and by how much. evidence: check.log C29 lines.
- [x] 9. Acoustic figures against PUI and the Knowles note; [ESTIMATE] tags; bench B7 named. evidence: acoustic.log, mic-path.md section 8.
- [x] 10. Change list, one line per change with file, line and present text. evidence: mic-path.md section 9 (35 lines).
- [x] 11. Every number sourced or [ESTIMATE]. evidence: evidence/audit.log.
- [x] 12. Block shape kept. evidence: mic-path.md section 2; no change of block size in the design.
- [x] 13. Only design/mech/mic-path/ written; no git command; no install; no browser; no folder deleted. evidence: commands of this run (all writes under this folder).
- [x] 14. Heavy commands with nice -n 19 and design/.venv/bin/python. evidence: commands of this run.
- [x] 15. Plain English, no em dashes. evidence: evidence/audit.log (dash count).
- [x] 16. Last line of mic-path.md starts RESULT:. evidence: evidence/audit.log.
- [x] 17. Final reply under 3,500 characters. evidence: evidence/audit.log (length).
- [x] 18. Final audit run and saved. evidence: evidence/audit.log.
