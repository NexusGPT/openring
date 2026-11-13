#!/usr/bin/env python3
"""Check design/wiring/product-wiring.csv against the design files.

Checks (each failure is printed as FAIL[<check>] ...):
  terminal-missing  a pin of an off-board part or a board-to-board land (from the netlists and parts lists) is in no line
  terminal-twice    such a pin is in more than one line
  terminal-unknown  a line names as a terminal a pin that the netlist does not hold
  band-pad          a pad of a band circuit board (flex1/flex2, any size) is named by no line
  ends-disagree     the two ends' signal names differ and the line names no pairing rule
  lead-length       a lead or wire has no cut length for each of the 7 ring sizes and not the words "not size dependent"
  state             a line has the state `not drawn` or a state outside the five allowed words
  incomplete        (only with --require-complete) a conductor line is not complete: its state is not `drawn and routed`
                    or `specified and landed`; each is listed with what it waits for (column waits_for)
  complete-open     a line marked complete has a board pad that is not joined to its net (KiCad copper connectivity):
                    for copper the two end pads on the carrier boards, for any other carrier every board pad it names
  state-kind        `drawn and routed` on a carrier that is not copper, or `specified and landed` on copper or without
                    its specification (marking, gauge or model, cut length per size or "not size dependent")
  proof-missing     an end or the carrier has no proof
  proof-text        a quoted proof is not found again at its cited file and line
  proof-board       a board proof (pad and net, or a copper path) is not found again in the board file
  joint             a line has no joint id
  field-newline     a field holds a carriage return or a newline (review 4 note N2), or a row has a short or long field list
  states-net        the net a line STATES at an end (signal_A, signal_B) differs from the net of that pin in the netlist or of
                    that pad in the board file(s) (every ring size for a band board); carrier_net does not follow the two
  states-tail       the tail land in the join text ("tail land N", the flex named) is not the line's own J_BAND land, or that
                    land on the flex board (7 sizes) does not carry the line's net
  states-face       the face stated at an end differs from the layers of that pad in the board file (the main board face and,
                    for a J_BAND land, the tail land face on the flex)
  states-colour     the colour of a lead or case wire (carrier_marking, carrier text) differs from the colour its source gives
                    (band-interface.md land table, lead-decisions.md case wire list, board-notes.md cell lead line)
  states-cut        a cut length per size differs from the source table (band-interface.md `lead cut length` row, whose header
                    order 7..13 is checked; board-notes.md wiring table; thermistor 10 mm)
  states-copper     a copper length per size differs by more than 0.001 mm from the shortest copper path read from that size's
                    board (only for a line with a PATH proof between two pads)
  rebuild           the line differs, field by field, from the line the generator (build_wiring.py, imported, run in memory
                    with its output captured, no file written) builds today from the same sources
Hardening of review 4 fault I1 (checks-harden-notes.md): `states-*` read the sources independently of the generator (netlist
rows, pad nets and layers through pcbnew, the source tables by their own regexes); `rebuild` compares every column with the
generator's own functions. `rebuild` shares the generator's reading of the sources, so it cannot catch a wrong source reading
that both make; `states-*` cannot catch a field they do not read (state_reason, waits_for, join texts other than the tail land).
It prints the counts per state and per joint, the sensing gaps (carrier_kind none: no conductor, counted apart) and,
before the RESULT line, `COMPLETE <n> of <total> conductors (<percent>)`. Without --require-complete the check is about
consistency; with it, it also exits 1 while any conductor line is incomplete. Last line: RESULT PASS|FAIL with the counts.
Pins with no net (no-connect) carry no signal and are not required (lead's ruling on the screen cable).

Run: python design/wiring/check_wiring.py [--csv <file>]   (re-runs itself under KiCad's Python when pcbnew is missing)
"""
import csv
import os
import re
import sys

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[2].as_posix())
HERE = os.path.join(ROOT, "design/wiring")
KIPY = os.path.join(ROOT, "design/ecad/ring/pcb/run_kipy.sh")
try:
    import pcbnew  # noqa: F401
except ImportError:
    if os.environ.get("WIRING_REEXEC") == "1":
        raise
    env = dict(os.environ, WIRING_REEXEC="1")
    os.execve("/bin/bash", ["/bin/bash", KIPY, os.path.abspath(__file__)] + sys.argv[1:], env)

