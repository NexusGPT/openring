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
                     openings read from the Gerber flashes of the paste file)
  R5 check-order     check_possible_at_this_step names a step before the row's step, or before a
                     step tag [needs step N] / [needs case N] written in the check
Passes with `RESULT PASS joints <n>`. --list-gaps prints every gap and exits 0.
"""
import csv, glob, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
PAD_DIR = os.path.join(HERE, "joint-table-work", "pads")
ASSEMBLY = os.path.join(ROOT, "design/mfg/assembly/assembly.md")
CASE_NOTES = os.path.join(ROOT, "design/ecad/case/pcb/board-notes.md")
FIELDS = ["joint_id", "wiring_line", "end", "what_meets_what", "step", "solder_source", "flux", "tool",
          "heat", "orientation", "alignment", "check", "check_possible_at_this_step", "source", "gap"]
NO_JOINT = ("copper (same board)", "made by", "none", "inside the part")
TOL = 0.02  # mm, a flash centre within this of the pad centre is the pad's opening


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


def has_opening(pad, flashes):
    px, py = float(pad["x_mm"]), -float(pad["y_mm"])  # KiCad Gerber: same origin, Y axis turned
    return any(abs(fx - px) <= TOL and abs(fy - py) <= TOL for fx, fy in flashes)


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
        flashes = read_flashes(path)
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
    if "--joints" in argv:
        joints = argv[argv.index("--joints") + 1]
    if "--wiring" in argv:
        wiring = argv[argv.index("--wiring") + 1]
    with open(joints, newline="") as f:
        rd = csv.DictReader(f)
        header = rd.fieldnames or []
        rows = list(rd)
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
    for key in required_ends(wiring) + required_passes():
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
