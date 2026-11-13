# Side slit as a grille: three variants at US 9 for the owner's pick (2026-11-13)

Owner today: "A: side slits (Recommended)", then "we can make it a design decision with a speaker grill maybe even ?". Each of the two floor slots opens through the block's long side wall; the opening is styled, the same on both long sides. Built on merged417flat US 9 (flat glass, 0.42 rolls). Evidence folder: design/look/s1/out/work-flat/slit/ (below: slit/). exterior.py and the inside model are NOT changed: slit/slit_grille.py loads exterior.py for merged417flat US 9, cuts the slit and the grille from the body before the glass split and writes the files into slit/kK/ under new names (ring-merged417flat-slitK-us9.step, .stl, .glb), with one more solid "slit_fill" (the black sealant, flush). merged417flat's own files are untouched.

## Facts used (from the files)
- Slot: X -3.55 to -1.45 (2.1 wide), 0.6 wide at |Y| 5.9, so inner edge |Y| 5.6 (design/mech/thin/thin.py line 76 `tail_y=5.9, slot_x=-2.5, slot_w=2.1`; line 539 the 0.6 slot box); 0.15 end clearance for the 1.8 neck (design/wiring/lead-decisions.md line 37).
- Slot bottom at US 9: Z -0.23 (thin.py line 113, `slot_z0`); fold top Z 1.430 (design/mfg/assembly/hotbar-joint.md section 2.1, line 48 "board land face Z 1.430").
- The through slit: X -3.55..-1.45, from |Y| 5.6 out through the wall and the band blend, Z -0.23 to 1.53 (0.10 above the fold), so the 1.8 neck slides in along Y with 0.15 at each end. One through opening per side; filled flush with black sealant (slit_fill).

## Axis: how much the functional slit is disguised
| Variant | What it is | Files (slit/) | Black fill, both sides (mm3) |
|---|---|---|---|
| 1 plain | the one filled slit per side | k1/ring-merged417flat-slit1-us9.* | 18.6738 (inspect-all.log) |
| 2 grille | the slit is the -X one of a row of three equal vertical windows 2.1 wide with 0.4 metal between (X -3.55..-1.45, -1.05..1.05, 1.45..3.55); the other two are blind, 0.20 deep along Y, filled black like the slit | k2/ring-merged417flat-slit2-us9.* | 21.6299 (inspect-fill-try4.log) |
| 3 speaker grille | one recessed black panel across the band's whole flat, X -3.55..3.55, 0.20 deep along Y, filled black flush, with 4 metal ribs 0.15 wide at pitch 0.60 (X -1.15, -0.55, 0.05, 0.65) standing in its middle; the slit is the plain -X end of the panel and its mirror at +X (X 0.80..3.55 black) balances it | k3/ring-merged417flat-slit3-us9.* | 21.7713 (inspect-fill-try4.log) |