sys.path.insert(0, HERE)
os.environ["WIRING_NO_DRC"] = "1"
import build_wiring as bw  # noqa: E402

STATES = bw.STATES
SIZES = bw.SIZES
# which parts leave their board: decided by their footprint in the parts list
RING_OFFBOARD_FP = re.compile(r"^OpenRingBand:|FPCtail|FPC_Hirose")
CASE_OFFBOARD_FP = re.compile(r"CELL_LEADS|NTC_wired|HARWIN_P70|WIRE_PTH|TOUCH_E1")
# Board round 4 (lead's ruling of 2026-11-13, E2): J1's pin MP is the two fitting tabs of the screen connector, pads of a part on
# its own board soldered to that board's ground (ring-board-plan.md R2.6); no connection between boards or to an off-board part,
# so the wiring list has no line for them and they are left out of the terminal set
NOT_TERMINALS = {("ring", "J1", "MP")}


def expand(glob):
    m = re.search(r"\{([^}]*)\}", glob)
    if not m:
        return [glob]
    return [glob[:m.start()] + x + glob[m.end():] for x in m.group(1).split(",")]


def split_proofs(cell):
    """Proofs are joined by ';' ; a text proof is 'file:line|quote', a board proof starts with BOARD: or PATH:."""
    out = []
    for part in re.split(r";(?=(?:BOARD:|PATH:|design/))", cell):
        part = part.strip()
        if part:
            out.append(part)
    return out


# ---------------------------------------------------------------- hardening (review 4, fault I1 and note N2)
BOARD_OF = {"ring main board": [bw.RING_BOARD], "case main board (PCB1)": [bw.CASE_MAIN], "case pin board (PCB2)": [bw.CASE_PINS],
            "FLEX1": [bw.FLEX["FLEX1"].format(s) for s in SIZES], "FLEX2": [bw.FLEX["FLEX2"].format(s) for s in SIZES]}
LAYER_RX = re.compile(r"through hole|F\.Cu|B\.Cu")


def read_text(rel):
    """Plain read of a source file (own reader, newline translation on), a list of lines."""
    with open(bw.p(rel), encoding="utf-8") as f:
        return f.read().split("\n")


def end_boards(r, e):
    lab = r.get("end_%s_board" % e, "")
    for k, v in BOARD_OF.items():
        if lab == k:
            return v
    return []


def product_of(r, e):
    lab = r.get("end_%s_board" % e, "")
    return "case" if "case" in lab else "ring"


def netlist_net(prod, ref, pin):
    """Net of (ref, pin) in the product's netlist, read here from the file; None if the pin has no row."""
    key = (prod, ref, pin)
    if key not in _NL:
        _NL[key] = None
        for x in bw.read_netlist(bw.RING_NETLIST if prod == "ring" else bw.CASE_NETLIST):
            if x["reference"] == ref and x["pin_number"] == pin:
                _NL[key] = x["net"]
    return _NL[key]


_NL = {}


def same_net(stated, real):
    if not real:
        return stated.startswith("(no connect")
    return stated == real


def source_tables():
    """The three source tables the lead and cut checks compare with, read by their own regexes."""
    t = {"motor": {}, "motor_cut": None, "case_cut": {}, "case_colour": {}, "th1_cut": None, "cell_colour": {}}
    bi = read_text(bw.BI)
    for ln in bi:
        if "Land 1 (pad 1) = " in ln and "M1 pin 1" in ln:
            for m in re.finditer(r"Land (\d) \(pad \d\) = (\w+) lead = M1 pin (\d) = net (\w+) = J_BAND_A land (\d)", ln):
                land, colour, pin, net, jl = m.groups()
                t["motor"][land] = (colour, pin, net, jl)
    head = [i for i, ln in enumerate(bi) if re.match(r"^\| US \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \|", ln)]
    cut = [ln for ln in bi if ln.startswith("| lead cut length, mm |")]
    if head and cut:
        t["motor_cut"] = {s: c.strip() for s, c in zip(SIZES, cut[0].strip("|").split("|")[1:])}
    cbn = read_text(bw.CBN)
    h = [i for i, ln in enumerate(cbn) if ln.startswith("### Wiring table (replaces part f)")]
    for ln in cbn[h[0]:h[0] + 20] if h else []:
        m = re.match(r"^\| (W\d) \| ([^|]+) \| (W\d) \| (\S+) \| ([\d.]+) \| ([\d.]+) \| (\d+) \|", ln)
        if m:
            t["case_cut"][m.group(3)] = m.group(6)
    for ln in cbn:
        m = re.search(r"unchanged \((\d+) mm leads\)", ln)
        if m:
            t["th1_cut"] = m.group(1)
        m = re.search(r"lead 1 (\w+) = \+, lead 2 (\w+) = -", ln)
        if m:
            t["cell_colour"] = {"1": m.group(1), "2": m.group(2)}
    for ln in read_text(bw.LD):
        if ln.startswith("| case wires W1 to W4 and W7: colour |"):
            for m in re.finditer(r"(W\d) \(([^)]+)\) (\w+)", ln):
                t["case_colour"][m.group(1)] = (m.group(2), m.group(3))
    return t


