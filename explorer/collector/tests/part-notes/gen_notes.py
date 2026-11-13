import csv, json, re, sys
from pathlib import Path
EXPLORER = Path(__file__).resolve().parents[3]
D = str(EXPLORER.parent)
rows = list(csv.DictReader(open(D + "/design/bom.csv", newline="")))
A = "architecture 17.3"
# group: (first refs of lines) -> (what, why, checked_against)
G = []
def g(refs, what, why, ca): G.append((refs.split(), what, why, ca))
g("U1", "The main chip. It runs the ring's program, handles Bluetooth and USB, and receives the microphone signals.",
  "It is the brain of the ring: every other part is set up and read by this chip.", "architecture 17.4")
g("U2", "The power chip. It charges the cell and makes the steady supply voltages the other parts need.",
  "The cell's voltage is not what the chips need, so this chip charges it safely and shares the power out.", "architecture 3")
g("R71 R72", "A small resistor that tells the power chip which output voltage to give.",
  "The power chip reads this resistor at start-up, so the main chip gets the right voltage.", "architecture 3")
g("U3", "The storage chip. It holds the recorded audio inside the ring.",
  "The ring records on its own, so the audio waits here until it is copied off.", "architecture 17.4")
g("U4", "The screen supply chip. It turns the cell's voltage into the two voltages the screen needs.",
  "The screen needs a higher voltage and a negative voltage that the cell cannot give directly.", "architecture 3")
g("U5", "A microphone. It hears sound through a small hole in the underside of the block.",
  "Two microphones together give a stereo recording of the voices around the wearer.", "architecture 17.19")
g("DISP1", "The screen, a small display set under the cover glass on top of the block.",
  "It shows the wearer what the ring is doing, and the joystick moves around on it.", "architecture 9")
g("J1", "A tiny connector on the main board that the screen's flat cable plugs into.",
  "It joins the screen to the main board so the chip can send pictures to the screen.", "architecture 16.4")
g("ANT1", "The antenna. It sends and receives the Bluetooth radio signal.",
  "Without it the ring cannot talk to a phone.", "architecture 2")
g("L2 L3 L4 C3 C12 C13", "A small part of the antenna matching set. Together they tune the radio signal between chip and antenna.",
  "Tuning the match lets the radio signal pass cleanly instead of being reflected back. One position is left empty for later tuning.", "architecture 2")
g("X1 X2", "A crystal. It makes a very steady beat that the main chip uses as its clock.",
  "The chip needs a steady clock for the radio and for keeping time, and a crystal keeps it exact.", "architecture 2")
g("L1", "A small coil next to the main chip that helps it make its own supply voltage efficiently.",
  "It lets the chip run on less energy, which keeps the battery lasting longer.", "architecture 2")
g("FB1", "A filter bead on the chip's supply line. It blocks electrical noise.",
  "Noise on the supply would disturb the radio, so this bead keeps it clean.", "architecture 2")
g("R1 R2", "A resistor copied from the chip maker's reference design for the main chip.",
  "The chip maker tested the chip with this value, so the ring keeps it.", "architecture 2")
g("C1 C4 C6 C7 C11", "A capacitor on the main chip's supply. It acts as a tiny local energy store.",
  "It smooths the supply so the chip does not stall when it suddenly needs more current.", "architecture 2")
g("L10", "A coil that is part of the screen supply circuit.",
  "The screen supply chip uses it to build the higher voltage the screen needs.", "architecture 3")
g("C21 C22 C23 C24 C28", "A capacitor in the screen supply circuit. It smooths the supply voltages going to the screen.",
  "A steady voltage keeps the picture on the screen stable.", "architecture 3")
g("C31 C35", "A capacitor next to each microphone's power pin. It smooths that microphone's supply.",
  "A clean supply keeps electrical noise out of the recorded sound.", "architecture 14")
g("R31", "A resistor on each microphone's data line.",
  "It keeps the fast data signal from ringing, so the audio reaches the chip cleanly.", "architecture 14")
g("SW1", "One of four small switches under the joystick cap, one for each direction.",
  "Pressing the cap toward a switch moves the choice on the screen in that direction.", "architecture 17.15")
