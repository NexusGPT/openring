# Inside, layout round 1, informed lane: notes

Mode: INFORMED (I saw the current Inside captures, the stage capture open-live.png, and the Home capture). Rung: LAYOUT (labelled boxes, no data, no styling).
Both boards keep the app-level layout L1 (ring left, reading panel right) and the area tabs, so Inside stays consistent with Home.

## The movie (what both boards must carry)
- The owner taps the Home tile "Inside". The ring is where it was on Home, same angle: no jump.
- The owner presses Open: the ring opens into 5 layers with an animation. Pointing at a part shows its name tag.
- The owner clicks a part (in the ring, in a layer row, or from search). The camera eases to it and a card opens.
- A maker arrives from Files ("For a manufacturer") or a Parts row ("show in the ring", `?part=`), goes straight to the chosen part, picks a ring size for the body, and downloads the drawing, specification, STEP and STL.

## What the current screen does wrong (what both boards fix)
- The selected card is a wall of text (a three-line serif headline, then long rows); the maker's data is hidden under a closed "Exact data" fold at the bottom of the screen.
- No downloads for a maker; no way to find "the parts a maker builds" without knowing their names.
- The open/close control is a slider with two labels; the brief asks for one control.
- The "not drawn in 3D" fact is not said.

## IA · "The ring stays whole" (board-a.html)
- Thesis: the ring stays whole on the left so you always see where a part sits; the chosen part's card on the right holds plain words first, then a "For a maker" block one step below.
- Named axis: what the stage shows once a part is chosen. IA: the whole ring, with the part lit in place.
- Worse at: reading the drawing. It is a small preview in the side card, so checking a measurement means opening the PDF in a new tab; at 1280 x 800 the links at the bottom of the card need a short scroll.
- Lock amendment: none.
- Data it needs: per made-to-drawing part: a "made to drawing" flag on its parts line; drawing PDF + a page-1 picture for the preview; one-page specification PDF + 4 summary fields (material, tolerance, finish, quantity per ring); STEP; STL; for the body, one STEP and one STL per ring size and the list of sizes. A small picture per made part for the "Made to drawing" list.
- Links (journey step → control on the board):
  - in, Home tile "Inside" (J1.2) → frame 1 as a whole.
  - J1.2 open layer by layer → "Open / Close button" (stage, bottom left) + "Layers of the ring" rows (panel).
  - J1.3 click a part → the ring (stage), a layer row, "Find a part", "Made to drawing" rows → frame 2 card.
  - J1.4 the part's source → "Links out: Source file ↗" (panel, bottom).
  - in, Parts row "show in the ring" / an Electronics part (`?part=`) → frame 2 directly.
  - out, Parts screen at the part's line → "Links out: This part in the Parts list →".
  - out, Files group "For a manufacturer" → "Links out: All maker files →".
  - out, Parts (small parts not drawn) → "Not drawn in 3D" line (frame 1).

## IB · "The part on the bench" (board-b.html)
- Thesis: choosing a made part puts that part alone on the stage, big, turnable, with its measurements drawn on it and its drawing one click away in the same space; the ring shrinks to a corner inset; the panel keeps plain words and the four files.
- Named axis: what the stage shows once a part is chosen. IB: the part itself, on its own, with its measurements; the ring is a small inset.
- Worse at: seeing the part in its place. While a part is open the ring is a small corner picture, so seeing how parts fit together, or hopping to a neighbouring part, takes a step back to the whole ring first.
- Lock amendment (the one allowed): L1 says the 3D ring is always on the left. In IB the ring stays on screen but shrinks to an inset while a made part is open (a bought part keeps the whole ring). Cost: no large in-place view while reading a part; the part-to-ring transition is one more animation to build well.
- Data it needs: everything IA needs, plus per made part: 3 to 5 key measurements with their two end points on the 3D part (for the measure lines); the drawing as an image the stage can zoom (SVG or a large PNG), not only a PDF; for the body, one 3D model per ring size so the part on the stage changes with the size.
- Links (journey step → control on the board):
  - in, Home tile "Inside" (J1.2) → frame 1 as a whole (same as IA).
  - J1.2 open layer by layer → "Open / Close button" (stage, bottom left) + "Layers of the ring" rows.
  - J1.3 click a part → the ring, a layer row, "Find a part", "Made to drawing" rows → frame 2.
  - J1.4 the part's source → "Links out: Source file ↗" (panel, bottom).
  - back to the ring → "Where it sits" inset (stage, bottom left), view switch "In the ring" (stage, top), Esc or a click on empty space.
  - in, Parts row "show in the ring" / an Electronics part (`?part=`) → frame 2 directly.
  - out, Parts at the part's line → "Links out: This part in the Parts list →"; Files "For a manufacturer" → "Links out: All maker files →"; Parts (small parts not drawn) → "Not drawn in 3D" line.
