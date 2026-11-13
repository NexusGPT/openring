# review 3: one checker for B1, B2, B3 (pad nets against netlists), B5 (J_BAND mating, J1, case wire pads) and the ring-case pairing.
# usage: python3 check_all.py <product-wiring.csv> <pads dir> [ring-case-contact.csv]
# reads the pad dumps written by dump_board.py (KiCad's own reading of the 17 board files) and the design's netlists.
import csv, sys, re, os, collections
R = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
CSV = sys.argv[1]; PADS = sys.argv[2]
CONTACT = sys.argv[3] if len(sys.argv) > 3 else R + "/design/wiring/ring-case-contact.csv"
SIZES = range(7, 14)
fails = []
def fail(kind, msg): fails.append((kind, msg)); print("FAIL", kind, msg)

def load(name):
    d = {}
    for r in csv.DictReader(open(os.path.join(PADS, name + "-pads.csv"))):
        d[(r["ref"], r["pad"])] = r
    return d
B = {"ring": load("ring"), "case_main": load("case_main"), "case_pins": load("case_pins")}
for s in SIZES:
    B["flex1-us%d" % s] = load("flex1-us%d" % s); B["flex2-us%d" % s] = load("flex2-us%d" % s)

def boards_of(label):
    l = label.lower()
    if l.startswith("ring main board"): return ["ring"]
    if l.startswith("flex1"): return ["flex1-us%d" % s for s in SIZES]
    if l.startswith("flex2"): return ["flex2-us%d" % s for s in SIZES]
    if "case pin board" in l: return ["case_pins"]
    if "case main board" in l: return ["case_main"]
    return []
def pin_of(p): return p.split(" ")[0].strip()
def face_ok(endface, pad):
    if pad["face"] == "both": return endface.startswith("through hole")
    return endface.startswith(pad["face"])

rows = list(csv.DictReader(open(CSV)))
print("lines", len(rows))
covered = set(); seen = collections.Counter(); ends_checked = 0
for i, r in enumerate(rows, start=2):
    keyends = []
    for side in "AB":
        board, ref, pin, face, sig = r["end_%s_board" % side], r["end_%s_ref" % side], r["end_%s_pin" % side], r["end_%s_face" % side], r["signal_%s" % side]
        keyends.append((board.split(" (")[0], ref, pin_of(pin)))
        bl = boards_of(board)
        if not bl: continue
        if ref.startswith("copper of net"):
            net = ref.replace("copper of net ", "").strip()
            for b in bl:
                if not any(p["net"] == net for p in B[b].values()): fail("node", "L%d %s net %s not on %s" % (i, r["id"], net, b))
            continue
        for b in bl:
            p = B[b].get((ref, pin_of(pin)))
            ends_checked += 1
            if p is None: fail("end", "L%d %s %s %s.%s not a pad of %s" % (i, r["id"], side, ref, pin, b)); continue
            covered.add((b, ref, pin_of(pin)))
            if p["net"] != sig: fail("net", "L%d %s %s %s.%s pad net %s != line signal %s on %s" % (i, r["id"], side, ref, pin, p["net"], sig, b))
            if not face_ok(face, p): fail("face", "L%d %s %s %s.%s face '%s' but pad on %s (%s)" % (i, r["id"], side, ref, pin, face, p["face"], b))
        # tail land named inside the join text
        m = re.search(r"(FLEX[12]) tail land (\d+)", r["join_%s" % side])
        if m:
            fl = m.group(1).lower(); tref = "J_BAND_A" if fl == "flex1" else "J_BAND_B"
            for s in SIZES:
                b = "%s-us%d" % (fl, s); p = B[b].get((tref, m.group(2))); ends_checked += 1
                if p is None or p["net"] != sig: fail("tail", "L%d %s tail land %s of %s: %s != %s" % (i, r["id"], m.group(2), b, None if p is None else p["net"], sig))
                else: covered.add((b, tref, m.group(2)))
    if r["signal_A"] != r["signal_B"] and not r["signal_A"].startswith("(none") and r["pairing_rule"].startswith("same net"):
        fail("signal", "L%d %s signal A %s != signal B %s" % (i, r["id"], r["signal_A"], r["signal_B"]))
    seen[frozenset(keyends)] += 1
    kind = r["carrier_kind"]
    if kind in ("lead", "wire", "tab", "cable", "part cable", "spring pin"):
        cuts = [r["cut_mm_us%d" % s] for s in SIZES]
        if not r["carrier_marking"].strip(): fail("mark", "L%d %s no marking" % (i, r["id"]))
        if not (all(c.strip() for c in cuts) or "not size dependent" in r["cut_note"]): fail("cut", "L%d %s cuts %s note '%s'" % (i, r["id"], cuts, r["cut_note"]))
    if not r["join_A"].strip() or not r["join_B"].strip(): fail("join", "L%d %s join missing" % (i, r["id"]))
for k, n in seen.items():
    if n > 1: fail("dup", "end pair %s appears %d times" % (sorted(k), n))
print("kinds", collections.Counter(r["carrier_kind"] for r in rows))

# coverage of interface pads
need = []
for (ref, pad), p in B["ring"].items():
    if ref in ("J_BAND_A", "J_BAND_B", "ANT1") or (ref == "J1" and p["net"]): need.append(("ring", ref, pad))
