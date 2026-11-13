#!/usr/bin/env python3
"""Check the joint table design/mfg/assembly/joints.csv against the wiring list and the design files.

Run: design/.venv/bin/python design/mfg/assembly/check_joints.py [--joints FILE] [--wiring FILE] [--list-gaps]

Fails (exit 1, one line per problem, last line `RESULT FAIL n`) when:
  R1 missing-row     a joint end of the wiring list (or a board pass) has no row
  R2 empty/MISSING   a row has an empty field (gap may be empty) or the word MISSING, or a gap text
  R3 no-step         a row's step (or the step of its check) is not a step of assembly.md or of the
                     case procedure (board-notes.md, "Case procedure" list)
  R4 paste           solder_source names a paste layer file that does not exist, or that holds no
                     opening at a land it names (pads read from KiCad pad dumps of board copies,
                     openings read from the Gerber flashes, stroked circles and regions of the paste file)
  R5 check-order     check_possible_at_this_step names a step before the row's step, or before a
                     step tag [needs step N] / [needs case N] written in the check
  R6 weak-check      (review 4 fault I2) the check field does not name BOTH what is measured or looked at (a method form of
                     CHECK_METHOD) AND a pass value or pass condition the builder can decide (a form of CHECK_PASS: a number with
                     a unit, a named reading, a named visual condition, an accept rule of step N of assembly.md, or file:line
                     whose line holds a pass value or condition). A check such as "ok" fails.
  R7 weak-heat       (review 4 fault I2) the heat field is not one of HEAT_FORMS: a value with a unit (C, s, N) AND a tool or
                     process named in the heat text or in the row's tool field; or a named profile Pn with its file
                     (process.md Pn, the section existing); or "none" / "no heat" followed by a reason. A heat such as "hot" fails.
                     An empty tool field is left to R2 (the tool clause is then not applied again).
Passes with `RESULT PASS joints <n>`. --list-gaps prints every gap and exits 0. --list-weak prints every row R6 or R7 would
reject (rule, row, why) and exits 0 (a dry run of the two rules).
--joints, --wiring and --passes point the check at other files (broken copies, test miniature).
"""
import csv, glob, math, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
PAD_DIR = os.path.join(HERE, "joint-table-work", "pads")
ASSEMBLY = os.path.join(ROOT, "design/mfg/assembly/assembly.md")
CASE_NOTES = os.path.join(ROOT, "design/ecad/case/pcb/board-notes.md")
FIELDS = ["joint_id", "wiring_line", "end", "what_meets_what", "step", "solder_source", "flux", "tool",
          "heat", "orientation", "alignment", "check", "check_possible_at_this_step", "source", "gap"]
NO_JOINT = ("copper (same board)", "made by", "none", "inside the part")
TOL = 0.02  # mm, a flash centre within this of the pad centre is the pad's opening


# ---------- R6 and R7: the accepted forms, as data (review 4 fault I2) ----------
# A form is (name, regex). A check needs at least one METHOD form and at least one PASS form; a heat needs one HEAT form.
UNITS = r"(?:mm|V|A|mA|ohm|ohms|kohm|k|Mohm|C|C/s|N|s|ms|MB|MHz|%)"  # "times" (a magnification) is a method, not a pass value
NUM = r"\d+(?:\.\d+)?"
CHECK_METHOD = [
    ("instrument", r"\b(?:ohmmeter|multimeter|meter|continuity|probe|probes|needle tips|diode mode|feeler|gauge|thermocouple|bench supply|jig|X-ray)\b"),
    ("looked at", r"\b(?:inspection|inspected|optical|magnifier|microscope|by eye|visual)\b|\b\d+ times\b"),
    ("named test or reading", r"\b(?:T-[A-Z][A-Z-]*|FACTORY ENTER|GET_INFO|USB through|beeps?|reads?|voltage|measured|height|lights)\b"),
]
CHECK_PASS = [
    ("number with a unit", r"(?<![\w.])%s(?:\s*(?:to|and)\s*%s)?\s*%s(?![\w])" % (NUM, NUM, UNITS)),
    ("named reading", r"\b(?:beeps?|no beep|(?:does|do) not beep|reads? open|reads? (?:the )?cell voltage|a diode drop|enumerates|answers|vibrates|0 violations|continuity|positive|breathing|blink)\b"),
    ("named visual condition", r"\b(?:flat|no bridge|not tilted|no tilt|not skewed|touch nothing else|none of its .* lifted|in place|centred)\b"),
]
ACCEPT_RULE_RX = re.compile(r"accept rules? of step (\d+)")
FILE_LINE_RX = re.compile(r"((?:design/)?[\w./-]+\.(?:md|csv|py|txt|json)):(\d+)")
HEAT_TOOL = r"\b(?:iron|tip|hot bar|blade|thermode|hot plate|reflow|oven|profile|pressed contact|hand solder)\b"
HEAT_VALUE = r"(?<![\w.])%s\s*(?:degrees C|C|s|seconds|N)(?![\w])" % NUM
HEAT_NONE = r"^(?:none|no heat)\s*[:;,]\s*\S.{5,}"
PROFILE_RX = re.compile(r"\b(P\d) profile\b")
PROFILE_FILE_RX = re.compile(r"process\.md (P\d)\b")
PROCESS = os.path.join(ROOT, "design/mfg/assembly/process.md")


