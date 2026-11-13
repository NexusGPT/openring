"""A7 edit of design/bom.csv. Every change names the line it changes by its reference cell; prints old and new cells.
Paths in new or changed cells are relative to the project root (ai-ring-recorder)."""
import csv, io, sys
F = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/bom.csv")
raw = open(F, newline='', encoding='utf-8').read()
rows = list(csv.reader(io.StringIO(raw)))
H = rows[0]
ix = {c: i for i, c in enumerate(H)}
body = rows[1:]


def find(ref):
    hit = [r for r in body if r and r[ix['reference']] == ref]
    if len(hit) != 1:
        sys.exit('reference %s found %d times' % (ref, len(hit)))
    return hit[0]


def setc(ref, **kw):
    r = find(ref)
    for k, v in kw.items():
        print('CHANGE %s %s\n   old: %s\n   new: %s' % (ref, k, r[ix[k]], v))
        r[ix[k]] = v


def new(after_ref, **kw):
    r = [''] * len(H)
    for k, v in kw.items():
        r[ix[k]] = v
    pos = body.index(find(after_ref)) + 1
    body.insert(pos, r)
    print('NEW after %s: %s' % (after_ref, r))


def delete(ref):
    r = find(ref)
    print('DELETE %s: %s' % (ref, r))
    body.remove(r)


NP = 'design/datasheets/npm1304_datasheet_v1_0.pdf'
# ---- 1. power chip (17.18; npm1304-reference.md D1 to D4)
setc('U2', maker_part_number='nPM1304-CAAA-R7', package='CSP-35 (nPM1304-CAAA)', size_mm='2.3775 x 3.0775 x 0.464',
     key_figures='nPM1304 (review F05): charge current 4 to 100 mA in 0.5 mA steps, accuracy +-10 % (p29); charge voltage 4.35 V is register BCHGVTERM value 9 (p36); battery discharge current limit IBATLIM 100 mA minimum (p29); 35 balls, VBUS B1 B2, VSYS C1 C2, VBAT D1 D2, no GPIO4 (Table 33 p153); order code nPM1304-CAAA-R7, reel of 1500 (Table 50 p168); charge setting 15 mA and 4.35 V',
     evidence='DS', source_file_or_url=NP + ' p29, p36, p153, p155, p157, p168 ; design/ecad/ring/npm1304-balls.csv ; design/architecture.md 17.18',
     open_action='S22 (architecture 17.22): bench proof of the motor regulator U11, which keeps the motor out of the IBATLIM path; price at quantity 1 not read (a distributor)')
for ref in ('R71', 'R72'):
    setc(ref, open_action='confirmed for the nPM1304: spec Table 36 page 156 (47 kohm gives 1.8 V, 150 kohm gives 3.0 V), resistor tolerance 5 % or better (npm1304-reference.md)')
setc('C71', item='Power chip VBUS capacitor 1.0 uF 25 V', function='U2 VBUS capacitor at balls B1, B2 (A7, npm1304-reference.md D1: Nordic C1 is 1.0 uF X5R 25 V; the former 4.7 uF part GRM155R60J475ME47D is rated 6.3 V)',
     maker='', maker_part_number='', package='C_0402', value='1.0 uF 25 V X5R', key_figures='X5R, 25 V, +-10 % (Nordic Table 37); VBUS accepts transients to 22 V (npm1304-reference.md D1)',
     evidence='DS', source_file_or_url=NP + ' p157 Table 37 ; design/ecad/ring/npm1304-reference.md D1',
     open_action='NEW-13: a distributor or the electronics designer must answer: a 1.0 uF 25 V X5R part (0402 or 0603) with its maker sheet; no such sheet is on file')
new('C71', item='Power chip VBAT capacitor 2.2 uF', reference='C85', quantity='1',
    function='U2 VBAT capacitor at balls D1, D2 (A7, npm1304-reference.md D2: Nordic C6; C21 on VBAT serves U4)',
    package='C_0402', value='2.2 uF 10 V X5R', key_figures='X5R, 10 V, +-10 % (Nordic Table 37)', evidence='DS',
    source_file_or_url=NP + ' p157 Table 37 ; design/ecad/ring/npm1304-reference.md D2',
    open_action='NEW-13: a distributor or the electronics designer must answer: the part code with its maker sheet')
