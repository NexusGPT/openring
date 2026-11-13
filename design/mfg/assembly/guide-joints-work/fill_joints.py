"""Fill design/mfg/assembly/joints.csv for the rows the guide rewrite settles.
Reads joints-before.csv (the table as found), writes ../joints.csv. Every changed field is printed.
Run: design/.venv/bin/python -I <this file>"""
import csv, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import linemap  # noqa: E402

SRC = os.path.join(HERE, "joints-before.csv")
DST = os.path.join(HERE, "..", "joints.csv")
GUIDE = os.path.join(HERE, "..", "assembly.md")
A = "design/mfg/assembly/assembly.md"
ROOT_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

new = open(GUIDE, encoding="utf-8").read().split("\n")
idx = linemap.index(new)
rev = {v: k for k, v in idx.items()}


def L(step, field):
    return "%s:%d" % (A, rev[(step, field)])



def LP(prefix):
    hits = [i for i, l in enumerate(new, 1) if l.startswith(prefix)]
    assert len(hits) == 1, prefix
    return "%s:%d" % (A, hits[0])


lmap = linemap.build()


def remap(text):
    def sub(m):
        old = int(m.group(1))
        to = lmap.get(old, (None,))[0]
        if to is None:
            raise SystemExit("no new line for %s:%d" % (A, old))
        return "%s:%d" % (A, to)
    return re.sub(re.escape(A) + r":(\d+)", sub, text)


rows = list(csv.DictReader(open(SRC, newline="", encoding="utf-8")))
fields = list(rows[0].keys())

