# Lane part-notes

Owner of `content/part-notes.json`, the plain-words note for each part (`what`, `why`, `checked_against`, `model_names`).

## Regenerate

The file is written by `collector/tests/part-notes/gen_notes.py`. The wording lives in that script as groups: parts of one kind share one text, and every line of `design/bom.csv` must fall in exactly one group (the script stops with the line named when one does not).

    python3 -I collector/tests/part-notes/gen_notes.py

It rewrites `content/part-notes.json`; a path argument writes elsewhere. A test (`test_generator_reproduces_file`) fails when the file and the script disagree, so edit the script, never the JSON by hand.

## When the parts list changes

A new bom line makes the script stop: add it to a group (or a new `g(...)` call) with `what` of at most NOTE_WHAT_WORDS and `why` of at most NOTE_WHY_WORDS words, no figure that is not in the bom row or `design/architecture.md`.

## model_names

Ring: read from `design/mech/thin/placement.csv`. Each row's `reference` names the parts-list ref; rows with an empty `reference` are mapped by the `NO_REF` table in the script (for example `joystick_cap` to CAP1). The row's `part` is the 3D object name stored in `model_names`. A new placement row with no reference and no `NO_REF` entry stops the script. If the table does not exist the ring lists stay empty and the check accepts that.
Case: the names come from `design/case/out/case_params.json` `parts` and are written in the script's `C` list.

## Check

    .venv-pytest/bin/python -m pytest collector/tests/part-notes -q

Checks: C01 coverage, word limits, model names exist, every placement object is linked; C02 no invented figure; C03 report against the live bom (prints, never fails). The last two are in the same test file.

## What goes red and what only reports

- The wording is locked: `test_generator_reproduces_wording` compares what, why and checked_against with the generator's output, and ignores `model_names`.
- `model_names` is not compared on the live design. The linking rule is tested on `collector/tests/part-notes/fixtures/placement.csv` (the generator takes the placement path as its second argument).
- `test_live_model_names_report_never_fails` prints the notes whose `model_names` differ from the live `design/mech/thin/placement.csv`, and the refresh command `python3 -I collector/tests/part-notes/gen_notes.py`. It never fails on live data.
