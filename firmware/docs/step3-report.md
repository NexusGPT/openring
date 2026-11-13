# Ring software step 3 (iPhone notifications, media, time): report to the owner

Date: 2026-11-12. Code: commit f6678d5. Proof: the lead's own run of the whole build and test on the server, 09:49 to 10:13, last line `RESULT PASS`, 15 stages with exit 0 (`firmware/build-logs/step3/20261112-094919-lead-step3-r3-rerun2.log`).

## What exists

- The ring is the Bluetooth client of an iPhone for Apple's notification, media and time services.
- A store of the last 16 notifications: app, title, message, flags, date.
- Two actions per notification: the positive one and the negative one (dismiss).
- The track title, the artist and the player state, and six media commands.
- A clock that takes the iPhone's time and time zone and holds universal time.

## What is proven, in simulation on the ring's chip model with real encryption

A stand-in iPhone written for this project serves Apple's three services.

- Notifications arrive and are stored exactly; a long message is cut at a character, never inside one (80 checks).
- A change replaces the text, a removal deletes the entry, the 17th drops the oldest.
- A dismiss chosen on the ring arrives at the stand-in; an action the notification does not offer is never sent, and the stand-in itself confirms that.
- After a dropped link the store is empty, then rebuilt from what the stand-in sends again (33 checks).
- The notification service removed and added again while linked: the ring stops, then subscribes again.
- A late answer that lands inside a later request does not shift the later texts (17 checks, 130 stray bytes skipped).
- A link that drops during set-up: the next link finds all three services (19 checks).
- The clock follows the stand-in to within 100 ms, follows a zone change (13 checks), and keeps the local time with a "zone not known" mark when the stand-in gives no zone (13 checks).
- With a device that has no Apple service, nothing fails and the keys of step 2 still work (19 checks).
- Notifications, media reports and time changes never start or stop a recording.
- 23 deliberately broken copies over Bluetooth and 10 broken logic runs of this step each give their required result (fail on their own named check).
- The product build is proven to use the same link settings as the tests.
- Step 1 and step 2 tests all still pass.
- The real build for the development kit compiles: 186,232 bytes of flash (19.1 percent), 51,264 bytes of RAM (9.8 percent).

## Deviations from the brief and the specification

- Nordic's ready notification part keeps only 32 bytes per text. The step wrote its own reader for the answers, to keep 48, 48 and 160 bytes.
- The ring now also reads from the iPhone on the same link (it was "sender only" in the specification's wording). The specification says so since section 7.6.

## Not built, not proven

- Nothing ran against a real iPhone. The stand-in shares one reading of Apple's documents with the ring.
- Several data formats rest only on Nordic's kit code, and the time zone format on no saved document. They are listed in `firmware/docs/step3-round2.md` section 8.
- No screen shows the notifications yet, and no control calls dismiss or the media commands. That is step 4.
- The clock is lost at a restart; the saved time of the specification is not built.
- The memory margin of one work stack on the real chip is not measured.
- One rare case is not fixed: a notification with the id 0 right after a late answer costs one retry.
- Round 3's changes were rerun by the lead and not read by a third independent reviewer.

## Usage

- One builder (Sonnet) over three passes: the first build and two correction rounds.
- Two independent reviews (Opus).
- Four full runs by the lead on the server, about 25 minutes each; one of them gave no result (its log disappeared from the server; cause not established).
- Clock: started 2026-11-11 23:06, finished 2026-11-12 10:13, with a stop of about six hours on the account's usage limit.
- Token figures are not visible to the lead.
