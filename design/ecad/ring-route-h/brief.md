# Brief: board A2 of the thin ring (lead, 2026-11-13)

Goal: Make "board A2" of the ring's main board. Start from board A1 (J1 already on the under face). Move the eight 0201 parts of the screen face to the under face and re-route their nets, so that nothing but flat test pads is left on the screen face. Reason: with a panel of 0.80 mm the thin ring leaves 0.10 mm above the board (design/mfg/specs/screen-panel-work/connection-options.md lines 28 to 40). The owner chose "Thin ring, 3.20 mm block (Recommended)" and said "MUCH THINER NEEDED".

Project root (ROOT): .
Your folder (H): design/ecad/ring-route-h

Version: project commit b62e7d09. Base board: design/ecad/ring-route-g/pcb/ring-thin-a1.kicad_pcb with its .kicad_pro and .kicad_dru (read only; copy them into H as H/steps/h00-base.kicad_pcb).

The eight parts: C1, C2, C5, C7, C14, FB1, R71, R72 (places today: design/ecad/ring/pcb/placement-final.csv lines 4, 5, 6, 9, 10, 11, 45, 46). Their nets: DECA, DECD, GND, VDD_1V8, VSET1, VSET2. They were under the board before and were moved up to close the routing (design/ecad/ring/pcb/board-notes-r2.md step 13; design/ecad/ring-route-c/notes.md lines 13 to 18 and 50: C7 walled MIC_A_CLK). Since then three spare pins were dropped and two nets moved (design/ecad/ring-route-f/pin-changes.md), so the copper differs.

What you may change: the place and rotation of these eight parts on the under face (each keeps its nets; C7 should stay within 3.0 mm of U1 ball A8; each decoupling capacitor stays as near its ball as you can, state each distance); any track or via of any net except the antenna nets and the USB pair, if a move needs it. What you may not change: any other part's place, side or rotation; any pad's net; J1; the 12 test pads; layers, stack, rules file, rule areas, outline.

Keep-free zones on the under face (no part): X -3.5 to -0.9 with Y 3.4 to 5.6 and Y -5.6 to -3.4 (ribbon folds, design/mfg/specs/main-board.md line 37); the antenna copper-free zone; every courtyard of a part already there.

Bar (it can fail):
1. On H/pcb/ring-thin-a2.kicad_pcb the rules check (your scripts/drc.sh set-up of route-g, project and rules beside the board) prints `Found 0 violations` and `Found 0 unconnected items`.
2. The screen face holds no footprint with a body: only test pads. The eight parts are on the under face, courtyards clear, outside the keep-free zones.
3. Your compare script (extend route-g's) against the A1 board shows: every other footprint identical in place, side, rotation and pad nets; the eight parts' pad nets identical; antenna nets' copper and the USB pair's copper item-for-item identical; rule areas, outline, layers, rules unchanged.
4. One broken copy proves the compare script can fail (leave C7 on the screen face: the script must name it).
If the board does not close inside the limit: stop at your best board, write its two rules-check figures, each open net and what blocks it, and which of the eight parts could move and which could not. A partial result is useful: say plainly how many of the eight are under the board on a board that still passes 0 and 0.

Owns: H and everything under it. Nothing else.
Must not touch: every path outside H (route-g and the base board folder are read only; never run design/ecad/band/check_band.py). No process you did not start (a web server runs on port 8790). No browser of any kind. No purchase, sign-up or supplier contact.
Writes to: design/ecad/ring-route-h/notes.md (written as you go).
Done when: a reader can run from ROOT one script of yours (H/scripts/check_final.sh) and see bar items 1 to 4.

Standing rules:
- You never run git (not even read commands). The lead commits.
- Shell: never send stderr to /dev/null; use 2>&1.
- Name every folder by its absolute path. Chain each git, rm or mv to its folder with `cd "<path>" && …` or `git -C "<path>" …`, and a new worktree or clone too (`git worktree add <dir> <ref> && cd <dir> && …`); never put `;` or a new line between a `cd` and a command that needs it.
- A helper's file names never start with REPORT, SUMMARY, FINDINGS or ANALYSIS; its final reply is its report. A report that cites a proof file quotes that file's last line verbatim; a count assembled from partial runs is not a result.
- Clock times are read from `date`.
- Heavy commands at `nice -n 19`. No foreground `sleep`; wait with `until <test>; do perl -e 'select(undef,undef,undef,20)'; done` for runs under about two minutes; a longer run goes to the background with an exit file and you end your turn naming the job and its output file.
- The Mac has about 10 GB of free disk. Keep H under 150 MB and at most 12 step boards.
- No secret, key, server address or e-mail in any file or output.
- Every number in notes.md comes from a log line you name. Do not write a check's result before you have read it.

Limits: 3 hours from your first `date`, written at the top of notes.md.
End line: the last line of notes.md is `RESULT: <done|blocked>, <one sentence>`.
Your report ends with `questions_for_owner:` (`none` if there are none).
When you finish, your final reply is your report: it reaches the lead automatically. Keep it under 3,500 characters and put anything longer in a file it names. Do not also send it with SendMessage; use SendMessage only for a question or news while you keep working.
