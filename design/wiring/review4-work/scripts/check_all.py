# Review 4 checker (my own). Reads the wiring csv, the pad dumps of the 17 boards (pads/), the two netlists,
# the ring-case contact table. Prints one line per failure and a RESULT line. Exit 1 on any failure.
# usage: check_all.py <wiring.csv> <pads_dir> [<ring_netlist> <case_netlist> <contact_csv>]
import csv, sys, os, re, collections
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
wiring = sys.argv[1]; PADS = sys.argv[2]
RNET = sys.argv[3] if len(sys.argv) > 3 else ROOT + "/design/ecad/ring/netlist.csv"
CNET = sys.argv[4] if len(sys.argv) > 4 else ROOT + "/design/ecad/case/netlist.csv"
CONT = sys.argv[5] if len(sys.argv) > 5 else ROOT + "/design/wiring/ring-case-contact.csv"
SIZES = range(7, 14)
fails = []; info = collections.Counter()
def F(msg): fails.append(msg); print("FAIL", msg)

def load_pads(name):
    p = os.path.join(PADS, name + "-pads.csv")
    d = collections.defaultdict(list)
    for r in csv.DictReader(open(p)): d[(r["ref"], r["pad"])].append(r)
    return d
boards = {"ring": load_pads("ring"), "case_main": load_pads("case_main"), "case_pins": load_pads("case_pins")}
for f in (1, 2):
    for s in SIZES: boards["flex%d-us%d" % (f, s)] = load_pads("flex%d-us%d" % (f, s))

def netlist(path):
    d = {}
    for r in csv.DictReader(open(path)): d[(r["reference"], r["pin_number"])] = r["net"]
    return d
rn = netlist(RNET); cn = netlist(CNET)

rows = list(csv.DictReader(open(wiring)))
info["rows"] = len(rows)
cols_needed = ["id", "carrier_kind", "end_A_board", "end_A_ref", "end_A_pin", "end_B_board", "end_B_ref", "end_B_pin", "carrier_net", "carrier_marking", "cut_note"]
for c in cols_needed:
    if rows and c not in rows[0]: F("column missing: " + c)
if len(rows) == 0: F("no rows")

# B1: ids unique, end pairs unique, marking and cuts
ids = collections.Counter(r.get("id") for r in rows)
for k, v in ids.items():
    if v > 1: F("duplicate id %s x%d" % (k, v))
pairs = collections.Counter()
for r in rows:
    a = (r.get("end_A_board"), r.get("end_A_ref"), r.get("end_A_pin")); b = (r.get("end_B_board"), r.get("end_B_ref"), r.get("end_B_pin"))
    pairs[tuple(sorted([a, b]))] += 1
for k, v in pairs.items():
    if v > 1: F("duplicate end pair %s x%d" % (k, v))
PHYS = {"lead", "wire", "tab", "part cable", "spring pin"}
for r in rows:
    if r.get("carrier_kind") in PHYS:
        info["physical"] += 1
        if not (r.get("carrier_marking") or "").strip(): F("%s no marking" % r["id"])
        cuts = [r.get("cut_mm_us%d" % s, "") for s in SIZES]
        ok_cuts = all(re.fullmatch(r"\d+(\.\d+)?", c or "") and float(c) > 0 for c in cuts)
        if not ok_cuts and (r.get("cut_note") or "").strip() != "not size dependent":
            F("%s cut lengths missing and not 'not size dependent'" % r["id"])

# map of an end to board files
def end_boards(board):
    if board == "ring main board": return ["ring"]
    if board == "FLEX1": return ["flex1-us%d" % s for s in SIZES]
    if board == "FLEX2": return ["flex2-us%d" % s for s in SIZES]
    if board.startswith("case main board"): return ["case_main"]
    if board.startswith("case pin board"): return ["case_pins"]
    return []
def pin_of(p): return (p or "").split(" ")[0]
CASE_NET = {"VBUS/VRING": ("VBUS", "VRING"), "USB_DN/USB_D-": ("USB_DN", "USB_D-"), "USB_DP/USB_D+": ("USB_DP", "USB_D+")}
def expected_net(r, side):
    n = r.get("carrier_net", "")
    if n in CASE_NET: return CASE_NET[n][0 if side == "A" else 1]
    return n
