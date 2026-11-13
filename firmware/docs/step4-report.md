# Ring software step 4 (the screens): report to the owner

Date: 2026-11-12. Code: commit 1c99739. Proof: the lead's own run of the whole build and test on the server, 18:24 to 19:10, last line `RESULT PASS`, 23 stages with exit 0 (`firmware/build-logs/step4/20261112-182447-lead-step4-r3-rerun.log`).

## What exists

- The screens of the ring, drawn by the ring's own code on a 240 x 120 picture that one function turns for the 120 x 240 panel.
- 21 pictures: status, recording (full, with a highlight, dimmed), notification list (empty and filled), one notification with its two actions, menu, control mode list, the four control screens, device list, one device, pairing code, a question, two messages, charging, settings.
- The rules behind them: which screen follows which state and which joystick action, the screen times, the joystick lock, the menu, the settings.
- The picture sheet: `design/software/os/screens/all-screens.png`. You judge the look from it.

## What is proven, in simulation

- Each of the 21 pictures is drawn, read back from the display memory and checked on two simulated targets. The saved pictures are byte for byte the ones of the lead's run (84 files compared).
- Each picture check rejects the other 20 screens (420 of 420), a blank frame and a white frame, and reads key values: the time, the timer, the pairing code, the battery percent.
- The screen table is checked row by row (112 rows). 323 of 323 test cases pass on both targets (steps 1 to 4 together).
- The screen is never dark while recording. The dimmed recording screen is driven at panel level 85 of 255, never 0.
- The recording sign is drawn by one thread. A start that times out is cancelled and never drawn later.
- A ring with its screens against the stand-in iPhone of step 3 over Bluetooth: the list, the detail, a dismiss chosen on the screen, the pairing code, a power off (38 checks).
- A second paired device no longer takes over: the first device stays the active one (changed in the devices part of step 2, tested over Bluetooth).
- 16 deliberately broken copies of the screens and 3 broken copies of the Bluetooth test each fail on their own named check. The broken copies of steps 1 to 3 still fail as required.
- The real build for the development kit compiles: 518,984 bytes of flash (53.25 percent), 182,184 bytes of RAM (34.82 percent).

## Decisions I took for you (you can change each one)

- The notification list opens with Up from the status screen.
- "Battery low" shows for 5 s in amber, and never interrupts the pairing code or a control session.
- "Power off" is in the menu only in standby.
- A notification with no title shows the word "Notification". The app identifier is never shown.
- A newly paired device becomes the active one only when none is active.
- The fourth control mode ("Agent": accept or decline a request) is built with words only, no logo. Keep it or drop it: your call.
- The built-in font of the drawing library is kept. No outside font was added.

## Deviations from the specification

- The picture is landscape (the specification said portrait). It follows the screen designs you accepted.
- The status and recording screens do not show the battery, the storage left or a Bluetooth icon. They follow the accepted designs, and no part gives these values yet.
- The pairing screen stays on for its whole 60 s (a code that disappears after 5 s cannot be typed).
- The waveform on the recording screen is a drawn set of lines. It is not live.
- All of these are written into `design/firmware.md` (version F7 part 4, its check gives 0 failures).

## Not built, not proven

- No real panel has shown a picture. The driver for the ring's panel is not written; the code draws on a display kept in memory.
- Nothing calls the function that starts the recording sign yet. The recorder (step 6) must call it before it powers the microphones, and must refuse to record when the sign is not drawn.
- Stack use on the real chip is not measured. The figures are static sums with a margin.
- The memory for the drawing library (32,768 bytes) is sized from one pass of the picture test (peak 8,848 bytes). No long run exists.
- The settings are not saved. Device names do not come from Bluetooth yet.
- The screens for the recordings list, transfer, errors and the factory test are a title and one line.
- Which way the panel is turned on the real ring is not known.
- Round 3's changes were rerun by the lead and not read by a third independent reviewer.
- The second review's remaining notes (a short stale window of the lock fact with no bad effect found, a weak picture check for a screen outside the 21) are listed in `firmware/docs/step4-review2.md`.

## Usage

- One builder (Sonnet) over three passes: the first build and two correction rounds.
- Two independent reviews (Opus). The first found 15 points, the second closed 10 of them and found 13 new ones (1 major, fixed in round 3).
- Three full runs by the lead on the server. Two ran to the end in about 47 minutes each and passed. One gave no usable result: the builder's cleanup on the server deleted part of its files.
- Clock: started 2026-11-12 10:20, finished 19:10, with one stop of about 20 minutes on connection errors.
- Token figures are not visible to the lead.
