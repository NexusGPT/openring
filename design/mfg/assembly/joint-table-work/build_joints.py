"""Build design/mfg/assembly/joints.csv from the wiring list and hand-written facts, each with its
citation (file, quote). The line number of each citation is FOUND here by searching the quote in the
file, never typed. Writes joints.csv and joint-table-work/citations.csv (joint_id, field, path, line,
quote) for the audit. Run: design/.venv/bin/python -B build_joints.py"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(HERE, "..", "joints.csv")
A = "design/mfg/assembly/assembly.md"
BI = "design/ecad/band/band-interface.md"
PW = "design/wiring/product-wiring.csv"
BN = "design/ecad/case/pcb/board-notes.md"
LD = "design/wiring/lead-decisions.md"
CA = "design/case/case-architecture.md"
SC = "design/wiring/screen-cable-study.md"
RV = "design/wiring/wiring-review-3.md"
ST = "design/ecad/ring/pcb/fab/stackup.txt"
FLUXLOG = "design/mfg/assembly/joint-table-work/logs/flux-search.log"
PASTELOG = "design/mfg/assembly/joint-table-work/logs/probe_paste.log"
FIDLOG = "design/mfg/assembly/joint-table-work/logs/fiducial-search.log"
FLEXLOG = "design/mfg/assembly/joint-table-work/logs/flex-fab-listing.log"
FIELDS = ["joint_id", "wiring_line", "end", "what_meets_what", "step", "solder_source", "flux", "tool",
          "heat", "orientation", "alignment", "check", "check_possible_at_this_step", "source", "gap"]

_lines = {}


def lines_of(rel):
    if rel not in _lines:
        with open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace", newline="") as f:
            _lines[rel] = f.read().split("\n")
    return _lines[rel]


def find(rel, quote, at=None):
    """Line number (1-based) of the first line holding quote; with at, that line must hold it."""
    L = lines_of(rel)
    if at is not None:
        if quote not in L[at - 1]:
            raise SystemExit("quote not on %s:%d: %r" % (rel, at, quote))
        return at
    for i, l in enumerate(L, start=1):
        if quote in l:
            return i
    raise SystemExit("quote not found in %s: %r" % (rel, quote))


CITES = []


def C(rel, quote, at=None):
    return (rel, find(rel, quote, at), quote)


def wiring():
    rows = {}
    with open(os.path.join(ROOT, PW), newline="") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):
            r["_line"] = i
            rows[r["id"]] = r
    return rows


W = wiring()


def wcite(wid, quote=None):
    r = W[wid]
    return C(PW, quote if quote is not None else wid + ",", at=r["_line"])


ROWS = []


def add(jid, wline, end, fields, cites, gap=""):
    """fields: dict field -> value; cites: dict field -> list of (rel, line, quote)."""
    row = {"joint_id": jid, "wiring_line": wline, "end": end}
    row.update(fields)
    row["gap"] = gap
    cites.setdefault("joint_id", cites.get("wiring_line", []))
    src = []
    for fld in FIELDS:
        if fld in ("source", "gap"):
            continue
        cl = cites.get(fld, [])
        if not cl:
            raise SystemExit("no citation for %s field %s" % (jid, fld))
        for (rel, ln, q) in cl:
            CITES.append(dict(joint_id=jid, field=fld, path=rel, line=ln, quote=q))
        src.append("%s: %s" % (fld, "; ".join("%s:%d" % (rel, ln) for rel, ln, q in cl)))
    row["source"] = " | ".join(src)
    for fld in FIELDS:
        if fld != "gap" and not row.get(fld):
            raise SystemExit("empty %s in %s" % (fld, jid))
    ROWS.append(row)


def end_words(r, e):
    return "%s %s pin %s, face %s (%s)" % (r["end_%s_board" % e], r["end_%s_ref" % e], r["end_%s_pin" % e],
                                           r["end_%s_face" % e], r["join_%s" % e])


G2 = ("check probe point: the land numbers of the ribbon's board end are drawn on no file a builder is "
      "given (14 flex drawings carry no land number or net, flex boards have no silkscreen); only "
      "band-interface.md section 2 gives them as (u, v) numbers (review 3 G2)")
FLUX_GAP = ("flux: none of the searched design files (design/mfg, band-interface.md, case board-notes.md, case-architecture.md, lead-decisions.md, screen-cable-study.md) names a flux for this joint (logs/flux-search.log)")
fluxc = [C("design/mfg/assembly/v7-update-notes.md", "No file names the flux or the cleaner."), C(FLUXLOG, "No file names the flux or the cleaner.")]

# ---------------- 1. hot-bar lands (A ends) ----------------
HOT = ["W001", "W002", "W003", "W004", "W005", "W011", "W021", "W022",
       "W025", "W026", "W027", "W029", "W030", "W031", "W032"]
for wid in HOT:
    r = W[wid]
    flex2 = r["end_A_ref"] == "J_BAND_B"
    land = r["end_A_pin"].split()[0]
    what = "%s %s land %s, face %s, to %s tail land %s (%s); %s, every ring size US 7 to 13" % (
        r["end_A_board"], r["end_A_ref"], r["end_A_pin"], r["end_A_face"], r["end_B_board"], land,
        r["signal_A"], r["join_A"])
    f = dict(what_meets_what=what, step="16",
             solder_source="MISSING",
             flux="MISSING",
             tool="hot bar (thermode), not an iron; blade 3 mm wide covering the whole foot",
             heat="260 C for 4 s at 20 N (band-interface.md section 7, the band builder's starting values)",
             orientation="MISSING",
             alignment="MISSING")
    cites = dict(wiring_line=[wcite(wid)], end=[wcite(wid, r["join_A"])], what_meets_what=[wcite(wid)],
                 step=[C(A, "### Step 16. Solder the ribbon ends to the board")],
                 solder_source=[C(BI, "Pre-tin each land with a thin solder layer"),
                                C(BI, "Board lands pre-tinned (SAC305 stencil 0.05 mm)"),
                                C(A, "J_BAND_A and J_BAND_B are copper on the parts face and get no paste"),
                                C(A, "the hot-bar joints of step 16 need bare copper"),
                                C(PASTELOG, "NO OPENING ring %s:%s " % (r["end_A_ref"], land)),
                                C(ST, "Finish: ENEPIG")],
                 flux=fluxc,
                 tool=[C(BI, "Soldering method: HOT BAR (thermode), not an iron"), C(BI, "Hot bar blade 3 mm wide")],
                 heat=[C(BI, "260 C for 4 s at 20 N [my starting values")],
                 orientation=[C(A, "parts face up, while the ribbons rise through the slots"),
                              C(BI, "outer face (F.Cu, the lands) up")],
                 alignment=[C(BI, "alignment by the 0.10 mm outline shown on the fixture"),
                            C(RV, "no fixture is drawn in the design")])
    gaps = ["solder: band-interface.md asks a pre-tinned board land (stencil paste 0.05 mm or a tinned land), "
            "but no step tins it: step 2 gives the land no paste, step 4 cleans it to bare copper, step 16 adds none; "
            "ring-F_Paste.gbr holds no opening at this land (logs/probe_paste.log); the tail land is bare ENIG; "
            "no file read here names a 0.05 mm stencil (review 3 G1)",
            FLUX_GAP,
            "orientation: step 16 holds the board parts face up while the tail arrives with its lands face up "
            "(band-interface.md section 3), so the lands cannot meet unless the board faces down or the tail turns; "
            "no file read here says which (review 3 G3)",
            "alignment: the fixture with the 0.10 mm outline is drawn in no file (review 3, fixture-search.log) and the ring board has no "
            "silkscreen; nothing says how to set the foot on the 0.51 mm pitch (review 3 G3)",
            "heat (note): 260 C, 4 s, 20 N are the band builder's starting values, and the same line gives the Alps "
            "and polyimide limit as 260 C 3 s; step 16 of the guide carries no heat value"]
    if flex2 and land in ("1", "2"):
        f["check"] = ("the battery voltage reaches the power chip; above 2.75 V the chip powers up by itself and "
                      "the ring boots to STANDBY; then USB through CP1 to CP4: the ring enumerates and GET_INFO answers")
        f["check_possible_at_this_step"] = "yes"
        cites["check"] = [C(A, "once FLEX2 is joined, the battery voltage reaches the power chip")]
        cites["check_possible_at_this_step"] = [C(A, "once FLEX2 is joined, the battery voltage reaches the power chip")]
    elif flex2 and land == "3":
        f["check"] = "MISSING"
        f["check_possible_at_this_step"] = "yes"
        cites["check"] = [C(A, "That proves the four pads, FLEX2 and J_BAND_B at once.")]
        cites["check_possible_at_this_step"] = [C(A, "That proves the four pads, FLEX2 and J_BAND_B at once.")]
        gaps.append("check: the step 16 check proves the cell supply and the four USB lands; no check at step 16 "
                    "names land 3 (NTC)")
    elif flex2:
        f["check"] = "the jig's spring pins on CP1 to CP4 give USB; the ring enumerates and GET_INFO answers"
        f["check_possible_at_this_step"] = "yes"
        cites["check"] = [C(A, "the ring enumerates and GET_INFO answers")]
        cites["check_possible_at_this_step"] = [C(A, "That proves the four pads, FLEX2 and J_BAND_B at once.")]
    else:
        test = "T-MOTOR" if r["signal_A"] in ("VMOT",) or "MOT" in r["end_A_pin"] else "T-JOY and T-CENTRE"
        f["check"] = "%s pass in the factory test of the open ring [needs step 18]" % test
        f["check_possible_at_this_step"] = "no, 18"
        cites["check"] = [C(A, "T-SCREEN (screen without glass), T-SIGN")]
        cites["check_possible_at_this_step"] = [C(A, "T-SCREEN (screen without glass), T-SIGN"),
                                                C(A, "Lifting the board after this tears the ribbons.")]
        gaps.append("check: nothing checks this FLEX1 land at step 16 (band-interface.md section 7 asks continuity "
                    "'by the test pads', but none of the 12 test pads of step 5 carries this net); the first proof "
                    "is %s at step 18, after step 17 closes the joint for good" % test)
    add("J-%s-A" % wid, wid, "A", f, cites, " ; ".join(gaps))

# ---------------- 2. switch terminals reflowed on FLEX1 (B ends) ----------------
SWB = ["W001", "W002", "W003", "W004", "W005", "W010", "W011", "W016", "W017", "W018", "W019", "W020"]
for wid in SWB:
    r = W[wid]
    f = dict(what_meets_what="%s, switch terminal on its land, every ring size US 7 to 13" % end_words(r, "B"),
             step="6", solder_source="MISSING", flux="MISSING",
             tool="reflow oven, the head on a flat carrier",
             heat="MISSING",
             orientation=("switch on the F.Cu face of the FLEX1 head, the head flat on the carrier with its "
                          "stiffener under it; footprint turns SW1 90, SW2 90, SW3 -90, SW4 180, SW5 0 degrees"),
             alignment=("the cross at 2.4 mm from the cap axis, SW2 at the centre, 0.30 mm to its neighbours; each "
                        "switch on the lands of footprint Alps_SKTAAAE010_pads34 (SW1, SW3, SW4, SW5) or "
                        "Alps_SKTAAAE010_4pad (SW2), drawn in design/ecad/band/flex1-us7.kicad_pcb to flex1-us13.kicad_pcb"),
             check=("each switch closes its own line and no other (ohmmeter on the ribbon's board end while pressing) "
                    "and reads open when released; height 0.53 mm; switch base flat on the head, feeler 0.02 mm"),
             check_possible_at_this_step="yes")
    cites = dict(wiring_line=[wcite(wid)], end=[wcite(wid, r["join_B"])], what_meets_what=[wcite(wid)],
                 step=[C(A, "### Step 6. Solder the five joystick switches on the ribbon FLEX1")],
                 solder_source=[C(BI, "- Solder: reflow, paste 0.08 thick"), C(A, "with solder paste and reflow on a flat carrier"),
                                C(FLEXLOG, "flex pads with a Paste layer:")],
                 flux=fluxc,
                 tool=[C(A, "with solder paste and reflow on a flat carrier"), C(A, "REFLOW: soldering in an oven")],
                 heat=[C(BI, "peak 260 C 3 s max, at most 2 reflows")],
                 orientation=[C(BI, "SW1 90, SW2 90, SW3 -90, SW4 180, SW5 0 degrees"), wcite(wid, r["end_B_face"]),
                              C(A, "the flex maker bonds the stiffener to the head before this step")],
                 alignment=[C(A, "the cross at 2.4 mm from the cap axis"), C(BI, 'Footprint "Alps_SKTAAAE010_pads34"'),
                            C(A, "FLEX1 is drawn as a board for each size")],
                 check=[C(A, "each switch closes its own line and no other")],
                 check_possible_at_this_step=[C(A, "each switch closes its own line and no other")])
    gaps = ["solder: paste 0.08 thick is asked, but the flex fab folders hold no paste layer and the switch pads carry "
            "no paste layer (logs/flex-fab-listing.log, pads/flex1-us9-pads.csv), so no stencil can be cut, and no "
            "file says how else the paste goes on (review 3 G7)",
            FLUX_GAP,
            "heat: no reflow profile; only Alps' limit (peak 260 C 3 s max, at most 2 reflows) is given",
            G2]
    add("J-%s-B" % wid, wid, "B", f, cites, " ; ".join(gaps))

# ---------------- 3. motor leads on FLEX1 lands (B ends) ----------------
for wid in ["W021", "W022", "W023", "W024"]:
    r = W[wid]
    plus = r["signal_B"] == "VMOT"
    f = dict(what_meets_what="%s, the motor's %s lead on its land, every ring size US 7 to 13" % (
                 end_words(r, "B"), "red (+)" if plus else "blue (-)"),
             step="7", solder_source="MISSING", flux="MISSING", tool="hand soldering iron",
             heat="iron 320 C, 2 s",
             orientation=("red lead to land 1 (+, VMOT), the land nearer the slot" if plus else
                          "blue lead to land 2 (-, GND), the land farther from the slot") +
                         "; the motor stands on the +X side of the tail, so the leads arrive from +v",
             alignment=("stripped end laid along the 0.80 mm side of its land (lands 0.30 x 0.80 at pitch 1.0); "
                        "FLEX1 has no mark on it"),
             check=("3.0 V through a 200 mA current limit, + on land 7 (VMOT) and - on land 6 (GND) of J_BAND_A at "
                    "the ribbon's board end, for 0.5 s: the motor vibrates"),
             check_possible_at_this_step="yes")
    cites = dict(wiring_line=[wcite(wid)], end=[wcite(wid, r["join_B"])], what_meets_what=[wcite(wid)],
                 step=[C(A, "### Step 7. Solder the motor's lead wires to FLEX1")],
                 solder_source=[C(A, "Strip 0.6 mm, tin the end"), C(BI, "strip 0.6 mm, tin it")],
                 flux=fluxc, tool=[C(A, "by hand soldering (iron 320 C, 2 s)")],
                 heat=[C(A, "by hand soldering (iron 320 C, 2 s)")],
                 orientation=[C(A, "The + land is the land nearer the slot"), C(BI, "The motor stands on the +X side of the tail")],
                 alignment=[C(A, "lay it along the 0.80 mm side of its land"), C(A, "FLEX1 has no mark on it"),
                            C(BI, "two lands 0.30 along the tail x 0.80 across, pitch 1.0")],
                 check=[C(A, "apply 3.0 V through a 200 mA current limit")],
                 check_possible_at_this_step=[C(A, "apply 3.0 V through a 200 mA current limit")])
    gaps = ["solder: the lead end is tinned (step 7), but no file read here names the solder (alloy, wire size) for the tinning "
            "or the joint, nor whether the land is tinned first", FLUX_GAP, G2]
    add("J-%s-B" % wid, wid, "B", f, cites, " ; ".join(gaps))

# ---------------- 4. cell pack tabs on FLEX2 lands (B ends) ----------------
TABTXT = {"1": ("tab P+ on land 1 (VBAT)", "the meter's red probe on land 1 (VBAT) reads the cell voltage, positive against land 2 (GND)"),
          "2": ("tab P- on land 2 (GND)", "the meter's red probe on land 1 (VBAT) reads the cell voltage, positive against land 2 (GND)"),
          "3": ("tab NTC on land 3 (NTC)", "about 10 k between land 3 (NTC) and land 2 (GND) at room temperature")}
for wid in ["W025", "W026", "W027", "W033", "W034", "W035"]:
    r = W[wid]
    land = r["end_B_pin"].split()[0]
    o, chk = TABTXT[land]
    f = dict(what_meets_what="%s, a tab of the bought cell pack on its land, every ring size US 7 to 13" % end_words(r, "B"),
             step="9", solder_source="MISSING", flux="MISSING", tool="hand soldering iron",
             heat="iron 280 C at most, 2 s per joint",
             orientation="%s; the lands sit on the tail's outer face (F.Cu, facing the cell)" % o,
             alignment=("tabs in the order P+, NTC, P- from the slot toward the cell (lands 1, 3, 2); lands of footprint "
                        "PRT1_Tabs 0.26 along the tail x 0.45 across, pitch 0.43; first land centre at s = 0.586 mm "
                        "(US 7) to 1.774 mm (US 13) after the slot junction"),
             check=chk + ", at the ribbon's board end", check_possible_at_this_step="yes")
    cites = dict(wiring_line=[wcite(wid)], end=[wcite(wid, r["join_B"])], what_meets_what=[wcite(wid)],
                 step=[C(A, "### Step 9. Join the cell, its protection circuit and the thermistor to FLEX2")],
                 solder_source=[C(BI, "solder SAC305 0.3 wire or a pre-tinned land")],
                 flux=fluxc, tool=[C(A, "by hand soldering at low heat (iron 280 C at most, 2 s per joint)")],
                 heat=[C(A, "by hand soldering at low heat (iron 280 C at most, 2 s per joint)")],
                 orientation=[C(A, "Tab P+ goes on land 1 (VBAT), tab NTC on land 3 (NTC), tab P- on land 2 (GND)"),
                              C(BI, "The lands sit on the tail's outer face (F.Cu, facing the cell)")],
                 alignment=[C(A, "The tabs lie in the order P+, NTC, P- from the slot toward the cell"),
                            C(BI, "FLEX2 lands (footprint PRT1_Tabs): 0.26 along the tail x 0.45 across, pitch 0.43"),
                            C(BI, "first land centre at s = 0.586 (US 7)")],
                 check=[C(A, "the meter's red probe on land 1 reads a positive voltage") if land != "3"
                        else C(A, "the thermistor inside the pack reads about 10 k")],
                 check_possible_at_this_step=[C(A, "the cell voltage appears on the cell lands at the ribbon's board end")])
    gaps = ["solder: band-interface.md offers SAC305 0.3 wire OR a pre-tinned land; step 9 names neither, and no step "
            "tins the PRT1 lands", FLUX_GAP, G2]
    add("J-%s-B" % wid, wid, "B", f, cites, " ; ".join(gaps))

# ---------------- 5. gold discs on FLEX2 (B ends) ----------------
DISCLAND = {"CP1": "4", "CP2": "5", "CP3": "6", "CP4": "7"}
for wid in ["W029", "W030", "W031", "W032"]:
    r = W[wid]
    cp = r["end_B_ref"]
    f = dict(what_meets_what="%s, gold-plated disc 1.6 mm x 0.07 mm soldered flat on its land, every ring size US 7 to 13" % end_words(r, "B"),
             step="8",
             solder_source="SAC305 paste, one dot per land put on with a dispensing needle, the dot smaller than the land",
             flux="MISSING",
             tool="hot plate (cold at the start), dispensing needle, tweezers, 10 times lens",
             heat="MISSING",
             orientation="flat ribbon on the plate, pad lands (B.Cu) up; one disc per land, the four discs are alike",
             alignment="disc centred on its 1.6 mm land by eye under a 10 times lens",
             check=("disc flat on its land and centred, no tilt; continuity from the disc to land %s of J_BAND_B at the "
                    "ribbon's board end; no short between neighbouring discs or their lands; disc flush with the liner's "
                    "inner face [needs step 21]" % DISCLAND[cp]),
             check_possible_at_this_step="yes")
    cites = dict(wiring_line=[wcite(wid)], end=[wcite(wid, r["join_B"])], what_meets_what=[wcite(wid), C(A, "The pad is a gold-plated disc, 1.6 mm across and 0.07 mm thick")],
                 step=[C(A, "### Step 8. Make the charging pads on FLEX2")],
                 solder_source=[C(A, "Put one dot of SAC305 paste on each of the four lands with a dispensing needle")],
                 flux=fluxc,
                 tool=[C(A, "Lay the flat ribbon on a clean hot plate that is still cold"), C(A, "Lay one disc on each dot with tweezers")],
                 heat=[C(A, "Heat the plate until the paste turns bright")],
                 orientation=[C(A, "pad lands up"), wcite(wid, r["end_B_face"])],
                 alignment=[C(A, "centred by eye under a 10 times lens")],
                 check=[C(A, "each disc lies flat on its land and is centred on it"),
                        C(A, "each disc is flush with the liner's inner face as the model says"),
                        C(A, "### Step 21. Cast the resin liner")],
                 check_possible_at_this_step=[C(A, "each disc lies flat on its land and is centred on it")])
    gaps = [FLUX_GAP + " (the flux type of the paste, no-clean or to be washed, is not named and no cleaning follows step 8)",
            "heat: no plate temperature or time, only 'until the paste turns bright' (SAC305 melts at 217 to 220 C)",
            "check: step 8 asks 'flush with the liner's inner face', which needs the liner cast at step 21; how high "
            "the disc stands on its solder before the cast is not given (review 3 G5)", G2]
    add("J-%s-B" % wid, wid, "B", f, cites, " ; ".join(gaps))

# ---------------- 6. screen cable contacts in J1 (B ends) ----------------
for n in range(40, 54):
    wid = "W%03d" % n
    r = W[wid]
    f = dict(what_meets_what="%s cable contact %s (%s) to %s" % (r["end_A_ref"], r["end_A_pin"], r["end_A_face"], end_words(r, "B")),
             step="15", solder_source="none: pressed contact", flux="none: pressed contact",
             tool="MISSING",
             heat="none: pressed contact, no heat; lever open (1.8 mm high), cable in, lever closed",
             orientation=("screen turned 180 degrees; the cable enters J1 from the fingertip side (+X), lying flat above "
                          "the board, contacts facing UP away from the board, contact 1 on the +Y side (antenna side); the "
                          "glass-and-panel unit lies folded away beyond the fingertip end while the cable goes in"),
             alignment=("J1 by its land pattern on the screen face at X -4.933, Y -0.003; the cable's neck, 4.8 mm wide, "
                        "centred in J1's opening; the cable end at X -4.833"),
             check=("latch closed over the whole cable width (microscope); contact 1 on the +Y side, checked on the "
                    "maker's drawing page 5 before the lever is closed; cable flat in J1 and not skewed"),
             check_possible_at_this_step="yes")
    cites = dict(wiring_line=[wcite(wid)], end=[wcite(wid, r["join_B"])], what_meets_what=[wcite(wid)],
                 step=[C(A, "### Step 15. Turn the screen, plug its cable into J1 on the screen face")],
                 solder_source=[wcite(wid, "no soldered end (pressed contact in J1)")],
                 flux=[wcite(wid, "no soldered end (pressed contact in J1)")],
                 tool=[C(A, "The lever of J1 is open for this")],
                 heat=[C(A, "The lever of J1 is open for this"), C(SC, "0.9 +-0.1 high; 1.8 high with the lever open")],
                 orientation=[C(A, "The screen is turned 180 degrees"), C(A, "with its contacts facing UP, away from the board"),
                              C(SC, "the cable is plugged into J1 with the lever open")],
                 alignment=[C(A, "J1 (`screen_connector`) on the screen face at X -4.933, Y -0.003"),
                            C(A, "the cable's neck, 4.8 mm wide, centred in J1's opening"), C(A, "the cable end then lies at X -4.833")],
                 check=[C(A, "the latch is closed over the whole cable width")],
                 check_possible_at_this_step=[C(A, "the latch is closed over the whole cable width")])
    gaps = ["tool: no file read here names the tool to open and close J1's lever or to push the 0.3 mm pitch cable in",
            "check: the continuity of this contact cannot be measured at step 15 (no test pad, or only a no-short "
            "test TP17 to TP18); the guide leaves it to T-SCREEN at step 18 and marks it open for the lead, while J1 "
            "can be opened only until step 17"]
    add("J-%s-B" % wid, wid, "B", f, cites, " ; ".join(gaps))

# ---------------- 7. spring pin tip on the gold disc (A ends) and 8. spring pin into PCB2 (B ends) ----------------
for wid in ["W054", "W055", "W056", "W057"]:
    r = W[wid]
    pin = r["end_B_ref"]
    f = dict(what_meets_what="%s %s %s (%s) under case spring pin %s's plunger tip; %s" % (
                 r["end_A_board"], r["end_A_ref"], r["end_A_pin"], r["end_A_face"], pin, r["join_A"]),
             step="28", solder_source="none: pressed contact", flux="none: pressed contact",
             tool="none: the ring is set by hand into the pocket and around the post, lid closed",
             heat="no heat; the pins push the band with 4 x 0.39 N",
             orientation=("ring with its band axis vertical, the band's bottom face on the floor, the block in the pocket "
                          "on the +X side of the post; a ring flipped over is not blocked at every size (the case then "
                          "blinks amber 3 times: turn the ring over)"),
             alignment=("pin y equals pad y within 0.006 mm (pins at +3.521, +1.197, -1.197, -3.521); pin working height "
                        "1.98 to 2.15 mm over the 7 sizes, inside the maker's 1.90 to 2.20 mm"),
             check=("the case lights blue breathing while it copies; no attach within 3 s gives an amber blink 3 times; "
                    "on the first case the ring is listed by the case's chip and 100 MB are copied without an error"),
             check_possible_at_this_step="yes")
    cites = dict(wiring_line=[wcite(wid)], end=[wcite(wid, r["join_A"])], what_meets_what=[wcite(wid)],
                 step=[C(A, "### Step 28. Pack"), C(A, "The ring goes into its case.")],
                 solder_source=[wcite(wid, "pressed contact (pin tip on the disc)")],
                 flux=[wcite(wid, "pressed contact (pin tip on the disc)")],
                 tool=[C(CA, "Ring set into the pocket and around the post, lid closed")],
                 heat=[C(CA, "the pins push the band onto the V wall with 4 x 0.39 N")],
                 orientation=[C(CA, "The ring stands with its band axis vertical"), C(CA, "A ring FLIPPED over"),
                              C(CA, 'light amber blink 3 times ("turn the ring over"')],
                 alignment=[C(BN, "equals the y of its ring pad"), C(CA, "each pin stands at 1.98 to 2.15 mm")],
                 check=[C(CA, "Light: blue breathing."), C(CA, 'light amber blink 3 times ("turn the ring over"'),
                        C(LD, "The ring's USB link through the 4 spring pins is tested on the first case")],
                 check_possible_at_this_step=[C(CA, "Light: blue breathing.")])
    add("J-%s-A" % wid, wid, "A", f, cites, "")

    f = dict(what_meets_what="%s %s, spring pin %s (Harwin P70-6000045R) in its plated hole; %s" % (
                 r["end_B_board"], r["end_B_face"], pin, r["join_B"]),
             step="case 3", solder_source="MISSING", flux="MISSING", tool="MISSING", heat="MISSING",
             orientation="pin on the front face of PCB2 (F.Cu, the face with the pins and the five wire pads), only the 0.60 mm plunger stands out of the holder",
             alignment=("pin in its plated hole (pad 1.70, hole 1.10, footprint HARWIN_P70_6000045R); wing marks 'P1 +' "
                        "and 'P4 -' on the front face: the mark on each wing, not its shape, tells which is which"),
             check=("depth gauge after the stakes are formed: free plunger tip in front of the holder face, P2 and P3 "
                    "1.170 mm +-0.04, P1 and P4 1.021 mm +-0.03 [needs case 4]; continuity plunger tip to its main "
                    "board pad, beep below about 50 ohm [needs case 8]"),
             check_possible_at_this_step="no, case 8")
    cites = dict(wiring_line=[wcite(wid)], end=[wcite(wid, r["join_B"])], what_meets_what=[wcite(wid)],
                 step=[C(BN, "3. Which end first:"), C(BN, "So: solder P1 to P4 and the five wire ends on the pin board")],
                 solder_source=[C(CA, "Order: solder P1 to P4 to PCB2")], flux=fluxc,
                 tool=[C(CA, "Order: solder P1 to P4 to PCB2"), wcite(wid, "solder (P1 to P4 soldered to PCB2)")],
                 heat=[C(CA, "Order: solder P1 to P4 to PCB2")],
                 orientation=[C(BN, "PCB2 front (F.SilkS, the face with the pins and the five wire pads)"),
                              C(CA, "only the 0.60 mm plungers stand out")],
                 alignment=[C(BN, '"Recommended PC Board Pattern": pad 1.70, hole 1.10'),
                            C(BN, "the mark on each wing, not its shape, tells which is which")],
                 check=[C(BN, "4. Depth gauge, after the stakes are formed"), C(BN, "P1 to W1, P2 to W2, P3 to W3, P4 to W4 must all beep")],
                 check_possible_at_this_step=[C(BN, "8. Check after soldering")])
    gaps = ["solder, flux, tool and heat: the files say only 'solder P1 to P4 to PCB2' (iron or reflow, solder, flux, "
            "temperature and time are in no file read here; the Harwin documents in design/datasheets were not searched here: unverified)"]
    add("J-%s-B" % wid, wid, "B", f, cites, " ; ".join(gaps))

# ---------------- 9. case wires W1 to W4, W7 (A ends on PCB2, B ends on PCB1) ----------------
WCOL = {"W063": "W1 red", "W064": "W2 white", "W065": "W3 green", "W066": "W4 black", "W067": "W7 yellow"}
for wid in ["W063", "W064", "W065", "W066", "W067"]:
    r = W[wid]
    wire = WCOL[wid]
    for e in "AB":
        if e == "A":
            f = dict(what_meets_what="%s, wire %s (30 AWG stranded) laid on the pad" % (end_words(r, "A"), wire),
                     step="case 6",
                     orientation=("stripped end laid flat on the pad of the same number, on the front face of the pin "
                                  "board; order inside the end W4, W2, W3, W7, W1"),
                     alignment=("each wire pad in the column of its pin (WP1 with P1, WP2 under P2, WP3 under P3, WP4 "
                                "under P4, WP7 in the middle below E1); pads 0.9 mm wide, WP2, WP7 and WP3 only 0.30 mm apart"),
                     check=("colour against the table and the wire not touching the next pad; continuity at case step 8, "
                            "beep below about 50 ohm [needs case 8]"))
            cites = dict(step=[C(BN, "6. Pin board end:")],
                         orientation=[C(BN, "lay the stripped end flat on the pad of the same number"), C(BN, "5. Order inside each end:")],
                         alignment=[C(BN, "each wire pad is in the column of its pin")],
                         check=[C(BN, "check that the wire is not touching the next pad"), C(BN, "P1 to W1, P2 to W2, P3 to W3, P4 to W4 must all beep")])
        else:
            f = dict(what_meets_what="%s, wire %s (30 AWG stranded) through the hole" % (end_words(r, "B"), wire),
                     step="case 7",
                     orientation=("wire through the hole of its label, soldered on the face the wire stands out of; "
                                  "order inside the end W4, W2, W3, W7, W1"),
                     alignment=("labels W1 +, W2 D-, W7 TCH, W3 D+, W4 GND on the bottom face in the row of each hole "
                                "(printed mirrored); the holes are one column in the floor slot, order W1, W2, W7, W3, W4, 1.6 mm pitch"),
                     check=("continuity plunger tip to main board pad (P1 to W1, P2 to W2, P3 to W3, P4 to W4) beeps "
                            "(below about 50 ohm), E1 to W7 beeps; no beep between any two of the five pads; about "
                            "147 kohm between W1 and W4 is normal [needs case 8]"))
            cites = dict(step=[C(BN, "7. Main board end:")],
                         orientation=[C(BN, "Put each wire through the hole of its label"), C(BN, "solder on the face the wire stands out of")],
                         alignment=[C(BN, "The bottom face of the main board carries the labels W1 +"), C(BN, "the five holes are one column in the floor slot")],
                         check=[C(BN, "P1 to W1, P2 to W2, P3 to W3, P4 to W4 must all beep"), C(BN, "A reading of about 147 kohm between W1 and W4 is normal")])
        f.update(solder_source="MISSING", flux="MISSING", tool="hand soldering iron", heat="MISSING",
                 check_possible_at_this_step="no, case 8")
        cites.update(wiring_line=[wcite(wid)], end=[wcite(wid, r["join_" + e])], what_meets_what=[wcite(wid), C(LD, "W1 (VRING) red, W2 (USB_D-) white")],
                     solder_source=[C(BN, "Strip 2.5 mm of insulation from both ends of each wire")], flux=fluxc,
                     tool=[wcite(wid, r["join_" + e])], heat=[C(BN, "Strip 2.5 mm of insulation from both ends of each wire")],
                     check_possible_at_this_step=[C(BN, "8. Check after soldering")])
        gaps = ["solder: the ends are tinned at case step 1, but no file read here names the solder (alloy, wire size)", FLUX_GAP,
                "heat: no iron temperature or time for the 30 AWG wire joints"]
        if wid == "W063" and e == "B":
            gaps.append("check: VRING also carries C15, so a continuity meter may chirp while it charges; the check does not say to wait for a steady reading (review 3 G10)")
        add("J-%s-%s" % (wid, e), wid, e, f, cites, " ; ".join(gaps))

# ---------------- 10. case cell leads (B ends) ----------------
for wid, txt, mark in [("W059", "red lead (+) through the hole marked 'W5 +', cut 13.0 mm, 2 mm stripped", "'W5 +' 1.35 mm from hole W5"),
                       ("W060", "black lead (-) through the hole marked 'W6 -', cut 15.2 mm, 2 mm stripped", "'W6 -' 1.45 mm from hole W6")]:
    r = W[wid]
    f = dict(what_meets_what="%s, the case cell's own lead" % end_words(r, "B"), step="case 9",
             solder_source="MISSING", flux="MISSING", tool="hand soldering iron", heat="MISSING",
             orientation=txt + "; before cutting, the red probe on the red lead reads +3.0 to 4.35 V",
             alignment="mark %s on the bottom face of the main board, printed mirrored" % mark,
             check="MISSING", check_possible_at_this_step="yes")
    cites = dict(wiring_line=[wcite(wid)], end=[wcite(wid, r["join_B"])], what_meets_what=[wcite(wid)],
                 step=[C(BN, "9. Cell leads W5 and W6 and thermistor TH1")],
                 solder_source=[C(BN, "the cell's red lead (+) goes through the hole marked")], flux=fluxc,
                 tool=[wcite(wid, r["join_B"])],
                 heat=[C(LD, "it states no gauge, no insulation, no polarity by colour and no solder limit")],
                 orientation=[C(BN, "the cell's red lead (+) goes through the hole marked"), C(BN, "Before cutting, measure the cell with the red probe on the red lead")],
                 alignment=[C(BN, '"W5 +" 1.35 mm from the hole W5 (BAT), "W6 -" 1.45 mm from the hole W6 (GND)')],
                 check=[C(BN, "Before cutting, measure the cell with the red probe on the red lead")],
                 check_possible_at_this_step=[C(BN, "9. Cell leads W5 and W6 and thermistor TH1")])
    gaps = ["solder: no file read here names the solder for the cell leads", FLUX_GAP,
            "heat: no iron temperature or time (the cell maker states no solder limit)",
            "check: no check after the joint is named (only the polarity test before cutting)"]
    add("J-%s-B" % wid, wid, "B", f, cites, " ; ".join(gaps))

# ---------------- 11. case thermistor leads (B ends) ----------------
for wid in ["W061", "W062"]:
    r = W[wid]
    f = dict(what_meets_what="%s, a bare lead of the 103AT-2 thermistor" % end_words(r, "B"), step="case 9",
             solder_source="MISSING", flux="MISSING", tool="50 W soldering iron",
             heat="at most 7 seconds at 340 degrees C, the joint 5 mm or more from the bead",
             orientation="either way round, one lead in each of the two holes TH1.1 and TH1.2, leads cut to 10 mm from the bead",
             alignment="mark 'TH1' 1.45 mm below the two thermistor holes, bottom face, printed mirrored",
             check="the two bare leads stay 2.54 mm apart and touch nothing else (by eye); continuity test to the cell's can: open",
             check_possible_at_this_step="yes")
    cites = dict(wiring_line=[wcite(wid)], end=[wcite(wid, r["join_B"])], what_meets_what=[wcite(wid)],
                 step=[C(BN, "9. Cell leads W5 and W6 and thermistor TH1")],
                 solder_source=[C(BN, "at most 7 seconds at 340 degrees C with a 50 W iron")], flux=fluxc,
                 tool=[C(BN, "at most 7 seconds at 340 degrees C with a 50 W iron")],
                 heat=[C(BN, "at most 7 seconds at 340 degrees C with a 50 W iron"), C(BN, "joints 5 mm or more from the bead")],
                 orientation=[C(BN, "cut to 10 mm, one in each of the two holes at the mark")],
                 alignment=[C(BN, '"TH1" 1.45 mm below the two thermistor holes')],
                 check=[C(LD, "checked by eye and with a continuity test to the cell's can: open")],
                 check_possible_at_this_step=[C(LD, "checked by eye and with a continuity test to the cell's can: open")])
    gaps = ["solder: no file read here names the solder for the thermistor leads", FLUX_GAP]
    add("J-%s-B" % wid, wid, "B", f, cites, " ; ".join(gaps))

# ---------------- 12. ANT1 on the ring board (A ends) ----------------
FID_GAP = ("alignment: step 2 locates by 'fiducials of the board file', but no board file holds a fiducial "
           "(logs/fiducial-search.log)")
for wid in ["W036", "W037", "W038", "W039"]:
    r = W[wid]
    pad = r["end_A_pin"].split()[0]
    f = dict(what_meets_what="%s, the antenna's pad on its maker's land pattern" % end_words(r, "A"), step="2",
             solder_source="paste layer design/ecad/ring/pcb/fab/gerber/ring-F_Paste.gbr for ANT1:%s" % pad,
             flux="MISSING", tool="paste stencil and reflow oven (pass 2)", heat="MISSING",
             orientation=("pass 2: parts face (F.Cu) up, the board on a carrier with the screen face down and a pocket "
                          "under J1; nobody moves the board while the solder is liquid"),
             alignment="MISSING",
             check="optical inspection of every part of the parts face after pass 2 other than U1, U2, U4 and U3; expected look: MISSING",
             check_possible_at_this_step="yes")
    cites = dict(wiring_line=[wcite(wid)], end=[wcite(wid, r["join_A"])], what_meets_what=[wcite(wid)],
                 step=[C(A, "### Step 2. Print paste, place the board parts on both faces")],
                 solder_source=[C(A, "PASS 2, the PARTS FACE (KiCad F.Cu, 72 parts")], flux=fluxc,
                 tool=[C(A, "REFLOW: soldering in an oven")],
                 heat=[C(A, "The number of reflow passes that J1 and the 0201 parts accept is not in any file cited here")],
                 orientation=[C(A, "the board lies on a carrier with the screen face down")],
                 alignment=[C(A, "fiducials of the board file"), C(FIDLOG, "--- refs starting FID:")],
                 check=[C(A, "optical inspection of every other part of the parts face")],
                 check_possible_at_this_step=[C(A, "optical inspection of every other part of the parts face")])
    gaps = [FLUX_GAP, "heat: no reflow profile for pass 2 in assembly.md, band-interface.md or design/mfg/specs (logs/profile-search.log)", FID_GAP,
            "check: no file read here says what a good ANT1 joint looks like (expected value)"]
    add("J-%s-A" % wid, wid, "A", f, cites, " ; ".join(gaps))

# ---------------- 13. board passes ----------------
f = dict(what_meets_what="ring main board, parts face (KiCad F.Cu): every part of ring-pos-front.csv except the land rows J_BAND_A and J_BAND_B",
         step="2",
         solder_source="paste layer design/ecad/ring/pcb/fab/gerber/ring-F_Paste.gbr for parts of design/ecad/ring/pcb/fab/ring-pos-front.csv except J_BAND_A,J_BAND_B",
         flux="MISSING", tool="paste stencil and reflow oven (pass 2)", heat="MISSING",
         orientation="pass 2: parts face up, the board on a carrier with the screen face down and a pocket under J1",
         alignment="MISSING",
         check=("X-ray of U1 (61 balls), U2, U4 and the U3 lands; optical inspection of every other part of the parts "
                "face; then the screen face again: all 9 parts still in place, J1 still flat"),
         check_possible_at_this_step="yes")
cites = dict(wiring_line=[C(A, "PASS 2, the PARTS FACE (KiCad F.Cu, 72 parts")], end=[C(A, "PASS 2, the PARTS FACE (KiCad F.Cu, 72 parts")],
             what_meets_what=[C(A, "PASS 2, the PARTS FACE (KiCad F.Cu, 72 parts"), C(A, "J_BAND_A and J_BAND_B are copper on the parts face and get no paste")],
             step=[C(A, "### Step 2. Print paste, place the board parts on both faces")],
             solder_source=[C(A, "PASS 2, the PARTS FACE (KiCad F.Cu, 72 parts")], flux=fluxc,
             tool=[C(A, "REFLOW: soldering in an oven")],
             heat=[C(A, "The number of reflow passes that J1 and the 0201 parts accept is not in any file cited here")],
             orientation=[C(A, "the board lies on a carrier with the screen face down")],
             alignment=[C(A, "fiducials of the board file"), C(FIDLOG, "--- refs starting FID:")],
             check=[C(A, "After PASS 2, X-ray of U1 (61 balls)")],
             check_possible_at_this_step=[C(A, "After PASS 2, X-ray of U1 (61 balls)")])
add("P-ring-F", "board pass", "ring F.Cu", f, cites, " ; ".join([FLUX_GAP, "heat: no reflow profile for pass 2 in assembly.md, band-interface.md or design/mfg/specs (logs/profile-search.log)", FID_GAP]))

f = dict(what_meets_what="ring main board, screen face (KiCad B.Cu): J1 and the eight 0201 parts C1, C2, C5, C7, C14, FB1, R71, R72 (and the 12 test pads, which the stencil maker closes)",
         step="2",
         solder_source="paste layer design/ecad/ring/pcb/fab/gerber/ring-B_Paste.gbr for parts of design/ecad/ring/pcb/fab/ring-pos-back.csv except none",
         flux="MISSING", tool="paste stencil and reflow oven (pass 1)", heat="MISSING",
         orientation="pass 1, first: the screen face; the parts face goes second",
         alignment="MISSING",
         check=("optical inspection of the screen face at 10 times: J1 flat with none of its 15 contact tails and 2 "
                "mounting tails lifted, no bridge between neighbouring contacts (0.3 mm pitch), each 0201 part in "
                "place and not tilted, no solder on any of the 12 test pads"),
         check_possible_at_this_step="yes")
cites = dict(wiring_line=[C(A, "PASS 1, the SCREEN FACE (KiCad B.Cu, 21 parts")], end=[C(A, "PASS 1, the SCREEN FACE (KiCad B.Cu, 21 parts")],
             what_meets_what=[C(A, "PASS 1, the SCREEN FACE (KiCad B.Cu, 21 parts"), C(A, "so the stencil maker closes those 12 openings")],
             step=[C(A, "### Step 2. Print paste, place the board parts on both faces")],
             solder_source=[C(A, "PASS 1, the SCREEN FACE (KiCad B.Cu, 21 parts")], flux=fluxc,
             tool=[C(A, "REFLOW: soldering in an oven")],
             heat=[C(A, "The number of reflow passes that J1 and the 0201 parts accept is not in any file cited here"),
                   C(RV, "at most 2 reflow cycles, peak 250 C")],
             orientation=[C(A, "the screen face goes first and the parts face second")],
             alignment=[C(A, "fiducials of the board file"), C(FIDLOG, "--- refs starting FID:")],
             check=[C(A, "optical inspection of the screen face at 10 times")],
             check_possible_at_this_step=[C(A, "optical inspection of the screen face at 10 times")])
add("P-ring-B", "board pass", "ring B.Cu", f, cites, " ; ".join([
    FLUX_GAP, "heat: no reflow profile in assembly.md, band-interface.md or design/mfg/specs (logs/profile-search.log); J1 takes at most 2 reflow cycles, peak 250 C (Hirose drawing page 6, read by review 3 G6), and the guide does not say that the two-pass plan uses both", FID_GAP]))

for size in range(7, 14):
    b = "flex1-us%d" % size
    f = dict(what_meets_what="%s (FLEX1 at US %d): the five switches SW1 to SW5 on the head, face F.Cu" % (b, size),
             step="6", solder_source="MISSING", flux="MISSING", tool="reflow oven, the head on a flat carrier",
             heat="MISSING",
             orientation="head flat on the carrier, switches on F.Cu up, stiffener (bonded by the flex maker) under it",
             alignment="the lands of the board file design/ecad/band/%s.kicad_pcb; the cross at 2.4 mm from the cap axis" % b,
             check="each switch closes its own line and no other, reads open when released; height 0.53 mm; bases flat (feeler 0.02 mm)",
             check_possible_at_this_step="yes")
    cites = dict(wiring_line=[C(A, "### Step 6. Solder the five joystick switches on the ribbon FLEX1")],
                 end=[C(A, "FLEX1 is drawn as a board for each size")],
                 what_meets_what=[C(A, "FLEX1 is drawn as a board for each size"), C(A, "SW1 (up), SW3 (down), SW4 (toward the hand)")],
                 step=[C(A, "### Step 6. Solder the five joystick switches on the ribbon FLEX1")],
                 solder_source=[C(BI, "- Solder: reflow, paste 0.08 thick"), C(FLEXLOG, "flex pads with a Paste layer:")], flux=fluxc,
                 tool=[C(A, "with solder paste and reflow on a flat carrier")], heat=[C(BI, "peak 260 C 3 s max, at most 2 reflows")],
                 orientation=[C(A, "the flex maker bonds the stiffener to the head before this step")],
                 alignment=[C(A, "FLEX1 is drawn as a board for each size"), C(A, "the cross at 2.4 mm from the cap axis")],
                 check=[C(A, "each switch closes its own line and no other")],
                 check_possible_at_this_step=[C(A, "each switch closes its own line and no other")])
    add("P-%s" % b, "board pass", b, f, cites, " ; ".join([
        "solder: no paste layer file for %s (logs/flex-fab-listing.log), so no stencil (review 3 G7)" % b, FLUX_GAP,
        "heat: no reflow profile; only Alps' limit"]))
for size in range(7, 14):
    b = "flex2-us%d" % size
    f = dict(what_meets_what="%s (FLEX2 at US %d): the four gold discs CP1 to CP4 on their B.Cu lands (the only parts soldered by heat on FLEX2; the cell tabs follow by iron at step 9)" % (b, size),
             step="8", solder_source="SAC305 paste, one dot per land with a dispensing needle",
             flux="MISSING", tool="hot plate (cold at the start), dispensing needle, tweezers, 10 times lens", heat="MISSING",
             orientation="flat ribbon on the plate, pad lands (B.Cu) up",
             alignment="each disc centred by eye under a 10 times lens on its land of design/ecad/band/%s.kicad_pcb" % b,
             check="each disc flat and centred, no tilt; continuity disc to its J_BAND_B land at the board end; no short between neighbouring discs",
             check_possible_at_this_step="yes")
    cites = dict(wiring_line=[C(A, "### Step 8. Make the charging pads on FLEX2")],
                 end=[C(A, "FLEX2 is drawn as a board for each size")],
                 what_meets_what=[C(A, "FLEX2 is drawn as a board for each size"), C(A, "Four discs, one per land")],
                 step=[C(A, "### Step 8. Make the charging pads on FLEX2")],
                 solder_source=[C(A, "Put one dot of SAC305 paste on each of the four lands with a dispensing needle")], flux=fluxc,
                 tool=[C(A, "Lay the flat ribbon on a clean hot plate that is still cold")], heat=[C(A, "Heat the plate until the paste turns bright")],
                 orientation=[C(A, "pad lands up")],
                 alignment=[C(A, "centred by eye under a 10 times lens"), C(A, "FLEX2 is drawn as a board for each size")],
                 check=[C(A, "each disc lies flat on its land and is centred on it")],
                 check_possible_at_this_step=[C(A, "each disc lies flat on its land and is centred on it")])
    add("P-%s" % b, "board pass", b, f, cites, " ; ".join([FLUX_GAP, "heat: no plate temperature or time"]))

TPS = ",".join("TP%d" % i for i in range(1, 17))
f = dict(what_meets_what="case main board (PCB1) top face: every part of case_main_position.csv except the 16 bare test pads and the wire, cell and thermistor holes",
         step="MISSING",
         solder_source="paste layer design/ecad/case/pcb/fab/case_main/gerber/case_main-F_Paste.gbr for parts of design/ecad/case/pcb/fab/case_main/case_main_position.csv except %s,W1,W2,W3,W4,W5,W6,W7,TH1" % TPS,
         flux="MISSING", tool="MISSING", heat="MISSING",
         orientation="all parts on the top face; no part on the bottom face (only the 16 bare test pads)",
         alignment="MISSING", check="MISSING", check_possible_at_this_step="MISSING")
cites = dict(wiring_line=[C(BN, "Position files: fab/case_main/case_main_position.csv")], end=[C(BN, "Position files: fab/case_main/case_main_position.csv")],
             what_meets_what=[C(BN, "Position files: fab/case_main/case_main_position.csv"), C(LD, "(1) The 16 test pads stay on the bottom face of the case's main board")],
             step=[C(BN, "**Case procedure: soldering order of the five case wires")],
             solder_source=[C(BN, "Gerber files and drill files: fab/case_main/gerber/ (F.Cu, In1.Cu, In2.Cu, B.Cu, masks, paste"),
                            C(LD, "(1) The 16 test pads stay on the bottom face of the case's main board"),
                            C(BN, "Pad names for the wires (solder joints)")],
             flux=fluxc, tool=[C(BN, "**Case procedure: soldering order of the five case wires")],
             heat=[C(BN, "**Case procedure: soldering order of the five case wires")],
             orientation=[C(BN, "no part on the bottom face")],
             alignment=[C(FIDLOG, "--- refs starting FID:")],
             check=[C(BN, "**Case procedure: soldering order of the five case wires")],
             check_possible_at_this_step=[C(BN, "**Case procedure: soldering order of the five case wires")])
add("P-case_main", "board pass", "case_main", f, cites, " ; ".join([
    "step: no step of assembly.md or of the case procedure places and reflows the parts of the case main board",
    "solder: the charger U2's thermal pad (pad 25) has no paste opening in case_main-F_Paste.gbr and no paste layer in its footprint (logs/probe_paste.log)",
    FLUX_GAP, "tool and heat: no reflow method or profile", "alignment: no fiducial on the board (logs/fiducial-search.log)",
    "check: no inspection of the case main board is named; the USB socket J1's shell slots (plated, SH) are soldered by no named step"]))

f = dict(what_meets_what="case pin board (PCB2), three pieces in one file: spring pins P1 to P4 (through hole), five wire pads WP1 to WP4 and WP7, touch strip E1 (copper only); no surface-mount part",
         step="case 3",
         solder_source="MISSING",
         flux="MISSING", tool="MISSING", heat="MISSING",
         orientation="the pins on the front face (F.Cu, the face with the pins and the five wire pads)",
         alignment="wing marks 'P1 +' and 'P4 -' on the front face: the mark on each wing, not its shape, tells which is which",
         check="depth gauge of the free plunger tips after the stakes [needs case 4]; continuity at case step 8 [needs case 8]",
         check_possible_at_this_step="no, case 8")
cites = dict(wiring_line=[C(BN, "PCB2 build")], end=[C(BN, "PCB2 build")],
             what_meets_what=[C(BN, "the pin board file holds three separate closed outlines"), C(BN, "Pad names for the wires (solder joints)")],
             step=[C(BN, "3. Which end first:")],
             solder_source=[C(CA, "Order: solder P1 to P4 to PCB2"), C(PASTELOG, "case_pins-F_Paste.gbr flashes 0")], flux=fluxc,
             tool=[C(CA, "Order: solder P1 to P4 to PCB2")], heat=[C(CA, "Order: solder P1 to P4 to PCB2")],
             orientation=[C(BN, "PCB2 front (F.SilkS, the face with the pins and the five wire pads)")],
             alignment=[C(BN, "the mark on each wing, not its shape, tells which is which")],
             check=[C(BN, "4. Depth gauge, after the stakes are formed"), C(BN, "8. Check after soldering")],
             check_possible_at_this_step=[C(BN, "8. Check after soldering")])
add("P-case_pins", "board pass", "case_pins", f, cites, " ; ".join([
    "solder, flux, tool and heat: the pin board has no reflow (paste layers hold 0 openings, logs/probe_paste.log) and the files say only 'solder P1 to P4 to PCB2'"]))

with open(OUT, "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(ROWS)
with open(os.path.join(HERE, "citations.csv"), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=["joint_id", "field", "path", "line", "quote"])
    w.writeheader()
    w.writerows(CITES)
print("rows", len(ROWS), "citations", len(CITES))
