# Look notes, case C5b (2026-11-11)

C5 (57.7 x 52.1 x 43.0 mm, a soft cube) was not accepted; its files are in `design/case/out/old_C5/` and `design/case/look/old_C5/`. C5b takes size as the first rule.

## Size and radii (numbers from out/case_size.txt, out/case_params.json, look/explore2.log)
- Outside: 45.5 x 45.9 x 41.4 mm (limit 45.5 x 46.0 x 41.5; C4 43.2 x 44.0 x 40.6; +2.3, +1.9, +0.8 mm).
- Plan: superellipse, no straight segment, smallest radius of curvature 5.6 mm at the -X corners (the 40 mm cell's corners and the 45.9 mm width set it; look/explore2.py searched for the largest). This is far from the soft triangle of the reference.
- Bottom edge: elliptical, 7.5 mm wide x 3.1 mm high (a taller edge would cut the cell's lower corners). Base crowned by 0.44 mm.
- Top edge: elliptical, 10.0 mm wide x 1.8 mm high; lid crowned by 0.68 mm. The lid is the whole top; the seam (0.3 mm gap) is in the straight wall at z = 37.66 / 37.96 mm; above it the wall runs 0.5 mm before the top edge starts.
- Straight wall: 85.7 percent of the height is within 5 degrees of vertical (the C5 rule of 40 percent was dropped on the owner's instruction).
- USB-C: recessed rounded slot (radius 0.9 mm) with a curved 0.9 mm lead-in, socket front 0.3 mm behind the skin at its outermost corner (1.4 mm at the middle of the mouth, because the skin curves); light: one 1.0 mm dot. Pivot hidden (pin in the lid, 1.3 mm under the crown), base magnet under a 0.5 mm skin, no screw, no latch.
- Dish: rolls into the wall with a 1.8 mm radius; pocket and notch with rounded corners.

## What I judged in each picture (renderer look/render.py: numpy, 1600 x 1200 from 3200 x 2400, no browser)
- case-closed.png: one continuous skin, a fine even seam, no step, the lid reads as the top of the object. It still reads as a soft rounded block, not a pebble: the straight wall and the 5.6 mm corners make it boxy. Silver is lighter than C5 but still a grey, flat satin; the reference's gradient (bright top, darker flank, soft reflection) is only partly reached.
- case-open.png: lid swung 100 degrees at the corner pivot, dish and post white, ring black, gold pins visible; rim clean (no glide, magnet, screw). The well is deep (the ring stands 29 mm tall), nothing like the shallow dish of the reference.
- case-open-empty.png: the same without the ring: post, pin lug, pocket.
- case-side.png: even dark seam line (the C5 white broken line was the background seen through the gap; the picture now has a dark liner behind the gap, as the real case has an interior), wall, rounded bottom edge, crowned lid. Slight ripples in the wall shading remain (tessellation of the lofted wall, not a measured surface defect).
- case-compare-c4-c5b.png: C4 (left) and C5b (right) at one scale with a 20 mm bar; C5b is 2.3 mm longer, 1.9 mm wider, 0.8 mm taller and softer at the edges; the form is the same family as C4.
- case-in-hand.png: the case beside a 1 euro coin and a faint 80 x 45 mm palm outline; the palm outline is weak.

## Still not as good as the reference, and why
- Not a flat pebble. The ring lies flat around the post with its 29.3 mm block standing up (14.65 mm each side of the band's middle), so the inside is at least 29.3 mm high. With the cell under the ring floor as modelled the smallest height of this concept is about 39.4 mm [CALC from the stack: plate 1.5, cell 8.5, board 1.0, socket 3.31, gaps, floor 1.8, band 8.0, block above the band 14.65, rim 0.3, gap 0.3, lid 3.0, flat bottom and top]; C5b is 41.4 mm because the bottom edge and crown need a 3.0 mm plate and the lid crown 3.4 mm. With the cell BESIDE the ring instead of under it [ESTIMATE, not modelled]: the block hangs below the band into its pocket, so the floor can drop to 1.5 + 0.4 + 14.65 - 4.0 = 12.5 mm and the case to about 12.5 + 4.0 + 14.65 + 0.6 + 3.0 = 34.8 mm (about 35 mm), but the plan grows to about 70 x 46 mm (cell 40 x 23 mm plus the 29 mm well): lower, not smaller, still not a flat pebble.
- Plan corners 5.6 mm (the reference has no corner under about 20 mm): the cell's four corners sit 2.7 mm above the base and 1.15 mm inside the skin.
- The lid is the whole top, but with the 3.4 mm thickness and 0.5 mm wall it reads as a lid on a block more than as the upper half of a pebble.
- USB-C mouth: a recessed slot, but dark and hard-edged in the picture.
- Metal: a simple studio reflection, not a measured finish; the real body is a moulded polymer with a metal-look layer (case-architecture.md section 7), to confirm with a maker.
- No shadow of the lid on the rim; no reflection of the ground in the case.

## Checks
case_check.py tests 1 to 7 as C4; new tests 8 (no planar face on the outside skin; run once on the C4 shape it finds 10), 9 (information only now) and 10 (seam gap 0.3 mm, lip 0.3 mm, dot 1.0 mm). Result lines in look/check_final.log.

RESULT: done, outside 45.5 x 45.9 x 41.4 mm (C4 43.2 x 44.0 x 40.6 mm); case_check last line "case_check: PASS, 1842 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]"; pictures in design/case/look/: case-closed.png, case-open.png, case-open-empty.png, case-side.png, case-compare-c4-c5b.png, case-in-hand.png
