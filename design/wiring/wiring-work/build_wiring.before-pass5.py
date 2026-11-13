#!/usr/bin/env python3
"""Build design/wiring/product-wiring.csv: one line per conductor of the ring and its case.

Every value is read from the design files when this script runs:
  - netlists and parts lists (design/ecad/ring, design/ecad/case),
  - the board files (band circuits flex1/flex2 per ring size, the ring main board, the case boards),
    read with KiCad's own Python (pcbnew); the ring main board is read in place, never copied,
  - KiCad's rules check (kicad-cli pcb drc), run on each board into design/wiring/wiring-work/drc/,
  - text lines of the design notes, found by a search pattern; the line number and the matched text
    are written as the proof, so check_wiring.py can find them again.
Only the rows of design/wiring/system-joints.csv are typed by hand (joints R8/R10, R15, R16); they are merged.

Run: python design/wiring/build_wiring.py   (re-runs itself under KiCad's Python when pcbnew is missing)
"""
import csv
import heapq
import io
import json
import math
import os
import re
import subprocess
import sys

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
HERE = os.path.join(ROOT, "design/wiring")
WORK = os.path.join(HERE, "wiring-work")
KIPY = os.path.join(ROOT, "design/ecad/ring/pcb/run_kipy.sh")
KICAD_CLI = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")

try:
    import pcbnew  # noqa: F401
except ImportError:
    if os.environ.get("WIRING_REEXEC") == "1":
        raise
    env = dict(os.environ, WIRING_REEXEC="1")
    os.execve("/bin/bash", ["/bin/bash", KIPY, os.path.abspath(__file__)] + sys.argv[1:], env)

SIZES = [7, 8, 9, 10, 11, 12, 13]
RING_NETLIST = "design/ecad/ring/netlist.csv"
RING_PARTS = "design/ecad/ring/parts.csv"
CASE_NETLIST = "design/ecad/case/netlist.csv"
CASE_PARTS = "design/ecad/case/parts.csv"
RING_BOARD = "design/ecad/ring/pcb/ring.kicad_pcb"
CASE_MAIN = "design/ecad/case/pcb/case_main.kicad_pcb"
CASE_PINS = "design/ecad/case/pcb/case_pins.kicad_pcb"
FLEX = {"FLEX1": "design/ecad/band/flex1-us{}.kicad_pcb", "FLEX2": "design/ecad/band/flex2-us{}.kicad_pcb"}
TAIL_OF = {"FLEX1": "J_BAND_A", "FLEX2": "J_BAND_B"}
BI = "design/ecad/band/band-interface.md"
CBN = "design/ecad/case/pcb/board-notes.md"
CELL = "design/mfg/specs/cell.md"
RSN = "design/ecad/ring/sch-notes.md"
SCS = "design/wiring/screen-cable-study.md"
SYSTEM_JOINTS = "design/wiring/system-joints.csv"
LD = "design/wiring/lead-decisions.md"
LSPEC = "design/case/lead-specs.md"
OUT = "design/wiring/product-wiring.csv"

COLUMNS = [
    "id", "joint", "end_joints", "carrier_kind",
    "signal_A", "end_A_kind", "end_A_board", "end_A_ref", "end_A_pin", "end_A_face", "join_A",
    "signal_B", "end_B_kind", "end_B_board", "end_B_ref", "end_B_pin", "end_B_face", "join_B",
    "pairing_rule", "carrier", "carrier_net",
    "copper_mm_us7", "copper_mm_us8", "copper_mm_us9", "copper_mm_us10", "copper_mm_us11", "copper_mm_us12", "copper_mm_us13",
    "cut_mm_us7", "cut_mm_us8", "cut_mm_us9", "cut_mm_us10", "cut_mm_us11", "cut_mm_us12", "cut_mm_us13", "cut_note",
    "carrier_marking", "carrier_gauge_or_model", "solder_first", "spec_missing", "waits_for",
    "proof_A", "proof_carrier", "proof_B", "proof_join",
    "state", "state_reason", "main_board_land",
]
STATES = ["drawn and routed", "specified and landed", "drawn, not routed", "stated in text only", "not drawn"]
COMPLETE = STATES[:2]  # lead's ruling 2026-11-13: a line is complete when its state is one of these two


def p(rel):
    return os.path.join(ROOT, rel)


# ---------------------------------------------------------------- text sources
_text_cache = {}


def lines_of(rel):
    if rel not in _text_cache:
        with open(p(rel), encoding="utf-8") as f:
            _text_cache[rel] = f.read().split("\n")
    return _text_cache[rel]


def find_line(rel, pattern, nth=0):
    """Return (line_number, matched_text) of the nth line of rel matching the regex pattern."""
    rx = re.compile(pattern)
    hits = []
    for i, ln in enumerate(lines_of(rel), 1):
        m = rx.search(ln)
        if m:
            hits.append((i, m.group(0)))
    if len(hits) <= nth:
        raise SystemExit("SOURCE NOT FOUND: %s /%s/" % (rel, pattern))
    return hits[nth]


def tproof(rel, pattern, nth=0):
    n, q = find_line(rel, pattern, nth)
    return "%s:%d|%s" % (rel, n, q)


# ---------------------------------------------------------------- netlists
def read_netlist(rel):
    rows = []
    with open(p(rel), newline="", encoding="utf-8") as f:
        text = f.read().split("\n")
    rd = csv.DictReader(io.StringIO("\n".join(text)))
    for i, r in enumerate(rd, 2):
        r = {k: (v or "").strip() for k, v in r.items()}
        r["line"] = i
        r["raw"] = text[i - 1].rstrip("\r")
        rows.append(r)
    return rows


def read_parts(rel):
    with open(p(rel), newline="", encoding="utf-8") as f:
        return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]


def nl_index(rows):
    return {(r["reference"], r["pin_number"]): r for r in rows}


def nproof(rel, row):
    return "%s:%d|%s" % (rel, row["line"], row["raw"])


# ---------------------------------------------------------------- boards
_boards = {}