new('C85', item='Power chip load switch output capacitors 1.0 uF', reference='C86,C87', quantity='2',
    function='U2 LSOUT1 (VDD_MIC, ball A4) and LSOUT2 (VDD_SD, ball A5), one each next to the ball (A7, npm1304-reference.md D4: Nordic configuration 2 puts C14 1.0 uF on the load switch output; the LOADSW chapter 6.4 itself states no capacitor rule)',
    package='C_0201', value='1.0 uF 10 V X5R', key_figures='X5R, 10 V, +-10 % (Nordic Table 38)', evidence='DS',
    source_file_or_url=NP + ' p158 Figure 59, p159 Table 38, p67 to p69 ; design/ecad/ring/npm1304-reference.md D4',
    open_action='NEW-13: a distributor or the electronics designer must answer: the part code with its maker sheet (a 10 V part; GRM033R60J105MEA2D on file is 6.3 V)')
new('C86,C87', item='Power chip VSYS capacitor, third 10 uF', reference='C88', quantity='1',
    function='U2 VSYS/PVDD third 10 uF at balls C1, C2, C7 (A7, npm1304-reference.md D3: Nordic C2, C3, C4)',
    package='C_0402', value='10 uF 16 V X5R', key_figures='X5R, 16 V, +-20 % (Nordic Table 37); a 10 uF 0402 loses much of its value under voltage (npm1304-reference.md D7)', evidence='DS',
    source_file_or_url=NP + ' p157 Table 37 ; design/ecad/ring/npm1304-reference.md D3',
    open_action='NEW-13: a distributor or the electronics designer must answer: the part code with its maker sheet (16 V)')
# ---- 2. motor (17.16, 17.22; motor-drive.md B1 to B6)
delete('Q1')
delete('D1')
new('M1', item='Motor regulator (in place of the motor switch and the motor diode)', reference='U11', quantity='1',
    function='3.0 V LDO from VBAT for the motor, enabled by MOTOR; keeps the motor current out of the nPM1304 battery limit (architecture 17.22)',
    maker='Texas Instruments', maker_part_number='TLV75530PDQNR', package='X2SON-4 (DQN)', size_mm='1.0 x 1.0 x 0.4 max', value='3.0 V',
    key_figures='500 mA, dropout 325 mV max at 500 mA, +-1.2 %, shutdown 1 uA max', evidence='DS',
    source_file_or_url='design/datasheets/motor_tlv755p.pdf p3 p5 p6 p28 p41 ; design/ecad/motor-drive/motor-drive.md 2.2',
    open_action='S22: bench proof of this circuit and the layout room for U11, C83, C84 (architecture 17.22); price not read')
new('U11', item='Capacitor 10 uF 0402 6.3 V', reference='C83,C84', quantity='2',
    function='U11 input and output; C84 is also the 2 uF or more across the motor that Jinlong asks', maker='Murata',
    maker_part_number='GRM155R60J106ME15', package='0402', size_mm='1.0 x 0.5', value='10 uF', key_figures='X5R, 6.3 V', evidence='DS',
    source_file_or_url='design/datasheets/p3_sgm38046.pdf p4 Table 1 ; design/ecad/motor-drive/motor-drive.md 2.2')
setc('M1', open_action='S21 closed by design/ecad/motor-drive/motor-drive.md: the motor is fed from VBAT by U11, outside the nPM1304 limit; the maker must confirm the part and its price (no price read); rim metal at the motor is 0.425 mm (rule 0.40)',
     function='haptic motor in the joystick-side shoulder of the band at -44 degrees, 0.7 mm off the band\'s centre line (inside model v4, architecture 17.15); red lead + on VMOT (U11 output), blue lead - on ground; two lead wires soldered to flex tail A pads MOT+ and MOT- (BAND_SPLIT table of make_netlist.py)')
setc('R61', item='Motor regulator enable series resistor 100 ohm', function='motor regulator enable series resistor 100 ohm')
setc('R62,R66', item='Pull-down 100 kohm: motor regulator enable (R62) and screen supply AVDDEN (R66)',
     function='motor regulator enable pull-down 100 kohm (R62); AVDDEN pull-down 100 kohm (R66, W10)')
