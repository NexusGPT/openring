The microphone sound path for F02 is designed, and the fit check passes: `check.log` ends `RESULT PASS`, exit 0.

**Recommended path**
- **Part:** Knowles SPK0641HT4H-1, a top-port PDM microphone, 4.00 x 3.00 x 1.00 ±0.10 mm, port Ø0.25. Source: the datasheet copy in `design/mech/mic-path/datasheets/`, text lines 30 and 345 to 348. The port sits 1.030 mm from one end and 1.500 mm from the side; I read that from the drawing on sheet 6, rendered to `evidence/pages/`.
- **Place:** both microphones on the board's under face, port facing down. U5 sits at (-10.8, -4.8, 0.93) and U6 at (10.8, -4.8, 0.93).
- **Path:** port, then a foam gasket ring (bore 1.0), then a 1.0 mm hole straight down through the floor, then a membrane in a 2.0 x 0.10 seat flush with the underside. The bore is 0.43 mm long. It matches Knowles' advice (gasket cavity at least 1.0, case hole 1.0 to 1.5) and the PUI guide.
- **Conflict K8:** no opening in any side wall, so the two wall slots go.
- **Floor:** a 0.10 mm pocket under each microphone, leaving 0.30 of floor.

**Fit numbers (check.log)**
- Overlap with other parts: 0.0000 mm3.
- U5 sits 0.200 mm from LED1 and from U3, exactly at the 0.2 keep-out.
- Margin to the inside walls: 0.100.
- Gap from the lid to the pocket bottom: 0.13 nominal, 0.03 to 0.23 across the part's height tolerance.
- Air below each hole: confirmed on the exterior STEP.

**Larger parts at today's place (C29)**
- A 4.0 x 3.0 part cuts the -Y wall by 0.175 mm, and U5 touches LED1.
- A 4.0 x 2.0 x 1.1 part also sits 0.070 mm below the floor top.
- The fix is my new centres: 0.325 mm toward +Y for both, and U5 0.2 mm toward the fingertip.

**Rejected options (mic-path.md section 7)**
- (a) Bottom port with a board hole: it opens into the closed 0.10 foam layer.
- (b) Bottom port with a side channel: the only room is the 0.02 pad and the solder seal.
- (d) Part standing on edge: it needs 3.0 or 2.0 mm of height, and only 1.03 exists.
- (e) Second best: a 0.13 mm high slit to the end wall. It fits, but its flow resistance is 1052 times the bore's [ESTIMATE].

**Open problems**
- The part's height tolerance gives a gap from 0.03 to 0.23. No single gasket covers that, so the gasket is picked per unit from three thicknesses [ESTIMATE].
- The metal under each membrane seat is 0.20 mm thick, below the 0.30 stack floor. The body maker must accept that.
- No membrane part is chosen. The Gore GAW112 in the BOM is 0.24 thick and does not fit.
- I did not check the orderable code or stock of the part.
- Whether the finger or thumb covers the openings is [ESTIMATE]; bench B7 settles it.
- The acoustic estimate shows an open gasket leak would cut the high frequencies, so the gasket must seal.
- SNR drops from 67.5 to 64.5 dB(A).
- Sensitivity is 11 dB hotter, so the firmware gain must change.

**Changes for others:** section 9 of mic-path.md lists 35, none made. They cover 13 architecture lines, 8 bom.csv rows, placement.csv lines 11 and 12, thin.py, the exterior.py slots, the new 8-pin list against the old 5 provisional pins, the footprint, and four board parts to move (`board-conflicts.log`).

**Files** (all in `design/mech/mic-path/`): `mic-path.md`, `check_mic_path.py`, `check.log`, `acoustic.log`, `board-conflicts.log`, `CHECKLIST.md`, `datasheets/`, `evidence/` (with `audit.log`).

RESULT: done, check.log `RESULT PASS`, check_mic_path.py exit 0