HOTBAR = {  # wiring line -> (land, check)
    "W001": ("A1", "board without power, meter in diode mode: red probe on C28 pad 2 (ground), black on SW1 terminal 3: a diode drop (OL open, 0 short); no beep to the neighbour lands"),
    "W002": ("A2", "board without power, diode mode: C28 pad 2 to SW3 terminal 3 reads a diode drop (OL open, 0 short); SW3 t3 to SW4 t3 and to SW2 t1 do not beep"),
    "W003": ("A3", "board without power, diode mode: C28 pad 2 to SW4 terminal 3 reads a diode drop (OL open, 0 short); SW4 t3 to M1 land 1 does not beep"),
    "W004": ("A4", "board without power, diode mode: C28 pad 2 to SW5 terminal 3 reads a diode drop (OL open, 0 short); SW1 t3 to SW5 t3 does not beep"),
    "W005": ("A5", "board without power, diode mode: C28 pad 2 to SW2 terminal 1 reads a diode drop (OL open, 0 short); SW2 t1 to M1 land 1 does not beep"),
    "W011": ("A8", "one of the ground pair A6 and A8 that FLEX1's own copper joins; by the lead's decision a redundant pair, proven as a pair by the electrical test of step 14, no X-ray asked (design/wiring/lead-decisions.md:89). Meter, board without power: SW1 terminal 4 to C28 pad 2 beeps; this proves that at least one of A6 and A8 is joined, not this land alone. Eye: before the press, the land's own smooth solder dome and no bridge to its neighbours (step 14 How 2, at 10 times); after the press the land lies wholly under the foot, and both of its 0.125 mm ends lie under ribbon copper at all 7 sizes, so this land itself cannot be seen; the look of step 14 How 7 judges the foot as a whole: flat, no lifted corner, not moved, no solder ball beside it"),
    "W021": ("A6", "one of the ground pair A6 and A8 that FLEX1's own copper joins; by the lead's decision a redundant pair, proven as a pair by the electrical test of step 14, no X-ray asked (design/wiring/lead-decisions.md:89). Meter, board without power: SW1 terminal 4 to C28 pad 2 beeps; this proves that at least one of A6 and A8 is joined, not this land alone. Eye: before the press, the land's own smooth solder dome and no bridge to its neighbours (step 14 How 2, at 10 times); after the press the land lies wholly under the foot; one of its 0.125 mm ends lies under no ribbon copper and could show through the foot only if the coverlay and the 0.10 mm stiffener let light through, which no file states (not proven); the look of step 14 How 7 judges the foot as a whole: flat, no lifted corner, not moved, no solder ball beside it"),
    "W022": ("A7", "board without power: M1 land 1 (red lead) to C84 pad 1 (VMOT) beeps; M1 land 1 to C28 pad 2 reads the motor's own reading of step 7, not 0 ohm"),
    "W025": ("B1", "board on the cell: C83 pad 1 to C83 pad 2 reads the cell voltage recorded at step 9 within 0.05 V (starting value)"),
    "W026": ("B2", "one of the ground pair B2 and B7 that FLEX2's own copper joins; by the lead's decision a redundant pair, proven as a pair by the electrical test of step 14, no X-ray asked (design/wiring/lead-decisions.md:89). Meter, board on the cell: C83 pad 1 to C83 pad 2 reads the cell voltage recorded at step 9 within 0.05 V (starting value), and disc CP4 to C83 pad 2 beeps; these prove land B1 and that at least one of B2 and B7 is joined, not B2 alone. Eye: before the press, the land's own smooth solder dome and no bridge to its neighbours (step 14 How 2, at 10 times); after the press the land lies wholly under the foot; one of its 0.125 mm ends lies under no ribbon copper and could show through the foot only if the coverlay and the 0.10 mm stiffener let light through, which no file states (not proven); the look of step 14 How 7 judges the foot as a whole: flat, no lifted corner, not moved, no solder ball beside it"),
    "W027": ("B3", "FACTORY ENTER and T-CHARGE pass at the end of the step, as step 14 Check (c) says (design/mfg/assembly/assembly.md:205); an open NTC land reads as cold and T-CHARGE fails with the charger off"),
    "W029": ("B4", "disc CP1 to C71 pad 1 beeps; then USB through CP1 to CP4 enumerates and GET_INFO answers"),
    "W030": ("B5", "USB through CP1 to CP4 enumerates and GET_INFO answers (a D- open or a D+ to D- bridge stops USB)"),
    "W031": ("B6", "USB through CP1 to CP4 enumerates and GET_INFO answers (a D+ open or a D+ to D- bridge stops USB)"),
    "W032": ("B7", "one of the ground pair B2 and B7 that FLEX2's own copper joins; by the lead's decision a redundant pair, proven as a pair by the electrical test of step 14, no X-ray asked (design/wiring/lead-decisions.md:89). Meter: disc CP4 to C83 pad 2 beeps; then USB through CP1 to CP4 enumerates; with the cell voltage at C83 these prove that at least one of B2 and B7 is joined, not B7 alone. Eye: before the press, the land's own smooth solder dome and no bridge to its neighbours (step 14 How 2, at 10 times); after the press the land lies wholly under the foot; one of its 0.125 mm ends lies under no ribbon copper and could show through the foot only if the coverlay and the 0.10 mm stiffener let light through, which no file states (not proven); the look of step 14 How 7 judges the foot as a whole: flat, no lifted corner, not moved, no solder ball beside it"),
}
HB = "design/mfg/assembly/hotbar-joint.md"
SW_LAND = {"W001": 1, "W002": 2, "W003": 3, "W004": 4, "W005": 5}

changed = 0


def setf(r, k, v):
    global changed
    if r[k] != v:
        print("%s | %s | %s -> %s" % (r["joint_id"], k, r[k][:70].replace("\n", " "), v[:110]))
        r[k] = v
        changed += 1