def board(rel):
    if rel not in _boards:
        b = pcbnew.LoadBoard(p(rel))
        pads = {}
        for fp in b.GetFootprints():
            ref = fp.GetReference()
            for pd in fp.Pads():
                key = (ref, pd.GetNumber())
                if pd.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                    lays = ["through hole"] + [n for n in ("F.Cu", "B.Cu")]
                else:
                    lays = [pcbnew.BOARD.GetStandardLayerName(l) for l in pd.GetLayerSet().CuStack()]
                pads.setdefault(key, []).append({
                    "net": pd.GetNetname(), "x": pd.GetPosition().x / 1e6, "y": pd.GetPosition().y / 1e6,
                    "layers": lays, "obj": pd})
        tracks, vias = [], []
        for t in b.GetTracks():
            tn = type(t).__name__
            if tn == "PCB_VIA":
                vias.append({"x": t.GetPosition().x / 1e6, "y": t.GetPosition().y / 1e6,
                             "r": t.GetWidth(pcbnew.F_Cu) / 2e6, "net": t.GetNetname()})
            else:
                tracks.append({"a": (t.GetStart().x / 1e6, t.GetStart().y / 1e6),
                               "b": (t.GetEnd().x / 1e6, t.GetEnd().y / 1e6),
                               "w": t.GetWidth() / 1e6, "layer": t.GetLayerName(), "net": t.GetNetname(),
                               "len": t.GetLength() / 1e6})
        drc = run_drc(rel)
        if True:
            # KiCad's list of unconnected items names pads along ratsnest edges, which varied between two runs on the
            # same file (wiring-work/diff-fields-run8-run9.log); the per-pad state is taken from the copper clusters
            drc["open_pads_drc"] = drc["open_pads"]
            drc["open_pads"] = open_pads_by_cluster(b)
        _boards[rel] = {"board": b, "pads": pads, "tracks": tracks, "vias": vias, "drc": drc}
    return _boards[rel]


def open_pads_by_cluster(b):
    """A pad is open when the copper cluster it belongs to (KiCad's connectivity: tracks, vias, arcs, filled zones)
    holds at most half of the pads of its net. Deterministic for a given board file."""
    b.BuildConnectivity()
    conn = b.GetConnectivity()
    bynet = {}
    for fp in b.GetFootprints():
        for pd in fp.Pads():
            if pd.GetNetname():
                bynet.setdefault(pd.GetNetname(), []).append(pd)
    out = set()
    for net, lst in bynet.items():
        if len(lst) < 2:
            continue
        key = lambda pd: (pd.GetParentFootprint().GetReference(), pd.GetNumber())
        seen = {}
        for start in lst:
            if key(start) in seen:
                continue
            todo, cl_items, cl_pads = [start], set(), set()
            while todo:
                it = todo.pop()
                iid = str(it.m_Uuid.AsString())
                if iid in cl_items:
                    continue
                cl_items.add(iid)
                if type(it).__name__ == "PAD":
                    cl_pads.add(key(it))
                for nx in conn.GetConnectedItems(it):
                    if nx.GetNetname() == net and str(nx.m_Uuid.AsString()) not in cl_items:
                        todo.append(nx)
            for k in cl_pads:
                seen[k] = len(cl_pads)
        for pd in lst:
            if seen.get(key(pd), 1) * 2 <= len(lst):
                out.add(key(pd))
    return out


def run_drc(rel):
    """kicad-cli rules check of one board; returns the set of (ref, pad) named in unconnected items."""
    if os.environ.get("WIRING_NO_DRC") == "1":
        return {"unconnected": None, "violations": None, "open_pads": set()}
    os.makedirs(os.path.join(WORK, "drc"), exist_ok=True)
    name = rel.replace("/", "_")
    out = os.path.join(WORK, "drc", name + ".json")
    log = os.path.join(WORK, "drc", name + ".log")
    with open(log, "w") as lf:
        rc = subprocess.call(["nice", "-n", "19", KICAD_CLI, "pcb", "drc", "--severity-all", "--all-track-errors",
                              "--format", "json", "-o", out, p(rel)], stdout=lf, stderr=subprocess.STDOUT)
    if rc != 0:
        raise SystemExit("DRC FAILED on %s (exit %d, log %s)" % (rel, rc, log))
    d = json.load(open(out))
    open_pads = set()
    rx = re.compile(r"Pad (\S+) \[([^\]]*)\] of (\S+) on")
    for it in d.get("unconnected_items", []):
        for x in it.get("items", []):
            m = rx.search(x.get("description", ""))
            if m:
                open_pads.add((m.group(3), m.group(1)))
    return {"unconnected": len(d.get("unconnected_items", [])), "violations": len(d.get("violations", [])),
            "open_pads": open_pads}


def pad_of(rel, ref, num):
    lst = board(rel)["pads"].get((ref, num))
    return lst[0] if lst else None


def bproof(rel, ref, num, net):
    return "BOARD:%s|%s:%s|%s" % (rel, ref, num, net)


# ---------------------------------------------------------------- copper path (Dijkstra over tracks, vias, pads)
def _seg_dist(pt, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((pt[0] - ax) * dx + (pt[1] - ay) * dy) / L2))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(pt[0] - cx, pt[1] - cy), t


def _seg_seg(a, b, c, d):
    """Closest points of segments ab and cd: (distance, s on ab, t on cd)."""
    best = None
    for pt, tt in ((c, 0.0), (d, 1.0)):
        dd, s = _seg_dist(pt, a, b)
        if best is None or dd < best[0]:
            best = (dd, s, tt)
    for pt, s in ((a, 0.0), (b, 1.0)):
        dd, tt = _seg_dist(pt, c, d)
        if dd < best[0]:
            best = (dd, s, tt)
    r = (b[0] - a[0], b[1] - a[1])
    q = (d[0] - c[0], d[1] - c[1])
    den = r[0] * q[1] - r[1] * q[0]
    if abs(den) > 1e-12:
        s = ((c[0] - a[0]) * q[1] - (c[1] - a[1]) * q[0]) / den
        tt = ((c[0] - a[0]) * r[1] - (c[1] - a[1]) * r[0]) / den
        if 0 <= s <= 1 and 0 <= tt <= 1:
            best = (0.0, s, tt)
    return best


