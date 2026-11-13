# Ring software step 2 (paired devices, keyboard and media control): report to the owner

Date: 2026-11-11, 23:05. Code: commit 221746b. Proof: the lead's own run of the whole build and test on the server, 22:52 to 23:02, last line `RESULT PASS` (`firmware/build-logs/step2/20261111-225221-lead-step2-r3-rerun.log`).

## What exists

- The ring pairs with a six-digit passkey, keeps up to three paired devices and switches the active one.
- The ring acts as a Bluetooth keyboard, media remote and pointer for the active device.
- Four control modes: media, presenter, pointer, agent.
- A long press on the joystick's centre still starts and stops a recording in every mode. No device can start or stop a recording.

## What is proven, in simulation on the ring's chip model with real encryption

- A stand-in computer pairs with the ring and receives the right key for each joystick action in each mode (76 checks).
- After a switch, the second stand-in receives the keys and the first receives none (44 checks).
- Three stand-ins pair in turn, each receives only its own keys, and a fourth pairing is refused (56 checks).
- Removing a paired device deletes its keys; the old device no longer works (28 checks).
- A long press sends no key and still records; a write from a computer starts nothing (31 checks).
- An unpaired device outside the pairing window gets no pairing and no key; the ring drops it after 102 ms (23 checks).
- Ten deliberately broken copies each fail on their own named check. Two copies that remove one of the two pairing protections still pass, so each protection holds alone.
- The real build for the development kit compiles: 168,592 bytes of flash (17.3 percent), 36,924 bytes of RAM (7.1 percent).

## Deviation from the approved plan

- The plan lists three control modes. The software has four: the helper added "agent" (Return to accept, Escape to decline, up and down arrows; keys only, no text) from the owner's words "You can even control claude code with it". The owner keeps it or drops it.

## Not built, not proven

- Nothing ran on a real iPhone, Android phone or Mac.
- Real phones change their Bluetooth address every few minutes. The ring's check of "is this my paired device" is proven only with fixed addresses.
- Paired devices surviving a restart of the ring, and the 60 s end of the pairing window, are not tested.
- The joystick driver and the screens (passkey, device picker, mode choice) come in later steps. Until the screens exist, the product build sends no key by itself.
- Two devices linked at the same time held in one trial; it is not part of the product.
- Round 3's changes were rerun by the lead and not read by a third independent reviewer.

## Usage

- One builder (Sonnet) over four passes: the first build and three correction rounds.
- Two independent reviews (Opus), one experiment on a pairing failure (cause: a simulator setting, not our code).
- Three full reruns by the lead on the server, 8 to 10 minutes each.
- Clock: started 12:52, finished 23:02, with the film work in between.
- Token figures are not visible to the lead.
