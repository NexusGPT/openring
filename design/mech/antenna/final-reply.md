F06 antenna study is written. The facts are measured on the inside model's STEP, and there is one recommendation: a bonded resin "radio corner" in the body, which the bench test proves or drops.

Files in design/mech/antenna/: antenna-study.md, measure_antenna.py with measure.log (last line `RESULT measured`), insert_check.py with its log, audit.py with audit_final.log, CHECKLIST.md.

New datasheets are in design/datasheets/antenna_*: the Johanson 2450AT18D0100001E datasheet (a 2023 5-page copy and a 2024 8-page copy), Infineon AN91445 and TI SWRA161B. Four more downloads (Nordic, Silicon Labs, Taoglas, Abracon) were blocked or wrong; I recorded them and did not work around them.

What I measured (measure.log):
- Metal is 0.050 mm under the antenna.
- The hand-end wall is 0.225 mm away and the thumb-side wall 0.450 mm.
- The screen panel covers the antenna's whole footprint (5.120 of 5.120 mm2). It is the driver ledge, 0.200 mm above.
- Above the antenna: foam 0.100, panel lower glass 0.400, an open 0.400 gap, adhesive 0.100 and cover glass 0.570 to 0.941.
- Body metal lies inside the design's own 4.2 x 4.7 keep-out.

What Johanson says (8-page copy):
- 72 % efficiency, measured on a 40 x 20 mm evaluation board.
- A "No GND on all layers" area of 4 x 6 mm (page 3).
- "no other metallic components like batteries and displays directly underneath antenna" (page 5).
- It gives no match values and asks for slots for a pi network.
- The two copies disagree on the minimum return loss: 6 dB in one, 10 dB in the other.

I claim no efficiency or range figure: there is no simulation and no RF measurement.

Recommendation, option (a4): the body inside X -14.8 to -10.6, Y 2.05 to the outer skin, all Z (20.265 mm3) becomes a bonded resin part, coloured, with no metal coat. ANT1 stays where it is. Its nearest body metal goes from 0.050 to 0.752 mm (insert_check.log lines 8 and 9). The two bond faces are 3.970 and 2.834 mm2.

Two problems stay open:
- The panel ledge and driver IC above the antenna. Only the screen maker can answer this.
- S15, the antenna pads that sit off the board. A pocket in the resin floor would allow an under-board mount, but the maker's 4.0 x 1.9 land pattern does not fit at this spot.

The study lists 15 file changes (file, present text, new text); I made none of them. architecture.md gained a section 17.17 while I worked, so the study proposes the new section as 17.18.

Bench test:
- Build one body. Measure it all metal (T1), then cut the corner off, bond the resin in and measure again (T2).
- Compare both with the bare board (T0): return loss on a network analyser, and RSSI at the nRF54LM20 DK.
- Pass line: return loss of at least 10 dB from 2400 to 2480 MHz while worn. On RSSI, T2 must be within 10 dB of T0 and at least 3 dB better than T1. The two RSSI lines are my [ESTIMATE].
- If T1 already passes, keep the one-piece body.
- The bench kit lacks a network analyser and Johanson's evaluation board.

For the owner, the look does change. The hand-end corner on the thumb side, about 4 x 5.3 mm, becomes a different material, with fine seams on the end face, the thumb side and the underside. The top stays all glass.

No git, no install, no browser. Side finding: the cover glass over the antenna is 0.570 to 0.941 mm thick, while architecture 17.1 says 0.4 mm. I reported it and did not fix it.

RESULT: done, commit none (the lead commits), measure.log ends RESULT measured