# ---- 3. microphones (17.19; mic-path.md section 9 items 14 to 20)
KN = 'design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.pdf'
setc('U5,U6', function='PDM microphone, top port facing down through the floor, one stereo input (architecture 17.19); pins 1 DATA, 2 CLOCK, 3 SELECT, 4 Vdd, 5 to 8 GROUND',
     maker='Knowles', maker_part_number='SPK0641HT4H-1', package='8-pad LGA, top port 0.25 mm', size_mm='4.00 x 3.00 x 1.00',
     key_figures='SNR 64.5 dB(A), sensitivity -26 dBFS, 630 uA at 1.8 V (710 max), supply 1.6 to 3.6 V, clock 1.0 to 4.8 MHz, AOP 120 dB SPL (Knowles Rev A sheets 2 and 6, third-party host copy); U5 at X -10.8 and U6 at X +10.8, Y -4.8, ports 23.54 mm apart',
     evidence='DS', source_file_or_url=KN + ' sheets 2, 4, 6 ; design/mech/mic-path/mic-path.md sections 3, 4, 9 ; design/architecture.md 17.19',
     open_action='S23: Knowles or a distributor must answer: the orderable code (reel suffix) and stock of SPK0641HT4H-1; price at quantity 1 not read; second source SPK0838HT4H-B has another pin order')
setc('C31,C32', function='one per microphone (2), 1 uF on VDD_MIC kept from W4; Knowles sheet 4 (text lines 230 to 231): \'Bypass capacitors should be placed next to each microphone\'s Vdd pin\' and \'Capacitors near the microphone should not contain Class 2 dielectrics\': this X5R part is Class 2, so it sits on VDD_MIC away from the microphone and C35, C36 are the bypass next to Vdd',
     source_file_or_url=KN + ' sheet 4 ; design/parts/order-codes.md')
setc('C35,C36', function='one per microphone (2), 0.1 uF next to the Vdd pin (Knowles SPK0641HT4H-1 sheet 4, Figure 4); no Class 2 dielectric near the microphone (same sheet)',
     maker='', maker_part_number='', value='100 nF Class 1 (C0G/NP0)', key_figures='Class 1 dielectric required near the microphone (Knowles sheet 4); 0201 assumed',
     evidence='DS', source_file_or_url=KN + ' sheet 4',
     open_action='NEW-14: a distributor or the electronics designer must answer: a 100 nF Class 1 (C0G/NP0) part that fits under the board, with its maker sheet; the former code CL03A104KP3NNNC is X5R (Class 2)')
setc('R31,R32', function='series resistor on DATA, one per microphone (2); design choice kept from W4 (the SPK0641HT4H-1 sheet names no series resistor); pads kept on the board')
setc('PCB1', key_figures='0.325 mm ball pitch of U1; stack-up and pad pattern not yet drawn; 15 test pads; sound holes: none (top-port microphones port down through the floor)')
setc('HSG1', key_figures=find('HSG1')[ix['key_figures']].replace('openings: 2 microphone slots 1.2 x 0.3, 2 floor slots',
     'openings: 2 floor pockets 4.4 x 3.35 x 0.10, 2 holes 1.0 dia, 2 seats 2.0 dia x 0.10 on the underside (no microphone slots; design/mech/mic-path/mic-path.md section 5), 2 floor slots'))
setc('MEM1,MEM2', function='acoustic membrane disc over each floor hole of the 2 microphones, in a 2.0 x 0.10 mm seat flush with the underside (architecture 17.19)',
     package='disc with adhesive ring', size_mm='2.0 dia, 0.10 thick at most',
     key_figures='hydrophobic acoustic membrane (ePTFE class), at most 0.10 thick with its adhesive; the GAW112 cut on file is 0.24 thick, too thick for the seat (mic-path.md section 5)',
     evidence='CALC', source_file_or_url='design/mech/mic-path/mic-path.md sections 5 and 9 item 19',
     open_action='12.6: Gore must answer: a thinner cut (at most 0.10 mm) part number and price; no membrane part is chosen (mic-path.md O4)')
