# Constants: Ring Explorer

Every threshold, count and port is written once, in `contract/schema/constants.json`. This file names each one, says what it means and what it depends on. It holds no values: `npm run check:docs` fails when a name here is missing from the JSON or the reverse. Code reads the JSON (`src/contract/constants.ts`, `collector/lib/records.py`, `vite.config.ts`, `tests/playwright.config.ts`).

| Name | Meaning | Depends on / source |
|---|---|---|
| HOST | the only interface any server binds | PRD Access: "runs on localhost on the owner's Mac" |
| APP_PORT | port of the app (strictPort) | CONTRACT section 9; checked free at planning time, 8791 was held by another process |
| JOURNEY_PORT | port of the journey and check servers | CONTRACT section 9 |
| GLB_MAX_MB | largest model file the bundle may hold, after meshopt compression | PRD Perf-budget first-paint line; re-check after the meshopt run on look C |
| EXPLODE_MIN_GAP_MM | smallest gap between two layers when Inside is fully opened | plan todo interaction-explode |
| BOARD_SIDE_MM | distance from the board faces within which a part counts as top or bottom | plan todo functionality-board-extract |
| NOTE_WHAT_WORDS | most words in a part note "what" | the 20-word sentence rule in design/look/viewer/collect.py |
| NOTE_WHY_WORDS | most words in a part note "why" | same rule |
| PANEL_MAX_WORDS | most words in one side panel | DESIGN.md anti-reference "a wall of text"; inferred |

Performance numbers are not copied here: the source is the `Perf-budget:` line of `docs/PRD.md`.

## collector-model additions

No new constant. GLB_MAX_MB is read from `contract/schema/constants.json` by `collector/extract/ring_model.py` and applied to `internals.glb` and `exterior.glb` after meshopt (gltf-transform from `node_modules/.bin`; absent tool: shipped uncompressed and said so in the manifest message). Measured on 2026-11-10: internals.glb 0.143 MB, exterior.glb 0.451 MB (cap 5).
