"""wiring (a helper of electronics.py, no extract() of its own): the connection map of the electronics record.

Source: design/wiring/connections.md, its "Part 1" table: one row per joint between boards and off-board parts. The row
count must equal the count the file states ("Count: N joints"); a row the file says is not a joint (it starts its
"Drawn?" cell with "No joint") is left out, as the file leaves it out of its count.

Added from other design files, by section, when they are there:
  design/ecad/band/band-interface.md      section 2 (the lands of each flexible tail on the main board) and section 6
                                          (the motor leads, with the lead cut length per ring size);
  design/ecad/case/pcb/board-notes.md     "Wiring table" (the case wires, with their cut lengths) and "Part g" (the ring
                                          pad to case pin table).
The "Stated at" cell of a row names files by short keys (RN, AS, ...); the key table at the head of connections.md turns
them into files. Nothing here holds a ring value: ends, nets, carriers and lengths are read from those files. What is
held here is the vocabulary of connections.md: which words of an end name a board and which name a part (NODE_RULES), and
which words of a carrier name how a joint is made (HOW_RULES).
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import boards as boardlist  # noqa: E402
from lib import csvread, md  # noqa: E402
from lib.source import pointer  # noqa: E402

CONNECTIONS = "design/wiring/connections.md"
BAND_INTERFACE = "design/ecad/band/band-interface.md"
CASE_NOTES = "design/ecad/case/pcb/board-notes.md"

# (pattern on the text of an end, node id, plain label, bom, references). First match wins. A node is a part when it has references or a
# label from the text; the board nodes come after, so a text that names a part and a board names the part.
NODE_RULES = [
    (r"case spring pins?", "case-spring-pins", "Spring pins", "case", ["P1-P4"]),
    (r"case electrode", "case-touch-electrode", "Touch electrode", "case", ["E1"]),
    (r"case cell", "case-cell", "Battery cell", "case", ["BT1"]),
    (r"case ntc", "case-thermistor", "Thermistor", "case", ["TH1"]),
    (r"usb-c socket", "case-usb-socket", "USB-C socket", "case", ["J1"]),
    (r"switch terminal", "ring-switches", "Joystick switches", "ring", ["SW1", "SW2", "SW3", "SW4", "SW5"]),
    (r"\bmotor\b", "ring-motor", "Vibration motor", "ring", ["M1"]),
    (r"^cell bt1", "ring-cell", "Battery cell", "ring", ["BT1"]),
    (r"thermistor rt1", "ring-thermistor", "Thermistor", "ring", ["RT1"]),
    (r"charging pads cp1", "ring-charging-pads", "Charging pads", "ring", ["CP1", "CP2", "CP3", "CP4"]),
    (r"protection circuit", "ring-cell-protection", "Cell protection circuit", "ring", ["PRT1"]),
    (r"antenna ant1", "ring-antenna", "Antenna", "ring", ["ANT1"]),
    (r"screen tail", "ring-screen", "Screen", "ring", ["DISP1"]),
    (r"ring band metal", "ring-band-metal", "Band metal", "ring", []),
    (r"flex tail a|flex1|tail a\b", "band-1", None, None, None),
    (r"flex tail b|flex2|tail b\b|tail b has", "band-2", None, None, None),
    (r"case pcb2|^pcb2", "case-pins", None, None, None),
    (r"case pcb1|case board|\bu2 pin|\bts net", "case-main", None, None, None),
    (r"ring board|board connector|gnd net on board|match chain", "ring", None, None, None),
]
# (pattern on the carrier or the net words, kind in words). First match wins.
HOW_RULES = [
    (r"hot[- ]?bar", "hot bar"),
    (r"spring pin", "spring pin"),
    (r"capacitive", "touch, no contact"),
    (r"connector|inserted", "connector"),
    (r"\blead|\bwire", "lead wire"),
    (r"gold", "gold disc"),
    (r"track", "board track"),
    (r"solder|reflow|surface mount|termination|tabs", "soldered land"),
    (r"flex", "flex circuit line"),
    (r"not stated", "not stated"),
]
KEY_LINE = re.compile(r"\b([A-Z]{2,4})\s+(\d+(?:\s*(?:,|and|to)\s*\d+)*)")


class WiringError(Exception):
    """connections.md is there but cannot be read as the connection list."""


def clean(text):
    return re.sub(r"\s+", " ", text.replace("`", "")).strip()


def read_keys(text):
    """{key: repo-relative file} from the key table at the head of connections.md."""
    out = {}
    for t in md.tables(text):
        if [c.lower() for c in t["columns"][:2]] == ["key", "file"]:
            for key, file in t["rows"]:
                out[key.strip()] = clean(file)
            break
    return out


def part1_rows(text):
    """(table, rows kept as (row cells, line)) of the 'Part 1' table; WiringError when it is not there."""
    sec = md.section(text, r"^Part 1\b", level=2)
    if sec is None:
        raise WiringError("connections.md has no 'Part 1' section")
    first, last, _ = sec
    tabs = md.tables(text, first, last)
    if not tabs:
        raise WiringError("the 'Part 1' section of connections.md holds no table")
    t = tabs[0]
    cols = [c.strip() for c in t["columns"]]
    want = ["#", "From", "To", "Carrier", "Conductors", "Net names", "Stated at", "Drawn?"]
    if len(cols) < 8 or not all(c.lower().startswith(w.lower()) for c, w in zip(cols, want)):
        raise WiringError(f"the 'Part 1' table has columns {cols}, not {want}")
    return [(row, ln) for row, ln in zip(t["rows"], t["row_lines"])]


PRODUCT_WIRING = "design/wiring/product-wiring.csv"
# The two states in which design/wiring/build_wiring.py (COMPLETE) calls a conductor line complete; a test compares them with that file.
COMPLETE_STATES = ("drawn and routed", "specified and landed")


def drawn_state(cell):
    """'not-drawn' when the Drawn? cell says not drawn; 'text-only' when it begins "Stated in text only"; else 'drawn'."""
    if re.match(r"not drawn\b", cell, re.I):
        return "not-drawn"
    if re.match(r"stated in text only\b", cell, re.I):
        return "text-only"
    return "drawn"


def stated_open(text):
    """Ids the Count line sentence names as 'stated in text only' ('R10, R15 and R16 are stated in text only' or 'except R16, which is stated in text only'), or None."""
    m = (re.search(r"((?:[RC]\d+,\s*)*[RC]\d+(?:\s+and\s+[RC]\d+)?)\s+(?:are|is)\s+stated\s+in\s+text\s+only", text)
         or re.search(r"except\s+((?:[RC]\d+,\s*)*[RC]\d+(?:\s+and\s+[RC]\d+)?),?\s+(?:which|that)\s+(?:are|is)\s+stated\s+in\s+text\s+only", text))
    return re.findall(r"[RC]\d+", m.group(1)) if m else None


def conductor_counts(ctx):
    """{joint: {'complete': n, 'total': m}} from the `joint` and `state` columns of product-wiring.csv (a line whose carrier_kind
    is 'none' is no conductor); {} when the file is not there or lacks a column."""
    from lib import csvread  # noqa: PLC0415

    f = ctx.source_path(PRODUCT_WIRING)
    if not f.is_file():
        return {}
    try:
        rows = csvread.read(f, ["joint", "state", "carrier_kind"])
    except Exception:  # noqa: BLE001  (a file the reader cannot read: no counts, said by its absence)
        return {}
    out = {}
    for r in rows:
        c = r["cells"]
        if c["carrier_kind"].strip() == "none" or not c["joint"].strip():
            continue
        e = out.setdefault(c["joint"].strip(), {"complete": 0, "total": 0})
        e["total"] += 1
        e["complete"] += 1 if c["state"].strip() in COMPLETE_STATES else 0
    return out


SIZE_COLUMN = re.compile(r"^(copper|cut)_mm_us(\d+)$")


def conductor_data(ctx):
    """(per joint {'lines': [...], 'none': [...]}, info) from design/wiring/product-wiring.csv. Each conductor line carries its signal at
    each end, its first and last terminal (board, part, pin, face, how it is joined), what carries it, its state and its lengths per ring
    size (the columns copper_mm_us<N> and cut_mm_us<N>, when filled), and its source {file, line}. A line whose carrier_kind is 'none'
    is no conductor: it goes in 'none' with its carrier text as the reason. `info` is the conductor_file record of the map: status ok,
    missing or unreadable, the whole-product count of complete and total conductors."""
    f = ctx.source_path(PRODUCT_WIRING)
    src = pointer(PRODUCT_WIRING, None)
    empty = {"source": src, "status": "ok", "note": None, "complete": 0, "total": 0, "no_conductor": 0}
    if not f.is_file():
        return {}, {**empty, "status": "missing", "note": f"{PRODUCT_WIRING} is not there: no conductor list"}
    try:
        rows = csvread.read(f, ["id", "joint", "state", "carrier_kind", "carrier"])
    except Exception as e:  # noqa: BLE001  (a file the reader cannot read: said in words, never shown as fine)
        return {}, {**empty, "status": "unreadable", "note": f"{PRODUCT_WIRING} cannot be read: {e}"}
    by, info = {}, dict(empty)
    for r in rows:
        c, ptr = r["cells"], pointer(PRODUCT_WIRING, r["line"])
        slot = by.setdefault(c["joint"].strip(), {"lines": [], "none": []})
        if c["carrier_kind"].strip() == "none":
            slot["none"].append({"id": c["id"], "reason": c["carrier"], "state": c["state"], "state_reason": c.get("state_reason", ""), "source": ptr})
            info["no_conductor"] += 1
            continue
        end = lambda t: {"board": c.get(f"end_{t}_board", ""), "part": c.get(f"end_{t}_ref", ""), "pin": c.get(f"end_{t}_pin", ""),  # noqa: E731
                         "face": c.get(f"end_{t}_face", ""), "join": c.get(f"join_{t}", "")}
        lengths = []
        for col, v in c.items():
            m = SIZE_COLUMN.match(col)
            if m and v.strip():
                lengths.append({"size": f"US {m.group(2)}", "kind": m.group(1), "mm": v})
        slot["lines"].append({
            "id": c["id"], "signal_a": c.get("signal_A", ""), "signal_b": c.get("signal_B", ""), "first": end("A"), "last": end("B"),
            "carrier": {"kind": c["carrier_kind"], "text": c["carrier"]}, "state": c["state"], "state_reason": c.get("state_reason", ""),
            "lengths": lengths, "source": ptr})
        info["total"] += 1
        info["complete"] += 1 if c["state"].strip() in COMPLETE_STATES else 0
    return by, info


def stated_count(text):
    m = re.search(r"^Count:\s*(\d+)\s+joints", text, re.M)
    return int(m.group(1)) if m else None


def node_of(end_text, tokens_by_bom, nodes):
    """The node id of an end; the node is added to `nodes` on first use."""
    t = clean(end_text)
    for pat, nid, label, bom, refs in NODE_RULES:
        if not re.search(pat, t, re.I):
            continue
        if nid in nodes:
            return nid
        group = next((g for g in boardlist.GROUPS if g["id"] == nid), None)
        if group is not None:
            nodes[nid] = {"id": nid, "label": group["title"], "kind": "board", "board": nid, "scope": None, "part_ids": []}
            return nid
        ids = []
        for r in refs:
            pid = boardlist.part_id_of(r, bom, tokens_by_bom[bom])
            if pid:
                ids.append(pid)
        nodes[nid] = {"id": nid, "label": label, "kind": "part", "board": None, "scope": bom, "part_ids": ids}
        return nid
    nid = "unmapped-" + re.sub(r"[^a-z0-9]+", "-", t.lower())[:40].strip("-")
    nodes.setdefault(nid, {"id": nid, "label": re.split(r"[(,:]", t)[0].strip().capitalize() or "Unnamed end", "kind": "part", "board": None,
                           "scope": None, "part_ids": []})
    return nid


def how_made(carrier, conductors):
    text = clean(carrier)
    for pat, kind in HOW_RULES:
        if re.search(pat, text, re.I):
            return {"kind": kind, "text": text, "conductors": clean(conductors)}
    return {"kind": "other", "text": text, "conductors": clean(conductors)}


def proofs(stated, keys, rel_exists, section_of):
    """[{file, lines, section}] from a 'Stated at' cell."""
    out = {}
    for m in KEY_LINE.finditer(stated):
        key = m.group(1)
        if key not in keys:
            continue
        nums = [int(n) for n in re.findall(r"\d+", m.group(2))]
        rec = out.setdefault(keys[key], [])
        for n in nums:
            if n not in rec and len(rec) < 6:
                rec.append(n)
    return [{"file": f, "lines": ls, "section": section_of(f, ls[0]) if ls else None} for f, ls in out.items() if rel_exists(f)]


def tail_lands(text, rel):
    """{'J_BAND_A': (rows, line), ...} from section 2 of band-interface.md: each land table is named by the paragraph above it."""
    sec = md.section(text, r"^2\.\s", level=2)
    out = {}
    if sec is None:
        return out
    first, last, _ = sec
    lines = text.splitlines()
    for t in md.tables(text, first, last):
        if [c.lower() for c in t["columns"][:3]] != ["land", "name", "net"]:
            continue
        i = t["line"] - 2
        while i >= 0 and not lines[i].strip():
            i -= 1
        m = re.match(r"\s*(J_BAND_[AB])", lines[i]) if i >= 0 else None
        if m:
            out[m.group(1)] = (t["rows"], t["line"])
    return out


def lead_lengths(text):
    """('lead cut length per size' text, line) from section 6 of band-interface.md, or None."""
    sec = md.section(text, r"^6\.\s", level=2)
    if sec is None:
        return None
    first, last, _ = sec
    for t in md.tables(text, first, last):
        if t["columns"][0].upper() == "US" and t["rows"] and "length" in t["rows"][0][0].lower():
            sizes = t["columns"][1:]
            vals = t["rows"][0][1:]
            return " · ".join(f"US {s} {v} mm" for s, v in zip(sizes, vals)), t["row_lines"][0]
    return None


def case_wires(text):
    """({wire: row dict}, line of the table) from the 'Wiring table' sections of the case board notes (the last one wins)."""
    out, line = {}, None
    for lv, title, ln in md.headings(text):
        if not re.match(r"Wiring table", title):
            continue
        sec = md.section(text, r"^" + re.escape(title) + r"$", level=lv)
        if sec is None:
            continue
        for t in md.tables(text, sec[0], sec[1]):
            if t["columns"] and t["columns"][0].lower() == "wire":
                for row, rl in zip(t["rows"], t["row_lines"]):
                    out[row[0].strip()] = dict(zip([c.lower() for c in t["columns"]], row), _line=rl)
                line = t["line"]
    return out, line


def ring_to_case(text):
    """(rows, line) of the 'ring pad to case pin' table of the case board notes, or None."""
    sec = md.section(text, r"^Part g\b", level=2)
    if sec is None:
        return None
    for t in md.tables(text, sec[0], sec[1]):
        if t["columns"] and t["columns"][0].lower().startswith("ring pad"):
            return t, t["line"]
    return None


def details(ctx, cid, conn_text, cache):
    """Extra rows for one connection from the band and case notes: [{label, value, source}]."""
    out = []
    band = cache("band", BAND_INTERFACE)
    case = cache("case", CASE_NOTES)
    for jb in sorted(set(re.findall(r"J_BAND_[AB]", conn_text))):
        if band is None:
            continue
        lands = tail_lands(band, BAND_INTERFACE).get(jb)
        if lands:
            rows, line = lands
            value = " · ".join(f"{r[0]} {r[1]} ({r[2]})" for r in rows if r[0].strip().isdigit())
            out.append({"label": f"{jb} lands on the main board", "value": value, "source": pointer(BAND_INTERFACE, line)})
    if band is not None and re.search(r"\bmotor\b", conn_text, re.I):
        lead = lead_lengths(band)
        if lead:
            out.append({"label": "Motor lead cut length, by ring size", "value": lead[0], "source": pointer(BAND_INTERFACE, lead[1])})
    if case is not None:
        wires, line = case_wires(case)
        named = [w for w in wires if re.search(rf"\b{re.escape(w)}\b", conn_text)]
        # a range such as 'W1 to W4' names the wires between
        for m in re.finditer(r"\bW(\d+) to W(\d+)\b", conn_text):
            named += [w for w in wires if w.startswith("W") and w[1:].isdigit() and int(m.group(1)) <= int(w[1:]) <= int(m.group(2))]
        for w in dict.fromkeys(named):
            r = wires[w]
            bits = [f"cut {r['cut mm']} mm"] if r.get("cut mm") else []
            if r.get("path mm"):
                bits.append(f"path {r['path mm']} mm")
            if r.get("cb length mm"):
                bits.append(f"case parts list says {r['cb length mm']} mm")
            out.append({"label": f"Wire {w}", "value": ", ".join(bits) or "see the table", "source": pointer(CASE_NOTES, r["_line"])})
        if re.search(r"spring pin", conn_text, re.I):
            g = ring_to_case(case)
            if g:
                t, gl = g
                cols = [c.lower() for c in t["columns"]]
                for row in t["rows"]:
                    d = dict(zip(cols, row))
                    out.append({"label": f"Ring pad {d.get('ring pad', '')}",
                                "value": f"to case pin {d.get('case pin', '')}; ring net {d.get('ring net (rn)', '')}, case net {d.get('case net (cn)', '')}",
                                "source": pointer(CASE_NOTES, gl)})
    return out


def build(ctx):
    """(connection_map dict, [files read], message) or (None, [], message) when connections.md is not there."""
    p = ctx.source_path(CONNECTIONS)
    if not p.is_file():
        return None, [], f"{CONNECTIONS} is not there: no connection map"
    text = p.read_text(encoding="utf-8")
    texts = {}

    def cache(key, rel):
        if key not in texts:
            f = ctx.source_path(rel)
            texts[key] = f.read_text(encoding="utf-8") if f.is_file() else None
        return texts[key]

    try:
        keys = read_keys(text)
        rows = part1_rows(text)
    except WiringError as e:
        note = f"The connection list cannot be read: {e}."
        return {"source": pointer(CONNECTIONS, None), "file_time": boardlist.stamp(p), "stated_count": None, "note": note,
                "nodes": [], "connections": []}, [CONNECTIONS], note
    tokens_by_bom = {}
    for bom, rel in boardlist.BOM_FILES.items():
        tokens_by_bom[bom] = set()
        f = ctx.source_path(rel)
        if not f.is_file():
            continue
        for r in csvread.read(f):
            for ref in csvread.split_refs(r["cells"].get("reference", "")):
                tokens_by_bom[bom].add(ref)

    heads = {}

    def section_of(rel, line):
        if not rel.endswith(".md"):
            return None
        if rel not in heads:
            f = ctx.source_path(rel)
            heads[rel] = md.headings(f.read_text(encoding="utf-8")) if f.is_file() else []
        best = None
        for _lv, title, ln in heads[rel]:
            if ln <= line:
                best = title
        return best

    nodes, conns = {}, []
    read = [CONNECTIONS]
    counts = conductor_counts(ctx)
    by_joint, cinfo = conductor_data(ctx)
    if cinfo["status"] == "ok":
        read.append(PRODUCT_WIRING)
    for row, line in rows:
        num, frm, to, carrier, conductors, nets, stated, drawn = (clean(c) for c in row[:8])
        if re.match(r"no joint\b", drawn, re.I):
            continue
        a, b = node_of(frm, tokens_by_bom, nodes), node_of(to, tokens_by_bom, nodes)
        conn = {
            "id": num, "signal": nets, "ends": [{"node": a, "text": frm}, {"node": b, "text": to}],
            "how": how_made(carrier, conductors),
            "drawn": {"state": drawn_state(drawn), "words": drawn},
            "details": details(ctx, num, " ".join([frm, to, carrier, nets]), cache),
            "proof": proofs(stated, keys, lambda f: ctx.source_path(f).is_file(), section_of),
            "source": pointer(CONNECTIONS, line),
        }
        if num in counts:
            conn["conductors"] = counts[num]
        if by_joint.get(num, {}).get("lines"):
            conn["conductor_lines"] = by_joint[num]["lines"]
        if by_joint.get(num, {}).get("none"):
            conn["no_conductor"] = by_joint[num]["none"]
        for d in conn["details"]:
            read.append(d["source"]["file"])
        conns.append(conn)
    stated_n = stated_count(text)
    note = None
    if stated_n is None:
        note = "connections.md does not state how many joints there are."
    elif stated_n != len(conns):
        note = f"connections.md states {stated_n} joints; its table holds {len(conns)}."
    m = md.section(text, r"^Part 1\b", level=2)
    data = {"source": pointer(CONNECTIONS, m[0] if m else None), "file_time": boardlist.stamp(p), "stated_count": stated_n, "note": note,
            "nodes": sorted(nodes.values(), key=lambda n: (n["kind"] != "board", n["id"])), "connections": conns,
            "conductor_file": cinfo}
    return data, list(dict.fromkeys(read)), note
