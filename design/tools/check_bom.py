"""Check design/bom.csv.  Usage: python -I check_bom.py [bom.csv] [architecture.md] [placement.csv] [netlist.csv] [body.md] [index.csv]

Exit 1 when any of these fail (each failure is printed):
  1. a line has an empty maker_part_number and an empty open_action
  2. a reference designator appears twice (ranges like C1..C3 are expanded)
  3. quantity is not a positive integer
  4. evidence is not DS, LIST or CALC
  5. a part named in architecture.md section 2 is absent from the CSV
  6. one control, no record button (owner rule): every switch designator is SW1 to SW5, the switch
     part SKTAAAE010 is used exactly 5 times in all, the words record button, record switch, record key or
     pill cap appear only with a removal word (no, former, removed, not), and no line but SW2 says that
     a press starts or stops a recording (review 2, G17, fake B1)
  7. charging pads (lines with CP designators): diameter and pitch equal the ring's inside model, read from
     the pad rows of design/mech/thin/placement.csv (size_x as the diameter, "(N mm pitch along the arc)"
     in the note text); the size_mm, value and key_figures cells must state them (review 2, G17, fake B3)
  8. designators against the model and the wiring (review 3, H11, fakes B4, B5, B8): every designator of the
     parts list is a reference in design/ecad/ring/netlist.csv or design/mech/thin/placement.csv, or one of the
     five named non-electrical, non-placed lines (HSG1, LNR1, PRT1, FLEX1, FLEX2); every reference of those two
     files is on the parts list (a removed CAP1 or FRM1, a line of junk parts, fails here)
  9. removed in v7 (architecture 17.30; review 3, fake B1): no designator LED1, R41, Q2, LG1, LP1, no part number
     KPG-1005SURC-TT, and no line names a recording light, a light guide or LED1 without a removal word
 10. charging pad order: the CP1..CP4 line says "order" followed by the pad names of the placement.csv rows
     pad_*, ordered by CP number (review 3, fake B7)
 11. motor angle per ring size: the M1 line says "at" and the seven angles of the row "motor position" of
     design/mfg/specs/body.md (US 7 to 13), and the US 9 angle equals the M1 row of placement.csv (fake B9)
 12. cover glass outline: the GL1 size_mm starts with the plan outline of the maker file, index.csv line
     "cover-glass" (bbox_x x bbox_y) (review 3, H06)
 13. thermistor RT1 sits on the cell (architecture 17.3, W13 replaced): the RT1 line says so and carries no
     question to the owner about its place (review 3, H05)
Extra checks (also exit 1): header columns, empty reference, quantity differs from the
number of designators in the reference cell.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(HERE)
COLS = ["item", "reference", "quantity", "function", "maker", "maker_part_number", "package", "size_mm",
        "value", "key_figures", "evidence", "source_file_or_url", "unit_price_and_currency_at_qty1", "open_action"]


def expand(ref):
    out = []
    for tok in [t.strip() for t in ref.split(",") if t.strip()]:
        m = re.fullmatch(r"([A-Za-z_-]+?)(\d+)\.\.(?:\1)?(\d+)", tok)
        if m:
            a, b = int(m.group(2)), int(m.group(3))
            out += [m.group(1) + str(n) for n in range(a, b + 1)]
        else:
            out.append(tok)
    return out


def section2_rows(arch_path):
    text = open(arch_path, encoding="utf-8").read()
    m = re.search(r"^## 2\. Fixed parts\s*$(.*?)^## 3\.", text, re.S | re.M)
    if not m:
        return None
    rows = []
    for line in m.group(1).splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| Function"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2:
            rows.append((cells[0], cells[1]))
    return rows


PART_TOKEN = re.compile(r"^(?=.*[A-Z])(?=.*\d)[A-Za-z0-9][A-Za-z0-9.=/\-]{4,}$")


def part_tokens(part_cell):
    toks = []
    for piece in re.split(r"[,()]", part_cell):
        for w in piece.split():
            w = w.strip(";:")
            if PART_TOKEN.match(w) and not re.fullmatch(r"\d+(\.\d+)?", w):
                toks.append(w)
    return toks


SWITCH_PART = "SKTAAAE010"
REMOVAL = re.compile(r"\b(no|former|removed|not|never)\b", re.I)
RECORD_WORDS = re.compile(r"record(ing)? (button|switch|key|cap)|pill cap", re.I)
PRESS_STARTS = re.compile(r"(long press|press)[^.;]{0,60}\b(starts?|stops?)\b[^.;]{0,30}record|\b(starts?|stops?)\b[^.;]{0,30}record[^.;]{0,40}press", re.I)


def check_one_control(lines, fails):
    """Rule 6. Returns the number of lines that name a switch."""
    n_sw, total_parts = 0, 0
    for n, d in lines:
        refs = expand(d["reference"])
        sw_refs = [r for r in refs if re.match(r"(SW|S|KEY|BTN|REC)\d", r, re.I)]
        if sw_refs:
            n_sw += 1
        for r in refs:
            if r.upper().startswith("SW") and r not in ("SW1", "SW2", "SW3", "SW4", "SW5"):
                fails.append("line %d (%s): switch %s is not one of SW1 to SW5 (owner rule: one control, no record button)" % (n, d["item"], r))
        for r in sw_refs:
            if not r.upper().startswith("SW"):
                fails.append("line %d (%s): designator %s looks like a button; the ring has SW1 to SW5 only" % (n, d["item"], r))
        if d["maker_part_number"].strip() == SWITCH_PART:
            total_parts += len(refs)
        for col in ("item", "function", "value", "key_figures", "size_mm", "package"):
            cell = d[col]
            if RECORD_WORDS.search(cell) and not REMOVAL.search(cell):
                fails.append("line %d (%s): %s names a record button without saying it is removed" % (n, d["item"], col))
        if "SW2" not in refs and PRESS_STARTS.search(d["function"] + " " + d["key_figures"]):
            fails.append("line %d (%s): a part other than SW2 starts or stops a recording by a press" % (n, d["item"]))
    if total_parts != 5:
        fails.append("switch part %s is used %d times, the ring has 5 (SW1 to SW5)" % (SWITCH_PART, total_parts))
    return n_sw


def pad_truth(placement, fails):
    """Diameter and pitch of the ring's four pads from placement.csv."""
    dias, pitches = set(), set()
    try:
        with open(placement, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["part"].startswith("pad_"):
                    dias.add(float(row["size_x"]))
                    dias.add(float(row["size_y"]))
                    m = re.search(r"\(([\d.]+) mm pitch along the arc\)", row["note"])
                    if m:
                        pitches.add(float(m.group(1)))
    except (OSError, KeyError, ValueError) as e:
        fails.append("placement.csv cannot be read for the pad check: %s" % e)
        return None, None
    if len(dias) != 1 or len(pitches) != 1:
        fails.append("placement.csv pad rows give diameters %s and pitches %s, need one of each" % (sorted(dias), sorted(pitches)))
        return None, None
    return dias.pop(), pitches.pop()


def check_pads(lines, placement, fails):
    """Rule 7. Returns the number of pad lines."""
    dia, pitch = pad_truth(placement, fails)
    n_pad = 0
    for n, d in lines:
        refs = expand(d["reference"])
        if not any(r.startswith("CP") for r in refs):
            continue
        n_pad += 1
        if dia is None:
            continue
        a = re.findall(r"([\d.]+) dia", d["size_mm"])
        b = re.findall(r"gold pad ([\d.]+) mm", d["value"])
        c = re.findall(r"([\d.]+) mm pitch", d["key_figures"])
        for name, got, want in (("size_mm diameter", a, dia), ("value diameter", b, dia), ("key_figures pitch", c, pitch)):
            if len(got) != 1 or abs(float(got[0]) - want) > 0.005:
                fails.append("line %d (%s): %s is %s, the inside model (placement.csv) has %s" % (n, d["item"], name, got or "missing", want))
    if n_pad != 1:
        fails.append("%d lines carry charging pads CP1 to CP4, expected 1" % n_pad)
    return n_pad


NON_ELECTRICAL = ("HSG1", "LNR1", "PRT1", "FLEX1", "FLEX2")  # on the parts list, in neither netlist.csv nor placement.csv
REMOVED_V7_REFS = ("LED1", "R41", "Q2", "LG1", "LP1")
REMOVED_V7_PARTS = ("KPG-1005SURC-TT",)
LIGHT_WORDS = re.compile(r"recording light|light guide|\bLED1\b|\bLG1\b|\bLP1\b", re.I)


def csv_refs(path, fails, what):
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return {r["reference"].strip() for r in csv.DictReader(f) if r["reference"].strip()}
    except (OSError, KeyError) as e:
        fails.append("%s cannot be read: %s" % (what, e))
        return None


def check_designators(lines, netlist, placement, fails):
    """Rules 8 and 9. Returns the number of designators compared."""
    net, pl = csv_refs(netlist, fails, "netlist.csv"), csv_refs(placement, fails, "placement.csv")
    bom = {}
    for n, d in lines:
        for r in expand(d["reference"]):
            bom[r] = n
    if net is not None and pl is not None:
        known = net | pl | set(NON_ELECTRICAL)
        for r, n in sorted(bom.items(), key=lambda kv: kv[1]):
            if r not in known:
                fails.append("line %d: designator %s is in neither netlist.csv, placement.csv nor the non-electrical list %s" % (n, r, list(NON_ELECTRICAL)))
        for r in sorted((net | pl) - set(bom)):
            fails.append("designator %s is in netlist.csv or placement.csv and missing from the parts list" % r)
    for r in REMOVED_V7_REFS:
        if r in bom:
            fails.append("line %d: designator %s was removed in v7 (no recording light, architecture 17.30)" % (bom[r], r))
    for n, d in lines:
        for p in REMOVED_V7_PARTS:
            if p.lower() in d["maker_part_number"].lower() or p.lower() in d["item"].lower():
                fails.append("line %d (%s): part %s was removed in v7 (recording light)" % (n, d["item"], p))
        for col in ("item", "function", "value", "key_figures", "size_mm", "package"):
            if LIGHT_WORDS.search(d[col]) and not REMOVAL.search(d[col]):
                fails.append("line %d (%s): %s names a recording light or light guide without saying it is removed" % (n, d["item"], col))
    return len(bom)


def check_pad_order(lines, placement, fails):
    """Rule 10."""
    names = {}
    try:
        with open(placement, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["part"].startswith("pad_"):
                    names[row["reference"]] = row["part"][4:]
    except (OSError, KeyError) as e:
        fails.append("placement.csv cannot be read for the pad order: %s" % e)
        return
    order = ", ".join(names[k] for k in sorted(names, key=lambda k: int(re.sub(r"\D", "", k))))
    for n, d in lines:
        if any(r.startswith("CP") for r in expand(d["reference"])):
            m = re.search(r"order ([A-Za-z+\-]+(?:, [A-Za-z+\-]+)+)", d["function"])
            if not m or m.group(1) != order:
                fails.append("line %d (%s): pad order is %s, the inside model (placement.csv) has %s" % (n, d["item"], m.group(1) if m else "missing", order))


def check_motor_angle(lines, body_md, placement, fails):
    """Rule 11."""
    try:
        text = open(body_md, encoding="utf-8").read()
        m = re.search(r"^\| motor position \| ([-\d., ]+) deg on US 7 to 13 \|", text, re.M)
        want = [x.strip() for x in m.group(1).split(",")]
        assert len(want) == 7
    except (OSError, AttributeError, AssertionError) as e:
        fails.append("body.md row 'motor position' (7 angles for US 7 to 13) cannot be read: %r" % e)
        return
    us9 = None
    try:
        with open(placement, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["reference"] == "M1":
                    us9 = float(row["angle_deg"])
    except (OSError, KeyError, ValueError) as e:
        fails.append("placement.csv M1 angle cannot be read: %s" % e)
    if us9 is not None and abs(float(want[2]) - us9) > 0.005:
        fails.append("body.md motor angle at US 9 is %s, placement.csv M1 has %s" % (want[2], us9))
    seen = 0
    for n, d in lines:
        if "M1" in expand(d["reference"]):
            seen += 1
            got = re.search(r" at ((?:-\d+(?:\.\d+)?, )*-\d+(?:\.\d+)?) degrees from the top on US 7, 8, 9, 10, 11, 12, 13", d["function"])
            if not got or [x.strip() for x in got.group(1).split(",")] != want:
                fails.append("line %d (%s): motor angles are %s, body.md has %s for US 7 to 13" % (n, d["item"], got.group(1) if got else "missing", ", ".join(want)))
    if seen != 1:
        fails.append("%d lines carry the motor M1, expected 1" % seen)


def check_glass(lines, index, fails):
    """Rule 12."""
    box = None
    try:
        with open(index, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["part"] == "cover-glass" and row["format"] == "STEP":
                    box = (float(row["bbox_x_mm"]), float(row["bbox_y_mm"]))
    except (OSError, KeyError, ValueError) as e:
        fails.append("index.csv cover-glass row cannot be read: %s" % e)
        return
    if box is None:
        fails.append("index.csv has no cover-glass STEP row")
        return
    for n, d in lines:
        if "GL1" in expand(d["reference"]):
            m = re.match(r"([\d.]+) x ([\d.]+) x ", d["size_mm"])
            if not m or abs(float(m.group(1)) - box[0]) > 0.0005 or abs(float(m.group(2)) - box[1]) > 0.0005:
                fails.append("line %d (%s): glass outline is %s, the maker file (index.csv) has %s x %s" % (n, d["item"], d["size_mm"][:40], box[0], box[1]))


def check_rt1(lines, fails):
    """Rule 13."""
    for n, d in lines:
        if "RT1" in expand(d["reference"]):
            if "RT1 sits on the cell" not in d["function"]:
                fails.append("line %d (%s): RT1 place is not stated as on the cell (architecture 17.3)" % (n, d["item"]))
            if re.search(r"owner must say|the owner must|on the main board beside the cell", d["function"] + " " + d["open_action"]):
                fails.append("line %d (%s): RT1 line still asks the owner for its place or puts it on the main board" % (n, d["item"]))


def main():
    bom = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DESIGN, "bom.csv")
    arch = sys.argv[2] if len(sys.argv) > 2 else os.path.join(DESIGN, "architecture.md")
    placement = sys.argv[3] if len(sys.argv) > 3 else os.path.join(DESIGN, "mech", "thin", "placement.csv")
    netlist = sys.argv[4] if len(sys.argv) > 4 else os.path.join(DESIGN, "ecad", "ring", "netlist.csv")
    body_md = sys.argv[5] if len(sys.argv) > 5 else os.path.join(DESIGN, "mfg", "specs", "body.md")
    index = sys.argv[6] if len(sys.argv) > 6 else os.path.join(DESIGN, "mfg", "parts", "index.csv")
    fails = []
    with open(bom, newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        header = next(rd, [])
        if header != COLS:
            fails.append("header columns differ from the required list/order: %r" % header)
        lines = []
        for n, row in enumerate(rd, start=2):
            if not any(c.strip() for c in row):
                continue
            if len(row) != len(COLS):
                fails.append("line %d: %d fields, need %d" % (n, len(row), len(COLS)))
                continue
            lines.append((n, dict(zip(COLS, row))))
    seen = {}
    for n, d in lines:
        if not d["maker_part_number"].strip() and not d["open_action"].strip():
            fails.append("line %d (%s): empty maker_part_number and no open_action" % (n, d["item"]))
        q = d["quantity"].strip()
        if not re.fullmatch(r"[1-9]\d*", q):
            fails.append("line %d (%s): quantity %r is not a positive integer" % (n, d["item"], q))
        if d["evidence"].strip() not in ("DS", "LIST", "CALC"):
            fails.append("line %d (%s): evidence %r is not DS, LIST or CALC" % (n, d["item"], d["evidence"]))
        refs = expand(d["reference"])
        if not refs:
            fails.append("line %d (%s): empty reference" % (n, d["item"]))
        for ref in refs:
            if ref in seen:
                fails.append("line %d (%s): reference %s already on line %d" % (n, d["item"], ref, seen[ref]))
            else:
                seen[ref] = n
        if refs and re.fullmatch(r"[1-9]\d*", q) and int(q) != len(refs):
            fails.append("line %d (%s): quantity %s but %d designators" % (n, d["item"], q, len(refs)))
    n_sw, n_pads = check_one_control(lines, fails), check_pads(lines, placement, fails)
    n_cmp = check_designators(lines, netlist, placement, fails)
    check_pad_order(lines, placement, fails)
    check_motor_angle(lines, body_md, placement, fails)
    check_glass(lines, index, fails)
    check_rt1(lines, fails)
    rows = section2_rows(arch)
    n_tokens = 0
    if rows is None:
        fails.append("architecture.md: section 2 table not found")
    else:
        hay = [" ".join(d[c] for c in COLS if c not in ("source_file_or_url", "open_action", "function")).lower()
               for _, d in lines]
        allhay = "\n".join(hay)
        for func, part in rows:
            fname = re.sub(r"\s+x\d+$", "", func).lower()
            if fname not in allhay:
                fails.append("architecture section 2: function %r is absent from the CSV" % func)
            for tok in part_tokens(part):
                n_tokens += 1
                if tok.lower() not in allhay:
                    fails.append("architecture section 2: part %s (%s) is absent from the CSV" % (tok, func))
    print("lines %d, designators %d, section-2 rows %s, section-2 part tokens %d, switch lines %d, pad lines %d, designators against model and wiring %d, failures %d"
          % (len(lines), len(seen), "n/a" if rows is None else len(rows), n_tokens, n_sw, n_pads, n_cmp, len(fails)))
    for f_ in fails:
        print("FAIL", f_)
    sys.exit(1 if fails else 0)


main()