g("SW2", "The centre switch under the joystick cap.",
  "A long press on the joystick starts or stops a recording, a short press marks a highlight.", "architecture 17.15")
g("R57", "A resistor that holds the two data lines between the main chip and the power chip at a set level.",
  "These lines need it to talk to each other reliably.", "architecture 14")
g("R60 R63 R61 R62", "A resistor on the storage or motor circuit that holds a line at a set level.",
  "It keeps the line from floating, so the storage and the motor do not act on stray signals.", "architecture 14")
g("C60 C61 C71 C73 C74 C76 C85 C86 C88 L71", "A capacitor or coil around the power chip or the storage supply. It smooths or filters one supply line.",
  "These parts keep the supply steady while the cell charges and the storage writes.", "architecture 14")
g("M1", "The vibration motor in the band, on the joystick side.",
  "It buzzes to confirm start, stop and warnings when you cannot look at the screen.", "architecture 17.16")
g("U11", "The motor's own supply chip. It feeds the vibration motor straight from the cell.",
  "The motor's start current is higher than the power chip allows, so the motor gets its own supply.", "architecture 17.22")
g("R73", "A resistor from the charging line to ground. It empties the charging line when the ring leaves its case.",
  "Without it the charging pad on your finger would keep several volts for a while after the ring leaves the case.", "lead-decisions.md row sim finding 1")
g("C84", "The capacitor at the output of the motor's supply chip.",
  "It holds the motor's supply steady. It was made smaller so that a motor start no longer pulls the cell voltage too low.", "lead-decisions.md row sim finding 4")
g("RC1", "A corner of the block made of resin, not metal, around the antenna.",
  "Metal around the antenna would block the radio; the resin lets Bluetooth out.", "architecture 17.20")
g("LT1", "A tiny part at the far end of the antenna.",
  "On the test bench it can be swapped to tune the antenna to the right frequency.", "ring-board-plan.md e.2")
g("C89", "An empty place for one more antenna tuning part.",
  "Nothing is fitted at first; the bench measurement says whether a part is needed there.", "ring-board-plan.md e.4")
g("FRM1", "The round metal frame around the joystick.",
  "It holds the joystick cap in its opening in the band and closes the gap around it.", "architecture 17.31")
g("C25", "A capacitor at the screen's supply chip.",
  "It holds one of the screen's supply voltages steady while the picture changes.", "bom.csv row C25")
g("C83", "A capacitor beside the motor's supply chip. It is a small local energy store.",
  "It keeps the motor's supply steady at the moment the motor starts.", "architecture 17.22")
g("SEAL1", "A thin seal ring between the cover glass and the metal body.",
  "It keeps water and dust from getting in around the edge of the glass.", "architecture 17.23")
g("DAM1", "A small frame of cured glue around the joystick's switches.",
  "It keeps the liner's resin out of the switches when the band is closed.", "architecture 17.23")
g("SEAL2", "A small plug of sealant between the motor's pocket and the block, on ring sizes US 7 to 9.",
  "On small sizes the wall between motor and block opens; the plug closes it before the liner is cast.", "architecture 17.27")
g("U10", "A small chip that translates the signals between the main chip and the storage chip.",
  "The main chip talks at 1.8 volts and the storage chip at 3.0 volts; without it they cannot understand each other.", "architecture 17.13")
g("BT1", "Battery cell, curved to follow the inside of the band. It stores the energy that runs the ring.",
  "It is thin and long, so it fits the band instead of the block, which keeps the block flat.", A)
g("PRT1", "The protection circuit of the cell, on the cell's tab.",
  "It cuts the cell off if it is overcharged or shorted, so the ring stays safe.", A)
g("PCB1", "The main circuit board. The chips and small parts sit on it and are wired together.",
  "It holds everything electronic in one flat piece, inside the block under the screen.", "architecture 17.2")
g("TP1 TP16 TP17 TP20 TP21", "A bare copper pad on the board. It is a place to touch with a probe.",
  "Factory and bench tests use these pads to program the ring and check signals. There is nothing to buy.", "architecture 14")
