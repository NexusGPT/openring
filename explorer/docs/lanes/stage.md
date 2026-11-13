# Lane stage: the shared 3D view (consumer guide)

Owner: stage lane. Code: `src/stage/**`. Test API type: `src/contract/stage-api.ts` (stage lane is its only writer).
Everything below is what a screen needs; nothing else of the stage is public.

## Shell mount (what the shell loads)

`src/stage/index.tsx` default export = `SceneStage({scene})`. It reads `ring-model`, `part-placements`, `look-options`, `case` itself and builds `<Stage/>`; the shell keeps one mounted. A screen steers it with `useStageScene({...})`; keys (all optional):
`show` (`exterior` | `internals` | `case` | `looks`; default by route: inside = internals, case = case, else exterior), `preset`, `finish` (a finish name), `screen` (state id; `null` = off; absent = first state), `light`, `explode` (0..1), `isolatedLayer`, `lidOpen` (deg). The selected part is the URL `?part=<id>` (read for the highlight; a click on a part writes it). The canvas carries the shell slot's `data-stage-id`.
Request to the shell piece: none needed; `StageOptions` carries everything above.

## Mount it once (direct use, harness)

`import { Stage, exteriorView, lookView, internalsView, caseView } from '../stage'`

The shell renders ONE `<Stage …/>` and gives it a box (it fills 100 % of its parent). Screens change its props; they never mount a second one. The WebGL renderer is a module singleton, so `window.__stage.contexts` stays 1 across routes (a remount re-attaches the same canvas).
Pass records by stable reference (the react-query result object): a new `ringModel` or `placements` object rebuilds every view.

## Props (`StageProps`, `src/stage/types.ts`)

| Prop | Meaning |
|---|---|
| `views` | one `ViewSpec` per side-by-side view, in one canvas. Build them with the helpers below. |
| `ringModel`, `placements` | the `ring-model` and `part-placements` records (null while not available). |
| `finish` | `{colour, roughness}` of one entry of `look-options.finishes`. |
| `screenState` | a `state` id of `ringModel.screens.states`; `null` or unknown = screen off (black). |
| `lightOn` | red light glow on/off. |
| `preset` | `three-quarter` (default), `top`, `side`, `finger`. Eased camera move; `finger` shows the finger and a 10 mm cue. |
| `explode` | 0 assembled .. 1 fully opened (eased). Layers come from `placements.layers`, parts from `ringModel.nodes[].layer`. |
| `isolatedLayer` | a layer id: other layers are hidden; `null` = all. |
| `selectedNode`, `onPick` | highlight a part; `onPick({viewId, node})` on a click that is not a drag, `onPick(null)` on empty space. Map `node` to parts with `ringModel.nodes[].part_ids`. |
| `route` | test-id scope of the placeholder banner (`look.state-banner`, …). Default `app`. |

## Views

- `exteriorView(ring, id?, label?)`: the approved exterior from `ring.exterior.file`; while `exterior.status` is not `picked` it is the **plain black slab** at `ring.block.size_mm` (no detail). The route shows the `exterior-not-picked` banner itself.
- `lookView(ring, option)`: one look option's `glb` (`fileUrl`), shown as an exterior. Pass N of them for the side-by-side compare; each gets a caption (`option.title`, React text).
- `internalsView(ring)`: `ring.internals.file`; layers, explode, isolate and pick apply.
- `caseView(case)`: `case.glb` (via `dataUrl`; if the collector writes repo-relative paths here, switch to `fileUrl`: one line in `views.ts`). Nodes get kind `plain`. `lid.openDeg` is eased about the record's hinge; `window.__stage.nodeRotationDeg(lid_node)` reports it. Returns null when `case.glb` is null.
- Node kinds (`finish metal, glass, screen, light, satin, matte, gold, plain`) and layers come from the bundle. A mesh whose node is not in the map is drawn `plain` and listed by `__stage.unmappedNodes()`.
- Models: GLB (metres, meshopt decoded) or STL (mm, Z up), loaded from the URL the helper built. A model that fails to load: the stage shows `StateBanner kind=missing` (vocabulary words) in the view area and logs no uncaught error. No WebGL: same banner.

## Screen face

Drawn on a canvas from `ringModel.screens.states[state].fields`: kinds `dot, timer, battery, storage, bar, icon, text`. The only words drawn are the fields' `label`s; `__stage.screenFields()` lists them. `ringModel` null = the face is never built (the glass stays black); show a `StateBanner kind=missing` in the route.

## Explode direction (open contract point)

