# Lane notes: behaviour

Files: `src/routes/behaviour/` (index, engine adapter, useBehaviour, press3d, CentrePress, Joystick, Readout, StateList, model, states, nodes, behaviour.css), `tests/checks/behaviour/` (behaviour.spec.ts, run.config.ts), captures `_captures/behaviour/`.

## What it does
- Panel: state now (large, label from `firmware-rules`), the light, the recording timer, highlight marks, vibration marks (one per motor pulse, fading), one joystick pad: four directions around a centre press with a progress ring (the ring has no separate record button since 2026-11-10), what each gesture does in this state, and every firmware state as a chip with the current one marked.
- The screen holds no rule. `engine.ts` keeps a log of press, release and joystick events with times and replays it through `src/engine/behaviour` (`initialModel`, `step`, a closing `tick`). Hold time, transitions, pulses, light and timer all come out of the record through the engine.
- Hold: pointer on the joystick's centre (`behaviour.joystick-centre`), Space (focus on it or on the page body), or a press on the joystick of the 3D ring (`press3d.ts`: the stage reports only clicks, so the hold is read from `__stage.screenPos('joystick')`; moving the pointer more than 6 px cancels it, so a drag turns the ring and is not a press). The progress ring fills from the engine's hold time.
- Stage steering: `show: exterior`, `screen` = the ring screen whose label names the firmware state (`model.ts screenFor`), `light` = engine light.
- Honest states: missing / unparsed = one banner, no controls; stale = the contract sentence and all content dimmed.

## Checks (`tests/checks/behaviour`, run: `npx playwright test -c tests/checks/behaviour/run.config.ts`)
Own apps on 8831 (live) and 8832 (empty). C01 rest state · C02 held mouse press · C03 Space · C04 short hold changes nothing · C05 tap highlight, second hold stops · C06 progress ring · C07 press on the 3D record cap, drag only turns · C08 state list · C09 stale · C10 empty bundle · C11 no page scroll at 3 sizes. Mutation log: `_captures/behaviour/MUTATIONS.log`.

## Open points for other pieces
1. Stage: no hook to pulse the ring on a vibration and no press/hold event on a part. The screen shows vibration on the panel only; the 3D press is read through `screenPos`.
2. Stage face: the timer drawn on the ring's screen does not follow the engine's timer (it shows a fixed time).
3. The `record_cap` node is the only stage node name in source (`nodes.ts`); the exterior's own `button` node is not a stage part.

## Not proven in a browser
- The one-control change of 2026-11-10 (CentrePress inside Joystick, `PRESS_NODE = 'joystick'`) passed the type check and the unit tests only. The owner's order of 2026-11-10 forbids browser runs, so `tests/checks/behaviour` and `journeys/J5.spec.ts` were edited to the new ids and not run.
