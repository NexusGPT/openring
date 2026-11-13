"""gen_round2.py <final log> : writes docs/step3-round2.md. Every `LOG:n` and `file:n` is found by searching for the exact
text in the saved log and in the delivered files; the script stops when a text is not found."""
import pathlib
import re
import sys

FW = pathlib.Path((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/firmware"))
log_path = pathlib.Path(sys.argv[1])
log = log_path.read_text(encoding="utf-8", errors="replace").split("\n")
rel_log = log_path.relative_to(FW)
cache = {}


def src(rel):
    if rel not in cache:
        cache[rel] = (FW / rel).read_text(encoding="utf-8", errors="replace").split("\n")
    return cache[rel]


def S(rel, text, nth=1):
    n = 0
    for i, l in enumerate(src(rel)):
        if text in l:
            n += 1
            if n == nth:
                return f"`{rel}:{i + 1}`"
    raise SystemExit(f"source text not found in {rel}: {text!r}")


def Ln(text, after=0):
    for i, l in enumerate(log):
        if i + 1 > after and text in l:
            return i + 1
    raise SystemExit(f"log text not found: {text!r}")


def L(text, after=0):
    return f"`LOG:{Ln(text, after)}`"


s_iph = Ln("=== stage bsim-iphone start")
s_brk = Ln("=== stage bsim-iphone-broken start")
s_lnk = Ln("=== stage link-settings start")
RN = "tests/bsim/iphone/ring_app/src/main.c"
HN = "tests/bsim/iphone/host_app/src/main.c"
RIP = "modules/ring_iphone/src/rip.c"
RIPL = "modules/ring_iphone/src/ripl.c"
out = []
w = out.append
last_result = max(i + 1 for i, l in enumerate(log) if l == "RESULT PASS")
exit_line = next(l for l in reversed(log) if l.startswith("# remote exit code"))
w("# Step 3, round 2: answers to the review")
w("")
w("Version: the files under `firmware/` at commit e455a9f (as the lead named it; I ran no git). Review: `docs/step3-review.md`. Paths are under `firmware/`.")
w("")
w(f"Bar command (my own run, my own server copy `RING_REMOTE_SRC=/root/ring-os/src-step3r2c`): `sh firmware/tools/remote.sh os-iphone-r2 \"tools/build_all.sh\"`. Log: `{rel_log}`. The last line build_all printed is `RESULT PASS` (`LOG:{last_result}`); remote.sh then wrote `{exit_line}`. `LOG:n` is a line of that file, `file:n` a line of a delivered file.")
w("")
ends = [l for l in log if l.startswith("=== stage") and " end " in l]
bad = [l for l in ends if not l.endswith(" exit 0")]
w(f"{len(ends)} stages ended, {len(bad)} with a non-zero exit. New in the log: the Bluetooth scenarios L and D ({L('TEST L RESULT PASS', s_iph)}, {L('TEST D RESULT PASS', s_iph)}), the five new broken copies (points 2, 3, 5 and 7) and the stage `link-settings` ({L('=== stage link-settings end')}). Counts: N, R, P, L, D passed with "
  + ", ".join(f"{k} {re.search(r'[(](\d+) checks passed[)]', log[Ln('TEST ' + k + ' RESULT PASS', s_iph) - 1]).group(1)}" for k in "NRPLD") + " checks. Logic suites: all pass on both boards (`LOG:" + str(Ln("ring_iphone.logic", Ln("=== stage tests-native_sim start"))) + "` and the lines after it).")
w("")

# ---------------------------------------------------------------- 1
w("## 1. The product build lacks the link settings the tests ran with")
w("")
w("- **The false claim.** Round 1 said `app/prj.conf` set the MTU and buffer sizes; it did not (review part 4, point 1). The notes now say so: " + S("docs/iphone-notes.md", "Round 1 of these notes claimed") + ".")
w("- **One file.** " + S("modules/ring_iphone/ring_iphone_link.conf", "CONFIG_BT_L2CAP_TX_MTU=247") + ", " + S("modules/ring_iphone/ring_iphone_link.conf", "CONFIG_BT_BUF_ACL_RX_SIZE=251") + ", " + S("modules/ring_iphone/ring_iphone_link.conf", "CONFIG_BT_BUF_ACL_TX_SIZE=251") + ", " + S("modules/ring_iphone/ring_iphone_link.conf", "CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE=3072") + ". The product adds it: " + S("app/CMakeLists.txt", "EXTRA_CONF_FILE") + "; the test ring adds the same file: " + S("tests/bsim/iphone/ring_app/CMakeLists.txt", "EXTRA_CONF_FILE") + ". The old lines are gone from `app/prj.conf` and `tests/bsim/iphone/ring_app/prj.conf` (a search of both for `MTU`, `ACL` and `WORKQUEUE` finds nothing but a comment).")
w("- **The check.** " + S("tools/check_link_settings.sh", "for k in CONFIG_BT_L2CAP_TX_MTU") + " compares the four values of two built `.config` files; stage `link-settings` (" + S("tools/build_all.sh", "link_settings() {") + ") runs it on the development kit build (`dk/app/zephyr/.config`), on the simulated chip product build (`bsim/zephyr/.config`) and on the iPhone test ring (`bsim-iphone/ring/zephyr/.config`). A self test first changes the MTU in a copy of the ring's file and requires the check to refuse it.")
w("  - Log: self test " + L("link-settings: self test ok: the changed MTU was refused", s_lnk) + "; development kit product " + ", ".join(L("link-settings: dk-product " + k, s_lnk) for k in ("CONFIG_BT_L2CAP_TX_MTU=247", "CONFIG_BT_BUF_ACL_RX_SIZE=251", "CONFIG_BT_BUF_ACL_TX_SIZE=251", "CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE=3072")) + "; simulated chip product " + ", ".join(L("link-settings: bsim-product " + k, s_lnk) for k in ("CONFIG_BT_L2CAP_TX_MTU=247", "CONFIG_BT_BUF_ACL_RX_SIZE=251", "CONFIG_BT_BUF_ACL_TX_SIZE=251", "CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE=3072")) + "; stage end " + L("=== stage link-settings end") + ". Each of those lines prints the product's value and the test ring's value.")
fl = log[Ln("FLASH:      ", s_dk := Ln("=== stage dk start")) - 1]
ra = log[Ln("RAM:       ", s_dk) - 1]
w("- **Cost, from the log:** the product's MTU 247 buffers and the larger stack change the kit build to " + re.sub(r"\s+", " ", fl.strip()) + " (" + L("FLASH:      ", s_dk) + ") and " + re.sub(r"\s+", " ", ra.strip()) + " (" + L("RAM:       ", s_dk) + "); round 1 had FLASH 184,932 B and RAM 45,196 B with the default link settings (`build-logs/step3/20261111-235859-os-iphone.log`, lines 543 and 544).")
w("- **Stack margin: not measured.** The product's `bsim-run` stage only boots for 2 s (`" + f"LOG:{Ln('=== stage bsim-run end')}" + "`). In the test ring I tried to read the system workqueue's unused stack with `k_thread_stack_space_get`; the first run printed 3048 of 3072 bytes unused (`console-r2-second.txt`, \"RING INFO system workqueue stack\"). I did not trust it: the simulated chip's threads run on host stacks, so the figure says nothing about the chip. I removed that print and its two settings (`CONFIG_INIT_STACKS`, `CONFIG_THREAD_STACK_INFO`); the margin of the 3072-byte stack on the chip is unmeasured.")
w("")

# ---------------------------------------------------------------- 2
w("## 2. A late answer fragment after the 3 s timeout")
w("")
w("- **Fix, parser.** Before a valid header the stream is searched byte by byte: a late answer of another request, or fragments without a header, are skipped (counted in `skipped`), not an error (" + S(RIPL, "Before a valid header the stream is searched") + "). The four bytes read as an id are searched again when they are not ours (" + S(RIPL, "so they are searched again") + "), and a \"header\" whose first attribute is wrong is searched again too (" + S(RIPL, "not the first tuple of our request") + "): the end of a stale answer can make a false header with the first byte of ours (found by my own logic test `tests/iphone/src/test_iphone.c`, \"05 00 00\" case, before I wrote the second rule).")
w("- **Fix, retry.** " + S(RIP, "static void fetch_failed_locked") + ": a request that timed out, got a wrong answer or whose write failed goes to the front of the queue once (`fetch_retries`); a second failure is given up (`fetch_failed`). Called from the timeout (" + S(RIP, "st.fetch_timeouts++;") + "), the answer error, the write callback and the write start.")
w("- **Logic test:** " + S("tests/iphone/src/test_iphone.c", "test_ds_late_answer_of_another_request_is_skipped") + " (a stale answer then ours, in every fragment size from 1 byte up; the middle of a stale answer; the stale-end false header; only a stale answer never completes; another command id is skipped).")
w("- **Test over Bluetooth, scenario L:** the stand-in holds the answer for notification 401 for 3,500 ms, past the ring's timeout, then sends it (" + S(HN, "late_held == 0") + ", " + S(HN, "static void script_l") + "), with 402, 403 and 404 queued behind it and 405 added later. The stand-in's outgoing answers go through one queue so two answers never interleave (" + S(HN, "static void out_push") + "). The ring checks (" + S(RN, "static void run_l") + "): " + L("RING CHECK L: the four notifications all get their text, although the answer for the first is late PASS", s_iph) + ", " + L("RING CHECK L: each of the four holds its own text (none shifted to its neighbour) PASS", s_iph) + ", " + L("RING CHECK L: one request timed out and was asked for once more, nothing was given up PASS", s_iph) + ", " + L("RING CHECK L: a later notification gets its own text too PASS", s_iph) + ". The stand-in's own record: " + L("PHONE CHECK the answer for 401 was held past the timeout and then sent PASS", s_iph) + ", " + L("PHONE CHECK the ring asked for 401 twice (the timeout, then one retry) and once for each other notification PASS", s_iph) + " (its log line: " + L("PHONE INFO the held answer is sent now", s_iph) + ").")
w("- **Broken copy `late_fragment`** (the round 1 behaviour restored: both skip rules become errors, and no retry; " + S("tests/bsim/iphone/broken_edit.py", '"late_fragment"') + "): " + L("broken late_fragment: test L failed on its named check, as required", s_brk) + ".")
w("")

# ---------------------------------------------------------------- 3
w("## 3. Bar c: an action without its flag sends nothing")
w("")
w("- The stand-in now records every action command BEFORE it can refuse one (" + S(HN, "every command is recorded BEFORE it can be refused") + ") and counts the ones for a notification that does not have that action (`flagless_cmds`, " + S(HN, "flagless_cmds++") + "). Its check: " + L("PHONE CHECK no action command arrived for a notification that does not have that action (every command is recorded before it can be refused) PASS", s_iph) + " (`ncmds == 2 && flagless_cmds == 0`: the two accepted commands were all that arrived, including the refused ones). The ring's check that `action_failed` stays 0 is added to the no-error check (" + L("RING CHECK no error was counted by the iPhone part PASS", s_iph) + ").")
w("- **Broken copy `action_sent`** (the flag check sends the kit's write and still returns -ENOTSUP; " + S("tests/bsim/iphone/broken_edit.py", '"action_sent"') + "): " + L("broken action_sent: test N failed on its named check, as required", s_brk) + " (the named check is the stand-in's; the ring's two refusal checks pass in that copy, as the review predicted: " + L("RING CHECK c: an action without its flag is refused: dismiss of 104 (no actions) PASS", Ln("##### broken copy: action_sent")) + "; the ring's no-error check, which now includes `action_failed`, does fail in it because the iPhone answers 0xA3: " + L("RING CHECK no error was counted by the iPhone part FAIL", Ln("##### broken copy: action_sent")) + ").")
w("")

# ---------------------------------------------------------------- 4
w("## 4. Bar h: the check tests what its name says")
w("")
w("I chose to make the check prove Service Changed was looked for. It now also requires `gattp_found == 1 && gattp_missing == 0` (the plain host has the GATT service with Service Changed) next to the three missing services and `dm_errors == 0`, and its name says so (" + S(RN, "h: Service Changed was looked for and found") + "): " + L("RING CHECK h: Service Changed was looked for and found (the host has the GATT service), the three Apple services were looked for and not found (not an error) PASS", s_iph) + ". The notes' bar h answer uses the new name. The copy `service_error` (a `dm_errors++` on the not-found path) is caught on this check: " + L("broken service_error: test P failed on its named check, as required", s_brk) + ". The remaining weakness the review named (\"no error\" rests on the ring's counters) stays; the key check of the stand-in (" + L("PHONE CHECK the ring's key arrived once (media centre: usage 0x00CD, then release) PASS", s_iph) + ") is the outside witness that the link worked.")
w("")

# ---------------------------------------------------------------- 5
w("## 5. The clock: UTC and the zone")
w("")
w("- **Code.** The ring reads Local Time Information next to Current Time (" + S(RIP, "static void lti_refresh") + ", " + S(RIP, "static uint8_t lti_read_cb") + "), finds the characteristic in the same discovery as the kit's Current Time handles (" + S(RIP, "bt_gatt_dm_char_by_uuid(dm, BT_UUID_GATT_LTI)") + "), converts with `ripl_cts_zone` (" + S(RIPL, "bool ripl_cts_zone") + ") and sets the clock to UTC = local - zone - daylight with the offset (" + S(RIP, "rtime_set(ms - (int64_t)zm * 60000, zm, true);") + "); with no zone it keeps the local time (" + S(RIP, "rtime_set(ms, 0, false);") + "). The clock stores a `zone_known` flag and its API returns it: " + S("modules/ring_time/include/ring_time/rtime.h", "bool rtime_zone_known(void);") + ", " + S("modules/ring_time/src/rtime_logic.c", "r->zone_known = zone_known;") + ".")
w("- **Logic tests:** `test_cts_zone` (" + S("tests/iphone/src/test_iphone.c", "ZTEST(ring_iphone, test_cts_zone)") + ": +1 h, +1 h with daylight +1 h = 120 minutes, -5 h and +0.5 h = -270, the limits, the unknown values -128 and 255, out-of-range values, nothing written when unknown) and `test_zone_not_known_is_kept_as_a_flag` (" + S("tests/time/src/test_time.c", "test_zone_not_known_is_kept_as_a_flag") + "). Both ran on both boards in stage `tests-*` of the log and in the broken runs of stage `broken-iphone`/`broken-time`.")
w("- **With a zone (scenario N):** the stand-in serves zone +1 h and daylight +1 h (" + S(HN, "lti_dst = 4;") + "); the local time it serves is the base literal 22:05:46, so UTC is two hours earlier. " + L("RING CHECK the ring's clock equals the iPhone's time within 1 s, as UTC (the iPhone's zone +2 h taken off) PASS", s_iph) + ", " + L("RING CHECK the zone is known and is +120 minutes PASS", s_iph) + ", " + L("RING CHECK g: the ring's clock follows the iPhone's time change (two hours) PASS", s_iph) + ", " + L("RING CHECK g: the zone stays known and +120 minutes PASS", s_iph) + ", the stand-in saw the zone read: " + L("PHONE CHECK the ring read Local Time Information PASS", s_iph) + ".")
w("- **Without a zone (scenario R):** the stand-in serves -128 and 255 (unknown): " + L("RING CHECK R: the iPhone gave no zone: the clock holds its local time and says the zone is not known PASS", s_iph) + ".")
w("- **Broken copies:** `zone_ignored` (the zone is not taken off) -> " + L("broken zone_ignored: test N failed on its named check, as required", s_brk) + "; `zone_assumed` (an unknown zone is treated as known) -> " + L("broken zone_assumed: test R failed on its named check, as required", s_brk) + "; `time_ignored` now ignores the whole notification (" + L("broken time_ignored: test N failed on its named check, as required", s_brk) + ").")
w("- **Not sourced:** the Local Time Information layout (zone in 15-minute units, daylight codes 0, 2, 4, 8, unknown values -128 and 255) is the author's reading of the Bluetooth SIG specification; no saved document or kit file has it. The stand-in and the ring share it. It is the last row of the table of point 8 and in the notes, section 3. A zone with an unknown daylight value (255) counts as \"zone not known\".")
w("")

# ---------------------------------------------------------------- 6
w("## 6. A link that ends during discovery")
w("")
w("- **Test, scenario D** (" + S(RN, "static void run_d") + ", " + S(HN, "static void script_d") + "): the stand-in ends the link 60 ms after the ring subscribed to the Data Source (" + S(HN, "drop_in_discovery = false;") + "), while the ring is still looking for the Media and Current Time services, stays away 3 s, then reconnects. Stand-in side: " + L("PHONE CHECK the link ended before the ring had subscribed to Media and Time (the drop came during discovery) PASS", s_iph) + " (its log line: " + L("PHONE INFO the link is ended while the ring is discovering", s_iph) + "), " + L("PHONE CHECK in the next session the ring subscribed to the Notification Source, Entity Update and Current Time PASS", s_iph) + ". Ring side: " + L("RING CHECK D: the ring counted a session that ended in discovery PASS", s_iph) + ", " + L("RING CHECK D: the three services are found in the next session PASS", s_iph) + ", " + L("RING CHECK D: a notification sent in the next session arrives with its text PASS", s_iph) + ", " + L("RING CHECK D: a discovery was running when the link ended and its answer was dropped as stale PASS", s_iph) + ", " + L("RING CHECK D: no service was reported missing", s_iph) + ". The ring's counters in that run: " + L("RING INFO D: missing 0/0/0", s_iph) + ".")
w("- **What the test showed, and the fix.** The first run of D (`console-r2-second.txt`) passed every check about the next session (the kit's discovery manager frees itself when the link ends: the three services were found) but failed the check \"no service was reported missing\". I added a diagnostic line; the next run (`console-r2-third.txt`) printed `RING INFO D: missing 0/1/0, dm_errors 0, dm_stale 0`: the Media service was counted as \"not found\" in the session that had ended. The Bluetooth host ends a running discovery when the link goes down and calls the discovery's callback as \"not found\" before this module's own disconnect callback runs; the same callback could also have moved the phase of the next session. Fix, first attempt: every discovery carries the number of its session and a stale session's answer is dropped; it did not change the result (which suggests that the callback comes while the session is still the current one). Fix that worked: the answer is also dropped when the link is no longer connected (the link is asked), counted as `dm_stale`: " + S(RIP, "static bool dm_stale") + ", " + S(RIP, "session_gen++") + ", " + S(RIP, "#define DM_CTX") + ". The review's worry that the discovery manager would stay busy and the service be skipped for the whole next session did not occur in this test: the manager was free in the next session and no retry was needed (`dm_errors` 0).")
w("- **Limit:** the drop comes after the Notification Center discovery and before the Media discovery has finished; a drop during the first (GATT service) or the last (Current Time) discovery is not tried. No broken copy for D (not asked for): the fix is checked by the counters and the three-services check, and the \"missing 0/1/0\" run above is the before state.")
w("")

# ---------------------------------------------------------------- 7
w("## 7. Small points")
w("")
w("1. **Flags written or read outside the lock.** `ds_subscribed` is now written under the mutex (" + S(RIP, "ds_subscribed = (err == 0);") + " has the lock lines around it) and `sconn` is read under it in `ready_fn` (" + S(RIP, "had = (sconn != NULL);") + "). `rip_action` and `rip_media_command` already read `sconn` inside the lock. Not tested as a race: by reading only.")
w("2. **Range of `CONFIG_RING_IPHONE_FETCH_QUEUE`:** " + S("modules/ring_iphone/Kconfig", "range 1 255") + " (the indexes are `uint8_t`). By reading; a value outside the range is refused by Kconfig.")
w("3. **\"No message is longer than 160 bytes\" covers every entry:** " + S(RN, "static bool all_entries_within_limits") + " checks every entry of the inbox for identifier at most 48, title at most 48, message at most 160 and complete UTF-8 (the strict checker " + S(RN, "static bool utf8_ok") + " is written in the test, not taken from the inbox): " + L("RING CHECK a: no message is longer than 160 bytes and none ends inside a character (every entry) PASS", s_iph) + ".")
w("4. **No adjust reason on a time change:** the stand-in sends reason 0 (" + S(HN, "the ADG: the iPhone gives no Adjust Reason") + "). The ring ignores the field.")
w("5. **The player-state copy covers play:** scenario N now sends play while the player is paused (" + S(RN, "f: play is sent while the player is paused") + "), and the stand-in's command list ends with a second play (id 0, " + L("PHONE CHECK the six media commands arrived: play, pause, next, previous, volume up, volume down (ids 0,1,3,4,5,6), then play again (id 0) PASS", s_iph) + "). Copy `media_local_play` (play sets the state): " + L("broken media_local_play: test N failed on its named check, as required", s_brk) + "; the pause copy `media_local` still fails on its check (" + L("broken media_local: test N failed on its named check, as required", s_brk) + ").")
w("6. **The citation of the stage's own result.** Round 1 cited `LOG:4390`, which is a line of the first broken copy, not the stage result. The notes are regenerated from the new log with the stage's real result line (`" + f"LOG:{max(i + 1 for i, l in enumerate(log) if l == 'RESULT PASS' and i + 1 < Ln('=== stage bsim-iphone-broken end'))}" + "`, just before " + L("=== stage bsim-iphone-broken end") + ").")
w("")

# ---------------------------------------------------------------- 8
w("## 8. Formats that rest only on the kit")
w("")
w("The table is section 3 of `docs/iphone-notes.md` (\"Formats that rest only on the kit, or on nothing\"), copied here:")
w("")
w((FW / "build-logs/step3/kit_only_table.md").read_text().strip())
w("")

w("## What I could not do, and what changed after the run started")
w("")
w("- The product's stack margin on the chip (point 1): not measured, no run gives it.")
w("- The Local Time Information layout and the replay behaviour of a real iPhone are unproven (point 5, table of point 8).")
w("- A drop during the first or the last discovery, and a drop in scenario D with a broken copy, were not tried (point 6).")
w("- No delivered source file changed after the bar run began: `build-logs/step3/files-changed-after-r2-start.txt` lists two files (`tests/bsim/iphone/run.sh`, `tests/bsim/iphone/host_app/src/main.c`) with a modification time of 01:41:04, before the run's own start at 01:41:23 and its copy to the server. `docs/iphone-notes.md` and this file were written after the run from its log.")
w("- Earlier looks at results in round 2, in order: `console-r2-first.txt` (logic: one failed case, `test_ds_late_answer_of_another_request_is_skipped`, found a real flaw in my first parser rule, fixed as in point 2; the Bluetooth build failed to link because the stack read needed `CONFIG_THREAD_STACK_INFO`), `console-r2-second.txt` (scenarios N R P L passed, D failed on the \"missing\" check, point 6), `console-r2-third.txt` (D after the first fix: still `missing 0/1/0`, because the stale test looked at the session only), `console-r2-fourth.txt` (all five scenarios passed), `console-r2-dk.txt` (the development kit build holds the four settings), and `20261112-010644-os-iphone-r2.log` (a first full run of the bar command: stages up to `bsim-iphone` passed, but its first broken copy `inbox_size` showed `infra: ring-not-done-before-eval`, because the longer scenario N made the ring in a broken copy finish after the stand-in's evaluation time. I stopped it (my `remote.sh` killed; its container took minutes to stop on the loaded server), moved the stand-in's evaluation from 80 s to 95 s after its start, and ran the bar command again; this second run got as far as the new copy `late_fragment`, whose scenario L had the same infra problem (`broken late_fragment: the run itself failed (infra: ring-not-done-before-eval)`, `20261112-012046-os-iphone-r2.log`). I stopped it as well, moved the evaluation time of scenario L from 30 s to 75 s after its start and its simulated length from 90 s to 130 s, checked the new copies alone in two short runs (`console-r2-newbroken.txt`, `console-r2-newbroken2.txt`: late_fragment, action_sent, zone_ignored, zone_assumed, media_local_play, time_ignored and core_touch each failed on their named check) and ran the bar command a third time: the log of this file is that third run).")
w("")
w("RESULT: done, `sh firmware/tools/remote.sh os-iphone-r2 \"tools/build_all.sh\"` ends RESULT PASS and points 1 to 8 are fixed or answered above, with the stack margin on the chip and the Local Time Information layout named as not measured and not sourced.")
(FW / "docs" / "step3-round2.md").write_text("\n".join(out) + "\n")
print("written", len("\n".join(out)), "bytes")
