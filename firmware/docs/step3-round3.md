# Step 3, round 3: answers to the second review

Version: the files under `firmware/` at commit 1e7ccd8 (as the lead named it; I ran no git). Review: `docs/step3-review-2.md`. Paths are under `firmware/`.

Bar command (my own run, own server copy `RING_REMOTE_SRC=/root/ring-os/src-step3r3d`): `sh firmware/tools/remote.sh os-iphone-r3 "tools/build_all.sh"`. Log: `build-logs/step3/20261112-090932-os-iphone-r3.log`. The last line build_all printed is `RESULT PASS` (`LOG:7950`); remote.sh then wrote `# remote exit code: 0`. 15 stages ended, 0 with a non-zero exit. `LOG:n` is a line of that file.

New in the log: scenarios Z and W (`LOG:4367`, `LOG:4399`), scenario counts N 80, R 33, P 19, L 17, D 19, Z 13, W 13 checks; five new Bluetooth broken copies (23 in all); two new logic broken copies; the extended `link-settings` stage (`LOG:7465`).

## 1. The clock

- **(a) No drift.** The iPhone part keeps, in a pure state `struct ripl_clock` (`modules/ring_iphone/include/ring_iphone/ripl.h:134`), the Current Time value with the uptime at which it ARRIVED. A zone read that returns changes the zone only; the clock is set from the stored time at the arrival uptime (`modules/ring_iphone/src/ripl.c:309`, used by `modules/ring_iphone/src/rip.c:397`). The old code paired the stored time with the uptime of now (review part 3, point 1).
- **(b) A failed read keeps the zone.** `modules/ring_iphone/src/ripl.c:298`: a read that failed or had the wrong length is counted (`zone_errors`, `modules/ring_iphone/src/rip.c:441`) and changes nothing else. "Zone not known" follows only from unknown values or from a link without the characteristic (the clock state is reset at each link: `modules/ring_iphone/src/rip.c:647`).
- **Logic tests** (both boards): `test_clock_no_drift_with_delayed_zone_read` (`tests/iphone/src/test_iphone.c:372`: 100 time notifications, zone reads delayed 37 to 400 ms, exact to 1 ms at two moments each) and `test_clock_failed_zone_read_keeps_the_last_zone` (`tests/iphone/src/test_iphone.c:403`). Broken copies of the logic suite (stage `broken-iphone`, both boards, `tests/iphone/broken_run.sh`): `clock_drift` `LOG:7784` and `LOG:7816`; `clock_failed_read` `LOG:7852` and `LOG:7884`. The old `media_state` copy still fails on its case (`LOG:7716`).
- **Over Bluetooth.** The clock checks are tightened from 1 s to 100 ms (`tests/bsim/iphone/ring_app/src/main.c:274`, also in the new `clock_is_zone`). Scenario N, with a zone: `LOG:3992` (the name still says "1 s"; the tolerance in the code is 100 ms). A failed zone read after good ones, at 42.5 s: the stand-in refuses the read (`LOG:4097`) and `LOG:4033`. Zone change while linked, scenario Z: `LOG:4345`, `LOG:4346`, `LOG:4347`. A stand-in without Local Time Information, scenario W (the service is registered with its first four attributes only, `tests/bsim/iphone/host_app/src/main.c:217`): `LOG:4377`, `LOG:4378`, `LOG:4379`, stand-in side `LOG:4396`.
- **Broken copies over Bluetooth:** `zone_read_failed` (a failed read counts as a good one with unknown values; for the failed read) `LOG:7286`; `zone_not_reread` (no zone read after a notification) `LOG:7396`; `no_lti_known` (a link without the characteristic is taken as zone known) `LOG:7443`. The drift copy is the logic copy `clock_drift` above: the Bluetooth clock check is 100 ms and a one-interval delay is below what one simulated run can show reliably, so the drift proof is the exact logic test.
- **Limit:** the real iPhone's zone-read delay and whether it serves Local Time Information are unproven (notes, section 3).

## 2. The late answer lands inside a later request

- **Test.** In scenario L the stand-in holds the answer for 401 for 3,500 ms and sends it twice, 200 ms apart, and holds every answer for 402 for 1,000 ms (`tests/bsim/iphone/host_app/src/main.c:1403`, `tests/bsim/iphone/host_app/src/main.c:1405`). The ring has by then given up 401, asked again (the retry is answered at once), and gone on to 402, so the late bytes arrive while the request for 402 is in flight. The ring reports the bytes it skipped and the check requires more than 0: `LOG:4254` (value: `LOG:4255`). The four own-text checks: `LOG:4252`, `LOG:4253`.
- **Broken copy `late_parser`** (keeps the retry, restores the round 1 parser: both skip rules become errors, `tests/bsim/iphone/broken_edit.py:125`): `LOG:7119` on the named "own text" check. The old copy `late_fragment` (retry removed too) stays: `LOG:6434`.

