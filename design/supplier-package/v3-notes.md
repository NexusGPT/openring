# Supplier package version 3: notes of the builder (2026-11-12)

Basis: commit 78681c7 (the script reads the last commit by itself; I ran no git command myself). Inside model v7, case C5d.
All logs named here are in `supplier-package/trial-v3/logs/` unless a path says otherwise.

## Result of the trial build
- Command (log `trial_build_final.log`):
  `nice -n 19 python3 design/tools/build_supplier_package.py supplier-package/trial-v3 --trial-pictures-from-working-folder`
- Last line `RESULT PASS`, exit 0, 301 files, zip 52.8 MB, from commit 78681c7. The line before it: `cover page: 301 files, 82 parts-list lines, 65 drawing sheets, 88 maker files, 15 custom parts, case fit check PASS, 3447 pairs checked, 0 failures`.
- The trial switch `--trial-pictures-from-working-folder` was needed only because the 8 new pictures are not in a commit yet. Folder and zip carry `-TRIAL-uncommitted-pictures` in their name and the cover page prints "TRIAL BUILD: not for sending". The final build does not use the switch.
- File count of the trial: the manifest has 300 rows plus MANIFEST.csv itself = 301 (`wc -l` of MANIFEST.csv gives 301 with its header line); the cover page says "301 files" (`grep` in 00-READ-FIRST.html); the one-page PDF says "301 files" (`one_pager_text.txt` line 34, made by `pdftotext` from `supplier-package/trial-v3/ring-recorder-one-pager-TRIAL.pdf`). The one-pager script reads the count from the package folder and stops if the folder differs from its manifest (`one_pager_final.log`).
- Earlier trial runs, all kept as logs: `trial_build_try1.log` to `trial_build_try3.log` ended RESULT FAIL while I tuned the check (try1: lines of the long records that name removed parts; try2: three lines of the v7 handover, the microphone study and a `.log` file copied without path cleaning; try3: one line of the v7 handover). `trial_build_try4.log` ended RESULT PASS. `trial_build_try5_before_snapshot_cleanup.log` ended RESULT PASS (before the script learned to delete its scratch copy of the commit). The output folders of try1 to try5 were deleted before the next run (disk, and the script refuses an existing folder). Only `trial_build_final.log` counts.

## Faulty trials (the new check fails)
- `faulty_A_removed_part.log`: extra files added by `--trial-extra` (the old light guide STEP from `old_v63`, and `record-cap.md`). Ends `RESULT FAIL` (exit 1) with four lines that name the fault: removed part named in a file name (light guide) `02-3d/maker-files/light-guide/light-guide.step`; removed part inside a model file (light guide); removed part named in a file name (record button) `05-mechanical/specifications/record-cap.md`; removed part (record button) named as current at `record-cap.md:1`.
- `faulty_B_missing_custom_part.log`: `--trial-omit "joystick-frame/joystick-frame.stl"`. Ends `RESULT FAIL` (exit 1): "custom part joystick-frame (size all, STL) has no file in the package".
- `faulty_B_try1_omit_not_applied_to_tree.log`: my first run of B ended RESULT PASS: the omit flag did not reach files taken by whole-folder rules. That was a fault in my test hook, fixed, then B was run again (the log above). Reported because it shows the first B run proved nothing.
- The output folders of the faulty runs are deleted (listing before deletion: `listing_before_cleanup.log`). The scratch copies of the commit that my runs left in the system temp folder are deleted (`snapshots_made_today.log` lists them, `snapshots_after_cleanup.log` shows the two that were not mine remain).

## What the new checks do (in `design/tools/build_supplier_package.py`)
1. Ring-side files only (the case has its own LED1 and light window, those stay). Fails on: a file name that names a removed part (light guide, light plug, recording light, record button, joystick nub; the spec page `joystick-nub.md` is allowed by name because it keeps its old name and other files cite it, its content is the round cap CAP1 and frame FRM1); a stale-version name (`old_*`, `merged32a` to `g`, `_v1` to `_v6`, `_before_`, `c5a/b/c`); a solid named after a removed part inside a STEP or GLB file; a text line that names a removed part without a removal marker word (for example "removed", "was", "pin", "broken").
2. Fails if a row of `02-3d/maker-files/index.csv` (every custom part, every ring size) has no file in the package, if a custom part has no drawing sheet, or if `part-map.csv` names a part not in the index.
3. Fails if the case fit check log in the package does not end in PASS; the cover page takes its pair count from that log.
4. Fails if the cover page keeps an unfilled field or does not name the file count.
- Limit of check 1, stated plainly: it is a marker-word rule on text lines, so it can miss a line that names a removed part together with a marker word, and it flags nothing in pictures. Pictures were looked at by me (below).

