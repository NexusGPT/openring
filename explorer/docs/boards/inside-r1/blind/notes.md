# Inside, round 1, blind layout c: "The ring above, the drawing below"

## Idea (checkpoint, written before drawing)
1. At rest the screen is the usual app shape: the ring in 3D on the left, a calm panel on the right with a search and the 5 layers as a list.
2. Clicking a made-to-drawing part keeps the ring on screen (eased to the part) and slides a drawing strip up under it: the part's flat views with its main sizes.
3. The panel stays plain words first, then a "For the maker" block one step below: the specification lines and the four files to take.

## The movie
- The owner arrives from the Home tile: the ring sits closed on the stage; the panel shows the title, the count of parts drawn in 3D, a search, and the 5 layers.
- They press "Open the ring": the layers move apart (the band's parts outward). Pointing shows a name tag.
- They click the body shell (made to drawing): the view eases to it, the rest fades, and a drawing strip slides up under the ring with front, side and top views plus sizes. The panel reads: name, "Made to drawing", two plain lines; below a rule, the specification and four file buttons.
- A maker arriving from Parts "show in the ring" lands directly in that state and takes the STL for one ring size.
- Click on empty space or "x" clears: the strip slides down, the ring takes the full stage again.
- A bought part (for example the cell) gives the same panel with maker and order code, and no drawing strip.

## Alternative
- id: c · rung: layout · board: board-c.html
- Name + thesis: The ring above, the drawing below. Selecting a made part puts its measured drawing on the stage under the 3D ring, so place and sizes are seen in one look.
- Axis: what the stage shows when a part is selected (the part in the ring and its drawing together, not the ring alone).
- Worse at: while a made part is selected the 3D ring loses about two fifths of its height; the stage changes shape between made and bought parts; every made part needs flat drawing views exported as pictures.
- Lock amendment (one): on this screen the left stage splits into ring (top) and drawing strip (bottom) while a made part is selected. Cost: the only screen whose 3D area splits; one more animated transition to build.
- Data it needs: per made part, the flat views (front, side, top) as SVG taken from its drawing, per ring size for the body; per made part a spec record (material, finish, tolerances, quantity per ring); the maker files (drawing PDF, 1-page spec, STEP, STL) indexed per part. DATA-MAP.md has no row for "maker files per made-to-drawing part" today.
- 1280 x 800: same split; the three views shrink, the four file buttons go to two rows of two; the panel scrolls below "Specification".
- Links: Home tile -> frame 1 · Parts "show in the ring" and Electronics part -> frame 2 with the part selected · J1.2 -> "Open the ring" (stage bottom) and layer entries (panel) · J1.3 -> click in the stage or a name under its layer · J1.4 -> "Source" (panel bottom left, new tab) · out to Parts -> "Parts line" (panel bottom middle) · out to Files "For a manufacturer" -> "Maker files" (frame 2) and "For a manufacturer" (frame 1).
- Killed: a "workbench" version where the part replaced the ring on the whole stage, with the ring as a small inset. Killed because it breaks the owner's "consistent with rest" ask and loses where the part sits.

## Findings for the lead
- The brief says 78 parts-list lines; DATA-MAP.md (row parts) and JOURNEYS.md (header) both say 77.
- Render: headless Chromium, 1440 x 900 and 1280 x 800, device scale 2: <scratch>/insidec/board-c-1440.png (looked at; no clipped label). The board itself is 1440 wide, so the 1280 shot cuts its right edge.
- The board makes no external request (no link, script, or URL in the file).
- I read only SUBSCREEN-OBJECTIVES.md, DATA-MAP.md and JOURNEYS.md (the whole file, using J1). I did not read the shared design references, because the brief limited what I could read.

I opened no screenshot, no app source, no _captures file, and no other designer's file.

## questions_for_owner
none

RESULT: done, layout c "The ring above, the drawing below" takes the position that a selected made part shows its measured drawing on the stage under the 3D ring, not the ring alone.