def copper_graph(rel, net):
    """Graph of the copper of one net: each track is chained through every point where something touches it
    (another track's end, body or crossing, a via, a pad); a via inside a pad joins the pad."""
    bd = board(rel)
    adj = {}

    def edge(u, v, w):
        adj.setdefault(u, []).append((v, w))
        adj.setdefault(v, []).append((u, w))

    tr = [t for t in bd["tracks"] if t["net"] == net]
    vs = [v for v in bd["vias"] if v["net"] == net]
    pads = [(k, d) for k, lst in bd["pads"].items() for d in lst if d["net"] == net]
    tol = 1e-4
    att = {i: [(0.0, ("T", i, 0)), (1.0, ("T", i, 1))] for i in range(len(tr))}

    def vec(pt):
        return pcbnew.VECTOR2I(int(round(pt[0] * 1e6)), int(round(pt[1] * 1e6)))

    for i, t in enumerate(tr):
        for j in range(i + 1, len(tr)):
            u = tr[j]
            if u["layer"] != t["layer"]:
                continue
            dd, s, tt = _seg_seg(t["a"], t["b"], u["a"], u["b"])
            if dd <= (t["w"] + u["w"]) / 2 + tol:
                if dd <= tol:
                    node = ("X", i, j)
                    att[i].append((s, node))
                    att[j].append((tt, node))
                else:
                    # copper overlaps but the centre lines do not meet: the step between them counts as length
                    att[i].append((s, ("X", i, j, "i")))
                    att[j].append((tt, ("X", i, j, "j")))
                    edge(("X", i, j, "i"), ("X", i, j, "j"), dd)
        for k, v in enumerate(vs):
            dd, s = _seg_dist((v["x"], v["y"]), t["a"], t["b"])
            if dd <= v["r"] + t["w"] / 2 + tol:
                if dd <= tol:
                    att[i].append((s, ("V", k)))
                else:
                    # via copper overlaps the track but the track's centre line does not reach the via centre
                    att[i].append((s, ("VT", k, i)))
                    edge(("VT", k, i), ("V", k), dd)
        for (ref, num), d in pads:
            if t["layer"] not in d["layers"]:
                continue
            for s, pt in ((0.0, t["a"]), (1.0, t["b"])):
                if d["obj"].HitTest(vec(pt)):
                    att[i].append((s, ("P", ref, num)))
            dd, s = _seg_dist((d["x"], d["y"]), t["a"], t["b"])
            cp = (t["a"][0] + s * (t["b"][0] - t["a"][0]), t["a"][1] + s * (t["b"][1] - t["a"][1]))
            if d["obj"].HitTest(vec(cp)):
                att[i].append((s, ("P", ref, num)))
    for i, lst in att.items():
        lst.sort(key=lambda x: (x[0], str(x[1])))
        for (s0, n0), (s1, n1) in zip(lst, lst[1:]):
            edge(n0, n1, (s1 - s0) * tr[i]["len"])
    for k, v in enumerate(vs):
        for (ref, num), d in pads:
            if d["obj"].HitTest(vec((v["x"], v["y"]))):
                edge(("V", k), ("P", ref, num), 0.0)
    return adj


def dijkstra(adj, src):
    dist = {src: 0.0}
    h = [(0.0, src)]
    while h:
        d, u = heapq.heappop(h)
        if d > dist.get(u, 1e18):
            continue
        for v, w in adj.get(u, []):
            nd = d + w
            if nd < dist.get(v, 1e18) - 1e-12:
                dist[v] = nd
                heapq.heappush(h, (nd, v))
    return dist


# ---------------------------------------------------------------- helpers
def blank_row():
    return {c: "" for c in COLUMNS}


def put_lengths(row, prefix, vals):
    for s in SIZES:
        v = vals.get(s)
        row["%s_us%d" % (prefix, s)] = "" if v is None else ("%.3f" % v if isinstance(v, float) else str(v))


def spec_state(row, ends_ok, problems):
    """State of a line whose carrier is not board copper (lead, wire, tab, spring pin, part cable, inside the part).
    `specified and landed`: every end drawn with the net (ends_ok), no open connection at its pads (problems empty)
    and the carrier's full specification cited (marking, gauge or model, cut length per size or 'not size dependent');
    otherwise `drawn, not routed` with what is missing."""
    missing = []
    if not row.get("carrier_marking"):
        missing.append("colour or marking of the carrier")
    if not row.get("carrier_gauge_or_model"):
        missing.append("gauge or model of the carrier")
    cuts = [row.get("cut_mm_us%d" % s, "") for s in SIZES]
    if not all(cuts) and row.get("cut_note") != "not size dependent":
        missing.append("cut length per ring size")
    row["spec_missing"] = "; ".join(missing)
    if ends_ok and not problems and not missing:
        row["state"] = "specified and landed"
    else:
        row["state"] = "drawn, not routed"
    why = [p_ for p_ in problems] + (["specification incomplete: " + row["spec_missing"]] if missing else [])
    return "; ".join(why)