def check_statements(rows, fail):
    """What each line STATES, read against the boards, the netlists and the source tables (fault I1)."""
    tab = source_tables()
    for r in rows:
        rid = r.get("id", "?")
        kind = r.get("carrier_kind", "")
        if kind == "none":
            continue
        nets = {}
        for e in ("A", "B"):
            ref = r.get("end_%s_ref" % e, "")
            pin = (r.get("end_%s_pin" % e, "") or "").split(" ")[0]
            sig = r.get("signal_%s" % e, "")
            ek = r.get("end_%s_kind" % e, "")
            nets[e] = sig
            if ek == "node":
                if sig != r.get("carrier_net"):
                    fail("states-net", "%s end %s is a copper node of net %r but the line's net is %r" % (rid, e, sig, r.get("carrier_net")))
                continue
            prod = product_of(r, e)
            real = netlist_net(prod, ref, pin)
            boards = end_boards(r, e)
            if real is not None and not same_net(sig, real):
                fail("states-net", "%s end %s %s.%s states net %r, the %s netlist says %r" % (rid, e, ref, pin, sig, prod, real))
            for b in boards:
                pad = bw.pad_of(b, ref, pin)
                if pad is None:
                    fail("states-net", "%s end %s %s.%s has no pad on %s" % (rid, e, ref, pin, b))
                elif not same_net(sig, pad["net"]):
                    fail("states-net", "%s end %s %s.%s states net %r, the pad on %s has net %r" % (rid, e, ref, pin, sig, b, pad["net"]))
            # face
            face = r.get("end_%s_face" % e, "")
            if boards and ek in ("terminal", "land", "face"):
                want = []
                for b in boards:
                    pad = bw.pad_of(b, ref, pin)
                    if pad is None:
                        continue
                    if r["end_%s_board" % e] == "ring main board":
                        w = [pad["layers"][0]]
                        if ref.startswith("J_BAND"):
                            fl = "FLEX1" if ref == "J_BAND_A" else "FLEX2"
                            w2 = []
                            for fb in BOARD_OF[fl]:
                                fp_ = bw.pad_of(fb, ref, pin)
                                w2.append(sorted(fp_["layers"]) if fp_ else None)
                            if any(x != w2[0] for x in w2):
                                fail("states-face", "%s tail land %s:%s has different faces at the 7 sizes" % (rid, ref, pin))
                            got_tail = face.split("tail land on")[1] if "tail land on" in face else ""
                            if sorted(LAYER_RX.findall(got_tail)) != (w2[0] or []):
                                fail("states-face", "%s end %s tail land face states %r, the flex boards have %s" % (rid, e, got_tail.strip(), w2[0]))
                            face_main = face.split("tail land on")[0]
                        else:
                            face_main = face
                        if LAYER_RX.findall(face_main) != w:
                            fail("states-face", "%s end %s %s.%s face states %r, the board file has %s" % (rid, e, ref, pin, face_main.strip(" ;"), w))
                        break
                    want.append(sorted(pad["layers"]))
                if want and any(x != want[0] for x in want):
                    fail("states-face", "%s end %s %s.%s has different layers at the sizes" % (rid, e, ref, pin))
                elif want and sorted(LAYER_RX.findall(face)) != want[0]:
                    fail("states-face", "%s end %s %s.%s face states %r, the board file has %s" % (rid, e, ref, pin, face, want[0]))
        exp = nets["A"] if nets["A"] == nets["B"] else "%s/%s" % (nets["A"], nets["B"])
        if r.get("carrier_net") != exp:
            fail("states-net", "%s carrier net %r does not follow its end nets %r and %r" % (rid, r.get("carrier_net"), nets["A"], nets["B"]))
        # tail land in the join text
        m = re.search(r"hot bar \(main board land to (FLEX\d) tail land (\d+)\)", r.get("join_A", ""))
        if m:
            fl, land = m.groups()
            ref = r.get("end_A_ref", "")
            pin = (r.get("end_A_pin", "") or "").split(" ")[0]
            if bw.TAIL_OF.get(fl) != ref or land != pin or r.get("end_A_board") != "ring main board":
                fail("states-tail", "%s join text says %s tail land %s but end A is %s %s.%s" % (rid, fl, land, r.get("end_A_board"), ref, pin))
            if not r.get("carrier", "").startswith(fl + " "):
                fail("states-tail", "%s join text names %s but the carrier is %r" % (rid, fl, r.get("carrier", "")[:40]))
            for fb in BOARD_OF[fl]:
                pad = bw.pad_of(fb, bw.TAIL_OF[fl], land)
                if pad is None or not same_net(r.get("signal_A", ""), pad["net"]):
                    fail("states-tail", "%s %s tail land %s on %s has net %r, the line states %r" % (
                        rid, fl, land, fb, None if pad is None else pad["net"], r.get("signal_A")))
        elif r.get("join_A", "").startswith("hot bar"):
            fail("states-tail", "%s join text %r not understood" % (rid, r.get("join_A")))
        # lead and wire colours and cuts
        cuts = {s: r.get("cut_mm_us%d" % s, "") for s in SIZES}
        colour = None
        want_cut = None
        if kind == "lead" and r.get("end_A_ref") == "M1":
            land = (r.get("end_B_pin") or "").split(" ")[0]
            src = tab["motor"].get(land)
            if src is None:
                fail("states-colour", "%s motor land %s is in no source line of %s" % (rid, land, bw.BI))
            else:
                colour = src[0]
                if src[2] != r.get("carrier_net") or src[1] != (r.get("end_A_pin") or "").split(" ")[0]:
                    fail("states-colour", "%s source pairs land %s with M1 pin %s net %s, the line has pin %s net %s" % (
                        rid, land, src[1], src[2], r.get("end_A_pin"), r.get("carrier_net")))
            if tab["motor_cut"] is None:
                fail("states-cut", "%s the lead cut length row or its header order 7..13 is not in %s" % (rid, bw.BI))
            else:
                want_cut = tab["motor_cut"]
        elif kind in ("lead", "wire") and r.get("end_B_ref", "").startswith("W") and r.get("end_B_board", "").startswith("case main"):
            w = r["end_B_ref"]
            if w in tab["case_colour"]:
                colour = tab["case_colour"][w][1]
                if tab["case_colour"][w][0] != r.get("carrier_net"):
                    fail("states-colour", "%s source gives %s net %s, the line net %s" % (rid, w, tab["case_colour"][w][0], r.get("carrier_net")))
            elif kind == "wire":
                fail("states-colour", "%s %s is in no colour entry of %s" % (rid, w, bw.LD))
            elif kind == "lead" and r.get("end_A_ref") == "BT1":
                pin = (r.get("end_A_pin") or "").split(" ")[0]
                c = tab["cell_colour"].get(pin)
                sign = "+" if pin == "1" else "-"
                bt = netlist_net("case", "BT1", pin)
                if c is None or r.get("carrier_marking") != "%s (%s)" % (c, sign):
                    fail("states-colour", "%s cell lead %s marking %r, the source gives colour %r" % (rid, pin, r.get("carrier_marking"), c))
            if w in tab["case_cut"]:
                want_cut = {s: tab["case_cut"][w] for s in SIZES}
            else:
                fail("states-cut", "%s %s is in no row of the wiring table of %s" % (rid, w, bw.CBN))
        elif kind == "lead" and r.get("end_A_ref") == "TH1":
            if tab["th1_cut"] is None:
                fail("states-cut", "%s the thermistor lead length is not found in %s" % (rid, bw.CBN))
            else:
                want_cut = {s: tab["th1_cut"] for s in SIZES}
        if colour is not None:
            if r.get("carrier_marking") != colour + " insulation" or not (" %s " % colour) in (" " + r.get("carrier", "") + " ").replace(",", " "):
                fail("states-colour", "%s source says %s, the line says marking %r, carrier %r" % (rid, colour, r.get("carrier_marking"), r.get("carrier", "")[:50]))
        if want_cut is not None:
            for s in SIZES:
                try:
                    same = abs(float(cuts[s]) - float(want_cut[s])) < 1e-9
                except ValueError:
                    same = False
                if not same:
                    fail("states-cut", "%s cut length at US %d is %r, the source table says %r" % (rid, s, cuts[s], want_cut[s]))
        # copper length per size against the shortest path of that size's board
        if kind == "copper":
            for pr in split_proofs(r.get("proof_carrier", "")):
                if pr.startswith("PATH:"):
                    g, net, ends = pr[5:].split("|")
                    a, z = ends.split("-")
                    if a == "node" or z == "node":
                        continue
                    for b in expand(g):
                        mm = re.search(r"us(\d+)\.kicad_pcb", b)
                        if not mm or not os.path.exists(bw.p(b)):
                            continue
                        d = bw.dijkstra(bw.copper_graph(b, net), ("P",) + tuple(a.split(":"))).get(("P",) + tuple(z.split(":")))
                        stated = r.get("copper_mm_us%s" % mm.group(1), "")
                        if d is None or not re.match(r"^\d+(\.\d+)?$", stated) or abs(float(stated) - d) > 0.001:
                            fail("states-copper", "%s copper length at US %s is %r, the board gives %s" % (
                                rid, mm.group(1), stated, None if d is None else "%.3f" % d))


