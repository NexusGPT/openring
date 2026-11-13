#!/usr/bin/env python3
"""broken_edit.py <variant> <modules dir> <out dir>: copy the modules a variant breaks to <out dir>/<module> and make the named
fault in the copy (the real files are not touched).

Prints MODULE= (the copied modules), SCEN= (H or I), EXPECT= (a regular expression that the one check line of the variant must
match: the line says FAIL). An edit that does not match exactly once is an error."""
import pathlib
import shutil
import sys

RIP = ("ring_iphone", "src/rip.c")
BT = ("ring_relay", "src/rrl_bt.c")
RRL = ("ring_relay", "src/rrl.c")
INB = ("ring_inbox", "src/rinbox.c")

EDITS = {
    # a relay frame reaches the core: the frame drives the joystick path while a recording runs
    "relay_reaches_core": ("H", [(BT, "\tst.writes++;\n\tapple = (rip_src_of(conn) == RIP_SRC_APPLE);",
        "\tst.writes++;\n\t{\n\t\textern void bsim_fault_hook(void);\n\n\t\tbsim_fault_hook();\n\t}\n\tapple = (rip_src_of(conn) == RIP_SRC_APPLE);")],
        r"RING CHECK H: the core is still RECORDING, no recording started or stopped by the relay frames.* FAIL"),
    # code 7 is not enforced on a link whose notifications come from Apple's service
    "code7_not_enforced": ("I", [(RRL, "\tif (apple) {", "\tif (false) {")],
        r"HELPER CHECK I: PUT on an iPhone's link: refused with ATT error 0x80 and ERROR code 7, id 302.* FAIL"),
    # an action is sent without its flag
    "action_without_flag": ("H", [(RIP, "\tif ((rinbox_get(&inbox, (uint8_t)at)->flags & need) == 0) {", "\tif (false) {")],
        r"HELPER CHECK H: no ACTION frame arrived for an action 1004 does not have.* FAIL"),
    # the store is not emptied at the end of the link: the link's source does not end with the link (both places where it ends)
    "store_not_emptied_at_link_end": ("H", [
        (RIP, "\tif (conn == src_conn) {", "\tif (false) {"),
        (RIP, "\tif (c != NULL && src_conn == c) {", "\tif (false) {")],
        r"RING CHECK H: the link dropped: the store is empty.* FAIL"),
    # REMOVE is ignored
    "remove_ignored": ("H", [(RIP, "\t\t(void)rinbox_remove(&inbox, uid);\n\t\tst.relay_removes++;", "\t\t(void)uid;\n\t\tst.relay_removes++;")],
        r"RING CHECK H: REMOVE arrived: 1002 left the store.* FAIL"),
    # a PUT is stored before its last piece
    "put_early": ("H", [(RRL, "\t\tif (s->got == s->total) {", "\t\tif (s->got * 2 >= s->total) {")],
        r"HELPER CHECK H: PUT 1001 \(59 bytes in 6 frames of at most 20 bytes\) accepted.* FAIL"),
    # a refused frame still changes the store: a malformed PUT removes the held entry of its id
    "refused_changes_store": ("H", [(RRL, "\t\t\t\tdrop_record(s);\n\t\t\t\trefuse(r, RRL_E_RECORD, id);\n\t\t\t\tbreak;",
        "\t\t\t\tdrop_record(s);\n\t\t\t\trefuse(r, RRL_E_RECORD, id);\n\t\t\t\tr->act = RRL_ACT_REMOVE;\n\t\t\t\tbreak;")],
        r"HELPER CHECK H: M20 flag bit 7 set: refused with ATT error 0x80 and ERROR code 5, id 2003.* FAIL"),
    # the Bluetooth part does not ask for security level 4 (no authenticated permission, no check in the handler)
    "no_security_check": ("H", [
        (BT, "BT_GATT_CHRC_WRITE, BT_GATT_PERM_WRITE_AUTHEN, NULL, in_write, NULL)", "BT_GATT_CHRC_WRITE, BT_GATT_PERM_WRITE, NULL, in_write, NULL)"),
        (BT, "\tARG_UNUSED(attr);\n\tif (bt_conn_get_security(conn) < BT_SECURITY_L4) {", "\tARG_UNUSED(attr);\n\tif (bt_conn_get_security(conn) < BT_SECURITY_L1) {")],
        r"HELPER CHECK H: a write to In before security level 4 fails.* FAIL"),
    # the action byte of ACTION is always 0
    "action_id": ("H", [(RRL, "\to[5] = action;", "\to[5] = 0;")],
        r"HELPER CHECK H: ACTION arrived: id 1002, negative \(1\).* FAIL"),
    # HELLO does not empty what the relay stored
    "hello_keeps_store": ("H", [(RIP, "\t\trinbox_clear(&inbox); /* HELLO empties what the relay stored (and nothing else is in the store on this link) */",
        "\t\t/* HELLO empties nothing */")],
        r"RING CHECK H: the store holds 2003, 2002, 2001 \(HELLO emptied what was there\).* FAIL"),
    # ERROR is never notified
    "error_not_notified": ("H", [(BT, "\t\t(void)q_push_locked(o, rrl_out_error(o, res.err, res.id), true);", "\t\t(void)o;")],
        r"HELPER CHECK H: PUT before HELLO: refused with ATT error 0x80 and ERROR code 2, id 1900.* FAIL"),
    # the link's source is not fixed by the first user: Apple's service found after a relay HELLO takes over the link
    "source_not_fixed": ("B", [(RIP, "\t\tblocked = (src == RIP_SRC_RELAY && src_conn == ancs_c.conn);", "\t\tblocked = false;")],
        r"RING CHECK B: Apple's notification service was found on the relay's link and was not used.* FAIL"),
    # a refused frame (ATT error 0x80 and ERROR) still changes the store: the error path removes the entry of the frame's id
    "refused_frame_changes_store": ("H", [(BT, "\tif (res.act == RRL_ACT_ERROR) {\n\t\tst.refused++;", "\tif (res.act == RRL_ACT_ERROR) {\n\t\t(void)rip_relay_remove(conn, res.id);\n\t\tst.refused++;")],
        r"RING CHECK H: the malformed frames changed nothing.* FAIL"),
    # Service Changed on a relay link empties the relay's entries
    "sc_clears_relay_entries": ("B", [(RIP, "\tif (src == RIP_SRC_RELAY) {\n\t\t/* the relay's entries belong", "\tif (false) {\n\t\t/* the relay's entries belong")],
        r"RING CHECK B: Service Changed was indicated and the ring still holds the relay's entries.* FAIL"),
    # an accepted HELLO does not drop the frames that wait for Out
    "hello_keeps_queue": ("Q", [(BT, "\t\t\tout_reset_locked();\n\t\t\t(void)q_push_locked(o, rrl_out_ready(o), true);", "\t\t\t(void)q_push_locked(o, rrl_out_ready(o), true);")],
        r"HELPER CHECK Q: after the second HELLO the first frame on Out is READY.* FAIL"),
    # an action whose frame cannot be queued is counted as sent
    "action_counted_when_queue_full": ("Q", [(BT, "\t\tst.actions_refused++;\n\t\tr = -EBUSY;", "\t\tst.actions_sent++;\n\t\tr = 0;")],
        r"RING CHECK Q: with the Out queue full an action is refused on the ring.* FAIL"),
    # the session start after a relay HELLO empties the relay's entries (the guard of ready_fn removed)
    "session_start_clears_relay": ("B", [(RIP, "\tif (!(src == RIP_SRC_RELAY && src_conn == c)) {", "\tif (true) {")],
        r"RING CHECK B: the session start after a relay HELLO kept the entries.* FAIL"),
    # a relay frame turns the screen on while it is off
    "relay_wakes_screen": ("H", [(BT, "\tst.writes++;\n\tapple = (rip_src_of(conn) == RIP_SRC_APPLE);",
        "\tst.writes++;\n\t{\n\t\textern void bsim_wake_hook(void);\n\n\t\tbsim_wake_hook();\n\t}\n\tapple = (rip_src_of(conn) == RIP_SRC_APPLE);")],
        r"RING CHECK H: relay frames \(CLEAR, PUT\) did not wake the screen: it is still off and the panel is blanked.* FAIL"),
    # a replace moves the entry to the front and loses its read mark
    "replace_moves_front": ("H", [(INB, "\t\t(void)rinbox_modify(b, uid, category, flags);", "\t\tdropped_one = rinbox_add(b, uid, category, flags, dropped);")],
        r"RING CHECK H: the replace of 1002 arrives \(new category, flags and text\).* FAIL"),
}

variant, mods, out = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
if variant not in EDITS:
    print("unknown variant", variant, file=sys.stderr)
    sys.exit(2)
scen, edits, expect = EDITS[variant]
copied = []
for (module, rel), old, new in edits:
    dst = out / module
    if module not in copied:
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(mods / module, dst)
        copied.append(module)
    f = dst / rel
    s = f.read_text()
    if s.count(old) != 1:
        print("the edit did not match exactly once:", s.count(old), variant, rel, file=sys.stderr)
        sys.exit(1)
    f.write_text(s.replace(old, new))
    print("edited", module, rel, file=sys.stderr)
print("MODULE=" + " ".join(copied))
print("SCEN=" + scen)
print("EXPECT=" + expect)