for r in rows:
    jid, wl, st = r["joint_id"], r["wiring_line"], r["step"]
    # every row: citations of the guide follow the new line numbers
    for k in fields:
        if A + ":" in r[k]:
            setf(r, k, remap(r[k]))
    if jid.startswith("J-") and jid.endswith("-A") and wl in HOTBAR:
        land, chk = HOTBAR[wl]
        setf(r, "step", "14")
        setf(r, "solder_source", "alloy SAC305 (process.md P1.1); form: a solder layer of about 0.03 mm on each board land, Kester NP505-HR paste printed through the 0.075 mm parts face stencil in pass 2 of step 2 and reflowed (hotbar-joint.md section 1; guide step 2); the opening at this land in ring-F_Paste.gbr: MISSING, the board helper adds the 15 openings (hotbar-joint.md section 7)")
        setf(r, "flux", "Kester 959T no-clean liquid flux, ORL0, a thin coat on the lands of this foot only, dried before the press; flash point 18 C (process.md P1.4)")
        setf(r, "tool", "hot bar (thermode), blade 2.5 x 1.6 mm on the foot's stiffener (a 3 mm blade lands on R61); the fixture design/mfg/assembly/hotbar-fixture.svg; stereo microscope at 20 times; meter with needle tips 0.2 mm or finer (hotbar-joint.md sections 3, 4; process.md P6)")
        setf(r, "heat", "260 C, 4 s, 20 N, pressure held until the blade is below 150 C: starting values, confirmed on the first build; at most two presses per foot; first board: thermocouple at J1's nearest corner must stay below 217 C (hotbar-joint.md sections 4, 5)")
        setf(r, "orientation", "on the bench before the ribbons go into the body: board PARTS FACE UP in the fixture pocket, J1 down in the relief channel; foot on top with its lands (F.Cu) DOWN on the board lands, the neck leaving over the board edge (J_BAND_A upper edge, J_BAND_B lower edge, as engraved); FLEX1 first, then FLEX2 (lead-decisions.md row 'ribbon-to-board joint'; hotbar-joint.md sections 2.5 A, 3, 4)")
        setf(r, "alignment", "foot aligned to the board's own lands by eye at 20 times: long edges 0.335 mm outside the outer land columns, end 0.20 mm inside the inner row; after it lies flat each board land shows 0.125 mm at both ends of its tail land (hotbar-joint.md section 3)")
        setf(r, "check", "land %s, %s (hotbar-joint.md section 4)" % (land, chk))
        setf(r, "check_possible_at_this_step", "yes")
        wcl = "design/wiring/product-wiring.csv:%s" % r["source"].split("product-wiring.csv:")[1].split(" ")[0]
        src = " | ".join([
            "joint_id: %s" % wcl, "wiring_line: %s" % wcl, "end: %s" % wcl, "what_meets_what: %s" % wcl,
            "step: %s" % L(14, "head"),
            "solder_source: %s:%d; %s:23; %s:228; design/ecad/band/band-interface.md:137" % (A, [i for i, l in enumerate(new, 1) if l.startswith("- **The 15 ribbon lands:**")][0], HB, HB),
            "flux: %s; design/mfg/assembly/process.md P1.4" % L(14, "Join"),
            "tool: %s; %s:167" % (L(14, "Join"), HB),
            "heat: %s; %s:175; %s:191" % (L(14, "Join"), HB, HB),
            "orientation: %s; %s; design/wiring/lead-decisions.md:81" % (L(14, "Join"), L(14, "How")),
            "alignment: %s; %s:130; %s:131" % (L(14, "Locate"), HB, HB),
            "check: %s; %s:147" % (L(14, "Check"), HB),
            "check_possible_at_this_step: %s" % L(14, "Check"),
            "process: design/mfg/assembly/process.md P1.1, P1.4, P6"])
        setf(r, "source", src)
        setf(r, "gap", "waits for the board helper: ring-F_Paste.gbr holds no opening at this J_BAND land yet (hotbar-joint.md section 7, items 1 and 2: 15 openings, 302 flashes today, 317 after); until then the stencil of step 2 brings no solder to the joint")
    elif st == "6" and jid.startswith("J-"):
        # switch rows: check by the foot's land numbers
        n = SW_LAND.get(wl)
        if n:
            setf(r, "check", "every joint passes the accept rules of step 2; the switch closes its own line and no other while pressed and reads open when released: ohmmeter at the FLEX1 foot between tail land %d and land 8 (GND), lands numbered on the flex drawing flex1-usN-drawing.pdf (change C13), needle tips 0.2 mm or finer; height 0.53 mm; switch base flat on the head, feeler 0.02 mm" % n)
        else:
            setf(r, "check", "every joint passes the accept rules of step 2; each switch closes its own line and no other while pressed (ohmmeter at the FLEX1 foot, lands numbered on the flex drawing flex1-usN-drawing.pdf, change C13, against land 8 GND) and reads open when released; height 0.53 mm; base flat, feeler 0.02 mm")
        setf(r, "source", re.sub(r"check: [^|]*\|", "check: %s; design/mfg/assembly/hotbar-joint.md:149 |" % L(6, "Check"), r["source"]))
        setf(r, "source", re.sub(r"solder_source: [^|]*\|", "solder_source: %s; design/mfg/assembly/process.md:86; design/mfg/assembly/process.md:195 |" % L(6, "How"), r["source"]))
    elif st == "7" and jid.startswith("J-"):
        setf(r, "check", "both joints pass the accept rules of step 2; 3.0 V through a 200 mA current limit for 0.5 s, + on tail land 7 (VMOT) and - on tail land 6 (GND) of the FLEX1 foot, numbered on the flex drawing (change C13), needle tips 0.2 mm or finer: the motor vibrates; the meter reading between lands 7 and 6 is recorded for step 14")
        setf(r, "source", re.sub(r"tool: [^|]*\|", "tool: %s; design/mfg/assembly/process.md:150 |" % L(7, "How"), r["source"]))
        setf(r, "source", re.sub(r"solder_source: [^|]*\|", "solder_source: %s; design/mfg/assembly/process.md:65 |" % L(7, "How"), r["source"]))
        setf(r, "source", re.sub(r"flux: [^|]*\|", "flux: %s; design/mfg/assembly/process.md:70 |" % L(7, "How"), r["source"]))
        setf(r, "source", re.sub(r"heat: [^|]*\|", "heat: %s |" % L(7, "How"), r["source"]))
        setf(r, "source", re.sub(r"alignment: [^|]*\|", "alignment: %s; %s; design/ecad/band/band-interface.md:122 |" % (L(7, "How"), L(7, "Join")), r["source"]))
    elif st == "9" and jid.startswith("J-"):
        net = {"W025": "the red probe on tail land 1 (VBAT) and the black on land 2 (GND) read the cell voltage, positive; a negative reading: first check on the drawing that the probes sit on lands 1 and 2, only then is a tab on the wrong land",
               "W026": "land 1 (VBAT) to land 2 (GND) reads the cell voltage, positive (as W025)",
               "W027": "about 10 k between tail land 3 (NTC) and land 2 (GND) at room temperature",
               }.get(wl, "the pack's three tab joints: cell voltage positive from tail land 1 to land 2, about 10 k from land 3 to land 2")
        setf(r, "check", "the joints pass the accept rules of step 2; at the FLEX2 foot, lands numbered on the flex drawing (change C13), needle tips 0.2 mm or finer: %s; cell voltage measured before and after the joints" % net)
        setf(r, "source", re.sub(r"tool: [^|]*\|", "tool: %s; design/mfg/assembly/process.md:151 |" % L(9, "How"), r["source"]))
        setf(r, "source", re.sub(r"solder_source: [^|]*\|", "solder_source: %s; design/mfg/assembly/process.md:65 |" % L(9, "How"), r["source"]))
        setf(r, "source", re.sub(r"flux: [^|]*\|", "flux: %s; design/mfg/assembly/process.md:70 |" % L(9, "How"), r["source"]))
        setf(r, "source", re.sub(r"heat: [^|]*\|", "heat: %s |" % L(9, "How"), r["source"]))
    elif st == "8" and jid.startswith("J-"):
        land = {"W029": 4, "W030": 5, "W031": 6, "W032": 7}[wl]
        setf(r, "check", "the joint passes the accept rules of step 2; disc flat on its land and centred, no tilt; disc top 0.070 to 0.112 mm above the land copper (feeler or microscope focus, 0.02 mm steps); continuity from the disc to tail land %d of the FLEX2 foot, numbered on the flex drawing (change C13); no short between neighbouring discs or their lands; flush with the liner is checked at step 21" % land)
        setf(r, "source", re.sub(r"check: [^|]*\|", "check: %s; design/mfg/assembly/process.md:163 |" % L(8, "Check"), r["source"]))
    elif st == "15" and jid.startswith("J-W0") and 40 <= int(wl[1:]) <= 53:
        setf(r, "step", "16")
        setf(r, "tool", "no tool on J1: fingertip on the middle of the lever, never tweezers or another sharp tool; the cable held by its stiffened end and pushed in flat to the very end; 10 times magnifier (process.md P6, change C18)")
        setf(r, "check", "latch closed over the whole cable width (magnifier); contact 1 on the +Y side, checked on the maker's drawing page 5 before the lever is closed; cable flat in J1 and not skewed; continuity of every contact proven in the same step before step 17 closes J1: ring on its cell, USB from the jig through CP1 to CP4, FACTORY ENTER, screen folded down, T-SCREEN and T-SIGN pass; on a fault the cable is re-seated (process.md P8 change C12)")
        setf(r, "check_possible_at_this_step", "yes")
        s = r["source"]
        s = re.sub(r"step: [^|]*\|", "step: %s |" % L(16, "head"), s)
        s = re.sub(r"tool: [^|]*\|", "tool: %s; design/mfg/assembly/process.md:175 |" % L(16, "Tool"), s)
        s = re.sub(r"check: [^|]*\|", "check: %s |" % L(16, "Check"), s)
        s = re.sub(r"check_possible_at_this_step: [^|]*\|", "check_possible_at_this_step: %s |" % L(16, "Check"), s)
        setf(r, "source", s)
    elif st == "2" and (jid.startswith("J-W03") or jid in ("P-ring-F", "P-ring-B")):
        setf(r, "alignment", "by hand: the stencil laid on the board and moved until every opening sits over its land, seen under the 10 times magnifier (the board itself has no fiducial); a placing machine uses the three 1 mm fiducials on the panel rails of the face (change C4); in pass 2 the board on its outline in the carrier with a pocket under J1 (process.md P7, P6)")
        if "expected look: MISSING" in r["check"]:
            setf(r, "check", r["check"].replace("expected look: MISSING", "each joint passes the eight accept rules of step 2 (paste melted and flowed; solder wets land and part end in a hollow curve; no unwetted ball, no bare ring; no bridge; no loose ball; part flat and square, not on one end; each end on its own land; no crack or hole); for ANT1 each end wetted with a hollow curve onto its land (lead-decisions.md row 'soldering process')"))
        s = r["source"]
        s = re.sub(r"alignment: [^|]*\|", "alignment: %s; design/mfg/assembly/process.md:185; design/mfg/assembly/process.md:189 |" % L(2, "Locate"), s)
        s = re.sub(r"check: [^|]*\|", "check: %s; design/wiring/lead-decisions.md:82 |" % L(2, "Check"), s)
        s = re.sub(r"heat: [^|]*\|", "heat: %s; %s; design/mfg/assembly/process.md:104 |" % (LP("- **Reflow profile (both passes):**"), LP("- **Never a third reflow:**")), s)
        setf(r, "source", s)
        if jid == "P-ring-B":
            setf(r, "gap", "waits for the board helper: solder: the J1 openings of ring-B_Paste.gbr are 1:1 and the 12 test pads have openings; Hirose's reduced J1 openings and no test pad opening are change C3 (process.md P8)")
        else:
            setf(r, "gap", "")
        if jid == "P-ring-F":
            setf(r, "what_meets_what", "ring main board, parts face (KiCad F.Cu): every part of ring-pos-front.csv; the 15 J_BAND lands get their paste in this pass too, and their solder is tracked in the hot-bar rows (step 14)")