g("HSG1", "The metal body, block and band in one piece.",
  "It holds and protects every part, and it forms the ring you wear.", "architecture 17.1")
g("GL1", "The cover glass over the screen.",
  "It protects the screen and lets you see it.", "architecture 17.1")
g("ADH1", "A clear adhesive layer between the glass and the screen.",
  "It glues the glass to the screen and leaves no air gap that would blur the picture.", "architecture 17.2")
g("FOAM1", "A thin foam pad between the screen and the board.",
  "It cushions the screen against the board and takes up small differences in thickness.", "architecture 17.2")
g("MEM1", "A thin membrane over a microphone hole in the underside of the block.",
  "It lets sound in and keeps water and dust out of the microphone.", "architecture 17.19")
g("GSK2", "A small foam ring between a microphone and the floor of the block.",
  "It makes sure the sound reaches the microphone and does not leak around it.", "architecture 17.19")
g("U9", "A protection chip on the charging lines.",
  "It guards the ring against static shocks from the charging pads, which people touch.", "architecture 14")
g("CP1", "A small gold charging pad on the inside of the band, opposite the block.",
  "The case's pins touch these pads to charge the ring and to move data.", "architecture 17.15")
g("RT1", "A temperature sensor, a resistor whose value changes with heat, placed for the cell.",
  "The power chip reads it so charging stops if the cell gets too hot or too cold.", A)
g("J_BAND_A J_BAND_B", "A row of solder pads on the main board where a flex tail is soldered on.",
  "The wiring of the band joins the main board here.", A)
g("FLEX1 FLEX2", "A thin flexible circuit that carries wires through the band from the main board.",
  "It reaches the parts in the band: the joystick on one side, the motor, cell and pads on the other.", A)
g("LNR1", "A thin resin liner that closes the band channel on the side toward the finger.",
  "It seals and covers the parts in the band so they do not touch the skin.", A)
g("CAP1", "The joystick cap, a moulded cap with its own flange over the switches.",
  "You tilt it with the thumb to move, and you hold it down to start and stop a recording; it keeps water out.", A)
G_ = G

def refs(cell): return [t.strip() for t in re.split(r"[,;]", cell) if t.strip()]
line_of = {}
for r in rows:
    for t in refs(r["reference"]): line_of[t] = r["reference"]
# map each BOM line to a group by any of the group's refs
notes = {}
NO_NOTE = []
used = set()
for r in rows:
    rl = refs(r["reference"])
    hit = [i for i, gg in enumerate(G) if any(x in rl for x in gg[0])]
    if not hit:
        NO_NOTE.append(r["reference"])  # a line of the parts list that has no note yet: said, never invented
        continue
    assert len(set(hit)) == 1, (r["reference"], hit)
    what, why, ca = G[hit[0]][1:]
    used.add(hit[0])
    for t in rl:
        notes["ring:" + t] = {"what": what, "why": why, "checked_against": ca, "model_names": []}
assert used == set(range(len(G))), set(range(len(G))) - used

# ring model names from the inside model's table: reference column, plus the parts whose reference cell is empty
NO_REF = {"outer_body": "HSG1", "band_liner": "LNR1", "band_flex_thumb": "FLEX1", "band_flex_away": "FLEX2",
          "joystick_cap": "CAP1", "joy_sw_fingertip": "SW5", "joy_sw_hand": "SW4", "joy_sw_up": "SW1",
          "joy_sw_down": "SW3", "record_cap": None, "record_switch": "SW2", "cell_protection": "PRT1"}
thin = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(D) / "design" / "mech" / "thin" / "placement.csv"
if thin.exists():
    for r in csv.DictReader(open(thin, newline="")):
        if not r["reference"] and r["part"] in NO_REF and NO_REF[r["part"]] is None:
            continue  # drawn in an older inside model, no longer a part of the ring (the record cap, removed 2026-11-10)
        ref = r["reference"] or NO_REF.get(r["part"])
        assert ref, "placement part with no reference and no entry in NO_REF: " + r["part"]
        key = "ring:" + ref
        if key not in notes:
            NO_NOTE.append(ref)
            continue
        notes[key]["model_names"].append(r["part"])
