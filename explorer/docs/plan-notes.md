# Ring Explorer: plan notes

Companion to `explorer/docs/plan.json` (the contract). This file holds what the JSON cannot carry well: the base decision, the conflicts with exact lines, the proposed constants, and the requests to the design lanes.

## In one view
- Status: `needs_taste_answers` (3 taste questions, 3 readings to confirm, 7 gaps).
- 61 todos in 8 slices; slice 1 = journey J1 on the frozen real-data record.
- 30 lanes, 1 root (`contract`), 5 dependency levels, `owns` lists checked pairwise-disjoint by the generator (literal and folder-prefix).
- 52 units enumerated; 22 merged into lanes, each merge with its written reason (`merged_units` + `unsplittable_reason`).
- Mobile: 0 todos on purpose (PRD Non-goals: "no phone layout").

## Owner answers received 2026-11-10 (via the lead), now in the plan
- Exterior: "I hate all of them, they are not as slick as the ring I shared". A, B, C are retired: Look never shows them as current; with no new option it shows "New options in design" (todos ux-look-options, functionality-look-extract; capture cap-look-options). The fixture keeps A, B, C un-retired so J2 still runs.
- Size: "Slim, like the photo (Recommended)", thumb control "Custom joystick". Every ring figure is bundle data; the journey example figures (30 x 20 x 9.5 mm, 135 mAh, 4 microphones, 77 lines) hold on the A3 fixture only.
- Style "S1 Gallery (Recommended)" and the bar word "slick": stated interpretation rows; the taste judge grades slickness, the blind checks grade the S1 floor.
- Taste question tq-stage-without-exterior no longer offers a ghosted A; tq-rejected-looks now asks only whether the retired looks stay reachable anywhere.

## Base decision (scorecard, base-decision.md section 1)

| Dimension | Build fresh (chosen) | Org starter (`apps-starter`) |
|---|---|---|
| Stack vs goal | static React + Vite SPA, three.js stage, Python collector on the existing `design/.venv` | zero-dep node server with a record data spine, config-driven objects and views (starter-guide.md:27) |
| License | three, React, Vite: MIT; apps-ui MIT, private | MIT, private |
| De-brand / strip | none | remove objects, demo rows, sign-in wiring, warehouse driver, `.<platform>-starter` deploy-gate marker |
| Build weight | about 10 runtime dependencies | the full skeleton plus a server this app never calls |
| Design malleability | tokens.css from DESIGN.md over the apps-ui token canvas | same token canvas |
| Components shipped | apps-ui vendored by `<platform> apps vendor-package` (catalog not read yet: gap G2) | the same library |
| <platform> wiring | none needed (LOCAL, no agent) | present, unused |
| Client state | TanStack Query over static JSON (one cache entry per record) | the starter's server-backed data layer, unused for a static bundle |
| Strip vs build cost | one root lane | strip work larger than the scaffold |
| Verdict | adopt | reject |

Not verified: the starter and library were not fetched; their rows come from `references/starter-guide.md:22-28`. No spike is needed: no row is uncertain enough to change the verdict.

## Readings to confirm with the owner (one line each, before dispatch)
1. Area states come from `design/status.json`, a file the lead writes when board rows move (state, why, who per area; look picked and rejected). No file means every tile says "state unknown".
2. The journeys test a frozen copy of the A3 design (commit 99dfb85 plus a frozen copy of look C). The app itself shows whatever `npm run collect` last built from the live slim design.
3. "In rework" means: the file says it follows an older architecture version than the current one, or its area is "in progress". The screen then shows its content dimmed under "Made for design A3; the design is now A4. Being redone." It never hides the content.

## Taste questions (also in plan.json `taste_questions`)
1. tq-stage-without-exterior: what sits on the stage while no exterior is picked? Recommended: a neutral frosted shell at the block size with the real parts visible inside.
2. tq-rejected-looks: where do rejected exteriors go on Look? Recommended: hidden, with one link "Earlier options (rejected)".
3. tq-behaviour-button: where does the owner press and hold? Recommended: a large virtual button and a 5-way pad in the right panel, while the 3D ring reacts.

## Gaps (blocking rows, plan.json `gaps`)
- G1: `docs/surfaces/<surface>.md` is missing for all 9 surfaces. The lead writes them as inheriting L1 Stage and S1 Gallery.
- G2: the component library is not vendored yet. After the contract lane, the lead reads `catalog.json` and fills `component_source` on 7 todos.
- G3: the 4 finishes exist only in `design/look/viewer/viewer.js:11-16`.
- G4: nobody writes `design/status.json` yet.
- G5: two data-map changes need the owner's OK (C4, C5).
- G6: the real-data commit and the J7.1 figure (C1, C9).
- G7: the PRD names a 3D frame-time budget but gives no number. Frame time is recorded, not gated.

