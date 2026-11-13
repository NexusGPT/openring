# Lane notes: look

Files: `src/routes/look/` (index, Switches, OptionPanel, model, look.css), `tests/checks/look/` (look.spec.ts, bundles.ts, run.config.ts), captures `_captures/look/`.

## What it does
- Panel (right of the shell's stage): title, the exterior banner (`exterior-in-design` / `exterior-not-picked` from `ring-model.exterior.status`), three switches, then OPTIONS.
- Switches (each button has `aria-pressed`; ids `look.finish`, `look.screen`, `look.view`, group ids `look.<name>-switch`, `data-value` = finish name / screen state id / preset):
  - Finish: every entry of `look-options.finishes` (swatch = its colour). None in the bundle: one muted line.
  - Screen: the first two states of `ring-model.screens.states` (their label up to the first comma or bracket), `Off` (stage `screen: null`), and the others behind "More".
  - View: three-quarter, top, side, on a finger (the four presets the stage has).
  - All three go to the stage through `useStageScene({show, preset, finish, screen})`: one action changes every option at once; the stage eases it, `prefers-reduced-motion` makes it instant (checked: C11).
- Options: `look-options.options` minus `rejected`; with `picked` set, that one alone with the label "Picked". Each = `look.look-option` (title, one sentence, "Worse at" list, "Details" disclosure: source file:line and bounds). All text is the bundle's.
- Stage steering: `show: 'looks'` (side by side) only when more than one open option has a model and nothing is picked; otherwise `show: 'exterior'` (the ring-model's exterior, which is the one open or picked look).
- No open option in a readable record: one banner `new-options` ("New options in design.") and no exterior banner.
- `look-options` missing or unreadable: the ring-model's own exterior stands in as one panel (title = `exterior.look_id`, Details = its source), the record's banner (`missing`) sits under OPTIONS. Seen live before the collector landed the record.
- Empty bundle (both records down): one panel banner, no switches.

## Checks (`tests/checks/look`, run: `npx playwright test -c tests/checks/look/run.config.ts`)
Starts one app at a time on 8809 (live bundle, three open options, one picked, all rejected, empty, one open + one rejected, no look-options record); the made bundles are copies of public/data plus a written `looks/index.json` and a source folder with the models. Mutations seen red: `_captures/look/mutate.py`, log `_captures/look/MUTATIONS.log`.

## Open points for other pieces (each reported with the call and what was seen)
1. stage, `src/stage/views.ts` `lookView`: it builds the model URL with `fileUrl(option.glb.file)` (repo-root files listed in files.json). The collector writes `looks/<id>.glb`, a path inside the bundle (`dataUrl`). With two or more open options on the real bundle, `show: 'looks'` requests `/files/looks/<id>.glb` and gets 404. Fix: `dataUrl` in `lookView` (one line) or the collector writing a repo path. The screen avoids it today: one open option = the ring-model exterior.
2. stage, `SceneStage.tsx`: with `look-options.picked` set, `show: 'looks'` would still draw every non-rejected option (it filters on `rejected` only). The screen asks for `exterior` when something is picked.
3. stage presets: only `three-quarter`, `top`, `side`, `finger`. The owner's list also has "thumb side" and "from below": the stage needs two presets, then one line in `VIEW_CHOICES` (`src/routes/look/model.ts`).
4. (closed) collector-look now writes complete "Worse at" lines.
5. data layer: an absent record logs one `Failed to load resource ... 404` in the console (same as home point 1).
6. Two `look.state-banner` ids can be on screen when the stage draws its own notice (route prop = scene route); tests scope to `app.panel`.

Proof: `_captures/look/checks-final.log` (last line `exit 0`, 11 passed), `_captures/look/MUTATIONS.log` (each of C01..C11 seen RED), shots `_captures/look/<case>-<step>-<w>x<h>.png` (cases live, three, none, empty; steps default, finish-*, finger, off), driver `_captures/look/shoot.ts`.
