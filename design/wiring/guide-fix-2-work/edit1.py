import sys
P = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mfg/assembly/assembly.md")
s = open(P, encoding="utf-8").read()
E = []
def rep(tag, old, new):
    global s
    n = s.count(old)
    print(tag, "matches", n)
    if n != 1:
        sys.exit(1)
    s = s.replace(old, new)

# F4 step 1
rep("F4-1", "the board files exist. Today they do not: no track is drawn (`design/architecture.md:512`, open item S14), and the board file lacks U10, C81, C82 (`design/architecture.md:575`). This step cannot start until S14 is closed.",
 "the board files exist. The ring board is routed: the rules check prints `Found 0 violations` and `Found 0 unconnected items` (`design/ecad/ring/pcb/board-notes-r3.md:20`), and U10, C81 and C82 are placed on it (`design/ecad/ring/pcb/fab/ring-pos-front.csv:34`, `design/ecad/ring/pcb/fab/ring-pos-front.csv:35`, `design/ecad/ring/pcb/fab/ring-pos-front.csv:72`).")
# step 2 locate
rep("F4-2", "each part's land pattern (from S14);", "each part's land pattern (from the routed board file, `design/ecad/ring/pcb/board-notes-r3.md:20`);")
# N6 step 5
rep("N6", "POWER: the jig feeds a battery voltage on the J_BAND_B cell lands and a 10 k resistor on its thermistor land [PROPOSED: reason, the cell is not yet on the board and the power chip needs a battery and a thermistor reading], and VBUS, D-, D+, GND on the J_BAND_B pad lands, which are the USB lines of the four charging pads (`design/bom.csv:77`).",
 "POWER: the jig feeds a battery voltage on land 1 (VBAT) of J_BAND_B, with land 2 (GND) as its return, and a 10 k resistor between land 3 (NTC) and land 2 (GND) (`design/ecad/band/band-interface.md:111` to `design/ecad/band/band-interface.md:113`) [PROPOSED: reason, the cell is not yet on the board and the power chip needs a battery and a thermistor reading]. The jig also feeds VBUS, D-, D+ and GND on lands 4, 5, 6 and 7 of J_BAND_B, which are the USB lines of the four charging pads (`design/wiring/product-wiring.csv:30` to `design/wiring/product-wiring.csv:33`, `design/bom.csv:77`).")
# F4/F7 step 6
rep("F4-6", "Today no outline exists (`design/bom.csv:78`; `design/mfg/specs/band-flex-tails.md:62`). The switch land pattern is open (S9, `design/bom.csv:39`).",
 "The outline exists: FLEX1 is drawn as a board for each size, `design/ecad/band/flex1-us7.kicad_pcb` to `design/ecad/band/flex1-us13.kicad_pcb` (`design/ecad/band/band-interface.md:100`). The switch land pattern is decided: Alps_SKTAAAE010, four lands for SW2 and two lands for each outer switch (`design/ecad/band/band-interface.md:102`, `design/ecad/band/band-interface.md:103`).")
rep("F7", "- **Check:** each switch closes its own line and no other, measured with an ohmmeter on the ribbon's board end while pressing it; height 0.53 mm;",
 "- **Check:** each switch closes its own line and no other, measured with an ohmmeter on the ribbon's board end while pressing it; each switch also reads open (no connection) on its own line when it is released, so a switch that is closed all the time fails; height 0.53 mm;")
# F2 step 7
rep("F2-join", "red lead to the + pad, blue to the - pad, by hand soldering (`design/architecture.md:597`, `design/architecture.md:605`).",
 "the red lead to the + land and the blue lead to the - land, by hand soldering (iron 320 C, 2 s) (`design/architecture.md:597`, `design/architecture.md:605`). FLEX1 has no mark on it. The + land is the land nearer the slot: land 1 of the motor lands, net VMOT, joined to land 7 (MOT+) of J_BAND_A. The - land is the other one: land 2, net GND, joined to land 6 (MOT-) of J_BAND_A (`design/ecad/band/band-interface.md:123`). The red lead is the + lead (`design/wiring/product-wiring.csv:24`).")
rep("F2-locate", "table above); the lead length as delivered is open (S10).",
 "table above).")
rep("F2-before", "The lead length is known (S10) so the lead can be cut to fit the pocket [PROPOSED: cut to the length the v6 model gives for the size; reason, a loose loop has no room in the channel, `design/mech/thin/thin-notes.md:69`].",
 "Cut each lead to the length of its ring size, measured from the motor body edge to the lead end: US 7 1.12 mm, US 8 1.07, US 9 1.08, US 10 1.14, US 11 1.39, US 12 1.44, US 13 1.39 (`design/wiring/product-wiring.csv:24`, `design/wiring/product-wiring.csv:25`, `design/ecad/band/band-interface.md:125`). Strip 0.6 mm, tin the end, and lay it along the 0.80 mm side of its land (`design/ecad/band/band-interface.md:125`).")