# case
cp = json.load(open(D + "/design/case/out/case_params.json"))["parts"]
C = [
 ("U1", "The case's main chip, a small computer on a module.", "It runs the case: it reads the ring, drives the light and uploads recordings.", ["U1_esp32s3_mini1"]),
 ("U2", "The case's charger chip. It charges the case cell and powers the ring.", "It lets one USB-C cable charge the case and, through the case, the ring.", ["U2_bq25895"]),
 ("U3", "A voltage regulator that makes a steady supply for the case chips.", "The chips need a steady voltage, and the cell's voltage changes as it empties.", ["U3_tps63802"]),
 ("U4", "A memory chip in the case. It holds recordings copied from the ring.", "It keeps the audio safe until the case sends it on.", ["U4_zdsd64g"]),
 ("U5", "A switch with a current limit for the ring's charging line.", "It protects the case and the ring if something shorts the charging pins.", ["U5_tps2553"]),
 ("L1", "A coil in the case's charging circuit.", "The charger chip needs it to turn the supply into the charging current.", ["L1_1uH"]),
 ("L2", "A coil in the case's voltage regulator.", "The regulator needs it to produce a steady supply.", ["L2_0u47"]),
 ("J1", "The USB-C socket of the case.", "You plug the charging cable in here.", ["J1_usb4105"]),
 ("LED1", "The case's light.", "It shows the owner the state of the case and the ring.", ["LED1"]),
 ("BT1", "The case's battery cell.", "It stores the energy that charges the ring away from a wall socket.", ["cell_dnk852338"]),
 ("PCB1", "The case's main circuit board.", "It carries the case chips and joins them together.", ["main_board"]),
 ("PCB2", "A small circuit board that carries the four contact pins.", "It brings the ring's charging contacts out to the main board.", ["pin_board_pcb2", "pin_board_pcb2_wing_L", "pin_board_pcb2_wing_R"]),
 ("MECH1", "The case shell, a soft pebble shape.", "It holds the parts and gives the ring its seat.", ["shell"]),
 ("MECH2", "The case lid, a crowned cap that swivels aside.", "It closes the case and covers the ring.", ["lid"]),
 ("MECH3", "The bottom plate that closes the underside of the case.", "It holds the case parts in place from below.", ["base_plate"]),
 ("MECH4", "A hidden metal pin that the lid turns around.", "It is the lid's pivot.", ["hinge_pivot"]),
 ("MECH5", "The centre post that the ring lies around.", "It holds the pin board and the four pins against the pads on the inside of the band.", ["post"]),
 ("MECH8", "A thin glide disc between the lid and the shell.", "It lets the lid swivel smoothly and without scratching.", ["glide_1", "glide_2", "glide_3", "glide_4"]),
 ("MECH9", "A small magnet, one in the shell and one in the lid.", "The pair holds the lid closed.", ["magnet_base", "magnet_lid"]),
 ("MECH7", "A clear fill in the window of the case light.", "It lets the light show through and seals the opening.", []),
]
CASE_GONE = []
C.append(("P1-P4", "A spring-loaded contact pin that touches one pad of the ring.", "It carries charging power and data between the case and the ring.", ["pin_P1_VBUS", "pin_P2_D-", "pin_P3_D+", "pin_P4_GND"]))
for ref, w, y, m in C:
    gone = [x for x in m if x not in cp]  # model objects the case model no longer has: left out of the note, said below
    CASE_GONE.extend(gone)
    m = [x for x in m if x in cp]
    notes["case:" + ref] = {"what": w, "why": y, "checked_against": "design/case/case-architecture.md", "model_names": m}
out = sys.argv[1] if len(sys.argv) > 1 else str(EXPLORER / "content" / "part-notes.json")
import os; os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"notes": notes}, open(out, "w"), indent=1, ensure_ascii=False); open(out, "a").write("\n")
bad = [(k, len(v["what"].split()), len(v["why"].split())) for k, v in notes.items() if len(v["what"].split()) > 20 or len(v["why"].split()) > 25]
print(len(notes), bad)
print("case model objects no longer in case_params.json:", sorted(set(CASE_GONE)))
print("lines with no note yet:", sorted(set(NO_NOTE)))
