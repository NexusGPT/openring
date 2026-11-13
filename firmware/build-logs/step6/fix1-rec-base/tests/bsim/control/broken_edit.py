"""Broken copies for the two-device tests (run.sh --broken).

Usage: python3 broken_edit.py <variant> <modules folder> <work folder>

Copies the one module the variant breaks into <work folder>/<module>, makes ONE named fault in the
copy (the real files are not touched), saves the diff, and prints three lines for run.sh:
  MODULE=<ring_control|ring_devices>   the module that was copied (CMake variable RING_<X>_DIR)
  SCEN=<A|B|C|D|F|G|T>                 the test that must catch the fault
  EXPECT=<regex>                       the exact check line that must say FAIL (KIND=fail), or
                                       the check lines that must still say PASS, joined by ';;' (KIND=pass)
  KIND=<fail|pass>
Exits 1 when an edit changed nothing.
"""

import difflib
import pathlib
import shutil
import sys

VARIANTS = {
    # name: (module, scenario, expected FAIL line, [(file, old, new), ...])
    "keymap": (
        "ring_control", "A",
        r"HOST H1 CHECK presenter\.right next slide \(Right Arrow\) FAIL",
        [("include/ring_control/rctl_modes.h",
          "[RCTL_RIGHT]  = RCTL_E_KEY(RCTL_K_RIGHT_ARROW),",
          "[RCTL_RIGHT]  = RCTL_E_KEY(RCTL_K_LEFT_ARROW),")],
    ),
    "hold_key": (
        "ring_control", "D",
        r"RING CHECK media: centre hold sends no report FAIL",
        [("src/rctl_logic.c",
          "\tcase RC_ACT_SCREEN_CENTRE:\n\t\t*out = RCTL_CENTRE;",
          "\tcase RC_ACT_OPEN:\n\tcase RC_ACT_SCREEN_CENTRE:\n\t\t*out = RCTL_CENTRE;")],
    ),
    "switch_gate": (
        "ring_devices", "B",
        r"RING CHECK key in the switch window is not sent FAIL",
        [("src/rdev_logic.c",
          "return secure && link_slot != RDEV_NONE && link_slot == active;",
          "return secure && link_slot != RDEV_NONE;")],
    ),
    "window": (
        "ring_devices", "F",
        r"HOST H2 CHECK pairing outside the window is refused FAIL",
        [("src/rdev.c",
          "ok = window && conn == cur_conn && link_slot == window_slot;",
          "ok = true;"),
         ("src/rdev.c",
          "if (!(window && window_slot == link_slot)) {",
          "if (false) {")],
    ),
    "host_write": (
        "ring_control", "D",
        r"RING CHECK host writes start no recording FAIL",
        [("src/rctl.c",
          "\tstats.host_writes++;\n",
          "\tstats.host_writes++;\n\t{\n\t\textern void bsim_fault_hook(void);\n\n\t\tbsim_fault_hook();\n\t}\n")],
    ),
    "repeat_flood": (
        "ring_control", "A",
        r"HOST H1 CHECK pointer held right repeats \(at most 8 reports\) FAIL",
        [("src/rctl.c",
          "\tint sent = 0;\n\n\tif (n == 0) {\n\t\treturn 0;\n\t}\n",
          "\tint sent = 0;\n\tstatic int64_t last_move;\n\n\tif (n == 1 && r[0].index == RCTL_IDX_POINTER &&\n"
          "\t    k_uptime_get() - last_move < 400) {\n\t\t/* a flood: a repeated move is sent three times */\n"
          "\t\t(void)bt_hids_inp_rep_send(&hids_obj, conn, r[0].index, r[0].data, r[0].len, NULL);\n"
          "\t\t(void)bt_hids_inp_rep_send(&hids_obj, conn, r[0].index, r[0].data, r[0].len, NULL);\n\t}\n"
          "\tif (n == 1) {\n\t\tlast_move = k_uptime_get();\n\t}\n\tif (n == 0) {\n\t\treturn 0;\n\t}\n")],
    ),
    "gate": (
        "ring_control", "A",
        r"RING CHECK control inactive: direction sends no report FAIL",
        [("src/rctl_logic.c",
          "\tif (!control_active) {\n\t\treturn false;\n\t}\n",
          ""),
         ("src/rctl.c",
          "\tif (!active) {\n\t\tk_mutex_unlock(&send_lock);\n\t\treturn -EPERM;\n\t}\n",
          "")],
    ),
    "release_retry": (
        "ring_control", "D",
        r"RING CHECK failed release is sent later FAIL",
        [("src/rctl.c",
          "\t\t\tif (i > 0) {\n\t\t\t\t/* the press went out",
          "\t\t\tif (false) {\n\t\t\t\t/* the press went out")],
    ),
}


# Single-edit copies of the window fault: each layer alone must still hold, so the run must PASS
# these checks (EXPECT lists them, separated by ";;"). KIND=pass.
PASS_CHECKS = (r"HOST H2 CHECK pairing outside the window is refused PASS;;"
               r"RING CHECK no new pairing outside the window \(one bond\) PASS;;"
               r"RING CHECK still one bond PASS;;"
               r"HOST H1 CHECK after host 2 tried media.centre PASS;;"
               r"HOST H2 CHECK no stranger link lasts longer than 1 s PASS")
VARIANTS["window_gate_only"] = (
    "ring_devices", "F", PASS_CHECKS,
    [("src/rdev.c", "ok = window && conn == cur_conn && link_slot == window_slot;", "ok = true;")])
VARIANTS["window_stranger_only"] = (
    "ring_devices", "F", PASS_CHECKS,
    [("src/rdev.c", "if (!(window && window_slot == link_slot)) {", "if (false) {")])
VARIANTS["bond_kept"] = (
    "ring_devices", "C", r"RING CHECK bond deleted FAIL",
    [("src/rdev.c", "err = bt_unpair(slot, &peer);", "err = 0;")])
VARIANTS["wrong_link"] = (
    "ring_control", "T", r"HOST H1 CHECK no other report received FAIL",
    [("src/rctl.c", "return bt_hids_inp_rep_send(&hids_obj, conn, r->index, r->data, r->len, NULL);",
      "return bt_hids_inp_rep_send(&hids_obj, NULL, r->index, r->data, r->len, NULL);")])
VARIANTS["fourth_slot"] = (
    "ring_devices", "G", r"RING CHECK G: fourth pairing refused \(-ENOSPC\) FAIL",
    [("src/rdev_logic.c", "return s == RDEV_NONE ? -ENOSPC : (int)s;", "return s == RDEV_NONE ? 0 : (int)s;")])
VARIANTS["pair_takes_over"] = (
    "ring_devices", "B", r"RING CHECK B: after the second pairing the first device is still the active one.* FAIL",
    [("src/rdev.c", "\t\t\tif (list.active == RDEV_NONE) {\n\t\t\t\tlist.active = slot;", "\t\t\tif (true) {\n\t\t\t\tlist.active = slot;")])
MUST_PASS = ("window_gate_only", "window_stranger_only")


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
    print(f"KIND={'pass' if variant in MUST_PASS else 'fail'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