rep("F2-check", "apply 3.0 V through a 200 mA current limit to the ribbon's motor lines for 0.5 s: the motor vibrates",
 "apply 3.0 V through a 200 mA current limit to the ribbon's board end, + on land 7 (VMOT) and - on land 6 (GND) of J_BAND_A (`design/ecad/band/band-interface.md:123`), for 0.5 s: the motor vibrates")
# F1 F4 step 8
rep("F1-join", "to the four pad lands of FLEX2 (`band_flex_away`). How the pad is made is open (`design/bom.csv:61`: \"pad part or plating\"). [PROPOSED default: the land itself is the pad, with thick hard gold; reason, a soldered disc adds a joint that sweat reaches through the liner edge.] The disc of the model is 1.6 mm, 0.07 thick, flush with the liner's inner face (`design/mech/thin/placement.csv:43`).",
 "to the four pad lands of FLEX2 (`band_flex_away`). The pad is a gold-plated disc, 1.6 mm across and 0.07 mm thick, soldered flat on its land with SAC305 paste at this step. The bare land is NOT the pad: its ENIG gold would wear through under the case's spring pins (`design/ecad/band/band-interface.md:141`; `design/wiring/product-wiring.csv:30` to `design/wiring/product-wiring.csv:33`). Four discs, one per land, in the order VBUS (CP1), D- (CP2), D+ (CP3), GND (CP4). Each disc has a via at the centre of its land (`design/ecad/band/band-interface.md:141`). The disc is flush with the liner's inner face, as the model has it (`design/mech/thin/placement.csv:43`). The part is not in the parts list today (see the notes of this round).")
rep("F4-8", "- **Before:** FLEX2 is made (no outline exists today, `design/bom.csv:79`).\n- **Check:** continuity from each pad to its land at the ribbon's board end; no short between pads.",
 "- **Before:** FLEX2 is made. The outline exists: FLEX2 is drawn as a board for each size, `design/ecad/band/flex2-us7.kicad_pcb` to `design/ecad/band/flex2-us13.kicad_pcb` (`design/ecad/band/band-interface.md:141`). The four discs are on hand.\n- **Check:** each disc lies flat on its land and is centred on it, with no tilt and no solder ball under it (a lifted disc fails); each disc is flush with the liner's inner face as the model says (`design/mech/thin/placement.csv:43`); continuity from each disc to its land at the ribbon's board end (VBUS to land 4, D- to land 5, D+ to land 6, GND to land 7 of J_BAND_B, `design/wiring/product-wiring.csv:30` to `design/wiring/product-wiring.csv:33`); no short between neighbouring discs or between their lands.")
# F3 step 9
rep("F3-join", "the output tabs of PRT1 (`cell_protection`, delivered on the cell's tab by the cell maker, `design/bom.csv:48`) to the cell lands of FLEX2, and RT1 to its land, by hand soldering at low heat",
 "the three output tabs of the bought cell pack (BT1 with PRT1 and RT1 inside it as one part, `design/bom.csv:48`; `design/wiring/product-wiring.csv:34` to `design/wiring/product-wiring.csv:36`) to the three lands of FLEX2, by hand soldering at low heat (iron 280 C at most, 2 s per joint). RT1 is not a separate part and has no joint of its own. Tab P+ goes on land 1 (VBAT), tab NTC on land 3 (NTC), tab P- on land 2 (GND). The tabs lie in the order P+, NTC, P- from the slot toward the cell, which is lands 1, 3, 2 (`design/ecad/band/band-interface.md:111` to `design/ecad/band/band-interface.md:115`)")
rep("F3-check", "- **Check:** the cell voltage appears on the two cell lands at the ribbon's board end; RT1 reads about 10 k at room temperature (`design/bom.csv:74`).",
 "- **Check:** the cell voltage appears on the cell lands at the ribbon's board end, positive on land 1 (VBAT) and negative on land 2 (GND): the meter's red probe on land 1 reads a positive voltage, and a negative reading means a tab is on the wrong land; the thermistor inside the pack reads about 10 k between land 3 (NTC) and land 2 (GND) at room temperature (`design/bom.csv:74`; `design/ecad/band/band-interface.md:113`, `design/ecad/band/band-interface.md:114`).")
# step 12/17 join mention
rep("F3-step17", "and FLEX2 with BT1, PRT1, RT1 and CP1 to CP4, into the channel.", "and FLEX2 with the cell pack BT1 (PRT1 and RT1 inside it) and CP1 to CP4, into the channel.")
open(P, "w", encoding="utf-8").write(s)
