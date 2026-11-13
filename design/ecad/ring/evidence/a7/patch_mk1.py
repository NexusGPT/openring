"""A7 edit of make_netlist.py: additions, open order codes, provisional reasons. Each replacement must hit once."""
import sys
F = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/make_netlist.py")
s = open(F).read()
R = [
    ("    ('R61', 'W6 gate series resistor 100 ohm'), ('R62', 'W6 gate pull-down 100 kohm'),",
     "    ('R61', 'motor regulator enable series resistor 100 ohm (motor-drive.md)'), ('R62', 'motor regulator enable pull-down 100 kohm (motor-drive.md)'),\n"
     "    ('U11', 'motor 3.0 V regulator from VBAT, TLV75530PDQNR (motor-drive.md)'), ('C83', 'U11 input 10 uF'),\n"
     "    ('C84', 'U11 output and motor 10 uF (Jinlong 9-4 asks 2 uF or more)'),\n"
     "    ('C85', 'A7 D2: U2 VBAT 2.2 uF at balls D1, D2 (nPM1304 spec Table 37 C6, page 157)'),\n"
     "    ('C86', 'A7 D4: U2 LSOUT1 (VDD_MIC) 1.0 uF at ball A4 (nPM1304 spec configuration 2, C14, pages 158 and 159)'),\n"
     "    ('C87', 'A7 D4: U2 LSOUT2 (VDD_SD) 1.0 uF at ball A5 (nPM1304 spec configuration 2, C14, pages 158 and 159)'),\n"
     "    ('C88', 'A7 D3: U2 VSYS/PVDD third 10 uF (nPM1304 spec Table 37 C2 to C4, page 157)'),"),
    ("('C71', 'U2 VBUS 4.7 uF (nPM1300 DK PCA10184 C36; confirm against the nPM1304 specification, S18)')",
     "('C71', 'A7 D1: U2 VBUS 1.0 uF X5R 25 V (nPM1304 spec Table 37 C1, page 157)')"),
    ("OPEN_ORDER_CODE = {'U2': 'S18: Nordic. Order code left empty on the lead\\'s instruction (architecture 17.9 S18). Note for the lead: parts/research-npm1304.md section 4 lists nPM1304-CAAA-R and -R7 from Nordic spec Table 11, which disagrees with the brief\\'s \"not in the research\"; not used here'}",
     "OPEN_ORDER_CODE = {\n"
     "    'C71': ('A7 D1: 1.0 uF X5R 25 V 10 % (nPM1304 spec Table 37, page 157); no maker sheet of such a part is on file', 'a distributor or the electronics designer: a 1.0 uF 25 V X5R part in 0402 or 0603 with its maker sheet'),\n"
     "    'C85': ('A7 D2: 2.2 uF X5R 10 V (nPM1304 spec Table 37, page 157); no maker sheet on file', 'a distributor or the electronics designer: the part code with its maker sheet'),\n"
     "    'C86': ('A7 D4: 1.0 uF X5R 10 V (nPM1304 spec Table 38, page 159); no maker sheet of a 10 V part on file', 'a distributor or the electronics designer: the part code with its maker sheet'),\n"
     "    'C87': ('A7 D4: 1.0 uF X5R 10 V (nPM1304 spec Table 38, page 159); no maker sheet of a 10 V part on file', 'a distributor or the electronics designer: the part code with its maker sheet'),\n"
     "    'C88': ('A7 D3: 10 uF X5R 16 V (nPM1304 spec Table 37, page 157); no maker sheet of a 16 V part on file', 'a distributor or the electronics designer: the part code with its maker sheet'),\n"
     "    'C35': ('A7: 100 nF next to the microphone Vdd pin, no Class 2 dielectric near the microphone (Knowles SPK0641HT4H-1 sheet 4); the old code CL03A104KP3NNNC is X5R (Class 2)', 'a distributor or the electronics designer: a 100 nF Class 1 (C0G/NP0) part that fits under the board, or the lead accepts a Class 2 part'),\n"
     "    'C36': ('as C35', 'as C35'),\n"
     "}"),
    ("                w.writerow([p['reference'], '', 'order code', OPEN_ORDER_CODE[p['reference']], 'Nordic (open item S18)'])",
     "                w.writerow([p['reference'], '', 'order code'] + list(OPEN_ORDER_CODE[p['reference']]))"),
]
for old, new in R:
    n = s.count(old)
    print('hits', n, repr(old[:70]))
    if n != 1:
        sys.exit('replacement does not hit exactly once')
    s = s.replace(old, new)
# provisional reasons: drop nPM1304, IM68D128B and LED (pins now from maker tables), update MOTOR
lines = s.split('\n')
out = []
for l in lines:
    st = l.strip()
    if st.startswith("'nPM1304_CSP35': (") or st.startswith("'IM68D128B': (") or st.startswith("'LED_KPG1005': ("):
        print('dropped PROV row', st[:40]); continue
    if st.startswith("'MOTOR': ("):
        l = ("        'MOTOR': ('Jinlong W0525AB001D has two lead wires, red + and blue - (architecture 17.16, spec S-525113 rev 0); "
             "the maker gives colours, not numbers: P1 (+) and P2 (-) are this schematic\\'s names; the lead length is open item S10', "
             "'Jinlong drawing of the leads (S10, S4)'),")
        print('updated PROV MOTOR')
    out.append(l)
open(F, 'w').write('\n'.join(out))
print('done')
