f=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/build_wiring.py")
s=open(f).read()
NEW = r'''
# ---------------------------------------------------------------- cell pack (lead's ruling 08:31: BT1 + PRT1 + RT1 is one purchased part)
def cellpack_lines(rnx):
    rows = []
    one = tproof(BI, r"Seen from the ring, BT1 plus PRT1 is one part with three outputs")
    mat = tproof(BI, r"Tab material: nickel strip 0\.30 wide x 0\.10 thick")
    solder = tproof(BI, r"soldered by hand, low heat")
    glob_ = FLEX["FLEX2"].format("{" + ",".join(map(str, SIZES)) + "}")
    tabs = [("BT1", "1", "Tab P\\+ \\(PRT1 pad 1\\) = cell positive after protection = ring netlist BT1 pin 1", "P+", "1", "R6"),
            ("BT1", "2", "Tab P- \\(PRT1 pad 2\\) = cell negative after protection = ring netlist BT1 pin 2", "P-", "2", "R6"),
            ("RT1", "1", "Tab NTC \\(PRT1 pad 3\\) = RT1 pin 1, net NTC, FLEX2 land 3", "NTC", "3", "R7")]
    for ref, pin, pat, tab, land, ej in tabs:
        r = rnx[(ref, pin)]
        net = r["net"]
        row = blank_row()
        row.update({
            "joint": "R10", "end_joints": ej, "carrier_kind": "tab",
            "signal_A": net, "end_A_kind": "terminal", "end_A_board": "off board (cell pack BT1 + PRT1 + RT1, one purchased part)",
            "end_A_ref": ref, "end_A_pin": pin + (" (" + r["pin_name"] + ")" if r["pin_name"] not in ("", "~") else ""),
            "end_A_face": "output tab %s of the pack" % tab, "join_A": "made by the pack maker",
            "signal_B": net, "end_B_kind": "land", "end_B_board": "FLEX2", "end_B_ref": "PRT1",
            "end_B_pin": land + " (land of footprint PRT1_Tabs)",
            "end_B_face": ",".join(pad_of(FLEX["FLEX2"].format(SIZES[0]), "PRT1", land)["layers"]),
            "join_B": "hand solder, low heat (iron 280 C max, 2 s)", "pairing_rule": "same net",
            "carrier": "pack output tab %s, nickel strip 0.30 wide x 0.10 thick" % tab, "carrier_net": net,
            "cut_note": "not size dependent", "carrier_marking": "tab %s (order P+, NTC, P- from the slot)" % tab,
            "carrier_gauge_or_model": "nickel strip 0.30 x 0.10 (pack's own tab)",
            "solder_first": "one soldered end (the pack end is the maker's)",
            "proof_A": nproof(RING_NETLIST, r) + ";" + tproof(BI, pat) + ";" + one,
            "proof_B": bproof(glob_, "PRT1", land, net), "proof_carrier": mat + ";" + one, "proof_join": solder,
        })
        ok = all((pad_of(FLEX["FLEX2"].format(s_), "PRT1", land) or {}).get("net") == net for s_ in SIZES)
        probs = ["us%d: PRT1 land %s not joined to its net" % (s_, land) for s_ in SIZES
                 if ("PRT1", land) in board(FLEX["FLEX2"].format(s_))["drc"]["open_pads"]]
        why = spec_state(row, ok, probs)
        row["state_reason"] = why or ("pack pin in the netlist; FLEX2 land PRT1:%s holds net %s in all 7 boards, joined; tab "
                                      "specified in %s section 5" % (land, net, BI))
        rows.append(row)
    r = rnx[("RT1", "2")]
    row = blank_row()
    g = tproof(BI, r"RT1 pin 2 \(ground\) is on the PRT1 board and is joined there to tab P- \(pad 2 of the same board\)")
    row.update({
        "joint": "R8", "end_joints": "R10", "carrier_kind": "inside the part",
        "signal_A": r["net"], "end_A_kind": "terminal", "end_A_board": "off board (cell pack BT1 + PRT1 + RT1, one purchased part)",
        "end_A_ref": "RT1", "end_A_pin": "2", "end_A_face": "on the PRT1 board", "join_A": "made by the pack maker",
        "signal_B": "GND", "end_B_kind": "internal", "end_B_board": "off board (inside the pack)", "end_B_ref": "BT1",
        "end_B_pin": "2", "end_B_face": "tab P- of the pack", "join_B": "inside the part", "pairing_rule": "same net",
        "carrier": "PRT1 board copper inside the purchased pack", "carrier_net": "GND", "cut_note": "not size dependent",
        "carrier_marking": "inside the purchased pack", "carrier_gauge_or_model": "cell pack BT1 + PRT1 + RT1 (band-interface.md section 5)",
        "solder_first": "not soldered by the builder",
        "proof_A": nproof(RING_NETLIST, r), "proof_B": nproof(RING_NETLIST, rnx[("BT1", "2")]) + ";" + g,
        "proof_carrier": g + ";" + one, "proof_join": one,
    })
    why = spec_state(row, True, [])
    row["state_reason"] = why or "inside the purchased pack: RT1 pin 2 joined to tab P- on the PRT1 board (%s section 5)" % BI
    rows.append(row)
    return rows


# ---------------------------------------------------------------- ring pads to case pins (lead's ruling 08:31)
CONTACT = "design/wiring/ring-case-contact.csv"
PINTRAVEL = "design/case/pin-travel.md"


def contact_lines(rnx, cnx):
    rows = []
    sjoin = tproof("design/case/case-architecture.md", r"solder P1 to P4 to PCB2")
    model = tproof("design/case/case-architecture.md", r"Harwin P70-6000045R \(the fitted pin")
    rng = tproof(PINTRAVEL, r"Working-height range stated: minimum compression 2\.20 mm, maximum compression 1\.90 mm")
    order = tproof(BI, r"order VBUS, D-, D\+, GND with rising angle")
    have = os.path.exists(p(CONTACT))
    crow = []
    if have:
        with open(p(CONTACT), newline="", encoding="utf-8") as f_:
            text = f_.read().split("\n")
        crow = [dict(r_, _line=i_) for i_, r_ in enumerate(csv.DictReader(io.StringIO("\n".join(text))), 2)]
    for k in ("1", "2", "3", "4"):
        cp_, pn = "CP" + k, "P" + k
        a, b = rnx[(cp_, "1")], cnx[(pn, "1")]
        fpad = pad_of(FLEX["FLEX2"].format(SIZES[0]), cp_, "1")
        ppad = pad_of(CASE_PINS, pn, "1")
        rule = "same net" if a["net"] == b["net"] else "ring %s to case %s (case sch-notes.md line 17)" % (a["net"], b["net"])
        row = blank_row()
        row.update({
            "joint": "R15", "end_joints": "R9;C4", "carrier_kind": "spring pin",
            "signal_A": a["net"], "end_A_kind": "face", "end_A_board": "FLEX2", "end_A_ref": cp_, "end_A_pin": "1 (gold disc face)",
            "end_A_face": ",".join(fpad["layers"]) if fpad else "", "join_A": "pressed contact (pin tip on the disc)",
            "signal_B": b["net"], "end_B_kind": "terminal", "end_B_board": "case pin board (PCB2)", "end_B_ref": pn, "end_B_pin": "1",
            "end_B_face": ",".join(ppad["layers"]) if ppad else "", "join_B": "solder (P1 to P4 soldered to PCB2)",
            "pairing_rule": rule, "carrier": "Harwin P70-6000045R spring pin %s pressed on ring disc %s" % (pn, cp_),
            "carrier_net": a["net"] if a["net"] == b["net"] else "%s/%s" % (a["net"], b["net"]),
            "cut_note": "not size dependent", "carrier_marking": "pin position %s in the pin holder" % pn,
            "carrier_gauge_or_model": "Harwin P70-6000045R", "solder_first": "pin soldered to PCB2 before the holder is fitted",
            "proof_A": nproof(RING_NETLIST, a) + ";" + order + ";" + bproof(FLEX["FLEX2"].format("{" + ",".join(map(str, SIZES)) + "}"), cp_, "1", a["net"]),
            "proof_B": nproof(CASE_NETLIST, b) + ";" + bproof(CASE_PINS, pn, "1", b["net"]),
            "proof_carrier": model + ";" + rng, "proof_join": sjoin,
        })
        ends_ok = bool(ppad and ppad["net"] == b["net"]) and all(
            (pad_of(FLEX["FLEX2"].format(s_), cp_, "1") or {}).get("net") == a["net"] for s_ in SIZES)
        probs = []
        if not have:
            probs.append("%s does not exist yet (pairing by coordinates and pin working range per size)" % CONTACT)
        else:
            cols = {c.lower(): c for c in (crow[0].keys() if crow else [])}
            cpad = next((cols[c] for c in cols if c == "pad" or c.startswith("ring_pad") or c == "ring pad"), None)
            cpin = next((cols[c] for c in cols if c == "pin" or c.startswith("case_pin") or c == "case pin"), None)
            csz = next((cols[c] for c in cols if c in ("us", "size", "ring_size", "ring size")), None)
            cin = next((cols[c] for c in cols if c.replace(" ", "_") == "in_range"), None)
            if not (cpad and cpin and csz and cin):
                probs.append("%s: columns not understood (found %s)" % (CONTACT, ", ".join(crow[0].keys()) if crow else "no rows"))
            else:
                mine = [x for x in crow if x[cpin].strip() == pn]
                sizes = {re.sub(r"\D", "", x[csz]) for x in mine}
                if {x[cpad].strip() for x in mine} != {cp_}:
                    probs.append("%s pairs %s with %s" % (CONTACT, pn, sorted({x[cpad].strip() for x in mine})))
                if sizes != {str(s_) for s_ in SIZES}:
                    probs.append("%s has %s at sizes %s, not all 7" % (CONTACT, pn, sorted(sizes)))
                bad = [x for x in mine if x[cin].strip().lower() != "yes"]
                if bad:
                    probs.append("%s: in_range not yes for %s at lines %s" % (CONTACT, pn, ", ".join(str(x["_line"]) for x in bad)))
                if mine:
                    row["proof_carrier"] += ";" + ";".join("%s:%d|%s" % (CONTACT, x["_line"], text[x["_line"] - 1]) for x in mine)
        if not have:
            row["state"] = "stated in text only"
            row["state_reason"] = probs[0]
            row["waits_for"] = probs[0]
        else:
            why = spec_state(row, ends_ok, probs)
            row["state_reason"] = why or "pad and pin drawn with their nets; %s pairs them at all 7 sizes, every in_range yes; maker range cited" % CONTACT
        rows.append(row)
    return rows

'''
a = '''# ---------------------------------------------------------------- hand rows'''
assert s.count(a)==1
s = s.replace(a, NEW + a)
b = '''    rows += system_rows()
'''
assert s.count(b)==1
s = s.replace(b, '''    rows += cellpack_lines(rnx)
    rows += contact_lines(rnx, cnx)
    rows += system_rows()
''')
open(f,'w').write(s); print('patched')
