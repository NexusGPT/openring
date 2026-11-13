# behaviour-engine

Files: `src/engine/behaviour/engine.ts`, `index.ts`, `engine.test.ts` (7 tests, `npx vitest run src/engine/behaviour`).

A pure interpreter of `behaviour.json`. `createEngine(rules).send(event)` takes `press`, `release`, `tick`, `joystick` or `signal` events with times and returns `{state, light, pulses, pulseCount, highlights, recordingMs, screen, fired, joystickEffect}`. `step(rules, model, event)` is the pure form. Gestures (long hold, short press after its window, double press) are recognised from the record's own timings; transitions, motor patterns, light rule and screen text come from the record. The resting state is derived: the state a long press leaves for a microphone state that a long press leaves back. Highlights count transitions whose action text says "highlight"; the timer runs while the state has the microphones on.

Tests use a made-up three-state record; one more test runs the live `public/data/behaviour.json` (skipped when the collector has not made it). `grep -rn 'RECORDING\|STANDBY\|1000' src/engine` returns nothing (`_captures/behaviour-engine/grep.log`).

Not done: the double-press 60 ms minimum gap (not in the record); BLE and other signals are accepted as `signal` events by kind but no screen sends them yet.

Proof: `_captures/behaviour-engine/red.log` (a broken long-hold check: 4 failed), `green.log` (7 passed).
