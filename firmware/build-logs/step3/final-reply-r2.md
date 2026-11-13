Round 2 is done: `sh firmware/tools/remote.sh os-iphone-r2 "tools/build_all.sh"` ended `RESULT PASS`, `# remote exit code: 0`, and all 15 stages ended with exit 0. Log: `firmware/build-logs/step3/20261112-014123-os-iphone-r2.log`. Answers to points 1 to 8, with file:line and LOG:n: `firmware/docs/step3-round2.md`; the notes `firmware/docs/iphone-notes.md` are corrected and regenerated from this log. I ran no git.

1. Link settings: the false claim is corrected. One file, `modules/ring_iphone/ring_iphone_link.conf` (MTU 247, ACL 251/251, workqueue stack 3072), is added by the product and by the test ring. New stage `link-settings` compares the built dk and bsim product settings with the test ring's, after a self test that a changed MTU is refused. Cost: kit build FLASH 186,072 B, RAM 51,240 B (round 1: 184,932 and 45,196). Product stack margin on the chip: not measured (the simulation's host stacks say nothing).
2. Late fragment: the parser skips bytes that are not the answer to the request in flight; a failed request is asked once more. New scenario L (answer held 3,500 ms): 16 checks pass; copy `late_fragment` fails on its named check.
3. Bar c: the stand-in records every action command before refusing one and checks that none arrived for a notification without that action. Copy `action_sent` fails on that check.
4. Bar h: the check now also requires Service Changed found; its name says so.
5. Clock: Local Time Information is read next to Current Time; the clock holds UTC plus the zone offset, or local time with `rtime_zone_known()` false. Logic tests, scenario N (zone) and R (no zone); copies `zone_ignored`, `zone_assumed`.
6. Link ending during discovery: scenario D (19 checks). It showed a real fault: the ended session's discovery was counted as "Media not found" (`missing 0/1/0`). Fixed: stale discovery answers are dropped (`dm_stale`). The kit's discovery manager was free in the next session.
7. Small points: lock fixes, queue range 1 to 255, every-entry 160-byte check, no adjust reason, play covered (copy `media_local_play`), citation fixed.
8. Table of formats that rest only on the kit: in both documents.

Passes: N 79, R 33, P 19, L 16, D 19 checks; 18 Bluetooth broken copies each fail on their named check.

Not done or unproven: the Local Time Information layout (zone in 15-minute units, daylight codes 0, 2, 4, 8) has no saved source; a drop during the first or last discovery was not tried; nothing ran on a real iPhone. Earlier looks in round 2, including two full runs I stopped after infra timing faults in broken copies, are listed in the file. Server copies and outputs are removed (`build-logs/step3/cleanup-round2.txt`).
