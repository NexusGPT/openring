f=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/build_wiring.py")
s=open(f).read()
R=[]
R.append(('''    "cut_mm_us7", "cut_mm_us8", "cut_mm_us9", "cut_mm_us10", "cut_mm_us11", "cut_mm_us12", "cut_mm_us13", "cut_note",
''','''    "cut_mm_us7", "cut_mm_us8", "cut_mm_us9", "cut_mm_us10", "cut_mm_us11", "cut_mm_us12", "cut_mm_us13", "cut_note",
    "carrier_marking", "carrier_gauge_or_model", "solder_first", "spec_missing",
'''))
R.append(('''STATES = ["drawn and routed", "drawn, not routed", "stated in text only", "not drawn"]''',
'''STATES = ["drawn and routed", "specified and landed", "drawn, not routed", "stated in text only", "not drawn"]
COMPLETE = STATES[:2]  # lead's ruling 2026-11-13: a line is complete when its state is one of these two'''))
R.append(('''STRICT = os.environ.get("WIRING_STRICT", "0") == "1"
''','''def spec_state(row, ends_ok, problems):
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
'''))
# switches inside the part
R.append(('''            "proof_carrier": src, "proof_join": src, "cut_note": "",
            "state": "drawn and routed",
            "state_reason": "pin in the netlist; not soldered by design; joined to pin %s inside the part" % mate,
        })
        rows.append(row)''','''            "proof_carrier": src, "proof_join": src, "cut_note": "not size dependent",
            "carrier_marking": "Alps terminal numbers 1 to 4 (catalog page 2, Drawing No.1)",
            "carrier_gauge_or_model": "Alps SKTAAAE010", "solder_first": "not soldered",
        })
        why = spec_state(row, True, [])
        row["state_reason"] = why or "pin in the netlist; not soldered by design; joined to pin %s inside the part (%s)" % (
            mate, src.split("|")[0])
        rows.append(row)'''))
# motor
R.append(('''        put_lengths(row, "cut_mm", dict(zip(SIZES, cuts)))
        row["state"] = "drawn and routed" if not STRICT else "drawn, not routed"
        row["state_reason"] = ("motor pin in the netlist, land with net %s in all 7 flex1 boards, colour and cut "
                               "length per size in %s line %d" % (net, BI, cn))''','''        put_lengths(row, "cut_mm", dict(zip(SIZES, cuts)))
        row.update({"carrier_marking": colour + " insulation", "carrier_gauge_or_model": "AWG32 (Jinlong W0525AB001D lead)",
                    "solder_first": "one soldered end (the motor end is made by the maker)"})
        fb = board(FLEX["FLEX1"].format(SIZES[0]))
        probs = ["us%d rules check: open connection at M1:%s" % (s, land) for s in SIZES
                 if ("M1", land) in board(FLEX["FLEX1"].format(s))["drc"]["open_pads"]]
        why = spec_state(row, pad_of(FLEX["FLEX1"].format(SIZES[0]), "M1", land) is not None, probs)
        row["state_reason"] = why or ("motor pin in the netlist, land with net %s in all 7 flex1 boards without open "
                                      "connection; colour, gauge and cut length per size in %s lines %d, %s, %d" % (
                                          net, BI, n, gauge.split("|")[0].split(":")[1], cn))'''))
# screen
R.append(('''    pins = sorted({r["pin_number"] for r in rn if r["reference"] == "J1"}, key=lambda x: int(x))
    for k in pins:''','''    contact_no = tproof(SCS, r"back view draws the 15 fingers as pads")
    pinmap = tproof(RSN, r"closed by the table on page 5 of the Tailor sheet")
    thick = tproof(SCS, r"0\\.2 \\+-0\\.03 including the polyimide \\(PI\\) stiffener")
    pitch = tproof(SCS, r"15 at 0\\.297 pitch \\(0\\.3\\)")
    pins = sorted({r["pin_number"] for r in rn if r["reference"] == "J1" and r["net"]}, key=lambda x: int(x))
    for k in pins:'''))
