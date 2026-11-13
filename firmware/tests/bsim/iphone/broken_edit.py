"""Broken copies for the iPhone tests (run.sh --broken).

Usage: python3 broken_edit.py <variant> <modules folder> <work folder>

Copies the one module the variant breaks into <work folder>/<module>, makes ONE named fault in the copy (the real
files are not touched), saves the diff, and prints for run.sh:
  MODULE=<ring_iphone|ring_inbox|ring_time>   the module that was copied (CMake variable RING_<X>_DIR)
  SCEN=<N|R|P>                                the test that must catch the fault
  EXPECT=<regex>                              the exact check line that must say FAIL
Exits 1 when an edit did not match exactly once.
"""

import difflib
import pathlib
import shutil
import sys

I = "src/rip.c"
VARIANTS = {
    # name: (module, scenario, expected FAIL line, [(file, old, new), ...])
    "inbox_size": (
        "ring_inbox", "N",
        r"RING CHECK b: thirteen more arrive: the store holds 16 FAIL",
        [("include/ring_inbox/rinbox.h", "#define RINBOX_MAX      16", "#define RINBOX_MAX      17")],
    ),
    "utf8_cut": (
        "ring_inbox", "N",
        r"RING CHECK a: 103 exact: identifier cut at 48 bytes, title at 48, the 200-byte message cut to 159 bytes on a character FAIL",
        [("src/rinbox.c", "\tif (n < len) {\n\t\twhile (n > 0 && is_cont(p[n])) {",
          "\tif (false) {\n\t\twhile (n > 0 && is_cont(p[n])) {"),
         ("src/rinbox.c", "\t\tif (seq_len(p[k]) > 1 && k + seq_len(p[k]) > n) {", "\t\tif (false) {")],
    ),
    "remove_ignored": (
        "ring_iphone", "N",
        r"RING CHECK b: the removal deletes the entry FAIL",
        [(I, "\t\t\t(void)rinbox_remove(&inbox, n->notif_uid);\n", "\t\t\t;\n")],
    ),
    "modify_ignored": (
        "ring_iphone", "N",
        r"RING CHECK b: the change arrived FAIL",
        [(I, "\t\t\t\tst.ns_modified++;\n\t\t\t\tfetch = true;\n", "\t\t\t\tst.ns_modified++;\n")],
    ),
    "action_flag": (
        "ring_iphone", "N",
        r"RING CHECK c: an action without its flag is refused: dismiss of 104 \(no actions\) FAIL",
        [(I, "\tif ((rinbox_get(&inbox, (uint8_t)at)->flags & need) == 0) {", "\tif (false) {")],
    ),
    "action_id": (
        "ring_iphone", "N",
        r"PHONE CHECK two actions arrived: negative for 122, positive for 121, and no other FAIL",
        [(I, "action == RIP_ACTION_POSITIVE ? BT_ANCS_ACTION_ID_POSITIVE\n\t\t\t\t\t\t\t\t\t: BT_ANCS_ACTION_ID_NEGATIVE,",
          "action == RIP_ACTION_POSITIVE ? BT_ANCS_ACTION_ID_NEGATIVE\n\t\t\t\t\t\t\t\t\t: BT_ANCS_ACTION_ID_POSITIVE,")],
    ),
    "reset_on_drop": (
        "ring_iphone", "R",
        r"RING CHECK d: the inbox is empty when the link has ended FAIL",
        [(I, "\trinbox_clear(&inbox);\n\tfq_clear();\n}\n\n/* ----", "\tfq_clear();\n}\n\n/* ----")],
    ),
    "sc_ignored": (
        "ring_iphone", "R",
        r"RING CHECK e: the ring stops when the service goes away FAIL",
        [(I, "\t\tsc_pending = true;\n", "\t\tsc_pending = false;\n")],
    ),
    "media_local": (
        "ring_iphone", "N",
        r"RING CHECK f: the stored state did not change on the commands alone \(pause was sent, the state is still playing\) FAIL",
        [(I, "\tif (err == 0) {\n\t\tst.media_sent++;\n",
          "\tif (err == 0) {\n\t\tst.media_sent++;\n\t\tif (cmd == RIP_MEDIA_PAUSE) {\n\t\t\tmedia.state = RIPL_PLAYER_PAUSED;\n\t\t}\n")],
    ),
    "time_ignored": (
        "ring_iphone", "N",
        r"RING CHECK g: the ring's clock follows the iPhone's time change \(two hours\) FAIL",
        [(I, "\tcts_apply(t, k_uptime_get());\n\tlti_refresh();\n}", "\tARG_UNUSED(t);\n}")],
    ),
    "core_touch": (
        "ring_iphone", "N",
        r"RING CHECK i: the core is still RECORDING, no recording started or stopped, no key sent FAIL",
        [(I, "\tif (ripl_cts_to_ms(e->year,",
          "\t{\n\t\textern void bsim_fault_hook(void);\n\n\t\tbsim_fault_hook();\n\t}\n\tif (ripl_cts_to_ms(e->year,")],
    ),
    "request_len": (
        "ring_iphone", "N",
        r"PHONE CHECK every Get Notification Attributes request is the 13 bytes Apple's format and the kit's encoder give FAIL",
        [("include/ring_iphone/ripl.h", "#define RIPL_REQ_MESSAGE_MAX       160", "#define RIPL_REQ_MESSAGE_MAX       120")],
    ),
    "service_error": (
        "ring_iphone", "P",
        r"RING CHECK h: Service Changed was looked for and found \(the host has the GATT service\), the three Apple services were looked for and not found \(not an error\) FAIL",
        [(I, "\t} else if (p == P_ANCS) {\n\t\tst.ancs_missing++;", "\t} else if (p == P_ANCS) {\n\t\tst.ancs_missing++;\n\t\tst.dm_errors++;")],
    ),
    # ---- round 2 ----
    "late_fragment": (
        "ring_iphone", "L",
        r"RING CHECK L: the four notifications all get their text, although the answer for the first is late FAIL",
        # the round 1 behaviour restored: a stream that is not the answer to this request is an error that abandons the
        # request, and a failed request is not asked for again
        [("src/ripl.c", "\t\t\t} else {\n\t\t\t\td->skipped++;\n\t\t\t}", "\t\t\t} else {\n\t\t\t\td->state = DS_ERR;\n\t\t\t}"),
         ("src/ripl.c", "\t\t\t\t\t(void)ripl_ds_feed(d, again, 4);", "\t\t\t\t\td->state = DS_ERR;"),
         (I, "\tif (cur_try == 0 && !fq_has(cur_uid)", "\tif (false && !fq_has(cur_uid)")],
    ),
    "action_sent": (
        "ring_iphone", "N",
        r"PHONE CHECK no action command arrived for a notification that does not have that action \(every command is recorded before it can be refused\) FAIL",
        # the command is sent, and "not supported" is still returned
        [(I, "\t\tst.actions_refused++;\n\t\tk_mutex_unlock(&lk);\n\t\treturn -ENOTSUP;",
          "\t\tst.actions_refused++;\n\t\tk_mutex_unlock(&lk);\n\t\t(void)bt_ancs_notification_action(&ancs_c, uid,\n\t\t\t\t\t\t  action == RIP_ACTION_POSITIVE ? BT_ANCS_ACTION_ID_POSITIVE\n\t\t\t\t\t\t\t\t\t\t: BT_ANCS_ACTION_ID_NEGATIVE,\n\t\t\t\t\t\t  action_write_cb);\n\t\treturn -ENOTSUP;")],
    ),
    "zone_ignored": (
        "ring_iphone", "N",
        r"RING CHECK the ring's clock equals the iPhone's time within 1 s, as UTC \(the iPhone's zone \+2 h taken off\) FAIL",
        [("src/ripl.c", "c->local_ms - (int64_t)c->zone_min * 60000, c->zone_min, true);", "c->local_ms, c->zone_min, true);")],
    ),
    "zone_assumed": (
        "ring_iphone", "R",
        r"RING CHECK R: the iPhone gave no zone: the clock holds its local time and says the zone is not known FAIL",
        [("src/ripl.c", "\tc->zone_known = known;\n", "\tc->zone_known = true;\n")],
    ),
    "media_local_play": (
        "ring_iphone", "N",
        r"RING CHECK f: the stored state did not change on a play command either \(paused stays paused\) FAIL",
        [(I, "\tif (err == 0) {\n\t\tst.media_sent++;\n",
          "\tif (err == 0) {\n\t\tst.media_sent++;\n\t\tif (cmd == RIP_MEDIA_PLAY) {\n\t\t\tmedia.state = RIPL_PLAYER_PLAYING;\n\t\t}\n")],
    ),
    # ---- round 3 ----
    "late_parser": (
        "ring_iphone", "L",
        r"RING CHECK L: the four notifications all get their text, although the answer for the first is late FAIL",
        # the retry is KEPT; the round 1 parser is restored: bytes that are not the answer in flight are an error
        [("src/ripl.c", "\t\t\t} else {\n\t\t\t\td->skipped++;\n\t\t\t}", "\t\t\t} else {\n\t\t\t\td->state = DS_ERR;\n\t\t\t}"),
         ("src/ripl.c", "\t\t\t\t\t(void)ripl_ds_feed(d, again, 4);", "\t\t\t\t\td->state = DS_ERR;")],
    ),
    "zone_read_failed": (
        "ring_iphone", "N",
        r"RING CHECK g: a zone read that failed changed nothing: the clock is still UTC \(\+2 h taken off\) and the zone known FAIL",
        # a failed zone read is taken as "the iPhone gave no zone"
        [(I, "ripl_clock_zone(&clk, ok, known, m, k_uptime_get());", "ripl_clock_zone(&clk, true, known, m, k_uptime_get());")],
    ),
    "dm_gone": (
        "ring_iphone", "D",
        r"RING CHECK D: no service was reported missing \(the answer of the ended session's discovery was not counted\) FAIL",
        # the "link gone" test of the discovery answer is removed
        [(I, "\tbool gone = (link == NULL) || (bt_conn_get_info(link, &info) != 0) || (info.state != BT_CONN_STATE_CONNECTED);",
          "\tbool gone = false;\n\t(void)link;\n\t(void)info;")],
    ),
    "zone_not_reread": (
        "ring_iphone", "Z",
        r"RING CHECK Z: the zone changed to \+180 minutes while linked and the local time moved by 2 h: the clock still shows the same UTC \(within 100 ms\) and the new zone FAIL",
        # the zone is not read again after a Current Time notification
        [(I, "\tcts_apply(t, k_uptime_get());\n\tlti_refresh();\n}", "\tcts_apply(t, k_uptime_get());\n}")],
    ),
    "no_lti_known": (
        "ring_iphone", "W",
        r"RING CHECK W: no Local Time Information: the clock holds the iPhone's local time \(within 100 ms\) and says the zone is not known FAIL",
        # a link without Local Time Information is taken as "zone known, offset 0"
        [(I, "\t\tripl_clock_init(&clk);\n\t\tlti_busy = false;", "\t\tripl_clock_init(&clk);\n\t\tripl_clock_zone(&clk, true, true, 0, 0);\n\t\tlti_busy = false;")],
    ),
}


def main():
    variant, modules, work = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
    if variant not in VARIANTS:
        print("unknown variant", variant, "known:", " ".join(VARIANTS), file=sys.stderr)
        return 2
    module, scen, expect, edits = VARIANTS[variant]
    dst = work / module
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(modules / module, dst)
    diff = []
    for rel, old, new in edits:
        f = dst / rel
        text = f.read_text()
        if text.count(old) != 1:
            print(f"edit of {rel} did not match exactly once ({text.count(old)} matches)", file=sys.stderr)
            return 1
        f.write_text(text.replace(old, new))
        diff += difflib.unified_diff((modules / module / rel).read_text().splitlines(), f.read_text().splitlines(),
                                     f"a/{module}/{rel}", f"b/{module}/{rel}", lineterm="")
    (work / "broken.diff").write_text("\n".join(diff) + "\n")
    print("\n".join(diff), file=sys.stderr)
    print(f"MODULE={module}")
    print(f"SCEN={scen}")
    print(f"EXPECT={expect}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
