# Handoff: screen-face (the glass of the 3D ring shows the ring software's own pictures)

Owner, 2026-11-13: "amke sure (i) panel poroperly done (ii) edge to edge panel and (iii) proper display of app". SPEC row 17. No browser of any kind was opened. The result is built and unit-tested and seen by nobody. The dev server (pid 36469) was not touched.

## What I built
- Collector: `collector/extract/screens.py` reads `design/software/os/screens/manifest.md`, gives each state of firmware.md 3.3 its pictures (`pictures[]`, first one is shown) or `picture_words`, and copies the 240 x 120 PNGs to `public/data/screens/` (21 files, 1.8 MB). `ring_model.py` calls it. Schema `contract/schema/ring-model.schema.json` + `contract/schema/records.json` (extra `screens/`) + regenerated `src/contract/records.ts`.
- Rule of the mapping: a manifest row belongs to the state named by the first `SCR_` name in its scene; a scene without one (status, charging) belongs to the state whose label starts with the same capital mode word. A picture whose file is missing, wrong size or differs from the manifest sha is not attached; the state then says so in words.
- Stage: `screenFace.ts` (draws black, then the picture with hard pixel edges; no text, no timer), `faceTexture.ts` (loads the picture of the chosen state from the data folder, redraws only when the shown picture changes), `materials.ts` (lit picture colour 1.0 instead of 0.85: the picture's own colours). Each picture pixel becomes 4 x 4 texture pixels (`scale` in the record), so 240 x 120 stays sharp.
- Checker `collector/lib/screencheck.py` (reads manifest, source PNGs and bundle files itself, decodes PNGs to check the outer frame is pure black).

## Mapping state to picture (from the collected record)
| state | picture | | state | picture |
|---|---|---|---|---|
| SCR_STATUS | status | | SCR_PAIR | pairing |
| SCR_NOTIFS | notifications-empty (+ notifications) | | SCR_MODES | modes |
| SCR_NOTIF | notification | | SCR_CONTROL | control-media (+ presenter, pointer, agent) |
| SCR_RECORDING | recording (+ recording-highlight) | | SCR_DEVICES | devices |
| SCR_REC_DIM | recording-idle | | SCR_DEVICE | device |
| SCR_MENU | menu | | SCR_MESSAGE | message (+ message-battery-low) |
| SCR_SETTINGS | settings | | SCR_CHARGING | charging |
| SCR_CONFIRM | confirm | | no picture: SCR_RECORDINGS, SCR_RECORDING_INFO, SCR_TRANSFER, SCR_ERROR, SCR_RECOVERY, SCR_FACTORY | words: "The ring software has no picture for this screen." |

15 states with a picture, 6 without; all 21 manifest pictures are in the record once. The first picture in manifest order is shown; the extra ones are in the record but no control in the app picks them.

## Orientation (asked for in the brief)
The ring software draws the 240 x 120 picture as the wearer sees it (`firmware/docs/screens-notes.md` line 170: "the wearer sees the 240 x 120 picture"; the panel turn is `rscr_to_panel`, `firmware/modules/ring_screens/src/rscr_logic.c` line 882; lead-decisions row "block height 4.17 mm: what follows" says the software turns the picture 180 degrees for the turned panel). So the picture is NOT turned again in the app. Mapping: the picture's right edge is +x of the record (along the finger), its top edge is +y of the record (thumb side), i.e. upright for a reader of the plan; this is the existing plane of `src/stage/viewExtras.ts` lines 23 to 25 (not changed; test C15b locks it). `firmware/docs/screens-notes.md` line 114 says which way the wearer reads the picture on the worn ring "is not known": see the question below.

## (i) panel properly done: what I found
- Doubled text, cause: the old `drawFace` drew the label of the dot field and the label of the first text field on the same row at the same x (different font sizes), plus more labels of the specification below. Gone: no text is drawn at all.
- Place and size: the lit plane is built from `screens.rect` (21.6 x 10.8 mm, cx 1.48, cy 0, placement.csv line 24), once per exterior view (test C15a: one plane, that size and place). Measured in `design/look/s1/out/ring-merged32h.glb` (the exterior model): its `screen` node is 21.6 x 10.8 mm, x from -9.325 to 12.275 (centre 1.475), y +-5.4, top at z 3.870 mm. That is the solid the plane sits on (kind `screen`).
- Pixel pitch: 21.6 / 240 = 10.8 / 120 = 0.09 mm, square pixels (test C06 and C13).

## (ii) edge to edge: what I could and could not do
- Done: the `screen` kind and the `glass` kind are one material instance (test C15d), the lit picture is additive (black adds nothing), and every picture has a pure black outer frame (checked on all 21 sources, test C07).
- Not fixable in my files, found in the model: in the exterior model the glass solid has no triangle over the lit area (no vertex with |x|<9 and |y|<6.85 except the rim at y=+-7.2) and the `screen` box is a separate flat solid whose top (3.870 mm) stands above the glass at its long edges (glass top 3.85 mm on the centre line, 3.09 at y=+-7.2; the model still has the old crowned glass, the owner chose flat glass on 2026-11-13). A rectangle edge may therefore still show in the model's geometry, with identical material. I cannot see the pixels. If the owner still sees it, the cure is in `src/stage/view.ts` / `viewExtras.ts` (outside my list) or the new 4.17 exterior model.

## Checks (command, last line)
| command | last line |
|---|---|
| `npm run collect` | `collector: ce56ff0 -> .../explorer/public/data  ok 13` |
| `npm run typecheck` | `> tsc --noEmit`, exit 0, no errors |
| `npm run test:unit` | `Test Files  37 passed (37)` / `Tests  260 passed (260)` |
| `npm run test:collector` (whole, 13:42 to 13:47) | `2 failed, 278 passed in 263.51s (0:04:23)` |
| `.venv-pytest/bin/pytest -q collector/tests/collector-screens` | `14 passed in 2.21s` |
| `npm run check:types` | `types fresh: 32 declarations` |
| `npm run guard` | `guard-no-ring-facts: clean` |
| `npm run check:docs` | RED: `CONTRACT.md lacks: check id range for lane screen-face` (see lead items) |

The 2 collector failures are `part-notes::test_every_ring_line_covered` and `test_generator_reproduces_wording` ("bom.csv line 6: no note for ring:R73": a design file changed outside this lane; the same two were open in the case-true handoff). None touches screens.

Dev server (bar 4), by curl at 13:52 against http://localhost:8790: `data/ring-model.json` served sha256 e36392d2a73ea529... = disk; `data/screens/status.png` served 66f277b72280141b... = disk = source `design/software/os/screens/status.png`; `recording.png` equal as well (f24f817eaa0a37c5...). The served `src/stage/screenFace.ts` and `faceTexture.ts` hold the new code.

## TESTS (each line of the brief)
- Unit (vitest) `src/stage/__tests__/screenFace.test.ts` (C10 to C13: picture or none, picture drawn once on black with no text, black only without a picture, aspect and pixel pitch), `faceTexture.test.ts` (C14a to d: black until loaded, then the picture once, no redraw, no timer text, back to black), `face.test.ts` (C15a to d: one plane of the record's size and place, orientation, no plane without a screen solid, glass and screen one material). `harness-data.ts` carries a made-up picture.
- Collector (pytest) `collector/tests/collector-screens/test_screens.py` C01 to C09 (21 states, 21 pictures; mapping equals the table read off manifest.md; 15 with picture, 6 with words; sha equal to the source; schema; black frame; collected data folder) and `test_checker_flags_*`.
- Red first, seen: stage tests on the old code: 9 of 13 failed (C10, C11, C13, C14a to d, C15a, C15d; C15a only for a missing `scale`/size, C15d for the old 0.85 colour). Collector C09 failed on the data folder before the first collect (42 problems). Kept broken fixtures `collector/tests/collector-screens/fixtures/{missing-file,wrong-state,no-words}` fail the real-data test with `RING_EXPLORER_BROKEN=<name>`: "SCR_MENU: screens/zz-missing.png is not in the data folder", "belongs to 2 states", "must have pictures or words".
- Mutations seen red, restored: drawFace calling `fillText` (7 tests red); `screen: glass.clone()` (C15d red); a second `scene.add(plane.clone())` in buildFace (C15a red; file restored byte for byte).
- Runner: the default runners above. Not run by me: any browser, journey or check test.

## For the lead
- `docs/CONTRACT.md` line 102 needs `screen-face-C01..C99` (my ids: collector C01 to C09, stage C10 to C15) or `npm run check:docs` stays red; add a change line for `pictures`, `picture_words` of `screens.states[]` and the `screens/` data folder. DATA-MAP row ring-model could name `screens/` too.
- Not drawn any more, still tested elsewhere: `testApi.screenFields()` (`src/stage/testApi.ts`, not mine) still returns the record's field labels; `journeys/J2.spec.ts` line 219, `journeys/J5.spec.ts` line 247 and `tests/checks/look/look.spec.ts` lines 112/115 assert them as "drawn on the glass". They are not run by me; they need a `screenPicture()` probe or a new expectation.
- Words for a state without a picture ("the part card says in words"): the words are in the record (`picture_words`). No file of mine renders them: the state picker is `src/routes/look/Switches.tsx` / `index.tsx` (tooltip `title`), the part card is not in my list. Suggest showing `pictureWords(state)` there.
- The record's pictures list has extras (e.g. the recording with a highlight) that no control selects; the Look picker has one entry per state.
- `FaceTexture.draw` still takes `visible` and `elapsed` (unused) because `engine.ts` (not mine) calls it so.

questions_for_owner:
- Which way does the text run on the worn ring: along the finger with the top toward the thumb side (as drawn now), or turned? The design files say this is not known (`firmware/docs/screens-notes.md` line 114).

RESULT: done, each of the 21 screen states shows its ring-software picture (15) or says in words it has none (6) on the lit plane of the record, no text is drawn and the glass material is one; built and unit-tested but seen by nobody, 2 unrelated part-notes collector tests fail and check:docs needs the lead's line in CONTRACT.md.

## Edge at the left of the glass (owner, 2026-11-13: "what is the weird border/edge on left of screen")
Files changed: `src/stage/viewExtras.ts`, `src/stage/view.ts` (one call), `src/stage/materials.ts` (depth offset on the lit picture), tests `src/stage/__tests__/face.test.ts`, `faceOnGlass.test.ts`. No other path was needed.

**Cause.** In the exterior model (`design/look/s1/out/ring-merged32h.glb`, shipped as `exterior.glb`) the `screen` node is a flat slab of 21.6 x 10.8 mm whose top is at 3.870 mm. The glass over it is a dome: measured by ray at the lit area, its top is 3.85 mm on the centre line and falls to about 3.37 mm at the two long edges (3.73 at +-2.7 mm), the same at every x. So the slab stood proud of the glass by 0.02 mm at the middle and about 0.5 mm at the long edges, and its end faces and flat top reflected differently from the glass. The lit area is also off centre in the face (cx 1.48), so one end shows closer to the glass end: that is the real part. The app drew this slab as its own surface (same material, but its own geometry and reflection), and put the picture plane flat above it.

**Change.**
- `hideScreenUnderGlass(parts)`: when the view has a glass solid, the meshes of the `screen` solid are not drawn (`mesh.visible = false`; they stay in the part, so picking and the part card still work). Called from `view.ts` right after the face is built. With no glass in the view the screen solid still shows. The cut-away and exploded views are not touched: they use the inside model, whose panel still shows.
- `buildFace`: the picture plane is the record's rectangle (21.6 x 10.8 mm at cx 1.48, cy 0, unchanged), now a 48 x 24 grid whose every vertex lies at the glass height, found by a ray from above on the glass meshes (`glassHeight`). It follows the dome, lies on it and not above it. Without a glass it stays flat just above the screen solid, as before.
- `materials.ts`: the lit picture material has a depth offset (-2, -2) so a plane exactly on the glass is drawn in front of it without flicker. Colour, additive blending and the one glass material are unchanged.

**Tests (vitest, real `public/data/exterior.glb` and `ring-model.json`, skipped when absent).**
- C16a: with the glass on, every mesh of the screen solid is not drawn and the glass meshes are.
- C16b: at the plane's four corners, four edge midpoints and centre, and at every one of its vertices, the plane is on or under the glass surface (tolerance 1e-6 mm); its size is 21.6 x 10.8.
- C16c: the slab top is above the glass at its long edge by more than 0.05 mm (the defect, kept as a fact of the data).
- C16d: the slab is hidden only when a glass is there. `face.test.ts` C15a/C15e updated: plane on the glass (3.85) with glass, flat above the slab without.
- Mutations seen red, restored: slab visible again (C16a and C16d red); plane flat above the slab again (C16b red).
- `npm run test:unit`: `Test Files  38 passed (38)` / `Tests  265 passed (265)`. `npm run typecheck`: no errors.

**What the owner should now see (unproven, no browser).** One continuous glass surface over the lit area: no step, no end face and no separate darker panel at the left; the reflection band of the dome runs unbroken; the picture sits on the dome and so follows its curve (it is flat in the real part under glass; here it is drawn on the glass surface). The thin light rim at the far left end came from the slab's end face and should be gone. Whether the glass itself shows an edge at its own rim cannot be known from the data.

questions_for_owner: none new (the earlier one on text direction stands)

RESULT: done, the screen solid is no longer drawn under the glass and the lit picture lies on the glass surface at every vertex of its grid, proven on the real model by unit tests (265 passed, typecheck clean); built and unit-tested but seen by nobody.