R.append(('''        row["state"] = ("drawn and routed" if not STRICT else "drawn, not routed") if (ok and face_ok) else "drawn, not routed"
        if ok and face_ok:
            row["state_reason"] = ("both pins in the netlist, J1 pad %s on the main board's screen face (B.Cu) with net %s; "
                                   "the cable is the screen maker's part" % (k, mb["net"]))
        elif ok:
            row["state_reason"] = ("J1 pad %s is on %s in the board file, the under face (screen-cable-study.md: Face F is the "
                                   "under face); the stock cable of layout C reaches J1 only on the screen face "
                                   "(screen-cable-study.md section 4.3)" % (k, mb["layers"][0]))
        else:
            row["state_reason"] = "J1 pad %s %s on the main board" % (k, "missing" if not mb else "has net " + mb["net"])''',
'''        row["proof_A"] += ";" + contact_no + ";" + pinmap
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
            probs.append("main board rules check: open connection at J1 pad %s" % k)
        why = spec_state(row, ok, probs)
        row["state_reason"] = why or ("both pins in the netlist, J1 pad %s on the screen face (B.Cu) with net %s, no open "
                                      "connection; cable specified in the maker drawing" % (k, mb["net"]))'''))
# case wires and cell leads
R.append(('''        if ok and not opens:
            row["state"] = "drawn and routed" if not STRICT else "drawn, not routed"
            row["state_reason"] = "both pads drawn with net %s; rules checks of the case boards: no open connection on them; cut length in %s line %d" % (net, CBN, i)
        else:
            row["state"] = "drawn, not routed"
            row["state_reason"] = "pad or net mismatch or open connection: %s" % (", ".join(opens) or "net/pad")''',
'''        if frm.startswith("WP"):
            row.update({"carrier_marking": "", "carrier_gauge_or_model": "30 AWG",
                        "solder_first": "not stated in the files"})
        else:
            row.update({"carrier_marking": "red (+)" if w == "W5" else "black (-)", "carrier_gauge_or_model": "",
                        "solder_first": "one soldered end (the cell end is made by the maker)"})
        probs = ["open connection: " + x for x in opens] + ([] if ok else ["pad or net mismatch"])
        why = spec_state(row, ok, probs)
        row["state_reason"] = why or ("both pads drawn with net %s; rules checks of the case boards: no open connection "
                                      "on them; cut length in %s line %d" % (net, CBN, i))'''))
R.append(('''        ok = mpad and mpad["net"] == r["net"] and ("TH1", pin) not in cm["drc"]["open_pads"]
        row["state"] = ("drawn and routed" if not STRICT else "drawn, not routed") if ok else "drawn, not routed"
        row["state_reason"] = "thermistor pin in the netlist; hole TH1.%s on PCB1 with net %s; lead length 10 mm in %s line %d" % (
            pin, mpad["net"] if mpad else "-", CBN, cutp[0])''','''        ok = bool(mpad and mpad["net"] == r["net"])
        row.update({"carrier_marking": "", "carrier_gauge_or_model": "",
                    "solder_first": "one soldered end (the thermistor end is made by the maker)"})
        probs = ["open connection at TH1.%s" % pin] if ("TH1", pin) in cm["drc"]["open_pads"] else []
        why = spec_state(row, ok, probs)
        row["state_reason"] = why or "thermistor pin in the netlist; hole TH1.%s on PCB1 with net %s; lead length 10 mm in %s line %d" % (
            pin, mpad["net"] if mpad else "-", CBN, cutp[0])'''))
R.append(('''    print("strict reading of 'drawn and routed':", STRICT)''','''    done = sum(counts.get(s, 0) for s in COMPLETE)
    print("complete (drawn and routed or specified and landed): %d of %d" % (done, len(rows)))'''))
for a,b in R:
    assert s.count(a)==1, a[:70]
    s=s.replace(a,b)
open(f,'w').write(s); print('patched', len(R))
