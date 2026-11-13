# Ring software: design for "connect to notifications and control iPhone, Android and Mac"

Date: 2026-11-11. Owner, the same day: "You build the ring software Operating System. Goal is to be able to connect to notification and control iPhone, Android and Mac".

Sources: `research-platforms.md` (RP, what the three systems accept; tags [F] page read, [S] search text) and `research-sdk.md` (RS, the parts of Nordic's nRF Connect SDK v3.4.2, file and line per finding) in this folder; the behaviour specification `design/firmware.md` version F6 (FW). Nothing here is tried on hardware.

## 1. What the goal means per device

| Device | Control by the ring | Notifications on the ring | Extra software on that device |
|---|---|---|---|
| iPhone | yes: the ring acts as a Bluetooth keyboard and media remote (HID over GATT; Apple's guidelines cover it, RP 2 [F]); Apple's media service also gives play, pause, next, volume and the track title (RP 2 [F]) | yes: Apple's notification service gives category, app, title, message and two actions per notification, for example dismiss or answer (RP 1 [F]) | none |
| Android phone | yes: Android lists the HID over GATT host profile (RP 5 [F]) | only through a helper app: Android has no standard Bluetooth notification service (RP 4, not found); an app reads notifications with the user's permission and sends them on (RP 4 [F]) | a small helper app, for notifications only |
| Mac | yes: Bluetooth keyboards and mice connect (RP 7 [F], generic text) | not found: Apple's notification service is described for the iPhone and iPad only, and no way for an app to read other apps' notifications was found (RP 6) | none for control; notifications stay open |

So version 1 can promise: control of all three with no app, and notifications from the iPhone with no app. Android notifications need the helper app. Mac notifications have no known supported way; this is stated, not hidden.

## 2. Design choices

1. **Standard Bluetooth services first.** Control uses the standard keyboard and media-remote role. iPhone notifications, media and time use Apple's three services. This replaces the home-made phone link (design/protocol, four failed reviews) as the first link. A small service of our own carries only what no standard covers: notifications relayed by the Android helper app, and later the ring's own status and recordings.
2. **Up to three paired devices, one active.** The ring keeps one Bluetooth identity per paired device and switches identity to switch device, as Nordic's multi-device product does (RS 5 [F]). The wearer picks the active device on the ring. Holding two devices at once (for example iPhone notifications while controlling the Mac) is allowed by the settings but shown by no example (RS 5): it is tried in simulation and added only if it holds.
3. **Four control modes on the ring.** Media (play or pause, next, previous, volume), Presenter (next and previous slide, with arrow or page keys), Pointer (the joystick moves a pointer, the centre clicks; on an iPhone the pointer needs AssistiveTouch switched on, RP 2 [F]), Agent (accept with Return, decline with Escape, up and down arrows; keys only, no text). Agent was added on 2026-11-11 from the owner's words "You can even control claude code with it"; the approved build plan lists three modes, so the fourth is a deviation reported to the owner with step 2. The key tables are in `design/firmware.md` section 7.5. Apple's rule is kept: a key is sent only when the wearer acts on a real control (RP 2 [F]).
4. **Recording stays above everything.** A long press of 1.0 s on the joystick's centre starts and stops a recording in every mode (FW 2.1). Control and notification screens use short presses and directions only. No message from any device can start or stop a recording.
5. **Nordic's kit and Zephyr.** nRF Connect SDK v3.4.2. Its notification, media, time and keyboard parts and their examples list the ring's chip target `nrf54lm20dk/nrf54lm20a/cpuapp` (RS 1 to 4 [F]). Media keys need a report table written by hand (RS 3 [F]).
6. **The behaviour specification stays the base.** States, gestures, storage, USB, power and factory tests of FW stand. FW section 7 (Bluetooth) changes: more than one paired device (three, not two), the new services, and security as the examples use it with the ring's passkey screen.

### Rules from Apple's documents that steps 2 and 3 must meet (RP 1, 2 [F])

- The ring advertises the HID service in its advertising data ("the accessory shall advertise the HID Service in the Advertising Data").
- A key is sent only for a real action on the ring's control.
- The ring keeps the keys of each pairing and deletes both sets when a pairing is removed.
- Apple's notification service "is not guaranteed to always be present": the ring subscribes to the Service Changed characteristic and copes with the service appearing and disappearing.
- The service keeps no state across sessions: after a reconnect the ring's store is rebuilt from what the iPhone sends again.
- A media command that was written is not a proof that the player acted: the ring shows the state the iPhone reports, not the state it asked for.

## 3. Parts of the software

| Part | What it does | From |
|---|---|---|
| Core | the state table, gestures of the joystick, time, settings | FW 1, 2 (W12, W9) |
| Devices | pairing with a passkey on the screen, three identities, the active device, reconnect | new; RS 5 |
| Control | keyboard, media keys and pointer reports; the four modes | new; RS 3 |
| iPhone | notifications with their actions, media and track title, time | new; RS 1, 2 |
| Relay | our small service: notifications sent by a helper app (Android) | new |
| Inbox | the store of the last notifications, read and dismissed marks | new |
| Screens | watch face, notification list and detail, control screens, device picker, pairing, recording | FW 3.3 plus new |
| Recorder | microphones, storage, USB transfer, power, factory tests | FW 4 to 9 (W3 to W8, W13) |
| Board | the ring's board description, and one for the development kit | FW 10.2 W1 |

## 4. How each part is proven with no hardware

| Proof | What it shows | Where it runs |
|---|---|---|
| Logic tests | every row of the state table, each gesture, the inbox, the report builder, the device switch, as tests that can fail | Zephyr's simulated board, Linux (RS 6 [F]) |
| Two simulated devices over the real Bluetooth software | the ring against a stand-in iPhone that serves Apple's services, and against a stand-in keyboard host: pairing, notifications arriving, an action sent back, keys received, switching device | the simulated ring chip `nrf54lm20bsim` with BabbleSim, Linux, needs the 32-bit C library (RS 6 [F]) |
| Screen pictures | each screen drawn by the real screen code and saved as a picture for the owner | Zephyr's simulated display (RS 7 [F], not yet tried) |
| Real build | the software compiles for the development kit target; flash and memory use are reported | Nordic's toolchain image `ghcr.io/nrfconnect/sdk-nrf-toolchain` (RS 9 [F]) |

None of this runs on macOS (RS 6). A Linux machine with an Intel or AMD processor is needed.

## 5. What stays unproven until hardware exists

- Real pairing and behaviour with a real iPhone, Android phone and Mac. Apple says its notification service can change at any time (RS 1 [F]). From which iOS and Android versions each key works was not found (RP 2, 5).
- Radio range under the metal body, battery life, the screen driver (none exists for this screen), the microphones and storage.
- The Android helper app: it needs a real phone.
- Memory use against the chip (no figures found, RS 8); the first real build measures it.

## 6. Order of work

1. Workspace, build and test commands on the Linux machine; the core with its logic tests.
2. Devices and Control, with the two-device tests against a stand-in host.
3. iPhone part and Inbox, with the tests against a stand-in iPhone.
4. Screens, with pictures for the owner.
5. Relay service, and the specification of the Android helper app.
6. Recorder parts against simulated drivers, then the real board description.

## 7. Open points for the owner

- Where the software is compiled and tested: the owner's Linux server, or another Linux machine.
- Mac notifications: no supported way was found. Version 1 leaves them out unless the owner knows a route.
- The Android helper app is a second product to build and to publish.