for s in SIZES:
    for b in ("flex1-us%d" % s, "flex2-us%d" % s):
        for (ref, pad), p in B[b].items(): need.append((b, ref, pad))
for b in ("case_main", "case_pins"):
    for (ref, pad), p in B[b].items():
        if re.match(r"^(W\d|TH1|WP\d|P\d|E1)$", ref): need.append((b, ref, pad))
unc = [n for n in need if n not in covered]
for n in unc: fail("uncovered", "%s %s.%s" % n)
print("interface pads needed %d, covered %d" % (len(need), len(need) - len(unc)))

# B3 parity: pad nets against netlists
def netlist(p):
    d = {}
    for r in csv.DictReader(open(p)): d[(r["reference"], r["pin_number"])] = r["net"]
    return d
RN = netlist(R + "/design/ecad/ring/netlist.csv"); CN = netlist(R + "/design/ecad/case/netlist.csv")
PRT = {"1": ("BT1", "1"), "2": ("BT1", "2"), "3": ("RT1", "1")}
par = collections.Counter()
for b, pads in B.items():
    NL = CN if b.startswith("case") else RN
    for (ref, pad), p in pads.items():
        if not p["net"]: continue
        key = PRT[pad] if ref == "PRT1" else (ref, pad)
        par["checked"] += 1
        if key not in NL: fail("parity-norow", "%s %s.%s net %s has no netlist row" % (b, ref, pad, p["net"])); continue
        if NL[key] != p["net"]: fail("parity-net", "%s %s.%s board %s netlist %s" % (b, ref, pad, p["net"], NL[key]))
# netlist rows of parts placed on a board whose pad is missing
for b, NL in (("ring", RN), ("case_main", CN), ("case_pins", CN)):
    refs = set(k[0] for k in B[b])
    for (ref, pin), net in NL.items():
        if ref in refs and (ref, pin) not in B[b] and not (b != "ring" and ref not in refs):
            fail("parity-nopad", "%s netlist %s.%s (%s) has no pad" % (b, ref, pin, net))
print("parity pads checked", par["checked"])

# B5 mating: tail lands mapped onto the main board (X = v - 2.5, Y = side * (3.4 + u); u = x - 50; v = y - 80 on FLEX2, 80 - y on FLEX1; ring file = model + 100)
mat = 0
for s in SIZES:
    for fl, side, tref in (("flex1", -1, "J_BAND_A"), ("flex2", 1, "J_BAND_B")):
        b = "%s-us%d" % (fl, s)
        for (ref, pad), p in B[b].items():
            if ref != tref: continue
            u = float(p["x"]) - 50.0; v = (float(p["y"]) - 80.0) if side == 1 else (80.0 - float(p["y"]))
            X = v - 2.5; Y = side * (3.4 + u)
            q = B["ring"].get((tref, pad)); mat += 1
            if q is None: fail("mate", "%s %s.%s no ring land" % (b, ref, pad)); continue
            dx = abs(float(q["x"]) - 100 - X); dy = abs(float(q["y"]) - 100 - Y)
            if dx > 0.05 or dy > 0.05 or q["net"] != p["net"]: fail("mate", "%s %s.%s off %.3f %.3f nets %s/%s" % (b, ref, pad, dx, dy, p["net"], q["net"]))
        # every ring land of that row has a tail land
        for (ref, pad), q in B["ring"].items():
            if ref == tref and (ref, pad) not in B[b]: fail("mate", "%s lacks tail land %s.%s" % (b, ref, pad))
print("mating lands checked", mat)

# pairing ring pad to case pin (ring-case-contact.csv) against the wiring lines W054..W057 and the maker range 1.90 to 2.20
pairs = {}
for r in rows:
    if r["end_A_ref"].startswith("CP") and r["end_B_ref"].startswith("P"): pairs[r["end_A_ref"]] = (r["end_B_ref"], r["signal_A"], r["signal_B"])
cr = list(csv.DictReader(open(CONTACT))); pc = 0
sizes_seen = collections.Counter()
for r in cr:
    pc += 1; sizes_seen[r["ring_pad"]] += 1
    w = pairs.get(r["ring_pad"])
    if w is None or w[0] != r["case_pin"] or w[1] != r["ring_net"] or w[2] != r["case_net"]: fail("pair", "contact %s %s: csv line %s" % (r["ring_pad"], r["ring_size"], w))
    h = float(r["working_height_mm"])
    if not (1.90 <= h <= 2.20): fail("pair-height", "%s %s %.3f outside 1.90..2.20" % (r["ring_pad"], r["ring_size"], h))
    rn = B["flex2-us%s" % r["ring_size"].split()[-1]].get((r["ring_pad"], "1"))
    cn = B["case_pins"].get((r["case_pin"], "1"))
    if rn is None or rn["net"] != r["ring_net"] or cn is None or cn["net"] != r["case_net"]: fail("pair-board", "%s %s board nets %s/%s" % (r["ring_pad"], r["ring_size"], rn and rn["net"], cn and cn["net"]))
for k, n in sizes_seen.items():
    if n != 7: fail("pair-count", "%s has %d sizes" % (k, n))
print("pairing rows checked", pc)
print("ends checked", ends_checked)
print("RESULT lines=%d fails=%d" % (len(rows), len(fails)))
