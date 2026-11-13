# Ring software step 6 (the recorder parts): report to the owner

Date: 2026-11-13. Code: commit 344a8979. Proof: the lead's own run of the whole build and test on the server, 19:00 to 21:11, last line `RESULT PASS`, 43 stages with exit 0 (`firmware/build-logs/step6/20261113-190009-lead-full4.log`).

## What exists

- The recorder of the specification, written against simulated drivers: microphones, storage on the card, USB transfer, power and charging, the motor, the watchdog and crash record, the factory tests, and the part that joins them to the core and the screens.
- A long press on the joystick starts and stops a recording through these parts. The screen shows the recording sign before the microphones get power.
- The real driver files exist for each part. They compile for the development kit and never run: the kit has no card, microphones or power chip of the ring.
- Ten new test suites for the join, and one or more suites per part. The notes of each part are in `firmware/docs/` (`recorder-notes.md` is the join's).

## What is proven, in simulation

- All suites of steps 1 to 6 together: 732 of 732 test cases pass on each of the two simulated targets. Step 5 had 346.
- The five two-device Bluetooth tests of steps 2 to 6 pass with the recorder built in (control, iPhone, relay, screens, factory).
- Broken copies: the run prints 331 times that a deliberately broken copy failed on its own named case, as required. A copy that runs on both targets counts twice in this figure.
- Four searches pass, each with a planted fault that the same search finds: one place only turns the microphones on; no recorder part can start or stop a recording by itself (only a long press does); no step 6 file names a chip pin by number; the kit build has the simulated drivers switched off.
- The build for the development kit compiles: 585,128 bytes of flash (60.03 percent), 461,528 bytes of RAM (88.20 percent). Step 5 was 522,212 and 183,080.
- Two independent reviews read the code against the specification. The first found 6 major and 8 minor faults. The second passed the fixes: 0 major open, 10 new minor faults and 3 notes. The 10 minor faults are fixed in this commit; 2 notes stay as they are (one test counts a call and not its effect; after a failed shipping sleep the radio stays off until a restart).

## One finding you should know: RAM

- The kit build uses 461,528 of 523,264 bytes of RAM. The specification's budget (section 4.6 of `design/firmware.md`) is 305,408 bytes. The build is 156,120 bytes over that budget and 61,736 bytes are free.
- The largest users, from the build's own symbol list (`firmware/build-logs/step6/lead-full4-kit-ram-symbols.txt`):
  - the audio queue of 3 chunks: 100,296 bytes (in the budget: 99,840);
  - a full picture of the screen held in memory: 57,600 bytes (the stand-in for the missing panel driver; not in the budget);
  - two work buffers of one chunk each in the storage part: 66,560 bytes (not in the budget);
  - the USB transfer part's state with its buffers: 34,828 bytes (budget: 32,768).
- It fits and it runs. The budget in the specification is wrong, or two of these buffers must shrink. I settle this in step 7, where the real ring's memory layout is written.

## Decisions I took for you (you can change each one)

- Shipping sleep: the ring closes USB first, tries once more to close the card, then sleeps even if the card stays busy. It writes event 0x0290 in that case.
- Shipping sleep waits at most 1,000 ms for the screen to go dark.
- When the cable is pulled during a transfer, the ring waits for the running card command, then closes the card. The worst case is about 10 seconds.
- The 18 choices of the build plan and the later rulings are written, each with its reason, in `firmware/docs/step6-plan.md` (the sections "Lead's rulings") and `firmware/docs/recorder-notes.md`.

## Not built, not proven

- No real driver ran. Microphones, card, USB, power chip, motor, watchdog and update are proven on simulated drivers only. The list by part is section 7 of `firmware/docs/step6-plan.md`.
- The real USB file compiles and is unproven: in a standalone try its start call failed on the virtual controller.
- The ring's USB vendor and product numbers are the kit's test pair, marked not for shipping.
- The screen's panel driver is not written. Sound quality, battery life, charging and the felt motor pulse need hardware.
- The fixes of the second review's minor findings were rerun by the lead and not read by a third reviewer.
- Stack use on the real chip is not measured.

## Usage

- One planner (Opus): a build plan of 11 units with 18 choices for the lead.
- Eleven builders, one per unit: two on Opus (the shared base and the join), nine on Sonnet. One more Sonnet builder for one failing check.
- One fix builder (Opus) over two rounds.
- Two independent reviews (Opus).
- Four full runs by the lead on the server, 43 stages each. The first failed one stage (a broken copy of the screens test that did not fail); the next three passed. Each took about two hours because the server carries other work.
- Clock: started 2026-11-13 03:48, finished 2026-11-13 21:11.
- Token figures are not visible to the lead.

## Question only you can answer

- The ring's USB numbers: buy a vendor number, or use a product number lent under another vendor? Nothing waits on it before a ring ships.