covered = set()
for r in rows:
    for side in ("A", "B"):
        bd = r.get("end_%s_board" % side, ""); ref = r.get("end_%s_ref" % side, ""); pin = pin_of(r.get("end_%s_pin" % side))
        face = r.get("end_%s_face" % side, "")
        bl = end_boards(bd)
        if not bl or not ref or ref.startswith("copper of") or ref in ("ground",): continue
        net = expected_net(r, side)
        for b in bl:
            pads = boards[b].get((ref, pin))
            if not pads: F("%s end %s: no pad %s:%s on %s" % (r["id"], side, ref, pin, b)); continue
            for p in pads:
                info["end_checks"] += 1
                covered.add((b, ref, pin))
                if net and p["net"] != net: F("%s end %s %s %s:%s net %s, list says %s" % (r["id"], side, b, ref, pin, p["net"], net))
                lay = p["layers"].split("|")
                if "through hole" in face:
                    if not ("F.Cu" in lay and "B.Cu" in lay): F("%s end %s %s not through hole" % (r["id"], side, b))
                else:
                    want = "F.Cu" if face.startswith("F.Cu") else ("B.Cu" if face.startswith("B.Cu") else None)
                    if want and want not in lay: F("%s end %s %s %s:%s face %s, pad on %s" % (r["id"], side, b, ref, pin, want, p["layers"]))
            # netlist
            nl = rn if b in ("ring",) or b.startswith("flex") else cn
            if (ref, pin) in nl and net and nl[(ref, pin)] != net: F("%s end %s netlist %s:%s = %s, list %s" % (r["id"], side, ref, pin, nl[(ref, pin)], net))
            if (ref, pin) not in nl and ref not in ("PRT1",): F("%s end %s %s:%s not in netlist" % (r["id"], side, ref, pin))
    # node ends: copper of net X reaches land J_BAND_x:n  -> the tail land with that net exists on every size
    for side in ("A", "B"):
        pin = r.get("end_%s_pin" % side, "")
        m = re.match(r"reaches land (J_BAND_[AB]):(\d+)", pin)
        if m:
            for b in end_boards(r.get("end_%s_board" % side)):
                ps = boards[b].get((m.group(1), m.group(2)))
                if not ps or ps[0]["net"] != r["carrier_net"]: F("%s node land %s:%s on %s wrong" % (r["id"], m.group(1), m.group(2), b))
                else: info["node_checks"] += 1; covered.add((b, m.group(1), m.group(2)))
    # joins naming a tail land: "FLEX1 tail land n"
    for side in ("A",):
        m = re.search(r"to (FLEX[12]) tail land (\d+)", r.get("join_A", ""))
        if m:
            ref = "J_BAND_A" if m.group(1) == "FLEX1" else "J_BAND_B"
            for b in end_boards(m.group(1)):
                ps = boards[b].get((ref, m.group(2)))
                if not ps or ps[0]["net"] != r["carrier_net"]: F("%s tail land %s:%s on %s wrong" % (r["id"], ref, m.group(2), b))
                else: info["tail_land_checks"] += 1; covered.add((b, ref, m.group(2)))

# coverage of interface pads
iface = []
for (ref, pin), ps in boards["ring"].items():
    if ref in ("J_BAND_A", "J_BAND_B", "ANT1"): iface.append(("ring", ref, pin))
    if ref == "J1" and ps[0]["net"] and pin != "MP": iface.append(("ring", ref, pin))
for f in (1, 2):
    for s in SIZES:
        b = "flex%d-us%d" % (f, s)
        for (ref, pin) in boards[b]: iface.append((b, ref, pin))
for (ref, pin) in boards["case_main"]:
    if re.fullmatch(r"W\d|TH1", ref): iface.append(("case_main", ref, pin))
for (ref, pin) in boards["case_pins"]:
    if re.fullmatch(r"WP\d|P[1-4]|E1", ref): iface.append(("case_pins", ref, pin))
