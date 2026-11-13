#!/usr/bin/env python3
"""Check design/wiring/product-wiring.csv against the design files.

Checks (each failure is printed as FAIL[<check>] ...):
  terminal-missing  a pin of an off-board part or a board-to-board land (from the netlists and parts lists) is in no line
  terminal-twice    such a pin is in more than one line
  terminal-unknown  a line names as a terminal a pin that the netlist does not hold
  band-pad          a pad of a band circuit board (flex1/flex2, any size) is named by no line
  ends-disagree     the two ends' signal names differ and the line names no pairing rule
  lead-length       a lead or wire has no cut length for each of the 7 ring sizes and not the words "not size dependent"
  state             a line has the state `not drawn` or a state outside the four allowed words
  proof-missing     an end or the carrier has no proof
  proof-text        a quoted proof is not found again at its cited file and line
  proof-board       a board proof (pad and net, or a copper path) is not found again in the board file
  joint             a line has no joint id
It prints the counts per state and per joint. Last line: RESULT PASS|FAIL with the counts.

Run: python design/wiring/check_wiring.py [--csv <file>]   (re-runs itself under KiCad's Python when pcbnew is missing)
"""
import csv
import os
import re
import sys

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
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


def main():
    args = sys.argv[1:]
    path = os.path.join(HERE, "product-wiring.csv")
    if "--csv" in args:
        path = os.path.abspath(args[args.index("--csv") + 1])
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    fails = []

    def fail(check, msg):
        fails.append("FAIL[%s] %s" % (check, msg))

    # ---------------- the terminal set, from the netlists and parts lists
    terms = {}
    for prod, nl, parts, rx in (("ring", bw.RING_NETLIST, bw.RING_PARTS, RING_OFFBOARD_FP),
                                ("case", bw.CASE_NETLIST, bw.CASE_PARTS, CASE_OFFBOARD_FP)):
        refs = {r["reference"] for r in bw.read_parts(parts) if rx.search(r["footprint"])}
        for r in bw.read_netlist(nl):
            if r["reference"] in refs:
                terms[(prod, r["reference"], r["pin_number"])] = r
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
    print("terminals required (off-board pins and board-to-board lands): %d, in exactly one line: %d" % (
        len(terms), sum(1 for k in terms if len(seen.get(k, [])) == 1)))
    for s in STATES:
        print("state %-22s %d" % (s, by_state.get(s, 0)))
    print("lines per joint: " + ", ".join("%s %d" % (j, by_joint[j]) for j in sorted(by_joint, key=lambda x: (x[0], int(x[1:]) if x[1:].isdigit() else 0))))
    print("lines naming a joint at an end: " + ", ".join("%s %d" % (j, by_end_joint[j]) for j in sorted(by_end_joint)))
    checks = sorted({f_.split("]")[0][5:] for f_ in fails})
    summary = "lines %d, %s, problems %d" % (len(rows), ", ".join("%s %d" % (s, by_state.get(s, 0)) for s in STATES), len(fails))
    if fails:
        print("RESULT FAIL %s (checks failing: %s)" % (summary, " ".join(checks)))
        sys.exit(1)
    print("RESULT PASS %s" % summary)


if __name__ == "__main__":
    main()
