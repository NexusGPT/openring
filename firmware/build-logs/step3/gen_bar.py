"""gen_bar.py <log file>: writes section 1 of docs/iphone-notes.md (the answers to the bar) from the saved log
and the delivered source files. Every `LOG:n` and `file:n` is found by searching for the exact text; the script
stops with an error when a text is not found, so no citation is typed by hand."""
import pathlib
import re
import sys

FW = pathlib.Path((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/firmware"))
log_path = pathlib.Path(sys.argv[1])
log = log_path.read_text(encoding="utf-8", errors="replace").split("\n")
cache = {}


def src(rel):
    if rel not in cache:
        cache[rel] = (FW / rel).read_text(encoding="utf-8", errors="replace").split("\n")
    return cache[rel]


def L(text, nth=1, after=None):
    """the line number of the nth log line holding text (searching after line `after`)"""
    n = 0
    for i, l in enumerate(log):
        if after is not None and i + 1 <= after:
            continue
        if text in l:
            n += 1
            if n == nth:
                return i + 1
    raise SystemExit(f"log text not found: {text!r}")


def S(rel, text):
    for i, l in enumerate(src(rel)):
        if text in l:
            return f"`{rel}:{i + 1}`"
    raise SystemExit(f"source text not found in {rel}: {text!r}")


def lc(text, after=None, nth=1):
    return f"`LOG:{L(text, nth, after)}`"


# the start of each stage in the log, so that a pattern is searched in the right stage
def stage(name):
    return L(f"=== stage {name} start")


s_iph = stage("bsim-iphone")
s_iph_b = stage("bsim-iphone-broken")
RN = "tests/bsim/iphone/ring_app/src/main.c"
HN = "tests/bsim/iphone/host_app/src/main.c"
RIP = "modules/ring_iphone/src/rip.c"

out = []
w = out.append

# find the scenario boundaries inside stage bsim-iphone
tN = L("=== test N (ok)", after=s_iph)
tR = L("=== test R (ok)", after=s_iph)
tP = L("=== test P (ok)", after=s_iph)


def ln(text, after):
    return lc(text, after=after)


w("**a. Three or more notifications, exact text and flags, the 200-byte message cut on a character: yes.** "
  "The stand-in sends five (`script_n`, " + S(HN, "add(101, 4, 0x1A") + " to " + S(HN, "add(105, 11, 0x10") + "). The ring's checks hold literals "
  "for app identifier, title, message, date, category and flags (" + S(RN, 'CHECK("a: 101 exact') + " to " + S(RN, 'CHECK("a: 105 exact') + "). "
  "Log: " + ln("RING CHECK a: 101 exact (SMS: category 4, flags important+positive+negative) PASS", tN) + ", "
  + ln("RING CHECK a: 102 exact (mail: category 6, negative action) PASS", tN) + ", "
  + ln("RING CHECK a: 103 exact: identifier cut at 48 bytes, title at 48, the 200-byte message cut to 159 bytes on a character PASS", tN) + ", "
  + ln("RING CHECK a: 104 exact (no actions, empty message) PASS", tN) + ", "
  + ln("RING CHECK a: 105 exact (the iPhone sent all 200 bytes: kept 160 and cut at a character) PASS", tN) + ", "
  + ln("RING CHECK a: no message is longer than 160 bytes and none ends inside a character (every entry) PASS", tN) + ". "
  "103 is the case where the iPhone cuts at the 160 bytes the ring asked for, inside a character (so the ring drops the half character); "
  "105 is the case where the iPhone ignores the maximum length and sends 200 bytes. The cut is " + S("modules/ring_inbox/src/rinbox.c", "size_t rinbox_utf8_cut") +
  "; its logic test `test_utf8_cut_property` (`tests/inbox/src/test_inbox.c`) tries every length and limit of a mixed string. "
  "Broken copies that must fail here: `utf8_cut` -> " + ln("broken utf8_cut: test N failed on its named check, as required", s_iph_b) +
  "; `request_len` -> " + ln("broken request_len: test N failed on its named check, as required", s_iph_b) + ".")

w("")
w("**b. A change replaces the text, a removal deletes the entry, the 17th drops the oldest: yes.** "
  + ln("RING CHECK b: the change arrived PASS", tN) + ", " + ln("RING CHECK b: the changed notification keeps its place and has the new flags (positive action gone) PASS", tN) + ", "
  + ln("RING CHECK b: the removal deletes the entry PASS", tN) + ", " + ln("RING CHECK b: thirteen more arrive: the store holds 16 PASS", tN) + ", "
  + ln("RING CHECK b: the 17th notification dropped the oldest (101) and only that one PASS", tN) + " (it also checks that `inbox_dropped` is exactly 1). "
  "Code: " + S(RIP, "static void ns_cb") + ", " + S("modules/ring_inbox/src/rinbox.c", "int rinbox_add") + ". "
  "Broken copies: `inbox_size` -> " + ln("broken inbox_size: test N failed on its named check, as required", s_iph_b) + ", `remove_ignored` -> "
  + ln("broken remove_ignored: test N failed on its named check, as required", s_iph_b) + ", `modify_ignored` -> "
  + ln("broken modify_ignored: test N failed on its named check, as required", s_iph_b) + ".")

w("")
w("**c. A dismiss chosen on the ring arrives as the negative action, a positive action likewise, an action without its flag sends nothing: yes.** "
  + ln("RING CHECK c: dismiss chosen on the ring for 122 is sent PASS", tN) + ", " + ln("RING CHECK c: positive action for 121 is sent PASS", tN) + "; the stand-in's own record: "
  + ln("PHONE CHECK two actions arrived: negative for 122, positive for 121, and no other PASS", tN) + " (its log line for the command: " + ln("PHONE INFO action 1 for notification 122", tN) + "). "
  "Refusals: " + ln("RING CHECK c: an action without its flag is refused: dismiss of 104 (no actions) PASS", tN) + ", "
  + ln("RING CHECK c: an action without its flag is refused: positive action of 103 (negative only) PASS", tN) + ", "
  + ln("RING CHECK c: two commands were sent and three were refused PASS", tN) + " and the stand-in's own witness: it records every action command before it can refuse one, and " + ln("PHONE CHECK no action command arrived for a notification that does not have that action (every command is recorded before it can be refused) PASS", tN) + " (`ncmds == 2 && flagless_cmds == 0`). "
  "The inbox does not change on the ring's own command: " + ln("RING CHECK c: the inbox does not change on the ring's own command (122 is still there) PASS", tN) + "; it changes when the iPhone reports the removal: "
  + ln("RING CHECK c: the iPhone reports the dismissed notification removed: 122 leaves the inbox PASS", tN) + ". "
  "Code: " + S(RIP, "int rip_action") + ". Broken copies: `action_flag` -> " + ln("broken action_flag: test N failed on its named check, as required", s_iph_b) +
  ", `action_id` -> " + ln("broken action_id: test N failed on its named check, as required", s_iph_b) + ".")

w("")
w("**d. After a dropped link and a reconnect the inbox is first empty, then holds what the stand-in sends again: yes.** Scenario R. "
  + ln("RING CHECK d: the link drops PASS", tR) + ", " + ln("RING CHECK d: the inbox is empty when the link has ended PASS", tR) + ", "
  + ln("RING CHECK d: the inbox holds what the iPhone sends again PASS", tR) + ", "
  + ln("RING CHECK d: rebuilt from the iPhone: 203 then 201 with the pre-existing mark, the edited text; 202 is gone PASS", tR) +
  ". The stand-in removed 202, edited 201 and added 203 while the link was down, so the new content cannot be old data kept by the ring; the stand-in's replay carries the pre-existing flag, which the ring's stored flags show (0x1C and 0x04). "
  "Code: " + S(RIP, "static void end_session") + ". Broken copy `reset_on_drop` -> " + ln("broken reset_on_drop: test R failed on its named check, as required", s_iph_b) + ".")

w("")
w("**e. The service removed and added again while linked (Service Changed): the ring stops, then subscribes again and receives a new notification: yes.** Scenario R. "
  + ln("RING CHECK e: the ring stops when the service goes away PASS", tR) + ", " + ln("RING CHECK e: the inbox is emptied when the service ends PASS", tR) + ", "
  + ln("RING CHECK e: Service Changed was indicated and the services were stopped (twice: the drop and the removal) PASS", tR) + ", "
  + ln("RING CHECK e: the ring subscribes again when the service is back PASS", tR) + ", "
  + ln("RING CHECK e: a new notification arrives and is stored exactly PASS", tR) + ", " + ln("RING CHECK e: subscribed three times in all (start, after the drop, after Service Changed) PASS", tR) + ". "
  "The stand-in's side: " + ln("PHONE INFO the Notification Center Service is removed", tR) + ", " + ln("PHONE INFO the Notification Center Service is added again", tR) + ", "
  + ln("PHONE CHECK the ring subscribed to the Notification Source three times (start, after the drop, after Service Changed) PASS", tR) + ". "
  "Code: " + S(RIP, "static void sc_indicated") + ", " + S(RIP, "static void stop_services") + ". Broken copy `sc_ignored` -> " + ln("broken sc_ignored: test R failed on its named check, as required", s_iph_b) + ".")

w("")
w("**f. Track title, artist and player state follow the stand-in's reports; the six media commands arrive; the stored state does not change on a command alone: yes.** "
  + ln("RING CHECK the player state and track follow the iPhone's first report (paused, Bohemian Rhapsody, Queen) PASS", tN) + ", "
  + ln("RING CHECK f: a new track and the playing state arrive from the iPhone PASS", tN) + ", "
  + ln("RING CHECK f: the stored state did not change on the commands alone (pause was sent, the state is still playing) PASS", tN) + ", "
  + ln("RING CHECK f: the stored state follows the iPhone's next report (paused) PASS", tN) + ". The commands at the stand-in: "
  + ln("PHONE CHECK the six media commands arrived: play, pause, next, previous, volume up, volume down (ids 0,1,3,4,5,6), then play again (id 0) PASS", tN) + " (its log lines " + ln("PHONE INFO remote command 0", tN) + " to " + ln("PHONE INFO remote command 6", tN) + "). "
  "The stand-in never changes its player state because of a command (`rc_write`, " + S(HN, "static ssize_t rc_write") + "). Code: " + S(RIP, "static void eu_cb") + ", " + S("modules/ring_iphone/src/ripl.c", "int ripl_media_apply") + ". "
  "Broken copy `media_local` -> " + ln("broken media_local: test N failed on its named check, as required", s_iph_b) + ".")

w("")
w("**g. The ring's clock equals the stand-in's time within 1 s after the link is ready, and follows a time change: yes; since round 2 the clock holds UTC (the iPhone's zone is read and taken off), or the local time with \"zone not known\" when the iPhone gives no zone (section 4, point 2).** "
  + ln("RING CHECK the ring's clock equals the iPhone's time within 1 s, as UTC (the iPhone's zone +2 h taken off) PASS", tN) + ", " + ln("RING CHECK g: the ring's clock follows the iPhone's time change (two hours) PASS", tN) + ". "
  "The ring's check compares `rtime_utc_ms()` with a literal base (2026-11-11T22:05:46 local, 1794434746000 ms) minus the stand-in's +2 h zone plus the simulated uptime (" + S(RN, "static bool clock_is") + "); the stand-in serves that time as Current Time with its own civil-date code (" + S(HN, "static void civil_from_days") + "). "
  "Logic tests of the clock and of the date conversion: `tests/time/src/test_time.c`. Code: " + S(RIP, "static void cts_apply") + ". Broken copy `time_ignored` -> " + ln("broken time_ignored: test N failed on its named check, as required", s_iph_b) + ".")

w("")
w("**h. With a host that serves no Apple service as the active device: no error, keys still work, the inbox stays empty: yes (stand-in in plain mode, section 4, point 3).** Scenario P. "
  + ln("RING CHECK h: Service Changed was looked for and found (the host has the GATT service), the three Apple services were looked for and not found (not an error) PASS", tP) + ", " + ln("RING CHECK h: the inbox stays empty PASS", tP) + ", "
  + ln("RING CHECK h: keys still work: media centre sends 2 reports PASS", tP) + ", " + ln("PHONE CHECK the ring's key arrived once (media centre: usage 0x00CD, then release) PASS", tP) + ". "
  "Also in scenario N, with the iPhone as the active device: " + ln("RING CHECK keys still go to the active device: media centre sends 2 reports PASS", tN) + ". Broken copy `service_error` -> " + ln("broken service_error: test P failed on its named check, as required", s_iph_b) + ".")

w("")
w("**i. A notification, a media report and a time change during RECORDING and during STANDBY change no core state and start or stop no recording: yes.** Scenario N. "
  + ln("RING CHECK i: a long press starts a recording PASS", tN) + ", " + ln("RING CHECK i: events arrived during RECORDING (one added, one modified, one removed, a track, a state, a time) PASS", tN) + ", "
  + ln("RING CHECK i: the core is still RECORDING, no recording started or stopped, no key sent PASS", tN) + ", " + ln("RING CHECK i: a long press stops the recording PASS", tN) + ", "
  + ln("RING CHECK i: events arrived during STANDBY (one added, one modified, one removed, a track, a state, a time) PASS", tN) + ", "
  + ln("RING CHECK i: the core is still STANDBY, no recording started or stopped, no key sent PASS", tN) + ". "
  "By construction too: `modules/ring_iphone` includes no header of the core or the glue (`rip.c` includes: " + S(RIP, "#include <ring_devices/rdev.h>") + " to " + S(RIP, "#include <ring_time/rtime.h>") + "). Broken copy `core_touch` (a time change presses the centre while a recording runs) -> " + ln("broken core_touch: test N failed on its named check, as required", s_iph_b) + ".")

w("")
s_bin = stage("broken-inbox")
s_btm = stage("broken-time")
s_bip = stage("broken-iphone")
s_tn = stage("tests-native_sim")
s_tb = stage("tests-nrf54lm20bsim_nrf54lm20a_cpuapp")
nb = sum(1 for k, l in enumerate(log) if k + 1 > s_iph_b and "failed on its named check, as required" in l and k + 1 < L("=== stage bsim-iphone-broken end"))
w("**j. Logic tests of the inbox and the clock on native_sim and on the ring chip board; every Bluetooth test has a broken copy that fails on its own named check: yes.** "
  "Logic suites on native_sim: " + lc("native_sim/native         ring_inbox.logic", after=s_tn) + ", " + lc("native_sim/native         ring_time.logic", after=s_tn) + ", " + lc("native_sim/native         ring_iphone.logic", after=s_tn) +
  "; on `nrf54lm20bsim/nrf54lm20a/cpuapp`: " + lc("ring_inbox.logic", after=s_tb) + ", " + lc("ring_time.logic", after=s_tb) + ", " + lc("ring_iphone.logic", after=s_tb) + ". "
  "Broken copies of the logic suites (the named case must fail on each board; stages `broken-inbox`, `broken-time`, `broken-iphone`): "
  + lc("native_sim: the named case failed, as required", after=s_bin) + " and " + lc("nrf54lm20bsim/nrf54lm20a/cpuapp: the named case failed, as required", after=s_bin) + " (inbox); "
  + lc("native_sim: the named case failed, as required", after=s_btm) + " and " + lc("nrf54lm20bsim/nrf54lm20a/cpuapp: the named case failed, as required", after=s_btm) + " (time); "
  + lc("native_sim: the named case failed, as required", after=s_bip) + " and " + lc("nrf54lm20bsim/nrf54lm20a/cpuapp: the named case failed, as required", after=s_bip) + " (iPhone logic). "
  "Bluetooth: scenarios N, R, P, L, D, Z and W have " + str(nb) + " broken copies in stage `bsim-iphone-broken` (listed in section 1, a to i; the run counts one only when both devices ran to their RESULT line, the ring finished before the stand-in evaluated, and the exact named check line says FAIL: `tests/bsim/iphone/run.sh`, " + S("tests/bsim/iphone/run.sh", "named check, as required") + "); each one's diff is in `tests/bsim/iphone/broken_edit.py` and in the log. "
  "The stage's own result: " + f"`LOG:{max(i + 1 for i, l in enumerate(log) if l == 'RESULT PASS' and i + 1 < L('=== stage bsim-iphone-broken end'))}`" + ".")

w("")
ends = [(l.split()[2], l.split()[-1]) for l in log if l.startswith("=== stage") and " end " in l]
bad = [n for n, c in ends if c != "0"]
_d = L("=== stage dk start")
_fi = next(i for i in range(_d, len(log)) if "FLASH:" in log[i] and "974704 B" in log[i])  # the application image (not MCUboot)
fl, ra = log[_fi], log[_fi + 1]
mf = re.search(r"FLASH:\s+(\d+) B\s+(\d+) B\s+([\d.]+)%", fl)
mr = re.search(r"RAM:\s+(\d+) B\s+(\d+ \w+)\s+([\d.]+)%", ra)
fr = (f"FLASH {int(mf.group(1)):,} B of {int(mf.group(2)):,} B ({mf.group(3)}%), `LOG:{_fi + 1}`; RAM {int(mr.group(1)):,} B of {mr.group(2)} ({mr.group(3)}%), `LOG:{_fi + 2}`")
w("**k. `sh firmware/tools/remote.sh os-iphone \"tools/build_all.sh\"` ends with the last line RESULT PASS, every step 1 and step 2 stage still passing, flash and RAM use in the log: yes.** "
  "The last build_all line is " + f"`LOG:{max(i + 1 for i, l in enumerate(log) if l == 'RESULT PASS')}`" + "; " + str(len(ends)) + " stages ended, " + str(len(bad)) + " with a non-zero exit"
  + (" (" + ", ".join(bad) + ")" if bad else "") + ". The step 1 and step 2 stages are `dk`, `bsim-build`, `bsim-run`, `tests-native_sim`, `tests-nrf54lm20bsim_nrf54lm20a_cpuapp`, `bsim-control`, `bsim-control-broken`, `broken-control`, `broken-devices`; their end lines: "
  + ", ".join(f"{n} {lc('=== stage ' + n + ' end')}" for n in ["dk", "bsim-build", "bsim-run", "tests-native_sim", "tests-nrf54lm20bsim_nrf54lm20a_cpuapp", "bsim-control", "bsim-control-broken", "broken-control", "broken-devices"]) + ". "
  "Kit build for `nrf54lm20dk/nrf54lm20a/cpuapp` (the application with MCUboot, sysbuild): " + fr + " (application image); step 2's figure was FLASH 168,592 B (`docs/step2-round3.md`).")

w("")
def cnt(s):
    return re.search(r"\((\d+) checks passed\)", log[L("TEST " + s + " RESULT PASS", after=s_iph) - 1]).group(1)


w("Scenario results (both devices' checks counted): N " + cnt("N") + " checks passed " + lc("TEST N RESULT PASS", after=s_iph) + ", R " + cnt("R") + " " + lc("TEST R RESULT PASS", after=s_iph) + ", P " + cnt("P") + " " + lc("TEST P RESULT PASS", after=s_iph) + ", L " + cnt("L") + " " + lc("TEST L RESULT PASS", after=s_iph) + ", D " + cnt("D") + " " + lc("TEST D RESULT PASS", after=s_iph) + ".")
print("\n".join(out))
