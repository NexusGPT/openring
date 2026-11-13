# collector-behaviour

File: `collector/extract/behaviour.py` (record `firmware-rules`, written as `behaviour.json`). Tests: `collector/tests/collector-behaviour/test_behaviour.py` (6 tests, run with `node scripts/run-pytest.mjs collector/tests/collector-behaviour`).

Reads `design/firmware.md` by table headings (1.1 states, 1.2 transitions, 2.1 button gestures and parameters, 2.2 joystick, 3.1 motors, 3.2 light), never by state name. Real source: 14 states, 60 transitions, 6 motor patterns. Basis `A3` (what firmware.md follows), current `A5-draft` (architecture.md), so the runner marks the record stale.

Schema change (additive, optional): `notes` (text + source) in `contract/schema/firmware-rules.schema.json`, then `npm run gen:types`. It carries five plain notes from `design/architecture.md` (16.5 lines 365-367, 17.3 line 443, 17.8 line 494): four joystick switches, centre press = two opposite switches within 40 ms, record button its own switch.

Not done: the double-press minimum gap (60 ms) has no field in the schema, so it stays in `timing_text` only. Event kinds come from words in the event text (see `classify`), so a new kind of wording lands in `other`.

Proof: `_captures/collector-behaviour/red.log` (extractor absent: 6 failed), `green.log` (6 passed).
