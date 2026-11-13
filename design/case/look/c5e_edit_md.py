"""C5e (review 3, H03 H04 H16): text edits of case-architecture.md and case-notes.md; each replacement must match exactly once."""
import os
CASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def sub(fn, pairs):
    p = os.path.join(CASE, fn); t = open(p).read()
    for a, b in pairs:
        assert t.count(a) == 1, (fn, t.count(a), a[:60])
        t = t.replace(a, b)
    open(p, "w").write(t)
ROLL = ("US 7: +0.75 / -0.75 degrees, pad row at most 0.113 mm; US 8: +0.75 / -0.75, 0.119 mm; US 9: +0.75 / -0.75, 0.124 mm; US 10: +0.75 / -0.75, 0.129 mm; "
        "US 11: +0.75 / -0.75, 0.135 mm; US 12: +0.50 / -0.50, 0.093 mm; US 13: +0.25 / -0.25, 0.048 mm; limit 0.50 mm (a 0.6 mm pin tip stays on a 1.6 mm pad), every size OK")
sub("case-architecture.md", [
 ("Check: look/c5d_check_final.log.", "Check: look/c5d_check_lead_rerun.log (last line: \"case_check: PASS, 3447 pairs checked, 0 failures\")."),
 ("the case is 45.5 x 45.9 x 41.4 mm (C4:", "the case was 45.5 x 45.9 x 41.4 mm at C5b (since C5d: 45.4 x 45.9 x 41.4 mm, out/case_size.txt) (C4:"),
 ("| 45.5 x 45.9 x 41.4 mm (out/case_size.txt): +2.3, +1.9, +0.8 mm;", "| 45.4 x 45.9 x 41.4 mm (out/case_size.txt): +2.2, +1.9, +0.8 mm;"),
 ("| unchanged: Harwin P70-6000045R, proposed, not confirmed (K1);", "| the fitted pin is the Harwin P70-6000045R (proposed, stroke not confirmed, K1; the Mill-Max 0981 does not fit the pin holder's 1.60 mm bores);"),
 ("4 spring pins P1-P4 (Harwin P70-6000045R, not confirmed) on pin board", "4 spring pins P1-P4 (Harwin P70-6000045R, stroke not confirmed) on pin board"),
 ("| Harwin P70-6000045R (proposed, NOT confirmed: conflict K1) | barrel 1.5 mm, free height 2.80 mm, working height 2.10 mm; stroke unknown (not in the page read); the contact window 2.15 to 2.65 mm is my assumption | LIST |",
  "| Harwin P70-6000045R (the fitted pin; proposed, stroke NOT confirmed: conflict K1; the Mill-Max 0981 does not fit the pin holder and is history only, case-bom.csv reference PA1-PA4 quantity 0) | barrel 1.5 mm in the holder's four 1.60 mm bores, free height 2.80 mm, working height 2.10 mm; to confirm with Harwin: the stroke (at least 0.34 mm needed), the force curve over 2.10 to 2.65 mm and the life, none of which is in the files read; the contact window 2.15 to 2.65 mm is my assumption | LIST |"),
 ("(the power chip's 32 mA minimum is above 1 C for this cell)", "(CHARGE_CURRENT = 15 mA, 1 C of the smallest cell, from `design/architecture.md` 17.13 line 567; the nPM1304 sets 4 to 100 mA, so the 32 mA minimum of the old nPM1300 no longer applies)"),
 ("(Harwin P70 pin of conflict K1, working height 2.10 mm)", "(Harwin P70-6000045R, working height 2.10 mm)"),
 ("`look/check_final.log` (last line: \"case_check: PASS, 1842 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]\")",
  "`look/c5d_check_lead_rerun.log` (last line: \"case_check: PASS, 3447 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]\")"),
 ("**Outer size, closed** (out/case_size.txt): 45.5 x 45.9 x 41.4 mm, against 43.2 x 44.0 x 40.6 mm in C4 (+2.3, +1.9, +0.8 mm).", "**Outer size, closed** (out/case_size.txt): 45.4 x 45.9 x 41.4 mm, against 43.2 x 44.0 x 40.6 mm in C4 (+2.2, +1.9, +0.8 mm)."),
 ("**Roll (open item R1).**", "**Roll (R1, held since C5d).**"),
 ("the pad row then moves at most 0.680 mm, against 0.2 mm that a 0.6 mm pin tip can take on a 1.0 mm pad before it leaves the pad. So the roll is NOT held to the pad's tolerance: the check proves the nominal pose, not the roll tolerance. A nub channel (two walls along the joystick nub's path, as in C3) or a ring-side feature is needed; not designed. Conflict R1 in case-notes.md.",
  "the pad row then moves at most 0.135 mm (US 11) against 0.50 mm that a 0.6 mm pin tip can take on a 1.6 mm pad before it leaves the pad: OK. Current figures, look/c5d_check_lead_rerun.log: " + ROLL + ". State before C5d (C5b/C5c, kept as history only): the pad row moved at most 0.680 mm against 0.2 mm on a 1.0 mm pad, and the roll was not held; the real ring files, the 1.6 mm pad and the wider limit changed that. Not proven: the roll with the real moulded tolerances; the check proves the modelled play."),
])
sub("case-notes.md", [
 ("limit 0.50).", "limit 0.50; look/c5d_check_lead_rerun.log, US 7 to 13: 0.113, 0.119, 0.124, 0.129, 0.135, 0.093, 0.048 mm, all OK)."),
 ("Status: [LIST] proposed, not confirmed (no stroke, no maker confirmation). The BOM line P1-P4 (item 15) still lists the 0981: decision needed (lead or owner): swap the pin, or change the ring's pad pitch.",
  "Status: [LIST] proposed, not confirmed (no stroke, no maker confirmation). Decided in C5e: the fitted pin for P1-P4 is the Harwin P70-6000045R (BOM item 15); the Mill-Max 0981 is history only (BOM item 78, quantity 0). To confirm with Harwin: stroke (at least 0.34 mm), force curve over 2.10 to 2.65 mm, life."),
 ("- **R1 (open, roll).**", "- **R1 (closed in C5d; this paragraph is the state before C5d, history).**"),
 ("the pad row moves at most 0.680 mm against 0.2 mm a 0.6 mm pin tip can take on a 1.0 mm pad: NOT held. A nub channel (as in C3) or a ring-side feature is needed; not designed. The check proves the nominal pose only.",
  "the pad row moved at most 0.680 mm against 0.2 mm a 0.6 mm pin tip can take on a 1.0 mm pad: not held at that time. Current (C5d, look/c5d_check_lead_rerun.log): the pad row moves at most 0.135 mm (US 11) against 0.50 mm on a 1.6 mm pad, OK on all seven sizes (0.113, 0.119, 0.124, 0.129, 0.135, 0.093, 0.048 mm for US 7 to 13)."),
 ("- **F4 (BOM).** Item 15 (Mill-Max 0981) still lists the pin that does not fit; PA1-PA4 (Harwin P70-6000045R) is the proposed replacement, [LIST] proposed, not confirmed: decision needed (lead or owner).",
  "- **F4 (BOM).** History: item 15 listed the Mill-Max 0981, which does not fit. Since C5e item 15 (P1-P4) is the Harwin P70-6000045R, [LIST] proposed, stroke not confirmed; the Mill-Max 0981 is item 78 (reference PA1-PA4), quantity 0, history only."),
 ("last line \"case_check: PASS, 1807 pairs checked,", "(history, C4/C5; the current check is look/c5d_check_lead_rerun.log with 3447 pairs) last line \"case_check: PASS, 1807 pairs checked,"),
 ("RESULT: done, outside 45.5 x 45.9 x 41.4 mm (C4 43.2 x 44.0 x 40.6 mm); case_check last line \"case_check: PASS, 1842 pairs checked,",
  "RESULT: done (history, C5b; current C5d: outside 45.4 x 45.9 x 41.4 mm, 3447 pairs), outside 45.5 x 45.9 x 41.4 mm then (C4 43.2 x 44.0 x 40.6 mm); case_check last line \"case_check: PASS, 1842 pairs checked,"),
 ("1. Pin conflict K1: swap to a 1.5 mm barrel pin (Harwin P70-6000045R, stroke unknown) or keep asking Harwin for the stroke?", "1. Pin conflict K1 (decided in C5e: the Harwin P70-6000045R is the fitted pin; its stroke is still to be confirmed with Harwin)."),
])
print("ok")
