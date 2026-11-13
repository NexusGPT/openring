# Android helper app for the OpenRing ring: specification

Version: written against commit 1aae4da of the project. Licence: CC BY 4.0.
Status: a specification. The app is not built. Nothing here ran on a phone.

## 1. Purpose and scope

Android has no standard Bluetooth service for notifications (`design/software/os/research-platforms.md` section 4, "not found"). The ring therefore has a small service of its own, the relay service. This document tells a developer how to build the app that:

- reads the phone's notifications, with the user's permission;
- sends them to the relay service of the ring;
- carries a dismiss chosen on the ring back to the phone.

Out of scope: control of the phone (keys and media go through the ring's standard keyboard role, not through this app), media and time from the phone, recordings.

Words: "ring" is the device, "helper" is this app, "frame" is one write to In or one notification on Out, "record" is the bytes of one notification.

## 2. The ring's side: a fixed contract

The contract is section 7.7 of `design/firmware.md` (relay service, F7 part 5). This section repeats its tables and rules with no change. The helper must not change them. If the two texts differ, section 7.7 wins and this document has a fault. All numbers are little endian. Every characteristic needs an encrypted, authenticated link (security level 4).

Relay service, UUID `a3c20000-5b7e-4f2a-9c1d-7e2b6f4d8a90` (the ring is the GATT server).

| Characteristic | UUID | Properties | Use |
|---|---|---|---|
| In | `a3c20001-5b7e-4f2a-9c1d-7e2b6f4d8a90` | write with response | frames from the helper to the ring |
| Out | `a3c20002-5b7e-4f2a-9c1d-7e2b6f4d8a90` | notify | frames from the ring to the helper |
| Info | `a3c20003-5b7e-4f2a-9c1d-7e2b6f4d8a90` | read | 6 bytes: protocol version u8 (1), store size u8 (16), application identifier limit u8 (48), title limit u8 (48), message limit u8 (160), date length u8 (15) |

Frames written to In (the first byte is the opcode):

| Opcode | Name | Bytes after the opcode | Meaning |
|---|---|---|---|
| 0x01 | HELLO | version u8 | the helper starts a session. The ring empties what the relay stored and answers READY on Out |
| 0x02 | PUT | id u32, total u16, offset u16, then data bytes | one piece of the record of notification `id`. `total` is the length of the whole record, `offset` the place of this piece. Pieces arrive in order, the first with offset 0; a piece with offset 0 drops an unfinished record and begins a new one. The record is stored when offset plus the data length equals `total` |
| 0x03 | REMOVE | id u32 | the phone removed the notification |
| 0x04 | CLEAR | none | the phone has no notification left: the ring empties what the relay stored |

The record of a PUT: category u8 (the values of section 7.6, 0 to 11; the ring does not read the category, and a value above 11 is stored as received, never refused), flags u8 (the bits of section 7.6: silent 0, important 1, pre-existing 2, has a positive action 3, has a negative action 4; the other bits must be 0), then fields, each as type u8, length u8, bytes: type 1 application identifier, 2 title, 3 message, 4 date (`yyyyMMdd'T'HHmmSS`). Each type at most once, in any order; a missing field is empty. A record is at least 2 and at most 512 bytes. A text longer than its limit is cut at a character, as in section 7.6. A PUT for an id that is stored replaces that notification and keeps its place and its read mark; a new id goes to the front, and the 17th pushes the oldest out.

Category values (section 7.6 points to Apple's CategoryID list, `design/software/os/research-platforms.md` section 1, [F]): 0 Other, 1 IncomingCall, 2 MissedCall, 3 Voicemail, 4 Social, 5 Schedule, 6 Email, 7 News, 8 HealthAndFitness, 9 BusinessAndFinance, 10 Location, 11 Entertainment.

Frames notified on Out:

| Opcode | Name | Bytes after the opcode | When |
|---|---|---|---|
| 0x81 | READY | version u8 (1), store size u8 (16) | after HELLO |
| 0x82 | ACTION | id u32, action u8 (0 positive, 1 negative) | the wearer chose an action on the ring |
| 0x83 | ERROR | code u8, id u32 (0 when none) | a frame was refused |

Rules of the ring (section 7.7, same words in short):

- **Refusals.** A refused frame changes nothing in the store. The write is answered with ATT error 0x80 and, when the helper has subscribed to Out, ERROR is notified. Codes: 1 unknown opcode or wrong frame length; 2 no HELLO in this session; 3 PUT piece out of order or beyond `total`; 4 `total` under 2 or over 512; 5 record malformed (a field runs past the end, a type is unknown or repeated, a flag bit above 4 is set); 6 version not supported; 7 the link's notifications come from Apple's service.
- **Sessions.** The relay's notifications live for one link. When the link ends they are emptied. The helper sends HELLO and its notifications again after it reconnects, those that were already there with the pre-existing flag. A PUT that is not finished when the link ends is dropped.
- **One source per link.** The first of the two that is used on a link fixes the source of that link until the link ends. Apple's notification service found first: every relay frame on that link is refused with code 7. A relay HELLO accepted first: the ring does not use Apple's notification service on that link, and relay frames stay accepted.
- **Out and the size of a write (added 2026-11-12 after the review of the ring's code).** An accepted HELLO drops every frame that still waits for Out from before it, so READY always has room. An action whose ACTION frame cannot be queued is refused on the ring; the app then sees no ACTION. A frame is one write: a write longer than the link's payload (a prepared or long write) is refused with the ATT error for an invalid offset (0x07), not with 0x80. The date is stored like every text (up to 15 bytes, cut at a character).
- **Actions.** A dismiss chosen on the ring is the negative action. The ring notifies ACTION and changes nothing in the store; the entry leaves when the helper sends REMOVE. An action that the notification does not have (its flag is not set) is refused on the ring and sends nothing. With no subscription to Out the action is refused on the ring.
- **Read mark.** The read mark lives on the ring only.
- **Not built on the ring in step 5:** media and time from an Android phone.

Limits the helper must obey (from the Info row and the store rules, `firmware/modules/ring_inbox/include/ring_inbox/rinbox.h`): store 16 entries; application identifier at most 48 bytes, title 48, message 160, date 15 characters; strings UTF-8, cut at a character boundary. With every text cut to its limit the largest record is 2 + (2+48) + (2+48) + (2+160) + (2+15) = 281 bytes, under the 512 of the contract.

## 3. What Android demands

Only facts saved in `design/software/os/research-platforms.md` sections 4 and 5 are used. Tags there: [F] a page was read, [S] search text only. Where that file has nothing, the cell says so.

| Need | What the project's research holds | Source and tag |
|---|---|---|
| Read notifications | NotificationListenerService "receives calls from the system when new notifications are posted or removed, or their ranking changed" | developer.android.com NotificationListenerService, [F] |
| Declare the listener | the service is declared in the manifest with the BIND_NOTIFICATION_LISTENER_SERVICE permission | same page, [F] |
| Wait for connection | "The service should wait for the onListenerConnected() event before performing any operations." | same page, [F] |
| How the user grants access | the research holds only: "access to notifications can be turned off by users in the Notification Access settings in the Settings app." That page is the Automotive policy page and not a general Android rule. How a third-party app sends the user there: not in the project's research: to verify against Android's documentation | source.android.com automotive notification-access, [F] with the caveat |
| Companion device | "Your app must have an association with a device before calling this API." and "Side-loaded apps must allow restricted settings before requesting notification access." | CompanionDeviceManager page, [F] |
| Companion presence | callbacks when the associated device's presence changes (BLE range in or out, Bluetooth connected or disconnected); needs a CompanionDeviceService; marked "Added in API level 36" | same page, [F] |
| Background with a connected device | "There is no restriction on connecting to a device while the app is in the background, although the connection is closed if your process is killed." Advice: "Start a foreground service with the connectedDevice type." Foreground service launch restrictions apply starting in Android 12 | developer.android.com BLE background page, [F] |
| Low-memory devices | "Notification listeners cannot get notification access or be bound by the system on low-RAM devices running Android Q (and below)." | NotificationListenerService page, [F] |
| Work profile | "The system also ignores notification listeners running in a work profile." | same page, [F] |
| Store policy | the Play page read ("Permissions and APIs that Access Sensitive Information") names restricted permissions with extra requirements but does not name the notification listener. Other Play policy pages were not opened. Whether the app can be published: not in the project's research: to verify against Google Play's policy pages | support.google.com answer 16559646, [F] |
| Which Android versions the app supports | not in the project's research: to verify against Android's documentation | none |
| Bluetooth permissions at run time, bonding calls, GATT calls, passkey entry | not in the project's research: to verify against Android's documentation | none |

HOGP and HID (research section 5) concern control, which this app does not do.

## 4. Worked example in bytes

The script `design/software/os/android-helper-example.py` (Python standard library only) builds every byte below from the tables of section 2. Run `python3 design/software/os/android-helper-example.py`. The output shown here is that output, copied. The script and this section must agree; a reader can run it and compare.

A write value is the bytes of one write to In. At an ATT payload of 20 the write value is at most 20 bytes (ATT MTU 23 minus 3 bytes of ATT header). At 244 it is at most 244 bytes (ATT MTU 247, the ring's MTU, minus 3). The ring does not publish a write size; this is the helper's choice and the ring accepts any piece size (Question 2).

The notification: id 0x000100a5, category Social (4), flags important plus has a negative action (0x02 + 0x10 = 0x12), application identifier `com.example.chat`, title `Anna`, message `Lunch at 12? ` followed by the noodle emoji (4 UTF-8 bytes, to show a multi-byte character), date `20261112T191500`.

Session start (Info read, HELLO, READY):

```
Info (read, 6 bytes): 01 10 30 30 a0 0f
HELLO  : 01 01
READY  : 81 01 10
```

- Info: 01 version 1; 10 store size 16; 30 application identifier limit 48; 30 title limit 48; a0 message limit 160; 0f date length 15.
- HELLO: 01 opcode; 01 version 1.
- READY (from the ring, on Out): 81 opcode; 01 version 1; 10 store size 16.

The record (62 bytes):

```
id = 0x000100a5, little endian: a5 00 01 00
record, 62 bytes:
  category 04, flags 12
  type 01 (application identifier), length 10 (16), bytes 63 6f 6d 2e 65 78 61 6d 70 6c 65 2e 63 68 61 74  = 'com.example.chat'
  type 02 (title), length 04 (4), bytes 41 6e 6e 61  = 'Anna'
  type 03 (message), length 11 (17), bytes 4c 75 6e 63 68 20 61 74 20 31 32 3f 20 f0 9f 8d 9c  = 'Lunch at 12? 🍜'
  type 04 (date), length 0f (15), bytes 32 30 32 36 31 31 31 32 54 31 39 31 35 30 30  = '20261112T191500'
  whole record: 04 12 01 10 63 6f 6d 2e 65 78 61 6d 70 6c 65 2e 63 68 61 74 02 04 41 6e 6e 61 03 11 4c 75 6e 63 68 20 61 74 20 31 32 3f 20 f0 9f 8d 9c 04 0f 32 30 32 36 31 31 31 32 54 31 39 31 35 30 30
```

- 04: category 4. 12: flags, binary 00010010, bit 1 and bit 4.
- Each field is type, length, bytes. Lengths are in bytes, not characters: the message is 13 characters and 17 bytes (f0 9f 8d 9c is one character).
- 62 = 2 + 18 + 6 + 19 + 17.

PUT at a write value of 20 bytes. Header of every frame: 02 opcode; a5 00 01 00 id; 3e 00 total (0x3e = 62); two bytes offset; then data. 11 data bytes fit in 20. The emoji is split between frames 4 and 5; this is allowed, the ring joins the pieces before it reads the record.

```
PUT at a write value of 20 bytes: 6 frame(s)
  frame 1 (20 bytes): 02 | a5 00 01 00 | 3e 00 | 00 00 | data 11 bytes at offset 0
    02 a5 00 01 00 3e 00 00 00 04 12 01 10 63 6f 6d 2e 65 78 61
  frame 2 (20 bytes): 02 | a5 00 01 00 | 3e 00 | 0b 00 | data 11 bytes at offset 11
    02 a5 00 01 00 3e 00 0b 00 6d 70 6c 65 2e 63 68 61 74 02 04
  frame 3 (20 bytes): 02 | a5 00 01 00 | 3e 00 | 16 00 | data 11 bytes at offset 22
    02 a5 00 01 00 3e 00 16 00 41 6e 6e 61 03 11 4c 75 6e 63 68
  frame 4 (20 bytes): 02 | a5 00 01 00 | 3e 00 | 21 00 | data 11 bytes at offset 33
    02 a5 00 01 00 3e 00 21 00 20 61 74 20 31 32 3f 20 f0 9f 8d
  frame 5 (20 bytes): 02 | a5 00 01 00 | 3e 00 | 2c 00 | data 11 bytes at offset 44
    02 a5 00 01 00 3e 00 2c 00 9c 04 0f 32 30 32 36 31 31 31 32
  frame 6 (16 bytes): 02 | a5 00 01 00 | 3e 00 | 37 00 | data 7 bytes at offset 55
    02 a5 00 01 00 3e 00 37 00 54 31 39 31 35 30 30
```

- Offsets 0x00, 0x0b (11), 0x16 (22), 0x21 (33), 0x2c (44), 0x37 (55). The last piece ends at 55 + 7 = 62 = total, so the ring stores the record at frame 6.

PUT at a write value of 244 bytes: one frame of 9 header bytes and 62 data bytes (71 bytes).

```
PUT at a write value of 244 bytes: 1 frame(s)
  frame 1 (71 bytes): 02 | a5 00 01 00 | 3e 00 | 00 00 | data 62 bytes at offset 0
    02 a5 00 01 00 3e 00 00 00 04 12 01 10 63 6f 6d 2e 65 78 61 6d 70 6c 65 2e 63 68 61 74 02 04 41 6e 6e 61 03 11 4c 75 6e 63 68 20 61 74 20 31 32 3f 20 f0 9f 8d 9c 04 0f 32 30 32 36 31 31 31 32 54 31 39 31 35 30 30
```

The other frames:

```
REMOVE : 03 a5 00 01 00
CLEAR  : 04
ACTION negative (ring to helper): 82 a5 00 01 00 01
ACTION positive (ring to helper): 82 a5 00 01 00 00
ERROR code 2 (no HELLO), no id   : 83 02 00 00 00 00
```

- REMOVE: 03 opcode; a5 00 01 00 id.
- ACTION for a dismiss on the ring (on Out): 82 opcode; a5 00 01 00 id; 01 action negative. The helper then dismisses the notification on the phone and, when the phone reports it removed, sends REMOVE.
- ACTION positive differs only in the last byte: 00.
- ERROR: 83 opcode; 02 code; 00 00 00 00 id 0 (none).

## 5. Requirements for the app

Each requirement is testable. "Test" says how. Items marked (V) rest on an Android fact that is not in the project's research: verify against Android's documentation before building.

### 5.1 Pairing, bonding, finding the service

- R1. The app has a "pair the ring" screen. It tells the user to open the pairing screen on the ring first (the ring accepts pairing only for 60 s, section 7.4). Test: with the ring's pairing window closed, the app shows the instruction and no passkey prompt.
- R2. The app scans and offers only devices whose scan response has the local name starting "Ring" or the ring service UUID `a3c10000-5b7e-4f2a-9c1d-7e2b6f4d8a90` (section 7.3). Test: a fake advertiser with another name is not offered. (V) scanning and its permissions.
- R3. The app pairs with LE Secure Connections. The ring shows a six-digit passkey (display only); the app gives the user a field to type it. The result must be an authenticated, encrypted bond (security level 4). Test: the bond exists after pairing; a wrong passkey ends with "pairing failed" and no bond. (V) the Android calls and the passkey entry.
- R4. The app associates the ring as a companion device before it asks for notification access (research: association is required before the API). Test: the notification-access request is not started before the association exists.
- R5. After the link is up, the app discovers the services and looks for the relay service UUID of section 2. If it is not found, the app says "this ring has no relay service" and stops. Test: a fake server without the service gives this message and no HELLO.
- R6. The app reads Info and checks that the version is 1. A different version: stop, show "update the app or the ring", send nothing. The app uses the limits in Info, not fixed numbers. Test: fake Info with version 2 sends nothing; fake Info with title limit 20 makes the app cut the title at 20 bytes.
- R7. Only the active device of the ring can connect (section 7.4 and 7.3). If the link is refused or dropped at once, the app shows "make this phone the active device on the ring (Devices screen)". Test: message shown after 3 refused connections in 60 s (the numbers are this spec's choice).

### 5.2 The session

- R8. The app enables notifications on Out before it sends HELLO, so READY and ERROR reach it. Test: in a trace, the Out subscription write comes before the HELLO write.
- R9. The app sends HELLO with version 1 and waits for READY for 5 s (this spec's choice). No READY: disconnect, count one failure, reconnect as in R25. Test: fake ring that never answers. The app ignores every Out frame that arrives after its HELLO write and before READY (the ring may still deliver one frame it was sending when HELLO arrived; section 7.7, Details). Test: fake ring that sends ERROR code 2 between HELLO and READY; the app does not send HELLO again.
- R10. After READY the app sends the notifications already on the phone, with the pre-existing flag (bit 2) set. The ring puts a new id in front, so the app sends the oldest first and at most the newest 16 (the store size from READY). Test: with 20 active notifications, 16 PUTs go out, the newest last, each with flag bit 2.
- R11. After that, each notification posted is sent as a PUT without the pre-existing flag. A notification that is updated keeps its id and goes again as a PUT. Test: post, update, post: the first and the second PUT carry the same id.
- R12. When the phone removes a notification (the user, the app, or a timeout), the app sends REMOVE with its id and forgets the id. If the app sent the notification, no other REMOVE is sent for it. Test: removal of a never-sent (skipped) notification sends nothing.
- R13. When the phone has no notification left to show, the app sends CLEAR. Test: after the last removal, a single CLEAR follows.
- R14. Frames go out one at a time. The app waits for the answer of one write before the next, and sends the pieces of one record in order, without another record between them. Test: two notifications posted together never interleave their pieces. (V) the Android rule on one GATT operation at a time.
- R15. The app picks the piece size from the ATT payload it negotiated: write value size minus 9 for the data. If it cannot tell the MTU it uses 20. Test: section 4 byte for byte at 20 and at 244.
- R16. The app does not read or write anything of the ring service `a3c10000-...` (status, time, files): not in this step.

### 5.3 From an Android notification to the record

Notifications are delivered by the notification listener service (research: NotificationListenerService [F]; the app waits for onListenerConnected before it does anything). The class fields named below are this spec's proposals. Each one: not in the project's research: to verify against Android's documentation.

| Record part | Proposed Android source (V) | Rule |
|---|---|---|
| id u32 | the notification's key string, mapped by the app | see R17 |
| category u8 | the notification's category string | table below; any other or missing: 0 |
| flag silent (bit 0) | the notification makes no sound and no vibration, taken from its importance or ranking | set when silent |
| flag important (bit 1) | its importance is high or more | set when important |
| flag pre-existing (bit 2) | not from Android: set by the app for notifications sent after READY at session start | R10 |
| flag positive (bit 3) | the notification has at least one action button | see R21 |
| flag negative (bit 4) | the app can dismiss the notification | set unless it cannot be dismissed |
| application identifier (type 1) | the package name of the app that posted it | at most Info limit, UTF-8 |
| title (type 2) | the title text in the notification's extras | empty if none |
| message (type 3) | the main text in the extras (the long text if present, else the text) | empty if none |
| date (type 4) | the time the notification was posted, a millisecond count | R19 |

Proposed category map (the ring only stores the number; this map is the spec's choice, undecided):

| Android category | Ring category |
|---|---|
| call | 1 IncomingCall |
| missed call | 2 MissedCall |
| message, social | 4 Social |
| event, reminder, alarm | 5 Schedule |
| email | 6 Email |
| workout | 8 HealthAndFitness |
| location sharing, navigation | 10 Location |
| everything else | 0 Other |

- R17. Stable id. The app keeps a table from the notification's key to a u32 id. A new key gets the next number of a counter that starts at 1, never gives 0 (0 means "none" in ERROR) and never gives an id that is in the table. The same key always gets the same id while the table holds it. The table is kept while the app's process lives and is emptied at the end of a session with HELLO (the ring forgets all at HELLO too). An id leaves the table after REMOVE. Test: 100 000 posts and removals never give 0 or a duplicate among live ids; an update keeps its id.
- R18. Skipped, never sent, never counted as removed: ongoing notifications; group summaries; notifications of the app's own package. Test: one of each is posted and no PUT goes out. The three skip tests (flag names, V): the ongoing flag, the group-summary flag, the package name.
- R19. Date. The app writes the posting time as 15 characters `yyyyMMdd'T'HHmmSS` in the phone's local time, with SS the two digits of the seconds (section 7.6 gives the pattern; Question 1). Test: the example of section 4 from a known time.
- R20. Texts. The app cuts each text to its Info limit in bytes, at a character boundary, never inside a UTF-8 character. A record over 281 bytes is a bug. Test: a message of 200 bytes of 3-byte characters is cut to 159 bytes (53 characters), not 160.
- R21. Positive action. The flag (bit 3) is set when the notification has at least one action button. What the positive action does with several buttons is not decided (section 7). Until decided: the first button in the notification's action list.
- R22. A notification with no title and no message is still sent, with empty fields, when it is not skipped.

### 5.4 Actions from the ring

- R23. ACTION negative (action byte 1) for an id the app knows: dismiss that notification on the phone through the listener service. When the phone then reports it removed, send REMOVE (R12). The app does not send REMOVE before the phone reports it. Test: ACTION negative, then a removal report, then one REMOVE. (V) the dismiss call.
- R24. ACTION positive (action byte 0) for a known id: run the action chosen by R21 (fire the button's intent). The app does not send REMOVE for it; the phone decides. If the notification has no action now, or the id is unknown, the app ignores the frame and logs it. Test: positive on an id with no button changes nothing. (V) how an action is run.
- An ACTION for an unknown id is ignored and logged, never answered.

### 5.5 ERROR codes

The app logs each ERROR with code, id and a counter. A refused frame changed nothing on the ring.

| Code | Meaning | The app does |
|---|---|---|
| 1 | unknown opcode or wrong length | abandon that record, go on. A bug of the app: show in the log. After 3 in one session, disconnect and show "protocol error" |
| 2 | no HELLO in this session | send HELLO, wait for READY, then send all notifications again as in R10 |
| 3 | piece out of order or beyond total | send that record again once from offset 0; a second code 3 for the same id: skip it |
| 4 | total under 2 or over 512 | skip that notification (R20 should prevent it) |
| 5 | record malformed | skip that notification; log the record bytes of the frame |
| 6 | version not supported | stop; show "update the app or the ring"; try again only after the app is updated or the ring's Info read changes |
| 7 | the link's notifications come from Apple's service | stop sending on this link; show "this phone is already served by Apple's service"; try again after the next connect |

- R25. Each row above is a test: a fake ring answers the matching ERROR and the app does exactly what the row says.

### 5.6 Dropped link and reconnect

- R26. When the link drops, the app drops the unfinished PUT, keeps its id table, and starts to reconnect. Waits between tries: 1 s, 2 s, 4 s, 8 s, up to 30 s, then every 30 s (this spec's choice). The wait returns to 1 s after a link that lasted 10 s. The app never stops trying while the bond exists and notification access is on. (V) how the connection is requested on Android, and whether the system reconnects by itself.
- R27. After each reconnect the app runs 5.1 from R5 and 5.2 again, in order: discover, Info, subscribe, HELLO, READY, the existing notifications with the pre-existing flag, live ones. The ring emptied its store with the link, so the app never assumes anything is still there. Test: drop the link after 3 PUTs; after reconnect HELLO and the same 3 notifications arrive with flag bit 2.
- R28. If the bond is gone (the ring removed this device, or the phone lost it), the app stops and shows "pair the ring again" and does not loop. Test: fake link that fails encryption: the app shows it after one try. (V) how Android reports a lost bond.
- R29. Process death. The research says the connection is closed if the process is killed. The app runs a foreground service of type connectedDevice while a ring is associated (research, section 3). Test: kill the process; on the next start the app begins a new session.
- R30. The app ends the foreground service and the link when the user removes the ring in the app.

### 5.7 Notification permission taken away

- R31. The app does not start the notification listener work before it is connected (research: wait for onListenerConnected).
- R32. If notification access is off at start, the app shows a screen "Allow notification access" with a button to the system settings page where the user grants it (research: the Notification Access settings in the Settings app; how to open it: V). It sends nothing to the ring. Test: with access off, no HELLO is sent after the ring link is up.
- R33. When the user takes access away while a session runs, the app sends CLEAR (the ring must not keep notifications the user no longer shares; this is the spec's reading of CLEAR, Question 4), stops reading, keeps the link, and shows the same screen as R32. When access comes back, the app starts a new session with HELLO and R10. Test: revoke, see one CLEAR and no PUT; grant, see HELLO and the pre-existing notifications. (V) how the app learns that access was taken away.
- R34. A work profile or a low-memory device on Android Q or below cannot give access (research, section 3). The app shows "this phone cannot give notification access to the app" when the system refuses it. (V) how the app can tell.
- R35. The app collects no notification text for itself: the texts go to the ring and nowhere else. It writes no notification text to its log, to a file, or to the network. Test: grep of the app's logs and files after a run with the example notification finds neither title nor message.

## 6. How the ring side is tested

The ring's relay service is tested on a simulated ring by `firmware/tests/bsim/relay/` (software step 5, being built now). It is a test of the ring against a stand-in helper, with no phone. A reader can use it to see what the ring does with each frame of section 2. It does not test this app. The app's own tests are the "Test" lines of section 5, run against a fake ring that answers as section 2 says; the fake ring is part of the app's work and does not exist yet.

The worked example of section 4 is a good first test of the app: its bytes must equal the script's output. The ring's own tests use the same bytes (logic case `test_helper_example_bytes` and scenario H of `firmware/tests/bsim/relay`, checked by the second review of software step 5).

## 7. Not decided, not proven

- The app does not exist. Nothing ran on a phone, on Android, or against a real ring.
- Which Android versions the app supports: not decided. The research gives only: no access on low-memory devices running Android Q and below; the companion presence API marked "Added in API level 36"; foreground service launch restrictions from Android 12.
- Battery cost of the app (foreground service, Bluetooth link, listener): not measured.
- What the positive action maps to when a notification has several buttons: not decided. R21 is a placeholder.
- The category map of section 5.3, the retry times, the 5 s READY wait, the 3-failure rules: the spec's choices, not tested.
- Every Android class, field and call named in section 5.3 and marked (V): not verified.
- Media and time from an Android phone are not part of the relay. The ring's Media screen shows a track only with an iPhone (section 7.7).
- Google Play: whether an app with notification access can be published is not found in the project's research.
- Behaviour with a notification that has an image, a progress bar, or a reply field: only title and message are sent; not decided beyond that.

## 8. Questions for the lead, with the answers

These concern `design/firmware.md` section 7.7. The answers were added by the lead on 2026-11-12 and are now part of section 7.7.

1. The date pattern is written `yyyyMMdd'T'HHmmSS`, the pattern of Apple's service copied into 7.6 and 7.7. In common date-pattern notation capital SS means fractions of a second, but the field is 15 characters, so 6 digits `HHmmss` is the only fit. Is the time local or UTC? 7.7 does not say; R19 assumes local, as Apple's. Please confirm.
   - Answer of the lead: local time of the phone; the last two digits are the seconds; the ring stores the 15 characters and does not read them (now in 7.7).
2. 7.7 gives no write size for In. The helper chooses its piece size (section 4). Does the ring accept any piece from 1 data byte up to MTU minus 12? And is a write of 1 byte (opcode only, for CLEAR) the smallest?
   - Answer of the lead: yes. A PUT carries at least 1 data byte and as many as the link allows; CLEAR is one byte (now in 7.7).
3. The advertising (section 7.3) carries the HID UUID and, in the scan response, the ring service UUID `a3c10000-...` but not the relay UUID `a3c20000-...`. R2 finds the ring by the ring service UUID or the name, then finds the relay by discovery. Is that intended?
   - Answer of the lead: yes, the advertising is unchanged in step 5.
4. CLEAR is defined as "the phone has no notification left". R33 uses it also when the user takes the permission away. Is that acceptable, or should the helper end the session by disconnecting?
   - Answer of the lead: acceptable. CLEAR may be sent at any time in a session (now in 7.7).
5. 7.7 says ERROR is notified "when the helper has subscribed to Out" and READY is also on Out. A helper that sends HELLO before subscribing gets the write accepted but never sees READY. Does HELLO without a subscription count as a session? R8 avoids the case; the ring behaviour is not stated.
   - Answer of the lead: HELLO starts a session also without a subscription; READY is then not delivered. R8 is the rule for the helper (now in 7.7).
6. Pre-existing notifications: 7.7 says the helper sends them with the pre-existing flag. The ring keeps the newest first; R10 derives "send oldest first". Please confirm the ring does not sort by date.
   - Answer of the lead: confirmed. The order is the order of arrival, newest first (now in 7.7).
7. A positive ACTION: 7.7 allows it when flag bit 3 is set, but 7.6 and the ring's screens only mention dismiss. Is a positive action reachable on the ring in step 5?
   - Answer of the lead: yes. Right on the notification screen sends the positive action when the notification has one (`design/firmware.md` section 2.2).

RESULT: done, the specification and its byte-example script are written; every Android detail outside the project's research is marked "to verify" and nothing ran on a phone.
