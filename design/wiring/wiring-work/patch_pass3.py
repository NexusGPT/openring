f=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/build_wiring.py")
s=open(f).read()
R=[
('''        if os.environ.get("WIRING_NO_DRC") != "1":
            # KiCad's list''','''        if True:
            # KiCad's list'''),
('''    "carrier_marking", "carrier_gauge_or_model", "solder_first", "spec_missing",
''','''    "carrier_marking", "carrier_gauge_or_model", "solder_first", "spec_missing", "waits_for",
'''),
('''    rows += system_rows()
''','''    rows += system_rows()
    for r in rows:
        if r["state"] in COMPLETE or r["carrier_kind"] == "none" or r["waits_for"]:
            continue
        need = []
        if r["spec_missing"]:
            src = CBN if "case" in (r["end_A_board"] + r["end_B_board"]) else BI
            need.append("%s: %s" % (src, r["spec_missing"]))
        rest = [x for x in r["state_reason"].split("; ") if not x.startswith("specification incomplete")]
        if rest and rest != [""]:
            where = RING_BOARD if "main board" in r["state_reason"] or "J1 pad" in r["state_reason"] else "design files"
            need.append("%s: %s" % (where, "; ".join(rest)))
        r["waits_for"] = " | ".join(need)
'''),
]
for a,b in R:
    assert s.count(a)==1, a[:60]
    s=s.replace(a,b)
open(f,'w').write(s); print('build patched', len(R))
