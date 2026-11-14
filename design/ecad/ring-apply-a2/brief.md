# Brief: apply board A2 to the ring's board folder (lead, 2026-11-13)

Goal: Make board A2 the ring's main board in the design files, so the fabrication files, the placement table and every check describe the thin ring's board. The owner chose "Thin ring, 3.20 mm block (Recommended)"; the lead's decision is the last row of design/wiring/lead-decisions.md.

ROOT: .
PCB: design/ecad/ring/pcb
Your work folder (logs, notes): design/ecad/ring-apply-a2
Version: project commit 284a7770. Source board: design/ecad/ring-route-h/pcb/ring-thin-a2.kicad_pcb (read only).

Steps:
1. Keep the 4.17 mm fallback: COPY (never move) today's PCB/ring.kicad_pcb, PCB/placement-final.csv, PCB/drc-report.txt, the board pictures and the folder PCB/fab into a new folder PCB/fallback-417/ with a short README.md that says what it is (the routed board of ring board round 4, J1 and eight 0201 parts on the screen face, for the 4.17 mm block with the stock screen).
2. Put A2 in place: PCB/ring.kicad_pcb becomes a byte copy of the A2 board (the project and rules files are already identical: prove it by sha256). Update PCB/placement-final.csv for J1 and the eight parts (side, x, y, rotation, zone text, kicad_x, kicad_y) from the board itself by script, and prove every row of the table equals the board (a read-back script; one broken row must fail).
3. Regenerate what is made from the board with the folder's own tools (read each first): the rules check report, PCB/make_fab.sh and make_fab_docs.py (fabrication files, paste layers, drawings, pick-and-place), the board pictures (without any browser). Run PCB/check_board.py (it takes CHECK_BOARD_OUT for its output folder), PCB/check_footprints.py, and design/ecad/ring/check_netlist.py (run from design/ecad/ring). If check_board.py holds a declared exception or a table that must follow A2, change only that and list it.
4. The controlled lines: board-notes-r4.md section "The 8 controlled-line limits" names a read-back script and 8 limits. Run it on A2 and report each line against its limit. The display lines are 3.9 to 9.8 mm longer than on the old board and DECA is 8.4 mm longer: say plainly whether any limit is now exceeded.
5. Documents that state the old places. Update: design/mfg/specs/main-board.md (which face carries which parts, J1's place) and PCB/board-notes-r5.md (new: what changed from round 4, the checks, what is left). Then run from ROOT: design/.venv/bin/python design/wiring/build_wiring.py ; design/.venv/bin/python design/wiring/check_wiring.py --require-complete ; design/.venv/bin/python design/tools/check_bom.py ; design/.venv/bin/python design/mfg/assembly/check_joints.py ; design/.venv/bin/python design/mfg/assembly/check_assembly.py ; design/.venv/bin/python design/mfg/tools/check_docs.py . Where one fails because a document cites the old place of J1 or of the eight parts, correct that citation or sentence in the document (smallest change, old value kept as "REPLACED 2026-11-13 (was ...)" where the file uses that form) and list every changed line. The full rework of the build guide for the thin ring is a later job: do not rewrite steps beyond what the checks need; list what you saw that is now wrong.
6. Do not edit the inside model (design/mech) or the wiring's board plan tables beyond what a check forces; list every place where they disagree with A2 (for example the model's placement.csv rows of J1 and the eight parts).

Bar (it can fail):
1. PCB/ring.kicad_pcb is byte-identical to the A2 board; the rules check on it prints `Found 0 violations` and `Found 0 unconnected items`.
2. check_board.py, check_footprints.py, check_netlist.py end with their pass lines on the new board; the notes quote each last line.
3. The placement table equals the board (read-back script passes; its broken row fails).
4. The six checks of step 5 pass; the notes quote each last line. If one cannot pass without a change you may not make, stop and say which line of which file.
5. PCB/fallback-417 holds the old board, and the rules check on that copy still prints 0 and 0.

Owns: PCB (the folder and everything under it), design/ecad/ring-apply-a2, design/mfg/specs/main-board.md, the files build_wiring.py writes (design/wiring/product-wiring.csv and its drawings), and single lines of other documents under design/ that a check of step 5 forces (each listed).
Must not touch: design/ecad/ring-route-g and ring-route-h (read only); design/ecad/ring/netlist.csv, parts.csv and the schematic files (no pad net changes: if a check says the netlist differs, stop and report); design/mech; design/look; firmware; explorer; design/ecad/band/check_band.py (never run it); any process you did not start (a web server on port 8790); any browser; no purchase, sign-up or supplier contact.
Writes to: design/ecad/ring-apply-a2/notes.md (as you go).
Done when: a reader can run one script of yours (ring-apply-a2/check_all.sh) from ROOT and see bars 1 to 5.

Standing rules:
- You never run git (not even read commands). The lead commits.
- Shell: never send stderr to /dev/null; use 2>&1.
- Name every folder by its absolute path. Chain each git, rm or mv to its folder with `cd "<path>" && …` or `git -C "<path>" …`, and a new worktree or clone too (`git worktree add <dir> <ref> && cd <dir> && …`); never put `;` or a new line between a `cd` and a command that needs it.
- A helper's file names never start with REPORT, SUMMARY, FINDINGS or ANALYSIS; its final reply is its report. A report that cites a proof file quotes that file's last line verbatim; a count assembled from partial runs is not a result.
- Clock times are read from `date`.
- Heavy commands at `nice -n 19`. No foreground `sleep`; wait with `until <test>; do perl -e 'select(undef,undef,undef,20)'; done` for runs under about two minutes; a longer run goes to the background with an exit file and you end your turn naming the job and its output file.
- The Mac has about 5 GB of free disk: write nothing large; the fallback copy is the only big copy.
- No maker document, datasheet picture or maker text is copied into the board folder.
- Every number in the notes comes from a log line you name. Do not write a check's result before you have read it.

Limits: 2 hours from your first `date` (at the top of the notes).
End line: the last line of notes.md is `RESULT: <done|blocked>, <one sentence>`.
Your report ends with `questions_for_owner:` (`none` if there are none).
When you finish, your final reply is your report: it reaches the lead automatically. Keep it under 3,500 characters and put anything longer in a file it names. Do not also send it with SendMessage; use SendMessage only for a question or news while you keep working.
