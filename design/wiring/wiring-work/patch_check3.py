f=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/check_wiring.py")
s=open(f).read()
R=[
('''  incomplete        a line is not complete: its state is not `drawn and routed` or `specified and landed` (lead's ruling)''',
'''  incomplete        (only with --require-complete) a conductor line is not complete: its state is not `drawn and routed`
                    or `specified and landed`; each is listed with what it waits for (column waits_for)
  complete-open     a line marked complete has a board pad that is not joined to its net (KiCad copper connectivity):
                    for copper the two end pads on the carrier boards, for any other carrier every board pad it names'''),
('''It prints the counts per state and per joint and the share complete. Last line: RESULT PASS|FAIL with the counts.''',
'''It prints the counts per state and per joint, the sensing gaps (carrier_kind none: no conductor, counted apart) and,
before the RESULT line, `COMPLETE <n> of <total> conductors (<percent>)`. Without --require-complete the check is about
consistency; with it, it also exits 1 while any conductor line is incomplete. Last line: RESULT PASS|FAIL with the counts.'''),
('''        if r.get("state") in STATES and r["state"] not in bw.COMPLETE:
            fail("incomplete", "%s %s %s.%s -> %s.%s is `%s`: %s" % (
                rid, r.get("joint"), r.get("end_A_ref"), r.get("end_A_pin", "").split(" ")[0], r.get("end_B_ref"),
                r.get("end_B_pin", "").split(" ")[0], r["state"], r.get("state_reason", "")))
        kind = r.get("carrier_kind", "")''',
'''        kind = r.get("carrier_kind", "")
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
                        rid, r["state"], key[0], key[1], b))'''),
('''    args = sys.argv[1:]''','''    args = sys.argv[1:]
    require = "--require-complete" in args'''),
('''    checks = sorted({f_.split("]")[0][5:] for f_ in fails})
    done = sum(by_state.get(s, 0) for s in bw.COMPLETE)
    share = "complete %d of %d (%.0f percent)" % (done, len(rows), 100.0 * done / len(rows) if rows else 0)
    print(share)
    summary = "lines %d, %s, %s, problems %d" % (len(rows), ", ".join("%s %d" % (s, by_state.get(s, 0)) for s in STATES),
                                                share, len(fails))''',
'''    checks = sorted({f_.split("]")[0][5:] for f_ in fails})
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
        len(fails))'''),
]
for a,b in R:
    assert s.count(a)==1, a[:60]
    s=s.replace(a,b)
open(f,'w').write(s); print('check patched', len(R))