## Conflicts (exact lines)
- C1. `docs/JOURNEYS.md:2` "real-data: the ring design in this project at git commit 7274c69" against `docs/JOURNEYS.md:22` "options A, B, C in 3D ... look-options from design/look". `git ls-tree -r 7274c69` lists no `design/look/` file; at 99dfb85 `design/look/c/out/ring.glb` is untracked. Plan: freeze 99dfb85 plus a copy of look C (interpretation 2).
- C2. `docs/JOURNEYS.md:12` "numbers read 30 x 20 x 9.5 mm, 135 mAh" and `:40` "chip, 4 microphones" against lead fact 4: slim ring "about 22 x 15 x 6.5 mm, 2 microphones". The tests pin to the A3 fixture, and the live app shows the slim values.
- C3. `docs/DATA-MAP.md:14` area-states "collector, from the project record export" against `docs/PRD.md:16` "that state matches the project files". No export exists. Plan: `design/status.json` (G4).
- C4. `docs/DATA-MAP.md:16` blocks "collector, from design/architecture.md section 1". `design/architecture.md:16-32` is a text drawing with no machine-readable shape. Plan: the blocks are the 7 schematic sheets (their own titles), and the links are the nets that cross sheets.
- C5. `docs/DATA-MAP.md:12` part-notes "plain-words text per part: what it is, why it is there". `design/mech/placement.csv:1` has no reference column, so the plan adds `model_names[]` to each note (the link from a 3D object to a parts-list line).
- C6. The lead's brief says "Mark every interpretation `inferred`". `references/plan-format.md:64` says "Cap: at most 3 `inferred` rows reach the user". Plan: the user's stated constraints stay `stated`; 3 architect readings are `inferred` with `surface_to_user: true`; the other readings are in `assumptions_decided`.
- C7. `docs/JOURNEYS.md:58` J6.1 arrives by "top bar · Files", but the style board's tab list (`docs/boards/styles.html:106`) has "Open items" only. Plan: a second entry "Files" at the right of the bar, on the same route.
- C8. `docs/PRD.md:30` "The 3D library loads from the local install, not from the internet" against the seed's CDN import map (`design/look/viewer/index.html:52-57`) and the board's Google Fonts link (`docs/boards/styles.html:7-8`). Plan: npm packages only, plus a no-network check.
- C9. `docs/JOURNEYS.md:66` "6.4 minutes per recorded hour" against `design/architecture.md:219` "takes 6.3 minutes" and `:299` "6.3 minutes per recorded hour". No 6.4 was found in the case files. A fix is owed in JOURNEYS.md, or the test asserts the source value.

## Constants to land in `explorer/docs/CONSTANTS.md` (contract lane; proposed values)
- App port 8790 (strictPort, 127.0.0.1); journey port 8797 (free at planning time; 8791 is held by another process).
- GLB_MAX_MB 5 (depends on the PRD first-paint budget of 1500 ms; to re-check after the meshopt run on look C).
- EXPLODE_MIN_GAP_MM 2.0; BOARD_SIDE_MM 2.0; NOTE_WHAT_WORDS 20; NOTE_WHY_WORDS 25 (from the 20-word sentence rule in `design/look/viewer/collect.py:73`); PANEL_MAX_WORDS 120 (anti-reference "a wall of text"; inferred).
- The perf numbers are not copied. CONSTANTS.md cites the PRD `Perf-budget:` line.

## Requests to the design lanes (via the lead; none blocks the root)
- Architecture A4: keep the section titles the collector reads (sections 2, 4, 6, 7, 12, 13, "How to read this"), and add a `## Key numbers` table (Fact | Value | Source). The collector reads that table first.
- Mechanics: add a `reference` column to `placement.csv` (for example cell gets BT1). The collector then prefers it over the notes' `model_names`.
- Look: write `design/look/shared/finishes.json`; keep `envelope.py` as the shape contract (part names, screen rectangle, band size).
- Firmware F3: keep the state, transition, gesture and motor tables in the same column shapes (`design/firmware.md:52`, `:86`, `:160`, `:212`).

## Not verified
- The starter and apps-ui contents.
- `kicad-cli sch export svg` output (only its help was read).
- Whether build123d reads STEP labels or exports the case GLB. A rival probe is owed in the collector-model lane.
- The meshopt size of look C.
- The weight value.
- `design/firmware.md` after line 260, and the other documents beyond their headings and the lines cited.
- `references/parallel-agent-builds.md` (0 of 715 lines read).
- The ports after planning time.

## questions_for_owner
- The 3 readings and 3 taste questions above.
- The re-pin of the real-data record from 7274c69 to 99dfb85 (C1).
- The J7.1 transfer figure: 6.4 or 6.3 minutes per recorded hour (C9).

RESULT: done, plan.json holds 30 lanes (1 root, pairwise-disjoint owns) and 61 todos in 8 slices, status needs_taste_answers.