def _file_line_text(rel, n):
    """Text of line n of the cited file (None when the file or the line does not exist)."""
    for base in (ROOT, os.path.join(ROOT, "design/mfg/assembly")):
        path = os.path.join(base, rel)
        if os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.read().split("\n")
            return lines[int(n) - 1] if 1 <= int(n) <= len(lines) else None
    return None


def _holds_pass_form(text):
    return any(re.search(rx, text) for _n, rx in CHECK_PASS)


def _step_has_accept_rules(n):
    """True when step n of assembly.md names its accept rules (the step is the named rule)."""
    t = open(ASSEMBLY, encoding="utf-8").read()
    m = re.search(r"^### Step %d\..*?(?=^### Step |\Z)" % n, t, flags=re.S | re.M)
    return bool(m and re.search(r"accept rules?", m.group(0)))


def weak_check(text, a_steps):
    """Problems of rule R6 for one check text (empty list = accepted)."""
    method = [n for n, rx in CHECK_METHOD if re.search(rx, text)]
    passes = [n for n, rx in CHECK_PASS if re.search(rx, text)]
    for m in ACCEPT_RULE_RX.finditer(text):
        if int(m.group(1)) in a_steps and _step_has_accept_rules(int(m.group(1))):   # the step exists and names its accept rules
            passes.append("accept rule of step %s" % m.group(1))
    for m in FILE_LINE_RX.finditer(text):
        cited = _file_line_text(m.group(1), m.group(2))
        if cited is not None and _holds_pass_form(cited):                            # the cited line itself holds a pass value or condition
            passes.append("file:line %s:%s" % (m.groups()))
    out = []
    if not method:
        out.append("names no method (what is measured or looked at)")
    if not passes:
        out.append("names no pass value or pass condition")
    return out


def weak_heat(text, tool):
    """Problems of rule R7 for one heat text; tool is the row's tool field."""
    t = text.strip()
    if re.match(HEAT_NONE, t, re.I):
        return []
    if re.search(r"\bnone\b|\bno heat\b", t, re.I) and not re.search(HEAT_VALUE, t):
        return ["says none or no heat without a reason after a colon"]
    for m in PROFILE_RX.finditer(t):
        fm = PROFILE_FILE_RX.search(t)
        if fm and fm.group(1) == m.group(1) and re.search(r"^## %s\." % m.group(1), open(PROCESS, encoding="utf-8").read(), re.M):
            return []
    out = []
    if not re.search(HEAT_VALUE, t):
        out.append("names no value with a unit (C, s, N) and no profile with its file, and is not none with a reason")
    elif tool.strip() and not (re.search(HEAT_TOOL, t, re.I) or re.search(HEAT_TOOL, tool, re.I)):
        out.append("names a value but no tool or process (neither here nor in the tool field)")
    return out


# ---------- steps ----------
def assembly_steps(path=ASSEMBLY):
    s = set()
    for line in open(path, encoding="utf-8"):
        m = re.match(r"### Step (\d+)\.", line)
        if m:
            s.add(int(m.group(1)))
    return s


def case_steps(path=CASE_NOTES):
    s, inside = set(), False
    for line in open(path, encoding="utf-8"):
        if line.startswith("**Case procedure"):
            inside = True
            continue
        if inside:
            m = re.match(r"(\d+)\. ", line)
            if m:
                s.add(int(m.group(1)))
            elif line.startswith("#"):
                break
    return s


def parse_step(text):
    """'16' -> ('assembly', 16); 'case 3' -> ('case', 3); else None."""
    t = text.strip()
    m = re.fullmatch(r"(\d+)", t)
    if m:
        return ("assembly", int(m.group(1)))
    m = re.fullmatch(r"case (\d+)", t)
    if m:
        return ("case", int(m.group(1)))
    return None