# ---- case procedure of commit 9e09f881 (changes C5, C6, C15, C16; lead's message): case step k is now k + 1,
# and the new case step 1 builds the case main board. board-notes.md lines are mapped from the case helper's
# before copy (board-notes-before-case-proc.md) to the delivered file (board-notes-9e09f881.md).
BN = "design/ecad/case/pcb/board-notes.md"
bn_old = open(os.path.join(HERE, "board-notes-before-case-proc.md"), encoding="utf-8").read().split("\n")
bn_new = open(os.path.join(HERE, "board-notes-current.md"), encoding="utf-8").read().split("\n")  # 9e09f881 plus the power-up test (g)
assert open(os.path.join(ROOT_DIR, BN), encoding="utf-8").read().split("\n") == bn_new, "board-notes.md changed since the copy"
PROC = [i for i, l in enumerate(bn_new, 1) if l.startswith("**Case procedure")][0]


def bn_line(n):
    l = bn_old[n - 1]
    ex = [i for i, x in enumerate(bn_new, 1) if x == l]
    if len(ex) == 1:
        return ex[0]
    m = re.match(r"(\d+)\. ", l)
    if m and n > PROC - 5:
        k = int(m.group(1)) + 1
        hit = [i for i, x in enumerate(bn_new, 1) if i > PROC and x.startswith("%d. " % k)]
        return hit[0]
    pf = [i for i, x in enumerate(bn_new, 1) if l.strip() and x[:40] == l[:40]]
    if len(pf) == 1:
        return pf[0]
    raise SystemExit("no new board-notes line for %d" % n)


