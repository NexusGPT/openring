p=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/make_netlist.py")
s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a,s.count(a))
    s=s.replace(a,b)
rep("part('J1', 'FPC_15', 'FPC 15p 0.3mm', 'OPEN 12.1', 'ring:FPC_15P_0.3', D,",
    "part('J1', 'FPC_15', 'FH35C-15S-0.3SHW(50)', 'FH35C-15S-0.3SHW(50)', 'ring:Hirose_FH35C-15S-0.3SHW', D,")
rep("# J1 board connector: position numbers provisional (action 12.1); names follow the tail",
    "# J1 board connector Hirose FH35C-15S-0.3SHW(50), 15 positions: position numbers provisional (drawing not read); names follow the tail")

# controls
a=s.index("# joystick link (lead, 2026-11-10)")
b=s.index("part('D1', 'NSR0230P2'")
s=s[:a]+'''# A5 17.3: the five switches and the motor are in the band, reached through the two flex tails J_BAND_A and
# J_BAND_B (sheet "band"); each switch is one SKTAAAE010 between its line and ground.
# SW1 UP, SW2 record (keeps the bom.csv designator), SW3 DOWN, SW4 LEFT, SW5 RIGHT.
part('J_BAND_A', 'BAND_PADS_A', 'flex tail A (thumb side) 6 pads', '', 'ring:FLEX_PADS_1x6', BD,
     {str(i + 1): n for i, n in enumerate(BAND_A)}, by='number')
part('J_BAND_B', 'BAND_PADS_B', 'flex tail B 9 pads', '', 'ring:FLEX_PADS_1x9', BD,
     {str(i + 1): n for i, n in enumerate(BAND_B)}, by='number')
for sw, line in (('SW1', 'JOY_UP'), ('SW2', 'BTN_REC'), ('SW3', 'JOY_DOWN'), ('SW4', 'JOY_LEFT'), ('SW5', 'JOY_RIGHT')):
    part(sw, 'SKTAAAE010', 'SKTAAAE010', 'SKTAAAE010', 'ring:Alps_SKTA', BD, {'P1': line, 'P2': 'GND'}, by='number')
part('M1', 'MOTOR', 'VC0720B088L', 'VC0720B088L', 'ring:FPC_TAIL_2', BD,
     {'+': 'VDD_3V0', '-': 'MOTOR_DRV'})
'''+s[b:]

# contacts
a=s.index("# ---- case contacts and test pads (W7, W12)")
b=s.index("part('U9', 'TPD4E05U06'")
s=s[:a]+'''# ---- charging pads, USB protection and test pads (W7, W12)
# pads from -Y to +Y: VBUS, D-, D+, GND (case design, lead 2026-11-10); in the band, outside, reach the board by J_BAND_B
for cp, net in (('CP1', 'VBUS'), ('CP2', 'USB_DN'), ('CP3', 'USB_DP'), ('CP4', 'GND')):
    part(cp, 'CONTACTPAD_VBUS' if net == 'VBUS' else 'CONTACTPAD', 'gold pad 1.0mm', '', 'ring:PAD_1.0',
         BD, {'1': net}, by='number')
'''+s[b:]
rep("'SPARE_P3_04', 'SPARE_P3_05', 'VDD_1V8', 'GND', 'SHPHLD']",
    "'SPARE_P3_04', 'SPARE_P3_05', 'VDD_1V8', 'GND', 'SHPHLD', 'MIC_B_CLK', 'MIC_B_DATA', 'JOY_CENTER']")