def check_rebuild(rows, fail, path):
    """Field by field against the line the generator builds today (run in memory; its output file is captured)."""
    import contextlib
    import io

    class Cap(io.StringIO):
        def close(self):
            pass

    buf = Cap()
    target = bw.p(bw.OUT)

    def cap_open(fp, *a, **k):
        if os.path.abspath(fp) == os.path.abspath(target) and a and a[0] == "w":
            return buf
        return open(fp, *a, **k)

    bw.open = cap_open
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            bw.main()
    except SystemExit as ex:
        fail("rebuild", "the generator stops: %s" % ex)
        return
    finally:
        del bw.open
    new = list(csv.DictReader(io.StringIO(buf.getvalue(), newline="")))
    if len(new) != len(rows):
        fail("rebuild", "the list has %d lines, the generator builds %d" % (len(rows), len(new)))
    for a, b in zip(new, rows):
        for k in bw.COLUMNS:
            if a.get(k) != b.get(k):
                fail("rebuild", "%s field %s: list says %r, the generator builds %r" % (
                    b.get("id", "?"), k, (b.get(k) or "")[:90], (a.get(k) or "")[:90]))
    extra = [k for k in (rows[0].keys() if rows else []) if k not in bw.COLUMNS]
    if extra:
        fail("rebuild", "columns the generator does not know: %s" % extra)