info["interface_pads"] = len(iface)
for x in iface:
    if x not in covered: F("interface pad not on a line: %s %s:%s" % x)
info["interface_covered"] = sum(1 for x in iface if x in covered)

# pad nets vs netlist on all boards
for b, d in boards.items():
    nl = cn if b.startswith("case") else rn
    for (ref, pin), ps in d.items():
        for p in ps:
            info["pads_total"] += 1
            if (ref, pin) in nl:
                info["pads_vs_netlist"] += 1
                if (nl[(ref, pin)] or "") != p["net"]: F("pad net %s %s:%s %s vs netlist %s" % (b, ref, pin, p["net"], nl[(ref, pin)]))
            elif ref not in ("PRT1",) and not ref.startswith("TP") and not ref.startswith("MH") and b.startswith("flex"):
                F("flex pad %s %s:%s not in netlist" % (b, ref, pin))
# netlist pins of board parts that have no pad (ring and case)
for (ref, pin), net in rn.items():
    if ref in ("BT1", "RT1", "DISP1") or re.fullmatch(r"SW\d|M1|CP\d", ref): continue
    if (ref, pin) not in boards["ring"]: F("ring netlist pin without pad %s:%s" % (ref, pin))
for (ref, pin), net in cn.items():
    if (ref, pin) not in boards["case_main"] and (ref, pin) not in boards["case_pins"]: info["case_netlist_offboard"] += 1

# B5 mating: tail land (u, v) -> ring (X, Y)
for f in (1, 2):
    ref = "J_BAND_A" if f == 1 else "J_BAND_B"; side = -1 if f == 1 else 1
    for s in SIZES:
        b = "flex%d-us%d" % (f, s)
        for (r_, pin), ps in boards[b].items():
            if r_ != ref: continue
            p = ps[0]; u = float(p["x"]) - 50.0; v = (80.0 - float(p["y"])) if f == 1 else (float(p["y"]) - 80.0)
            X = v - 2.5; Y = side * (3.4 + u)
            rp = boards["ring"].get((ref, pin))
            if not rp: F("mating %s %s:%s no ring land" % (b, ref, pin)); continue
            rX = float(rp[0]["x"]) - 100.0; rY = float(rp[0]["y"]) - 100.0
            dd = ((X - rX) ** 2 + (Y - rY) ** 2) ** 0.5
            info["mating"] += 1
            if dd > 0.05: F("mating %s %s:%s off %.3f" % (b, ref, pin, dd))
            if rp[0]["net"] != p["net"]: F("mating net %s %s:%s %s vs %s" % (b, ref, pin, p["net"], rp[0]["net"]))
            if "F.Cu" not in p["layers"] or "F.Cu" not in rp[0]["layers"]: F("mating face %s %s:%s" % (b, ref, pin))

# ring to case pins
want = {"CP1": ("VBUS", "P1", "VRING"), "CP2": ("USB_DN", "P2", "USB_D-"), "CP3": ("USB_DP", "P3", "USB_D+"), "CP4": ("GND", "P4", "GND")}
crow = list(csv.DictReader(open(CONT)))
for r in crow:
    info["contact_rows"] += 1
    w = want.get(r["ring_pad"])
    if not w or (r["ring_net"], r["case_pin"], r["case_net"]) != w: F("contact row %s" % r)
    h = float(r["working_height_mm"])
    if not (1.90 <= h <= 2.20): F("contact height %s %s %.3f" % (r["ring_pad"], r["ring_size"], h))
if len(crow) != 28: F("contact rows %d, want 28 (4 pins x 7 sizes)" % len(crow))
for r in rows:
    if r.get("carrier_kind") == "spring pin":
        w = want.get(r["end_A_ref"])
        if not w or r["end_B_ref"] != w[1]: F("%s spring pin pairs %s to %s" % (r["id"], r["end_A_ref"], r["end_B_ref"]))
        else: info["spring_pin_rows"] += 1
print("INFO", dict(info))
print("RESULT lines=%d fails=%d" % (len(rows), len(fails)))
sys.exit(1 if fails else 0)
