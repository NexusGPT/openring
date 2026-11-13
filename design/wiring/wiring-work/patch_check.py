f=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/check_wiring.py")
s=open(f).read()
R=[]
R.append(('''  state             a line has the state `not drawn` or a state outside the four allowed words''',
'''  state             a line has the state `not drawn` or a state outside the five allowed words
  incomplete        a line is not complete: its state is not `drawn and routed` or `specified and landed` (lead's ruling)
  state-kind        `drawn and routed` on a carrier that is not copper, or `specified and landed` on copper or without
                    its specification (marking, gauge or model, cut length per size or "not size dependent")'''))
R.append(('''It prints the counts per state and per joint. Last line: RESULT PASS|FAIL with the counts.''',
'''It prints the counts per state and per joint and the share complete. Last line: RESULT PASS|FAIL with the counts.
Pins with no net (no-connect) carry no signal and are not required (lead's ruling on the screen cable).'''))
R.append(('''        for r in bw.read_netlist(nl):
            if r["reference"] in refs:
                terms[(prod, r["reference"], r["pin_number"])] = r''','''        for r in bw.read_netlist(nl):
            if r["reference"] in refs:
                if r["net"]:
                    terms[(prod, r["reference"], r["pin_number"])] = r
                else:
                    noconnect.append("%s %s.%s" % (prod, r["reference"], r["pin_number"]))'''))
R.append(('''    terms = {}
''','''    terms = {}
    noconnect = []
'''))
R.append(('''        elif r["state"] == "not drawn":
            fail("state", "%s is `not drawn` (%s)" % (rid, r.get("state_reason", "")))''','''        elif r["state"] == "not drawn":
            fail("state", "%s is `not drawn` (%s)" % (rid, r.get("state_reason", "")))
        if r.get("state") in STATES and r["state"] not in bw.COMPLETE:
            fail("incomplete", "%s %s %s.%s -> %s.%s is `%s`: %s" % (
                rid, r.get("joint"), r.get("end_A_ref"), r.get("end_A_pin", "").split(" ")[0], r.get("end_B_ref"),
                r.get("end_B_pin", "").split(" ")[0], r["state"], r.get("state_reason", "")))
        kind = r.get("carrier_kind", "")
        if r.get("state") == "drawn and routed" and kind not in ("copper",):
            fail("state-kind", "%s is `drawn and routed` but its carrier is %r, not copper" % (rid, kind))
        if r.get("state") == "specified and landed":
            cuts = [r.get("cut_mm_us%d" % s, "") for s in SIZES]
            if kind == "copper" or not r.get("carrier_marking") or not r.get("carrier_gauge_or_model") or (
                    not all(cuts) and r.get("cut_note") != "not size dependent"):
                fail("state-kind", "%s is `specified and landed` but carrier %r has marking %r, gauge or model %r, cuts %s" % (
                    rid, kind, r.get("carrier_marking"), r.get("carrier_gauge_or_model"), cuts))'''))
R.append(('''    print("terminals required (off-board pins and board-to-board lands): %d, in exactly one line: %d" % (
        len(terms), sum(1 for k in terms if len(seen.get(k, [])) == 1)))''','''    print("terminals required (off-board pins and board-to-board lands with a net): %d, in exactly one line: %d" % (
        len(terms), sum(1 for k in terms if len(seen.get(k, [])) == 1)))
    print("no-connect pins not required: %d (%s)" % (len(noconnect), ", ".join(noconnect)))'''))
R.append(('''    summary = "lines %d, %s, problems %d" % (len(rows), ", ".join("%s %d" % (s, by_state.get(s, 0)) for s in STATES), len(fails))''',
'''    done = sum(by_state.get(s, 0) for s in bw.COMPLETE)
    share = "complete %d of %d (%.0f percent)" % (done, len(rows), 100.0 * done / len(rows) if rows else 0)
    print(share)
    summary = "lines %d, %s, %s, problems %d" % (len(rows), ", ".join("%s %d" % (s, by_state.get(s, 0)) for s in STATES),
                                                share, len(fails))'''))
for a,b in R:
    assert s.count(a)==1, a[:70]
    s=s.replace(a,b)
open(f,'w').write(s); print('patched', len(R))
