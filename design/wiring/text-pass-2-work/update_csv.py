import csv,re,subprocess
R=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/")
P=R+'design/wiring/deferred-triage.csv'
raw=open(P,newline='',encoding='utf-8').read()
crlf='\r\n' in raw
rows=list(csv.reader(open(P,newline='',encoding='utf-8')))
C={}  # closed: id -> (sentence, quote, file, line)
def c(i,s,q,f,l): C[str(i)]=(s,q,f,l)
c(1,'the routed ring board passes the rules check with no unconnected item','Found 0 unconnected items','design/ecad/ring/pcb/board-notes-r3.md',20)
c(5,'the board checker declares the 0.20 mm courtyard exception of U5 and U6 and the round 3 check passes','U5 and U6 by 0.20','design/ecad/ring/pcb/check_board.py',7)
c(12,'the board has no hole in its outline (the light guide hole is removed in v7)','no drilled or routed hole in the outline','design/mfg/specs/main-board.md',34)
c(17,'the microphone part has no port in its -Y wall, so nothing is drawn on the footprint for it','The part has no such port.','design/mech/mic-path/mic-path.md',21)
c(18,'the J_BAND_A footprint is the land group only, hot-bar soldered to the tail foot; the stale PROVISIONAL text of provisional-footprints.json lines 13 and 14 is corrected today','hot-bar soldered to the tail foot','design/ecad/band/OpenRingBand.pretty/J_BAND_A_BOARD.kicad_mod',6)
c(28,'the VSYS ball C2 typed passive is a drawing choice with no change','VSYS ball C2 is typed passive in the symbol so ERC sees one VSYS output','design/ecad/ring/sch-notes.md',280)
c(52,'the lit window belonged to the recording light, which v7 removed, so the item is void','the recording light, LED1, the light guide LG1 and the board hole are removed in v7','design/architecture.md',523)
c(113,'the test pad access limit stays by design (testable only before step 17)','The access limit itself stays, by design.','design/mfg/assembly/assembly.md',320)
c(114,'K-A7 is closed by firmware F6, SHIP_SAMPLE keeps the factory flag for sample rings','CLOSED by firmware F6: SHIP_SAMPLE 0x7E keeps the','design/mfg/assembly/assembly.md',326)
c(116,'the liner resin is fixed as Master Bond EP30Med','Casting resin of the liner: fixed, Master Bond EP30Med','design/mfg/assembly/assembly.md',365)
c(117,'the clear adhesive ADH1 is fixed as tesa 69404','Clear adhesive ADH1: fixed, tesa 69404','design/mfg/assembly/assembly.md',363)
c(147,'the light path is void because the recording light was removed in v7, and light-path.md now says at its first line that it is history','the recording light was removed in design version 7','design/mech/light-path/light-path.md',1)
c(156,'architecture.md now marks 6.3 minutes per recorded hour REPLACED by 3.21 minutes (2 microphones) of firmware.md line 718','3.21 minutes per recorded hour, 2 microphones','design/architecture.md',303)
c(11,'finish ENEPIG and green solder mask on both sides are written into main-board.md from the stack-up and its open point 3 is closed','Surface finish ENEPIG; solder mask green on both sides','design/mfg/specs/main-board.md',18)
c(121,'S6 is a goal (splash and sweat resistant, no rating claimed) and the IP65 test is no longer required; requirements.md line 204 is marked REPLACED by line 26','Splash and sweat resistant as a goal; no rating is claimed','requirements.md',26)
O={
42:'open, needs hardware: bench step B-M3 on the built board, how long the motor current stays above 80 mA at a start',
43:'open, needs hardware: Power Profiler readings of buck efficiency, radio and MCU current, start phase and ship current, to replace the [ESTIMATE] constants of budget.py',
54:"open, needs a maker's answer: Tailor Pixels' written weight of the screen TOH095XVT-01 (or a weighing of the first ring's screen)",
57:'open, needs hardware: measure the panel supply with OLED_PWR_EN low and run the panel-failure test in use (b2-notes.md section 4)',
58:'open, needs hardware: bench B4 return-loss sweep on the built board with a network analyser, then fix the match parts',
59:'open, needs hardware: a network analyser for the return-loss test and bench tests T0 to T3 on a worn ring',
60:'open, owner: confirm or tighten the 10 dB and 3 dB RSSI pass lines',
66:'open, needs hardware: Power Profiler readings of the main chip, radio and power chip currents (build guide step W9)',
68:"open, needs a maker's answer: Tailor Pixels' written VCI current of TOH095XVT-01, then the rail measurement with the screen on (bench B5)",
71:'open, needs hardware: the built charge test at 15 mA to 4.35 V; the two requirements files now agree on paper (requirements.md line 195 states 1.17 to 1.57 hours at US 7 and 1.59 to 2.13 hours at US 13 from cell.md line 63), and the larger sizes are above the 90 minute line on paper',
75:'open, needs hardware: bench B7 recordings with the openings free and covered by a finger or thumb, against a bare part, with the gasket fitted',
79:'open, needs hardware: bench B1 recordings of the same meeting with the ring and a reference at 1 m and 3 m at three noise levels',
86:'open, needs hardware: pull test of the two heat stakes on a built case with a force gauge (the five wires below the holder are also not in the model)',
87:'open, needs hardware: bench B3 touch reading of E1 through the 1.97 mm wall on a built case, ring present and absent',
93:'open, needs hardware: bench B2 push-force test of the lid pad on a built case, pass above 159 gf',
94:'open, needs hardware: bench B7 on a built case, lid friction fit and droop on the pivot pin',
142:'open, needs hardware: run bench B2 (the 10 hour recording test) on a built ring first, then B1 and B3 to B9',
143:"open, needs a maker's answer: Nordic's nPM1304 EK user guide (polarity, header labels, VDDIO tie), the Power Profiler and SDK documents and a real Plaud export file, each read from a copy the team can open",
144:"open, needs a maker's answer: Nordic's nRF54LM20 DK user guide, Connector interface table, from a copy the team can open",
145:"open, needs a maker's answer: Grepow's written confirmation of 15 mA to 4.35 V and of the peak discharge with the protection circuit",
146:'open, needs hardware: run the section 2.9 bench steps on the nPM1304-EK kit and record the readings',
150:'open, needs hardware: Power Profiler readings during an open Bluetooth link and live audio, and the LC3 margin measured on the chip',
151:'open, needs hardware: bench tests A4 (directional part against omni array), A8 (hand effect), P7 (standby over days) and D3 (OLED power)',
159:'open, needs hardware: bench steps B-M3 and B-M5 for the motor start allowance and the T-MOTOR pass line, and bench B2 for the microphone current at 1.280 MHz',
10:'open, design work: make assembly.md row 370 match placement-final.csv, or state what is still to confirm (assembly.md is under independent review)',
20:"open, needs a maker's answer: Nordic's CSP61 (nRF54LM20A CAAA) package drawing: ball pitch, ball diameter, A1 corner and orientation",
27:'open, design work: write a fixed decision line for each open design risk (ring section 9, case section 7), using the maker documents on disk; the lead rules',
48:'open, design work: inside model v10 folds the 12.4 mm cable of layout C, and the owner closes S27 (the taller block rework is under way)',
55:"open, needs a maker's answer: Tailor Pixels sends the SH8501A start-up code and datasheet for TOH095XVT-01 (action 12.1)",
61:'open, design work: run the integer check on the antenna texts and record its result in design/mech/antenna/CHECKLIST.md',
72:"open, needs a maker's answer: Knowles or a distributor gives the orderable code with reel suffix and the stock of SPK0641HT4H-1",
83:"open, needs a maker's answer: the case cell maker's datasheet for its protection circuit and tolerance",
84:"open, needs a maker's answer: Harwin's stroke (at least 0.34 mm) and length tolerance of P70-6000045R",
90:"open, needs a maker's answer: TI's answer on the PMID load while charging and on D+ and D- (S5)",
95:'open, design work: decide whether the 0.25 mm step test is the straight lift-out; if not, simulate the lift as a motion and re-render the C5c pictures (the lead rules)',
102:'open, design work: settle each ASSUMED value in dimensions.csv and ring.py, or keep the tag with a reason (the lead rules)',
103:'open, design work: confirm the mic port position and the 2.5 mm joystick stem in the model (mech-notes.md line 70); the M1.2 screw part is closed, architecture.md line 162 is marked REPLACED today',
111:"open, needs a maker's answer: the 3M order number of DP420 Black 50 ml cartridge, and a bom row for the floor slot sealant",
112:'open, design work: the mechanical designer names the DAM1 material and checks the seal of the pocket edge (K15) (the lead rules)',
115:'open, design work: the mechanical designer decides the K-A12 route and writes it into steps 20 and 21 with the DAM1 material (the lead rules)',
119:"open, needs a maker's answer: a moulder quote for CAP1, the body maker quote for FRM1, and the flex maker's answer on the joystick head stiffener and its bond (S26)",
120:'open, needs hardware: bench B7 sound loss through bore, gasket and mesh on the first ring, to choose the gasket thickness (0.10, 0.2 or 0.3 mm)',
122:'open, design work: run check_assembly.py, fix the A1 and A2 rows (missing steps for U11, C83 to C88, SEAL1) and record a pass (assembly.md is under independent review)',
123:'open, design work: the assembly owner rewrites steps 2 and 25 of assembly.md as H19 says (assembly.md is under independent review)',
124:'open, design work: make the rows still open in assembly.md section 6 in the files they name: bom row, placement.csv line 39, architecture text (assembly.md is under independent review)',
126:"open, needs a maker's answer: distributor or maker order codes for items 5, 6 and 9 and the 100 nF X7R",
129:'open, design work: check C73 to C79 against design/datasheets/npm1304_datasheet_v1_0.txt and write the result in bom.csv (the lead rules)',
157:'open, design work: the architecture owner rewrites the H13 sections after the 16.9 items close (the lead rules)',
158:'open, design work: architecture.md lines 153 and 229 are marked REPLACED today; the record button is still described without a REPLACED mark at lines 23, 369, 433 and 482 (outside the named lines)',
160:'open, design work: do the work of lead-decisions.md line 65 in order (exterior 4.17 mm, inside model v10, and the rest of the row)',
161:"open, design work: the one-pager script lines 64 and 99 are corrected and the PDF rebuilt today; READ-FIRST.template.html lines 69 and 106 still say the board is not routed",
}
O={str(k):v for k,v in O.items()}
before=sum(1 for r in rows[1:] if r[5].startswith('open'))
ids=set(C)|set(O)
n=0
for r in rows[1:]:
    if r[0] in ids:
        assert r[5].startswith('open'),(r[0],r[5])
        if r[0] in C:
            s,q,f,l=C[r[0]]
            line=open(R+f,encoding='utf-8').read().split('\n')[l-1]
            assert q in line,(r[0],q)
            r[5]='closed 2026-11-13: %s ("%s"); %s:%d'%(s,q,f,l)
        else:
            r[5]=O[r[0]]
        n+=1
assert n==66 and len(ids)==66,(n,len(ids))
after=sum(1 for r in rows[1:] if r[5].startswith('open'))
with open(P,'w',newline='',encoding='utf-8') as fh:
    w=csv.writer(fh,lineterminator='\r\n' if crlf else '\n')
    w.writerows(rows)
print('rows',len(rows)-1,'open before',before,'after',after,'crlf',crlf)