## Files in the list: removed and why
- Exterior files `merged32g` (5 pictures `merged32f-*`, `merged32g-us7/us8-before-after.png`, `ring-merged32g.glb`, 7 STEP, 7 measures JSON, `merged32g-report.md`): replaced by the `merged32h` files (round joystick). The old pictures show the rectangular nub; `merged32f-screen-end.png` shows the recording light window.
- `design/mech/thin/out/v5/v5-joystick.png`, `v5-hand-end-below.png` (the picture "inside-microphone-and-light"): v5, show the light guide, LED1, the old nub.
- `design/mech/light-path/light-path.md` (study of the recording light): feature removed.
- `design/mfg/maker-files-v62-notes.md`: replaced by `mfg-notes.md` (v7). `maker-files-v63-notes.md` is not used ("not regenerated").
- Maker-file tree: `old_v63/` (light guide, light plug, rectangular nub, v6.2 index) is skipped; `old_merged32c` skipped as before. The drawings rule takes only `design/mfg/drawings/*.pdf`, so `drawings/old_v63/` is not taken.
- `merged32h-us9-before-after.png` is not used: its left half shows the removed rectangular nub.

## Files in the list: added and why
- 8 new pictures (named in the list, source `design/mech/thin/out/v7/pictures/`): `v7-ring-exterior-iso.png`, `-top.png`, `-joystick.png`, `-underside.png` (exterior merged32h, no recording light), `v7-joystick.png`, `v7-hand-end-below.png`, `v7-board-underside.png`, `v7-band-cross-section-view.png` (inside model v7). Packaged under `01-product/pictures/` with names `ring-exterior-*` and `inside-*`.
- Case: `case-post-closeup.png`, `case-post-closeup-ring.png` (new in C5d), `case_pin_holder.stl`, `case_pin_board_pcb2.stl`, `c5d-open-points-handover.md` (as `case-c5d-handover.md`), `c5d_check_lead_rerun.log` (as `case-fit-check-log.txt`, PASS 3447 pairs). `case/out/parts/*.step` already includes `pin_holder.step` (glob).
- v7 notes: `design/mech/thin/v7-handover.md` (as `model-v7-handover.md`), `design/mfg/specs/v7-refresh-notes.md` (as `what-changed-in-v7.md`), `design/ecad/ring/v7-wiring-notes.md` (as `wiring-notes-v7.md`), `design/mfg/part-map.csv`, `design/mfg/mfg-notes.md`.
- Switched to the current exterior: `ring-merged32h.glb`, `ring-merged32h-us7..13.step`, `measures-merged32h-us7..13.json`, `merged32h-report.md`.
- Coverage: the maker-file tree takes all 88 STEP/STL/CSV files of `design/mfg/parts/` (15 custom parts, including `joystick-cap` and `joystick-frame` with STL) and the drawings glob takes 65 sheets including `joystick-cap.pdf` and `joystick-frame.pdf`; the check proves every row of `index.csv` is present.
- History banner: the script puts a banner on top of 6 long working records that still name removed parts in older sections (`design-record.md`, `requirements.md`, `model-notes.md`, `wiring-notes.md`, `ring-parts-list-notes.md`, `microphone-path.md`) and does not scan them line by line. This is a decision of mine; see finding 2.

## Pictures of the inside
- Rendered by script, no browser: `design/mech/thin/out/v7/pictures/render_v7.py` (copy of the v5 matplotlib renderer; it stops if the model file holds a node named after a removed part) and `render_exterior_v7.py`. Logs `render_v7_final.log`, `render_exterior_v7_final.log` in that folder (each has the sha256 of its input: inside model `thin-inside.glb` 41142fd5...; exterior `ring-merged32h-us9.glb` d5ee0572...). The model's 47 nodes are listed in `v7-nodes-drawn.txt`: no light guide, light plug, LED1 or record button.
- The exterior renderer leaves out the exterior file's separate `light` node (see finding 1). I opened the pictures myself: no recording light, round cap. Earlier tries are kept as `render_v7_try1.log` and `render_exterior_v7_try1.log` to `try5.log` (exterior try1 to try4 stopped with an error or read the glb wrongly; try5 drew but mixed glass and body faces, fixed in the final).
- Limit: the pictures are flat-shaded software renders, not photos; the ribbon heads show triangle edges.

