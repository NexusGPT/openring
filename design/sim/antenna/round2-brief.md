# Antenna simulation, round 2: the lead's rulings

For: the helper antenna-sim. From: the lead, 2026-11-13. Round 1: `design/sim/antenna/antenna-sim.md` (read in full by the lead).

What round 1 showed: the solver runs (about 1.5 to 3 minutes per run on the lean mesh when the server is free), but the tool is not validated: the chip antenna's inside is not published, one free number could not put the model's resonance at the maker's 2.45 GHz, and the ring cases (8.3 percent and 2.0 percent radiated, input resistance under 1 ohm) therefore decide nothing. The owner asked for a simulation that properly tests the design. Round 2 must end with a validated tool, or with the exact reason it cannot be validated.

You keep the rules of round 1 (pre-registration before runs, no pass line changed after a run, every number from a kept output, "simulated, not proven on hardware"). New pass lines and methods are written into your file with a time stamp before the first round 2 run, as a section "Round 2 pre-registration".

## Part 1. Validate the tool with an antenna whose geometry is fully published (H1b)
The solver itself must be shown right on a known antenna before any chip model is trusted. Use a printed 2.4 GHz antenna whose every dimension, board and measured result are published by its maker (for example a Texas Instruments or Silicon Labs or Nordic application note on a printed inverted-F or meander antenna; look in `design/datasheets/antenna_*.pdf` first: antenna_ti_swra161b.pdf, antenna_silabs_an1088.pdf, antenna_infineon_an91445.pdf, antenna_nordic_nwp017.pdf, antenna_abracon_design_guide.pdf; fetch another maker's note if none gives full dimensions with a measured S11). Pass line, written first: resonance within 3 percent of the published one, and the published bandwidth or return loss at the band edges within a tolerance you state with its reason. No free parameter. If this fails, stop and report: the tool or your use of it is wrong.

## Part 2. A calibrated stand-in for the chip antenna (H1c)
The chip's inside stays unknown, so the chip model is a stand-in, calibrated on the maker's evaluation board and then frozen. Free parameters: at most three (for example the radiator's length, its height in the block, the permittivity). Calibration targets (all from the maker's sheet, 8-page copy pages 1 and 4): S11 minimum at 2.45 GHz; return loss at 2.40, 2.45, 2.50 GHz; efficiency 72 percent; peak gain 1.5 dBi. Pass line, written first: S11 minimum in 2.44 to 2.46 GHz, return loss at least 10 dB at 2.45 GHz and at least 6 dB at 2.40 and 2.50 GHz, efficiency 52 to 92 percent, peak gain -1.0 to +4.0 dBi (the round 1 lines). Say plainly in the file: a calibrated stand-in reproduces the maker's board; how the real part reacts to nearby metal can differ, and that limit stays. Test the stand-in once on a second published condition if the maker gives one (the "thin edge" mounting of the 8-page copy page 5: say what it publishes and whether the stand-in agrees), as a check that was not used for calibration.

## Part 3. The ring (H2, same pass line as round 1: return loss 6 dB or better across 2.40 to 2.48 GHz after a three-part match, and at least 10 percent of the accepted power radiated)
Board and mount: read them from `design/wiring/ring-board-plan.md` and `design/wiring/ring-board-plan-work/placement-plan.csv` as they are on disk when you start part 3 (the antenna is now at (-10.80, 5.25), the copper-free zone X -13.60 to -8.75, Y 3.10 to 6.30, the resin corner to X -8.60, the floor pocket X -12.60 to -9.00; values on disk win over this text). Mesh: first a mesh study on case A (two meshes; the second with the finger and the body interior twice as fine): if the radiated share or the input resistance moves by more than 20 percent, use the finer mesh for all cases.
Cases, each with S11 before match, input impedance, best three-part match, S11 after match, radiated share at 2.40, 2.44, 2.48 GHz:
- D: the board and antenna in free air (control).
- A: as designed, metal body with the floor pocket, on the finger.
- A0: case A without the finger.
- B: resin corner as the plan gives it, on the finger. B0: without the finger.
- B2: resin corner, and no metal and no resin floor under the antenna at all down to the liner (say what the model then has under the antenna).
- E: the antenna standing on the board's screen face under the glass, in the same corner, with the screen's glass and the resin corner around it (the panel's active area does not cover that corner: check the panel outline in `design/mech/thin/placement.csv`; say if it does). State what would have to change in the block stack for this, in mm, from `design/architecture.md` 17.2.
- F: one more place or mount of your own choice that the numbers of the first cases suggest, with a one-sentence reason.
For the best case: the sensitivity to the two things the design can still change (the size of the resin corner in 1 mm steps along X, and the gap between the antenna and the nearest metal).

## Part 4. What the design should do
One table: case, radiated share, return loss after match, pass or fail. Then, in plain words: which mount the numbers support, what it costs (size of the resin corner, thickness, parts moved), and what stays unknown until a built unit is measured (with the measurement). If no case passes, say so first and give the best radiated share reached and by which change.

## Limits and rules
- Up to 60 solver runs, 4 hours. Each run at most 30 minutes; run niced; if the server is loaded (load average over 40), wait in loops and say so; a run stopped for load does not count.
- On the server only your own folder /root/ring-antenna-sim; delete nothing by pattern; never touch a container, image, folder or process that is not yours.
- No secret, no server address in any file or output. No git. No browser. `2>&1`, never /dev/null. Absolute paths.
- Maker documents: numbers only, at most 25 quoted words.
- Append to `design/sim/antenna/antenna-sim.md` (sections "Round 2 ..."); keep round 1 unchanged. New last line: `RESULT: <done|blocked>, <one sentence: H1b and H1c confirmed or not, and for each ring case its radiated share and verdict>`.
- Your final reply is your report (under 3,500 characters); do not send it a second time by message. Send the lead ONE message when part 2 has its verdict.
