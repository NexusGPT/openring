f=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/build_wiring.py")
s=open(f).read()
R=[
('''SYSTEM_JOINTS = "design/wiring/system-joints.csv"''','''SYSTEM_JOINTS = "design/wiring/system-joints.csv"
LD = "design/wiring/lead-decisions.md"
LSPEC = "design/case/lead-specs.md"'''),
('''        if frm.startswith("WP"):
            row.update({"carrier_marking": "", "carrier_gauge_or_model": "30 AWG",
                        "solder_first": "not stated in the files"})
        else:
            row.update({"carrier_marking": "red (+)" if w == "W5" else "black (-)", "carrier_gauge_or_model": "",
                        "solder_first": "one soldered end (the cell end is made by the maker)"})''',
'''        if frm.startswith("WP"):
            cn_, cl_ = find_line(LD, r"^\\| case wires W1 to W4 and W7: colour \\|.*")
            mm = re.search(r"%s \\(%s\\) (\\w+)" % (w, re.escape(net)), cl_)
            gq = re.search(r"All five are 30 AWG stranded hook-up wire \\(conductor 0\\.25 mm\\)", cl_)
            row.update({"carrier_marking": (mm.group(1) + " insulation") if mm else "",
                        "carrier_gauge_or_model": "30 AWG stranded hook-up wire" if gq else "",
                        "solder_first": "not stated in the files"})
            if mm:
                row["carrier"] = "wire 30 AWG stranded, %s, cut %s mm (path %s mm)" % (mm.group(1), cut, path)
                row["proof_carrier"] += ";%s:%d|%s" % (LD, cn_, mm.group(0))
            if gq:
                row["proof_carrier"] += ";%s:%d|%s" % (LD, cn_, gq.group(0))
        else:
            cn_, cl_ = find_line(LD, r"^\\| case cell BT1 leads \\(wiring lines for joints C1, C2\\) \\|.*")
            q1 = re.search(r"the leads are used as the maker delivers them, never replaced", cl_)
            q2 = re.search(r"red probe on the red lead: the reading must be positive, between 3\\.0 and 4\\.35 V", cl_)
            row.update({"carrier_marking": "red (+)" if w == "W5" else "black (-)",
                        "carrier_gauge_or_model": ("DNK852338 own lead as delivered (no gauge stated by the maker; "
                                                   "polarity measured before cutting)") if (q1 and q2) else "",
                        "solder_first": "one soldered end (the cell end is made by the maker)"})
            for q in (q1, q2):
                if q:
                    row["proof_carrier"] += ";%s:%d|%s" % (LD, cn_, q.group(0))'''),
('''        row.update({"carrier_marking": "", "carrier_gauge_or_model": "",
                    "solder_first": "one soldered end (the thermistor end is made by the maker)"})''',
'''        tn_, tl_ = find_line(LD, r"^\\| case thermistor TH1 leads \\(joint C3\\) and bead size \\|.*")
        qa = re.search(r"two bare leads of 0\\.5 mm tin plated 42 alloy at 2\\.54 mm pitch; no insulation, no colour, no polarity", tl_)
        qb = re.search(r"soldered into the two plated holes TH1\\.1 and TH1\\.2 \\(either way round\\), the joint 5 mm or more from the bead", tl_)
        sp_ = tproof(LSPEC, r"0\\.5 tin plated 42 alloy")
        row.update({"carrier_marking": "bare, no polarity" if qa else "",
                    "carrier_gauge_or_model": "Semitec 103AT-2 own lead as delivered (0.5 mm tin plated 42 alloy)" if qa else "",
                    "solder_first": "one soldered end (the bead end is the maker's); either way round, joint 5 mm or more from the bead" if qb else
                    "one soldered end (the thermistor end is made by the maker)"})
        for q in (qa, qb):
            if q:
                row["proof_carrier"] += ";%s:%d|%s" % (LD, tn_, q.group(0))
        row["proof_carrier"] += ";" + sp_'''),
]
for a,b in R:
    assert s.count(a)==1, a[:60]
    s=s.replace(a,b)
open(f,'w').write(s); print('patched', len(R))