# ---------- pads and Gerber ----------
def read_pads(board):
    path = os.path.join(PAD_DIR, board + "-pads.csv")
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def read_flashes(path):
    """Flash centres (x, y) in mm from a KiCad Gerber (FSLAX46Y46, MOMM). Modal coordinates kept."""
    pts, x, y, dec = [], None, None, 6
    for raw in open(path, encoding="utf-8", errors="replace"):
        line = raw.strip()
        m = re.match(r"%FSLAX(\d)(\d)Y(\d)(\d)\*%", line)
        if m:
            dec = int(m.group(2))
            continue
        if line.startswith("%") or line.startswith("G04"):
            continue
        mx = re.search(r"X(-?\d+)", line)
        my = re.search(r"Y(-?\d+)", line)
        if mx:
            x = int(mx.group(1)) / 10 ** dec
        if my:
            y = int(my.group(1)) / 10 ** dec
        if line.endswith("D03*") and x is not None and y is not None:
            pts.append((x, y))
    return pts


def read_openings(path):
    """Openings of a paste file in three forms (added 2026-11-13 by the guide helper, granted by the lead):
    ('flash', x, y): a D03 flash, as read_flashes;
    ('circle', cx, cy, r, w): a circle stroked with a round aperture of width w (arcs drawn with I/J offsets);
        r - w/2 > 0 is a ring (a hole in the middle), else a filled dot;
    ('region', [(x, y), ...]): a filled region G36 ... G37 (its outline points)."""
    out = [("flash", x, y) for x, y in read_flashes(path)]
    ap, cur, x, y, dec, region, pts = {}, None, None, None, 6, False, []
    circles = {}
    for raw in open(path, encoding="utf-8", errors="replace"):
        line = raw.strip()
        m = re.match(r"%FSLAX(\d)(\d)Y(\d)(\d)\*%", line)
        if m:
            dec = int(m.group(2))
            continue
        m = re.match(r"%ADD(\d+)C,([\d.]+)", line)
        if m:
            ap[int(m.group(1))] = float(m.group(2))
            continue
        if line.startswith("%") or line.startswith("G04"):
            continue
        if line.startswith("G36"):
            region, pts = True, []
            continue
        if line.startswith("G37"):
            if len(pts) >= 3:
                out.append(("region", pts))
            region = False
            continue
        m = re.fullmatch(r"(?:G54)?D(\d+)\*", line)
        if m and int(m.group(1)) >= 10:
            cur = int(m.group(1))
            continue
        mx, my = re.search(r"X(-?\d+)", line), re.search(r"Y(-?\d+)", line)
        mi, mj = re.search(r"I(-?\d+)", line), re.search(r"J(-?\d+)", line)
        nx = int(mx.group(1)) / 10 ** dec if mx else x
        ny = int(my.group(1)) / 10 ** dec if my else y
        if region and (line.endswith("D01*") or line.endswith("D02*")) and nx is not None:
            pts.append((nx, ny))
        elif line.endswith("D01*") and (mi or mj) and x is not None:
            i = int(mi.group(1)) / 10 ** dec if mi else 0.0
            j = int(mj.group(1)) / 10 ** dec if mj else 0.0
            key = (round(x + i, 4), round(y + j, 4))
            circles[key] = (math.hypot(i, j), ap.get(cur, 0.0))
        x, y = nx, ny
    for (cx, cy), (r, w) in circles.items():
        out.append(("circle", cx, cy, r, w))
    return out


def has_opening(pad, flashes):
    px, py = float(pad["x_mm"]), -float(pad["y_mm"])  # KiCad Gerber: same origin, Y axis turned
    hw, hh = float(pad["w_mm"]) / 2, float(pad["h_mm"]) / 2
    for o in flashes:
        if not isinstance(o[0], str):  # a bare (x, y) flash centre, as read_flashes gives it
            o = ("flash", o[0], o[1])
        if o[0] == "flash":
            if abs(o[1] - px) <= TOL and abs(o[2] - py) <= TOL:
                return True
        elif o[0] == "circle":
            _, cx, cy, r, w = o
            if r - w / 2 > 0.001:  # a ring: centred on the land
                if abs(cx - px) <= TOL and abs(cy - py) <= TOL:
                    return True
            else:  # a filled dot: wholly on the land (the pad dump has no rotation: either way round)
                ro = r + w / 2
                if any(abs(cx - px) + ro <= ax + TOL and abs(cy - py) + ro <= ay + TOL for ax, ay in ((hw, hh), (hh, hw))):
                    return True
        elif o[0] == "region":
            pts = o[1]
            a = cx = cy = 0.0
            for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
                c = x1 * y2 - x2 * y1
                a += c
                cx += (x1 + x2) * c
                cy += (y1 + y2) * c
            if abs(a) < 1e-12:
                continue
            cx, cy = cx / (3 * a), cy / (3 * a)
            for ax, ay in ((hw, hh), (hh, hw)):  # the pad dump has no rotation: either way round
                inside_c = abs(cx - px) <= ax and abs(cy - py) <= ay
                inside_box = all(abs(x - px) <= ax + TOL and abs(y - py) <= ay + TOL for x, y in pts)
                if inside_c and inside_box:  # a region: its centre and its whole outline on the land
                    return True
    return False


