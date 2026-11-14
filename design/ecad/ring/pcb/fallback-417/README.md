# fallback-417: the ring main board for the 4.17 mm block

This folder keeps the routed board of ring board round 4 (board-notes-r4.md), as it stood before board A2 replaced it on 2026-11-13: J1 and the eight 0201 parts (C1, C2, C5, C7, C14, FB1, R71, R72) on the screen face, for the 4.17 mm block with the stock screen.

- ring.kicad_pcb, placement-final.csv, drc-report.txt, board-top/bottom pictures, pictures/, fab/: byte copies of the board folder's files at that time (sha256 lists in design/ecad/ring-apply-a2/logs/fallback-sha-*.log and fallback-tree-*.log).
- ring.kicad_pro, ring.kicad_dru: byte copies of the board folder's project and rules.
- fp-lib-table: written for this folder; it points at the board folder's OpenRing.pretty one level up and at design/ecad/band, so the rules check here finds the same libraries.
- Rules check on this copy: design/ecad/ring-apply-a2/check_all.sh (bar 5).