# ---------------------------------------------------------------- the band circuits
def band_lines(rn, rnx, rparts):
    rows = []
    hot = tproof(BI, r"Soldering method: HOT BAR \(thermode\)")
    joins = {
        "Alps_SKTAAAE010_pads34": ("reflow", tproof(BI, r"- Solder: reflow, paste 0\.08 thick")),
        "Alps_SKTAAAE010_4pad": ("reflow", tproof(BI, r"- Solder: reflow, paste 0\.08 thick")),
        "CP_Pad_1.6": ("reflow (disc soldered flat with SAC305 paste)",
                       tproof(BI, r"soldered flat on the land with SAC305 paste")),
        "W0525AB001D_Lands": ("hand solder (lead on land)", tproof(BI, r"solder by hand \(iron 320 C, 2 s\)")),
        "PRT1_Tabs": ("hand solder (tab on land)", tproof(BI, r"soldered by hand, low heat")),
    }
    ring_b = board(RING_BOARD)
    for flex in ("FLEX1", "FLEX2"):
        tail = TAIL_OF[flex]
        per_size = {}
        for s in SIZES:
            rel = FLEX[flex].format(s)
            bd = board(rel)
            fps = {fp.GetReference(): fp.GetFPIDAsString().split(":")[-1] for fp in bd["board"].GetFootprints()}
            nets = sorted({d["net"] for lst in bd["pads"].values() for d in lst if d["net"]})
            pairs = []
            for net in nets:
                lands = sorted(k for k, lst in bd["pads"].items() if k[0] == tail and lst[0]["net"] == net)
                far = sorted(k for k, lst in bd["pads"].items() if k[0] != tail and lst[0]["net"] == net)
                adj = copper_graph(rel, net)
                dists = {}
                for L in lands:
                    dd = dijkstra(adj, ("P",) + L)
                    for F in far:
                        dists[(L, F)] = dd.get(("P",) + F)
                cand = sorted(((d, L, F) for (L, F), d in dists.items() if d is not None))
                usedL, usedF = set(), set()
                for d, L, F in cand:
                    if L in usedL or F in usedF:
                        continue
                    usedL.add(L)
                    usedF.add(F)
                    pairs.append((net, L, F, d, "nearest"))
                for F in far:
                    if F not in usedF:
                        reach = [(dists[(L, F)], L) for L in lands if dists.get((L, F)) is not None]
                        if reach:
                            d, L = min(reach)
                            pairs.append((net, ("node", net), F, d, "node:" + "%s:%s" % L))
                        else:
                            pairs.append((net, ("node", net), F, None, "unreached"))
                for L in lands:
                    if L not in usedL:
                        pairs.append((net, L, ("node", net), None, "land-only"))
            per_size[s] = {"pairs": pairs, "fps": fps, "drc": bd["drc"]}
        # the pairing must be the same at every size
        keyset = {s: sorted((a, b[0] if isinstance(b, tuple) else b, c, e) for a, b, c, _, e in per_size[s]["pairs"])
                  for s in SIZES}
        same = all(keyset[s] == keyset[SIZES[0]] for s in SIZES)
        base = per_size[SIZES[0]]
        for net, L, F, _, how in base["pairs"]:
            row = blank_row()
            row["carrier_kind"] = "copper"
            row["carrier"] = "%s band circuit (flex1/flex2 board per size), copper of net %s" % (flex, net)
            row["carrier_net"] = net
            lens = {}
            ok_all = same
            reasons = [] if same else ["pairing differs between sizes"]
            for s in SIZES:
                for (n2, L2, F2, d2, h2) in per_size[s]["pairs"]:
                    if n2 == net and L2 == L and F2 == F:
                        lens[s] = d2
                drc = per_size[s]["drc"]
                bad = {k for k in drc["open_pads"] if k in (L, F)}
                if bad or drc["unconnected"]:
                    ok_all = False
                    reasons.append("us%d: rules check %s unconnected items, pads not joined %s" % (s, drc["unconnected"], sorted(bad)))
                if lens.get(s) is None and how != "land-only":
                    ok_all = False
                    reasons.append("us%d: no copper path" % s)
            put_lengths(row, "copper_mm", {s: (round(v, 3) if v is not None else None) for s, v in lens.items()})
            sizes_glob = FLEX[flex].format("{" + ",".join(str(s) for s in SIZES) + "}")
            # end A: the main board land (board-to-board land) or a copper node
            if L[0] == "node":
                row["end_A_kind"] = "node"
                row["end_A_board"] = flex
                row["end_A_ref"] = "copper of net " + net
                row["end_A_pin"] = how.replace("node:", "reaches land ") if how.startswith("node:") else how
                row["signal_A"] = net
                row["proof_A"] = "BOARD:%s|net %s" % (sizes_glob, net)
                row["join_A"] = "copper (same board)"
            else:
                ref, num = L
                nrow = rnx.get((ref, num))
                row["end_A_kind"] = "terminal"
                row["end_A_board"] = "ring main board"
                row["end_A_ref"] = ref
                row["end_A_pin"] = num + (" (" + nrow["pin_name"] + ")" if nrow else "")
                mb = pad_of(RING_BOARD, ref, num)
                row["end_A_face"] = (mb["layers"][0] if mb else "not on board") + "; tail land on " + \
                    ",".join(pad_of(FLEX[flex].format(SIZES[0]), ref, num)["layers"])
                row["signal_A"] = nrow["net"] if nrow else ""
                row["join_A"] = "hot bar (main board land to %s tail land %s)" % (flex, num)
                row["proof_A"] = ";".join([nproof(RING_NETLIST, nrow) if nrow else "MISSING netlist row",
                                           bproof(RING_BOARD, ref, num, mb["net"] if mb else "MISSING"),
                                           bproof(sizes_glob, ref, num, net)])
                row["proof_join"] = hot
                if not mb or (nrow and mb["net"] != nrow["net"]):
                    ok_all = False
                    reasons.append("main board land %s:%s %s" % (ref, num, "missing" if not mb else "net " + mb["net"]))
                row["main_board_land"] = "absent" if not mb else (
                    "open on main board (its copper cluster holds at most half of the net)" if (ref, num) in ring_b["drc"]["open_pads"] else "joined on main board")
            # end B: far pad on the tail
            if F[0] == "node":
                row["end_B_kind"] = "node"
                row["end_B_board"] = flex
                row["end_B_ref"] = "copper of net " + net
                row["end_B_pin"] = "no far pad"
                row["signal_B"] = net
                row["proof_B"] = "BOARD:%s|net %s" % (sizes_glob, net)
                row["join_B"] = "copper (same board)"
            else:
                ref, num = F
                fpname = base["fps"].get(ref, "")
                jn, jp = joins.get(fpname, ("", ""))
                nrow = rnx.get((ref, num))
                fpad = pad_of(FLEX[flex].format(SIZES[0]), ref, num)
                row["end_B_face"] = ",".join(fpad["layers"])
                row["end_B_board"] = flex
                row["end_B_ref"] = ref
                row["end_B_pin"] = num
                row["signal_B"] = net
                row["join_B"] = jn
                row["proof_join"] = (row["proof_join"] + ";" if row["proof_join"] else "") + jp
                row["proof_B"] = bproof(sizes_glob, ref, num, net)
                if nrow and fpname not in ("W0525AB001D_Lands",):
                    # the part pin is soldered straight onto this land: the part pin is the end
                    row["end_B_kind"] = "terminal"
                    row["proof_B"] = nproof(RING_NETLIST, nrow) + ";" + row["proof_B"]
                    row["signal_B"] = nrow["net"]
                else:
                    # a land that a lead or tab is soldered to (the part pin has its own line)
                    row["end_B_kind"] = "land"
                    row["end_B_pin"] = num + " (land of footprint %s)" % fpname
            row["proof_carrier"] = "PATH:%s|%s|%s-%s" % (sizes_glob, net, ":".join(L) if L[0] != "node" else "node",
                                                         ":".join(F) if F[0] != "node" else "node")
            if how == "land-only":
                row["proof_carrier"] = "BOARD:%s|net %s" % (sizes_glob, net)
            row["pairing_rule"] = "same net" if how == "nearest" else (
                "same net; this end's copper reaches the main board through " + how.replace("node:", "land ")
                if how.startswith("node:") else "same net; " + how)
            row["state"] = "drawn and routed" if ok_all else "drawn, not routed"
            row["state_reason"] = "; ".join(reasons) if reasons else (
                "both ends in all 7 %s board files with net %s, copper path found, rules check of each "
                "board 0 unconnected items" % (flex.lower(), net))
            rows.append(row)
    return rows