## 3. A broken copy for scenario D

`dm_gone` removes the "link gone" test of the discovery answer (`modules/ring_iphone/src/rip.c:688` is replaced by `gone = false`; `tests/bsim/iphone/broken_edit.py:138`): `LOG:7349` on "no service was reported missing".

## 4. The settings check

- `CONFIG_BT_GATT_DM_MAX_ATTRS` is compared too, and the MTU is pinned to at least 247: `tools/check_link_settings.sh:11`, `tools/check_link_settings.sh:23`. Self test with two equal wrong values (both sides MTU 23): `LOG:7452`; the first self test (one side changed) `LOG:7449`; the product values, five per build: `LOG:7459`, `LOG:7464`.
- **A build-time assert in the module:** `modules/ring_iphone/src/rip.c:43`. The stage builds the iPhone test ring with a copy of the shared file whose MTU is 100 (`-DRING_IPHONE_LINK_CONF=...`, a variable the test ring's CMakeLists now has for this; Zephyr itself refuses an MTU of 23 or a second value for the symbol, so 100 is the lowest valid test value I used) and requires that the build fails with the assert's text: `LOG:7454` (the assert's own line: `LOG:7453`). Stage end `LOG:7465`.

## 5. The false header with notification id 0

No rule can tell it from a real header without keeping about 300 bytes of the stream to read again; I did not build that. The stale answer's last bytes `05 00 00` plus the first byte of the answer for id 0 read as header, id 0, first attribute 0, length 0, and the parser goes wrong from there. It ends in an error (or, with other length bytes, a timeout), and the ring then asks again with a fresh parser state: the cost is one retry (at most the 3 s timeout), and it needs our id to be 0 together with a stale answer that ends in an empty date. Logic test showing both halves (the spoiled stream does not complete, the fresh start does): `tests/iphone/src/test_iphone.c:437`. iPhone ids are 32-bit values chosen by the iPhone; a 0 is possible but nothing says it is used. Said in the notes, section 6.

## 6. Notes and comments

The three false claims of `docs/iphone-notes.md` (round 2 lines 14, 28, 133), each re-read before the change:
- line 14 (bar c): it rested on `nactions == 2`; it now cites the stand-in's own witness (`LOG:4121`) and says so (`docs/iphone-notes.md`, bar c).
- line 28 (bar j): "every Bluetooth test has a broken copy" was false for D. D now has `dm_gone`, and Z and W have `zone_not_reread` and `no_lti_known`; the count in the notes is computed from the log (`LOG:7396`).
- line 133: "the fetch timeout stays 0" and "a link that ends during discovery" are reached by no run: both are now reached (L and D); the section 6 text is rewritten with what is still unreached.
- `docs/step3-round2.md`: the two citations are corrected (`rip.c:319`; the round 1 log named by its file for line 4390) and a note says the line numbers of that file refer to the round 2 files.
- Stale comments: `modules/ring_iphone/include/ring_iphone/ripl.h:158` and `tests/bsim/iphone/host_app/src/main.c:44` (the stand-in's header now says Local Time Information is served, and scenario W leaves it out).

## Earlier looks in round 3

In order: `console-r3-first.txt` (logic 40 of 40 pass; scenario L passed with 130 skipped bytes; Z failed its stand-in check `lti_reads >= 3`, which was my wrong count: the ring reads the zone at the start and after the one notification, so 2; changed); `console-r3-a.txt`, `console-r3-b.txt`, `console-r3-c.txt` (the new copies late_parser, zone_read_failed, dm_gone, zone_not_reread, no_lti_known and the logic copies each failed on their named check); `20261112-084253-os-iphone-r3.log` (a full run of the bar command that ended `RESULT FAIL link-settings`: my new MTU build test used `-DCONFIG_BT_L2CAP_TX_MTU=23`, which Zephyr refuses before the assert is reached, so the stage said so and failed; nothing else failed in that run); `console-r3-mtu.txt` (the same with a file copy: Zephyr refuses 23 as a value), `console-r3-mtu2.txt` (MTU 100: the build stops on the module's assert). The bar run of this file is the one after that fix.

## What I could not do

- A Bluetooth broken copy for the drift itself (point 1): the drift proof is the exact logic test and its copy; see point 1.
- The product's workqueue stack margin on the chip stays unmeasured; the false header with id 0 is not fixed (point 5); nothing ran on a real iPhone.

RESULT: done, `sh firmware/tools/remote.sh os-iphone-r3 "tools/build_all.sh"` ends RESULT PASS and points 1 to 6 are fixed or answered above, with the false header for id 0 explained and not fixed.
