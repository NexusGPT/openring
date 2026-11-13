P=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mfg/assembly/assembly.md")
L=open(P,encoding='utf-8').read().split('\n')
def idx(prefix,after=0):
    for i in range(after,len(L)):
        if L[i].startswith(prefix): return i
    raise SystemExit('missing '+prefix)
def block(h):
    return idx(h)
# ---- step 2
i=block('### Step 2. ')
old_join=L[i+2]
assert old_join.startswith('- **Join:** every board part')
# keep the parts-face list from the old line (without J1, screen face parts, test pads)
L[i]='### Step 2. Print paste, place the board parts on both faces, reflow twice (screen face first, then parts face)'
L[i+2]=("- **Join:** the board parts of `design/bom.csv` to PCB1 in TWO solder passes, one per face, each with its own paste stencil and its own reflow. The board has parts on both faces (`design/ecad/ring/pcb/board-notes-r3.md:35`). "
"PASS 1, the SCREEN FACE (KiCad B.Cu, 21 parts in `design/ecad/ring/pcb/fab/ring-pos-back.csv:1`): J1 (`screen_connector`, Hirose FH35C-15S-0.3SHW(50), `design/bom.csv:11`), the eight 0201 parts C1, C2, C5, C7, C14, FB1, R71 and R72, with the stencil of `design/ecad/ring/pcb/fab/gerber/ring-B_Paste.gbr`. "
"The 12 test pads TP1, TP3, TP4, TP5, TP6, TP12, TP14, TP15, TP17, TP18, TP19 and TP21 are copper on this face and get no paste (TP2, TP7 to TP11, TP13, TP16, TP20 and TP22 do not exist) [PROPOSED: reason, a solder bump on a test pad spoils the spring-pin contact of step 5; the file `ring-B_Paste.gbr` as delivered has a round 0.80 mm opening at each of the 12 test pads (`design/wiring/guide-fix-work/paste_count.log`), so the stencil maker closes those 12 openings]. "
"PASS 2, the PARTS FACE (KiCad F.Cu, 72 parts in `design/ecad/ring/pcb/fab/ring-pos-front.csv:1`), with the stencil of `design/ecad/ring/pcb/fab/gerber/ring-F_Paste.gbr`: "
"U1 (`main_chip`), U2 (`power_chip`, nPM1304, `design/architecture.md:566`), U3 (`storage`), U10, U4 (`screen_supply_chip`), U5 (`mic_1`) and U6 (`mic_2`), Knowles SPK0641HT4H-1 (`design/architecture.md:654`, `design/bom.csv:9`), ANT1 (`antenna`, on the parts face at X -10.80, Y 5.25, on its maker's land pattern, no notch), C89 (not fitted: the pad only) and LT1 (0 ohm) at the antenna (`design/bom.csv:85`, `design/bom.csv:86`), L2, L3, L4, C3, C12, X1 (`crystal_32M`), X2 (`crystal_32k`), L1, R1, R2, C4, C6, C10, C11, L10 (`screen_supply_coil`), C21, C26, C27, C24, C25, C23, C22, C28, C29, C31, C32, C35, C36, R31, R32, R57, R58, R60, C60, U11 (`motor_regulator`, TLV75530PDQNR, at X 0.0, Y 4.2), C83 (`motor_cap_in`, X 0.0, Y 5.45), C84 (`motor_cap_out`, X 1.27, Y 5.0, turned 90) (`design/architecture.md:705`, `design/mech/thin/placement.csv:19` to `design/mech/thin/placement.csv:21`; the places are the model's proposal until the board layout confirms them, `design/architecture.md:760`), U9, R61 and R62 (now on U11's enable pin, `design/architecture.md:705`), R66, R63, R64, R65, C61, C72, C80, C81, C82, C71, C73, C74, C75, C78, C79, C76, C77, C85, C86, C87, C88 (`design/bom.csv:67` to `design/bom.csv:69`), L71 (`power_coil_1`), L72 (`power_coil_2`). "
"The two ribbon land rows J_BAND_A and J_BAND_B are copper on the parts face and get no paste [PROPOSED: reason, a solder bump on a land spoils the hot-bar joint of step 16]. "
"The motor switch and the motor diode of earlier versions are not fitted: they left the design (`design/architecture.md:705`). LED1, R41 and Q2 are removed in v7 and are not fitted (`design/architecture.md:834`). C13 is not mounted (`design/bom.csv:18`). "
"ORDER OF THE TWO PASSES [PROPOSED: the lead confirms]: the screen face goes first and the parts face second. Reason: the face reflowed first hangs face down during the second reflow, and the melted solder holds a part there only if the part is small; the screen face has 9 parts, all small (eight 0201 parts and the connector), and the parts face has 72, among them U1 and the 1.00 mm parts (`design/architecture.md:426`). "
"How the screen face parts stay on during pass 2: the board lies on a carrier with the screen face down, flat, with a pocket under J1 (the housing is 0.9 mm high, `design/wiring/screen-cable-study.md:59`); nobody touches or moves the board while the solder is liquid; the board is not turned over until it is cold.")
L[i+3]="- **Locate:** fiducials of the board file; each part's land pattern (from S14); in pass 2 the board lies on its outline in the carrier."
L[i+4]=("- **Before:** step 1 passed. The antenna mount is decided: ANT1 is soldered on its maker's land pattern on the parts face, with no notch (before model v9, ANT1 stood in a corner notch with its pads off the board, `design/architecture.md:513`, open item S15). Before pass 2: the pass 1 check below has passed.")
L[i+5]=("- **Check:** after PASS 1, optical inspection of the screen face at 10 times: J1 sits flat on the board with none of its 15 contact tails and its 2 mounting tails lifted, no solder bridge between neighbouring contacts (0.3 mm pitch), each of the eight 0201 parts in place and not tilted, no solder on any of the 12 test pads. "
"After PASS 2, X-ray of U1 (61 balls), U2, U4 and the U3 lands; optical inspection of every other part of the parts face; then the screen face again: all 9 parts still in place, J1 still flat. A screen face part that fell in pass 2 is put back by hand soldering on that face (the ring is not reflowed a third time) [PROPOSED]. "
"The number of reflow passes that J1 and the 0201 parts accept is not in any file cited here: the parts see two reflows (open, for the lead).")
L[i+6]="- **After:** reflow is not undone. A parts face part can be reworked by hand until step 17; a screen face part until step 15, because from step 15 the screen's cable lies over that face."
# ---- step 3
j=block('### Step 3.')
L[j+2]=L[j+2].replace("below the board's under face","below the board's parts face")
L[j+3]=L[j+3].replace("the board's under face as zero","the board's parts face as zero")
# ---- step 4
k=block('### Step 4.')
L[k]='### Step 4. Clean and inspect both faces before the jig'
L[k+2]=("- **Join:** nothing is joined. Both faces of PCB1 are cleaned of flux residue, then dried: the SCREEN FACE round the 12 test pads, the PARTS FACE round the ribbon lands J_BAND_A and J_BAND_B [PROPOSED: reason, the spring pins of step 5 and the hot-bar joints of step 16 need bare copper; the paste and flux of step 2 are not named by any file]. History: this step fitted the light guide LG1 until v6; the light guide is removed in v7 (`design/architecture.md:834`).")
L[k+4]="- **Before:** steps 2 and 3 passed."
L[k+5]="- **Check:** under a microscope at 10 times, no residue on any of the 12 test pads or on any ribbon land [PROPOSED]; the gasket choice of step 3 is still recorded against the board's serial number."
# ---- step 5
m=block('### Step 5.')
L[m+2]=("- **Join:** nothing is joined. A jig touches the SCREEN FACE, where the 12 test pads are, and the PARTS FACE, where the ribbon lands J_BAND_B are (`design/ecad/ring/pcb/placement-final.csv:80`; the jig holds the board between two sets of spring pins [PROPOSED: the lead and the jig maker confirm]). "
"THE 12 TEST PADS, 0.80 mm round, on the screen face in a grid of 3 columns and 5 rows at a pitch of 1.05 mm, in the ring frame (X along the finger, `design/ecad/ring/pcb/placement-final.csv:87` to `design/ecad/ring/pcb/placement-final.csv:98`): "
"column X -2.65: TP1 (Y -2.10), TP3 (Y -1.05), TP4 (Y 0.00), TP5 (Y 1.05), TP6 (Y 2.10); column X -1.60: TP12 (Y 1.05), TP14 (Y 2.10); column X -0.55: TP15 (Y -2.10), TP17 (Y -1.05), TP18 (Y 0.00), TP19 (Y 1.05), TP21 (Y 2.10). "
"The signal of each pad (`design/ecad/ring/netlist.csv:18`, `design/ecad/ring/netlist.csv:116`, `design/ecad/ring/netlist.csv:189`, `design/ecad/ring/netlist.csv:196`, `design/ecad/ring/netlist.csv:253`, `design/ecad/ring/netlist.csv:255`, `design/ecad/ring/netlist.csv:257`, `design/ecad/ring/netlist.csv:259`, `design/ecad/ring/netlist.csv:261`, `design/ecad/ring/netlist.csv:267`, `design/ecad/ring/netlist.csv:269`, `design/ecad/ring/netlist.csv:319`): "
"SWD TP3 SWDCLK, TP4 SWDIO, TP5 NRESET, TP17 VDD_1V8, TP18 GND (`design/architecture.md:291`); log TP1 DBG_TX, send-only; TP19 SHPHLD; TP21 MIC_B_DATA; TP6, TP12, TP14 and TP15 are on four spare pins (P1.00, P2.00, P3.03, P3.04), used by nothing in this guide. No other test pad exists. "
"POWER: the jig feeds a battery voltage on the J_BAND_B cell lands and a 10 k resistor on its thermistor land [PROPOSED: reason, the cell is not yet on the board and the power chip needs a battery and a thermistor reading], and VBUS, D-, D+, GND on the J_BAND_B pad lands, which are the USB lines of the four charging pads (`design/bom.csv:77`).")
L[m+3]="- **Locate:** the jig's pins on the 12 test pads and on the J_BAND_B lands; the board sits on its outline, the screen face toward the pad pins."
L[m+6]=("- **After:** this is the last moment the SWD pads can be reached with the screen face open. They lie on the screen face. From step 15 the screen's cable and its panel lie over them, and the cable floats 0.40 mm above them (`design/wiring/screen-cable-study.md:205`: they are reachable before the panel goes on). After step 17 the only way into the chip is USB through the charging pads; a broken boot loader after step 17 means a scrapped ring (conflict K-A1).")
open(P,'w',encoding='utf-8').write('\n'.join(L))