def band_internal_lines(rnx, rparts):
    """Netlist pins of the switches that are not soldered (joined to the soldered pin inside the part)."""
    rows = []
    fl = FLEX["FLEX1"].format(SIZES[0])
    bd = board(fl)
    src = tproof(BI, r"Terminals 1 and 2 are not soldered: Alps' circuit diagram joins 1 to 3 and 2 to 4")
    for (ref, num), r in sorted(rnx.items()):
        if not re.match(r"SW\d$", ref):
            continue
        if (ref, num) in bd["pads"]:
            continue
        mate = {"1": "3", "2": "4", "3": "1", "4": "2"}[num]
        row = blank_row()
        row.update({
            "carrier_kind": "inside the part", "signal_A": r["net"], "end_A_kind": "terminal", "end_A_board": "off board",
            "end_A_ref": ref, "end_A_pin": num, "end_A_face": "not soldered", "join_A": "none (not soldered)",
            "signal_B": rnx[(ref, mate)]["net"], "end_B_kind": "internal", "end_B_board": "off board", "end_B_ref": ref,
            "end_B_pin": mate, "end_B_face": "inside the switch", "join_B": "inside the part",
            "pairing_rule": "same net (switch contact side)", "carrier": "the switch's own contact (Alps SKTAAAE010)",
            "carrier_net": r["net"], "proof_A": nproof(RING_NETLIST, r), "proof_B": nproof(RING_NETLIST, rnx[(ref, mate)]),
            "proof_carrier": src, "proof_join": src, "cut_note": "not size dependent",
            "carrier_marking": "Alps terminal numbers 1 to 4 (catalog page 2, Drawing No.1)",
            "carrier_gauge_or_model": "Alps SKTAAAE010", "solder_first": "not soldered",
        })
        why = spec_state(row, True, [])
        row["state_reason"] = why or "pin in the netlist; not soldered by design; joined to pin %s inside the part (%s)" % (
            mate, src.split("|")[0])
        rows.append(row)
    return rows


def motor_lead_lines(rnx):
    rows = []
    n, line = None, None
    for i, ln in enumerate(lines_of(BI), 1):
        if "Land 1 (pad 1) = " in ln and "M1 pin 1" in ln:
            n, line = i, ln
            break
    if n is None:
        raise SystemExit("SOURCE NOT FOUND: motor lead colours in " + BI)
    hn, _ = find_line(BI, r"^\| US \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \|")
    cn, cline = find_line(BI, r"^\| lead cut length, mm \|.*")
    cuts = [c.strip() for c in cline.strip("|").split("|")[1:]]
    gauge = tproof(BI, r"lead wire AWG32")
    join = tproof(BI, r"solder by hand \(iron 320 C, 2 s\)")
    for m in re.finditer(r"Land (\d) \(pad \d\) = (\w+) lead = M1 pin (\d) = net (\w+) = J_BAND_A land (\d)", line):
        land, colour, pin, net, jl = m.groups()
        r = rnx[("M1", pin)]
        row = blank_row()
        row.update({
            "joint": "R5", "end_joints": "R1", "carrier_kind": "lead",
            "signal_A": r["net"], "end_A_kind": "terminal", "end_A_board": "off board (motor M1)", "end_A_ref": "M1",
            "end_A_pin": pin + " (" + r["pin_name"] + ")", "end_A_face": "lead from the motor rim",
            "join_A": "made by the motor maker",
            "signal_B": net, "end_B_kind": "land", "end_B_board": "FLEX1", "end_B_ref": "M1",
            "end_B_pin": land + " (land of footprint W0525AB001D_Lands)",
            "end_B_face": ",".join(pad_of(FLEX["FLEX1"].format(SIZES[0]), "M1", land)["layers"]),
            "join_B": "hand solder (iron 320 C, 2 s)",
            "pairing_rule": "same net", "carrier": "%s lead wire AWG32 of the motor" % colour, "carrier_net": net,
            "proof_A": nproof(RING_NETLIST, r),
            "proof_B": bproof(FLEX["FLEX1"].format("{" + ",".join(map(str, SIZES)) + "}"), "M1", land, net),
            "proof_carrier": "%s:%d|%s;%s;%s:%d|%s" % (BI, n, m.group(0), gauge, BI, cn, cline.strip()),
            "proof_join": join,
        })
        put_lengths(row, "cut_mm", dict(zip(SIZES, cuts)))
        row.update({"carrier_marking": colour + " insulation", "carrier_gauge_or_model": "AWG32 (Jinlong W0525AB001D lead)",
                    "solder_first": "one soldered end (the motor end is made by the maker)"})
        fb = board(FLEX["FLEX1"].format(SIZES[0]))
        probs = ["us%d: M1 land %s not joined to its net" % (s, land) for s in SIZES
                 if ("M1", land) in board(FLEX["FLEX1"].format(s))["drc"]["open_pads"]]
        why = spec_state(row, pad_of(FLEX["FLEX1"].format(SIZES[0]), "M1", land) is not None, probs)
        row["state_reason"] = why or ("motor pin in the netlist, land with net %s in all 7 flex1 boards without open "
                                      "connection; colour, gauge and cut length per size in %s lines %d, %s, %d" % (
                                          net, BI, n, gauge.split("|")[0].split(":")[1], cn))
        rows.append(row)
    return rows