def board_of_paste(rel):
    base = os.path.basename(rel)
    m = re.match(r"(.+)-([FB])_Paste\.gbr$", base)
    return (m.group(1), m.group(2)) if m else (None, None)


def pos_refs(rel):
    refs = []
    with open(os.path.join(ROOT, rel), newline="") as f:
        for r in csv.DictReader(f):
            refs.append((r.get("Ref") or r.get("# Ref") or "").strip().strip('"'))
    return [r for r in refs if r]


def paste_problems(row):
    """Return problem texts for rule R4."""
    out = []
    t = row["solder_source"]
    for m in re.finditer(r"paste layer (\S+) for (parts of (\S+) except ([^;]*)|([A-Za-z0-9_]+:[A-Za-z0-9]+(?: [A-Za-z0-9_]+:[A-Za-z0-9]+)*))", t):
        rel = m.group(1)
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            out.append("paste layer file does not exist: %s" % rel)
            continue
        board, face = board_of_paste(rel)
        if board is None or not os.path.isfile(os.path.join(PAD_DIR, board + "-pads.csv")):
            out.append("paste layer %s: no pad dump for its board" % rel)
            continue
        flashes = read_openings(path)
        pads = read_pads(board)
        cu = face + ".Cu"
        if m.group(3):
            posrel = m.group(3)
            if not os.path.isfile(os.path.join(ROOT, posrel)):
                out.append("position file does not exist: %s" % posrel)
                continue
            exc = {e.strip() for e in m.group(4).split(",") if e.strip()}
            refs = set(pos_refs(posrel)) - exc
            lands = [p for p in pads if p["ref"] in refs and p["attr"] == "SMD" and cu in p["layers"].split()]
            for r in sorted(refs):
                if not any(p["ref"] == r for p in pads):
                    out.append("paste layer %s: part %s of %s has no pad on the board" % (rel, r, posrel))
        else:
            want = m.group(5).split()
            lands = []
            for w in want:
                ref, num = w.split(":")
                hit = [p for p in pads if p["ref"] == ref and p["pad"] == num and cu in p["layers"].split()]
                if not hit:
                    out.append("paste layer %s: land %s not found on %s" % (rel, w, cu))
                lands += hit
        for p in lands:
            if not has_opening(p, flashes):
                out.append("paste layer %s holds no opening for land %s:%s (%s)" % (rel, p["ref"], p["pad"], p["net"]))
    return out


# ---------- wiring ends ----------
def required_ends(wiring):
    req = []
    with open(wiring, newline="") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):
            for e in "AB":
                j = r["join_" + e].strip()
                if j.startswith(NO_JOINT):
                    continue
                req.append((r["id"], e))
    return req


def required_passes():
    req = [("board pass", "ring F.Cu"), ("board pass", "ring B.Cu")]
    for p in sorted(glob.glob(os.path.join(ROOT, "design/ecad/band/flex[12]-us*.kicad_pcb"))):
        req.append(("board pass", os.path.basename(p)[:-10]))
    for p in sorted(glob.glob(os.path.join(ROOT, "design/ecad/case/pcb/case_*.kicad_pcb"))):
        req.append(("board pass", os.path.basename(p)[:-10]))
    return req


