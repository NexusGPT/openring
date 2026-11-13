"""Write design/mfg/assembly/joint-gaps.md from joints.csv: one line per joint with a gap, sorted by what a
builder would get wrong first (the rank of its kind below), with the file that would have to say it and the
lead decision that settles it (quoted from lead-decisions.md, found by text, or 'none').
Run: design/.venv/bin/python -B make_gaps.py"""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LD = os.path.join(ROOT, "design/wiring/lead-decisions.md")
ld_lines = open(LD, encoding="utf-8", newline="").read().split("\n")


def ld(quote):
    for i, l in enumerate(ld_lines, start=1):
        if quote in l:
            row = l.split("|")[1].strip()
            return 'row "%s" (lead-decisions.md:%d): "%s"' % (row, i, quote)
    raise SystemExit("lead decision quote not found: " + quote)


NONE = "none (no row of lead-decisions.md names a solder alloy or form, a flux, a paste or stencil, a reflow profile, a hot bar, a fixture or a fiducial: logs/lead-decisions-search2.log)"
# kind: (rank, why first, files that must say it, decision)
KINDS = [
    ("hotbar", lambda j: j["step"] == "16", 1,
     "no solder on either side: the joint is not made at all, and the lands cannot face each other as the step holds them",
     "assembly.md steps 2, 4 and 16 (a tinning or paste step for J_BAND_A/B and a paste layer file with openings there, or a solder preform); band-interface.md section 7 (flux, face, a drawn fixture)",
     NONE),
    ("case_main", lambda j: j["joint_id"] == "P-case_main", 2,
     "no step builds the case main board, and the charger's thermal pad gets no paste",
     "design/ecad/case/pcb/board-notes.md case procedure (a reflow step with stencil, profile and inspection); the U2 footprint and case_main-F_Paste.gbr (paste on pad 25)",
     NONE),
    ("switch", lambda j: j["step"] == "6", 3,
     "no stencil can be cut for the switch paste, so the 0.08 mm paste cannot be put on as asked",
     "design/ecad/band/fab/flex1-usN/ (a paste layer for the switch lands) and assembly.md step 6 (flux, reflow profile, tail land numbers)",
     NONE),
    ("disc", lambda j: j["step"] == "8" and j["joint_id"].startswith("J-"), 4,
     "a disc heated without a set temperature or time, and a flush check that cannot be done before the liner exists",
     "assembly.md step 8 (plate temperature and time, flux type, disc height before the cast, which check moves to step 21)",
     NONE),
    ("ringpass", lambda j: j["step"] == "2", 5,
     "no reflow profile (J1 accepts at most 2 cycles), and the step locates by fiducials the board does not have",
     "assembly.md step 2 (profile, flux, fiducials or another locating feature) and ring.kicad_pcb (fiducials)",
     NONE),
    ("pin", lambda j: j["joint_id"] in ("J-W054-B", "J-W055-B", "J-W056-B", "J-W057-B", "P-case_pins"), 6,
     "how the four spring pins are soldered (iron or reflow, solder, heat) is in no file read here",
     "design/ecad/case/pcb/board-notes.md case procedure step 3, or design/case/case-architecture.md section 7 (pin holder)",
     NONE),
    ("tab", lambda j: j["step"] == "9", 7,
     "the solder for the cell tabs is an either-or that the step does not choose",
     "assembly.md step 9 (solder and flux), the flex drawings (tail land numbers)",
     NONE),
    ("motor", lambda j: j["step"] == "7", 8,
     "the solder for the motor leads is not named",
     "assembly.md step 7 (solder and flux), the flex drawings (tail land numbers)",
     NONE),
    ("j1", lambda j: j["step"] == "15", 9,
     "no tool for the 0.3 mm pitch lever and cable, and no continuity check before J1 is closed off",
     "assembly.md step 15 (tool; a continuity check before step 17)",
     NONE),
    ("casewire", lambda j: j["step"] in ("case 6", "case 7"), 10,
     "solder and iron heat for the 30 AWG wires are not named",
     "design/ecad/case/pcb/board-notes.md case procedure steps 1, 6, 7 (and 8 for the reading of W1)",
     ld("W1 (VRING) red, W2 (USB_D-) white") + " settles the colours only"),
    ("caselead", lambda j: j["joint_id"] in ("J-W059-B", "J-W060-B"), 11,
     "no solder, no heat limit and no check after the cell lead joints",
     "design/ecad/case/pcb/board-notes.md case procedure step 9",
     ld("it states no gauge, no insulation, no polarity by colour and no solder limit") + " records that the maker gives no limit; it settles nothing"),
    ("th1", lambda j: j["joint_id"] in ("J-W061-B", "J-W062-B"), 12,
     "the solder for the thermistor leads is not named",
     "design/ecad/case/pcb/board-notes.md case procedure step 9",
     ld("at most 7 seconds at 340 degrees C with a 50 W iron") + " settles heat and iron only"),
    ("flex2pass", lambda j: j["joint_id"].startswith("P-flex2"), 13,
     "the board-level disc pass has no temperature, time or flux",
     "assembly.md step 8",
     NONE),
]
rows = list(csv.DictReader(open(os.path.join(ROOT, "design/mfg/assembly/joints.csv"), newline="")))
out, unplaced = [], []
for r in rows:
    if not r["gap"].strip():
        continue
    for name, test, rank, why, files, dec in KINDS:
        if test(r):
            out.append((rank, r["joint_id"], r, why, files, dec))
            break
    else:
        unplaced.append(r["joint_id"])
out.sort(key=lambda t: (t[0], t[1]))
n_rows, n_gap = len(rows), len(out)
L = ["# Joint gaps of today (from joints.csv)", "",
     "Written by `design/mfg/assembly/joint-table-work/make_gaps.py` from `design/mfg/assembly/joints.csv`. One line per joint that has a gap: "
     "what is missing (the gap column), which design file would have to say it, and whether a row of "
     "`design/wiring/lead-decisions.md` settles it (quoted). Sorted by what a builder would get wrong first: the group "
     "number comes first, then the joint id. The order of the groups is my judgment (the joint table helper), not a design decision.", "",
     "Rows: %d; with a gap: %d; complete: %d. Rows with a gap that no group placed: %d." % (n_rows, n_gap, n_rows - n_gap, len(unplaced)), ""]
last = None
for rank, jid, r, why, files, dec in out:
    if rank != last:
        L.append("## Group %d: %s" % (rank, why))
        L.append("")
        L.append("File that must say it: %s. Lead decision: %s." % (files, dec))
        L.append("")
        last = rank
    L.append("- %s (%s; step %s): missing: %s." % (jid, r["what_meets_what"], r["step"], r["gap"]))
L.append("")
L.append("Complete rows (no gap): %s." % ", ".join(r["joint_id"] for r in rows if not r["gap"].strip()))
open(os.path.join(ROOT, "design/mfg/assembly/joint-gaps.md"), "w").write("\n".join(L) + "\n")
print("gap lines", n_gap, "complete", n_rows - n_gap, "unplaced", len(unplaced), unplaced)