def screen_lines(rn, rnx):
    rows = []
    ring_b = board(RING_BOARD)
    mapping = tproof(RSN, r"contact k of the tail on position k of J1")
    plug = tproof(SCS, r"the cable is plugged into J1 with the lever open")
    place = tproof(SCS, r"J1 centre at \(-4\.933, -0\.003\)")
    under = tproof(SCS, r"Face F is the board's under face")
    contact_no = tproof(SCS, r"back view draws the 15 fingers as pads")
    pinmap = tproof(RSN, r"closed by the table on page 5 of the Tailor sheet")
    thick = tproof(SCS, r"0\.2 \+-0\.03 including the polyimide \(PI\) stiffener")
    pitch = tproof(SCS, r"15 at 0\.297 pitch \(0\.3\)")
    pins = sorted({r["pin_number"] for r in rn if r["reference"] == "J1" and r["net"]}, key=lambda x: int(x))
    for k in pins:
        a = rnx[("DISP1", k)]
        b = rnx[("J1", k)]
        mb = pad_of(RING_BOARD, "J1", k)
        row = blank_row()
        row.update({
            "joint": "R13", "carrier_kind": "part cable",
            "signal_A": a["net"] or "(no connect, %s)" % a["pin_name"], "end_A_kind": "terminal",
            "end_A_board": "off board (screen DISP1)", "end_A_ref": "DISP1", "end_A_pin": k + " (" + a["pin_name"] + ")",
            "end_A_face": "contact on the cable's back face", "join_A": "made by the screen maker (cable bonded on the glass)",
            "signal_B": b["net"] or "(no connect, %s)" % b["pin_name"], "end_B_kind": "terminal",
            "end_B_board": "ring main board", "end_B_ref": "J1", "end_B_pin": k + " (" + b["pin_name"] + ")",
            "end_B_face": mb["layers"][0] if mb else "not on board",
            "join_B": "pressed contact (cable plugged into J1, lever closed)",
            "pairing_rule": "contact k of the screen cable on position k of J1",
            "carrier": "the screen's own cable (Tailor TOH095XVT-01), contact %s" % k, "carrier_net": b["net"],
            "proof_A": nproof(RING_NETLIST, a),
            "proof_B": nproof(RING_NETLIST, b) + ";" + bproof(RING_BOARD, "J1", k, mb["net"] if mb else "MISSING"),
            "proof_carrier": mapping + ";" + place, "proof_join": plug,
            "main_board_land": "absent" if not mb else (
                "open on main board (its copper cluster holds at most half of the net)" if ("J1", k) in ring_b["drc"]["open_pads"] else "joined on main board"),
        })
        ok = mb is not None and mb["net"] == b["net"] and a["net"] == b["net"]
        face_ok = mb is not None and mb["layers"][0] == "B.Cu"
        row["proof_carrier"] += ";" + under
        row["proof_A"] += ";" + contact_no + ";" + pinmap
        row["proof_carrier"] += ";" + thick + ";" + pitch
        row.update({"carrier_marking": "contact number %s of the maker drawing" % k,
                    "carrier_gauge_or_model": "Tailor TOH095XVT-01 stock cable, 15 contacts at 0.3 pitch, 0.2 thick at the contact end",
                    "cut_note": "not size dependent", "solder_first": "no soldered end (pressed contact in J1)"})
        probs = []
        if not ok:
            probs.append("J1 pad %s %s on the main board" % (k, "missing" if not mb else "has net " + mb["net"]))
        elif not face_ok:
            probs.append("J1 pad %s is on %s in the board file, the under face (screen-cable-study.md: Face F is the "
                         "under face); the stock cable of layout C reaches J1 only on the screen face "
                         "(screen-cable-study.md section 4.3)" % (k, mb["layers"][0]))
        if mb is not None and ("J1", k) in ring_b["drc"]["open_pads"]:
            probs.append("main board copper: J1 pad %s not joined to its net" % k)
        why = spec_state(row, ok, probs)
        row["state_reason"] = why or ("both pins in the netlist, J1 pad %s on the screen face (B.Cu) with net %s, no open "
                                      "connection; cable specified in the maker drawing" % (k, mb["net"]))
        rows.append(row)
    return rows


def antenna_lines(rn, rnx):
    rows = []
    rb = board(RING_BOARD)
    for r in sorted((r for r in rn if r["reference"] == "ANT1"), key=lambda r: r["pin_number"]):
        net = r["net"]
        others = sorted((x["reference"], x["pin_number"]) for x in rn if x["net"] == net and x["reference"] != "ANT1")
        mb = pad_of(RING_BOARD, "ANT1", r["pin_number"])
        row = blank_row()
        row.update({
            "joint": "R11" if r["pin_number"] == "1" else "R12", "carrier_kind": "copper",
            "signal_A": net, "end_A_kind": "terminal", "end_A_board": "ring main board", "end_A_ref": "ANT1",
            "end_A_pin": r["pin_number"] + " (" + r["pin_name"] + ")", "end_A_face": mb["layers"][0] if mb else "not on board",
            "join_A": "reflow (part on the main board)",
            "signal_B": net, "end_B_kind": "node", "end_B_board": "ring main board", "end_B_ref": "copper of net " + net,
            "end_B_pin": " ".join("%s:%s" % o for o in others) if net != "GND" else "ground",
            "join_B": "copper (same board)", "pairing_rule": "same net", "carrier": "main board copper, net " + net,
            "carrier_net": net, "proof_A": nproof(RING_NETLIST, r) + ";" + bproof(RING_BOARD, "ANT1", r["pin_number"],
                                                                                  mb["net"] if mb else "MISSING"),
            "proof_B": "BOARD:%s|net %s" % (RING_BOARD, net), "proof_carrier": "BOARD:%s|net %s" % (RING_BOARD, net),
            "cut_note": "",
        })
        opens = [o for o in [("ANT1", r["pin_number"])] + (others if net != "GND" else []) if o in rb["drc"]["open_pads"]]
        if not mb:
            row["state"], row["state_reason"] = "drawn, not routed", "ANT1 pad missing on the main board"
        elif opens:
            row["state"] = "drawn, not routed"
            row["state_reason"] = "main board copper: not joined to its net at %s" % ", ".join("%s:%s" % o for o in opens)
        else:
            row["state"] = "drawn and routed"
            row["state_reason"] = "main board copper: ANT1 pad %s joined to its net" % r["pin_number"]
        row["main_board_land"] = row["state_reason"]
        rows.append(row)
    return rows