def check_fields(rows, fail):
    for i, r in enumerate(rows, 2):
        rid = r.get("id", "line %d" % i)
        if None in r:
            fail("field-newline", "%s has more fields than the header (%d extra)" % (rid, len(r[None])))
        for k, v in r.items():
            if v is None:
                fail("field-newline", "%s has no field %s (short row)" % (rid, k))
            elif k is not None and ("\r" in v or "\n" in v):
                fail("field-newline", "%s field %s holds %d carriage return and %d newline characters (first at offset %d)" % (
                    rid, k, v.count("\r"), v.count("\n"), min(x for x in (v.find("\r"), v.find("\n")) if x >= 0)))


def main():
    args = sys.argv[1:]
    require = "--require-complete" in args
    path = os.path.join(HERE, "product-wiring.csv")
    if "--csv" in args:
        path = os.path.abspath(args[args.index("--csv") + 1])
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    fails = []

    def fail(check, msg):
        fails.append("FAIL[%s] %s" % (check, msg))

    # ---------------- the terminal set, from the netlists and parts lists
    terms = {}
    noconnect = []
    for prod, nl, parts, rx in (("ring", bw.RING_NETLIST, bw.RING_PARTS, RING_OFFBOARD_FP),
                                ("case", bw.CASE_NETLIST, bw.CASE_PARTS, CASE_OFFBOARD_FP)):
        refs = {r["reference"] for r in bw.read_parts(parts) if rx.search(r["footprint"])}
        for r in bw.read_netlist(nl):
            if r["reference"] in refs and (prod, r["reference"], r["pin_number"]) not in NOT_TERMINALS:
                if r["net"]:
                    terms[(prod, r["reference"], r["pin_number"])] = r
                else:
                    noconnect.append("%s %s.%s" % (prod, r["reference"], r["pin_number"]))
    nl_all = {}
    for prod, nl in (("ring", bw.RING_NETLIST), ("case", bw.CASE_NETLIST)):
        for r in bw.read_netlist(nl):
            nl_all[(prod, r["reference"], r["pin_number"])] = r

    seen = {}
    named_pads = set()
    for r in rows:
        rid = r.get("id", "?")
        if not r.get("joint"):
            fail("joint", "%s has no joint id" % rid)
        # state
        if r.get("state") not in STATES:
            fail("state", "%s state %r is not one of %s" % (rid, r.get("state"), STATES))
        elif r["state"] == "not drawn":
            fail("state", "%s is `not drawn` (%s)" % (rid, r.get("state_reason", "")))
        kind = r.get("carrier_kind", "")
        if require and kind != "none" and r.get("state") in STATES and r["state"] not in bw.COMPLETE:
            fail("incomplete", "%s %s %s.%s -> %s.%s is `%s`; waits for: %s" % (
                rid, r.get("joint"), r.get("end_A_ref"), r.get("end_A_pin", "").split(" ")[0], r.get("end_B_ref"),
                r.get("end_B_pin", "").split(" ")[0], r["state"], r.get("waits_for") or r.get("state_reason", "")))
        if r.get("state") in bw.COMPLETE:
            pads_to_test = []
            if kind == "copper":
                for pr in split_proofs(r.get("proof_carrier", "")):
                    if pr.startswith("PATH:"):
                        g, net, ends = pr[5:].split("|")
                        for e in ends.split("-"):
                            if e != "node":
                                pads_to_test += [(b, tuple(e.split(":"))) for b in expand(g)]
                    elif pr.startswith("BOARD:") and pr.count("|") == 1 and r.get("end_A_ref") == "ANT1":
                        for pr2 in split_proofs(r.get("proof_A", "")):
                            if pr2.startswith("BOARD:") and pr2.count("|") == 2:
                                g, rp, _n = pr2[6:].split("|")
                                pads_to_test += [(b, tuple(rp.split(":"))) for b in expand(g)]
            else:
                for col in ("proof_A", "proof_B"):
                    for pr in split_proofs(r.get(col, "")):
                        if pr.startswith("BOARD:") and pr.count("|") == 2:
                            g, rp, _n = pr[6:].split("|")
                            pads_to_test += [(b, tuple(rp.split(":"))) for b in expand(g)]
            for b, key in pads_to_test:
                if os.path.exists(bw.p(b)) and key in bw.board(b)["drc"]["open_pads"]:
                    fail("complete-open", "%s is `%s` but pad %s:%s on %s is not joined to its net" % (
                        rid, r["state"], key[0], key[1], b))
        if r.get("state") == "drawn and routed" and kind not in ("copper",):
            fail("state-kind", "%s is `drawn and routed` but its carrier is %r, not copper" % (rid, kind))
        if r.get("state") == "specified and landed":
            cuts = [r.get("cut_mm_us%d" % s, "") for s in SIZES]
            if kind == "copper" or not r.get("carrier_marking") or not r.get("carrier_gauge_or_model") or (
                    not all(cuts) and r.get("cut_note") != "not size dependent"):
                fail("state-kind", "%s is `specified and landed` but carrier %r has marking %r, gauge or model %r, cuts %s" % (
                    rid, kind, r.get("carrier_marking"), r.get("carrier_gauge_or_model"), cuts))
        # proofs present
        for col in ("proof_A", "proof_carrier", "proof_B"):
            if not r.get(col, "").strip():
                fail("proof-missing", "%s has no %s" % (rid, col))
        # terminals
        for e in ("A", "B"):
            kind = r.get("end_%s_kind" % e, "")
            ref = r.get("end_%s_ref" % e, "")
            pin = (r.get("end_%s_pin" % e, "") or "").split(" ")[0]
            prf = r.get("proof_%s" % e, "")
            if kind == "terminal":
                m = re.search(r"design/ecad/(ring|case)/netlist\.csv:\d+\|[^,]*,%s,%s," % (re.escape(ref), re.escape(pin)), prf)
                if not m:
                    fail("terminal-unknown", "%s end %s %s.%s has no netlist row in its proof" % (rid, e, ref, pin))
                    continue
                key = (m.group(1), ref, pin)
                if key not in nl_all:
                    fail("terminal-unknown", "%s end %s %s %s.%s is not in the %s netlist" % (rid, e, key[0], ref, pin, key[0]))
                seen.setdefault(key, []).append(rid)
            for pr in split_proofs(prf):
                if pr.startswith("BOARD:"):
                    parts = pr[len("BOARD:"):].split("|")
                    if len(parts) == 3:
                        for b in expand(parts[0]):
                            if "/band/" in b:
                                named_pads.add((b, parts[1]))
        # signal names
        sa, sb, rule = r.get("signal_A", ""), r.get("signal_B", ""), r.get("pairing_rule", "")
        if sa != sb:
            if not rule or rule.startswith("same net") or not (
                    ("no conductor" in rule) or (sa.split(" ")[0] in rule and sb.split(" ")[0] in rule)):
                fail("ends-disagree", "%s signal A %r and signal B %r differ; pairing rule %r does not name them" % (rid, sa, sb, rule))
        # leads
        if r.get("carrier_kind") in ("lead", "wire"):
            vals = [r.get("cut_mm_us%d" % s, "") for s in SIZES]
            okv = all(re.match(r"^\d+(\.\d+)?$", v or "") for v in vals)
            if not okv and r.get("cut_note", "") != "not size dependent":
                fail("lead-length", "%s %s has cut lengths %s and no 'not size dependent'" % (rid, r.get("carrier_kind"), vals))
        # proofs found again
        for col in ("proof_A", "proof_carrier", "proof_B", "proof_join"):
            for pr in split_proofs(r.get(col, "")):
                if pr.startswith("BOARD:") or pr.startswith("PATH:"):
                    kind, body = pr.split(":", 1)
                    parts = body.split("|")
                    for b in expand(parts[0]):
                        if not os.path.exists(bw.p(b)):
                            fail("proof-board", "%s %s: board %s does not exist" % (rid, col, b))
                            continue
                        bd = bw.board(b)
                        if kind == "BOARD" and len(parts) == 3:
                            ref, num = parts[1].split(":")
                            pad = bw.pad_of(b, ref, num)
                            if pad is None or pad["net"] != parts[2]:
                                fail("proof-board", "%s %s: %s pad %s:%s %s (wanted net %s)" % (
                                    rid, col, b, ref, num, "missing" if pad is None else "net " + pad["net"], parts[2]))
                        elif kind == "BOARD" and len(parts) == 2 and parts[1].startswith("net "):
                            net = parts[1][4:]
                            has = any(d["net"] == net for lst in bd["pads"].values() for d in lst)
                            if not has:
                                fail("proof-board", "%s %s: no pad of net %s on %s" % (rid, col, net, b))
                        elif kind == "PATH" and len(parts) == 3:
                            net = parts[1]
                            a, z = parts[2].split("-")
                            adj = bw.copper_graph(b, net)
                            ends = [("P",) + tuple(x.split(":")) for x in (a, z) if x != "node"]
                            if len(ends) == 2:
                                d = bw.dijkstra(adj, ends[0])
                                if ends[1] not in d:
                                    fail("proof-board", "%s %s: no copper path %s on net %s in %s" % (rid, col, parts[2], net, b))
                            elif len(ends) == 1:
                                d = bw.dijkstra(adj, ends[0])
                                tails = [k for k in bd["pads"] if k[0].startswith("J_BAND") and ("P",) + k in d]
                                if not tails:
                                    fail("proof-board", "%s %s: %s reaches no J_BAND land on net %s in %s" % (rid, col, parts[2], net, b))
                        else:
                            fail("proof-board", "%s %s: proof %r not understood" % (rid, col, pr))
                else:
                    m = re.match(r"^(design/[^:|]+):(\d+)\|(.*)$", pr, re.S)
                    if not m:
                        fail("proof-text", "%s %s: proof %r has no file:line|quote form" % (rid, col, pr[:80]))
                        continue
                    f, n, q = m.group(1), int(m.group(2)), m.group(3)
                    if not os.path.exists(bw.p(f)):
                        fail("proof-text", "%s %s: file %s does not exist" % (rid, col, f))
                        continue
                    lines = open(bw.p(f), encoding="utf-8").read().split("\n")
                    if n < 1 or n > len(lines) or q not in lines[n - 1].rstrip("\r"):
                        fail("proof-text", "%s %s: %s line %d does not hold %r" % (rid, col, f, n, q[:70]))

    for key in sorted(terms):
        if key not in seen:
            fail("terminal-missing", "%s %s pin %s (net %r) is in no line" % (key[0], key[1], key[2], terms[key]["net"]))
    for key, ids in sorted(seen.items()):
        if len(ids) > 1:
            fail("terminal-twice", "%s %s pin %s is in %d lines: %s" % (key[0], key[1], key[2], len(ids), " ".join(ids)))
    # every pad of every band circuit board is named by at least one line
    for flex, g in bw.FLEX.items():
        for s in SIZES:
            b = g.format(s)
            for (ref, num) in sorted(bw.board(b)["pads"]):
                if (b, "%s:%s" % (ref, num)) not in named_pads:
                    fail("band-pad", "%s pad %s:%s is named by no line" % (b, ref, num))

    check_fields(rows, fail)
    if rows and not any(f_.startswith("FAIL[field-newline]") and "short row" in f_ for f_ in fails):
        check_statements(rows, fail)
        check_rebuild(rows, fail, path)

    # counts
    by_state = {s: 0 for s in STATES}
    by_joint, by_end_joint = {}, {}
    for r in rows:
        by_state[r.get("state")] = by_state.get(r.get("state"), 0) + 1
        by_joint[r.get("joint")] = by_joint.get(r.get("joint"), 0) + 1
        for j in (r.get("end_joints") or "").split(";"):
            if j:
                by_end_joint[j] = by_end_joint.get(j, 0) + 1
    for f_ in fails:
        print(f_)
    print("csv:", path)
    print("terminals required (off-board pins and board-to-board lands with a net): %d, in exactly one line: %d" % (
        len(terms), sum(1 for k in terms if len(seen.get(k, [])) == 1)))
    print("no-connect pins not required: %d (%s)" % (len(noconnect), ", ".join(noconnect)))
    for s in STATES:
        print("state %-22s %d" % (s, by_state.get(s, 0)))
    print("lines per joint: " + ", ".join("%s %d" % (j, by_joint[j]) for j in sorted(by_joint, key=lambda x: (x[0], int(x[1:]) if x[1:].isdigit() else 0))))
    print("lines naming a joint at an end: " + ", ".join("%s %d" % (j, by_end_joint[j]) for j in sorted(by_end_joint)))
    checks = sorted({f_.split("]")[0][5:] for f_ in fails})
    gaps = [r for r in rows if r.get("carrier_kind") == "none"]
    cond = [r for r in rows if r.get("carrier_kind") != "none"]
    done = sum(1 for r in cond if r.get("state") in bw.COMPLETE)
    print("sensing gaps, no conductor (carrier_kind none, counted apart): %d (%s)" % (
        len(gaps), ", ".join("%s %s" % (r["id"], r["joint"]) for r in gaps)))
    pct = 100.0 * done / len(cond) if cond else 0.0
    share = "COMPLETE %d of %d conductors (%.0f percent)" % (done, len(cond), pct)
    print("mode: %s" % ("--require-complete (incomplete lines fail)" if require else "consistency (incomplete lines are counted, not failed)"))
    print(share)
    summary = "lines %d (%d conductors, %d sensing gap), %s, complete %d of %d conductors (%.0f percent), problems %d" % (
        len(rows), len(cond), len(gaps), ", ".join("%s %d" % (s, by_state.get(s, 0)) for s in STATES), done, len(cond), pct,
        len(fails))
    if fails:
        print("RESULT FAIL %s (checks failing: %s)" % (summary, " ".join(checks)))
        sys.exit(1)
    print("RESULT PASS %s" % summary)


if __name__ == "__main__":
    main()
