# Lane notes: electronics

Files: `src/routes/electronics/` (index, useElectronics, model, BlockDiagram, PagePane, PartsOnPage, TableView, useScrollIn, electronics.css), `tests/checks/electronics/` (electronics.spec.ts, rich-bundle.ts, run.config.ts), captures `_captures/electronics/`.

## What it does
- Panel: title and design stamp; one banner per record that is down (electronics, schematic-pages, parts), deduplicated; three tabs (Wiring, Pin plan, Power budget; `?tab=`).
- Wiring: the block diagram (the block with most links in the middle, the others in two columns; a line per link, thicker with more nets; the lines of the hovered or chosen block turn ink). A block is a button (`electronics.block`, `aria-pressed`). Choosing one (`?block=<id>`) opens its page of the wiring diagram in the SvgViewer, the page list (all pages, `electronics.page-tab`), "Shares signals with" (the linked blocks, click to jump), "Parts of this page" (link to `/parts?page=<page id>`) and the parts on the page (`electronics.part-row`). A part row sets `?part=<id>`: the stage highlights it and the PartCard opens under the list (`electronics.part-card`). With no `?block=` the block with most links is shown. A wide panel (container query, 820 px) puts the diagram and parts left, the page right.
- Block to page: the page whose id equals the block's `sheet`, else its id, else its title, else the page that shares the most parts (`model.pageOfBlock`). With the real collector, block id = sheet = page id.
- Pin plan and Power budget: the bundle's tables as text; the pin plan has a find box; the source file is linked when it is in `files.json`.
- Honest states: empty bundle = one banner and "Nothing to show yet."; pictures missing (svg null, or the schematic-pages record down) = "This page is only available as a PDF." or "The wiring pictures are not built yet." plus a PDF link when a PDF is listed (`files.json`, area electronics, `.pdf`); the blocks stay listed.
- Stage: `useStageScene({show:'internals'})`.

## Checks (`npx playwright test -c tests/checks/electronics/run.config.ts`)
Own apps on 8840 (live bundle), 8841 (made-up rich bundle), 8842 (pictures-record missing), 8843 (empty). C01 counts and tables equal the bundle · C02 block opens its page within 1 s, image loads, 2 % non-blank, expand and Escape · C03 "Parts of this page" goes to `/parts?page=<id>`, part rows equal the page's parts · C04 pictures missing · C05 empty bundle · C06 part row, card, reload · C07 no page scroll and no sideways scroll at 3 sizes · C08 pin plan find. Mutations seen red: `_captures/electronics/mutate.py`, log `MUTATIONS.log`.

## Open points for other pieces
1. The SvgViewer exists, so no adapter file was written; the viewer is used directly.
2. Empty bundle: the browser logs `Failed to load resource ... 404` (manifest.json) from the data layer; the check filters 404s of `/data/` only (same as home).
3. On the live bundle the root page of the wiring diagram is also a block (9 blocks for 9 pages, collector-electronics): "7 blocks" in the plan is the made-up bundle.
4. Dev-server load: the machine ran at a load average near 190 during these runs; checks need generous timeouts (set).

## Round 2: the picture takes the main area
- On mount the screen presses the shell's own expand button once (`useWide.ts`), because docs/lanes/shell.md offers only "Panel: [data-testid="app.panel-expand"] toggles; Escape and leaving the route collapse": there is no call to ask for a wide panel. Proposal for the shell: `useWidePanel()` in `src/app`.
- Wide panel (container query 820 px): picture left (about 980 px at 1440, height `100dvh - 285px`, sticky), a 380 px column right (block diagram, page chips, shared signals, parts, card). The viewer refits when its box changes width (`useRefit`).
- A part row jumps the picture to the part: one fetch of the page's SVG (`focus.ts`) gives its viewBox and the place of the part's `<text>` label; the viewer gets `viewBox` and `focus`. If the label is not found there is no jump.
- Ring on the stage: not shown. The wide panel covers the whole stage area (shell.css `.main[data-expanded='true'] .panel { width: 100cqw }`); an inset ring is not possible without a shell change. After Escape the panel is narrow and the ring returns, with the selected part highlighted.
- New check C09 (live): viewer >= 900 px wide, tall, part row jumps (red seen with a 200 px viewer).