def CS(k):
    return "%s:%d" % (BN, [i for i, x in enumerate(bn_new, 1) if i > PROC and x.startswith("%d. " % k)][0])


def bump(text):
    # one pass only: it also covers "[needs case N]"
    text = re.sub(r"\bcase (step )?(\d+)\b", lambda m: "case %s%d" % (m.group(1) or "", int(m.group(2)) + 1), text)
    return text


PINS = {"J-W054-B": "P1:1", "J-W055-B": "P2:1", "J-W056-B": "P3:1", "J-W057-B": "P4:1", "P-case_pins": "P1:1 P2:1 P3:1 P4:1"}
PASTE_PINS = "design/ecad/case/pcb/fab/case_pins/gerber/case_pins-F_Paste.gbr"
for r in rows:
    jid = r["joint_id"]
    if BN + ":" in r["source"]:
        setf(r, "source", re.sub(re.escape(BN) + r":(\d+)", lambda m: "%s:%d" % (BN, bn_line(int(m.group(1)))), r["source"]))
    if r["step"].startswith("case "):
        for k in ("step", "check_possible_at_this_step", "check", "solder_source", "what_meets_what", "alignment", "orientation", "tool", "heat", "gap"):
            setf(r, k, bump(r[k]))
    if jid in PINS:
        setf(r, "solder_source", "Kester NP505-HR SAC305 Type 4 (20 to 38 um), 88.5 % metal, no-clean, part 7040211410, printed through a 0.10 mm stainless stencil cut from the pin board paste file, one ring opening (1.70 mm outside, 1.10 mm inside) over each pin pad (pin in paste, case step 4 (a), change C6): paste layer " + PASTE_PINS + " for " + PINS[jid])
        setf(r, "source", re.sub(r"solder_source: [^|]*\|", "solder_source: %s; %s |" % (CS(4), "design/mfg/assembly/process.md P4"), r["source"]))
        setf(r, "source", re.sub(r"step: [^|]*\|", "step: %s |" % CS(4), r["source"]))
        setf(r, "gap", "")
    if jid == "P-case_main":
        setf(r, "step", "case 1")
        setf(r, "alignment", "by hand: the stencil aligned by its openings on the lands under the 10 times magnifier (case step 1 (b); process.md P7); the parts where case_main_position.csv puts them (case step 1 (c))")
        setf(r, "check", "every joint at 10 times: each part in place and flat, no bridge between neighbouring pads, hardest look at the 0.5 mm pitch of U2; the four J1 shell slots soldered and inspected the same way (case step 1 (e), (f))")
        s = r["source"]
        for key in ("step", "tool", "heat", "check", "check_possible_at_this_step"):
            s = re.sub(r"%s: [^|]*\|" % key, "%s: %s |" % (key, CS(1)), s)
        s = re.sub(r"alignment: [^|]*\|", "alignment: %s; design/mfg/assembly/process.md:189 |" % CS(1), s)
        setf(r, "source", s)
        setf(r, "gap", "check (open, for the lead, as case step 1 (e) says): the full written accept rule of a reflowed joint is not cited by the case step (the eight rules of assembly.md step 2 now exist), and no file gives a check of the joints under the module U1 and the thermal pad of U2")