# ---------------------------------------------------------------- the case
def case_lines(cn, cnx):
    rows = []
    cm, cp = board(CASE_MAIN), board(CASE_PINS)
    hn, _ = find_line(CBN, r"^### Wiring table \(replaces part f\)")
    gauge = tproof(CBN, r"Wire: 30 AWG \(conductor 0\.25 mm\)")
    colours = tproof(CBN, r"lead 1 red = \+, lead 2 black = -")
    joinp = tproof(CBN, r"Pad names for the wires \(solder joints\)")
    table = []
    for i, ln in enumerate(lines_of(CBN)[hn:hn + 20], hn + 1):
        m = re.match(r"^\| (W\d) \| ([^|]+) \| (W\d) \| (\S+) \| ([\d.]+) \| ([\d.]+) \| (\d+) \|", ln)
        if m:
            table.append((i, m))
    for i, m in table:
        w, frm, to, net, path, cut, cb = [g.strip() for g in m.groups()]
        r = cnx.get((to, "1"))
        row = blank_row()
        mpad = pad_of(CASE_MAIN, to, "1")
        row.update({"carrier_kind": "wire" if frm.startswith("WP") else "lead", "joint": "C5" if frm.startswith("WP") else
                    ("C1" if w == "W5" else "C2"),
                    "signal_B": r["net"] if r else "", "end_B_kind": "terminal", "end_B_board": "case main board (PCB1)",
                    "end_B_ref": to, "end_B_pin": "1", "end_B_face": ",".join(mpad["layers"]) if mpad else "not on board",
                    "join_B": "hand solder", "carrier_net": net, "cut_note": "not size dependent",
                    "proof_B": (nproof(CASE_NETLIST, r) if r else "MISSING") + ";" +
                    bproof(CASE_MAIN, to, "1", mpad["net"] if mpad else "MISSING"),
                    "proof_join": joinp})
        put_lengths(row, "cut_mm", {s: cut for s in SIZES})
        opens = []
        if mpad and (to, "1") in cm["drc"]["open_pads"]:
            opens.append("PCB1 %s" % to)
        if frm.startswith("WP"):
            ppad = pad_of(CASE_PINS, frm, "1")
            row.update({"signal_A": ppad["net"] if ppad else "", "end_A_kind": "land", "end_A_board": "case pin board (PCB2)",
                        "end_A_ref": frm, "end_A_pin": "1", "end_A_face": ",".join(ppad["layers"]) if ppad else "not on board",
                        "join_A": "hand solder", "pairing_rule": "same net",
                        "carrier": "wire 30 AWG, cut %s mm (path %s mm)" % (cut, path),
                        "proof_A": bproof(CASE_PINS, frm, "1", ppad["net"] if ppad else "MISSING"),
                        "proof_carrier": "%s:%d|%s;%s" % (CBN, i, m.group(0), gauge)})
            if ppad and (frm, "1") in cp["drc"]["open_pads"]:
                opens.append("PCB2 %s" % frm)
            ok = bool(ppad and mpad and r and ppad["net"] == mpad["net"] == r["net"])
        else:
            pin = "1" if w == "W5" else "2"
            c = cnx[("BT1", pin)]
            row.update({"signal_A": c["net"], "end_A_kind": "terminal", "end_A_board": "off board (case cell BT1)",
                        "end_A_ref": "BT1", "end_A_pin": pin + " (" + c["pin_name"] + ")", "end_A_face": "flying lead",
                        "join_A": "made by the cell maker", "pairing_rule": "same net",
                        "carrier": "cell's own flying lead (%s), cut %s mm (path %s mm)" % (
                            "red +" if pin == "1" else "black -", cut, path),
                        "proof_A": nproof(CASE_NETLIST, c),
                        "proof_carrier": "%s:%d|%s;%s" % (CBN, i, m.group(0), colours)})
            ok = bool(mpad and r and mpad["net"] == r["net"] == c["net"])
        if frm.startswith("WP"):
            cn_, cl_ = find_line(LD, r"^\| case wires W1 to W4 and W7: colour \|.*")
            mm = re.search(r"%s \(%s\) (\w+)" % (w, re.escape(net)), cl_)
            gq = re.search(r"All five are 30 AWG stranded hook-up wire \(conductor 0\.25 mm\)", cl_)
            row.update({"carrier_marking": (mm.group(1) + " insulation") if mm else "",
                        "carrier_gauge_or_model": "30 AWG stranded hook-up wire" if gq else "",
                        "solder_first": "not stated in the files"})
            if mm:
                row["carrier"] = "wire 30 AWG stranded, %s, cut %s mm (path %s mm)" % (mm.group(1), cut, path)
                row["proof_carrier"] += ";%s:%d|%s" % (LD, cn_, mm.group(0))
            if gq:
                row["proof_carrier"] += ";%s:%d|%s" % (LD, cn_, gq.group(0))
        else:
            cn_, cl_ = find_line(LD, r"^\| case cell BT1 leads \(wiring lines for joints C1, C2\) \|.*")
            q1 = re.search(r"the leads are used as the maker delivers them, never replaced", cl_)
            q2 = re.search(r"red probe on the red lead: the reading must be positive, between 3\.0 and 4\.35 V", cl_)
            row.update({"carrier_marking": "red (+)" if w == "W5" else "black (-)",
                        "carrier_gauge_or_model": ("DNK852338 own lead as delivered (no gauge stated by the maker; "
                                                   "polarity measured before cutting)") if (q1 and q2) else "",
                        "solder_first": "one soldered end (the cell end is made by the maker)"})
            for q in (q1, q2):
                if q:
                    row["proof_carrier"] += ";%s:%d|%s" % (LD, cn_, q.group(0))
        probs = ["open connection: " + x for x in opens] + ([] if ok else ["pad or net mismatch"])
        why = spec_state(row, ok, probs)
        row["state_reason"] = why or ("both pads drawn with net %s; pads joined to their net on the case boards; "
                                      "cut length in %s line %d" % (net, CBN, i))
        rows.append(row)
    # thermistor TH1: its own two leads into PCB1 holes TH1.1 and TH1.2
    cutp = find_line(CBN, r"TH1 is unchanged \(10 mm leads\)")
    for pin in ("1", "2"):
        r = cnx[("TH1", pin)]
        mpad = pad_of(CASE_MAIN, "TH1", pin)
        row = blank_row()
        row.update({"joint": "C3", "carrier_kind": "lead", "signal_A": r["net"], "end_A_kind": "terminal",
                    "end_A_board": "off board (thermistor on the cell face)", "end_A_ref": "TH1", "end_A_pin": pin,
                    "end_A_face": "lead", "join_A": "made by the thermistor maker",
                    "signal_B": mpad["net"] if mpad else "", "end_B_kind": "land", "end_B_board": "case main board (PCB1)",
                    "end_B_ref": "TH1", "end_B_pin": pin + " (plated hole of footprint NTC_wired)",
                    "end_B_face": ",".join(mpad["layers"]) if mpad else "not on board", "join_B": "hand solder",
                    "pairing_rule": "same net", "carrier": "thermistor's own lead, 10 mm", "carrier_net": r["net"],
                    "cut_note": "not size dependent", "proof_A": nproof(CASE_NETLIST, r),
                    "proof_B": bproof(CASE_MAIN, "TH1", pin, mpad["net"] if mpad else "MISSING"),
                    "proof_carrier": "%s:%d|%s;%s" % (CBN, cutp[0], cutp[1], tproof(CBN, r"glued on the cell face, with two flying leads soldered into the two plated holes TH1\.1 and TH1\.2")),
                    "proof_join": joinp})
        put_lengths(row, "cut_mm", {s: "10" for s in SIZES})
        ok = bool(mpad and mpad["net"] == r["net"])
        tn_, tl_ = find_line(LD, r"^\| case thermistor TH1 leads \(joint C3\) and bead size \|.*")
        qa = re.search(r"two bare leads of 0\.5 mm tin plated 42 alloy at 2\.54 mm pitch; no insulation, no colour, no polarity", tl_)
        qb = re.search(r"soldered into the two plated holes TH1\.1 and TH1\.2 \(either way round\), the joint 5 mm or more from the bead", tl_)
        sp_ = tproof(LSPEC, r"0\.5 tin plated 42 alloy")
        row.update({"carrier_marking": "bare, no polarity" if qa else "",
                    "carrier_gauge_or_model": "Semitec 103AT-2 own lead as delivered (0.5 mm tin plated 42 alloy)" if qa else "",
                    "solder_first": "one soldered end (the bead end is the maker's); either way round, joint 5 mm or more from the bead" if qb else
                    "one soldered end (the thermistor end is made by the maker)"})
        for q in (qa, qb):
            if q:
                row["proof_carrier"] += ";%s:%d|%s" % (LD, tn_, q.group(0))
        row["proof_carrier"] += ";" + sp_
        probs = ["open connection at TH1.%s" % pin] if ("TH1", pin) in cm["drc"]["open_pads"] else []
        why = spec_state(row, ok, probs)
        row["state_reason"] = why or "thermistor pin in the netlist; hole TH1.%s on PCB1 with net %s; lead length 10 mm in %s line %d" % (
            pin, mpad["net"] if mpad else "-", CBN, cutp[0])
        rows.append(row)
    return rows


