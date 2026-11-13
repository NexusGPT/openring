"""r4 edits of design/case/case-bom.csv: lines the routed boards made wrong (board-notes.md Round 2 list items 5 and 6, and TH1's package), and the three
new mechanical items of the main board's holding. Exact line replacements (each must match once); writes the file and prints each changed line."""
import csv
import io
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "case-bom.csv")
lines = open(P, encoding="utf-8").read().split("\n")
rep = {
    '16,LED1,1,one light (RGB),Kingbright,APTF1616SEEZGQBDC,SMD 1616,1.6 x 1.6 x 0.7,,"common anode pin 1 on 3V3, cathodes red 2 green 3 blue 4, driven active low; VF at 20 mA: red 2.0, green 3.3, blue 3.3 typ",DS,design/datasheets/case_kb_aptf1616.pdf p.1-2,,price not read; bench B4 green and blue brightness at 3.3 V drive':
    '16,LED1,1,one light (RGB),Kingbright,APTF1616SEEZGQBDC,SMD 1616,1.6 x 1.6 x 0.7,,"common anode pin 1 on SYS (design/ecad/case/sch-notes.md section 9), cathodes red 2 green 3 blue 4, driven active low; VF at 20 mA: red 2.0, green 3.3, blue 3.3 typ",DS,design/datasheets/case_kb_aptf1616.pdf p.1-2; design/ecad/case/sch-notes.md section 9,,price not read; bench B4 brightness over SYS 3.5 to 4.35 V',
    '17,R8-R10,3,LED series resistors,,,0402,1.0 x 0.5,"470 Ohm (red), 150 Ohm (green), 150 Ohm (blue), GPIO to cathode",,LIST,design/case/case-architecture.md section 6,,choose maker part after bench B4':
    '17,R8-R10,3,LED series resistors (anode on SYS),Yageo,RC0402FR-07510RL (R8); RC0402FR-07270RL (R9 and R10),0402,1.0 x 0.5,"510 Ohm (red), 270 Ohm (green), 270 Ohm (blue), GPIO to cathode","2.2 to 4.7 mA over SYS 3.5 to 4.35 V",CALC,design/ecad/case/sch-notes.md section 9; design/ecad/case/pcb/board-notes.md Round 2 list item 6,,bench B4',
    '22,R14-R22,9,"pull-ups and pull-downs: R14 SDA, R15 SCL, R16 INT, R17 FAULT, R18 SD_CMD, R19 SD_D0, R20 SD_D1, R21 CHG_CE_N to GND, R22 BOOT",,,0402,1.0 x 0.5,10 kOhm,,LIST,design/case/case-architecture.md section 6,,choose maker part':
    '22,R14-R22,9,"pull-ups and pull-downs: R14 SDA, R15 SCL, R16 INT, R17 FAULT, R18 SD_CMD, R19 SD_D0, R20 SD_D1, R21 CHG_CE_N to 3V3 (charging off until the software has set the charger, sch-notes.md section 9), R22 BOOT",,,0402,1.0 x 0.5,10 kOhm,,LIST,design/case/case-architecture.md section 6; design/ecad/case/sch-notes.md section 9,,choose maker part',
    '24,E1,1,ring-presence touch electrode,,,copper on pin board,6 x 3,,read by IO4 TOUCH4,CALC,design/case/case-architecture.md section 5,,bench B3: touch delta with ring present':
    '24,E1,1,ring-presence touch electrode,,,copper on pin board,"front strip 3.9 x 1.15 plus a back pour 4.1 x 4.6 of the same net (18.9 mm2), two vias",,read by IO4 TOUCH4,CALC,design/ecad/case/pcb/board-notes.md (conflict 7; Round 2 list item 5); design/ecad/case/pcb/case_pins.kicad_pcb,,bench B3: touch delta with ring present',
    '25,PCB1,1,main board,,,FR4 4 layers,23.0 x 35.4 x 1.0,,"lies flat above the cell (C4); U1 module, J1 and the small parts on its top face",CALC,design/case/case.py,,board fab quote; layout not started':
    '25,PCB1,1,main board,,,FR4 4 layers,23.0 x 37.9 x 1.0 (plus a 1.85 x 10.2 tab under J1),,"routed, 0 violations and 0 unconnected (board-notes.md Round 2); lies flat above the cell; all parts on its top face, 16 bare test pads on its back; held by the board retainer (MECH18) on the stack foam pad (MECH19), cell, insulating sheet (MECH20)",CALC,design/ecad/case/pcb/case_main.kicad_pcb; design/case/case-model-r4-notes.md,,board fab quote',
    '79,TH1,1,BQ25895 TS NTC,,,0402,1.0 x 0.5,10 kOhm NTC 103AT,datasheet example for 103AT,DS,design/datasheets/case_bq25895.pdf section 8 (RT1 RT2),,choose maker parts; NTC on the cell face':
    '79,TH1,1,BQ25895 TS NTC,Semitec,103AT-2,"leaded bead (footprint NTC_wired: two plated holes), glued on the cell\'s top face beside the main board\'s +X edge",bead 1.6 dia (start value; maker sheet not read),10 kOhm NTC 103AT,datasheet example for 103AT,DS,design/datasheets/case_bq25895.pdf section 8 (RT1 RT2); design/ecad/case/pcb/board-notes.md part e,,NTC on the cell face; leads about 7 and 5 mm (case-model-r4-notes.md)',
}
new_rows = [
    '98,MECH18,1,"board retainer (own part `board_retainer`, r4): a web under the cavity ceiling with four posts that press the main board onto the stack and a fence at the board\'s +X edge that takes the push of a USB-C plug to the cavity wall",,,"PA12 printed (as the shell), or PLA/PETG on a hobby printer",see case-model-r4-notes.md,,"web 0.8 thick; 4 posts dia 1.6; fence between the board edge and the cavity wall; laid into the upturned shell before the board",CALC,design/case/out/case_board_retainer.stl; design/case/out/parts/board_retainer.step,,"named measurement: board does not move when a USB-C plug is pushed in and pulled 10 times (case-model-r4-notes.md)"',
    '99,MECH19,1,foam pad under the cell (r4),,,"closed-cell PE or PU foam, 0.8 mm free thickness, one face self-adhesive",22 x 38 x 0.8 free (0.36 compressed in the model),,"pressed to about 0.4 mm by the bottom plate: the clamp force of the stack",CALC,design/case/case.py (FOAM_FREE),,"choose maker part; named measurement: stack clamp, see case-model-r4-notes.md"',
    '100,MECH20,1,insulating sheet between the cell and the main board\'s back face (r4),,,"polyimide or PET film, 0.25 mm",about 20 x 34 x 0.25,,"covers the 16 bare test pads on the board\'s back face; lies in the 0.3 mm gap",CALC,design/case/case.py (insulation_sheet),,choose maker part',
]
changed = []
for i, l in enumerate(lines):
    if l in rep:
        changed.append((i + 1, l, rep[l]))
        lines[i] = rep[l]
assert len(changed) == len(rep), (len(changed), len(rep))
body = [l for l in lines if l.strip()]
body += new_rows
for r in new_rows:
    assert len(next(csv.reader(io.StringIO(r)))) == 14, r
for r in body:
    assert len(next(csv.reader(io.StringIO(r)))) == 14, r[:60]
open(P, "w", encoding="utf-8").write("\n".join(body) + "\n")
for n, a, b in changed:
    print("line %d changed:\n  - %s\n  + %s" % (n, a, b))
for r in new_rows:
    print("added: %s" % r)
