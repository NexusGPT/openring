# Ring software: specification and approved build plan

Approved by the owner in plan mode on 2026-11-11. Owner, the same day: "You build the ring software Operating System. Goal is to be able to connect to notification and control iPhone, Android and Mac".

The design is `design/software/os/design.md`. The behaviour specification is `design/firmware.md`. The work pieces and their files are `docs/lane-dag.json` in this folder. The approved plan follows, word for word.

# Ring software: build plan

## Context

- You said: "You build the ring software Operating System. Goal is to be able to connect to notification and control iPhone, Android and Mac".
- Today the ring has a full behaviour specification (`design/firmware.md`, version F6) and no code.
- The design for your goal is written and saved: `design/software/os/design.md`. It rests on two fact files with a source for each finding (`research-platforms.md`, `research-sdk.md` in the same folder).
- No hardware exists here. So every step below ends with a proof that runs without hardware, and the plan says what stays unproven.

## What version 1 does

| Device | Control by the ring | Notifications on the ring | Extra software on that device |
|---|---|---|---|
| iPhone | yes | yes: app, title, message, two actions (for example dismiss, answer) | none |
| Android | yes | yes, through a small helper app | the helper app (a later step, section "Not in this plan") |
| Mac | yes | no supported way was found | none |

- Control means: the ring acts as a standard Bluetooth keyboard and media remote. Three modes on the ring: media (play or pause, next, previous, volume), presenter (next and previous slide), pointer (the joystick moves a pointer, the centre clicks).
- Up to three paired devices. You pick the active one on the ring.
- A long press on the joystick's centre still starts and stops a recording in every mode. No device can start or stop a recording.

## How it is built

- **Base:** Nordic's software kit (nRF Connect SDK 3.4.2) on Zephyr. Its ready parts for Apple's notification, media and time services and for the keyboard role list the ring's chip.
- **One new folder in the project:** `firmware/`, with the application, its tests and the two stand-in devices used for the Bluetooth tests.
- **Where it is compiled and tested:** on your Linux server, inside Nordic's own toolchain image. The simulation of the ring's chip does not run on a Mac. This Mac only holds the source and receives the results.
- **The behaviour specification stays the base.** Its Bluetooth section is rewritten for three paired devices and the new services, as version F7, with its check.

## Steps, each with what you get and how it is proven

| # | Step | What exists at the end | Proof (can fail) |
|---|---|---|---|
| 1 | Workspace and core | `firmware/` builds on the server with one command. The state table and the joystick gestures of the specification are code. | Every row of the state table and every gesture is a test; the tests run on the simulated board and pass; one deliberately broken copy fails. The real build for the development kit target compiles, and its flash and memory use are reported. |
| 2 | Devices and control | Pairing with a passkey, three paired devices, switching the active one. Keyboard, media keys and pointer in the three modes. | Two simulated devices over the real Bluetooth software: a stand-in computer pairs with the ring and receives the right key for each joystick action in each mode; after a switch, the second stand-in receives the keys and the first receives none. |
| 3 | iPhone | Notifications with their actions, the track title and media commands, the time. A store of the last notifications. | A stand-in iPhone that serves Apple's three services sends notifications; the ring's store holds them; a dismiss chosen on the ring arrives at the stand-in; the ring's clock takes the stand-in's time. |
| 4 | Screens | Watch face, notification list and detail, the three control screens, the device picker, pairing, recording. | Each screen is drawn by the real screen code on the simulated display and saved as a picture. You judge the pictures. |
| 5 | Relay for Android | A small service of our own on the ring that accepts notifications from a helper app, and its written specification for that app. | A stand-in helper sends notifications through it; they land in the same store and screens as the iPhone's. |
| 6 | Recorder parts | Microphones, storage, USB transfer, power and factory tests of the specification, written against simulated drivers. | The storage format, the transfer commands and the power rules run as tests on the simulated board. The drivers themselves stay unproven. |
| 7 | Ring board | The board description of the real ring (pins, power chip settings, memory layout). | It compiles. Nothing more can be proven without a board. |

After each step I show you the result and the usage it cost before I start the next one.

## Who does the work

- I write the design decisions and check every result myself.
- Helpers write code and tests, one piece each, with its own files. They never judge their own work: a separate helper reads each step's code and tests against the specification before I call the step done.
- At most three helpers at a time on the server.

## My readings, used unless you change them

1. **Your Linux server is the build machine.** It is already rented. The toolchain image takes about 10 GB there. Nothing heavy is installed on this Mac.
2. **Standard Bluetooth services replace the home-made phone link as the first link.** The home-made link (four failed reviews) stays paused. Its two open questions are answered by this plan: iPhone, Android and Mac control and notifications come first; the ring's own status and recordings over Bluetooth come later.
3. **Mac notifications are left out of version 1.** No supported way was found. If you know one, I add it.
4. **Two devices at the same time** (for example iPhone notifications while the ring controls the Mac) is tried in step 2 and kept only if the simulation holds. Otherwise the ring serves one device at a time.
5. **Pairing uses a six-digit passkey shown on the ring's screen**, as the specification already says.
6. **The source stays private**, in this project's own git folder. Nothing is published.

## Not in this plan

- The Android helper app. Step 5 writes its specification; building and publishing the app is its own job and needs a real phone.
- The phone application for recordings and transcripts.
- The driver for the ring's screen (none exists for this screen; it needs screen samples).
- Anything on real hardware: flashing, radio range, battery life, real phones and a real Mac.

## What stays unproven until a development kit is on a desk

- Pairing and behaviour with a real iPhone, Android phone and Mac. Apple states that its notification service can change at any time.
- Memory use on the real chip beyond the build's own report.
- Power, radio, microphones, storage and the screen.
- To close these you need: Nordic's nRF54LM20 development kit and the nPM1304 evaluation kit. I list the order codes when you want them.

## Risks

- **The kit's support for this chip is young** (marked experimental in an earlier release). If a ready part does not build for the chip, I report it with the error and build that step for the sister chip's simulation first.
- **Simulation is not a phone.** A stand-in iPhone that I write can share a wrong reading of Apple's document with the ring. A real iPhone is the only full proof.
- **Server load.** Other work of yours runs on the same servers. Builds run at low priority.

## Files this plan creates or changes

- New: `firmware/` (application, tests, the two stand-in devices, build and test scripts, a README that says how to build, test and what is not built).
- New: `design/software/os/android-helper-spec.md` (step 5), `design/software/os/screens/` (pictures, step 4).
- Changed: `design/firmware.md` to version F7 (Bluetooth section) with its check; `design/architecture.md` section 18 (software platform) with the decision of this plan.
- Reused as they are: the state table, gestures, storage format, USB commands, power rules and factory tests of `design/firmware.md`; the pin list of the wiring files; the samples of Nordic's kit named in `design/software/os/research-sdk.md`.

## How it is verified end to end

1. On the server: one command builds everything and runs every test; its last line says pass or fail and it exits with an error on any failure.
2. Each step has one broken copy that must fail, kept with its log.
3. I rerun the command myself after each step and read the logs; a separate helper reviews the code against the specification.
4. You judge the screen pictures of step 4, and the result of each step in plain words.