# ---------------------------------------------------------------- hand rows
def system_rows():
    with open(p(SYSTEM_JOINTS), newline="", encoding="utf-8") as f:
        rows = []
        for r in csv.DictReader(f):
            row = blank_row()
            for k, v in r.items():
                if k in row:
                    row[k] = (v or "").strip()
            row["state_reason"] = (row["state_reason"] + " " if row["state_reason"] else "") + "(row typed by hand in system-joints.csv)"
            rows.append(row)
    return rows


# ---------------------------------------------------------------- main
def main():
    rn = read_netlist(RING_NETLIST)
    cn = read_netlist(CASE_NETLIST)
    rnx, cnx = nl_index(rn), nl_index(cn)
    rparts = read_parts(RING_PARTS)
    rows = []
    blines = band_lines(rn, rnx, rparts)
    joint_by_far = {"SW": "R3", "CP": "R9"}
    for r in blines:
        far = r["end_B_ref"]
        if r["carrier_net"] == "GND" and far.startswith("SW"):
            r["joint"] = "R4"
        elif far.startswith("SW"):
            r["joint"] = "R3"
        elif far.startswith("CP"):
            r["joint"] = "R9"
        elif far == "M1":
            r["joint"] = "R5"
        elif far == "PRT1":
            r["joint"] = "R7" if r["carrier_net"] == "NTC" else "R6"
        else:
            r["joint"] = "R1" if "FLEX1" in r["carrier"] else "R2"
        r["end_joints"] = ("R1" if "FLEX1" in r["carrier"] else "R2") if r["end_A_kind"] == "terminal" else ""
    rows += blines
    for r in band_internal_lines(rnx, rparts):
        r["joint"] = "R4" if r["carrier_net"] == "GND" else "R3"
        rows.append(r)
    rows += motor_lead_lines(rnx)
    rows += screen_lines(rn, rnx)
    rows += antenna_lines(rn, rnx)
    rows += case_lines(cn, cnx)
    rows += system_rows()
    for r in rows:
        if r["state"] in COMPLETE or r["carrier_kind"] == "none" or r["waits_for"]:
            continue
        need = []
        if r["spec_missing"]:
            src = CBN if "case" in (r["end_A_board"] + r["end_B_board"]) else BI
            need.append("%s: %s" % (src, r["spec_missing"]))
        reason = r["state_reason"].replace("specification incomplete: " + r["spec_missing"], "") if r["spec_missing"] else r["state_reason"]
        rest = [x for x in reason.split("; ") if x.strip()]
        if rest:
            where = RING_BOARD if "main board" in r["state_reason"] or "J1 pad" in r["state_reason"] else "design files"
            need.append("%s: %s" % (where, "; ".join(rest)))
        r["waits_for"] = " | ".join(need)
    order = {j: i for i, j in enumerate(["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12",
                                         "R13", "R15", "R16", "C1", "C2", "C3", "C4", "C5", "C6"])}
    rows.sort(key=lambda r: (order.get(r["joint"], 99), r["end_A_ref"], r["end_A_pin"], r["end_B_ref"], r["end_B_pin"],
                             r["carrier_net"]))
    for i, r in enumerate(rows, 1):
        r["id"] = "W%03d" % i
    out = p(OUT)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("lines written:", len(rows), "->", OUT)
    counts = {}
    for r in rows:
        counts[r["state"]] = counts.get(r["state"], 0) + 1
    for s in STATES:
        print("state %-22s %d" % (s, counts.get(s, 0)))
    done = sum(counts.get(s, 0) for s in COMPLETE)
    print("complete (drawn and routed or specified and landed): %d of %d" % (done, len(rows)))


if __name__ == "__main__":
    main()
