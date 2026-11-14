# Ring software step 7 (the real ring's board description): report to the owner

Date: 2026-11-14. Code: commit 92b8c6ac. Proof: the lead's own run of the whole build and test on the server, 09:09 to 11:13, last line `RESULT PASS`, 53 stages with exit 0 (`firmware/build-logs/step7/20261114-090925-lead-full8.log`). The fourth independent review passed this version (`firmware/docs/step7-review-4.md`).

## What exists

- The board description of the real ring for the ring software: every chip pin, the power chip's settings, the memory layout (`firmware/boards/ringrec`).
- The software now builds for the real ring's board, with the real drivers of every part: microphones, card storage, USB, power and charging, motor, watchdog and crash record, update.
- A second build of the same software without the debug port, as the specification asks for rings that ship.
- A pin check that compares the board description with the circuit's connection list, and a rule in the build tool that refuses to run when the software's copy of that list differs from the design's.

## What is proven, by building and by checks that can fail

- The ring build compiles: 643,288 bytes of program memory (65.45 percent), 471,904 bytes of RAM (90.36 percent). The build without the debug port: 642,456 and 471,888.
- All 36 chip pins equal the circuit's connection list. The first reviewer read them itself. Ten deliberately wrong copies each fail on their own pin: a wrong pin, a wrong port, a removed part, a switched-off part, an extra pin, a wrong pin setting, an unknown line, a changed line of the connection list.
- The 21 power chip settings and the memory layout equal the specification (first review).
- The build without the debug port is checked: five deliberately wrong copies are refused.
- Nothing of steps 1 to 6 broke: 732 of 732 test cases pass on each simulated target, and the 43 earlier stages pass.
- Four independent reviews. Major faults open after each: 2, 1, 1, 0.

## What the reviews found, and what changed because of them

- The memory card's lines must never be driven while the card's supply is off. Three reviews found three paths that broke this rule: going to sleep, start-up, a failed first start of the card. After the third I stopped patching paths: one function now makes the four lines safe with no condition, and it runs on every way to "supply off". A check in the build proves that shape.
- The power part's real file did not compile with this software kit. My step 6 report said the real files compile for the development kit; for the power part that was wrong, because the kit has no power chip and the file was never compiled. It is fixed and compiles for the ring.
- The battery current went to the charge estimate with the wrong sign. It now has the sign that Nordic's own example uses.
- The software's copy of the connection list could drift from the design's with nothing failing. The build tool now refuses.

## Decisions I took for you (you can change each one)

- Settings are stored with the storage method the software kit recommends for this chip's memory type (ZMS).
- The bootloader area is 64 KB, as the specification says.
- The battery model is Nordic's 20 mAh sample. It is NOT the ring's cell; the files say so.
- The bootloader is signed with the software kit's test key. NOT FOR SHIPPING; the production key is made at the factory step.
- RAM: the build uses 471,904 bytes; the specification's budget says 305,408. It fits, with about 50,000 bytes free. I keep the software as it is. Two storage work buffers (66,560 bytes together) and the stand-in picture of the screen (57,600 bytes) can go when the screen's driver is written; the specification's budget table is corrected then.

## Not built, not proven

- Nothing has run on a ring or on any hardware. Step 7 proves that the software builds for the real board and that its pins and settings match the design, nothing more.
- Only a ring can show: the pins' state at power-on; that the "safe" setting leaves the card's lines without pull on this chip; the card's lines when the ring goes to shipping sleep while the card refuses to close; the charge estimate on a real cell.
- The screen's panel driver and the joystick's driver are not written.
- Two weaknesses the last review left, both minor: the new build check compares text, not behaviour (four hand-made wrong copies got past it; it catches the likely mistakes); and the pin check has blind spots, listed in `firmware/docs/board-notes.md`.
- The last version's changes were read by the fourth reviewer and rerun by the lead; no fifth reviewer read the reviewer's two minor points.

## Usage

- One builder (Opus) over four passes: the first build and three fix rounds.
- Four independent reviews (Opus).
- The lead's full runs on the server: three passed (48, 50 and 53 stages, about two hours each); one was stopped when the third review made its version obsolete. The builder ran three full runs and several short ones.
- The lead's own probes: the pin check with six planted faults; the build tool's refusal with three cases; a read of the software kit's source for one line the last review could not prove.
- The account's weekly usage limit was reached once during the night. The builder's turn and one turn of the lead stopped on it and resumed.
- Clock: started 2026-11-13 21:22, finished 2026-11-14 11:13.
- Token figures are not visible to the lead.

## What comes next in the software

- The approved plan's seven steps are done. Not in that plan, in this order when you say so: the screen's panel driver (needs the panel maker's answer), the joystick's driver, the Android helper app, the phone app's specification.