- Frame 2 shows, as the lead asked: where the dimensioned drawing sits (the stage itself, switch "Its drawing"), where the four downloads sit (panel, "The four downloads"), and the one-click way back (the "Where it sits" inset).
- At rest (frame 1) IB is the same as IA on purpose: the choice is only about what happens once a part is chosen.

## Killed before showing
- "Explore / Make switch": a mode switch at the top of Inside, the "Make" side a shelf of made parts with their files. Killed: it makes two screens out of one, the maker loses the 3D view, and the shelf repeats the Files group "For a manufacturer". Its one good idea (a short list of made parts as the maker's front door) is kept in both boards as the "Made to drawing" rows.
- "Full-width ring with floating cards": the stage over the whole width, layers and the card floating over it. Killed: the cards cover the ring, it breaks the consistency with Home the owner asked for, and floating panels read as a dashboard.

## Viewports (estimated from the box heights; the boards are drawn at 1440 x 900 only)
- 1440 x 900: both frames fit without scroll in the panel.
- 1280 x 800: the stage narrows; in IA the "Links out" row of frame 2 needs a short scroll in the panel; in IB the four file rows fit, the links need a short scroll. No phone layout (signed spec).

## Manifest lines (also written to alternatives.json in this folder, allowed by the lead 2026-11-10)
{"id":"IA","rung":"layout","title":"The ring stays whole","axis":"what the stage shows once a part is chosen: the whole ring, part lit in place","entry":"board-a.html","worse_at":"reading the drawing: a small preview in the side card; at 1280 x 800 the links need a short scroll","links":"Open/Close (stage) · layer rows · Find a part · Made to drawing rows · Source file ↗ · Parts list → · All maker files →"}
{"id":"IB","rung":"layout","title":"The part on the bench","axis":"what the stage shows once a part is chosen: the part alone with its measurements, ring as inset","entry":"board-b.html","worse_at":"seeing the part in its place: the ring is only a corner picture while a part is open","links":"Open/Close (stage) · layer rows · Find a part · Made to drawing rows · Where it sits inset · view switch In the ring · Source file ↗ · Parts list → · All maker files →"}

## Findings for the lead
- Count conflict in the sources: docs/DATA-MAP.md row "parts" says 77 lines and docs/JOURNEYS.md says 77; the brief and the Home capture say 78. The boards name no count, so they are not affected.
- The surface contract has no "domain formula" category; on a layout rung nothing needs it.
- Renders: both boards shot headless at 1440 x 900 and full page with the capture tool (file:// pages, no server started); I looked at both pictures. Shots in <scratch>/ (a-full.png, a-900.png, b-full.png, b-900.png).

## questions_for_owner
- For the body, which ring sizes must the maker files cover? Both boards show one size picker; the list of sizes must come from the design.

RESULT: done, IA "The ring stays whole" and IB "The part on the bench" differ on what the stage shows once a part is chosen (the whole ring with the part lit, or the part alone with its measurements and the ring as an inset).