# additions
a=s.index("    ('J2', 'joystick link: 6-pad")
b=s.index("]\n# bom.csv designators intentionally not placed")
s=s[:a]+'''    ('J_BAND_A', 'A5 17.3 flex tail A (thumb side): 5 switch lines and ground, 6 pads on the main board'),
    ('J_BAND_B', 'A5 17.3 flex tail B: motor 2, cell 2, temperature 1, charging pads 4 = 9 pads on the main board'),
    ('SW3', 'A5 16.4 joystick switch DOWN (SKTAAAE010)'), ('SW4', 'A5 16.4 joystick switch LEFT (toward hand)'),
    ('SW5', 'A5 16.4 joystick switch RIGHT (toward fingertip)'),
'''+s[b:]
rep("('CBL1', 'flat cable replaced by 6 wires W5-W10 and pad connectors J2, J3 (lead, 2026-11-10)'),",
    "('CBL1', 'joystick cable removed: switches reach the board through flex tail J_BAND_A (A5 17.3)'),\n              ('U7', 'A5 16.4: 2 microphones in place of 4'), ('U8', 'A5 16.4'), ('R33', 'A5 16.4 (decoupling of the removed pair)'), ('R34', 'A5 16.4'),\n              ('C33', 'A5 16.4'), ('C34', 'A5 16.4'), ('C37', 'A5 16.4'), ('C38', 'A5 16.4'),\n              ('W1', 'A5 17.3: contact board removed, the 4 charging pads reach the board through J_BAND_B'), ('W2', 'A5 17.3'), ('W3', 'A5 17.3'), ('W4', 'A5 17.3'),")

# provisional table
rep("        'ZDSD64GLGEAG': ('SD-card SPI-mode names per W3; the LGA-8 package drawing with numbers not obtained', 'Zetta ZDSD64GLGEAG-R datasheet with pad drawing (action 12.3)'),\n",
    "        'IM68D128B': ('names Clock, VDD, Ground, Data, Select from the Infineon IM68D121J brief of the same package (slim.md 5.1); no pin numbers in any document here', 'Infineon IM68D128B datasheet pin table'),\n        'SKTAAAE010': ('Alps spec KTA-601 shows two terminals but no terminal numbers or drawing (open item S9)', 'Alps SKTAAAE010 assembly drawing (S9)'),\n")
rep("'FPC_15': ('connector part and its position numbering not fixed; tail contact k assumed on connector position k', 'screen cable drawing and mating connector (action 12.1)'),",
    "'FPC_15': ('Hirose FH35C-15S-0.3SHW(50) selected (A5 16.4) but its drawing and position numbering are not read; tail contact k assumed on connector position k', 'Hirose FH35C drawing and the screen tail drawing (action 12.1, open item S8)'),")
rep("'MOTOR': ('motor datasheet 3A-03208B gives no lead colour or polarity', 'motor maker (action 12.4)'),",
    "'MOTOR': ('Vybronics VC0720B088L datasheet (slim-2.md 1.3) shows an FPC tail with no marked polarity or tail contact numbers', 'Vybronics VC0720B088L tail drawing (action 12.4)'),")
# PROV pins for DISP1 + bom override
rep("    with open(os.path.join(HERE, 'open-pins.csv'), 'w', newline='') as f:",
    '''    DISP1_PROV = {'3': 'MTP: the Tailor table (slim.md 1.3 p6) prints "4 MTP, 4 VCI": pin 3 is absent and pin 4 appears twice; order kept as printed, this entry is the 3rd printed',
                  '4': 'VCI: second printed "4" of the Tailor table (slim.md 1.3); number provisional'}
    with open(os.path.join(HERE, 'open-pins.csv'), 'w', newline='') as f:''')
rep("        for p in PARTS:\n            if 'OPEN' in p['value']",
    "        for k, why in DISP1_PROV.items():\n            nm = [x[1] for x in SYM['TOH095XVT-01'] if x[0] == k][0]\n            w.writerow(['DISP1', k, nm, why, 'Tailor Pixels pin table correction (open item S8)']); n += 1\n        for p in PARTS:\n            if 'OPEN' in p['value']")
rep("        if p['reference'] in bom and p['mpn'] != bom[p['reference']]:",
    "        if p['reference'] in A5_KEEP and p['reference'] in bom and p['mpn'] != bom[p['reference']]:\n            print('A5 keeps', p['reference'], repr(p['mpn']), '; bom.csv still says', bom[p['reference']])\n        elif p['reference'] in bom and p['mpn'] != bom[p['reference']]:")
rep("TESTPAD_REFS = [", "# references whose maker part changed in A5 (architecture 16.4, 17.4): bom.csv is behind, the lead updates it\nA5_KEEP = {'U3', 'U5', 'U6', 'M1', 'SW1', 'SW2', 'SW3', 'SW4', 'SW5', 'J1'}\nTESTPAD_REFS = [")
open(p,'w').write(s)
