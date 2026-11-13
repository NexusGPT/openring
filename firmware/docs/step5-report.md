# Ring software step 5 (the relay for Android notifications): report to the owner

Date: 2026-11-13. Code: commit 4faca0a. Proof: the lead's own run of the whole build and test on the server, 02:04 to 03:35, last line `RESULT PASS`, 27 stages with exit 0 (`firmware/build-logs/step5/20261113-020446-lead-step5-r3-rerun.log`).

## What exists

- A small Bluetooth service on the ring, the relay. A helper app on an Android phone writes notifications to it; the ring answers and sends back the action the wearer chooses.
- The notifications land in the same store and on the same screens as the iPhone's. The screens do not know where a notification comes from.
- One link has one source. A link that uses Apple's notification service refuses the relay, and a link that uses the relay never uses Apple's service. The first user of a link decides.
- The written specification for the helper app: `design/software/os/android-helper-spec.md`, with a worked example in bytes (`android-helper-example.py`). The ring's tests send those same bytes.
- The rules of the relay are section 7.7 of `design/firmware.md` (its check gives 0 failures).

## What is proven, in simulation

- A stand-in helper app talks to a ring with its screens over the real Bluetooth software with encryption. Four scenarios pass: the full protocol (156 checks), an iPhone link that refuses the relay (39), a relay that arrives before Apple's service is found (37), a full answer queue (33).
- The worked example of the specification is sent byte for byte. A notification sent in six pieces is stored and checked field by field on the ring, then removed.
- The relay's logic passes 23 test cases on two simulated targets. All suites of steps 1 to 5 together: 346 of 346 cases on both targets.
- 32 deliberately broken copies of the relay (19 in the two-device test, 13 in the logic tests) each fail on their own named check. The broken copies of steps 1 to 4 still fail as required (91 broken copies in the whole run).
- The earlier steps' Bluetooth tests (control, iPhone, screens) pass with the relay built in.
- The relay calls nothing in the ring's core, so it cannot start or stop a recording: a search of its sources for the core's names finds nothing, and a planted copy is found by the same search. Relay messages do not wake the screen (checked in the two-device test).
- The test-only switches are off in both product builds. The check that proves it refuses a planted product settings file with the switches on.
- The real build for the development kit compiles: 522,212 bytes of flash (53.58 percent), 183,080 bytes of RAM (34.99 percent). Step 4 was 518,984 and 182,184.

## Decisions I took for you (you can change each one)

- A category number the ring does not know is stored as received, not refused.
- A new start of the helper (HELLO) empties the ring's notification store and drops answers still waiting.
- An action that cannot be sent to the helper (the helper is not listening, or the answer queue is full) is refused on the ring. The notification stays until the helper removes it.
- One protocol message is one Bluetooth write. A long write is refused.
- The date of a notification is stored as text and never read by the ring.

## Deviations from the specification

- None from section 7.7 as it stands. The points on which 7.7 was silent were ruled during the build and written into 7.7 and into the helper specification.

## Not built, not proven

- The helper app on the Android phone is not built. Nothing ran against a real Android phone, a real iPhone or hardware. The stand-ins are written for this project and can share a wrong reading with the ring.
- The wearer gets no sign on the screen when an action is refused. The screens part does not show it yet.
- Media and time from an Android phone are not built (the specification leaves them out).
- Three faults of the first review (numbers 10 to 12) are fixed in the code with no test that can reach them. A failed send in the middle of a link end has no test.
- A relay on a link that is not the active device's link has no test.
- Stack use on the real chip is not measured.
- Round 3's changes were rerun by the lead and not read by a third independent reviewer.

## Usage

- One builder (Sonnet) over three passes: the first build and two correction rounds.
- One writer of the helper specification (Sonnet).
- Two independent reviews (Opus). The first found 0 major and 8 minor faults with 6 notes; the second closed 11 of 14 and found 0 major and 2 minor faults with 6 notes. Round 3 closed the 2 minor ones.
- Three full runs by the lead on the server, all passed: 27 stages each. The last one took 90 minutes because the server carries other work.
- Clock: started 2026-11-12 19:15, finished 2026-11-13 03:35.
- Token figures are not visible to the lead.