# ---- ribbons of commit a3492b1f (changes C1, C2, C13; the lead's message): paste layers and land numbers landed.
SIZES = ["us7", "us8", "us9", "us10", "us11", "us12", "us13"]
PADS_DIR = os.path.join(ROOT_DIR, "design/mfg/assembly/joint-table-work/pads")


def flex_paste(flex, lands):
    face = "F" if flex == "flex1" else "B"
    return "; ".join("paste layer design/ecad/band/fab/%s-%s/%s-%s-%s_Paste.gbr for %s" % (flex, s, flex, s, face, lands) for s in SIZES)


def pass_lands(board, refpre, face):
    ps = list(csv.DictReader(open(os.path.join(PADS_DIR, board + "-pads.csv"), newline="")))
    got = sorted("%s:%s" % (p["ref"], p["pad"]) for p in ps if p["ref"].startswith(refpre) and p["attr"] == "SMD" and face in p["layers"].split())
    return " ".join(got)


PASTE1 = "Kester NP505-HR SAC305 Type 4 (20 to 38 um), 88.5 % metal, no-clean, part 7040211410, printed through a 0.08 mm stainless stencil cut from the FLEX1 paste layer, one 0.55 x 0.55 opening per switch land (change C1, 12 openings per size)"
PASTE2 = "Kester NP505-HR SAC305 Type 4 (20 to 38 um), 88.5 % metal, no-clean, part 7040211410, printed through a 0.08 mm stainless stencil cut from the FLEX2 paste layer, four 0.58 mm round openings per disc land off the centre via (change C2)"
for r in rows:
    jid, st = r["joint_id"], r["step"]
    if st == "6" and jid.startswith("J-"):
        m = re.match(r"FLEX1 (SW\d) pin (\d)", r["what_meets_what"])
        setf(r, "solder_source", PASTE1 + ": " + flex_paste("flex1", "%s:%s" % (m.group(1), m.group(2))))
        setf(r, "gap", "")
    elif st == "8" and jid.startswith("J-"):
        m = re.match(r"FLEX2 (CP\d) pin (\d)", r["what_meets_what"])
        setf(r, "solder_source", PASTE2 + ": " + flex_paste("flex2", "%s:%s" % (m.group(1), m.group(2))))
        setf(r, "gap", "")
    elif st in ("7", "9") and jid.startswith("J-"):
        setf(r, "gap", "")
    elif jid.startswith("P-flex1-"):
        b = jid[2:]
        setf(r, "solder_source", PASTE1 + ": paste layer design/ecad/band/fab/%s/%s-F_Paste.gbr for %s" % (b, b, pass_lands(b, "SW", "F.Cu")))
        setf(r, "gap", "")
    elif jid.startswith("P-flex2-"):
        b = jid[2:]
        setf(r, "solder_source", PASTE2 + ": paste layer design/ecad/band/fab/%s/%s-B_Paste.gbr for %s" % (b, b, pass_lands(b, "CP", "B.Cu")))
        setf(r, "gap", "")
    if st in ("6", "7", "8", "9") and jid.startswith("J-"):
        setf(r, "check", r["check"].replace("numbered on the flex drawing flex1-usN-drawing.pdf (change C13)", "numbered on the flex drawing flex1-usN-drawing.pdf, detail 'BOARD END OF THE RIBBON: LAND NUMBERS AND NETS' (change C13)").replace("numbered on the flex drawing (change C13)", "numbered on the flex drawing, detail 'BOARD END OF THE RIBBON: LAND NUMBERS AND NETS' (change C13)"))
    if jid == "P-case_main":
        G = [i for i, x in enumerate(bn_new, 1) if "(g) First power-up test of the case main board" in x][0]
        H = {k: [i for i, x in enumerate(bn_new, 1) if x.lstrip().startswith("- Hidden joint group %s," % k)][0] for k in ("H1", "H2", "H3", "H4")}
        NOTP = [i for i, x in enumerate(bn_new, 1) if x.lstrip().startswith("- What this test does NOT prove")][0]
        setf(r, "check", r["check"] + "; then the first power-up test of case step 1 (g), before any wire is soldered: bench supply 5.0 V, 1.5 A limit, on J1 only; VBUS_IN above 3.6 V, SYS 3.50 to 3.65 V at no load (up to 4.42 V with the module running), REGN 4.7 V or more, 3V3 3.274 to 3.341 V, VRING under 0.1 V, TXD0 (TP3) prints the ROM boot messages. Hidden joints: the module U1 supply and ground pads are \"shown by TP3 only, with the 3V3 reading in range\", but \"One missing ground joint among the many does not change any reading: NOT proven\"; of the module's signal pads \"only pin 39 (TXD0) is shown\", \"The module pins IO0 to IO48 other than TXD0: NOT proven\"; the charger U2's edge pads VBUS, SW, SYS, PGND and REGN are proven by SYS and REGN, BAT is not; the charger's centre pad: \"this test does NOT prove it\" (an X-ray or a section would be needed, for the lead)")
        s = r["source"]
        s = re.sub(r"check: [^|]*\|", "check: %s:%d; %s:%d; %s:%d; %s:%d; %s:%d; %s:%d |" % (BN, G, BN, H["H1"], BN, H["H2"], BN, H["H3"], BN, H["H4"], BN, NOTP), s)
        s = re.sub(r"check_possible_at_this_step: [^|]*\|", "check_possible_at_this_step: %s:%d |" % (BN, G), s)
        setf(r, "source", s)
        setf(r, "check_possible_at_this_step", "yes")
        setf(r, "gap", "")