## Wall and seat figures near the slit (slit/walls_slit.py, log slit/walls-slit.log, last line before the date `exit 0`)
Wall from the cavity envelope |Y| 6.45 outward along Y, X -4..4 every 0.25, Z 0.45..1.50 every 0.15 (the band of check (3)'s low and mid zones):
- merged417flat (no slit): thinnest 1.1019 (+Y) and 1.1123 (-Y) at X 4.00, Z 1.50; at the slit place 1.1500 (+Y) and 1.1458 (-Y) at X -3.50, Z 1.50.
- Variant 1: at the slit place 72 of 72 points open on each side (the through opening, by intent); elsewhere unchanged: 1.1019 / 1.1123.
- Variants 2 and 3: the slit 72 of 72 open on each side; behind the blind grooves / panel the wall is 0.9344 (+Y) and 0.9458 (-Y) at X 3.50, Z 1.50, against 1.1019 / 1.1123 in merged417flat. Against the reference of check (3) (merged32h, same place class): +Y and -Y wall low 0.6617 and mid 0.9250 (work-flat/measure-flat-final-us9.log), so 0.9344 and 0.9458 are not thinner than the reference's class minimum; the blind grooves open nothing (0 open points outside the slit X band, every file).
- Seat: the glass bottom is 3.7200 at X 0 Y 0 and at X -2.5, Y +-6.0, and the body top at X -2.5, Y +-6.8 is 3.7200, in all four files: the slit (top Z 1.53) is 2.19 under the seat.
- Not measured: the full check (3) and the other measure_417flat.py checks on these three files (not run: the owner picks first); the band channel itself (inside model, not touched).

## Pictures (slit/render_slit.py = work-flat/render_flat.py with slit_fill drawn near-black and views from each long side; no browser; opened with Read)
Per variant K: slit/slitK-us9-side_p.png (+Y side), slitK-us9-side_m.png (-Y side, the joystick side), slitK-us9-three_quarter.png, slitK-us9-close.png (+Y side round the slit). All 12 under 220 kB (`ls -la`, render-slit-all.log lists each exit 0).
- slit1-us9-close.png: one dark square window on the band's blend at one end of the band, the rest of the blend plain metal. slit1-us9-side_m.png: a small black square at the left end of the blend, the rest of the side unchanged.
- slit2-us9-close.png: three equal black windows side by side across the band with two narrow metal bars between. slit2-us9-side_m.png and slit2-us9-three_quarter.png: the same three windows on the joystick side; they read as a vent.
- slit3-us9-close.png: one wide black panel across the band's width with four thin metal ribs in its middle and plain black at both ends. slit3-us9-side_m.png: the same black band with the four ribs on the joystick side.
- Renderer limit: triangle edges show as faint lines; they are not shape.

## Pictures for judging the look (14:23 to 14:30, slit/render_smooth.py; no browser)
Renderer: a numpy software rasterizer written for this (no VTK or other 3D library is installed: slit/render-libs.log): z-buffer, per-pixel interpolated vertex normals (smooth shading, no facets or mesh lines), 2x supersampling, PIL. Body and joystick dark gloss metal (dark base, soft studio reflection, sharp highlight), glass black gloss, slit and grooves matte black (the sealant), light grey background, 70 px per mm (the grille X -3.55..3.55 is about 497 px wide in the side views and about 415 px in the three-quarter view). Opened with Read: slit1-side_m.png, slit3-three_quarter.png and compare-three_quarter.png of the final set, and slit2-side_p.png and slit3-side_m.png of the first set (same shapes, wrong captions); the other final files were not opened one by one.
- Variant 1 plain: slit/smooth/slit1-side_p.png (+Y side), slit/smooth/slit1-side_m.png (-Y, joystick side), slit/smooth/slit1-three_quarter.png. One small black square at the hand end of the band, high on the blend; the rest of the side is plain dark metal.
- Variant 2 three-window grille: slit/smooth/slit2-side_p.png, slit2-side_m.png, slit2-three_quarter.png. Three equal black squares in a row across the band, centred under the block.
- Variant 3 speaker grille: slit/smooth/slit3-side_p.png, slit3-side_m.png, slit3-three_quarter.png. One wide black panel across the band with four thin bright metal ribs in its middle; plain black at both ends.
- Side by side, same view and scale, labelled 1, 2, 3: slit/smooth/compare-three_quarter.png (32 px per mm).
- File sizes 195 to 538 kB (slit/smooth/sizes.log). One slip on the way: the first set of nine had their captions shifted by one variant (shell arrays in zsh start at 1); the shapes were right. They are kept in slit/smooth/wrong-labels/ and were all made again with the right captions (render-smooth-all.log, "relabel exit 0" nine times).
- What the pictures also show: the soft light band where the blend meets the taller wall is the fold of merged417flat (not part of the grille).

## What each is worse at
1. Plain: reads as an unexplained hole, off-centre (only at the hand end of the band, X -2.5) and alone; the most "repair-like" of the three; least sealant (18.67 mm3).
2. Grille: two more black windows to fill on each side (21.6299 mm3 of sealant); the metal behind the blind windows drops to 0.93 from 1.10; three square black windows read as a vent or an air intake rather than a speaker; the 0.4 bars between windows are narrow for a filled inlay (sealant must not bridge them).
3. Speaker grille: hardest to make: four free-standing ribs 0.15 wide on a curved blend (fine milling or EDM), sealant filled flush between them without smearing the ribs; the ribs cover only the middle 2.9 mm, so the 2.1 slit and its mirror stay plain black ends; same 0.93 wall behind the panel; most sealant (21.77 mm3).

## How it was built (tries)
- Try 1 (slit/try1/): variant 3 failed ("Cannot subtract shape from empty compound", one wide skin-and-box intersection came out empty); variants 1 and 2 wrote a STEP and STL holding the fill alone (the export rebuilt the assembly for each file and the solids moved to the first copy; slit/inspect-k1.log). Fixed: the recess cut gap by gap, one assembly for the three exports.
- Try 2: variant 2's blind grooves were left as open metal: in slit2-us9-close.png of that try (kept in slit/try2-k2/) they read only as two hair lines; try 3 fills them black like the slit.
- Try 3 (files kept in slit/try3/): the blind grooves and the panel existed on the +Y side only (slit/inspect-fill.log: no -Y piece); the skin made on the whole body came out empty on -Y. Try 4 makes it on a local piece of the body per side: 3 of 6 fill solids (variant 2) and 5 of 10 (variant 3) are on -Y (slit/inspect-fill-try4.log). The pictures of variants 2 and 3 were made again from the try-4 files.
- Work folder after this item: 170,380 kB (slit/du-after-slit.log), no file over 50 MB.

## questions_for_owner
1. Which of the three: plain slit, row of three equal black windows, or black speaker-grille panel with fine ribs (pictures above)?

RESULT: done, three slit variants (plain, three-window grille, ribbed speaker grille) are built at US 9 on both long sides with the slit filled black, measured (seat 3.7200 unchanged, wall behind the blind grille 0.9344 / 0.9458 against 1.10 without it, not thinner than merged32h's class minimum) and pictured from both sides, smooth shaded (slit/smooth/); the owner picks before any 7-size build.