setc('GSK2,GSK3', function='foam gasket ring between each microphone lid and the floor pocket, PSA on both faces (architecture 17.19)',
     size_mm='1.8 outer dia, 1.0 bore', value='free thickness 0.10, 0.20 or 0.30, chosen per unit',
     key_figures='soft closed-cell foam ring OD 1.8, bore 1.0, PSA both faces; thickness chosen per unit from the measured lid gap (mic-path.md section 8)',
     source_file_or_url='design/mech/mic-path/mic-path.md sections 5, 8 and 9 item 20',
     open_action='S23: a gasket maker must answer: material, the three thicknesses and quote; bench B7 (seal, response)')
# ---- 4. recording light (17.21; light-path.md sections 6 and 10)
LT = 'design/datasheets/light_kb_KPG-1005SURC-TT_rs-copy.pdf'
setc('LED1', function='red top-view LED on the board\'s under face at X -9.70, Y -2.10, shining down into light guide LG1; pad 1 cathode, pad 2 anode (architecture 17.21)',
     key_figures='forward voltage 1.767 V typ at 1.5 mA (p3 curve), 2.0 V typ and 2.4 V max at 20 mA; 631 nm; 125 degrees (Kingbright preliminary sheet 2013)',
     source_file_or_url=LT + ' p1, p2, p3 ; design/mech/light-path/light-path.md sections 3, 4, 6',
     open_action='S25: Kingbright or a distributor must answer: is KPG-1005SURC-TT still sold, and its current sheet (12.5); fallback APHHS1005SURCK, not fit-checked')
setc('R41', value='820 ohm 1 %', key_figures='(3.0 V - 1.767 V - 1.5 mA x 0.7 ohm) / 1.5 mA = 821 ohm; 820 ohm gives 1.502 mA, 1.381 to 1.624 mA over the +-0.1 V spread (light-path.md section 6)',
     function='series resistor of the recording light, 1.5 mA from 3.0 V (architecture 17.21)',
     source_file_or_url='design/mech/light-path/light-path.md section 6 ; ' + LT + ' p3',
     open_action='NEW-9: a distributor (DigiKey or LCSC) must answer: the order code of the 820 ohm 0201 in the Yageo RC0201FR-07 series')
new('R41', item='Recording light guide', reference='LG1', quantity='1',
    function='clear moulded L-shaped light guide under the board: LED1 light turned by three 45 degree mirrors and up a riser through a 0.5 mm board hole to the window at X -12.425, Y -2.95 (architecture 17.21)',
    package='custom moulded part (polycarbonate or PMMA, mirror faces aluminium-coated)', size_mm='legs 3.265 and 1.390 long, section 0.40 x 0.680, riser 0.3 dia',
    key_figures='three aluminium-coated 45 degree mirrors; riser glued in the board hole with clear UV glue (light-path.md section 4)', evidence='CALC',
    source_file_or_url='design/mech/light-path/light-path.md sections 2, 4, 10',
    open_action='S25 (S-L3): a guide maker must answer: LG1 quote, the mirror coat and the glue')
new('LG1', item='Light plug', reference='LP1', quantity='1',
    function='clear block on the screen ledge at X -12.425, Y -2.95, between the ledge glass and the adhesive under the window (architecture 17.21)',
    package='custom clear block', size_mm='0.4 x 0.4 x 0.4', key_figures='clear, glued with clear glue to the glass (light-path.md section 4)', evidence='CALC',
    source_file_or_url='design/mech/light-path/light-path.md sections 4, 10',
    open_action='S25: the screen maker must confirm the ledge glass is clear at the plug; a maker must quote LP1')
# ---- 5. cell (17.17)
setc('BT1', value='20 to 27 mAh at US 9 (18.2 to 24.3 mAh at US 7)',
     key_figures=find('BT1')[ix['key_figures']] + '; by ring size 18.2 to 24.3 mAh at US 7 up to 24.7 to 32.9 mAh at US 13, smallest 18.2 mAh at US 7 (architecture 17.17)',
     source_file_or_url=find('BT1')[ix['source_file_or_url']] + ' ; design/architecture.md 17.17')

out = io.StringIO()
w = csv.writer(out, lineterminator='\n')
w.writerow(H)
w.writerows(body)
open(F, 'w', newline='', encoding='utf-8').write(out.getvalue())
print('rows', len(body))