# ---- ring board of commit 796a0086 (the lead's message; design/ecad/ring/pcb/board-notes-r4.md E1, E7, E8):
# ring-F_Paste.gbr holds 15 regions 0.300 x 0.440 on the ribbon lands; ring-B_Paste.gbr holds J1 to Hirose's
# pattern and no test pad opening (logs/ring-paste-counts.log: 15 of 15 lands, 0 of 12 test pads).
RF = "design/ecad/ring/pcb/fab/gerber/ring-F_Paste.gbr"
TPS = "TP1,TP3,TP4,TP5,TP6,TP12,TP14,TP15,TP17,TP18,TP19,TP21"
for r in rows:
    jid = r["joint_id"]
    if jid.startswith("J-") and jid.endswith("-A") and r["step"] == "14":
        m = re.match(r"ring main board (J_BAND_[AB]) land (\d+)", r["what_meets_what"])
        setf(r, "solder_source", "alloy SAC305 (process.md P1.1); form: a solder layer of about 0.03 mm on the board land, Kester NP505-HR paste printed through the 0.075 mm parts face stencil in pass 2 of step 2 and reflowed, one 0.300 x 0.440 mm opening per land (hotbar-joint.md section 1; board-notes-r4.md E7): paste layer %s for %s:%s" % (RF, m.group(1), m.group(2)))
        setf(r, "source", re.sub(r"solder_source: [^|]*\|", "solder_source: %s; design/mfg/assembly/hotbar-joint.md:23; design/ecad/ring/pcb/board-notes-r4.md (E7) |" % LP("- **The 15 ribbon lands:**"), r["source"]))
        setf(r, "gap", "")
    if jid == "P-ring-F":
        setf(r, "solder_source", "paste layer %s for parts of design/ecad/ring/pcb/fab/ring-pos-front.csv except none" % RF)
        setf(r, "what_meets_what", "ring main board, parts face (KiCad F.Cu): every part of ring-pos-front.csv, the 15 J_BAND ribbon lands included (their paste is the solder of the hot-bar joint of step 14)")
    if jid == "P-ring-B":
        setf(r, "solder_source", "paste layer design/ecad/ring/pcb/fab/gerber/ring-B_Paste.gbr for parts of design/ecad/ring/pcb/fab/ring-pos-back.csv except %s; J1 to Hirose's stencil pattern (8 openings 0.65 x 0.23, 7 of 0.55 x 0.23, 2 tabs 0.70 x 0.30); the 12 test pads get no paste (0 of 12 with an opening, checked by the guide helper, not by R4) (board-notes-r4.md E1, E8; process.md P2 change C3)" % TPS)
        setf(r, "gap", "")

with open(DST, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print("rows", len(rows), "fields changed", changed)