## Files the lead must commit before the final build
All paths under ``:
1. The 8 pictures: `design/mech/thin/out/v7/pictures/v7-ring-exterior-iso.png`, `v7-ring-exterior-top.png`, `v7-ring-exterior-joystick.png`, `v7-ring-exterior-underside.png`, `v7-joystick.png`, `v7-hand-end-below.png`, `v7-board-underside.png`, `v7-band-cross-section-view.png`. Without them the final build ends RESULT FAIL ("missing source ... commit it before the final build").
2. Their scripts and logs: `design/mech/thin/out/v7/pictures/render_v7.py`, `render_exterior_v7.py`, `inspect_ext.py`, `list_nodes.py`, `list_nodes.log`, `v7-nodes-drawn.txt`, the `render_*` logs.
3. `design/tools/build_supplier_package.py`, `design/supplier-package/READ-FIRST.template.html` (the script reads the cover template from the commit, so the new template must be in it), `design/supplier-package/make_one_pager.py`, `design/supplier-package/v3-notes.md`.
4. The trial folder `supplier-package/trial-v3/` is mine; it is not part of the final package. Do not commit its zip.

## Exact command of the final build (after that commit)
```
cd . && nice -n 19 python3 design/tools/build_supplier_package.py
```
It writes `supplier-package/ring-supplier-package-<date>-<new commit>/` and `.zip`, and must end `RESULT PASS`. Then the one-page PDF:
```
cd . && nice -n 19 design/.venv/bin/python -I design/supplier-package/make_one_pager.py <out.pdf> supplier-package/ring-supplier-package-<date>-<new commit>
```
The page prints "N files" from the package it is given, so run it on the final package only. A new commit changes the folder name; if the folder of the same name exists the script refuses.

## Findings for the lead (outside my files)
1. **Exterior files still hold a `light` solid.** (Checked 2026-11-13: stale for the files now on disk. `grep -c -a -i light` gives 0 on all seven `design/look/s1/out/ring-merged32h-us*.step` and all eight `ring-merged32h*.glb`, log `design/wiring/text-pass-work/check_light_solid.log`. The statement below describes the files of the package at the time.) Every `ring-merged32h-us*.step` and `ring-merged32h*.glb` has a solid named `light` (the window skin; `design/look/s1/exterior.py` lines 872 to 883 still make it). v7-handover.md names it as "not used by the model". The new check lists it as a KNOWN OPEN POINT on every build (8 lines in the final log) and the cover page tells the supplier to ignore it. A real fix (exterior without that solid, then new STEP files) is outside my files; until then the package ships a removed part inside 8 files. The case assembly has no such solid in the ring.
2. **Long records still describe the recording light.** `design/architecture.md` (dozens of lines, for example lines 23, 24, 153, 154, 284, 692 in the package copy), `requirements.md` (requirement U5 "Recording light", D5 "record button"), `thin-notes.md` and others. I did not edit them; the package carries a banner on top of each. A clean v7 extract of the design record would remove the ambiguity the owner asked to avoid.
3. **Circuit board files** `design/ecad/ring/pcb/` still hold R41, LED1 and Q2 (v7-handover.md). They are not in the package (as before); the cover page states it.
4. `design/mfg/specs/record-cap.md` has no v7 content and is not in the package. (Checked 2026-11-13: `grep -c v7` gives 0, true; the page describes a part the design removed and now says so at its top.) `case-side.png` is the C5c render (the outside did not change, said in c5d-open-points-handover.md); I did not re-render it.
5. The cover page's older open points S15 (antenna pads off the board) and S27 (screen cable) were kept: `design/architecture.md` lines 513 and 525 still show them open. The recording time (4.3 to 7.8 hours) is stated as "calculated before the light was removed, not recalculated" because v7-handover.md says the 2.6 mA figure has no number for the always-lit sign yet.

## Not in the package
Datasheets of bought parts; circuit board fabrication files and the board work files (they do not exist or still hold R41, LED1, Q2); software code; full tolerance drawings; the removed parts' files (recording light, light guide, light plug, rectangular nub, record cap); the exterior pictures of earlier versions; the phone application; `firmware/` and `design/review/`.

## Not done / unverified
- I did not check that the working-folder files equal the commit's files; the package comes from the commit, the 8 pictures come from the working folder. The inside GLB in the commit matches the one I rendered (same sha256 41142fd5... in `hash_check.log` and in MANIFEST.csv); the exterior picture source `ring-merged32h-us9.glb` is not a packaged file, its commit state is unverified.
- The cover page's hand-typed design facts (block size, band size, materials, cell sizes, chips) were kept from version 2 where I had no reason to change them; I did not re-derive them from the design record. Counts and names are computed.
- No browser, no upload, no supplier contact, no git command by me.

RESULT: done, trial build ends RESULT PASS with 301 files (cover page and one-page PDF name 301) and two faulty trials end RESULT FAIL naming the fault; the lead must commit the 8 new pictures and the script, template and notes before the final build, and finding 1 (a `light` solid in the 8 exterior files) is open.
