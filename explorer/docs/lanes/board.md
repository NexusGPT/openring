# Lane notes: board

Files: `src/routes/board/` (index, useBoard, model, PlanSvg, PlacedList, SideToggle, board.css), `tests/checks/board/` (board.spec.ts, run.config.ts; uses `tests/checks/electronics/rich-bundle.ts`), captures `_captures/board/`.

## What it does
- Panel: title and stamp; the contract banner `board-not-routed` ("Board not routed yet. Missing: <list from the bundle>.") whenever `routed` is false; banners for a record that is down; facts (board size, parts placed with top and bottom counts, cut-outs, "Not on the board yet": parts whose centre is outside the outline).
- Top / Bottom / Both (`board.side-*`, `aria-pressed`, `?side=`). The plan (`board.plan`, inline SVG drawn from the record's numbers, React shapes only) has one `board.plan-part` per placement with `data-part` (name) and `data-side`; a part of the other side is hidden (opacity then visibility, `visibility:hidden` after 200 ms). Bottom parts are dashed, top parts solid, the chosen part ink. Hover or focus draws the part's name on the plan.
- A click (or Enter) on a part, or on its row, selects it: `?part=<id>` when it has a part id (the record's `part_id`, else the part note whose `model_names` names it), else `?object=<name>` and the words "no parts-list line for this object". The PartCard (`board.part-card`) opens under the list and scrolls into view. The stage highlights the part.
- The list of parts starts closed behind a find box when a side holds more than 8 parts ("Show all", or type a name or reference).
- A picture from the board file (`svg.top` or `svg.bottom`) is shown in the SvgViewer when the board is routed, and on request ("Plan | Board file", `?view=drawing`) when it is not.
- y direction: a board read from a `.kicad_pcb` (outline source file) counts y downwards; a plan made from the design placement table counts y upwards. `model.yDown` picks by the outline's source file; the plan reads as seen from above in both. Contract gap: the record does not state it.
- Stage: `useStageScene({show:'internals', explode:0.4, isolatedLayer:<layer>})`; the layer is the one most of the board's placed objects sit in (`model.boardLayerId`, from `part-placements`).

## Checks (`npx playwright test -c tests/checks/board/run.config.ts`)
Own apps on 8860 (live), 8861 (rich, not routed), 8862 (rich, routed), 8863 (empty). C01 banner text and the missing items · C02 plan elements equal placements, Bottom hides tops, a part opens its card · C03 isolated layer equals the board layer · C04 routed has no banner · C05 no page scroll and no sideways scroll · C06 side and part survive a reload · C07 empty bundle. Mutations seen red: `_captures/board/mutate.py`, log `MUTATIONS.log`.

## Open points for other pieces
1. Live board (today): 100 placements, all `top`, 22 test pads outside the outline (centres), the board file holds no tracks (`routed:false`); the KiCad pictures exist for both sides.
2. The contract should state the y direction of `board-files` (see above).
3. Empty bundle: the data layer logs one 404 for the manifest; the check filters `/data/` 404s.

## Round 2: the picture takes the main area
- Same wide layout and `useWide.ts` as Electronics (shell limit as in docs/lanes/electronics.md; no inset ring for the same reason). Default picture is the board file (top or bottom) when the record has one, "Plan" (the drawn plan, `?view=plan`) beside it; Both shows the top picture.
- A part row jumps the picture to the part: the board pictures start at the outline's top-left corner, so position = (x - (outline.x - w/2), y - (outline.y - h/2)); offered only when the picture's size matches the outline's.
- Check C08 (live): default picture, 900 px wide, Top/Bottom change the image, part row jumps. C02 and C06 use `?view=plan`.
