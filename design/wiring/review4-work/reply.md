Wiring review 4 is written: **FAIL**, with 3 major faults. All faults of review 3 (G1 to G11) are closed.

Review: design/wiring/wiring-review-4.md
Evidence: design/wiring/review4-work/ (15M)

Pin: HEAD 9d7745158773; git status shows no change on any judged path (`pin-status.log`, `pin-status-final.log`). I changed no design file, ran no check_band.py, used no browser and made no git write.

| Bar | Result | Checked |
|---|---|---|
| B1 | pass | 67 of 67 lines, 304 of 304 interface pads, 32 of 32 physical carriers |
| B2 | pass (I1) | 262 end, 105 tail-land and 42 node checks, 0 wrong; ring to case 28 of 28 |
| B3 | pass | rules check 17 of 17 at 0 and 0; my control copy fails (1 unconnected); 906 of 934 pads compared with the netlists, 0 wrong |
| B4 | FAIL | 99 of 99 joint rows read; paste openings read in the Gerbers |
| B5 | pass | 105 of 105 tail lands; J1 15 of 15 contacts, contact 1 at +Y |

G1 is closed: `ring-F_Paste.gbr` has a 0.300 x 0.440 opening on 15 of 15 ribbon lands, and the file equals a fresh export of the board.

The 3 major faults:
- **H1:** Steps 15 and 16 need features that no body file has. There are no side slits (the body files have only 2.1 x 0.6 floor slots, against a 2.5 mm foot). The block is not 4.17 mm and the cable fold pocket is missing. So the 15 ribbon joints and the 14 screen contacts cannot go into the ring.
- **H2:** Step 14 claims to prove ribbon lands B2 and B7 one by one, through the cell voltage at C83 and a beep from CP4. But FLEX2's own copper joins B2 and B7 (7 of 7 sizes), so either joint can be open unseen. A6 and A8 can also be open unseen, unless the lead orders an X-ray.
- **H3:** No step of the case procedure proves the two TH1 thermistor joints.

Minor faults:
- H4: case step 10 gives no solder or heat for the cell leads W5 and W6.
- H5: 45 of 50 bom.csv citations in the guide point at the wrong row.
- H6: the guide cites the wrong netlist line for J1 contact 3 (381; the right lines are 386 and 387).
- H7: step numbers in process.md and hotbar-joint.md are out of date.
- H8: band-interface.md section 7 still gives a 3 mm blade, a 0.05 mm stencil and alignment by the fixture outline.

The four checks:
- check_board (ring): sound. It fails a copy with a track removed and a copy with a wrong pad net. Run on a copy, because it writes ring-drc.json beside the board.
- check_wiring: passes, but it also passes 5 of 17 faulty copies, including a wrong net, a wrong face and a wrong tail land (I1).
- check_joints: passes, and catches the 15 paste openings removed, but it accepts "ok" as a check and "hot" as a heat (I2).
- check_assembly: passes, but it also passes G1 put back, swapped cell tabs and a citation to the wrong line (I3).
- The case check_boards passes and fails its broken copy.

Limits:
- I wrote the review in one pass after the checks, not bar line by bar line.
- Small read scripts ran without nice.
- J1's insertion side and contact 1 rest on my reading of the Hirose and Tailor drawings.
- I did not re-run the case model.

questions_for_owner: none
