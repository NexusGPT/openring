"""Pin lines of case-architecture.md, case-notes.md, case-bom.csv after the maker's working range (lead 07:19 and 09:1x rulings): each replacement must
match once; prints file, line, old and new."""
import os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = "design/case/pin-travel.md; design/datasheets/w15_harwin_drawing_P70-600 (sheet 2), w15_harwin_component_spec_C056, w15_harwin_graph_CPPOGO.txt row P70-6000045R"
GAUGE = ("Builder's step (depth gauge, 0.01 mm digital, ring out, holder staked): measure how far each free plunger tip stands in front of the pin holder's "
         "front face along the pin: P2 and P3 1.170 mm, P1 and P4 1.021 mm (r4/pin_gauge.log). Accept within +-0.04 mm (P2, P3) and +-0.03 mm (P1, P4). "
         "A tip standing out too little means the island sits too far back (pins too high): put stainless shim behind that island (between island and lug) "
         "in steps of 0.025 mm up to the shortfall (shim stock 0.025, 0.05 and 0.10 mm). A tip standing out too much: lap the lug's face for that island "
         "on 600-grit paper on a flat plate by the excess, then measure again.")
E = {
    "case-architecture.md": [
        ("the fitted pin is the Harwin P70-6000045R (proposed, stroke not confirmed, K1; the Mill-Max 0981 does not fit the pin holder's 1.60 mm bores); the pitch is now a parameter and the contact window of 2.15 to 2.65 mm is my assumption (stroke not in the file read) |",
         "the fitted pin is the Harwin P70-6000045R (the Mill-Max 0981 does not fit the pin holder's 1.60 mm bores); the pitch is now a parameter; since C5d-r4 the working range is the maker's 1.90 to 2.20 mm (" + SRC + "), which closes the stroke question |"),
        ("4 spring pins P1-P4 (Harwin P70-6000045R, stroke not confirmed) on pin board",
         "4 spring pins P1-P4 (Harwin P70-6000045R, 1.90-2.20 mm) on pin board"),
        ("| Harwin P70-6000045R (the fitted pin; proposed, stroke NOT confirmed: conflict K1; the Mill-Max 0981 does not fit the pin holder and is history only, case-bom.csv reference PA1-PA4 quantity 0) | barrel 1.5 mm in the holder's four 1.60 mm bores, free height 2.80 mm, working height 2.10 mm; to confirm with Harwin: the stroke (at least 0.34 mm needed), the force curve over 2.10 to 2.65 mm and the life, none of which is in the files read; the contact window 2.15 to 2.65 mm is my assumption | LIST |",
         "| Harwin P70-6000045R (the fitted pin on all four positions; the Mill-Max 0981 does not fit the pin holder and is history only, case-bom.csv reference PA1-PA4 quantity 0) | maker's drawing: flange 1.50 x 0.40 mm at the board, body 1.06 mm to 1.85 mm, plunger 0.60 mm, free height 2.80 mm; working height 1.90 (most compressed) to 2.20 (least), normal 2.10, 0.39 +-0.09 N at 2.10, 1 A, 30 milliohm, 10,000 cycles; the force at our 1.98 to 2.15 mm is not confirmed by a measurement | DS (" + SRC + ") |"),
        ("Pin heights (from the pin base plane to the pad face) over the seven sizes and the four pins run from 2.277 to 2.421 mm, a spread of 0.144 mm (inner pins P2, P3 vary most, 0.144 mm from US 7 to US 13). PCB2 is a rigid-flex of three islands: the inner island (P2, P3) and two outer islands (P1, P4) recessed by 0.401 mm, because the pad row is an arc and the outer pads sit nearer the post; with the islands stepped, all four pins stand at 2.35 mm at US 10. With 0.2 mm of tolerance on top a pin needs 0.344 mm of stroke from first contact: pin compression 0.37 to 0.58 mm below the 2.80 mm free height. The model assumes the Harwin P70-6000045R works in a window of 2.15 to 2.65 mm (the low end: its barrel edge must clear the concave pad row, sag 0.29 mm at 0.75 mm off the pad centre on US 7, so 1.85 + 0.30; the high end: 0.15 mm below the free height); the stroke is NOT in the file read, so this is [LIST] proposed, not confirmed (K1, supplier item S4). All 28 pin heights are inside the window",
         "C5d-r4 (maker's range 1.90 to 2.20 mm, " + SRC + "): pin heights (from the pin base plane to the pad face) of the inner pins P2, P3 run 1.980 (US 13) to 2.118 mm (US 7), centred on 2.05 at US 10 (+-0.08 left to the maker's range); the outer pins P1, P4 run 2.139 to 2.150 mm, centred on 2.15, because their pads sit about 21 degrees round the bore and the band face under them is tilted: the pin body (1.06 mm, maker's drawing) clears the band from 2.10 mm (r4/outer_pin_scan_fine.log), so their tolerance is +-0.05 (2.10 to 2.20). Heights per pin and size: design/wiring/ring-case-contact.csv (written by case_check test 18). PCB2 is three islands: the inner island (P2, P3) and two outer islands (P1, P4) recessed by 0.676 mm. C5d had 2.277 to 2.421 mm in an assumed 2.15 to 2.65 window, above the maker's range, with the body modelled 1.50 x 1.85. " + GAUGE + " All 28 pin heights are inside the range"),
        ("Force: 0.39 N at the 2.10 mm working height [`design/parts/ui-pass3.md` line 190]; at 2.2 to 2.45 mm the pins are less compressed, the force there is not measured.",
         "Force: 0.39 +-0.09 N at the 2.10 mm normal working height (maker); at 1.98 to 2.15 mm it is not measured."),
        ("| S4 | Pin for 1.6 mm pad pitch (conflict K1) | Harwin | the stroke (at least 0.34 mm needed), force curve over 2.10 to 2.65 mm and life of the Harwin P70-6000045R (none is in the catalogue page read) |",
         "| S4 | Pin for 1.6 mm pad pitch (conflict K1) | Harwin | closed in C5d-r4 by the maker's documents (working range 1.90 to 2.20 mm, force, life: " + SRC + "); left: the force curve between 1.90 and 2.20 mm (only the 2.10 value is stated) |"),
    ],
    "case-notes.md": [
        ("| M4 | Contact window 1.90 to 2.65 mm (0.15 to 0.90 mm below the free height 2.80) | stroke of the Harwin pin is not in the file read; the window is my assumption (A3) |",
         "| M4 | Working range 1.90 to 2.20 mm, the maker's (C5d-r4); inner pins centred 2.05, outer pins 2.15 | " + SRC + " (A3 closed) |"),
        ("- A3. Pin working window 1.90 to 2.65 mm (travel up to 0.90 mm from the free height); the Harwin stroke is not in the file read.",
         "- A3. Closed in C5d-r4: the maker states the working range of P70-6000045R, 1.90 to 2.20 mm (" + SRC + "); the 1.90 to 2.65 window was an assumption above that range."),
        ("1. Pin conflict K1 (decided in C5e: the Harwin P70-6000045R is the fitted pin; its stroke is still to be confirmed with Harwin).",
         "1. Pin conflict K1 (decided in C5e: the Harwin P70-6000045R is the fitted pin; its working range 1.90 to 2.20 mm is the maker's since C5d-r4; its force between 1.90 and 2.20 mm is not confirmed by a measurement)."),
    ],
    "case-bom.csv": [
        ('15,P1-P4,4,"spring pins VBUS D- D+ GND to the ring pads (fitted pin: Harwin P70-6000045R, 1.50 mm barrel, fits the pin holder\'s four 1.60 mm bores)",Harwin,P70-6000045R,SMT with peg,barrel 1.50 x 1.85 (length is my reading),,2.80 free height; 0.39 N +-0.09 N at 2.10 mm working height; 1 A; plunger 0.60; stroke NOT confirmed (not in the files read),LIST,design/datasheets/p3_harwin_p70.txt; design/datasheets/p3_harwin_p70_chipdip.pdf; design/parts/ui-pass3.md line 190,,"[LIST] proposed, stroke not confirmed (conflict K1): confirm with Harwin the stroke, the force curve at 2.10 to 2.65 mm and the life; the pin must give at least 0.34 mm of stroke (out/case_params.json pin_travel needed_stroke 0.338, free height 2.80 to heights 2.280 to 2.418 mm)"',
         '15,P1-P4,4,"spring pins VBUS D- D+ GND to the ring pads (fitted pin: Harwin P70-6000045R, flange 1.50, body 1.06, in the pin holder\'s four 1.60 mm bores)",Harwin,P70-6000045R,SMT with peg,"flange 1.50 x 0.40, body 1.06 to 1.85, plunger 0.60, peg 1.00 x 0.65",,"2.80 free height; working 1.90 to 2.20 (normal 2.10); 0.39 N +-0.09 N at 2.10; 1 A; 30 milliohm; 10,000 cycles",DS,design/case/pin-travel.md; design/datasheets/w15_harwin_drawing_P70-600.pdf sheet 2; design/datasheets/w15_harwin_component_spec_C056.pdf; design/datasheets/w15_harwin_graph_CPPOGO.txt,,"heights in the model: P2 P3 1.980 to 2.118, P1 P4 2.139 to 2.150 (design/wiring/ring-case-contact.csv); builder sets them with the depth-gauge and shim step of case-architecture.md section 7; force between 1.90 and 2.20 not confirmed by a measurement"'),
    ],
}
for fn, reps in E.items():
    p = os.path.join(D, fn)
    s = open(p, encoding="utf-8").read()
    for a, b in reps:
        assert s.count(a) == 1, (fn, a[:70], s.count(a))
        ln = s[:s.index(a)].count("\n") + 1
        s = s.replace(a, b)
        print("%s:%d\n  - %s\n  + %s" % (fn, ln, a, b))
    open(p, "w", encoding="utf-8").write(s)
print("done")