`part-placements.layers[]` has no direction field. The stage reads an OPTIONAL `explode` per layer, a `Vec3` in design coordinates or the word `"radial"` (type `LayerRecord` in `types.ts`); without it, it derives: layers whose parts sit on one side of the band move along that side's direction, layers spread around the band move each part outward along its own radius. Each layer moves `rank x EXPLODE_MIN_GAP_MM x explode`, so touching layers end `EXPLODE_MIN_GAP_MM` apart. Needed from collector-model: add the optional field from `design/mech/thin/layers.json`.

## Test API additions (stage-api.ts)

`clearColor()` (renderer clear colour and alpha), `preset()`, `explode()`. Box coordinates in `layerBoxes()` are design coordinates (x, y, z up), mm, at the current explode value.

## Dev harness and checks (headless, 127.0.0.1 only)

- `npx vite --port 8802 --host 127.0.0.1 --strictPort`, then `/src/stage/harness.html?mode=assembled|exploded|slab|compare|fail|lid`. Dev only; not in the build.
- `../design/.venv/bin/python _captures/stage/shoot.py [mode ...]`, `drive.py` (drag, presets, finish, pick, layers), `mutate.py` (each check seen red; log `_captures/stage/MUTATIONS.log`).
- `npx vitest run src/stage`.