def main(argv):
    joints = os.path.join(HERE, "joints.csv")
    wiring = os.path.join(ROOT, "design/wiring/product-wiring.csv")
    list_gaps = "--list-gaps" in argv
    list_weak = "--list-weak" in argv
    if "--joints" in argv:
        joints = argv[argv.index("--joints") + 1]
    if "--wiring" in argv:
        wiring = argv[argv.index("--wiring") + 1]
    passes = required_passes()
    if "--passes" in argv:  # a file with one board pass name per line (used by the test miniature)
        with open(argv[argv.index("--passes") + 1]) as f:
            passes = [("board pass", l.strip()) for l in f if l.strip()]
    with open(joints, newline="") as f:
        rd = csv.DictReader(f)
        header = rd.fieldnames or []
        rows = list(rd)
    if list_weak:
        a_steps_ = assembly_steps()
        n = 0
        for r in rows:
            for rule, why in (([("R6", w) for w in weak_check(r["check"], a_steps_)] if r["check"].strip() else []) +
                              ([("R7", w) for w in weak_heat(r["heat"], r["tool"])] if r["heat"].strip() else [])):
                n += 1
                print("WEAK %s %s | %s | %s" % (rule, r["joint_id"], why, (r["check"] if rule == "R6" else r["heat"]).strip()[:200]))
        print("WEAK %d lines in %d rows" % (n, len(rows)))
        return 0
    if list_gaps:
        n = 0
        for r in rows:
            if (r.get("gap") or "").strip():
                n += 1
                print("GAP %s | %s | %s" % (r["joint_id"], r["what_meets_what"], r["gap"]))
        print("GAPS %d of %d rows" % (n, len(rows)))
        return 0
    probs = []
    for fld in FIELDS:
        if fld not in header:
            probs.append("R2 column missing: %s" % fld)
    if probs:
        for p in probs:
            print(p)
        print("RESULT FAIL %d" % len(probs))
        return 1
    a_steps, c_steps = assembly_steps(), case_steps()

    def step_exists(st):
        return st is not None and ((st[0] == "assembly" and st[1] in a_steps) or (st[0] == "case" and st[1] in c_steps))

    have = {}
    for r in rows:
        if r["wiring_line"].strip() == "board pass":
            key = ("board pass", r["end"].strip())
        else:
            key = (r["wiring_line"].strip(), r["end"].strip())
        have.setdefault(key, []).append(r["joint_id"])
    for key in required_ends(wiring) + passes:
        if key not in have:
            probs.append("R1 missing-row: no row for %s end %s" % key)
    for r in rows:
        jid = r["joint_id"] or "(no id)"
        for fld in FIELDS:
            v = (r.get(fld) or "").strip()
            if fld == "gap":
                continue
            if not v:
                probs.append("R2 empty: %s field %s is empty" % (jid, fld))
            elif "MISSING" in v:
                probs.append("R2 MISSING: %s field %s" % (jid, fld))
        if (r.get("gap") or "").strip():
            probs.append("R2 gap: %s has a gap: %s" % (jid, r["gap"].strip()[:160]))
        st_text = r["step"].strip()
        st = parse_step(st_text)
        if st_text and "MISSING" not in st_text and not step_exists(st):
            probs.append("R3 no-step: %s step '%s' is not a step of assembly.md or of the case procedure" % (jid, st_text))
        for p in paste_problems(r):
            probs.append("R4 paste: %s %s" % (jid, p))
        if r["check"].strip() and "MISSING" not in r["check"]:
            for w in weak_check(r["check"], a_steps):
                probs.append("R6 weak-check: %s check %s: %r" % (jid, w, r["check"].strip()[:80]))
        if r["heat"].strip() and "MISSING" not in r["heat"]:
            for w in weak_heat(r["heat"], r["tool"]):
                probs.append("R7 weak-heat: %s heat %s: %r" % (jid, w, r["heat"].strip()[:80]))
        cp = r["check_possible_at_this_step"].strip()
        if st is not None and cp and "MISSING" not in cp:
            if cp == "yes":
                at = st
            else:
                m = re.fullmatch(r"no, (.+)", cp)
                at = parse_step(m.group(1)) if m else None
                if at is None or not step_exists(at):
                    probs.append("R3 no-step: %s check step '%s' is not a step of assembly.md or of the case procedure" % (jid, cp))
                    at = None
            if at is not None:
                needs = [st]
                for m in re.finditer(r"\[needs (step|case) (\d+)\]", r["check"]):
                    needs.append(("assembly" if m.group(1) == "step" else "case", int(m.group(2))))
                for nd in needs:
                    if nd[0] != at[0]:
                        probs.append("R5 check-order: %s check at %s and needed %s are in different procedures" % (jid, at, nd))
                    elif at[1] < nd[1]:
                        probs.append("R5 check-order: %s check marked possible at %s %d, but it needs %s %d" % (jid, at[0], at[1], nd[0], nd[1]))
    for p in probs:
        print(p)
    if probs:
        print("RESULT FAIL %d" % len(probs))
        return 1
    print("RESULT PASS joints %d" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
