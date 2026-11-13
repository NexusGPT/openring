#!/usr/bin/env python3
"""broken_edit.py <variant> <modules dir> <out dir>: copy modules/ring_screens to <out dir>/ring_screens and make ONE named fault.

Prints MODULE=, EXPECT= (a regular expression that the one check line of the variant must match: the line says FAIL).
The real files are not touched. An edit that does not match exactly once is an error."""
import pathlib
import shutil
import sys

variant, mods, out = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
dst = out / "ring_screens"
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(mods / "ring_screens", dst)

EDITS = {
    # a dismiss chosen on the screen sends the positive action instead of the negative one
    "dismiss_positive": ("src/rscr_real.c", "return rip_dismiss(uid);", "return rip_action(uid, RIP_ACTION_POSITIVE);",
                         r"PHONE CHECK the dismiss chosen on the ring's screen arrived.* FAIL"),
    # Right on the notification list does not open the detail
    "no_detail": ("src/rscr_logic.c", "\t\t} else if (v->inbox_n > 0) {\n\t\t\tclamp_sel(&s->notif_sel, v->inbox_n);\n\t\t\topen_notif(s, v, s->notif_sel, now, fx);",
                  "\t\t} else if (false) {\n\t\t\tclamp_sel(&s->notif_sel, v->inbox_n);\n\t\t\topen_notif(s, v, s->notif_sel, now, fx);",
                  r"RING CHECK S: Right opens the notification detail.* FAIL"),
    # the passkey digits are not drawn
    "passkey_not_drawn": ("src/rscr_draw.c", "\tif (f->s.pair_has_key) {", "\tif (false) {",
                          r"RING CHECK S: the frame with the digits differs from the pairing frame without them.* FAIL"),
}
if variant not in EDITS:
    print("unknown variant", variant, file=sys.stderr)
    sys.exit(2)
rel, old, new, expect = EDITS[variant]
f = dst / rel
s = f.read_text()
if s.count(old) != 1:
    print("the edit did not match exactly once:", s.count(old), variant, file=sys.stderr)
    sys.exit(1)
f.write_text(s.replace(old, new))
print("MODULE=ring_screens")
print("EXPECT=" + expect)
print("edited", rel, file=sys.stderr)