## Added on real data
- Units: a GLB whose `asset.extras.units` is `mm` (the collector's internals.glb) is not scaled; others are metres (x1000).
- Explode: layers that open in the same direction (the record's `explode`, or derived) open one `EXPLODE_MIN_GAP_MM` apart, the first one gap from rest; `radial` moves each part outward along its own radius. Internals show their `finish metal` parts in a light neutral metal so parts read on white.
- Pick: assembled (explode < 0.05) a click goes through the cover glass to the part behind it (the lit area picks the screen); exploded, the glass is pickable. Proof: `_captures/stage/pick.py`.
- `exterior.status = not-picked` with a file: the stage shows the plain slab (contract section 3), not the model; the collector note about labelling it "in design" is not followed.

## Fit, exterior state, notices (round 3)
- Fit: every preset keeps the object and its contact shadow inside the view with 12 % margin per side, at any azimuth (a sphere around the target, 76 % of the smaller field of view); it re-fits on resize (a turned ring keeps its direction). `__stage.fitBox(viewId)` reports the projected box (shares of the view); `fit.test.ts` fails if a camera leaves the margin.
- Exterior state: a model that is not approved but has a file is shown, `exterior: 'in-design'` on the view, `data-exterior` on the stage host and `__stage.exteriorState()`; a screen labels it. Only with no file is it the slab (`none`). The vocabulary sentence `exterior-not-picked` (contract) still says the stage shows a slab: contract lane to reword.
- Missing record: with `ring-model` missing or unreadable the stage shows the contract banner (prop `notice`), never a blank stage.
- Gap for collector-model: ring-model.nodes lists only internals node names; the exterior model's nodes (body, glass, screen, band, joystick, button, light, mic_1, mic_2, contacts) have no kind. Until they do, unmapped exterior nodes take the finish metal and are listed by `unmappedNodes()`.

## Round 4: points on surfaces, hover, objects
- `__stage.screenPos(node)` returns a point ON the part's visible surface (canvas px): rays through the part's projected box, nearest the centre where the part is the first hit; a fully hidden part gets a point on its own surface (a click there lands on what hides it: isolate the layer or open the ring first). The ring auto-rotates until the first drag: stop it (a drag, or change the preset) before clicking a computed point.
- Hover: prop `onHover({viewId, node, x, y} | null)` (x, y in CSS px inside the stage) and `labels` (node name -> display name). The stage draws the name tag (`<route>.part-tag`, class `label`, tokens only) from `labels`; no entry, no tag. In the shell the screen passes `names` (a JSON string node -> name) in its scene options; without it the tag shows the node name with spaces.
- Pick writes the address: `?part=<id>` for a node with a parts-list line, `?object=<node>` for one without; empty space clears both. `?object=` also highlights the node.

## Round 5: opening the ring
- Enclosures ghost when `explode > 0.15` (about 12 % opacity, thin edge line in the `--hairline` token). A layer may say `ghost_when_open: true|false` (read if present; the placements schema needs the optional field); else a part whose box holds more than half of the other parts' centres is an enclosure. Picks and `screenPos` pass through a ghost; isolating the enclosure's own layer makes it solid.
- Parts of a `radial` layer that sit along one radius (within 12 degrees) open one extra `EXPLODE_MIN_GAP_MM` each, in order of distance from the axis.
- Live proof (`_captures/stage/open_live.py`, `open-live.png`, `open-live-tilted.png`): fully open, nothing isolated: cell = `ring:BT1`, vibration motor = `ring:M1`, joystick cap = `ring:CAP1` from the default view. The board's chips sit under the opaque screen and glass layers from above: from a lower view they pick `ring:U1`, `U2`, `U3`, `ANT1`, `U4`, `X1`. From the default top-down view a click on a chip lands on the screen layer; that is what the owner sees.

## Round 6: opened gap
Layers that open in one direction travel from their real boxes: the clear space between neighbouring layers' boxes along the direction is at least `EXPLODE_MIN_GAP_MM` fully open, whatever their closed overlap (`layers.ts`, test in `opening.test.ts`; inside-C12 passes).

## Round 7: one ring, one easing, detail
- One ring: `ringView(ring)` = the exterior (or slab) with the inside model hidden in it; Home and Inside use the SAME view (`show: 'exterior'` or `'internals'` both give it), so the first frame of Inside equals Home's pixel for pixel (checked: 0 differing pixels, reduced motion so the camera is still) and the camera eases between routes. `show: 'internals-only'` draws the inside model alone (tests). From 0 to 0.25 on the control the exterior fades out, the inside appears and the enclosure becomes the ghost; from 0.25 to 1 the layers travel.
- One easing (`ease.ts`): duration `--t-slow` and curve `--ease-settle` from `src/styles/tokens.css` (fallback 320 ms ease-out). A new goal restarts from the current value: a dragged control is followed without steps, a clicked value animates. Isolating fades the other layers to ghosts; selecting a part eases the camera to frame it and draws an outline in `--ink`; preset and route changes ease the camera; the hover tag fades (`--t-med`). `prefers-reduced-motion`: every change is instant, no auto-rotate.
- Materials: one table `classMaterials.ts` keyed by the bundle's class names (children named `<part>__<class>`: metal, gold, pcb, chip, ceramic, polymer, glass, screen, foam, flex, cell, resin, mark). Until the model carries them the part's kind maps to a class (`KIND_CLASS`). An unknown class is polymer and is listed by `unmappedNodes()` as `<part>__<class>`. A click on a child selects its top-level part.
- Smoothness: antialiasing at the device pixel ratio (cap 2), smooth normals (creased at 34 degrees) for inside meshes, soft contact shadow in every view, the shaders and buffers of the transition states are drawn once at build so the first opening does not stall.
- Test API additions: `exteriorOpacity()`, `partOpacity(node)`, `outline()`, `cameraDistance()`.

## Round 8: speed, clicks, thin shells
- Rendering: nothing is drawn when nothing moves. Frames that answer the user (drag, click, hover, eased changes) are drawn at once; ambient frames (auto-rotate, the animated screen face, only while the face is visible) are drawn at most every 4 frame times (cap 600 ms), so a slow machine or the 201,479-triangle exterior leaves room for clicks and screenshots. The ring holds still (no auto-rotate, no inertia) while the pointer is over it.
- Clicks: a click is judged by the events' own timestamps (a busy page no longer turns a click into a long press); `screenPos` goes coarse to fine (a visible part costs one ray).
- Ghosts when open, three rules: a layer or a part flagged `ghost_when_open` (the part flag, read from `placements[].ghost_when_open` by node name, wins); a part whose box holds more than half of the other parts' centres; a thin shell (solid volume under 20 % of its box) that hides at least 30 % of another part's surface samples from the current camera. Of nested shells only the outermost (largest box) ghosts, so the cell is clickable once the liner ghosts. Live: open fully, click the cell from the default view: `?part=ring%3ABT1` (`_captures/stage/cell_live.py`).

## Round 9: timer, case, lid
- Screen timer: `formatTimer(elapsedSec)` = mm:ss, seconds never above 59; the screen that owns the clock passes `elapsed` (seconds, scene option; prop `elapsedSec`). Without it the timer reads 00:00. The face no longer has a clock of its own.
- Case nodes: a default map from name shapes to material classes (`caseKinds.ts`: housing and lid polymer, window and LED resin, boards pcb, contact pins gold, hinge and springs metal, the cell cell, reference designators chip); a collector that writes kinds replaces it. The case record has no ring nodes: a seated ring needs a pose in the case record (not there today).
- Lid: eased in 600 ms from the record's hinge point and axis; the reported angle is the applied one. A part whose primitives hang under a group of its own name now moves as the group (before, only its first primitive moved, so the lid looked closed at 116 degrees). The camera keeps the open lid in frame.
